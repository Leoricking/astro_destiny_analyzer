"""
Tests for V1.9.6 Lead Magnet UI integration.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREE_REPORT_PAGE = "PAGE_FREE_REPORT"


def _read(rel: str) -> str:
    with open(os.path.join(PROJECT_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def _app_src() -> str:
    return _read("ui/streamlit_app.py")


def _get_pages_base_block(src: str) -> str:
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


def _get_pages_dev_block(src: str) -> str:
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


def _get_free_report_block(src: str) -> str:
    start = src.find('elif page == PAGE_FREE_REPORT:')
    end = src.find("# PAGE: 輸入資料", start)
    return src[start:end] if start != -1 else ""


class TestFreeReportUIPageLists:
    def test_ui_source_contains_free_report_page(self):
        src = _app_src()
        assert FREE_REPORT_PAGE in src

    def test_pages_base_contains_free_report(self):
        src = _app_src()
        base = _get_pages_base_block(src)
        assert FREE_REPORT_PAGE in base

    def test_customer_mode_can_see_free_report(self):
        src = _app_src()
        base = _get_pages_base_block(src)
        assert FREE_REPORT_PAGE in base

    def test_developer_mode_can_see_free_report(self):
        src = _app_src()
        dev = _get_pages_dev_block(src)
        assert FREE_REPORT_PAGE in dev

    def test_page_impl_present(self):
        src = _app_src()
        assert 'elif page == PAGE_FREE_REPORT:' in src


class TestFreeReportUIPageContent:
    def test_has_consent_checkbox(self):
        block = _get_free_report_block(_app_src())
        assert "consent" in block.lower() or "checkbox" in block.lower()

    def test_has_email_input(self):
        block = _get_free_report_block(_app_src())
        assert "email" in block.lower() or "Email" in block

    def test_has_report_type_selector(self):
        block = _get_free_report_block(_app_src())
        assert "selectbox" in block or "report_type" in block.lower()

    def test_customer_mode_no_leads_list_by_default(self):
        block = _get_free_report_block(_app_src())
        # leads dataframe must be inside DEVELOPER_MODE guard
        dev_idx = block.find("DEVELOPER_MODE")
        leads_idx = block.find("leads_df") if "leads_df" in block else block.find("dataframe")
        assert dev_idx != -1
        assert leads_idx != -1
        assert dev_idx < leads_idx

    def test_developer_mode_has_leads_dataframe(self):
        block = _get_free_report_block(_app_src())
        assert "DEVELOPER_MODE" in block
        assert "dataframe" in block.lower() or "leads_df" in block

    def test_developer_mode_has_export_csv(self):
        block = _get_free_report_block(_app_src())
        assert "CSV" in block or "csv" in block.lower()

    def test_no_golden_case_in_page(self):
        block = _get_free_report_block(_app_src())
        assert "golden case" not in block.lower()

    def test_no_rossi_in_page(self):
        block = _get_free_report_block(_app_src())
        assert "Rossi" not in block


class TestPublicContentFreeReportIntegration:
    def _get_public_page_block(self, src: str) -> str:
        start = src.find('elif page == PAGE_PUBLIC_CONTENT:')
        end = src.find("# PAGE: 輸入資料", start)
        return src[start:end] if start != -1 else ""

    def test_public_content_has_free_report_cta(self):
        src = _app_src()
        block = self._get_public_page_block(src)
        assert "free_report" in block.lower() or "免費報告" in block or FREE_REPORT_PAGE in block

    def test_free_report_target_in_public_content_block(self):
        src = _app_src()
        block = self._get_public_page_block(src)
        assert FREE_REPORT_PAGE in block or "free_report" in block.lower()
