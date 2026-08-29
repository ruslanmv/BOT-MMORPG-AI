"""
Regression tests for GitHub issues #8, #27, #57, #81 and #82.

Each test pins a defect a user actually reported, so a future refactor
that reintroduces it fails here rather than in someone's living room.

  #82  "torch.size error"
       Training with mouse recording on produces a 39-wide action vector
       (keyboard 9 + gamepad 20 + mouse 10), but `load_model` always
       rebuilt the architecture with the 29-action default, so "Run Bot"
       died before the first frame with
       "size mismatch for action_head.3.weight: copying a param with
       shape torch.Size([39, 256]) ... current model is
       torch.Size([29, 256])".

  #81  "screen capture wont capture my screen" (4K display)
  #57  "Screen preview not working -- only 'No Preview yet'"
       Two independent causes:
         - The Rust shell forwards Preview to POST /capture/preview, a
           route the Python sidecar never defined. Every request 404'd
           and the UI silently stayed on its empty state.
         - A process that has not declared DPI awareness gets a
           virtualized desktop from Win32: on a scaled 4K monitor the
           screen metrics and the BitBlt result disagree with the real
           pixels, which is why lowering the resolution changed nothing.

  #27  "Training issues" -- CUDA OOM at the default batch size, and
       GPU training measured slower than CPU. The shipped trainer
       (versions/0.01/2-train_model.py, what the desktop app runs) had
       none of the VRAM-aware batch sizing, mixed precision or OOM
       recovery that the modern script grew.

  #8   2K/QHD capture support, verified through the resolution presets.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
VERSIONS = ROOT / "versions" / "0.01"

TORCH_MISSING = importlib.util.find_spec("torch") is None
NUMPY_MISSING = importlib.util.find_spec("numpy") is None
CV2_MISSING = importlib.util.find_spec("cv2") is None
FASTAPI_MISSING = importlib.util.find_spec("fastapi") is None

requires_torch = pytest.mark.skipif(TORCH_MISSING, reason="PyTorch required")
requires_numpy = pytest.mark.skipif(NUMPY_MISSING, reason="numpy required")
requires_cv2 = pytest.mark.skipif(CV2_MISSING, reason="opencv required")


def _load_versioned(module_name: str, filename: str):
    """Import one of the hyphen-named scripts under versions/0.01/."""
    for path in (str(VERSIONS), str(SRC)):
        if path not in sys.path:
            sys.path.insert(0, path)
    spec = importlib.util.spec_from_file_location(module_name, VERSIONS / filename)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _models_pytorch():
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    from bot_mmorpg.scripts import models_pytorch

    return models_pytorch


# =====================================================================
# #82 -- the checkpoint decides the output width, not the caller
# =====================================================================


@requires_torch
def test_save_model_records_the_action_count(tmp_path):
    """A checkpoint must carry the width it was trained with."""
    import torch

    mp = _models_pytorch()
    model = mp.get_model("mobilenet_v3", num_actions=39, pretrained=False)
    path = tmp_path / "m.pth"
    mp.save_model(model, str(path), model_name="MobileNetV3Model")

    ckpt = torch.load(str(path), map_location="cpu", weights_only=False)
    assert ckpt["num_actions"] == 39


@requires_torch
def test_load_model_honours_mouse_enabled_checkpoint(tmp_path):
    """The exact failure from #82: 39-output model, 29-action default."""
    import torch

    mp = _models_pytorch()
    trained = mp.get_model("efficientnet_lstm", num_actions=39, pretrained=False)
    path = tmp_path / "efficientnet_lstm_best.pth"
    mp.save_model(trained, str(path), model_name="EfficientNetLSTM", temporal_frames=4)

    # num_actions is left at its 29 default, as every caller does.
    model, metadata = mp.load_model(str(path), device=torch.device("cpu"))

    assert model.action_head[-1].out_features == 39
    assert metadata["num_actions"] == 39


@requires_torch
def test_load_model_infers_width_from_legacy_checkpoint(tmp_path):
    """Checkpoints trained before save_model recorded num_actions."""
    import torch

    mp = _models_pytorch()
    trained = mp.get_model("efficientnet_lstm", num_actions=39, pretrained=False)
    # A pre-fix checkpoint: architecture name, no num_actions key.
    torch.save(
        {
            "model_state_dict": trained.state_dict(),
            "model_name": "EfficientNetLSTM",
            "temporal_frames": 4,
        },
        str(tmp_path / "legacy.pth"),
    )

    model, metadata = mp.load_model(
        str(tmp_path / "legacy.pth"), device=torch.device("cpu")
    )

    assert model.action_head[-1].out_features == 39
    assert metadata["num_actions"] == 39


@requires_torch
def test_load_model_infers_width_from_bare_state_dict(tmp_path):
    """torch.save(model.state_dict()) with no metadata at all."""
    import torch

    mp = _models_pytorch()
    trained = mp.get_model("mobilenet_v3", num_actions=35, pretrained=False)
    torch.save(trained.state_dict(), str(tmp_path / "bare.pth"))

    model, metadata = mp.load_model(
        str(tmp_path / "bare.pth"),
        model_name="mobilenet_v3",
        device=torch.device("cpu"),
    )

    assert metadata["num_actions"] == 35
    assert model.num_actions == 35


@requires_torch
@pytest.mark.parametrize(
    "arch",
    [
        "efficientnet_lstm",
        "efficientnet_simple",
        "mobilenet_v3",
        "resnet18_lstm",
        "inception_v3",
        "alexnet",
        "sentnet_2d",
    ],
)
def test_every_architecture_round_trips_a_wide_head(tmp_path, arch):
    """Mouse-enabled training must load back on any architecture."""
    import torch

    mp = _models_pytorch()
    trained = mp.get_model(arch, num_actions=39, pretrained=False)
    path = tmp_path / f"{arch}.pth"
    mp.save_model(trained, str(path), model_name=arch)

    model, metadata = mp.load_model(str(path), device=torch.device("cpu"))
    assert metadata["num_actions"] == 39
    assert getattr(model, "num_actions", None) == 39


@requires_torch
def test_plain_29_action_checkpoints_are_unaffected(tmp_path):
    """The common no-mouse case must not change behaviour."""
    import torch

    mp = _models_pytorch()
    trained = mp.get_model("mobilenet_v3", num_actions=29, pretrained=False)
    path = tmp_path / "m29.pth"
    mp.save_model(trained, str(path), model_name="MobileNetV3Model")

    model, metadata = mp.load_model(str(path), device=torch.device("cpu"))
    assert metadata["num_actions"] == 29
    assert model.num_actions == 29


@requires_torch
def test_infer_num_actions_declines_when_the_vote_is_split():
    """Guessing is worse than the explicit size-mismatch error."""
    import torch

    mp = _models_pytorch()
    reference = mp.get_model("mobilenet_v3", num_actions=29, pretrained=False)

    state = {}
    seen_head = False
    for key, tensor in reference.state_dict().items():
        if tensor.ndim >= 1 and tensor.shape[0] == 29:
            # Contradictory widths for two head tensors.
            width = 39 if not seen_head else 41
            seen_head = True
            state[key] = torch.zeros((width, *tensor.shape[1:]))
        else:
            state[key] = tensor

    assert mp.infer_num_actions(state, reference) is None


@requires_torch
def test_versioned_models_pytorch_carries_the_same_fix():
    """versions/0.01 is what the packaged app imports -- keep it in sync."""
    src_text = (SRC / "bot_mmorpg" / "scripts" / "models_pytorch.py").read_text()
    versioned_text = (VERSIONS / "models_pytorch.py").read_text()
    assert "def infer_num_actions" in versioned_text
    assert src_text == versioned_text, (
        "versions/0.01/models_pytorch.py has drifted from the src copy; "
        "the packaged app would keep the old behaviour."
    )


@requires_numpy
@requires_cv2
def test_action_weights_match_the_model_output_width():
    """39 predictions * 29 weights used to raise a broadcast error."""
    mod = _load_versioned("issue82_test_model", "3-test_model.py")

    assert mod.build_action_weights(29).shape == (29,)
    assert mod.build_action_weights(39).shape == (39,)
    assert mod.build_action_weights(35).shape == (35,)
    # Legacy 6-value mouse block is recognised too.
    assert mod.build_action_weights(35)[-4:].tolist() == [1.0, 1.0, 0.8, 0.3]
    # The base 29 weights are untouched by the mouse block.
    assert mod.build_action_weights(39)[:29].tolist() == (
        mod.build_action_weights(29).tolist()
    )


@requires_torch
@requires_numpy
@requires_cv2
def test_inference_engine_runs_a_mouse_enabled_model(tmp_path):
    """End-to-end #82: train with mouse on, then Run Bot."""
    import numpy as np
    import torch

    mp = _models_pytorch()
    trained = mp.get_model("mobilenet_v3", num_actions=39, pretrained=False)
    path = tmp_path / "mobilenet_v3_best.pth"
    mp.save_model(trained, str(path), model_name="MobileNetV3Model")

    mod = _load_versioned("issue82_engine", "3-test_model.py")
    engine = mod.InferenceEngine(
        str(path), device=torch.device("cpu"), enable_gamepad=False
    )

    assert engine.num_actions == 39
    assert engine.has_mouse_output is True

    frame = np.zeros((2160, 3840, 3), dtype=np.uint8)  # a 4K grab
    action_idx, _value, predictions = engine.predict(frame)

    assert predictions.shape == (39,)
    # Mouse slots are continuous outputs and must never win the argmax.
    assert 0 <= action_idx < 29


# =====================================================================
# #81 / #57 -- screen capture and the missing preview endpoint
# =====================================================================


def _grabscreen():
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    from bot_mmorpg.scripts import grabscreen

    return grabscreen


@requires_numpy
@requires_cv2
def test_dpi_awareness_is_declared_at_import():
    """The capture module must opt into physical pixels before first use."""
    gs = _grabscreen()
    assert hasattr(gs, "enable_dpi_awareness")
    # Off Windows this is a no-op that must not raise.
    assert gs.enable_dpi_awareness() in (True, False)


@requires_numpy
@requires_cv2
def test_blank_frame_detection():
    """An all-black GDI frame is what a protected/fullscreen game returns."""
    import numpy as np

    gs = _grabscreen()
    assert gs._is_blank(np.zeros((16, 16, 3), dtype=np.uint8)) is True
    assert gs._is_blank(np.ones((16, 16, 3), dtype=np.uint8)) is False
    assert gs._is_blank(None) is True


@requires_numpy
@requires_cv2
def test_grab_screen_falls_back_to_mss_on_a_blank_win32_frame(monkeypatch):
    """A black BitBlt must not become a black recording."""
    import numpy as np

    gs = _grabscreen()
    real = np.full((8, 8, 3), 7, dtype=np.uint8)

    monkeypatch.setattr(gs, "IS_WINDOWS", True)
    monkeypatch.setattr(gs, "_WIN32_AVAILABLE", True)
    monkeypatch.setattr(gs, "_MSS_AVAILABLE", True)
    monkeypatch.setattr(
        gs, "_grab_screen_win32", lambda region=None: np.zeros((8, 8, 3), np.uint8)
    )
    monkeypatch.setattr(gs, "_grab_screen_mss", lambda region=None: real)

    assert gs.grab_screen().tolist() == real.tolist()


@requires_numpy
@requires_cv2
def test_grab_screen_falls_back_to_mss_when_win32_raises(monkeypatch):
    """A GDI error is recoverable while mss can still read the screen."""
    import numpy as np

    gs = _grabscreen()
    real = np.full((8, 8, 3), 3, dtype=np.uint8)

    def _boom(region=None):
        raise RuntimeError("cannot reshape array of size 4147200")

    monkeypatch.setattr(gs, "IS_WINDOWS", True)
    monkeypatch.setattr(gs, "_WIN32_AVAILABLE", True)
    monkeypatch.setattr(gs, "_MSS_AVAILABLE", True)
    monkeypatch.setattr(gs, "_grab_screen_win32", _boom)
    monkeypatch.setattr(gs, "_grab_screen_mss", lambda region=None: real)

    assert gs.grab_screen().tolist() == real.tolist()


@requires_numpy
@requires_cv2
def test_win32_failure_still_raises_without_a_fallback(monkeypatch):
    """Silently returning nothing would be worse than an error."""
    gs = _grabscreen()

    def _boom(region=None):
        raise RuntimeError("GDI died")

    monkeypatch.setattr(gs, "IS_WINDOWS", True)
    monkeypatch.setattr(gs, "_WIN32_AVAILABLE", True)
    monkeypatch.setattr(gs, "_MSS_AVAILABLE", False)
    monkeypatch.setattr(gs, "_grab_screen_win32", _boom)

    with pytest.raises(RuntimeError):
        gs.grab_screen()


@requires_numpy
@requires_cv2
def test_thumbnail_downscales_4k_without_upscaling_small_frames(monkeypatch):
    """Preview thumbnails of a 4K desktop, and no degenerate sizes."""
    import numpy as np

    gs = _grabscreen()

    monkeypatch.setattr(
        gs,
        "grab_screen_monitor",
        lambda monitor_id=1: np.zeros((2160, 3840, 3), dtype=np.uint8),
    )
    thumb = gs.grab_screen_thumbnail(1, 320, 180)
    assert thumb.shape[0] <= 180 and thumb.shape[1] <= 320
    assert thumb.shape[0] >= 1 and thumb.shape[1] >= 1

    # A frame already smaller than the box must not be blown up.
    monkeypatch.setattr(
        gs,
        "grab_screen_monitor",
        lambda monitor_id=1: np.zeros((90, 160, 3), dtype=np.uint8),
    )
    assert gs.grab_screen_thumbnail(1, 320, 180).shape[:2] == (90, 160)


@requires_numpy
@requires_cv2
def test_versioned_grabscreen_carries_the_same_fix():
    """versions/0.01/grabscreen.py is what the recorder imports."""
    src_text = (SRC / "bot_mmorpg" / "scripts" / "grabscreen.py").read_text()
    versioned_text = (VERSIONS / "grabscreen.py").read_text()
    assert "def enable_dpi_awareness" in versioned_text
    assert src_text == versioned_text


def test_capture_module_resolves_in_a_shipped_install(tmp_path, monkeypatch):
    """The installer bundles versions/0.01/*.py but no src/ tree at all.

    If the resolver only knew the src-layout package, the preview would
    keep failing on exactly the installs issue #81 came from.
    """
    import shutil

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from modelhub import tauri as sidecar

    bundled_dir = tmp_path / "versions" / sidecar.DEFAULT_VERSION
    bundled_dir.mkdir(parents=True)
    shutil.copy(VERSIONS / "grabscreen.py", bundled_dir / "grabscreen.py")

    monkeypatch.setattr(sidecar, "RESOURCE_ROOT", tmp_path)
    monkeypatch.setattr(sidecar, "repo_root", tmp_path)
    # Hide the installed/src-layout package so only the bundle can win.
    monkeypatch.setattr(sys, "path", [p for p in sys.path if not p.endswith("src")])
    monkeypatch.delitem(sys.modules, "bot_mmorpg", raising=False)
    monkeypatch.delitem(sys.modules, "bot_mmorpg.scripts", raising=False)
    monkeypatch.delitem(sys.modules, "bot_mmorpg.scripts.grabscreen", raising=False)

    module = sidecar._import_grabscreen()
    assert hasattr(module, "list_monitors")
    assert hasattr(module, "grab_screen_base64")


@pytest.mark.skipif(FASTAPI_MISSING, reason="fastapi required")
def test_sidecar_serves_the_capture_endpoints_the_shell_calls(monkeypatch):
    """POST /capture/preview 404'd -- the preview pane could never fill."""
    from fastapi.testclient import TestClient

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from modelhub import tauri as sidecar

    stub = types.SimpleNamespace(
        list_monitors=lambda: [
            {
                "id": 1,
                "name": "Monitor 1 (3840x2160)",
                "width": 3840,
                "height": 2160,
                "left": 0,
                "top": 0,
            }
        ],
        grab_screen_base64=lambda mid, w, h, q: f"IMG:{mid}:{w}x{h}:{q}",
    )
    monkeypatch.setattr(sidecar, "_import_grabscreen", lambda: stub)

    client = TestClient(sidecar.create_app("tkn"))
    headers = {"X-Auth-Token": "tkn"}

    monitors = client.get("/capture/monitors", headers=headers)
    assert monitors.status_code == 200
    assert monitors.json()["monitors"][0]["width"] == 3840

    preview = client.post("/capture/preview", json={"monitor_id": 0}, headers=headers)
    assert preview.status_code == 200
    body = preview.json()
    assert body["ok"] is True
    # monitor_id 0 from the shell means "primary" -> mss monitor 1.
    assert body["monitor_id"] == 1
    assert body["image"] == "IMG:1:640x360:70"


@pytest.mark.skipif(FASTAPI_MISSING, reason="fastapi required")
def test_capture_endpoints_require_the_auth_token():
    from fastapi.testclient import TestClient

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from modelhub import tauri as sidecar

    client = TestClient(sidecar.create_app("tkn"))
    assert client.get("/capture/monitors").status_code == 401
    assert client.post("/capture/preview", json={}).status_code == 401


@pytest.mark.skipif(FASTAPI_MISSING, reason="fastapi required")
def test_capture_preview_reports_missing_dependencies(monkeypatch):
    """A structured error beats a 500 the UI cannot explain."""
    from fastapi.testclient import TestClient

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from modelhub import tauri as sidecar

    def _no_capture():
        raise ImportError("no grabscreen here")

    monkeypatch.setattr(sidecar, "_import_grabscreen", _no_capture)

    client = TestClient(sidecar.create_app("tkn"))
    body = client.post(
        "/capture/preview", json={}, headers={"X-Auth-Token": "tkn"}
    ).json()

    assert body["ok"] is False
    assert "hint" in body


def test_ui_reports_a_failed_preview_instead_of_staying_blank():
    """'No Preview yet' with an empty log is indistinguishable from idle."""
    js = (ROOT / "tauri-ui" / "main.js").read_text()
    assert "Screen preview failed: " in js
    assert "_lastPreviewError" in js


# =====================================================================
# #8 -- 2K/QHD capture presets
# =====================================================================


def test_two_k_resolution_is_offered_to_the_ui():
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    from bot_mmorpg.config.game_resolutions import (
        get_resolution_for_model,
        get_resolution_options_for_ui,
    )

    values = [opt["value"] for opt in get_resolution_options_for_ui()]
    assert "2560x1440" in values
    assert "1920x1080" in values

    # A native 4K desktop is capped to a trainable size, not rejected.
    assert get_resolution_for_model("native", 3840, 2160) == (2560, 1440)


# =====================================================================
# #27 -- VRAM-aware batch sizing in the trainer the app actually runs
# =====================================================================


@requires_torch
@requires_numpy
@requires_cv2
@pytest.mark.parametrize(
    "vram_gb,requested,expected_bs,expected_amp,expected_ckpt",
    [
        (6.0, 16, 4, True, True),
        (8.0, 16, 8, True, True),
        (12.0, 32, 16, True, False),
        (24.0, 16, 16, True, False),
    ],
)
def test_batch_size_is_fitted_to_the_gpu(
    monkeypatch, vram_gb, requested, expected_bs, expected_amp, expected_ckpt
):
    import torch

    trainer = _load_versioned("issue27_trainer", "2-train_model.py")
    monkeypatch.setattr(trainer, "_safe_total_vram_gb", lambda: vram_gb)

    batch, amp, ckpt = trainer.autotune_batch_size(requested, torch.device("cuda"))
    assert (batch, amp, ckpt) == (expected_bs, expected_amp, expected_ckpt)


@requires_torch
@requires_numpy
@requires_cv2
def test_unreadable_vram_falls_back_to_the_safest_tier(monkeypatch):
    """A CUDA build we cannot query must not crash the run (#59 + #27)."""
    import torch

    trainer = _load_versioned("issue27_trainer_vram", "2-train_model.py")
    monkeypatch.setattr(trainer, "_safe_total_vram_gb", lambda: None)

    batch, amp, ckpt = trainer.autotune_batch_size(16, torch.device("cuda"))
    assert (batch, amp, ckpt) == (4, True, True)


@requires_torch
@requires_numpy
@requires_cv2
def test_cpu_training_is_left_alone(monkeypatch):
    import torch

    trainer = _load_versioned("issue27_trainer_cpu", "2-train_model.py")
    assert trainer.autotune_batch_size(16, torch.device("cpu")) == (16, False, False)


@requires_torch
@requires_numpy
@requires_cv2
def test_trainer_exposes_the_autotune_escape_hatches():
    """An advanced user must be able to keep their own batch size."""
    trainer = _load_versioned("issue27_trainer_args", "2-train_model.py")
    text = (VERSIONS / "2-train_model.py").read_text()
    assert "--no-autotune" in text
    assert "--amp" in text
    assert hasattr(trainer, "autotune_batch_size")


@requires_torch
@requires_numpy
@requires_cv2
def test_training_survives_an_out_of_memory_batch():
    """One oversized batch used to abort the whole run."""
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, TensorDataset

    trainer = _load_versioned("issue27_trainer_oom", "2-train_model.py")

    frames = torch.randn(8, 4)
    actions = torch.zeros(8, 2)
    loader = DataLoader(TensorDataset(frames, actions), batch_size=2)

    model = nn.Linear(4, 2)
    calls = {"n": 0}
    real_forward = model.forward

    def flaky(x):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("CUDA out of memory. Tried to allocate 2.00 GiB")
        return real_forward(x)

    model.forward = flaky

    loss = trainer.train_epoch(
        model=model,
        dataloader=loader,
        optimizer=torch.optim.SGD(model.parameters(), lr=0.01),
        criterion=nn.BCEWithLogitsLoss(),
        device=torch.device("cpu"),
        epoch=1,
    )

    # 4 batches, the first skipped -- the run completed instead of dying.
    assert calls["n"] == 4
    assert loss > 0


@requires_torch
@requires_numpy
@requires_cv2
def test_relentless_oom_stops_with_an_actionable_message():
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, TensorDataset

    trainer = _load_versioned("issue27_trainer_oom2", "2-train_model.py")

    loader = DataLoader(
        TensorDataset(torch.randn(20, 4), torch.zeros(20, 2)), batch_size=2
    )

    model = nn.Linear(4, 2)

    def always_oom(x):
        raise RuntimeError("CUDA out of memory")

    model.forward = always_oom

    with pytest.raises(RuntimeError, match="--batch-size"):
        trainer.train_epoch(
            model=model,
            dataloader=loader,
            optimizer=torch.optim.SGD(model.parameters(), lr=0.01),
            criterion=nn.BCEWithLogitsLoss(),
            device=torch.device("cpu"),
            epoch=1,
        )


@requires_torch
@requires_numpy
@requires_cv2
def test_non_oom_runtime_errors_still_propagate():
    """OOM recovery must not swallow real bugs."""
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, TensorDataset

    trainer = _load_versioned("issue27_trainer_err", "2-train_model.py")

    loader = DataLoader(
        TensorDataset(torch.randn(4, 4), torch.zeros(4, 2)), batch_size=2
    )
    model = nn.Linear(4, 2)

    def broken(x):
        raise RuntimeError("shape mismatch in layer 3")

    model.forward = broken

    with pytest.raises(RuntimeError, match="shape mismatch"):
        trainer.train_epoch(
            model=model,
            dataloader=loader,
            optimizer=torch.optim.SGD(model.parameters(), lr=0.01),
            criterion=nn.BCEWithLogitsLoss(),
            device=torch.device("cpu"),
            epoch=1,
        )
