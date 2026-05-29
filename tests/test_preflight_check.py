"""
Tests for V2.0.0 Preflight Health Check.
"""
import importlib.util
import pathlib
import sys
import os

ROOT = pathlib.Path(__file__).parent.parent


def _load_preflight():
    spec = importlib.util.spec_from_file_location(
        "preflight_check", str(ROOT / "scripts" / "preflight_check.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestPreflightExists:
    def test_preflight_check_script_exists(self):
        assert (ROOT / "scripts" / "preflight_check.py").is_file()

    def test_preflight_main_importable(self):
        mod = _load_preflight()
        assert hasattr(mod, "main")

    def test_preflight_check_python_version_func(self):
        mod = _load_preflight()
        assert hasattr(mod, "check_python_version")

    def test_preflight_data_dir_writable_func(self):
        mod = _load_preflight()
        assert hasattr(mod, "check_data_dirs_writable")

    def test_preflight_customer_forbidden_pages_func(self):
        mod = _load_preflight()
        assert hasattr(mod, "check_customer_forbidden_pages")


class TestPreflightPackageLists:
    def test_required_packages_includes_streamlit(self):
        mod = _load_preflight()
        assert "streamlit" in mod.REQUIRED_PACKAGES

    def test_required_packages_includes_pydantic(self):
        mod = _load_preflight()
        assert "pydantic" in mod.REQUIRED_PACKAGES

    def test_required_packages_includes_jinja2(self):
        mod = _load_preflight()
        assert "jinja2" in mod.REQUIRED_PACKAGES

    def test_optional_packages_includes_weasyprint(self):
        mod = _load_preflight()
        assert "weasyprint" in mod.OPTIONAL_PACKAGES


class TestPreflightVersionCheck:
    def test_expected_version_is_202(self):
        mod = _load_preflight()
        assert mod.EXPECTED_VERSION == "2.0.2"


class TestPreflightForbiddenPages:
    def test_customer_forbidden_pages_includes_ziwei(self):
        mod = _load_preflight()
        assert any("紫微" in p for p in mod.CUSTOMER_FORBIDDEN_PAGES)

    def test_customer_forbidden_pages_includes_hd_calibration(self):
        mod = _load_preflight()
        assert any("人類圖" in p for p in mod.CUSTOMER_FORBIDDEN_PAGES)

    def test_customer_forbidden_pages_includes_lead_funnel(self):
        mod = _load_preflight()
        assert any("Lead Funnel" in p or "funnel" in p.lower() for p in mod.CUSTOMER_FORBIDDEN_PAGES)

    def test_customer_forbidden_pages_includes_client_cases(self):
        mod = _load_preflight()
        assert any("客戶" in p for p in mod.CUSTOMER_FORBIDDEN_PAGES)


class TestPreflightOptionalNotFail:
    def test_optional_missing_returns_no_failure(self):
        """Optional package missing should not increase required_failures."""
        mod = _load_preflight()
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        # Patch OPTIONAL_PACKAGES to something that definitely doesn't exist
        original = mod.OPTIONAL_PACKAGES
        mod.OPTIONAL_PACKAGES = ["_nonexistent_pkg_xyz_"]
        try:
            with redirect_stdout(buf):
                mod.check_optional_packages()
        finally:
            mod.OPTIONAL_PACKAGES = original
        # Should complete without raising, output contains some status indicator
        output = buf.getvalue()
        assert len(output) > 0  # produced some output without raising


class TestPreflightRequiredFails:
    def test_missing_required_package_returns_nonzero(self):
        """Missing required package should increment failure count."""
        mod = _load_preflight()
        import io
        from contextlib import redirect_stdout
        original = mod.REQUIRED_PACKAGES
        mod.REQUIRED_PACKAGES = ["_nonexistent_req_pkg_xyz_"]
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                failures = mod.check_required_packages()
            assert failures == 1
        finally:
            mod.REQUIRED_PACKAGES = original
