"""
Astro Destiny Analyzer — Human Design Validation Module (V1.9.3)

Manages accuracy notes, calibration status, and external validation guidance
for the Human Design MVP calculation pipeline.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional


class HDValidationStatus(BaseModel):
    gate_table_status: str = ""
    channel_table_status: str = ""
    center_mapping_status: str = ""
    design_time_method: str = ""
    ephemeris_status: str = ""
    validation_level: str = "phase1_internal"
    warnings: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
    # V1.9.3 calibration fields
    design_date_method: str = "solar_arc_88"
    gate_wheel_offset_degrees: float = 0.0
    solar_arc_error_degrees: Optional[float] = None


def build_validation_status(chart) -> HDValidationStatus:
    """
    Build a HDValidationStatus from a HumanDesignChart.
    chart: HumanDesignChart instance (typed as Any to avoid circular import)
    """
    calc_mode = getattr(chart, "calculation_mode", "mock_fallback")
    design_date_method = getattr(chart, "design_date_method", "solar_arc_88")
    wheel_offset = getattr(chart, "gate_wheel_offset_degrees", 0.0)
    solar_arc_error = getattr(chart, "design_solar_arc_error_degrees", None)
    fallback_used = getattr(chart, "design_date_fallback_used", False)

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

    if design_date_method == "solar_arc_88" and not fallback_used:
        design_method_str = "exact 88° solar arc retrogression (Sun longitude search)"
        if solar_arc_error is not None:
            design_method_str += f" — error {solar_arc_error:.4f}°"
    elif fallback_used or "fallback" in design_date_method:
        design_method_str = (
            "birth time − 88 days (fallback: solar arc unavailable or failed). "
            "Precise calculation uses exact 88° solar arc retrogression."
        )
    else:
        design_method_str = (
            "birth time − 88 days (minus_88_days mode). "
            "Set HUMAN_DESIGN_DESIGN_DATE_METHOD=solar_arc_88 for exact calculation."
        )

    warnings = [
        "Human Design requires precise birth time for accurate Type, Authority, and Centers.",
        "Gate wheel (I-Ching order) should be externally validated against a reference source.",
    ]

    if fallback_used or design_date_method not in ("solar_arc_88",):
        warnings.append(
            "Design date uses approximation (not exact solar arc). "
            "Design-side gates and profile line 2 may be inaccurate."
        )
    else:
        warnings.append(
            "Design date calculated via exact 88° solar arc. "
            "Gate wheel and timezone settings still require external validation."
        )

    if wheel_offset != 0.0:
        warnings.append(
            f"Gate wheel offset {wheel_offset:+.3f}° is active. "
            "Results will differ from Phase 1 default (offset = 0°)."
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
        design_time_method=design_method_str,
        ephemeris_status=eph_status,
        validation_level="phase1_internal",
        warnings=warnings,
        notes=[
            "This module is for self-reflection and decision-pattern exploration only.",
            "Results do not constitute medical, legal, financial, or life-path advice.",
            "For professional-grade Human Design charts, cross-reference with Jovian Archive, "
            "Genetic Matrix, or MyBodyGraph (comparison only — this system does not claim equivalence).",
        ],
        design_date_method=design_date_method,
        gate_wheel_offset_degrees=wheel_offset,
        solar_arc_error_degrees=solar_arc_error,
    )


def render_validation_markdown(status: HDValidationStatus) -> str:
    """Render validation status as a Markdown section."""
    lines = [
        "## 人類圖準確度與外部校準說明",
        "",
        "> 本節說明 V1.9.3 人類圖計算的精準度現況與後續校準建議。",
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
        "### 方法資訊",
        "",
        f"- **Design Date 計算方式**：{status.design_date_method}",
        f"- **Gate Wheel Offset**：{status.gate_wheel_offset_degrees:+.3f}°",
    ]
    if status.solar_arc_error_degrees is not None:
        lines.append(f"- **Solar Arc 誤差**：{status.solar_arc_error_degrees:.4f}°")
    lines += [
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
