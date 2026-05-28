"""
Tests for V1.9.2 Human Design Reconciliation UI integration.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HD_REC_PAGE = "🔷 人類圖校準"


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


# ── A. Page list gating ────────────────────────────────────────────────────────

class TestHDRecPageGating:
    def test_customer_pages_no_hd_reconciliation(self):
        src = _app_src()
        base_block = _get_pages_base_block(src)
        assert HD_REC_PAGE not in base_block

    def test_developer_pages_has_hd_reconciliation(self):
        src = _app_src()
        dev_block = _get_pages_dev_block(src)
        assert HD_REC_PAGE in dev_block

    def test_stale_nav_fallback_for_hd_rec_present(self):
        src = _app_src()
        assert f'nav_page") == "{HD_REC_PAGE}"' in src

    def test_hd_rec_page_impl_present(self):
        src = _app_src()
        assert f'elif page == "{HD_REC_PAGE}"' in src


# ── B. UI content ─────────────────────────────────────────────────────────────

class TestHDRecUIContent:
    def _get_page_block(self) -> str:
        src = _app_src()
        start = src.find(f'elif page == "{HD_REC_PAGE}"')
        end = src.find("# PAGE: 設定", start)
        return src[start:end] if start != -1 else ""

    def test_page_has_dev_mode_guard(self):
        block = self._get_page_block()
        assert "if not DEVELOPER_MODE" in block

    def test_page_has_json_text_area(self):
        src = _app_src()
        idx = src.find(f'elif page == "{HD_REC_PAGE}"')
        end = src.find("# PAGE: 設定", idx)
        block = src[idx:end]
        assert "text_area" in block

    def test_page_has_blank_template_button(self):
        block = self._get_page_block()
        assert "空白模板" in block

    def test_page_has_rossi_template_button(self):
        block = self._get_page_block()
        assert "Rossi template" in block

    def test_page_has_reconcile_button(self):
        block = self._get_page_block()
        assert "開始人類圖校準比對" in block

    def test_page_has_download_markdown(self):
        block = self._get_page_block()
        assert "human_design_reconciliation_report.md" in block or "下載" in block

    def test_page_handles_json_parse_error(self):
        block = self._get_page_block()
        assert "_hd_parse_error" in block or "parse_error" in block.lower()

    def test_customer_mode_not_in_base_pages(self):
        src = _app_src()
        base_block = _get_pages_base_block(src)
        assert HD_REC_PAGE not in base_block
