"""
Tests for V2.0.2 Release Smoke Test Script.
"""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
SMOKE_TEST_PATH = ROOT / "scripts" / "release_smoke_test.py"


def _load_smoke_test():
    spec = importlib.util.spec_from_file_location(
        "release_smoke_test", str(SMOKE_TEST_PATH)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestSmokeTestScriptExists:
    def test_script_exists(self):
        assert SMOKE_TEST_PATH.is_file()

    def test_script_importable(self):
        mod = _load_smoke_test()
        assert hasattr(mod, "main")
        assert hasattr(mod, "run_smoke_test")


class TestRequiredFilesList:
    def _mod(self):
        return _load_smoke_test()

    def test_customer_required_includes_customer_onboarding(self):
        mod = self._mod()
        required = mod.REQUIRED_FILES_CUSTOMER
        assert any("CUSTOMER_ONBOARDING" in f for f in required)

    def test_customer_required_includes_run_bat(self):
        mod = self._mod()
        required = mod.REQUIRED_FILES_CUSTOMER
        assert any("run.bat" in f for f in required)

    def test_customer_required_includes_version_txt(self):
        mod = self._mod()
        required = mod.REQUIRED_FILES_CUSTOMER
        assert any("VERSION.txt" in f for f in required)

    def test_customer_required_includes_streamlit_app(self):
        mod = self._mod()
        required = mod.REQUIRED_FILES_CUSTOMER
        assert any("streamlit_app.py" in f for f in required)

    def test_customer_required_includes_customer_readme(self):
        mod = self._mod()
        required = mod.REQUIRED_FILES_CUSTOMER
        assert any("CUSTOMER_README" in f for f in required)


class TestForbiddenEntriesList:
    def _mod(self):
        return _load_smoke_test()

    def test_forbidden_all_includes_git(self):
        mod = self._mod()
        assert ".git" in mod.FORBIDDEN_ENTRIES_ALL

    def test_forbidden_all_includes_venv(self):
        mod = self._mod()
        assert ".venv" in mod.FORBIDDEN_ENTRIES_ALL

    def test_forbidden_all_includes_leads_mock(self):
        mod = self._mod()
        assert any("leads_mock" in e for e in mod.FORBIDDEN_ENTRIES_ALL)

    def test_forbidden_customer_extra_includes_run_dev_bat(self):
        mod = self._mod()
        assert any("run_dev.bat" in e for e in mod.FORBIDDEN_ENTRIES_CUSTOMER_EXTRA)


class TestForbiddenEntryHelper:
    def _mod(self):
        return _load_smoke_test()

    def test_rejects_git_entry(self):
        mod = self._mod()
        assert mod._is_forbidden_entry(".git/config", "customer")

    def test_rejects_venv_entry(self):
        mod = self._mod()
        assert mod._is_forbidden_entry(".venv/Scripts/python.exe", "customer")

    def test_rejects_leads_mock(self):
        mod = self._mod()
        assert mod._is_forbidden_entry("data/leads_mock.json", "customer")

    def test_rejects_rossi(self):
        mod = self._mod()
        assert mod._is_forbidden_entry("Rossi_chart.json", "customer")

    def test_rejects_run_dev_bat_for_customer(self):
        mod = self._mod()
        assert mod._is_forbidden_entry("run_dev.bat", "customer")

    def test_rejects_tests_for_customer(self):
        mod = self._mod()
        assert mod._is_forbidden_entry("tests/test_foo.py", "customer")

    def test_allows_safe_entry(self):
        mod = self._mod()
        assert not mod._is_forbidden_entry("ui/streamlit_app.py", "customer")
        assert not mod._is_forbidden_entry("config.py", "customer")
        assert not mod._is_forbidden_entry("run.bat", "customer")
        assert not mod._is_forbidden_entry("CUSTOMER_README.md", "customer")
        assert not mod._is_forbidden_entry("CUSTOMER_ONBOARDING.md", "customer")


class TestVersionCheck:
    def test_expected_version_is_202(self):
        mod = _load_smoke_test()
        assert mod.EXPECTED_VERSION == "2.0.3"


class TestOptionalDemoCheck:
    def _mod(self):
        return _load_smoke_test()

    def test_smoke_test_has_optional_demo_check(self):
        """Smoke test must verify optional demo import fallback in ZIP."""
        src = SMOKE_TEST_PATH.read_text(encoding="utf-8")
        assert "except ModuleNotFoundError" in src or "SAMPLE_PROFILES = {}" in src

    def test_safe_entry_allows_no_demo(self):
        """ZIP without demo/ should not be flagged as unsafe."""
        mod = self._mod()
        # demo/ absence is expected for customer/consultant — no forbidden entry for it
        assert not mod._is_forbidden_entry("config.py", "customer")
        assert not mod._is_forbidden_entry("ui/streamlit_app.py", "customer")

    def test_customer_zip_may_exclude_demo(self):
        """customer profile does NOT require demo/ in ZIP."""
        mod = self._mod()
        required = mod.REQUIRED_FILES_CUSTOMER
        assert not any("demo" in f.lower() for f in required)

    def test_consultant_zip_may_exclude_demo(self):
        """consultant profile does NOT require demo/ in ZIP."""
        mod = self._mod()
        required = mod.REQUIRED_FILES_CONSULTANT
        assert not any("demo" in f.lower() for f in required)
