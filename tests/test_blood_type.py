"""Tests for BloodTypeEngine — static analysis."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from engines.blood_type import BloodTypeEngine
from core.models import BloodType, BloodTypeAnalysis


@pytest.fixture
def engine():
    return BloodTypeEngine()


class TestBloodTypeEngine:
    @pytest.mark.parametrize("bt", [BloodType.A, BloodType.B, BloodType.O,
                                     BloodType.AB, BloodType.UNKNOWN])
    def test_returns_analysis_for_all_types(self, engine, bt):
        result = engine.analyze(bt)
        assert isinstance(result, BloodTypeAnalysis)
        assert result.blood_type == bt

    @pytest.mark.parametrize("bt", [BloodType.A, BloodType.B, BloodType.O, BloodType.AB])
    def test_all_fields_non_empty(self, engine, bt):
        result = engine.analyze(bt)
        assert len(result.interpersonal_style) > 20
        assert len(result.love_response) > 20
        assert len(result.stress_response) > 20
        assert len(result.workplace_cooperation) > 20
        assert len(result.money_attitude) > 20

    def test_unknown_returns_placeholder(self, engine):
        result = engine.analyze(BloodType.UNKNOWN)
        assert "未知" in result.interpersonal_style

    def test_deterministic(self, engine):
        r1 = engine.analyze(BloodType.A)
        r2 = engine.analyze(BloodType.A)
        assert r1.interpersonal_style == r2.interpersonal_style

    def test_different_types_differ(self, engine):
        ra = engine.analyze(BloodType.A)
        rb = engine.analyze(BloodType.B)
        assert ra.interpersonal_style != rb.interpersonal_style

    def test_integration_notes_for_known(self, engine):
        result = engine.analyze(BloodType.O)
        assert len(result.integration_notes) > 0

    def test_integration_notes_empty_for_unknown(self, engine):
        result = engine.analyze(BloodType.UNKNOWN)
        assert result.integration_notes == ""
