"""Tests for ReportGenerator — end-to-end pipeline (no DB persistence)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import date, time
from core.models import (
    BirthProfile, BloodType, AnalysisTheme,
    ReportLanguage, ReportLength, FullReport,
)
from reports.generator import ReportGenerator
from reports.markdown_exporter import MarkdownExporter
from reports.html_exporter import HtmlExporter


@pytest.fixture
def sample_profile():
    return BirthProfile(
        name="測試用戶",
        birth_date=date(1990, 6, 15),
        birth_time=time(14, 30),
        birth_city="台北市",
        birth_country="台灣",
        blood_type=BloodType.A,
        themes=list(AnalysisTheme),
        report_language=ReportLanguage.TRADITIONAL_CHINESE,
        report_length=ReportLength.STANDARD,
    )


@pytest.fixture
def sample_profile_no_time():
    return BirthProfile(
        name="無時間用戶",
        birth_date=date(1985, 3, 22),
        birth_city="高雄市",
        birth_country="台灣",
        blood_type=BloodType.O,
        report_length=ReportLength.SHORT,
    )


@pytest.fixture
def generator():
    return ReportGenerator()


class TestReportGeneration:
    def test_generates_full_report(self, generator, sample_profile):
        report = generator.generate(sample_profile, persist=False)
        assert isinstance(report, FullReport)
        assert report.profile.name == "測試用戶"

    def test_all_charts_present(self, generator, sample_profile):
        report = generator.generate(sample_profile, persist=False)
        assert report.western_chart is not None
        assert report.bazi_chart is not None
        assert report.ziwei_chart is not None
        assert report.blood_type_analysis is not None
        assert report.numerology_chart is not None
        assert report.synthesis is not None

    def test_bazi_correct_structure(self, generator, sample_profile):
        report = generator.generate(sample_profile, persist=False)
        bc = report.bazi_chart
        assert bc.year_pillar is not None
        assert bc.month_pillar is not None
        assert bc.day_pillar is not None
        assert bc.hour_pillar is not None  # time provided
        assert len(bc.five_element_ratio) == 5
        assert abs(sum(bc.five_element_ratio.values()) - 100.0) < 1.0

    def test_bazi_no_hour_when_no_time(self, generator, sample_profile_no_time):
        report = generator.generate(sample_profile_no_time, persist=False)
        assert report.bazi_chart.hour_pillar is None

    def test_western_chart_has_all_planets(self, generator, sample_profile):
        report = generator.generate(sample_profile, persist=False)
        planet_names = [pp.planet.value for pp in report.western_chart.planet_positions]
        assert "太陽" in planet_names
        assert "月亮" in planet_names
        assert "金星" in planet_names

    def test_western_sun_sign_deterministic(self, generator):
        p1 = BirthProfile(name="A", birth_date=date(1990, 6, 15),
                          birth_city="台北", birth_country="台灣")
        p2 = BirthProfile(name="B", birth_date=date(1990, 6, 15),
                          birth_city="台北", birth_country="台灣")
        r1 = generator.generate(p1, persist=False)
        r2 = generator.generate(p2, persist=False)
        sun1 = next(pp for pp in r1.western_chart.planet_positions if pp.planet.value == "太陽")
        sun2 = next(pp for pp in r2.western_chart.planet_positions if pp.planet.value == "太陽")
        assert sun1.sign == sun2.sign

    def test_synthesis_has_content(self, generator, sample_profile):
        report = generator.generate(sample_profile, persist=False)
        s = report.synthesis
        assert len(s.core_personality) > 50
        assert len(s.love_pattern) > 20
        assert isinstance(s.suitable_careers, list)

    def test_created_at_set(self, generator, sample_profile):
        report = generator.generate(sample_profile, persist=False)
        assert report.created_at is not None
        assert len(report.created_at) >= 10


class TestMarkdownExport:
    def test_produces_markdown(self, generator, sample_profile):
        report = generator.generate(sample_profile, persist=False)
        md = MarkdownExporter().export(report)
        assert isinstance(md, str)
        assert len(md) > 500
        assert "測試用戶" in md
        assert "#" in md  # has headings

    def test_full_report_longer_than_standard(self, generator):
        p_full = BirthProfile(name="長版", birth_date=date(1990, 1, 1),
                              birth_city="台北", birth_country="台灣",
                              report_length=ReportLength.FULL)
        p_std  = BirthProfile(name="標準", birth_date=date(1990, 1, 1),
                              birth_city="台北", birth_country="台灣",
                              report_length=ReportLength.STANDARD)
        r_full = generator.generate(p_full, persist=False)
        r_std  = generator.generate(p_std, persist=False)
        md_full = MarkdownExporter().export(r_full)
        md_std  = MarkdownExporter().export(r_std)
        assert len(md_full) > len(md_std)


class TestHtmlExport:
    def test_produces_html(self, generator, sample_profile):
        report = generator.generate(sample_profile, persist=False)
        html = HtmlExporter().export(report)
        assert html.startswith("<!DOCTYPE html>")
        assert "測試用戶" in html
        assert "</html>" in html

    def test_contains_style_block(self, generator, sample_profile):
        report = generator.generate(sample_profile, persist=False)
        html = HtmlExporter().export(report)
        assert "<style>" in html
