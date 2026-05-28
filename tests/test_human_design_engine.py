"""
Tests for V1.9.0 Human Design Engine.
"""
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import date, time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _rossi_profile():
    from core.models import (
        BirthProfile, BloodType, AnalysisTheme, Gender,
        ReportLanguage, ReportLength,
    )
    return BirthProfile(
        name="Rossi",
        birth_date=date(1989, 9, 21),
        birth_time=time(11, 5),
        birth_city="新竹",
        birth_country="台灣",
        blood_type=BloodType.A,
        themes=list(AnalysisTheme),
        report_language=ReportLanguage.TRADITIONAL_CHINESE,
        report_length=ReportLength.STANDARD,
        birth_latitude=24.8138,
        birth_longitude=120.9675,
        birth_timezone_offset=8.0,
        birth_time_is_known=True,
    )


def _unknown_time_profile():
    from core.models import (
        BirthProfile, BloodType, AnalysisTheme,
        ReportLanguage, ReportLength,
    )
    return BirthProfile(
        name="Unknown Time",
        birth_date=date(1990, 1, 1),
        birth_time=None,
        birth_city="台北",
        birth_country="台灣",
        themes=list(AnalysisTheme),
        report_language=ReportLanguage.TRADITIONAL_CHINESE,
        report_length=ReportLength.SHORT,
        birth_time_is_known=False,
    )


# ── A. Engine instantiation ───────────────────────────────────────────────────

class TestEngineInstantiation:
    def test_engine_importable(self):
        from human_design.engine import HumanDesignEngine
        assert HumanDesignEngine is not None

    def test_engine_createable(self):
        from human_design.engine import HumanDesignEngine
        engine = HumanDesignEngine()
        assert engine is not None

    def test_engine_has_calculate(self):
        from human_design.engine import HumanDesignEngine
        assert callable(getattr(HumanDesignEngine, "calculate", None))


# ── B. Rossi chart calculation ────────────────────────────────────────────────

class TestRossiChart:
    @pytest.fixture(scope="class")
    def chart(self):
        from human_design.engine import HumanDesignEngine
        return HumanDesignEngine().calculate(_rossi_profile())

    def test_type_name_not_empty(self, chart):
        assert chart.type_name != ""
        assert chart.type_name in [
            "Generator", "Manifesting Generator", "Manifestor",
            "Projector", "Reflector", "Unknown",
        ]

    def test_type_name_zh_not_empty(self, chart):
        assert chart.type_name_zh != ""

    def test_strategy_not_empty(self, chart):
        assert chart.strategy != ""
        assert chart.strategy != "─"

    def test_authority_not_empty(self, chart):
        assert chart.authority != ""
        assert chart.authority != "─"

    def test_profile_format(self, chart):
        assert re.match(r"^\d/\d$", chart.profile), f"Invalid profile format: {chart.profile}"

    def test_conscious_activations_not_empty(self, chart):
        assert len(chart.conscious_activations) > 0

    def test_design_activations_not_empty(self, chart):
        assert len(chart.design_activations) > 0

    def test_activated_gates_not_empty(self, chart):
        assert len(chart.activated_gates) > 0

    def test_centers_count_is_9(self, chart):
        assert len(chart.centers) == 9

    def test_defined_plus_open_equals_9(self, chart):
        assert len(chart.defined_centers) + len(chart.open_centers) == 9

    def test_defined_centers_are_valid(self, chart):
        valid = {"Head", "Ajna", "Throat", "G", "Heart", "Sacral", "Spleen", "Solar Plexus", "Root"}
        for c in chart.defined_centers:
            assert c in valid

    def test_calculation_mode_valid(self, chart):
        valid_modes = {"swiss_ephemeris_phase1", "mock_fallback", "partial"}
        assert chart.calculation_mode in valid_modes

    def test_incarnation_cross_not_empty(self, chart):
        assert chart.incarnation_cross != ""

    def test_design_datetime_set(self, chart):
        assert chart.design_datetime is not None

    def test_birth_datetime_set(self, chart):
        assert chart.birth_datetime is not None


# ── C. Unknown birth time ─────────────────────────────────────────────────────

class TestUnknownBirthTime:
    @pytest.fixture(scope="class")
    def chart(self):
        from human_design.engine import HumanDesignEngine
        return HumanDesignEngine().calculate(_unknown_time_profile())

    def test_does_not_crash(self, chart):
        assert chart is not None

    def test_calculation_mode_partial_or_fallback(self, chart):
        assert chart.calculation_mode in {"partial", "mock_fallback"}

    def test_centers_count_9(self, chart):
        assert len(chart.centers) == 9

    def test_accuracy_note_mentions_time(self, chart):
        note = chart.accuracy_note.lower()
        assert "時間" in note or "time" in note.lower()


# ── D. SwissEph missing fallback ──────────────────────────────────────────────

class TestSwissEphFallback:
    def test_mock_activations_stable(self):
        from human_design.engine import _mock_activations
        result = _mock_activations(date(1989, 9, 21), "conscious")
        assert len(result) == 13  # 13 HD planets

    def test_mock_gates_valid_range(self):
        from human_design.engine import _mock_activations
        acts = _mock_activations(date(1989, 9, 21), "design")
        for a in acts:
            assert 1 <= a.gate <= 64
            assert 1 <= a.line <= 6

    def test_fallback_returns_chart(self):
        from human_design.engine import HumanDesignEngine
        engine = HumanDesignEngine()
        chart = engine._fallback(_rossi_profile(), "test error")
        assert chart is not None
        assert len(chart.centers) == 9
        assert chart.calculation_mode == "mock_fallback"
