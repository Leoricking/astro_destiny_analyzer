"""Regression coverage for complete multilingual personal and compatibility exports."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _personal_report():
    from core.database import init_db
    init_db()
    from demo.sample_profiles import SAMPLE_PROFILES
    from reports.generator import ReportGenerator
    return ReportGenerator().generate(SAMPLE_PROFILES[0])


def _compat_report():
    from core.database import init_db
    init_db()
    from demo.sample_profiles import SAMPLE_COUPLES
    from compatibility.engine import CompatibilityEngine
    from compatibility.models import CompatibilityInput, RelationshipType
    c = SAMPLE_COUPLES[0]
    return CompatibilityEngine().generate(CompatibilityInput(
        person_a=c["person_a"],
        person_b=c["person_b"],
        relationship_type=RelationshipType(c["relationship_type"]),
    ))


def test_personal_six_language_exports():
    from reports.markdown_exporter import MarkdownExporter
    from reports.html_exporter import HtmlExporter
    from reports.docx_exporter import DocxExporter
    from reports.pdf_exporter import PdfExporter
    report = _personal_report()
    for lang in ("zh-TW", "en", "th", "ja", "es", "ar"):
        md = MarkdownExporter().export(report, language=lang)
        html = HtmlExporter().export(report, language=lang)
        docx = DocxExporter().export(report, language=lang)
        pdf = PdfExporter().export(report, language=lang)
        assert md and isinstance(md, str)
        assert html.startswith("<!DOCTYPE html>")
        assert docx.startswith(b"PK")
        assert pdf.startswith(b"%PDF")
        if lang == "ar":
            assert 'dir="rtl"' in html


def test_compatibility_six_language_exports():
    from compatibility.exporters import (
        export_compat_to_markdown,
        export_compat_to_html,
        export_compat_to_docx,
        export_compat_to_pdf,
    )
    report = _compat_report()
    for lang in ("zh-TW", "en", "th", "ja", "es", "ar"):
        md = export_compat_to_markdown(report, language=lang)
        html = export_compat_to_html(report, language=lang)
        docx = export_compat_to_docx(report, language=lang)
        pdf = export_compat_to_pdf(report, language=lang)
        assert md and isinstance(md, str)
        assert html.startswith("<!DOCTYPE html>")
        assert docx.startswith(b"PK")
        assert pdf.startswith(b"%PDF")
        if lang == "ar":
            assert 'dir="rtl"' in html


def test_ui_uses_report_language_for_all_formats():
    from pathlib import Path
    source = (Path(__file__).parents[1] / "ui" / "streamlit_app.py").read_text(encoding="utf-8")
    assert "MarkdownExporter().export(report, language=_export_language)" in source
    assert "HtmlExporter().export(report, language=_export_language)" in source
    assert "docx_exp.export(report, language=_export_language)" in source
    assert "pdf_exp.export(report, language=_export_language)" in source
    assert "export_compat_to_markdown(_cr, language=_compat_export_language)" in source
    assert "export_compat_to_pdf(_cr, language=_compat_export_language)" in source
