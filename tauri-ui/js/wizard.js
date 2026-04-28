/**
 * Setup Wizard Component
 * Zero-to-Hero setup wizard for MMORPG AI Training School
 */

class SetupWizard {
  constructor() {
    this.currentStep = 0;
    // Simplified: 4 steps instead of 6
    this.steps = [
      'welcome',  // Combined welcome + game selection
      'task',     // Task selection
      'config',   // Model + hardware summary
      'ready'     // Final review + next steps
    ];

    this.state = {
      hardware: null,
      game: null,
      gameName: null,
      task: null,
      taskInfo: null,
      model: null,
      modelRecommendation: null,
      config: {}
    };

    this.onComplete = null;
  }

  async start() {
    this.currentStep = 0;
    await this.detectHardware();
    this.render();
  }

  async detectHardware() {
    try {
      if (window.__TAURI__?.invoke) {
        // Try to get hardware info from backend
        const info = await window.__TAURI__.invoke('config_get_hardware');
        this.state.hardware = info;
      } else {
        // Fallback detection
        this.state.hardware = {
          tier: 'medium',
          gpu_name: 'Unknown GPU',
          gpu_vram_mb: 8192,
          cpu_cores: navigator.hardwareConcurrency || 4,
          ram_mb: 8192,
          cuda_available: false,
          summary: 'Hardware detection limited in browser mode'
        };
      }
    } catch (e) {
      console.warn('Hardware detection failed:', e);
      this.state.hardware = {
        tier: 'medium',
        gpu_name: 'Detection failed',
        summary: 'Using default medium tier settings'
      };
    }
  }

  render() {
    const step = this.steps[this.currentStep];
    const container = document.getElementById('wizard-content');
    if (!container) return;

    switch (step) {
      case 'welcome':
        this.renderWelcomeStep(container);
        break;
      case 'task':
        this.renderTaskStep(container);
        break;
      case 'config':
        this.renderConfigStep(container);
        break;
      case 'ready':
        this.renderReadyStep(container);
        break;
    }

    this.updateProgress();
  }

  updateProgress() {
    const progressSteps = document.querySelectorAll('.wizard-progress-step');
    progressSteps.forEach((el, i) => {
      el.classList.remove('completed', 'active');
      if (i < this.currentStep) {
        el.classList.add('completed');
      } else if (i === this.currentStep) {
        el.classList.add('active');
      }
    });

    const indicator = document.getElementById('wizard-step-indicator');
    if (indicator) {
      indicator.textContent = `Step ${this.currentStep + 1} of ${this.steps.length}`;
    }
  }

  // Combined welcome + game selection (Step 1)
  renderWelcomeStep(container) {
    const games = [
      { id: 'genshin_impact', name: 'Genshin Impact', icon: '🌟' },
      { id: 'world_of_warcraft', name: 'World of Warcraft', icon: '⚔️' },
      { id: 'guild_wars_2', name: 'Guild Wars 2', icon: '🛡️' },
      { id: 'lost_ark', name: 'Lost Ark', icon: '💎' },
      { id: 'final_fantasy_xiv', name: 'Final Fantasy XIV', icon: '✨' }
    ];

    // Auto-select Genshin Impact
    if (!this.state.game) {
      this.state.game = games[0].id;
      this.state.gameName = games[0].name;
    }

    const hw = this.state.hardware;
    const tierBadge = hw?.tier === 'high' ? '🚀 High-End' : hw?.tier === 'low' ? '💡 Lite' : '⚡ Standard';

    container.innerHTML = `
      <div class="wizard-step-content" style="text-align: center;">
        <div style="font-size: 64px; margin-bottom: 15px;">🎮</div>
        <h2 style="margin-bottom: 8px;">Let's Get Started!</h2>
        <p style="color: var(--text-dim); margin-bottom: 30px;">
          Select your game and we'll configure everything automatically.
        </p>

        <div style="display: inline-block; background: var(--bg-dark); padding: 8px 16px; border-radius: 20px; margin-bottom: 25px; font-size: 13px;">
          Hardware: <span style="color: var(--secondary); font-weight: 600;">${tierBadge}</span>
          ${hw?.cuda_available ? ' • <span style="color: var(--success);">CUDA Ready</span>' : ''}
        </div>

        <div class="game-grid" style="max-width: 600px; margin: 0 auto;">
          ${games.map(game => `
            <div class="game-card ${this.state.game === game.id ? 'selected' : ''}"
                 data-game-id="${game.id}" style="padding: 20px;">
              <div class="game-card-icon" style="font-size: 36px;">${game.icon}</div>
              <div class="game-card-name" style="font-size: 14px;">${game.name}</div>
            </div>
          `).join('')}

          <div class="game-card" data-game-id="custom" style="border-style: dashed; padding: 20px;">
            <div class="game-card-icon" style="font-size: 36px;">➕</div>
            <div class="game-card-name" style="font-size: 14px;">Other Game</div>
          </div>
        </div>
      </div>
    `;

    container.querySelectorAll('.game-card').forEach(card => {
      card.addEventListener('click', () => {
        container.querySelectorAll('.game-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        this.state.game = card.dataset.gameId;
        this.state.gameName = card.querySelector('.game-card-name').textContent;
      });
    });
  }

  renderTaskStep(container) {
    const tasks = [
      { id: 'combat', name: 'Combat', icon: '⚔️', temporal: true, description: 'Real-time combat with reaction requirements' },
      { id: 'farming', name: 'Farming', icon: '🌾', temporal: false, description: 'Resource gathering and repetitive tasks' },
      { id: 'navigation', name: 'Navigation', icon: '🗺️', temporal: true, description: 'Pathfinding and movement' },
      { id: 'crafting', name: 'Crafting', icon: '🔨', temporal: false, description: 'Crafting UI interaction' }
    ];

    container.innerHTML = `
      <div class="wizard-step-content">
        <h2 style="margin-bottom: 10px;">Select Your Task</h2>
        <p style="color: var(--text-dim); margin-bottom: 25px;">
          What do you want your AI to learn for ${this.state.gameName || 'your game'}?
        </p>

        <div class="game-grid" style="grid-template-columns: repeat(2, 1fr);">
          ${tasks.map(task => `
            <div class="game-card ${this.state.task === task.id ? 'selected' : ''}"
                 data-task-id="${task.id}" style="text-align: left; padding: 25px;">
              <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
                <div style="font-size: 32px;">${task.icon}</div>
                <div>
                  <div class="game-card-name">${task.name}</div>
                  ${task.temporal ? '<span style="font-size: 10px; color: var(--primary);">TEMPORAL</span>' : ''}
                </div>
              </div>
              <p style="color: var(--text-dim); font-size: 13px;">${task.description}</p>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    container.querySelectorAll('.game-card').forEach(card => {
      card.addEventListener('click', () => {
        container.querySelectorAll('.game-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        this.state.task = card.dataset.taskId;
        this.state.taskInfo = tasks.find(t => t.id === card.dataset.taskId);
      });
    });
  }

  // Combined model recommendation + config (Step 3)
  renderConfigStep(container) {
    const hw = this.state.hardware;
    const task = this.state.taskInfo;

    // Auto-recommend model based on hardware and task
    let recommendation;
    if (hw?.tier === 'high' && task?.temporal) {
      recommendation = {
        architecture: 'efficientnet_lstm',
        name: 'EfficientNet-LSTM',
        badge: 'BEST ACCURACY'
      };
    } else if (hw?.tier === 'low') {
      recommendation = {
        architecture: 'mobilenet_v3',
        name: 'MobileNetV3',
        badge: 'FAST & LIGHT'
      };
    } else {
      recommendation = {
        architecture: 'efficientnet_simple',
        name: 'EfficientNet',
        badge: 'BALANCED'
      };
    }

    this.state.model = recommendation.architecture;
    this.state.modelRecommendation = recommendation;

    container.innerHTML = `
      <div class="wizard-step-content" style="text-align: center;">
        <div style="font-size: 48px; margin-bottom: 15px;">🧠</div>
        <h2 style="margin-bottom: 8px;">AI Configuration</h2>
        <p style="color: var(--text-dim); margin-bottom: 30px;">
          We've selected the best model for your setup.
        </p>

        <div class="recommendation-card" style="max-width: 500px; margin: 0 auto; text-align: left;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
              <div class="recommendation-badge">${recommendation.badge}</div>
              <div style="font-size: 20px; font-weight: 700; margin-top: 8px;">${recommendation.name}</div>
            </div>
            <div style="font-size: 36px;">✨</div>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <div class="metric-card" style="text-align: center; padding: 12px;">
              <div class="metric-label">Game</div>
              <div style="font-weight: 600; color: var(--text-main);">${this.state.gameName}</div>
            </div>
            <div class="metric-card" style="text-align: center; padding: 12px;">
              <div class="metric-label">Task</div>
              <div style="font-weight: 600; color: var(--text-main);">${task?.name || 'General'}</div>
            </div>
            <div class="metric-card" style="text-align: center; padding: 12px;">
              <div class="metric-label">Hardware</div>
              <div style="font-weight: 600; color: var(--secondary);">${(hw?.tier || 'medium').toUpperCase()}</div>
            </div>
            <div class="metric-card" style="text-align: center; padding: 12px;">
              <div class="metric-label">Temporal</div>
              <div style="font-weight: 600; color: ${task?.temporal ? 'var(--success)' : 'var(--text-dim)'};">${task?.temporal ? 'Yes' : 'No'}</div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  // Final ready step (Step 4)
  renderReadyStep(container) {
    container.innerHTML = `
      <div class="wizard-step-content" style="text-align: center;">
        <div style="font-size: 64px; margin-bottom: 15px;">🚀</div>
        <h2 style="margin-bottom: 8px; color: var(--success);">You're All Set!</h2>
        <p style="color: var(--text-dim); margin-bottom: 30px;">
          Configuration saved. Here's what to do next:
        </p>

        <div style="max-width: 500px; margin: 0 auto; text-align: left;">
          <div style="display: flex; gap: 15px; padding: 15px; background: var(--bg-dark); border-radius: 12px; margin-bottom: 12px;">
            <div style="font-size: 28px;">1️⃣</div>
            <div>
              <div style="font-weight: 700; margin-bottom: 4px;">Record Training Data</div>
              <div style="color: var(--text-dim); font-size: 13px;">Go to "Teach" tab and play your game while recording (F9 to start, F10 to stop)</div>
            </div>
          </div>

          <div style="display: flex; gap: 15px; padding: 15px; background: var(--bg-dark); border-radius: 12px; margin-bottom: 12px;">
            <div style="font-size: 28px;">2️⃣</div>
            <div>
              <div style="font-weight: 700; margin-bottom: 4px;">Train Your Model</div>
              <div style="color: var(--text-dim); font-size: 13px;">After collecting 5,000+ samples, go to "Train Brain" to start training</div>
            </div>
          </div>

          <div style="display: flex; gap: 15px; padding: 15px; background: var(--bg-dark); border-radius: 12px;">
            <div style="font-size: 28px;">3️⃣</div>
            <div>
              <div style="font-weight: 700; margin-bottom: 4px;">Run Your Bot</div>
              <div style="color: var(--text-dim); font-size: 13px;">Once trained, go to "Run Bot" to let the AI play!</div>
            </div>
          </div>
        </div>

        <p style="color: var(--secondary); margin-top: 25px; font-weight: 600;">
          Click "Finish" to go to the Teach tab and start recording!
        </p>
      </div>
    `;
  }

  async next() {
    // Validate current step
    if (!this.validateCurrentStep()) return;

    if (this.currentStep < this.steps.length - 1) {
      this.currentStep++;
      this.render();
    } else {
      await this.finish();
    }
  }

  back() {
    if (this.currentStep > 0) {
      this.currentStep--;
      this.render();
    }
  }

  validateCurrentStep() {
    const step = this.steps[this.currentStep];

    switch (step) {
      case 'welcome':
        if (!this.state.game) {
          alert('Please select a game');
          return false;
        }
        break;
      case 'task':
        if (!this.state.task) {
          alert('Please select a task');
          return false;
        }
        break;
    }

    return true;
  }

  async finish() {
    // Save configuration
    this.state.config = {
      game_id: this.state.game,
      game_name: this.state.gameName,
      task: this.state.task,
      task_name: this.state.taskInfo?.name,
      architecture: this.state.model,
      architecture_name: this.state.modelRecommendation?.name,
      hardware_tier: this.state.hardware?.tier || 'medium'
    };

    try {
      if (window.__TAURI__?.invoke) {
        await window.__TAURI__.invoke('config_save_session', { config: this.state.config });
      }
    } catch (e) {
      console.warn('Failed to save config:', e);
    }

    // Save to localStorage for UI persistence
    localStorage.setItem('quickstart_config', JSON.stringify(this.state.config));

    // Auto-populate Teach (Record) tab
    const teachGameId = document.getElementById('teach-game-id');
    if (teachGameId) teachGameId.value = this.state.game;

    const teachDataset = document.getElementById('teach-dataset-name');
    if (teachDataset && !teachDataset.value) {
      teachDataset.value = `${this.state.game}_${this.state.task}_01`;
    }

    // Auto-populate Train tab
    const trainGameId = document.getElementById('train-game-id');
    if (trainGameId) trainGameId.value = this.state.game;

    const trainModelName = document.getElementById('train-model-name');
    if (trainModelName && !trainModelName.value) {
      trainModelName.value = `${this.state.game}_${this.state.task}_v1`;
    }

    const trainArch = document.getElementById('train-arch');
    if (trainArch) {
      trainArch.value = this.state.model || 'custom';
    }

    // Update active game pill
    const activeGamePill = document.getElementById('active-game-pill');
    if (activeGamePill) {
      activeGamePill.textContent = this.state.gameName || this.state.game;
    }

    if (this.onComplete) {
      this.onComplete(this.state.config);
    }

    // Show completion message and navigate to Teach tab
    alert('Setup complete! Go to "Teach (Record)" to start collecting training data.');

    // Navigate to teach tab
    if (window.showTab) {
      window.showTab('teach');
    }
  }
}

// Export for use in main.js
window.SetupWizard = SetupWizard;
