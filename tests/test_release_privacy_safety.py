"""
Tests for V1.9.9 Release Privacy Safety.
"""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).parent.parent


def _read(filename: str) -> str:
    return (ROOT / filename).read_text(encoding="utf-8")


def _load_build_release():
    spec = importlib.util.spec_from_file_location(
        "build_release", str(ROOT / "scripts" / "build_release.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_release_check():
    spec = importlib.util.spec_from_file_location(
        "release_check", str(ROOT / "scripts" / "release_check.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestGitignorePrivacy:
    def test_gitignore_contains_leads_mock(self):
        # Covered by specific filename OR by data/*.json wildcard
        text = _read(".gitignore")
        assert "leads_mock" in text or "data/*.json" in text

    def test_gitignore_contains_client_cases(self):
        # Covered by specific filename OR by data/*.json wildcard
        text = _read(".gitignore")
        assert "client_cases" in text or "data/*.json" in text

    def test_gitignore_contains_human_design_calibration(self):
        # Covered by specific filename OR by data/*.json wildcard
        text = _read(".gitignore")
        assert (
            "human_design_calibration" in text
            or "human_design_calibration_cases" in text
            or "data/*.json" in text
        )

    def test_gitignore_contains_env(self):
        text = _read(".gitignore")
        assert ".env" in text

    def test_gitignore_contains_json_wildcard_or_specific(self):
        text = _read(".gitignore")
        assert "*.json" in text or "leads_mock.json" in text


class TestBuildReleaseExclusionLists:
    def test_exclude_list_blocks_env(self):
        mod = _load_build_release()
        exclude_files = getattr(mod, "_EXCLUDE_FILES", set())
        extensions = getattr(mod, "_EXCLUDE_EXTENSIONS", set())
        block_subs = getattr(mod, "_BLOCK_FILENAME_SUBSTRINGS", set())
        assert ".env" in exclude_files or ".env" in str(exclude_files)

    def test_exclude_list_blocks_pem(self):
        mod = _load_build_release()
        extensions = getattr(mod, "_EXCLUDE_EXTENSIONS", set())
        assert ".pem" in extensions

    def test_exclude_list_blocks_key(self):
        mod = _load_build_release()
        extensions = getattr(mod, "_EXCLUDE_EXTENSIONS", set())
        assert ".key" in extensions

    def test_exclude_list_blocks_rossi_filename(self):
        mod = _load_build_release()
        block_subs = getattr(mod, "_BLOCK_FILENAME_SUBSTRINGS", set())
        assert "rossi" in block_subs

    def test_should_exclude_env_file(self):
        mod = _load_build_release()
        assert mod._should_exclude(".env")

    def test_should_exclude_pem_file(self):
        mod = _load_build_release()
        assert mod._should_exclude("secrets/server.pem")

    def test_should_exclude_leads_mock(self):
        mod = _load_build_release()
        assert mod._should_exclude("data/leads_mock.json")

    def test_should_exclude_client_cases(self):
        mod = _load_build_release()
        assert mod._should_exclude("data/client_cases.json")

    def test_should_exclude_calibration_data(self):
        mod = _load_build_release()
        assert mod._should_exclude("data/human_design_calibration_cases.json")


class TestZipSafetyChecker:
    def test_zip_rejects_forbidden_entry(self):
        mod = _load_build_release()
        safe = mod._zip_entry_safe
        assert not safe("data/leads_mock.json")
        assert not safe(".git/HEAD")
        assert not safe("__pycache__/module.pyc")
        assert not safe("data/client_cases.json")
        assert not safe("some/Rossi_chart.json")
        assert not safe(".env")

    def test_zip_allows_normal_entry(self):
        mod = _load_build_release()
        safe = mod._zip_entry_safe
        assert safe("config.py")
        assert safe("ui/streamlit_app.py")
        assert safe("run.bat")
        assert safe("CUSTOMER_README.md")


class TestReleaseCheckScript:
    def test_release_check_detects_version(self):
        mod = _load_release_check()
        assert hasattr(mod, "EXPECTED_VERSION")
        assert mod.EXPECTED_VERSION == "1.9.9"

    def test_forbidden_keywords_list_includes_password(self):
        mod = _load_release_check()
        forbidden = getattr(mod, "CUSTOMER_README_FORBIDDEN_CI", [])
        forbidden_all = getattr(mod, "CUSTOMER_README_FORBIDDEN", [])
        all_forbidden = [str(x).lower() for x in forbidden + forbidden_all]
        # password or token or api_key must be in the list
        found = any("password" in x or "token" in x or "api_key" in x for x in all_forbidden)
        assert found, f"password/token/api_key not found in forbidden list: {all_forbidden}"

    def test_required_files_list_includes_run_bat(self):
        mod = _load_release_check()
        required = getattr(mod, "REQUIRED_FILES", [])
        assert any("run.bat" in str(f) for f in required)

    def test_required_files_list_includes_customer_readme(self):
        mod = _load_release_check()
        required = getattr(mod, "REQUIRED_FILES", [])
        assert any("CUSTOMER_README" in str(f) for f in required)
