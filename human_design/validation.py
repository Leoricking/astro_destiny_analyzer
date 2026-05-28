"""
Astro Destiny Analyzer — Human Design Validation Module (V1.9.1)

Manages accuracy notes, calibration status, and external validation guidance
for the Human Design MVP calculation pipeline.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List


class HDValidationStatus(BaseModel):
    gate_table_status: str = ""
    channel_table_status: str = ""
    center_mapping_status: str = ""
    design_time_method: str = ""
    ephemeris_status: str = ""
    validation_level: str = "phase1_internal"
    warnings: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


def build_validation_status(chart) -> HDValidationStatus:
    """
    Build a HDValidationStatus from a HumanDesignChart.
    chart: HumanDesignChart instance (typed as Any to avoid circular import)
    """
    calc_mode = getattr(chart, "calculation_mode", "mock_fallback")

    if calc_mode == "swiss_ephemeris_phase1":
        eph_status = "Swiss Ephemeris available — planet longitudes calculated from real ephemeris data."
    elif calc_mode == "partial":
        eph_status = (
            "Partial calculation — birth time unknown, noon (12:00) used as approximation. "
            "Planet positions may be slightly inaccurate; Moon especially."
        )
    else:
        eph_status = (
            "Swiss Ephemeris unavailable — mock fallback used. "
            "Results are deterministic placeholders, not real planetary data."
        )

    return HDValidationStatus(
        gate_table_status=(
            "Phase 1 I-Ching wheel table; verify against external Human Design source "
            "before commercial use."
        ),
        channel_table_status=(
            "36-channel table loaded; names may use safe generic labels when official "
            "naming is uncertain."
        ),
        center_mapping_status="Centers are derived from defined channels.",
        design_time_method=(
            "Design side uses birth time minus 88 days MVP approximation. "
            "Precise calculation uses exact 88° solar arc retrogression; future versions may refine."
        ),
        ephemeris_status=eph_status,
        validation_level="phase1_internal",
        warnings=[
            "Human Design requires precise birth time for accurate Type, Authority, and Centers.",
            "Gate wheel (I-Ching order) should be externally validated against a reference source.",
            "Design date uses MVP 88-day approximation, not exact solar arc calculation.",
        ],
        notes=[
            "This module is for self-reflection and decision-pattern exploration only.",
            "Results do not constitute medical, legal, financial, or life-path advice.",
            "For professional-grade Human Design charts, cross-reference with Jovian Archive, "
            "Genetic Matrix, or MyBodyGraph (comparison only — this system does not claim equivalence).",
        ],
    )


def render_validation_markdown(status: HDValidationStatus) -> str:
    """Render validation status as a Markdown section."""
    lines = [
        "## 人類圖準確度與外部校準說明",
        "",
        "> 本節說明 V1.9.1 人類圖計算的精準度現況與後續校準建議。",
        "",
        "### 星曆來源（Ephemeris）",
        "",
        status.ephemeris_status,
        "",
        "### Gate Table 狀態",
        "",
        status.gate_table_status,
        "",
        "### Channel Table 狀態",
        "",
        status.channel_table_status,
        "",
        "### Design Date 方法",
        "",
        status.design_time_method,
        "",
        "### 中心定義方式",
        "",
        status.center_mapping_status,
        "",
        "### 限制與注意事項",
        "",
    ]
    for w in status.warnings:
        lines.append(f"- ⚠️ {w}")
    lines.append("")
    lines.append("### 後續校準建議")
    lines.append("")
    for n in status.notes:
        lines.append(f"- {n}")
    lines.append("")
    lines.append(
        f"**驗證等級**：{status.validation_level} — "
        "Phase 1 為內部參考級，適合自我探索與功能展示。"
        "正式商業交付建議進行外部校準。"
    )
    return "\n".join(lines)
