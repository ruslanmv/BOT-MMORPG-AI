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

struct AppStateInner {
    current_process: Mutex<Option<Child>>,
    sidecar_process: Mutex<Option<Child>>,
    sidecar: Mutex<Option<SidecarApi>>,
    http: Client,
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

/// Where we install python packages in PROD (portable, no venv)
fn managed_site_packages_dir(app: &AppHandle) -> PathBuf {
    managed_python_root(app).join("site-packages")
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
fn bundled_python_archive(app: &AppHandle) -> Option<PathBuf> {
    let candidates = [
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
        let p = rd.join("python-runtime.zip");
        if p.exists() {
            return Some(p);
        }
        let p2 = rd.join("resources").join("python-runtime.zip");
        if p2.exists() {
            return Some(p2);
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

    let mut lines: Vec<String> = fs::read_to_string(&pth)
        .unwrap_or_default()
        .lines()
        .map(|s| s.trim_end().to_string())
        .collect();

    let sp = site_packages.display().to_string();

    // Ensure site-packages is included
    if !lines.iter().any(|l| l.trim() == sp) {
        lines.push(sp);
    }

    // Ensure "import site" is present (must be a single line)
    if !lines.iter().any(|l| l.trim() == "import site") {
        lines.push("import site".to_string());
    }

    fs::write(&pth, lines.join("\r\n") + "\r\n").map_err(|e| e.to_string())?;
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
///  1) User-copied override:  <install_dir>\versions\<ver>\<script>
///                            (matches what users in issues #26/#37/#42 do manually)
///  2) Content override:      <install_dir>\content\versions\<ver>\<script>
///  3) Bundled resource:      resolve_resource("versions/<ver>/<script>")
///  4) Legacy staging:        <install_dir>\_up_\versions\<ver>\<script>
///
/// In debug, fallback to repo tree: <repo>/versions/<ver>/<script>
fn resolve_script(app: &AppHandle, script_name: &str) -> Result<PathBuf, String> {
    if !cfg!(debug_assertions) {
        let root = ensure_runtime_layout(app);
        let mut tried: Vec<String> = Vec::new();

        // 1) User-copied: <install_dir>\versions\<ver>\<script>
        // This is exactly the path users in issues #26/#37/#42 copied files to.
        let user_candidate = root
            .join("versions")
            .join(DEFAULT_VERSION)
            .join(script_name);
        tried.push(user_candidate.display().to_string());
        if user_candidate.exists() {
            return Ok(user_candidate);
        }

        // 2) Content override (writable) in installation directory
        let content_candidate = root
            .join("content")
            .join("versions")
            .join(DEFAULT_VERSION)
            .join(script_name);
        tried.push(content_candidate.display().to_string());
        if content_candidate.exists() {
            return Ok(content_candidate);
        }

        // 3) Bundled versions (from resources staged by build_pipeline Step 6.5)
        let rel = format!("versions/{}/{}", DEFAULT_VERSION, script_name);
        if let Some(p) = app.path_resolver().resolve_resource(&rel) {
            tried.push(p.display().to_string());
            if p.exists() {
                return Ok(p);
            }
        } else {
            tried.push(format!("<bundled> {}", rel));
        }

        // 4) Legacy staging (install dir)
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

        // Resolve the backend entry script from bundled resources
        let backend_script = app
            .path_resolver()
            .resolve_resource("backend/entry_main.py")
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

        // Add modelhub directory (sibling to backend)
        if let Some(p) = app.path_resolver().resolve_resource("modelhub") {
            if p.exists() {
                pypaths.push(p.display().to_string());
            }
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
/// Wait up to ~5 seconds for the sidecar to become ready, polling every 500ms.
async fn wait_for_sidecar(inner: &Arc<AppStateInner>) -> Result<SidecarApi, String> {
    for attempt in 0..10 {
        {
            let guard = inner.sidecar.lock().unwrap();
            if let Some(ref api) = *guard {
                return Ok(api.clone());
            }
        }
        if attempt < 9 {
            tokio::time::sleep(std::time::Duration::from_millis(500)).await;
        }
    }
    Err(
        "Sidecar API not ready after 5 s. Likely cause: the installer is missing \
         resources/python, resources/backend, or resources/modelhub. See the terminal \
         log for [Fatal] Sidecar failed: ... (issues #26, #37, #42)."
            .to_string(),
    )
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

            let w2 = window.clone();
            thread::spawn(move || {
                let reader = BufReader::new(stderr);
                for line in reader.lines().flatten() {
                    let _ = w2.emit("terminal_update", format!("(stderr) {}", line));
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

    if let Err(e) = api_post_with(
        &inner,
        "/session/begin_recording",
        json!({"game_id": gid, "dataset_name": name, "capture_mouse": cap_mouse}),
    )
    .await
    {
        let _ = window.emit("terminal_update", format!("[Warning] begin_recording failed: {}", e));
    }

    // Pass mouse capture preference as env var for the Python script
    if cap_mouse {
        std::env::set_var("BOTMMO_CAPTURE_MOUSE", "true");
    } else {
        std::env::set_var("BOTMMO_CAPTURE_MOUSE", "false");
    }

    run_python_script(app, "1-collect_data.py", window, inner)
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

    if let Err(e) = api_post_with(
        &inner,
        "/session/begin_training",
        json!({"game_id": gid, "model_name": mname, "dataset_id": did, "arch": a}),
    )
    .await
    {
        let _ = window.emit("terminal_update", format!("[Warning] begin_training failed: {}", e));
    }

    run_python_script(app, "2-train_model.py", window, inner)
}

#[tauri::command]
fn start_bot(app: AppHandle, window: Window, state: tauri::State<AppState>) -> Result<String, String> {
    run_python_script(app, "3-test_model.py", window, state.inner.clone())
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
            install_drivers
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
