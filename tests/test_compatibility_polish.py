"""
Tests for V1.7.1 Compatibility Report Polish & Demo Couples.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from demo.sample_profiles import SAMPLE_COUPLES
from compatibility.models import (
    CompatibilityInput, RelationshipType, ScoreBreakdown,
)
from compatibility.engine import CompatibilityEngine
from compatibility.templates import _build_relationship_type_advice
from compatibility.exporters import make_compat_filename, export_compat_to_html


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_report(couple_index: int = 0):
    couple = SAMPLE_COUPLES[couple_index]
    ci = CompatibilityInput(
        person_a=couple["person_a"],
        person_b=couple["person_b"],
        relationship_type=RelationshipType(couple["relationship_type"]),
    )
    return CompatibilityEngine().generate(ci)


# ── 1-3: Demo metadata ────────────────────────────────────────────────────────

class TestDemoMetadata:
    def test_romantic_has_label(self):
        c = SAMPLE_COUPLES[0]
        assert "label" in c and c["label"]

    def test_romantic_has_description(self):
        c = SAMPLE_COUPLES[0]
        assert "description" in c and c["description"]

    def test_romantic_has_talking_points(self):
        c = SAMPLE_COUPLES[0]
        assert "talking_points" in c and len(c["talking_points"]) >= 3

    def test_business_has_label(self):
        c = SAMPLE_COUPLES[1]
        assert "label" in c and c["label"]

    def test_business_has_description(self):
        c = SAMPLE_COUPLES[1]
        assert "description" in c and c["description"]

    def test_business_has_talking_points(self):
        c = SAMPLE_COUPLES[1]
        assert "talking_points" in c and len(c["talking_points"]) >= 3


# ── 4-6: Relationship type advice ─────────────────────────────────────────────

class TestRelationshipTypeAdvice:
    def test_romantic_advice_not_empty(self):
        adv = _build_relationship_type_advice("romantic")
        assert adv and adv.get("focus_title")
        assert len(adv.get("priority_questions", [])) > 0

    def test_business_advice_not_empty(self):
        adv = _build_relationship_type_advice("business")
        assert adv and adv.get("focus_title")
        assert len(adv.get("priority_questions", [])) > 0

    def test_parent_child_advice_not_empty(self):
        adv = _build_relationship_type_advice("parent_child")
        assert adv and adv.get("focus_title")
        assert len(adv.get("priority_questions", [])) > 0

    def test_general_advice_returns_dict(self):
        adv = _build_relationship_type_advice("general")
        assert isinstance(adv, dict)


# ── 7-11: Markdown content ────────────────────────────────────────────────────

class TestMarkdownContent:
    def setup_method(self):
        self.report = _make_report(0)
        self.md = self.report.markdown_body

    def test_contains_score_interpretation(self):
        assert "分數不是絕對適合度" in self.md

    def test_contains_conflict_score_note(self):
        assert "衝突分數高" in self.md

    def test_contains_thirty_day_practice_header(self):
        assert "30 天關係練習" in self.md

    def test_contains_week_1(self):
        assert "Week 1" in self.md

    def test_contains_week_2(self):
        assert "Week 2" in self.md

    def test_contains_week_3(self):
        assert "Week 3" in self.md

    def test_contains_week_4(self):
        assert "Week 4" in self.md

    def test_contains_safety_boundary(self):
        assert "安全界線" in self.md or "現實支持" in self.md


# ── 12-13: Dynamic label ──────────────────────────────────────────────────────

class TestDynamicLabel:
    def test_high_conflict_high_growth_is_high_tension(self):
        sc = ScoreBreakdown(
            overall_score=65,
            conflict_score=70,
            growth_score=72,
        )
        label = sc.dynamic_label()
        assert "高張力" in label

    def test_low_conflict_low_growth_avoids_stagnation(self):
        sc = ScoreBreakdown(
            overall_score=70,
            conflict_score=35,
            growth_score=42,
        )
        label = sc.dynamic_label()
        assert "停滯" in label or "舒適" in label

    def test_normal_case_returns_score_label(self):
        sc = ScoreBreakdown(overall_score=75, conflict_score=50, growth_score=65)
        assert sc.dynamic_label() == sc.score_label()


# ── 14-16: Synthesis min counts ───────────────────────────────────────────────

class TestSynthesisMinCounts:
    def setup_method(self):
        self.report = _make_report(0)

    def test_strengths_at_least_3(self):
        assert len(self.report.synthesis.strengths) >= 3

    def test_challenges_at_least_3(self):
        assert len(self.report.synthesis.challenges) >= 3

    def test_practical_advice_at_least_5(self):
        assert len(self.report.synthesis.practical_advice) >= 5

    def test_thirty_day_has_4_weeks(self):
        practice = self.report.synthesis.thirty_day_practice
        assert len(practice) == 4

    def test_thirty_day_has_week_markers(self):
        practice = "\n".join(self.report.synthesis.thirty_day_practice)
        assert "Week 1" in practice
        assert "Week 4" in practice


# ── 17-18: Export ─────────────────────────────────────────────────────────────

class TestExport:
    def setup_method(self):
        self.report = _make_report(0)

    def test_html_contains_relationship_type(self):
        html = export_compat_to_html(self.report)
        from compatibility.models import relationship_label
        rt_label = relationship_label(self.report.relationship_type)
        assert rt_label in html

    def test_filename_no_illegal_chars(self):
        fn = make_compat_filename("小明", "小花", "html", "romantic")
        illegal = set('\\/:*?"<>|')
        assert not any(c in fn for c in illegal)

    def test_filename_with_rel_type_no_illegal_chars(self):
        fn = make_compat_filename("Demo A", "Demo B", "html", "parent_child")
        illegal = set('\\/:*?"<>|')
        assert not any(c in fn for c in illegal)

    def test_filename_without_rel_type_still_works(self):
        fn = make_compat_filename("Alice", "Bob", "md")
        assert fn.endswith(".md")
        assert "Alice" in fn
        assert "Bob" in fn


# ── 19-20: Old tests backward-compat sentinel ─────────────────────────────────

class TestBackwardCompat:
    def test_sample_couples_at_least_two(self):
        assert len(SAMPLE_COUPLES) >= 2

    def test_each_couple_has_required_keys(self):
        for c in SAMPLE_COUPLES:
            assert "label" in c
            assert "person_a" in c
            assert "person_b" in c
            assert "relationship_type" in c

    def test_romantic_relationship_type(self):
        assert SAMPLE_COUPLES[0]["relationship_type"] == "romantic"

    def test_business_relationship_type(self):
        assert SAMPLE_COUPLES[1]["relationship_type"] == "business"

    def test_engine_generates_report(self):
        report = _make_report(0)
        assert report is not None
        assert report.markdown_body

    def test_score_label_works(self):
        sc = ScoreBreakdown(overall_score=80)
        assert sc.score_label()
