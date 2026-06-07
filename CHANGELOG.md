# Changelog

All notable changes to BOT-MMORPG-AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Recordings no longer disappear from the Train tab: the bundled
  `versions/0.01/1-collect_data.py` now honors the `--out` argument the
  Tauri shell passes, so data lands in `datasets/<game>/<name>/` where
  the dataset scanner looks (issues #57, #60, #63, #65).
- Training no longer crashes with
  `Target size (... 39) must be the same as input size (... 29)` when
  mouse recording is enabled. `2-train_model.py` now auto-detects the
  output-head size from the dataset's action vector (29 without mouse,
  39 with), and `--num-actions` defaults to `0` (auto) (issue #64).
- Windows installer build no longer fails with
  `Cannot open include file: 'Python.h'` / `Failed building wheel for
  gevent`. The embeddable-Python wheelhouse builders now provision the
  CPython headers + import library from the host interpreter so
  dependencies that lack a prebuilt `cp310`/`cp311` wheel can compile.

## [1.0.0] - 2026-02-09

### Added
- Tauri desktop application with NSIS Windows installer
- Python ML backend with PyTorch neural network models
- ModelHub: local model catalog, discovery, and session management
- Setup Wizard for guided first-run configuration
- AI Chat integration (Gemini, OpenAI, Ollama)
- Game profiles for Genshin Impact, WoW, FFXIV, Lost Ark, GW2
- Hardware-aware model selection and resolution recommendations
- Training School UI for data collection, training, and inference
- Screen capture with multi-monitor support
- Gamepad input simulation (vJoy, Interception drivers)
- CI/CD with GitHub Actions (test, lint, build, release)
- 120 automated tests covering config, models, bridge, and UI

### Fixed
- NSIS template resource bundling (Handlebars `{{this}}` vs `{{@key}}`)
- CI workflow downloads vJoySetup.exe from official release
- `.gitignore` whitelists Tauri config JSON and driver executables
- Git repository size reduced from 1.6 GB to 95 MB

### Security
- Tauri filesystem permissions restricted to granular read/write/dir ops
- CI lint and security checks now block on failure
- Secure data loader with SHA-256 hash verification for model files
