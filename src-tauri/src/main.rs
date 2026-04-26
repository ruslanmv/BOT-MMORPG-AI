// src-tauri/src/main.rs
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

use std::ffi::OsString;
use std::fs;
use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

use reqwest::Client;
use tauri::{AppHandle, Manager, Window};

// ---------------------------
// CONSTANTS / DEFAULTS
// ---------------------------
const DEFAULT_GAME_ID: &str = "genshin_impact";
const DEFAULT_VERSION: &str = "0.01";

// IMPORTANT:
// In production you are bundling Windows "embeddable" Python.
// Embeddable Python often cannot create venv ("No module named venv").
// So production uses a portable --target directory and adjusts python*. _pth to include it.
const PROD_EXTRAS: &str = "launcher,backend"; // exclude ml here; install ML later on-demand

// ---------------------------
// APP STATE
// ---------------------------
#[derive(Clone, Debug)]
struct SidecarApi {
    base_url: String,
    token: String,
}

// In-memory error record captured from the Rust side. The Python sidecar
// keeps its own ring buffer (modelhub/diagnostics/collector.py); the
// `recent_errors_for_ai` command merges both before formatting.
//
// Kept tiny on purpose: the diagnostic layer must not bloat AppState or
// trigger heavy serialization. Strings only, no boxed errors.
#[derive(Clone, serde::Serialize)]
struct ErrorEntry {
    timestamp_ms: u64,
    source: String,        // "rust" | "spawned_script"
    error_type: String,    // e.g. "ModuleNotFoundError", "SidecarTimeout"
    message: String,
    primary_file: String,  // best-effort first File "..." extracted from traceback
    primary_line: u32,
    traceback: String,     // raw traceback text for spawned scripts, empty for rust-side
    context: serde_json::Value,
}

const MAX_ERRORS: usize = 50;

struct AppStateInner {
    current_process: Mutex<Option<Child>>,
    sidecar_process: Mutex<Option<Child>>,
    sidecar: Mutex<Option<SidecarApi>>,
    http: Client,
    recent_errors: Mutex<std::collections::VecDeque<ErrorEntry>>,
}

#[derive(Clone)]
struct AppState {
    inner: Arc<AppStateInner>,
}

#[derive(Serialize, Deserialize)]
struct AiConfig {
    provider: String,
    gemini_key: String,
    openai_key: String,
}

// ---------------------------
// CONFIG (.env) HELPERS
// ---------------------------
fn env_file_path(app: &AppHandle) -> PathBuf {
    // DEV convenience: prefer repo root .env if present
    if cfg!(debug_assertions) {
        if let Ok(cwd) = std::env::current_dir() {
            let candidate = cwd.join("..").join(".env");
            if candidate.exists() {
                return candidate;
            }
        }
    }

    // PROD: Use installation directory (Program Files\BOT-MMORPG-AI)
    // This keeps config alongside the application
    let cfg_dir = local_data_root(app);
    let _ = fs::create_dir_all(&cfg_dir);
    cfg_dir.join(".env")
}

fn ensure_default_env(app: &AppHandle) {
    let path = env_file_path(app);
    if path.exists() {
        return;
    }
    let default_content =
        "AI_PROVIDER=\"gemini\"\nGEMINI_API_KEY=\"\"\nOPENAI_API_KEY=\"\"\nPYTHON_PATH=\"\"\n";
    let _ = fs::write(path, default_content);
}

fn get_env_var(app: &AppHandle, key: &str) -> String {
    ensure_default_env(app);
    let env_path = env_file_path(app);
    let content = fs::read_to_string(&env_path).unwrap_or_default();

    for line in content.lines() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        if let Some((k, v)) = line.split_once('=') {
            if k.trim() == key {
                let mut value = v.trim().to_string();
                if (value.starts_with('"') && value.ends_with('"'))
                    || (value.starts_with('\'') && value.ends_with('\''))
                {
                    value = value[1..value.len() - 1].to_string();
                }
                return value;
            }
        }
    }
    String::new()
}

fn update_env_file(app: &AppHandle, key: &str, value: &str) -> Result<(), String> {
    ensure_default_env(app);
    let env_path = env_file_path(app);

    let mut lines: Vec<String> = fs::read_to_string(&env_path)
        .unwrap_or_default()
        .lines()
        .map(|s| s.to_string())
        .collect();

    let mut found = false;
    for line in lines.iter_mut() {
        if let Some((k, _)) = line.split_once('=') {
            if k.trim() == key {
                *line = format!("{}=\"{}\"", key, value.replace('"', "\\\""));
                found = true;
                break;
            }
        }
    }
    if !found {
        lines.push(format!("{}=\"{}\"", key, value.replace('"', "\\\"")));
    }

    fs::write(&env_path, lines.join("\n") + "\n").map_err(|e| e.to_string())
}

// ---------------------------
// UTILS
// ---------------------------
fn is_windows() -> bool {
    cfg!(target_os = "windows")
}

fn path_sep() -> &'static str {
    if is_windows() {
        ";"
    } else {
        ":"
    }
}

fn normalize_game_id(game_id: Option<String>) -> String {
    let gid = game_id.unwrap_or_default().trim().to_string();
    if gid.is_empty() {
        DEFAULT_GAME_ID.to_string()
    } else {
        gid
    }
}

/// Dev repo root helper (src-tauri parent)
fn dev_repo_root() -> PathBuf {
    std::env::current_dir()
        .ok()
        .and_then(|p| p.parent().map(|x| x.to_path_buf()))
        .unwrap_or_else(|| PathBuf::from(".."))
}

fn venv_python_from_root(root: &Path) -> PathBuf {
    if is_windows() {
        root.join(".venv").join("Scripts").join("python.exe")
    } else {
        root.join(".venv").join("bin").join("python3")
    }
}

fn venv_bin_from_root(root: &Path) -> PathBuf {
    if is_windows() {
        root.join(".venv").join("Scripts")
    } else {
        root.join(".venv").join("bin")
    }
}

/// Optional bundled python path in resources (used for DEV fallback; PROD uses copy-to-LocalAppData)
fn bundled_python_path(app: &AppHandle) -> Option<PathBuf> {
    let rel = if is_windows() {
        "resources/python/python.exe"
    } else {
        "resources/python/bin/python3"
    };
    app.path_resolver()
        .resolve_resource(rel)
        .and_then(|p| if p.exists() { Some(p) } else { None })
}

fn find_python_for_app(app: &AppHandle) -> Result<PathBuf, String> {
    // 1) .env explicit python path
    let explicit = get_env_var(app, "PYTHON_PATH");
    if !explicit.trim().is_empty() {
        let p = PathBuf::from(explicit.trim());
        if p.exists() {
            return Ok(p);
        }
        return Err(format!("PYTHON_PATH was set but not found: {}", p.display()));
    }

    // 2) Dev: repo .venv
    if cfg!(debug_assertions) {
        let root = dev_repo_root();
        let vpy = venv_python_from_root(&root);
        if vpy.exists() {
            return Ok(vpy);
        }
    }

    // 3) Bundled python if present
    if let Some(p) = bundled_python_path(app) {
        return Ok(p);
    }

    // 4) Fallback: system python
    Ok(PathBuf::from(if is_windows() { "python" } else { "python3" }))
}

fn apply_dev_venv_env(cmd: &mut Command, repo_root: &Path) {
    let venv_root = repo_root.join(".venv");
    if !venv_root.exists() {
        return;
    }

    let venv_bin = venv_bin_from_root(repo_root);

    cmd.env("VIRTUAL_ENV", &venv_root);

    let old_path = std::env::var_os("PATH").unwrap_or_default();
    let mut new_path = OsString::new();
    new_path.push(venv_bin.as_os_str());
    new_path.push(path_sep());
    new_path.push(old_path);
    cmd.env("PATH", new_path);
}

/// Apply stable Python env (both dev + prod), avoids Windows stdout weirdness.
fn apply_stable_python_env(cmd: &mut Command) {
    cmd.env("PYTHONUNBUFFERED", "1");
    cmd.env("PYTHONUTF8", "1");
    cmd.env("PYTHONIOENCODING", "utf-8");
}

// ---------------------------
// PRODUCTION RUNTIME LAYOUT (Installation Directory - Program Files)
// ---------------------------

/// Returns the installation directory (where the executable is located).
/// In production this is C:\Program Files\BOT-MMORPG-AI
/// In dev this falls back to the current directory.
fn installation_dir() -> PathBuf {
    std::env::current_exe()
        .ok()
        .and_then(|exe| exe.parent().map(|p| p.to_path_buf()))
        .unwrap_or_else(|| std::env::current_dir().unwrap_or_else(|_| PathBuf::from(".")))
}

fn local_data_root(_app: &AppHandle) -> PathBuf {
    // Use the installation directory (Program Files\BOT-MMORPG-AI) for all data
    // This keeps everything in one place instead of scattering across AppData
    installation_dir()
}

fn ensure_runtime_layout(app: &AppHandle) -> PathBuf {
    let root = local_data_root(app);
    // Note: We no longer add "BOT-MMORPG-AI" suffix since we're already
    // in the installation directory (C:\Program Files\BOT-MMORPG-AI)
    let _ = fs::create_dir_all(root.join("runtime").join("py"));
    let _ = fs::create_dir_all(root.join("runtime").join("tools"));
    let _ = fs::create_dir_all(root.join("content"));
    let _ = fs::create_dir_all(root.join("datasets"));
    let _ = fs::create_dir_all(root.join("models"));
    let _ = fs::create_dir_all(root.join("logs"));
    root
}

fn managed_python_root(app: &AppHandle) -> PathBuf {
    ensure_runtime_layout(app).join("runtime").join("py")
}

/// Where the bundled Python keeps its site-packages tree.
///
/// The build pipeline (`scripts/build_pipeline.ps1` STEP 6.7) packs
/// `src-tauri/resources/python/` into `python-runtime.zip` AS-IS, with
/// `site-packages/` as a SUBDIRECTORY of the python interpreter dir.
/// At runtime `extract_zip_to` unpacks that zip into
/// `<INSTDIR>/runtime/py/python/`, so site-packages lands at
/// `<INSTDIR>/runtime/py/python/site-packages/` — INSIDE python/, not
/// next to it.
///
/// A previous version of this function returned `runtime/py/site-packages/`
/// (a sibling of `python/`), which was created empty by
/// `ensure_runtime_layout` and never populated. The site-packages-empty
/// detection in `ensure_python_env` then triggered a doomed wheelhouse
/// repair path on every launch — confusingly, while the application
/// itself worked fine because the embedded Python's `_pth` already
/// pointed at the real `.\site-packages` (which resolves to
/// `<runtime>/py/python/site-packages/` next to python.exe).
///
/// Returning the real location here makes the `_pth` re-patch
/// idempotent, silences the spurious repair messages, and aligns the
/// PYTHONPATH entries we add in `run_python_script` /
/// `start_sidecar_server` with the actual on-disk layout.
fn managed_site_packages_dir(app: &AppHandle) -> PathBuf {
    managed_python_root(app).join("python").join("site-packages")
}

/// Copy target for embedded python runtime in PROD
fn managed_embedded_python_dir(app: &AppHandle) -> PathBuf {
    managed_python_root(app).join("python")
}

fn bundled_python_dir(app: &AppHandle) -> Option<PathBuf> {
    // Try common resource layouts.
    let candidates = [
        "python",           // <resource_dir>\python
        "resources/python", // sometimes resources are nested
        "resources\\python",
        "python\\",
    ];

    for rel in candidates {
        if let Some(p) = app.path_resolver().resolve_resource(rel) {
            if p.exists() {
                return Some(if p.is_dir() { p } else { p.parent()?.to_path_buf() });
            }
        }
    }

    // Fallback: build from resource_dir() directly.
    if let Some(rd) = app.path_resolver().resource_dir() {
        let p1 = rd.join("python");
        if p1.exists() {
            return Some(p1);
        }

        let p2 = rd.join("resources").join("python");
        if p2.exists() {
            return Some(p2);
        }
    }

    None
}

/// Locate a packed python runtime archive. The build pipeline packs the entire
/// embedded python tree + site-packages into a single zip so Tauri's NSIS
/// bundler doesn't have to iterate tens of thousands of files (which floods
/// handlebars debug logs and kills the GitHub Actions job with exit 1).
///
/// IMPORTANT: the zip lives in a *subdirectory* of resources (`runtime/`),
/// not at the root, because Tauri 1.x's `resources/**` glob in tauri.conf
/// does not match files that sit directly under resources/. The earlier
/// (pre-fix) layout silently produced a 0.7 MB stub installer because NSIS
/// never saw the zip. We still probe a couple of legacy locations so an
/// older installer continues to work for users who upgraded in place.
fn bundled_python_archive(app: &AppHandle) -> Option<PathBuf> {
    let candidates = [
        // New layout (Tauri-glob safe).
        "runtime/python-runtime.zip",
        "runtime\\python-runtime.zip",
        "resources/runtime/python-runtime.zip",
        "resources\\runtime\\python-runtime.zip",
        // Legacy layout (kept so a re-installed-over-old build still works).
        "python-runtime.zip",
        "resources/python-runtime.zip",
        "resources\\python-runtime.zip",
    ];
    for rel in candidates {
        if let Some(p) = app.path_resolver().resolve_resource(rel) {
            if p.exists() {
                return Some(p);
            }
        }
    }
    if let Some(rd) = app.path_resolver().resource_dir() {
        for rel in &[
            "runtime/python-runtime.zip",
            "resources/runtime/python-runtime.zip",
            "python-runtime.zip",
            "resources/python-runtime.zip",
        ] {
            let p = rd.join(rel);
            if p.exists() {
                return Some(p);
            }
        }
    }
    None
}

/// Extract every entry of a zip archive into `dst`. Used on first launch to
/// unpack the bundled python runtime.
fn extract_zip_to(archive: &Path, dst: &Path) -> Result<(), String> {
    use std::io::{Read, Write};
    let file = fs::File::open(archive)
        .map_err(|e| format!("cannot open {}: {}", archive.display(), e))?;
    let mut zip = zip::ZipArchive::new(file)
        .map_err(|e| format!("cannot read zip {}: {}", archive.display(), e))?;
    fs::create_dir_all(dst).map_err(|e| e.to_string())?;
    for i in 0..zip.len() {
        let mut entry = zip
            .by_index(i)
            .map_err(|e| format!("zip entry {}: {}", i, e))?;
        let out_rel = match entry.enclosed_name() {
            Some(p) => p.to_path_buf(),
            None => continue, // skip unsafe/zip-slip entries
        };
        let out_path = dst.join(out_rel);
        if entry.is_dir() {
            fs::create_dir_all(&out_path).map_err(|e| e.to_string())?;
            continue;
        }
        if let Some(parent) = out_path.parent() {
            fs::create_dir_all(parent).map_err(|e| e.to_string())?;
        }
        let mut out_file =
            fs::File::create(&out_path).map_err(|e| format!("create {}: {}", out_path.display(), e))?;
        let mut buf = [0u8; 64 * 1024];
        loop {
            let n = entry.read(&mut buf).map_err(|e| e.to_string())?;
            if n == 0 {
                break;
            }
            out_file
                .write_all(&buf[..n])
                .map_err(|e| format!("write {}: {}", out_path.display(), e))?;
        }
    }
    Ok(())
}

fn bundled_wheelhouse_dir(app: &AppHandle) -> Option<PathBuf> {
    // Expected (recommended) layout:
    // resources/wheelhouse/<tag>/wheels/*.whl and requirements.lock.txt
    // If you keep only a single folder, this still works.
    let candidates = [
        "resources/wheelhouse",
        "wheelhouse",
        "resources\\wheelhouse",
    ];

    for rel in candidates {
        if let Some(p) = app.path_resolver().resolve_resource(rel) {
            if p.exists() {
                return Some(p);
            }
        }
    }
    None
}

/// Try to locate a lock file inside the wheelhouse
fn find_requirements_lock_in_wheelhouse(wh: &Path) -> Option<PathBuf> {
    // Accept either:
    // - <wheelhouse>/requirements.lock.txt
    // - <wheelhouse>/<tag>/requirements.lock.txt
    let direct = wh.join("requirements.lock.txt");
    if direct.exists() {
        return Some(direct);
    }

    // Search one level deep (fast, avoids expensive recursion)
    if let Ok(rd) = fs::read_dir(wh) {
        for entry in rd.flatten() {
            let p = entry.path();
            if p.is_dir() {
                let cand = p.join("requirements.lock.txt");
                if cand.exists() {
                    return Some(cand);
                }
            }
        }
    }
    None
}

fn copy_dir_all(src: &Path, dst: &Path) -> std::io::Result<()> {
    fs::create_dir_all(dst)?;
    for entry in fs::read_dir(src)? {
        let entry = entry?;
        let ty = entry.file_type()?;
        let from = entry.path();
        let to = dst.join(entry.file_name());
        if ty.is_dir() {
            copy_dir_all(&from, &to)?;
        } else {
            let _ = fs::create_dir_all(to.parent().unwrap_or(dst));
            fs::copy(&from, &to)?;
        }
    }
    Ok(())
}

/// Patch embeddable python *. _pth file so it can:
/// - import site (enables stdlib site behaviors)
/// - include our portable site-packages dir (absolute path) on sys.path
///
/// Without this, embeddable python may ignore env vars and refuse to import installed deps.
///
/// IDEMPOTENCY (added after a Program-Files install hit
/// "Failed to patch embeddable python _pth: Access is denied"):
/// the build pipeline already patches _pth at build time, so on the
/// install machine the file usually already has both required lines.
/// Re-writing the same bytes from a non-elevated process under
/// Program Files fails with EACCES even though no actual change is
/// needed. We now compute the desired content first; if it matches
/// what's on disk byte-for-byte, we skip the write entirely.
///
/// SOFT-FAIL: even when content DOES need updating, a write failure
/// here is non-fatal -- the build-time patch is normally sufficient
/// and any embedded-Python launch we do will still find site-packages
/// via the existing `.\site-packages` line. We log a warning instead
/// of returning an error so the recording / training flow proceeds.
fn patch_embedded_python_pth(py_dir: &Path, site_packages: &Path) -> Result<(), String> {
    // Common: python310._pth (or python311._pth, etc.)
    let mut pth_file: Option<PathBuf> = None;

    if let Ok(rd) = fs::read_dir(py_dir) {
        for e in rd.flatten() {
            let p = e.path();
            if p.is_file() {
                if let Some(name) = p.file_name().and_then(|s| s.to_str()) {
                    if name.starts_with("python") && name.ends_with("._pth") {
                        pth_file = Some(p);
                        break;
                    }
                }
            }
        }
    }

    let Some(pth) = pth_file else {
        // Not present -> nothing to patch
        return Ok(());
    };

    let existing = fs::read_to_string(&pth).unwrap_or_default();
    let mut lines: Vec<String> = existing.lines().map(|s| s.trim_end().to_string()).collect();

    let sp = site_packages.display().to_string();

    // Ensure site-packages is included
    if !lines.iter().any(|l| l.trim() == sp) {
        lines.push(sp);
    }

    // Ensure "import site" is present (must be a single line)
    if !lines.iter().any(|l| l.trim() == "import site") {
        lines.push("import site".to_string());
    }

    let desired = lines.join("\r\n") + "\r\n";

    // Idempotent fast-path: if the on-disk content already matches
    // what we'd write, skip the write entirely. This avoids the
    // EACCES on Program Files installs whose _pth was already
    // correctly patched at build time.
    if existing == desired {
        return Ok(());
    }

    // Soft-fail: write attempt may fail under Program Files for
    // unprivileged processes. The build-time patch is usually
    // sufficient -- log and proceed instead of blocking the user's
    // recording / training flow.
    if let Err(e) = fs::write(&pth, &desired) {
        // We deliberately do NOT return Err -- the caller treats the
        // return value as fatal (see ensure_python_env), and a
        // failure here historically blocked Start Recording entirely.
        eprintln!(
            "[warn] patch_embedded_python_pth: could not write {}: {} \
             (proceeding -- build-time patch is likely already sufficient)",
            pth.display(),
            e
        );
    }
    Ok(())
}

/// Ensure embeddable python is present in LocalAppData and deps are installed into portable site-packages.
/// Returns the python executable to run (base python).
fn ensure_python_env(app: &AppHandle, window: &Window) -> Result<PathBuf, String> {
    let py_root = managed_python_root(app);
    let local_py_dir = managed_embedded_python_dir(app);
    let target_dir = managed_site_packages_dir(app);

    let _ = fs::create_dir_all(&py_root);
    let _ = fs::create_dir_all(&local_py_dir);
    let _ = fs::create_dir_all(&target_dir);

    // Helper: check if site-packages directory is empty (or missing/unreadable -> treat as empty)
    let site_packages_empty = || -> bool {
        fs::read_dir(&target_dir)
            .map(|mut it| it.next().is_none())
            .unwrap_or(true)
    };

    // Helper: resolve python executable path inside local embedded python dir
    let python_exe_path = |dir: &Path| -> PathBuf {
        if is_windows() {
            dir.join("python.exe")
        } else {
            dir.join("bin").join("python3")
        }
    };

    // 0) Detect "stale state":
    // - python.exe exists (so old install looks "present")
    // - but site-packages is empty/corrupt
    // In that case, we MUST recopy bundled python/runtime instead of trying ensurepip.
    let base_py_candidate = python_exe_path(&local_py_dir);
    let needs_repair_recopy = base_py_candidate.exists() && site_packages_empty();

    // 1) Ensure embedded python runtime copied to LocalAppData (install OR repair)
    if !base_py_candidate.exists() || needs_repair_recopy {
        // Prefer the packed archive (python-runtime.zip) - this is what the
        // build pipeline ships. Fall back to an unpacked resources/python dir
        // for dev builds or legacy installers.
        let archive = bundled_python_archive(app);

        if let Some(archive_path) = archive.as_ref() {
            let _ = window.emit(
                "terminal_update",
                format!("[System] Bundled runtime archive: {}", archive_path.display()),
            );

            if needs_repair_recopy {
                let _ = window.emit(
                    "terminal_update",
                    "[System] Detected stale/corrupt install (python exists but site-packages empty) -> repairing by extracting bundled runtime..."
                        .to_string(),
                );
            } else {
                let _ = window.emit(
                    "terminal_update",
                    format!(
                        "[System] Extracting bundled Python runtime -> {}",
                        local_py_dir.display()
                    ),
                );
            }

            // Clean destination first to avoid partial/stale installs
            let _ = fs::remove_dir_all(&local_py_dir);
            fs::create_dir_all(&local_py_dir).map_err(|e| e.to_string())?;

            extract_zip_to(archive_path, &local_py_dir)
                .map_err(|e| format!("Failed to extract bundled python: {}", e))?;
        } else {
            let bundled_dir = bundled_python_dir(app).ok_or_else(|| {
                "Bundled Python runtime not found in installed resources. \
                 Expected either resources/python-runtime.zip (preferred) or resources/python/."
                    .to_string()
            })?;

            let _ = window.emit(
                "terminal_update",
                format!("[System] Bundled Python dir: {}", bundled_dir.display()),
            );

            if needs_repair_recopy {
                let _ = window.emit(
                    "terminal_update",
                    "[System] Detected stale/corrupt install (python exists but site-packages empty) -> repairing by recopying bundled runtime..."
                        .to_string(),
                );
            } else {
                let _ = window.emit(
                    "terminal_update",
                    format!(
                        "[System] Installing bundled Python runtime -> {}",
                        local_py_dir.display()
                    ),
                );
            }

            let _ = fs::remove_dir_all(&local_py_dir);
            fs::create_dir_all(&local_py_dir).map_err(|e| e.to_string())?;

            copy_dir_all(&bundled_dir, &local_py_dir)
                .map_err(|e| format!("Failed to copy bundled python: {}", e))?;
        }

        // IMPORTANT: ensure target_dir exists (may be inside or outside the bundle)
        let _ = fs::create_dir_all(&target_dir);
    }

    // Re-check after copy
    let base_py = python_exe_path(&local_py_dir);
    if !base_py.exists() {
        return Err(format!(
            "Bundled Python runtime missing executable after copy: {}",
            base_py.display()
        ));
    }

    // Inject sitecustomize.py into the bundled site-packages.
    //
    // Embedded Python (with a _pth file present) runs in *isolated mode*:
    //  - the script's own directory is NOT auto-prepended to sys.path
    //  - PYTHONPATH is IGNORED, even with `import site` enabled in _pth
    //
    // That second behaviour bites us specifically: `run_python_script`
    // adds the script's parent dir to PYTHONPATH (`vdir`) so scripts can
    // import siblings — but the embedded interpreter discards it, and
    // `1-collect_data.py` dies on `from grabscreen import grab_screen`
    // (grabscreen.py is a sibling, not a package install).
    //
    // What we CAN rely on: `import site` is in the patched _pth, so
    // site.py runs at startup and looks for `sitecustomize` on sys.path.
    // The bundled site-packages IS on sys.path (via `.\site-packages`
    // in _pth), so dropping a sitecustomize.py here makes Python pick
    // it up automatically. Inside it we read the `BOT_VERSION_DIR` env
    // var (which `run_python_script` already exports) and prepend it
    // to sys.path. Now sibling imports work without touching any of
    // the 50+ scripts in versions/0.01/.
    //
    // For the sidecar (start_sidecar_server) BOT_VERSION_DIR is unset,
    // so this is a no-op there. No collision.
    let sitecustomize = target_dir.join("sitecustomize.py");
    let _ = fs::create_dir_all(&target_dir);
    // IMPORTANT: build the file content as a Vec of one-line strings
    // joined by "\n" so leading whitespace inside the body of the `if`
    // is preserved verbatim. A previous version of this code used a
    // single Rust string literal with `\` line continuations -- which
    // collapsed every "\n\<spaces>" sequence into just "\n", silently
    // dedenting the `sys.path.insert(...)` line and making Python
    // reject sitecustomize.py with:
    //   IndentationError: expected an indented block after 'if' statement
    // When sitecustomize.py fails to load, BOT_VERSION_DIR is never
    // injected and `from grabscreen import grab_screen` (the very bug
    // this file exists to prevent) returns. Per-line strings avoid
    // the whitespace-mangling pitfall entirely.
    let sitecustomize_lines: &[&str] = &[
        "# Auto-injected by main.rs#ensure_python_env. Re-enables sibling-",
        "# module imports for scripts launched via run_python_script under",
        "# embedded Python's _pth-isolated mode (where PYTHONPATH is ignored).",
        "import os, sys",
        "_vdir = os.environ.get('BOT_VERSION_DIR', '').strip()",
        "if _vdir and os.path.isdir(_vdir) and _vdir not in sys.path:",
        "    sys.path.insert(0, _vdir)",
        "",
    ];
    let _ = fs::write(&sitecustomize, sitecustomize_lines.join("\n"));

    // 2) Patch _pth to include our portable site-packages (always do this)
    patch_embedded_python_pth(&local_py_dir, &target_dir).map_err(|e| {
        format!(
            "Failed to patch embeddable python _pth ({}): {}",
            local_py_dir.display(),
            e
        )
    })?;

    let _ = window.emit(
        "terminal_update",
        format!(
            "[System] Using portable site-packages: {}",
            target_dir.display()
        ),
    );

    // 3) If our portable site-packages looks empty, install deps from bundled wheelhouse (offline)
    //    CRITICAL FIX: Do NOT call ensurepip (missing in embeddable python). We only proceed if we have a wheelhouse.
    if site_packages_empty() {
        let _ = window.emit(
            "terminal_update",
            "[System] site-packages empty -> installing bundled dependencies (offline wheelhouse)".to_string(),
        );

        let wh = bundled_wheelhouse_dir(app);

        if let Some(wh_dir) = wh.as_ref() {
            let _ = window.emit(
                "terminal_update",
                format!("[System] Wheelhouse root: {}", wh_dir.display()),
            );
        } else {
            let _ = window.emit(
                "terminal_update",
                "[System] No wheelhouse found in resources. Cannot install deps. Reinstall app or bundle site-packages."
                    .to_string(),
            );
            return Ok(base_py);
        }

        let wh_dir = wh.unwrap();
        let lock = find_requirements_lock_in_wheelhouse(&wh_dir).ok_or_else(|| {
            format!(
                "Wheelhouse found but requirements.lock.txt not found under: {}",
                wh_dir.display()
            )
        })?;

        // Determine which folder contains wheels (either wh_dir itself or <tag>/wheels)
        // We'll pass --find-links to BOTH:
        // - <wheelhouse>/wheels
        // - <wheelhouse>/<tag>/wheels (if present)
        let mut find_links: Vec<PathBuf> = vec![];
        let direct_wheels = wh_dir.join("wheels");
        if direct_wheels.exists() {
            find_links.push(direct_wheels);
        }
        if let Some(tag_dir) = lock.parent() {
            let tag_wheels = tag_dir.join("wheels");
            if tag_wheels.exists() {
                find_links.push(tag_wheels);
            }
        }
        if find_links.is_empty() {
            // fallback: allow wh_dir itself (pip can still find wheels if stored flat)
            find_links.push(wh_dir.clone());
        }

        // Install from lock file into --target, offline
        {
            let mut cmd = Command::new(&base_py);
            apply_stable_python_env(&mut cmd);

            cmd.arg("-m")
                .arg("pip")
                .arg("install")
                .arg("--no-index");

            for fl in &find_links {
                cmd.arg("--find-links").arg(fl);
            }

            cmd.arg("--target").arg(&target_dir);

            // Install exactly what's locked
            cmd.arg("-r").arg(&lock);

            let _ = window.emit(
                "terminal_update",
                format!(
                    "[System] Installing offline deps into --target from lock: {}",
                    lock.display()
                ),
            );

            let out = cmd
                .output()
                .map_err(|e| format!("pip install (offline) failed to start: {}", e))?;

            if !out.stdout.is_empty() {
                let _ = window.emit(
                    "terminal_update",
                    format!("[System] pip stdout: {}", String::from_utf8_lossy(&out.stdout)),
                );
            }
            if !out.stderr.is_empty() {
                let _ = window.emit(
                    "terminal_update",
                    format!("[System] pip stderr: {}", String::from_utf8_lossy(&out.stderr)),
                );
            }
            if !out.status.success() {
                return Err(format!(
                    "pip install --target failed (exit={}).\n\
                     This build must bundle pip (or a pip launcher) AND a complete wheelhouse for your platform.\n\
                     Ensure wheelhouse contains all required wheels for your Python + OS.\n\
                     stderr={}",
                    out.status,
                    String::from_utf8_lossy(&out.stderr)
                ));
            }
        }

        // OPTIONAL: install your project wheel from wheelhouse (if you ship it)
        // NOTE: Your original code forgot to actually pass the package argument to pip.
        // If your lock already includes bot-mmorpg-ai, you can delete this whole block.
        {
            let mut cmd = Command::new(&base_py);
            apply_stable_python_env(&mut cmd);

            cmd.arg("-m")
                .arg("pip")
                .arg("install")
                .arg("--no-index");

            for fl in &find_links {
                cmd.arg("--find-links").arg(fl);
            }

            cmd.arg("--target").arg(&target_dir);

            let pkg = if PROD_EXTRAS.trim().is_empty() {
                "bot-mmorpg-ai".to_string()
            } else {
                format!("bot-mmorpg-ai[{}]", PROD_EXTRAS)
            };

            // FIX: actually install the package
            cmd.arg(&pkg);

            let _ = window.emit(
                "terminal_update",
                format!("[System] Installing app package (if wheel present): {}", pkg),
            );

            let out = cmd
                .output()
                .map_err(|e| format!("pip install bot package failed to start: {}", e))?;

            // If it fails, don't hard-fail because lock install may already have installed it.
            if !out.status.success() {
                let _ = window.emit(
                    "terminal_update",
                    format!(
                        "[System] Note: bot-mmorpg-ai wheel install step failed (may be OK if already installed by lock). stderr={}",
                        String::from_utf8_lossy(&out.stderr)
                    ),
                );
            }
        }

        // Verify minimal import
        {
            let out = Command::new(&base_py)
                .arg("-c")
                .arg("import numpy; print('numpy_ok')")
                .output()
                .map_err(|e| format!("verify failed to start: {}", e))?;

            if !out.status.success() {
                return Err(format!(
                    "Deps installed but verification failed. stderr={}",
                    String::from_utf8_lossy(&out.stderr)
                ));
            }
        }

        let _ = window.emit(
            "terminal_update",
            "[System] Python deps installed (portable target)".to_string(),
        );
    }

    Ok(base_py)
}

/// Writable runtime directory (datasets/models/logs) — uses installation directory (Program Files).
fn work_dir(app: &AppHandle) -> PathBuf {
    let p = ensure_runtime_layout(app);
    let _ = fs::create_dir_all(&p);
    p
}

/// Resolve scripts in production in this order:
///  1) Bundled resource (canonical install layout):
///                            <install_dir>\resources\versions\<ver>\<script>
///  2) User-copied override:  <install_dir>\versions\<ver>\<script>
///                            (matches what users in issues #26/#37/#42 do manually)
///  3) Content override:      <install_dir>\content\versions\<ver>\<script>
///  4) Tauri resolver:        resolve_resource("resources/versions/<ver>/<script>")
///  5) Legacy staging:        <install_dir>\_up_\versions\<ver>\<script>
///
/// In debug, fallback to repo tree: <repo>/versions/<ver>/<script>
fn resolve_script(app: &AppHandle, script_name: &str) -> Result<PathBuf, String> {
    if !cfg!(debug_assertions) {
        let root = ensure_runtime_layout(app);
        let mut tried: Vec<String> = Vec::new();

        // 1) Bundled (canonical): $INSTDIR\resources\versions\<ver>\<script>.
        // This is where the NSIS installer actually puts the files because
        // tauri.conf.json's `resources/**` glob preserves the `resources/`
        // prefix on extraction. Probed first so a clean install just works.
        let bundled = root
            .join("resources")
            .join("versions")
            .join(DEFAULT_VERSION)
            .join(script_name);
        tried.push(bundled.display().to_string());
        if bundled.exists() {
            return Ok(bundled);
        }

        // 2) User-copied: <install_dir>\versions\<ver>\<script>
        // This is exactly the path users in issues #26/#37/#42 copied files to.
        let user_candidate = root
            .join("versions")
            .join(DEFAULT_VERSION)
            .join(script_name);
        tried.push(user_candidate.display().to_string());
        if user_candidate.exists() {
            return Ok(user_candidate);
        }

        // 3) Content override (writable) in installation directory
        let content_candidate = root
            .join("content")
            .join("versions")
            .join(DEFAULT_VERSION)
            .join(script_name);
        tried.push(content_candidate.display().to_string());
        if content_candidate.exists() {
            return Ok(content_candidate);
        }

        // 4) Tauri resolver fallback (covers any non-standard install layout)
        let rel = format!("resources/versions/{}/{}", DEFAULT_VERSION, script_name);
        if let Some(p) = app.path_resolver().resolve_resource(&rel) {
            tried.push(p.display().to_string());
            if p.exists() {
                return Ok(p);
            }
        } else {
            tried.push(format!("<bundled> {}", rel));
        }

        // 5) Legacy staging (install dir)
        let legacy_up = root
            .join("_up_")
            .join("versions")
            .join(DEFAULT_VERSION)
            .join(script_name);
        tried.push(legacy_up.display().to_string());
        if legacy_up.exists() {
            return Ok(legacy_up);
        }

        return Err(format!(
            "Script '{}' not found. The installer is missing bundled versions/. \
             Workaround: copy the script into '{}'. Tried: [{}]",
            script_name,
            root.join("versions").join(DEFAULT_VERSION).display(),
            tried.join(" | ")
        ));
    }

    // DEV: repo tree
    let candidate = dev_repo_root()
        .join("versions")
        .join(DEFAULT_VERSION)
        .join(script_name);

    if candidate.exists() {
        Ok(candidate)
    } else {
        Err(format!("Script not found (dev): {}", candidate.display()))
    }
}

// ---------------------------
// SIDE-CAR STARTUP
// ---------------------------
fn parse_ready_line(line: &str) -> Option<SidecarApi> {
    let line = line.trim();
    if !line.starts_with("READY ") {
        return None;
    }
    let mut url: Option<String> = None;
    let mut token: Option<String> = None;
    for part in line.split_whitespace() {
        if let Some(v) = part.strip_prefix("url=") {
            url = Some(v.to_string());
        } else if let Some(v) = part.strip_prefix("token=") {
            token = Some(v.to_string());
        }
    }
    match (url, token) {
        (Some(base_url), Some(token)) => Some(SidecarApi { base_url, token }),
        _ => None,
    }
}

/// return both SidecarApi and the spawned Child handle
fn start_sidecar_server(app: &AppHandle) -> Result<(SidecarApi, Child), String> {
    let token = {
        let pid = std::process::id();
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_nanos();
        format!("tkn-{}-{}", pid, now)
    };

    // Writable data directory - use installation directory (Program Files\BOT-MMORPG-AI)
    let data_root = local_data_root(app);
    let _ = fs::create_dir_all(&data_root);

    // Read-only resources directory
    let resource_root = app
        .path_resolver()
        .resource_dir()
        .unwrap_or_else(|| std::env::current_dir().unwrap_or_else(|_| PathBuf::from(".")));

    let mut cmd = if cfg!(debug_assertions) {
        let py = find_python_for_app(app)?;

        let script = dev_repo_root().join("modelhub").join("tauri.py");
        if !script.exists() {
            return Err(format!(
                "Sidecar entrypoint not found in dev (expected {} )",
                script.display()
            ));
        }

        if let Some(w) = app.get_window("main") {
            let _ = w.emit::<String>(
                "terminal_update",
                format!("[System] Sidecar Python: {}", py.display()),
            );
            let _ = w.emit::<String>(
                "terminal_update",
                format!("[System] Sidecar Script: {}", script.display()),
            );
        }

        let mut c = Command::new(&py);
        apply_dev_venv_env(&mut c, &dev_repo_root());
        apply_stable_python_env(&mut c);
        c.arg(script);
        c
    } else {
        // PRODUCTION: Use embedded Python directly (no PyInstaller needed)
        // This reduces installer size by ~500MB and simplifies the architecture

        // Get window for progress updates
        let window = app
            .get_window("main")
            .ok_or_else(|| "Main window not available for sidecar setup".to_string())?;

        let py = ensure_python_env(app, &window)?;

        // Resolve the backend entry script from bundled resources.
        // The NSIS bundler places resources at $INSTDIR\resources\... (the
        // `resources/**` glob in tauri.conf.json preserves that prefix), so
        // resolve_resource() must be called with the matching path. A bare
        // "backend/entry_main.py" silently resolves to $INSTDIR\backend\...
        // which doesn't exist and makes the sidecar fail to launch.
        let backend_script = app
            .path_resolver()
            .resolve_resource("resources/backend/entry_main.py")
            .filter(|p| p.exists())
            .or_else(|| {
                let direct = local_data_root(app)
                    .join("resources")
                    .join("backend")
                    .join("entry_main.py");
                if direct.exists() { Some(direct) } else { None }
            })
            .ok_or_else(|| {
                "Bundled backend script not found: resources/backend/entry_main.py".to_string()
            })?;

        let _ = window.emit::<String>(
            "terminal_update",
            format!("[System] Sidecar Python: {}", py.display()),
        );
        let _ = window.emit::<String>(
            "terminal_update",
            format!("[System] Sidecar Script: {}", backend_script.display()),
        );

        let mut c = Command::new(&py);
        apply_stable_python_env(&mut c);

        // Set PYTHONPATH to include backend modules
        let sep = if is_windows() { ";" } else { ":" };
        let mut pypaths: Vec<String> = vec![];

        // Add the backend directory to Python path
        if let Some(backend_dir) = backend_script.parent() {
            pypaths.push(backend_dir.display().to_string());
        }

        // Add modelhub directory (sibling to backend under resources/).
        // Same prefix rule as the backend script above.
        let modelhub_dir = app
            .path_resolver()
            .resolve_resource("resources/modelhub")
            .filter(|p| p.exists())
            .unwrap_or_else(|| local_data_root(app).join("resources").join("modelhub"));
        if modelhub_dir.exists() {
            pypaths.push(modelhub_dir.display().to_string());
        }

        // Add site-packages from embedded Python
        let site_pkgs = managed_site_packages_dir(app);
        if site_pkgs.exists() {
            pypaths.push(site_pkgs.display().to_string());
        }

        // Add resource root for imports
        pypaths.push(resource_root.display().to_string());

        let old_pypath = std::env::var("PYTHONPATH").unwrap_or_default();
        if !old_pypath.is_empty() {
            pypaths.push(old_pypath);
        }

        c.env("PYTHONPATH", pypaths.join(sep));
        c.arg("-u"); // Unbuffered output for real-time logs
        c.arg(&backend_script);
        c
    };

    cmd.args([
        "--port",
        "0",
        "--token",
        &token,
        "--resource-root",
        &resource_root.to_string_lossy(),
        "--data-root",
        &data_root.to_string_lossy(),
    ]);

    cmd.env("MODELHUB_RESOURCE_ROOT", &resource_root);
    cmd.env("MODELHUB_DATA_ROOT", &data_root);
    cmd.current_dir(&data_root);

    cmd.stdout(Stdio::piped());
    cmd.stderr(Stdio::piped());

    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x08000000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }

    let mut child = cmd
        .spawn()
        .map_err(|e| format!("Failed to start sidecar: {e}"))?;

    let stdout = child
        .stdout
        .take()
        .ok_or_else(|| "Sidecar stdout unavailable".to_string())?;
    let stderr = child
        .stderr
        .take()
        .ok_or_else(|| "Sidecar stderr unavailable".to_string())?;

    let (tx, rx) = std::sync::mpsc::channel::<Result<SidecarApi, String>>();

    let tx_out = tx.clone();
    thread::spawn(move || {
        let reader = BufReader::new(stdout);
        for line in reader.lines().flatten() {
            if let Some(api) = parse_ready_line(&line) {
                let _ = tx_out.send(Ok(api));
                return;
            }
        }
        let _ = tx_out.send(Err("Sidecar exited without READY line (stdout)".to_string()));
    });

    let app_handle = app.clone();
    let tx_err = tx.clone();
    thread::spawn(move || {
        let reader = BufReader::new(stderr);
        for line in reader.lines().flatten() {
            if let Some(w) = app_handle.get_window("main") {
                let _ = w.emit::<String>("terminal_update", format!("[Sidecar stderr] {}", line));
            }
            if line.starts_with("FAILED ") {
                let _ = tx_err.send(Err(format!("Sidecar failed: {}", line)));
                return;
            }
        }
    });

    match rx.recv_timeout(Duration::from_secs(25)) {
        Ok(Ok(api)) => Ok((api, child)),
        Ok(Err(e)) => {
            let _ = child.kill();
            let _ = child.wait(); // reap the zombie
            Err(e)
        }
        Err(_) => {
            let _ = child.kill();
            let _ = child.wait(); // reap the zombie
            Err("Timed out waiting for sidecar READY line".to_string())
        }
    }
}

// ---------------------------
// HTTP HELPERS
// ---------------------------
/// Wait up to ~30 seconds for the sidecar to become ready, polling every 500ms.
///
/// Why 30s and not 5s: the bundled Python sidecar imports fastapi +
/// uvicorn + numpy + torch + cv2 before printing READY. On a cold
/// disk cache (first launch after install, AV real-time scan, slow
/// HDD), that easily exceeds 5 seconds. The previous 5s timeout
/// made `make build-installer` -> install -> launch fire a
/// FALSE-POSITIVE "Backend installation is incomplete" banner on
/// every first run. AAA launchers (Steam, Battle.net, Riot Client)
/// all wait 20-60s for backend services to come up before declaring
/// failure -- we follow that convention.
///
/// Polling stays at 500ms so a fast-starting sidecar (warm cache)
/// still feels instant -- we just don't give up early.
const SIDECAR_READY_TIMEOUT_SECS: u64 = 30;
const SIDECAR_READY_POLL_MS: u64 = 500;

async fn wait_for_sidecar(inner: &Arc<AppStateInner>) -> Result<SidecarApi, String> {
    let total_attempts = (SIDECAR_READY_TIMEOUT_SECS * 1000 / SIDECAR_READY_POLL_MS) as usize;
    for attempt in 0..total_attempts {
        {
            let guard = inner.sidecar.lock().unwrap();
            if let Some(ref api) = *guard {
                return Ok(api.clone());
            }
        }
        if attempt + 1 < total_attempts {
            tokio::time::sleep(std::time::Duration::from_millis(SIDECAR_READY_POLL_MS)).await;
        }
    }
    Err(format!(
        "Sidecar API not ready after {} s. Likely cause: the installer is missing \
         resources/python, resources/backend, or resources/modelhub, OR the embedded \
         Python crashed on import (check the terminal log for [Fatal] Sidecar failed: \
         ... -- issues #26, #37, #42).",
        SIDECAR_READY_TIMEOUT_SECS
    ))
}

/// Default timeout on every sidecar HTTP call so a hung Python backend
/// cannot freeze the UI indefinitely.
const SIDECAR_HTTP_TIMEOUT: Duration = Duration::from_secs(30);

async fn api_get_with(inner: &Arc<AppStateInner>, path: &str) -> Result<Value, String> {
    let api = wait_for_sidecar(inner).await?;
    let url = format!("{}{}", api.base_url, path);

    let res = inner
        .http
        .get(url)
        .header("X-Auth-Token", api.token)
        .timeout(SIDECAR_HTTP_TIMEOUT)
        .send()
        .await
        .map_err(|e| e.to_string())?;

    let status = res.status();
    let body = res.json::<Value>().await.map_err(|e| e.to_string())?;

    if !status.is_success() {
        return Err(body.to_string());
    }
    Ok(body)
}

async fn api_post_with(
    inner: &Arc<AppStateInner>,
    path: &str,
    payload: Value,
) -> Result<Value, String> {
    let api = wait_for_sidecar(inner).await?;
    let url = format!("{}{}", api.base_url, path);

    let res = inner
        .http
        .post(url)
        .header("X-Auth-Token", api.token)
        .timeout(SIDECAR_HTTP_TIMEOUT)
        .json(&payload)
        .send()
        .await
        .map_err(|e| e.to_string())?;

    let status = res.status();
    let body = res.json::<Value>().await.map_err(|e| e.to_string())?;

    if !status.is_success() {
        return Err(body.to_string());
    }
    Ok(body)
}

// ---------------------------
// PROCESS MANAGEMENT
// ---------------------------
fn ensure_monitor_thread(app: AppHandle, window: Window, inner: Arc<AppStateInner>) {
    thread::spawn(move || loop {
        thread::sleep(Duration::from_millis(250));

        let mut maybe_exit_code: Option<i32> = None;
        {
            let mut guard = inner.current_process.lock().unwrap();
            if let Some(child) = guard.as_mut() {
                match child.try_wait() {
                    Ok(Some(status)) => {
                        maybe_exit_code = status.code();
                        let _ = guard.take();
                    }
                    Ok(None) => {}
                    Err(_) => {
                        let _ = guard.take();
                    }
                }
            }
        }

        if let Some(code) = maybe_exit_code {
            let inner2 = inner.clone();
            let window2 = window.clone();
            tauri::async_runtime::spawn(async move {
                let _ = api_post_with(&inner2, "/session/finalize", json!({})).await;
                let _ = window2.emit("process_finished", format!("exit_code={}", code));
            });
        }

        let _ = app;
    });
}

fn stop_process_inner(window: &Window, inner: &Arc<AppStateInner>) -> String {
    let mut guard = inner.current_process.lock().unwrap();
    if let Some(mut child) = guard.take() {
        let _ = window.emit("terminal_update", format!("[System] Stopping PID {}", child.id()));
        let _ = child.kill();
        return "Process stopped".to_string();
    }
    "No process running".to_string()
}

fn stop_sidecar_inner(window: Option<&Window>, inner: &Arc<AppStateInner>) {
    let mut guard = inner.sidecar_process.lock().unwrap();
    if let Some(mut child) = guard.take() {
        if let Some(w) = window {
            let _ = w.emit(
                "terminal_update",
                format!("[System] Stopping sidecar PID {}", child.id()),
            );
        }
        let _ = child.kill();
    }
}

fn shutdown_all(app: &AppHandle, window: Option<&Window>) {
    if let Some(state) = app.try_state::<AppState>() {
        // Stop user scripts
        {
            let mut guard = state.inner.current_process.lock().unwrap();
            if let Some(mut child) = guard.take() {
                if let Some(w) = window {
                    let _ = w.emit("terminal_update", format!("[System] Stopping PID {}", child.id()));
                }
                let _ = child.kill();
            }
        }

        // Stop sidecar
        stop_sidecar_inner(window, &state.inner);
    }
}

fn run_python_script(
    app: AppHandle,
    script_name: &str,
    extra_args: &[&str],
    window: Window,
    inner: Arc<AppStateInner>,
) -> Result<String, String> {
    let script_path = resolve_script(&app, script_name)?;
    let data_root = work_dir(&app);

    // DEV: system/repo python
    // PROD: ensure embedded python + portable deps
    let py = if cfg!(debug_assertions) {
        find_python_for_app(&app)?
    } else {
        ensure_python_env(&app, &window)?
    };

    let _ = window.emit("terminal_update", format!("[System] Python: {}", py.display()));
    let _ = window.emit("terminal_update", format!("[System] Script: {}", script_path.display()));
    let _ = window.emit("terminal_update", format!("[System] WorkDir: {}", data_root.display()));

    let _ = stop_process_inner(&window, &inner);

    let mut cmd = Command::new(&py);
    apply_stable_python_env(&mut cmd);

    // Use -u for unbuffered output so UI gets logs immediately
    cmd.arg("-u").arg(&script_path);
    // Forward script-specific args (e.g. "--model <path>" for 3-test_model.py).
    for a in extra_args {
        cmd.arg(a);
    }

    // Build PYTHONPATH:
    //  - script directory (versions/<ver>)
    //  - PROD portable site-packages
    //  - existing PYTHONPATH
    let sep = if is_windows() { ";" } else { ":" };
    let mut pypaths: Vec<String> = vec![];

    if let Some(vdir) = script_path.parent() {
        let _ = window.emit("terminal_update", format!("[System] VersionDir: {}", vdir.display()));
        pypaths.push(vdir.display().to_string());
        cmd.env("BOT_VERSION_DIR", vdir);
    }

    if !cfg!(debug_assertions) {
        let sp = managed_site_packages_dir(&app);
        pypaths.push(sp.display().to_string());
    }

    let old = std::env::var("PYTHONPATH").unwrap_or_default();
    if !old.is_empty() {
        pypaths.push(old);
    }

    cmd.env("PYTHONPATH", pypaths.join(sep));
    cmd.current_dir(&data_root);

    if cfg!(debug_assertions) {
        apply_dev_venv_env(&mut cmd, &dev_repo_root());
    }

    // AI settings
    let provider = {
        let p = get_env_var(&app, "AI_PROVIDER");
        if p.is_empty() { "gemini".to_string() } else { p }
    };
    cmd.env("AI_PROVIDER", provider);
    cmd.env("GEMINI_API_KEY", get_env_var(&app, "GEMINI_API_KEY"));
    cmd.env("OPENAI_API_KEY", get_env_var(&app, "OPENAI_API_KEY"));

    cmd.env("MODELHUB_DATA_ROOT", &data_root);

    cmd.stdout(Stdio::piped());
    cmd.stderr(Stdio::piped());

    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x08000000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }

    match cmd.spawn() {
        Ok(mut child) => {
            let stdout = child.stdout.take().unwrap();
            let stderr = child.stderr.take().unwrap();

            *inner.current_process.lock().unwrap() = Some(child);

            let w1 = window.clone();
            thread::spawn(move || {
                let reader = BufReader::new(stdout);
                for line in reader.lines().flatten() {
                    let _ = w1.emit("terminal_update", line);
                }
            });

            // Stderr reader is also our traceback observer for the AI
            // debug-loop. We keep emitting every line as before (no UI
            // change), but maintain a small state machine that detects
            // Python tracebacks and records them in the in-memory error
            // buffer for the `recent_errors_for_ai` Tauri command.
            let w2 = window.clone();
            let inner_for_tb = inner.clone();
            let script_for_tb = script_path.display().to_string();
            thread::spawn(move || {
                let reader = BufReader::new(stderr);
                let mut in_tb = false;
                let mut tb_buf = String::new();
                for line in reader.lines().flatten() {
                    let _ = w2.emit("terminal_update", format!("(stderr) {}", line));

                    if line.trim_start().starts_with("Traceback (most recent call last):") {
                        in_tb = true;
                        tb_buf.clear();
                    }
                    if in_tb {
                        tb_buf.push_str(&line);
                        tb_buf.push('\n');
                        // A non-indented line in the form "Type: message"
                        // where Type starts uppercase is the error
                        // terminator (e.g. "ModuleNotFoundError: ...").
                        let raw = line.trim_end();
                        let is_indented = raw.starts_with(' ') || raw.starts_with('\t');
                        if !is_indented && !raw.is_empty() {
                            if let Some((etype, _)) = raw.split_once(": ") {
                                if etype
                                    .chars()
                                    .next()
                                    .map_or(false, |c| c.is_ascii_uppercase())
                                {
                                    let entry = parse_python_traceback(&tb_buf, &script_for_tb);
                                    record_error(&inner_for_tb, entry);
                                    in_tb = false;
                                    tb_buf.clear();
                                }
                            }
                        }
                    }
                }
                // Stream ended mid-traceback (process killed?). Capture
                // whatever we have so the user still sees something.
                if in_tb && !tb_buf.is_empty() {
                    let entry = parse_python_traceback(&tb_buf, &script_for_tb);
                    record_error(&inner_for_tb, entry);
                }
            });

            ensure_monitor_thread(app, window, inner);
            Ok(format!("Started {}", script_name))
        }
        Err(e) => {
            let msg = format!("Failed to spawn python: {}", e);
            let _ = window.emit("terminal_update", msg.clone());
            Err(msg)
        }
    }
}

// ---------------------------
// AI CHAT
// ---------------------------
fn get_provider(app: &AppHandle) -> String {
    let p = get_env_var(app, "AI_PROVIDER");
    let p = p.trim().to_lowercase();
    if p.is_empty() {
        "gemini".to_string()
    } else {
        p
    }
}

fn normalize_provider(p: &str) -> String {
    match p.trim().to_lowercase().as_str() {
        "openai" => "openai".to_string(),
        _ => "gemini".to_string(),
    }
}

#[tauri::command]
async fn ai_chat(
    app: AppHandle,
    state: tauri::State<'_, AppState>,
    message: String,
) -> Result<String, String> {
    let provider = normalize_provider(&get_provider(&app));
    let user_msg = message.trim().to_string();
    if user_msg.is_empty() {
        return Err("Message is empty.".to_string());
    }

    if provider == "openai" {
        let key = get_env_var(&app, "OPENAI_API_KEY");
        if key.trim().is_empty() {
            return Err("OPENAI_API_KEY is empty. Open Settings and save your key.".to_string());
        }

        let body = json!({
            "model": "gpt-4o-mini",
            "messages": [
                { "role": "system", "content": "You are a helpful assistant. Reply concisely." },
                { "role": "user", "content": user_msg }
            ],
            "temperature": 0.7
        });

        let res = state
            .inner
            .http
            .post("https://api.openai.com/v1/chat/completions")
            .bearer_auth(key.trim())
            .timeout(Duration::from_secs(60))
            .json(&body)
            .send()
            .await
            .map_err(|e| e.to_string())?;

        let status = res.status();
        let v: Value = res.json().await.map_err(|e| e.to_string())?;

        if !status.is_success() {
            return Err(v.to_string());
        }

        let text = v["choices"][0]["message"]["content"]
            .as_str()
            .unwrap_or("")
            .to_string();

        if text.trim().is_empty() {
            return Err("OpenAI returned an empty response.".to_string());
        }
        return Ok(text);
    }

    // Default: Gemini
    let key = get_env_var(&app, "GEMINI_API_KEY");
    if key.trim().is_empty() {
        return Err("GEMINI_API_KEY is empty. Open Settings and save your key.".to_string());
    }

    let url = format!(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={}",
        key.trim()
    );

    let body = json!({
        "contents": [{
            "role": "user",
            "parts": [{ "text": user_msg }]
        }]
    });

    let res = state
        .inner
        .http
        .post(url)
        .timeout(Duration::from_secs(60))
        .json(&body)
        .send()
        .await
        .map_err(|e| e.to_string())?;

    let status = res.status();
    let v: Value = res.json().await.map_err(|e| e.to_string())?;

    if !status.is_success() {
        return Err(v.to_string());
    }

    let text = v["candidates"][0]["content"]["parts"][0]["text"]
        .as_str()
        .unwrap_or("")
        .to_string();

    if text.trim().is_empty() {
        return Err("Gemini returned an empty response.".to_string());
    }

    Ok(text)
}

// ---------------------------
// TAURI COMMANDS
// ---------------------------
#[tauri::command]
fn get_ai_config(app: AppHandle) -> AiConfig {
    AiConfig {
        provider: get_env_var(&app, "AI_PROVIDER"),
        gemini_key: get_env_var(&app, "GEMINI_API_KEY"),
        openai_key: get_env_var(&app, "OPENAI_API_KEY"),
    }
}

#[tauri::command]
fn save_configuration(app: AppHandle, provider: String, api_key: Option<String>) -> Result<bool, String> {
    let provider = provider.trim().to_lowercase();
    let api_key = api_key.unwrap_or_default().trim().to_string();

    update_env_file(&app, "AI_PROVIDER", &provider)?;

    if api_key.is_empty() {
        return Ok(true);
    }

    match provider.as_str() {
        "gemini" => update_env_file(&app, "GEMINI_API_KEY", &api_key)?,
        "openai" => update_env_file(&app, "OPENAI_API_KEY", &api_key)?,
        _ => return Err(format!("Unknown provider: {}", provider)),
    }

    Ok(true)
}

#[tauri::command]
async fn start_recording(
    state: tauri::State<'_, AppState>,
    app: AppHandle,
    window: Window,
    game_id: Option<String>,
    dataset_name: Option<String>,
    capture_mouse: Option<bool>,
) -> Result<String, String> {
    let gid = normalize_game_id(game_id);
    let name = dataset_name.unwrap_or_else(|| "Untitled".to_string());
    let cap_mouse = capture_mouse.unwrap_or(false);
    let inner = state.inner.clone();

    // Sidecar bookkeeping is best-effort. If the sidecar is offline, the
    // Python script that does the actual recording still runs fine -- only
    // the SessionManager's dataset registration is skipped. Phrased so the
    // user doesn't think their recording is broken when it isn't.
    if let Err(_e) = api_post_with(
        &inner,
        "/session/begin_recording",
        json!({"game_id": gid, "dataset_name": name, "capture_mouse": cap_mouse}),
    )
    .await
    {
        let _ = window.emit(
            "terminal_update",
            "[Sidecar] Session metadata not recorded (sidecar offline). Recording will still start."
                .to_string(),
        );
    }

    // Pass mouse capture preference as env var for the Python script
    if cap_mouse {
        std::env::set_var("BOTMMO_CAPTURE_MOUSE", "true");
    } else {
        std::env::set_var("BOTMMO_CAPTURE_MOUSE", "false");
    }

    run_python_script(app, "1-collect_data.py", &[], window, inner)
}

#[tauri::command]
async fn start_training(
    state: tauri::State<'_, AppState>,
    app: AppHandle,
    window: Window,
    game_id: Option<String>,
    model_name: Option<String>,
    dataset_id: Option<String>,
    arch: Option<String>,
) -> Result<String, String> {
    let gid = normalize_game_id(game_id);
    let mname = model_name.unwrap_or_else(|| "New Model".to_string());
    let did = dataset_id.unwrap_or_default();
    let a = arch.unwrap_or_else(|| "custom".to_string());
    let inner = state.inner.clone();

    // Same fail-soft pattern as start_recording.
    if let Err(_e) = api_post_with(
        &inner,
        "/session/begin_training",
        json!({"game_id": gid, "model_name": mname, "dataset_id": did, "arch": a}),
    )
    .await
    {
        let _ = window.emit(
            "terminal_update",
            "[Sidecar] Session metadata not recorded (sidecar offline). Training will still start."
                .to_string(),
        );
    }

    run_python_script(app, "2-train_model.py", &[], window, inner)
}

// Inference. 3-test_model.py declares `--model` as a REQUIRED arg
// (versions/0.01/3-test_model.py:502), so spawning it without one
// previously failed silently with "argument --model is required".
//
// We resolve the active model from the running sidecar's
// /modelhub/catalog endpoint, which already returns an `active`
// field maintained by `mh_set_active_model` in
// modelhub/registry_store.py. If the user hasn't picked a model, we
// return a clear error instead of spawning a doomed subprocess --
// the frontend renders this back as a toast / log message.
#[tauri::command]
async fn start_bot(
    state: tauri::State<'_, AppState>,
    app: AppHandle,
    window: Window,
    game_id: Option<String>,
) -> Result<String, String> {
    let gid = normalize_game_id(game_id);
    let inner = state.inner.clone();

    let catalog = api_get_with(
        &inner,
        &format!("/modelhub/catalog?game_id={}", urlencoding::encode(&gid)),
    )
    .await
    .map_err(|e| {
        format!(
            "Cannot determine active model: backend sidecar is unreachable ({}). \
             Open Settings -> System Tools -> Run Diagnosis to inspect, or restart the app.",
            e
        )
    })?;

    let model_path = catalog
        .get("active")
        .and_then(|v| if v.is_null() { None } else { Some(v) })
        .and_then(|v| v.get("model_dir"))
        .and_then(|m| m.as_str())
        .map(|s| s.to_string())
        .ok_or_else(|| {
            format!(
                "No active model set for '{}'. Open ModelHub, pick a trained model, \
                 click 'Set Active', then start the bot.",
                gid
            )
        })?;

    run_python_script(
        app,
        "3-test_model.py",
        &["--model", &model_path],
        window,
        inner,
    )
}

#[tauri::command]
async fn stop_process(state: tauri::State<'_, AppState>, window: Window) -> Result<String, String> {
    let inner = state.inner.clone();
    let msg = stop_process_inner(&window, &inner);

    if let Err(e) = api_post_with(&inner, "/session/finalize", json!({})).await {
        let _ = window.emit("terminal_update", format!("[Warning] finalize failed: {}", e));
    }

    Ok(msg)
}

#[tauri::command]
async fn modelhub_is_available(state: tauri::State<'_, AppState>) -> Result<Value, String> {
    api_get_with(&state.inner, "/modelhub/available").await
}

#[tauri::command]
async fn modelhub_list_games(state: tauri::State<'_, AppState>) -> Result<Value, String> {
    api_get_with(&state.inner, "/modelhub/games").await
}

#[tauri::command]
async fn mh_get_catalog_data(
    state: tauri::State<'_, AppState>,
    game_id: Option<String>,
) -> Result<Value, String> {
    let gid = normalize_game_id(game_id);
    api_get_with(
        &state.inner,
        &format!("/modelhub/catalog?game_id={}", urlencoding::encode(&gid)),
    )
    .await
}

#[tauri::command]
async fn mh_set_active(
    state: tauri::State<'_, AppState>,
    game_id: Option<String>,
    model_id: String,
    path: String,
) -> Result<Value, String> {
    let gid = normalize_game_id(game_id);
    api_post_with(
        &state.inner,
        "/modelhub/active",
        json!({"game_id": gid, "model_id": model_id, "path": path}),
    )
    .await
}

#[tauri::command]
async fn mh_delete_model(
    state: tauri::State<'_, AppState>,
    game_id: Option<String>,
    model_id: String,
    path: String,
) -> Result<Value, String> {
    let gid = normalize_game_id(game_id);
    api_post_with(
        &state.inner,
        "/modelhub/delete",
        json!({"game_id": gid, "model_id": model_id, "path": path}),
    )
    .await
}

#[tauri::command]
async fn modelhub_validate_model(
    state: tauri::State<'_, AppState>,
    game_id: Option<String>,
    model_dir: String,
) -> Result<Value, String> {
    let gid = normalize_game_id(game_id);
    api_post_with(
        &state.inner,
        "/modelhub/validate",
        json!({"game_id": gid, "model_dir": model_dir}),
    )
    .await
}

#[tauri::command]
async fn modelhub_run_offline_evaluation(
    state: tauri::State<'_, AppState>,
    model_dir: String,
    dataset_dir: String,
) -> Result<Value, String> {
    api_post_with(
        &state.inner,
        "/modelhub/offline-eval",
        json!({"model_dir": model_dir, "dataset_dir": dataset_dir}),
    )
    .await
}

// ---------------------------
// MISSING COMMANDS the UI invokes
// ---------------------------
// Audit (this branch): tauri-ui/main.js was calling list_monitors,
// get_screen_preview, generate_dataset_name, list_datasets, delete_dataset
// without those handlers ever being registered, so every related UI
// interaction (Teach tab loading, Refresh preview, Auto dataset name,
// Train tab dataset list, Del button) silently failed with
// "command not found" and left the panel empty. Implementations below.

/// Pure-Rust dataset-name generator. Does NOT need the python sidecar to
/// be alive, so the "Auto" button works on a fresh install before the
/// runtime is unpacked. Format: <game>_<task>_<UTCdate>_<UTCtime>.
#[tauri::command]
fn generate_dataset_name(game_id: Option<String>, task: Option<String>) -> String {
    let gid = normalize_game_id(game_id);
    let task = task
        .as_deref()
        .map(str::trim)
        .filter(|s| !s.is_empty())
        .unwrap_or("general")
        .to_lowercase()
        .replace(|c: char| !c.is_ascii_alphanumeric(), "_");
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0);
    // Tiny home-grown UTC formatter (avoids pulling chrono just for this).
    let secs = now % 86_400;
    let days = now / 86_400;
    // 1970-01-01 was Thursday; we just use Unix epoch days since we only
    // need a unique-ish stamp, not a calendar date for humans.
    let h = secs / 3600;
    let m = (secs / 60) % 60;
    let s = secs % 60;
    format!("{}_{}_{:08}_{:02}{:02}{:02}", gid, task, days, h, m, s)
}

/// Lightweight monitor list. We don't pull a display-info crate yet (would
/// add 10+ deps for a single feature); instead return a single entry that
/// covers the primary monitor. Real multi-monitor support is tracked but
/// not blocking. Callers should still render the dropdown with one option
/// rather than fail.
#[derive(Serialize)]
struct MonitorInfo {
    id: u32,
    name: String,
    is_primary: bool,
    width: u32,
    height: u32,
}

#[tauri::command]
fn list_monitors() -> Vec<MonitorInfo> {
    vec![MonitorInfo {
        id: 0,
        name: "Primary".to_string(),
        is_primary: true,
        // 0/0 tells the UI "unknown" — it falls back to a sensible default.
        width: 0,
        height: 0,
    }]
}

/// Forward to the python sidecar's /capture/preview endpoint when the
/// sidecar is available; otherwise return a structured "backend missing"
/// response so the UI can show an actionable message instead of a blank
/// preview pane.
#[tauri::command]
async fn get_screen_preview(
    state: tauri::State<'_, AppState>,
    monitor_id: Option<u32>,
) -> Result<Value, String> {
    let mid = monitor_id.unwrap_or(0);
    match api_post_with(
        &state.inner,
        "/capture/preview",
        json!({ "monitor_id": mid }),
    )
    .await
    {
        Ok(v) => Ok(v),
        // Surface a friendly payload instead of a hard error so the UI's
        // catch block can render "Backend not installed" rather than
        // command-not-found noise.
        Err(e) => Ok(json!({
            "ok": false,
            "error": format!("Screen preview unavailable: {}", e),
            "hint": "Reinstall v0.2.2+ from GitHub releases to get the embedded backend."
        })),
    }
}

/// Forward to the sidecar's dataset listing. Same graceful-error pattern.
#[tauri::command]
async fn list_datasets(
    state: tauri::State<'_, AppState>,
    game_id: Option<String>,
) -> Result<Value, String> {
    let gid = normalize_game_id(game_id);
    match api_get_with(
        &state.inner,
        &format!("/modelhub/datasets?game_id={}", urlencoding::encode(&gid)),
    )
    .await
    {
        Ok(v) => Ok(v),
        Err(e) => Ok(json!({
            "ok": false,
            "datasets": [],
            "error": format!("Dataset list unavailable: {}", e),
            "hint": "Reinstall v0.2.2+ from GitHub releases to get the embedded backend."
        })),
    }
}

/// Delete a dataset via the sidecar.
#[tauri::command]
async fn delete_dataset(
    state: tauri::State<'_, AppState>,
    game_id: Option<String>,
    dataset_id: String,
    path: Option<String>,
) -> Result<Value, String> {
    let gid = normalize_game_id(game_id);
    api_post_with(
        &state.inner,
        "/modelhub/datasets/delete",
        json!({
            "game_id": gid,
            "dataset_id": dataset_id,
            "path": path.unwrap_or_default(),
        }),
    )
    .await
}

// ---------------------------
// INSTALL-HEALTH probe
// ---------------------------
// Returns a structured JSON describing every subsystem the app needs.
// Two consumers today:
//   1. The startup banner (main.js#checkInstallHealth) — only cares about
//      `healthy` and `issues` (plain strings) and the legacy fields.
//   2. The Settings → System Tools → Run Diagnosis panel — reads the
//      richer `checks` array and renders one row per item with a status
//      icon. Each row carries a `severity` so optional features like
//      drivers can show as "warn" without flipping the whole verdict to
//      "error" (AAA-game settings UX: optional features never fail-state
//      the app).
//
// Severity levels:
//   "ok"    — green check; subsystem present and working.
//   "warn"  — yellow; optional or recoverable (e.g. drivers not installed).
//   "error" — red; the app cannot function until this is fixed.
//
// Overall verdict:
//   "ready"   — every check is "ok".
//   "warning" — at least one "warn", no "error".
//   "error"   — at least one "error".

/// True when the given install dir lives under Program Files on Windows.
/// Used by install_health to surface a UX warning (writable scratch
/// dirs require admin elevation under Program Files), and by anything
/// else that wants to recommend relocation. Case-insensitive match
/// because Windows filesystems are case-insensitive by default.
fn _is_under_program_files(p: &Path) -> bool {
    let s = p.display().to_string().replace('\\', "/").to_ascii_lowercase();
    s.starts_with("c:/program files") || s.starts_with("c:/program files (x86)")
}

#[tauri::command]
async fn install_health(
    state: tauri::State<'_, AppState>,
    app: AppHandle,
) -> Result<Value, String> {
    let install_dir = installation_dir();

    let res_root = install_dir.join("resources");

    // --- Per-subsystem probes ---
    let sidecar_ok = state.inner.sidecar.lock().unwrap().is_some();

    let runtime_archive = bundled_python_archive(&app).is_some();
    let runtime_unpacked = bundled_python_dir(&app).is_some();
    let runtime_extracted = managed_embedded_python_dir(&app)
        .join(if is_windows() { "python.exe" } else { "bin/python3" })
        .exists();
    let python_ok = runtime_archive || runtime_unpacked || runtime_extracted;

    // Bundled Python entrypoints — must live under resources/ in the
    // canonical install layout. We accept either the canonical path or
    // a Tauri-resolver hit (covers non-standard installs).
    let backend_entry = res_root.join("backend").join("entry_main.py");
    let backend_ok = backend_entry.exists()
        || app
            .path_resolver()
            .resolve_resource("resources/backend/entry_main.py")
            .map(|p| p.exists())
            .unwrap_or(false);

    let modelhub_entry = res_root.join("modelhub").join("tauri.py");
    let modelhub_ok = modelhub_entry.exists()
        || app
            .path_resolver()
            .resolve_resource("resources/modelhub/tauri.py")
            .map(|p| p.exists())
            .unwrap_or(false);

    let scripts_root = res_root.join("versions").join(DEFAULT_VERSION);
    let bundled_scripts = scripts_root.join("1-collect_data.py").exists()
        && scripts_root.join("2-train_model.py").exists()
        && scripts_root.join("3-test_model.py").exists();
    // User-copy fallback (legacy issues #26/#37/#42 workaround).
    let user_copied_scripts = install_dir
        .join("versions")
        .join(DEFAULT_VERSION)
        .join("1-collect_data.py")
        .exists();
    let scripts_ok = bundled_scripts || user_copied_scripts;

    // Drivers are OPTIONAL — only needed for keyboard/mouse capture
    // (interception) or gamepad simulation (vJoy). Missing → warn, not error.
    let interception_ok = install_dir
        .join("drivers")
        .join("interception")
        .join("install-interception.exe")
        .exists();
    let vjoy_ok = install_dir
        .join("drivers")
        .join("vjoy")
        .join("vJoySetup.exe")
        .exists();

    // Writable logs dir — created by ensure_runtime_layout() on launch,
    // but we double-check here in case Program Files permissions changed.
    let logs_dir = install_dir.join("logs");
    let logs_writable = {
        let _ = fs::create_dir_all(&logs_dir);
        let probe = logs_dir.join(".write_probe");
        let ok = fs::write(&probe, b"ok").is_ok();
        let _ = fs::remove_file(&probe);
        ok
    };

    // --- Build the structured rows ---
    fn row(id: &str, label: &str, severity: &str, message: String) -> Value {
        json!({
            "id": id,
            "label": label,
            "severity": severity,
            "status": match severity { "ok" => "OK", "warn" => "Warning", _ => "Error" },
            "message": message,
        })
    }

    let checks = vec![
        row("install_dir", "Install directory", "ok",
            install_dir.display().to_string()),
        row("sidecar", "Backend sidecar (Python HTTP API)",
            if sidecar_ok { "ok" } else { "error" },
            if sidecar_ok { "Running".into() }
            else { "Not running. Restart the app to retry; if it persists the bundled Python or backend script is missing.".into() }),
        row("python", "Embedded Python runtime",
            if python_ok { "ok" } else { "error" },
            if python_ok { "python-runtime.zip present (or already extracted)".into() }
            else { "resources/runtime/python-runtime.zip missing. Reinstall the latest installer.".into() }),
        row("backend", "Bundled backend script",
            if backend_ok { "ok" } else { "error" },
            if backend_ok { format!("{}", backend_entry.display()) }
            else { "resources/backend/entry_main.py missing. Reinstall.".into() }),
        row("modelhub", "Bundled ModelHub package",
            if modelhub_ok { "ok" } else { "error" },
            if modelhub_ok { format!("{}", modelhub_entry.display()) }
            else { "resources/modelhub/tauri.py missing. Reinstall.".into() }),
        row("scripts", "ML scripts (versions/0.01)",
            if scripts_ok { "ok" } else { "error" },
            if bundled_scripts { format!("{}", scripts_root.display()) }
            else if user_copied_scripts { "Found user-copied fallback".into() }
            else { "1-collect_data.py / 2-train_model.py / 3-test_model.py missing. Reinstall.".into() }),
        row("drivers_interception", "Interception driver (keyboard/mouse capture)",
            if interception_ok { "ok" } else { "warn" },
            if interception_ok { "install-interception.exe present".into() }
            else { "Optional, not installed. Run Settings → Install Drivers if you need keyboard/mouse capture.".into() }),
        row("drivers_vjoy", "vJoy driver (gamepad simulation)",
            if vjoy_ok { "ok" } else { "warn" },
            if vjoy_ok { "vJoySetup.exe present".into() }
            else { "Optional, not installed. Required only for games that need gamepad input.".into() }),
        row("logs_writable", "Logs directory is writable",
            if logs_writable { "ok" } else { "error" },
            if logs_writable { format!("{}", logs_dir.display()) }
            else { format!("Cannot write to {}. Run as administrator or relocate the install.", logs_dir.display()) }),
        // Non-blocking: flag Program Files installs as a UX hazard.
        // Even when logs_writable currently passes (e.g. UAC elevated this
        // session), the install will fail to write logs / datasets / models
        // for unprivileged future launches. Surface as warn so the user
        // can choose to relocate proactively, but do NOT flip the
        // verdict to "error" -- the install still works, it's just
        // brittle on that location.
        row("install_location_privileged", "Install location",
            if _is_under_program_files(&install_dir) { "warn" } else { "ok" },
            if _is_under_program_files(&install_dir) {
                format!(
                    "Installed under Program Files ({}). Writes to logs/datasets/models \
                     require admin elevation; consider relocating to %LOCALAPPDATA% \
                     or another user-writable location to avoid permission errors.",
                    install_dir.display()
                )
            } else {
                format!("{} (user-writable)", install_dir.display())
            }),
    ];

    let any_error = checks.iter().any(|c| c["severity"] == "error");
    let any_warn = checks.iter().any(|c| c["severity"] == "warn");
    let verdict = if any_error { "error" } else if any_warn { "warning" } else { "ready" };

    // Legacy fields preserved so the existing startup banner keeps working.
    let healthy = !any_error;
    let issues: Vec<String> = checks
        .iter()
        .filter(|c| c["severity"] == "error")
        .map(|c| format!("{}: {}", c["label"].as_str().unwrap_or(""), c["message"].as_str().unwrap_or("")))
        .collect();

    Ok(json!({
        // Legacy (banner) fields:
        "healthy": healthy,
        "sidecar_ok": sidecar_ok,
        "python_ok": python_ok,
        "scripts_ok": scripts_ok,
        "issues": issues,
        "install_dir": install_dir.display().to_string(),
        "remediation": if healthy {
            "All systems go.".to_string()
        } else {
            "This install is incomplete. Reinstall the latest installer from \
             https://github.com/ruslanmv/BOT-MMORPG-AI/releases/latest".to_string()
        },
        // New (Diagnosis panel) fields:
        "verdict": verdict,
        "checks": checks,
    }))
}

// ─────────────────────────────────────────────────────────────────────
// AI debug-loop: Rust-side error capture and aggregation.
//
// Pairs with modelhub/diagnostics/ on the sidecar side. The sidecar
// captures FastAPI exceptions; this captures (a) Python tracebacks
// emitted on subprocess stderr and (b) explicit failures in Rust
// code paths. Both feed `recent_errors_for_ai` which builds a
// vendor-neutral Markdown+JSON bundle the user pastes into any AI
// coding assistant or LLM chat with file-read access.
// ─────────────────────────────────────────────────────────────────────

fn now_ms() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(0)
}

/// Append an error to the in-memory ring buffer. Bounded by MAX_ERRORS.
fn record_error(inner: &Arc<AppStateInner>, entry: ErrorEntry) {
    if let Ok(mut buf) = inner.recent_errors.lock() {
        if buf.len() >= MAX_ERRORS {
            buf.pop_front();
        }
        buf.push_back(entry);
    }
}

/// Parse a captured Python traceback into a structured ErrorEntry.
/// Best-effort: extracts the last `File "...", line N` and the final
/// `<ErrorType>: <message>` line. Falls back to opaque values if the
/// shape doesn't match.
fn parse_python_traceback(tb: &str, script_path: &str) -> ErrorEntry {
    let mut error_type = "PythonError".to_string();
    let mut message = String::new();
    let mut primary_file = String::new();
    let mut primary_line: u32 = 0;

    // Find the last "File ..." line so the primary_file is the most-recent frame.
    for line in tb.lines() {
        let l = line.trim_start();
        if l.starts_with("File \"") {
            if let Some(rest) = l.strip_prefix("File \"") {
                if let Some(end_quote) = rest.find('"') {
                    primary_file = rest[..end_quote].to_string();
                    if let Some(after) = rest[end_quote + 1..].strip_prefix(", line ") {
                        let n: String = after.chars().take_while(|c| c.is_ascii_digit()).collect();
                        if let Ok(num) = n.parse::<u32>() {
                            primary_line = num;
                        }
                    }
                }
            }
        }
    }

    // The error class+message is the last non-empty non-indented line that
    // contains ": " or "Error" / "Exception" in the type. Walk backwards.
    for line in tb.lines().rev() {
        let l = line.trim_end();
        if l.is_empty() || l.starts_with(' ') || l.starts_with('\t') {
            continue;
        }
        // Lines like "ModuleNotFoundError: No module named 'grabscreen'"
        if let Some((etype, emsg)) = l.split_once(": ") {
            if etype.chars().next().map_or(false, |c| c.is_ascii_uppercase()) {
                error_type = etype.to_string();
                message = emsg.to_string();
                break;
            }
        }
        // "(stderr) " prefix gets stripped if the caller passed in raw events
        if let Some(stripped) = l.strip_prefix("(stderr) ") {
            if let Some((etype, emsg)) = stripped.split_once(": ") {
                if etype.chars().next().map_or(false, |c| c.is_ascii_uppercase()) {
                    error_type = etype.to_string();
                    message = emsg.to_string();
                    break;
                }
            }
        }
    }

    ErrorEntry {
        timestamp_ms: now_ms(),
        source: "spawned_script".to_string(),
        error_type,
        message,
        primary_file,
        primary_line,
        traceback: tb.to_string(),
        context: json!({ "spawned_script": script_path }),
    }
}

/// Build the Markdown+JSON bundle the UI's "Copy AI Bundle" button
/// writes to the clipboard. Mirrors the Python formatter's shape so a
/// bundle from either layer is structurally identical.
fn build_ai_bundle(
    rust_errors: &[ErrorEntry],
    sidecar_entries: &[Value],
    probe: Option<&Value>,
    app_version: &str,
    install_dir: &str,
) -> String {
    let mut out = String::new();
    out.push_str("# AI Fix Request\n\n");
    out.push_str(&format!("- App version: `{}`\n", app_version));
    out.push_str(&format!("- Install dir: `{}`\n", install_dir));
    out.push_str(&format!(
        "- Error count: {} (Rust: {}, sidecar: {})\n",
        rust_errors.len() + sidecar_entries.len(),
        rust_errors.len(),
        sidecar_entries.len()
    ));
    out.push_str("\n## Errors\n\n");

    let mut idx = 1;
    for e in rust_errors {
        let formatted = json!({
            "task": "fix_runtime_error",
            "summary": format!("{}: {}", e.error_type, e.message),
            "source": e.source,
            "timestamp_ms": e.timestamp_ms,
            "context": e.context,
            "error": {
                "type": e.error_type,
                "message": e.message,
                "primary_file": e.primary_file,
                "primary_line": e.primary_line,
                "traceback": e.traceback,
            },
            "candidate_files": [
                "src-tauri/src/main.rs",
                "docs/installer/04-bug-index.md",
                e.primary_file.clone(),
            ],
            "instructions": [
                "Read each candidate_files path before proposing changes.",
                "Identify the minimal patch that fixes the root cause.",
                "Do NOT rewrite entire files. Edit targeted lines only.",
                "Reference docs/installer/04-bug-index.md for similar prior bugs."
            ]
        });
        out.push_str(&format!(
            "### Error {} — {}: {}\n\n```json\n{}\n```\n\n",
            idx,
            e.error_type,
            e.message,
            serde_json::to_string_pretty(&formatted).unwrap_or_default()
        ));
        idx += 1;
    }
    for e in sidecar_entries {
        out.push_str(&format!(
            "### Error {} — {}\n\n```json\n{}\n```\n\n",
            idx,
            e.get("summary").and_then(|v| v.as_str()).unwrap_or("(sidecar error)"),
            serde_json::to_string_pretty(e).unwrap_or_default()
        ));
        idx += 1;
    }

    if let Some(probe_val) = probe {
        out.push_str(
            "## System probe\n\n\
             _Deep diagnostic capture (system info, disk free, network, \
             embedded-Python health, file integrity, environment, \
             antivirus). Fired automatically when the runtime verdict \
             is non-OK._\n\n",
        );
        out.push_str("```json\n");
        out.push_str(
            &serde_json::to_string_pretty(probe_val).unwrap_or_default(),
        );
        out.push_str("\n```\n\n");
    }

    out.push_str(
        "## Usage\n\n\
        Paste this entire block into your AI coding assistant. It has \
        enough context (error type, primary file + line, traceback, \
        candidate files, system probe) to locate the root cause without \
        follow-up questions. Always review the proposed patch before \
        applying.\n",
    );
    out
}

/// Run a deep system probe via the bundled embedded Python.
///
/// The probe lives in `modelhub.diagnostics.health_probe.deep_probe`
/// and returns a structured dict with: system info, disk free, network
/// reachability, embedded-Python health (importable packages),
/// file-integrity hashes of critical bundled files, filtered env vars,
/// and an antivirus presence hint.
///
/// Two-pathway dispatch:
///   1. If the sidecar is up, fetch /diagnostics/deep_probe over HTTP.
///      Cheap, reuses the running interpreter.
///   2. If the sidecar is dead (the most common case when the user
///      needs a deep probe), spawn the bundled python.exe directly to
///      run the same module. We can't ask a dead sidecar to
///      introspect itself.
///
/// Returns None on total failure; the caller proceeds without the
/// probe field rather than escalating.
async fn fetch_deep_probe(app: &AppHandle, inner: &Arc<AppStateInner>) -> Option<Value> {
    // Path 1: sidecar HTTP. Short timeout so a hung sidecar doesn't
    // block the bundle for long.
    if let Ok(resp) = api_get_with(inner, "/diagnostics/deep_probe").await {
        if let Some(probe) = resp.get("probe") {
            return Some(probe.clone());
        }
    }

    // Path 2: spawn embedded python directly. Same code path that
    // the sidecar would have run, just from Rust.
    let py_exe = managed_embedded_python_dir(app).join(if is_windows() {
        "python.exe"
    } else {
        "bin/python3"
    });
    if !py_exe.exists() {
        return None;
    }

    let install_dir = installation_dir();
    let mut cmd = Command::new(&py_exe);
    apply_stable_python_env(&mut cmd);

    // PYTHONPATH must reach modelhub.diagnostics.health_probe. The
    // bundled modelhub package lives at $INSTDIR\resources\modelhub.
    let sep = if is_windows() { ";" } else { ":" };
    let pypaths = vec![
        install_dir.join("resources").display().to_string(),
        managed_site_packages_dir(app).display().to_string(),
    ];
    cmd.env("PYTHONPATH", pypaths.join(sep));
    cmd.env(
        "MODELHUB_DATA_ROOT",
        install_dir.display().to_string(),
    );
    cmd.env(
        "MODELHUB_RESOURCE_ROOT",
        install_dir.join("resources").display().to_string(),
    );

    cmd.arg("-c").arg(
        "import json, sys; \
         from modelhub.diagnostics.health_probe import deep_probe; \
         sys.stdout.write(json.dumps(deep_probe()))",
    );
    cmd.stdout(Stdio::piped());
    cmd.stderr(Stdio::piped());

    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x08000000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }

    let output = match cmd.output() {
        Ok(o) => o,
        Err(_) => return None,
    };
    if !output.status.success() {
        return None;
    }
    let stdout = String::from_utf8_lossy(&output.stdout);
    serde_json::from_str::<Value>(&stdout).ok()
}

/// Tauri command: returns the AI-ready Markdown bundle. Aggregates
/// Rust-captured errors with sidecar-captured errors (best-effort HTTP
/// call; if sidecar is offline we just ship the Rust portion). Also
/// runs a deep system probe so the bundle has enough context for an
/// AI assistant to diagnose issues that didn't produce a structured
/// error (e.g. sidecar that never started).
#[tauri::command]
async fn recent_errors_for_ai(
    state: tauri::State<'_, AppState>,
    app: AppHandle,
) -> Result<String, String> {
    let inner = state.inner.clone();
    let rust_errors: Vec<ErrorEntry> = inner
        .recent_errors
        .lock()
        .map(|b| b.iter().cloned().collect())
        .unwrap_or_default();

    // Best-effort sidecar fetch. Soft-fails so a dead sidecar doesn't
    // hide Rust-captured errors from the user.
    let sidecar_entries: Vec<Value> = match api_get_with(&inner, "/diagnostics/recent/ai").await {
        Ok(resp) => resp
            .get("entries")
            .and_then(|v| v.as_array())
            .cloned()
            .unwrap_or_default(),
        Err(_) => Vec::new(),
    };

    // Deep probe: fired unconditionally so the bundle is rich even when
    // no errors were captured (e.g. silent sidecar startup failure).
    let probe = fetch_deep_probe(&app, &inner).await;

    let version = app.package_info().version.to_string();
    let install_dir = installation_dir().display().to_string();
    Ok(build_ai_bundle(
        &rust_errors,
        &sidecar_entries,
        probe.as_ref(),
        &version,
        &install_dir,
    ))
}

/// Tauri command: clear the Rust-side ring buffer. Returns the count
/// cleared. The frontend pairs this with a sidecar DELETE to fully
/// reset state after a fix-and-verify cycle.
#[tauri::command]
fn clear_recent_errors(state: tauri::State<AppState>) -> usize {
    state
        .inner
        .recent_errors
        .lock()
        .map(|mut b| {
            let n = b.len();
            b.clear();
            n
        })
        .unwrap_or(0)
}

// Cheap version + channel probe. Used by the sidebar version label
// (so it doesn't have to wait for the GitHub-releases call) and any
// other UI that wants to show "Installed: vX.Y.Z" without coupling
// to install_health's bigger payload. Channel is derived from the
// version string -- "dev"/"alpha"/"nightly" => Dev Build,
// "rc"/"beta" => Pre-release, otherwise Stable.
#[tauri::command]
fn app_info(app: AppHandle) -> Value {
    let version = app.package_info().version.to_string();
    let v = version.to_lowercase();
    let channel = if v.contains("dev") || v.contains("alpha") || v.contains("nightly") {
        "Dev Build"
    } else if v.contains("rc") || v.contains("beta") {
        "Pre-release"
    } else {
        "Stable"
    };
    json!({
        "version": version,
        "channel": channel,
    })
}

// Plain-text bundle the user can paste into a GitHub issue / Discord.
// Aggregates: app version, OS, install paths, the structured health
// check results, and the active game. No log content here -- the
// frontend has direct access to the in-app terminal buffer and will
// append it client-side before copying.
#[tauri::command]
async fn support_report(
    state: tauri::State<'_, AppState>,
    app: AppHandle,
) -> Result<String, String> {
    // Clone the AppStateInner Arc BEFORE handing `state` to install_health
    // -- install_health consumes its state argument, but we still need
    // the inner reference afterward to drive fetch_deep_probe.
    let inner = state.inner.clone();
    let h = install_health(state, app.clone()).await?;

    let install_dir = installation_dir();
    let exe_path = std::env::current_exe()
        .map(|p| p.display().to_string())
        .unwrap_or_else(|_| "<unknown>".to_string());
    let version = app.package_info().version.to_string();
    let os = std::env::consts::OS;
    let arch = std::env::consts::ARCH;
    let verdict = h["verdict"].as_str().unwrap_or("?").to_string();

    let mut out = String::new();
    out.push_str("# BOT-MMORPG-AI Support Report\n\n");
    out.push_str(&format!("- App version: {}\n", version));
    out.push_str(&format!("- OS / arch: {} / {}\n", os, arch));
    out.push_str(&format!("- Install dir: {}\n", install_dir.display()));
    out.push_str(&format!("- Executable: {}\n", exe_path));
    out.push_str(&format!("- Verdict: {}\n\n", verdict));

    out.push_str("## Subsystem checks\n\n");
    if let Some(checks) = h["checks"].as_array() {
        for c in checks {
            let sym = match c["severity"].as_str().unwrap_or("") {
                "ok" => "[OK]",
                "warn" => "[WARN]",
                _ => "[FAIL]",
            };
            out.push_str(&format!(
                "- {} {}: {}\n",
                sym,
                c["label"].as_str().unwrap_or(""),
                c["message"].as_str().unwrap_or(""),
            ));
        }
    }

    // Deep probe -- only when the verdict is non-OK. On a healthy
    // install we omit it to keep the bundle small; the user is most
    // likely reporting a real issue when verdict != "ready".
    if verdict != "ready" {
        if let Some(probe) = fetch_deep_probe(&app, &inner).await {
            out.push_str("\n## System probe\n\n");
            out.push_str(
                "_Deep diagnostic capture (system info, disk free, network, \
                 embedded-Python health, file integrity, environment, \
                 antivirus). Fired automatically when verdict is non-OK._\n\n",
            );
            out.push_str("```json\n");
            out.push_str(
                &serde_json::to_string_pretty(&probe).unwrap_or_default(),
            );
            out.push_str("\n```\n");
        }
    }

    Ok(out)
}

// GitHub-releases-based update check. Called by the frontend on startup
// after install_health resolves; renders an "Update Available" card if
// a newer release is published. Uses the Rust-side reqwest client we
// already depend on for the modelhub HTTP plumbing -- no new HTTP
// allowlist needed in tauri.conf.json (which would have been a
// security-meaningful change).
//
// Version comparison is real semver via the `semver` crate -- string
// compares would do the wrong thing on prerelease tags like
// "0.2.1-rc.1" < "0.2.1" or pre-1.0 versions like "0.10.0" vs "0.2.0".
#[tauri::command]
async fn check_for_update(app: AppHandle) -> Result<Value, String> {
    let current_str = app.package_info().version.to_string();

    // GitHub Releases API. We could use /releases/latest, but that
    // skips prereleases; /releases?per_page=1 picks up nightlies too.
    // We default to the stable feed for users; switching to prerelease
    // is a user setting we don't expose yet.
    let url = "https://api.github.com/repos/ruslanmv/BOT-MMORPG-AI/releases/latest";

    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(8))
        .build()
        .map_err(|e| format!("http client: {}", e))?;

    let resp = match client
        .get(url)
        // GitHub requires a User-Agent on every API request.
        .header("User-Agent", format!("BOT-MMORPG-AI/{}", current_str))
        .header("Accept", "application/vnd.github+json")
        .send()
        .await
    {
        Ok(r) => r,
        // Don't propagate offline / DNS errors as a hard error -- the
        // frontend treats this as "no update info" rather than alerting.
        Err(e) => {
            return Ok(json!({
                "ok": false,
                "reason": format!("network: {}", e),
                "current_version": current_str,
            }));
        }
    };

    if !resp.status().is_success() {
        return Ok(json!({
            "ok": false,
            "reason": format!("http {}", resp.status().as_u16()),
            "current_version": current_str,
        }));
    }

    let release: Value = resp.json().await.map_err(|e| e.to_string())?;
    let tag = release["tag_name"].as_str().unwrap_or("");
    let latest_str = tag.trim_start_matches('v').to_string();
    let body = release["body"].as_str().unwrap_or("").to_string();
    let html_url = release["html_url"].as_str().unwrap_or("").to_string();
    let published = release["published_at"].as_str().unwrap_or("").to_string();

    // Parse both versions; if either fails, fall back to "no update"
    // rather than alarming the user with a cosmetic comparison failure.
    let update_available = match (
        semver::Version::parse(&current_str),
        semver::Version::parse(&latest_str),
    ) {
        (Ok(cur), Ok(lat)) => lat > cur,
        _ => false,
    };

    Ok(json!({
        "ok": true,
        "update_available": update_available,
        "current_version": current_str,
        "latest_version": latest_str,
        "release_notes": body,
        "release_url": html_url,
        "published_at": published,
    }))
}

#[tauri::command]
fn install_drivers(app: tauri::AppHandle) -> Value {
    #[cfg(target_os = "windows")]
    {
        let resource_path = app
            .path_resolver()
            .resolve_resource("resources/scripts/install_drivers.ps1");

        let script = match resource_path {
            Some(p) => p,
            None => return json!({"ok": false, "error": "Could not find install_drivers.ps1"}),
        };

        // Use -Wait so we know when the elevated process finishes,
        // and -Verb RunAs to request administrator privileges via UAC.
        let ps = format!(
            "Start-Process PowerShell -Verb RunAs -Wait -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"{}\"'",
            script.display()
        );

        let out = Command::new("powershell")
            .args(["-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", &ps])
            .output();

        match out {
            Ok(o) => {
                let stderr = String::from_utf8_lossy(&o.stderr);
                if o.status.success() {
                    json!({ "ok": true, "code": o.status.code() })
                } else {
                    json!({
                        "ok": false,
                        "code": o.status.code(),
                        "error": if stderr.is_empty() {
                            "User may have declined the UAC elevation prompt".to_string()
                        } else {
                            stderr.to_string()
                        }
                    })
                }
            }
            Err(e) => json!({ "ok": false, "error": e.to_string() }),
        }
    }
    #[cfg(not(target_os = "windows"))]
    {
        json!({"ok": false, "error": "Drivers are Windows-only"})
    }
}

// ---------------------------
// MAIN
// ---------------------------
fn main() {
    tauri::Builder::default()
        .manage(AppState {
            inner: Arc::new(AppStateInner {
                current_process: Mutex::new(None),
                sidecar_process: Mutex::new(None),
                sidecar: Mutex::new(None),
                http: Client::new(),
                recent_errors: Mutex::new(std::collections::VecDeque::with_capacity(MAX_ERRORS)),
            }),
        })
        .on_window_event(|event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event.event() {
                let app_handle = event.window().app_handle();
                shutdown_all(&app_handle, Some(event.window()));
            }
        })
        .setup(|app| {
            let app_handle = app.handle();
            let state = app.state::<AppState>();

            match start_sidecar_server(&app_handle) {
                Ok((api, child)) => {
                    *state.inner.sidecar.lock().unwrap() = Some(api);
                    *state.inner.sidecar_process.lock().unwrap() = Some(child);

                    if let Some(w) = app.get_window("main") {
                        let _ = w.emit::<String>(
                            "terminal_update",
                            "[System] Sidecar READY".to_string(),
                        );
                    }
                }
                Err(e) => {
                    if let Some(w) = app.get_window("main") {
                        let _ = w.emit::<String>(
                            "terminal_update",
                            format!("[Fatal] Sidecar failed: {}", e),
                        );
                        let _ = w.emit::<String>(
                            "terminal_update",
                            "[Hint] The installer is missing required resources. Required layout under the install dir:".to_string(),
                        );
                        let _ = w.emit::<String>(
                            "terminal_update",
                            "  resources/python/python.exe         (embedded Python 3.10)".to_string(),
                        );
                        let _ = w.emit::<String>(
                            "terminal_update",
                            "  resources/python/site-packages/...  (fastapi, uvicorn, torch, numpy)".to_string(),
                        );
                        let _ = w.emit::<String>(
                            "terminal_update",
                            "  resources/backend/entry_main.py     (sidecar entry)".to_string(),
                        );
                        let _ = w.emit::<String>(
                            "terminal_update",
                            "  resources/modelhub/tauri.py          (HTTP API)".to_string(),
                        );
                        let _ = w.emit::<String>(
                            "terminal_update",
                            "  resources/versions/0.01/*.py         (ML scripts)".to_string(),
                        );
                        let _ = w.emit::<String>(
                            "terminal_update",
                            "[Action] Re-run scripts/build_pipeline.ps1 to produce a complete installer, or download the latest GitHub release.".to_string(),
                        );
                    }
                }
            }

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            get_ai_config,
            save_configuration,
            ai_chat,
            start_recording,
            start_training,
            start_bot,
            stop_process,
            modelhub_is_available,
            modelhub_list_games,
            mh_get_catalog_data,
            mh_set_active,
            mh_delete_model,
            modelhub_validate_model,
            modelhub_run_offline_evaluation,
            install_drivers,
            // Previously missing handlers the UI was already invoking
            // (every Teach-tab interaction silently failed without these):
            generate_dataset_name,
            list_monitors,
            get_screen_preview,
            list_datasets,
            delete_dataset,
            install_health,
            support_report,
            check_for_update,
            app_info,
            recent_errors_for_ai,
            clear_recent_errors,
        ])
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(|app_handle, event| {
            if let tauri::RunEvent::ExitRequested { .. } = event {
                shutdown_all(&app_handle, None);
            }
        });
}

// ---------------------------
// UNIT TESTS
// ---------------------------
#[cfg(test)]
mod tests {
    use super::*;

    // --- normalize_game_id ---

    #[test]
    fn test_normalize_game_id_with_valid_id() {
        let result = normalize_game_id(Some("world_of_warcraft".to_string()));
        assert_eq!(result, "world_of_warcraft");
    }

    #[test]
    fn test_normalize_game_id_with_none() {
        let result = normalize_game_id(None);
        assert_eq!(result, DEFAULT_GAME_ID);
    }

    #[test]
    fn test_normalize_game_id_with_empty_string() {
        let result = normalize_game_id(Some("".to_string()));
        assert_eq!(result, DEFAULT_GAME_ID);
    }

    #[test]
    fn test_normalize_game_id_trims_whitespace() {
        let result = normalize_game_id(Some("  genshin_impact  ".to_string()));
        assert_eq!(result, "genshin_impact");
    }

    #[test]
    fn test_normalize_game_id_whitespace_only() {
        let result = normalize_game_id(Some("   ".to_string()));
        assert_eq!(result, DEFAULT_GAME_ID);
    }

    // --- parse_ready_line ---

    #[test]
    fn test_parse_ready_line_valid() {
        let line = "READY url=http://127.0.0.1:8080 token=tkn-123-456";
        let result = parse_ready_line(line);
        assert!(result.is_some());
        let api = result.unwrap();
        assert_eq!(api.base_url, "http://127.0.0.1:8080");
        assert_eq!(api.token, "tkn-123-456");
    }

    #[test]
    fn test_parse_ready_line_not_ready() {
        let line = "Starting sidecar...";
        assert!(parse_ready_line(line).is_none());
    }

    #[test]
    fn test_parse_ready_line_partial() {
        let line = "READY url=http://127.0.0.1:8080";
        // Missing token
        assert!(parse_ready_line(line).is_none());
    }

    #[test]
    fn test_parse_ready_line_empty() {
        assert!(parse_ready_line("").is_none());
    }

    #[test]
    fn test_parse_ready_line_with_whitespace() {
        let line = "  READY url=http://127.0.0.1:9090 token=abc  ";
        let result = parse_ready_line(line);
        assert!(result.is_some());
        let api = result.unwrap();
        assert_eq!(api.base_url, "http://127.0.0.1:9090");
        assert_eq!(api.token, "abc");
    }

    // --- is_windows / path_sep ---

    #[test]
    fn test_path_sep_returns_valid_separator() {
        let sep = path_sep();
        assert!(sep == ";" || sep == ":");
    }

    // --- normalize_provider ---

    #[test]
    fn test_normalize_provider_openai() {
        assert_eq!(normalize_provider("openai"), "openai");
        assert_eq!(normalize_provider("OpenAI"), "openai");
        assert_eq!(normalize_provider("  openai  "), "openai");
    }

    #[test]
    fn test_normalize_provider_gemini() {
        assert_eq!(normalize_provider("gemini"), "gemini");
        assert_eq!(normalize_provider("Gemini"), "gemini");
        assert_eq!(normalize_provider("anything_else"), "gemini");
        assert_eq!(normalize_provider(""), "gemini");
    }

    // --- Constants ---

    #[test]
    fn test_default_game_id_is_set() {
        assert!(!DEFAULT_GAME_ID.is_empty());
        assert_eq!(DEFAULT_GAME_ID, "genshin_impact");
    }

    #[test]
    fn test_default_version_is_set() {
        assert!(!DEFAULT_VERSION.is_empty());
        assert_eq!(DEFAULT_VERSION, "0.01");
    }

    #[test]
    fn test_prod_extras_does_not_include_ml() {
        // ML deps are installed on-demand, not at initial setup
        assert!(!PROD_EXTRAS.contains("ml"));
        assert!(PROD_EXTRAS.contains("launcher"));
        assert!(PROD_EXTRAS.contains("backend"));
    }

    // --- SidecarApi ---

    #[test]
    fn test_sidecar_api_clone() {
        let api = SidecarApi {
            base_url: "http://localhost:8080".to_string(),
            token: "test-token".to_string(),
        };
        let cloned = api.clone();
        assert_eq!(cloned.base_url, "http://localhost:8080");
        assert_eq!(cloned.token, "test-token");
    }

    // --- AiConfig serialization ---

    #[test]
    fn test_ai_config_serialization() {
        let config = AiConfig {
            provider: "gemini".to_string(),
            gemini_key: "key123".to_string(),
            openai_key: "".to_string(),
        };
        let json = serde_json::to_string(&config).unwrap();
        assert!(json.contains("gemini"));
        assert!(json.contains("key123"));
    }

    #[test]
    fn test_ai_config_deserialization() {
        let json = r#"{"provider":"openai","gemini_key":"","openai_key":"sk-123"}"#;
        let config: AiConfig = serde_json::from_str(json).unwrap();
        assert_eq!(config.provider, "openai");
        assert_eq!(config.openai_key, "sk-123");
    }

    // --- AppState construction ---

    #[test]
    fn test_app_state_construction() {
        let state = AppState {
            inner: Arc::new(AppStateInner {
                current_process: Mutex::new(None),
                sidecar_process: Mutex::new(None),
                sidecar: Mutex::new(None),
                http: Client::new(),
                recent_errors: Mutex::new(std::collections::VecDeque::with_capacity(MAX_ERRORS)),
            }),
        };
        assert!(state.inner.current_process.lock().unwrap().is_none());
        assert!(state.inner.sidecar_process.lock().unwrap().is_none());
        assert!(state.inner.sidecar.lock().unwrap().is_none());
    }

    // --- Dev helpers ---

    #[test]
    fn test_dev_repo_root_returns_path() {
        let root = dev_repo_root();
        // Should return a valid path (may not exist in CI)
        assert!(!root.to_string_lossy().is_empty());
    }

    #[test]
    fn test_venv_python_path_format() {
        let root = Path::new("/some/project");
        let py = venv_python_from_root(root);
        let py_str = py.to_string_lossy();

        if is_windows() {
            assert!(py_str.contains("Scripts"));
            assert!(py_str.ends_with("python.exe"));
        } else {
            assert!(py_str.contains("bin"));
            assert!(py_str.ends_with("python3"));
        }
    }

    #[test]
    fn test_venv_bin_path_format() {
        let root = Path::new("/some/project");
        let bin = venv_bin_from_root(root);
        let bin_str = bin.to_string_lossy();

        if is_windows() {
            assert!(bin_str.contains("Scripts"));
        } else {
            assert!(bin_str.contains("bin"));
        }
    }

    // --- Installation directory ---

    #[test]
    fn test_installation_dir_returns_valid_path() {
        let dir = installation_dir();
        assert!(!dir.to_string_lossy().is_empty());
    }
}
