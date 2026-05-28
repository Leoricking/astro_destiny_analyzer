"""
Tests for V1.6.2 Windows launcher scripts.
Verifies run.bat, setup.bat, and scripts/check_env.py exist and have
the correct content.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib
import pytest

# Project root is one level up from tests/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(rel_path: str) -> str:
    full = os.path.join(PROJECT_ROOT, rel_path)
    with open(full, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


# ══════════════════════════════════════════════════════════════════════════════
# A. File existence
# ══════════════════════════════════════════════════════════════════════════════

class TestFilesExist:
    def test_run_bat_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "run.bat"))

    def test_setup_bat_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "setup.bat"))

    def test_check_env_py_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "scripts", "check_env.py"))

    def test_scripts_init_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "scripts", "__init__.py"))


# ══════════════════════════════════════════════════════════════════════════════
# B. run.bat content
# ══════════════════════════════════════════════════════════════════════════════

class TestRunBat:
    @pytest.fixture(scope="class")
    def content(self):
        return _read("run.bat")

    def test_references_venv_python(self, content):
        assert r".venv\Scripts\python" in content or ".venv/Scripts/python" in content

    def test_references_streamlit_run(self, content):
        assert "streamlit run ui" in content.replace("\\", "/") or \
               r"streamlit run ui\streamlit_app.py" in content

    def test_references_check_env(self, content):
        assert "check_env.py" in content

    def test_does_not_use_activate_ps1(self, content):
        assert "activate.ps1" not in content

    def test_references_requirements(self, content):
        assert "requirements.txt" in content

    def test_has_step_markers(self, content):
        assert "[1/5]" in content
        assert "[5/5]" in content

    def test_has_error_handling(self, content):
        assert "pause" in content.lower()
        assert "exit /b 1" in content

    def test_has_cd_to_bat_dir(self, content):
        assert "%~dp0" in content


# ══════════════════════════════════════════════════════════════════════════════
# C. setup.bat content
# ══════════════════════════════════════════════════════════════════════════════

class TestSetupBat:
    @pytest.fixture(scope="class")
    def content(self):
        return _read("setup.bat")

    def test_creates_venv(self, content):
        assert "python -m venv .venv" in content

    def test_installs_requirements(self, content):
        assert "pip install -r requirements.txt" in content

    def test_references_check_env(self, content):
        assert "check_env.py" in content

    def test_has_success_message(self, content):
        assert "run.bat" in content

    def test_has_error_handling(self, content):
        assert "pause" in content.lower()
        assert "exit /b 1" in content

    def test_has_cd_to_bat_dir(self, content):
        assert "%~dp0" in content


# ══════════════════════════════════════════════════════════════════════════════
# D. scripts/check_env.py — importability and structure
# ══════════════════════════════════════════════════════════════════════════════

class TestCheckEnvPy:
    def test_importable(self):
        """Importing check_env should NOT call sys.exit."""
        import scripts.check_env as check_env  # noqa
        assert check_env is not None

    def test_has_main_function(self):
        import scripts.check_env as check_env
        assert callable(getattr(check_env, "main", None))

    def test_main_returns_int(self):
        import scripts.check_env as check_env
        result = check_env.main()
        assert isinstance(result, int)

    def test_main_returns_0_or_1(self):
        import scripts.check_env as check_env
        result = check_env.main()
        assert result in (0, 1)

    def test_has_check_import_helper(self):
        import scripts.check_env as check_env
        assert callable(getattr(check_env, "_check_import", None))

    def test_check_import_true_for_sys(self):
        import scripts.check_env as check_env
        assert check_env._check_import("sys") is True

    def test_check_import_false_for_nonexistent(self):
        import scripts.check_env as check_env
        assert check_env._check_import("_nonexistent_pkg_xyz_") is False

    def test_has_ensure_dir_helper(self):
        import scripts.check_env as check_env
        assert callable(getattr(check_env, "_ensure_dir", None))

    def test_does_not_exit_on_import(self):
        """Re-importing should be safe even if packages are missing."""
        import importlib
        import scripts.check_env as check_env
        importlib.reload(check_env)  # should not raise SystemExit


# ══════════════════════════════════════════════════════════════════════════════
# E. README contains launcher documentation
# ══════════════════════════════════════════════════════════════════════════════

class TestReadmeLauncher:
    @pytest.fixture(scope="class")
    def readme(self):
        return _read("README.md")

    def test_mentions_run_bat(self, readme):
        assert "run.bat" in readme

    def test_mentions_setup_bat(self, readme):
        assert "setup.bat" in readme

    def test_mentions_one_click(self, readme):
        assert "一鍵" in readme or "double" in readme.lower() or "雙擊" in readme


# ══════════════════════════════════════════════════════════════════════════════
# F. V1.8.3 — Encoding settings in launchers
# ══════════════════════════════════════════════════════════════════════════════

class TestEncodingSettings:
    def test_run_bat_has_pythonutf8(self):
        assert "PYTHONUTF8" in _read("run.bat")

    def test_run_bat_has_pythonioencoding(self):
        assert "PYTHONIOENCODING" in _read("run.bat")

    def test_run_bat_no_developer_mode_flag(self):
        assert "ASTRO_DEVELOPER_MODE=1" not in _read("run.bat")

    def test_setup_bat_has_pythonutf8(self):
        assert "PYTHONUTF8" in _read("setup.bat")

    def test_setup_bat_has_pythonioencoding(self):
        assert "PYTHONIOENCODING" in _read("setup.bat")

    def test_setup_bat_has_success_message(self):
        content = _read("setup.bat")
        assert "安裝完成" in content and "run.bat" in content


# ══════════════════════════════════════════════════════════════════════════════
# G. V1.8.3 — run_dev.bat
# ══════════════════════════════════════════════════════════════════════════════

class TestRunDevBat:
    def test_run_dev_bat_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "run_dev.bat"))

    def test_run_dev_bat_has_developer_mode(self):
        assert "ASTRO_DEVELOPER_MODE=1" in _read("run_dev.bat")

    def test_run_dev_bat_has_pythonutf8(self):
        assert "PYTHONUTF8" in _read("run_dev.bat")

    def test_run_dev_bat_has_pythonioencoding(self):
        assert "PYTHONIOENCODING" in _read("run_dev.bat")

    def test_run_dev_bat_references_streamlit(self):
        assert "streamlit run" in _read("run_dev.bat")

    def test_run_dev_bat_has_dev_mode_title(self):
        assert "DEV" in _read("run_dev.bat").upper()


# ══════════════════════════════════════════════════════════════════════════════
# H. V1.8.3 — install_pdf_support.bat
# ══════════════════════════════════════════════════════════════════════════════

class TestInstallPdfSupportBat:
    def test_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "install_pdf_support.bat"))

    def test_references_weasyprint(self):
        assert "weasyprint" in _read("install_pdf_support.bat").lower()

    def test_has_encoding_settings(self):
        assert "PYTHONUTF8" in _read("install_pdf_support.bat")

    def test_has_failure_message(self):
        content = _read("install_pdf_support.bat")
        assert "GTK" in content or "Pango" in content

    def test_has_venv_check(self):
        assert ".venv" in _read("install_pdf_support.bat")


# ══════════════════════════════════════════════════════════════════════════════
# I. V1.8.4 — Customer delivery mode flags in launchers
# ══════════════════════════════════════════════════════════════════════════════

class TestCustomerDeliveryFlags:
    def test_run_bat_has_customer_mode_on(self):
        assert "ASTRO_CUSTOMER_MODE=1" in _read("run.bat")

    def test_run_bat_has_show_demo_data_off(self):
        assert "ASTRO_SHOW_DEMO_DATA=0" in _read("run.bat")

    def test_run_dev_bat_has_customer_mode_off(self):
        assert "ASTRO_CUSTOMER_MODE=0" in _read("run_dev.bat")

    def test_run_dev_bat_has_show_demo_data_on(self):
        assert "ASTRO_SHOW_DEMO_DATA=1" in _read("run_dev.bat")
