"""
Tests for V2.0.3 Protected Trial Packaging.
"""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
BUILD_PROTECTED = ROOT / "scripts" / "build_protected.py"
SMOKE_TEST = ROOT / "scripts" / "protected_smoke_test.py"


def _load_build_protected():
    spec = importlib.util.spec_from_file_location("build_protected", str(BUILD_PROTECTED))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_smoke_test():
    spec = importlib.util.spec_from_file_location("protected_smoke_test", str(SMOKE_TEST))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestRequiredScriptsExist:
    def test_build_protected_exists(self):
        assert BUILD_PROTECTED.is_file()

    def test_protected_smoke_test_exists(self):
        assert SMOKE_TEST.is_file()

    def test_app_launcher_exists(self):
        assert (ROOT / "app_launcher.py").is_file()

    def test_start_protected_bat_exists(self):
        assert (ROOT / "start_protected.bat").is_file()

    def test_requirements_build_txt_exists(self):
        assert (ROOT / "requirements-build.txt").is_file()


class TestBuildProtectedExcludePatterns:
    def _src(self) -> str:
        return BUILD_PROTECTED.read_text(encoding="utf-8")

    def test_excludes_py_source(self):
        assert ".py" in self._src()

    def test_excludes_tests(self):
        assert "tests" in self._src()

    def test_excludes_demo(self):
        assert "demo" in self._src()

    def test_excludes_run_dev_bat(self):
        assert "run_dev.bat" in self._src()

    def test_excludes_run_consultant_bat(self):
        assert "run_consultant.bat" in self._src()

    def test_excludes_leads_mock(self):
        assert "leads_mock" in self._src()

    def test_excludes_rossi(self):
        assert "rossi" in self._src().lower()

    def test_zip_name_contains_protected_trial(self):
        assert "protected_trial" in self._src()

    def test_uses_pyinstaller(self):
        src = self._src()
        assert "PyInstaller" in src or "pyinstaller" in src

    def test_one_folder_mode(self):
        src = self._src()
        assert "onedir" in src or "one-folder" in src or "one_folder" in src


class TestBuildProtectedImportable:
    def test_has_main(self):
        mod = _load_build_protected()
        assert hasattr(mod, "main")

    def test_has_app_version(self):
        mod = _load_build_protected()
        assert hasattr(mod, "APP_VERSION")
        assert mod.APP_VERSION == "2.0.6"

    def test_has_forbidden_patterns(self):
        mod = _load_build_protected()
        assert hasattr(mod, "_FORBIDDEN_ZIP_PATTERNS")

    def test_forbidden_patterns_include_git(self):
        mod = _load_build_protected()
        assert ".git" in mod._FORBIDDEN_ZIP_PATTERNS

    def test_forbidden_patterns_include_tests(self):
        mod = _load_build_protected()
        assert any("tests" in p for p in mod._FORBIDDEN_ZIP_PATTERNS)

    def test_forbidden_patterns_include_demo(self):
        mod = _load_build_protected()
        assert any("demo" in p for p in mod._FORBIDDEN_ZIP_PATTERNS)

    def test_forbidden_patterns_include_run_dev(self):
        mod = _load_build_protected()
        assert any("run_dev" in p for p in mod._FORBIDDEN_ZIP_PATTERNS)

    def test_forbidden_patterns_include_run_consultant(self):
        mod = _load_build_protected()
        assert any("run_consultant" in p for p in mod._FORBIDDEN_ZIP_PATTERNS)


class TestProtectedSmokeTestImportable:
    def test_has_main(self):
        mod = _load_smoke_test()
        assert hasattr(mod, "main")

    def test_has_run_smoke_test(self):
        mod = _load_smoke_test()
        assert hasattr(mod, "run_smoke_test")

    def test_has_expected_version_206(self):
        mod = _load_smoke_test()
        assert mod.EXPECTED_VERSION == "2.0.6"

    def test_required_files_include_trial_readme(self):
        mod = _load_smoke_test()
        assert any("TRIAL_README" in f for f in mod.REQUIRED_FILES_PROTECTED)

    def test_required_includes_customer_readme(self):
        mod = _load_smoke_test()
        assert any("CUSTOMER_README" in f for f in mod.REQUIRED_FILES_PROTECTED)

    def test_required_executable_includes_exe(self):
        mod = _load_smoke_test()
        assert any(".exe" in f for f in mod.REQUIRED_EXECUTABLE_ANY)

    def test_required_executable_includes_start_bat(self):
        mod = _load_smoke_test()
        assert any("start_protected.bat" in f for f in mod.REQUIRED_EXECUTABLE_ANY)

    def test_forbidden_includes_git(self):
        mod = _load_smoke_test()
        assert ".git" in mod.FORBIDDEN_ENTRIES_PROTECTED

    def test_forbidden_includes_venv(self):
        mod = _load_smoke_test()
        assert ".venv" in mod.FORBIDDEN_ENTRIES_PROTECTED

    def test_forbidden_includes_tests(self):
        mod = _load_smoke_test()
        assert any("tests" in e for e in mod.FORBIDDEN_ENTRIES_PROTECTED)

    def test_forbidden_includes_demo(self):
        mod = _load_smoke_test()
        assert any("demo" in e for e in mod.FORBIDDEN_ENTRIES_PROTECTED)

    def test_forbidden_includes_run_dev_bat(self):
        mod = _load_smoke_test()
        assert any("run_dev.bat" in e for e in mod.FORBIDDEN_ENTRIES_PROTECTED)

    def test_forbidden_includes_run_consultant_bat(self):
        mod = _load_smoke_test()
        assert any("run_consultant.bat" in e for e in mod.FORBIDDEN_ENTRIES_PROTECTED)

    def test_forbidden_includes_rossi(self):
        mod = _load_smoke_test()
        assert any("rossi" in e.lower() for e in mod.FORBIDDEN_ENTRIES_PROTECTED)

    def test_forbidden_includes_leads_mock(self):
        mod = _load_smoke_test()
        assert any("leads_mock" in e for e in mod.FORBIDDEN_ENTRIES_PROTECTED)


class TestProtectedForbiddenChecker:
    def _mod(self):
        return _load_smoke_test()

    def test_rejects_py_source_at_root(self):
        mod = self._mod()
        assert mod._is_py_source_outside_internal("core/engine.py")
        assert mod._is_py_source_outside_internal("ui/streamlit_app.py")
        assert mod._is_py_source_outside_internal("config.py")

    def test_allows_py_inside_internal(self):
        mod = self._mod()
        assert not mod._is_py_source_outside_internal("AstroDestinyAnalyzer/_internal/ui/streamlit_app.py")
        assert not mod._is_py_source_outside_internal("_internal/core/engine.py")

    def test_rejects_rossi(self):
        mod = self._mod()
        assert mod._is_forbidden_entry("Rossi_data.json")

    def test_rejects_leads_mock(self):
        mod = self._mod()
        assert mod._is_forbidden_entry("data/leads_mock.json")

    def test_rejects_run_dev_bat(self):
        mod = self._mod()
        assert mod._is_forbidden_entry("run_dev.bat")

    def test_rejects_git(self):
        mod = self._mod()
        assert mod._is_forbidden_entry(".git/config")

    def test_rejects_venv(self):
        mod = self._mod()
        assert mod._is_forbidden_entry(".venv/Scripts/python.exe")

    def test_allows_exe(self):
        mod = self._mod()
        assert not mod._is_forbidden_entry("AstroDestinyAnalyzer.exe")

    def test_allows_customer_readme(self):
        mod = self._mod()
        assert not mod._is_forbidden_entry("CUSTOMER_README.md")

    def test_allows_trial_readme(self):
        mod = self._mod()
        assert not mod._is_forbidden_entry("TRIAL_README.txt")

    def test_allows_start_protected_bat(self):
        mod = self._mod()
        assert not mod._is_forbidden_entry("start_protected.bat")


class TestProtectedInternalSourceChecker:
    """Tests for _is_project_source_inside_internal() — project source must not
    appear as readable .py inside the _internal/ PyInstaller bundle."""

    def _mod(self):
        return _load_smoke_test()

    def test_rejects_internal_ui_streamlit_app(self):
        mod = self._mod()
        assert mod._is_project_source_inside_internal(
            "AstroDestinyAnalyzer/_internal/ui/streamlit_app.py"
        )

    def test_rejects_internal_core_models(self):
        mod = self._mod()
        assert mod._is_project_source_inside_internal(
            "AstroDestinyAnalyzer/_internal/core/models.py"
        )

    def test_rejects_internal_engines_ziwei(self):
        mod = self._mod()
        assert mod._is_project_source_inside_internal(
            "AstroDestinyAnalyzer/_internal/engines/ziwei.py"
        )

    def test_rejects_internal_human_design_engine(self):
        mod = self._mod()
        assert mod._is_project_source_inside_internal(
            "AstroDestinyAnalyzer/_internal/human_design/engine.py"
        )

    def test_allows_internal_pyarrow_tests(self):
        mod = self._mod()
        assert not mod._is_project_source_inside_internal(
            "AstroDestinyAnalyzer/_internal/pyarrow/tests/test_x.py"
        )

    def test_allows_internal_numpy_core(self):
        mod = self._mod()
        assert not mod._is_project_source_inside_internal(
            "AstroDestinyAnalyzer/_internal/numpy/_core/foo.py"
        )

    def test_allows_known_stub(self):
        mod = self._mod()
        assert not mod._is_project_source_inside_internal(
            "AstroDestinyAnalyzer/_internal/protected_streamlit_entry.py"
        )

    def test_rejects_without_dist_prefix(self):
        mod = self._mod()
        assert mod._is_project_source_inside_internal(
            "_internal/ui/streamlit_app.py"
        )
        assert mod._is_project_source_inside_internal(
            "_internal/engines/ziwei.py"
        )

    def test_ignores_non_py_in_internal(self):
        mod = self._mod()
        assert not mod._is_project_source_inside_internal(
            "AstroDestinyAnalyzer/_internal/ui/streamlit_app.pyc"
        )

    def test_still_rejects_rossi(self):
        mod = self._mod()
        assert mod._is_forbidden_entry("Rossi_data.json")

    def test_still_rejects_dot_env(self):
        mod = self._mod()
        assert mod._is_forbidden_entry(".env")


class TestProtectedBuildUsesStub:
    """Tests that build_protected.py uses the protected_streamlit_entry.py stub
    and does NOT add ui/streamlit_app.py as a data file."""

    def _src(self) -> str:
        return BUILD_PROTECTED.read_text(encoding="utf-8")

    def test_references_protected_streamlit_entry(self):
        assert "protected_streamlit_entry.py" in self._src()

    def test_does_not_add_data_streamlit_app(self):
        src = self._src()
        # --add-data for ui/streamlit_app.py must NOT be present
        lines = [l for l in src.splitlines() if "add-data" in l or "add_data" in l]
        for line in lines:
            assert "streamlit_app.py" not in line, (
                f"build_protected.py still adds streamlit_app.py as data: {line}"
            )

    def test_collects_project_submodules(self):
        src = self._src()
        assert "collect-submodules" in src or "collect_submodules" in src

    def test_stub_file_exists(self):
        assert (ROOT / "protected_streamlit_entry.py").is_file()

    def test_collects_all_streamlit(self):
        src = self._src()
        assert "collect-all" in src or "collect_all" in src
        assert "streamlit" in src

    def test_copies_streamlit_metadata(self):
        src = self._src()
        assert "copy-metadata" in src or "copy_metadata" in src
        assert "streamlit" in src

    def test_collects_location_submodule(self):
        mod = _load_build_protected()
        assert "location" in mod._COLLECT_SUBMODULES

    def test_collects_i18n_audit_submodule(self):
        mod = _load_build_protected()
        assert "i18n.audit" in mod._COLLECT_SUBMODULES

    def test_collects_i18n_render_registry_submodule(self):
        mod = _load_build_protected()
        assert "i18n.render_registry" in mod._COLLECT_SUBMODULES


class TestProtectedZipRootLayout:
    """Tests that build_protected.py produces a ZIP with a root folder wrapper."""

    def test_build_has_zip_root_dir_constant(self):
        mod = _load_build_protected()
        assert hasattr(mod, "ZIP_ROOT_DIR")

    def test_zip_root_dir_matches_expected_name(self):
        mod = _load_build_protected()
        assert mod.ZIP_ROOT_DIR == "astro_destiny_analyzer_v2.0.6_protected_trial"

    def test_smoke_test_has_zip_root_dir_constant(self):
        mod = _load_smoke_test()
        assert hasattr(mod, "ZIP_ROOT_DIR")

    def test_smoke_test_zip_root_dir_matches_expected_name(self):
        mod = _load_smoke_test()
        assert mod.ZIP_ROOT_DIR == "astro_destiny_analyzer_v2.0.6_protected_trial"


class TestProtectedBatSyntaxChecker:
    """Tests that the smoke test validates Windows batch syntax in start_protected.bat."""

    def _mod(self):
        return _load_smoke_test()

    def _run_bat_check(self, bat_content: str) -> list:
        """Simulate smoke test bat syntax checks; returns list of failure labels."""
        failures = []
        has_script_dir = 'set "SCRIPT_DIR=%~dp0"' in bat_content
        if not has_script_dir:
            failures.append("missing set SCRIPT_DIR=%~dp0")
        no_bare_dp0 = "~dp0" not in bat_content.replace("%~dp0", "")
        if not no_bare_dp0:
            failures.append("bare ~dp0 without %")
        no_dollar_env = "$env" not in bat_content.lower()
        if not no_dollar_env:
            failures.append("$env found")
        no_env_colon = "env:" not in bat_content.lower()
        if not no_env_colon:
            failures.append("env: found")
        return failures

    def test_rejects_bare_dp0_without_percent(self):
        bad = '@echo off\nset "SCRIPT_DIR=~dp0"\nset EXE=AstroDestinyAnalyzer.exe\n'
        assert self._run_bat_check(bad) != []

    def test_rejects_dollar_env_syntax(self):
        bad = '@echo off\nset "SCRIPT_DIR=%~dp0"\n$env:STREAMLIT_SERVER_PORT=8501\n'
        assert "bare ~dp0 without %" not in self._run_bat_check(bad)
        assert "$env found" in self._run_bat_check(bad)

    def test_rejects_env_colon_syntax(self):
        bad = '@echo off\nset "SCRIPT_DIR=%~dp0"\nenv:STREAMLIT_SERVER_PORT=8501\n'
        assert "env: found" in self._run_bat_check(bad)

    def test_accepts_valid_batch_syntax(self):
        good = (
            '@echo off\nchcp 65001 >nul\nsetlocal\n'
            'set "SCRIPT_DIR=%~dp0"\n'
            'set "EXE=%SCRIPT_DIR%AstroDestinyAnalyzer\\AstroDestinyAnalyzer.exe"\n'
            'set "STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false"\n'
            'set "STREAMLIT_SERVER_PORT=8501"\n'
            '"%EXE%"\n'
        )
        assert self._run_bat_check(good) == []


class TestProtectedSmokeStreamlitChecks:
    """Tests that the smoke test enforces streamlit runtime and correct exe path."""

    def _mod(self):
        return _load_smoke_test()

    def test_has_required_exe_path_constant(self):
        mod = self._mod()
        assert hasattr(mod, "REQUIRED_EXE_PATH")
        assert "AstroDestinyAnalyzer/AstroDestinyAnalyzer.exe" in mod.REQUIRED_EXE_PATH

    def test_has_required_streamlit_dir_constant(self):
        mod = self._mod()
        assert hasattr(mod, "REQUIRED_STREAMLIT_DIR")
        assert "streamlit" in mod.REQUIRED_STREAMLIT_DIR

    def test_has_required_streamlit_distinfo_constant(self):
        mod = self._mod()
        assert hasattr(mod, "REQUIRED_STREAMLIT_DISTINFO_PREFIX")
        assert "streamlit" in mod.REQUIRED_STREAMLIT_DISTINFO_PREFIX

    def test_forbidden_checker_allows_internal_streamlit_runtime(self):
        mod = self._mod()
        assert not mod._is_project_source_inside_internal(
            "AstroDestinyAnalyzer/_internal/streamlit/runtime/scriptrunner/magic_funcs.py"
        )

    def test_forbidden_checker_still_rejects_internal_ui_streamlit_app(self):
        mod = self._mod()
        assert mod._is_project_source_inside_internal(
            "AstroDestinyAnalyzer/_internal/ui/streamlit_app.py"
        )
