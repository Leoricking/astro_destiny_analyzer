"""
Tests for V1.8.4 Customer Delivery Mode.
Verifies CUSTOMER_MODE, SHOW_DEMO_DATA, page gating, and launcher script settings.
"""
import sys
import os
import importlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIWEI_PAGE = "🧭 紫微校準"


def _read(rel: str) -> str:
    with open(os.path.join(PROJECT_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def _app_src() -> str:
    return _read("ui/streamlit_app.py")


# ══════════════════════════════════════════════════════════════════════════════
# A. Config defaults
# ══════════════════════════════════════════════════════════════════════════════

class TestConfigDefaults:
    def test_customer_mode_default_true(self, monkeypatch):
        monkeypatch.delenv("ASTRO_CUSTOMER_MODE", raising=False)
        monkeypatch.delenv("ASTRO_DEVELOPER_MODE", raising=False)
        import config
        importlib.reload(config)
        assert config.CUSTOMER_MODE is True

    def test_developer_mode_default_false(self, monkeypatch):
        monkeypatch.delenv("ASTRO_DEVELOPER_MODE", raising=False)
        import config
        importlib.reload(config)
        assert config.DEVELOPER_MODE is False

    def test_show_demo_data_default_false(self, monkeypatch):
        monkeypatch.delenv("ASTRO_SHOW_DEMO_DATA", raising=False)
        monkeypatch.delenv("ASTRO_DEVELOPER_MODE", raising=False)
        import config
        importlib.reload(config)
        assert config.SHOW_DEMO_DATA is False

    def test_developer_mode_enables_show_demo_data(self, monkeypatch):
        monkeypatch.setenv("ASTRO_DEVELOPER_MODE", "1")
        monkeypatch.delenv("ASTRO_SHOW_DEMO_DATA", raising=False)
        import config
        importlib.reload(config)
        assert config.SHOW_DEMO_DATA is True

    def test_show_demo_data_explicit_true(self, monkeypatch):
        monkeypatch.setenv("ASTRO_SHOW_DEMO_DATA", "1")
        monkeypatch.delenv("ASTRO_DEVELOPER_MODE", raising=False)
        import config
        importlib.reload(config)
        assert config.SHOW_DEMO_DATA is True

    def test_customer_mode_can_be_disabled(self, monkeypatch):
        monkeypatch.setenv("ASTRO_CUSTOMER_MODE", "0")
        import config
        importlib.reload(config)
        assert config.CUSTOMER_MODE is False


# ══════════════════════════════════════════════════════════════════════════════
# B. Page lists
# ══════════════════════════════════════════════════════════════════════════════

class TestPageLists:
    def test_customer_pages_no_ziwei(self):
        src = _app_src()
        # _PAGES_BASE must not include 紫微校準
        lines = src.splitlines()
        in_base = False
        base_lines = []
        for line in lines:
            if "_PAGES_BASE = [" in line:
                in_base = True
            if in_base:
                base_lines.append(line)
                if "]" in line and "_PAGES_BASE = [" not in line:
                    break
        base_block = "\n".join(base_lines)
        assert ZIWEI_PAGE not in base_block

    def test_developer_pages_has_ziwei(self):
        src = _app_src()
        lines = src.splitlines()
        in_dev = False
        dev_lines = []
        for line in lines:
            if "_PAGES_DEV = [" in line:
                in_dev = True
            if in_dev:
                dev_lines.append(line)
                if "]" in line and "_PAGES_DEV = [" not in line:
                    break
        dev_block = "\n".join(dev_lines)
        assert ZIWEI_PAGE in dev_block

    def test_active_pages_selector_present(self):
        src = _app_src()
        assert "_PAGES_DEV if DEVELOPER_MODE else _PAGES_BASE" in src


# ══════════════════════════════════════════════════════════════════════════════
# C. Home page customer mode
# ══════════════════════════════════════════════════════════════════════════════

class TestHomePageCustomerMode:
    def test_home_demo_section_gated_by_show_demo_data(self):
        src = _app_src()
        home_start = src.find('if page == "🏠 首頁"')
        next_page = src.find('\nelif page ==', home_start + 1)
        home_section = src[home_start:next_page]
        # Demo buttons must be inside SHOW_DEMO_DATA guard
        assert "SHOW_DEMO_DATA" in home_section
        demo_idx = home_section.find("Demo 台北精準時間")
        show_demo_idx = home_section.find("SHOW_DEMO_DATA")
        assert show_demo_idx < demo_idx

    def test_home_has_customer_cta(self):
        src = _app_src()
        home_start = src.find('if page == "🏠 首頁"')
        next_page = src.find('\nelif page ==', home_start + 1)
        home_section = src[home_start:next_page]
        assert "📝 輸入資料" in home_section or "輸入" in home_section


# ══════════════════════════════════════════════════════════════════════════════
# D. Demo data gating
# ══════════════════════════════════════════════════════════════════════════════

class TestDemoDataGating:
    def test_get_sample_labels_false_returns_empty(self):
        from demo.sample_profiles import get_sample_labels
        assert get_sample_labels(show_internal=False) == []

    def test_get_sample_labels_true_returns_labels(self):
        from demo.sample_profiles import get_sample_labels, SAMPLE_LABELS
        assert get_sample_labels(show_internal=True) == SAMPLE_LABELS

    def test_get_sample_couples_false_returns_empty(self):
        from demo.sample_profiles import get_sample_couples
        assert get_sample_couples(show_internal=False) == []

    def test_get_sample_couples_true_returns_couples(self):
        from demo.sample_profiles import get_sample_couples, SAMPLE_COUPLES
        assert get_sample_couples(show_internal=True) == SAMPLE_COUPLES


# ══════════════════════════════════════════════════════════════════════════════
# E. Launcher scripts
# ══════════════════════════════════════════════════════════════════════════════

class TestLauncherScripts:
    def test_run_bat_no_developer_mode(self):
        assert "ASTRO_DEVELOPER_MODE=1" not in _read("run.bat")

    def test_run_bat_has_customer_mode(self):
        assert "ASTRO_CUSTOMER_MODE=1" in _read("run.bat")

    def test_run_dev_bat_has_developer_mode(self):
        assert "ASTRO_DEVELOPER_MODE=1" in _read("run_dev.bat")

    def test_run_dev_bat_has_show_demo_data(self):
        assert "ASTRO_SHOW_DEMO_DATA=1" in _read("run_dev.bat")


# ══════════════════════════════════════════════════════════════════════════════
# F. Stale session fallback
# ══════════════════════════════════════════════════════════════════════════════

class TestStaleFallback:
    def test_stale_nav_fallback_guard_present(self):
        src = _app_src()
        assert "not DEVELOPER_MODE" in src
        assert ZIWEI_PAGE in src

    def test_ziwei_page_stop_guard_present(self):
        src = _app_src()
        idx = src.find('elif page == "🧭 紫微校準"')
        assert idx != -1
        snippet = src[idx: idx + 600]
        assert "st.stop()" in snippet
