# Changelog

All notable changes to BOT-MMORPG-AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **[GAMER_GUIDE.md](GAMER_GUIDE.md)**: a short, picture-first guide for
  players (screenshots in `docs/images/guide/`). The README's gamer
  quick start now uses the app's buttons instead of command lines.
- **Install GPU PyTorch (NVIDIA)** in Settings -> System Tools. The app
  ships the CPU build of PyTorch, so an NVIDIA card sat idle and training
  took hours (issue #82). The button installs the CUDA build of the same
  torch/torchvision version from download.pytorch.org (about 3 GB; only
  the NVIDIA driver is needed, no CUDA Toolkit). It picks the CUDA builds
  the installed driver supports, tests each on the card, and retires the
  bundled CPU copy. **Check GPU** shows what PyTorch can use.
  **Repair PyTorch (pip)** goes back to the CPU build. Both refuse to run
  while training, recording or the bot is active.

### Fixed
- Training can be stopped. While a run is in progress, the Train button
  now reads **Stop training**. Before, it was a disabled "Training..."
  with no way to stop, so a slow CPU run could only be waited out.
  Stopping keeps the best model saved so far.
- The Train tab returns to idle when a job ends. The UI waited for a
  `process_finished` event that nothing sent once jobs moved to the
  sidecar, so the button stayed on "Training..." after training finished.
- Long model paths no longer overflow their card in ModelHub.
- The screen preview shows the screen again instead of a broken-image
  icon. Capture worked, but the app's Content Security Policy had no
  `img-src`, so the WebView refused every captured frame. A frame that
  still cannot be shown is now reported in the log.
- Run Bot works right after training. Set Active used to store only the
  model's folder name (`custom_farming_v1`), and the preflight rejected
  it as "Active model directory missing on disk". Trained models now
  carry their full folder path, Set Active stores an absolute path, and
  an already-broken active model is repaired on the next catalog load
  (issue #88).
- Start Bot no longer kills a running training job. The bot preflight
  now explains that training is still running. Stopping a long run that
  already saved a checkpoint offers that model for Set Active, so hours
  of training are not lost. When an NVIDIA GPU is present, the trainer
  says it is running on the CPU and why.
- The bot now replays mouse clicks for models trained with mouse
  recording, so click-to-move games get input (`--no-mouse` to disable;
  issue #88).
- The runtime doctor no longer warns about a missing
  `libomp140.x86_64.dll` when torch loads fine, and "Repair PyTorch via
  pip" now retires the bundled torch it used to leave shadowing the
  repaired copy, so the "2 torch trees" warning goes away (issue #87).
- The sidecar no longer fails with `No module named 'uvicorn'` after a
  pip-based runtime repair. The backend now adds both
  `<prefix>\site-packages` (the build's install target) and
  `<prefix>\Lib\site-packages` (where `pip install` repairs land) to its
  path, so packages reinstalled by "Repair PyTorch via pip" are actually
  importable instead of sitting in a directory the sidecar never looked
  at. Note: a torch broken by antivirus quarantine is a separate axis —
  add the AV exclusion first, then repair (issue #85).
- The sidecar starts on Python 3.9 again. One route annotation used the
  3.10+ `Dict[str, Any] | None` spelling; FastAPI evaluates route
  annotations at registration time, so `create_app()` itself raised
  `TypeError: Unable to evaluate type annotation` and the whole backend
  failed to come up — not just that endpoint. `pyproject` declares
  `>=3.8` and CI covers 3.9, so route signatures now stay on the
  `typing` spellings, guarded by a test that parses them.
- Running a bot trained with mouse recording no longer fails with
  `size mismatch for action_head.3.weight ... torch.Size([39, 256]) ...
  torch.Size([29, 256])`. `load_model()` now takes the output-head width
  from the checkpoint — its `num_actions` metadata, or inferred from the
  stored weights for checkpoints saved by earlier builds — instead of
  always rebuilding the 29-action default, `save_model()` records the
  width, and `3-test_model.py` sizes its action-weight table from the
  loaded model (issue #82).
- The screen preview works again. The Rust shell has always forwarded
  Preview to `POST /capture/preview`, but the Python sidecar never
  defined that route, so every request 404'd and both preview panes
  stayed on "No Preview yet" with nothing in the log. The sidecar now
  serves `/capture/preview` and `/capture/monitors`, and the UI reports a
  failed capture instead of silently staying blank (issues #57, #81).
- Screen capture is correct on 4K and other scaled displays. The capture
  module now declares per-monitor DPI awareness at import, so Windows
  reports real physical pixels instead of a virtualized desktop —
  lowering the display resolution never helped because scaling, not
  resolution, triggered the virtualization. Capture also tolerates
  padded GDI scanlines and falls back to `mss` when a BitBlt comes back
  blank or fails (issues #81, #8).
- Training on the GPU no longer dies with a CUDA out-of-memory dump at
  the default batch size. The shipped trainer
  (`versions/0.01/2-train_model.py`) now fits the batch size to the
  detected VRAM, enables mixed precision (which also removes the
  "GPU slower than CPU" result) and gradient checkpointing on small
  cards, and skips an out-of-memory batch instead of aborting the run.
  `--no-autotune` keeps a hand-picked `--batch-size` (issue #27).
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
