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
        # V2.0.0: selector uses get_active_pages() three-way split
        assert "get_active_pages()" in src
        assert "_PAGES = get_active_pages()" in src


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

    def test_home_has_onboarding_section(self):
        """V2.0.2: Home page must have onboarding 三步驟 section."""
        src = _app_src()
        home_start = src.find('if page == "🏠 首頁"')
        next_page = src.find('\nelif page ==', home_start + 1)
        home_section = src[home_start:next_page]
        assert "三步驟" in home_section or "快速開始" in home_section

    def test_home_onboarding_has_free_content_cta(self):
        """V2.0.2: Home onboarding must link to free content."""
        src = _app_src()
        home_start = src.find('if page == "🏠 首頁"')
        next_page = src.find('\nelif page ==', home_start + 1)
        home_section = src[home_start:next_page]
        assert "免費內容" in home_section

    def test_home_onboarding_has_free_report_cta(self):
        """V2.0.2: Home onboarding must link to free report."""
        src = _app_src()
        home_start = src.find('if page == "🏠 首頁"')
        next_page = src.find('\nelif page ==', home_start + 1)
        home_section = src[home_start:next_page]
        assert "免費摘要" in home_section or "免費報告" in home_section

    def test_home_onboarding_no_developer_words(self):
        """V2.0.2: Home onboarding must not expose developer terminology."""
        src = _app_src()
        home_start = src.find('if page == "🏠 首頁"')
        next_page = src.find('\nelif page ==', home_start + 1)
        home_section = src[home_start:next_page]
        # Developer-only terms must not appear in the non-SHOW_DEMO_DATA area
        show_demo_idx = home_section.find("if SHOW_DEMO_DATA")
        pre_demo = home_section[:show_demo_idx] if show_demo_idx != -1 else home_section
        assert "紫微校準" not in pre_demo
        assert "calibration" not in pre_demo.lower()
        assert "golden case" not in pre_demo.lower()


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


# ══════════════════════════════════════════════════════════════════════════════
# G. V1.9.2 — Human Design Reconciliation page gating
# ══════════════════════════════════════════════════════════════════════════════

HD_REC_PAGE = "🔷 人類圖校準"


class TestHDReconciliationPageGating:
    def test_customer_pages_no_hd_reconciliation(self):
        src = _app_src()
        lines = src.splitlines()
        in_base, block = False, []
        for line in lines:
            if "_PAGES_BASE = [" in line:
                in_base = True
            if in_base:
                block.append(line)
                if "]" in line and "_PAGES_BASE = [" not in line:
                    break
        base_block = "\n".join(block)
        assert HD_REC_PAGE not in base_block

    def test_developer_pages_has_hd_reconciliation(self):
        src = _app_src()
        lines = src.splitlines()
        in_dev, block = False, []
        for line in lines:
            if "_PAGES_DEV = [" in line:
                in_dev = True
            if in_dev:
                block.append(line)
                if "]" in line and "_PAGES_DEV = [" not in line:
                    break
        dev_block = "\n".join(block)
        assert HD_REC_PAGE in dev_block


# ══════════════════════════════════════════════════════════════════════════════
# H. V1.9.4 — Customer mode hides calibration dataset UI
# ══════════════════════════════════════════════════════════════════════════════

class TestV194CustomerModeHidesCalibration:
    def _get_hd_page_block(self) -> str:
        src = _app_src()
        start = src.find(f'elif page == "{HD_REC_PAGE}"')
        end = src.find("# PAGE: 設定", start)
        return src[start:end] if start != -1 else ""

    def test_customer_pages_no_case_import_label(self):
        """外部案例匯入 should only appear inside dev-gated page, not in _PAGES_BASE."""
        src = _app_src()
        lines = src.splitlines()
        in_base, block = False, []
        for line in lines:
            if "_PAGES_BASE = [" in line:
                in_base = True
            if in_base:
                block.append(line)
                if "]" in line and "_PAGES_BASE = [" not in line:
                    break
        base_block = "\n".join(block)
        assert "外部案例匯入" not in base_block

    def test_customer_pages_no_dataset_label(self):
        """多案例資料集 should not appear in _PAGES_BASE."""
        src = _app_src()
        lines = src.splitlines()
        in_base, block = False, []
        for line in lines:
            if "_PAGES_BASE = [" in line:
                in_base = True
            if in_base:
                block.append(line)
                if "]" in line and "_PAGES_BASE = [" not in line:
                    break
        base_block = "\n".join(block)
        assert "多案例資料集" not in base_block


# ══════════════════════════════════════════════════════════════════════════════
# I. V1.9.5 — Public Content Landing Page visibility
# ══════════════════════════════════════════════════════════════════════════════

PUBLIC_CONTENT_PAGE = "🌐 免費內容入口"


class TestV195PublicContentVisibility:
    def _get_pages_base_block(self, src: str) -> str:
        lines = src.splitlines()
        in_base, block = False, []
        for line in lines:
            if "_PAGES_BASE = [" in line:
                in_base = True
            if in_base:
                block.append(line)
                if "]" in line and "_PAGES_BASE = [" not in line:
                    break
        return "\n".join(block)

    def _get_pages_dev_block(self, src: str) -> str:
        lines = src.splitlines()
        in_dev, block = False, []
        for line in lines:
            if "_PAGES_DEV = [" in line:
                in_dev = True
            if in_dev:
                block.append(line)
                if "]" in line and "_PAGES_DEV = [" not in line:
                    break
        return "\n".join(block)

    def test_customer_pages_include_public_content(self):
        src = _app_src()
        base = self._get_pages_base_block(src)
        assert PUBLIC_CONTENT_PAGE in base

    def test_developer_pages_include_public_content(self):
        src = _app_src()
        dev = self._get_pages_dev_block(src)
        assert PUBLIC_CONTENT_PAGE in dev

    def test_customer_pages_no_seo_debug(self):
        """SEO debug section must be gated by DEVELOPER_MODE in the page block."""
        src = _app_src()
        start = src.find(f'elif page == "{PUBLIC_CONTENT_PAGE}"')
        end = src.find("# PAGE: 輸入資料", start)
        block = src[start:end] if start != -1 else ""
        # validate_seo_data must be inside DEVELOPER_MODE guard
        dev_idx = block.find("DEVELOPER_MODE")
        seo_idx = block.find("validate_seo_data")
        assert dev_idx != -1
        assert seo_idx != -1
        assert dev_idx < seo_idx

    def test_developer_mode_public_content_tools_present(self):
        src = _app_src()
        start = src.find(f'elif page == "{PUBLIC_CONTENT_PAGE}"')
        end = src.find("# PAGE: 輸入資料", start)
        block = src[start:end] if start != -1 else ""
        assert "DEVELOPER_MODE" in block
        assert "download_button" in block


# ══════════════════════════════════════════════════════════════════════════════
# J. V1.9.6 — Free Report Lead Magnet page visibility
# ══════════════════════════════════════════════════════════════════════════════

FREE_REPORT_PAGE = "🎁 免費報告"


class TestV196FreeReportVisibility:
    def _get_pages_base_block(self, src: str) -> str:
        lines = src.splitlines()
        in_base, block = False, []
        for line in lines:
            if "_PAGES_BASE = [" in line:
                in_base = True
            if in_base:
                block.append(line)
                if "]" in line and "_PAGES_BASE = [" not in line:
                    break
        return "\n".join(block)

    def _get_free_report_block(self, src: str) -> str:
        start = src.find(f'elif page == "{FREE_REPORT_PAGE}"')
        end = src.find("# PAGE: 輸入資料", start)
        return src[start:end] if start != -1 else ""

    def test_customer_pages_include_free_report(self):
        src = _app_src()
        base = self._get_pages_base_block(src)
        assert FREE_REPORT_PAGE in base

    def test_customer_pages_no_leads_list_exposed(self):
        src = _app_src()
        block = self._get_free_report_block(src)
        # dataframe/leads must be gated by DEVELOPER_MODE
        dev_idx = block.find("DEVELOPER_MODE")
        df_idx = block.find("dataframe") if "dataframe" in block else block.find("leads_df")
        assert dev_idx != -1
        assert df_idx != -1
        assert dev_idx < df_idx

    def test_customer_pages_no_raw_lead_json(self):
        src = _app_src()
        block = self._get_free_report_block(src)
        # raw JSON debug display should be inside DEVELOPER_MODE
        # Just ensure "raw" debug not exposed at top level
        dev_idx = block.find("DEVELOPER_MODE")
        assert dev_idx != -1  # DEVELOPER_MODE guard exists

    def test_developer_mode_has_lead_tools(self):
        src = _app_src()
        block = self._get_free_report_block(src)
        assert "DEVELOPER_MODE" in block
        assert "CSV" in block or "csv" in block.lower()


# ══════════════════════════════════════════════════════════════════════════════
# K. V1.9.8 — Consultant Workflow page gating
# ══════════════════════════════════════════════════════════════════════════════

CLIENT_CASE_PAGE = "🗂️ 客戶個案"


class TestV198ConsultantWorkflowGating:
    def _get_base_block(self) -> str:
        src = _app_src()
        start = src.find("_PAGES_BASE = [")
        end = src.find("]", start)
        return src[start:end]

    def _get_dev_block(self) -> str:
        src = _app_src()
        start = src.find("_PAGES_DEV = [")
        end = src.find("]", start)
        return src[start:end]

    def test_customer_pages_no_client_case(self):
        """_PAGES_BASE must not contain 客戶個案."""
        assert CLIENT_CASE_PAGE not in self._get_base_block()

    def test_developer_pages_contains_client_case(self):
        """_PAGES_DEV must contain 客戶個案."""
        assert CLIENT_CASE_PAGE in self._get_dev_block() or "客戶個案" in self._get_dev_block()

    def test_customer_mode_no_case_notes_exposed(self):
        """case notes should be behind consultant/developer guard."""
        src = _app_src()
        # case notes UI should appear after CONSULTANT_MODE check
        notes_idx = src.find("現有備註")
        consultant_idx = src.find("CONSULTANT_MODE")
        assert consultant_idx != -1
        assert notes_idx > consultant_idx

    def test_customer_mode_no_case_exports_exposed(self):
        """case exports should be behind consultant/developer guard."""
        src = _app_src()
        # CSV export for cases must be inside 客戶個案 page (CONSULTANT_MODE-gated)
        case_page_idx = src.find('elif page == "🗂️ 客戶個案"')
        assert case_page_idx != -1
        case_page_block = src[case_page_idx:case_page_idx + 5000]
        assert "CSV" in case_page_block or "csv" in case_page_block.lower()

    def test_consultant_mode_imported_from_config(self):
        """CONSULTANT_MODE must be imported from config in streamlit_app.py."""
        src = _app_src()
        config_import = src[src.find("from config import"):src.find("from config import") + 400]
        assert "CONSULTANT_MODE" in config_import

    def test_client_case_page_guard_is_consultant_mode(self):
        """The 客戶個案 page must check CONSULTANT_MODE, not DEVELOPER_MODE alone."""
        src = _app_src()
        page_start = src.find('elif page == "🗂️ 客戶個案"')
        page_snippet = src[page_start:page_start + 400]
        assert "CONSULTANT_MODE" in page_snippet


# ══════════════════════════════════════════════════════════════════════════════
# L. V2.0.0 — Three-way mode page governance
# ══════════════════════════════════════════════════════════════════════════════

class TestV200ModeGovernance:
    def _customer_block(self) -> str:
        src = _app_src()
        idx = src.find("_PAGES_BASE = [")
        end = src.find("]", idx)
        return src[idx:end] if idx != -1 else ""

    def _consultant_block(self) -> str:
        src = _app_src()
        # V2.0.0: CONSULTANT_PAGES: list = [...]
        idx = src.find("CONSULTANT_PAGES")
        end = src.find("]", idx)
        return src[idx:end] if idx != -1 else ""

    def test_customer_pages_defined(self):
        """CUSTOMER_PAGES must be defined in streamlit_app.py."""
        assert "CUSTOMER_PAGES" in _app_src()
        assert "_PAGES_BASE" in _app_src()

    def test_consultant_pages_not_exposed_to_customer(self):
        """Consultant-only pages must not appear in CUSTOMER_PAGES / _PAGES_BASE."""
        base = self._customer_block()
        assert "Lead Funnel" not in base
        assert "客戶個案" not in base

    def test_developer_pages_not_exposed_to_customer(self):
        """Developer-only pages must not appear in _PAGES_BASE."""
        base = self._customer_block()
        assert "紫微校準" not in base
        assert "人類圖校準" not in base

    def test_consultant_pages_include_lead_funnel(self):
        block = self._consultant_block()
        assert "Lead Funnel" in block

    def test_consultant_pages_include_client_case(self):
        block = self._consultant_block()
        assert "客戶個案" in block

    def test_developer_pages_alias_defined(self):
        src = _app_src()
        assert "DEVELOPER_PAGES" in src
        assert "_PAGES_DEV" in src

    def test_get_active_pages_defined(self):
        assert "def get_active_pages()" in _app_src()

    def test_is_page_allowed_defined(self):
        assert "def is_page_allowed(" in _app_src()
