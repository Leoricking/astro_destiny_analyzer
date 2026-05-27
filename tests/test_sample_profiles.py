"""
Tests for V1.6.1 demo sample profiles.
Verifies that all sample profiles are valid BirthProfile instances,
can produce reports without crash, and have the expected fields.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import date

from core.models import BirthProfile, ReportLength
from demo.sample_profiles import (
    SAMPLE_PROFILES, SAMPLE_LABELS,
    sample_taipei_known_time,
    sample_hsinchu_tech_career,
    sample_unknown_time,
)
from reports.generator import ReportGenerator


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def generator():
    return ReportGenerator()


# ══════════════════════════════════════════════════════════════════════════════
# A. Sample profile list structure
# ══════════════════════════════════════════════════════════════════════════════

class TestSampleProfileList:
    def test_at_least_3_profiles(self):
        assert len(SAMPLE_PROFILES) >= 3

    def test_labels_match_profiles_count(self):
        assert len(SAMPLE_LABELS) == len(SAMPLE_PROFILES)

    def test_all_are_birth_profiles(self):
        for p in SAMPLE_PROFILES:
            assert isinstance(p, BirthProfile)

    def test_all_names_start_with_demo(self):
        for p in SAMPLE_PROFILES:
            assert p.name.startswith("Demo"), f"{p.name!r} does not start with 'Demo'"

    def test_labels_match_names(self):
        for label, profile in zip(SAMPLE_LABELS, SAMPLE_PROFILES):
            assert label == profile.name


# ══════════════════════════════════════════════════════════════════════════════
# B. sample_taipei_known_time
# ══════════════════════════════════════════════════════════════════════════════

class TestSampleTaipei:
    def test_has_birth_time(self):
        assert sample_taipei_known_time.birth_time is not None

    def test_birth_time_is_known(self):
        assert sample_taipei_known_time.birth_time_is_known is True

    def test_birth_date(self):
        assert sample_taipei_known_time.birth_date == date(1990, 2, 5)

    def test_birth_city_taipei(self):
        assert "台北" in sample_taipei_known_time.birth_city

    def test_has_coordinates(self):
        assert sample_taipei_known_time.birth_latitude is not None
        assert sample_taipei_known_time.birth_longitude is not None

    def test_themes_not_empty(self):
        assert len(sample_taipei_known_time.themes) > 0

    def test_report_length_valid(self):
        assert sample_taipei_known_time.report_length in list(ReportLength)

    def test_generates_report(self, generator):
        report = generator.generate(sample_taipei_known_time, persist=False)
        assert report is not None
        assert report.profile.name == "Demo 台北精準時間"

    def test_report_has_all_charts(self, generator):
        report = generator.generate(sample_taipei_known_time, persist=False)
        assert report.western_chart is not None
        assert report.bazi_chart is not None
        assert report.ziwei_chart is not None


# ══════════════════════════════════════════════════════════════════════════════
# C. sample_hsinchu_tech_career
# ══════════════════════════════════════════════════════════════════════════════

class TestSampleHsinchu:
    def test_has_birth_time(self):
        assert sample_hsinchu_tech_career.birth_time is not None

    def test_birth_date(self):
        assert sample_hsinchu_tech_career.birth_date == date(1989, 9, 21)

    def test_full_report_length(self):
        assert sample_hsinchu_tech_career.report_length == ReportLength.FULL

    def test_themes_not_empty(self):
        assert len(sample_hsinchu_tech_career.themes) > 0

    def test_themes_include_career(self):
        from core.models import AnalysisTheme
        assert AnalysisTheme.CAREER in sample_hsinchu_tech_career.themes

    def test_themes_include_wealth(self):
        from core.models import AnalysisTheme
        assert AnalysisTheme.WEALTH in sample_hsinchu_tech_career.themes

    def test_generates_report_no_crash(self, generator):
        report = generator.generate(sample_hsinchu_tech_career, persist=False)
        assert report is not None

    def test_report_is_full_length(self, generator):
        from reports.markdown_exporter import MarkdownExporter
        report = generator.generate(sample_hsinchu_tech_career, persist=False)
        md = MarkdownExporter().export(report)
        assert len(md) > 1000


# ══════════════════════════════════════════════════════════════════════════════
# D. sample_unknown_time
# ══════════════════════════════════════════════════════════════════════════════

class TestSampleUnknownTime:
    def test_no_birth_time(self):
        assert sample_unknown_time.birth_time is None

    def test_birth_time_not_known(self):
        assert sample_unknown_time.birth_time_is_known is False

    def test_birth_date(self):
        assert sample_unknown_time.birth_date == date(1995, 6, 15)

    def test_themes_not_empty(self):
        assert len(sample_unknown_time.themes) > 0

    def test_generates_report_no_crash(self, generator):
        report = generator.generate(sample_unknown_time, persist=False)
        assert report is not None

    def test_ziwei_partial_layout(self, generator):
        """Without birth time, ziwei should use partial_lunar_only or mock mode."""
        report = generator.generate(sample_unknown_time, persist=False)
        zc = report.ziwei_chart
        mode = getattr(zc, "calculation_mode", "")
        assert mode in ("partial_lunar_only", "mock_fallback"), (
            f"Expected partial or mock mode, got: {mode!r}"
        )

    def test_western_chart_present(self, generator):
        report = generator.generate(sample_unknown_time, persist=False)
        assert report.western_chart is not None

    def test_bazi_no_hour_pillar(self, generator):
        report = generator.generate(sample_unknown_time, persist=False)
        assert report.bazi_chart.hour_pillar is None


# ══════════════════════════════════════════════════════════════════════════════
# E. All samples generate valid exports
# ══════════════════════════════════════════════════════════════════════════════

class TestSampleExports:
    @pytest.mark.parametrize("idx", [0, 1, 2])
    def test_markdown_export_no_crash(self, generator, idx):
        from reports.markdown_exporter import MarkdownExporter
        profile = SAMPLE_PROFILES[idx]
        report = generator.generate(profile, persist=False)
        md = MarkdownExporter().export(report)
        assert isinstance(md, str)
        assert len(md) > 200

    @pytest.mark.parametrize("idx", [0, 1, 2])
    def test_html_export_no_crash(self, generator, idx):
        from reports.html_exporter import HtmlExporter
        profile = SAMPLE_PROFILES[idx]
        report = generator.generate(profile, persist=False)
        html = HtmlExporter().export(report)
        assert "<html" in html
        assert profile.name in html
