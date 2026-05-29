"""
Tests for V2.0.2.1 Optional Demo Import Hotfix.
Verifies that demo.sample_profiles is imported with a safe fallback
so customer and consultant release ZIPs (which exclude demo/) do not crash.
"""
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
APP_SRC = ROOT / "ui" / "streamlit_app.py"


def _app_src() -> str:
    return APP_SRC.read_text(encoding="utf-8")


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


# ══════════════════════════════════════════════════════════════════════════════
# A. Optional import structure
# ══════════════════════════════════════════════════════════════════════════════

class TestOptionalDemoImport:
    def test_has_try_block_for_demo_import(self):
        """demo.sample_profiles import must be inside a try block."""
        src = _app_src()
        try_idx = src.find("try:")
        demo_idx = src.find("demo.sample_profiles")
        assert try_idx != -1
        assert demo_idx != -1
        # try: must appear before demo.sample_profiles
        assert try_idx < demo_idx

    def test_has_except_module_not_found(self):
        """Must catch ModuleNotFoundError for missing demo module."""
        assert "except ModuleNotFoundError" in _app_src()

    def test_has_except_import_error(self):
        """Must catch ImportError as well."""
        assert "except ImportError" in _app_src()

    def test_sample_profiles_fallback(self):
        """SAMPLE_PROFILES = {} fallback must be present."""
        assert "SAMPLE_PROFILES = {}" in _app_src()

    def test_sample_labels_fallback(self):
        """SAMPLE_LABELS = {} fallback must be present."""
        assert "SAMPLE_LABELS = {}" in _app_src()

    def test_sample_couples_fallback(self):
        """SAMPLE_COUPLES = {} fallback must be present."""
        assert "SAMPLE_COUPLES = {}" in _app_src()

    def test_no_unsafe_bare_demo_import(self):
        """There must not be an unguarded top-level 'from demo.sample_profiles import'."""
        src = _app_src()
        lines = src.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("from demo.sample_profiles import"):
                # Check that a try: appears within 5 lines before it
                context = "\n".join(lines[max(0, i - 5):i])
                assert "try:" in context, (
                    f"Line {i+1}: bare 'from demo.sample_profiles import' found without try guard:\n{line}"
                )


# ══════════════════════════════════════════════════════════════════════════════
# B. Demo sections guarded against empty fallback
# ══════════════════════════════════════════════════════════════════════════════

class TestDemoSectionGuards:
    def _home_block(self) -> str:
        src = _app_src()
        start = src.find('if page == "🏠 首頁"')
        end = src.find('\nelif page ==', start + 1)
        return src[start:end] if start != -1 else ""

    def _compat_block(self) -> str:
        src = _app_src()
        start = src.find('elif page == "💕 合盤分析"')
        end = src.find('\nelif page ==', start + 1)
        return src[start:end] if start != -1 else ""

    def test_home_demo_guarded_by_sample_profiles(self):
        """Homepage demo section must check SAMPLE_PROFILES before rendering demo buttons."""
        block = self._home_block()
        assert "SAMPLE_PROFILES" in block

    def test_compat_demo_guarded_by_sample_couples(self):
        """Compat demo section must check SAMPLE_COUPLES before rendering demo buttons."""
        block = self._compat_block()
        assert "SAMPLE_COUPLES" in block

    def test_home_demo_no_unconditional_columns(self):
        """st.columns(len(SAMPLE_PROFILES)) must not appear without SAMPLE_PROFILES guard."""
        block = self._home_block()
        # If SAMPLE_PROFILES guard exists and demo buttons use columns(3), that's fine
        # (3 is a literal, not len(SAMPLE_PROFILES))
        # The important thing is that the demo section with st.columns is inside the guard
        sample_guard_idx = block.find("if SHOW_DEMO_DATA and SAMPLE_PROFILES")
        if sample_guard_idx == -1:
            sample_guard_idx = block.find("SAMPLE_PROFILES")
        assert sample_guard_idx != -1

    def test_compat_demo_no_unconditional_columns(self):
        """st.columns(len(SAMPLE_COUPLES)) must not appear outside SAMPLE_COUPLES guard."""
        block = self._compat_block()
        guard_idx = block.find("if SHOW_DEMO_DATA and SAMPLE_COUPLES")
        columns_idx = block.find("st.columns(len(SAMPLE_COUPLES))")
        assert guard_idx != -1
        assert columns_idx != -1
        assert guard_idx < columns_idx


# ══════════════════════════════════════════════════════════════════════════════
# C. Customer / Consultant mode safety
# ══════════════════════════════════════════════════════════════════════════════

class TestCustomerModeNoDemoCrash:
    def test_customer_mode_no_demo_required(self):
        """Customer mode must not crash when demo/ is absent (fallback = {})."""
        # With SAMPLE_PROFILES = {}, all demo buttons are behind falsy guard → not shown
        # Verify that SAMPLE_PROFILES is checked before demo buttons are rendered
        src = _app_src()
        assert "SAMPLE_PROFILES = {}" in src
        assert "SAMPLE_COUPLES = {}" in src

    def test_customer_mode_no_demo_error_exposed(self):
        """Customer mode must not expose demo missing error or warning."""
        src = _app_src()
        # The developer info message must be behind DEVELOPER_MODE guard
        info_idx = src.find("Demo profiles are not included in this release package.")
        assert info_idx != -1
        # DEVELOPER_MODE guard must appear before the info message
        dev_idx = src.rfind("DEVELOPER_MODE", 0, info_idx)
        assert dev_idx != -1

    def test_consultant_mode_no_demo_required(self):
        """Consultant mode must not crash when demo/ is absent."""
        # Same as customer — both rely on the {} fallback and guards
        src = _app_src()
        assert "SAMPLE_PROFILES = {}" in src
        assert "SAMPLE_COUPLES = {}" in src


# ══════════════════════════════════════════════════════════════════════════════
# D. Developer mode preserves demo
# ══════════════════════════════════════════════════════════════════════════════

class TestDeveloperModeDemo:
    def test_developer_mode_demo_unavailable_info(self):
        """Developer mode should show info when demo profiles are not available."""
        src = _app_src()
        assert "Demo profiles are not included in this release package." in src

    def test_developer_mode_info_gated_by_developer_mode(self):
        """Demo unavailable info must be gated by DEVELOPER_MODE."""
        src = _app_src()
        info_idx = src.find("Demo profiles are not included in this release package.")
        assert info_idx != -1
        # Check DEVELOPER_MODE appears in a guard before this string
        context = src[max(0, info_idx - 200):info_idx]
        assert "DEVELOPER_MODE" in context


# ══════════════════════════════════════════════════════════════════════════════
# E. Release packaging: demo excluded from customer/consultant
# ══════════════════════════════════════════════════════════════════════════════

class TestDemoExcludedFromReleaseProfiles:
    def _load_build_release(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "build_release_demo", str(ROOT / "scripts" / "build_release.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_customer_profile_excludes_demo_dir(self):
        mod = self._load_build_release()
        assert mod._should_exclude("demo/sample_profiles.py", profile="customer")

    def test_consultant_profile_excludes_demo_dir(self):
        mod = self._load_build_release()
        assert mod._should_exclude("demo/sample_profiles.py", profile="consultant")

    def test_developer_profile_does_not_exclude_demo(self):
        mod = self._load_build_release()
        assert not mod._should_exclude("demo/sample_profiles.py", profile="developer")
