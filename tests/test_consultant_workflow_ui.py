"""
Tests for V1.9.8 Consultant Workflow UI.
"""
import pathlib

SRC = pathlib.Path("ui/streamlit_app.py").read_text(encoding="utf-8")


class TestPageListInclusion:
    def test_pages_dev_contains_client_case(self):
        # _PAGES_DEV must contain client_cases canonical ID
        assert "PAGE_CLIENT_CASES" in SRC
        # The list definition
        dev_block_start = SRC.find("_PAGES_DEV = [")
        dev_block_end = SRC.find("]", dev_block_start)
        dev_block = SRC[dev_block_start:dev_block_end]
        assert "PAGE_CLIENT_CASES" in dev_block

    def test_pages_base_does_not_contain_client_case(self):
        # _PAGES_BASE must NOT contain PAGE_CLIENT_CASES
        base_block_start = SRC.find("_PAGES_BASE = [")
        base_block_end = SRC.find("]", base_block_start)
        base_block = SRC[base_block_start:base_block_end]
        assert "PAGE_CLIENT_CASES" not in base_block

    def test_customer_mode_cannot_see_client_case(self):
        # _PAGES (customer mode) uses _PAGES_BASE which has no PAGE_CLIENT_CASES
        base_block_start = SRC.find("_PAGES_BASE = [")
        base_block_end = SRC.find("]", base_block_start)
        base_block = SRC[base_block_start:base_block_end]
        assert "PAGE_CLIENT_CASES" not in base_block

    def test_developer_mode_can_see_client_case(self):
        dev_block_start = SRC.find("_PAGES_DEV = [")
        dev_block_end = SRC.find("]", dev_block_start)
        dev_block = SRC[dev_block_start:dev_block_end]
        assert "PAGE_CLIENT_CASES" in dev_block

    def test_pages_selector_uses_consultant_mode(self):
        # _PAGES must be determined by CONSULTANT_MODE (not raw DEVELOPER_MODE)
        assert "CONSULTANT_MODE" in SRC
        # The _PAGES assignment references CONSULTANT_MODE
        idx = SRC.find("_PAGES = ")
        line = SRC[idx:idx+80]
        assert "CONSULTANT_MODE" in line


class TestUIContentPresent:
    def test_ui_source_contains_client_case_title(self):
        assert "客戶個案" in SRC

    def test_ui_source_contains_create_from_lead(self):
        assert "從 Lead 建立個案" in SRC

    def test_ui_source_contains_case_detail(self):
        assert "個案詳情" in SRC

    def test_ui_source_contains_tasks_delivery(self):
        assert "待辦與交付" in SRC

    def test_ui_source_contains_export_tab(self):
        assert "匯出" in SRC

    def test_ui_source_contains_case_status(self):
        assert "case_status" in SRC

    def test_ui_source_contains_report_status(self):
        assert "report_status" in SRC

    def test_ui_source_contains_download_cases_csv(self):
        assert "cases.csv" in SRC or "download cases CSV" in SRC.lower() or "CSV" in SRC

    def test_ui_source_contains_confirmation_for_clear(self):
        # Should have a confirmation checkbox before deleting all cases
        assert "確認清空" in SRC or "confirm" in SRC.lower()


class TestCustomerModeGating:
    def test_consultant_mode_guard_on_page(self):
        # The page must check CONSULTANT_MODE before rendering content
        page_block_start = SRC.find('elif page == PAGE_CLIENT_CASES:')
        assert page_block_start != -1
        # The guard should appear near the start of that page block
        page_snippet = SRC[page_block_start:page_block_start + 300]
        assert "CONSULTANT_MODE" in page_snippet

    def test_import_consultant_mode_from_config(self):
        # CONSULTANT_MODE must be imported from config
        assert "CONSULTANT_MODE" in SRC
        config_import_block = SRC[SRC.find("from config import"):SRC.find("from config import") + 300]
        assert "CONSULTANT_MODE" in config_import_block
