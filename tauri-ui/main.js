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
  refreshRunBotGate();
}

// Mirror the Rust-side gate for start_bot. 3-test_model.py declares
// --model as required; start_bot in main.rs refuses to spawn without
// an active model. Reflect that prerequisite in the UI so the user
// sees the block before the click rather than as a runtime error.
function refreshRunBotGate() {
  const card  = document.getElementById('run-bot-card');
  const badge = document.getElementById('run-bot-state-badge');
  const hint  = document.getElementById('run-bot-hint');
  const btn   = document.getElementById('btnStartBot');
  if (!card || !badge || !btn) return;

  const active = currentCatalog?.active;
  const hasActive = !!(active && (active.model_dir || active.path));

  if (hasActive) {
    card.dataset.state = 'ready';
    badge.className = 'diag-verdict ready';
    badge.textContent = '● Ready';
    btn.disabled = false;
    btn.style.opacity = '';
    btn.style.cursor = '';
    if (hint) {
      const name = active.name || active.model_id || active.model_dir || '(unnamed)';
      hint.innerHTML = `Active model: <b>${String(name).replace(/[<>&]/g, '')}</b>`;
    }
  } else {
    card.dataset.state = 'no-model';
    badge.className = 'diag-verdict warning';
    badge.textContent = '● No active model';
    btn.disabled = true;
    btn.style.opacity = '0.55';
    btn.style.cursor = 'not-allowed';
    if (hint) {
      hint.innerHTML =
        'No active model set. Open <b>ModelHub</b>, pick a trained model, ' +
        'click <b>Set Active</b>, then come back here to start the bot.';
    }
  }
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
      btn.innerHTML = "<span>●</span> Start Recording";
      btn.style.background = "var(--accent)";
      if (status) {
        status.innerText = "✓ Recording saved.";
        status.style.color = "var(--success)";
      }
      window.notifySuccess?.("Recording saved", "Dataset is ready for training.");
      // Refresh dataset list after recording
      await refreshDatasetListTauri();
      await loadCatalog(selectedGameId);
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
    window.notifyInfo?.("Training started", `${model_name} • ${arch} on dataset ${dataset_id || "(default)"}`);
  } catch (err) {
    logToTerminal(`Training failed to start: ${err}`, "error");
    window.notifyError?.("Training failed to start", String(err), [
      { label: "Run Diagnosis", onClick: () => {
        window.openSettings?.(); window.switchSettingsTab?.('system-tools');
        document.getElementById('btn-run-diagnosis')?.click();
      }},
    ]);
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
      // start_bot now requires game_id so the Rust side can resolve the
      // active model from /modelhub/catalog?game_id=... If the user
      // hasn't picked a model the Rust command returns a clear error
      // and we surface it as a toast instead of opening a doomed
      // subprocess that would die on argparse.
      const game_id = selectedGameId || DEFAULT_GAME_ID;
      const res = await invoke("start_bot", { game_id, monitor_id: monitorId, resolution });
      logToTerminal(res, "success");
      btn.innerText = "■ STOP BOT";
      btn.style.background = "var(--accent)";
      btn.style.color = "white";
      if (botState) botState.innerText = "RUNNING";
      // Only start live preview if user has it enabled (default: disabled)
      maybeStartLivePreviewTauri("run");
    } catch (err) {
      logToTerminal(`Failed to start bot: ${err}`, "error");
      window.notifyError?.("Cannot start bot", String(err), [
        { label: "Open ModelHub", primary: true,
          onClick: () => window.showTab && window.showTab('models') },
      ]);
      isBotRunning = false;
    } finally {
      btn.disabled = false;
      refreshRunBotGate();
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
    const h = await invoke("install_health");

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
          "The app can't write to its install directory. Two safe fixes:" +
          "<ul style='margin-top:6px;'>" +
            "<li>Right-click the app shortcut → <b>Run as administrator</b>.</li>" +
            "<li>Or reinstall to a user-writable location " +
              "(e.g. <code>%LOCALAPPDATA%\\BOT-MMORPG-AI</code>).</li>" +
          "</ul>";
      } else {
        title = "Backend installation is incomplete";
        remediation =
          h.remediation ||
          "Reinstall the latest installer to restore the missing components.";
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

    const lines = itemsToShow
      .map(c => {
        const label = (c.label || c.id || "").toString();
        const msg = (c.message || "").toString();
        const safe = s => s.replace(/[<>&]/g, ch => ({"<":"&lt;",">":"&gt;","&":"&amp;"})[ch]);
        return `<li><strong>${safe(label)}</strong>${msg ? ` — <span style="opacity:.85">${safe(msg)}</span>` : ""}</li>`;
      })
      .join("");

    detailEl.innerHTML =
      remediation + (lines ? `<br><br><strong>Detected:</strong><ul>${lines}</ul>` : "");

    banner.hidden = false;
    logToTerminal(
      `Install health: ${verdict.toUpperCase()} -- ` + (h.issues || []).join("; "),
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