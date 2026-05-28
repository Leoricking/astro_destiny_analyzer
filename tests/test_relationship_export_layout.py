"""
Tests for V1.8.3 export page UI behaviour — Word and PDF availability messaging.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_app_src() -> str:
    path = os.path.join(PROJECT_ROOT, "ui", "streamlit_app.py")
    with open(path, encoding="utf-8") as f:
        return f.read()


def _get_export_section(src: str) -> str:
    start = src.find('elif page == "📤 匯出"')
    if start == -1:
        start = src.find('page == "📤 匯出"')
    next_page = src.find('\nelif page ==', start + 1)
    if next_page == -1:
        next_page = len(src)
    return src[start:next_page]


# ══════════════════════════════════════════════════════════════════════════════
# A. DocxExporter — availability check
# ══════════════════════════════════════════════════════════════════════════════

class TestDocxExporter:
    def test_importable(self):
        from reports.docx_exporter import DocxExporter
        assert DocxExporter is not None

    def test_has_is_available(self):
        from reports.docx_exporter import DocxExporter
        assert callable(getattr(DocxExporter(), "is_available", None))

    def test_is_available_returns_bool(self):
        from reports.docx_exporter import DocxExporter
        assert isinstance(DocxExporter().is_available(), bool)

    def test_word_availability_depends_on_python_docx(self):
        try:
            import docx  # noqa
            docx_installed = True
        except ImportError:
            docx_installed = False
        from reports.docx_exporter import DocxExporter
        assert DocxExporter().is_available() == docx_installed

    def test_export_section_uses_is_available(self):
        src = _read_app_src()
        export_sec = _get_export_section(src)
        assert "is_available()" in export_sec
        assert "DocxExporter" in export_sec

    def test_word_missing_message_mentions_setup_or_requirements(self):
        src = _read_app_src()
        export_sec = _get_export_section(src)
        assert "setup.bat" in export_sec or "requirements.txt" in export_sec


# ══════════════════════════════════════════════════════════════════════════════
# B. PdfExporter — optional, no crash
# ══════════════════════════════════════════════════════════════════════════════

class TestPdfExporter:
    def test_importable(self):
        from reports.pdf_exporter import PdfExporter
        assert PdfExporter is not None

    def test_has_is_available(self):
        from reports.pdf_exporter import PdfExporter
        assert callable(getattr(PdfExporter(), "is_available", None))

    def test_is_available_returns_bool(self):
        from reports.pdf_exporter import PdfExporter
        assert isinstance(PdfExporter().is_available(), bool)

    def test_pdf_missing_does_not_crash(self):
        from reports.pdf_exporter import PdfExporter
        try:
            result = PdfExporter().is_available()
            assert isinstance(result, bool)
        except Exception as e:
            pytest.fail(f"PdfExporter.is_available() raised: {e}")

    def test_pdf_missing_message_mentions_weasyprint(self):
        src = _read_app_src()
        export_sec = _get_export_section(src)
        assert "WeasyPrint" in export_sec or "weasyprint" in export_sec.lower()

    def test_pdf_missing_message_mentions_install_bat(self):
        src = _read_app_src()
        export_sec = _get_export_section(src)
        assert "install_pdf_support.bat" in export_sec

    def test_pdf_missing_message_suggests_html_or_word(self):
        src = _read_app_src()
        export_sec = _get_export_section(src)
        assert "HTML" in export_sec or "Word" in export_sec

    def test_export_section_uses_pdf_is_available(self):
        src = _read_app_src()
        export_sec = _get_export_section(src)
        assert "is_available()" in export_sec
        assert "PdfExporter" in export_sec


# ══════════════════════════════════════════════════════════════════════════════
# C. Markdown and HTML always available
# ══════════════════════════════════════════════════════════════════════════════

class TestMarkdownHtmlExport:
    def test_markdown_exporter_importable(self):
        from reports.markdown_exporter import MarkdownExporter
        assert MarkdownExporter is not None

    def test_html_exporter_importable(self):
        from reports.html_exporter import HtmlExporter
        assert HtmlExporter is not None

    def test_export_section_has_markdown(self):
        src = _read_app_src()
        assert "Markdown" in _get_export_section(src)

    def test_export_section_has_html(self):
        src = _read_app_src()
        assert "HTML" in _get_export_section(src)
