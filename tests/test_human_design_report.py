"""
Tests for V1.9.0 Human Design report integration.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import date, time


def _make_profile(name="TestHD", birth_time_known=True):
    from core.models import (
        BirthProfile, BloodType, AnalysisTheme,
        ReportLanguage, ReportLength,
    )
    bt = time(12, 0) if birth_time_known else None
    return BirthProfile(
        name=name,
        birth_date=date(1990, 1, 1),
        birth_time=bt,
        birth_city="台北",
        birth_country="台灣",
        themes=list(AnalysisTheme),
        report_language=ReportLanguage.TRADITIONAL_CHINESE,
        report_length=ReportLength.FULL,
        birth_latitude=25.0330,
        birth_longitude=121.5654,
        birth_timezone_offset=8.0,
        birth_time_is_known=birth_time_known,
    )


@pytest.fixture(scope="module")
def full_report():
    from reports.generator import ReportGenerator
    return ReportGenerator().generate(_make_profile(), persist=False)


@pytest.fixture(scope="module")
def markdown_text(full_report):
    from reports.markdown_exporter import MarkdownExporter
    return MarkdownExporter().export(full_report)


@pytest.fixture(scope="module")
def html_text(full_report):
    from reports.html_exporter import HtmlExporter
    return HtmlExporter().export(full_report)


# ── A. Markdown content ───────────────────────────────────────────────────────

class TestMarkdownContent:
    def test_contains_human_design_section(self, markdown_text):
        assert "人類圖" in markdown_text or "Human Design" in markdown_text

    def test_contains_type(self, markdown_text):
        assert "Type" in markdown_text or "類型" in markdown_text

    def test_contains_strategy(self, markdown_text):
        assert "Strategy" in markdown_text or "策略" in markdown_text

    def test_contains_authority(self, markdown_text):
        assert "Authority" in markdown_text or "權威" in markdown_text

    def test_contains_profile(self, markdown_text):
        assert "Profile" in markdown_text or "角色" in markdown_text

    def test_contains_centers(self, markdown_text):
        assert "中心" in markdown_text or "Center" in markdown_text

    def test_contains_channels(self, markdown_text):
        assert "通道" in markdown_text or "Channel" in markdown_text

    def test_contains_conscious(self, markdown_text):
        assert "Conscious" in markdown_text or "意識" in markdown_text

    def test_contains_design(self, markdown_text):
        assert "Design" in markdown_text or "設計" in markdown_text


# ── B. HTML export ────────────────────────────────────────────────────────────

class TestHtmlContent:
    def test_html_contains_human_design_section(self, html_text):
        assert "Human Design" in html_text or "人類圖" in html_text


# ── C. Word export ────────────────────────────────────────────────────────────

class TestWordExport:
    def test_word_export_does_not_crash(self, full_report):
        try:
            from reports.docx_exporter import DocxExporter
            result = DocxExporter().export(full_report)
            assert isinstance(result, bytes)
        except ImportError:
            pytest.skip("python-docx not installed")


# ── D. Report with human_design_chart=None ───────────────────────────────────

class TestNullHumanDesignChart:
    def test_old_report_without_hd_does_not_crash(self):
        """FullReport with human_design_chart=None must still render."""
        from core.models import (
            BirthProfile, BloodType, AnalysisTheme, ReportLanguage, ReportLength,
        )
        from reports.generator import ReportGenerator
        from reports.markdown_exporter import MarkdownExporter
        p = BirthProfile(
            name="NoHD",
            birth_date=date(1990, 1, 1),
            birth_time=time(12, 0),
            birth_city="台北",
            birth_country="台灣",
            themes=list(AnalysisTheme),
            report_language=ReportLanguage.TRADITIONAL_CHINESE,
            report_length=ReportLength.SHORT,
            birth_time_is_known=True,
        )
        report = ReportGenerator().generate(p, persist=False)
        # Force null
        report.human_design_chart = None
        md = MarkdownExporter().export(report)
        assert md is not None
        assert len(md) > 0

    def test_full_report_with_null_hd_renders(self):
        from core.models import (
            BirthProfile, BloodType, AnalysisTheme, ReportLanguage, ReportLength,
        )
        from reports.generator import ReportGenerator
        from reports.templates import render_report
        p = BirthProfile(
            name="NoHDFull",
            birth_date=date(1990, 1, 1),
            birth_time=time(12, 0),
            birth_city="台北",
            birth_country="台灣",
            themes=list(AnalysisTheme),
            report_language=ReportLanguage.TRADITIONAL_CHINESE,
            report_length=ReportLength.FULL,
            birth_time_is_known=True,
        )
        report = ReportGenerator().generate(p, persist=False)
        report.human_design_chart = None
        text = render_report(report)
        assert text is not None


# ── E. HD chart in report ─────────────────────────────────────────────────────

class TestHDChartInReport:
    def test_report_has_hd_chart(self, full_report):
        assert full_report.human_design_chart is not None

    def test_hd_chart_type_not_empty(self, full_report):
        assert full_report.human_design_chart.type_name != ""

    def test_hd_chart_centers_count(self, full_report):
        assert len(full_report.human_design_chart.centers) == 9


# ── F. V1.9.1 Narrative & Validation in report ────────────────────────────────

class TestHDNarrativeInReport:
    def test_markdown_contains_validation_section(self, markdown_text):
        assert "人類圖準確度" in markdown_text

    def test_markdown_contains_type_narrative(self, markdown_text):
        assert "類型解讀" in markdown_text or "能量運作方式" in markdown_text

    def test_markdown_contains_authority_narrative(self, markdown_text):
        assert "內在權威" in markdown_text

    def test_markdown_contains_profile_narrative(self, markdown_text):
        assert "人生角色" in markdown_text

    def test_markdown_contains_centers_table(self, markdown_text):
        assert "已定義" in markdown_text or "開放" in markdown_text

    def test_markdown_contains_incarnation_cross(self, markdown_text):
        assert "輪迴交叉" in markdown_text

    def test_hd_narrative_render_does_not_crash(self, full_report):
        from human_design.templates import render_hd_full_narrative
        result = render_hd_full_narrative(full_report.human_design_chart)
        assert isinstance(result, str)
        assert len(result) > 100

    def test_hd_narrative_contains_overview_table(self, full_report):
        from human_design.templates import render_hd_full_narrative
        result = render_hd_full_narrative(full_report.human_design_chart)
        assert "人類圖總覽" in result

    def test_full_report_null_hd_narrative_skipped(self):
        from core.models import (
            BirthProfile, AnalysisTheme, ReportLanguage, ReportLength,
        )
        from reports.generator import ReportGenerator
        from reports.templates import render_report
        from datetime import date, time
        p = BirthProfile(
            name="NoHDNarrative",
            birth_date=date(1990, 1, 1),
            birth_time=time(12, 0),
            birth_city="台北",
            birth_country="台灣",
            themes=list(AnalysisTheme),
            report_language=ReportLanguage.TRADITIONAL_CHINESE,
            report_length=ReportLength.FULL,
            birth_time_is_known=True,
        )
        report = ReportGenerator().generate(p, persist=False)
        report.human_design_chart = None
        text = render_report(report)
        assert text is not None
