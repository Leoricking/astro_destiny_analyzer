"""
Tests for V2.0.0 App Mode Governance.
Verifies CUSTOMER_PAGES, CONSULTANT_PAGES, DEVELOPER_PAGES,
get_active_pages(), is_page_allowed(), and launcher scripts.
"""
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
SRC_PATH = ROOT / "ui" / "streamlit_app.py"


def _src() -> str:
    return SRC_PATH.read_text(encoding="utf-8")


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def _get_block(src: str, marker_start: str, end_char: str = "]") -> str:
    idx = src.find(marker_start)
    if idx == -1:
        return ""
    end = src.find(end_char, idx)
    return src[idx:end] if end != -1 else src[idx:idx + 500]


# ══════════════════════════════════════════════════════════════════════════════
# A. CUSTOMER_PAGES — forbidden pages
# ══════════════════════════════════════════════════════════════════════════════

class TestCustomerPages:
    def _customer_block(self) -> str:
        src = _src()
        # CUSTOMER_PAGES = _PAGES_BASE means we check _PAGES_BASE content
        return _get_block(src, "_PAGES_BASE = [")

    def test_customer_pages_no_lead_funnel(self):
        assert "Lead Funnel" not in self._customer_block()

    def test_customer_pages_no_client_case(self):
        assert "客戶個案" not in self._customer_block()

    def test_customer_pages_no_ziwei(self):
        assert "紫微校準" not in self._customer_block()

    def test_customer_pages_no_hd_calibration(self):
        assert "人類圖校準" not in self._customer_block()

    def test_customer_pages_has_home(self):
        assert "首頁" in self._customer_block()

    def test_customer_pages_alias_defined(self):
        assert "CUSTOMER_PAGES" in _src()
        assert "_PAGES_BASE" in _src()


# ══════════════════════════════════════════════════════════════════════════════
# B. CONSULTANT_PAGES
# ══════════════════════════════════════════════════════════════════════════════

class TestConsultantPages:
    def _consultant_block(self) -> str:
        src = _src()
        # V2.0.0: CONSULTANT_PAGES: list = [...]
        return _get_block(src, "CONSULTANT_PAGES")

    def test_consultant_pages_has_lead_funnel(self):
        assert "Lead Funnel" in self._consultant_block()

    def test_consultant_pages_has_client_case(self):
        assert "客戶個案" in self._consultant_block()

    def test_consultant_pages_no_ziwei(self):
        assert "紫微校準" not in self._consultant_block()

    def test_consultant_pages_no_hd_calibration(self):
        assert "人類圖校準" not in self._consultant_block()

    def test_consultant_pages_has_home(self):
        assert "首頁" in self._consultant_block()


# ══════════════════════════════════════════════════════════════════════════════
# C. DEVELOPER_PAGES
# ══════════════════════════════════════════════════════════════════════════════

class TestDeveloperPages:
    def _dev_block(self) -> str:
        src = _src()
        return _get_block(src, "_PAGES_DEV = [")

    def test_developer_pages_has_lead_funnel(self):
        assert "Lead Funnel" in self._dev_block()

    def test_developer_pages_has_client_case(self):
        assert "客戶個案" in self._dev_block()

    def test_developer_pages_has_ziwei(self):
        assert "紫微校準" in self._dev_block()

    def test_developer_pages_has_hd_calibration(self):
        assert "人類圖校準" in self._dev_block()

    def test_developer_pages_alias_defined(self):
        assert "DEVELOPER_PAGES" in _src()
        assert "_PAGES_DEV" in _src()


# ══════════════════════════════════════════════════════════════════════════════
# D. get_active_pages() helper
# ══════════════════════════════════════════════════════════════════════════════

class TestGetActivePages:
    def test_get_active_pages_defined(self):
        assert "def get_active_pages()" in _src()

    def test_get_active_pages_returns_developer_pages_for_dev(self):
        src = _src()
        idx = src.find("def get_active_pages()")
        block = src[idx:idx + 300]
        assert "DEVELOPER_MODE" in block
        assert "DEVELOPER_PAGES" in block

    def test_get_active_pages_returns_consultant_pages(self):
        src = _src()
        idx = src.find("def get_active_pages()")
        block = src[idx:idx + 300]
        assert "CONSULTANT_MODE" in block
        assert "CONSULTANT_PAGES" in block

    def test_get_active_pages_returns_customer_pages_else(self):
        src = _src()
        idx = src.find("def get_active_pages()")
        block = src[idx:idx + 300]
        assert "CUSTOMER_PAGES" in block

    def test_is_page_allowed_defined(self):
        assert "def is_page_allowed(" in _src()

    def test_pages_uses_get_active_pages(self):
        src = _src()
        assert "_PAGES = get_active_pages()" in src

    def test_stale_nav_guard_generic(self):
        src = _src()
        assert "get_active_pages()" in src
        assert "not in _active_pages" in src or "not in _active" in src


# ══════════════════════════════════════════════════════════════════════════════
# E. Launcher scripts
# ══════════════════════════════════════════════════════════════════════════════

class TestLauncherScripts:
    def test_run_bat_has_customer_flags(self):
        text = _read("run.bat")
        assert "ASTRO_CUSTOMER_MODE=1" in text
        assert "ASTRO_BUILD_PROFILE=customer" in text

    def test_run_bat_no_developer_mode(self):
        text = _read("run.bat")
        assert "ASTRO_DEVELOPER_MODE=1" not in text

    def test_run_bat_no_consultant_mode(self):
        text = _read("run.bat")
        assert "ASTRO_CONSULTANT_MODE=1" not in text

    def test_run_consultant_bat_has_consultant_flags(self):
        text = _read("run_consultant.bat")
        assert "ASTRO_CONSULTANT_MODE=1" in text
        assert "ASTRO_BUILD_PROFILE=consultant" in text

    def test_run_consultant_bat_no_developer_mode(self):
        text = _read("run_consultant.bat")
        assert "ASTRO_DEVELOPER_MODE=1" not in text

    def test_run_dev_bat_has_developer_flags(self):
        text = _read("run_dev.bat")
        assert "ASTRO_DEVELOPER_MODE=1" in text
        assert "ASTRO_BUILD_PROFILE=developer" in text

    def test_run_dev_bat_has_consultant_mode(self):
        text = _read("run_dev.bat")
        assert "ASTRO_CONSULTANT_MODE=1" in text
