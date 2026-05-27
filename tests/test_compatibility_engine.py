"""
Tests for compatibility.engine — V1.7.0
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from demo.sample_profiles import SAMPLE_COUPLES
from compatibility.models import CompatibilityInput, RelationshipType
from compatibility.engine import CompatibilityEngine


def _make_input(couple_index: int) -> CompatibilityInput:
    couple = SAMPLE_COUPLES[couple_index]
    return CompatibilityInput(
        person_a=couple["person_a"],
        person_b=couple["person_b"],
        relationship_type=RelationshipType(couple["relationship_type"]),
    )


# ── Basic generation ──────────────────────────────────────────────────────────

class TestEngineGenerate:
    def setup_method(self):
        self.engine = CompatibilityEngine()

    def test_romantic_couple_generates(self):
        ci = _make_input(0)
        report = self.engine.generate(ci)
        assert report is not None

    def test_business_partners_generates(self):
        ci = _make_input(1)
        report = self.engine.generate(ci)
        assert report is not None

    def test_missing_birth_time_no_crash(self):
        from datetime import date
        from core.models import BirthProfile
        p_no_time = BirthProfile(
            name="無時間者",
            birth_date=date(1990, 5, 5),
            birth_time=None,
            birth_city="台北",
            birth_country="台灣",
            birth_time_is_known=False,
        )
        p_normal = SAMPLE_COUPLES[0]["person_a"]
        ci = CompatibilityInput(person_a=p_no_time, person_b=p_normal)
        report = self.engine.generate(ci)
        assert report is not None

    def test_person_a_chart_summary_exists(self):
        ci = _make_input(0)
        report = self.engine.generate(ci)
        assert isinstance(report.person_a_chart_summary, dict)
        assert "sun" in report.person_a_chart_summary

    def test_person_b_chart_summary_exists(self):
        ci = _make_input(0)
        report = self.engine.generate(ci)
        assert isinstance(report.person_b_chart_summary, dict)
        assert "sun" in report.person_b_chart_summary

    def test_score_deterministic(self):
        ci = _make_input(0)
        r1 = self.engine.generate(ci)
        r2 = self.engine.generate(ci)
        assert r1.score_breakdown.overall_score == r2.score_breakdown.overall_score

    def test_overall_score_in_range(self):
        ci = _make_input(0)
        report = self.engine.generate(ci)
        assert 0 <= report.score_breakdown.overall_score <= 100

    def test_conflict_score_in_range(self):
        ci = _make_input(0)
        report = self.engine.generate(ci)
        assert 0 <= report.score_breakdown.conflict_score <= 100

    def test_all_scores_in_range(self):
        ci = _make_input(0)
        report = self.engine.generate(ci)
        sc = report.score_breakdown
        for field in ["emotional_score", "communication_score", "attraction_score",
                      "stability_score", "growth_score", "conflict_score",
                      "collaboration_score", "overall_score"]:
            val = getattr(sc, field)
            assert 0 <= val <= 100, f"{field}={val} out of range"

    def test_synthesis_strengths_not_empty(self):
        ci = _make_input(0)
        report = self.engine.generate(ci)
        assert len(report.synthesis.strengths) > 0

    def test_synthesis_challenges_not_empty(self):
        ci = _make_input(0)
        report = self.engine.generate(ci)
        assert len(report.synthesis.challenges) > 0

    def test_markdown_body_contains_name_a(self):
        ci = _make_input(0)
        report = self.engine.generate(ci)
        assert ci.person_a.name in report.markdown_body

    def test_markdown_body_contains_name_b(self):
        ci = _make_input(0)
        report = self.engine.generate(ci)
        assert ci.person_b.name in report.markdown_body


# ── Astrology compatibility ───────────────────────────────────────────────────

class TestAstrologyCompat:
    def setup_method(self):
        self.engine = CompatibilityEngine()
        self.report = self.engine.generate(_make_input(0))

    def test_sun_pair_not_empty(self):
        assert self.report.astrology.sun_pair != ""

    def test_moon_pair_not_empty(self):
        assert self.report.astrology.moon_pair != ""

    def test_interpretation_not_empty(self):
        assert self.report.astrology.interpretation != ""

    def test_accuracy_note_exists(self):
        assert self.report.astrology.accuracy_note is not None


# ── BaZi compatibility ────────────────────────────────────────────────────────

class TestBaziCompat:
    def setup_method(self):
        self.engine = CompatibilityEngine()
        self.report = self.engine.generate(_make_input(0))

    def test_day_master_relation_not_empty(self):
        assert self.report.bazi.day_master_relation != ""

    def test_five_element_balance_not_empty(self):
        assert self.report.bazi.five_element_balance != ""

    def test_interpretation_not_empty(self):
        assert self.report.bazi.interpretation != ""


# ── ZiWei compatibility ───────────────────────────────────────────────────────

class TestZiWeiCompat:
    def setup_method(self):
        self.engine = CompatibilityEngine()

    def test_key_palace_interactions_not_empty(self):
        report = self.engine.generate(_make_input(0))
        assert len(report.ziwei.key_palace_interactions) > 0

    def test_interpretation_not_empty(self):
        report = self.engine.generate(_make_input(0))
        assert report.ziwei.interpretation != ""

    def test_no_crash_with_mock_fallback(self):
        from datetime import date
        from core.models import BirthProfile
        p_a = BirthProfile(
            name="模擬A",
            birth_date=date(1980, 1, 1),
            birth_city="台北",
            birth_country="台灣",
        )
        p_b = BirthProfile(
            name="模擬B",
            birth_date=date(1982, 6, 15),
            birth_city="台中",
            birth_country="台灣",
        )
        ci = CompatibilityInput(person_a=p_a, person_b=p_b)
        report = self.engine.generate(ci)
        assert report.ziwei.interpretation != ""


# ── Numerology / Blood compatibility ─────────────────────────────────────────

class TestNumerologyBloodCompat:
    def setup_method(self):
        self.engine = CompatibilityEngine()
        self.report = self.engine.generate(_make_input(0))

    def test_numerology_interpretation_not_empty(self):
        assert self.report.numerology.interpretation != ""

    def test_blood_unknown_no_crash(self):
        from datetime import date
        from core.models import BirthProfile, BloodType
        p_a = BirthProfile(
            name="UnknownBloodA",
            birth_date=date(1990, 3, 3),
            birth_city="台北",
            birth_country="台灣",
            blood_type=BloodType.UNKNOWN,
        )
        p_b = BirthProfile(
            name="UnknownBloodB",
            birth_date=date(1992, 7, 7),
            birth_city="台中",
            birth_country="台灣",
            blood_type=BloodType.UNKNOWN,
        )
        ci = CompatibilityInput(person_a=p_a, person_b=p_b)
        report = self.engine.generate(ci)
        assert report.blood_type.blood_pair != ""
