"""
Tests for V1.8.3 developer mode and navigation gating.
Verifies DEVELOPER_MODE env var, page list composition, and fallback behaviour.
"""
import sys
import os
import importlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ZIWEI_PAGE = "PAGE_ZIWEI_RECONCILIATION"


# ══════════════════════════════════════════════════════════════════════════════
# A. DEVELOPER_MODE constant
# ══════════════════════════════════════════════════════════════════════════════

class TestDeveloperModeDefault:
    def test_developer_mode_default_false(self, monkeypatch):
        """DEVELOPER_MODE must be False when env var is absent."""
        monkeypatch.delenv("ASTRO_DEVELOPER_MODE", raising=False)
        import config
        importlib.reload(config)
        assert config.DEVELOPER_MODE is False

    def test_developer_mode_false_when_zero(self, monkeypatch):
        monkeypatch.setenv("ASTRO_DEVELOPER_MODE", "0")
        import config
        importlib.reload(config)
        assert config.DEVELOPER_MODE is False

    def test_developer_mode_true_when_one(self, monkeypatch):
        monkeypatch.setenv("ASTRO_DEVELOPER_MODE", "1")
        import config
        importlib.reload(config)
        assert config.DEVELOPER_MODE is True

    def test_developer_mode_true_when_true_string(self, monkeypatch):
        monkeypatch.setenv("ASTRO_DEVELOPER_MODE", "true")
        import config
        importlib.reload(config)
        assert config.DEVELOPER_MODE is True

    def test_developer_mode_true_when_yes(self, monkeypatch):
        monkeypatch.setenv("ASTRO_DEVELOPER_MODE", "yes")
        import config
        importlib.reload(config)
        assert config.DEVELOPER_MODE is True

    def test_developer_mode_true_when_on(self, monkeypatch):
        monkeypatch.setenv("ASTRO_DEVELOPER_MODE", "on")
        import config
        importlib.reload(config)
        assert config.DEVELOPER_MODE is True

    def test_developer_mode_false_when_false_string(self, monkeypatch):
        monkeypatch.setenv("ASTRO_DEVELOPER_MODE", "false")
        import config
        importlib.reload(config)
        assert config.DEVELOPER_MODE is False


# ══════════════════════════════════════════════════════════════════════════════
# B. Page list composition
# ══════════════════════════════════════════════════════════════════════════════

class TestPageLists:
    def test_pages_base_no_ziwei(self):
        """_PAGES_BASE must not contain 紫微校準."""
        src_path = os.path.join(PROJECT_ROOT, "ui", "streamlit_app.py")
        with open(src_path, encoding="utf-8") as f:
            src = f.read()
        assert "_PAGES_BASE" in src
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

    def test_pages_dev_has_ziwei(self):
        """_PAGES_DEV must contain 紫微校準."""
        src_path = os.path.join(PROJECT_ROOT, "ui", "streamlit_app.py")
        with open(src_path, encoding="utf-8") as f:
            src = f.read()
        assert "_PAGES_DEV" in src
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

    def test_pages_active_selector(self):
        """_PAGES = get_active_pages() (V2.0.0 three-way mode split)."""
        src_path = os.path.join(PROJECT_ROOT, "ui", "streamlit_app.py")
        with open(src_path, encoding="utf-8") as f:
            src = f.read()
        assert "_PAGES = get_active_pages()" in src

    def test_pages_active_contains_home(self):
        src_path = os.path.join(PROJECT_ROOT, "ui", "streamlit_app.py")
        with open(src_path, encoding="utf-8") as f:
            src = f.read()
        assert "PAGE_HOME" in src


# ══════════════════════════════════════════════════════════════════════════════
# C. Fallback guard in source
# ══════════════════════════════════════════════════════════════════════════════

class TestNavFallback:
    def _src(self):
        path = os.path.join(PROJECT_ROOT, "ui", "streamlit_app.py")
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_guard_resets_nav_page_in_client_mode(self):
        src = self._src()
        assert "not DEVELOPER_MODE" in src
        assert ZIWEI_PAGE in src

    def test_ziwei_page_has_stop_guard(self):
        src = self._src()
        idx = src.find('elif page == PAGE_ZIWEI_RECONCILIATION:')
        assert idx != -1
        snippet = src[idx: idx + 600]
        assert "st.stop()" in snippet
        assert "not DEVELOPER_MODE" in snippet

    def test_ziwei_page_no_crash_without_dev_mode(self):
        """Guard must appear before any ziwei_reconciliation imports."""
        src = self._src()
        idx = src.find('elif page == PAGE_ZIWEI_RECONCILIATION:')
        assert idx != -1
        guard_idx = src.find("not DEVELOPER_MODE", idx)
        stop_idx = src.find("st.stop()", idx)
        import_idx = src.find("from ziwei_reconciliation", idx)
        assert guard_idx < stop_idx < import_idx
