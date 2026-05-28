"""
Tests for V1.9.5 Public Content UI integration.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_PAGE = "🌐 免費內容入口"


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


def _get_public_page_block(src: str) -> str:
    start = src.find(f'elif page == "{PUBLIC_PAGE}"')
    end = src.find("# PAGE: 輸入資料", start)
    return src[start:end] if start != -1 else ""


class TestPublicContentUIPageLists:
    def test_ui_source_contains_free_content_page(self):
        src = _app_src()
        assert PUBLIC_PAGE in src

    def test_pages_base_contains_public_content(self):
        src = _app_src()
        base = _get_pages_base_block(src)
        assert PUBLIC_PAGE in base

    def test_customer_mode_can_see_public_content(self):
        src = _app_src()
        base = _get_pages_base_block(src)
        assert PUBLIC_PAGE in base

    def test_developer_mode_can_see_public_content(self):
        src = _app_src()
        dev = _get_pages_dev_block(src)
        assert PUBLIC_PAGE in dev

    def test_page_impl_present(self):
        src = _app_src()
        assert f'elif page == "{PUBLIC_PAGE}"' in src


class TestPublicContentUIPageContent:
    def test_ui_has_category_filter(self):
        block = _get_public_page_block(_app_src())
        assert "selectbox" in block or "cat" in block.lower()

    def test_ui_has_cta_button(self):
        block = _get_public_page_block(_app_src())
        assert "cta_button_label" in block or "cta_nav" in block

    def test_ui_has_featured_cards(self):
        block = _get_public_page_block(_app_src())
        assert "featured" in block.lower() or "精選" in block

    def test_ui_developer_mode_shows_seo_warnings(self):
        block = _get_public_page_block(_app_src())
        assert "DEVELOPER_MODE" in block
        assert "SEO" in block or "seo" in block.lower()

    def test_ui_customer_mode_no_seo_debug_exposed(self):
        # SEO debug section should only appear inside DEVELOPER_MODE guard
        src = _app_src()
        block = _get_public_page_block(src)
        dev_idx = block.find("DEVELOPER_MODE")
        seo_idx = block.find("validate_seo_data")
        # validate_seo_data call must appear AFTER the DEVELOPER_MODE check
        assert dev_idx < seo_idx

    def test_ui_no_golden_case_in_content_page(self):
        block = _get_public_page_block(_app_src())
        assert "golden case" not in block.lower()

    def test_ui_no_rossi_in_content_page(self):
        block = _get_public_page_block(_app_src())
        assert "Rossi" not in block

    def test_ui_has_download_buttons_dev_mode(self):
        block = _get_public_page_block(_app_src())
        assert "download_button" in block
