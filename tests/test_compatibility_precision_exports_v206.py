"""Regression tests for precise compatibility analysis and four-format export."""
import os
import sys
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compatibility.engine import CompatibilityEngine
from compatibility.models import CompatibilityInput, RelationshipType
from compatibility.exporters import (
    export_compat_to_html, export_compat_to_docx, export_compat_to_pdf,
    make_compat_filename,
)
from demo.sample_profiles import SAMPLE_COUPLES


def _report():
    c = SAMPLE_COUPLES[0]
    return CompatibilityEngine().generate(CompatibilityInput(
        person_a=c["person_a"], person_b=c["person_b"],
        relationship_type=RelationshipType(c["relationship_type"]),
    ))


def test_precision_fields_are_populated():
    syn = _report().synthesis
    assert syn.precision_summary
    assert syn.dimension_evidence
    assert syn.score_drivers
    assert syn.priority_actions
    assert "emotional" in syn.dimension_evidence
    assert "communication" in syn.dimension_evidence


def test_markdown_contains_precision_sections():
    md = _report().markdown_body
    assert "精準分析摘要" in md
    assert "分數形成依據" in md
    assert "各維度具體證據" in md
    assert "優先改善順序" in md


def test_html_contains_precision_content():
    html = export_compat_to_html(_report())
    assert "精準分析摘要" in html
    assert "各維度具體證據" in html


def test_docx_contains_bytes_when_available():
    try:
        import docx  # noqa: F401
    except ImportError:
        return
    data = export_compat_to_docx(_report())
    assert isinstance(data, bytes) and len(data) > 100


def test_pdf_export_reuses_html():
    report = _report()
    fake_html = mock.Mock()
    fake_html.return_value.write_pdf.return_value = b"%PDF-test"
    with mock.patch("compatibility.exporters._pdf_available", return_value=True):
        with mock.patch.dict(sys.modules, {"weasyprint": mock.Mock(HTML=fake_html)}):
            data = export_compat_to_pdf(report)
    assert data.startswith(b"%PDF")
    assert fake_html.call_args.kwargs["string"].startswith("<!DOCTYPE html>")


def test_four_extensions_supported_by_filename_helper():
    for ext in ("md", "html", "docx", "pdf"):
        assert make_compat_filename("A", "B", ext).endswith("." + ext)


def test_ui_has_four_export_columns():
    from pathlib import Path
    source = (Path(__file__).parents[1] / "ui" / "streamlit_app.py").read_text(encoding="utf-8")
    assert "ex1, ex2, ex3, ex4 = st.columns(4)" in source
    assert "export_compat_to_pdf" in source
    assert "下載 PDF" in source
