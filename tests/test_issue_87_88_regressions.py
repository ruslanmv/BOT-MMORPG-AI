"""
Regression tests for GitHub issues #87 and #88.

  #88  "Cannot start bot"
       Right after a successful training run, Run Bot was refused with
       "Active model directory missing on disk: custom_farming_v1. The
       model was deleted or moved". Nothing had been deleted:
       `discover_local_models` reports a model's folder only under
       `paths.dir`, so the UI's trained-model entries had no `path`, its
       model picker fell back to the bare folder name, and Set Active
       stored `model_dir="custom_farming_v1"`. The Rust preflight checks
       that string relative to its own working directory, where no such
       folder exists.

  #87  "torch_dlls" warning on a working install
       The runtime doctor warned that libomp140.x86_64.dll was missing
       while `torch_intact` passed in the same report -- torch's native
       extension had loaded, so nothing it needed was missing. The same
       row warned about two torch trees: "Repair PyTorch via pip" ran a
       plain `pip install`, which writes to `Lib\\site-packages`, while the
       bundled torch in `<python>\\site-packages` comes first on sys.path.
       The repaired copy was never imported and every repair left a
       second tree behind.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCTOR_PATH = ROOT / "scripts" / "runtime_doctor.py"
MAIN_RS = ROOT / "src-tauri" / "src" / "main.rs"
UI_JS = ROOT / "tauri-ui" / "main.js"

FASTAPI_MISSING = importlib.util.find_spec("fastapi") is None
requires_fastapi = pytest.mark.skipif(FASTAPI_MISSING, reason="fastapi required")


# =====================================================================
# #88 -- a freshly trained model must be runnable
# =====================================================================


@pytest.fixture
def sidecar(monkeypatch, tmp_path):
    """The sidecar module pointed at an empty data root.

    registry_store keeps `active_model.json` relative to the working
    directory (the data root in production), so chdir there too.
    """
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from modelhub import tauri as mod

    if not mod.MODELHUB_AVAILABLE:
        pytest.skip("ModelHub failed to initialise in this environment")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(mod, "DATA_ROOT", tmp_path)
    return mod


def _trained_model(data_root: pathlib.Path, gid: str, name: str) -> pathlib.Path:
    """What 2-train_model.py leaves behind for one finished run."""
    model_dir = data_root / "trained_models" / gid / name
    model_dir.mkdir(parents=True)
    (model_dir / "efficientnet_lstm_best.pth").write_bytes(b"best")
    (model_dir / "efficientnet_lstm_final.pth").write_bytes(b"final")
    return model_dir


def _client(sidecar):
    from fastapi.testclient import TestClient

    return TestClient(sidecar.create_app("tkn")), {"X-Auth-Token": "tkn"}


@requires_fastapi
def test_catalog_local_models_carry_their_folder_path(sidecar, tmp_path):
    """The UI keys cards and Set Active off `path`; discovery never set it."""
    model_dir = _trained_model(tmp_path, "custom", "custom_farming_v1")
    client, headers = _client(sidecar)

    body = client.get("/modelhub/catalog?game_id=custom", headers=headers).json()

    (entry,) = body["local_models"]
    assert entry["id"] == "custom_farming_v1"
    assert entry["path"] == model_dir.as_posix()
    assert entry["model_dir"] == model_dir.as_posix()
    assert entry["checkpoint"].endswith("efficientnet_lstm_best.pth")
    assert entry["has_artifacts"] is True


@requires_fastapi
def test_set_active_with_bare_model_name_stores_absolute_folder(sidecar, tmp_path):
    """The exact payload older UI builds sent for issue #88."""
    model_dir = _trained_model(tmp_path, "custom", "custom_farming_v1")
    client, headers = _client(sidecar)

    res = client.post(
        "/modelhub/active",
        json={"game_id": "custom", "model_id": "local", "path": "custom_farming_v1"},
        headers=headers,
    ).json()

    assert res["ok"] is True
    stored = json.loads((tmp_path / "active_model.json").read_text(encoding="utf-8"))
    assert stored["model_dir"] == model_dir.resolve().as_posix()
    assert pathlib.Path(stored["model_dir"]).is_absolute()
    assert stored["model_file"].endswith("efficientnet_lstm_best.pth")


@requires_fastapi
def test_set_active_resolves_data_root_relative_registry_paths(sidecar, tmp_path):
    """register_model records `trained_models\\<game>\\<name>` (Windows)."""
    model_dir = _trained_model(tmp_path, "custom", "custom_farming_v1")
    client, headers = _client(sidecar)

    client.post(
        "/modelhub/active",
        json={
            "game_id": "custom",
            "model_id": "reg",
            "path": "trained_models\\custom\\custom_farming_v1",
        },
        headers=headers,
    )

    stored = json.loads((tmp_path / "active_model.json").read_text(encoding="utf-8"))
    assert stored["model_dir"] == model_dir.resolve().as_posix()


@requires_fastapi
def test_catalog_heals_an_existing_bare_name_active_model(sidecar, tmp_path):
    """Users who already hit #88 have the bad value on disk. The next
    catalog load must fix it -- the preflight and start_bot both read
    `active.model_dir` from this response."""
    model_dir = _trained_model(tmp_path, "custom", "custom_farming_v1")
    (tmp_path / "active_model.json").write_text(
        json.dumps({"game": "custom", "model_id": "local", "model_dir": "custom_farming_v1"}),
        encoding="utf-8",
    )
    client, headers = _client(sidecar)

    active = client.get("/modelhub/catalog?game_id=custom", headers=headers).json()["active"]

    assert active["model_dir"] == model_dir.resolve().as_posix()
    assert active["model_file"].endswith("efficientnet_lstm_best.pth")
    persisted = json.loads((tmp_path / "active_model.json").read_text(encoding="utf-8"))
    assert persisted["model_dir"] == active["model_dir"]


@requires_fastapi
def test_catalog_heals_active_model_of_another_game(sidecar, tmp_path):
    """active_model.json is global; the selected game may differ."""
    model_dir = _trained_model(tmp_path, "eden_eternal", "eden_quests_v1")
    (tmp_path / "active_model.json").write_text(
        json.dumps({"game": "custom", "model_id": "local", "model_dir": "eden_quests_v1"}),
        encoding="utf-8",
    )
    client, headers = _client(sidecar)

    active = client.get("/modelhub/catalog?game_id=custom", headers=headers).json()["active"]

    assert active["model_dir"] == model_dir.resolve().as_posix()


@requires_fastapi
def test_unresolvable_active_model_is_left_for_the_preflight_to_report(sidecar, tmp_path):
    """A model that really is gone keeps its stored value, so the
    "missing on disk" message still names what the user activated."""
    (tmp_path / "active_model.json").write_text(
        json.dumps({"game": "custom", "model_id": "local", "model_dir": "deleted_model"}),
        encoding="utf-8",
    )
    client, headers = _client(sidecar)

    active = client.get("/modelhub/catalog?game_id=custom", headers=headers).json()["active"]

    assert active["model_dir"] == "deleted_model"


def test_merge_keeps_discovery_metadata_and_adds_scan_paths(sidecar, tmp_path):
    model_dir = _trained_model(tmp_path, "custom", "m1")
    discovered = [
        {
            "id": "m1",
            "name": "Farming v1",
            "architecture": "efficientnet_lstm",
            "created_at": None,
            "paths": {"dir": str(model_dir)},
        }
    ]
    scanned = sidecar._scan_trained_models_fs(tmp_path, "custom")

    (merged,) = sidecar._merge_local_models(discovered, scanned)

    assert merged["name"] == "Farming v1"
    assert merged["architecture"] == "efficientnet_lstm"
    assert merged["path"] == model_dir.as_posix()
    # None from discovery must not shadow the scan's timestamp.
    assert merged["created_at"]


def test_ui_never_falls_back_to_the_bare_model_id_for_a_path():
    js = UI_JS.read_text(encoding="utf-8")
    assert "function localModelPath(m)" in js
    assert "m.paths && m.paths.dir" in js
    # The card list and the hidden picker both go through the helper.
    assert "path: localModelPath(m)," in js
    assert "return localModelPath(m) || m.id" in js


# =====================================================================
# Screen preview shows a broken-image icon
# =====================================================================
#
# The sidecar captured the screen fine and the UI set
# `img.src = "data:image/jpeg;base64,..."`, but the app CSP had no
# `img-src`, so `default-src 'self'` applied and the WebView refused every
# data: URL. The pane showed a broken-image icon instead of the screen
# (#88 "live preview displays nothing", and the Teach-tab report).

TAURI_CONF = ROOT / "src-tauri" / "tauri.conf.json"


def _csp_directives() -> dict:
    csp = json.loads(TAURI_CONF.read_text(encoding="utf-8"))["tauri"]["security"]["csp"]
    out = {}
    for part in csp.split(";"):
        tokens = part.split()
        if tokens:
            out[tokens[0]] = tokens[1:]
    return out


def test_csp_allows_data_url_preview_frames():
    directives = _csp_directives()
    assert "img-src" in directives, "without img-src, default-src 'self' blocks data: images"
    assert "data:" in directives["img-src"]
    assert "'self'" in directives["img-src"]


def test_preview_image_failure_is_reported_not_silent():
    js = UI_JS.read_text(encoding="utf-8")
    assert "imgEl.onerror" in js
    assert "could not be displayed" in js


@pytest.mark.skipif(
    importlib.util.find_spec("cv2") is None or importlib.util.find_spec("numpy") is None,
    reason="opencv + numpy required",
)
def test_grab_screen_base64_is_a_decodable_jpeg(monkeypatch):
    import base64

    import numpy as np

    spec = importlib.util.spec_from_file_location(
        "grabscreen_i88", ROOT / "versions" / "0.01" / "grabscreen.py"
    )
    grabscreen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(grabscreen)
    frame = np.zeros((2160, 3840, 3), dtype=np.uint8)
    frame[:, :, 0] = 200
    monkeypatch.setattr(grabscreen, "grab_screen_monitor", lambda monitor_id=1: frame)

    raw = base64.b64decode(grabscreen.grab_screen_base64(1, 640, 360, 70))

    assert raw[:3] == b"\xff\xd8\xff", "not a JPEG -- the data: URL would not render"


# =====================================================================
# "Training has been running for 8 hours and I can't launch the run"
# =====================================================================


def test_bot_preflight_refuses_to_cancel_a_running_training_job():
    """start_bot -> submit_sidecar_job cancels the running job, so
    clicking Start Bot mid-training silently killed the training run."""
    rs = MAIN_RS.read_text(encoding="utf-8")
    bot_branch = rs[rs.index('"bot" => {'):]
    bot_branch = bot_branch[: bot_branch.index("other => {")]
    assert "running_sidecar_job_kind(&state.inner).await" in bot_branch
    assert "Training is still running" in bot_branch
    assert "async fn running_sidecar_job_kind" in rs


def test_stopped_training_with_a_checkpoint_is_finalized_as_partial():
    rs = MAIN_RS.read_text(encoding="utf-8")
    assert 'let partial = status == "cancelled";' in rs
    assert "resolve_checkpoint_path(None, Some(meta.out_dir.as_str()))" in rs
    assert '"partial": partial,' in rs
    assert 'status == "completed" || (partial && checkpoint.is_some())' in rs
    js = UI_JS.read_text(encoding="utf-8")
    assert "meta.partial === true" in js


def _trainer():
    if importlib.util.find_spec("numpy") is None or importlib.util.find_spec("cv2") is None:
        pytest.skip("numpy + opencv required")
    spec = importlib.util.spec_from_file_location(
        "train_model_i88", ROOT / "versions" / "0.01" / "2-train_model.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_cpu_training_hint_names_the_cpu_only_build():
    hint = _trainer().cpu_training_hint("NVIDIA GeForce RTX 5070 Ti", "2.13.0+cpu", None)
    assert "CPU-only" in hint
    assert "RTX 5070 Ti" in hint
    assert "Stop" in hint and "_best.pth" in hint


def test_cpu_training_hint_blames_the_driver_for_a_cuda_build():
    hint = _trainer().cpu_training_hint("NVIDIA GeForce RTX 3060", "2.5.0+cu121", "12.1")
    assert "driver" in hint


def test_cpu_training_hint_is_silent_without_an_nvidia_gpu():
    assert _trainer().cpu_training_hint(None, "2.13.0+cpu", None) == ""


# =====================================================================
# #87 -- torch_dlls: libomp140 false positive and the second torch tree
# =====================================================================


@pytest.fixture(scope="module")
def doctor():
    spec = importlib.util.spec_from_file_location("runtime_doctor_i87", DOCTOR_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["runtime_doctor_i87"] = mod
    spec.loader.exec_module(mod)
    return mod


def _pe_with_imports(path: pathlib.Path, dlls, delay_dlls=()) -> None:
    """Write a minimal PE32+ whose import (and delay-import) tables name `dlls`."""
    import struct

    va, raw_ptr = 0x1000, 0x200
    body = bytearray()
    n_desc = len(dlls) + 1
    delay_off = n_desc * 20
    n_delay = len(delay_dlls) + 1 if delay_dlls else 0
    names_off = delay_off + n_delay * 32
    names = bytearray()
    name_rvas = []
    for name in list(dlls) + list(delay_dlls):
        name_rvas.append(va + names_off + len(names))
        names += name.encode("ascii") + b"\0"
    for rva in name_rvas[: len(dlls)]:
        body += struct.pack("<IIIII", 0, 0, 0, rva, 0)
    body += b"\0" * 20
    for rva in name_rvas[len(dlls):]:
        body += struct.pack("<IIIIIIII", 1, rva, 0, 0, 0, 0, 0, 0)
    if delay_dlls:
        body += b"\0" * 32
    body += names

    dos = bytearray(64)
    dos[:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 64)
    coff = struct.pack("<HHIIIHH", 0x8664, 1, 0, 0, 0, 240, 0x2022)
    opt = bytearray(240)
    struct.pack_into("<H", opt, 0, 0x20B)
    struct.pack_into("<II", opt, 112 + 1 * 8, va, n_desc * 20)
    if delay_dlls:
        struct.pack_into("<II", opt, 112 + 13 * 8, va + delay_off, n_delay * 32)
    section = struct.pack("<8sIIIIIIHHI", b".idata", len(body), va, len(body), raw_ptr, 0, 0, 0, 0, 0)
    head = bytes(dos) + b"PE\0\0" + coff + bytes(opt) + section
    path.write_bytes(head + b"\0" * (raw_ptr - len(head)) + bytes(body))


def _torch_lib(tmp_path, *, fbgemm_imports=None):
    root = tmp_path / "site-packages" / "torch"
    lib = root / "lib"
    lib.mkdir(parents=True)
    for name in ("c10.dll", "torch_cpu.dll", "torch_python.dll"):
        (lib / name).write_bytes(b"MZ")
    if fbgemm_imports is not None:
        _pe_with_imports(lib / "fbgemm.dll", fbgemm_imports)
    return root


def test_pe_reader_lists_regular_and_delay_imports(doctor, tmp_path):
    dll = tmp_path / "fbgemm.dll"
    _pe_with_imports(dll, ["KERNEL32.dll", "libomp140.x86_64.dll"], delay_dlls=["asmjit.dll"])
    assert doctor._pe_imported_dlls(str(dll)) == [
        "kernel32.dll",
        "libomp140.x86_64.dll",
        "asmjit.dll",
    ]


def test_pe_reader_returns_none_for_non_pe(doctor, tmp_path):
    junk = tmp_path / "junk.dll"
    junk.write_bytes(b"MZ not really")
    assert doctor._pe_imported_dlls(str(junk)) is None
    assert doctor._pe_imported_dlls(str(tmp_path / "absent.dll")) is None


def _as_windows(doctor, monkeypatch, root, native_loaded=False):
    monkeypatch.setattr(doctor.sys, "platform", "win32")
    monkeypatch.setattr(doctor, "_resolve_pkg_root", lambda pkg: str(root))
    monkeypatch.setattr(doctor, "_torch_install_roots", lambda: [str(root)])
    monkeypatch.setattr(doctor, "_torch_native_loaded", lambda: native_loaded)


def test_no_libomp_warning_when_torch_already_loaded(doctor, monkeypatch, tmp_path):
    """The #87 bundle: torch_intact OK, torch_dlls WARN about libomp140."""
    root = _torch_lib(tmp_path)
    _as_windows(doctor, monkeypatch, root, native_loaded=True)

    result = doctor._check_torch_dlls()

    assert result.status == "ok", result.detail
    assert "does not need it" in result.detail


def test_no_libomp_warning_when_fbgemm_does_not_import_it(doctor, monkeypatch, tmp_path):
    root = _torch_lib(tmp_path, fbgemm_imports=["KERNEL32.dll", "c10.dll"])
    _as_windows(doctor, monkeypatch, root)

    assert doctor._check_torch_dlls().status == "ok"


def test_libomp_warning_kept_when_fbgemm_needs_it_and_torch_failed(doctor, monkeypatch, tmp_path):
    """The real #79 failure must still be diagnosed."""
    root = _torch_lib(tmp_path, fbgemm_imports=["libomp140.x86_64.dll"])
    _as_windows(doctor, monkeypatch, root)

    result = doctor._check_torch_dlls()

    assert result.status == "warn"
    assert "libomp140.x86_64.dll is not among them" in result.detail


def test_split_install_names_the_live_tree_and_the_fix(doctor, monkeypatch, tmp_path):
    root = _torch_lib(tmp_path)
    shadow = tmp_path / "Lib" / "site-packages" / "torch"
    shadow.mkdir(parents=True)
    _as_windows(doctor, monkeypatch, root, native_loaded=True)
    monkeypatch.setattr(doctor, "_torch_install_roots", lambda: [str(root), str(shadow)])

    result = doctor._check_torch_dlls()

    assert result.status == "warn"
    assert f"torch is imported from {root}" in result.detail
    assert f"{shadow} is a shadowed copy" in result.detail
    assert "Repair PyTorch via pip" in result.detail


def test_pip_repair_retires_the_shadowing_bundled_torch():
    rs = MAIN_RS.read_text(encoding="utf-8")
    assert "fn retire_shadowing_torch(py_dir: &Path)" in rs
    repair = rs[rs.index("async fn repair_pytorch_via_pip"):]
    repair = repair[: repair.index("\nfn shutdown_all")]
    assert "retire_shadowing_torch(py_dir)" in repair
    # Retire only AFTER every pip run succeeded (early returns come first).
    assert repair.index("return Err(msg);") < repair.index("retire_shadowing_torch(py_dir)")


# =====================================================================
# #88 follow-up -- "bot does nothing" with a mouse-trained model
# =====================================================================


class _FakeMouse:
    def __init__(self):
        self.events = []
        self._pos = (0, 0)

    @property
    def position(self):
        return self._pos

    @position.setter
    def position(self, value):
        self._pos = value
        self.events.append(("move", value))

    def press(self, button):
        self.events.append(("press", button))

    def release(self, button):
        self.events.append(("release", button))


def _bot():
    if importlib.util.find_spec("numpy") is None or importlib.util.find_spec("cv2") is None:
        pytest.skip("numpy + opencv required")
    versions = str(ROOT / "versions" / "0.01")
    if versions not in sys.path:
        sys.path.insert(0, versions)
    spec = importlib.util.spec_from_file_location("test_model_i88", ROOT / "versions" / "0.01" / "3-test_model.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _preds(x, y, lmb, rmb=0.0):
    import numpy as np

    p = np.zeros(39)
    p[29:39] = [x, y, 0.0, 0.0, 0.0, 0.0, lmb, rmb, 0.0, 0.0]
    return p


def test_mouse_replayer_clicks_once_at_the_predicted_position():
    bot = _bot()
    fake = _FakeMouse()
    rep = bot.MouseReplayer((0, 40, 1920, 1120), controller=fake, buttons={"left": "L", "right": "R"})

    label = rep.step(_preds(0.5, 0.25, 0.9))
    rep.step(_preds(0.5, 0.25, 0.95))  # still held: no second press
    rep.step(_preds(0.5, 0.25, 0.1))   # released

    assert fake.events == [("move", (960, 310)), ("press", "L"), ("release", "L")]
    assert label.startswith("left-click @ 960,310")


def test_mouse_replayer_ignores_models_without_mouse_output():
    import numpy as np

    bot = _bot()
    fake = _FakeMouse()
    rep = bot.MouseReplayer((0, 0, 100, 100), controller=fake, buttons={"left": "L", "right": "R"})
    assert rep.step(np.ones(29)) is None
    assert fake.events == []


def test_mouse_replayer_reads_the_legacy_six_value_layout():
    import numpy as np

    bot = _bot()
    p = np.zeros(35)
    p[29:35] = [0.1, 0.2, 0.0, 0.8, 0.0, 0.0]  # x, y, lmb, rmb, mmb, scroll
    assert bot.MouseReplayer.parse(p) == (pytest.approx(0.1), pytest.approx(0.2), 0.0, pytest.approx(0.8))


def test_release_all_lets_go_of_held_buttons():
    bot = _bot()
    fake = _FakeMouse()
    rep = bot.MouseReplayer((0, 0, 100, 100), controller=fake, buttons={"left": "L", "right": "R"})
    rep.step(_preds(0.5, 0.5, 0.0, 0.9))
    rep.release_all()
    assert fake.events[-1] == ("release", "R")
    assert rep.held == {"left": False, "right": False}


def test_capture_region_env_matches_the_recorder(monkeypatch):
    bot = _bot()
    monkeypatch.setenv("BOTMMO_CAPTURE_REGION", "0,0,1280,720")
    assert bot.capture_region_from_env((0, 40, 1920, 1120)) == (0, 0, 1280, 720)
    monkeypatch.setenv("BOTMMO_CAPTURE_REGION", "garbage")
    assert bot.capture_region_from_env((0, 40, 1920, 1120)) == (0, 40, 1920, 1120)


# =====================================================================
# GPU PyTorch -- the bundled CPU build left NVIDIA cards idle (#82)
# =====================================================================


def _rust_fn(rs: str, signature: str) -> str:
    body = rs[rs.index(signature):]
    return body[: body.index("\n}\n")]


def test_gpu_install_command_is_registered_and_guarded():
    rs = MAIN_RS.read_text(encoding="utf-8")
    handler = rs[rs.index("tauri::generate_handler!["):]
    assert "install_gpu_pytorch," in handler and "gpu_status," in handler
    body = _rust_fn(rs, "async fn install_gpu_pytorch(")
    # Never rewrite torch under a running training/recording/bot job.
    assert body.index("ensure_no_sidecar_job") < body.index('"pip", "install"')
    # Same torch version as bundled, CUDA flavour, no dependency churn.
    assert 'format!("torch=={}", torch_v)' in body
    assert '"--no-deps"' in body
    assert "https://download.pytorch.org/whl/{}" in body
    # Each install is proven on the GPU before success is reported.
    assert "GPU_PROBE_PY" in body and "compute_ok" in body
    assert "retire_shadowing_torch(py_dir)" in body
    assert "ensure_no_sidecar_job" in _rust_fn(rs, "async fn repair_pytorch_via_pip(")


def test_cuda_indexes_cover_rtx_50_and_older_cards():
    rs = MAIN_RS.read_text(encoding="utf-8")
    table = rs[rs.index("const CUDA_INDEXES"):]
    table = table[: table.index("];")]
    # Blackwell needs CUDA 12.8+; pre-Turing cards need a CUDA 12.x build.
    assert '("cu130", 580)' in table and '("cu128", 570)' in table
    assert '("cu126", 560)' in table
    assert table.index("cu130") < table.index("cu126")


def test_gpu_probe_script_runs_and_reports_json():
    """The probe the command runs through the embedded Python."""
    import re
    import subprocess

    rs = MAIN_RS.read_text(encoding="utf-8")
    code = re.search(r'const GPU_PROBE_PY: &str = r#"(.*?)"#;', rs, re.S).group(1)
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120).stdout
    line = next(ln for ln in out.splitlines() if ln.startswith("GPUPROBE "))
    report = json.loads(line[len("GPUPROBE "):])
    assert "torch" in report or "error" in report


def test_system_tools_offers_gpu_install():
    html = (ROOT / "tauri-ui" / "index.html").read_text(encoding="utf-8")
    assert 'id="btn-install-gpu-pytorch"' in html
    assert "invoke('install_gpu_pytorch')" in html
    assert "invoke('gpu_status')" in html


def test_cpu_training_hint_points_to_the_gpu_install():
    hint = _trainer().cpu_training_hint("NVIDIA GeForce RTX 5070 Ti", "2.13.0+cpu", None)
    assert "Install GPU PyTorch (NVIDIA)" in hint


# =====================================================================
# Training could not be stopped, and the Train tab never went idle
# =====================================================================


def test_train_button_becomes_stop_while_running():
    js = UI_JS.read_text(encoding="utf-8")
    start = js[js.index("window.startTraining = async function"):]
    head = start[: start.index("logToTerminal(\"-------------------------------------------\"")]
    assert 'btn.classList.contains("is-running")' in head
    assert 'invoke("stop_process")' in head
    running = js[js.index("function _setTrainBadgeRunning()"):]
    running = running[: running.index("\n}\n")]
    assert "btn.disabled = false;" in running
    assert '"Stop training"' in running


def test_job_end_emits_process_finished():
    """The UI resets Train/Run/Record on process_finished, but nothing
    emitted it after jobs moved to the sidecar -- the Train button sat on
    "Training..." forever."""
    rs = MAIN_RS.read_text(encoding="utf-8")
    worker = rs[rs.index("fn spawn_log_bridge_worker("):]
    worker = worker[: worker.index("\nfn stop_process_inner")]
    assert '"process_finished"' in worker
    assert "if !superseded" in worker


def test_gamer_guide_screenshots_exist():
    guide = (ROOT / "GAMER_GUIDE.md").read_text(encoding="utf-8")
    import re

    images = re.findall(r"\]\((docs/images/guide/[^)]+)\)", guide)
    assert len(images) == 5
    for rel in images:
        assert (ROOT / rel).is_file(), rel
