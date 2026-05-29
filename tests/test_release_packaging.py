"""
Tests for V1.9.9 Release Packaging.
"""
import pathlib
import sys
import os

ROOT = pathlib.Path(__file__).parent.parent


class TestRequiredFilesExist:
    def test_version_txt_exists(self):
        assert (ROOT / "VERSION.txt").is_file()

    def test_customer_readme_exists(self):
        assert (ROOT / "CUSTOMER_README.md").is_file()

    def test_release_notes_exists(self):
        assert (ROOT / "RELEASE_NOTES.md").is_file()

    def test_build_release_script_exists(self):
        assert (ROOT / "scripts" / "build_release.py").is_file()

    def test_release_check_script_exists(self):
        assert (ROOT / "scripts" / "release_check.py").is_file()

    def test_run_bat_exists(self):
        assert (ROOT / "run.bat").is_file()

    def test_setup_bat_exists(self):
        assert (ROOT / "setup.bat").is_file()

    def test_requirements_txt_exists(self):
        assert (ROOT / "requirements.txt").is_file()


class TestBuildReleaseExclusions:
    def _get_exclude_dirs(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "build_release", str(ROOT / "scripts" / "build_release.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod._EXCLUDE_DIRS, getattr(mod, "_EXCLUDE_DATA_PATTERNS", set()), getattr(mod, "_BLOCK_FILENAME_SUBSTRINGS", set())

    def test_exclude_dirs_contains_git(self):
        excl, _, _ = self._get_exclude_dirs()
        assert ".git" in excl

    def test_exclude_dirs_contains_venv(self):
        excl, _, _ = self._get_exclude_dirs()
        assert ".venv" in excl

    def test_exclude_data_patterns_contains_leads_mock(self):
        _, data_excl, _ = self._get_exclude_dirs()
        assert "leads_mock.json" in data_excl

    def test_exclude_data_patterns_contains_client_cases(self):
        _, data_excl, _ = self._get_exclude_dirs()
        assert "client_cases.json" in data_excl

    def test_block_substrings_contains_rossi(self):
        _, _, block_subs = self._get_exclude_dirs()
        assert "rossi" in block_subs

    def test_exclude_dirs_contains_pycache(self):
        excl, _, _ = self._get_exclude_dirs()
        assert "__pycache__" in excl

    def test_exclude_dirs_contains_tests(self):
        excl, _, _ = self._get_exclude_dirs()
        assert "tests" in excl


class TestBuildReleaseZipSafety:
    def _get_zip_safety_func(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "build_release", str(ROOT / "scripts" / "build_release.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod._zip_entry_safe

    def test_safe_zip_name_contains_version(self):
        # The zip name format includes the version
        src = (ROOT / "scripts" / "build_release.py").read_text(encoding="utf-8")
        assert "v{APP_VERSION}" in src or "APP_VERSION" in src

    def test_forbidden_entry_rejected(self):
        safe = self._get_zip_safety_func()
        assert not safe("data/leads_mock.json")
        assert not safe(".git/config")
        assert not safe("data/client_cases.json")
        assert not safe("__pycache__/foo.pyc")

    def test_normal_entry_allowed(self):
        safe = self._get_zip_safety_func()
        assert safe("ui/streamlit_app.py")
        assert safe("config.py")
        assert safe("README.md")
        assert safe("run.bat")


class TestScriptsImportable:
    def test_release_check_main_importable(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "release_check", str(ROOT / "scripts" / "release_check.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, "main")

    def test_build_release_main_importable(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "build_release", str(ROOT / "scripts" / "build_release.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, "main")
