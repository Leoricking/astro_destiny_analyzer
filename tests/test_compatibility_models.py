"""
Tests for compatibility.models — V1.7.0
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import date, time

from compatibility.models import (
    RelationshipType, CompatibilityInput, ScoreBreakdown,
    CompatibilityReport, AstrologyCompatibility, BaziCompatibility,
    ZiWeiCompatibility, NumerologyCompatibility, BloodTypeCompatibility,
    CompatibilitySynthesis, relationship_label,
)
from core.models import BirthProfile, BloodType, ReportLength, ReportLanguage, AnalysisTheme


def _make_profile(name="A", birth_date=date(1990, 1, 1)) -> BirthProfile:
    return BirthProfile(
        name=name,
        birth_date=birth_date,
        birth_city="台北",
        birth_country="台灣",
    )


# ── RelationshipType ──────────────────────────────────────────────────────────

class TestRelationshipType:
    def test_all_values_exist(self):
        for rt in RelationshipType:
            assert rt.value

    def test_romantic_value(self):
        assert RelationshipType.ROMANTIC.value == "romantic"

    def test_business_value(self):
        assert RelationshipType.BUSINESS.value == "business"

    def test_relationship_label_romantic(self):
        assert "情侶" in relationship_label(RelationshipType.ROMANTIC)

    def test_relationship_label_business(self):
        assert "合作" in relationship_label(RelationshipType.BUSINESS)


# ── CompatibilityInput ────────────────────────────────────────────────────────

class TestCompatibilityInput:
    def test_can_create(self):
        ci = CompatibilityInput(
            person_a=_make_profile("A"),
            person_b=_make_profile("B"),
        )
        assert ci.person_a.name == "A"
        assert ci.person_b.name == "B"

    def test_default_relationship_type(self):
        ci = CompatibilityInput(
            person_a=_make_profile("A"),
            person_b=_make_profile("B"),
        )
        assert ci.relationship_type == RelationshipType.GENERAL

    def test_default_report_length(self):
        ci = CompatibilityInput(
            person_a=_make_profile("A"),
            person_b=_make_profile("B"),
        )
        assert ci.report_length == ReportLength.STANDARD

    def test_set_relationship_type(self):
        ci = CompatibilityInput(
            person_a=_make_profile("A"),
            person_b=_make_profile("B"),
            relationship_type=RelationshipType.ROMANTIC,
        )
        assert ci.relationship_type == RelationshipType.ROMANTIC

    def test_focus_themes_default_empty(self):
        ci = CompatibilityInput(
            person_a=_make_profile("A"),
            person_b=_make_profile("B"),
        )
        assert ci.focus_themes == []


# ── ScoreBreakdown ────────────────────────────────────────────────────────────

class TestScoreBreakdown:
    def test_default_values_in_range(self):
        sc = ScoreBreakdown()
        for field in ["emotional_score", "communication_score", "attraction_score",
                      "stability_score", "growth_score", "conflict_score",
                      "collaboration_score", "overall_score"]:
            val = getattr(sc, field)
            assert 0 <= val <= 100, f"{field} out of range: {val}"

    def test_score_label_high(self):
        sc = ScoreBreakdown(overall_score=90)
        assert "高共鳴" in sc.score_label()

    def test_score_label_mid(self):
        sc = ScoreBreakdown(overall_score=72)
        assert "互補" in sc.score_label()

    def test_score_label_low(self):
        sc = ScoreBreakdown(overall_score=35)
        assert "成熟" in sc.score_label()

    def test_all_scores_int(self):
        sc = ScoreBreakdown(
            emotional_score=70, communication_score=65, attraction_score=80,
            stability_score=75, growth_score=60, conflict_score=50,
            collaboration_score=70, overall_score=72,
        )
        assert sc.overall_score == 72


# ── CompatibilityReport ───────────────────────────────────────────────────────

class TestCompatibilityReport:
    def _make_report(self) -> CompatibilityReport:
        return CompatibilityReport(
            person_a_profile=_make_profile("A"),
            person_b_profile=_make_profile("B"),
        )

    def test_can_create(self):
        r = self._make_report()
        assert r.person_a_profile.name == "A"
        assert r.person_b_profile.name == "B"

    def test_has_score_breakdown(self):
        r = self._make_report()
        assert isinstance(r.score_breakdown, ScoreBreakdown)

    def test_has_astrology(self):
        r = self._make_report()
        assert isinstance(r.astrology, AstrologyCompatibility)

    def test_has_bazi(self):
        r = self._make_report()
        assert isinstance(r.bazi, BaziCompatibility)

    def test_has_ziwei(self):
        r = self._make_report()
        assert isinstance(r.ziwei, ZiWeiCompatibility)

    def test_has_numerology(self):
        r = self._make_report()
        assert isinstance(r.numerology, NumerologyCompatibility)

    def test_has_blood_type(self):
        r = self._make_report()
        assert isinstance(r.blood_type, BloodTypeCompatibility)

    def test_has_synthesis(self):
        r = self._make_report()
        assert isinstance(r.synthesis, CompatibilitySynthesis)

    def test_markdown_body_default_empty(self):
        r = self._make_report()
        assert isinstance(r.markdown_body, str)

    def test_created_at_default_empty(self):
        r = self._make_report()
        assert isinstance(r.created_at, str)

    def test_relationship_type_default(self):
        r = self._make_report()
        assert r.relationship_type == RelationshipType.GENERAL
