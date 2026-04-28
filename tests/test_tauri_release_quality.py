"""
Tauri Release Quality Tests

Validates version consistency, release configuration, and installer quality
across the entire project. Ensures no duplicate versions, proper semver,
and that releases are gamer-friendly (easy to understand, no confusion).

These tests catch common release issues:
- Version mismatches between pyproject.toml, Cargo.toml, and tauri.conf.json
- Duplicate or inconsistent installer naming
- Missing release documentation
- Nightly build configuration problems
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAURI_DIR = ROOT / "src-tauri"
TAURI_CONF = TAURI_DIR / "tauri.conf.json"
CARGO_TOML = TAURI_DIR / "Cargo.toml"
PYPROJECT = ROOT / "pyproject.toml"


# ---------------------------------------------------------------------------
# Version Consistency
# ---------------------------------------------------------------------------
class TestVersionConsistency:
    """Ensure all version numbers match across the project."""

    def _get_pyproject_version(self):
        """Extract version from pyproject.toml."""
        content = PYPROJECT.read_text(encoding="utf-8")
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        return match.group(1) if match else None

    def _get_tauri_conf_version(self):
        """Extract version from tauri.conf.json."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        return conf.get("package", {}).get("version")

    def _get_cargo_version(self):
        """Extract version from Cargo.toml."""
        content = CARGO_TOML.read_text(encoding="utf-8")
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        return match.group(1) if match else None

    def _get_python_package_version(self):
        """Extract version from bot_mmorpg/__init__.py."""
        init_py = ROOT / "src" / "bot_mmorpg" / "__init__.py"
        if not init_py.exists():
            return None
        content = init_py.read_text(encoding="utf-8")
        match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
        return match.group(1) if match else None

    def test_pyproject_version_is_semver(self):
        """pyproject.toml version must be valid semver."""
        version = self._get_pyproject_version()
        assert version is not None, "pyproject.toml version not found"
        parts = version.split(".")
        assert len(parts) == 3, f"Version must be semver (x.y.z): {version}"
        assert all(p.isdigit() for p in parts), (
            f"Version parts must be numeric: {version}"
        )

    def test_tauri_conf_version_is_semver(self):
        """tauri.conf.json version must be valid semver."""
        version = self._get_tauri_conf_version()
        assert version is not None, "tauri.conf.json version not found"
        parts = version.split(".")
        assert len(parts) == 3, f"Version must be semver (x.y.z): {version}"

    def test_cargo_version_is_semver(self):
        """Cargo.toml version must be valid semver."""
        version = self._get_cargo_version()
        assert version is not None, "Cargo.toml version not found"
        parts = version.split(".")
        assert len(parts) == 3, f"Version must be semver (x.y.z): {version}"

    def test_all_versions_match(self):
        """All version numbers must be identical across config files."""
        pyproject_v = self._get_pyproject_version()
        tauri_v = self._get_tauri_conf_version()
        cargo_v = self._get_cargo_version()
        package_v = self._get_python_package_version()

        versions = {
            "pyproject.toml": pyproject_v,
            "tauri.conf.json": tauri_v,
            "Cargo.toml": cargo_v,
        }

        if package_v:
            versions["__init__.py"] = package_v

        unique = set(v for v in versions.values() if v is not None)
        assert len(unique) == 1, (
            f"Version mismatch detected! "
            f"All config files must use the same version.\n"
            f"Found: {versions}"
        )

    def test_version_not_zero(self):
        """Version must not be 0.0.0 (uninitialized)."""
        version = self._get_pyproject_version()
        assert version != "0.0.0", "Version must not be 0.0.0"


# ---------------------------------------------------------------------------
# Release Configuration
# ---------------------------------------------------------------------------
class TestReleaseConfiguration:
    """Verify release/CI configuration is correct."""

    def test_ci_workflow_exists(self):
        """CI workflow must exist for automated testing."""
        ci = ROOT / ".github" / "workflows" / "ci.yml"
        assert ci.exists(), "CI workflow missing"

    def test_release_workflow_exists(self):
        """Release workflow must exist for automated releases.

        Either of two candidate filenames is acceptable. The legacy
        `release.yml` was retired during the containerized-runtime
        migration because it bypassed build_pipeline.ps1 (and therefore
        the runtime-integrity check that gates Bug #9 / Bug #10
        regressions). The current workflow is `release-windows-installer.yml`.
        """
        candidates = [
            ROOT / ".github" / "workflows" / "release.yml",
            ROOT / ".github" / "workflows" / "release-windows-installer.yml",
        ]
        found = any(c.exists() for c in candidates)
        assert found, (
            "Release workflow missing -- expected either release.yml "
            "(legacy) or release-windows-installer.yml"
        )

    def test_build_installer_workflow_exists(self):
        """Windows installer build workflow must exist."""
        candidates = [
            ROOT / ".github" / "workflows" / "build-windows-installer.yml",
            ROOT / ".github" / "workflows" / "release-windows-installer.yml",
        ]
        found = any(c.exists() for c in candidates)
        assert found, "Windows installer build workflow missing"

    def test_product_name_consistent(self):
        """Product name must be consistent across configs."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        tauri_name = conf.get("package", {}).get("productName", "")

        content = PYPROJECT.read_text(encoding="utf-8")
        match = re.search(r'name\s*=\s*"([^"]+)"', content)
        pyproject_name = match.group(1) if match else ""

        # Normalize for comparison (hyphens vs underscores)
        assert tauri_name.lower().replace("-", "").replace(
            "_", ""
        ) == pyproject_name.lower().replace("-", "").replace("_", ""), (
            f"Product name mismatch: Tauri='{tauri_name}', pyproject='{pyproject_name}'"
        )

    def test_installer_exe_name_matches_version(self):
        """Installer filename pattern must include version for clarity."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        product = conf.get("package", {}).get("productName", "")
        version = conf.get("package", {}).get("version", "")

        # The expected installer name pattern
        expected_pattern = f"{product}_{version}"
        assert product and version, "Product name and version must be set"
        # Verify the pattern would produce a clear, non-empty filename
        assert len(expected_pattern) > 3, "Installer filename pattern too short"
        assert "_" not in product or product == "BOT-MMORPG-AI", (
            "Product name should use hyphens not underscores"
        )


# ---------------------------------------------------------------------------
# Nightly Build Compatibility
# ---------------------------------------------------------------------------
class TestNightlyBuildCompatibility:
    """Verify the project supports nightly builds correctly."""

    def test_no_duplicate_version_artifacts(self):
        """Build should not produce multiple .exe with different versions.

        Common issue: tauri.conf.json has v1.0.0 but the release tag is v0.1.5,
        producing two different installers (confusing for gamers).
        """
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        tauri_version = conf.get("package", {}).get("version", "")

        cargo_content = CARGO_TOML.read_text(encoding="utf-8")
        cargo_match = re.search(r'version\s*=\s*"([^"]+)"', cargo_content)
        cargo_version = cargo_match.group(1) if cargo_match else ""

        assert tauri_version == cargo_version, (
            f"Version mismatch will cause duplicate installers!\n"
            f"tauri.conf.json: {tauri_version}\n"
            f"Cargo.toml: {cargo_version}\n"
            f"Fix: Update both to the same version."
        )

    def test_version_not_stale(self):
        """Version should not be a legacy pre-release version.

        If the project is at v1.0.0, it should not still have 0.x.x in configs.
        """
        pyproject_v = None
        content = PYPROJECT.read_text(encoding="utf-8")
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        if match:
            pyproject_v = match.group(1)

        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        tauri_v = conf.get("package", {}).get("version", "")

        if pyproject_v and tauri_v:
            py_major = int(pyproject_v.split(".")[0])
            tauri_major = int(tauri_v.split(".")[0])

            # Major versions should match
            assert py_major == tauri_major, (
                f"Major version mismatch: pyproject={pyproject_v}, tauri={tauri_v}. "
                f"This will confuse gamers with duplicate installers."
            )


# ---------------------------------------------------------------------------
# Documentation for Gamers
# ---------------------------------------------------------------------------
class TestGamerDocumentation:
    """Verify documentation is accessible and clear for non-expert users."""

    def test_readme_exists(self):
        """README.md must exist."""
        assert (ROOT / "README.md").exists()

    def test_usage_guide_exists(self):
        """USAGE.md (gamer's guide) must exist."""
        assert (ROOT / "USAGE.md").exists()

    def test_readme_has_quick_start(self):
        """README must have a quick start section."""
        readme = (ROOT / "README.md").read_text(encoding="utf-8", errors="replace")
        has_quick = (
            "quick start" in readme.lower()
            or "getting started" in readme.lower()
            or "how to" in readme.lower()
        )
        assert has_quick, "README must have a quick start section for gamers"

    def test_readme_mentions_three_steps(self):
        """README must mention the 3 simple steps for gamers."""
        readme = (ROOT / "README.md").read_text(encoding="utf-8", errors="replace")
        has_record = "record" in readme.lower() or "collect" in readme.lower()
        has_train = "train" in readme.lower()
        has_play = (
            "play" in readme.lower()
            or "bot" in readme.lower()
            or "run" in readme.lower()
        )

        assert has_record, "README must mention recording/data collection"
        assert has_train, "README must mention training"
        assert has_play, "README must mention running the bot"

    def test_readme_has_system_requirements(self):
        """README must list system requirements."""
        readme = (ROOT / "README.md").read_text(encoding="utf-8", errors="replace")
        has_reqs = (
            "requirements" in readme.lower()
            or "system" in readme.lower()
            or "windows" in readme.lower()
        )
        assert has_reqs, "README must list system requirements"


# ---------------------------------------------------------------------------
# Python Package Integrity
# ---------------------------------------------------------------------------
class TestPythonPackageIntegrity:
    """Verify Python package structure is correct for bundling."""

    def test_bot_mmorpg_package_exists(self):
        """bot_mmorpg package must exist."""
        pkg = ROOT / "src" / "bot_mmorpg"
        assert pkg.exists()
        assert (pkg / "__init__.py").exists()

    def test_all_subpackages_have_init(self):
        """All subpackages must have __init__.py."""
        pkg = ROOT / "src" / "bot_mmorpg"
        subdirs = [
            d for d in pkg.iterdir() if d.is_dir() and not d.name.startswith("__")
        ]

        for subdir in subdirs:
            init = subdir / "__init__.py"
            assert init.exists(), f"Missing __init__.py in {subdir.name}/"

    def test_build_backend_configured(self):
        """Build backend must be configured in pyproject.toml."""
        content = PYPROJECT.read_text(encoding="utf-8")
        assert "build-backend" in content
        assert "hatchling" in content or "setuptools" in content

    def test_wheel_packages_configured(self):
        """Wheel build must include bot_mmorpg package."""
        content = PYPROJECT.read_text(encoding="utf-8")
        assert "bot_mmorpg" in content
