"""
Astro Destiny Analyzer — Compatibility Data Models (Pydantic v2)
V1.7.0
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum

from core.models import BirthProfile, ReportLength, ReportLanguage


# ── Relationship Type ─────────────────────────────────────────────────────────

class RelationshipType(str, Enum):
    ROMANTIC     = "romantic"
    MARRIAGE     = "marriage"
    BUSINESS     = "business"
    PARENT_CHILD = "parent_child"
    FRIENDSHIP   = "friendship"
    COLLEAGUE    = "colleague"
    GENERAL      = "general"


_RELATIONSHIP_LABELS: Dict[str, str] = {
    "romantic":     "情侶 / 伴侶",
    "marriage":     "婚姻",
    "business":     "合作夥伴",
    "parent_child": "親子",
    "friendship":   "朋友",
    "colleague":    "同事",
    "general":      "一般關係",
}


def relationship_label(rt: RelationshipType) -> str:
    return _RELATIONSHIP_LABELS.get(rt.value, rt.value)


# ── Input ─────────────────────────────────────────────────────────────────────

class CompatibilityInput(BaseModel):
    person_a: BirthProfile
    person_b: BirthProfile
    relationship_type: RelationshipType = RelationshipType.GENERAL
    focus_themes: List[str] = Field(default_factory=list)
    report_length: ReportLength = ReportLength.STANDARD
    language: ReportLanguage = ReportLanguage.TRADITIONAL_CHINESE


# ── Score ─────────────────────────────────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    emotional_score: int = 50
    communication_score: int = 50
    attraction_score: int = 50
    stability_score: int = 50
    growth_score: int = 50
    conflict_score: int = 50
    collaboration_score: int = 50
    overall_score: int = 50

    def score_label(self) -> str:
        s = self.overall_score
        if s >= 85:
            return "高共鳴"
        if s >= 70:
            return "互補佳"
        if s >= 55:
            return "需要溝通設計"
        if s >= 40:
            return "磨合壓力高"
        return "需要高度成熟與界線"

    def dynamic_label(self) -> str:
        """Context-aware label that factors in conflict + growth patterns."""
        if self.conflict_score >= 65 and self.growth_score >= 65:
            return "高張力高成長"
        if self.conflict_score < 45 and self.growth_score < 50:
            return "舒適但需避免停滯"
        return self.score_label()


# ── Sub-system Compatibility ──────────────────────────────────────────────────

class AstrologyCompatibility(BaseModel):
    sun_pair: str = ""
    moon_pair: str = ""
    venus_mars_pair: str = ""
    mercury_pair: str = ""
    ascendant_pair: str = ""
    key_aspects: List[str] = Field(default_factory=list)
    harmony_factors: List[str] = Field(default_factory=list)
    tension_factors: List[str] = Field(default_factory=list)
    interpretation: str = ""
    accuracy_note: str = ""


class BaziCompatibility(BaseModel):
    person_a_day_master: str = ""
    person_b_day_master: str = ""
    five_element_balance: str = ""
    supportive_elements: List[str] = Field(default_factory=list)
    conflicting_elements: List[str] = Field(default_factory=list)
    day_master_relation: str = ""
    interpretation: str = ""
    accuracy_note: str = ""


class ZiWeiCompatibility(BaseModel):
    person_a_ming_palace: str = ""
    person_b_ming_palace: str = ""
    person_a_shen_palace: str = ""
    person_b_shen_palace: str = ""
    key_palace_interactions: List[str] = Field(default_factory=list)
    main_star_resonance: str = ""
    da_xian_context: str = ""
    interpretation: str = ""
    accuracy_note: str = ""


class NumerologyCompatibility(BaseModel):
    life_path_pair: str = ""
    shared_theme: str = ""
    challenge_theme: str = ""
    interpretation: str = ""


class BloodTypeCompatibility(BaseModel):
    blood_pair: str = ""
    interaction_style: str = ""
    conflict_style: str = ""
    advice: str = ""


# ── Synthesis ─────────────────────────────────────────────────────────────────

class CompatibilitySynthesis(BaseModel):
    relationship_summary: str = ""
    strengths: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    emotional_pattern: str = ""
    communication_pattern: str = ""
    attraction_pattern: str = ""
    conflict_pattern: str = ""
    long_term_potential: str = ""
    practical_advice: List[str] = Field(default_factory=list)
    thirty_day_practice: List[str] = Field(default_factory=list)
    warning_note: str = ""


# ── Full Compatibility Report ─────────────────────────────────────────────────

class CompatibilityReport(BaseModel):
    report_id: Optional[str] = None
    created_at: str = ""
    person_a_profile: BirthProfile
    person_b_profile: BirthProfile
    person_a_chart_summary: Dict = Field(default_factory=dict)
    person_b_chart_summary: Dict = Field(default_factory=dict)
    relationship_type: RelationshipType = RelationshipType.GENERAL
    score_breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    astrology: AstrologyCompatibility = Field(default_factory=AstrologyCompatibility)
    bazi: BaziCompatibility = Field(default_factory=BaziCompatibility)
    ziwei: ZiWeiCompatibility = Field(default_factory=ZiWeiCompatibility)
    numerology: NumerologyCompatibility = Field(default_factory=NumerologyCompatibility)
    blood_type: BloodTypeCompatibility = Field(default_factory=BloodTypeCompatibility)
    synthesis: CompatibilitySynthesis = Field(default_factory=CompatibilitySynthesis)
    markdown_body: str = ""
