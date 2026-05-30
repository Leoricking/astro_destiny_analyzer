"""
Tests for V2.0.3 Protected Trial Customer Mode.
Verifies app_launcher.py and start_protected.bat enforce customer/trial mode.
"""
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
LAUNCHER_PATH = ROOT / "app_launcher.py"
START_BAT_PATH = ROOT / "start_protected.bat"


STUB_PATH = ROOT / "protected_streamlit_entry.py"


def _launcher_src() -> str:
    return LAUNCHER_PATH.read_text(encoding="utf-8")


def _start_bat_src() -> str:
    return START_BAT_PATH.read_text(encoding="utf-8")


def _stub_src() -> str:
    return STUB_PATH.read_text(encoding="utf-8")


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

    def test_points_to_subdirectory_exe(self):
        src = _start_bat_src()
        # EXE must be in AstroDestinyAnalyzer\ subdirectory (PyInstaller one-folder)
        assert "AstroDestinyAnalyzer\\AstroDestinyAnalyzer.exe" in src \
               or "AstroDestinyAnalyzer/AstroDestinyAnalyzer.exe" in src

    def test_does_not_point_to_same_folder_exe(self):
        src = _start_bat_src()
        # Must NOT have bare SCRIPT_DIR%AstroDestinyAnalyzer.exe (wrong path)
        lines_with_exe = [l.strip() for l in src.splitlines()
                          if "AstroDestinyAnalyzer.exe" in l and "set " in l.lower()]
        for line in lines_with_exe:
            # Every EXE set line must include the subdirectory
            assert "AstroDestinyAnalyzer\\AstroDestinyAnalyzer.exe" in line \
                   or "AstroDestinyAnalyzer/AstroDestinyAnalyzer.exe" in line, \
                   f"EXE path missing subdirectory: {line}"


class TestAppLauncherBrowserAutoOpen:
    """Verifies app_launcher.py auto-opens browser after server is ready."""

    def test_uses_socket_create_connection(self):
        assert "socket.create_connection" in _launcher_src()

    def test_uses_threading_thread(self):
        assert "threading.Thread" in _launcher_src()

    def test_uses_webbrowser_open(self):
        assert "webbrowser.open" in _launcher_src()

    def test_opens_127_0_0_1_8501(self):
        assert "127.0.0.1:8501" in _launcher_src()

    def test_does_not_open_localhost_3000(self):
        assert "localhost:3000" not in _launcher_src()
        assert ":3000" not in _launcher_src()

    def test_has_wait_for_server(self):
        assert "_wait_for_server" in _launcher_src()

    def test_has_open_browser_when_ready(self):
        assert "_open_browser_when_ready" in _launcher_src()

    def test_browser_thread_is_daemon(self):
        src = _launcher_src()
        assert "daemon=True" in src


class TestAppLauncherPortConfig:
    """Verifies app_launcher.py forces Streamlit to port 8501 on 127.0.0.1."""

    def test_clears_port_env_var(self):
        src = _launcher_src()
        assert 'pop("PORT"' in src or "pop('PORT'" in src

    def test_sets_global_development_mode_false(self):
        src = _launcher_src()
        assert "STREAMLIT_GLOBAL_DEVELOPMENT_MODE" in src

    def test_sets_global_development_mode_cli(self):
        src = _launcher_src()
        assert "global.developmentMode" in src

    def test_sets_development_mode_to_false(self):
        src = _launcher_src()
        lines = [l for l in src.splitlines()
                 if "developmentMode" in l or "DEVELOPMENT_MODE" in l]
        assert any("false" in l.lower() or "False" in l for l in lines)

    def test_sets_server_port_8501(self):
        src = _launcher_src()
        assert "8501" in src
        assert "STREAMLIT_SERVER_PORT" in src or "server.port" in src

    def test_sets_browser_server_port(self):
        src = _launcher_src()
        assert "browser.serverPort" in src or "STREAMLIT_BROWSER_SERVER_PORT" in src

    def test_sets_server_address_127(self):
        src = _launcher_src()
        assert "127.0.0.1" in src

    def test_does_not_mention_port_3000(self):
        src = _launcher_src()
        assert "localhost:3000" not in src
        assert ":3000" not in src

    def test_prints_local_url_8501(self):
        src = _launcher_src()
        assert "127.0.0.1:8501" in src


class TestStartBatPortConfig:
    """Verifies start_protected.bat forces port 8501 and clears PORT."""

    def test_clears_port(self):
        src = _start_bat_src()
        assert "PORT=" in src

    def test_sets_global_development_mode_false(self):
        src = _start_bat_src()
        assert "STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false" in src

    def test_sets_streamlit_server_port_8501(self):
        src = _start_bat_src()
        assert "STREAMLIT_SERVER_PORT=8501" in src

    def test_sets_streamlit_server_address(self):
        src = _start_bat_src()
        assert "127.0.0.1" in src

    def test_shows_url_127_0_0_1_8501(self):
        src = _start_bat_src()
        assert "127.0.0.1:8501" in src

    def test_does_not_mention_localhost_3000(self):
        src = _start_bat_src()
        assert "localhost:3000" not in src
        assert ":3000" not in src


class TestStartBatWindowsSyntax:
    """Verifies start_protected.bat uses pure Windows batch syntax."""

    def test_has_quoted_script_dir(self):
        src = _start_bat_src()
        assert 'set "SCRIPT_DIR=%~dp0"' in src

    def test_has_quoted_exe_path(self):
        src = _start_bat_src()
        assert 'set "EXE=%SCRIPT_DIR%AstroDestinyAnalyzer\\AstroDestinyAnalyzer.exe"' in src

    def test_no_dollar_env(self):
        src = _start_bat_src()
        assert "$env" not in src.lower()

    def test_no_env_colon(self):
        src = _start_bat_src()
        assert "env:" not in src.lower()

    def test_no_bare_dp0_without_percent(self):
        # After removing valid %~dp0 occurrences, bare ~dp0 must not remain
        src = _start_bat_src()
        assert "~dp0" not in src.replace("%~dp0", "")

    def test_has_expected_exe_in_error(self):
        src = _start_bat_src()
        assert "Expected: %EXE%" in src

    def test_shows_url_127_0_0_1_8501(self):
        src = _start_bat_src()
        assert "127.0.0.1:8501" in src

    def test_has_development_mode_false(self):
        src = _start_bat_src()
        assert "STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false" in src


class TestProtectedEntryStub:
    """Verifies protected_streamlit_entry.py stub has port/devmode reinforcement."""

    def test_stub_sets_global_development_mode_false(self):
        src = _stub_src()
        assert "STREAMLIT_GLOBAL_DEVELOPMENT_MODE" in src

    def test_stub_sets_server_port(self):
        src = _stub_src()
        assert "STREAMLIT_SERVER_PORT" in src

    def test_stub_does_not_contain_app_source(self):
        src = _stub_src()
        # Stub must remain minimal — no business logic
        assert "st.title" not in src
        assert "st.sidebar" not in src


class TestAppLauncherStubUsage:
    """Verifies app_launcher.py uses the minimal stub, not the full source."""

    def test_launcher_uses_protected_entry_stub(self):
        src = _launcher_src()
        assert "protected_streamlit_entry.py" in src

    def test_launcher_does_not_reference_ui_streamlit_app_as_data(self):
        src = _launcher_src()
        # The launcher must not construct a path joining "ui" + "streamlit_app.py"
        lines = [l for l in src.splitlines()
                 if "streamlit_app.py" in l and '"ui"' in l]
        assert len(lines) == 0, (
            f"Launcher still references ui/streamlit_app.py path: {lines}"
        )


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
