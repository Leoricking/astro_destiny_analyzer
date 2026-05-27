"""
Tests for compatibility report rendering and export — V1.7.0
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from demo.sample_profiles import SAMPLE_COUPLES
from compatibility.models import CompatibilityInput, RelationshipType
from compatibility.engine import CompatibilityEngine
from compatibility.report import render_compatibility_report
from compatibility.exporters import (
    make_compat_filename, export_compat_to_html, export_compat_to_docx,
)
from reports.utils import sanitize_filename


def _make_report(couple_index: int = 0):
    couple = SAMPLE_COUPLES[couple_index]
    ci = CompatibilityInput(
        person_a=couple["person_a"],
        person_b=couple["person_b"],
        relationship_type=RelationshipType(couple["relationship_type"]),
    )
    engine = CompatibilityEngine()
    return engine.generate(ci)


# ── Markdown export ───────────────────────────────────────────────────────────

class TestMarkdownExport:
    def setup_method(self):
        self.report = _make_report(0)

    def test_contains_report_title(self):
        assert "關係合盤分析報告" in self.report.markdown_body

    def test_contains_disclaimer(self):
        assert "免責聲明" in self.report.markdown_body

    def test_contains_name_a(self):
        assert self.report.person_a_profile.name in self.report.markdown_body

    def test_contains_name_b(self):
        assert self.report.person_b_profile.name in self.report.markdown_body

    def test_render_compatibility_report_returns_string(self):
        md = render_compatibility_report(self.report)
        assert isinstance(md, str)
        assert len(md) > 100

    def test_markdown_contains_score_section(self):
        assert "總分" in self.report.markdown_body or "分數" in self.report.markdown_body

    def test_business_couple_markdown(self):
        report = _make_report(1)
        assert "關係合盤分析報告" in report.markdown_body


# ── HTML export ───────────────────────────────────────────────────────────────

class TestHtmlExport:
    def setup_method(self):
        self.report = _make_report(0)

    def test_returns_html_string(self):
        html = export_compat_to_html(self.report)
        assert isinstance(html, str)
        assert "<html" in html

    def test_contains_doctype(self):
        html = export_compat_to_html(self.report)
        assert "DOCTYPE" in html or "doctype" in html.lower()

    def test_contains_title(self):
        html = export_compat_to_html(self.report)
        assert "<title>" in html

    def test_html_not_empty(self):
        html = export_compat_to_html(self.report)
        assert len(html) > 500


# ── Word export ───────────────────────────────────────────────────────────────

class TestDocxExport:
    def setup_method(self):
        self.report = _make_report(0)

    def test_docx_returns_bytes_if_available(self):
        try:
            import docx  # noqa: F401
            result = export_compat_to_docx(self.report)
            assert isinstance(result, bytes)
            assert len(result) > 0
        except ImportError:
            pytest.skip("python-docx not installed")

    def test_docx_raises_without_python_docx(self):
        import unittest.mock as mock
        import builtins
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "docx":
                raise ImportError("mocked missing")
            return original_import(name, *args, **kwargs)

        with mock.patch("builtins.__import__", side_effect=mock_import):
            # Force re-evaluation of _docx_available
            from compatibility import exporters
            orig = exporters._docx_available
            exporters._docx_available = lambda: False
            try:
                with pytest.raises(RuntimeError):
                    export_compat_to_docx(self.report)
            finally:
                exporters._docx_available = orig


# ── Filename helpers ──────────────────────────────────────────────────────────

class TestFilenameHelpers:
    def test_make_compat_filename_no_illegal_chars(self):
        fn = make_compat_filename("Demo 新竹科技職涯", "Demo 情侶B", "html")
        illegal = set('\\/:*?"<>|')
        assert not any(c in fn for c in illegal)

    def test_make_compat_filename_contains_ext(self):
        fn = make_compat_filename("A", "B", "md")
        assert fn.endswith(".md")

    def test_make_compat_filename_contains_both_names(self):
        fn = make_compat_filename("Alice", "Bob", "html")
        assert "Alice" in fn
        assert "Bob" in fn

    def test_sanitize_filename_no_spaces_needed(self):
        result = sanitize_filename("Demo 新竹科技職涯")
        assert result

    def test_make_compat_filename_docx(self):
        fn = make_compat_filename("甲", "乙", "docx")
        assert fn.endswith(".docx")


# ── Sample couples ────────────────────────────────────────────────────────────

class TestSampleCouples:
    def test_at_least_two_couples(self):
        assert len(SAMPLE_COUPLES) >= 2

    def test_romantic_couple_generates_report(self):
        report = _make_report(0)
        assert report.person_a_profile is not None
        assert report.person_b_profile is not None

    def test_business_couple_generates_report(self):
        report = _make_report(1)
        assert report.person_a_profile is not None
        assert report.person_b_profile is not None

    def test_each_couple_has_required_keys(self):
        for couple in SAMPLE_COUPLES:
            assert "label" in couple
            assert "person_a" in couple
            assert "person_b" in couple
            assert "relationship_type" in couple

    def test_romantic_couple_relationship_type(self):
        assert SAMPLE_COUPLES[0]["relationship_type"] == "romantic"

    def test_business_couple_relationship_type(self):
        assert SAMPLE_COUPLES[1]["relationship_type"] == "business"
