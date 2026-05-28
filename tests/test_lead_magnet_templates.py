"""
Tests for V1.9.6 Lead Magnet Templates.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


def _make_result():
    from lead_magnet.models import FreeReportResult, FreeReportSection
    return FreeReportResult(
        lead_id="lead_test",
        report_type="zodiac_free_summary",
        title="免費星座速覽：測試",
        summary="這是測試摘要。",
        sections=[
            FreeReportSection(heading="第一節", body="節的內容。", bullets=["重點 A"]),
        ],
        cta_title="升級完整報告",
        cta_description="建立完整命盤報告。",
        cta_button_label="建立完整命盤報告",
        cta_target="📝 輸入資料",
        disclaimer="本報告為免費初步摘要，僅供探索參考。",
    )


class TestRenderFreeReportMarkdown:
    def test_contains_title(self):
        from lead_magnet.templates import render_free_report_markdown
        md = render_free_report_markdown(_make_result())
        assert "免費星座速覽：測試" in md

    def test_contains_cta(self):
        from lead_magnet.templates import render_free_report_markdown
        md = render_free_report_markdown(_make_result())
        assert "建立完整命盤報告" in md

    def test_contains_disclaimer(self):
        from lead_magnet.templates import render_free_report_markdown
        md = render_free_report_markdown(_make_result())
        assert "摘要" in md

    def test_contains_footer(self):
        from lead_magnet.templates import render_free_report_markdown
        md = render_free_report_markdown(_make_result())
        assert "Astro Destiny Analyzer" in md

    def test_returns_string(self):
        from lead_magnet.templates import render_free_report_markdown
        assert isinstance(render_free_report_markdown(_make_result()), str)


class TestRenderFreeReportHtml:
    def test_contains_meta_charset_utf8(self):
        from lead_magnet.templates import render_free_report_html
        html = render_free_report_html(_make_result())
        assert "charset=utf-8" in html.lower() or 'charset="utf-8"' in html.lower()

    def test_contains_cta(self):
        from lead_magnet.templates import render_free_report_html
        html = render_free_report_html(_make_result())
        assert "建立完整命盤報告" in html

    def test_no_script_tag(self):
        from lead_magnet.templates import render_free_report_html
        html = render_free_report_html(_make_result())
        assert "<script" not in html.lower()

    def test_no_cdn(self):
        from lead_magnet.templates import render_free_report_html
        html = render_free_report_html(_make_result())
        assert "cdn." not in html.lower()

    def test_contains_footer(self):
        from lead_magnet.templates import render_free_report_html
        html = render_free_report_html(_make_result())
        assert "Astro Destiny Analyzer" in html

    def test_returns_string(self):
        from lead_magnet.templates import render_free_report_html
        assert isinstance(render_free_report_html(_make_result()), str)


class TestRenderLeadCaptureCopy:
    def test_has_consent_text(self):
        from lead_magnet.templates import render_lead_capture_copy
        copy = render_lead_capture_copy("zodiac_free_summary")
        assert "consent_text" in copy
        assert copy["consent_text"] != ""

    def test_has_button_label(self):
        from lead_magnet.templates import render_lead_capture_copy
        copy = render_lead_capture_copy("zodiac_free_summary")
        assert "button_label" in copy
        assert copy["button_label"] != ""

    def test_has_title(self):
        from lead_magnet.templates import render_lead_capture_copy
        copy = render_lead_capture_copy("integrated_free_summary")
        assert "title" in copy

    def test_unknown_type_returns_default(self):
        from lead_magnet.templates import render_lead_capture_copy
        copy = render_lead_capture_copy("unknown_type")
        assert "consent_text" in copy


class TestRenderUpgradeCta:
    def test_has_button_label(self):
        from lead_magnet.templates import render_upgrade_cta
        cta = render_upgrade_cta("zodiac_free_summary")
        assert "button_label" in cta
        assert cta["button_label"] != ""

    def test_has_target(self):
        from lead_magnet.templates import render_upgrade_cta
        cta = render_upgrade_cta("compatibility_free_summary")
        assert "target" in cta

    def test_compatibility_targets_synastry(self):
        from lead_magnet.templates import render_upgrade_cta
        cta = render_upgrade_cta("compatibility_free_summary")
        assert "合盤" in cta["target"] or "合盤" in cta["button_label"]


class TestSafeFreeReportFilename:
    def test_no_emoji(self):
        from lead_magnet.exporters import safe_free_report_filename
        fn = safe_free_report_filename("test 🎁 user", "zodiac_free_summary", "md")
        assert "🎁" not in fn

    def test_no_illegal_chars(self):
        from lead_magnet.exporters import safe_free_report_filename
        fn = safe_free_report_filename('test/user:name*"', "zodiac_free_summary", "html")
        for ch in r'\/:*?"<>|':
            assert ch not in fn

    def test_starts_with_free_report(self):
        from lead_magnet.exporters import safe_free_report_filename
        fn = safe_free_report_filename("user", "zodiac_free_summary", "md")
        assert fn.startswith("free_report_")

    def test_correct_suffix(self):
        from lead_magnet.exporters import safe_free_report_filename
        fn = safe_free_report_filename("user", "zodiac_free_summary", "html")
        assert fn.endswith(".html")

    def test_empty_name_safe(self):
        from lead_magnet.exporters import safe_free_report_filename
        fn = safe_free_report_filename("", "zodiac_free_summary", "md")
        assert fn.endswith(".md")
        assert "free_report_" in fn
