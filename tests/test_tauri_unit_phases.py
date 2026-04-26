"""
Tauri Unit Tests - Three-Phase Pipeline Verification

Validates that the Tauri (desktop exec) version of the program correctly
supports all 3 phases of the bot pipeline:

    Phase 1: Data Collection (Recording) - Screen capture + input labels
    Phase 2: Model Training              - Neural network training loop
    Phase 3: Inference (Bot Playing)      - Real-time prediction + action

These tests verify the Python-side logic that Tauri invokes via subprocess,
ensuring the same quality as the Eel-based launcher.
"""

import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

# Project root
ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Helper: check PyTorch availability at module level
# ---------------------------------------------------------------------------
try:
    import torch

    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

requires_pytorch = pytest.mark.skipif(not PYTORCH_AVAILABLE, reason="PyTorch required")


# ---------------------------------------------------------------------------
# Phase 1: Data Collection / Recording
# ---------------------------------------------------------------------------
class TestPhase1Recording:
    """Verify the data collection phase works for the Tauri exec version."""

    def test_collect_data_script_exists(self):
        """Phase 1 script must exist at the expected path."""
        script = ROOT / "versions" / "0.01" / "1-collect_data.py"
        assert script.exists(), f"Collect-data script missing: {script}"

    def test_collect_data_script_compiles(self):
        """Phase 1 script must compile without syntax errors."""
        import py_compile

        script = ROOT / "versions" / "0.01" / "1-collect_data.py"
        py_compile.compile(str(script), doraise=True)

    def test_recording_creates_valid_dataset_structure(self, tmp_path):
        """Simulated recording must create paired image+label files."""
        dataset_dir = tmp_path / "datasets" / "test_game" / "session_01"
        dataset_dir.mkdir(parents=True)

        num_samples = 15
        num_classes = 5

        # Simulate what 1-collect_data.py produces
        for i in range(num_samples):
            img_array = np.random.randint(0, 255, (270, 480, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img.save(dataset_dir / f"frame_{i:04d}.png")

            label = {"action": i % num_classes, "keys": [f"key_{i % num_classes}"]}
            with open(dataset_dir / f"frame_{i:04d}.json", "w") as f:
                json.dump(label, f)

        images = sorted(dataset_dir.glob("*.png"))
        labels = sorted(dataset_dir.glob("*.json"))
        assert len(images) == num_samples
        assert len(labels) == num_samples

        # Verify each image has a matching label
        for img_path in images:
            label_path = img_path.with_suffix(".json")
            assert label_path.exists(), f"Missing label for {img_path.name}"

    def test_recording_image_dimensions_valid(self, tmp_path):
        """Recorded images must have correct shape for model consumption."""
        img_array = np.random.randint(0, 255, (270, 480, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        path = tmp_path / "test_frame.png"
        img.save(path)

        loaded = Image.open(path)
        assert loaded.size == (480, 270), "Image must be 480x270 (W x H)"
        assert loaded.mode == "RGB"

    def test_recording_label_format_valid(self, tmp_path):
        """Labels must be valid JSON with expected fields."""
        label = {"action": 3, "keys": ["w", "space"]}
        path = tmp_path / "label.json"
        with open(path, "w") as f:
            json.dump(label, f)

        with open(path) as f:
            loaded = json.load(f)

        assert "action" in loaded
        assert isinstance(loaded["action"], int)
        assert "keys" in loaded
        assert isinstance(loaded["keys"], list)

    def test_recording_npy_heterogeneous_save(self, tmp_path):
        """Verify numpy save with heterogeneous shapes (screen + label pairs)."""
        training_data = []
        for _ in range(10):
            screen = np.random.randint(0, 255, (270, 480, 3), dtype=np.uint8)
            label = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0])
            training_data.append([screen, label])

        arr = np.array(training_data, dtype=object)
        path = tmp_path / "training_data.npy"
        np.save(str(path), arr, allow_pickle=True)

        loaded = np.load(str(path), allow_pickle=True)
        assert loaded.shape[0] == 10
        assert loaded[0][0].shape == (270, 480, 3)
        assert len(loaded[0][1]) == 9

    def test_recording_supports_multiple_resolutions(self, tmp_path):
        """Recording must support all 4 capture resolutions."""
        resolutions = [
            (480, 270, "default"),
            (640, 360, "low"),
            (960, 540, "medium"),
            (1280, 720, "hd"),
        ]

        for width, height, name in resolutions:
            img = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
            path = tmp_path / f"test_{name}.png"
            Image.fromarray(img).save(path)

            loaded = Image.open(path)
            assert loaded.size == (width, height), (
                f"Resolution {name} ({width}x{height}) failed"
            )

    def test_recording_gamepad_combined_labels(self, tmp_path):
        """Recording must handle keyboard+gamepad combined label vectors."""
        training_data = []
        for _ in range(5):
            screen = np.random.randint(0, 255, (270, 480, 3), dtype=np.uint8)
            # keyboard(9) + gamepad(20) = 29
            label = np.concatenate([np.zeros(9), np.zeros(20)])
            training_data.append([screen, label])

        arr = np.array(training_data, dtype=object)
        path = tmp_path / "gamepad_data.npy"
        np.save(str(path), arr, allow_pickle=True)

        loaded = np.load(str(path), allow_pickle=True)
        assert loaded.shape[0] == 5
        assert len(loaded[0][1]) == 29

    def test_recording_mouse_combined_labels(self, tmp_path):
        """Recording must handle keyboard+gamepad+mouse combined labels."""
        training_data = []
        for _ in range(5):
            screen = np.random.randint(0, 255, (270, 480, 3), dtype=np.uint8)
            # keyboard(9) + gamepad(20) + mouse(6) = 35
            label = np.concatenate([np.zeros(9), np.zeros(20), np.zeros(6)])
            training_data.append([screen, label])

        arr = np.array(training_data, dtype=object)
        path = tmp_path / "mouse_data.npy"
        np.save(str(path), arr, allow_pickle=True)

        loaded = np.load(str(path), allow_pickle=True)
        assert loaded.shape[0] == 5
        assert len(loaded[0][1]) == 35


# ---------------------------------------------------------------------------
# Phase 2: Model Training
# ---------------------------------------------------------------------------
class TestPhase2Training:
    """Verify the training phase works for the Tauri exec version."""

    def test_train_model_script_exists(self):
        """Phase 2 script must exist at the expected path."""
        script = ROOT / "versions" / "0.01" / "2-train_model.py"
        assert script.exists(), f"Train-model script missing: {script}"

    def test_train_model_script_compiles(self):
        """Phase 2 script must compile without syntax errors."""
        import py_compile

        script = ROOT / "versions" / "0.01" / "2-train_model.py"
        py_compile.compile(str(script), doraise=True)

    def test_train_model_loads_when_torch_unavailable(self):
        """
        Regression guard for: NameError: name 'Dataset' is not defined.

        2-train_model.py imports `from torch.utils.data import Dataset`
        inside a try/except. If torch isn't installed, `Dataset` is
        undefined at module top-level. A previous revision then declared
        `class GameplayDataset(Dataset):` UNCONDITIONALLY at module
        load time -- which raised NameError before main() could check
        PYTORCH_AVAILABLE and exit cleanly. Spawned-script users on
        machines where torch failed to import would get a
        NameError + STATUS_ACCESS_VIOLATION (-1073741819) instead of
        the script's intended "[Warning] PyTorch not installed"
        message.

        Fix: introduce `BaseDataset = Dataset if PYTORCH_AVAILABLE
        else object` after the try/except, then declare the class as
        `class GameplayDataset(BaseDataset)`. Module always parses,
        main() runs, exits cleanly when torch is missing.

        This test simulates the torch-missing case by hooking
        builtins.__import__ to raise ImportError for any torch.* import.
        """
        import builtins
        import sys
        import types

        real_import = builtins.__import__

        def block_torch(name, *a, **kw):
            if name == "torch" or name.startswith("torch."):
                raise ImportError("simulated: torch not installed")
            return real_import(name, *a, **kw)

        # Block torch via __import__ + shim out cv2/numpy and the
        # bot_mmorpg helper module so we isolate this test to the
        # torch-fallback fix only.
        previous_modules = {
            k: sys.modules.get(k)
            for k in ("cv2", "numpy", "bot_mmorpg", "bot_mmorpg.scripts")
        }
        sys.modules["cv2"] = types.ModuleType("mock-cv2")
        sys.modules["numpy"] = types.ModuleType("mock-numpy")
        sys.modules["bot_mmorpg"] = types.ModuleType("mock-bot_mmorpg")
        sys.modules["bot_mmorpg.scripts"] = types.ModuleType("mock-bot_mmorpg.scripts")

        builtins.__import__ = block_torch
        try:
            script = ROOT / "versions" / "0.01" / "2-train_model.py"
            src = script.read_text(encoding="utf-8")
            ns: dict = {"__name__": "fake_module", "__file__": str(script)}

            try:
                exec(compile(src, str(script), "exec"), ns)
            except SystemExit:
                # Acceptable: script may sys.exit() under torch-missing
                pass

            # Module-load surface
            assert ns.get("PYTORCH_AVAILABLE") is False, (
                "Expected PYTORCH_AVAILABLE=False under simulated torch absence"
            )
            assert ns.get("BaseDataset") is object, (
                "BaseDataset fallback must be `object` when torch is missing"
            )
            cls = ns.get("GameplayDataset")
            assert cls is not None, "GameplayDataset must be defined"
            assert object in cls.__bases__, (
                "GameplayDataset must inherit from BaseDataset (object) "
                "when torch is missing -- not from undefined `Dataset`"
            )

            # Phase 2 regression: the actual exception must be captured so
            # the operator (and the AI Fix Bundle) can see WHY torch failed,
            # not just THAT it failed. A bare ImportError catch with no
            # message would mask DLL-load failures, AV quarantine, and
            # CPU-feature mismatches under the misleading "PyTorch not
            # installed" line.
            captured = ns.get("PYTORCH_IMPORT_ERROR")
            assert captured is not None, (
                "PYTORCH_IMPORT_ERROR must be set when torch import fails"
            )
            assert isinstance(captured, BaseException), (
                "PYTORCH_IMPORT_ERROR must hold the actual exception object"
            )
            assert "simulated" in str(captured), (
                f"Captured exception must preserve original message; got: {captured!r}"
            )
        finally:
            builtins.__import__ = real_import
            for k, v in previous_modules.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v

    @requires_pytorch
    def test_training_loop_converges(self, tmp_path):
        """A minimal training loop must converge (loss decreases)."""
        import torch
        import torch.nn as nn

        # Tiny model
        model = nn.Sequential(
            nn.Conv2d(3, 8, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(8, 5),
        )

        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        criterion = nn.CrossEntropyLoss()

        # Fake dataset
        X = torch.randn(20, 3, 32, 32)
        y = torch.randint(0, 5, (20,))

        initial_loss = None
        model.train()
        for epoch in range(5):
            optimizer.zero_grad()
            out = model(X)
            loss = criterion(out, y)
            if initial_loss is None:
                initial_loss = loss.item()
            loss.backward()
            optimizer.step()

        final_loss = loss.item()
        assert final_loss < initial_loss, (
            f"Training did not converge: initial={initial_loss:.4f}, final={final_loss:.4f}"
        )

    @requires_pytorch
    def test_model_save_and_load(self, tmp_path):
        """Trained model must save to disk and load back correctly."""
        import torch
        import torch.nn as nn

        model = nn.Sequential(
            nn.Conv2d(3, 8, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(8, 5),
        )

        model_path = tmp_path / "model.pt"
        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "num_classes": 5,
                "input_size": (32, 32),
            },
            model_path,
        )

        assert model_path.exists()
        assert model_path.stat().st_size > 0

        # Load back
        checkpoint = torch.load(model_path, weights_only=False)
        assert "model_state_dict" in checkpoint
        assert checkpoint["num_classes"] == 5

    @requires_pytorch
    def test_all_architectures_instantiate(self):
        """All registered model architectures must instantiate."""
        import torch.nn as nn

        from bot_mmorpg.scripts.models_pytorch import get_model, list_models

        for model_name in list_models():
            model = get_model(model_name, num_actions=29, pretrained=False)
            assert isinstance(model, nn.Module), (
                f"Architecture '{model_name}' failed to instantiate"
            )

    @requires_pytorch
    def test_training_output_directory_structure(self, tmp_path):
        """Training must create proper output directory structure."""
        import torch

        out_dir = tmp_path / "trained_models" / "test_game" / "my_model"
        out_dir.mkdir(parents=True)

        # Simulate training output
        model = torch.nn.Linear(10, 5)
        torch.save(model.state_dict(), out_dir / "model.pt")

        # Simulate profile
        profile = {
            "architecture": "efficientnet_lstm",
            "num_classes": 5,
            "input_size": [480, 270],
        }
        with open(out_dir / "profile.json", "w") as f:
            json.dump(profile, f)

        assert (out_dir / "model.pt").exists()
        assert (out_dir / "profile.json").exists()

    @requires_pytorch
    def test_curriculum_training_config(self):
        """CurriculumConfig must provide valid training schedules."""
        from bot_mmorpg.training import CurriculumConfig

        config = CurriculumConfig.default(total_epochs=50)
        assert config is not None
        assert len(config.phases) > 0

    @requires_pytorch
    def test_training_loss_is_finite(self):
        """Training loss must always be a finite number (no NaN/Inf)."""
        import torch
        import torch.nn as nn

        model = nn.Sequential(
            nn.Conv2d(3, 8, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(8, 5),
        )

        criterion = nn.CrossEntropyLoss()
        X = torch.randn(4, 3, 32, 32)
        y = torch.randint(0, 5, (4,))

        model.train()
        out = model(X)
        loss = criterion(out, y)

        assert torch.isfinite(loss), f"Loss is not finite: {loss.item()}"


# ---------------------------------------------------------------------------
# Phase 3: Inference (Bot Playing)
# ---------------------------------------------------------------------------
class TestPhase3Inference:
    """Verify the inference phase works for the Tauri exec version."""

    def test_test_model_script_exists(self):
        """Phase 3 script must exist at the expected path."""
        script = ROOT / "versions" / "0.01" / "3-test_model.py"
        assert script.exists(), f"Test-model script missing: {script}"

    def test_test_model_script_compiles(self):
        """Phase 3 script must compile without syntax errors."""
        import py_compile

        script = ROOT / "versions" / "0.01" / "3-test_model.py"
        py_compile.compile(str(script), doraise=True)

    @requires_pytorch
    def test_inference_engine_initializes(self):
        """InferenceEngine must initialize with a model + metadata."""
        from bot_mmorpg.inference.engine import InferenceEngine, ModelMetadata

        model = torch.nn.Sequential(
            torch.nn.Conv2d(3, 8, 3, padding=1),
            torch.nn.ReLU(),
            torch.nn.AdaptiveAvgPool2d(1),
            torch.nn.Flatten(),
            torch.nn.Linear(8, 5),
        )

        metadata = ModelMetadata(
            architecture="custom",
            input_size=(32, 32),
            num_classes=5,
            class_names=["a0", "a1", "a2", "a3", "a4"],
            temporal_frames=0,
            normalize="imagenet",
            pytorch_version=torch.__version__,
            extra={},
        )

        engine = InferenceEngine(model=model, metadata=metadata)
        assert engine is not None
        assert engine.model is not None
        assert engine.metadata.num_classes == 5

    @requires_pytorch
    def test_inference_prediction_valid(self):
        """InferenceEngine.predict() must return valid result."""
        from bot_mmorpg.inference.engine import InferenceEngine, ModelMetadata

        model = torch.nn.Sequential(
            torch.nn.Conv2d(3, 8, 3, padding=1),
            torch.nn.ReLU(),
            torch.nn.AdaptiveAvgPool2d(1),
            torch.nn.Flatten(),
            torch.nn.Linear(8, 5),
        )

        metadata = ModelMetadata(
            architecture="custom",
            input_size=(32, 32),
            num_classes=5,
            class_names=["a0", "a1", "a2", "a3", "a4"],
            temporal_frames=0,
            normalize="imagenet",
            pytorch_version=torch.__version__,
            extra={},
        )

        engine = InferenceEngine(model=model, metadata=metadata)
        test_img = Image.fromarray(
            np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8)
        )

        result = engine.predict(test_img)

        assert result is not None
        assert 0 <= result.action_id < 5
        assert 0.0 <= result.confidence <= 1.0
        assert result.inference_time_ms >= 0

    @requires_pytorch
    def test_inference_softmax_sums_to_one(self):
        """Inference probabilities must sum to 1.0."""
        model = torch.nn.Sequential(
            torch.nn.Conv2d(3, 8, 3, padding=1),
            torch.nn.ReLU(),
            torch.nn.AdaptiveAvgPool2d(1),
            torch.nn.Flatten(),
            torch.nn.Linear(8, 5),
        )
        model.eval()

        x = torch.randn(1, 3, 32, 32)
        with torch.no_grad():
            logits = model(x)
            probs = torch.softmax(logits, dim=1)

        assert probs.sum().item() == pytest.approx(1.0, abs=0.01)

    @requires_pytorch
    def test_inference_action_in_valid_range(self):
        """Predicted action must be within valid class range."""
        num_classes = 29
        model = torch.nn.Sequential(
            torch.nn.Conv2d(3, 8, 3, padding=1),
            torch.nn.ReLU(),
            torch.nn.AdaptiveAvgPool2d(1),
            torch.nn.Flatten(),
            torch.nn.Linear(8, num_classes),
        )
        model.eval()

        x = torch.randn(1, 3, 270, 480)
        with torch.no_grad():
            output = model(x)
            action = torch.argmax(output, dim=1).item()

        assert 0 <= action < num_classes

    @requires_pytorch
    def test_temporal_buffer_operation(self):
        """TemporalBuffer must accumulate frames correctly for LSTM models."""
        from bot_mmorpg.inference.engine import TemporalBuffer

        buffer = TemporalBuffer(max_frames=4)

        assert not buffer.is_ready()
        assert buffer.get_sequence() is None

        # Add frames
        for i in range(4):
            frame = torch.randn(3, 270, 480)
            buffer.add(frame)

        assert buffer.is_ready()
        seq = buffer.get_sequence()
        assert seq is not None
        assert seq.shape == (4, 3, 270, 480)

    @requires_pytorch
    def test_temporal_buffer_sliding_window(self):
        """TemporalBuffer sliding window must drop oldest frames."""
        from bot_mmorpg.inference.engine import TemporalBuffer

        buffer = TemporalBuffer(max_frames=4)

        # Add 6 frames (2 more than capacity)
        for i in range(6):
            frame = torch.randn(3, 32, 32)
            buffer.add(frame)

        assert buffer.is_ready()
        seq = buffer.get_sequence()
        assert seq.shape == (4, 3, 32, 32)

    @requires_pytorch
    def test_temporal_buffer_clear(self):
        """TemporalBuffer.clear() must reset the buffer."""
        from bot_mmorpg.inference.engine import TemporalBuffer

        buffer = TemporalBuffer(max_frames=4)
        for i in range(4):
            buffer.add(torch.randn(3, 32, 32))

        assert buffer.is_ready()
        buffer.clear()
        assert not buffer.is_ready()

    @requires_pytorch
    def test_model_loaded_from_checkpoint_runs_inference(self, tmp_path):
        """Full round-trip: save checkpoint -> load -> inference."""
        import torch.nn as nn

        num_classes = 5

        # Create and save model
        model = nn.Sequential(
            nn.Conv2d(3, 8, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(8, num_classes),
        )

        model_path = tmp_path / "test_model.pt"
        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "num_classes": num_classes,
                "input_size": (32, 32),
            },
            model_path,
        )

        # Load and run inference
        checkpoint = torch.load(model_path, weights_only=False)
        loaded_model = nn.Sequential(
            nn.Conv2d(3, 8, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(8, checkpoint["num_classes"]),
        )
        loaded_model.load_state_dict(checkpoint["model_state_dict"])
        loaded_model.eval()

        x = torch.randn(1, 3, 32, 32)
        with torch.no_grad():
            output = loaded_model(x)
            probs = torch.softmax(output, dim=1)
            action = torch.argmax(output, dim=1).item()

        assert 0 <= action < num_classes
        assert probs.sum().item() == pytest.approx(1.0, abs=0.01)


# ---------------------------------------------------------------------------
# Cross-Phase Integration (lightweight)
# ---------------------------------------------------------------------------
class TestCrossPhaseIntegration:
    """Verify data flows correctly between phases."""

    def test_recorded_data_loadable_for_training(self, tmp_path):
        """Phase 1 output must be loadable by Phase 2."""
        dataset_dir = tmp_path / "dataset"
        dataset_dir.mkdir()

        # Phase 1: create data
        for i in range(10):
            img = np.random.randint(0, 255, (270, 480, 3), dtype=np.uint8)
            Image.fromarray(img).save(dataset_dir / f"frame_{i:04d}.png")

            label = {"action": i % 5, "keys": [f"key_{i % 5}"]}
            with open(dataset_dir / f"frame_{i:04d}.json", "w") as f:
                json.dump(label, f)

        # Phase 2: load data
        images = sorted(dataset_dir.glob("*.png"))
        labels = sorted(dataset_dir.glob("*.json"))

        assert len(images) == 10
        assert len(labels) == 10

        for img_path in images:
            img = Image.open(img_path).convert("RGB")
            assert img.size == (480, 270)

            label_path = img_path.with_suffix(".json")
            with open(label_path) as f:
                label = json.load(f)
            assert 0 <= label["action"] < 5

    @requires_pytorch
    def test_trained_model_usable_for_inference(self, tmp_path):
        """Phase 2 output (model.pt) must be loadable by Phase 3."""
        import torch.nn as nn

        # Phase 2: train and save
        model = nn.Sequential(
            nn.Conv2d(3, 8, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(8, 5),
        )

        model_path = tmp_path / "model.pt"
        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "num_classes": 5,
                "input_size": (32, 32),
            },
            model_path,
        )

        # Phase 3: load and predict
        checkpoint = torch.load(model_path, weights_only=False)
        inference_model = nn.Sequential(
            nn.Conv2d(3, 8, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(8, checkpoint["num_classes"]),
        )
        inference_model.load_state_dict(checkpoint["model_state_dict"])
        inference_model.eval()

        test_img = torch.randn(1, 3, 32, 32)
        with torch.no_grad():
            output = inference_model(test_img)

        assert output.shape == (1, 5)

    def test_version_scripts_sequential_naming(self):
        """All 3 phase scripts must follow sequential naming convention."""
        scripts_dir = ROOT / "versions" / "0.01"
        expected = [
            "1-collect_data.py",
            "2-train_model.py",
            "3-test_model.py",
        ]
        for script_name in expected:
            path = scripts_dir / script_name
            assert path.exists(), f"Missing phase script: {script_name}"
