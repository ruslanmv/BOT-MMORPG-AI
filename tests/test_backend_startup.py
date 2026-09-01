"""
Tests for backend sidecar startup and argument forwarding.

Validates that main_backend.py correctly parses CLI args and forwards
them to modelhub.tauri with the right parameter names.
"""

import importlib.util
import pathlib
import sys

from unittest.mock import MagicMock, patch

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load_entry_main():
    """Import backend/entry_main.py under a unique name."""
    spec = importlib.util.spec_from_file_location(
        "entry_main_under_test", ROOT / "backend" / "entry_main.py"
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["entry_main_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestSidecarSitePackagesBootstrap:
    """Issue #85: the sidecar must find its own interpreter's packages.

    The bundled runtime can hold third-party deps in either
    ``<prefix>\\site-packages`` (the build's ``pip --target``) or
    ``<prefix>\\Lib\\site-packages`` (where a pip-based repair installs).
    The Rust supervisor only put the former on PYTHONPATH, so a repaired
    ``uvicorn`` in the latter was invisible -> ``No module named
    'uvicorn'``. entry_main now adds both, derived from sys.prefix.
    """

    def test_lib_site_packages_is_added_when_present(self, tmp_path, monkeypatch):
        entry = _load_entry_main()

        # A fake interpreter prefix whose deps live only in Lib/site-packages
        # -- the location a `pip install` repair uses by default.
        lib_sp = tmp_path / "Lib" / "site-packages"
        lib_sp.mkdir(parents=True)

        monkeypatch.setattr(sys, "prefix", str(tmp_path))
        monkeypatch.setattr(sys, "executable", str(tmp_path / "python.exe"))
        monkeypatch.setattr(sys, "path", list(sys.path))

        entry._bootstrap_site_packages()

        assert str(lib_sp) in sys.path

    def test_flat_site_packages_is_added_when_present(self, tmp_path, monkeypatch):
        entry = _load_entry_main()

        flat_sp = tmp_path / "site-packages"
        flat_sp.mkdir()

        monkeypatch.setattr(sys, "prefix", str(tmp_path))
        monkeypatch.setattr(sys, "executable", str(tmp_path / "python.exe"))
        monkeypatch.setattr(sys, "path", list(sys.path))

        entry._bootstrap_site_packages()

        assert str(flat_sp) in sys.path

    def test_missing_dirs_are_skipped_and_do_not_raise(self, tmp_path, monkeypatch):
        entry = _load_entry_main()

        monkeypatch.setattr(sys, "prefix", str(tmp_path))  # empty prefix
        monkeypatch.setattr(sys, "executable", str(tmp_path / "python.exe"))
        before = list(sys.path)
        monkeypatch.setattr(sys, "path", list(sys.path))

        entry._bootstrap_site_packages()  # must not raise

        # Nothing existed to add, so the path is unchanged.
        assert sys.path == before

    def test_bootstrap_is_idempotent(self, tmp_path, monkeypatch):
        entry = _load_entry_main()

        (tmp_path / "Lib" / "site-packages").mkdir(parents=True)
        monkeypatch.setattr(sys, "prefix", str(tmp_path))
        monkeypatch.setattr(sys, "executable", str(tmp_path / "python.exe"))
        monkeypatch.setattr(sys, "path", list(sys.path))

        entry._bootstrap_site_packages()
        entry._bootstrap_site_packages()

        target = str(tmp_path / "Lib" / "site-packages")
        assert sys.path.count(target) == 1


class TestBackendArgParsing:
    """Test CLI argument parsing in main_backend.py."""

    def test_default_args(self):
        """Test default argument values parse without error."""
        captured_args = []

        def fake_tauri_main(argv):
            captured_args.extend(argv)
            return 0

        mock_module = MagicMock()
        mock_module.main = fake_tauri_main
        with patch.dict(
            "sys.modules", {"modelhub": MagicMock(), "modelhub.tauri": mock_module}
        ):
            import importlib

            import backend.main_backend

            importlib.reload(backend.main_backend)
            backend.main_backend.main([])

        # Default port is 0, default token is ""
        assert "--port" in captured_args
        assert "0" in captured_args
        assert "--resource-root" in captured_args

    def test_project_root_resolution(self, tmp_path):
        """Test project root resolution from CLI arg."""
        from pathlib import Path

        from backend.main_backend import _resolve_project_root

        test_dir = str(tmp_path / "testroot")
        result = _resolve_project_root(test_dir)
        assert result == Path(test_dir).resolve()

    def test_project_root_env_fallback(self, tmp_path):
        """Test project root resolution from environment variable."""
        import os
        from pathlib import Path

        from backend.main_backend import _resolve_project_root

        env_dir = str(tmp_path / "envroot")
        with patch.dict(os.environ, {"MODELHUB_PROJECT_ROOT": env_dir}):
            result = _resolve_project_root("")
            assert result == Path(env_dir).resolve()

    def test_project_root_auto_detection(self):
        """Test project root auto-detection from file location."""
        import os

        from backend.main_backend import _resolve_project_root

        # Clear env to test fallback
        with patch.dict(os.environ, {"MODELHUB_PROJECT_ROOT": ""}):
            result = _resolve_project_root("")
            # Should resolve to repo root (parent of backend/)
            assert result.exists()

    def test_forwards_resource_root_not_project_root(self):
        """Test that main_backend forwards --resource-root to modelhub.tauri."""
        import backend.main_backend as bm

        captured_args = []

        def fake_tauri_main(argv):
            captured_args.extend(argv)
            return 0

        with patch.object(bm, "_ensure_sys_path"):
            # Patch the import inside main
            mock_module = MagicMock()
            mock_module.main = fake_tauri_main
            with patch.dict(
                "sys.modules", {"modelhub": MagicMock(), "modelhub.tauri": mock_module}
            ):
                import importlib

                importlib.reload(bm)
                bm.main(["--port", "8080", "--token", "abc123"])

        # Verify --resource-root is passed (not --project-root)
        assert "--resource-root" in captured_args
        assert "--data-root" in captured_args
        assert "--project-root" not in captured_args
        assert "--port" in captured_args
        assert "8080" in captured_args
        assert "--token" in captured_args
        assert "abc123" in captured_args


class TestDataSavefix:
    """Test the numpy save fix for inhomogeneous training data (Issue #13/#6)."""

    def test_save_heterogeneous_training_data(self, tmp_path):
        """Verify that [screen, label] pairs with different shapes can be saved."""
        import numpy as np

        # Simulate real training data: screen (H, W, 3) + label vector (variable len)
        training_data = []
        for _ in range(10):
            screen = np.random.randint(0, 255, (270, 480, 3), dtype=np.uint8)
            label = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0])  # keyboard output
            training_data.append([screen, label])

        # This is the FIXED code from collect_data.py
        arr = np.array(training_data, dtype=object)
        path = tmp_path / "test_training.npy"
        np.save(str(path), arr, allow_pickle=True)

        # Verify load
        loaded = np.load(str(path), allow_pickle=True)
        assert loaded.shape[0] == 10
        assert loaded[0][0].shape == (270, 480, 3)
        assert len(loaded[0][1]) == 9

    def test_save_heterogeneous_with_gamepad(self, tmp_path):
        """Verify save works with keyboard+gamepad combined labels."""
        import numpy as np

        training_data = []
        for _ in range(5):
            screen = np.random.randint(0, 255, (270, 480, 3), dtype=np.uint8)
            # keyboard(9) + gamepad(20) = 29
            label = np.concatenate([np.zeros(9), np.zeros(20)])
            training_data.append([screen, label])

        arr = np.array(training_data, dtype=object)
        path = tmp_path / "test_gamepad.npy"
        np.save(str(path), arr, allow_pickle=True)

        loaded = np.load(str(path), allow_pickle=True)
        assert loaded.shape[0] == 5
        assert len(loaded[0][1]) == 29

    def test_save_heterogeneous_with_mouse(self, tmp_path):
        """Verify save works with keyboard+gamepad+mouse combined labels."""
        import numpy as np

        training_data = []
        for _ in range(5):
            screen = np.random.randint(0, 255, (270, 480, 3), dtype=np.uint8)
            # keyboard(9) + gamepad(20) + mouse(6) = 35
            label = np.concatenate([np.zeros(9), np.zeros(20), np.zeros(6)])
            training_data.append([screen, label])

        arr = np.array(training_data, dtype=object)
        path = tmp_path / "test_mouse.npy"
        np.save(str(path), arr, allow_pickle=True)

        loaded = np.load(str(path), allow_pickle=True)
        assert loaded.shape[0] == 5
        assert len(loaded[0][1]) == 35
