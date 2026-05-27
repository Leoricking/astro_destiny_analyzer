"""
Data models for Zi Wei External Chart Reconciliation (V1.7.3).
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ── Status / severity enums (kept as plain str for JSON-friendliness) ─────────

VALID_STATUSES = {
    "match",
    "mismatch",
    "missing_local",
    "missing_external",
    "not_implemented",
    "likely_school_difference",
}

VALID_SEVERITIES = {"info", "low", "medium", "high"}

VALID_OVERALL_STATUSES = {
    "mostly_match",
    "partial_match",
    "major_difference",
    "insufficient_data",
}

# ── Chinese display mappings ───────────────────────────────────────────────────

STATUS_ZH: Dict[str, str] = {
    "match": "一致",
    "mismatch": "不一致",
    "missing_local": "本機缺少",
    "missing_external": "外部缺少",
    "not_implemented": "尚未實作",
    "likely_school_difference": "可能流派差異",
}

SEVERITY_ZH: Dict[str, str] = {
    "info": "資訊",
    "low": "低",
    "medium": "中",
    "high": "高",
}

OVERALL_STATUS_ZH: Dict[str, str] = {
    "mostly_match": "大致一致",
    "partial_match": "部分一致",
    "major_difference": "主要差異",
    "insufficient_data": "資料不足",
}


# ── External chart data models ─────────────────────────────────────────────────

class ExternalZiWeiPalace(BaseModel):
    """One palace's data as manually entered from an external source."""
    palace_name: str
    branch: str = ""
    main_stars: List[str] = Field(default_factory=list)
    auxiliary_stars: List[str] = Field(default_factory=list)
    malefic_stars: List[str] = Field(default_factory=list)
    transformations: Dict[str, str] = Field(default_factory=dict)
    da_xian_range: Optional[str] = None
    xiao_xian_ages: List[int] = Field(default_factory=list)
    brightness: Dict[str, str] = Field(default_factory=dict)
    raw_text: str = ""


class ExternalZiWeiChart(BaseModel):
    """
    Manually-entered external Zi Wei chart for comparison.
    Fill only what is available; leave unknowns as None / empty.
    """
    source_name: str = "manual_external"
    birth_solar_date: Optional[str] = None
    birth_lunar_date: Optional[str] = None
    birth_time_label: Optional[str] = None
    gender_label: Optional[str] = None
    five_element_bureau: Optional[str] = None
    ming_palace_branch: Optional[str] = None
    shen_palace_branch: Optional[str] = None
    ming_zhu: Optional[str] = None       # 命主
    shen_zhu: Optional[str] = None       # 身主
    sihua: Dict[str, str] = Field(default_factory=dict)   # star → 化祿/化權/化科/化忌
    palaces: List[ExternalZiWeiPalace] = Field(default_factory=list)
    luck_score: Optional[int] = None     # external site score, not standard
    raw_note: str = ""


# ── Reconciliation result models ───────────────────────────────────────────────

class ReconciliationItem(BaseModel):
    """Single comparison item between local and external chart."""
    category: str          # basic / main_stars / transformations / auxiliary / malefic / da_xian / score
    field_name: str
    local_value: str
    external_value: str
    status: str            # match | mismatch | missing_local | missing_external | not_implemented | likely_school_difference
    severity: str          # info | low | medium | high
    explanation: str = ""

    @property
    def status_zh(self) -> str:
        return STATUS_ZH.get(self.status, self.status)

    @property
    def severity_zh(self) -> str:
        return SEVERITY_ZH.get(self.severity, self.severity)


class ZiWeiReconciliationReport(BaseModel):
    """Full reconciliation report between local and external Zi Wei charts."""
    created_at: str
    source_name: str
    overall_status: str    # mostly_match | partial_match | major_difference | insufficient_data
    match_count: int = 0
    mismatch_count: int = 0
    not_implemented_count: int = 0
    school_difference_count: int = 0
    items: List[ReconciliationItem] = Field(default_factory=list)
    summary: str = ""
    recommendation: str = ""
    markdown_body: str = ""

    @property
    def overall_status_zh(self) -> str:
        return OVERALL_STATUS_ZH.get(self.overall_status, self.overall_status)
