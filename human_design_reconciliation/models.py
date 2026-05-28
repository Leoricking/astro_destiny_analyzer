"""
Astro Destiny Analyzer — Human Design Reconciliation Models (V1.9.2)

Pydantic models for external chart input and reconciliation reports.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional


class ExternalHDPlanetActivation(BaseModel):
    """A single planet activation from an external Human Design source."""
    planet: str = ""
    side: str = ""          # "conscious" | "design"
    gate: Optional[int] = None
    line: Optional[int] = None
    longitude: Optional[float] = None
    raw_text: str = ""


class ExternalHumanDesignChart(BaseModel):
    """External Human Design chart data for reconciliation comparison."""
    source_name: str = "manual_external"
    source_url: Optional[str] = None
    chart_owner_label: str = ""

    # Core type / strategy / authority
    type_name: Optional[str] = None
    type_name_zh: Optional[str] = None
    strategy: Optional[str] = None
    authority: Optional[str] = None
    profile: Optional[str] = None
    incarnation_cross: Optional[str] = None

    # Planet activations
    conscious_activations: List[ExternalHDPlanetActivation] = Field(default_factory=list)
    design_activations: List[ExternalHDPlanetActivation] = Field(default_factory=list)

    # Gates / channels / centers
    activated_gates: List[int] = Field(default_factory=list)
    defined_channels: List[str] = Field(default_factory=list)
    defined_centers: List[str] = Field(default_factory=list)
    open_centers: List[str] = Field(default_factory=list)

    raw_notes: str = ""


class HDReconciliationItem(BaseModel):
    """A single compared field between local and external HD charts."""
    category: str = ""
    # category options: type | strategy | authority | profile | incarnation_cross |
    #   conscious_planets | design_planets | gates | channels | centers | validation

    field: str = ""
    local_value: str = ""
    external_value: str = ""

    status: str = "not_comparable"
    # status options: match | mismatch | missing_external | missing_local |
    #   likely_method_difference | not_comparable

    severity: str = "info"
    # severity options: info | low | medium | high

    explanation: str = ""
    suggestion: str = ""


class HDReconciliationReport(BaseModel):
    """Full reconciliation report comparing local vs external HD chart."""
    overall_status: str = "insufficient_external_data"
    # options: mostly_match | minor_difference | major_difference | insufficient_external_data

    match_count: int = 0
    mismatch_count: int = 0
    method_difference_count: int = 0
    missing_count: int = 0

    items: List[HDReconciliationItem] = Field(default_factory=list)

    summary: str = ""
    next_actions: List[str] = Field(default_factory=list)

    local_accuracy_note: str = ""
    external_source_note: str = ""
    method_info_note: str = ""


# ── Display helpers ────────────────────────────────────────────────────────────

STATUS_ZH = {
    "match": "✅ 一致",
    "mismatch": "❌ 不一致",
    "missing_external": "⬜ 外部未提供",
    "missing_local": "⬜ 本機未計算",
    "likely_method_difference": "🏫 方法差異",
    "not_comparable": "─ 不可比對",
}

SEVERITY_ZH = {
    "info": "資訊",
    "low": "低",
    "medium": "中",
    "high": "高",
}

OVERALL_STATUS_ZH = {
    "mostly_match": "✅ 大致一致",
    "minor_difference": "⚠️ 輕微差異",
    "major_difference": "❌ 重大差異",
    "insufficient_external_data": "⬜ 外部資料不足",
}
