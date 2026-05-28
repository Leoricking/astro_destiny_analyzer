"""
Tests for V1.9.1 Human Design validation module.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


def _make_mock_chart(calculation_mode: str = "mock_fallback"):
    """Return a minimal HumanDesignChart with the given calculation_mode."""
    from human_design.engine import HumanDesignEngine
    from core.models import BirthProfile, BloodType, AnalysisTheme, ReportLanguage, ReportLength
    from datetime import date, time
    profile = BirthProfile(
        name="ValidTest",
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
    chart = HumanDesignEngine().calculate(profile)
    # Override calculation_mode for testing
    object.__setattr__(chart, "calculation_mode", calculation_mode)
    return chart


# ── A. build_validation_status ────────────────────────────────────────────────

class TestBuildValidationStatus:
    def test_returns_hdvalidationstatus_object(self):
        from human_design.validation import build_validation_status, HDValidationStatus
        chart = _make_mock_chart()
        status = build_validation_status(chart)
        assert isinstance(status, HDValidationStatus)

    def test_ephemeris_status_mock_fallback(self):
        from human_design.validation import build_validation_status
        chart = _make_mock_chart("mock_fallback")
        status = build_validation_status(chart)
        assert "mock" in status.ephemeris_status.lower() or "unavailable" in status.ephemeris_status.lower()

    def test_ephemeris_status_swiss_ephemeris(self):
        from human_design.validation import build_validation_status
        chart = _make_mock_chart("swiss_ephemeris_phase1")
        status = build_validation_status(chart)
        assert "Swiss" in status.ephemeris_status or "swiss" in status.ephemeris_status.lower()

    def test_ephemeris_status_partial(self):
        from human_design.validation import build_validation_status
        chart = _make_mock_chart("partial")
        status = build_validation_status(chart)
        assert "Partial" in status.ephemeris_status or "partial" in status.ephemeris_status.lower()

    def test_warnings_not_empty(self):
        from human_design.validation import build_validation_status
        chart = _make_mock_chart()
        status = build_validation_status(chart)
        assert len(status.warnings) >= 1

    def test_notes_not_empty(self):
        from human_design.validation import build_validation_status
        chart = _make_mock_chart()
        status = build_validation_status(chart)
        assert len(status.notes) >= 1

    def test_validation_level_is_phase1(self):
        from human_design.validation import build_validation_status
        chart = _make_mock_chart()
        status = build_validation_status(chart)
        assert status.validation_level == "phase1_internal"

    def test_gate_table_status_not_empty(self):
        from human_design.validation import build_validation_status
        chart = _make_mock_chart()
        status = build_validation_status(chart)
        assert status.gate_table_status != ""

    def test_design_time_method_not_empty(self):
        from human_design.validation import build_validation_status
        chart = _make_mock_chart()
        status = build_validation_status(chart)
        assert status.design_time_method != ""


# ── B. render_validation_markdown ─────────────────────────────────────────────

class TestRenderValidationMarkdown:
    def test_render_returns_string(self):
        from human_design.validation import build_validation_status, render_validation_markdown
        chart = _make_mock_chart()
        status = build_validation_status(chart)
        result = render_validation_markdown(status)
        assert isinstance(result, str)

    def test_render_contains_section_heading(self):
        from human_design.validation import build_validation_status, render_validation_markdown
        chart = _make_mock_chart()
        status = build_validation_status(chart)
        result = render_validation_markdown(status)
        assert "人類圖準確度" in result

    def test_render_contains_warning_symbol(self):
        from human_design.validation import build_validation_status, render_validation_markdown
        chart = _make_mock_chart()
        status = build_validation_status(chart)
        result = render_validation_markdown(status)
        assert "⚠️" in result

    def test_render_contains_validation_level(self):
        from human_design.validation import build_validation_status, render_validation_markdown
        chart = _make_mock_chart()
        status = build_validation_status(chart)
        result = render_validation_markdown(status)
        assert "phase1_internal" in result

    def test_validation_notes_mention_external_sources(self):
        from human_design.validation import build_validation_status
        chart = _make_mock_chart()
        status = build_validation_status(chart)
        all_notes = " ".join(status.notes)
        # V1.9.2: validation notes should reference external cross-reference sources
        assert (
            "Jovian Archive" in all_notes
            or "Genetic Matrix" in all_notes
            or "MyBodyGraph" in all_notes
            or "external" in all_notes.lower()
        )


# ── C. V1.9.3 new fields ──────────────────────────────────────────────────────

class TestV193ValidationFields:
    def test_status_has_design_date_method_field(self):
        from human_design.validation import build_validation_status, HDValidationStatus
        chart = _make_mock_chart()
        status = build_validation_status(chart)
        assert hasattr(status, "design_date_method")

    def test_status_has_gate_wheel_offset_field(self):
        from human_design.validation import build_validation_status
        chart = _make_mock_chart()
        status = build_validation_status(chart)
        assert hasattr(status, "gate_wheel_offset_degrees")
        assert isinstance(status.gate_wheel_offset_degrees, float)

    def test_status_has_solar_arc_error_field(self):
        from human_design.validation import build_validation_status
        chart = _make_mock_chart()
        status = build_validation_status(chart)
        assert hasattr(status, "solar_arc_error_degrees")

    def test_render_contains_method_info(self):
        from human_design.validation import build_validation_status, render_validation_markdown
        chart = _make_mock_chart()
        status = build_validation_status(chart)
        result = render_validation_markdown(status)
        assert "方法資訊" in result

    def test_render_contains_gate_wheel_offset_label(self):
        from human_design.validation import build_validation_status, render_validation_markdown
        chart = _make_mock_chart()
        status = build_validation_status(chart)
        result = render_validation_markdown(status)
        assert "Gate Wheel Offset" in result
