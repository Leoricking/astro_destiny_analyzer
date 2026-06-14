"""
Tests for V2.0.2 Customer Empty States & Export Format Guidance.
Checks that the required strings appear in ui/streamlit_app.py source.
"""
import pathlib

ROOT = pathlib.Path(__file__).parent.parent
APP_SRC_PATH = ROOT / "ui" / "streamlit_app.py"


def _app_src() -> str:
    return APP_SRC_PATH.read_text(encoding="utf-8")


class TestEmptyStateMessages:
    def test_report_preview_empty_state(self):
        """Report preview page must show empty state (via _tr key or literal)."""
        src = _app_src()
        assert "尚未產生報告" in src or "report_preview.empty" in src

    def test_history_empty_state(self):
        """History page must show empty state (via _tr key or literal)."""
        src = _app_src()
        assert "目前沒有歷史報告" in src or "history.no_reports" in src

    def test_export_empty_state(self):
        """Export page must show empty state (via _tr key or literal)."""
        src = _app_src()
        assert "目前沒有可匯出的報告" in src or "export.no_report" in src

    def test_free_report_info(self):
        """Free report page must show local-storage privacy info (via _tr key or literal)."""
        src = _app_src()
        assert "填寫 Email" in src or "free_report.info" in src

    def test_compat_empty_state(self):
        """Compat page must show not-ready message (via _tr key or literal)."""
        src = _app_src()
        assert "請先輸入兩人的基本資料" in src or "compatibility.not_ready" in src


class TestExportFormatGuidance:
    def _export_block(self) -> str:
        src = _app_src()
        start = src.find('elif page == PAGE_EXPORT:')
        end = src.find("\nelif page ==", start + 1)
        return src[start:end] if start != -1 else src

    def test_html_stable_note(self):
        """Export page must mention HTML guidance (via _tr key or literal)."""
        block = self._export_block()
        assert "HTML 最穩定" in block or "export.html_desc" in block

    def test_word_editable_note(self):
        """Export page must mention Word guidance (via _tr key or literal)."""
        block = self._export_block()
        assert "Word 可編輯" in block or "export.word_desc" in block

    def test_pdf_optional_note(self):
        """Export page must mention PDF guidance (via _tr key or literal)."""
        block = self._export_block()
        assert "PDF 為選用功能" in block or "export.pdf_desc" in block

    def test_pdf_unavailable_uses_info_not_error(self):
        """When PDF is unavailable, use st.info not raw error."""
        block = self._export_block()
        # st.info should appear for PDF unavailable guidance
        assert "st.info(" in block

    def test_install_pdf_support_mentioned(self):
        """PDF section should mention install_pdf_support.bat."""
        assert "install_pdf_support" in self._export_block()


class TestEmptyStatesNoDeveloperExposure:
    def test_report_preview_empty_no_debug(self):
        """Empty state for report preview must include st.stop() guard."""
        src = _app_src()
        start = src.find('elif page == PAGE_REPORT_PREVIEW:')
        end = src.find("\nelif page ==", start + 1)
        block = src[start:end] if start != -1 else ""
        # Find the empty state (either literal or _tr key)
        empty_idx = block.find("尚未產生報告")
        if empty_idx == -1:
            empty_idx = block.find("report_preview.empty")
        stop_idx = block.find("st.stop()", empty_idx)
        assert empty_idx != -1
        assert stop_idx != -1

    def test_history_empty_no_debug(self):
        """Empty state for history must include st.stop() guard."""
        src = _app_src()
        start = src.find('elif page == PAGE_HISTORY:')
        end = src.find("\nelif page ==", start + 1)
        block = src[start:end] if start != -1 else ""
        empty_idx = block.find("目前沒有歷史報告")
        if empty_idx == -1:
            empty_idx = block.find("history.no_reports")
        stop_idx = block.find("st.stop()", empty_idx)
        assert empty_idx != -1
        assert stop_idx != -1


class TestOnboardingSection:
    def _home_block(self) -> str:
        src = _app_src()
        start = src.find('if page == PAGE_HOME:')
        end = src.find('\nelif page ==', start + 1)
        return src[start:end] if start != -1 else ""

    def test_home_has_onboarding_section(self):
        """Home page must have the 三步驟 onboarding section."""
        assert "三步驟" in self._home_block() or "快速開始" in self._home_block() or "quick_start" in self._home_block()

    def test_home_has_cta_free_content(self):
        """Home page must have 查看免費內容 CTA."""
        assert "查看免費內容" in self._home_block() or "免費內容" in self._home_block() or "PAGE_PUBLIC_CONTENT" in self._home_block()

    def test_home_has_cta_free_report(self):
        """Home page must have 領取免費摘要 CTA."""
        assert "領取免費摘要" in self._home_block() or "免費摘要" in self._home_block() or "PAGE_FREE_REPORT" in self._home_block()
