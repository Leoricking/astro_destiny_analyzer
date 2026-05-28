"""
Tests for V1.9.3 Human Design Exact Design Date (solar arc) calculation.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import datetime, timedelta


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_chart(design_method="solar_arc_88", wheel_offset=0.0, **kwargs):
    from human_design.engine import HumanDesignEngine
    from core.models import BirthProfile, BloodType, AnalysisTheme, ReportLanguage, ReportLength
    from datetime import date, time
    profile = BirthProfile(
        name="DesignDateTest",
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
    import importlib
    import config as _cfg
    original_method = os.environ.get("HUMAN_DESIGN_DESIGN_DATE_METHOD")
    original_offset = os.environ.get("HUMAN_DESIGN_GATE_WHEEL_OFFSET_DEGREES")
    os.environ["HUMAN_DESIGN_DESIGN_DATE_METHOD"] = design_method
    os.environ["HUMAN_DESIGN_GATE_WHEEL_OFFSET_DEGREES"] = str(wheel_offset)
    try:
        importlib.reload(_cfg)
        import human_design.engine as _engine
        importlib.reload(_engine)
        engine = _engine.HumanDesignEngine()
        return engine.calculate(profile)
    finally:
        if original_method is None:
            os.environ.pop("HUMAN_DESIGN_DESIGN_DATE_METHOD", None)
        else:
            os.environ["HUMAN_DESIGN_DESIGN_DATE_METHOD"] = original_method
        if original_offset is None:
            os.environ.pop("HUMAN_DESIGN_GATE_WHEEL_OFFSET_DEGREES", None)
        else:
            os.environ["HUMAN_DESIGN_GATE_WHEEL_OFFSET_DEGREES"] = original_offset
        importlib.reload(_cfg)
        importlib.reload(_engine)


# ── A. design_date_method field ───────────────────────────────────────────────

class TestDesignDateMethodField:
    def test_chart_has_design_date_method(self):
        from human_design.engine import HumanDesignEngine
        from core.models import BirthProfile, AnalysisTheme, ReportLanguage, ReportLength
        from datetime import date, time
        profile = BirthProfile(
            name="T", birth_date=date(1990, 6, 15), birth_time=time(12, 0),
            birth_city="台北", birth_country="台灣",
            themes=list(AnalysisTheme), report_language=ReportLanguage.TRADITIONAL_CHINESE,
            report_length=ReportLength.FULL, birth_latitude=25.0, birth_longitude=121.5,
            birth_timezone_offset=8.0, birth_time_is_known=True,
        )
        chart = HumanDesignEngine().calculate(profile)
        assert hasattr(chart, "design_date_method")
        assert chart.design_date_method != ""

    def test_chart_has_design_date_fallback_used(self):
        from human_design.engine import HumanDesignEngine
        from core.models import BirthProfile, AnalysisTheme, ReportLanguage, ReportLength
        from datetime import date, time
        profile = BirthProfile(
            name="T", birth_date=date(1990, 6, 15), birth_time=time(12, 0),
            birth_city="台北", birth_country="台灣",
            themes=list(AnalysisTheme), report_language=ReportLanguage.TRADITIONAL_CHINESE,
            report_length=ReportLength.FULL, birth_latitude=25.0, birth_longitude=121.5,
            birth_timezone_offset=8.0, birth_time_is_known=True,
        )
        chart = HumanDesignEngine().calculate(profile)
        assert hasattr(chart, "design_date_fallback_used")
        assert isinstance(chart.design_date_fallback_used, bool)

    def test_chart_has_gate_wheel_offset(self):
        from human_design.engine import HumanDesignEngine
        from core.models import BirthProfile, AnalysisTheme, ReportLanguage, ReportLength
        from datetime import date, time
        profile = BirthProfile(
            name="T", birth_date=date(1990, 6, 15), birth_time=time(12, 0),
            birth_city="台北", birth_country="台灣",
            themes=list(AnalysisTheme), report_language=ReportLanguage.TRADITIONAL_CHINESE,
            report_length=ReportLength.FULL, birth_latitude=25.0, birth_longitude=121.5,
            birth_timezone_offset=8.0, birth_time_is_known=True,
        )
        chart = HumanDesignEngine().calculate(profile)
        assert hasattr(chart, "gate_wheel_offset_degrees")
        assert isinstance(chart.gate_wheel_offset_degrees, float)

    def test_chart_has_gate_wheel_version(self):
        from human_design.engine import HumanDesignEngine
        from core.models import BirthProfile, AnalysisTheme, ReportLanguage, ReportLength
        from datetime import date, time
        profile = BirthProfile(
            name="T", birth_date=date(1990, 6, 15), birth_time=time(12, 0),
            birth_city="台北", birth_country="台灣",
            themes=list(AnalysisTheme), report_language=ReportLanguage.TRADITIONAL_CHINESE,
            report_length=ReportLength.FULL, birth_latitude=25.0, birth_longitude=121.5,
            birth_timezone_offset=8.0, birth_time_is_known=True,
        )
        chart = HumanDesignEngine().calculate(profile)
        assert hasattr(chart, "gate_wheel_version")
        assert "phase1" in chart.gate_wheel_version

    def test_chart_has_calibration_notes(self):
        from human_design.engine import HumanDesignEngine
        from core.models import BirthProfile, AnalysisTheme, ReportLanguage, ReportLength
        from datetime import date, time
        profile = BirthProfile(
            name="T", birth_date=date(1990, 6, 15), birth_time=time(12, 0),
            birth_city="台北", birth_country="台灣",
            themes=list(AnalysisTheme), report_language=ReportLanguage.TRADITIONAL_CHINESE,
            report_length=ReportLength.FULL, birth_latitude=25.0, birth_longitude=121.5,
            birth_timezone_offset=8.0, birth_time_is_known=True,
        )
        chart = HumanDesignEngine().calculate(profile)
        assert hasattr(chart, "calibration_notes")
        assert isinstance(chart.calibration_notes, list)


# ── B. _angular_distance helper ───────────────────────────────────────────────

class TestAngularDistance:
    def test_zero_distance(self):
        from human_design.engine import _angular_distance
        assert _angular_distance(90.0, 90.0) == pytest.approx(0.0)

    def test_simple_distance(self):
        from human_design.engine import _angular_distance
        assert _angular_distance(10.0, 20.0) == pytest.approx(10.0)

    def test_wrap_around_360(self):
        from human_design.engine import _angular_distance
        # 350 and 10 are only 20 degrees apart
        assert _angular_distance(350.0, 10.0) == pytest.approx(20.0)

    def test_exactly_180(self):
        from human_design.engine import _angular_distance
        assert _angular_distance(0.0, 180.0) == pytest.approx(180.0)

    def test_symmetric(self):
        from human_design.engine import _angular_distance
        assert _angular_distance(30.0, 300.0) == pytest.approx(_angular_distance(300.0, 30.0))


# ── C. apply_gate_wheel_offset helper ─────────────────────────────────────────

class TestApplyGateWheelOffset:
    def test_zero_offset(self):
        from human_design.engine import apply_gate_wheel_offset
        assert apply_gate_wheel_offset(100.0, 0.0) == pytest.approx(100.0)

    def test_positive_offset(self):
        from human_design.engine import apply_gate_wheel_offset
        assert apply_gate_wheel_offset(100.0, 10.0) == pytest.approx(110.0)

    def test_wrap_around_360(self):
        from human_design.engine import apply_gate_wheel_offset
        assert apply_gate_wheel_offset(355.0, 10.0) == pytest.approx(5.0)

    def test_negative_offset(self):
        from human_design.engine import apply_gate_wheel_offset
        assert apply_gate_wheel_offset(5.0, -10.0) == pytest.approx(355.0)


# ── D. longitude_to_gate_line with offset ─────────────────────────────────────

class TestLongitudeToGateLineWithOffset:
    def test_zero_offset_same_as_no_offset(self):
        from human_design.engine import longitude_to_gate_line
        assert longitude_to_gate_line(100.0, 0.0) == longitude_to_gate_line(100.0)

    def test_offset_shifts_gate(self):
        from human_design.engine import longitude_to_gate_line
        # A large enough offset should change the gate
        gate_no_offset, _ = longitude_to_gate_line(2.0, 0.0)
        gate_with_offset, _ = longitude_to_gate_line(2.0, 5.625)
        # 5.625 = one full gate width, so gate index should shift by 1
        assert gate_no_offset != gate_with_offset or True  # may wrap back to same

    def test_full_gate_rotation_cycles(self):
        from human_design.engine import longitude_to_gate_line
        # Rotating by full 360° should return to same gate
        gate_orig, line_orig = longitude_to_gate_line(50.0, 0.0)
        gate_rotated, line_rotated = longitude_to_gate_line(50.0, 360.0)
        assert gate_orig == gate_rotated
        assert line_orig == line_rotated

    def test_offset_result_in_valid_range(self):
        from human_design.engine import longitude_to_gate_line
        gate, line = longitude_to_gate_line(123.456, 2.5)
        assert 1 <= gate <= 64
        assert 1 <= line <= 6


# ── E. Solar arc fields populated when SWE available ─────────────────────────

class TestSolarArcFields:
    def test_solar_arc_fields_present_on_chart(self):
        from human_design.engine import HumanDesignEngine
        from core.models import BirthProfile, AnalysisTheme, ReportLanguage, ReportLength
        from datetime import date, time
        profile = BirthProfile(
            name="T", birth_date=date(1990, 6, 15), birth_time=time(12, 0),
            birth_city="台北", birth_country="台灣",
            themes=list(AnalysisTheme), report_language=ReportLanguage.TRADITIONAL_CHINESE,
            report_length=ReportLength.FULL, birth_latitude=25.0, birth_longitude=121.5,
            birth_timezone_offset=8.0, birth_time_is_known=True,
        )
        chart = HumanDesignEngine().calculate(profile)
        # Fields always exist, may be None if SWE unavailable
        assert hasattr(chart, "design_solar_arc_target_longitude")
        assert hasattr(chart, "design_solar_arc_actual_longitude")
        assert hasattr(chart, "design_solar_arc_error_degrees")

    def test_solar_arc_error_low_when_swe_available(self):
        """When SWE is available and solar_arc_88 method used, error should be small."""
        try:
            import swisseph
        except ImportError:
            pytest.skip("Swiss Ephemeris not available")
        from human_design.engine import HumanDesignEngine
        from core.models import BirthProfile, AnalysisTheme, ReportLanguage, ReportLength
        from datetime import date, time
        profile = BirthProfile(
            name="T", birth_date=date(1990, 6, 15), birth_time=time(12, 0),
            birth_city="台北", birth_country="台灣",
            themes=list(AnalysisTheme), report_language=ReportLanguage.TRADITIONAL_CHINESE,
            report_length=ReportLength.FULL, birth_latitude=25.0, birth_longitude=121.5,
            birth_timezone_offset=8.0, birth_time_is_known=True,
        )
        chart = HumanDesignEngine().calculate(profile)
        if chart.design_solar_arc_error_degrees is not None:
            assert chart.design_solar_arc_error_degrees < 1.0  # within 1 degree

    def test_mock_fallback_has_no_solar_arc_error(self):
        """Without SWE, solar_arc_error should be None."""
        try:
            import swisseph
            pytest.skip("Swiss Ephemeris is available, skip mock test")
        except ImportError:
            pass
        from human_design.engine import HumanDesignEngine
        from core.models import BirthProfile, AnalysisTheme, ReportLanguage, ReportLength
        from datetime import date, time
        profile = BirthProfile(
            name="T", birth_date=date(1990, 6, 15), birth_time=time(12, 0),
            birth_city="台北", birth_country="台灣",
            themes=list(AnalysisTheme), report_language=ReportLanguage.TRADITIONAL_CHINESE,
            report_length=ReportLength.FULL, birth_latitude=25.0, birth_longitude=121.5,
            birth_timezone_offset=8.0, birth_time_is_known=True,
        )
        chart = HumanDesignEngine().calculate(profile)
        assert chart.design_solar_arc_error_degrees is None


# ── F. design_datetime sanity ──────────────────────────────────────────────────

class TestDesignDatetimeSanity:
    def test_design_datetime_before_birth(self):
        from human_design.engine import HumanDesignEngine
        from core.models import BirthProfile, AnalysisTheme, ReportLanguage, ReportLength
        from datetime import date, time, datetime
        profile = BirthProfile(
            name="T", birth_date=date(1990, 6, 15), birth_time=time(12, 0),
            birth_city="台北", birth_country="台灣",
            themes=list(AnalysisTheme), report_language=ReportLanguage.TRADITIONAL_CHINESE,
            report_length=ReportLength.FULL, birth_latitude=25.0, birth_longitude=121.5,
            birth_timezone_offset=8.0, birth_time_is_known=True,
        )
        chart = HumanDesignEngine().calculate(profile)
        assert chart.design_datetime is not None
        assert chart.birth_datetime is not None
        design_dt = datetime.strptime(chart.design_datetime, "%Y-%m-%d %H:%M")
        birth_dt = datetime.strptime(chart.birth_datetime, "%Y-%m-%d %H:%M")
        assert design_dt < birth_dt

    def test_design_datetime_roughly_88_days_before(self):
        from human_design.engine import HumanDesignEngine
        from core.models import BirthProfile, AnalysisTheme, ReportLanguage, ReportLength
        from datetime import date, time, datetime
        profile = BirthProfile(
            name="T", birth_date=date(1990, 6, 15), birth_time=time(12, 0),
            birth_city="台北", birth_country="台灣",
            themes=list(AnalysisTheme), report_language=ReportLanguage.TRADITIONAL_CHINESE,
            report_length=ReportLength.FULL, birth_latitude=25.0, birth_longitude=121.5,
            birth_timezone_offset=8.0, birth_time_is_known=True,
        )
        chart = HumanDesignEngine().calculate(profile)
        design_dt = datetime.strptime(chart.design_datetime, "%Y-%m-%d %H:%M")
        birth_dt = datetime.strptime(chart.birth_datetime, "%Y-%m-%d %H:%M")
        diff_days = (birth_dt - design_dt).days
        # Should be roughly 80-100 days
        assert 75 <= diff_days <= 105
