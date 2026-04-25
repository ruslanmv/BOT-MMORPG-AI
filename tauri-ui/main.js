// tauri-ui/main.js
// ------------------------------------------------------------
// BOT-MMORPG-AI (Tauri UI) - UPDATED v0.1.9
// - Fixed Settings: Loads/Saves API Keys correctly via Rust
// - Adds ModelHub commands wiring
// - Adds AI Chat wiring
// ------------------------------------------------------------

// State & Tauri Globals
const invoke = window.__TAURI__ ? window.__TAURI__.invoke : null;
const listen = window.__TAURI__ ? window.__TAURI__.event.listen : null;

// Global State
let isRecording = false;
let isBotRunning = false;

// ModelHub UI State
const DEFAULT_GAME_ID = "genshin_impact";
let modelhubAvailable = false;
let selectedGameId = DEFAULT_GAME_ID;
let selectedDatasetId = "";
let selectedBuiltinModelPath = "";
let selectedModelRegistryId = "";
let selectedLocalModelPath = "";

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
    teach: "Teach Mode (Data Collection)",
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
};

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
    architecture: "mobilenetv3",
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
  { id: "mobilenetv3", name: "MobileNetV3 (Fast)", tier: "modern" },
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

function applyGamePreset(gameId) {
  const preset = GAME_PRESETS[gameId] || GAME_PRESETS.custom;

  // Update resolution selects
  const teachRes = getEl("teach-capture-resolution");
  const runRes = getEl("run-capture-resolution");
  if (teachRes) teachRes.value = preset.resolution;
  if (runRes) runRes.value = preset.resolution;

  // Update resolution hints
  const teachHint = getEl("teach-resolution-hint");
  const runHint = getEl("run-resolution-hint");
  const hintText = `Optimized for ${preset.name}`;
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
    activeGamePill.innerHTML = `${preset.icon} ${preset.name}`;
    activeGamePill.style.color = preset.color;
  }

  // Update game info display if exists
  const gameInfo = getEl("game-preset-info");
  if (gameInfo) {
    gameInfo.innerHTML = `
      <div style="display:flex; gap:12px; align-items:flex-start;">
        <span style="font-size:32px;">${preset.icon}</span>
        <div>
          <strong style="color:${preset.color};">${preset.name}</strong>
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

  logToTerminal(`Applied preset for ${preset.name}: ${preset.resolution}, ${preset.action_space}, ${preset.architecture}`, "success");

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
    const totalModels = (currentCatalog.builtin_models.length || 0) +
                        (currentCatalog.models.length || 0) +
                        (currentCatalog.local_models.length || 0);
    statModels.textContent = totalModels || DEFAULT_ARCHITECTURES.length.toString();
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

  updateDashboardStats();
}

async function setActiveModelFromUI() {
  if (!invoke) return;
  const gid = selectedGameId || DEFAULT_GAME_ID;
  let model_id = "";
  let path = "";

  if (selectedLocalModelPath) {
    model_id = "local";
    path = selectedLocalModelPath;
  } else if (selectedBuiltinModelPath) {
    model_id = "builtin";
    path = selectedBuiltinModelPath;
  } else if (selectedModelRegistryId) {
    model_id = selectedModelRegistryId;
    const found = (currentCatalog.models || []).find((m) => valueForModel(m) === selectedModelRegistryId);
    path = found ? (found.path || "") : "";
    if (!path) path = selectedModelRegistryId;
  }

  if (!path) {
    alert("Select a model (local/builtin/registry) first.");
    return;
  }

  try {
    const res = await invoke("mh_set_active", { game_id: gid, model_id, path });
    logToTerminal(`Active model set: ${path}`, "success");
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
  const monitorId = parseInt(getEl("teach-monitor-select")?.value) || 1;
  const resolution = getEl("teach-capture-resolution")?.value || "480x270";

  if (isRecording) {
    try {
      logToTerminal("Requesting recording start...", "info");
      btn.disabled = true;
      const game_id = (getEl("teach-game-id")?.value || selectedGameId || DEFAULT_GAME_ID).trim();
      const dataset_name = (getEl("teach-dataset-name")?.value || "Untitled").trim();

      const captureMouse = getEl("teach-capture-mouse")?.checked ?? false;
      const res = await invoke("start_recording", { game_id, dataset_name, monitor_id: monitorId, resolution, capture_mouse: captureMouse });
      logToTerminal(res, "success");
      btn.innerHTML = "<span>■</span> Stop Recording";
      btn.style.background = "#333";
      if (status) {
        status.innerText = "🔴 Recording... Switch to game window!";
        status.style.color = "#FF5252";
      }
      // Only start live preview if user has it enabled (default: disabled)
      maybeStartLivePreviewTauri("teach");
    } catch (err) {
      logToTerminal(`Error starting recording: ${err}`, "error");
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
      btn.innerHTML = "<span>●</span> Start Recording";
      btn.style.background = "var(--accent)";
      if (status) {
        status.innerText = "✓ Recording saved.";
        status.style.color = "var(--success)";
      }
      // Refresh dataset list after recording
      await refreshDatasetListTauri();
      await loadCatalog(selectedGameId);
    } catch (err) {
      logToTerminal(`Error stopping recording: ${err}`, "error");
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
    logToTerminal("Initializing Neural Network Training...", "info");
    if (btn) btn.disabled = true;
    if (progressBar) progressBar.style.width = "0%";
    if (pctDisplay) pctDisplay.textContent = "0%";

    const game_id = (getEl("train-game-id")?.value || selectedGameId || DEFAULT_GAME_ID).trim();
    const model_name = (getEl("train-model-name")?.value || "New Model").trim();
    const dataset_id = (getEl("train-dataset-id")?.value || selectedDatasetId || "").trim();
    const arch = (getEl("train-arch")?.value || "custom").trim();

    const res = await invoke("start_training", { game_id, model_name, dataset_id, arch });
    logToTerminal(res, "success");
  } catch (err) {
    logToTerminal(`Training failed to start: ${err}`, "error");
    if (btn) btn.disabled = false;
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
window.toggleBot = async function (btn) {
  if (!invoke) return alert("Tauri backend not found.");
  isBotRunning = !isBotRunning;
  const monitorId = parseInt(getEl("run-monitor-select")?.value) || 1;
  const botState = getEl("bot-state");
  const resolution = getEl("run-capture-resolution")?.value || "480x270";

  if (isBotRunning) {
    try {
      logToTerminal("Initializing autonomous bot...", "info");
      btn.disabled = true;
      const res = await invoke("start_bot", { monitor_id: monitorId, resolution });
      logToTerminal(res, "success");
      btn.innerText = "■ STOP BOT";
      btn.style.background = "var(--accent)";
      btn.style.color = "white";
      if (botState) botState.innerText = "RUNNING";
      // Only start live preview if user has it enabled (default: disabled)
      maybeStartLivePreviewTauri("run");
    } catch (err) {
      logToTerminal(`Failed to start bot: ${err}`, "error");
      isBotRunning = false;
    } finally {
      btn.disabled = false;
    }
  } else {
    try {
      stopLivePreviewTauri();
      btn.disabled = true;
      const res = await invoke("stop_process");
      logToTerminal(res, "success");
      btn.innerText = "▶ START BOT";
      btn.style.background = "var(--success)";
      btn.style.color = "black";
      if (botState) botState.innerText = "IDLE";
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
  try {
    const res = await invoke("install_drivers");
    if (res && res.ok) {
      logToTerminal("Driver installer launched.", "success");
      const st = getEl("drivers-status");
      if (st) st.textContent = "Installer launched";
    } else {
      logToTerminal(`Driver install failed: ${JSON.stringify(res)}`, "warning");
    }
  } catch (e) {
    logToTerminal(`Driver install error: ${e}`, "error");
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

  await listen("process_finished", (event) => {
    const msg = typeof event.payload === "string" ? event.payload : JSON.stringify(event.payload);
    logToTerminal(`[System] Process finished: ${msg}`, "info");
    const btn = getEl("btnStartTraining");
    if (btn) btn.disabled = false;
    isRecording = false;
    isBotRunning = false;
  });
}

// ------------------------------------------------------------
// INITIALIZATION + UI WIRING
// ------------------------------------------------------------

document.addEventListener("DOMContentLoaded", async () => {
  logToTerminal("═══════════════════════════════════════", "info");
  logToTerminal("BOT MMORPG AI (Tauri Edition)", "info");
  logToTerminal("Initializing Rust Core...", "info");

  if (invoke) {
    updateBackendStatus("Running", "Rust Backend Active");
    logToTerminal("✓ Tauri Backend Connected", "success");

    await wireBackendEvents();

    // Initial Config Log (just for user confidence)
    invoke("get_ai_config").then((config) => {
      if(config.provider) {
        logToTerminal(`Loaded Config: ${config.provider}`, "info");
      }
    }).catch((err) => logToTerminal(`Config Load Warning: ${err}`, "warning"));

    await refreshModelhubAvailability();

    // Health probe: detect a broken install (the v0.2.0 case where the
    // installer shipped without python-runtime.zip and ML scripts) so the
    // user sees an actionable banner instead of clicking "Start Recording"
    // and getting "Script not found" with no idea what to do about it.
    await checkInstallHealth();
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
    const h = await invoke("install_health");
    const banner   = document.getElementById("install-health-banner");
    const detailEl = document.getElementById("install-health-detail");
    const dismiss  = document.getElementById("install-health-dismiss");
    if (!banner || !detailEl) return;

    if (h.healthy) {
      banner.style.display = "none";
      logToTerminal("Install health: OK", "success");
      return;
    }

    const issues = (h.issues || []).map(s => `• ${s}`).join("<br>");
    detailEl.innerHTML = (h.remediation || "")
      + (issues ? `<br><br><strong>Detected:</strong><br>${issues}` : "");
    banner.style.display = "block";
    logToTerminal(
      "Install health: INCOMPLETE -- " + (h.issues || []).join("; "),
      "error"
    );

    if (dismiss) {
      dismiss.onclick = () => { banner.style.display = "none"; };
    }
  } catch (e) {
    // If the install_health command itself isn't registered we silently
    // skip -- this only happens on legacy app builds that predate the
    // probe being added. The user has bigger problems in that case.
    console.warn("install_health probe failed:", e);
  }
}

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
      selectedDatasetId = dsSel.value || "";
      const t = getEl("train-dataset-id");
      if (t && !t.value) t.value = selectedDatasetId;
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

  // Refresh datasets list button
  const btnRefreshDatasets = getEl("btnRefreshDatasets");
  if (btnRefreshDatasets) btnRefreshDatasets.addEventListener("click", () => refreshDatasetListTauri());

  // Load monitors on startup
  loadMonitorsTauri();
  refreshDatasetListTauri();
}

// ============================================================
// SCREEN PREVIEW & MONITOR SELECTION (Tauri Version)
// ============================================================

let previewIntervalTauri = null;
let selectedMonitorTeach = 1;
let selectedMonitorRun = 1;
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
  const monitorId = parseInt(getEl("teach-monitor-select")?.value) || 1;
  selectedMonitorTeach = monitorId;
  await updatePreviewImageTauri("teach", monitorId);
}

async function refreshRunPreview() {
  const monitorId = parseInt(getEl("run-monitor-select")?.value) || 1;
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

  try {
    const result = await invoke("get_screen_preview", { monitor_id: monitorId });
    if (result && result.ok && result.image) {
      if (imgEl) {
        imgEl.src = "data:image/jpeg;base64," + result.image;
        imgEl.style.display = "block";
      }
      if (placeholder) placeholder.style.display = "none";
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

async function refreshDatasetListTauri() {
  const listEl = getEl("teach-dataset-list");
  if (!listEl) return;

  listEl.innerHTML = '<div style="color:var(--text-dim); font-size:12px;">Loading...</div>';

  if (!invoke) {
    listEl.innerHTML = '<div style="color:var(--text-dim); font-size:12px;">Backend not available</div>';
    return;
  }

  try {
    const gameId = getEl("teach-game-id")?.value || selectedGameId || DEFAULT_GAME_ID;
    const datasets = await invoke("list_datasets", { game_id: gameId });

    if (!datasets || datasets.length === 0) {
      listEl.innerHTML = '<div style="color:var(--text-dim); font-size:12px;">No datasets found. Start recording!</div>';
      return;
    }

    listEl.innerHTML = "";
    datasets.forEach(ds => {
      const item = document.createElement("div");
      item.style.cssText = "display:flex; justify-content:space-between; align-items:center; padding:10px; margin-bottom:8px; background:rgba(255,255,255,0.03); border:1px solid var(--border); border-radius:8px;";
      item.innerHTML = `
        <div>
          <div style="font-weight:600; color:#fff;">${escapeHtml(ds.name || ds.id)}</div>
          <div style="font-size:11px; color:var(--text-dim);">${escapeHtml(ds.created_at || '')} • ${ds.sample_count || '?'} samples</div>
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

  } catch (e) {
    console.warn("Failed to load datasets:", e);
    listEl.innerHTML = '<div style="color:var(--accent); font-size:12px;">Datasets: ' + (currentCatalog.datasets.length || 0) + ' (refresh via ModelHub)</div>';
  }
}

function selectDatasetForTrainingTauri(datasetId) {
  const trainDataset = getEl("train-dataset-id");
  if (trainDataset) trainDataset.value = datasetId;
  selectedDatasetId = datasetId;
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

  // Sync teach game-id input changes
  const teachGameInput = getEl("teach-game-id");
  if (teachGameInput) {
    teachGameInput.addEventListener("change", () => {
      const gameId = teachGameInput.value?.toLowerCase().replace(/\s+/g, '_');
      if (GAME_PRESETS[gameId]) {
        applyGamePreset(gameId);
        populateGamePresetGrid();
      }
    });
  }
});