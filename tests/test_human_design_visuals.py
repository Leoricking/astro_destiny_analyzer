"""
Tests for V1.9.1 Human Design visuals module.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


def _make_chart():
    """Return a HumanDesignChart using the engine."""
    from human_design.engine import HumanDesignEngine
    from core.models import BirthProfile, BloodType, AnalysisTheme, ReportLanguage, ReportLength
    from datetime import date, time
    profile = BirthProfile(
        name="VisualsTest",
        birth_date=date(1990, 6, 15),
        birth_time=time(12, 0),
        birth_city="台北",
        birth_country="台灣",
        themes=list(AnalysisTheme),
        report_language=ReportLanguage.TRADITIONAL_CHINESE,
        report_length=ReportLength.FULL,
        birth_latitude=25.0330,
        birth_longitude=121.5654,
        birth_timezone_offset=8.0,
        birth_time_is_known=True,
    )
    return HumanDesignEngine().calculate(profile)


# ── A. build_hd_visuals ───────────────────────────────────────────────────────

class TestBuildHdVisuals:
    def test_returns_hdvisualbundle(self):
        from human_design.visuals import build_hd_visuals, HDVisualBundle
        chart = _make_chart()
        bundle = build_hd_visuals(chart)
        assert isinstance(bundle, HDVisualBundle)

    def test_bundle_has_9_centers(self):
        from human_design.visuals import build_hd_visuals
        chart = _make_chart()
        bundle = build_hd_visuals(chart)
        assert len(bundle.centers) == 9

    def test_center_order_head_first(self):
        from human_design.visuals import build_hd_visuals
        chart = _make_chart()
        bundle = build_hd_visuals(chart)
        assert bundle.centers[0].center == "Head"

    def test_center_order_root_last(self):
        from human_design.visuals import build_hd_visuals
        chart = _make_chart()
        bundle = build_hd_visuals(chart)
        assert bundle.centers[-1].center == "Root"

    def test_defined_plus_open_equals_9(self):
        from human_design.visuals import build_hd_visuals
        chart = _make_chart()
        bundle = build_hd_visuals(chart)
        assert bundle.defined_count + bundle.open_count == 9

    def test_defined_percentage_in_range(self):
        from human_design.visuals import build_hd_visuals
        chart = _make_chart()
        bundle = build_hd_visuals(chart)
        assert 0.0 <= bundle.defined_percentage <= 100.0

    def test_summary_not_empty(self):
        from human_design.visuals import build_hd_visuals
        chart = _make_chart()
        bundle = build_hd_visuals(chart)
        assert bundle.summary != ""

    def test_center_state_label_valid(self):
        from human_design.visuals import build_hd_visuals
        chart = _make_chart()
        bundle = build_hd_visuals(chart)
        for v in bundle.centers:
            assert v.state_label in ("已定義", "開放")

    def test_center_zh_name_present(self):
        from human_design.visuals import build_hd_visuals
        chart = _make_chart()
        bundle = build_hd_visuals(chart)
        for v in bundle.centers:
            assert v.center_zh != ""


# ── B. render functions ───────────────────────────────────────────────────────

class TestRenderFunctions:
    def test_render_markdown_table_returns_string(self):
        from human_design.visuals import build_hd_visuals, render_centers_markdown_table
        chart = _make_chart()
        bundle = build_hd_visuals(chart)
        result = render_centers_markdown_table(bundle)
        assert isinstance(result, str)

    def test_render_markdown_table_contains_header(self):
        from human_design.visuals import build_hd_visuals, render_centers_markdown_table
        chart = _make_chart()
        bundle = build_hd_visuals(chart)
        result = render_centers_markdown_table(bundle)
        assert "中心" in result

    def test_render_html_returns_string(self):
        from human_design.visuals import build_hd_visuals, render_centers_html
        chart = _make_chart()
        bundle = build_hd_visuals(chart)
        result = render_centers_html(bundle)
        assert isinstance(result, str)

    def test_render_html_contains_table_tag(self):
        from human_design.visuals import build_hd_visuals, render_centers_html
        chart = _make_chart()
        bundle = build_hd_visuals(chart)
        result = render_centers_html(bundle)
        assert "<table" in result
