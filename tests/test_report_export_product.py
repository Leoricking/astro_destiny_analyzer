"""
Tests for V1.6.0 report export and product polish.
Covers: sanitize_filename, MarkdownExporter, HtmlExporter,
        DocxExporter, PdfExporter, and safe export filenames.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import date, time

from core.models import (
    BirthProfile, BloodType, AnalysisTheme,
    ReportLanguage, ReportLength,
)
from reports.utils import sanitize_filename, make_export_filename, build_report_meta, DISCLAIMER
from reports.markdown_exporter import MarkdownExporter
from reports.html_exporter import HtmlExporter
from reports.docx_exporter import DocxExporter
from reports.pdf_exporter import PdfExporter
from reports.generator import ReportGenerator


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def sample_profile():
    return BirthProfile(
        name="匯出測試",
        birth_date=date(1992, 8, 20),
        birth_time=time(10, 0),
        birth_city="台北",
        birth_country="台灣",
        blood_type=BloodType.B,
        themes=list(AnalysisTheme),
        report_language=ReportLanguage.TRADITIONAL_CHINESE,
        report_length=ReportLength.STANDARD,
    )


@pytest.fixture(scope="module")
def sample_report(sample_profile):
    return ReportGenerator().generate(sample_profile, persist=False)


# ══════════════════════════════════════════════════════════════════════════════
# A. sanitize_filename
# ══════════════════════════════════════════════════════════════════════════════

class TestSanitizeFilename:
    def test_removes_backslash(self):
        assert "\\" not in sanitize_filename("a\\b")

    def test_removes_slash(self):
        assert "/" not in sanitize_filename("a/b")

    def test_removes_colon(self):
        assert ":" not in sanitize_filename("a:b")

    def test_removes_asterisk(self):
        assert "*" not in sanitize_filename("a*b")

    def test_removes_question_mark(self):
        assert "?" not in sanitize_filename("a?b")

    def test_removes_double_quote(self):
        assert '"' not in sanitize_filename('a"b')

    def test_removes_angle_brackets(self):
        result = sanitize_filename("a<b>c")
        assert "<" not in result
        assert ">" not in result

    def test_removes_pipe(self):
        assert "|" not in sanitize_filename("a|b")

    def test_empty_string_fallback(self):
        assert sanitize_filename("") == "astro_report"

    def test_whitespace_only_fallback(self):
        assert sanitize_filename("   ") == "astro_report"

    def test_all_illegal_chars_fallback(self):
        assert sanitize_filename('\\/:*?"<>|') == "astro_report"

    def test_chinese_preserved(self):
        result = sanitize_filename("王小明命盤報告")
        assert "王小明命盤報告" in result

    def test_long_string_truncated(self):
        long_name = "a" * 200
        assert len(sanitize_filename(long_name)) <= 80

    def test_normal_name_unchanged(self):
        assert sanitize_filename("John Doe") == "John Doe"

    def test_newline_removed(self):
        result = sanitize_filename("abc\ndef")
        assert "\n" not in result

    def test_tab_removed(self):
        result = sanitize_filename("abc\tdef")
        assert "\t" not in result


# ══════════════════════════════════════════════════════════════════════════════
# B. make_export_filename
# ══════════════════════════════════════════════════════════════════════════════

class TestMakeExportFilename:
    def test_contains_extension(self):
        fn = make_export_filename("測試", "md")
        assert fn.endswith(".md")

    def test_contains_name(self):
        fn = make_export_filename("王小明", "html")
        assert "王小明" in fn

    def test_contains_timestamp(self):
        fn = make_export_filename("測試", "docx")
        # Should contain YYYYMMDD_HHMM pattern
        import re
        assert re.search(r"\d{8}_\d{4}", fn)

    def test_contains_report_label(self):
        fn = make_export_filename("測試", "pdf")
        assert "命盤整合分析報告" in fn

    def test_no_illegal_chars(self):
        fn = make_export_filename('a\\b:c*d?"e<f>g|h', "md")
        for ch in '\\/:*?"<>|':
            assert ch not in fn

    def test_empty_name_fallback(self):
        fn = make_export_filename("", "md")
        assert fn.endswith(".md")
        assert "astro_report" in fn


# ══════════════════════════════════════════════════════════════════════════════
# C. build_report_meta
# ══════════════════════════════════════════════════════════════════════════════

class TestBuildReportMeta:
    def test_name_present(self, sample_report):
        meta = build_report_meta(sample_report)
        assert meta["name"] == "匯出測試"

    def test_disclaimer_present(self, sample_report):
        meta = build_report_meta(sample_report)
        assert len(meta["disclaimer"]) > 20

    def test_all_required_keys(self, sample_report):
        meta = build_report_meta(sample_report)
        required = [
            "name", "birth_date", "birth_time", "location",
            "gender", "blood_type", "themes", "report_length",
            "created_at", "app_name", "app_version", "disclaimer",
            "western_mode", "bazi_mode", "ziwei_mode",
            "sun_sign", "moon_sign", "day_master", "life_path",
        ]
        for key in required:
            assert key in meta, f"Missing key: {key}"

    def test_birth_time_known(self, sample_report):
        meta = build_report_meta(sample_report)
        # Profile has birth_time=10:00
        assert meta["birth_time"] != "未知"

    def test_birth_time_unknown(self):
        profile = BirthProfile(
            name="無時間", birth_date=date(1990, 1, 1),
            birth_city="台北", birth_country="台灣",
        )
        report = ReportGenerator().generate(profile, persist=False)
        meta = build_report_meta(report)
        assert meta["birth_time"] == "未知"

    def test_disclaimer_content(self, sample_report):
        meta = build_report_meta(sample_report)
        assert "娛樂" in meta["disclaimer"] or "參考" in meta["disclaimer"]


# ══════════════════════════════════════════════════════════════════════════════
# D. MarkdownExporter
# ══════════════════════════════════════════════════════════════════════════════

class TestMarkdownExporter:
    def test_output_non_empty(self, sample_report):
        md = MarkdownExporter().export(sample_report)
        assert len(md) > 500

    def test_contains_user_name(self, sample_report):
        md = MarkdownExporter().export(sample_report)
        assert "匯出測試" in md

    def test_contains_disclaimer(self, sample_report):
        md = MarkdownExporter().export(sample_report)
        assert "免責聲明" in md

    def test_disclaimer_text_present(self, sample_report):
        md = MarkdownExporter().export(sample_report)
        # The DISCLAIMER constant should appear
        assert "娛樂" in md or "參考" in md

    def test_contains_calc_mode_summary(self, sample_report):
        md = MarkdownExporter().export(sample_report)
        assert "計算模式摘要" in md

    def test_contains_toc(self, sample_report):
        md = MarkdownExporter().export(sample_report)
        assert "目錄" in md

    def test_contains_headings(self, sample_report):
        md = MarkdownExporter().export(sample_report)
        assert "#" in md

    def test_contains_cover_info(self, sample_report):
        md = MarkdownExporter().export(sample_report)
        assert "出生日期" in md
        assert "出生時間" in md

    def test_utf8_encodable(self, sample_report):
        md = MarkdownExporter().export(sample_report)
        # Should not raise
        encoded = md.encode("utf-8")
        assert len(encoded) > 0


# ══════════════════════════════════════════════════════════════════════════════
# E. HtmlExporter
# ══════════════════════════════════════════════════════════════════════════════

class TestHtmlExporter:
    def test_output_starts_with_doctype(self, sample_report):
        html = HtmlExporter().export(sample_report)
        assert html.startswith("<!DOCTYPE html>")

    def test_output_has_html_tag(self, sample_report):
        html = HtmlExporter().export(sample_report)
        assert "<html" in html
        assert "</html>" in html

    def test_contains_css(self, sample_report):
        html = HtmlExporter().export(sample_report)
        assert "<style>" in html

    def test_contains_microsoft_jheng_hei(self, sample_report):
        html = HtmlExporter().export(sample_report)
        assert "Microsoft JhengHei" in html

    def test_contains_noto_sans_tc(self, sample_report):
        html = HtmlExporter().export(sample_report)
        assert "Noto Sans TC" in html

    def test_contains_disclaimer(self, sample_report):
        html = HtmlExporter().export(sample_report)
        assert "免責聲明" in html

    def test_contains_user_name(self, sample_report):
        html = HtmlExporter().export(sample_report)
        assert "匯出測試" in html

    def test_title_contains_name(self, sample_report):
        html = HtmlExporter().export(sample_report)
        assert "<title>" in html
        assert "匯出測試" in html

    def test_contains_cover_block(self, sample_report):
        html = HtmlExporter().export(sample_report)
        assert 'class="cover"' in html

    def test_contains_calc_mode_card(self, sample_report):
        html = HtmlExporter().export(sample_report)
        assert "計算模式摘要" in html

    def test_contains_toc_block(self, sample_report):
        html = HtmlExporter().export(sample_report)
        assert 'class="toc"' in html

    def test_contains_print_media(self, sample_report):
        html = HtmlExporter().export(sample_report)
        assert "@media print" in html

    def test_utf8_encodable(self, sample_report):
        html = HtmlExporter().export(sample_report)
        encoded = html.encode("utf-8")
        assert len(encoded) > 0

    def test_max_width_960(self, sample_report):
        html = HtmlExporter().export(sample_report)
        assert "960px" in html


# ══════════════════════════════════════════════════════════════════════════════
# F. DocxExporter
# ══════════════════════════════════════════════════════════════════════════════

class TestDocxExporter:
    def test_is_available_returns_bool(self):
        result = DocxExporter().is_available()
        assert isinstance(result, bool)

    def test_export_returns_bytes_if_available(self, sample_report):
        exp = DocxExporter()
        if not exp.is_available():
            pytest.skip("python-docx not installed")
        data = exp.export(sample_report)
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_export_raises_import_error_if_unavailable(self, sample_report):
        exp = DocxExporter()
        if exp.is_available():
            pytest.skip("python-docx is installed — cannot test unavailable path")
        with pytest.raises(ImportError):
            exp.export(sample_report)

    def test_bytes_is_zip_signature_if_available(self, sample_report):
        """docx files are ZIP archives starting with PK\\x03\\x04."""
        exp = DocxExporter()
        if not exp.is_available():
            pytest.skip("python-docx not installed")
        data = exp.export(sample_report)
        assert data[:2] == b"PK"


# ══════════════════════════════════════════════════════════════════════════════
# G. PdfExporter
# ══════════════════════════════════════════════════════════════════════════════

class TestPdfExporter:
    def test_is_available_returns_bool(self):
        result = PdfExporter().is_available()
        assert isinstance(result, bool)

    def test_unavailable_raises_runtime_error(self, sample_report):
        exp = PdfExporter()
        if exp.is_available():
            pytest.skip("WeasyPrint is installed — cannot test unavailable path")
        with pytest.raises(RuntimeError):
            exp.export(sample_report)

    def test_export_returns_bytes_if_available(self, sample_report):
        exp = PdfExporter()
        if not exp.is_available():
            pytest.skip("WeasyPrint not installed")
        data = exp.export(sample_report)
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_export_pdf_signature_if_available(self, sample_report):
        exp = PdfExporter()
        if not exp.is_available():
            pytest.skip("WeasyPrint not installed")
        data = exp.export(sample_report)
        assert data[:4] == b"%PDF"


# ══════════════════════════════════════════════════════════════════════════════
# H. DISCLAIMER constant
# ══════════════════════════════════════════════════════════════════════════════

class TestDisclaimerConstant:
    def test_not_empty(self):
        assert len(DISCLAIMER) > 20

    def test_no_science_claims(self):
        # Should mention it's NOT a scientific conclusion
        assert "科學" in DISCLAIMER or "娛樂" in DISCLAIMER

    def test_mention_medical_or_legal(self):
        assert "醫療" in DISCLAIMER or "法律" in DISCLAIMER


# ══════════════════════════════════════════════════════════════════════════════
# I. Generator to_docx / to_pdf
# ══════════════════════════════════════════════════════════════════════════════

class TestGeneratorExportMethods:
    def test_to_markdown_returns_str(self, sample_report):
        md = ReportGenerator().to_markdown(sample_report)
        assert isinstance(md, str)

    def test_to_html_returns_str(self, sample_report):
        html = ReportGenerator().to_html(sample_report)
        assert isinstance(html, str)

    def test_to_docx_returns_bytes_if_available(self, sample_report):
        if not DocxExporter().is_available():
            pytest.skip("python-docx not installed")
        data = ReportGenerator().to_docx(sample_report)
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_to_pdf_raises_if_unavailable(self, sample_report):
        if PdfExporter().is_available():
            pytest.skip("WeasyPrint installed — cannot test unavailable path")
        with pytest.raises(RuntimeError):
            ReportGenerator().to_pdf(sample_report)
