// tauri-ui/main.js
// ------------------------------------------------------------
// BOT-MMORPG-AI (Tauri UI) - UPDATED v0.1.9
// - Fixed Settings: Loads/Saves API Keys correctly via Rust
// - Adds ModelHub commands wiring
// - Adds AI Chat wiring
// ------------------------------------------------------------

// Phase 23-B: build-time fingerprint. `scripts/stamp_ui_build_tag.py`
// substitutes `%BUILD_TAG%` with the live `git describe`/version
// string before `make dev` and `make artifact` bundle this file. At
// runtime we log it inside DOMContentLoaded so any debug bundle the
// user pastes shows EXACTLY which UI bundle was loaded -- if it
// drifts from the Rust shell version (also logged via app_info),
// we instantly know we have a stale-JS situation and can act on it
// instead of guessing whether a fix shipped.
//
// The `%BUILD_TAG%` literal is a sentinel: if the substitution
// hasn't happened yet (raw checkout, no make target run), the JS
// reports "ui-bundle:dev (unstamped)" instead of pretending to be
// versioned.
const BUILD_TAG = "%BUILD_TAG%";
window.__BUILD_TAG__ = BUILD_TAG;

// State & Tauri Globals
const __rawInvoke = window.__TAURI__ ? window.__TAURI__.invoke : null;
const listen = window.__TAURI__ ? window.__TAURI__.event.listen : null;

// ---------------------------------------------------------------
// Issues #70 / #76: the argument-name bridge.
//
// Tauri derives each command's argument struct with serde's default
// camelCase renaming, so a Rust handler declared as
//
//     async fn list_datasets(game_id: Option<String>)
//
// expects the JS payload key `gameId` -- NOT `game_id`. Half of this
// file was written against the snake_case names, which produced two
// distinct failure classes depending on the Rust type:
//
//   Option<T> args  -> silently deserialize to None. `list_datasets`,
//                      `mh_get_catalog_data`, `generate_dataset_name`,
//                      `open_datasets_folder` and `delete_dataset` all
//                      dropped `game_id` and fell back to
//                      DEFAULT_GAME_ID ("genshin_impact"). Recording
//                      wrote to datasets/<custom game>/ (start_recording
//                      happened to send both key styles) while every
//                      listing read datasets/genshin_impact/ -- so a
//                      custom-game recording existed on disk but never
//                      appeared in the Train tab. That is issue #70
//                      verbatim, including why "select Genshin Impact"
//                      was a working workaround.
//   Required args   -> hard error. `modelhub_validate_model` produced
//                      "invalid args `modelDir` ... missing required
//                      key modelDir" (issue #76).
//
// Rather than hand-patch every call site (and re-break on the next one
// added), normalize centrally: every payload key is emitted in BOTH
// snake_case and camelCase. Serde ignores the unknown twin, so this is
// safe for handlers using either convention, including any older
// shipped binary a user upgrades from.
// ---------------------------------------------------------------
function __toCamel(key) {
  return key.replace(/_+([a-z0-9])/g, (_, c) => c.toUpperCase());
}

function __toSnake(key) {
  return key.replace(/([a-z0-9])([A-Z])/g, "$1_$2").toLowerCase();
}

function normalizeInvokeArgs(args) {
  if (!args || typeof args !== "object" || Array.isArray(args)) return args;
  const out = { ...args };
  for (const [k, v] of Object.entries(args)) {
    const camel = __toCamel(k);
    const snake = __toSnake(k);
    // Never overwrite a key the caller set explicitly -- a call site
    // that already sends both forms stays authoritative.
    if (camel !== k && !(camel in out)) out[camel] = v;
    if (snake !== k && !(snake in out)) out[snake] = v;
  }
  return out;
}

const invoke = __rawInvoke
  ? (cmd, args, options) =>
      args === undefined || args === null
        ? __rawInvoke(cmd)
        : __rawInvoke(cmd, normalizeInvokeArgs(args), options)
  : null;

// Exposed for the UI regression tests (and for debug bundles, where
// seeing the exact payload the shell received is worth a lot).
window.__normalizeInvokeArgs = normalizeInvokeArgs;

// Global State
let isRecording = false;
let isBotRunning = false;

// Phase 4 (gap #5): per-action precondition gate. Calls Rust's
// preflight_action (cheap, ~50ms typical) before each start_recording /
// start_training / start_bot. Returns true if the action may proceed,
// false (with a toast + terminal log) if any precondition is missing.
//
// Failure modes covered:
//   - sidecar /health unresponsive
//   - non-writable datasets/ or trained_models/
//   - dataset name empty / contains path separators / collides
//   - dataset_id missing or unknown for training
//   - architecture not in the allow-list for training
//   - another sidecar job already running
//   - active model missing for inference
//   - monitor selection invalid
//
// Soft fail: if the preflight command itself is missing (old Rust
// binary on first upgrade) or throws, we let the action through --
// the user gets the legacy fail-fast behavior, not a hard block.
// Phase 5: keep the dashboard hero, the header chip, and the
// install-health banner in sync. Without this, a user with a
// failed sidecar saw the contradictory triple-message
//   - "Backend installation is incomplete" (banner, red)
//   - "🟢 System Ready" (hero, green)
//   - "Running • Rust Backend Active" (header chip, green)
// which destroyed trust in the rest of the UI. Now the three
// surfaces all reflect the same single source of truth: install
// health verdict.
function applyDashboardStatus(verdict) {
  // Dashboard hero (#tab-dashboard .hero-status .hero-text)
  const heroH2 = document.querySelector('#tab-dashboard .hero-status .hero-text h2');
  const activePill = document.getElementById('active-game-pill');
  const headerBadge = document.getElementById('backend-status-badge');
  const headerStatus = document.getElementById('backend-status');
  const footerText = document.getElementById('backend-status-text');
  const dot = document.querySelector('.status-dot');

  if (verdict === 'error') {
    if (heroH2) {
      heroH2.style.color = 'var(--accent)'; // red/orange accent
      heroH2.textContent = '⚠️ System Issue';
    }
    if (activePill?.parentElement) {
      activePill.parentElement.innerHTML =
        '<span style="opacity:.8;">Backend not running &mdash; see banner above.</span>';
    }
    if (headerBadge) headerBadge.textContent = 'Degraded';
    if (headerStatus) headerStatus.textContent = 'Backend not running';
    if (footerText) footerText.textContent = 'System Issue';
    if (dot) dot.style.backgroundColor = 'var(--accent)';
  } else if (verdict === 'warning') {
    if (heroH2) {
      heroH2.style.color = 'var(--warning, #facc15)';
      heroH2.textContent = '🟡 System Ready (with warnings)';
    }
    if (headerBadge) headerBadge.textContent = 'Running';
    if (headerStatus) headerStatus.textContent = 'Rust Backend Active';
    if (footerText) footerText.textContent = 'System Online';
    if (dot) dot.style.backgroundColor = 'var(--warning, #facc15)';
  } else {
    // ready
    if (heroH2) {
      heroH2.style.color = 'var(--secondary)';
      heroH2.textContent = '🟢 System Ready';
    }
    if (headerBadge) headerBadge.textContent = 'Running';
    if (headerStatus) headerStatus.textContent = 'Rust Backend Active';
    if (footerText) footerText.textContent = 'System Online';
    if (dot) dot.style.backgroundColor = 'var(--success)';
  }
}

// Phase 4 (gap #5): visually gate the three action buttons on
// install_health.verdict. "error" -> disabled with a tooltip;
// "ready"/"warning" -> normal. Called from checkInstallHealth after
// it has merged the runtime_doctor checks.
//
// We re-enable on every health refresh (Run Diagnosis click, restart
// sidecar, etc.) so a user who fixes the underlying issue without
// relaunching the app gets their buttons back without confusion.
function applyHealthGate(verdict) {
  const blocked = verdict === "error";
  const tooltip = blocked
    ? "Install health is in error state. Run Diagnosis (Settings -> System Tools) and fix the red rows first."
    : "";
  for (const id of ["btnRecord", "btnStartTraining", "btnStartBot"]) {
    const el = document.getElementById(id);
    if (!el) continue;
    el.disabled = blocked;
    el.title = tooltip;
    // Also surface visually in case the button's CSS doesn't restyle
    // disabled state. Soft change so we don't fight the tab's design.
    el.style.opacity = blocked ? "0.55" : "";
    el.style.cursor = blocked ? "not-allowed" : "";
  }
}

// Phase 23-A: returns the full preflight response object so callers
// can read server-resolved fields like resolved_dataset_name. The
// presence of `.ok` (boolean) replaces the old "true on pass" bool
// contract -- callers should check `.ok`. For backward compat with
// any caller that still does `if (await preflightOrAlert(...))`,
// the returned object is truthy on success and on transient failure
// (preflight unavailable). It returns a falsy value (null) ONLY on
// an explicit blocking rejection.
async function preflightOrAlert(kind, params) {
  if (!invoke) return { ok: true, reasons: [] };
  try {
    // Bridge hardening now lives in normalizeInvokeArgs() (see the
    // invoke wrapper at the top of this file), which emits both the
    // snake_case and camelCase form of every key for EVERY command --
    // preflight_action was only one of a dozen affected call sites.
    const res = await invoke("preflight_action", { kind, ...params });
    if (res && res.ok) return res;
    const reasons = (res && Array.isArray(res.reasons) && res.reasons.length)
      ? res.reasons
      : ["Unknown precondition failure."];
    const summary = reasons.map((r) => "• " + r).join("\n");
    logToTerminal(`Preflight (${kind}) blocked the action:\n${summary}`, "error");
    if (window.notifyError) {
      window.notifyError(
        `Cannot start ${kind}`,
        summary,
        [
          { label: "Run Diagnosis", onClick: () => {
            window.openSettings?.(); window.switchSettingsTab?.('system-tools');
            document.getElementById('btn-run-diagnosis')?.click();
          }},
          { label: "Dismiss", onClick: () => {}, primary: false },
        ]
      );
    } else {
      alert(`Cannot start ${kind}:\n\n${summary}`);
    }
    return null;
  } catch (e) {
    // preflight_action missing on the Rust side -- old binary, first
    // upgrade. Don't block; warn quietly so support can spot it.
    console.warn("preflight_action unavailable:", e);
    return { ok: true, reasons: [], _missing: true };
  }
}

// ModelHub UI State
const DEFAULT_GAME_ID = "genshin_impact";
let modelhubAvailable = false;
let selectedGameId = DEFAULT_GAME_ID;
let selectedDatasetId = "";
let selectedBuiltinModelPath = "";
let selectedModelRegistryId = "";
let selectedLocalModelPath = "";
// Phase 29: tracks the last real (non-action) selection in the
// train-dataset-id <select>. MUST live at module scope so
// populateTrainDatasetDropdown can seed it after every refresh --
// the wireEvents()-local version was unreachable from there, which
// meant the "Refresh datasets" action would revert sel.value to ""
// for any user who hadn't manually picked a dataset yet (a fresh
// app load with auto-selected latest had _lastRealTrainDatasetValue
// frozen at ""). That was one of the paths producing the empty
// dataset_id at preflight time.
let _lastRealTrainDatasetValue = "";

// Cache catalog payload
let currentCatalog = {
  builtin_models: [],
  datasets: [],
  models: [],
  local_models: [],
  active: null,
};

// --- TAB NAVIGATION ---
window.showTab = function (tabId) {
  const titles = {
    dashboard: "Dashboard",
    teach: "Teach mode — record gameplay data",
    train: "Neural Network Training",
    run: "Run Bot",
    strategist: "AI Strategist",
    models: "ModelHub",
    wizard: "Training School",
  };

  const pageTitle = document.getElementById("page-title");
  if (pageTitle) pageTitle.textContent = titles[tabId] || "Dashboard";

  document.querySelectorAll(".tab-content").forEach((el) => {
    el.classList.remove("active");
    el.style.display = "";
  });

  const selectedTab = document.getElementById("tab-" + tabId);
  if (selectedTab) {
    selectedTab.classList.add("active");
    if (tabId === "teach" || tabId === "train") selectedTab.style.display = "flex";
    else selectedTab.style.display = "block";
  }

  document.querySelectorAll(".nav-btn").forEach((el) => el.classList.remove("active"));
  const selectedBtn =
    document.getElementById("btn-" + tabId) || document.querySelector(`button[data-tab="${tabId}"]`);
  if (selectedBtn) selectedBtn.classList.add("active");

  // Phase 22: when the user navigates to the Teach tab, populate the
  // dataset-name input if empty. Belt-and-suspenders for the Phase 21
  // fix in toggleRecord -- the user sees the auto-name BEFORE clicking
  // Start, so there's no possibility of a "Dataset name is empty"
  // surprise. Defensive: only writes if the field has no user input.
  if (tabId === "teach") {
    try {
      if (typeof updateDatasetName === "function") updateDatasetName();
    } catch (e) {
      console.warn("updateDatasetName on tab show failed:", e);
    }
  }
};

// --- LOGGING ---
function logToTerminal(msg, type = "info") {
  const terminal = document.getElementById("terminal");
  if (!terminal) return;

  const timestamp = new Date().toLocaleTimeString();
  const entry = document.createElement("div");
  entry.className = `log-entry log-${type}`;
  entry.innerHTML = `<span class="log-time">[${timestamp}]</span> ${msg}`;

  terminal.appendChild(entry);
  terminal.scrollTop = terminal.scrollHeight;

  // Keep log size manageable
  const entries = terminal.querySelectorAll(".log-entry");
  if (entries.length > 200) entries[0].remove();
}

// Backward-compat global hook
window.update_terminal = function (line) {
  logToTerminal(line, "info");

  // Parse progress for Training
  if (line.includes("Epoch")) {
    const match = line.match(/Epoch (\d+)\/(\d+)/);
    if (match) {
      const current = parseInt(match[1], 10);
      const total = parseInt(match[2], 10);
      const percent = Math.round((current / total) * 100);

      const progressBar = document.getElementById("progress-bar");
      const pctDisplay = document.getElementById("train-pct");

      if (progressBar) progressBar.style.width = percent + "%";
      if (pctDisplay) pctDisplay.textContent = percent + "%";
    }
  }

  // Sidecar status chip (UI-Phase A). Drives off the [Sidecar]
  // heartbeat lines emitted by start_sidecar_server / restart_sidecar
  // so the chip reflects live state without separate IPC.
  updateSidecarChipFromLogLine(line);
  maybeRaiseCrashNotification(line);
};

// Reusable AI bundle copy: builds the full bundle (including in-app
// log tail) and writes to clipboard. Returns true on success. Used
// by the Settings -> System Tools button, the crash-reporter
// notification, and any future UI surface that needs one-click
// "send to AI assistant".
// Phase 4: renamed from copyAIBundle -> copyDebugBundle. The bundle
// now leads with the SidecarLaunchReport (command, env, stdout,
// stderr, /health), so the framing is "everything needed to debug
// startup or backend failures", not just "AI fix request". The old
// copyAIBundle name is kept as an alias below for any external code
// that still calls it.
window.copyDebugBundle = async function copyDebugBundle() {
  if (!window.__TAURI__?.invoke) {
    window.notifyError?.("Copy Debug Bundle failed", "Tauri unavailable.");
    return false;
  }
  try {
    let bundle = await window.__TAURI__.invoke("recent_errors_for_ai");
    const term = document.getElementById("terminal");
    if (term) {
      const lines = Array.from(term.querySelectorAll(".log-entry"))
        .map(el => el.textContent.replace(/\s+/g, " ").trim());
      if (lines.length) {
        bundle += "\n## Recent in-app log tail\n\n```\n"
               +  lines.slice(-200).join("\n")
               +  "\n```\n";
      }
    }
    await navigator.clipboard.writeText(bundle);
    window.notifySuccess?.(
      "Debug bundle copied",
      "Paste into your AI assistant or a GitHub issue. Includes sidecar launch (command, env, stdout, stderr, /health), likely-cause analysis, install layout, errors, runtime doctor, and recent log."
    );
    return true;
  } catch (e) {
    window.notifyError?.("Copy debug bundle failed", String(e));
    return false;
  }
};
// Backward-compatibility alias -- any external/legacy call site
// (notifications spawned before this script ran, etc.) still works.
window.copyAIBundle = window.copyDebugBundle;

// Job-failed crash reporter. The log-bridge worker emits
// "[Sidecar] Job XYZ -> failed (exit_code=N)" when a sidecar-owned
// child exits non-zero. We surface a persistent notification with
// one-click "Copy Debug Bundle" so the user grabs context immediately
// instead of having to navigate to Settings -> System Tools after
// the failure scrolls off the log.
function maybeRaiseCrashNotification(line) {
  const m = line.match(/\[Sidecar\] Job ([a-f0-9]+) -> (failed|cancelled) \(exit_code=([^\)]+)\)/);
  if (!m) return;
  const [, jobId, status, exitCode] = m;
  if (status !== "failed") return;  // cancelled is user-initiated; don't surprise them.
  // Only surface once per job_id even if the line is duplicated.
  window.__crashedJobs = window.__crashedJobs || new Set();
  if (window.__crashedJobs.has(jobId)) return;
  window.__crashedJobs.add(jobId);
  window.notifyError?.(
    `Job ${jobId} failed (exit_code=${exitCode})`,
    "The sidecar's child process exited with an error. Click below to copy the full debug bundle.",
    [
      { label: "Copy debug bundle", onClick: () => window.copyDebugBundle?.() },
      { label: "Run diagnostics",  onClick: () => document.getElementById("install-health-open-diagnosis")?.click(), primary: false },
      { label: "Dismiss",          onClick: () => {}, primary: false },
    ]
  );
}

// Sidecar chip state machine. Pure DOM, no async dependencies, so
// missing elements (chip not present in some test layouts) are no-ops.
function updateSidecarChipFromLogLine(line) {
  const chip       = document.getElementById("sidecar-status-chip");
  const stateEl    = document.getElementById("sidecar-chip-state");
  const elapsedEl  = document.getElementById("sidecar-chip-elapsed");
  const actionsEl  = document.getElementById("sidecar-chip-actions");
  if (!chip || !stateEl) return;

  const setState = (state, label, elapsedText = "", showActions = false) => {
    chip.dataset.state = state;
    chip.hidden = false;
    stateEl.textContent = label;
    if (elapsedEl) elapsedEl.textContent = elapsedText;
    if (actionsEl) actionsEl.hidden = !showActions;
  };

  // Heartbeat: "[Sidecar] still warming up... 12s/60s elapsed (cold-disk import)"
  const heartbeat = line.match(/\[Sidecar\] still warming up\.\.\. (\d+)s\/(\d+)s/);
  if (heartbeat) {
    setState("starting", "Starting...", `${heartbeat[1]}s/${heartbeat[2]}s`);
    return;
  }
  if (line.includes("[System] Sidecar READY")) {
    setState("ready", "Ready", "");
    // Auto-fade after 3s -- the chip stays in DOM but hides.
    setTimeout(() => { if (chip.dataset.state === "ready") chip.hidden = true; }, 3000);
    return;
  }
  if (line.includes("[Fatal] Sidecar failed")) {
    setState("failed", "Failed", "", true);
    return;
  }
  if (line.includes("[System] Restart sidecar requested")) {
    setState("starting", "Restarting...", "0s/60s");
    return;
  }
  if (line.includes("[Fatal] Sidecar restart failed")) {
    setState("failed", "Restart failed", "", true);
    return;
  }
}

// --- BACKEND STATUS ---
function updateBackendStatus(status, message) {
  const statusText = document.getElementById("backend-status");
  const statusBadge = document.getElementById("backend-status-badge");
  const footerText = document.getElementById("backend-status-text");

  if (statusText) statusText.textContent = message;
  if (statusBadge) statusBadge.textContent = status;
  if (footerText) footerText.textContent = status === "Running" ? "System Online" : "System Offline";

  const dot = document.querySelector(".status-dot");
  if (dot) dot.style.backgroundColor = status === "Running" ? "var(--success)" : "var(--accent)";
}

// ============================================================
// ✅ NEW: SETTINGS MANAGEMENT (Fixes API Key Error)
// ============================================================

// 1. Load Settings from Rust -> UI Modal
window.loadSettingsIntoModal = async function() {
  if (!invoke) return;
  try {
    const config = await invoke("get_ai_config");
    
    // Select Provider
    const providerSel = document.getElementById("settings-provider");
    if (providerSel) {
        providerSel.value = (config.provider || "gemini").trim().toLowerCase();
    }

    // Populate Key based on provider
    const keyInput = document.getElementById("settings-api-key");
    if (keyInput) {
      const p = (config.provider || "").trim().toLowerCase();
      if (p === "openai") {
        keyInput.value = config.openai_key || "";
      } else {
        keyInput.value = config.gemini_key || "";
      }
    }
  } catch (e) {
    console.warn("Failed to load settings:", e);
    logToTerminal("Error loading settings: " + e, "warning");
  }
}

// 2. Save Settings from UI Modal -> Rust
async function saveSettingsFromModal() {
  if (!invoke) return alert("Tauri backend not found.");

  const provider = document.getElementById("settings-provider")?.value || "gemini";
  const api_key = (document.getElementById("settings-api-key")?.value || "").trim();
  
  if (!api_key) return alert("Please enter an API Key.");

  const btn = document.getElementById("btn-save-settings");
  if (btn) {
    btn.disabled = true;
    btn.textContent = "Saving...";
  }

  try {
    // Call the Rust command
    await invoke("save_configuration", { provider, api_key });

    if (btn) btn.textContent = "Saved!";
    logToTerminal(`Configuration saved. Provider: ${provider}`, "success");

    // Close modal after delay
    setTimeout(() => {
      if (btn) { 
        btn.textContent = "Save Configuration"; 
        btn.disabled = false; 
      }
      document.getElementById("settings-modal-overlay")?.classList.remove("open");
    }, 800);
  } catch (e) {
    if (btn) {
        btn.disabled = false;
        btn.textContent = "Save Configuration";
    }
    alert("Save failed: " + e);
    logToTerminal("Save failed: " + e, "error");
  }
}

// ============================================================
// MODELHUB UI HELPERS
// ============================================================

function getEl(id) {
  return document.getElementById(id);
}

function setSelectOptions(selectEl, items, getLabel, getValue, placeholder = "Select...", defaultValue = "") {
  if (!selectEl) return;
  selectEl.innerHTML = "";
  const opt0 = document.createElement("option");
  opt0.value = "";
  opt0.textContent = placeholder;
  selectEl.appendChild(opt0);

  for (const it of items) {
    const opt = document.createElement("option");
    opt.value = getValue(it);
    opt.textContent = getLabel(it);
    if (defaultValue && opt.value === defaultValue) {
      opt.selected = true;
    }
    selectEl.appendChild(opt);
  }
}

// =============================================================================
// GAME PRESETS - Optimal Settings for Each Game
// =============================================================================

const GAME_PRESETS = {
  genshin_impact: {
    id: "genshin_impact",
    name: "Genshin Impact",
    icon: "⚔️",
    color: "#FFD93D",
    resolution: "480x270",
    action_space: "combat",
    architecture: "efficientnet_lstm",
    description: "Action RPG with elemental combat. Mobile UI scales well.",
    recommended_tasks: ["exploration", "farming", "combat", "domains"],
    notes: "Smooth animations, clear UI indicators. 480p captures all elements."
  },
  world_of_warcraft: {
    id: "world_of_warcraft",
    name: "World of Warcraft",
    icon: "🐉",
    color: "#FF6B35",
    resolution: "640x360",
    action_space: "extended",
    architecture: "efficientnet_lstm",
    description: "Classic MMORPG with complex addon UI system.",
    recommended_tasks: ["dungeons", "raids", "questing", "farming"],
    notes: "Complex UI with addons. 640p recommended for addon text readability."
  },
  final_fantasy_xiv: {
    id: "final_fantasy_xiv",
    name: "Final Fantasy XIV",
    icon: "🔮",
    color: "#4169E1",
    resolution: "640x360",
    action_space: "extended",
    architecture: "efficientnet_lstm",
    description: "Story-rich MMORPG with detailed hotbar system.",
    recommended_tasks: ["dungeons", "trials", "crafting", "gathering"],
    notes: "Detailed HUD with many skills. 640p for hotbar visibility."
  },
  guild_wars_2: {
    id: "guild_wars_2",
    name: "Guild Wars 2",
    icon: "🛡️",
    color: "#DC143C",
    resolution: "480x270",
    action_space: "combat",
    architecture: "efficientnet_lstm",
    description: "Dynamic events with clean UI design.",
    recommended_tasks: ["meta_events", "fractals", "pvp", "exploration"],
    notes: "Clean UI design. 480p sufficient for core gameplay."
  },
  lost_ark: {
    id: "lost_ark",
    name: "Lost Ark",
    icon: "⚡",
    color: "#FFB347",
    resolution: "640x360",
    action_space: "combat",
    architecture: "efficientnet_lstm",
    description: "Fast-paced ARPG with many skill indicators.",
    recommended_tasks: ["chaos_dungeons", "guardian_raids", "abyss"],
    notes: "Many skill indicators. 640p recommended for combat clarity."
  },
  elder_scrolls_online: {
    id: "elder_scrolls_online",
    name: "Elder Scrolls Online",
    icon: "📜",
    color: "#8B4513",
    resolution: "480x270",
    action_space: "combat",
    architecture: "efficientnet_lstm",
    description: "Action combat with minimal UI design.",
    recommended_tasks: ["questing", "dungeons", "pvp", "crafting"],
    notes: "Minimal UI design. 480p works well for action combat."
  },
  black_desert_online: {
    id: "black_desert_online",
    name: "Black Desert Online",
    icon: "🌙",
    color: "#191970",
    resolution: "640x360",
    action_space: "combat",
    architecture: "game_attention",
    description: "Fast action combat with detailed skill effects.",
    recommended_tasks: ["grinding", "lifeskills", "node_wars"],
    notes: "Action combat with many effects. 640p for skill visibility."
  },
  new_world: {
    id: "new_world",
    name: "New World",
    icon: "🏝️",
    color: "#228B22",
    resolution: "480x270",
    action_space: "combat",
    architecture: "efficientnet_lstm",
    description: "Survival MMORPG with clean modern UI.",
    recommended_tasks: ["expeditions", "gathering", "pvp", "crafting"],
    notes: "Clean modern UI. 480p captures gameplay well."
  },
  path_of_exile: {
    id: "path_of_exile",
    name: "Path of Exile",
    icon: "💀",
    color: "#8B0000",
    resolution: "640x360",
    action_space: "combat",
    architecture: "game_attention",
    description: "Complex ARPG with detailed loot and skills.",
    recommended_tasks: ["mapping", "bossing", "delve", "heist"],
    notes: "Complex UI with many indicators. 640p for item/skill visibility."
  },
  runescape: {
    id: "runescape",
    name: "RuneScape / OSRS",
    icon: "🗡️",
    color: "#D4AF37",
    resolution: "480x270",
    action_space: "standard",
    architecture: "mobilenet_v3",
    description: "Classic MMO with low-res friendly design.",
    recommended_tasks: ["skilling", "bossing", "questing", "minigames"],
    notes: "Low-res friendly. 480p is ideal for classic gameplay."
  },
  albion_online: {
    id: "albion_online",
    name: "Albion Online",
    icon: "🏰",
    color: "#4682B4",
    resolution: "480x270",
    action_space: "combat",
    architecture: "efficientnet_simple",
    description: "Sandbox MMO with isometric view.",
    recommended_tasks: ["dungeons", "gathering", "zvz", "ganking"],
    notes: "Isometric view scales well. 480p recommended."
  },
  custom: {
    id: "custom",
    name: "Custom Game",
    icon: "🎮",
    color: "#9932CC",
    resolution: "480x270",
    action_space: "standard",
    architecture: "efficientnet_lstm",
    description: "Configure your own game settings.",
    recommended_tasks: ["custom"],
    notes: "Default configuration. Adjust settings as needed."
  }
};

// Default data when sidecar is not available
const DEFAULT_GAMES = Object.values(GAME_PRESETS).map(g => ({
  id: g.id,
  name: g.name,
  icon: g.icon
}));

const DEFAULT_ARCHITECTURES = [
  { id: "efficientnet_lstm", name: "EfficientNet-LSTM (Recommended)", recommended: true, tier: "modern" },
  { id: "efficientnet_simple", name: "EfficientNet (Balanced)", tier: "modern" },
  // Registry key is `mobilenet_v3` (MODEL_REGISTRY in
  // src/bot_mmorpg/scripts/models_pytorch.py). This list used to say
  // `mobilenetv3`, which the train preflight rejected as "Unknown
  // architecture" and which get_model() would have raised on anyway.
  { id: "mobilenet_v3", name: "MobileNetV3 (Fast)", tier: "modern" },
  { id: "resnet18_lstm", name: "ResNet18-LSTM", tier: "modern" },
  { id: "efficientnet_transformer", name: "EfficientNet-Transformer (Advanced)", tier: "advanced" },
  { id: "multihead_action", name: "Multi-Head Action (Simultaneous)", tier: "advanced" },
  { id: "game_attention", name: "Game Attention Network (UI Focus)", tier: "advanced" },
  { id: "inception_v3", name: "Inception V3 (Legacy)", tier: "legacy" },
  { id: "alexnet", name: "AlexNet (Legacy)", tier: "legacy" },
];

const DEFAULT_TASKS = [
  { id: "combat", name: "Combat / Dungeons" },
  { id: "farming", name: "Farming / Gathering" },
  { id: "exploration", name: "Exploration / Questing" },
  { id: "pvp", name: "PvP / Competitive" },
  { id: "crafting", name: "Crafting / Lifeskills" },
  { id: "custom", name: "Custom Task" },
];

// Action space configurations
const ACTION_SPACES = {
  basic: { id: "basic", name: "Basic (9 actions)", actions: 9, description: "WASD movement only" },
  standard: { id: "standard", name: "Standard (29 actions)", actions: 29, description: "Keyboard + full gamepad" },
  combat: { id: "combat", name: "Combat (48 actions)", actions: 48, description: "Movement + skills + combat" },
  extended: { id: "extended", name: "Extended (73 actions)", actions: 73, description: "Full MMORPG action space" }
};

// =============================================================================
// GAME PRESET AUTO-CONFIGURATION
// =============================================================================

// Turn any free-text game name into a filesystem-safe id that matches
// the folder the backend creates under datasets/<id>/. The backend only
// .strip()s the value (see modelhub/tauri.py:_normalize_game_id and
// src-tauri/src/main.rs:normalize_game_id), so the UI is responsible for
// making the id consistent. Applying the SAME normalization on the record
// (write) path and every refresh (read) path is what guarantees a custom
// game's dataset is found again after recording. Idempotent for built-in
// ids like "genshin_impact" / "world_of_warcraft".
function normalizeCustomGameId(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    || DEFAULT_GAME_ID;
}

// The currently active game id, taken from the visible inputs and
// normalized. Used by stop/refresh flows so they never fall back to a
// stale selectedGameId (the root cause of the custom-game bug).
function getActiveGameIdFromInputs() {
  return normalizeCustomGameId(
    getEl("teach-game-id")?.value
    || getEl("train-game-id")?.value
    || selectedGameId
    || DEFAULT_GAME_ID
  );
}

function applyGamePreset(gameId) {
  gameId = normalizeCustomGameId(gameId);
  const isKnownPreset = Boolean(GAME_PRESETS[gameId]);
  // Unknown (custom) games borrow the "custom" preset's safe capture/
  // model defaults but keep their real id + a readable display name.
  const preset = GAME_PRESETS[gameId] || GAME_PRESETS.custom;
  const displayName = isKnownPreset ? preset.name : gameId.replace(/_/g, " ");

  // Update resolution selects
  const teachRes = getEl("teach-capture-resolution");
  const runRes = getEl("run-capture-resolution");
  if (teachRes) teachRes.value = preset.resolution;
  if (runRes) runRes.value = preset.resolution;

  // Update resolution hints
  const teachHint = getEl("teach-resolution-hint");
  const runHint = getEl("run-resolution-hint");
  const hintText = isKnownPreset
    ? `Optimized for ${preset.name}`
    : `Using custom game profile: ${displayName}`;
  if (teachHint) teachHint.textContent = hintText;
  if (runHint) runHint.textContent = hintText;

  // Update architecture select
  const archSelect = getEl("train-arch");
  if (archSelect) archSelect.value = preset.architecture;

  // Update action space select if exists
  const actionSelect = getEl("train-action-space");
  if (actionSelect) actionSelect.value = preset.action_space;

  // Update game ID inputs
  const teachGameId = getEl("teach-game-id");
  const trainGameId = getEl("train-game-id");
  if (teachGameId) teachGameId.value = gameId;
  if (trainGameId) trainGameId.value = gameId;

  // Update active game pill
  const activeGamePill = getEl("active-game-pill");
  if (activeGamePill) {
    activeGamePill.innerHTML = `${preset.icon} ${displayName}`;
    activeGamePill.style.color = preset.color;
  }

  // Update game info display if exists
  const gameInfo = getEl("game-preset-info");
  if (gameInfo) {
    gameInfo.innerHTML = `
      <div style="display:flex; gap:12px; align-items:flex-start;">
        <span style="font-size:32px;">${preset.icon}</span>
        <div>
          <strong style="color:${preset.color};">${displayName}</strong>
          <p style="font-size:12px; color:var(--text-dim); margin:4px 0 0;">${preset.description}</p>
          <p style="font-size:11px; color:var(--text-dim); margin-top:4px;">
            <strong>Resolution:</strong> ${preset.resolution} |
            <strong>Actions:</strong> ${ACTION_SPACES[preset.action_space]?.actions || 29} |
            <strong>Model:</strong> ${preset.architecture}
          </p>
        </div>
      </div>
    `;
  }

  // Store selected game
  selectedGameId = gameId;
  localStorage.setItem('selected_game_preset', gameId);

  logToTerminal(`${isKnownPreset ? "Applied preset" : "Using custom game"} for ${displayName}: ${preset.resolution}, ${preset.action_space}, ${preset.architecture}`, "success");

  return preset;
}

function getGamePreset(gameId) {
  return GAME_PRESETS[gameId] || GAME_PRESETS.custom;
}

function labelForGame(g) {
  if (typeof g === "string") return g;
  return g.name || g.title || g.id || JSON.stringify(g);
}
function valueForGame(g) {
  if (typeof g === "string") return g;
  return g.id || g.game_id || g.slug || g.name || "";
}

function labelForDataset(d) {
  return d.name || d.title || d.id || d.dataset_id || d.path || "dataset";
}
function valueForDataset(d) {
  return d.id || d.dataset_id || d.path || "";
}

function labelForModel(m) {
  return m.name || m.title || m.id || m.model_id || m.path || "model";
}
function valueForModel(m) {
  return m.id || m.model_id || m.path || "";
}

function labelForBuiltin(b) {
  return b.name || b.id || b.path || "builtin";
}
function valueForBuiltin(b) {
  return b.path || b.id || "";
}

// Issue #76: when the sidecar reports no bundled builtin models (the
// normal case for a Custom Game), loadCatalog falls back to
// DEFAULT_ARCHITECTURES and synthesises entries whose `path` is just
// the architecture id ("efficientnet_lstm"). Those are training
// TEMPLATES, not model folders -- activating one stored
// model_dir="efficientnet_lstm" and the bot preflight then rejected the
// run with "Active model directory missing on disk: efficientnet_lstm",
// which reads like the user deleted something they never had.
//
// A real builtin always carries a filesystem path. So: no separator +
// a known architecture id == a template, never a deployable model.
function isArchitectureTemplatePath(p) {
  const s = String(p || "").trim();
  if (!s || s.includes("/") || s.includes("\\")) return false;
  return DEFAULT_ARCHITECTURES.some((a) => a.id === s);
}

function labelForLocalModel(m) {
  return m.name || m.id || m.path || "local";
}
function valueForLocalModel(m) {
  return m.path || m.id || "";
}

async function refreshModelhubAvailability() {
  if (!invoke) return;

  try {
    const res = await invoke("modelhub_is_available");
    modelhubAvailable = !!(res && (res.available === true || res.available === "true" || res.ok === true && res.available));
    logToTerminal(`ModelHub: ${modelhubAvailable ? "Available" : "Unavailable"}`, modelhubAvailable ? "success" : "warning");
    const badge = getEl("modelhub-status");
    if (badge) badge.textContent = modelhubAvailable ? "Available" : "Unavailable";
  } catch (e) {
    modelhubAvailable = false;
    logToTerminal(`ModelHub availability check failed: ${e}`, "warning");
  }
}

async function loadGamesIntoUI() {
  const sel = getEl("game-select");
  let games = DEFAULT_GAMES;

  if (invoke && modelhubAvailable) {
    try {
      const res = await invoke("modelhub_list_games");
      const fetchedGames = (res && res.games) ? res.games : (Array.isArray(res) ? res : []);
      if (fetchedGames.length > 0) {
        games = fetchedGames;
      }
    } catch (e) {
      logToTerminal(`Using default games list`, "info");
    }
  }

  setSelectOptions(sel, games, labelForGame, valueForGame, "Choose game...", selectedGameId);

  // Update dashboard stats
  updateDashboardStats();
}

// Update dashboard statistics
function updateDashboardStats() {
  const statDatasets = getEl("stat-datasets");
  const statModels = getEl("stat-models");
  const statActive = getEl("stat-active");

  if (statDatasets) {
    statDatasets.textContent = currentCatalog.datasets.length || "0";
  }
  if (statModels) {
    // Phase 31: count only trained-on-disk artifacts. Built-in
    // architectures are training templates, not deployable models, so
    // including them in the dashboard count was a category error.
    statModels.textContent = String(currentCatalog.local_models?.length || 0);
  }
  if (statActive) {
    if (currentCatalog.active) {
      statActive.textContent = currentCatalog.active.name || currentCatalog.active.path || "Set";
    } else {
      statActive.textContent = "Not Set";
    }
  }

  // Update run tab active model display
  const runActiveModel = getEl("run-active-model");
  if (runActiveModel) {
    runActiveModel.textContent = currentCatalog.active ?
      (currentCatalog.active.name || currentCatalog.active.path || "Active") : "None selected";
  }
}

async function loadCatalog(gameId) {
  const gid = (gameId || "").trim() || DEFAULT_GAME_ID;
  selectedGameId = gid;

  // Default catalog with built-in architectures
  currentCatalog = {
    builtin_models: DEFAULT_ARCHITECTURES.map(a => ({ id: a.id, name: a.name, path: a.id })),
    datasets: [],
    models: [],
    local_models: [],
    active: null,
  };

  if (invoke && modelhubAvailable) {
    try {
      const res = await invoke("mh_get_catalog_data", { game_id: gid });
      const payload = res && res.ok === true ? res : res;
      currentCatalog = {
        builtin_models: payload.builtin_models?.length > 0 ? payload.builtin_models : currentCatalog.builtin_models,
        datasets: payload.datasets || [],
        models: payload.models || [],
        local_models: payload.local_models || [],
        active: payload.active || null,
      };
      logToTerminal(`Catalog loaded for game: ${gid}`, "success");
    } catch (e) {
      logToTerminal(`Using default catalog for: ${gid}`, "info");
    }
  } else {
    logToTerminal(`ModelHub offline - using default architectures`, "info");
  }

  // Populate UI dropdowns
  const dsSel = getEl("dataset-select");
  if (currentCatalog.datasets.length > 0) {
    setSelectOptions(dsSel, currentCatalog.datasets, labelForDataset, valueForDataset, "Choose dataset...");
  } else {
    setSelectOptions(dsSel, [{ id: "no_datasets", name: "No datasets found - record some data first" }],
      d => d.name, d => d.id, "Choose dataset...");
  }

  // Hidden state-shim selects (see index.html ModelHub section). The new
  // card UI is the source of truth, but main.js still reads
  // selectedLocalModelPath / selectedBuiltinModelPath off these handlers,
  // so we keep them populated.
  const builtinSel = getEl("builtin-model-select");
  setSelectOptions(builtinSel, currentCatalog.builtin_models, labelForBuiltin, valueForBuiltin, "Choose architecture...");

  const regSel = getEl("registry-model-select");
  if (currentCatalog.models.length > 0) {
    setSelectOptions(regSel, currentCatalog.models, labelForModel, valueForModel, "Choose registry model...");
  } else {
    setSelectOptions(regSel, [], labelForModel, valueForModel, "No registry models");
  }

  const localSel = getEl("local-model-select");
  if (currentCatalog.local_models.length > 0) {
    setSelectOptions(localSel, currentCatalog.local_models, labelForLocalModel, valueForLocalModel, "Choose local model...");
  } else {
    setSelectOptions(localSel, [], labelForLocalModel, valueForLocalModel, "No trained models yet");
  }

  const activeBox = getEl("active-model");
  if (activeBox) {
    activeBox.textContent = currentCatalog.active ?
      (currentCatalog.active.name || JSON.stringify(currentCatalog.active)) : "None";
  }

  // Render the new card-based ModelHub gallery + active-model section.
  renderModelHubCards();

  updateDashboardStats();
  refreshRunBotGate();
}

// ----------------------------------------------------------------
// ModelHub card UI (Phase 30)
// ----------------------------------------------------------------
// Replaces the legacy three-dropdown picker with a unified library:
//   - Active model section at the top (the answer to "what runs?")
//   - One card per model (built-in + local trained), sorted newest first
//   - Badges: ACTIVE / LATEST / BUILT-IN
//   - Per-card actions: Set Active / Validate / Delete (local only)
// `_lastTrainedPath` is set by the training_finalized listener so the
// just-finished model gets the "LATEST" badge + glow even before its
// folder mtime overtakes older ones (e.g. when retraining on top).
let _lastTrainedPath = "";

function _activePathFromCatalog(active) {
  if (!active) return "";
  return String(active.model_dir || active.path || "").trim();
}

function _normPath(p) {
  // OS-agnostic compare: lower-case + collapse separators.
  return String(p || "").replace(/\\/g, "/").replace(/\/+$/, "").toLowerCase();
}

function _buildUnifiedModelList() {
  // Phase 31: ModelHub now lists trained artifacts only. Built-in
  // architectures (EfficientNet, ResNet, MobileNet, ...) are not
  // deployable models — they're training templates and live in
  // Train Brain. Showing them here was a category error: a card
  // labelled "EfficientNet" looks like a runnable model but has no
  // weights, no dataset, and no `.pth`. Rule: Architecture ≠ Trained
  // Model. So this list is local-trained-only, sorted newest first.
  const local = (currentCatalog.local_models || []).map(m => ({
    kind: "local",
    id: m.id || m.path || m.name || "",
    name: m.name || m.id || "Trained Model",
    path: m.path || m.model_dir || "",
    arch: m.arch || m.architecture || "",
    accuracy: m.accuracy != null ? m.accuracy : (m.metrics?.accuracy ?? null),
    resolution: m.resolution || m.input_resolution || "",
    frames: m.frames || m.num_frames || m.dataset_size || null,
    dataset: m.dataset || m.dataset_id || "",
    mtime_ms: m.mtime_ms || 0,
    created_at: m.created_at || "",
    has_artifacts: m.has_artifacts !== false,
  }));
  local.sort((a, b) => (b.mtime_ms || 0) - (a.mtime_ms || 0));
  return local;
}

function _formatRelTime(ms) {
  if (!ms) return "";
  const diff = (Date.now() - ms) / 1000;
  if (diff < 60) return "Just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 86400 * 7) return `${Math.floor(diff / 86400)}d ago`;
  try { return new Date(ms).toLocaleDateString(); } catch (_) { return ""; }
}

function _escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
}

function renderModelHubCards() {
  const grid = document.getElementById("mh-models-grid");
  const empty = document.getElementById("mh-empty-state");
  const countEl = document.getElementById("mh-models-count");
  if (!grid) return;

  const items = _buildUnifiedModelList();
  const activePath = _normPath(_activePathFromCatalog(currentCatalog.active));
  const lastTrained = _normPath(_lastTrainedPath);

  // Pick LATEST: explicit lastTrained wins; otherwise newest model
  // with a real artifact on disk.
  let latestPath = "";
  if (lastTrained) {
    latestPath = lastTrained;
  } else {
    const firstWithArtifacts = items.find(it => it.has_artifacts);
    if (firstWithArtifacts) latestPath = _normPath(firstWithArtifacts.path);
  }

  if (countEl) {
    countEl.textContent = `${items.length} model${items.length === 1 ? "" : "s"}`;
  }

  // Clear (but keep the empty-state node in case we need to put it back)
  grid.innerHTML = "";
  if (items.length === 0) {
    if (empty) { grid.appendChild(empty); empty.hidden = false; }
    _renderActiveModelSection(null, items);
    return;
  }
  if (empty) empty.hidden = true;

  for (const it of items) {
    const itPath = _normPath(it.path);
    const isActive = itPath && itPath === activePath;
    const isLatest = itPath && itPath === latestPath;

    const card = document.createElement("div");
    card.className = "mh-model";
    if (isActive) card.classList.add("is-active");
    if (isLatest) card.classList.add("is-latest");
    card.dataset.path = it.path;
    card.dataset.kind = it.kind;

    const badges = [];
    if (isActive) badges.push(`<span class="mh-badge badge-active">Active</span>`);
    if (isLatest) badges.push(`<span class="mh-badge badge-latest">Latest</span>`);

    // Phase 31: trained-model card. Each line is one fact about the
    // artifact on disk (architecture used to train, dataset, accuracy,
    // when). No more "Built-in" framing — those aren't here anymore.
    const stats = [];
    if (it.arch) stats.push(`<span class="mh-model-stat">Arch: <strong>${_escapeHtml(it.arch)}</strong></span>`);
    if (it.dataset) stats.push(`<span class="mh-model-stat">Dataset: <strong>${_escapeHtml(it.dataset)}</strong></span>`);
    if (it.resolution) stats.push(`<span class="mh-model-stat">${_escapeHtml(it.resolution)}</span>`);
    if (it.frames) stats.push(`<span class="mh-model-stat"><strong>${_escapeHtml(it.frames)}</strong> frames</span>`);
    if (it.accuracy != null) {
      const acc = (typeof it.accuracy === "number") ? `${(it.accuracy * 100).toFixed(1)}%` : String(it.accuracy);
      stats.push(`<span class="mh-model-stat">Acc: <strong>${_escapeHtml(acc)}</strong></span>`);
    }
    const rel = _formatRelTime(it.mtime_ms);
    if (rel) stats.push(`<span class="mh-model-stat">${_escapeHtml(rel)}</span>`);

    const setActiveLabel = isActive ? "✓ Active" : "Set Active";
    const setActiveClass = isActive ? "btn btn-secondary" : "btn";

    card.innerHTML = `
      <div class="mh-badges">${badges.join("")}</div>
      <div class="mh-model-name">${_escapeHtml(it.name)}</div>
      <div class="mh-model-arch">Trained model${it.path ? " · " + _escapeHtml(it.path) : ""}</div>
      <div class="mh-model-stats">${stats.join("")}</div>
      <div class="mh-model-actions">
        <button class="${setActiveClass}" data-mh-action="set-active" type="button" ${isActive ? "disabled" : ""}>${setActiveLabel}</button>
        <button class="btn btn-secondary" data-mh-action="validate" type="button">Validate</button>
        <button class="btn btn-danger" data-mh-action="delete" type="button">Delete</button>
      </div>
    `;

    card.addEventListener("click", (ev) => {
      const actionBtn = ev.target.closest("[data-mh-action]");
      const action = actionBtn?.dataset.mhAction;
      _selectModelCard(it);
      if (!action) return;
      ev.stopPropagation();
      if (action === "set-active") _mhSetActiveFor(it);
      else if (action === "validate") _mhValidateFor(it);
      else if (action === "delete") _mhDeleteFor(it);
    });

    grid.appendChild(card);
  }

  // Pre-select the LATEST candidate visually so the user sees the
  // "fresh from the oven" model first. Active is highlighted separately
  // by its green border; we only auto-select the LATEST when no card
  // is already selected.
  if (latestPath) {
    const candidate = items.find(it => _normPath(it.path) === latestPath);
    if (candidate) _selectModelCard(candidate, /*silent*/ true);
  }

  _renderActiveModelSection(currentCatalog.active, items);
}

function _selectModelCard(it, silent) {
  // Mirror the click into the hidden state-shim selects so existing
  // setActiveModelFromUI / deleteSelectedModel / validateSelectedModel
  // pick up the same target without a refactor. Phase 31: only local
  // trained models live in the gallery now (architectures belong in
  // Train Brain), so the dispatch is single-branch.
  selectedLocalModelPath = it.path;
  selectedBuiltinModelPath = "";
  selectedModelRegistryId = "";
  const localSel = getEl("local-model-select");
  if (localSel && Array.from(localSel.options).some(o => o.value === it.path)) {
    localSel.value = it.path;
  }
  // Visually mark the selected card.
  document.querySelectorAll(".mh-model.is-selected").forEach(n => n.classList.remove("is-selected"));
  const target = document.querySelector(`.mh-model[data-path="${(it.path || "").replace(/"/g, '\\"')}"]`);
  if (target) target.classList.add("is-selected");
  if (!silent) {
    logToTerminal(`Selected model: ${it.name}`, "info");
  }
}

async function _mhSetActiveFor(it) {
  _selectModelCard(it, /*silent*/ true);
  await setActiveModelFromUI();
}
async function _mhValidateFor(it) {
  _selectModelCard(it, /*silent*/ true);
  await validateSelectedModel();
}
async function _mhDeleteFor(it) {
  _selectModelCard(it, /*silent*/ true);
  await deleteSelectedModel();
}

function _renderActiveModelSection(active, items) {
  const card = document.getElementById("mh-active-card");
  const status = document.getElementById("mh-active-status");
  const empty = document.getElementById("mh-active-empty");
  const detail = document.getElementById("mh-active-detail");
  const nameEl = document.getElementById("mh-active-name");
  const metaEl = document.getElementById("mh-active-meta");
  const goRun = document.getElementById("mh-go-run");
  if (!card) return;

  const path = _activePathFromCatalog(active);
  if (!active || !path) {
    card.dataset.state = "empty";
    if (status) status.textContent = "No active model selected";
    if (empty) empty.hidden = false;
    if (detail) detail.hidden = true;
    if (goRun) goRun.disabled = true;
    return;
  }
  card.dataset.state = "set";
  if (status) status.textContent = "● Active";
  if (empty) empty.hidden = true;
  if (detail) detail.hidden = false;

  // Try to enrich the active card with the matching catalog item's metadata.
  const match = (items || []).find(x => _normPath(x.path) === _normPath(path));
  const displayName = match?.name || active.name || active.model_id || path.split(/[\\/]/).pop() || "Active model";
  const metaParts = [];
  if (match?.arch || active.arch) metaParts.push(_escapeHtml(match?.arch || active.arch));
  if (match?.resolution) metaParts.push(_escapeHtml(match.resolution));
  if (match?.accuracy != null) {
    const acc = typeof match.accuracy === "number" ? `${(match.accuracy * 100).toFixed(1)}%` : String(match.accuracy);
    metaParts.push(`Acc: <strong>${_escapeHtml(acc)}</strong>`);
  }
  metaParts.push(_escapeHtml(path));

  if (nameEl) nameEl.textContent = displayName;
  if (metaEl) metaEl.innerHTML = metaParts.join(" · ");
  if (goRun) {
    goRun.disabled = false;
    goRun.onclick = () => {
      if (typeof window.showTab === "function") window.showTab("run");
      else document.getElementById("btn-run")?.click();
    };
  }
}

// Mirror the Rust-side gate for start_bot. 3-test_model.py declares
// --model as required; start_bot in main.rs refuses to spawn without
// an active model. Reflect that prerequisite in the UI so the user
// sees the block before the click rather than as a runtime error.
// Phase 30: Run Bot HUD state machine.
// The Run Bot screen behaves like a game-launcher control HUD with
// three discrete states: no-model | ready | running. The CTA label,
// glow, and secondary CTA all switch off `card.dataset.state`. The
// "running" state is set/cleared by toggleBot below; this gate
// decides only between no-model and ready.
function refreshRunBotGate() {
  const card        = document.getElementById('run-bot-card');
  const badge       = document.getElementById('run-bot-state-badge');
  const btn         = document.getElementById('btnStartBot');
  const ctaIcon     = document.getElementById('runbot-cta-icon');
  const ctaLabel    = document.getElementById('runbot-cta-label');
  const chooseBtn   = document.getElementById('btnRunChooseModel');
  const activeIcon  = document.getElementById('runbot-active-icon');
  const activeLabel = document.getElementById('runbot-active-label');
  const activeSub   = document.getElementById('runbot-active-sub');
  const statePill   = document.getElementById('bot-state');
  const stateMeta   = document.getElementById('run-active-model');
  if (!card || !btn) return;

  // While the bot is actually running, leave that state alone — only
  // toggleBot transitions in and out of "running".
  if (card.dataset.state === 'running') return;

  const active = currentCatalog?.active;
  const hasActive = !!(active && (active.model_dir || active.path));

  if (hasActive) {
    const name = active.name || active.model_id || active.model_dir || '(unnamed)';
    const safeName = String(name).replace(/[<>&]/g, '');
    card.dataset.state = 'ready';
    if (badge) {
      badge.className = 'runbot-hud-badge diag-verdict ready';
      badge.textContent = '● READY';
    }
    btn.disabled = false;
    btn.removeAttribute('aria-disabled');
    btn.style.opacity = '';
    btn.style.cursor = '';
    if (ctaIcon) ctaIcon.textContent = '▶';
    if (ctaLabel) ctaLabel.textContent = 'START BOT';
    if (activeIcon) activeIcon.textContent = '🎮';
    if (activeLabel) activeLabel.textContent = safeName;
    if (activeSub) activeSub.textContent = '✔ Ready to play';
    if (statePill) statePill.textContent = 'READY';
    if (stateMeta) stateMeta.textContent = safeName;
    if (chooseBtn) chooseBtn.hidden = true;
  } else {
    card.dataset.state = 'no-model';
    if (badge) {
      badge.className = 'runbot-hud-badge diag-verdict warning';
      badge.textContent = '● IDLE';
    }
    btn.disabled = true;
    btn.setAttribute('aria-disabled', 'true');
    btn.title = 'Select a model first';
    if (ctaIcon) ctaIcon.textContent = '🎯';
    if (ctaLabel) ctaLabel.textContent = 'Choose Model First';
    if (activeIcon) activeIcon.textContent = '🎮';
    if (activeLabel) activeLabel.textContent = 'No active model';
    if (activeSub) activeSub.textContent = 'Select a trained model to start playing';
    if (statePill) statePill.textContent = 'IDLE';
    if (stateMeta) stateMeta.textContent = '—';
    if (chooseBtn) {
      chooseBtn.hidden = false;
      chooseBtn.onclick = () => {
        if (typeof window.showTab === "function") window.showTab("models");
        else document.getElementById("btn-models")?.click();
      };
    }
  }
}

// Set / clear the visual "running" state on the Run Bot HUD. Called
// from toggleBot so the start/stop CTA, badge, and pill stay in sync
// with the actual bot lifecycle even when the catalog hasn't reloaded.
function _setRunBotRunning(isRunning) {
  const card     = document.getElementById('run-bot-card');
  const badge    = document.getElementById('run-bot-state-badge');
  const ctaIcon  = document.getElementById('runbot-cta-icon');
  const ctaLabel = document.getElementById('runbot-cta-label');
  const activeSub = document.getElementById('runbot-active-sub');
  const statePill = document.getElementById('bot-state');
  const visionLive = document.getElementById('runbot-vision-live');
  if (!card) return;

  if (isRunning) {
    card.dataset.state = 'running';
    if (badge) {
      badge.className = 'runbot-hud-badge diag-verdict warning';
      badge.textContent = '● RUNNING';
    }
    if (ctaIcon) ctaIcon.textContent = '■';
    if (ctaLabel) ctaLabel.textContent = 'STOP BOT';
    if (activeSub) activeSub.textContent = 'Bot active in game — press STOP to regain control';
    if (statePill) statePill.textContent = 'RUNNING';
    if (visionLive) visionLive.hidden = false;
  } else {
    if (visionLive) visionLive.hidden = true;
    // Hand control back to the gate, which will set ready/no-model.
    card.dataset.state = 'checking';
    refreshRunBotGate();
  }
}

async function setActiveModelFromUI() {
  if (!invoke) return;
  const gid = selectedGameId || DEFAULT_GAME_ID;
  let model_id = "";
  let path = "";
  // Phase 31: forward the resolved checkpoint file alongside the
  // directory. The Python endpoint persists it as `model_file` and
  // the Rust inference launcher prefers it over walking the dir,
  // which is what fixes the "Permission denied: '...New Model'"
  // error when the user activates a trained model whose folder
  // contains spaces or where the resolution would otherwise depend on
  // mtime ordering.
  let model_file = "";

  if (selectedLocalModelPath) {
    model_id = "local";
    path = selectedLocalModelPath;
    const found = (currentCatalog.local_models || []).find(
      (m) => (m.path || m.model_dir) === selectedLocalModelPath
    );
    if (found && found.checkpoint) model_file = found.checkpoint;
  } else if (selectedBuiltinModelPath) {
    model_id = "builtin";
    path = selectedBuiltinModelPath;
  } else if (selectedModelRegistryId) {
    model_id = selectedModelRegistryId;
    const found = (currentCatalog.models || []).find((m) => valueForModel(m) === selectedModelRegistryId);
    path = found ? (found.path || "") : "";
    if (!path) path = selectedModelRegistryId;
    if (found && found.checkpoint) model_file = found.checkpoint;
  }

  if (!path) {
    alert("Select a model (local/builtin/registry) first.");
    return;
  }

  // Issue #76: block the "activated an architecture template" trap at
  // the source instead of letting it fail later inside the bot
  // preflight with a misleading "model directory missing on disk".
  if (isArchitectureTemplatePath(path)) {
    const msg =
      `"${path}" is a training architecture, not a trained model.\n\n` +
      "Architectures are templates you pick in the Train tab. Record a " +
      "dataset, train it with this architecture, then activate the " +
      "resulting model from the Trained Models section.";
    logToTerminal(`Set Active rejected: ${path} is an architecture template, not a trained model.`, "warning");
    if (window.notifyError) {
      window.notifyError("Not a trained model", msg);
    } else {
      alert(msg);
    }
    return;
  }

  try {
    const res = await invoke("mh_set_active", {
      game_id: gid,
      gameId: gid,
      model_id,
      modelId: model_id,
      path,
      model_file,
      modelFile: model_file,
    });
    const resolved = (res && res.model_file) || model_file;
    logToTerminal(
      resolved
        ? `Active model set: ${path}\n  ↳ checkpoint: ${resolved}`
        : `Active model set: ${path}`,
      "success"
    );
    await loadCatalog(gid);
    return res;
  } catch (e) {
    logToTerminal(`Failed to set active model: ${e}`, "error");
  }
}

async function deleteSelectedModel() {
  if (!invoke) return;
  const gid = selectedGameId || DEFAULT_GAME_ID;

  if (!selectedLocalModelPath) {
    alert("Deletion is only allowed for local trained models. Select a local model first.");
    return;
  }

  const ok = confirm(`Delete model folder?\n\n${selectedLocalModelPath}\n\nThis cannot be undone.`);
  if (!ok) return;

  try {
    const res = await invoke("mh_delete_model", {
      game_id: gid,
      model_id: "local",
      path: selectedLocalModelPath,
    });
    logToTerminal(`Deleted model: ${selectedLocalModelPath}`, "success");
    selectedLocalModelPath = "";
    await loadCatalog(gid);
    return res;
  } catch (e) {
    logToTerminal(`Delete failed: ${e}`, "error");
  }
}

async function validateSelectedModel() {
  if (!invoke) return;
  const gid = selectedGameId || DEFAULT_GAME_ID;
  const modelDir = selectedLocalModelPath || selectedBuiltinModelPath || "";

  if (!modelDir) {
    alert("Select a model folder (local/builtin) to validate.");
    return;
  }

  try {
    const res = await invoke("modelhub_validate_model", { game_id: gid, model_dir: modelDir });
    const result = res && res.result ? res.result : res;
    const msg = result && result.message ? result.message : JSON.stringify(result);
    logToTerminal(`Validate: ${msg}`, (result && result.ok) ? "success" : "warning");
    const box = getEl("model-validate-result");
    if (box) box.textContent = msg;
    return res;
  } catch (e) {
    logToTerminal(`Validation failed: ${e}`, "error");
  }
}

async function runOfflineEvaluation() {
  if (!invoke) return;
  const modelDir = selectedLocalModelPath || selectedBuiltinModelPath || "";
  const datasetDir = getEl("offline-dataset-dir")?.value?.trim() || "";

  if (!modelDir || !datasetDir) {
    alert("Provide model_dir and dataset_dir for offline evaluation.");
    return;
  }

  try {
    const res = await invoke("modelhub_run_offline_evaluation", { model_dir: modelDir, dataset_dir: datasetDir });
    logToTerminal("Offline evaluation started.", "success");
    return res;
  } catch (e) {
    logToTerminal(`Offline eval failed: ${e}`, "error");
  }
}

// ------------------------------------------------------------
// BUTTON HANDLERS (Rust Commands)
// ------------------------------------------------------------

// TEACH: Toggle Recording
window.toggleRecord = async function (btn) {
  if (!invoke) return alert("Tauri backend not found.");
  isRecording = !isRecording;
  const status = document.getElementById("record-status");
  const _rawTeachMon = parseInt(getEl("teach-monitor-select")?.value, 10);
  const monitorId = Number.isFinite(_rawTeachMon) ? _rawTeachMon : 0;
  const resolution = getEl("teach-capture-resolution")?.value || "480x270";

  if (isRecording) {
    try {
      logToTerminal("Requesting recording start...", "info");
      btn.disabled = true;
      // Normalize the typed game id to the SAME safe form used by every
      // refresh path, then put ALL game-id state in lockstep before we
      // record. This guarantees the folder we record into
      // (datasets/<game_id>/) is the exact folder the Train tab later
      // scans -- the mismatch here was why custom-game recordings were
      // invisible (they landed under a custom id while the Train tab
      // still looked under a stale built-in like genshin_impact). We sync
      // the identity fields directly rather than calling applyGamePreset()
      // so a user's hand-picked capture resolution isn't reset on record.
      const game_id = getActiveGameIdFromInputs();
      selectedGameId = game_id;
      const _teachGameEl = getEl("teach-game-id");
      const _trainGameEl = getEl("train-game-id");
      if (_teachGameEl) _teachGameEl.value = game_id;
      if (_trainGameEl) _trainGameEl.value = game_id;

      // Phase 21+23-A: client-side auto-generate is the FIRST line of
      // defense. The server-side preflight (Rust) is the AUTHORITY:
      // even if this JS is stale (WebView2 cached an older bundle),
      // Rust will synthesize a valid name when sent an empty string
      // and return it as `resolved_dataset_name`. We use that
      // resolved name for the actual start_recording call so the
      // recording lands in the directory the preflight validated.
      const datasetInputEl = getEl("teach-dataset-name");
      let dataset_name = (datasetInputEl?.value || "").trim();
      if (!dataset_name) {
        dataset_name = generateDatasetName(game_id);
        if (datasetInputEl) datasetInputEl.value = dataset_name;
        logToTerminal(`Auto-generated dataset name: ${dataset_name}`, "info");
      }

      // Phase 4: preflight gate. Phase 23-A: returns the full
      // response object so we can read resolved_dataset_name.
      const preflight = await preflightOrAlert("record", { game_id, dataset_name, monitor_id: monitorId });
      if (!preflight) {
        isRecording = false;
        btn.disabled = false;
        return;
      }
      // Phase 23-A: trust the server's resolved name. If JS sent an
      // empty value (stale bundle), Rust generated one; reflect it
      // in the input field for visual feedback AND use it for the
      // spawn so the recording matches the preflight-validated path.
      if (preflight.resolved_dataset_name && preflight.resolved_dataset_name !== dataset_name) {
        if (datasetInputEl) datasetInputEl.value = preflight.resolved_dataset_name;
        logToTerminal(
          `Server-resolved dataset name: ${preflight.resolved_dataset_name}`,
          "info"
        );
        dataset_name = preflight.resolved_dataset_name;
      }

      const captureMouse = getEl("teach-capture-mouse")?.checked ?? false;
      const res = await invoke("start_recording", {
        game_id,
        gameId: game_id,
        dataset_name,
        datasetName: dataset_name,
        monitor_id: monitorId,
        monitorId,
        resolution,
        capture_mouse: captureMouse,
        captureMouse,
      });
      logToTerminal(res, "success");
      // Phase 21: explicit stop state. Red border + dark fill so the
      // user immediately recognizes "click here to stop", not "click
      // to start" -- the previous always-pink button confused both.
      btn.innerHTML = "<span>■</span> Stop recording";
      btn.style.background = "#7a1f1f";
      btn.style.borderColor = "#FF5252";
      if (status) {
        status.innerText = "🔴 Recording — switch to the game window.";
        status.style.color = "#FF5252";
      }
      window.notifyInfo?.("Recording started", `Capturing dataset "${dataset_name}" for ${game_id}.`);
      // Only start live preview if user has it enabled (default: disabled)
      maybeStartLivePreviewTauri("teach");
    } catch (err) {
      logToTerminal(`Error starting recording: ${err}`, "error");
      window.notifyError?.("Recording failed to start", String(err), [
        { label: "Run Diagnosis", onClick: () => {
          window.openSettings?.(); window.switchSettingsTab?.('system-tools');
          document.getElementById('btn-run-diagnosis')?.click();
        }},
      ]);
      isRecording = false;
    } finally {
      btn.disabled = false;
    }
  } else {
    try {
      stopLivePreviewTauri();
      btn.disabled = true;
      const res = await invoke("stop_process");
      logToTerminal(res, "success");
      // Phase 21: restore start state -- accent fill + sentence case.
      btn.innerHTML = "<span>▶</span> Start recording";
      btn.style.background = "var(--accent)";
      btn.style.borderColor = "var(--accent)";
      if (status) {
        status.innerText = "✓ Recording saved.";
        status.style.color = "var(--success)";
      }
      window.notifySuccess?.("Recording saved", "Dataset is ready for training.");
      // Refresh dataset list + catalog for the game we ACTUALLY recorded
      // (read from the live inputs), never a stale selectedGameId. The
      // authoritative refresh still happens in the recording_finalized
      // handler below using the backend's reported game_id; this is the
      // immediate-feedback pass for when that event is slow/absent.
      const stoppedGameId = getActiveGameIdFromInputs();
      await refreshDatasetListTauri(undefined, stoppedGameId);
      await loadCatalog(stoppedGameId);
    } catch (err) {
      logToTerminal(`Error stopping recording: ${err}`, "error");
      window.notifyError?.("Could not stop recording cleanly", String(err));
    } finally {
      btn.disabled = false;
    }
  }
};

// TRAIN: Start Training
window.startTraining = async function () {
  if (!invoke) return alert("Tauri backend not found.");
  const progressBar = document.getElementById("progress-bar");
  const pctDisplay = document.getElementById("train-pct");
  const btn = document.getElementById("btnStartTraining");

  try {
    logToTerminal("-------------------------------------------", "info");
    logToTerminal("Initializing neural network training...", "info");
    if (btn) btn.disabled = true;
    if (progressBar) progressBar.style.width = "0%";
    if (pctDisplay) pctDisplay.textContent = "0%";

    const dsSel = getEl("train-dataset-id");
    const dsValue = dsSel ? (dsSel.value || "") : "";
    // Normalize so training scans the SAME datasets/<game_id> folder the
    // recording was written into (train-game-id keeps priority here since
    // this is the Train tab). Without this, a custom game typed straight
    // into the Train field would train against datasets/<raw name>/ and
    // miss the normalized folder the recorder created.
    const game_id = normalizeCustomGameId(getEl("train-game-id")?.value || selectedGameId || DEFAULT_GAME_ID);
    const model_name = (getEl("train-model-name")?.value || "New Model").trim();
    // Phase 29: priority-ordered resolver instead of trusting one
    // state field. Walks select.value -> data-dataset-id -> label
    // prefix -> selectedDatasetId. This addresses the report where
    // the dropdown visibly shows a dataset but preflight receives
    // an empty dataset_id -- multiple browser-quirky failure modes
    // funnel into "select.value is empty" without a corresponding
    // visual change, so we pick from whichever channel still has
    // the id.
    let dataset_id = resolveSelectedTrainDatasetId();
    const arch = (getEl("train-arch")?.value || "custom").trim();

    // Phase 29: defense-in-depth. If every UI source is empty (a
    // race we can't trace, a stale bundle in WebView2's cache, or
    // a path-vs-id payload mismatch we haven't seen yet), fetch
    // fresh datasets from the backend and pick the newest. This
    // is the same auto-pick logic populate uses, just driven from
    // the click-time path so a transient UI state can never starve
    // a real-on-disk dataset of being trained on.
    if (!dataset_id) {
      try {
        const { datasets } = await fetchDatasetsForGameTauri(game_id);
        const first = (Array.isArray(datasets) && datasets.length > 0)
          ? normalizeDatasetId(datasets[0])
          : "";
        if (first) {
          dataset_id = first;
          selectedDatasetId = first;
          _lastRealTrainDatasetValue = first;
          if (dsSel && Array.from(dsSel.options).some(o => o.value === first)) {
            dsSel.value = first;
          }
          logToTerminal(`Auto-selected latest dataset for training: ${first}`, "info");
        }
      } catch (e) {
        console.warn("startTraining: fallback fetch failed", e);
      }
    }

    // Phase 29: telemetry the bug report explicitly asked for.
    // Every Start Training click now records the four candidate
    // sources + the final resolved id + the exact payload going
    // to preflight. Hand-traceable from a single bundle paste.
    const _selOpt = dsSel?.selectedOptions?.[0];
    logToTerminal(
      `[Debug] train state: selectedDatasetId='${selectedDatasetId || ""}' | sel.value='${dsValue}' | option.dataset.datasetId='${(_selOpt?.dataset?.datasetId) || ""}' | resolved='${dataset_id}'`,
      "info"
    );
    logToTerminal(
      `[Debug] train payload: ${JSON.stringify({ game_id, model_name, dataset_id, arch })}`,
      "info"
    );

    // Phase 4: preflight gate. Catches missing dataset, unknown arch,
    // and "another job already running" before the spawn fires.
    const cleared = await preflightOrAlert("train", { game_id, dataset_id, arch });
    if (!cleared) {
      // Re-enable through the gate path so we don't accidentally
      // unblock when the user is on a no-dataset state.
      _refreshTrainGate();
      return;
    }

    // Phase 28: lock the badge into "Running" and the button into
    // its training-pulse state so both surfaces tell the same story
    // for the duration of the run. process_finished restores idle.
    _setTrainBadgeRunning();

    const res = await invoke("start_training", {
      game_id,
      gameId: game_id,
      model_name,
      modelName: model_name,
      dataset_id,
      datasetId: dataset_id,
      arch,
    });
    logToTerminal(res, "success");
    window.notifyInfo?.("Training started", `${model_name} • ${arch} on dataset ${dataset_id || "(default)"}`);
  } catch (err) {
    logToTerminal(`Training failed to start: ${err}`, "error");
    window.notifyError?.("Training failed to start", String(err), [
      { label: "Run Diagnosis", onClick: () => {
        window.openSettings?.(); window.switchSettingsTab?.('system-tools');
        document.getElementById('btn-run-diagnosis')?.click();
      }},
    ]);
    _setTrainBadgeIdle();
  }
};

// TRAIN: Analyze Logs
window.analyzeLogs = async function () {
  const terminal = document.getElementById("terminal");
  const resultBox = document.getElementById("log-analysis-result");
  const resultText = document.getElementById("analysis-text");
  if (!terminal) return;
  const logs = terminal.innerText;
  if (logs.length < 50) {
    alert("Not enough logs to analyze. Please run training first.");
    return;
  }
  if (resultText) resultText.textContent = "Analyzing local logs...";
  if (resultBox) resultBox.style.display = "block";
  setTimeout(() => {
    let analysis = "Log Analysis: \n";
    const epochCount = (logs.match(/Epoch/g) || []).length;
    if (epochCount > 0) analysis += `• Found ${epochCount} training epochs.\n`;
    else analysis += "• No training epochs detected yet.\n";
    if (logs.includes("Error") || logs.includes("Exception")) analysis += "• ⚠️ Errors detected in logs.\n";
    else analysis += "• System appears stable.\n";
    if (resultText) resultText.textContent = analysis;
  }, 800);
};

// RUN: Toggle Bot
//
// Phase 30: HUD-aware. CTA visuals are controlled by the parent
// .runbot-hud[data-state] state machine, NOT by mutating the button's
// inline style/text — the new CTA has child spans (icon + label) that
// would be wiped by a naive `btn.innerText = ...`. We delegate all
// label/glow updates to _setRunBotRunning + refreshRunBotGate.
window.toggleBot = async function (btn) {
  if (!invoke) return alert("Tauri backend not found.");
  isBotRunning = !isBotRunning;
  const _rawRunMon = parseInt(getEl("run-monitor-select")?.value, 10);
  const monitorId = Number.isFinite(_rawRunMon) ? _rawRunMon : 0;
  const resolution = getEl("run-capture-resolution")?.value || "480x270";

  if (isBotRunning) {
    try {
      logToTerminal("Initializing autonomous bot...", "info");
      btn.disabled = true;
      // start_bot now requires game_id so the Rust side can resolve the
      // active model from /modelhub/catalog?game_id=... If the user
      // hasn't picked a model the Rust command returns a clear error
      // and we surface it as a toast instead of opening a doomed
      // subprocess that would die on argparse.
      const game_id = selectedGameId || DEFAULT_GAME_ID;

      // Phase 4: preflight gate. Catches missing active model and
      // model-dir-deleted-on-disk before the spawn fires.
      const cleared = await preflightOrAlert("bot", { game_id, monitor_id: monitorId });
      if (!cleared) {
        isBotRunning = false;
        btn.disabled = false;
        return;
      }

      const res = await invoke("start_bot", {
        game_id,
        gameId: game_id,
        monitor_id: monitorId,
        monitorId,
        resolution,
      });
      logToTerminal(res, "success");
      _setRunBotRunning(true);
      // Only start live preview if user has it enabled (default: disabled)
      maybeStartLivePreviewTauri("run");
    } catch (err) {
      logToTerminal(`Failed to start bot: ${err}`, "error");
      window.notifyError?.("Cannot start bot", String(err), [
        { label: "Open ModelHub", primary: true,
          onClick: () => window.showTab && window.showTab('models') },
      ]);
      isBotRunning = false;
      _setRunBotRunning(false);
    } finally {
      btn.disabled = false;
    }
  } else {
    try {
      stopLivePreviewTauri();
      btn.disabled = true;
      const res = await invoke("stop_process");
      logToTerminal(res, "success");
      _setRunBotRunning(false);
    } catch (err) {
      logToTerminal(`Failed to stop bot: ${err}`, "error");
    } finally {
      btn.disabled = false;
    }
  }
};

// RUN: Install Drivers
window.installDrivers = async function () {
  if (!invoke) return alert("Tauri backend not found.");
  logToTerminal("Installing drivers (admin)...", "info");
  window.notifyInfo?.("Driver installer launching", "Approve the UAC prompt to continue.");
  try {
    const res = await invoke("install_drivers");
    if (res && res.ok) {
      logToTerminal("Driver installer launched.", "success");
      const st = getEl("drivers-status");
      if (st) st.textContent = "Installer launched";
      window.notifySuccess?.(
        "Drivers installed",
        "Interception + vJoy installer finished. Restart the app if you didn't already."
      );
      // Re-run health so the Diagnosis panel + Drivers card pick up the new state.
      checkInstallHealth?.();
    } else {
      const reason = res?.error || JSON.stringify(res);
      logToTerminal(`Driver install failed: ${reason}`, "warning");
      window.notifyError?.(
        "Driver install failed",
        reason,
        [
          { label: "Run Diagnosis", onClick: () => {
              window.openSettings?.();
              window.switchSettingsTab?.('system-tools');
              document.getElementById('btn-run-diagnosis')?.click();
          }},
          { label: "Copy Details", onClick: async () => {
              try { await navigator.clipboard.writeText(`Driver install failed: ${reason}`); }
              catch (e) {}
          }, primary: false },
        ]
      );
    }
  } catch (e) {
    logToTerminal(`Driver install error: ${e}`, "error");
    window.notifyError?.("Driver install error", String(e));
  }
};

// AI STRATEGIST: Chat
window.sendChatMessage = async function () {
  if (!invoke) return alert("Tauri backend not found.");
  const input = document.getElementById("chat-input");
  const history = document.getElementById("chat-history");
  const spinner = document.getElementById("chat-spinner");
  const sendBtn = document.getElementById("btnSendChat");
  if (!input || !history) return;
  const msg = input.value.trim();
  if (!msg) return;

  const userBubble = document.createElement("div");
  userBubble.className = "chat-bubble bubble-user";
  userBubble.textContent = msg;
  history.appendChild(userBubble);
  input.value = "";
  history.scrollTop = history.scrollHeight;

  if (spinner) spinner.style.display = "block";
  if (sendBtn) sendBtn.disabled = true;

  try {
    const reply = await invoke("ai_chat", { message: msg });
    const aiBubble = document.createElement("div");
    aiBubble.className = "chat-bubble bubble-ai";
    aiBubble.textContent = reply;
    history.appendChild(aiBubble);
  } catch (e) {
    const aiBubble = document.createElement("div");
    aiBubble.className = "chat-bubble bubble-ai";
    aiBubble.textContent = `⚠️ AI error: ${e}`;
    history.appendChild(aiBubble);
  } finally {
    if (spinner) spinner.style.display = "none";
    if (sendBtn) sendBtn.disabled = false;
    history.scrollTop = history.scrollHeight;
  }
};

// ------------------------------------------------------------
// EVENTS FROM RUST
// ------------------------------------------------------------
async function wireBackendEvents() {
  if (!listen) return;

  await listen("terminal_update", (event) => {
    const line = typeof event.payload === "string" ? event.payload : JSON.stringify(event.payload);
    window.update_terminal(line);
  });

  // Replay any terminal_update lines that Rust emitted DURING setup()
  // before this listener existed. Tauri 1.x has no event buffering for
  // late listeners, so the most diagnostic startup lines ([Sidecar
  // stderr] tracebacks, [Sidecar] still warming up... heartbeats,
  // [Fatal]/[Hint] blocks) used to vanish without reaching the user.
  // The Rust side now retains them in a 500-line ring buffer; we
  // drain it here exactly once so the terminal panel reflects what
  // really happened during launch.
  if (invoke) {
    try {
      const replay = await invoke("drain_early_log");
      if (Array.isArray(replay) && replay.length > 0) {
        for (const line of replay) {
          window.update_terminal(line);
        }
      }
    } catch (e) {
      // Old Rust binary without the command -- harmless on first
      // upgrade. Don't spam the user; just record for support.
      console.warn("drain_early_log unavailable:", e);
    }
  }

  await listen("process_finished", (event) => {
    const msg = typeof event.payload === "string" ? event.payload : JSON.stringify(event.payload);
    logToTerminal(`[System] Process finished: ${msg}`, "info");
    isRecording = false;
    isBotRunning = false;
    // Phase 28: training-state restore. Drops the running badge and
    // re-runs the gate so the button settles to ready/blocked based
    // on whether a dataset is still selected.
    _setTrainBadgeIdle();
    // Phase 30: bot HUD restore — if the bot subprocess dies (clean
    // exit or crash) the HUD must drop out of "running" so the CTA
    // becomes a START button again instead of a stuck STOP button.
    if (typeof _setRunBotRunning === "function") _setRunBotRunning(false);
  });

  // Phase 25 + 27: Rust emits this after stop_process -> /session/finalize
  // when a recording archive has been registered. We now refetch the
  // dataset list so the Train tab dropdown reflects what actually
  // exists on disk (not just what we *think* exists), then auto-
  // select the just-archived id. Storing it directly on .value (the
  // old approach) was unreliable -- a backgrounded loadCatalog or
  // tab refresh could overwrite the input. Going through the
  // populate-and-select path makes the selection authoritative.
  await listen("recording_finalized", (event) => {
    const ds = event.payload || {};
    const did = (ds.id || "").trim();
    // The backend tells us the EXACT game folder it archived under
    // (session_manager.finalize_recording -> entry.game_id). Trust it as
    // the source of truth so we refresh the right folder even if the
    // selected game drifted while recording. Fall back to the live
    // inputs only if the payload omitted it.
    const gid = normalizeCustomGameId(ds.game_id || getActiveGameIdFromInputs());
    if (!did) return;
    selectedDatasetId = did;
    // Re-sync all game-id state to the finalized game so the Teach/Train
    // tabs and any later manual refresh point at the same folder.
    selectedGameId = gid;
    const teachGameId = getEl("teach-game-id");
    const trainGameId = getEl("train-game-id");
    if (teachGameId) teachGameId.value = gid;
    if (trainGameId) trainGameId.value = gid;
    refreshDatasetListTauri(did, gid).catch(e =>
      console.warn("recording_finalized: failed to refresh dataset list", e)
    );
    logToTerminal(`Dataset ready for training: ${did}`, "success");
    window.notifyInfo?.(
      "Dataset archived",
      `${ds.file_count || "?"} file(s) • selected for training as "${did}".`
    );
  });

  // Phase 30: training_finalized — Rust emits this from the log-bridge
  // worker when a `train` job reaches status=completed (see
  // src-tauri/src/main.rs spawn_log_bridge_worker). Mirrors the
  // recording_finalized flow but for trained models: refresh the
  // ModelHub catalog, mark the just-trained model as the LATEST
  // candidate, switch to the ModelHub tab, and surface the
  // celebratory banner with a "Set Active & Run" CTA.
  //
  // Auto-select = YES, auto-activate = NO. The user must still click
  // Set Active before the bot is allowed to run with the new model.
  await listen("training_finalized", async (event) => {
    const meta = event.payload || {};
    const modelDir = String(meta.model_dir || "").trim();
    const modelName = String(meta.model_name || "").trim();
    const gid = String(meta.game_id || selectedGameId || DEFAULT_GAME_ID).trim();
    if (!modelDir) return;

    _lastTrainedPath = modelDir;
    logToTerminal(`Training complete -> ${modelDir}`, "success");
    window.notifySuccess?.(
      "Training complete",
      `${modelName || "New model"} is ready in ModelHub.`
    );

    // Refresh catalog so the new model appears in the gallery.
    try {
      await loadCatalog(gid);
    } catch (e) {
      console.warn("training_finalized: loadCatalog failed", e);
    }

    // Reveal celebration banner with Set Active CTA. The button
    // pre-selects the freshly trained model card (via _lastTrainedPath
    // which renderModelHubCards picked up) and calls Set Active for
    // the user — but they still triggered it explicitly with a click.
    const banner = document.getElementById("mh-just-trained-banner");
    const sub = document.getElementById("mh-jt-sub");
    const setBtn = document.getElementById("mh-jt-set-active");
    const dismissBtn = document.getElementById("mh-jt-dismiss");
    if (banner) banner.hidden = false;
    if (sub) sub.textContent = `${modelName || "New Model"} is ready. Set it active to run the bot.`;
    if (setBtn) {
      setBtn.onclick = async () => {
        // Mirror the latest-card selection into the hidden state shims.
        selectedLocalModelPath = modelDir;
        selectedBuiltinModelPath = "";
        selectedModelRegistryId = "";
        const localSel = getEl("local-model-select");
        if (localSel && Array.from(localSel.options).some(o => o.value === modelDir)) {
          localSel.value = modelDir;
        }
        await setActiveModelFromUI();
        if (banner) banner.hidden = true;
        if (typeof window.showTab === "function") window.showTab("run");
      };
    }
    if (dismissBtn) {
      dismissBtn.onclick = () => { if (banner) banner.hidden = true; };
    }

    // Switch to ModelHub so the user lands on the gallery, sees the
    // glowing LATEST card, and can confirm activation.
    if (typeof window.showTab === "function") window.showTab("models");
  });
}

// ------------------------------------------------------------
// INITIALIZATION + UI WIRING
// ------------------------------------------------------------

document.addEventListener("DOMContentLoaded", async () => {
  logToTerminal("═══════════════════════════════════════", "info");
  logToTerminal("BOT MMORPG AI (Tauri Edition)", "info");
  // Phase 23-B: log the UI bundle fingerprint as the FIRST thing
  // after the banner. Every captured bundle now carries this line,
  // so a stale-JS situation is visible at a glance.
  const _bundleTag = (BUILD_TAG === "%BUILD_TAG%") ? "dev (unstamped)" : BUILD_TAG;
  logToTerminal(`UI bundle: ${_bundleTag}`, "info");
  logToTerminal("Initializing Rust Core...", "info");

  // Show the sidecar chip immediately in "starting" state so the user
  // sees progress feedback during the cold-disk warm-up window. The
  // updateSidecarChipFromLogLine handler will flip it to ready/failed
  // when the corresponding terminal_update line arrives.
  const _chip = document.getElementById("sidecar-status-chip");
  const _chipState = document.getElementById("sidecar-chip-state");
  const _chipElapsed = document.getElementById("sidecar-chip-elapsed");
  if (_chip && _chipState) {
    _chip.dataset.state = "starting";
    _chip.hidden = false;
    _chipState.textContent = "Starting...";
    if (_chipElapsed) _chipElapsed.textContent = "0s/60s";
  }

  if (invoke) {
    updateBackendStatus("Running", "Rust Backend Active");
    // Phase 1.2: this line USED to read "✓ Tauri Backend Connected"
    // tagged "success", which was misleading -- it only confirms the
    // Tauri RPC bridge is up, not that the Python sidecar is running.
    // Users with a failed sidecar saw a green check immediately
    // followed by "Sidecar startup failed at app launch" and were
    // left guessing which "backend" was OK. Reword + downgrade tag
    // so the log reflects what was actually verified.
    logToTerminal("Tauri RPC bridge ready (Python sidecar status reported separately).", "info");

    await wireBackendEvents();

    // Initial Config Log (just for user confidence)
    invoke("get_ai_config").then((config) => {
      if(config.provider) {
        logToTerminal(`Loaded Config: ${config.provider}`, "info");
      }
    }).catch((err) => logToTerminal(`Config Load Warning: ${err}`, "warning"));

    // Pull installed version + channel from Rust and paint the sidebar.
    // Doing this BEFORE the GitHub-releases probe so the user sees a
    // real version on screen even when offline. The "Latest" line below
    // it is filled in later by checkForUpdate() if a newer release is
    // published.
    invoke("app_info").then((info) => {
      const ver = document.getElementById("sv-installed-version");
      const ch  = document.getElementById("sv-installed-channel");
      if (ver && info?.version) ver.textContent = "v" + info.version;
      if (ch  && info?.channel) ch.textContent  = "(" + info.channel + ")";
      // Stash for the support_report copy path / Settings -> Runtime tab.
      window.__appInfo = info;
    }).catch((err) => console.warn("app_info failed:", err));

    await refreshModelhubAvailability();

    // Health probe: detect a broken install (the v0.2.0 case where the
    // installer shipped without python-runtime.zip and ML scripts) so the
    // user sees an actionable banner instead of clicking "Start Recording"
    // and getting "Script not found" with no idea what to do about it.
    await checkInstallHealth();

    // Update probe: hits the GitHub Releases API via the Rust-side
    // reqwest client (no extra HTTP allowlist needed) and renders the
    // #update-banner if a newer version is published. Runs after
    // install_health so it appears below the more important error
    // banner when both fire.
    checkForUpdate();
  } else {
    updateBackendStatus("Offline", "Running in Offline Mode");
    logToTerminal("Running in offline mode - using default configurations", "warning");
  }

  // Always load games and catalog (uses defaults when sidecar unavailable)
  await loadGamesIntoUI();
  await loadCatalog(selectedGameId);

  wireEvents();
  wireDashboardButtons();
});

async function checkInstallHealth() {
  if (!invoke) return;
  try {
    // Two probes in parallel:
    //   install_health -- structural Rust-side check (files exist, sidecar
    //                     up, logs writable). Fast.
    //   runtime_doctor -- functional Python-side self-test (torch.testing
    //                     importable, VC++ present, port bindable). Slower
    //                     (~3-5s on cold disk because of torch import).
    // We merge the doctor's checks into the health rows so the existing
    // verdict-aware banner handles them with no schema changes.
    const [h, doctorRaw] = await Promise.all([
      invoke("install_health"),
      invoke("runtime_doctor").catch(e => {
        console.warn("runtime_doctor invocation failed:", e);
        return null;
      }),
    ]);

    if (doctorRaw && Array.isArray(doctorRaw.checks)) {
      // Map doctor's {name, status, detail} -> install_health's
      // {id, label, severity, status, message} schema. Status/severity
      // wording is normalized so the banner CSS classes line up.
      const sevMap = { ok: "ok", warn: "warn", error: "error" };
      const labelMap = {
        python_boot:           "Bundled Python boots",
        vc_redist:             "Visual C++ runtime",
        torch_intact:          "PyTorch (incl. torch.testing)",
        torch_dlls:            "PyTorch native libraries",
        torchvision_intact:    "torchvision",
        numpy_intact:          "NumPy (incl. numpy.testing)",
        fastapi_intact:        "FastAPI / uvicorn",
        cv2_intact:            "OpenCV (cv2)",
        data_dir_writable:     "Local data dir writable",
        sidecar_port_bindable: "Loopback port available",
        // Shell-fallback names (synth_doctor_error in main.rs):
        python_not_found:           "Bundled Python missing",
        doctor_script_not_found:    "Runtime doctor missing",
        spawn_failed:               "Doctor spawn failed",
        doctor_unparseable_output:  "Doctor output corrupt",
      };
      for (const c of doctorRaw.checks) {
        h.checks = h.checks || [];
        h.checks.push({
          id: `doctor_${c.name}`,
          label: labelMap[c.name] || c.name,
          severity: sevMap[c.status] || "error",
          status: (c.status === "ok") ? "OK"
                : (c.status === "warn") ? "Warning"
                : "Error",
          message: c.detail || "",
        });
      }
      // Verdict can only get worse from the doctor's verdict, never better.
      // (install_health says "ready", doctor says "error" -> show "error".)
      const order = { ready: 0, warning: 1, error: 2 };
      const merged = order[h.verdict] >= order[doctorRaw.verdict === "ok" ? "ready" : doctorRaw.verdict]
        ? h.verdict
        : (doctorRaw.verdict === "ok" ? "ready" : doctorRaw.verdict);
      h.verdict = merged;
      // Stash the raw doctor payload for the Settings -> Runtime tab.
      window.__lastDoctor = doctorRaw;
    }

    // Stash for the Settings -> Runtime tab to read without re-invoking.
    window.__lastHealth = h;

    // Sidebar gear gets a red dot when any check is severity=error.
    // Warnings alone don't show the dot -- avoids alarm fatigue.
    const dot = document.getElementById("settings-health-dot");
    if (dot) {
      const anyErr = Array.isArray(h.checks)
        ? h.checks.some(c => c.severity === "error")
        : !h.healthy;
      dot.hidden = !anyErr;
    }

    // Phase 4 (gap #5): hard-block the three action buttons when
    // install_health verdict is "error". Without this, a user with a
    // dead sidecar clicks Train and gets the fail-fast string from
    // wait_for_sidecar -- which is correct but feels like the click
    // "did something" before failing. With this, the button is
    // visibly disabled with a tooltip pointing at Diagnosis. We DON'T
    // disable on "warning" -- driver-missing alone is a per-action
    // concern (preflight_action handles it).
    applyHealthGate(h.verdict);

    // Phase 5: keep dashboard hero + header chip in lockstep with
    // the banner verdict. Without this they contradict each other
    // ("System Ready" + "Backend installation is incomplete").
    applyDashboardStatus(h.verdict);

    const banner   = document.getElementById("install-health-banner");
    const titleEl  = document.getElementById("install-health-title");
    const detailEl = document.getElementById("install-health-detail");
    if (!banner || !detailEl || !titleEl) return;

    // Verdict: "ready" / "warning" / "error". Fall back to legacy
    // healthy boolean for builds that predate the verdict field.
    const verdict = h.verdict || (h.healthy ? "ready" : "error");

    // Healthy -> hide. Warnings alone don't trigger the banner unless
    // we want them to (we do, with softer copy -- see below).
    if (verdict === "ready") {
      banner.hidden = true;
      logToTerminal("Install health: OK", "success");
      return;
    }

    const errs = Array.isArray(h.checks)
      ? h.checks.filter(c => c.severity === "error")
      : (h.issues || []).map(s => ({ label: s, message: "" }));
    const warns = Array.isArray(h.checks)
      ? h.checks.filter(c => c.severity === "warn")
      : [];

    // Pick title + remediation by verdict, with extra branching for
    // permissions-only error sets (the user CAN fix that without a
    // reinstall -- "run as admin or relocate" is the actionable copy).
    let title;
    let remediation;
    let cardClass;
    let logSeverity;
    let itemsToShow;

    const isPermissionsOnly =
      errs.length > 0 &&
      errs.every(c =>
        c.id === "logs_writable" ||
        /writable|permission|access\s*denied/i.test(c.message || "")
      );

    if (verdict === "error") {
      cardClass = "notification-card error";
      logSeverity = "error";
      itemsToShow = errs;
      if (isPermissionsOnly) {
        // User-fixable without a reinstall. Steam-grade: tell them
        // exactly what to do and why.
        title = "Permission issue — admin required";
        remediation =
          "The app can't write to its data directory. Two safe fixes:" +
          "<ul style='margin-top:6px;'>" +
            "<li>Right-click the app shortcut → <b>Run as administrator</b>.</li>" +
            "<li>Or reinstall to a user-writable location " +
              "(e.g. <code>%LOCALAPPDATA%\\BOT-MMORPG-AI</code>).</li>" +
          "</ul>";
      } else {
        // Phase 5: framed as a startup failure (which it is), not an
        // "install corruption" (which it usually isn't -- runtime
        // doctor is typically green when this fires). Action ladder
        // is the user-facing first response; advanced fixes live
        // in the collapsible details below.
        title = "Backend failed to start";
        remediation =
          "The AI backend did not start. This usually happens on first launch " +
          "or if something blocks Python from running." +
          "<div style='margin-top:10px;'><b>What to try:</b></div>" +
          "<ol style='margin:6px 0 0 20px; padding:0;'>" +
            "<li>Wait up to 60 seconds (first launch can be slow).</li>" +
            "<li>Click <b>Retry</b>.</li>" +
            "<li>Restart the app.</li>" +
            "<li>If it still fails, click <b>Open logs</b> or use Advanced fixes below.</li>" +
          "</ol>";
      }
    } else {
      // verdict === "warning". Lighter visual + non-blocking copy.
      cardClass = "notification-card warning";
      logSeverity = "warning";
      itemsToShow = warns;
      title = "Action recommended";
      remediation =
        "The app is running, but a non-critical issue was detected. " +
        "Review the items below — none of them block recording or training.";
    }

    titleEl.textContent = title;
    banner.className = cardClass;

    // Phase 5: keep the Detected list short (label only by default).
    // The long technical messages bloat the landing page; they're
    // available in full via Settings → System Tools → Run Diagnostics.
    const lines = itemsToShow
      .map(c => {
        const label = (c.label || c.id || "").toString();
        const safe = s => s.replace(/[<>&]/g, ch => ({"<":"&lt;",">":"&gt;","&":"&amp;"})[ch]);
        return `<li>${safe(label)}</li>`;
      })
      .join("");

    detailEl.innerHTML =
      remediation + (lines ? `<div style='margin-top:10px;'><b>Detected:</b><ul style='margin:6px 0 0 20px;'>${lines}</ul></div>` : "");

    banner.hidden = false;
    // Issue #79: this used to log only `h.issues`, the LEGACY string
    // array that install_health builds from its own rows. The runtime
    // doctor's failures are merged into `h.checks` (and can push the
    // verdict to "error") without ever touching `h.issues` -- so a user
    // whose only fault was a doctor row saw the bare line
    // "Install health: ERROR --" with nothing after the dashes, in a
    // log they were then asked to paste into a bug report.
    //
    // Prefer the merged checks; fall back to the legacy array for older
    // shells that don't emit `checks`.
    const reported = (errs.length ? errs : warns)
      .map(c => {
        const label = (c.label || c.id || "").toString().trim();
        const message = (c.message || "").toString().trim();
        return label && message ? `${label}: ${message}` : (label || message);
      })
      .filter(Boolean);
    const summary = reported.length ? reported : (h.issues || []);
    logToTerminal(
      `Install health: ${verdict.toUpperCase()} -- ` +
        (summary.length ? summary.join("; ") : "no per-check detail reported"),
      logSeverity
    );
    // NOTE: install-health-dismiss / install-health-open-diagnosis click
    // handlers are wired ONCE in the inline DOMContentLoaded block at the
    // bottom of index.html (so they fire even if this function throws
    // before reaching the wiring lines). Don't re-bind here.
  } catch (e) {
    console.warn("install_health probe failed:", e);
  }

  refreshDriversCard();
}
// Phase 5: expose for the Retry button (wired in index.html DOMContentLoaded).
// Keeping the bare `checkInstallHealth` name unchanged for the existing
// in-file callers; this just aliases it on window for cross-script use.
window.checkInstallHealth = checkInstallHealth;

// GitHub-releases update probe. Renders #update-banner when a newer
// version is published. Silently no-ops on network failure (offline
// users shouldn't see a scary error for a non-critical check).
async function checkForUpdate() {
  if (!invoke) return;
  try {
    const u = await invoke("check_for_update");
    if (!u || !u.ok || !u.update_available) return;

    // Stash so the patch-notes button (wired statically in index.html)
    // can read the latest release info without re-fetching.
    window.__lastUpdate = u;

    const banner = document.getElementById("update-banner");
    const pill   = document.getElementById("update-version-pill");
    const msg    = document.getElementById("update-banner-msg");
    if (!banner) return;

    if (pill) pill.textContent = `v${u.current_version} → v${u.latest_version}`;
    if (msg)  msg.textContent  =
      `A newer release of BOT-MMORPG-AI is published on GitHub. Updating preserves your models and datasets.`;
    banner.hidden = false;

    // Surface the "Latest" line in the sidebar version block. Hidden
    // until now (only shown when an update is genuinely available)
    // so users on the freshest build don't see a misleading empty
    // "Latest:" row.
    const updateRow  = document.getElementById("sv-update-row");
    const latestVerEl = document.getElementById("sv-latest-version");
    if (latestVerEl) latestVerEl.textContent = "v" + u.latest_version;
    if (updateRow)   updateRow.hidden = false;
    // NOTE: update-close / btn-update-later / btn-update-notes click
    // handlers are wired ONCE in the inline DOMContentLoaded block at
    // the bottom of index.html. Don't re-bind here.

    // Also drop a quieter toast so users who dismiss the banner still
    // see one passing reminder. Persistent because update-class.
    // Note: notifyUpdate's button onClicks route through window.open
    // which goes through the global <a> interceptor's fallback path
    // (the toast buttons aren't <a> elements so they need an explicit
    // shell.open call here too).
    const openExternal = (url) => {
      const open = window.__TAURI__?.shell?.open;
      if (typeof open === "function") {
        open(url).catch(() => window.open(url, "_blank", "noopener,noreferrer"));
      } else {
        window.open(url, "_blank", "noopener,noreferrer");
      }
    };
    window.notifyUpdate?.(
      `Update available: v${u.latest_version}`,
      u.release_notes ? u.release_notes.split("\n").slice(0, 3).join(" ") : "",
      [
        { label: "Update Now", primary: true, onClick: () => openExternal(u.release_url) },
        { label: "View Notes", onClick: () => window.openPatchNotes && window.openPatchNotes(u) },
      ]
    );
  } catch (e) {
    console.warn("check_for_update probe failed:", e);
  }
}

// State-aware Drivers card. Decides between three states based on the
// most recent install_health response (window.__lastHealth):
//
//   "ready"   - All hard prerequisites OK (sidecar, python, backend,
//               modelhub, scripts). Show the Install Drivers button as
//               normal. Driver-specific checks are still warn-level
//               and surface in the Settings -> Diagnosis panel.
//   "blocked" - Any error-severity check is failing. Hide the install
//               button, show the recovery panel ([Run Diagnosis]
//               [Copy Details] [Download Latest Installer]).
//   "checking"- No probe result yet (page loaded before checkInstallHealth
//               returned). Show a neutral checking state.
function refreshDriversCard() {
  const card     = document.getElementById('drivers-card');
  const badge    = document.getElementById('drivers-state-badge');
  const ready    = document.getElementById('drivers-pane-ready');
  const blocked  = document.getElementById('drivers-pane-blocked');
  const list     = document.getElementById('drivers-missing-list');
  const installBtn = document.getElementById('btnInstallDrivers');
  if (!card || !badge || !ready || !blocked) return;

  const h = window.__lastHealth;

  // No probe yet -> neutral
  if (!h) {
    card.dataset.state = 'checking';
    badge.className = 'diag-verdict warning';
    badge.textContent = '● Checking';
    ready.hidden = false;
    blocked.hidden = true;
    return;
  }

  // Hard prerequisites = every error-severity check.
  const hardErrors = Array.isArray(h.checks)
    ? h.checks.filter(c => c.severity === 'error')
    : (h.healthy ? [] : (h.issues || []).map(s => ({ label: s, message: '' })));

  if (hardErrors.length === 0) {
    card.dataset.state = 'ready';
    badge.className = 'diag-verdict ready';
    badge.textContent = '● Ready';
    ready.hidden = false;
    blocked.hidden = true;
    if (installBtn) installBtn.disabled = false;
  } else {
    card.dataset.state = 'blocked';
    badge.className = 'diag-verdict error';
    badge.textContent = '● Setup incomplete';
    ready.hidden = true;
    blocked.hidden = false;
    if (installBtn) installBtn.disabled = true;

    if (list) {
      list.innerHTML = hardErrors.map(c => {
        const label = (c.label || c.id || '').toString();
        const msg   = (c.message || '').toString();
        const lblHtml = label.replace(/[<>&]/g, '');
        const msgHtml = msg.replace(/[<>&]/g, '');
        return `<li><strong>${lblHtml}</strong>${msg ? ' — <span style="color: var(--text-dim);">' + msgHtml + '</span>' : ''}</li>`;
      }).join('');
    }
  }
}

// Wire the recovery actions inside the blocked-state Drivers panel.
// We do this once on DOMContentLoaded; the buttons live in static HTML
// so they're always present even when the panel is hidden.
document.addEventListener('DOMContentLoaded', () => {
  const runBtn = document.getElementById('btn-drivers-run-diagnosis');
  if (runBtn) runBtn.addEventListener('click', () => {
    if (typeof window.openSettings === 'function') window.openSettings();
    if (typeof window.switchSettingsTab === 'function') window.switchSettingsTab('system-tools');
    document.getElementById('btn-run-diagnosis')?.click();
  });

  const copyBtn = document.getElementById('btn-drivers-copy-details');
  if (copyBtn) copyBtn.addEventListener('click', async () => {
    if (!invoke) return;
    const orig = copyBtn.textContent;
    copyBtn.disabled = true; copyBtn.textContent = '⏳ Copying...';
    try {
      let report = await invoke('support_report');
      const term = document.getElementById('terminal');
      if (term) {
        const lines = Array.from(term.querySelectorAll('.log-entry'))
          .map(el => el.textContent.replace(/\s+/g, ' ').trim());
        if (lines.length) {
          report += '\n\n## Recent in-app log\n\n```\n' + lines.slice(-200).join('\n') + '\n```\n';
        }
      }
      await navigator.clipboard.writeText(report);
      copyBtn.textContent = '✓ Copied!';
    } catch (e) {
      copyBtn.textContent = '✗ Failed';
      console.warn('support_report failed:', e);
    } finally {
      setTimeout(() => { copyBtn.disabled = false; copyBtn.textContent = orig; }, 1500);
    }
  });
});

// Wire Dashboard Quick Action cards to navigate to tabs
function wireDashboardButtons() {
  // Dashboard hero Quick Start button
  const heroBtn = document.querySelector('.hero-status .btn');
  if (heroBtn) {
    heroBtn.addEventListener('click', (e) => {
      e.preventDefault();
      window.showTab('wizard');
    });
  }

  // Quick Action cards
  const cards = document.querySelectorAll('#tab-dashboard .card');
  cards.forEach(card => {
    // Get existing onclick attribute target
    const onclickAttr = card.getAttribute('onclick');
    if (onclickAttr) {
      // Extract tab name from onclick="window.showTab && window.showTab('teach')"
      const match = onclickAttr.match(/showTab\(['"](\w+)['"]\)/);
      if (match) {
        const tabName = match[1];
        // Remove onclick and add event listener
        card.removeAttribute('onclick');
        card.addEventListener('click', (e) => {
          e.preventDefault();
          window.showTab(tabName);
        });
      }
    }
  });

  // Also bind inline onclick buttons in other tabs
  document.querySelectorAll('[onclick*="showTab"]').forEach(el => {
    const onclickAttr = el.getAttribute('onclick');
    if (onclickAttr) {
      const match = onclickAttr.match(/showTab\(['"](\w+)['"]\)/);
      if (match) {
        const tabName = match[1];
        el.removeAttribute('onclick');
        el.addEventListener('click', (e) => {
          e.preventDefault();
          window.showTab(tabName);
        });
      }
    }
  });
}

// Generate dataset name based on game and timestamp
function generateDatasetName(gameId) {
  const gameName = gameId.replace(/_/g, '-');
  const date = new Date();
  const timestamp = `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getDate()).padStart(2, '0')}_${String(date.getHours()).padStart(2, '0')}${String(date.getMinutes()).padStart(2, '0')}`;
  return `${gameName}_session_${timestamp}`;
}

// Update dataset name when game changes
function updateDatasetName() {
  const gameId = getEl("teach-game-id")?.value || selectedGameId || DEFAULT_GAME_ID;
  const datasetInput = getEl("teach-dataset-name");
  if (datasetInput && !datasetInput.value) {
    datasetInput.value = generateDatasetName(gameId);
  }
}

function wireEvents() {
  // Tabs
  document.querySelectorAll("button[data-tab], a[data-tab]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const tab = btn.getAttribute("data-tab");
      if (tab) window.showTab(tab);
    });
  });

  // Auto-populate dataset name when game changes
  const teachGameId = getEl("teach-game-id");
  if (teachGameId) {
    teachGameId.addEventListener("change", () => {
      const datasetInput = getEl("teach-dataset-name");
      if (datasetInput) {
        datasetInput.value = generateDatasetName(teachGameId.value);
      }
      // Also update train tab
      const trainGameId = getEl("train-game-id");
      if (trainGameId) trainGameId.value = teachGameId.value;
    });
    // Generate initial dataset name
    updateDatasetName();
  }

  // Phase 22: also auto-fill the dataset-name input when the user
  // focuses it (clicks into it / tabs to it), if it's still empty.
  // Triple-redundant with the showTab hook + the toggleRecord
  // fallback, but cheap insurance against any timing weirdness
  // where one of the three fires too early (DOM not ready) or too
  // late (user clicked Start within ms of opening the tab).
  const datasetNameInput = getEl("teach-dataset-name");
  if (datasetNameInput) {
    datasetNameInput.addEventListener("focus", () => {
      if (!datasetNameInput.value) {
        const gid = getEl("teach-game-id")?.value || selectedGameId || DEFAULT_GAME_ID;
        datasetNameInput.value = generateDatasetName(gid);
      }
    });
  }

  // Buttons
  const bind = (id, func) => {
    const el = getEl(id);
    if (el) el.addEventListener("click", () => func(el));
  };

  bind("btnRecord", window.toggleRecord);
  bind("btnStartTraining", () => window.startTraining());
  bind("btnAnalyzeLogs", () => window.analyzeLogs());
  bind("btnStartBot", window.toggleBot);
  bind("btnInstallDrivers", () => window.installDrivers());
  bind("btnSendChat", () => window.sendChatMessage());
  
  // Settings Modal Buttons
  // Note: HTML might have them; ensure they exist before binding
  const btnOpenSettings = getEl("btn-open-settings");
  if (btnOpenSettings) {
    btnOpenSettings.addEventListener("click", () => {
        window.loadSettingsIntoModal();
        const overlay = getEl("settings-modal-overlay");
        if(overlay) overlay.classList.add("open");
    });
  }
  
  const btnSaveSettings = getEl("btn-save-settings");
  if (btnSaveSettings) {
      btnSaveSettings.addEventListener("click", saveSettingsFromModal);
  }

  // When provider changes in modal, clear the key input (UX safety)
  const settingsProvider = getEl("settings-provider");
  if(settingsProvider) {
      settingsProvider.addEventListener("change", () => {
          const keyInput = getEl("settings-api-key");
          if(keyInput) keyInput.value = "";
      });
  }

  // Chat Input
  const chatInput = getEl("chat-input");
  if (chatInput) {
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") window.sendChatMessage();
    });
  }

  // ModelHub UI wiring
  const gameSel = getEl("game-select");
  if (gameSel) {
    gameSel.addEventListener("change", async () => {
      selectedGameId = gameSel.value || DEFAULT_GAME_ID;
      await loadCatalog(selectedGameId);
    });
  }

  const dsSel = getEl("dataset-select");
  if (dsSel) {
    dsSel.addEventListener("change", () => {
      // Phase 29: normalize before mirroring. dataset-select's
      // valueForDataset() returns d.path (which can be a path-
      // shaped string like "genshin_impact/2026..."), but the
      // train-dataset-id <select> stores the leaf id only. Without
      // this normalize, mirroring set sel.value to a path that
      // didn't match any option -- the browser dropped the
      // assignment and the dropdown ended up empty.
      const normalized = normalizeDatasetId(dsSel.value || "");
      selectedDatasetId = normalized;
      const t = getEl("train-dataset-id");
      if (!t) return;
      if (t.tagName === "SELECT") {
        const has = Array.from(t.options).some(o => o.value === normalized);
        if (normalized && has) {
          t.value = normalized;
          _lastRealTrainDatasetValue = normalized;
          _refreshTrainGate?.();
        }
      } else if (!t.value) {
        t.value = normalized;
      }
    });
  }

  const builtinSel = getEl("builtin-model-select");
  if (builtinSel) {
    builtinSel.addEventListener("change", () => {
      selectedBuiltinModelPath = builtinSel.value || "";
      selectedModelRegistryId = "";
      selectedLocalModelPath = "";
      getEl("registry-model-select").value = "";
      getEl("local-model-select").value = "";
    });
  }

  const regSel = getEl("registry-model-select");
  if (regSel) {
    regSel.addEventListener("change", () => {
      selectedModelRegistryId = regSel.value || "";
      selectedBuiltinModelPath = "";
      selectedLocalModelPath = "";
      getEl("builtin-model-select").value = "";
      getEl("local-model-select").value = "";
    });
  }

  const localSel = getEl("local-model-select");
  if (localSel) {
    localSel.addEventListener("change", () => {
      selectedLocalModelPath = localSel.value || "";
      selectedBuiltinModelPath = "";
      selectedModelRegistryId = "";
      getEl("builtin-model-select").value = "";
      getEl("registry-model-select").value = "";
    });
  }

  const btnSetActive = getEl("btnSetActiveModel");
  if (btnSetActive) btnSetActive.addEventListener("click", () => setActiveModelFromUI());

  const btnDelete = getEl("btnDeleteModel");
  if (btnDelete) btnDelete.addEventListener("click", () => deleteSelectedModel());

  const btnValidate = getEl("btnValidateModel");
  if (btnValidate) btnValidate.addEventListener("click", () => validateSelectedModel());

  const btnOfflineEval = getEl("btnOfflineEval");
  if (btnOfflineEval) btnOfflineEval.addEventListener("click", () => runOfflineEvaluation());

  // ModelHub gallery refresh button (re-runs the catalog fetch so the
  // user can pick up newly trained models without restarting the app).
  const btnMhRefresh = getEl("mh-refresh");
  if (btnMhRefresh) btnMhRefresh.addEventListener("click", () => loadCatalog(selectedGameId));

  // Screen Preview buttons
  const btnRefreshTeachPreview = getEl("btnRefreshTeachPreview");
  if (btnRefreshTeachPreview) btnRefreshTeachPreview.addEventListener("click", () => refreshTeachPreview());

  const btnRefreshRunPreview = getEl("btnRefreshRunPreview");
  if (btnRefreshRunPreview) btnRefreshRunPreview.addEventListener("click", () => refreshRunPreview());

  // Live Preview toggle checkboxes
  const teachLiveToggle = getEl("teach-live-preview-toggle");
  if (teachLiveToggle) {
    teachLiveToggle.addEventListener("change", () => toggleTeachLivePreviewTauri(teachLiveToggle.checked));
  }

  const runLiveToggle = getEl("run-live-preview-toggle");
  if (runLiveToggle) {
    runLiveToggle.addEventListener("change", () => toggleRunLivePreviewTauri(runLiveToggle.checked));
  }

  // Auto-generate dataset name button
  const btnAutoGenDataset = getEl("btnAutoGenDataset");
  if (btnAutoGenDataset) btnAutoGenDataset.addEventListener("click", () => autoGenerateDatasetNameTauri());

  // Refresh datasets list button (Teach tab)
  const btnRefreshDatasets = getEl("btnRefreshDatasets");
  if (btnRefreshDatasets) btnRefreshDatasets.addEventListener("click", () => refreshDatasetListTauri());

  // Phase 27: refresh button next to the Train tab dataset dropdown.
  // Same backend call -- and refreshDatasetListTauri already updates
  // the dropdown -- so this is just a UX shortcut for "I recorded
  // from somewhere else; pull the latest list".
  const btnRefreshTrainDatasets = getEl("btnRefreshTrainDatasets");
  if (btnRefreshTrainDatasets) {
    btnRefreshTrainDatasets.addEventListener("click", () => refreshDatasetListTauri());
  }

  // Phase 27: re-fetch when the user retypes the Train tab's game id.
  // Datasets are scoped per-game in the backend, so the dropdown must
  // re-populate or it'll silently offer datasets from a stale game.
  const trainGameIdEl = getEl("train-game-id");
  if (trainGameIdEl) {
    let _retrainGameTimer = null;
    trainGameIdEl.addEventListener("input", () => {
      // Debounce: the user is mid-typing. Wait for a pause.
      clearTimeout(_retrainGameTimer);
      _retrainGameTimer = setTimeout(() => refreshDatasetListTauri(), 400);
    });
  }

  // Phase 27/28: dropdown change listener.
  //   - Refresh / Open-folder action items are intercepted and never
  //     become the chosen value (we revert to the previous selection
  //     after firing the action).
  //   - Real dataset picks update selectedDatasetId, the selected-
  //     dataset preview card, and the Start-Training gate so the
  //     button enables/disables atomically with the value.
  // (Phase 29: _lastRealTrainDatasetValue moved to module scope so
  // populateTrainDatasetDropdown can seed it from outside this
  // closure -- otherwise the Refresh action wipes the selection on
  // a fresh load.)
  const trainDatasetSel = getEl("train-dataset-id");
  if (trainDatasetSel && trainDatasetSel.tagName === "SELECT") {
    trainDatasetSel.addEventListener("change", () => {
      const v = trainDatasetSel.value || "";
      const opt = trainDatasetSel.selectedOptions[0];
      const action = opt && opt.dataset ? opt.dataset.action : null;

      if (action === "refresh") {
        trainDatasetSel.value = _lastRealTrainDatasetValue || "";
        refreshDatasetListTauri();
        return;
      }
      if (action === "open-folder") {
        trainDatasetSel.value = _lastRealTrainDatasetValue || "";
        const gid = (
          getEl("train-game-id")?.value
          || selectedGameId
          || DEFAULT_GAME_ID
        ).trim();
        if (invoke) {
          invoke("open_datasets_folder", { game_id: gid })
            .then(msg => logToTerminal(`Datasets folder: ${msg}`, "info"))
            .catch(e => {
              logToTerminal(`Could not open datasets folder: ${e}`, "error");
              window.notifyError?.("Could not open folder", String(e));
            });
        }
        return;
      }

      // Real dataset selection.
      _lastRealTrainDatasetValue = v;
      selectedDatasetId = v;
      // Re-render the selected-card + gate from current dropdown
      // state. We don't have the full dataset entry on hand here so
      // we synthesize a minimal one from the option label; the next
      // refreshDatasetListTauri call will replace it with the rich
      // version.
      const synth = { id: v, name: v, created_at: "", file_count: null };
      // Index 0 of an optgroup-driven select is the "Latest" entry.
      const isLatest = trainDatasetSel.selectedIndex === 0;
      _renderTrainSelectedCard(synth, isLatest);
      _refreshTrainGate();

      const hint = getEl("train-dataset-hint");
      if (hint) {
        hint.classList.remove("is-empty");
        hint.textContent = isLatest
          ? "Latest recording auto-selected."
          : "Older dataset selected.";
      }
    });
  }

  // Load monitors on startup
  loadMonitorsTauri();
  refreshDatasetListTauri();
}

// ============================================================
// SCREEN PREVIEW & MONITOR SELECTION (Tauri Version)
// ============================================================

let previewIntervalTauri = null;
let selectedMonitorTeach = 0;
let selectedMonitorRun = 0;
let livePreviewEnabledTeach = false;
let livePreviewEnabledRun = false;

async function loadMonitorsTauri() {
  if (!invoke) return;

  try {
    const monitors = await invoke("list_monitors");
    const teachSelect = getEl("teach-monitor-select");
    const runSelect = getEl("run-monitor-select");

    if (monitors && monitors.length > 0) {
      if (teachSelect) {
        teachSelect.innerHTML = '';
        monitors.forEach(m => {
          const opt = document.createElement("option");
          opt.value = m.id;
          opt.textContent = m.name;
          teachSelect.appendChild(opt);
        });
      }
      if (runSelect) {
        runSelect.innerHTML = '';
        monitors.forEach(m => {
          const opt = document.createElement("option");
          opt.value = m.id;
          opt.textContent = m.name;
          runSelect.appendChild(opt);
        });
      }
    }
  } catch (e) {
    console.warn("Failed to load monitors:", e);
    logToTerminal("Monitor detection not available", "info");
  }
}

async function refreshTeachPreview() {
  const _rawTeachMon = parseInt(getEl("teach-monitor-select")?.value, 10);
  const monitorId = Number.isFinite(_rawTeachMon) ? _rawTeachMon : 0;
  selectedMonitorTeach = monitorId;
  await updatePreviewImageTauri("teach", monitorId);
}

async function refreshRunPreview() {
  const _rawRunMon = parseInt(getEl("run-monitor-select")?.value, 10);
  const monitorId = Number.isFinite(_rawRunMon) ? _rawRunMon : 0;
  selectedMonitorRun = monitorId;
  await updatePreviewImageTauri("run", monitorId);
}

// Toggle functions for live preview checkboxes
function toggleTeachLivePreviewTauri(enabled) {
  livePreviewEnabledTeach = enabled;
  if (enabled) {
    startLivePreviewTauri("teach");
  } else {
    stopLivePreviewTauri();
  }
}

function toggleRunLivePreviewTauri(enabled) {
  livePreviewEnabledRun = enabled;
  if (enabled) {
    startLivePreviewTauri("run");
  } else {
    stopLivePreviewTauri();
  }
}

async function updatePreviewImageTauri(tab, monitorId) {
  if (!invoke) return;

  const imgEl = getEl(tab + "-preview-img");
  const placeholder = getEl(tab + "-preview-placeholder");
  // Phase 30: the Run viewport uses .runbot-viewport.is-live to swap
  // between the empty state and the live image (CSS rule). Toggle the
  // class instead of poking inline display so the AAA-style frame +
  // gradient stay intact.
  const container = getEl(tab + "-preview-container");

  try {
    const result = await invoke("get_screen_preview", { monitor_id: monitorId });
    if (result && result.ok && result.image) {
      if (imgEl) {
        imgEl.src = "data:image/jpeg;base64," + result.image;
        imgEl.style.display = "block";
      }
      if (placeholder) placeholder.style.display = "none";
      if (container) container.classList.add("is-live");
    }
  } catch (e) {
    console.warn("Preview error:", e);
    logToTerminal("Screen preview not available (requires Python sidecar)", "info");
  }
}

function startLivePreviewTauri(tab) {
  stopLivePreviewTauri();
  previewIntervalTauri = setInterval(async () => {
    const monitorId = tab === "teach" ? selectedMonitorTeach : selectedMonitorRun;
    await updatePreviewImageTauri(tab, monitorId);
  }, 500); // 2 FPS
}

function stopLivePreviewTauri() {
  if (previewIntervalTauri) {
    clearInterval(previewIntervalTauri);
    previewIntervalTauri = null;
  }
}

// Start live preview only if toggle is enabled
function maybeStartLivePreviewTauri(tab) {
  const enabled = tab === "teach" ? livePreviewEnabledTeach : livePreviewEnabledRun;
  if (enabled) {
    startLivePreviewTauri(tab);
  }
}

// ============================================================
// DATASET MANAGEMENT (Tauri Version)
// ============================================================

async function autoGenerateDatasetNameTauri() {
  const gameId = getEl("teach-game-id")?.value || selectedGameId || DEFAULT_GAME_ID;
  const datasetInput = getEl("teach-dataset-name");

  if (invoke) {
    try {
      const name = await invoke("generate_dataset_name", { game_id: gameId, task: "general" });
      if (datasetInput && name) {
        datasetInput.value = name;
        logToTerminal(`Generated dataset name: ${name}`, "success");
        return;
      }
    } catch (e) {
      console.warn("Auto-generate via backend failed:", e);
    }
  }

  // Fallback: client-side generation
  if (datasetInput) {
    datasetInput.value = generateDatasetName(gameId);
    logToTerminal(`Generated dataset name: ${datasetInput.value}`, "success");
  }
}

// Phase 27: shared fetch + sort. Both the Teach tab list and the
// Train tab dropdown render from the same backend response so they
// can never disagree about what exists. Newest-first ordering is
// driven primarily by `created_at` (ISO 8601, lexicographically
// sortable) with a fallback to the dataset id which itself encodes
// a YYYYMMDD_HHMMSS prefix.
async function fetchDatasetsForGameTauri(gameId) {
  if (!invoke) return { datasets: [], error: "Backend not available" };
  try {
    const resp = await invoke("list_datasets", { game_id: gameId });
    const arr = Array.isArray(resp) ? resp : (resp && resp.datasets) || [];
    arr.sort((a, b) => {
      const ka = (a.created_at || a.id || "");
      const kb = (b.created_at || b.id || "");
      // Descending: newest first.
      return kb.localeCompare(ka);
    });
    return { datasets: arr, error: resp && resp.error };
  } catch (e) {
    console.warn("Failed to fetch datasets:", e);
    return { datasets: [], error: String(e) };
  }
}

// Phase 29: canonicalize a dataset entry into the leaf id Rust's
// preflight expects (`<datasets_dir>/<game>/<id>` exists check).
// Tolerates several legacy shapes:
//   { id: "20260428_..." }            -> "20260428_..."
//   { dataset_id: "20260428_..." }    -> "20260428_..."
//   { path: "genshin_impact/2026..." } -> "2026..."
//   { path: "C:\\...\\genshin_impact\\2026..." } -> "2026..."
// Also strips any " · ? frames" UI suffix that might have leaked in
// (defensive -- our options shouldn't carry it but the bug report
// suggested it could happen).
function normalizeDatasetId(d) {
  if (!d) return "";
  let raw = "";
  if (typeof d === "string") raw = d;
  else raw = (d.id || d.dataset_id || d.path || "").toString();
  raw = raw.trim();
  if (!raw) return "";
  // If raw contains a path separator, take the last segment.
  if (raw.includes("/") || raw.includes("\\")) {
    const parts = raw.split(/[\\/]+/).filter(Boolean);
    raw = (parts[parts.length - 1] || "").trim();
  }
  // Strip " · " UI suffix (defensive against any code path that
  // accidentally wrote a label into a value field).
  const dotIdx = raw.indexOf("·");
  if (dotIdx >= 0) raw = raw.slice(0, dotIdx).trim();
  return raw;
}

// Phase 29: priority-ordered resolver. Returns the canonical dataset
// id for the train preflight, trying every UI source so we never
// ship an empty payload while a dataset visibly exists in the
// dropdown:
//   1. select.value  -- normal happy path, set by populate
//   2. selectedOption.dataset.datasetId -- mirror attribute we now
//      stamp on every option as a parallel id channel that survives
//      browser quirks where .value gets dropped (path-vs-id, stale
//      placeholder, etc.)
//   3. selectedOption.textContent before " · " -- last-ditch
//      reconstruction from the visible label
//   4. selectedDatasetId global -- caches recent picks
// Action items (__action_*) are returned as "" so they never become
// a dataset id.
function resolveSelectedTrainDatasetId() {
  const sel = getEl("train-dataset-id");
  if (!sel) return (selectedDatasetId || "").trim();

  const value = (sel.value || "").trim();
  if (value && !value.startsWith("__action_")) {
    return normalizeDatasetId(value);
  }

  const opt = sel.selectedOptions && sel.selectedOptions[0];
  if (opt) {
    const fromData = (opt.dataset && opt.dataset.datasetId) || "";
    if (fromData) return normalizeDatasetId(fromData);
    const fromLabel = (opt.textContent || "").split("·")[0].trim();
    if (fromLabel && !fromLabel.toLowerCase().startsWith("loading")) {
      return normalizeDatasetId(fromLabel);
    }
  }

  return (selectedDatasetId || "").trim();
}

// Phase 28: human-friendly "when" string from an ISO 8601 created_at.
// Shows "Today HH:MM", "Yesterday HH:MM", "MMM D" for older entries.
// Falls back to the raw string if parsing fails so we never display
// "NaN" or "Invalid Date".
function _trainDatasetWhen(createdAt) {
  if (!createdAt) return "";
  const d = new Date(createdAt);
  if (isNaN(d.getTime())) return createdAt;
  const now = new Date();
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  const sameDay = d.toDateString() === now.toDateString();
  const yest = new Date(now); yest.setDate(now.getDate() - 1);
  const wasYesterday = d.toDateString() === yest.toDateString();
  if (sameDay) return `Today ${hh}:${mm}`;
  if (wasYesterday) return `Yesterday ${hh}:${mm}`;
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function _trainDatasetSamples(ds) {
  const n = ds.sample_count ?? ds.file_count;
  if (n == null) return "? frames";
  // Comma-separate large counts: 4280 -> "4,280"
  return `${Number(n).toLocaleString()} frames`;
}

function _trainDatasetResolution(ds) {
  // Future-proof: dataset entry MAY include a resolution field; if
  // not, infer from the recording session is impossible here -- we
  // omit rather than guess.
  return ds.resolution || "";
}

// Phase 27/28: keeps the Train tab's dataset <select> in lockstep
// with the backend. Renders three optgroups:
//   Latest         -- the single newest dataset (the auto-pick)
//   Recent datasets -- everything else, newest first
//   Actions        -- "Refresh datasets" / "Open datasets folder"
//                     intercepted on change so they never become the
//                     chosen value.
// Also drives the selected-dataset preview card and the Start-
// Training enable-gate so UI state can never contradict itself
// (the Phase 28 "Dataset id filled but preflight says 'No dataset
// selected'" bug fix).
function populateTrainDatasetDropdown(datasets, preferId) {
  const sel = getEl("train-dataset-id");
  if (!sel || sel.tagName !== "SELECT") return;

  const hint = getEl("train-dataset-hint");
  const list = Array.isArray(datasets) ? datasets : [];

  // Wipe and rebuild. Cheap and avoids stale-option leaks.
  sel.innerHTML = "";

  if (list.length === 0) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.disabled = true;
    opt.selected = true;
    opt.textContent = "No datasets yet — record one in the Teach tab";
    sel.appendChild(opt);

    // Even the empty state offers Refresh -- user might have
    // recorded from another machine / pulled a dataset folder in.
    const actions = document.createElement("optgroup");
    actions.label = "Actions";
    const refresh = document.createElement("option");
    refresh.value = "__action_refresh__";
    refresh.dataset.action = "refresh";
    refresh.textContent = "↻  Refresh datasets";
    actions.appendChild(refresh);
    sel.appendChild(actions);

    selectedDatasetId = "";
    _lastRealTrainDatasetValue = "";
    if (hint) {
      hint.classList.add("is-empty");
      hint.textContent = "No datasets for this game yet. Switch to the Teach tab and record one.";
    }
    _renderTrainSelectedCard(null);
    _refreshTrainGate();
    return;
  }

  // Phase 29: normalize ids up front so the value/preferId/find
  // comparisons all operate on the same form. Path-shaped ids
  // (`genshin_impact/2026...`) used to silently mismatch when the
  // option's value was the leaf id but preferId was the path -- the
  // browser would then drop sel.value=preferId and the dropdown
  // ended up with the FIRST option's value (or "" if it was the
  // disabled placeholder), which is one of the paths producing the
  // empty dataset_id at preflight time.
  const latest = list[0];
  const latestId = normalizeDatasetId(latest);
  const wantId = preferId ? normalizeDatasetId(preferId) : "";

  // ----- Latest group -----
  const grpLatest = document.createElement("optgroup");
  grpLatest.label = "Latest";
  grpLatest.appendChild(_makeTrainDatasetOption(latest, true));
  sel.appendChild(grpLatest);

  // ----- Recent group (everything else, newest-first) -----
  if (list.length > 1) {
    const grpRecent = document.createElement("optgroup");
    grpRecent.label = "Recent datasets";
    list.slice(1).forEach(ds => {
      grpRecent.appendChild(_makeTrainDatasetOption(ds, false));
    });
    sel.appendChild(grpRecent);
  }

  // ----- Actions group (intercepted on change) -----
  const grpActions = document.createElement("optgroup");
  grpActions.label = "Actions";
  const refresh = document.createElement("option");
  refresh.value = "__action_refresh__";
  refresh.dataset.action = "refresh";
  refresh.textContent = "↻  Refresh datasets";
  grpActions.appendChild(refresh);
  const openFolder = document.createElement("option");
  openFolder.value = "__action_open_folder__";
  openFolder.dataset.action = "open-folder";
  openFolder.textContent = "📂  Open datasets folder";
  grpActions.appendChild(openFolder);
  sel.appendChild(grpActions);

  // Pick: explicit prefer wins; otherwise newest (= latest group).
  let chosen = "";
  if (wantId) {
    const found = list.find(d => normalizeDatasetId(d) === wantId);
    if (found) {
      sel.value = wantId;
      chosen = wantId;
    }
  }
  if (!chosen) {
    sel.value = latestId;
    chosen = latestId;
  }
  selectedDatasetId = chosen;
  // Phase 29: seed the action-revert anchor from outside the
  // wireEvents() closure. Without this seed, a fresh-app user who
  // clicked the Refresh action item would have sel.value reverted
  // to "" because _lastRealTrainDatasetValue was still "".
  _lastRealTrainDatasetValue = chosen;

  if (hint) {
    hint.classList.remove("is-empty");
    const isLatest = chosen === latestId;
    hint.textContent = isLatest
      ? `Latest recording auto-selected (${list.length} available).`
      : `Older dataset selected. Newest: ${latestId}`;
  }

  const chosenEntry = list.find(d => normalizeDatasetId(d) === chosen) || latest;
  _renderTrainSelectedCard(chosenEntry, normalizeDatasetId(chosenEntry) === latestId);
  _refreshTrainGate();
}

function _makeTrainDatasetOption(ds, isLatest) {
  const opt = document.createElement("option");
  // Phase 29: canonical id via normalize, plus a redundant
  // data-dataset-id attribute. The redundancy is intentional:
  // resolveSelectedTrainDatasetId() falls back to data-dataset-id
  // if .value somehow got blanked (path vs id mismatch, browser
  // dropping a value when the option set was being rebuilt, etc.).
  const id = normalizeDatasetId(ds);
  opt.value = id;
  opt.dataset.datasetId = id;
  const samples = _trainDatasetSamples(ds);
  const when = _trainDatasetWhen(ds.created_at);
  const res = _trainDatasetResolution(ds);
  const human = ds.name && ds.name !== id ? ds.name : id;
  const parts = [human];
  if (when) parts.push(when);
  parts.push(samples);
  if (res) parts.push(res);
  opt.textContent = parts.join("  ·  ");
  if (isLatest) opt.dataset.latest = "true";
  return opt;
}

function _renderTrainSelectedCard(ds, isLatest) {
  const card = getEl("train-selected-card");
  if (!card) return;
  if (!ds) {
    card.hidden = true;
    return;
  }
  card.hidden = false;
  const tag  = getEl("train-selected-tag");
  const name = getEl("train-selected-name");
  const meta = getEl("train-selected-meta");
  const idEl = getEl("train-selected-id");
  if (tag) {
    tag.textContent = isLatest ? "Latest" : "Older";
    tag.classList.toggle("is-older", !isLatest);
  }
  if (name) name.textContent = ds.name && ds.name !== ds.id ? ds.name : ds.id;
  if (meta) {
    const parts = [];
    const when = _trainDatasetWhen(ds.created_at);
    if (when) parts.push(when);
    parts.push(_trainDatasetSamples(ds));
    const res = _trainDatasetResolution(ds);
    if (res) parts.push(res);
    meta.textContent = parts.join("  ·  ");
  }
  if (idEl) idEl.textContent = ds.id || "—";
}

// Phase 28: gate Start Training on having a real dataset selected.
// Driven by the dropdown's current value. Status row text reflects
// the same state so UI can never contradict itself ("dataset id
// filled but preflight says no dataset selected").
function _refreshTrainGate() {
  const sel    = getEl("train-dataset-id");
  const btn    = getEl("btnStartTraining");
  const statEl = getEl("train-status-text");
  const badge  = getEl("train-status-badge");
  if (!btn) return;

  const value = sel ? (sel.value || "") : "";
  const isAction = value.startsWith("__action_");
  const hasDataset = !!value && !isAction;

  // Don't unblock the button if a training run is already underway.
  if (btn.classList.contains("is-running")) return;

  btn.disabled = !hasDataset;

  if (statEl) {
    statEl.classList.remove("is-blocked", "is-ready", "is-running");
    if (!hasDataset) {
      statEl.textContent = "Pick a dataset to start";
      statEl.classList.add("is-blocked");
    } else {
      statEl.textContent = "Ready to train";
      statEl.classList.add("is-ready");
    }
  }
  if (badge && !badge.dataset.locked) {
    badge.dataset.state = hasDataset ? "ready" : "idle";
    const label = badge.querySelector(".train-status-label");
    if (label) label.textContent = hasDataset ? "Ready" : "Idle";
  }
}

function _setTrainBadgeRunning() {
  const badge = getEl("train-status-badge");
  const btn   = getEl("btnStartTraining");
  const statEl = getEl("train-status-text");
  if (badge) {
    badge.dataset.state = "running";
    badge.dataset.locked = "1";
    const label = badge.querySelector(".train-status-label");
    if (label) label.textContent = "Running";
  }
  if (btn) {
    btn.classList.add("is-running");
    btn.disabled = true;
    const labelSpan = btn.querySelector(".train-start-label");
    if (labelSpan) labelSpan.textContent = "Training...";
  }
  if (statEl) {
    statEl.classList.remove("is-blocked", "is-ready");
    statEl.classList.add("is-running");
    statEl.textContent = "Training in progress...";
  }
}

function _setTrainBadgeIdle() {
  const badge = getEl("train-status-badge");
  const btn   = getEl("btnStartTraining");
  if (badge) {
    delete badge.dataset.locked;
  }
  if (btn) {
    btn.classList.remove("is-running");
    const labelSpan = btn.querySelector(".train-start-label");
    if (labelSpan) labelSpan.textContent = "Start training";
  }
  _refreshTrainGate();
}

async function refreshDatasetListTauri(preferId, gameIdOverride) {
  const listEl = getEl("teach-dataset-list");

  if (listEl) {
    listEl.innerHTML = '<div style="color:var(--text-dim); font-size:12px;">Loading...</div>';
  }

  if (!invoke) {
    if (listEl) listEl.innerHTML = '<div style="color:var(--text-dim); font-size:12px;">Backend not available</div>';
    populateTrainDatasetDropdown([], null);
    return;
  }

  // An explicit override (from the stop/finalize flows) wins so an
  // event-driven refresh can target the game that was actually recorded
  // and never gets routed to stale state. Otherwise prefer the Train-tab
  // game id, then Teach, staying backwards-compatible. Normalized so the
  // scanned folder matches the safe id used at record time.
  const gameId = normalizeCustomGameId(
    gameIdOverride
    || getEl("train-game-id")?.value
    || getEl("teach-game-id")?.value
    || selectedGameId
    || DEFAULT_GAME_ID
  );

  const { datasets, error } = await fetchDatasetsForGameTauri(gameId);

  // Update the Train dropdown FIRST so an event-driven prefer (e.g.
  // recording_finalized) doesn't race against the slower DOM build
  // of the Teach list below.
  populateTrainDatasetDropdown(datasets, preferId);

  if (!listEl) return;

  if (!datasets || datasets.length === 0) {
    const emptyMsg = error
      ? `No datasets found (${error})`
      : "No datasets yet — recordings on the Teach tab show up here.";
    listEl.innerHTML = `<div style="color:var(--text-dim); font-size:12px;">${emptyMsg}</div>`;
    return;
  }

  listEl.innerHTML = "";
  datasets.forEach(ds => {
    const item = document.createElement("div");
    item.style.cssText = "display:flex; justify-content:space-between; align-items:center; padding:10px; margin-bottom:8px; background:rgba(255,255,255,0.03); border:1px solid var(--border); border-radius:8px;";
    item.innerHTML = `
      <div>
        <div style="font-weight:600; color:#fff;">${escapeHtml(ds.name || ds.id)}</div>
        <div style="font-size:11px; color:var(--text-dim);">${escapeHtml(ds.created_at || '')} • ${ds.sample_count || ds.file_count || '?'} samples</div>
      </div>
      <div style="display:flex; gap:6px;">
        <button class="btn btn-small btn-secondary" data-action="use" data-id="${escapeHtml(ds.id)}">Use</button>
        <button class="btn btn-small btn-danger" data-action="delete" data-id="${escapeHtml(ds.id)}" data-path="${escapeHtml(ds.path || '')}">Del</button>
      </div>
    `;
    listEl.appendChild(item);
  });

  // Wire up buttons
  listEl.querySelectorAll('button[data-action="use"]').forEach(btn => {
    btn.addEventListener("click", () => selectDatasetForTrainingTauri(btn.dataset.id));
  });
  listEl.querySelectorAll('button[data-action="delete"]').forEach(btn => {
    btn.addEventListener("click", () => deleteDatasetTauri(btn.dataset.id, btn.dataset.path));
  });
}

function selectDatasetForTrainingTauri(datasetId) {
  // Phase 27: now drives a <select>, not a freeform input. If the
  // option already exists (it should, since the Teach list and the
  // Train dropdown share the same fetch), just set .value. If it
  // doesn't (e.g. dataset registered after the last refresh), kick
  // off a refresh that prefers this id, which will both populate
  // and select it.
  const trainDataset = getEl("train-dataset-id");
  if (trainDataset && trainDataset.tagName === "SELECT") {
    const has = Array.from(trainDataset.options).some(o => o.value === datasetId);
    if (has) {
      trainDataset.value = datasetId;
      selectedDatasetId = datasetId;
    } else {
      refreshDatasetListTauri(datasetId);
    }
  } else if (trainDataset) {
    // Defensive fallback for the legacy <input> form.
    trainDataset.value = datasetId;
    selectedDatasetId = datasetId;
  }
  logToTerminal(`Selected dataset: ${datasetId}`, "success");
  window.showTab("train");
}

async function deleteDatasetTauri(datasetId, path) {
  if (!confirm(`Delete dataset "${datasetId}"?\n\nThis cannot be undone.`)) return;

  if (!invoke) return;

  try {
    const gameId = getEl("teach-game-id")?.value || selectedGameId || DEFAULT_GAME_ID;
    const result = await invoke("delete_dataset", { game_id: gameId, dataset_id: datasetId, path });
    if (result && result.ok) {
      logToTerminal(`Deleted dataset: ${datasetId}`, "success");
      await refreshDatasetListTauri();
      await loadCatalog(gameId);
    } else {
      logToTerminal(`Delete failed: ${result?.message || 'Unknown error'}`, "error");
    }
  } catch (e) {
    console.warn("Delete failed:", e);
    logToTerminal(`Delete error: ${e}`, "error");
  }
}

function escapeHtml(str) {
  return (str ?? "").toString()
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// =============================================================================
// GAME PRESET GRID UI
// =============================================================================

function populateGamePresetGrid() {
  const grid = getEl("game-preset-grid");
  if (!grid) return;

  grid.innerHTML = "";

  const savedGame = localStorage.getItem('selected_game_preset') || 'genshin_impact';

  Object.values(GAME_PRESETS).forEach(preset => {
    const card = document.createElement("div");
    const isSelected = preset.id === savedGame;

    card.className = "game-preset-card";
    card.dataset.gameId = preset.id;
    card.style.cssText = `
      padding: 12px 10px;
      border-radius: 10px;
      border: 2px solid ${isSelected ? preset.color : 'var(--border)'};
      background: ${isSelected ? `rgba(255,255,255,0.08)` : 'rgba(0,0,0,0.2)'};
      cursor: pointer;
      transition: all 0.2s ease;
      text-align: center;
      ${isSelected ? `box-shadow: 0 0 15px ${preset.color}40;` : ''}
    `;

    card.innerHTML = `
      <div style="font-size: 28px; margin-bottom: 6px;">${preset.icon}</div>
      <div style="font-size: 12px; font-weight: 600; color: ${isSelected ? preset.color : 'var(--text-main)'}; line-height: 1.2;">
        ${preset.name.split(' ').slice(0, 2).join(' ')}
      </div>
      <div style="font-size: 10px; color: var(--text-dim); margin-top: 3px;">${preset.resolution}</div>
    `;

    // Hover effects
    card.addEventListener("mouseenter", () => {
      if (card.dataset.gameId !== selectedGameId) {
        card.style.borderColor = preset.color;
        card.style.background = "rgba(255,255,255,0.05)";
      }
    });
    card.addEventListener("mouseleave", () => {
      if (card.dataset.gameId !== selectedGameId) {
        card.style.borderColor = "var(--border)";
        card.style.background = "rgba(0,0,0,0.2)";
      }
    });

    // Click handler
    card.addEventListener("click", () => {
      // Remove selection from all cards
      grid.querySelectorAll(".game-preset-card").forEach(c => {
        const cPreset = GAME_PRESETS[c.dataset.gameId];
        c.style.borderColor = "var(--border)";
        c.style.background = "rgba(0,0,0,0.2)";
        c.style.boxShadow = "none";
        c.querySelector("div:nth-child(2)").style.color = "var(--text-main)";
      });

      // Select this card
      card.style.borderColor = preset.color;
      card.style.background = "rgba(255,255,255,0.08)";
      card.style.boxShadow = `0 0 15px ${preset.color}40`;
      card.querySelector("div:nth-child(2)").style.color = preset.color;

      // Apply preset settings
      applyGamePreset(preset.id);

      // Load catalog for selected game
      loadCatalog(preset.id);
    });

    grid.appendChild(card);
  });

  // Apply saved preset on load
  if (savedGame) {
    applyGamePreset(savedGame);
  }
}

// Initialize game presets on page load
document.addEventListener("DOMContentLoaded", () => {
  // Populate game preset grid
  populateGamePresetGrid();

  // Sync game select changes in ModelHub
  const gameSelect = getEl("game-select");
  if (gameSelect) {
    gameSelect.addEventListener("change", () => {
      const gameId = gameSelect.value;
      if (gameId && GAME_PRESETS[gameId]) {
        applyGamePreset(gameId);
        populateGamePresetGrid();
      }
    });
  }

  // Sync teach game-id input changes. Previously this ignored anything
  // that wasn't a built-in preset, which left selectedGameId/train-game-id
  // stuck on the prior game for custom titles -- the core of issue #70.
  // Now ANY game id is normalized + applied so the whole UI (and the
  // dataset folder it later scans) follows the custom game.
  const teachGameInput = getEl("teach-game-id");
  if (teachGameInput) {
    teachGameInput.addEventListener("change", () => {
      const gameId = normalizeCustomGameId(teachGameInput.value);
      applyGamePreset(gameId);
      populateGamePresetGrid();
      loadCatalog(gameId);
      refreshDatasetListTauri(undefined, gameId);
    });
  }
});
