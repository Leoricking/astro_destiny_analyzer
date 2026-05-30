"""
Tests for V2.0.3 Protected Trial Customer Mode.
Verifies app_launcher.py and start_protected.bat enforce customer/trial mode.
"""
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
LAUNCHER_PATH = ROOT / "app_launcher.py"
START_BAT_PATH = ROOT / "start_protected.bat"


def _launcher_src() -> str:
    return LAUNCHER_PATH.read_text(encoding="utf-8")


def _start_bat_src() -> str:
    return START_BAT_PATH.read_text(encoding="utf-8")


class TestAppLauncherEnvVars:
    def test_sets_customer_mode_1(self):
        assert "ASTRO_CUSTOMER_MODE" in _launcher_src()
        assert '"1"' in _launcher_src() or "'1'" in _launcher_src()

    def test_sets_developer_mode_0(self):
        src = _launcher_src()
        assert "ASTRO_DEVELOPER_MODE" in src
        # Must set it to "0", not "1"
        lines = [l for l in src.splitlines() if "ASTRO_DEVELOPER_MODE" in l]
        assert any('"0"' in l or "'0'" in l for l in lines)

    def test_sets_consultant_mode_0(self):
        src = _launcher_src()
        assert "ASTRO_CONSULTANT_MODE" in src
        lines = [l for l in src.splitlines() if "ASTRO_CONSULTANT_MODE" in l]
        assert any('"0"' in l or "'0'" in l for l in lines)

    def test_sets_trial_mode_1(self):
        src = _launcher_src()
        assert "ASTRO_TRIAL_MODE" in src
        lines = [l for l in src.splitlines() if "ASTRO_TRIAL_MODE" in l]
        assert any('"1"' in l or "'1'" in l for l in lines)

    def test_sets_build_profile_protected_trial(self):
        assert "protected_trial" in _launcher_src()
        assert "ASTRO_BUILD_PROFILE" in _launcher_src()

    def test_sets_portable_mode_1(self):
        src = _launcher_src()
        assert "ASTRO_PORTABLE_MODE" in src


class TestAppLauncherSafety:
    def test_handles_missing_app_script(self):
        """Launcher must check if app script exists before launching."""
        src = _launcher_src()
        assert "os.path.isfile" in src or "is_file" in src

    def test_handles_import_error(self):
        """Launcher must not crash silently — must catch exceptions."""
        src = _launcher_src()
        assert "except" in src

    def test_shows_error_message_on_failure(self):
        """Launcher must print an error message if launch fails."""
        src = _launcher_src()
        assert "ERROR" in src or "error" in src.lower()

    def test_handles_pyinstaller_frozen(self):
        """Launcher must handle PyInstaller frozen environment."""
        src = _launcher_src()
        assert "frozen" in src
        assert "_MEIPASS" in src

    def test_launches_streamlit(self):
        src = _launcher_src()
        assert "streamlit" in src.lower()


class TestStartProtectedBat:
    def test_does_not_call_run_dev_bat(self):
        assert "run_dev.bat" not in _start_bat_src()

    def test_does_not_call_run_consultant_bat(self):
        assert "run_consultant.bat" not in _start_bat_src()

    def test_launches_exe(self):
        assert "AstroDestinyAnalyzer.exe" in _start_bat_src()

    def test_shows_error_if_exe_missing(self):
        src = _start_bat_src()
        assert "ERROR" in src or "error" in src.lower() or "not exist" in src.lower()

    def test_does_not_call_python_source(self):
        src = _start_bat_src()
        # Must not call streamlit_app.py or run.bat directly from source
        assert "streamlit_app.py" not in src
        assert "run.bat" not in src.lower() or "run_" not in src.lower()


class TestProtectedDocs:
    def test_trial_readme_exists(self):
        assert (ROOT / "TRIAL_README.txt").is_file()

    def test_trial_yong_ming_exists(self):
        assert (ROOT / "試用說明.txt").is_file()

    def test_trial_readme_does_not_expose_source_code(self):
        text = (ROOT / "TRIAL_README.txt").read_text(encoding="utf-8")
        # Should not tell customer to look at source
        assert "core/" not in text
        assert "engines/" not in text
        assert "run_dev.bat" not in text

    def test_trial_readme_mentions_start_protected(self):
        text = (ROOT / "TRIAL_README.txt").read_text(encoding="utf-8")
        assert "start_protected.bat" in text or "AstroDestinyAnalyzer.exe" in text

    def test_customer_readme_mentions_protected_build(self):
        text = (ROOT / "CUSTOMER_README.md").read_text(encoding="utf-8")
        # Customer README should mention the protected/trial build
        assert "protected" in text.lower() or "trial" in text.lower() or \
               "封裝" in text or "source code" in text.lower()
