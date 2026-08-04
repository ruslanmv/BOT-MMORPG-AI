"""
Regression tests for GitHub issues #70, #75 and #76.

Each test in this file pins the specific defect a user reported, so a
future refactor that reintroduces it fails here rather than in someone's
living room.

  #70  "Dataset not appearing after recording for me either"
       A custom-game recording landed on disk but never showed up in the
       Train tab. Root cause: tauri-ui/main.js invoked the Rust commands
       with snake_case argument keys (`game_id`) while Tauri derives its
       argument structs with serde's default camelCase renaming
       (`gameId`). For `Option<T>` arguments the key was silently
       dropped, so every listing fell back to DEFAULT_GAME_ID
       ("genshin_impact") -- which is exactly why "just select Genshin
       Impact" was the working workaround in the issue thread.

  #75  "Backend failed to start"
       ModuleNotFoundError: No module named 'torch._strobelight', while
       the runtime doctor's remediation text talked only about
       torch/testing/ -- in one bundle right next to
       `torch_testing_dir_exists=True`. Users followed advice that could
       not fix their failure.

  #76  Program does not see the training files (RU). Same camelCase
       bridge as #70, plus three follow-on defects visible in the
       attached logs:
         - `invalid args 'modelDir' ... missing required key modelDir`
           (the required-argument flavour of the same bug)
         - "Active model directory missing on disk: efficientnet_lstm"
           (an architecture template activated as if it were a model)
         - UnicodeDecodeError inside subprocess's reader thread while
           decoding `tasklist` output on a localized Windows.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import pathlib
import re
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
UI_JS = ROOT / "tauri-ui" / "main.js"
RUST_MAIN = ROOT / "src-tauri" / "src" / "main.rs"
DOCTOR_PATH = ROOT / "scripts" / "runtime_doctor.py"
MODELS_PY = ROOT / "src" / "bot_mmorpg" / "scripts" / "models_pytorch.py"
VERSIONED_MODELS_PY = ROOT / "versions" / "0.01" / "models_pytorch.py"
GAME_PROFILES = ROOT / "game_profiles"


# =====================================================================
# Helpers: static extraction from the JS / Rust sources
# =====================================================================

# Arguments Tauri injects itself -- never part of the JS payload.
_INJECTED_ARG_TYPES = ("tauri::State", "AppHandle", "Window", "tauri::Window")


def _rust_commands() -> dict[str, list[tuple[str, bool]]]:
    """Map every #[tauri::command] fn to its caller-supplied arguments.

    Each entry is ``(arg_name, is_optional)`` -- an ``Option<T>``
    argument deserializes to ``None`` when the key is absent (the silent
    failure mode of #70), while a bare ``String`` hard-errors with
    "missing required key" (the #76 flavour).
    """
    src = RUST_MAIN.read_text(encoding="utf-8", errors="replace")
    commands: dict[str, list[str]] = {}
    pattern = re.compile(
        r"#\[tauri::command(?:\([^)]*\))?\]\s*(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*\(([^)]*)\)",
        re.S,
    )
    for match in pattern.finditer(src):
        name = match.group(1)
        raw_args = re.sub(r"//[^\n]*", "", match.group(2))

        # Split on top-level commas only (generics contain their own).
        params, depth, current = [], 0, ""
        for ch in raw_args:
            if ch in "<([":
                depth += 1
            elif ch in ">)]":
                depth -= 1
            if ch == "," and depth == 0:
                params.append(current)
                current = ""
            else:
                current += ch
        params.append(current)

        arg_names = []
        for param in params:
            param = param.strip()
            if not param or ":" not in param:
                continue
            arg_name, arg_type = (p.strip() for p in param.split(":", 1))
            if any(t in arg_type for t in _INJECTED_ARG_TYPES):
                continue
            arg_names.append((arg_name, arg_type.startswith("Option<")))
        commands[name] = arg_names
    return commands


def _js_invocations() -> list[tuple[str, set[str], bool]]:
    """Extract (command, payload keys, has_spread) for every invoke()."""
    js = UI_JS.read_text(encoding="utf-8", errors="replace")
    out: list[tuple[str, set[str], bool]] = []
    # Match invoke("cmd", { ... }) allowing one level of object nesting.
    pattern = re.compile(
        r"""invoke\(\s*["'](\w+)["']\s*(?:,\s*(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}))?""",
        re.S,
    )
    for match in pattern.finditer(js):
        obj = match.group(2) or ""
        keys = set(re.findall(r"([A-Za-z_]\w*)\s*:", obj))
        # Shorthand properties: { provider, api_key }. Lookahead on both
        # delimiters -- a consuming match would eat the comma that the
        # next shorthand key needs and silently drop it.
        keys |= set(re.findall(r"(?<=[{,])\s*([A-Za-z_]\w*)\s*(?=[,}])", obj))
        out.append((match.group(1), keys, "..." in obj))
    return out


def _to_camel(key: str) -> str:
    """Mirror serde's default rename_all = "camelCase" for arg names."""
    head, *rest = key.split("_")
    return head + "".join(part[:1].upper() + part[1:] for part in rest if part)


def _normalize_invoke_args(keys: set[str]) -> set[str]:
    """Python mirror of normalizeInvokeArgs() in tauri-ui/main.js."""
    out = set(keys)
    for key in keys:
        out.add(_to_camel(key))
        out.add(re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key).lower())
    return out


# =====================================================================
# Issue #70 / #76: the Tauri argument-name bridge
# =====================================================================


def test_ui_wraps_invoke_with_arg_normalizer():
    """main.js must route every invoke through normalizeInvokeArgs."""
    js = UI_JS.read_text(encoding="utf-8", errors="replace")
    assert "function normalizeInvokeArgs" in js
    assert "normalizeInvokeArgs(args)" in js, (
        "The invoke wrapper must actually call the normalizer -- defining "
        "it without wiring it up is how issue #70 shipped."
    )
    # The raw handle stays available for the wrapper, but nothing else
    # may bind `invoke` straight to it and bypass normalization.
    assert (
        re.search(r"const\s+invoke\s*=\s*window\.__TAURI__", js) is None
    ), "`invoke` must be the normalizing wrapper, not window.__TAURI__.invoke"


def test_normalize_invoke_args_emits_both_key_styles():
    """The normalizer's contract, verified against the real JS via node."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not available")

    js = UI_JS.read_text(encoding="utf-8", errors="replace")
    start = js.index("function __toCamel(")
    end = js.index("const invoke =", start)
    harness = (
        js[start:end]
        + "\nconsole.log(JSON.stringify(normalizeInvokeArgs("
        + '{game_id: "custom", modelDir: "C:/m", path: "p"}'
        + ")));\n"
    )
    result = subprocess.run(
        [node, "-e", harness],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    # snake -> camel (this is the direction issue #70 needed)
    assert payload["gameId"] == "custom"
    assert payload["game_id"] == "custom"
    # camel -> snake (so a handler using rename_all="snake_case" works)
    assert payload["model_dir"] == "C:/m"
    assert payload["modelDir"] == "C:/m"
    # Single-word keys are untouched, no duplicates invented.
    assert payload["path"] == "p"


def test_normalize_invoke_args_never_overwrites_explicit_keys():
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not available")

    js = UI_JS.read_text(encoding="utf-8", errors="replace")
    start = js.index("function __toCamel(")
    end = js.index("const invoke =", start)
    harness = (
        js[start:end]
        + "\nconsole.log(JSON.stringify(normalizeInvokeArgs("
        + '{game_id: "snake", gameId: "camel"}'
        + ")));\n"
    )
    result = subprocess.run(
        [node, "-e", harness],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["gameId"] == "camel", "explicit caller keys must win"
    assert payload["game_id"] == "snake"


def test_every_invoke_target_is_a_registered_command():
    registered = _rust_commands()
    unknown = sorted({cmd for cmd, _, _ in _js_invocations() if cmd not in registered})
    assert not unknown, (
        "main.js invokes commands with no #[tauri::command] handler: "
        f"{unknown}. These fail at runtime with 'command not found'."
    )


def test_every_invoke_payload_reaches_its_rust_handler():
    """The #70/#76 root cause, pinned.

    After normalization every declared Rust argument must be present in
    the payload under the camelCase name Tauri deserializes. Call sites
    that build their payload with a spread are checked for required
    arguments only -- the spread's contents are not statically known.
    """
    registered = _rust_commands()
    failures: list[str] = []

    for cmd, keys, has_spread in _js_invocations():
        if cmd not in registered:
            continue  # covered by the test above
        delivered = _normalize_invoke_args(keys)
        for arg, is_optional in registered[cmd]:
            if is_optional and has_spread:
                continue
            expected = _to_camel(arg)
            if expected not in delivered:
                failures.append(
                    f"{cmd}: Rust expects '{expected}' (from `{arg}`), "
                    f"JS sends {sorted(keys) or '{}'}"
                )

    assert not failures, "Tauri argument bridge broken:\n  " + "\n  ".join(failures)


def test_dataset_listing_commands_carry_the_game_id():
    """The precise call sites that made custom-game datasets invisible."""
    invocations = {cmd: keys for cmd, keys, _ in _js_invocations()}
    for cmd in (
        "mh_get_catalog_data",
        "list_datasets",
        "generate_dataset_name",
        "delete_dataset",
        "open_datasets_folder",
    ):
        assert cmd in invocations, f"{cmd} is no longer invoked from main.js"
        delivered = _normalize_invoke_args(invocations[cmd])
        assert "gameId" in delivered, (
            f"{cmd} does not deliver a game id, so it silently falls back to "
            "DEFAULT_GAME_ID and custom-game datasets disappear (issue #70)."
        )


# =====================================================================
# Issue #76: architecture templates are not deployable models
# =====================================================================


def test_ui_rejects_activating_an_architecture_template():
    js = UI_JS.read_text(encoding="utf-8", errors="replace")
    assert "function isArchitectureTemplatePath" in js
    start = js.index("async function setActiveModelFromUI")
    end = js.index("\nasync function deleteSelectedModel", start)
    set_active = js[start:end]
    assert "isArchitectureTemplatePath(path)" in set_active, (
        "Set Active must reject bare architecture ids before they are "
        "stored as the active model_dir (issue #76)."
    )


def test_rust_preflight_distinguishes_architecture_from_missing_dir():
    rust = RUST_MAIN.read_text(encoding="utf-8", errors="replace")
    assert "fn is_architecture_id(" in rust
    assert "is_architecture_id(model_dir)" in rust, (
        "The bot preflight must not report an activated architecture as a "
        "model directory that was 'deleted or moved' (issue #76)."
    )


def test_ui_default_architectures_match_the_model_registry():
    """`mobilenetv3` in the UI vs `mobilenet_v3` in MODEL_REGISTRY meant
    the train preflight rejected an architecture the UI itself offered."""
    js = UI_JS.read_text(encoding="utf-8", errors="replace")
    start = js.index("const DEFAULT_ARCHITECTURES")
    end = js.index("];", start)
    block = js[start:end]
    ui_ids = re.findall(r'\{\s*id:\s*"([^"]+)"', block)
    assert ui_ids, "DEFAULT_ARCHITECTURES parse failed"

    known = _model_registry_keys() | _model_aliases().keys()
    unknown = sorted(set(ui_ids) - known)
    assert not unknown, f"UI offers architectures unknown to MODEL_REGISTRY: {unknown}"


# =====================================================================
# Issue #76: architecture aliases (shipped profiles say `mobilenetv3`)
# =====================================================================


def _models_module_ast(path: pathlib.Path = MODELS_PY) -> ast.Module:
    """Parse models_pytorch.py without importing it (needs torch)."""
    return ast.parse(path.read_text(encoding="utf-8", errors="replace"))


def _dict_literal(tree: ast.Module, name: str) -> dict[str, str]:
    for node in tree.body:
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
            value = node.value
        else:
            continue
        for target in targets:
            if isinstance(target, ast.Name) and target.id == name:
                assert isinstance(value, ast.Dict)
                out = {}
                for k, v in zip(value.keys, value.values):
                    key = k.value if isinstance(k, ast.Constant) else None
                    if key is None:
                        continue
                    out[key] = v.value if isinstance(v, ast.Constant) else v.id
                return out
    raise AssertionError(f"{name} not found in {MODELS_PY.name}")


def _model_registry_keys(path: pathlib.Path = MODELS_PY) -> set[str]:
    return set(_dict_literal(_models_module_ast(path), "MODEL_REGISTRY"))


def _model_aliases(path: pathlib.Path = MODELS_PY) -> dict[str, str]:
    return _dict_literal(_models_module_ast(path), "MODEL_ALIASES")


def test_model_aliases_all_point_at_real_registry_keys():
    registry = _model_registry_keys()
    for alias, target in _model_aliases().items():
        assert (
            target in registry
        ), f"MODEL_ALIASES['{alias}'] -> '{target}' is not a MODEL_REGISTRY key"
        assert alias not in registry, f"'{alias}' is both an alias and a registry key -- pick one"


def test_mobilenetv3_profile_spelling_is_aliased():
    """14 shipped profiles say `mobilenetv3`; get_model() knows
    `mobilenet_v3` and raised ValueError before the first epoch."""
    assert _model_aliases().get("mobilenetv3") == "mobilenet_v3"


def test_every_shipped_game_profile_architecture_is_trainable():
    if not GAME_PROFILES.is_dir():
        pytest.skip("game_profiles/ not present")

    known = _model_registry_keys() | _model_aliases().keys()
    offenders: list[str] = []
    for profile in sorted(GAME_PROFILES.rglob("profile.yaml")):
        text = profile.read_text(encoding="utf-8", errors="replace")
        for arch in re.findall(r'(?:recommended_)?architecture:\s*"([^"]+)"', text):
            if arch not in known:
                offenders.append(f"{profile.relative_to(ROOT)}: {arch}")
    assert (
        not offenders
    ), "Game profiles reference architectures get_model() cannot build:\n  " + "\n  ".join(
        offenders
    )


def test_versioned_models_copy_carries_the_alias_fix():
    """versions/0.01/ is what the installer ships and what training
    actually imports at runtime -- it must not drift from src/."""
    assert VERSIONED_MODELS_PY.exists()
    assert _model_aliases(VERSIONED_MODELS_PY) == _model_aliases()
    assert "resolve_model_name(model_name)" in VERSIONED_MODELS_PY.read_text(
        encoding="utf-8", errors="replace"
    )


@pytest.mark.skipif(importlib.util.find_spec("torch") is None, reason="PyTorch required")
def test_get_model_accepts_the_profile_spelling():
    sys.path.insert(0, str(ROOT / "src"))
    from bot_mmorpg.scripts.models_pytorch import (  # noqa: PLC0415
        get_model_info,
        resolve_model_name,
    )

    assert resolve_model_name("mobilenetv3") == "mobilenet_v3"
    assert resolve_model_name("MobileNetV3") == "mobilenet_v3"
    assert resolve_model_name("efficientnet_lstm") == "efficientnet_lstm"
    # Unknown names pass through so the error still names what was asked.
    assert resolve_model_name("nonsense_arch") == "nonsense_arch"
    assert get_model_info("mobilenetv3")["name"]


# =====================================================================
# Issue #76: subprocess output decoding on localized Windows
# =====================================================================


def test_health_probe_pins_subprocess_encoding():
    from modelhub.diagnostics import health_probe  # noqa: PLC0415

    kwargs = health_probe._SUBPROCESS_TEXT_KWARGS
    assert kwargs["encoding"] == "utf-8"
    assert kwargs["errors"] == "replace", (
        "Without errors='replace' a cp866 byte from tasklist raises "
        "UnicodeDecodeError inside subprocess's reader thread (issue #76)."
    )
    assert kwargs["text"] is True and kwargs["capture_output"] is True


def test_health_probe_has_no_unpinned_text_subprocess():
    """Every subprocess.run in the probe must go through the shared
    kwargs -- a new unpinned call reintroduces the crash."""
    src = (ROOT / "modelhub" / "diagnostics" / "health_probe.py").read_text(
        encoding="utf-8", errors="replace"
    )
    tree = ast.parse(src)
    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "run"):
            continue
        if not (isinstance(func.value, ast.Name) and func.value.id == "subprocess"):
            continue
        keywords = {kw.arg for kw in node.keywords}
        if None in keywords:  # **_SUBPROCESS_TEXT_KWARGS
            continue
        if "text" in keywords and "encoding" not in keywords:
            offenders.append(node.lineno)
    assert not offenders, f"subprocess.run with text=True but no encoding= at line(s) {offenders}"


def test_antivirus_hint_survives_undecodable_output(monkeypatch):
    """Simulate the Russian-Windows tasklist that produced the
    UnicodeDecodeError traceback pasted into issue #76."""
    from modelhub.diagnostics import health_probe  # noqa: PLC0415

    probe = getattr(health_probe, "_antivirus_hint", None)
    if probe is None:
        pytest.skip("_antivirus_hint not present")

    captured: dict = {}

    class _Result:
        returncode = 0
        # What errors="replace" yields for cp866 bytes read as UTF-8.
        stdout = '"\ufffd\ufffd\ufffd.exe","1234"\n"MsMpEng.exe","4321"\n'
        stderr = ""

    def fake_run(cmd, **kwargs):
        captured.update(kwargs)
        return _Result()

    # The probe short-circuits off Windows; we are testing the Windows
    # code path, so claim to be there.
    monkeypatch.setattr(health_probe.platform, "system", lambda: "Windows")
    monkeypatch.setattr(health_probe.subprocess, "run", fake_run)
    result = probe()

    assert captured.get("encoding") == "utf-8"
    assert captured.get("errors") == "replace"
    assert "error" not in result, f"probe degraded instead of reporting: {result}"
    assert "MsMpEng.exe" in result.get("detected", [])


# =====================================================================
# Issue #75: torch._strobelight diagnosis
# =====================================================================


@pytest.fixture(scope="module")
def doctor():
    spec = importlib.util.spec_from_file_location("runtime_doctor_i75", DOCTOR_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["runtime_doctor_i75"] = mod
    spec.loader.exec_module(mod)
    return mod


def _fail_torch_import(monkeypatch, missing: str):
    import importlib as _il

    real_import = _il.import_module

    def fake_import(name, *args, **kwargs):
        if name == "torch":
            raise ModuleNotFoundError(f"No module named '{missing}'", name=missing)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(_il, "import_module", fake_import)


def _fake_torch_tree(monkeypatch, doctor, tmp_path, keep_testing: bool):
    """Stand in for an installed torch so the detail has a real root."""
    torch_root = tmp_path / "site-packages" / "torch"
    torch_root.mkdir(parents=True)
    if keep_testing:
        (torch_root / "testing").mkdir()
    monkeypatch.setattr(doctor, "_resolve_pkg_root", lambda pkg: str(torch_root))
    return torch_root


def test_doctor_names_the_module_that_actually_failed(doctor, monkeypatch, tmp_path):
    """Issue #75: the detail said 'torch/testing' for a failure that was
    nothing to do with torch/testing."""
    _fake_torch_tree(monkeypatch, doctor, tmp_path, keep_testing=True)
    _fail_torch_import(monkeypatch, "torch._strobelight")
    result = doctor._check_torch_intact()

    assert result.status == "error"
    assert "missing_module=torch._strobelight" in result.detail, (
        "The doctor must report WHICH submodule failed; a bundle that only "
        "says 'torch/testing' sends the user after the wrong file."
    )
    assert "missing_module_path_exists=False" in result.detail


def test_doctor_recommends_pip_repair_for_a_single_missing_subpackage(
    doctor, monkeypatch, tmp_path
):
    """Re-extracting the same zip cannot add a file it never contained,
    so the remediation for this signature is the pip path.

    This is the exact bundle from issue #75: torch._strobelight missing
    while torch_testing_dir_exists=True.
    """
    _fake_torch_tree(monkeypatch, doctor, tmp_path, keep_testing=True)
    _fail_torch_import(monkeypatch, "torch._strobelight")
    result = doctor._check_torch_intact()

    assert "torch_testing_dir_exists=True" in result.detail
    assert "Repair PyTorch via pip" in result.detail
    assert "not a broad" in result.detail, (
        "Advice that blames a broad AV quarantine is wrong when the rest "
        "of the torch tree is present -- that is what sent #75 in circles."
    )


def test_doctor_still_blames_quarantine_when_the_tree_is_gutted(doctor, monkeypatch, tmp_path):
    """The original bug-#9 signature must keep its original advice."""
    _fake_torch_tree(monkeypatch, doctor, tmp_path, keep_testing=False)
    _fail_torch_import(monkeypatch, "torch.testing")
    result = doctor._check_torch_intact()

    assert "torch_testing_dir_exists=False" in result.detail
    assert "AV Exclusion" in result.detail
    assert "Repair Runtime" in result.detail


def test_missing_submodule_context_maps_dotted_names_to_paths(doctor, tmp_path):
    torch_root = tmp_path / "torch"
    (torch_root / "_strobelight").mkdir(parents=True)

    present = doctor._missing_submodule_context(str(torch_root), "torch._strobelight")
    assert "missing_module_path_exists=True" in present

    absent = doctor._missing_submodule_context(str(torch_root), "torch.testing")
    assert "missing_module_path_exists=False" in absent

    # Unresolvable inputs degrade to an empty fragment, never a crash.
    assert doctor._missing_submodule_context("<not found on sys.path>", "torch.fx") == ""
    assert doctor._missing_submodule_context(str(torch_root), "torch") == ""
    assert doctor._missing_submodule_context(str(torch_root), "") == ""


def test_doctor_report_still_parses_end_to_end(doctor):
    """Schema guard: the enriched detail must not break JSON output."""
    report = doctor.run_selftest()
    payload = json.loads(doctor.report_to_json(report))
    assert payload["doctor_version"] == doctor.DOCTOR_VERSION
    names = {check["name"] for check in payload["checks"]}
    assert {"torch_intact", "torchvision_intact", "numpy_intact"} <= names
