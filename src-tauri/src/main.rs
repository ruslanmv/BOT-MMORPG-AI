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
    /// MVP-3c: ID of the currently-running sidecar-owned job
    /// (POSTed via /jobs). When Some, stop_process forwards
    /// DELETE /jobs/{id} instead of (or in addition to) killing
    /// the local Child. Cleared by the log-bridge worker when the
    /// job reaches a terminal status.
    current_sidecar_job: Mutex<Option<String>>,
    /// Set to true when start_sidecar_server returned Err on launch.
    /// `wait_for_sidecar` reads this to fail-fast: when the slot is
    /// None AND startup is known-failed, no point polling another
    /// 65 seconds for a process that's never coming. Without this
    /// every subsequent api_post / api_get blocks the UI for the
    /// full timeout budget.
    sidecar_startup_failed: std::sync::atomic::AtomicBool,
    /// Ring buffer of `terminal_update` lines emitted BEFORE the
    /// WebView's JS finished registering a `listen("terminal_update")`
    /// handler. Tauri 1.x's event bus has no buffering for late
    /// listeners, so the most informative startup lines (the
    /// `[Sidecar stderr]` traceback, `[Sidecar] still warming up...`
    /// heartbeats, `[Fatal]`/`[Hint]` blocks) used to vanish without
    /// reaching the user. `emit_with_buffer` pushes here in addition
    /// to emitting; `drain_early_log` returns + clears the buffer
    /// when the JS attaches its listener.
    early_log: Mutex<std::collections::VecDeque<String>>,
    /// Snapshot of the most recent sidecar spawn attempt. Populated
    /// by `start_sidecar_server` so the debug bundle / launch-report
    /// command can report exactly what was launched, what came back
    /// on stdout + stderr, the exit code, and the post-spawn /health
    /// result. Replaced (not appended) on every restart_sidecar.
    last_launch_report: Mutex<Option<SidecarLaunchReport>>,
}

/// Cap on `early_log` retention. Sized to comfortably cover one
/// 60s sidecar warm-up: ~12 heartbeats + an unbounded Python
/// traceback. 500 lines ~= 50 KB, negligible vs. AppState as a
/// whole. Older lines are dropped FIFO so a runaway stderr can't
/// pin RAM.
const EARLY_LOG_CAP: usize = 500;

/// Cap on stdout/stderr capture inside `SidecarLaunchReport`. 200
/// lines covers a full Python traceback plus context; bigger means
/// we'd be retaining payload-on-payload (every spawn re-allocates).
const LAUNCH_LOG_CAP: usize = 200;

/// Snapshot of a single sidecar spawn attempt -- what was launched,
/// how it ran, and what came back. Built incrementally during
/// `start_sidecar_server` and exposed via `get_sidecar_launch_report`
/// + folded into the AI / debug bundle so a user reporting
/// "sidecar failed" never has to copy-paste 8 separate things.
///
/// The rule that motivates this: never report a sidecar failure
/// without attaching the launch command, env, stdout, stderr, exit
/// code, and health-probe result. Otherwise diagnosis becomes a
/// guessing game.
#[derive(Clone, serde::Serialize, Default)]
struct SidecarLaunchReport {
    /// "starting" | "ok" | "failed"
    status: String,
    /// Quoted argv joined with spaces, suitable for paste-to-shell.
    command: String,
    /// Working directory the child was spawned in.
    cwd: String,
    /// Filtered (key, value) pairs. We drop anything that isn't
    /// either set by us (BOT_, MODELHUB_, BOTMMO_, PYTHONPATH, etc.)
    /// or a small allow-list of harmless system vars (LOCALAPPDATA,
    /// USERPROFILE, TEMP, OS, NUMBER_OF_PROCESSORS). PATH is
    /// included but truncated to the first 4 entries because full
    /// PATH dumps are noisy and may contain unrelated tools.
    env_filtered: Vec<(String, String)>,
    /// Child PID after spawn (None until `Command::spawn` returns).
    pid: Option<u32>,
    /// READY budget for this spawn (60 or 120 seconds).
    timeout_secs: u64,
    /// Unix-millis when we called `cmd.spawn()`.
    started_at_ms: u64,
    /// Unix-millis when we either parsed READY (status=ok) or
    /// returned Err (status=failed).
    finished_at_ms: Option<u64>,
    /// Exit code if the child died before READY. Tauri-side
    /// timeouts kill the child and report None for exit_code.
    exit_code: Option<i32>,
    /// Wrapped Err string from start_sidecar_server.
    error_string: Option<String>,
    /// Up to LAUNCH_LOG_CAP raw stdout lines, FIFO eviction.
    stdout_lines: Vec<String>,
    /// Up to LAUNCH_LOG_CAP raw stderr lines, FIFO eviction.
    stderr_lines: Vec<String>,
    /// Result of GET /health AFTER the spawn settled. Populated
    /// only when status=ok. e.g. "200 OK", "Connection refused",
    /// "Timed out after 2s".
    health_probe_result: Option<String>,
    /// Body of the health-probe response when present (parsed as
    /// text; sidecar always returns JSON but we keep it generic).
    health_probe_body: Option<String>,
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

    // PROD: %LOCALAPPDATA%\com.bot.mmorpg.ai\.env (user-writable)
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

/// Architecture allow-list. Mirrors MODEL_REGISTRY in
/// src/bot_mmorpg/scripts/models_pytorch.py (the single source of truth
/// -- 2-train_model.py forwards to it via get_model()). Adding a new
/// model class? Add it to the backend registry first, then here.
///
/// Also mirrors DEFAULT_ARCHITECTURES in tauri-ui/main.js, which the UI
/// uses as its fallback catalog. `custom` is a synthetic value the UI
/// never emits, kept as a no-op for safety.
///
/// Phase 25: was out of sync (had `resnet50`, which does not exist in
/// the registry, and was missing every modern / advanced / legacy arch
/// the UI offers), so the train preflight rejected valid archs like
/// `efficientnet_simple` with "Unknown architecture".
const KNOWN_ARCHS: &[&str] = &[
    "custom",
    // Modern (recommended)
    "efficientnet_lstm",
    "efficientnet_simple",
    "mobilenet_v3",
    // Alias: 14 shipped game profiles spell it this way. The Python
    // side normalises it via MODEL_ALIASES, so accept it here rather
    // than blocking the action with "Unknown architecture".
    "mobilenetv3",
    "resnet18_lstm",
    // Advanced (experimental)
    "efficientnet_transformer",
    "multihead_action",
    "game_attention",
    // Legacy (backward compatibility)
    "inception_v3",
    "alexnet",
    "sentnet",
    "sentnet_2d",
];

/// True when `s` is a bare architecture id rather than a model path.
///
/// Issue #76: the UI's fallback catalog advertises architectures with
/// `path == id`, so an activated architecture reaches the bot preflight
/// as a `model_dir` that is a single token like "efficientnet_lstm".
/// Anything containing a path separator is a real (if possibly stale)
/// directory and must NOT be reported as an architecture.
fn is_architecture_id(s: &str) -> bool {
    let t = s.trim();
    if t.is_empty() || t.contains('/') || t.contains('\\') {
        return false;
    }
    KNOWN_ARCHS.contains(&t)
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
    let raw = std::env::current_exe()
        .ok()
        .and_then(|exe| exe.parent().map(|p| p.to_path_buf()))
        .unwrap_or_else(|| std::env::current_dir().unwrap_or_else(|_| PathBuf::from(".")));
    // PHASE 14: Windows' current_exe() commonly returns paths with
    // the `\\?\` extended-length prefix. That prefix is *valid* for
    // Win32 file APIs but *breaks* Python's import machinery: an
    // entry like `\\?\C:\Program Files\BOT-MMORPG-AI\resources` on
    // sys.path produces `ModuleNotFoundError` even when the package
    // dir + __init__.py exist on disk. Strip it at the source so
    // every downstream consumer (PYTHONPATH, --resource-root,
    // MODELHUB_RESOURCE_ROOT, install_health rows) gets a clean
    // path. Our install dir is well under 260 chars; we don't need
    // the long-path namespace.
    strip_extended_path_prefix(&raw)
}

/// Strip the Windows extended-length-path prefix `\\?\` (or
/// `\\?\UNC\`) from a path. On non-Windows or on paths without the
/// prefix, returns the input unchanged.
///
///   `\\?\C:\foo`        -> `C:\foo`
///   `\\?\UNC\srv\share` -> `\\srv\share`
///   `C:\foo`            -> `C:\foo` (unchanged)
///
/// Why we need this: Windows APIs that go through `current_exe()`,
/// `canonicalize()`, or certain Tauri path resolvers return the
/// prefixed form. Most consumers handle it fine; Python's
/// importlib does NOT, which broke first-launch package resolution
/// despite the package being on disk and on PYTHONPATH (Phase 9
/// got the path STRUCTURE right, this got the path FORM right).
fn strip_extended_path_prefix(p: &Path) -> PathBuf {
    if !cfg!(windows) {
        return p.to_path_buf();
    }
    let s = match p.to_str() {
        Some(s) => s,
        None => return p.to_path_buf(),
    };
    if let Some(rest) = s.strip_prefix(r"\\?\") {
        // `\\?\UNC\server\share\...` -> `\\server\share\...`
        if let Some(unc_rest) = rest.strip_prefix(r"UNC\") {
            return PathBuf::from(format!(r"\\{}", unc_rest));
        }
        // `\\?\C:\...` -> `C:\...`
        return PathBuf::from(rest);
    }
    p.to_path_buf()
}

/// Where mutable user data lives (datasets, models, logs, runtime, .env).
///
/// Resolves to `%LOCALAPPDATA%\com.bot.mmorpg.ai\` on Windows
/// (e.g. `C:\Users\<user>\AppData\Local\com.bot.mmorpg.ai\`) via Tauri's
/// `app_local_data_dir`. On Linux/macOS it falls back to the platform's
/// XDG / Library equivalent.
///
/// Why not the installation directory: prior versions wrote to
/// `C:\Program Files\BOT-MMORPG-AI\` -- which requires admin elevation
/// for any write. That broke pip self-repair, sitecustomize.py rewrites
/// on launch, dataset / model writes for non-elevated sessions, and
/// triggered Defender heuristics on writes under Program Files. Moving
/// to %LOCALAPPDATA% follows the convention of every modern heavy-
/// runtime desktop tool (VS Code, Docker Desktop, Steam shaders).
///
/// Final fallback (only if Tauri's resolver returns None, which
/// shouldn't happen on a healthy install) is the legacy installation
/// directory so the app still launches in a degraded state instead of
/// panicking.
/// Probe whether a directory is writable by creating + deleting a
/// tiny marker file. Used by `install_health` and `preflight_action`
/// to surface read-only / locked / OneDrive-stub failures before the
/// spawned Python script blows up halfway through with a
/// PermissionError. Best-effort: we create the dir if missing,
/// because the data subdirs (datasets/, trained_models/) are made
/// lazily on first use.
fn probe_writable(dir: &Path) -> bool {
    let _ = fs::create_dir_all(dir);
    let probe = dir.join(".write_probe");
    let ok = fs::write(&probe, b"ok").is_ok();
    let _ = fs::remove_file(&probe);
    ok
}

/// Phase 17: enriched writability check. Distinguishes the four
/// states a probe can land in so install_health rows can give a
/// precise remediation instead of a generic "cannot write to ...".
///
/// Returns `(ok, detail)`:
///   ok=true,  detail=<empty>      -- dir exists and is writable
///   ok=false, detail="dir exists but is not writable. ..." -- common when
///        a prior production install (running as Admin via NSIS) created
///        the dir with restrictive perms; current dev/user run can't write
///   ok=false, detail="cannot create dir ..." -- create_dir_all failed, eg.
///        parent doesn't exist or read-only filesystem
///   ok=false, detail="cannot write probe ..." -- something else (AV lock,
///        OneDrive on-demand stub, antivirus directory hold)
fn probe_writable_detailed(dir: &Path) -> (bool, String) {
    let existed_before = dir.exists();
    if let Err(e) = fs::create_dir_all(dir) {
        return (
            false,
            format!(
                "cannot create directory: {}. Common causes: parent path missing, read-only volume, NTFS permission denied. Try: `Remove-Item -Recurse \"{}\"` and relaunch.",
                e,
                dir.display()
            ),
        );
    }
    let probe = dir.join(".write_probe");
    match fs::write(&probe, b"ok") {
        Ok(_) => {
            let _ = fs::remove_file(&probe);
            (true, String::new())
        }
        Err(e) => {
            let hint = if existed_before {
                // The dir was already there -- most likely created by a
                // previous Admin install; current user can't write into it.
                format!(
                    "directory exists but is not writable: {}. Most common cause: a previous install created this dir as Administrator and the current run is unprivileged. Fix: `Remove-Item -Recurse \"{}\"` (it will be recreated on next launch with the correct owner).",
                    e,
                    dir.display()
                )
            } else {
                // We just created it but still can't write -- AV lock or
                // OneDrive file-on-demand stub on the parent.
                format!(
                    "directory created but write probe failed: {}. Common causes: antivirus directory lock, OneDrive file-on-demand stub on the parent, group policy. Try moving %LOCALAPPDATA% off OneDrive or whitelist BOT-MMORPG-AI in your AV.",
                    e
                )
            };
            (false, hint)
        }
    }
}

fn local_data_root(app: &AppHandle) -> PathBuf {
    // Phase 19: in DEV builds, isolate from the production data dir
    // (`%LOCALAPPDATA%\com.bot.mmorpg.ai`) so `make dev` never inherits
    // leftover state from a prior production install -- Admin-owned
    // subfolders that the unprivileged user-mode dev process can't
    // write to (the "Logs/Datasets directory: Cannot write" error
    // the user kept hitting). Maps to `<repo>/.dev-data/` instead.
    //
    // Opt out with `BOT_USE_PROD_DATA_DIR=1` if a dev specifically
    // wants to test against their installed app's data (rare).
    //
    // Production builds (release, where !cfg!(debug_assertions)) ALWAYS
    // use the platform data dir -- this branch is purely a dev-mode
    // safeguard.
    if cfg!(debug_assertions) && std::env::var("BOT_USE_PROD_DATA_DIR").is_err() {
        let dev_root = dev_repo_root().join(".dev-data");
        let _ = fs::create_dir_all(&dev_root);
        return dev_root;
    }
    if let Some(p) = app.path_resolver().app_local_data_dir() {
        let _ = fs::create_dir_all(&p);
        return p;
    }
    // Degraded fallback: keep the legacy behaviour so the app still
    // boots even when Tauri can't compute the local data dir. The
    // user will see permission errors on writes, but the rest of the
    // diagnostic surface keeps working.
    installation_dir()
}

/// Move the legacy on-disk runtime tree from the installation
/// directory (Program Files\BOT-MMORPG-AI\runtime\, datasets\, etc.)
/// into the new local-data root, exactly once, on first launch
/// after upgrading. Idempotent: returns immediately if either there
/// is nothing legacy to migrate, or the new root already has data.
///
/// Side-effects only -- never panics, never blocks launch. Failures
/// are reported via the terminal_update channel so the operator can
/// see them in the AI Fix Bundle.
fn migrate_legacy_runtime_if_needed(app: &AppHandle) {
    // Skip if Tauri's resolver disagreed with us about where local
    // data lives -- in that degraded case local_data_root falls back
    // to installation_dir() and source==dest, so migration is a no-op.
    let new_root = match app.path_resolver().app_local_data_dir() {
        Some(p) => p,
        None => return,
    };
    let legacy_root = installation_dir();
    if same_path(&new_root, &legacy_root) {
        return;
    }

    // Subdirectories worth migrating. NOT 'resources' (that ships with
    // the installer and lives under Program Files) and NOT '.env'
    // (we re-create it on demand if missing).
    let movable = ["runtime", "datasets", "models", "logs", "content"];

    for sub in movable {
        let src = legacy_root.join(sub);
        let dst = new_root.join(sub);
        if !src.exists() {
            continue;
        }
        // Don't clobber: if the new root already has data here, the
        // user has already migrated (or started fresh on the new
        // location) and we leave both alone.
        if dst.exists() && fs::read_dir(&dst).map(|mut it| it.next().is_some()).unwrap_or(false) {
            continue;
        }
        if let Some(window) = app.get_window("main") {
            let _ = window.emit::<String>(
                "terminal_update",
                format!("[Migration] Moving {} -> {}", src.display(), dst.display()),
            );
        }
        // Try rename first (atomic, near-zero cost on same volume).
        // Fall back to recursive copy + remove on cross-volume.
        if fs::rename(&src, &dst).is_err() {
            if let Err(e) = copy_dir_recursive(&src, &dst) {
                if let Some(window) = app.get_window("main") {
                    let _ = window.emit::<String>(
                        "terminal_update",
                        format!("[Migration][Warning] Copy failed for {}: {}", src.display(), e),
                    );
                }
                continue;
            }
            // Best-effort cleanup; if Windows holds a handle on the
            // legacy tree we'll just leak it and rely on the user
            // uninstalling the old layout later.
            let _ = fs::remove_dir_all(&src);
        }
    }
}

fn same_path(a: &Path, b: &Path) -> bool {
    fs::canonicalize(a)
        .ok()
        .zip(fs::canonicalize(b).ok())
        .map(|(ca, cb)| ca == cb)
        .unwrap_or_else(|| a == b)
}

fn copy_dir_recursive(src: &Path, dst: &Path) -> std::io::Result<()> {
    fs::create_dir_all(dst)?;
    for entry in fs::read_dir(src)? {
        let entry = entry?;
        let from = entry.path();
        let to = dst.join(entry.file_name());
        if entry.file_type()?.is_dir() {
            copy_dir_recursive(&from, &to)?;
        } else {
            fs::copy(&from, &to)?;
        }
    }
    Ok(())
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
/// PYTHONPATH entries we add in `build_python_script_command` /
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
    // Pull AppState so the install/repair progress lines route through
    // emit_with_buffer -- otherwise they're lost to the same
    // pre-listener gap that swallowed the [Sidecar stderr] block.
    let state_inner: Arc<AppStateInner> = app.state::<AppState>().inner.clone();

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
            emit_with_buffer(
                &state_inner,
                Some(window),
                format!("[System] Bundled runtime archive: {}", archive_path.display()),
            );

            if needs_repair_recopy {
                emit_with_buffer(
                    &state_inner,
                    Some(window),
                    "[System] Detected stale/corrupt install (python exists but site-packages empty) -> repairing by extracting bundled runtime..."
                        .to_string(),
                );
            } else {
                emit_with_buffer(
                    &state_inner,
                    Some(window),
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

            emit_with_buffer(
                &state_inner,
                Some(window),
                format!("[System] Bundled Python dir: {}", bundled_dir.display()),
            );

            if needs_repair_recopy {
                emit_with_buffer(
                    &state_inner,
                    Some(window),
                    "[System] Detected stale/corrupt install (python exists but site-packages empty) -> repairing by recopying bundled runtime..."
                        .to_string(),
                );
            } else {
                emit_with_buffer(
                    &state_inner,
                    Some(window),
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
    // That second behaviour bites us specifically:
    // `build_python_script_command` adds the script's parent dir to
    // PYTHONPATH (`vdir`) so scripts can import siblings — but the
    // embedded interpreter discards it, and `1-collect_data.py` dies
    // on `from grabscreen import grab_screen` (grabscreen.py is a
    // sibling, not a package install).
    //
    // What we CAN rely on: `import site` is in the patched _pth, so
    // site.py runs at startup and looks for `sitecustomize` on sys.path.
    // The bundled site-packages IS on sys.path (via `.\site-packages`
    // in _pth), so dropping a sitecustomize.py here makes Python pick
    // it up automatically. Inside it we read the `BOT_VERSION_DIR` env
    // var (which `build_python_script_command` already exports) and
    // prepend it to sys.path. Now sibling imports work without
    // touching any of the 50+ scripts in versions/0.01/.
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
        "# module imports for scripts launched via build_python_script_command",
        "# under embedded Python's _pth-isolated mode (PYTHONPATH is ignored).",
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

/// Emit a `terminal_update` line AND record it in the `early_log`
/// ring buffer so a late-attaching JS listener can replay missed
/// lines via `drain_early_log`. Use this for every startup-time
/// emit that fires from `setup()` or `start_sidecar_server`,
/// because the WebView's `listen("terminal_update")` handler does
/// not exist until DOMContentLoaded -- which runs AFTER `setup()`
/// returns. Without buffering, the [Sidecar stderr] / [Fatal] /
/// [Hint] / "still warming up..." lines are dropped on the floor.
fn emit_with_buffer(inner: &Arc<AppStateInner>, window: Option<&Window>, line: String) {
    if let Some(w) = window {
        let _ = w.emit::<String>("terminal_update", line.clone());
    }
    if let Ok(mut buf) = inner.early_log.lock() {
        if buf.len() >= EARLY_LOG_CAP {
            buf.pop_front();
        }
        buf.push_back(line);
    }
}

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

// ---------------------------
// LAUNCH REPORT HELPERS
// ---------------------------

/// Quote a shell argument: bare if safe, double-quoted with internal
/// quotes escaped otherwise. Targets a Windows-paste audience but
/// also reads sanely on POSIX. Used only for the "Command" line in
/// the debug bundle -- not for actual process spawning.
fn shell_quote(s: &str) -> String {
    let safe = s
        .chars()
        .all(|c| c.is_alphanumeric() || matches!(c, '_' | '-' | '.' | '/' | ':' | '\\'));
    if safe && !s.is_empty() {
        s.to_string()
    } else {
        let escaped = s.replace('"', "\\\"");
        format!("\"{}\"", escaped)
    }
}

/// Filter the spawn-time env down to a small allow-list. Keeps:
///   - keys we set ourselves (BOT_*, MODELHUB_*, BOTMMO_*, PYTHON*)
///   - a small allow-list of harmless system vars
///   - PATH (truncated to first 4 entries for readability)
/// Drops everything else so we never accidentally surface API keys,
/// OAuth tokens, or unrelated tooling paths in a debug bundle.
fn filter_launch_env(env_iter: impl Iterator<Item = (OsString, OsString)>) -> Vec<(String, String)> {
    const SYSTEM_ALLOW: &[&str] = &[
        "LOCALAPPDATA",
        "USERPROFILE",
        "TEMP",
        "TMP",
        "OS",
        "NUMBER_OF_PROCESSORS",
        "PROCESSOR_ARCHITECTURE",
        "ProgramFiles",
        "ProgramFiles(x86)",
        "SystemRoot",
        "windir",
    ];
    let mut out: Vec<(String, String)> = Vec::new();
    for (k, v) in env_iter {
        let key = k.to_string_lossy().to_string();
        let upper = key.to_ascii_uppercase();
        let keep = upper.starts_with("BOT_")
            || upper.starts_with("BOTMMO_")
            || upper.starts_with("MODELHUB_")
            || upper.starts_with("PYTHON")
            || SYSTEM_ALLOW.iter().any(|a| a.eq_ignore_ascii_case(&key))
            || upper == "PATH";
        if !keep {
            continue;
        }
        let mut val = v.to_string_lossy().to_string();
        // PATH gets truncated -- the first few entries are the
        // ones that matter (embedded python, repo .venv) and the
        // tail just clutters the bundle.
        if upper == "PATH" {
            let sep = if cfg!(windows) { ';' } else { ':' };
            let parts: Vec<&str> = val.split(sep).collect();
            if parts.len() > 4 {
                val = format!(
                    "{}{}... ({} more entries elided)",
                    parts[..4].join(&sep.to_string()),
                    sep,
                    parts.len() - 4
                );
            }
        }
        out.push((key, val));
    }
    out.sort_by(|a, b| a.0.cmp(&b.0));
    out
}

fn unix_now_ms() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(0)
}

/// Push a line into a capped Vec<String>, dropping the oldest on
/// overflow. Used by the stdout/stderr threads to populate the
/// launch report's ring buffers without unbounded growth.
fn push_capped(vec: &mut Vec<String>, line: String, cap: usize) {
    if vec.len() >= cap {
        vec.remove(0);
    }
    vec.push(line);
}

/// Record a structured ErrorEntry for a sidecar-startup failure.
///
/// Without this, the AI/Debug Bundle reports `Error count: 0`
/// even when the sidecar genuinely failed to start, because the
/// error count only reflects the Rust ring buffer + the sidecar's
/// /diagnostics/recent feed -- and a sidecar that never came up
/// can't populate either. The launch report (command/cwd/env/
/// stdout/stderr/health) IS captured, but a downstream reviewer
/// reading "errors: 0" might still misread the bundle as "looks
/// fine". Calling record_error() with a SidecarStartupFailed
/// entry closes that gap so the bundle's structured-errors
/// section also reflects the failure.
///
/// Attaches the launch report's `pid`, `timeout_secs`, the first
/// stderr line (best clue when stderr captured something), and
/// the exit_code into ErrorEntry.context.
fn record_startup_failure(
    inner: &Arc<AppStateInner>,
    error_message: String,
    rep: Option<&SidecarLaunchReport>,
) {
    let timestamp_ms = unix_now_ms();
    let first_stderr = rep
        .and_then(|r| r.stderr_lines.first().cloned())
        .unwrap_or_default();
    let context = match rep {
        Some(r) => json!({
            "phase": "startup",
            "pid": r.pid,
            "timeout_secs": r.timeout_secs,
            "exit_code": r.exit_code,
            "stderr_first_line": first_stderr,
            "stderr_line_count": r.stderr_lines.len(),
            "stdout_line_count": r.stdout_lines.len(),
            "duration_ms": r
                .finished_at_ms
                .map(|f| f.saturating_sub(r.started_at_ms))
                .unwrap_or(0),
        }),
        None => json!({"phase": "startup"}),
    };
    record_error(
        inner,
        ErrorEntry {
            timestamp_ms,
            source: "rust".to_string(),
            error_type: "SidecarStartupFailed".to_string(),
            message: error_message,
            primary_file: "src-tauri/src/main.rs".to_string(),
            primary_line: 0,
            traceback: String::new(),
            context,
        },
    );
}

/// Update the inner.last_launch_report slot via a closure. Lock is
/// held only for the closure's duration. No-op if the mutex is
/// poisoned -- we'd rather lose the diagnostic than crash.
fn with_launch_report(inner: &Arc<AppStateInner>, f: impl FnOnce(&mut SidecarLaunchReport)) {
    if let Ok(mut slot) = inner.last_launch_report.lock() {
        if slot.is_none() {
            *slot = Some(SidecarLaunchReport::default());
        }
        if let Some(rep) = slot.as_mut() {
            f(rep);
        }
    }
}

/// return both SidecarApi and the spawned Child handle
fn start_sidecar_server(app: &AppHandle) -> Result<(SidecarApi, Child), String> {
    // Reach into AppState so we can route every startup-time emit
    // through `emit_with_buffer` (so a late JS listener can still
    // pick up the [Sidecar stderr] / heartbeat / [Fatal] / [Hint]
    // lines via drain_early_log). Cloning the Arc is cheap.
    let state_inner: Arc<AppStateInner> = app.state::<AppState>().inner.clone();

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

    // Read-only resources directory.
    // Phase 14: strip the Windows extended-length-path prefix
    // (`\\?\`) so all paths derived from this -- backend script
    // path, modelhub package parent, --resource-root arg,
    // MODELHUB_RESOURCE_ROOT env -- arrive at Python in the plain
    // form. importlib silently fails to resolve packages on
    // sys.path entries that start with `\\?\`.
    let resource_root = strip_extended_path_prefix(
        &app.path_resolver()
            .resource_dir()
            .unwrap_or_else(|| std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."))),
    );

    let mut cmd = if cfg!(debug_assertions) {
        let py = find_python_for_app(app)?;

        // Phase 18: dev mode now uses the same backend/entry_main.py
        // entry as production. Previously it ran modelhub/tauri.py
        // directly as a script, which meant Python loaded tauri.py
        // as a top-level module rather than as `modelhub.tauri` --
        // and the relative imports inside it (`from .jobs.routes
        // import ...`, `from .diagnostics.routes import ...`) raised
        // "attempted relative import with no known parent package",
        // mounting the routers as no-ops in dev. Routing through
        // entry_main.py loads tauri.py as part of the modelhub
        // package, so the relative imports resolve and dev mode has
        // the same /jobs and /diagnostics endpoints as prod.
        let script = dev_repo_root().join("backend").join("entry_main.py");
        if !script.exists() {
            return Err(format!(
                "Sidecar entrypoint not found in dev (expected {} )",
                script.display()
            ));
        }

        let win = app.get_window("main");
        emit_with_buffer(
            &state_inner,
            win.as_ref(),
            format!("[System] Sidecar Python: {}", py.display()),
        );
        emit_with_buffer(
            &state_inner,
            win.as_ref(),
            format!("[System] Sidecar Script: {}", script.display()),
        );

        let mut c = Command::new(&py);
        apply_dev_venv_env(&mut c, &dev_repo_root());
        apply_stable_python_env(&mut c);
        // Phase 18: also export MODELHUB_RESOURCE_ROOT so
        // entry_main.py's _bootstrap_sys_path() can find the repo
        // root (and therefore the modelhub package). Without this
        // the bootstrap falls back to walking up from __file__,
        // which works -- but explicit is better than implicit.
        c.env("MODELHUB_RESOURCE_ROOT", dev_repo_root());
        c.arg("-u"); // unbuffered, matches prod
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
        // Phase 14: strip `\\?\` defense-in-depth. resource_root
        // was already stripped above, but resolve_resource() can
        // independently return a prefixed path on Windows.
        let backend_script = strip_extended_path_prefix(
            &app
                .path_resolver()
                .resolve_resource("resources/backend/entry_main.py")
                .filter(|p| p.exists())
                .or_else(|| {
                    // Fallback for read-only resources: look under the
                    // installation directory (Program Files\BOT-MMORPG-AI\)
                    // -- NOT local_data_root(), which now points to
                    // %LOCALAPPDATA% and never carries shipped resources.
                    let direct = installation_dir()
                        .join("resources")
                        .join("backend")
                        .join("entry_main.py");
                    if direct.exists() { Some(direct) } else { None }
                })
                .ok_or_else(|| {
                    "Bundled backend script not found: resources/backend/entry_main.py".to_string()
                })?,
        );

        emit_with_buffer(
            &state_inner,
            Some(&window),
            format!("[System] Sidecar Python: {}", py.display()),
        );
        emit_with_buffer(
            &state_inner,
            Some(&window),
            format!("[System] Sidecar Script: {}", backend_script.display()),
        );

        let mut c = Command::new(&py);
        apply_stable_python_env(&mut c);

        // Set PYTHONPATH to include backend modules
        let sep = if is_windows() { ";" } else { ":" };
        let mut pypaths: Vec<String> = vec![];

        // Add the backend directory to Python path. backend_script
        // was already stripped of any `\\?\` prefix above; the
        // explicit strip here is defense-in-depth in case that
        // wrapper is ever refactored away.
        if let Some(backend_dir) = backend_script.parent() {
            pypaths.push(strip_extended_path_prefix(backend_dir).display().to_string());
        }

        // Add the PARENT of the modelhub/ directory to PYTHONPATH so
        // Python resolves `import modelhub` to the package (its
        // __init__.py), and `from modelhub.tauri import main` resolves
        // to <parent>/modelhub/tauri.py.
        //
        // Phase 9 BUG FIX: previously this pushed `modelhub_dir`
        // ITSELF onto PYTHONPATH, which made tauri.py look like a
        // top-level module and broke entry_main.py's
        // `from modelhub.tauri import main` with
        //     ModuleNotFoundError: No module named 'modelhub'
        // The parent directory (<install>/resources/) is what Python
        // needs to see `modelhub/` as a package.
        // Phase 14: strip `\\?\` from the resolver's return BEFORE
        // taking .parent() so the parent we push is also clean.
        let modelhub_dir = strip_extended_path_prefix(
            &app
                .path_resolver()
                .resolve_resource("resources/modelhub")
                .filter(|p| p.exists())
                .unwrap_or_else(|| installation_dir().join("resources").join("modelhub")),
        );
        if modelhub_dir.exists() {
            if let Some(modelhub_parent) = modelhub_dir.parent() {
                // Strip again as belt-and-suspenders -- parent of a
                // clean path is clean, but a future refactor that
                // changes modelhub_dir's source should not be able
                // to silently re-introduce the bug.
                pypaths.push(strip_extended_path_prefix(modelhub_parent).display().to_string());
            }
        }

        // Add site-packages from embedded Python (managed dir is
        // under %LOCALAPPDATA% so it shouldn't have `\\?\`, but
        // strip defensively).
        let site_pkgs = strip_extended_path_prefix(&managed_site_packages_dir(app));
        if site_pkgs.exists() {
            pypaths.push(site_pkgs.display().to_string());
        }

        // Add resource root for imports (already stripped above
        // when resource_root was assigned; redundant strip is
        // harmless and signals intent).
        pypaths.push(strip_extended_path_prefix(&resource_root).display().to_string());

        let old_pypath = std::env::var("PYTHONPATH").unwrap_or_default();
        if !old_pypath.is_empty() {
            pypaths.push(old_pypath);
        }

        c.env("PYTHONPATH", pypaths.join(sep));
        c.arg("-u"); // Unbuffered output for real-time logs
        c.arg(&backend_script);
        c
    };

    // Phase 14: strip `\\?\` defensively from every path arg that
    // crosses the Rust->Python boundary. resource_root was stripped
    // when it was assigned; data_root is derived from
    // app_local_data_dir() (KNOWN_FOLDER) and shouldn't carry the
    // prefix in practice -- but a one-line strip here is cheap
    // insurance against a future Tauri / OS API surprise.
    let resource_root_clean = strip_extended_path_prefix(&resource_root);
    let data_root_clean = strip_extended_path_prefix(&data_root);
    cmd.args([
        "--port",
        "0",
        "--token",
        &token,
        "--resource-root",
        &resource_root_clean.to_string_lossy(),
        "--data-root",
        &data_root_clean.to_string_lossy(),
    ]);

    cmd.env("MODELHUB_RESOURCE_ROOT", &resource_root_clean);
    cmd.env("MODELHUB_DATA_ROOT", &data_root_clean);
    cmd.current_dir(&data_root_clean);

    cmd.stdout(Stdio::piped());
    cmd.stderr(Stdio::piped());

    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x08000000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }

    // Phase 4 -- LaunchReport: snapshot what we are about to spawn
    // BEFORE the spawn, so even a failed `cmd.spawn()` (executable
    // missing, permission denied) leaves us with command/cwd/env
    // attributable to the failure. We seed the report with a clean
    // default and overwrite the slot regardless of prior content.
    {
        let argv_quoted: Vec<String> = std::iter::once(cmd.get_program().to_os_string())
            .chain(cmd.get_args().map(|a| a.to_os_string()))
            .map(|os| shell_quote(&os.to_string_lossy()))
            .collect();
        let env_filtered = filter_launch_env(
            cmd.get_envs()
                .filter_map(|(k, v)| v.map(|val| (k.to_os_string(), val.to_os_string()))),
        );
        let cwd_str = cmd
            .get_current_dir()
            .map(|p| p.display().to_string())
            .unwrap_or_else(|| "(unset)".to_string());
        if let Ok(mut slot) = state_inner.last_launch_report.lock() {
            *slot = Some(SidecarLaunchReport {
                status: "starting".to_string(),
                command: argv_quoted.join(" "),
                cwd: cwd_str,
                env_filtered,
                pid: None,
                timeout_secs: 0, // filled below once the budget is decided
                started_at_ms: unix_now_ms(),
                finished_at_ms: None,
                exit_code: None,
                error_string: None,
                stdout_lines: Vec::new(),
                stderr_lines: Vec::new(),
                health_probe_result: None,
                health_probe_body: None,
            });
        }
    }

    let mut child = cmd
        .spawn()
        .map_err(|e| {
            // Capture the spawn-time failure in the launch report
            // before bailing -- the user's debug bundle should show
            // exactly what we attempted even when the OS refused.
            with_launch_report(&state_inner, |r| {
                r.status = "failed".to_string();
                r.finished_at_ms = Some(unix_now_ms());
                r.error_string = Some(format!("spawn failed: {}", e));
            });
            // Phase 6: also push a structured ErrorEntry so the AI
            // bundle's error count reflects the failure (without
            // this it reads "Error count: 0" even when startup
            // really failed -- the user finding that motivated this).
            let snap = state_inner
                .last_launch_report
                .lock()
                .ok()
                .and_then(|g| g.as_ref().cloned());
            record_startup_failure(
                &state_inner,
                format!("spawn failed: {}", e),
                snap.as_ref(),
            );
            format!("Failed to start sidecar: {e}")
        })?;
    with_launch_report(&state_inner, |r| {
        r.pid = Some(child.id());
    });

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
    let stdout_inner = state_inner.clone();
    thread::spawn(move || {
        let reader = BufReader::new(stdout);
        for line in reader.lines().flatten() {
            // Capture into the launch report's stdout ring (capped).
            // We capture every line, including the READY line, so
            // a debug bundle always shows the canonical handshake.
            with_launch_report(&stdout_inner, |r| {
                push_capped(&mut r.stdout_lines, line.clone(), LAUNCH_LOG_CAP);
            });
            if let Some(api) = parse_ready_line(&line) {
                let _ = tx_out.send(Ok(api));
                return;
            }
        }
        let _ = tx_out.send(Err("Sidecar exited without READY line (stdout)".to_string()));
    });

    let app_handle = app.clone();
    let tx_err = tx.clone();
    let stderr_inner = state_inner.clone();
    thread::spawn(move || {
        let reader = BufReader::new(stderr);
        for line in reader.lines().flatten() {
            // Capture the raw line into the launch report's stderr
            // ring BEFORE prefix-formatting, so the bundle shows
            // exactly what Python printed (no [Sidecar stderr]
            // prefix noise in the markdown blocks).
            with_launch_report(&stderr_inner, |r| {
                push_capped(&mut r.stderr_lines, line.clone(), LAUNCH_LOG_CAP);
            });
            let formatted = format!("[Sidecar stderr] {}", line);
            let win = app_handle.get_window("main");
            emit_with_buffer(&stderr_inner, win.as_ref(), formatted);
            if line.starts_with("FAILED ") {
                let _ = tx_err.send(Err(format!("Sidecar failed: {}", line)));
                return;
            }
        }
    });

    // Wait for the READY line in a loop with periodic heartbeats so the
    // user sees progress instead of a frozen UI for the full timeout
    // budget. On a fresh install + Defender real-time scan, the bundled
    // python's `import torch + fastapi + uvicorn + numpy + cv2` chain
    // can legitimately exceed 30s; the previous 25s budget killed the
    // child mid-import and the user got a misleading "installer is
    // missing" error. 60s with a heartbeat every 5s lets cold imports
    // complete cleanly while still failing fast on a true hang.
    //
    // Phase 3.3: on the very first launch after install, the runtime
    // tree is being extracted, every .pyd / .dll is being scanned by
    // AV for the first time, and the disk cache is cold. Stretch the
    // budget to 120 s the first time so we don't time out a legitimate
    // (slow) startup. Subsequent launches drop back to 60 s. Detection
    // uses a marker file under local_data_root: presence == "we have
    // successfully booted at least once before".
    let first_launch_marker = local_data_root(app).join(".sidecar_warmed_once");
    let is_first_launch = !first_launch_marker.exists();
    let total_budget = if is_first_launch {
        Duration::from_secs(120)
    } else {
        Duration::from_secs(60)
    };
    // Stamp the timeout into the launch report so the debug bundle
    // shows whether we used the first-launch (120s) or the steady-
    // state (60s) budget. Helps diagnose "we timed out at exactly
    // 60s every time" cold-disk loops.
    with_launch_report(&state_inner, |r| {
        r.timeout_secs = total_budget.as_secs();
    });
    if is_first_launch {
        let win = app.get_window("main");
        emit_with_buffer(
            &state_inner,
            win.as_ref(),
            "[Sidecar] First launch detected -- using extended 120s warm-up budget for cold-disk imports + AV scan.".to_string(),
        );
    }
    let heartbeat_interval = Duration::from_secs(5);
    let started = std::time::Instant::now();
    loop {
        let elapsed = started.elapsed();
        if elapsed >= total_budget {
            // Capture the exit code from the (now-killed) child so
            // the debug bundle distinguishes "child died at second
            // 30" from "child still running at second 60". We try
            // try_wait first to see if it already exited on its own.
            let try_exit = child.try_wait().ok().flatten().and_then(|s| s.code());
            let _ = child.kill();
            let waited_exit = child.wait().ok().and_then(|s| s.code());
            let exit_code = try_exit.or(waited_exit);
            with_launch_report(&state_inner, |r| {
                r.status = "failed".to_string();
                r.finished_at_ms = Some(unix_now_ms());
                r.exit_code = exit_code;
                r.error_string = Some("Timed out waiting for sidecar READY line".to_string());
            });
            let snap = state_inner
                .last_launch_report
                .lock()
                .ok()
                .and_then(|g| g.as_ref().cloned());
            record_startup_failure(
                &state_inner,
                "Timed out waiting for sidecar READY line".to_string(),
                snap.as_ref(),
            );
            return Err("Timed out waiting for sidecar READY line".to_string());
        }
        let remaining = total_budget - elapsed;
        let next_wait = std::cmp::min(remaining, heartbeat_interval);
        match rx.recv_timeout(next_wait) {
            Ok(Ok(api)) => {
                // Phase 3.3: record that a sidecar has successfully
                // started here at least once. From now on the budget
                // drops to the standard 60s. Best-effort -- if the
                // marker can't be written (read-only FS, full disk),
                // future launches just keep using the long budget,
                // which is not a regression.
                if is_first_launch {
                    if let Some(parent) = first_launch_marker.parent() {
                        let _ = fs::create_dir_all(parent);
                    }
                    let _ = fs::write(&first_launch_marker, b"ok");
                }
                // Success: stamp the report. Health-probe enrichment
                // happens AFTER this function returns (in setup() /
                // restart_sidecar) so we don't block the spawn path
                // on a 2s reqwest call -- see record_post_launch_health.
                with_launch_report(&state_inner, |r| {
                    r.status = "ok".to_string();
                    r.finished_at_ms = Some(unix_now_ms());
                });
                return Ok((api, child));
            }
            Ok(Err(e)) => {
                let try_exit = child.try_wait().ok().flatten().and_then(|s| s.code());
                let _ = child.kill();
                let waited_exit = child.wait().ok().and_then(|s| s.code());
                let exit_code = try_exit.or(waited_exit);
                with_launch_report(&state_inner, |r| {
                    r.status = "failed".to_string();
                    r.finished_at_ms = Some(unix_now_ms());
                    r.exit_code = exit_code;
                    r.error_string = Some(e.clone());
                });
                let snap = state_inner
                    .last_launch_report
                    .lock()
                    .ok()
                    .and_then(|g| g.as_ref().cloned());
                record_startup_failure(&state_inner, e.clone(), snap.as_ref());
                return Err(e);
            }
            Err(std::sync::mpsc::RecvTimeoutError::Timeout) => {
                let win = app.get_window("main");
                emit_with_buffer(
                    &state_inner,
                    win.as_ref(),
                    format!(
                        "[Sidecar] still warming up... {}s/{}s elapsed (cold-disk import)",
                        elapsed.as_secs() + next_wait.as_secs(),
                        total_budget.as_secs()
                    ),
                );
                continue;
            }
            Err(std::sync::mpsc::RecvTimeoutError::Disconnected) => {
                let try_exit = child.try_wait().ok().flatten().and_then(|s| s.code());
                let _ = child.kill();
                let waited_exit = child.wait().ok().and_then(|s| s.code());
                let exit_code = try_exit.or(waited_exit);
                with_launch_report(&state_inner, |r| {
                    r.status = "failed".to_string();
                    r.finished_at_ms = Some(unix_now_ms());
                    r.exit_code = exit_code;
                    r.error_string = Some("Sidecar channel closed unexpectedly".to_string());
                });
                let snap = state_inner
                    .last_launch_report
                    .lock()
                    .ok()
                    .and_then(|g| g.as_ref().cloned());
                record_startup_failure(
                    &state_inner,
                    "Sidecar channel closed unexpectedly".to_string(),
                    snap.as_ref(),
                );
                return Err("Sidecar channel closed unexpectedly".to_string());
            }
        }
    }
}

/// Run a one-shot GET /health after a successful spawn and stamp the
/// result into the launch report. Best-effort and non-blocking from
/// the user's perspective because we call it from the post-Ok path
/// in `setup()` / `restart_sidecar`. Without this, `status="ok"`
/// only proves we parsed the READY line -- not that the sidecar
/// actually answers HTTP. Closes the loop on the "rule" the user
/// asked for: never report a sidecar without /health.
async fn record_post_launch_health(inner: Arc<AppStateInner>) {
    let probe_timeout = Duration::from_secs(3);
    let api: Option<SidecarApi> = match inner.sidecar.lock() {
        Ok(g) => g.as_ref().cloned(),
        Err(_) => None,
    };
    let Some(api) = api else {
        with_launch_report(&inner, |r| {
            r.health_probe_result = Some("slot empty (sidecar not registered)".to_string());
        });
        return;
    };
    let url = format!("{}/health", api.base_url);
    let res = inner
        .http
        .get(&url)
        .header("X-Auth-Token", &api.token)
        .timeout(probe_timeout)
        .send()
        .await;
    match res {
        Ok(resp) => {
            let status = resp.status();
            let body = resp.text().await.unwrap_or_default();
            // Truncate body to keep the bundle readable.
            let body_short = if body.len() > 2048 {
                format!("{}\n... ({} bytes elided)", &body[..2048], body.len() - 2048)
            } else {
                body
            };
            with_launch_report(&inner, |r| {
                r.health_probe_result = Some(format!("{}", status));
                r.health_probe_body = Some(body_short);
            });
        }
        Err(e) => {
            // reqwest's Error already includes the kind (timeout,
            // connect refused, etc.) -- surface it verbatim.
            with_launch_report(&inner, |r| {
                r.health_probe_result = Some(format!("error: {}", e));
                r.health_probe_body = None;
            });
        }
    }
}

// ---------------------------
// AAA-GRADE STARTUP SUPERVISION (Phase 7)
// ---------------------------
//
// Bounded retry with exponential backoff + health-gated readiness +
// bounded auto-restart. Mirrors how Steam, Battle.net, Riot Client,
// and the Epic Games Launcher supervise their backend services:
//
//   1. The first launch attempt gets the full warm-up budget
//      (60s steady-state, 120s first-launch). On Err, retry once
//      with a shorter budget (the cold-start factors are no longer
//      relevant by then -- the runtime is warm).
//   2. NEVER claim "ready" until /health round-trips cleanly. A
//      parsed READY line proves uvicorn bound the port; it does
//      NOT prove the FastAPI app actually answers requests. Treat
//      a /health miss as a failed attempt and either retry or fail.
//   3. After successful startup, the liveness watch (Phase 3.2)
//      polls /health every 15s. On failure, auto-restart up to N
//      times before requiring a manual click. Same pattern Steam
//      uses for steamwebhelper.

/// Cap on retries for INITIAL startup. Two attempts is the AAA
/// sweet spot: one full-budget attempt, one fast retry. More than
/// that is just annoying the user with a ~3-minute "starting up"
/// window if a transient race / port conflict / AV scan holds the
/// first one back.
const STARTUP_MAX_ATTEMPTS: u32 = 2;

/// Cap on AUTO-restarts during a session. Anything more than 2 in
/// one session is almost certainly a stable failure -- prompt the
/// user instead of looping forever. (Steam stops retrying
/// steamwebhelper after 3 misses; we use 2 because the manual
/// "Retry" button is one click away.)
const LIVENESS_MAX_AUTO_RESTARTS: u32 = 2;

/// /health probe budget when used as a startup gate. 5s is
/// generous for a localhost round-trip but bounded so a
/// completely dead sidecar doesn't trap the user another minute
/// inside the gate.
const STARTUP_HEALTH_GATE_TIMEOUT: Duration = Duration::from_secs(5);

/// Sleep between startup attempts. Exponential -- 2s after attempt 1,
/// 4s after attempt 2, etc. Capped at LIVENESS_MAX_AUTO_RESTARTS so
/// total worst-case is bounded.
fn startup_backoff_for(attempt: u32) -> Duration {
    Duration::from_secs(2u64.pow(attempt.min(3)))
}

/// Sync wrapper around `quick_health_probe` that's safe to call
/// from any context (sync `setup()` or async `restart_sidecar`).
/// Spawns a one-shot tokio current-thread runtime on a dedicated
/// worker thread so we never block the surrounding async runtime
/// (`tokio::Handle::block_on` from inside an async fn deadlocks).
///
/// Returns false on any internal failure (thread panic, runtime
/// build error, channel disconnect) -- callers treat that as
/// "/health didn't respond" which is the correct outcome anyway.
fn sync_health_gate(inner: &Arc<AppStateInner>) -> bool {
    let inner_clone = inner.clone();
    let (tx, rx) = std::sync::mpsc::channel::<bool>();
    let handle = std::thread::spawn(move || {
        let rt = match tokio::runtime::Builder::new_current_thread()
            .enable_all()
            .build()
        {
            Ok(r) => r,
            Err(_) => {
                let _ = tx.send(false);
                return;
            }
        };
        let result = rt.block_on(quick_health_probe(
            &inner_clone,
            STARTUP_HEALTH_GATE_TIMEOUT,
        ));
        let _ = tx.send(result);
    });
    // Bound the wait at probe-timeout + 1s of slack for runtime
    // setup; if we don't hear back in that window assume the worker
    // got stuck and report unhealthy.
    let result = rx
        .recv_timeout(STARTUP_HEALTH_GATE_TIMEOUT + Duration::from_secs(1))
        .unwrap_or(false);
    let _ = handle.join();
    result
}

/// AAA-grade startup wrapper. Call this from `setup()` and
/// `restart_sidecar` instead of `start_sidecar_server` directly.
///
/// Behavior:
///   - Up to STARTUP_MAX_ATTEMPTS attempts, each running the full
///     start_sidecar_server flow.
///   - After each Ok((api, child)), the api is provisionally
///     stashed and a /health probe is fired. If /health responds
///     2xx, we keep the slot and return Ok(()). If it fails, we
///     kill the child, clear the slot, and treat as a failed
///     attempt -- then retry per the loop.
///   - Inter-attempt backoff via `startup_backoff_for` so a
///     transient race doesn't immediately re-spawn into the same
///     conflict.
///   - On final failure, flips `sidecar_startup_failed = true` so
///     `wait_for_sidecar` returns the actionable error string
///     instantly instead of looping.
///
/// Returns Ok(()) on success (state slots populated), Err(msg)
/// on final failure (state slots empty, flag flipped).
fn try_start_sidecar_with_retries_and_gate(app: &AppHandle) -> Result<(), String> {
    let state_inner: Arc<AppStateInner> = app.state::<AppState>().inner.clone();
    let mut last_err = String::new();

    for attempt in 1..=STARTUP_MAX_ATTEMPTS {
        let win = app.get_window("main");
        if attempt > 1 {
            emit_with_buffer(
                &state_inner,
                win.as_ref(),
                format!(
                    "[Sidecar] Retrying startup (attempt {}/{}) -- previous attempt failed.",
                    attempt, STARTUP_MAX_ATTEMPTS
                ),
            );
        }

        match start_sidecar_server(app) {
            Ok((api, child)) => {
                // Provisionally stash so the /health probe can find
                // the api. We undo this if the gate fails.
                {
                    if let Ok(mut slot) = state_inner.sidecar.lock() {
                        *slot = Some(api.clone());
                    }
                }
                {
                    if let Ok(mut slot) = state_inner.sidecar_process.lock() {
                        *slot = Some(child);
                    }
                }

                // Health-gate. We run the async probe on a fresh
                // tokio runtime in a dedicated worker thread, then
                // pull the result back via a sync channel. This
                // makes the gate safe to call from BOTH sync setup()
                // and async restart_sidecar (where a naive block_on
                // would deadlock the surrounding runtime). Cost:
                // one extra OS thread per startup attempt -- cheap.
                let healthy = sync_health_gate(&state_inner);

                if healthy {
                    emit_with_buffer(
                        &state_inner,
                        win.as_ref(),
                        "[Sidecar] /health gate passed. Sidecar is fully READY.".to_string(),
                    );
                    return Ok(());
                }

                // Spawn succeeded but /health silent. Most common
                // cause: the FastAPI app is still importing (torch
                // cold-load) or the auth token rejected us. Either
                // way, we shouldn't claim "ready" yet. Tear down +
                // retry.
                last_err = format!(
                    "Sidecar process started but /health did not respond within {}s",
                    STARTUP_HEALTH_GATE_TIMEOUT.as_secs()
                );
                emit_with_buffer(
                    &state_inner,
                    win.as_ref(),
                    format!(
                        "[Sidecar] Attempt {} spawned cleanly but /health timed out -- treating as failed.",
                        attempt
                    ),
                );
                stop_sidecar_inner(win.as_ref(), &state_inner);
                if let Ok(mut slot) = state_inner.sidecar.lock() {
                    *slot = None;
                }
            }
            Err(e) => {
                last_err = e.clone();
                // start_sidecar_server has already emitted the
                // [Fatal]/stderr context for this attempt; we just
                // log the attempt counter so the user can see we
                // ARE retrying.
                emit_with_buffer(
                    &state_inner,
                    win.as_ref(),
                    format!("[Sidecar] Attempt {} failed: {}", attempt, e),
                );
            }
        }

        if attempt < STARTUP_MAX_ATTEMPTS {
            let backoff = startup_backoff_for(attempt);
            let win = app.get_window("main");
            emit_with_buffer(
                &state_inner,
                win.as_ref(),
                format!(
                    "[Sidecar] Backing off {}s before retry {} of {}...",
                    backoff.as_secs(),
                    attempt + 1,
                    STARTUP_MAX_ATTEMPTS
                ),
            );
            std::thread::sleep(backoff);
        }
    }

    // All attempts exhausted -- mark failure for fail-fast in
    // wait_for_sidecar and return the last error so the caller can
    // surface it on the banner.
    state_inner
        .sidecar_startup_failed
        .store(true, std::sync::atomic::Ordering::SeqCst);
    Err(last_err)
}

// ---------------------------
// HTTP HELPERS
// ---------------------------
/// Wait up to ~65 seconds for the sidecar to become ready, polling every 500ms.
///
/// Why 65s: must outlive the spawn-side budget in start_sidecar_server
/// (currently 60s) so we observe the slot getting populated when
/// READY arrives at second 59, not return "not ready" at second 30
/// while the spawn worker is still waiting another 30 seconds.
///
/// Why 60s on the spawn side: the bundled Python sidecar imports
/// fastapi + uvicorn + numpy + torch + cv2 before printing READY.
/// On a cold disk cache (first launch after install, Defender
/// real-time scan, slow HDD), that easily exceeds 30 seconds. AAA
/// launchers (Steam, Battle.net, Riot Client) all wait 60s+ for
/// backend services to come up before declaring failure -- we
/// follow that convention.
///
/// Polling stays at 500ms so a fast-starting sidecar (warm cache)
/// still feels instant -- we just don't give up early.
const SIDECAR_READY_TIMEOUT_SECS: u64 = 65;
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
        // Fail-fast: if startup is known-failed and the slot is still
        // None, no point polling for a process that's never coming.
        // The user clicks Run Diagnosis or restarts the app to retry.
        // Without this, every api_post / api_get blocks for the full
        // SIDECAR_READY_TIMEOUT_SECS budget on every click after the
        // sidecar's initial spawn-time failure.
        if inner
            .sidecar_startup_failed
            .load(std::sync::atomic::Ordering::SeqCst)
        {
            return Err(
                "Sidecar startup failed at app launch -- see [Fatal] / [Hint] lines in the \
                 terminal log. Restart the app to retry, or open Settings -> System Tools -> \
                 Run Diagnosis for a deterministic verdict."
                    .to_string(),
            );
        }
        // (Heartbeat for in-flight startup lives in start_sidecar_server,
        // which holds the AppHandle. wait_for_sidecar runs from arbitrary
        // call sites without one, so we deliberately don't try to emit
        // terminal_update here -- the spawn-side heartbeat is enough.)
        if attempt + 1 < total_attempts {
            tokio::time::sleep(std::time::Duration::from_millis(SIDECAR_READY_POLL_MS)).await;
        }
    }
    Err(format!(
        "Sidecar API not ready after {} s.\n\
         \n\
         Most likely causes on this build (in order of frequency):\n\
         \n\
         1. Antivirus is scanning the bundled Python runtime\n\
            Defender / corporate AV scans every newly-extracted .pyd / .dll the\n\
            first time you launch. Add this folder to AV exclusions:\n\
            %LOCALAPPDATA%\\com.bot.mmorpg.ai\\runtime\\\n\
         \n\
         2. Cold-disk first launch (slow HDD)\n\
            torch + numpy + fastapi + cv2 cold imports can exceed the budget\n\
            on a slow disk. Wait 30 more seconds and click Run Diagnosis to\n\
            retry, or restart the app -- the second launch is always faster.\n\
         \n\
         3. Embedded Python crashed on import\n\
            Look in the terminal log above for [Sidecar stderr] or\n\
            [Fatal] Sidecar failed lines. Common culprits: missing Visual\n\
            C++ Redistributable (install vc_redist.x64.exe) or a corrupted\n\
            torch wheel (run runtime_doctor for details).\n\
         \n\
         4. Loopback / firewall blocking 127.0.0.1\n\
            Some corporate firewalls block 127.0.0.1 even though the app\n\
            never reaches the network. Whitelist the BOT-MMORPG-AI binary.",
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

/// Quick liveness probe: does a real GET to /health without going
/// through `wait_for_sidecar`, with a tight timeout. Returns
/// `Ok(true)` only if the sidecar replied 2xx within the budget.
///
/// Used by `install_health` to convert a "slot is populated" check
/// (which cannot detect a process that died after printing READY)
/// into an actual round-trip test. Also used by the liveness watch
/// task to decide whether to flip `sidecar_startup_failed`.
///
/// Unlike `api_get_with` this does NOT call `wait_for_sidecar`: a
/// 65-second wait inside install_health would freeze the Diagnosis
/// banner forever the first time the sidecar is down. If the slot
/// is empty we report unhealthy immediately.
async fn quick_health_probe(inner: &Arc<AppStateInner>, timeout: Duration) -> bool {
    let api = {
        let guard = match inner.sidecar.lock() {
            Ok(g) => g,
            Err(_) => return false,
        };
        match guard.as_ref() {
            Some(api) => api.clone(),
            None => return false,
        }
    };
    let url = format!("{}/health", api.base_url);
    let res = inner
        .http
        .get(url)
        .header("X-Auth-Token", api.token)
        .timeout(timeout)
        .send()
        .await;
    matches!(res, Ok(r) if r.status().is_success())
}

/// Phase 3.2: spawn a background task that periodically pings
/// `/health` so we notice if the sidecar dies AFTER it printed
/// READY (segfault on first heavy import, OOM, AV quarantining
/// `torch_cuda.dll` mid-run). Without this, the only signal a user
/// gets is the next `invoke(...)` they trigger failing with a
/// connection error -- which can be 30+ minutes later.
///
/// On `LIVENESS_FAILURE_THRESHOLD` consecutive misses we:
///   1. flip `sidecar_startup_failed = true`, so subsequent
///      `wait_for_sidecar` calls fail-fast with the actionable error
///      string instead of waiting 65 s,
///   2. clear the SidecarApi slot so a manual restart can repopulate,
///   3. emit a `[Sidecar]` line so the UI's terminal panel reflects
///      it -- the sidecar chip handler picks it up via the same
///      `terminal_update` event.
///
/// Self-terminates if the slot is already None (manual stop) or
/// startup is known-failed (already noticed). Restart_sidecar
/// re-spawns a fresh task, so a sidecar that comes back from the
/// dead is monitored again.
fn spawn_sidecar_liveness_watch(app: AppHandle) {
    const LIVENESS_PROBE_INTERVAL: Duration = Duration::from_secs(15);
    const LIVENESS_PROBE_TIMEOUT: Duration = Duration::from_secs(3);
    const LIVENESS_FAILURE_THRESHOLD: u32 = 3;

    tauri::async_runtime::spawn(async move {
        let inner: Arc<AppStateInner> = app.state::<AppState>().inner.clone();
        let mut consecutive_failures: u32 = 0;
        // Phase 7: bounded auto-restart counter. Steam-grade: try
        // to recover automatically up to N times per session, then
        // fall back to "click Retry" instead of looping forever.
        // Resets to 0 on a successful health probe (i.e. after the
        // sidecar comes back). Persists across health-recovery
        // events so a flapping sidecar (recover -> die -> recover
        // -> die) doesn't silently auto-restart 50 times.
        let mut auto_restarts_used: u32 = 0;
        loop {
            tokio::time::sleep(LIVENESS_PROBE_INTERVAL).await;

            // Stop watching if the slot has been deliberately cleared
            // (manual restart in flight) -- the new spawn_sidecar_..
            // call from restart_sidecar / setup will start a fresh
            // task. Stopping here avoids two tasks racing to flip the
            // failure flag.
            let slot_present = match inner.sidecar.lock() {
                Ok(g) => g.is_some(),
                Err(_) => false,
            };
            if !slot_present {
                return;
            }
            if inner
                .sidecar_startup_failed
                .load(std::sync::atomic::Ordering::SeqCst)
            {
                return;
            }

            if quick_health_probe(&inner, LIVENESS_PROBE_TIMEOUT).await {
                consecutive_failures = 0;
                continue;
            }

            consecutive_failures += 1;
            if consecutive_failures < LIVENESS_FAILURE_THRESHOLD {
                continue;
            }

            // Phase 7: tripped. Try auto-restart up to
            // LIVENESS_MAX_AUTO_RESTARTS before giving up.
            if auto_restarts_used < LIVENESS_MAX_AUTO_RESTARTS {
                auto_restarts_used += 1;
                let win = app.get_window("main");
                emit_with_buffer(
                    &inner,
                    win.as_ref(),
                    format!(
                        "[Sidecar] Lost connection. Auto-restarting (attempt {} of {})...",
                        auto_restarts_used, LIVENESS_MAX_AUTO_RESTARTS
                    ),
                );

                // Tear down the old child + clear the slot so the
                // gate helper sees a clean state. We do NOT flip
                // sidecar_startup_failed here -- that's reserved
                // for "give up entirely".
                if let Ok(mut slot) = inner.sidecar.lock() {
                    *slot = None;
                }
                stop_sidecar_inner(win.as_ref(), &inner);

                // Spawn the helper on a blocking thread so we don't
                // tie up the runtime worker for up to ~120s.
                let app_clone = app.clone();
                let join_result = tokio::task::spawn_blocking(move || {
                    try_start_sidecar_with_retries_and_gate(&app_clone)
                })
                .await;
                let res = match join_result {
                    Ok(r) => r,
                    Err(e) => Err(format!("auto-restart worker panicked: {}", e)),
                };

                match res {
                    Ok(()) => {
                        emit_with_buffer(
                            &inner,
                            app.get_window("main").as_ref(),
                            format!(
                                "[Sidecar] Auto-restart succeeded ({} of {} used).",
                                auto_restarts_used, LIVENESS_MAX_AUTO_RESTARTS
                            ),
                        );
                        consecutive_failures = 0;
                        continue;
                    }
                    Err(e) => {
                        emit_with_buffer(
                            &inner,
                            app.get_window("main").as_ref(),
                            format!("[Sidecar] Auto-restart attempt failed: {}", e),
                        );
                        // Fall through to the give-up branch below
                        // by NOT continuing -- consecutive_failures
                        // stays >= threshold so we either retry on
                        // the next loop iteration (if budget left)
                        // or give up.
                        continue;
                    }
                }
            }

            // Auto-restart budget exhausted: latch the failure flag
            // so subsequent invokes fail fast, clear the slot, and
            // emit the actionable user-facing line.
            inner
                .sidecar_startup_failed
                .store(true, std::sync::atomic::Ordering::SeqCst);
            if let Ok(mut slot) = inner.sidecar.lock() {
                *slot = None;
            }
            let win = app.get_window("main");
            emit_with_buffer(
                &inner,
                win.as_ref(),
                format!(
                    "[Sidecar] Lost connection -- /health stopped responding after {} auto-restart attempts. Click Restart Sidecar (Settings -> Runtime), or relaunch the app.",
                    LIVENESS_MAX_AUTO_RESTARTS
                ),
            );
            // Phase 6: record a structured ErrorEntry so the
            // bundle reflects the dropped session, not just
            // the terminal_update line.
            let snap = inner
                .last_launch_report
                .lock()
                .ok()
                .and_then(|g| g.as_ref().cloned());
            record_startup_failure(
                &inner,
                format!(
                    "Sidecar liveness watch tripped: /health failed {} consecutive times AND auto-restart budget ({}) exhausted.",
                    LIVENESS_FAILURE_THRESHOLD, LIVENESS_MAX_AUTO_RESTARTS
                ),
                snap.as_ref(),
            );
            return;
        }
    });
}

async fn api_delete_with(inner: &Arc<AppStateInner>, path: &str) -> Result<Value, String> {
    let api = wait_for_sidecar(inner).await?;
    let url = format!("{}{}", api.base_url, path);

    let res = inner
        .http
        .delete(url)
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

// ---------------------------
// SIDECAR-OWNED JOB SUBMISSION (MVP-3c)
// ---------------------------
//
// Submits a job to the sidecar's /jobs endpoint and bridges its
// log buffer to terminal_update via polling. Returns immediately
// after the job_id is registered; the live log + terminal-status
// flow happens on a background thread.
//
// Why polling instead of SSE:
//   reqwest's bytes_stream support requires extra feature flags
//   and complex line-decoding. Polling /jobs/{id}/log every 500ms
//   keeps Rust-side complexity flat -- recording / training scripts
//   print at most a few times per second, so latency is invisible.
//
// As of MVP-3d, every user-facing Python spawn (collect_data,
// train_model, test_model) goes through this helper. The legacy
// local-spawn path (run_python_script) was removed once the
// traceback-parsing state machine had been ported to the log-bridge
// worker so AI Fix Bundle capture would not regress.
/// Metadata forwarded to the log-bridge worker so it can emit a
/// `training_finalized` event when a training job finishes successfully.
/// Only `start_training` populates this; every other caller passes None.
#[derive(Clone, Debug)]
struct TrainingFinalizeMeta {
    game_id: String,
    model_name: String,
    out_dir: String,
}

async fn submit_sidecar_job(
    inner: &Arc<AppStateInner>,
    window: &Window,
    kind: &str,
    argv: Vec<String>,
    env: serde_json::Map<String, Value>,
    cwd: Option<String>,
    training_meta: Option<TrainingFinalizeMeta>,
) -> Result<String, String> {
    // Cancel any previously-running sidecar job before we register
    // ours. This matches the legacy run_python_script behaviour
    // (calls stop_process_inner before each spawn) so a user
    // clicking Start a second time always replaces, never doubles
    // up. Read+take under the lock so two concurrent submissions
    // can't both think they own the slot.
    let prev = inner.current_sidecar_job.lock().unwrap().take();
    if let Some(prev_job_id) = prev {
        let path = format!("/jobs/{}", prev_job_id);
        if let Err(e) = api_delete_with(inner, &path).await {
            // Soft fail: the cancel is a courtesy, not a contract.
            // The runner will just have two jobs; only ours is the
            // user-visible "current" one.
            let _ = window.emit::<String>(
                "terminal_update",
                format!(
                    "[Sidecar] Could not cancel prior job {} before submitting new one: {}",
                    prev_job_id, e
                ),
            );
        }
    }

    let payload = json!({
        "kind": kind,
        "argv": argv,
        "env": env,
        "cwd": cwd,
    });

    let resp = api_post_with(inner, "/jobs", payload).await?;
    let job_id = resp
        .get("job")
        .and_then(|j| j.get("job_id"))
        .and_then(|v| v.as_str())
        .map(|s| s.to_string())
        .ok_or_else(|| "Sidecar returned no job_id".to_string())?;

    *inner.current_sidecar_job.lock().unwrap() = Some(job_id.clone());

    let _ = window.emit::<String>(
        "terminal_update",
        format!("[Sidecar] Submitted job {} (kind={})", job_id, kind),
    );

    spawn_log_bridge_worker(window.clone(), inner.clone(), job_id.clone(), training_meta);
    Ok(job_id)
}

/// Background worker that polls the sidecar for log lines + status
/// transitions and forwards them to the UI via terminal_update.
///
/// The worker exits when the job reaches a terminal status
/// ("completed" / "failed" / "cancelled"). On exit it clears the
/// inner.current_sidecar_job slot so a follow-up Start can register
/// a new job cleanly.
fn spawn_log_bridge_worker(
    window: Window,
    inner: Arc<AppStateInner>,
    job_id: String,
    training_meta: Option<TrainingFinalizeMeta>,
) {
    use std::time::Duration as StdDuration;
    tauri::async_runtime::spawn(async move {
        let mut last_seen = 0usize;
        let poll_interval = StdDuration::from_millis(500);
        // Traceback parser state. Mirrors the run_python_script
        // stderr-reader thread so AI-Fix-Bundle traceback capture
        // is not lost when scripts spawn via the sidecar.
        let mut in_tb = false;
        let mut tb_buf = String::new();
        // Best-effort attribution for parse_python_traceback. The
        // sidecar /jobs/{id} response carries argv, but at this
        // worker's scope we don't have it -- store the empty path
        // and let the parser fall back to a generic label.
        let script_for_tb = format!("[sidecar-job:{}]", job_id);
        loop {
            // 1. Pull new log lines.
            let log_path = format!("/jobs/{}/log", job_id);
            if let Ok(body) = api_get_with(&inner, &log_path).await {
                if let Some(lines) = body.get("lines").and_then(|v| v.as_array()) {
                    for line in lines.iter().skip(last_seen) {
                        let stream =
                            line.get("stream").and_then(|v| v.as_str()).unwrap_or("stdout");
                        let text = line.get("text").and_then(|v| v.as_str()).unwrap_or("");
                        let prefix = if stream == "stderr" { "(stderr) " } else { "" };
                        let _ = window.emit::<String>(
                            "terminal_update",
                            format!("{}{}", prefix, text),
                        );

                        // Traceback state machine -- only stderr lines
                        // can start or terminate a traceback. Mirrors
                        // the legacy run_python_script logic exactly.
                        if stream == "stderr" {
                            if text.trim_start().starts_with("Traceback (most recent call last):") {
                                in_tb = true;
                                tb_buf.clear();
                            }
                            if in_tb {
                                tb_buf.push_str(text);
                                tb_buf.push('\n');
                                let raw = text.trim_end();
                                let is_indented = raw.starts_with(' ') || raw.starts_with('\t');
                                if !is_indented && !raw.is_empty() {
                                    if let Some((etype, _)) = raw.split_once(": ") {
                                        if etype
                                            .chars()
                                            .next()
                                            .map_or(false, |c| c.is_ascii_uppercase())
                                        {
                                            let entry = parse_python_traceback(&tb_buf, &script_for_tb);
                                            record_error(&inner, entry);
                                            in_tb = false;
                                            tb_buf.clear();
                                        }
                                    }
                                }
                            }
                        }
                    }
                    last_seen = lines.len();
                }
            }

            // 2. Check terminal status.
            let status_path = format!("/jobs/{}", job_id);
            let status_body = api_get_with(&inner, &status_path).await;
            let job = status_body.as_ref().ok().and_then(|b| b.get("job"));
            if let Some(job) = job {
                let status = job
                    .get("status")
                    .and_then(|v| v.as_str())
                    .unwrap_or("running");
                if matches!(status, "completed" | "failed" | "cancelled") {
                    let exit_code = job
                        .get("exit_code")
                        .and_then(|v| v.as_i64())
                        .map(|n| n.to_string())
                        .unwrap_or_else(|| "?".to_string());
                    let _ = window.emit::<String>(
                        "terminal_update",
                        format!(
                            "[Sidecar] Job {} -> {} (exit_code={})",
                            job_id, status, exit_code
                        ),
                    );
                    // Capture a stranded traceback (process died mid-tb).
                    if in_tb && !tb_buf.is_empty() {
                        let entry = parse_python_traceback(&tb_buf, &script_for_tb);
                        record_error(&inner, entry);
                    }

                    // Phase 30: training-job finalization. When a training
                    // job completes successfully, tell the UI which model
                    // is now on disk so the ModelHub view can auto-refresh
                    // and pre-select the just-trained candidate. Mirrors
                    // the `recording_finalized` pattern (see stop_process)
                    // so the post-train UX is symmetric with post-record.
                    // Auto-select = YES, auto-activate = NO -- the JS
                    // listener only refreshes + highlights; the user must
                    // still click "Set Active".
                    if status == "completed" {
                        if let Some(meta) = training_meta.as_ref() {
                            let payload = json!({
                                "game_id": meta.game_id,
                                "model_name": meta.model_name,
                                "model_dir": meta.out_dir,
                                "job_id": job_id,
                            });
                            let _ = window.emit("training_finalized", payload);
                        }
                    }

                    // Clear the slot only if the job we owned is still
                    // the one stored. A user could theoretically have
                    // started a fresh job while we were polling.
                    let mut slot = inner.current_sidecar_job.lock().unwrap();
                    if slot.as_deref() == Some(job_id.as_str()) {
                        *slot = None;
                    }
                    break;
                }
            }
            tokio::time::sleep(poll_interval).await;
        }
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

/// Tauri command: drain the pre-listener `early_log` ring buffer.
///
/// The JS calls this once, immediately after attaching its
/// `listen("terminal_update")` handler in `wireBackendEvents`.
/// Returns the buffered lines (in emission order) and clears the
/// buffer, so subsequent calls return nothing -- no double-logging
/// on hot reload or restart_sidecar follow-ups.
///
/// Without this command, the most diagnostic startup lines
/// ([Sidecar stderr] tracebacks, [Fatal]/[Hint] blocks, the
/// "still warming up..." heartbeats) never reach the user, because
/// they are emitted from `setup()` BEFORE the WebView attaches its
/// listener and Tauri 1.x has no event buffering.
#[tauri::command]
async fn drain_early_log(state: tauri::State<'_, AppState>) -> Result<Vec<String>, String> {
    let mut buf = state
        .inner
        .early_log
        .lock()
        .map_err(|e| format!("early_log lock poisoned: {}", e))?;
    let drained: Vec<String> = buf.drain(..).collect();
    Ok(drained)
}

/// Tauri command: tear down the current sidecar and spawn a fresh one
/// without restarting the whole app. Wired to the UI's "Restart Sidecar"
/// button on the dashboard status chip and in Settings -> Runtime.
///
/// Without this command, a user who hits a sidecar startup failure (cold
/// disk + AV scan timing out the 60s budget) had no recourse but to
/// fully quit and relaunch the app.
#[tauri::command]
async fn restart_sidecar(
    state: tauri::State<'_, AppState>,
    app: AppHandle,
    window: Window,
) -> Result<String, String> {
    let _ = window.emit::<String>(
        "terminal_update",
        "[System] Restart sidecar requested...".to_string(),
    );

    // Tear down whatever's there. Both the slot and the Child handle.
    {
        let mut slot = state.inner.sidecar.lock().unwrap();
        *slot = None;
    }
    stop_sidecar_inner(Some(&window), &state.inner);

    // Clear the failure flag so wait_for_sidecar will poll again
    // (otherwise it'd fail-fast immediately on the leftover flag).
    state
        .inner
        .sidecar_startup_failed
        .store(false, std::sync::atomic::Ordering::SeqCst);

    // Phase 7: route restart through the same retry-and-gate
    // helper used by setup(). Spawned on a blocking thread because
    // the helper is sync and we are inside an async fn; a direct
    // call would block the runtime worker thread for up to 120s.
    let app_clone = app.clone();
    let join_result = tokio::task::spawn_blocking(move || {
        try_start_sidecar_with_retries_and_gate(&app_clone)
    })
    .await;
    let result = match join_result {
        Ok(r) => r,
        Err(e) => Err(format!("restart worker panicked: {}", e)),
    };

    match result {
        Ok(()) => {
            let _ = window.emit::<String>(
                "terminal_update",
                "[System] Sidecar READY (restart succeeded).".to_string(),
            );
            // Phase 3.2: re-arm the liveness watch on the new
            // sidecar. The previous task self-terminated when it
            // saw the slot cleared during teardown above.
            spawn_sidecar_liveness_watch(app.clone());
            // Phase 4: refresh the launch report's /health probe
            // result so the debug bundle reflects this restart.
            let inner_clone = state.inner.clone();
            tauri::async_runtime::spawn(async move {
                record_post_launch_health(inner_clone).await;
            });
            Ok("Sidecar restarted.".to_string())
        }
        Err(e) => {
            // The helper has already flipped sidecar_startup_failed
            // and emitted per-attempt detail; just surface the
            // top-line error to the user.
            let _ = window.emit::<String>(
                "terminal_update",
                format!("[Fatal] Sidecar restart failed: {}", e),
            );
            Err(e)
        }
    }
}

/// Tauri command: open the user's local-data root in Explorer / Finder.
/// Wired to the "Open Logs Folder" button. Surfaces the layout (runtime,
/// datasets, models, logs) so the user can inspect on-disk state.
#[tauri::command]
async fn open_local_data_folder(
    app: AppHandle,
    window: Window,
) -> Result<String, String> {
    let root = local_data_root(&app);
    let _ = std::fs::create_dir_all(&root);
    let path = root.display().to_string();

    #[cfg(target_os = "windows")]
    {
        std::process::Command::new("explorer.exe")
            .arg(&path)
            .spawn()
            .map_err(|e| format!("Failed to launch Explorer: {}", e))?;
    }
    #[cfg(target_os = "macos")]
    {
        std::process::Command::new("open")
            .arg(&path)
            .spawn()
            .map_err(|e| format!("Failed to launch Finder: {}", e))?;
    }
    #[cfg(all(not(target_os = "windows"), not(target_os = "macos")))]
    {
        std::process::Command::new("xdg-open")
            .arg(&path)
            .spawn()
            .map_err(|e| format!("Failed to launch file manager: {}", e))?;
    }

    let _ = window.emit::<String>(
        "terminal_update",
        format!("[System] Opened: {}", path),
    );
    Ok(format!("Opened {}", path))
}

/// Phase 28: open the per-game datasets folder in the OS file
/// browser. Wired to the Train tab dataset dropdown's "Open
/// datasets folder" action so the user can inspect/manage the
/// archived recordings without leaving the app. We resolve the
/// path the same way the sidecar does (`<local_data_root>/datasets/
/// <game_id>/`) and create it if missing so the user never lands
/// in "folder doesn't exist" purgatory just because they haven't
/// recorded yet.
#[tauri::command]
async fn open_datasets_folder(
    app: AppHandle,
    window: Window,
    game_id: Option<String>,
) -> Result<String, String> {
    let gid = normalize_game_id(game_id);
    let root = local_data_root(&app).join("datasets").join(&gid);
    let _ = std::fs::create_dir_all(&root);
    let path = root.display().to_string();

    #[cfg(target_os = "windows")]
    {
        std::process::Command::new("explorer.exe")
            .arg(&path)
            .spawn()
            .map_err(|e| format!("Failed to launch Explorer: {}", e))?;
    }
    #[cfg(target_os = "macos")]
    {
        std::process::Command::new("open")
            .arg(&path)
            .spawn()
            .map_err(|e| format!("Failed to launch Finder: {}", e))?;
    }
    #[cfg(all(not(target_os = "windows"), not(target_os = "macos")))]
    {
        std::process::Command::new("xdg-open")
            .arg(&path)
            .spawn()
            .map_err(|e| format!("Failed to launch file manager: {}", e))?;
    }

    let _ = window.emit::<String>(
        "terminal_update",
        format!("[System] Opened datasets folder: {}", path),
    );
    Ok(format!("Opened {}", path))
}

/// Tauri command: spawn an elevated PowerShell that adds the runtime
/// folder to Microsoft Defender exclusions. Wired to the "Add AV
/// Exclusion" button on the sidecar-failed banner.
///
/// We don't execute Add-MpPreference ourselves because it requires
/// admin; instead we shell out to `powershell -Verb RunAs` which
/// triggers UAC. The user accepts/declines; we don't see the result.
/// Returns the exact command we ran so the user can re-run manually
/// if UAC was declined.
#[tauri::command]
async fn add_av_exclusion(
    app: AppHandle,
    window: Window,
) -> Result<String, String> {
    let runtime_root = local_data_root(&app).join("runtime");
    let path_str = runtime_root.display().to_string();

    #[cfg(target_os = "windows")]
    {
        // Single-quote the path inside the inner script so embedded
        // backslashes don't need escaping. The outer Start-Process
        // launches a UAC-elevated PowerShell that runs Add-MpPreference.
        let inner = format!(
            "Add-MpPreference -ExclusionPath '{}'",
            path_str.replace('\'', "''")
        );
        let outer = format!(
            "Start-Process powershell -Verb RunAs -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-Command','{}')",
            inner.replace('\'', "''")
        );
        std::process::Command::new("powershell")
            .args(["-NoProfile", "-Command", &outer])
            .spawn()
            .map_err(|e| format!("Failed to launch elevated PowerShell: {}", e))?;
        let _ = window.emit::<String>(
            "terminal_update",
            format!(
                "[System] Requested AV exclusion for {} (UAC prompt -- accept to apply).",
                path_str
            ),
        );
        Ok(format!(
            "Triggered UAC prompt to exclude {} from Microsoft Defender.",
            path_str
        ))
    }
    #[cfg(not(target_os = "windows"))]
    {
        let _ = window.emit::<String>(
            "terminal_update",
            "[System] add_av_exclusion is Windows-only; no-op on this platform.".to_string(),
        );
        Ok("AV exclusion only applies on Windows.".to_string())
    }
}

/// Tauri command: re-extract the bundled python-runtime.zip over the
/// existing %LOCALAPPDATA%\com.bot.mmorpg.ai\runtime\py\ tree. Wired to
/// the "Repair Runtime" button. Catches AV-quarantine and partial-
/// extraction recoveries without a full reinstall.
///
/// The actual heavy lifting is in ensure_python_env, which is idempotent
/// and re-runs the extraction if the runtime directory is missing or
/// the marker file is older than the bundled zip. Calling it explicitly
/// (under the `force` flag this command sets) re-extracts unconditionally.
#[tauri::command]
async fn repair_runtime(
    app: AppHandle,
    window: Window,
) -> Result<String, String> {
    let _ = window.emit::<String>(
        "terminal_update",
        "[System] Repair Runtime: re-extracting python-runtime.zip...".to_string(),
    );

    // Force re-extraction by removing the marker file ensure_python_env
    // uses to short-circuit. Don't remove the actual python tree --
    // ensure_python_env will overwrite as needed and a partial state is
    // safer than a deleted-and-failed-to-extract one.
    let runtime_dir = managed_python_root(&app).join("python");
    let marker = runtime_dir.join(".bot_extract_marker");
    let _ = std::fs::remove_file(&marker);

    match ensure_python_env(&app, &window) {
        Ok(py) => {
            let _ = window.emit::<String>(
                "terminal_update",
                format!("[System] Repair Runtime: OK -- python at {}", py.display()),
            );
            Ok(format!("Runtime repaired. Python: {}", py.display()))
        }
        Err(e) => {
            let _ = window.emit::<String>(
                "terminal_update",
                format!("[Fatal] Repair Runtime failed: {}", e),
            );
            Err(e)
        }
    }
}

/// Tauri command: deepest-recovery option for the bug-#9-style failure
/// where torch/testing or numpy/testing is missing on disk despite
/// torch/numpy themselves being importable. Downloads fresh wheels
/// from PyPI's PyTorch CPU index using the bundled python.exe + the
/// bundled pip, force-reinstalling without touching dependencies.
///
/// Why this exists alongside repair_runtime:
///   - repair_runtime re-extracts python-runtime.zip. If the zip
///     itself is incomplete (built before MVP-4), repair has nothing
///     better to extract.
///   - repair_pytorch_via_pip downloads fresh torch / torchvision /
///     numpy directly from upstream, bypassing both the bundled zip
///     AND any antivirus product that's quarantining specific
///     subdirectories during extraction (pip writes to a temp dir
///     first, then atomic-renames -- AV often gives that pattern a
///     pass where a raw zip extraction trips heuristics).
///
/// Slow (downloads ~250 MB on cold cache) so wired to a separate
/// button so users don't trigger it accidentally. Streams pip output
/// to terminal_update so the operator sees progress.
#[tauri::command]
async fn repair_pytorch_via_pip(
    app: AppHandle,
    window: Window,
) -> Result<String, String> {
    let py = managed_embedded_python_dir(&app)
        .join(if is_windows() { "python.exe" } else { "bin/python3" });
    if !py.exists() {
        return Err(format!(
            "Bundled python.exe not found at {}. Run Repair Runtime first.",
            py.display()
        ));
    }

    let _ = window.emit::<String>(
        "terminal_update",
        "[System] Repair PyTorch via pip: downloading fresh torch + torchvision + numpy wheels...".to_string(),
    );
    let _ = window.emit::<String>(
        "terminal_update",
        "[System] This is the deepest recovery option. May take 2-5 minutes on first run.".to_string(),
    );

    // We run three pip invocations:
    //   1. torch + torchvision from PyTorch's CPU wheel index
    //   2. numpy from default PyPI
    //   3. fastapi + uvicorn (sidecar HTTP API deps) from default PyPI
    //
    // Issue #58 / #26: when the bundled python-runtime.zip is missing
    // or partially extracted (AV quarantine, antivirus heuristics on
    // typing_inspection, etc.) the sidecar refuses to start with
    // `No module named 'uvicorn'`. The original repair_pytorch_via_pip
    // only touched torch/torchvision/numpy, leaving fastapi+uvicorn
    // broken even after the user clicked the button -- so the sidecar
    // stayed red. Reinstalling the backend stack from pip here turns
    // this into a one-click fix.
    //
    // All three runs use --force-reinstall --no-deps so the existing
    // site-packages tree is preserved and only the targeted packages
    // are rewritten. We install fastapi/uvicorn WITH their transitive
    // deps because they pull in a handful of small pure-python pieces
    // (starlette, pydantic, h11, click, anyio) that the bundled
    // runtime may also be missing alongside the top-level package.
    let runs: &[(&str, Vec<&str>)] = &[
        (
            "torch+torchvision",
            vec![
                "-m", "pip", "install",
                "--upgrade", "--force-reinstall", "--no-deps",
                "--index-url", "https://download.pytorch.org/whl/cpu",
                "torch", "torchvision",
            ],
        ),
        (
            "numpy",
            vec![
                "-m", "pip", "install",
                "--upgrade", "--force-reinstall", "--no-deps",
                "numpy",
            ],
        ),
        (
            "fastapi+uvicorn",
            vec![
                "-m", "pip", "install",
                "--upgrade", "--force-reinstall",
                "fastapi", "uvicorn[standard]",
            ],
        ),
    ];

    for (label, args) in runs {
        let _ = window.emit::<String>(
            "terminal_update",
            format!("[System] pip install {} ...", label),
        );
        let mut cmd = Command::new(&py);
        apply_stable_python_env(&mut cmd);
        for a in args {
            cmd.arg(a);
        }
        cmd.stdout(Stdio::piped());
        cmd.stderr(Stdio::piped());
        #[cfg(target_os = "windows")]
        {
            use std::os::windows::process::CommandExt;
            const CREATE_NO_WINDOW: u32 = 0x08000000;
            cmd.creation_flags(CREATE_NO_WINDOW);
        }

        let output = cmd.output().map_err(|e| {
            format!("Failed to spawn pip for {}: {}", label, e)
        })?;
        let stdout_str = String::from_utf8_lossy(&output.stdout);
        let stderr_str = String::from_utf8_lossy(&output.stderr);
        // Forward the last 20 lines of each to the UI so the operator
        // can see what happened without having to crack open the log.
        for line in stdout_str.lines().rev().take(20).collect::<Vec<_>>().into_iter().rev() {
            let _ = window.emit::<String>("terminal_update", format!("(pip stdout) {}", line));
        }
        for line in stderr_str.lines().rev().take(10).collect::<Vec<_>>().into_iter().rev() {
            let _ = window.emit::<String>("terminal_update", format!("(pip stderr) {}", line));
        }
        if !output.status.success() {
            let msg = format!(
                "pip install {} failed with exit {}. See (pip stderr) lines above.",
                label,
                output.status.code().map(|c| c.to_string()).unwrap_or_else(|| "?".to_string())
            );
            let _ = window.emit::<String>("terminal_update", format!("[Fatal] {}", msg));
            return Err(msg);
        }
        let _ = window.emit::<String>(
            "terminal_update",
            format!("[System] pip install {}: OK", label),
        );
    }

    let _ = window.emit::<String>(
        "terminal_update",
        "[System] Repair PyTorch via pip: COMPLETE. Re-run the doctor to verify.".to_string(),
    );
    Ok("torch + torchvision + numpy reinstalled. Re-run the doctor to verify.".to_string())
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
    // Phase 23-A: defense-in-depth -- auto-generate the same
    // server-side default the preflight uses so that even a caller
    // that bypasses preflight (older JS, programmatic test) gets a
    // valid recording dir. Was previously falling back to "Untitled"
    // which wasn't path-safe and would collide on every retry.
    let raw = dataset_name.unwrap_or_default();
    let trimmed_raw = raw.trim();
    let name: String = if trimmed_raw.is_empty() {
        let auto = format!("{}_session_{}", gid.replace('_', "-"), unix_now_ms());
        let _ = window.emit::<String>(
            "terminal_update",
            format!("[Sidecar] Dataset name was empty -- auto-generated: {}", auto),
        );
        auto
    } else {
        trimmed_raw.to_string()
    };
    let cap_mouse = capture_mouse.unwrap_or(false);
    let inner = state.inner.clone();

    // Sidecar bookkeeping is best-effort. If the sidecar is offline,
    // submitting the actual collect_data.py job below will fail too --
    // we surface that in the same flow rather than two separate banners.
    if let Err(_e) = api_post_with(
        &inner,
        "/session/begin_recording",
        json!({"game_id": gid, "dataset_name": name, "capture_mouse": cap_mouse}),
    )
    .await
    {
        let _ = window.emit::<String>(
            "terminal_update",
            "[Sidecar] Session metadata not recorded (sidecar offline). Recording will still start."
                .to_string(),
        );
    }

    // MVP-3d: spawn collect_data.py via the sidecar's /jobs endpoint
    // instead of locally. Crashes in the recording script are now
    // contained inside the sidecar's process tree; the Tauri UI never
    // sees a 0xC0000005 from a misbehaving torch import.
    //
    // Mouse-capture preference: passed as env on the spawned child,
    // not via std::env::set_var on the Tauri process. The latter
    // mutated *Tauri's* env which leaked across recordings (a
    // followup recording with capture_mouse=false would still see
    // BOTMMO_CAPTURE_MOUSE=true if the previous one set it). The
    // sidecar-job env is per-spawn, no leak.
    let mut extra_env = serde_json::Map::new();
    extra_env.insert(
        "BOTMMO_CAPTURE_MOUSE".to_string(),
        Value::String(if cap_mouse { "true" } else { "false" }.to_string()),
    );

    // Tell collect_data.py exactly where to write. Without --out it
    // defaults to "data/raw" (relative to cwd=data_root), which lands
    // outside the `datasets/<gid>/<name>/` layout that
    // SessionManager.finalize_recording, _scan_datasets_fs, and the
    // Train tab's dataset list all look at. End result: recording
    // "succeeds" but no dataset ever appears in the UI (issues #57,
    // #60). Pin the output to the same path the preflight already
    // reserves at src-tauri/src/main.rs:4863 so the recording, the
    // session bookkeeping, and the dataset listing all agree.
    let dataset_out = local_data_root(&app)
        .join("datasets")
        .join(&gid)
        .join(&name);
    let dataset_out_s = dataset_out.display().to_string();
    let mut cmd = build_python_script_command(
        &app,
        "1-collect_data.py",
        &["--out", &dataset_out_s],
        &window,
    )?;
    for (k, v) in extra_env {
        cmd.env.insert(k, v);
    }
    let job_id = submit_sidecar_job(
        &inner,
        &window,
        "collect",
        cmd.argv,
        cmd.env,
        Some(cmd.cwd),
        None,
    )
    .await?;
    Ok(format!("Started collect_data job {}", job_id))
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
    let local_root = local_data_root(&app);
    let data_dir = local_root.join("datasets").join(&gid).join(did.trim());
    let out_dir = local_root.join("trained_models").join(&gid).join(mname.trim());
    let data_dir_s = data_dir.display().to_string();
    let out_dir_s = out_dir.display().to_string();
    let inner = state.inner.clone();

    // Same fail-soft pattern as start_recording.
    if let Err(_e) = api_post_with(
        &inner,
        "/session/begin_training",
        json!({
            "game_id": gid,
            "model_name": mname,
            "dataset_id": did,
            "arch": a,
            "out_dir": out_dir_s.clone()
        }),
    )
    .await
    {
        let _ = window.emit::<String>(
            "terminal_update",
            "[Sidecar] Session metadata not recorded (sidecar offline). Training will still start."
                .to_string(),
        );
    }

    // MVP-3d: train_model.py also runs via the sidecar now. The 0xC0000005
    // teardown crash that motivated the migration was specifically a
    // training-time failure mode (torch._C native shutdown race after a
    // half-loaded torch.testing import). Containing it inside the
    // sidecar's process tree means the UI keeps responding even when
    // training crashes mid-run.
    let job_id = start_python_script_via_sidecar(
        &app,
        &inner,
        &window,
        "train",
        "2-train_model.py",
        &[
            "--data",
            &data_dir_s,
            "--out",
            &out_dir_s,
            "--model",
            &a,
        ],
        // Phase 30: forward enough metadata so the log-bridge worker can
        // emit a `training_finalized` event when the job completes.
        // The UI listens and auto-refreshes ModelHub, pre-selecting
        // this freshly trained model as the LATEST candidate.
        Some(TrainingFinalizeMeta {
            game_id: gid.clone(),
            model_name: mname.clone(),
            out_dir: out_dir_s.clone(),
        }),
    )
    .await?;
    Ok(format!("Started train_model job {}", job_id))
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

    let active = catalog
        .get("active")
        .and_then(|v| if v.is_null() { None } else { Some(v) })
        .ok_or_else(|| {
            format!(
                "No active model set for '{}'. Open ModelHub, pick a trained model, \
                 click 'Set Active', then start the bot.",
                gid
            )
        })?;

    // Phase 31: resolve model_dir -> concrete checkpoint file.
    //
    // 3-test_model.py declares --model as a `.pth` file path
    // (versions/0.01/3-test_model.py:502) and torch.load() opens it
    // with the file API. Passing a directory yields
    //   [Errno 13] Permission denied: '...\\New Model'
    // on Windows. mh_set_active_model historically stored the
    // training-output directory under the `model_dir` key, so every
    // existing active_model.json is broken without this resolver.
    //
    // Resolution priority (matches the script's docstring example
    // at 3-test_model.py:8-9 which prefers `_best.pth`):
    //   1. active.model_file        -- explicit override from UI/registry
    //   2. <dir>/*_best.pth         -- best validation snapshot
    //   3. <dir>/*_final.pth        -- last-epoch weights
    //   4. <dir>/*.pth (newest mtime)
    //
    // If `model_dir` already points at a `.pth`, use it verbatim.
    let active_dir = active
        .get("model_dir")
        .and_then(|m| m.as_str())
        .map(|s| s.to_string());
    let active_file = active
        .get("model_file")
        .and_then(|m| m.as_str())
        .filter(|s| !s.is_empty())
        .map(|s| s.to_string());

    let model_path = match resolve_checkpoint_path(active_file.as_deref(), active_dir.as_deref()) {
        Ok(p) => p,
        Err(e) => {
            return Err(format!(
                "Cannot start bot: {} \
                 Train a model in Train Brain (it writes <name>_best.pth and \
                 <name>_final.pth into the model folder), then re-activate it \
                 in ModelHub.",
                e
            ));
        }
    };

    let _ = window.emit::<String>(
        "terminal_update",
        format!("[Inference] Using checkpoint: {}", model_path),
    );

    // MVP-3d: route inference (3-test_model.py) through the sidecar's
    // /jobs endpoint too. start_bot was the most-likely-to-crash of the
    // three commands historically (it loads the trained model into
    // torch and hits the same 0xC0000005 class of failures on broken
    // installs). Keeping it on the legacy local-spawn path while the
    // others used the sidecar would have left exactly that failure
    // mode propagating to the UI.
    let job_id = start_python_script_via_sidecar(
        &app,
        &inner,
        &window,
        "inference",
        "3-test_model.py",
        &["--model", &model_path],
        None,
    )
    .await?;
    Ok(format!("Started test_model job {}", job_id))
}

/// Resolve the active model's path to a concrete `.pth` checkpoint
/// file that `3-test_model.py --model` can torch.load().
///
/// This is the production fix for the "Permission denied: '...\\New Model'"
/// inference error: ModelHub stores the training-output **directory**
/// as the active path, but the inference script needs a **file**.
///
/// Tries in order:
///   1. `explicit_file` if non-None and points at an existing file
///   2. If `dir` is itself a `.pth` file, use it verbatim
///   3. Inside `dir`, prefer `*_best.pth` (lowest val_loss snapshot;
///      matches the script's documented example), then `*_final.pth`
///      (last-epoch weights), then the newest `*.pth` by mtime.
///
/// Returns a user-friendly error string when no checkpoint can be
/// resolved -- the caller wraps it with the "train one in Train Brain"
/// hint so the message is actionable, not stack-trace-ish.
fn resolve_checkpoint_path(
    explicit_file: Option<&str>,
    dir: Option<&str>,
) -> Result<String, String> {
    use std::path::Path;

    if let Some(f) = explicit_file {
        let p = Path::new(f);
        if p.is_file() {
            return Ok(f.to_string());
        }
        // Fall through: explicit file was set but doesn't exist on
        // disk anymore (model deleted, drive remounted, ...). Try the
        // directory fallback rather than failing on the registry's
        // stale pointer.
    }

    let dir_str = dir.ok_or_else(|| "active model has no path on disk.".to_string())?;
    let dir_path = Path::new(dir_str);

    if dir_path.is_file() {
        // Some old configs may have stored a file path directly under
        // model_dir. Honour that.
        if dir_path.extension().and_then(|s| s.to_str()) == Some("pth") {
            return Ok(dir_str.to_string());
        }
        return Err(format!(
            "active model path '{}' is a file but not a .pth checkpoint.",
            dir_str
        ));
    }

    if !dir_path.is_dir() {
        return Err(format!(
            "active model path '{}' does not exist on disk.",
            dir_str
        ));
    }

    let entries = std::fs::read_dir(dir_path)
        .map_err(|e| format!("cannot read active model folder '{}': {}", dir_str, e))?;

    let mut best: Option<std::path::PathBuf> = None;
    let mut final_: Option<std::path::PathBuf> = None;
    let mut newest: Option<(std::path::PathBuf, std::time::SystemTime)> = None;

    for entry in entries.flatten() {
        let p = entry.path();
        if !p.is_file() {
            continue;
        }
        if p.extension().and_then(|s| s.to_str()) != Some("pth") {
            continue;
        }
        let name = match p.file_name().and_then(|s| s.to_str()) {
            Some(n) => n.to_string(),
            None => continue,
        };
        // First match wins per category, but we still scan everything
        // so the "newest" branch sees every file.
        if best.is_none() && name.ends_with("_best.pth") {
            best = Some(p.clone());
        } else if final_.is_none() && name.ends_with("_final.pth") {
            final_ = Some(p.clone());
        }
        if let Ok(meta) = entry.metadata() {
            if let Ok(mtime) = meta.modified() {
                match &newest {
                    Some((_, t)) if *t >= mtime => {}
                    _ => newest = Some((p.clone(), mtime)),
                }
            }
        }
    }

    if let Some(p) = best {
        return Ok(p.to_string_lossy().into_owned());
    }
    if let Some(p) = final_ {
        return Ok(p.to_string_lossy().into_owned());
    }
    if let Some((p, _)) = newest {
        return Ok(p.to_string_lossy().into_owned());
    }

    Err(format!(
        "active model folder '{}' has no .pth checkpoint -- training never produced one.",
        dir_str
    ))
}

/// Tauri command wrapper around submit_sidecar_job (MVP-3c).
///
/// Submits an arbitrary command line to the sidecar's /jobs endpoint
/// and returns the job_id. The log-bridge worker then forwards
/// stdout/stderr to terminal_update and clears the slot when the job
/// reaches a terminal status. As of MVP-3d the existing start_recording /
/// start_training / start_bot commands all use this path; this Tauri
/// command stays in place so the round-trip can also be exercised
/// directly from the devtools console.
#[tauri::command]
async fn submit_sidecar_job_cmd(
    state: tauri::State<'_, AppState>,
    window: Window,
    kind: String,
    argv: Vec<String>,
    env: Option<serde_json::Map<String, Value>>,
    cwd: Option<String>,
) -> Result<String, String> {
    let inner = state.inner.clone();
    submit_sidecar_job(
        &inner,
        &window,
        &kind,
        argv,
        env.unwrap_or_default(),
        cwd,
        None,
    )
    .await
}

/// Resolved command line + env for a bundled Python script, ready to
/// hand to submit_sidecar_job. Pure-data so it's easy to inspect in
/// tests / log lines without spawning anything.
struct PythonScriptCommand {
    /// argv[0] is the python interpreter; argv[1..] are -u + script + extras.
    argv: Vec<String>,
    /// Env vars to layer on top of the spawning process's environment.
    /// PYTHONPATH / BOT_VERSION_DIR / AI_PROVIDER / API keys live here.
    env: serde_json::Map<String, Value>,
    /// Working directory for the spawned child.
    cwd: String,
}

/// Build the (argv, env, cwd) tuple for one of the bundled Python
/// scripts (e.g. "1-collect_data.py"). Mirrors the resolution that
/// run_python_script does internally, but does NOT spawn anything --
/// callers either spawn locally or POST the result to the sidecar's
/// /jobs endpoint.
///
/// Side-effect: emits `[System] Python: ...` / `[System] Script: ...`
/// / `[System] WorkDir: ...` / `[System] VersionDir: ...` to the
/// terminal_update channel, matching the legacy run_python_script
/// output exactly so the UI's terminal pane looks identical between
/// the two spawn paths.
fn build_python_script_command(
    app: &AppHandle,
    script_name: &str,
    extra_args: &[&str],
    window: &Window,
) -> Result<PythonScriptCommand, String> {
    let script_path = resolve_script(app, script_name)?;
    let data_root = work_dir(app);

    let py = if cfg!(debug_assertions) {
        find_python_for_app(app)?
    } else {
        ensure_python_env(app, window)?
    };

    let _ = window.emit::<String>("terminal_update", format!("[System] Python: {}", py.display()));
    let _ = window.emit::<String>("terminal_update", format!("[System] Script: {}", script_path.display()));
    let _ = window.emit::<String>("terminal_update", format!("[System] WorkDir: {}", data_root.display()));

    // argv: [python_exe, -u, script_path, ...extra_args]
    let mut argv: Vec<String> = vec![
        py.display().to_string(),
        "-u".to_string(),
        script_path.display().to_string(),
    ];
    for a in extra_args {
        argv.push((*a).to_string());
    }

    // PYTHONPATH composition (same order as run_python_script):
    //   - script's parent dir (versions/<ver>)
    //   - PROD bundled site-packages
    //   - existing PYTHONPATH from the spawning process env
    let sep = if is_windows() { ";" } else { ":" };
    let mut pypaths: Vec<String> = Vec::new();
    if let Some(vdir) = script_path.parent() {
        let _ = window.emit::<String>("terminal_update", format!("[System] VersionDir: {}", vdir.display()));
        pypaths.push(vdir.display().to_string());
    }
    if !cfg!(debug_assertions) {
        let sp = managed_site_packages_dir(app);
        pypaths.push(sp.display().to_string());
    }
    let old = std::env::var("PYTHONPATH").unwrap_or_default();
    if !old.is_empty() {
        pypaths.push(old);
    }

    let mut env: serde_json::Map<String, Value> = serde_json::Map::new();

    // Stable Python env (apply_stable_python_env equivalent).
    env.insert("PYTHONUNBUFFERED".to_string(), Value::String("1".to_string()));
    env.insert("PYTHONUTF8".to_string(), Value::String("1".to_string()));
    env.insert("PYTHONIOENCODING".to_string(), Value::String("utf-8".to_string()));

    if let Some(vdir) = script_path.parent() {
        env.insert(
            "BOT_VERSION_DIR".to_string(),
            Value::String(vdir.display().to_string()),
        );
    }
    env.insert("PYTHONPATH".to_string(), Value::String(pypaths.join(sep)));

    if cfg!(debug_assertions) {
        // apply_dev_venv_env equivalent. Only set if the venv exists,
        // matching the legacy guard behaviour.
        let repo_root = dev_repo_root();
        let venv_root = repo_root.join(".venv");
        if venv_root.exists() {
            env.insert(
                "VIRTUAL_ENV".to_string(),
                Value::String(venv_root.display().to_string()),
            );
            let venv_bin = venv_bin_from_root(&repo_root);
            // Prepend venv bin to PATH inherited at submit time. The
            // sidecar will merge our env over its own when spawning.
            let old_path = std::env::var_os("PATH").unwrap_or_default();
            let mut new_path = OsString::new();
            new_path.push(venv_bin.as_os_str());
            new_path.push(path_sep());
            new_path.push(old_path);
            env.insert(
                "PATH".to_string(),
                Value::String(new_path.to_string_lossy().to_string()),
            );
        }
    }

    let provider = {
        let p = get_env_var(app, "AI_PROVIDER");
        if p.is_empty() { "gemini".to_string() } else { p }
    };
    env.insert("AI_PROVIDER".to_string(), Value::String(provider));
    env.insert("GEMINI_API_KEY".to_string(), Value::String(get_env_var(app, "GEMINI_API_KEY")));
    env.insert("OPENAI_API_KEY".to_string(), Value::String(get_env_var(app, "OPENAI_API_KEY")));
    env.insert(
        "MODELHUB_DATA_ROOT".to_string(),
        Value::String(data_root.display().to_string()),
    );

    Ok(PythonScriptCommand {
        argv,
        env,
        cwd: data_root.display().to_string(),
    })
}

/// Submit one of the bundled Python scripts to the sidecar's /jobs
/// endpoint. High-level helper used by start_recording / start_training
/// / start_bot now that they own no local subprocess.
///
/// On submit:
///   - any previously-running sidecar job for this app is cancelled,
///     so the user clicking Start a second time replaces the first
///     job rather than running both.
///   - argv + env + cwd are computed by build_python_script_command,
///     which mirrors the legacy run_python_script resolution exactly.
async fn start_python_script_via_sidecar(
    app: &AppHandle,
    inner: &Arc<AppStateInner>,
    window: &Window,
    kind: &str,
    script_name: &str,
    extra_args: &[&str],
    training_meta: Option<TrainingFinalizeMeta>,
) -> Result<String, String> {
    let cmd = build_python_script_command(app, script_name, extra_args, window)?;
    submit_sidecar_job(
        inner,
        window,
        kind,
        cmd.argv,
        cmd.env,
        Some(cmd.cwd),
        training_meta,
    )
    .await
}

#[tauri::command]
async fn stop_process(state: tauri::State<'_, AppState>, window: Window) -> Result<String, String> {
    let inner = state.inner.clone();
    let msg = stop_process_inner(&window, &inner);

    // MVP-3c: also cancel any sidecar-owned job. Read+clear under the
    // lock so a concurrent submission can't observe a stale "still
    // running" state. The DELETE is best-effort -- if the sidecar is
    // already gone the local kill above has already disposed of the
    // child, so the result here doesn't change UX.
    //
    // Phase 26: the sidecar's cancel() now runs a cooperative-stop
    // ladder (write stop-flag, wait up to 8s for the child to flush
    // its dataset and exit, escalate to SIGTERM, then SIGKILL). The
    // DELETE call therefore CAN take several seconds to return when
    // a recording was active. Emit a "saving" line up front so the
    // user can see the stop click was received and the system is
    // intentionally giving the recorder time to flush, not hung.
    let sidecar_job = inner.current_sidecar_job.lock().unwrap().take();
    if let Some(job_id) = sidecar_job {
        let _ = window.emit(
            "terminal_update",
            format!(
                "[Sidecar] Stop requested for job {} -- waiting for clean shutdown (saving any buffered samples)...",
                job_id
            ),
        );
        let path = format!("/jobs/{}", job_id);
        if let Err(e) = api_delete_with(&inner, &path).await {
            let _ = window.emit(
                "terminal_update",
                format!("[Warning] could not cancel sidecar job {}: {}", job_id, e),
            );
        } else {
            let _ = window.emit(
                "terminal_update",
                format!("[Sidecar] Cancelled job {}", job_id),
            );
        }
    }

    // Phase 25: capture the finalize response so we can forward the
    // archived dataset entry (id, name, path, file_count, game_id) to
    // the UI as a `recording_finalized` event. The Teach tab listens
    // and prefills `train-dataset-id`, eliminating the
    // "No dataset selected" preflight that hits first-time users
    // immediately after their first successful recording.
    match api_post_with(&inner, "/session/finalize", json!({})).await {
        Ok(resp) => {
            if resp
                .get("finalized")
                .and_then(|v| v.as_str())
                .map(|s| s == "recording")
                .unwrap_or(false)
            {
                if let Some(dataset) = resp.get("dataset") {
                    if !dataset.is_null() {
                        let _ = window.emit("recording_finalized", dataset.clone());
                    }
                }
            }
        }
        Err(e) => {
            let _ = window.emit("terminal_update", format!("[Warning] finalize failed: {}", e));
        }
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
    // Phase 31: optional resolved checkpoint file. The UI sends this
    // alongside the directory when it knows it (from catalog metadata
    // or training_finalized); the Python endpoint persists it under
    // `model_file` and start_bot prefers it over walking the dir.
    model_file: Option<String>,
) -> Result<Value, String> {
    let gid = normalize_game_id(game_id);
    api_post_with(
        &state.inner,
        "/modelhub/active",
        json!({
            "game_id": gid,
            "model_id": model_id,
            "path": path,
            "model_file": model_file.unwrap_or_default(),
        }),
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


#[tauri::command]
async fn install_health(
    state: tauri::State<'_, AppState>,
    app: AppHandle,
) -> Result<Value, String> {
    let install_dir = installation_dir();

    let res_root = install_dir.join("resources");

    // --- Per-subsystem probes ---
    // Phase 3.1: actual round-trip to /health, not just "is the slot
    // populated". The old slot check missed the case where the
    // Python process died after printing READY (segfault, OOM,
    // AV quarantine of torch_cuda.dll mid-run) -- the slot was
    // still Some(api), so install_health would falsely report
    // green while every subsequent invoke() failed with a connection
    // error. 2-second timeout keeps the Diagnosis panel snappy on a
    // wedged sidecar.
    let sidecar_ok = quick_health_probe(&state.inner, Duration::from_secs(2)).await;

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

    // Writable logs dir — created by ensure_runtime_layout() on launch.
    // Lives under local_data_root() (%LOCALAPPDATA%\com.bot.mmorpg.ai\
    // logs\), NOT under the install dir, so writability does not depend
    // on whether the install dir is admin-only.
    let local_root = local_data_root(&app);
    let logs_dir = local_root.join("logs");
    let (logs_writable, logs_detail) = probe_writable_detailed(&logs_dir);

    // Phase 4 (gap #6): the spawned ML scripts write to `datasets/<game>/`
    // (collect_data) and `trained_models/<game>/` (train_model). If
    // either of those is unwritable (read-only FS, antivirus locking,
    // OneDrive file-on-demand stub) the user gets an opaque
    // PermissionError mid-run. Probe both up-front so the Diagnosis
    // panel surfaces it before they click Train / Record.
    let datasets_dir = local_root.join("datasets");
    let models_dir = local_root.join("trained_models");
    let (datasets_writable, datasets_detail) = probe_writable_detailed(&datasets_dir);
    let (models_writable, models_detail) = probe_writable_detailed(&models_dir);

    // Phase 8: when sidecar_ok is false, surface the actual launch
    // error (and the first stderr line) in the install_health row's
    // message instead of the generic "Not running". This makes the
    // Diagnosis panel + the support_report carry the cause, not just
    // the symptom -- matching the AAA pattern where every failure
    // surface answers "what broke" not just "something broke".
    let sidecar_failure_detail: Option<String> = if !sidecar_ok {
        state
            .inner
            .last_launch_report
            .lock()
            .ok()
            .and_then(|g| g.as_ref().cloned())
            .and_then(|rep| {
                let err = rep.error_string.unwrap_or_default();
                let first_stderr = rep
                    .stderr_lines
                    .iter()
                    .find(|l| !l.trim().is_empty())
                    .cloned()
                    .unwrap_or_default();
                if err.is_empty() && first_stderr.is_empty() {
                    None
                } else if first_stderr.is_empty() {
                    Some(err)
                } else if err.is_empty() {
                    Some(format!("First stderr line: {}", first_stderr))
                } else {
                    Some(format!("{} | First stderr line: {}", err, first_stderr))
                }
            })
    } else {
        None
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
        row("sidecar", "Backend sidecar",
            if sidecar_ok { "ok" } else { "error" },
            if sidecar_ok { "Running".into() }
            else {
                // Phase 8: prefer the captured launch-error detail over
                // the generic "Not running" so support reports carry the
                // cause. Fall through to the generic line only when
                // last_launch_report has no useful content (rare --
                // implies start_sidecar_server was never called this
                // session, e.g. fresh install dir without a prior boot).
                match sidecar_failure_detail.as_deref() {
                    Some(detail) => format!("Not running. {}", detail),
                    None => "Not running.".to_string(),
                }
            }),
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
        // Phase 5: the labels are noun-only ("Logs directory") so the
        // banner no longer reads as "X is writable -- Cannot write to
        // X" (a self-contradicting sentence). The detail message is
        // also tighter; the long technical explanation lives in the
        // Diagnosis panel where the user has space to read it.
        // Phase 17: when a writability probe fails, the row's message
        // names *which* failure mode (exists-but-not-writable vs.
        // can't-create-at-all vs. AV-lock) and includes the exact
        // PowerShell command to fix it. Common case: a previous
        // production install created these dirs as Administrator and
        // the current user-mode session can't write into them; the
        // suggested `Remove-Item -Recurse <dir>` lets the next launch
        // recreate them with the right owner.
        row("logs_writable", "Logs directory",
            if logs_writable { "ok" } else { "error" },
            if logs_writable { format!("{}", logs_dir.display()) }
            else { format!("Cannot write to {}: {}", logs_dir.display(), logs_detail) }),
        row("datasets_writable", "Datasets directory",
            if datasets_writable { "ok" } else { "error" },
            if datasets_writable { format!("{}", datasets_dir.display()) }
            else { format!("Cannot write to {}: {}", datasets_dir.display(), datasets_detail) }),
        row("trained_models_writable", "Trained-models directory",
            if models_writable { "ok" } else { "error" },
            if models_writable { format!("{}", models_dir.display()) }
            else { format!("Cannot write to {}: {}", models_dir.display(), models_detail) }),
        // Surface the local-data root for the operator. With the MVP-1
        // migration the runtime + datasets + models + logs live under
        // %LOCALAPPDATA%\com.bot.mmorpg.ai\, NOT under the install dir.
        // The install dir itself can stay in Program Files without
        // affecting writability of those paths -- which is why the
        // previous "install_location_privileged" warn check is gone.
        row("local_data_root", "Local data root",
            "ok",
            format!("{} (writes go here, not the install dir)", local_root.display())),
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

// ---------------------------
// PREFLIGHT (per-action precondition checks)
// ---------------------------
//
// Phase 4 (gap #5): a fast, per-action validation pass the UI runs
// before submitting a record / train / bot job. Without this, a user
// who clicks "Train" with a misspelled architecture or an unknown
// dataset_id has to wait for the spawn, read the Python traceback in
// `(stderr)` lines, and decode argparse failures themselves. With
// this command, those failures become a clear toast at click time.
//
// The check list is deliberately small + cheap (returns in <50 ms in
// the common case): no torch.load smoke test (which would need a new
// sidecar endpoint), no file-system traversal beyond a single
// `Path::exists()` and a write probe. The runtime_doctor command
// already does the heavy functional checks at startup; preflight
// only validates the args specific to *this* click.
//
// Returns a structured JSON the UI can render verbatim:
//   { ok: true,  reasons: [] }                       -> green-light
//   { ok: false, reasons: ["dataset name empty", ...] }
//
// Failure to reach the sidecar shows up as `ok: false` with a
// "Backend sidecar not responding" reason -- by design, since none
// of the three actions can succeed if /jobs is unreachable.

#[tauri::command]
async fn preflight_action(
    state: tauri::State<'_, AppState>,
    app: AppHandle,
    kind: String,
    game_id: Option<String>,
    dataset_name: Option<String>,
    dataset_id: Option<String>,
    arch: Option<String>,
    monitor_id: Option<u32>,
) -> Result<Value, String> {
    let mut reasons: Vec<String> = Vec::new();
    // Phase 23-A: server-side resolved name. When the JS sends an
    // empty/missing dataset_name (because the input was blank or
    // because a stale-cached JS bundle skipped its auto-fill code
    // path), we generate one here AUTHORITATIVELY and return it to
    // the UI. The frontend writes it back to the input field for
    // visual feedback, AND uses it for the subsequent
    // start_recording call so the recording actually lands in the
    // directory we validated. Defense against pre-Phase-21 JS
    // bundles silently shipping in WebView2's resource cache.
    let mut resolved_dataset_name: Option<String> = None;

    // 0. Sidecar must be responsive. Same probe install_health uses,
    // so the verdicts agree. 2s timeout to keep the toast snappy.
    if !quick_health_probe(&state.inner, Duration::from_secs(2)).await {
        reasons.push(
            "Backend sidecar is not responding to /health. Click Restart Sidecar (Settings -> Runtime) or run the Diagnosis panel."
                .to_string(),
        );
    }

    // 1. Output dirs must be writable. Mirrors the install_health
    // probes. We re-run them here because the user might have toggled
    // OneDrive / antivirus between launches without restarting.
    let local_root = local_data_root(&app);
    let datasets_dir = local_root.join("datasets");
    let models_dir = local_root.join("trained_models");

    let gid = normalize_game_id(game_id);

    match kind.as_str() {
        "record" => {
            if !probe_writable(&datasets_dir) {
                reasons.push(format!(
                    "Datasets directory is not writable: {}. Recording will crash mid-capture.",
                    datasets_dir.display()
                ));
            }
            let raw = dataset_name.unwrap_or_default();
            let trimmed_raw = raw.trim();
            // Phase 23-A: synthesize a name when the input is empty
            // instead of rejecting. JS-side auto-fill (Phase 21+22)
            // is best-effort; the server-side default is the
            // contract.
            let final_name: String = if trimmed_raw.is_empty() {
                let auto = format!(
                    "{}_session_{}",
                    gid.replace('_', "-"),
                    unix_now_ms()
                );
                resolved_dataset_name = Some(auto.clone());
                auto
            } else {
                trimmed_raw.to_string()
            };
            // Reject path-traversal characters early -- the spawned
            // collect_data.py joins this into a path and would
            // otherwise fail with a confusing OSError. Apply this to
            // both user-typed and auto-generated names (the auto
            // form is generated to avoid these chars but check
            // anyway in case the format ever changes).
            if final_name.contains(['/', '\\', ':', '*', '?', '"', '<', '>', '|']) {
                reasons.push(format!(
                    "Dataset name '{}' contains a path separator or reserved character.",
                    final_name
                ));
            } else {
                let target = datasets_dir.join(&gid).join(&final_name);
                if target.exists() {
                    reasons.push(format!(
                        "Dataset '{}' already exists for {}. Pick a new name or delete the old one.",
                        final_name, gid
                    ));
                }
            }
            // Always report the resolved name so JS can update the
            // input field even when the user-typed value was used
            // verbatim (lets the UI confirm "this is what we
            // recorded against").
            if resolved_dataset_name.is_none() {
                resolved_dataset_name = Some(final_name.clone());
            }
            // Monitor sanity: list_monitors() returns a single {id:0}
            // today. Anything else is caller error (UI passing a stale
            // selection).
            if let Some(mid) = monitor_id {
                let known: Vec<u32> = list_monitors().iter().map(|m| m.id).collect();
                if !known.contains(&mid) {
                    reasons.push(format!(
                        "Monitor #{} is not in the connected list ({:?}). Pick a valid monitor in the Teach tab.",
                        mid, known
                    ));
                }
            }
        }
        "train" => {
            if !probe_writable(&models_dir) {
                reasons.push(format!(
                    "Trained-models directory is not writable: {}. Training will fail at the first checkpoint save.",
                    models_dir.display()
                ));
            }
            // No second job in flight. We're stricter than
            // submit_sidecar_job (which cancels-and-replaces) because
            // a user who clicks Train twice almost always means
            // "Train one model, not abort and re-train".
            let busy = state
                .inner
                .current_sidecar_job
                .lock()
                .ok()
                .map(|g| g.is_some())
                .unwrap_or(false);
            if busy {
                reasons.push(
                    "Another sidecar job is already running. Stop it first (or wait for it to finish) before starting training."
                        .to_string(),
                );
            }
            let did = dataset_id.unwrap_or_default();
            if did.trim().is_empty() {
                reasons.push("No dataset selected. Pick one in the Train tab.".to_string());
            } else {
                let dataset_path = datasets_dir.join(&gid).join(did.trim());
                if !dataset_path.exists() {
                    reasons.push(format!(
                        "Dataset '{}' for {} not found at {}. Re-record it or pick another from the Train tab.",
                        did, gid, dataset_path.display()
                    ));
                }
            }
            // Architecture allow-list lives at module scope (see
            // KNOWN_ARCHS) so is_architecture_id() shares it.
            let a = arch.unwrap_or_else(|| "custom".to_string());
            if !KNOWN_ARCHS.contains(&a.as_str()) {
                reasons.push(format!(
                    "Unknown architecture '{}'. Valid options: {}.",
                    a,
                    KNOWN_ARCHS.join(", ")
                ));
            }
        }
        "bot" => {
            // start_bot requires --model. Resolve it here so the user
            // gets the same clear error at click time as they would
            // get from start_bot's body. We call /modelhub/catalog
            // directly (not via start_bot) so this stays read-only.
            let url = format!("/modelhub/catalog?game_id={}", urlencoding::encode(&gid));
            match api_get_with(&state.inner, &url).await {
                Ok(catalog) => {
                    let active = catalog.get("active");
                    let model_dir = active
                        .and_then(|v| if v.is_null() { None } else { Some(v) })
                        .and_then(|v| v.get("model_dir"))
                        .and_then(|m| m.as_str())
                        .unwrap_or("");
                    if model_dir.is_empty() {
                        reasons.push(
                            "No active model selected for inference. Pick one in the Models tab and click 'Set Active'."
                                .to_string(),
                        );
                    } else if !Path::new(model_dir).exists() {
                        // Issue #76: distinguish "the folder vanished"
                        // from "you activated an architecture template".
                        // The UI's fallback catalog (used whenever the
                        // sidecar reports no bundled builtins, i.e. every
                        // Custom Game) lists architectures with
                        // path == the arch id, so a user who clicked Set
                        // Active on one stored model_dir="efficientnet_lstm"
                        // and was then told their model had been "deleted
                        // or moved" -- naming a folder that never existed.
                        if is_architecture_id(model_dir) {
                            reasons.push(format!(
                                "'{}' is a training architecture, not a trained model. Architectures are templates: record a dataset, train it with '{}' in the Train tab, then activate the resulting model in the Models tab.",
                                model_dir, model_dir
                            ));
                        } else {
                            reasons.push(format!(
                                "Active model directory missing on disk: {}. The model was deleted or moved -- pick another in the Models tab.",
                                model_dir
                            ));
                        }
                    }
                }
                Err(_) => {
                    // Already caught by the /health check above, but
                    // keep a specific reason in case /health passes
                    // and /modelhub/catalog fails for a different
                    // reason (router not mounted).
                    reasons.push(
                        "Could not query /modelhub/catalog -- the modelhub router may not be mounted. See [Sidecar] lines in the terminal log."
                            .to_string(),
                    );
                }
            }
            if let Some(mid) = monitor_id {
                let known: Vec<u32> = list_monitors().iter().map(|m| m.id).collect();
                if !known.contains(&mid) {
                    reasons.push(format!(
                        "Monitor #{} is not in the connected list ({:?}).",
                        mid, known
                    ));
                }
            }
        }
        other => {
            reasons.push(format!(
                "preflight_action: unknown kind '{}'. Expected 'record', 'train', or 'bot'.",
                other
            ));
        }
    }

    Ok(json!({
        "ok": reasons.is_empty(),
        "reasons": reasons,
        // Phase 23-A: present only for kind="record". The UI uses
        // it to (a) reflect the auto-generated name in the input
        // field and (b) pass the same name into start_recording so
        // the spawn matches the directory the preflight validated.
        "resolved_dataset_name": resolved_dataset_name,
    }))
}

/// Runtime doctor (MVP-2): invokes the bundled self-test script and
/// returns its JSON verdict to the UI.
///
/// The doctor lives at resources/scripts/runtime_doctor.py (staged by
/// build_pipeline.ps1 STEP 6). It is run with the bundled Python
/// interpreter via `apply_stable_python_env`, so it sees the same
/// site-packages tree the sidecar and training scripts actually use.
///
/// On any failure (script missing, interpreter crash, malformed
/// JSON), this command synthesises a minimal "verdict=error" report
/// rather than returning Err -- the UI relies on this command to
/// drive a verdict banner and must always get a parseable payload.
#[tauri::command]
async fn runtime_doctor(app: AppHandle) -> Result<Value, String> {
    use std::time::Instant;
    let started = Instant::now();

    // Phase 20: in dev builds the embedded Python doesn't exist
    // (it's only extracted by ensure_python_env in production from
    // python-runtime.zip). Running runtime_doctor against a missing
    // embedded interpreter would always return python_not_found and
    // poison install_health.verdict to "error", disabling the
    // Train/Record/Bot buttons (Phase 4 applyHealthGate). Route the
    // doctor through the host venv python in dev mode -- it imports
    // the same modules from the same .venv site-packages, so the
    // doctor's torch_intact / fastapi_intact / cv2_intact checks
    // still verify what we care about.
    let py = if cfg!(debug_assertions) {
        // Dev: prefer the host venv Python via find_python_for_app
        // (.venv/Scripts/python.exe on Windows). Falls back to the
        // embedded path if for some reason the venv is missing,
        // and finally to the synthesized python_not_found error.
        match find_python_for_app(&app) {
            Ok(p) if p.exists() => p,
            _ => {
                let fallback = managed_embedded_python_dir(&app)
                    .join(if is_windows() { "python.exe" } else { "bin/python3" });
                if fallback.exists() {
                    fallback
                } else {
                    return Ok(synth_doctor_error(
                        "python_not_found",
                        "No Python interpreter available -- neither the dev .venv nor the bundled embedded runtime were found. Run `make install` to create the venv.",
                        started.elapsed().as_millis() as u64,
                    ));
                }
            }
        }
    } else {
        // Prod: the only correct thing to test is the bundled
        // embedded Python -- the host system Python is irrelevant.
        match managed_embedded_python_dir(&app)
            .join(if is_windows() { "python.exe" } else { "bin/python3" })
        {
            p if p.exists() => p,
            _ => {
                return Ok(synth_doctor_error(
                    "python_not_found",
                    "Bundled Python interpreter not found in runtime tree.",
                    started.elapsed().as_millis() as u64,
                ));
            }
        }
    };

    // Locate the doctor script itself. Probe the install-time location
    // first (resources/scripts/runtime_doctor.py); fall back to the
    // dev-time path for `cargo run`.
    let doctor_script = app
        .path_resolver()
        .resolve_resource("resources/scripts/runtime_doctor.py")
        .filter(|p| p.exists())
        .or_else(|| {
            let direct = installation_dir()
                .join("resources")
                .join("scripts")
                .join("runtime_doctor.py");
            if direct.exists() { Some(direct) } else { None }
        })
        .or_else(|| {
            // dev fallback: repo-relative
            let dev = installation_dir().join("..").join("scripts").join("runtime_doctor.py");
            if dev.exists() { Some(dev) } else { None }
        });
    let doctor_script = match doctor_script {
        Some(p) => p,
        None => {
            return Ok(synth_doctor_error(
                "doctor_script_not_found",
                "resources/scripts/runtime_doctor.py is missing from the install. \
                 Reinstall to restore the runtime self-test.",
                started.elapsed().as_millis() as u64,
            ));
        }
    };

    let local_root = local_data_root(&app);

    let mut cmd = Command::new(&py);
    apply_stable_python_env(&mut cmd);
    cmd.arg(&doctor_script);
    cmd.arg("--selftest");
    cmd.arg("--data-dir");
    cmd.arg(local_root.display().to_string());
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
        Err(e) => {
            return Ok(synth_doctor_error(
                "spawn_failed",
                &format!("Failed to launch doctor: {e}"),
                started.elapsed().as_millis() as u64,
            ));
        }
    };

    let stdout_str = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr_str = String::from_utf8_lossy(&output.stderr).to_string();

    // The doctor's stdout is JSON. If we can parse it, return that
    // verbatim -- it already carries verdict / per-check status.
    // If parsing fails, the doctor itself crashed (or the bundled
    // python is so broken it couldn't even import json) -- synthesise
    // an error report including the captured stderr for debugging.
    match serde_json::from_str::<Value>(stdout_str.trim()) {
        Ok(v) => Ok(v),
        Err(parse_err) => Ok(synth_doctor_error(
            "doctor_unparseable_output",
            &format!(
                "Doctor produced non-JSON stdout (exit={}). parse_err={parse_err}. \
                 stderr={}. stdout_head={:?}",
                output.status.code().map(|c| c.to_string()).unwrap_or_else(|| "?".to_string()),
                stderr_str.lines().next().unwrap_or(""),
                stdout_str.chars().take(200).collect::<String>(),
            ),
            started.elapsed().as_millis() as u64,
        )),
    }
}

/// Build a minimal "the doctor itself failed" report so the UI's
/// verdict-aware banner still has something to render.
fn synth_doctor_error(check_name: &str, detail: &str, elapsed_ms: u64) -> Value {
    json!({
        "doctor_version": "shell-fallback",
        "verdict": "error",
        "elapsed_ms": elapsed_ms,
        "platform": {
            "os": std::env::consts::OS,
        },
        "checks": [
            {
                "name": check_name,
                "status": "error",
                "detail": detail,
                "elapsed_ms": 0
            }
        ],
    })
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
/// Format a SidecarLaunchReport as the markdown block specified in
/// the design doc (status, command, cwd, pid, exit code, duration,
/// stdout/stderr fenced blocks, health probe). Always rendered when
/// a report exists, even if status="ok" -- a green report still
/// helps when reproducing an intermittent failure.
// ---------------------------
// PHASE 10: SELF-DIAGNOSIS RULES
// ---------------------------
//
// Pattern-match a SidecarLaunchReport (+ recent errors) against a
// curated table of known failure modes. Each rule returns
// (likely_cause, confidence, fix) when it matches. The bundle
// folds these into a "Likely Causes" markdown section so a reader
// (AI or human) sees the conclusion before scrolling through raw
// stderr / JSON.
//
// Adding a new rule:
//   1. Append to LAUNCH_DIAGNOSIS_RULES below.
//   2. Pattern is a closure: |rep, errors| -> bool.
//   3. Keep the `cause` line short and the `fix` actionable.
//   4. Confidence: "high" only when the symptom is uniquely
//      attributable; "medium" / "low" when other causes share it.

#[derive(Debug)]
struct LaunchDiagnosis {
    cause: String,
    confidence: &'static str, // "high" | "medium" | "low"
    fix: String,
}

fn stderr_contains(rep: &SidecarLaunchReport, needle: &str) -> bool {
    rep.stderr_lines.iter().any(|l| l.contains(needle))
}

fn error_string_contains(rep: &SidecarLaunchReport, needle: &str) -> bool {
    rep.error_string
        .as_deref()
        .map(|s| s.contains(needle))
        .unwrap_or(false)
}

fn analyze_launch_report(
    rep: &SidecarLaunchReport,
    _errors: &[ErrorEntry],
) -> Vec<LaunchDiagnosis> {
    let mut out: Vec<LaunchDiagnosis> = Vec::new();

    // Rule 1a: ModuleNotFoundError on modelhub WHILE PYTHONPATH
    // contains a `\\?\`-prefixed entry. Python's importlib silently
    // ignores extended-length-path entries on sys.path even though
    // the path itself is valid -- so the package directory is on
    // disk, the parent is on PYTHONPATH (Phase 9), but the import
    // still fails. Phase 14 fix: strip_extended_path_prefix() on
    // every path that crosses the Rust->Python boundary.
    let pythonpath_has_extended_prefix = rep
        .env_filtered
        .iter()
        .find(|(k, _)| k.eq_ignore_ascii_case("PYTHONPATH"))
        .map(|(_, v)| v.contains(r"\\?\"))
        .unwrap_or(false);

    // Phase 17: detect the `python<ver>._pth` failure mode. Windows
    // embedded Python ships a `_pth` file alongside python.exe that
    // makes sys.path AUTHORITATIVE -- when that file exists, the
    // PYTHONPATH env var is IGNORED entirely. The supervisor's
    // PYTHONPATH=...resources can be perfectly correct (no \\?\,
    // parent-of-modelhub is included) and Python STILL won't see
    // the package. The fix is in entry_main.py's _bootstrap_sys_path
    // which inserts the resources dir directly via sys.path.insert
    // -- not via PYTHONPATH. If we see the symptom (clean PYTHONPATH
    // + ModuleNotFoundError) we point the reader at the bootstrap.
    let likely_pth_ignores_pythonpath = (stderr_contains(rep, "No module named 'modelhub'")
        || stderr_contains(rep, "No module named \"modelhub\""))
        && !pythonpath_has_extended_prefix;

    if (stderr_contains(rep, "No module named 'modelhub'")
        || stderr_contains(rep, "No module named \"modelhub\""))
        && pythonpath_has_extended_prefix
    {
        out.push(LaunchDiagnosis {
            cause: "Python cannot import the `modelhub` package because PYTHONPATH contains entries with the Windows `\\\\?\\` extended-length-path prefix. importlib silently ignores those entries even though the underlying paths are valid.".to_string(),
            confidence: "high",
            fix: "The Rust shell must call `strip_extended_path_prefix()` on every path that crosses the Rust->Python boundary (see Phase 14 in src-tauri/src/main.rs). Verify `start_sidecar_server` strips `\\\\?\\` from `resource_root`, `backend_script`, `modelhub_dir`, and the `pypaths` entries before pushing them.".to_string(),
        });
    }

    // Rule 1c: PHASE 17. ModuleNotFoundError despite a clean PYTHONPATH
    // strongly suggests Windows embedded Python's `python<ver>._pth`
    // file is overriding (== ignoring) the env var. This is documented
    // CPython behavior on the embedded distribution, not a bug.
    if likely_pth_ignores_pythonpath {
        out.push(LaunchDiagnosis {
            cause: "PYTHONPATH is set correctly but Python ignored it. Windows' embedded Python distribution treats `python<ver>._pth` as authoritative -- when that file is present the PYTHONPATH env var is silently dropped. The fix is to bootstrap sys.path inside backend/entry_main.py (Phase 17 _bootstrap_sys_path), not via PYTHONPATH.".to_string(),
            confidence: "high",
            fix: "Verify backend/entry_main.py contains `_bootstrap_sys_path()` and calls it FIRST inside main() (before `from modelhub.tauri import ...`). The bootstrap reads MODELHUB_RESOURCE_ROOT (set by the supervisor) and inserts `<root>/resources` at sys.path[0]. If the file is correct, rebuild: `make artifact`. Reference: https://docs.python.org/3/using/windows.html#finding-modules".to_string(),
        });
    }

    // Rule 1b: ModuleNotFoundError on modelhub WITHOUT the
    // `\\?\` prefix on PYTHONPATH AND without the bootstrap-already-
    // run signal. The Phase 9 bug variant -- PYTHONPATH didn't
    // include the parent of resources/modelhub/, or the bundled
    // resources/modelhub/__init__.py was filtered out by the build.
    // (We add this only when neither 1a nor 1c fired so the bundle
    // shows the most precise diagnosis without piling on duplicates.)
    if (stderr_contains(rep, "No module named 'modelhub'")
        || stderr_contains(rep, "No module named \"modelhub\""))
        && !pythonpath_has_extended_prefix
        && !likely_pth_ignores_pythonpath
    {
        out.push(LaunchDiagnosis {
            cause: "Python cannot import the `modelhub` package -- PYTHONPATH does not contain the parent directory of resources/modelhub/, or resources/modelhub/__init__.py is missing from the install.".to_string(),
            confidence: "high",
            fix: "Verify `<install>/resources/modelhub/__init__.py` exists. If missing, reinstall. If present, the Rust shell's PYTHONPATH builder is at fault (see `start_sidecar_server` in src-tauri/src/main.rs -- it must push `modelhub_dir.parent()`, not `modelhub_dir`).".to_string(),
        });
    }

    // Rule 2: ImportError DLL load failure (torch._C, torch_cuda,
    // numpy core extensions). Almost always vc_redist + AV.
    if stderr_contains(rep, "ImportError: DLL load failed")
        || stderr_contains(rep, "ImportError: DLL")
    {
        out.push(LaunchDiagnosis {
            cause: "A compiled Python extension (.pyd / .dll) failed to load. Top causes: missing Visual C++ Redistributable, or AV quarantined a torch / numpy / opencv DLL during extraction.".to_string(),
            confidence: "high",
            fix: "1) Install vc_redist.x64.exe from https://aka.ms/vs/17/release/vc_redist.x64.exe. 2) Add %LOCALAPPDATA%\\com.bot.mmorpg.ai\\runtime\\ to your AV exclusions (Settings -> Diagnosis -> Add AV Exclusion). 3) Click Repair Runtime to re-extract the bundled python-runtime.zip.".to_string(),
        });
    }

    // Rule 3: Generic ModuleNotFoundError that isn't modelhub.
    // Likely a stripped dist-info / partial install.
    if stderr_contains(rep, "ModuleNotFoundError")
        && !stderr_contains(rep, "No module named 'modelhub'")
    {
        out.push(LaunchDiagnosis {
            cause: "A Python module the sidecar imports is missing from the bundled site-packages. This usually means an over-aggressive build-time strip or an interrupted install.".to_string(),
            confidence: "medium",
            fix: "Click Repair Runtime to re-extract python-runtime.zip. If that doesn't help, click Repair PyTorch (pip) to re-download torch+torchvision+numpy from PyPI -- this bypasses the bundled archive entirely.".to_string(),
        });
    }

    // Rule 4: PermissionError on data dir (write probe failed mid-
    // capture). Common with OneDrive file-on-demand stubs and
    // antivirus directory locks.
    if stderr_contains(rep, "PermissionError")
        || stderr_contains(rep, "[Errno 13]")
        || stderr_contains(rep, "Access is denied")
    {
        out.push(LaunchDiagnosis {
            cause: "Sidecar tried to write to a directory it cannot access. Common causes: OneDrive file-on-demand stub, antivirus directory lock, read-only attribute, or %LOCALAPPDATA% redirected to a network share.".to_string(),
            confidence: "high",
            fix: "1) Right-click %LOCALAPPDATA%\\com.bot.mmorpg.ai\\ -> Properties -> uncheck Read-only. 2) If OneDrive: pause sync or move the install. 3) If corporate AV: ask IT to allow the runtime path.".to_string(),
        });
    }

    // Rule 5: Loopback / firewall block on /health.
    if let Some(health) = rep.health_probe_result.as_deref() {
        if health.contains("Connection refused")
            || health.contains("connection refused")
            || health.contains("ConnectError")
        {
            out.push(LaunchDiagnosis {
                cause: "The sidecar process is alive but no one accepted the /health connection on 127.0.0.1. Either uvicorn never bound (early crash) or a loopback firewall is blocking.".to_string(),
                confidence: "medium",
                fix: "1) Check Windows Defender Firewall -> Allow an app -> add BOT-MMORPG-AI.exe. 2) Some corporate firewalls block 127.0.0.1 -- ask IT for an exception. 3) If the sidecar's stderr contains a traceback, that's the real cause.".to_string(),
            });
        }
        if health.contains("timed out") || health.contains("operation timed out") {
            out.push(LaunchDiagnosis {
                cause: "Uvicorn bound the port and printed READY, but /health did not respond within the gate timeout. The FastAPI app is probably still importing torch / cv2 (cold-disk launch).".to_string(),
                confidence: "medium",
                fix: "Click Retry -- the warm cache should make the second attempt succeed in under a second.".to_string(),
            });
        }
    }

    // Rule 6: Spawn-time OS failure (executable missing, perm denied).
    if error_string_contains(rep, "spawn failed") {
        out.push(LaunchDiagnosis {
            cause: "Windows refused to start the python.exe child process. Most likely: AV quarantined python.exe after extraction, or the runtime/py/python/ tree was deleted.".to_string(),
            confidence: "high",
            fix: "Click Repair Runtime to re-extract python-runtime.zip. If that fails, add %LOCALAPPDATA%\\com.bot.mmorpg.ai\\runtime\\ to AV exclusions first.".to_string(),
        });
    }

    // Rule 7: READY-line timeout but stderr is empty.
    // No traceback means a cold-start / AV-scan delay, NOT a crash.
    if error_string_contains(rep, "Timed out waiting for sidecar READY")
        && rep.stderr_lines.is_empty()
    {
        out.push(LaunchDiagnosis {
            cause: "The sidecar did not print READY within the budget, but stderr is empty -- so it isn't crashing. Usually first-launch AV scan or slow disk.".to_string(),
            confidence: "medium",
            fix: "1) Wait, then click Retry -- second launch is always faster (warm cache). 2) Add %LOCALAPPDATA%\\com.bot.mmorpg.ai\\runtime\\ to Defender exclusions to skip the scan next time.".to_string(),
        });
    }

    // Rule 8: We have a Python traceback but no specific rule
    // above matched. Prompt the reader to look at the raw stderr.
    if out.is_empty() && stderr_contains(rep, "Traceback (most recent call last):") {
        out.push(LaunchDiagnosis {
            cause: "Python raised an unhandled exception during sidecar startup. The exact cause is in the stderr block above; this rule table doesn't have a specific match.".to_string(),
            confidence: "low",
            fix: "Read the last line of the stderr block (the exception type + message). Search for it in docs/installer/04-bug-index.md or paste this whole bundle into an AI assistant.".to_string(),
        });
    }

    out
}

/// Snapshot of the on-disk install layout that's relevant to a
/// sidecar startup failure. Names + sizes only -- no file contents.
/// Sized so the rendered Markdown stays well under 4 KB even for
/// a fully-extracted runtime tree.
/// Phase 18: rewrite a path string for bundle display so a markdown
/// renderer doesn't auto-link the `com.bot.mmorpg.ai` substring as
/// a hyperlink. The literal identifier appears as a directory
/// segment in every %LOCALAPPDATA% path the sidecar / Rust shell
/// writes to, and the user's renderer of choice (some chat tools,
/// some markdown previewers) treats `xxx.yyy.zzz.ai` as a TLD-like
/// URL even when wrapped in inline backticks.
///
/// We replace the literal segment with a clearly non-URL token
/// (`<localdata>`) only in BUNDLE-FACING strings -- the actual
/// filesystem operations still use the real path. Reading the
/// bundle, the user sees:
///   `C:\Users\rusla\AppData\Local\<localdata>\runtime\py\python\python.exe`
/// instead of the auto-linked variant.
fn redact_path_for_bundle(s: &str) -> String {
    s.replace("com.bot.mmorpg.ai", "<localdata>")
}

fn format_install_layout(app: &AppHandle) -> String {
    fn list_dir(p: &Path, max_entries: usize) -> String {
        let mut out = String::new();
        match fs::read_dir(p) {
            Ok(it) => {
                let mut entries: Vec<(String, bool, u64)> = it
                    .filter_map(|e| e.ok())
                    .map(|e| {
                        let name = e.file_name().to_string_lossy().to_string();
                        let meta = e.metadata().ok();
                        let is_dir = meta.as_ref().map(|m| m.is_dir()).unwrap_or(false);
                        let size = meta.as_ref().map(|m| m.len()).unwrap_or(0);
                        (name, is_dir, size)
                    })
                    .collect();
                entries.sort_by(|a, b| a.0.cmp(&b.0));
                let total = entries.len();
                let trim = total.min(max_entries);
                for (name, is_dir, size) in entries.into_iter().take(trim) {
                    if is_dir {
                        out.push_str(&format!("  {}/\n", name));
                    } else {
                        out.push_str(&format!("  {} ({} bytes)\n", name, size));
                    }
                }
                if total > max_entries {
                    out.push_str(&format!(
                        "  ... ({} more entries elided)\n",
                        total - max_entries
                    ));
                }
                if total == 0 {
                    out.push_str("  (empty)\n");
                }
            }
            Err(e) => {
                out.push_str(&format!("  (cannot read: {})\n", e));
            }
        }
        out
    }

    let mut out = String::new();
    out.push_str("\n## Install Layout\n\n");
    out.push_str(
        "_Snapshot of the directories the sidecar reads from. \
         Names + sizes only -- no file contents. Helps spot \
         missing __init__.py, partial extractions, and AV-quarantined .pyd files._\n\n",
    );

    let install_dir = installation_dir();
    let resources_dir = install_dir.join("resources");
    let modelhub_resource = resources_dir.join("modelhub");
    let backend_resource = resources_dir.join("backend");
    // managed_embedded_python_dir + managed_site_packages_dir
    // already derive paths from local_data_root() internally, so we
    // don't need a local copy of it here.
    let runtime_py_dir = managed_embedded_python_dir(app);
    let site_packages_modelhub = managed_site_packages_dir(app).join("modelhub");

    // Phase 18: paths in headers go through redact_path_for_bundle so
    // markdown renderers don't auto-link the `com.bot.mmorpg.ai`
    // segment. The displayed string is unambiguous (`<localdata>` is
    // explicitly mentioned at the top of the bundle as the
    // %LOCALAPPDATA% placeholder); the underlying filesystem operations
    // are unaffected.
    out.push_str(&format!(
        "### `{}` (top level)\n```text\n{}```\n\n",
        redact_path_for_bundle(&resources_dir.display().to_string()),
        list_dir(&resources_dir, 30)
    ));
    out.push_str(&format!(
        "### `{}` (the modelhub package -- must contain `__init__.py`)\n```text\n{}```\n\n",
        redact_path_for_bundle(&modelhub_resource.display().to_string()),
        list_dir(&modelhub_resource, 40)
    ));
    out.push_str(&format!(
        "### `{}` (sidecar entry)\n```text\n{}```\n\n",
        redact_path_for_bundle(&backend_resource.display().to_string()),
        list_dir(&backend_resource, 20)
    ));
    out.push_str(&format!(
        "### `{}` (extracted embedded Python)\n```text\n{}```\n\n",
        redact_path_for_bundle(&runtime_py_dir.display().to_string()),
        list_dir(&runtime_py_dir, 30)
    ));
    out.push_str(&format!(
        "### `{}` (site-packages copy of the package)\n```text\n{}```\n\n",
        redact_path_for_bundle(&site_packages_modelhub.display().to_string()),
        list_dir(&site_packages_modelhub, 40)
    ));

    // A short, scannable verdict so a human or AI doesn't have to
    // diff the listings to spot the most common breakage.
    let mut signals: Vec<String> = Vec::new();
    if !modelhub_resource.join("__init__.py").exists() {
        signals.push(format!(
            "MISSING: `{}` -- without this, `import modelhub` cannot resolve to a package.",
            modelhub_resource.join("__init__.py").display()
        ));
    }
    if !modelhub_resource.join("tauri.py").exists() {
        signals.push(format!(
            "MISSING: `{}` -- the sidecar app factory.",
            modelhub_resource.join("tauri.py").display()
        ));
    }
    if !backend_resource.join("entry_main.py").exists() {
        signals.push(format!(
            "MISSING: `{}` -- the sidecar entry script.",
            backend_resource.join("entry_main.py").display()
        ));
    }
    if !runtime_py_dir
        .join(if cfg!(windows) { "python.exe" } else { "bin/python3" })
        .exists()
    {
        signals.push(format!(
            "MISSING: python interpreter at `{}` -- click Repair Runtime.",
            runtime_py_dir.display()
        ));
    }
    if !signals.is_empty() {
        out.push_str("### Layout signals\n\n");
        for s in &signals {
            out.push_str(&format!("- {}\n", s));
        }
        out.push('\n');
    }

    out
}

/// Render a paste-ready PowerShell command that reproduces the
/// captured launch attempt. Token is redacted so a user pasting
/// this into a chat doesn't leak credentials. Useful when the
/// supervisor's 60s budget cut off the real failure mid-import --
/// running by hand has no time limit and shows the full traceback.
fn format_repro_command(rep: &SidecarLaunchReport) -> String {
    let mut out = String::new();
    out.push_str("\n### Reproduce this launch manually\n\n");
    out.push_str("Paste in PowerShell (token has been redacted; replace with `test-token`):\n\n");
    out.push_str("```powershell\n");
    for (k, v) in &rep.env_filtered {
        // Skip PATH -- it's noisy and usually fine. Re-export the
        // app-specific vars so the manual run sees the same env.
        if k == "PATH" {
            continue;
        }
        out.push_str(&format!("$env:{} = '{}'\n", k, v.replace('\'', "''")));
    }
    // Redact the auth token. The split-and-replace below preserves
    // every other arg verbatim.
    let redacted_command = rep
        .command
        .split_whitespace()
        .scan(false, |skip_next, tok| {
            if *skip_next {
                *skip_next = false;
                Some("test-token".to_string())
            } else if tok == "--token" {
                *skip_next = true;
                Some("--token".to_string())
            } else {
                Some(tok.to_string())
            }
        })
        .collect::<Vec<_>>()
        .join(" ");
    out.push_str(&format!("& {}\n", redacted_command));
    out.push_str("```\n");
    out
}

fn format_launch_report_md(rep: &SidecarLaunchReport) -> String {
    let mut out = String::new();
    out.push_str("## Sidecar Launch\n\n");
    out.push_str(&format!("- Status: `{}`\n", rep.status));
    // Phase 18: long path-bearing fields go through redact_path_for_bundle
    // so the renderer doesn't auto-link the `com.bot.mmorpg.ai` substring.
    out.push_str(&format!("- Command: `{}`\n", redact_path_for_bundle(&rep.command)));
    out.push_str(&format!("- CWD: `{}`\n", redact_path_for_bundle(&rep.cwd)));
    out.push_str(&format!(
        "- PID: {}\n",
        rep.pid
            .map(|p| p.to_string())
            .unwrap_or_else(|| "(spawn failed)".to_string())
    ));
    out.push_str(&format!(
        "- Exit code: {}\n",
        rep.exit_code
            .map(|c| c.to_string())
            .unwrap_or_else(|| "(still running or killed)".to_string())
    ));
    out.push_str(&format!("- Startup timeout: {}s\n", rep.timeout_secs));
    let duration_ms = rep
        .finished_at_ms
        .map(|f| f.saturating_sub(rep.started_at_ms))
        .unwrap_or(0);
    out.push_str(&format!("- Duration: {}ms\n", duration_ms));
    if let Some(err) = &rep.error_string {
        out.push_str(&format!("- Error: `{}`\n", redact_path_for_bundle(&err.replace('`', "'"))));
    }
    out.push_str("\n### Environment (filtered)\n\n");
    if rep.env_filtered.is_empty() {
        out.push_str("_(none captured)_\n");
    } else {
        out.push_str("```text\n");
        for (k, v) in &rep.env_filtered {
            out.push_str(&format!("{}={}\n", k, redact_path_for_bundle(v)));
        }
        out.push_str("```\n");
    }
    // stdout / stderr lines are NOT redacted: Python tracebacks need
    // the literal file path so the reader can navigate to the failing
    // line. The fenced code block already prevents auto-link in
    // CommonMark-compliant renderers; aggressive renderers that
    // auto-link inside fenced blocks are an unfixable client-side
    // quirk.
    out.push_str("\n### stdout\n\n");
    if rep.stdout_lines.is_empty() {
        out.push_str("_(no stdout captured)_\n");
    } else {
        out.push_str("```text\n");
        for line in &rep.stdout_lines {
            out.push_str(line);
            out.push('\n');
        }
        out.push_str("```\n");
    }
    out.push_str("\n### stderr\n\n");
    if rep.stderr_lines.is_empty() {
        out.push_str("_(no stderr captured)_\n");
    } else {
        out.push_str("```text\n");
        for line in &rep.stderr_lines {
            out.push_str(line);
            out.push('\n');
        }
        out.push_str("```\n");
    }
    out.push_str("\n### Health Probe\n\n");
    match &rep.health_probe_result {
        Some(r) => {
            out.push_str(&format!("- Result: `{}`\n", r));
            if let Some(body) = &rep.health_probe_body {
                out.push_str("- Response body:\n\n```json\n");
                out.push_str(body);
                out.push_str("\n```\n");
            }
        }
        None => out.push_str("_(not probed -- spawn never reached the post-READY phase)_\n"),
    }
    out.push('\n');
    out
}

/// Phase 10: bundle schema version. Bumped whenever a section is
/// added/removed/renamed so downstream tools can detect format
/// changes. Document the change in CHANGELOG.md too.
const BUNDLE_SCHEMA_VERSION: &str = "2";

fn build_ai_bundle(
    rust_errors: &[ErrorEntry],
    sidecar_entries: &[Value],
    probe: Option<&Value>,
    doctor: Option<&Value>,
    launch_report: Option<&SidecarLaunchReport>,
    install_layout_md: Option<&str>,
    app_version: &str,
    install_dir: &str,
) -> String {
    let mut out = String::new();
    out.push_str("# Debug Bundle\n\n");
    out.push_str(&format!("- Schema version: `{}`\n", BUNDLE_SCHEMA_VERSION));
    let captured_at = unix_now_ms();
    out.push_str(&format!(
        "- Captured at: `{}` (unix-ms)\n",
        captured_at
    ));
    out.push_str(&format!("- Platform: `{}` `{}`\n", std::env::consts::OS, std::env::consts::ARCH));
    out.push_str(&format!("- App version: `{}`\n", app_version));
    out.push_str(&format!("- Install dir: `{}`\n", redact_path_for_bundle(install_dir)));
    // Phase 18: explain the redaction placeholder so the reader knows
    // what `<localdata>` means in subsequent paths. Without this, the
    // renderer-friendly form is unambiguous to a tool but mysterious
    // to a human seeing the bundle for the first time.
    out.push_str("- `<localdata>` placeholder: `%LOCALAPPDATA%/com.bot.mmorpg.ai/` (substituted in paths to avoid markdown auto-link)\n");
    out.push_str(&format!(
        "- Error count: {} (Rust: {}, sidecar: {})\n",
        rust_errors.len() + sidecar_entries.len(),
        rust_errors.len(),
        sidecar_entries.len()
    ));
    if let Some(d) = doctor {
        let verdict = d
            .get("verdict")
            .and_then(|v| v.as_str())
            .unwrap_or("unknown");
        let elapsed_ms = d
            .get("elapsed_ms")
            .and_then(|v| v.as_u64())
            .unwrap_or(0);
        out.push_str(&format!(
            "- Runtime doctor: `{}` (elapsed {}ms)\n",
            verdict, elapsed_ms
        ));
    }
    if let Some(rep) = launch_report {
        out.push_str(&format!("- Sidecar launch: `{}`", rep.status));
        if let Some(code) = rep.exit_code {
            out.push_str(&format!(" (exit {})", code));
        }
        out.push('\n');
    }
    out.push('\n');

    // Phase 4: lead with the launch report when present so the
    // first thing the AI / human reviewer sees is "what we tried
    // to start, what came back, did /health respond". Errors,
    // doctor checks, and probe payload follow.
    if let Some(rep) = launch_report {
        out.push_str(&format_launch_report_md(rep));
        // Phase 10: paste-ready PowerShell repro command embedded
        // inside the launch block so a user can re-run the failing
        // launch by hand (no 60s supervisor budget) without leaving
        // the bundle to look up the command.
        if rep.status != "ok" {
            out.push_str(&format_repro_command(rep));
        }

        // Phase 10: self-diagnosis -- ranked list of likely causes
        // with confidence + concrete fix. Comes BEFORE the raw
        // Errors block so the reader sees the conclusion before
        // the JSON dump.
        let diagnoses = analyze_launch_report(rep, rust_errors);
        if !diagnoses.is_empty() {
            out.push_str("\n## Likely Causes\n\n");
            out.push_str(
                "_Pattern-matched against known failure modes. Apply the fix \
                 for the highest-confidence rule that matches your install._\n\n",
            );
            for (i, d) in diagnoses.iter().enumerate() {
                out.push_str(&format!(
                    "### {}. {} (confidence: `{}`)\n\n",
                    i + 1,
                    d.cause,
                    d.confidence
                ));
                out.push_str(&format!("**Fix:** {}\n\n", d.fix));
            }
        }
    }

    // Phase 10: install-layout snapshot. Caller computes via
    // format_install_layout(app) and passes the rendered Markdown.
    // Surfaces missing __init__.py / partial extractions etc.
    // without the user having to run shell commands.
    if let Some(layout) = install_layout_md {
        out.push_str(layout);
    }

    out.push_str("## Errors\n\n");

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

    if let Some(d) = doctor {
        out.push_str(
            "## Runtime doctor\n\n\
             _Self-test of the bundled Python runtime. Each check \
             names the failing submodule / dependency precisely so \
             the AI assistant can map an `error` row to a concrete \
             remediation (VC++ redist, AV exclusion, partial install \
             repair, etc.). Generated by `scripts/runtime_doctor.py \
             --selftest`._\n\n",
        );
        // Compact summary table first (markdown), then the full JSON.
        if let Some(checks) = d.get("checks").and_then(|v| v.as_array()) {
            out.push_str("| Check | Status | Detail |\n");
            out.push_str("|---|---|---|\n");
            for c in checks {
                let name = c.get("name").and_then(|v| v.as_str()).unwrap_or("?");
                let status = c.get("status").and_then(|v| v.as_str()).unwrap_or("?");
                let detail = c
                    .get("detail")
                    .and_then(|v| v.as_str())
                    .unwrap_or("")
                    .replace('|', "\\|")
                    .replace('\n', " ");
                let icon = match status {
                    "ok" => "OK",
                    "warn" => "WARN",
                    "error" => "ERR",
                    _ => "?",
                };
                out.push_str(&format!("| `{}` | {} | {} |\n", name, icon, detail));
            }
            out.push('\n');
        }
        out.push_str("```json\n");
        out.push_str(&serde_json::to_string_pretty(d).unwrap_or_default());
        out.push_str("\n```\n\n");
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
        Paste this entire block into your AI coding assistant or attach \
        to a GitHub issue. It contains everything needed to debug startup \
        failures, runtime crashes, and backend errors: the launch \
        command + env + stdout + stderr + health-probe result, plus any \
        captured Python tracebacks, the runtime doctor verdict, and the \
        deep system probe. Always review the proposed patch before \
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

    // Runtime doctor: append the structural runtime self-test so the
    // AI assistant gets the per-check picture (torch.testing intact,
    // VC++ present, port bindable, ...) instead of having to infer
    // it from a generic traceback. Best-effort -- if the doctor itself
    // can't be invoked, we still return whatever we have.
    let doctor: Option<Value> = match runtime_doctor(app.clone()).await {
        Ok(v) => Some(v),
        Err(_) => None,
    };

    let version = app.package_info().version.to_string();
    let install_dir = installation_dir().display().to_string();
    // Phase 4: pull the most recent launch report so the bundle
    // leads with command/cwd/env/stdout/stderr/health -- the
    // canonical answer to "why did the sidecar fail to start".
    // Explicit `as_ref().cloned()` rather than `g.clone()` because
    // MutexGuard itself isn't Clone -- we clone through the Deref.
    let launch_report: Option<SidecarLaunchReport> = inner
        .last_launch_report
        .lock()
        .ok()
        .and_then(|g| g.as_ref().cloned());
    // Phase 10: capture the install-layout snapshot only when a
    // launch failure is implicated (keeps healthy bundles small).
    let install_layout: Option<String> = match launch_report.as_ref() {
        Some(r) if r.status != "ok" => Some(format_install_layout(&app)),
        _ => None,
    };
    Ok(build_ai_bundle(
        &rust_errors,
        &sidecar_entries,
        probe.as_ref(),
        doctor.as_ref(),
        launch_report.as_ref(),
        install_layout.as_deref(),
        &version,
        &install_dir,
    ))
}

/// Tauri command: return the most recent sidecar launch report
/// formatted as Markdown. Subset of the full debug bundle, useful
/// for "I just want the launch info, not the error history" flows
/// (e.g., a power user pasting only the spawn snapshot into a chat).
///
/// Returns `(markdown_string, has_report)` so the UI can show a
/// distinct empty state vs. an "ok" launch.
#[tauri::command]
fn get_sidecar_launch_report(state: tauri::State<AppState>) -> Value {
    // See note above about explicit Deref-clone.
    let snap: Option<SidecarLaunchReport> = state
        .inner
        .last_launch_report
        .lock()
        .ok()
        .and_then(|g| g.as_ref().cloned());
    match snap {
        Some(rep) => {
            let md = format_launch_report_md(&rep);
            json!({
                "ok": true,
                "status": rep.status,
                "markdown": md,
                "raw": rep,
            })
        }
        None => json!({
            "ok": false,
            "status": "none",
            "markdown": "## Sidecar Launch\n\n_(no launch report captured yet -- the sidecar has not been spawned this session)_\n",
        }),
    }
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
                current_sidecar_job: Mutex::new(None),
                sidecar_startup_failed: std::sync::atomic::AtomicBool::new(false),
                early_log: Mutex::new(std::collections::VecDeque::with_capacity(EARLY_LOG_CAP)),
                last_launch_report: Mutex::new(None),
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

            // First-launch migration: move runtime/datasets/models/logs/
            // content from the legacy installation directory
            // (Program Files\BOT-MMORPG-AI\) into %LOCALAPPDATA%\
            // com.bot.mmorpg.ai\. Idempotent and best-effort -- never
            // blocks startup. Must run BEFORE start_sidecar_server because
            // the sidecar mutates the runtime tree (sitecustomize.py,
            // _pth file) on launch.
            migrate_legacy_runtime_if_needed(&app_handle);

            // Phase 7: AAA-grade startup -- bounded retry with
            // exponential backoff + /health gate. The helper handles
            // attempt counting, the health round-trip, slot
            // population, and flag flipping on terminal failure.
            // setup() only owns the success-side wiring (liveness
            // watch, post-launch health enrichment) and the failure
            // hint block.
            match try_start_sidecar_with_retries_and_gate(&app_handle) {
                Ok(()) => {
                    let win = app.get_window("main");
                    emit_with_buffer(
                        &state.inner,
                        win.as_ref(),
                        "[System] Sidecar READY".to_string(),
                    );

                    // Phase 3.2: spawn the lightweight liveness loop
                    // now that we have a SidecarApi to probe. Detects
                    // "process died after READY" failure modes that
                    // the slot-presence check cannot catch (segfault,
                    // OOM, AV quarantine).
                    spawn_sidecar_liveness_watch(app_handle.clone());

                    // Phase 4: enrich the launch report with the FIRST
                    // /health round-trip result. The gate already
                    // verified /health -- this call is for the bundle
                    // payload (status + body), not for readiness.
                    let inner_clone = state.inner.clone();
                    tauri::async_runtime::spawn(async move {
                        record_post_launch_health(inner_clone).await;
                    });
                }
                Err(e) => {
                    // sidecar_startup_failed is already set by the
                    // helper; we only emit the user-facing hint
                    // block here (the helper has emitted per-attempt
                    // detail already).
                    let win = app.get_window("main");
                    emit_with_buffer(
                        &state.inner,
                        win.as_ref(),
                        format!("[Fatal] Sidecar failed after {} attempts: {}", STARTUP_MAX_ATTEMPTS, e),
                    );

                    // Phase 11: surface the highest-confidence
                    // root cause BEFORE the generic hint ladder,
                    // so a user with a real Python traceback in
                    // stderr (e.g. ModuleNotFoundError) doesn't
                    // start chasing AV / cold-disk first. We
                    // re-use the same analyze_launch_report rules
                    // as the bundle so the in-app guidance and the
                    // bundle's "Likely Causes" agree.
                    let snapshot: Option<SidecarLaunchReport> = state
                        .inner
                        .last_launch_report
                        .lock()
                        .ok()
                        .and_then(|g| g.as_ref().cloned());
                    if let Some(rep) = snapshot.as_ref() {
                        let diagnoses = analyze_launch_report(rep, &[]);
                        if let Some(top) = diagnoses.first() {
                            emit_with_buffer(
                                &state.inner,
                                win.as_ref(),
                                format!("[Root cause] {} (confidence: {})", top.cause, top.confidence),
                            );
                            emit_with_buffer(
                                &state.inner,
                                win.as_ref(),
                                format!("[Fix] {}", top.fix),
                            );
                        }
                    }

                    // Generic hint ladder (kept as fallback for
                    // when no rule matched, AND as additional
                    // context when one did).
                    let lines: [&str; 8] = [
                        "[Hint] If the root cause above doesn't apply, try (in order of frequency):",
                        "  1. Antivirus is scanning the bundled Python runtime.",
                        "     Add this folder to AV exclusions: %LOCALAPPDATA%\\com.bot.mmorpg.ai\\runtime\\",
                        "  2. Cold-disk first launch: torch/numpy/fastapi cold imports timed out.",
                        "     Restart the app -- the second launch is always faster.",
                        "  3. Embedded Python crashed on import. See [Sidecar stderr] lines above for the traceback.",
                        "     Open Settings -> System Tools -> Run Diagnostics to inspect.",
                        "  4. Loopback firewall blocking 127.0.0.1. Whitelist BOT-MMORPG-AI.",
                    ];
                    for l in lines {
                        emit_with_buffer(&state.inner, win.as_ref(), l.to_string());
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
            preflight_action,
            runtime_doctor,
            submit_sidecar_job_cmd,
            restart_sidecar,
            drain_early_log,
            open_local_data_folder,
            open_datasets_folder,
            add_av_exclusion,
            repair_runtime,
            repair_pytorch_via_pip,
            support_report,
            check_for_update,
            app_info,
            recent_errors_for_ai,
            clear_recent_errors,
            get_sidecar_launch_report,
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

    // --- is_architecture_id (issue #76) ---
    //
    // The UI's fallback catalog advertises architectures with
    // path == id, so an activated architecture reaches the bot
    // preflight as a bare token. Telling that user their model was
    // "deleted or moved" was the single most confusing message in
    // issue #76 -- it named a directory that never existed.

    #[test]
    fn test_is_architecture_id_recognises_bare_arch() {
        assert!(is_architecture_id("efficientnet_lstm"));
        assert!(is_architecture_id("resnet18_lstm"));
        assert!(is_architecture_id("  mobilenet_v3  "));
    }

    #[test]
    fn test_is_architecture_id_rejects_paths() {
        // A real model dir must never be misreported as a template,
        // even when its LAST component happens to be an arch name.
        assert!(!is_architecture_id(
            "C:\\Users\\x\\AppData\\Local\\com.bot.mmorpg.ai\\trained_models\\custom\\efficientnet_lstm"
        ));
        assert!(!is_architecture_id("trained_models/custom/efficientnet_lstm"));
    }

    #[test]
    fn test_is_architecture_id_rejects_unknown_and_empty() {
        assert!(!is_architecture_id(""));
        assert!(!is_architecture_id("   "));
        assert!(!is_architecture_id("my_trained_model_v3"));
    }

    #[test]
    fn test_known_archs_covers_ui_default_architectures() {
        // Guards the mobilenet_v3 / mobilenetv3 split that made the
        // train preflight reject a model the UI itself offered.
        let ui_defaults = [
            "efficientnet_lstm",
            "efficientnet_simple",
            "mobilenet_v3",
            "mobilenetv3",
            "resnet18_lstm",
            "efficientnet_transformer",
            "multihead_action",
            "game_attention",
            "inception_v3",
            "alexnet",
        ];
        for arch in ui_defaults {
            assert!(
                KNOWN_ARCHS.contains(&arch),
                "UI offers architecture '{}' that the train preflight rejects",
                arch
            );
        }
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
                current_sidecar_job: Mutex::new(None),
                sidecar_startup_failed: std::sync::atomic::AtomicBool::new(false),
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

    // --- MVP-1: %LOCALAPPDATA% migration helpers ---
    //
    // We can't construct an AppHandle in unit tests (it requires a
    // running Tauri runtime), so the resolver itself is exercised
    // via integration / smoke tests. The two file helpers below
    // (same_path + copy_dir_recursive) ARE pure-fs and unit-testable.

    #[test]
    fn test_same_path_identical_inputs() {
        let here = std::env::current_dir().unwrap();
        assert!(same_path(&here, &here));
    }

    #[test]
    fn test_same_path_distinct_inputs() {
        let parent = std::env::current_dir().unwrap();
        let child = parent.join("Cargo.toml");
        // Cargo.toml is a file, not a dir, but same_path only canonicalizes
        // and compares -- the comparison should still be false because the
        // paths differ.
        if child.exists() {
            assert!(!same_path(&parent, &child));
        }
    }

    #[test]
    fn test_copy_dir_recursive_round_trip() {
        // Build a small tree under a temp dir, copy it, verify contents
        // match. Exercises the cross-volume fallback path of
        // migrate_legacy_runtime_if_needed.
        let tmp = std::env::temp_dir().join(format!(
            "botmmo_copy_test_{}",
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        let src = tmp.join("src");
        let dst = tmp.join("dst");
        let nested = src.join("a").join("b");
        fs::create_dir_all(&nested).unwrap();
        fs::write(src.join("top.txt"), b"top").unwrap();
        fs::write(nested.join("leaf.txt"), b"leaf").unwrap();

        copy_dir_recursive(&src, &dst).unwrap();

        assert_eq!(fs::read(dst.join("top.txt")).unwrap(), b"top");
        assert_eq!(
            fs::read(dst.join("a").join("b").join("leaf.txt")).unwrap(),
            b"leaf"
        );

        // cleanup -- best-effort, this is a unit test
        let _ = fs::remove_dir_all(&tmp);
    }
}
