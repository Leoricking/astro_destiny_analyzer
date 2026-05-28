"""
Astro Destiny Analyzer — Human Design Reconciliation Engine (V1.9.2)

Compares a local HumanDesignChart against an ExternalHumanDesignChart and
produces a HDReconciliationReport with per-field match/mismatch items.
"""
from __future__ import annotations
import re
from typing import Optional, List, Set

from collections import Counter

from human_design_reconciliation.models import (
    ExternalHumanDesignChart,
    HDReconciliationItem,
    HDReconciliationReport,
    HumanDesignCalibrationCase,
    HumanDesignCalibrationDataset,
    BatchReconciliationSummary,
)


# ── Normalize helpers ─────────────────────────────────────────────────────────

_TYPE_MAP = {
    "manifestor": "Manifestor",
    "顯示者": "Manifestor",
    "generator": "Generator",
    "生產者": "Generator",
    "manifesting generator": "Manifesting Generator",
    "顯示生產者": "Manifesting Generator",
    "projector": "Projector",
    "投射者": "Projector",
    "reflector": "Reflector",
    "反映者": "Reflector",
}

_AUTHORITY_MAP = {
    "emotional": "Emotional",
    "情緒": "Emotional",
    "情緒權威": "Emotional",
    "sacral": "Sacral",
    "薦骨": "Sacral",
    "薦骨權威": "Sacral",
    "splenic": "Splenic",
    "直覺": "Splenic",
    "直覺權威": "Splenic",
    "ego": "Ego",
    "意志": "Ego",
    "意志權威": "Ego",
    "self": "Self",
    "自我投射": "Self",
    "自我投射權威": "Self",
    "environmental": "Environmental",
    "環境": "Environmental",
    "環境權威": "Environmental",
    "lunar": "Lunar",
    "月亮": "Lunar",
    "月亮權威": "Lunar",
}

_CENTER_MAP = {
    "head": "Head",
    "頭頂中心": "Head",
    "ajna": "Ajna",
    "邏輯中心": "Ajna",
    "throat": "Throat",
    "喉嚨中心": "Throat",
    "g": "G",
    "g中心": "G",
    "g center": "G",
    "方向中心": "G",
    "heart": "Heart",
    "will": "Heart",
    "意志中心": "Heart",
    "sacral": "Sacral",
    "薦骨中心": "Sacral",
    "spleen": "Spleen",
    "直覺中心": "Spleen",
    "solar plexus": "Solar Plexus",
    "emotional": "Solar Plexus",
    "情緒中心": "Solar Plexus",
    "root": "Root",
    "根部中心": "Root",
}


def normalize_type(v: Optional[str]) -> str:
    """Normalize a Type value to canonical English form."""
    if not v:
        return ""
    vl = v.strip().lower()
    for k, canon in _TYPE_MAP.items():
        if k.lower() in vl:
            return canon
    return v.strip()


def normalize_authority(v: Optional[str]) -> str:
    """Normalize an Authority value to canonical English form."""
    if not v:
        return ""
    vl = v.strip().lower()
    for k, canon in _AUTHORITY_MAP.items():
        if k.lower() in vl:
            return canon
    return v.strip()


def normalize_profile(v: Optional[str]) -> str:
    """Normalize a Profile string — '4-6', '4｜6' → '4/6'."""
    if not v:
        return ""
    return re.sub(r"[-｜\s]+", "/", v.strip())


def normalize_channel(v: str) -> str:
    """Normalize a channel key — '34-20' and '20-34' both → '20-34'."""
    parts = v.replace(" ", "").split("-")
    if len(parts) == 2:
        try:
            nums = sorted([int(parts[0]), int(parts[1])])
            return f"{nums[0]}-{nums[1]}"
        except ValueError:
            pass
    return v.strip()


def normalize_center(v: str) -> str:
    """Normalize a center name — 'G中心', 'G Center' → 'G', etc."""
    vl = v.strip().lower()
    # Exact match first
    for k, canon in _CENTER_MAP.items():
        if k == vl:
            return canon
    # Substring match
    for k, canon in _CENTER_MAP.items():
        if k in vl:
            return canon
    return v.strip()


def _has_external_data(ext: ExternalHumanDesignChart) -> bool:
    return bool(
        ext.type_name or ext.strategy or ext.authority or ext.profile
        or ext.activated_gates or ext.defined_centers or ext.defined_channels
        or ext.conscious_activations or ext.design_activations
    )


def _find_activation(activations, planet_name: str):
    """Find a planet activation by partial name match (case-insensitive)."""
    pn = planet_name.lower()
    for a in activations:
        if pn in a.planet.lower():
            return a
    return None


# ── Reconciliation Engine ─────────────────────────────────────────────────────

class HumanDesignReconciliationEngine:
    """Compare a local HumanDesignChart against an ExternalHumanDesignChart."""

    def reconcile(
        self,
        local,
        external: ExternalHumanDesignChart,
    ) -> HDReconciliationReport:
        """
        Produce a HDReconciliationReport from local vs external HD chart data.
        local: HumanDesignChart instance (typed as Any to avoid circular import)
        """
        if not _has_external_data(external):
            return HDReconciliationReport(
                overall_status="insufficient_external_data",
                summary=(
                    "外部資料為空，無法進行比對。"
                    "請輸入外部人類圖資料後再進行校準。"
                ),
                next_actions=[
                    "前往 Jovian Archive / Genetic Matrix / MyBodyGraph 取得人類圖資料",
                    "將資料依格式填入外部盤 JSON 模板",
                    "再次點擊「開始校準比對」",
                ],
                external_source_note=external.raw_notes or "尚無外部資料",
            )

        items: List[HDReconciliationItem] = []

        # ── Type ──────────────────────────────────────────────────────────────
        items += self._compare_type(local, external)

        # ── Strategy ──────────────────────────────────────────────────────────
        items += self._compare_strategy(local, external)

        # ── Authority ─────────────────────────────────────────────────────────
        items += self._compare_authority(local, external)

        # ── Profile ───────────────────────────────────────────────────────────
        items += self._compare_profile(local, external)

        # ── Incarnation Cross ─────────────────────────────────────────────────
        items += self._compare_incarnation_cross(local, external)

        # ── Conscious planets ─────────────────────────────────────────────────
        items += self._compare_planets(
            local.conscious_activations, external.conscious_activations, "conscious_planets"
        )

        # ── Design planets ────────────────────────────────────────────────────
        items += self._compare_planets(
            local.design_activations, external.design_activations, "design_planets",
            is_design=True,
            local_design_method=getattr(local, "design_date_method", "unknown"),
        )

        # ── Gates ─────────────────────────────────────────────────────────────
        items += self._compare_gates(local, external)

        # ── Channels ──────────────────────────────────────────────────────────
        items += self._compare_channels(local, external)

        # ── Centers ───────────────────────────────────────────────────────────
        items += self._compare_centers(local, external)

        # ── Derive overall status ──────────────────────────────────────────────
        match_count = sum(1 for i in items if i.status == "match")
        mismatch_count = sum(1 for i in items if i.status == "mismatch")
        method_diff_count = sum(1 for i in items if i.status == "likely_method_difference")
        missing_count = sum(1 for i in items if i.status in ("missing_external", "missing_local"))

        high_mismatches = [i for i in items if i.status == "mismatch" and i.severity == "high"]

        if mismatch_count == 0:
            overall = "mostly_match"
        elif high_mismatches or mismatch_count >= 3:
            overall = "major_difference"
        else:
            overall = "minor_difference"

        if overall == "mostly_match":
            summary = "本機人類圖與外部資料大致一致，無重大差異。"
        elif overall == "major_difference":
            summary = f"發現 {mismatch_count} 個不一致項（其中 {len(high_mismatches)} 個高嚴重度）。建議檢查 Gate Wheel / Design Date / Timezone 設定。"
        else:
            summary = f"發現 {mismatch_count} 個輕微差異，可能來自計算方法或流派差異。"

        next_actions = self._build_next_actions(items)

        # Build method info note
        design_date_method = getattr(local, "design_date_method", "unknown")
        wheel_offset = getattr(local, "gate_wheel_offset_degrees", 0.0)
        solar_arc_error = getattr(local, "design_solar_arc_error_degrees", None)
        method_parts = [f"Design Date Method: {design_date_method}"]
        if wheel_offset != 0.0:
            method_parts.append(f"Gate Wheel Offset: {wheel_offset:+.3f}°")
        if solar_arc_error is not None:
            method_parts.append(f"Solar Arc Error: {solar_arc_error:.4f}°")
        method_info_note = " | ".join(method_parts)

        return HDReconciliationReport(
            overall_status=overall,
            match_count=match_count,
            mismatch_count=mismatch_count,
            method_difference_count=method_diff_count,
            missing_count=missing_count,
            items=items,
            summary=summary,
            next_actions=next_actions,
            local_accuracy_note=getattr(local, "accuracy_note", ""),
            external_source_note=external.source_name,
            method_info_note=method_info_note,
        )

    # ── Private comparison methods ─────────────────────────────────────────────

    def _compare_type(self, local, external: ExternalHumanDesignChart) -> List[HDReconciliationItem]:
        lv = normalize_type(getattr(local, "type_name", ""))
        ev = normalize_type(external.type_name)
        if not ev:
            return [HDReconciliationItem(
                category="type", field="type_name",
                local_value=getattr(local, "type_name", ""),
                external_value="",
                status="missing_external", severity="info",
                explanation="外部資料未提供 Type。",
            )]
        if lv == ev:
            return [HDReconciliationItem(
                category="type", field="type_name",
                local_value=getattr(local, "type_name", ""),
                external_value=external.type_name or "",
                status="match", severity="info",
                explanation="Type 一致。",
            )]
        return [HDReconciliationItem(
            category="type", field="type_name",
            local_value=getattr(local, "type_name", ""),
            external_value=external.type_name or "",
            status="mismatch", severity="high",
            explanation=(
                "Type 不一致。可能原因：defined centers 差異、"
                "motor-to-throat path 判斷差異、channel table 差異。"
            ),
            suggestion=(
                "請比對 defined centers 與 channels，確認 Sacral / Throat 連接路徑。"
                "若 Gate Wheel 或 Design Date 有差異，centers 可能因此不同。"
            ),
        )]

    def _compare_strategy(self, local, external: ExternalHumanDesignChart) -> List[HDReconciliationItem]:
        lv = (getattr(local, "strategy", "") or "").strip()
        ev = (external.strategy or "").strip()
        if not ev:
            return [HDReconciliationItem(
                category="strategy", field="strategy",
                local_value=lv, external_value="",
                status="missing_external", severity="info",
                explanation="外部資料未提供 Strategy。",
            )]
        # Normalize: lowercase, strip spaces for comparison
        if lv.lower().replace(" ", "") == ev.lower().replace(" ", ""):
            return [HDReconciliationItem(
                category="strategy", field="strategy",
                local_value=lv, external_value=ev,
                status="match", severity="info",
                explanation="Strategy 一致。",
            )]
        # Strategy usually follows Type — mismatch likely caused by Type mismatch
        return [HDReconciliationItem(
            category="strategy", field="strategy",
            local_value=lv, external_value=ev,
            status="mismatch", severity="medium",
            explanation="Strategy 不一致。Strategy 由 Type 決定，若 Type 一致則可能為中文翻譯差異。",
            suggestion="確認 Type 是否一致；若 Type 相同，可能是翻譯或策略描述方式不同。",
        )]

    def _compare_authority(self, local, external: ExternalHumanDesignChart) -> List[HDReconciliationItem]:
        lv_raw = getattr(local, "authority", "") or ""
        ev_raw = external.authority or ""
        lv = normalize_authority(lv_raw)
        ev = normalize_authority(ev_raw)
        if not ev_raw.strip():
            return [HDReconciliationItem(
                category="authority", field="authority",
                local_value=lv_raw, external_value="",
                status="missing_external", severity="info",
                explanation="外部資料未提供 Authority。",
            )]
        if lv == ev:
            return [HDReconciliationItem(
                category="authority", field="authority",
                local_value=lv_raw, external_value=ev_raw,
                status="match", severity="info",
                explanation="Authority 一致。",
            )]
        return [HDReconciliationItem(
            category="authority", field="authority",
            local_value=lv_raw, external_value=ev_raw,
            status="mismatch", severity="high",
            explanation=(
                "Authority 不一致。可能原因：Solar Plexus / Sacral / Spleen center definition 差異、"
                "center priority 差異。Authority 由已定義中心決定，中心差異會直接影響 Authority。"
            ),
            suggestion=(
                "比對 defined centers — 若 Solar Plexus / Sacral / Spleen 定義狀態不同，"
                "則 Authority 會不同。進一步檢查 gates / channels。"
            ),
        )]

    def _compare_profile(self, local, external: ExternalHumanDesignChart) -> List[HDReconciliationItem]:
        lv_raw = getattr(local, "profile", "") or ""
        ev_raw = external.profile or ""
        lv = normalize_profile(lv_raw)
        ev = normalize_profile(ev_raw)
        if not ev_raw.strip():
            return [HDReconciliationItem(
                category="profile", field="profile",
                local_value=lv_raw, external_value="",
                status="missing_external", severity="info",
                explanation="外部資料未提供 Profile。",
            )]
        if lv == ev:
            return [HDReconciliationItem(
                category="profile", field="profile",
                local_value=lv_raw, external_value=ev_raw,
                status="match", severity="info",
                explanation="Profile 一致。",
            )]
        return [HDReconciliationItem(
            category="profile", field="profile",
            local_value=lv_raw, external_value=ev_raw,
            status="mismatch", severity="high",
            explanation=(
                "Profile 不一致。可能原因：Conscious Sun line 或 Design Sun line 差異、"
                "gate / line boundary 問題、出生時間 / timezone 差異。"
            ),
            suggestion=(
                "比對 Conscious Sun gate / line 與 Design Sun gate / line。"
                "若 line 有差異，可能來自黃經計算精度、timezone 或 line boundary 設定。"
            ),
        )]

    def _compare_incarnation_cross(self, local, external: ExternalHumanDesignChart) -> List[HDReconciliationItem]:
        lv = getattr(local, "incarnation_cross", "") or ""
        ev = external.incarnation_cross or ""
        if not ev.strip():
            return [HDReconciliationItem(
                category="incarnation_cross", field="incarnation_cross",
                local_value=lv, external_value="",
                status="missing_external", severity="info",
                explanation="外部資料未提供 Incarnation Cross。",
            )]
        # Phase 1 local uses gate-based naming; external may use official cross names
        # Always mark as likely_method_difference — don't treat as high mismatch
        if lv.strip() == ev.strip():
            return [HDReconciliationItem(
                category="incarnation_cross", field="incarnation_cross",
                local_value=lv, external_value=ev,
                status="match", severity="info",
                explanation="Incarnation Cross 一致。",
            )]
        return [HDReconciliationItem(
            category="incarnation_cross", field="incarnation_cross",
            local_value=lv, external_value=ev,
            status="likely_method_difference", severity="info",
            explanation=(
                "Incarnation Cross 表示方式不同。本機 V1.9.x 以四個主要閘門初版命名；"
                "外部商業軟體使用完整正式交叉名稱。這屬於命名方法差異，不影響核心計算。"
            ),
            suggestion="後續版本可加入完整正式十字名稱對照表。",
        )]

    def _compare_planets(
        self,
        local_activations,
        external_activations: list,
        category: str,
        is_design: bool = False,
        local_design_method: str = "unknown",
    ) -> List[HDReconciliationItem]:
        items = []
        if not external_activations:
            return [HDReconciliationItem(
                category=category, field="planets",
                local_value=f"{len(local_activations)} planets",
                external_value="",
                status="missing_external", severity="info",
                explanation=f"外部資料未提供 {category} 行星資料。",
            )]

        for planet_name in ["Sun", "Earth"]:
            local_act = _find_activation(local_activations, planet_name)
            ext_act = _find_activation(external_activations, planet_name)

            field_label = f"{category.split('_')[0]}_{planet_name.lower()}"

            if local_act is None:
                items.append(HDReconciliationItem(
                    category=category, field=field_label,
                    local_value="N/A", external_value=str(ext_act.gate) if ext_act else "N/A",
                    status="missing_local", severity="info",
                    explanation=f"本機未找到 {planet_name} 行星資料。",
                ))
                continue

            if ext_act is None:
                items.append(HDReconciliationItem(
                    category=category, field=field_label,
                    local_value=f"Gate {local_act.gate} Line {local_act.line}",
                    external_value="",
                    status="missing_external", severity="info",
                    explanation=f"外部資料未提供 {planet_name} 行星資料。",
                ))
                continue

            local_gate = local_act.gate
            ext_gate = ext_act.gate
            local_line = local_act.line
            ext_line = ext_act.line

            local_str = f"Gate {local_gate} Line {local_line}"
            ext_str = f"Gate {ext_gate}" + (f" Line {ext_line}" if ext_line else "")

            if local_gate == ext_gate:
                if ext_line is None or local_line == ext_line:
                    items.append(HDReconciliationItem(
                        category=category, field=field_label,
                        local_value=local_str, external_value=ext_str,
                        status="match", severity="info",
                        explanation=f"{planet_name} gate / line 一致。",
                    ))
                else:
                    items.append(HDReconciliationItem(
                        category=category, field=field_label,
                        local_value=local_str, external_value=ext_str,
                        status="mismatch", severity="medium",
                        explanation=(
                            f"{planet_name} gate 一致，但 line 不一致。"
                            "可能原因：黃經精度、timezone 差異或 line boundary 設定。"
                        ),
                        suggestion="確認出生時間精確度；比對黃經計算結果。",
                    ))
            else:
                if is_design:
                    if local_design_method in ("solar_arc_88",):
                        design_note = (
                            "Design side 差異：本機已使用 exact 88° solar arc 計算設計日期。"
                            "差異可能來自 I-Ching wheel offset、timezone、或外部軟體使用不同起點。"
                        )
                        design_suggestion = (
                            "檢查 Gate Wheel 起點 offset（HUMAN_DESIGN_GATE_WHEEL_OFFSET_DEGREES）"
                            "及 timezone 設定。"
                        )
                    else:
                        design_note = (
                            f"Design side 差異：本機使用 {local_design_method}（近似值），"
                            "商業軟體多使用精準太陽弧（88° solar arc）回推設計日期。"
                        )
                        design_suggestion = (
                            "設定 HUMAN_DESIGN_DESIGN_DATE_METHOD=solar_arc_88 以啟用精準設計日期計算。"
                        )
                else:
                    design_note = "可能原因：I-Ching wheel order、黃經起點 offset、timezone 差異。"
                    design_suggestion = "檢查 Gate Wheel 起點、timezone offset、出生時間精確度。"

                items.append(HDReconciliationItem(
                    category=category, field=field_label,
                    local_value=local_str, external_value=ext_str,
                    status="mismatch", severity="high",
                    explanation=(
                        f"{planet_name} gate 不一致。{design_note}"
                    ),
                    suggestion=design_suggestion,
                ))
        return items

    def _compare_gates(self, local, external: ExternalHumanDesignChart) -> List[HDReconciliationItem]:
        if not external.activated_gates:
            return [HDReconciliationItem(
                category="gates", field="activated_gates",
                local_value=f"{len(getattr(local, 'activated_gates', []))} gates",
                external_value="",
                status="missing_external", severity="info",
                explanation="外部資料未提供 activated gates。",
            )]

        local_gates: Set[int] = {g.gate for g in (getattr(local, "activated_gates", []) or [])}
        ext_gates: Set[int] = set(external.activated_gates)

        overlap = local_gates & ext_gates
        missing_in_local = ext_gates - local_gates
        extra_in_local = local_gates - ext_gates

        status = "match" if not missing_in_local and not extra_in_local else "mismatch"
        severity = "info"
        if len(missing_in_local) + len(extra_in_local) > 4:
            severity = "high"
        elif len(missing_in_local) + len(extra_in_local) > 0:
            severity = "medium"

        explanation = (
            f"Gate 比對：{len(overlap)} 個一致，"
            f"{len(missing_in_local)} 個外部有本機無，"
            f"{len(extra_in_local)} 個本機有外部無。"
        )
        if missing_in_local:
            explanation += f" 外部有本機無：{sorted(missing_in_local)}。"
        if extra_in_local:
            explanation += f" 本機有外部無：{sorted(extra_in_local)}。"
        if status == "mismatch":
            explanation += " 可能原因：I-Ching wheel order、黃經 offset、Design Date 近似差異、timezone。"

        return [HDReconciliationItem(
            category="gates", field="activated_gates",
            local_value=f"{len(local_gates)} gates: {sorted(local_gates)}",
            external_value=f"{len(ext_gates)} gates: {sorted(ext_gates)}",
            status=status, severity=severity,
            explanation=explanation,
            suggestion=(
                "比對 I-Ching Wheel 起點 offset；"
                "確認 Design Date 是否因 88-day 近似而影響 Design side gates。"
                if status == "mismatch" else ""
            ),
        )]

    def _compare_channels(self, local, external: ExternalHumanDesignChart) -> List[HDReconciliationItem]:
        if not external.defined_channels:
            return [HDReconciliationItem(
                category="channels", field="defined_channels",
                local_value=f"{len(getattr(local, 'defined_channels', []))} channels",
                external_value="",
                status="missing_external", severity="info",
                explanation="外部資料未提供 defined channels。",
            )]

        local_channels: Set[str] = {
            normalize_channel(ch.channel)
            for ch in (getattr(local, "defined_channels", []) or [])
        }
        ext_channels: Set[str] = {normalize_channel(ch) for ch in external.defined_channels}

        overlap = local_channels & ext_channels
        missing_in_local = ext_channels - local_channels
        extra_in_local = local_channels - ext_channels

        status = "match" if not missing_in_local and not extra_in_local else "mismatch"
        severity = "info"
        if missing_in_local or extra_in_local:
            severity = "medium"

        explanation = (
            f"Channel 比對（已正規化）：{len(overlap)} 個一致，"
            f"{len(missing_in_local)} 個外部有本機無，"
            f"{len(extra_in_local)} 個本機有外部無。"
        )
        if missing_in_local:
            explanation += f" 外部有本機無：{sorted(missing_in_local)}。"
        if extra_in_local:
            explanation += f" 本機有外部無：{sorted(extra_in_local)}。"
        if status == "mismatch":
            explanation += " Channel 差異通常由 gate activation 差異造成。"

        return [HDReconciliationItem(
            category="channels", field="defined_channels",
            local_value=f"{sorted(local_channels)}",
            external_value=f"{sorted(ext_channels)}",
            status=status, severity=severity,
            explanation=explanation,
            suggestion=(
                "若 gate activation 已一致但 channel 不同，請比對 channel table mapping。"
                if status == "mismatch" else ""
            ),
        )]

    def _compare_centers(self, local, external: ExternalHumanDesignChart) -> List[HDReconciliationItem]:
        if not external.defined_centers:
            return [HDReconciliationItem(
                category="centers", field="defined_centers",
                local_value=f"{len(getattr(local, 'defined_centers', []))} centers",
                external_value="",
                status="missing_external", severity="info",
                explanation="外部資料未提供 defined centers。",
            )]

        local_defined: Set[str] = {
            normalize_center(c)
            for c in (getattr(local, "defined_centers", []) or [])
        }
        ext_defined: Set[str] = {normalize_center(c) for c in external.defined_centers}

        overlap = local_defined & ext_defined
        missing_in_local = ext_defined - local_defined
        extra_in_local = local_defined - ext_defined

        status = "match" if not missing_in_local and not extra_in_local else "mismatch"
        severity = "info"
        if missing_in_local or extra_in_local:
            severity = "medium"

        explanation = (
            f"Centers 比對（已正規化）：{len(overlap)} 個一致，"
            f"{len(missing_in_local)} 個外部有本機無，"
            f"{len(extra_in_local)} 個本機有外部無。"
        )
        if missing_in_local:
            explanation += f" 外部有本機無：{sorted(missing_in_local)}。"
        if extra_in_local:
            explanation += f" 本機有外部無：{sorted(extra_in_local)}。"
        if status == "mismatch":
            explanation += " Centers 差異通常由 channel / gate activation 差異造成。"

        return [HDReconciliationItem(
            category="centers", field="defined_centers",
            local_value=f"{sorted(local_defined)}",
            external_value=f"{sorted(ext_defined)}",
            status=status, severity=severity,
            explanation=explanation,
            suggestion=(
                "比對 channels：若 channel activation 有差異，centers 會跟著不同。"
                if status == "mismatch" else ""
            ),
        )]

    def _build_next_actions(self, items: List[HDReconciliationItem]) -> List[str]:
        actions = []
        categories_with_mismatch = {i.category for i in items if i.status == "mismatch"}
        if "gates" in categories_with_mismatch or "conscious_planets" in categories_with_mismatch:
            actions.append("檢查 I-Ching Wheel 起點偏移（Phase 1 wheel 需外部校準）")
        if "design_planets" in categories_with_mismatch:
            actions.append(
                "比對 Design Date 計算方式：確認本機使用 solar_arc_88 模式，"
                "並檢查 HUMAN_DESIGN_GATE_WHEEL_OFFSET_DEGREES 設定"
            )
        if "centers" in categories_with_mismatch or "channels" in categories_with_mismatch:
            actions.append("比對 channel table mapping 與 center 連接規則")
        if "type" in categories_with_mismatch or "authority" in categories_with_mismatch:
            actions.append("先解決 centers 差異，Type 與 Authority 通常會隨之修正")
        if "profile" in categories_with_mismatch:
            actions.append("確認出生時間精確到分鐘；比對 Conscious Sun gate / line")
        if not actions:
            actions.append("人類圖計算結果良好，無需立即調整")
            actions.append("建議定期與外部資料對照，確保 Gate Wheel 持續校準")
        return actions

    def reconcile_case(
        self,
        local,
        case: HumanDesignCalibrationCase,
    ) -> HDReconciliationReport:
        """
        Reconcile a local HumanDesignChart against a HumanDesignCalibrationCase.
        Convenience wrapper around reconcile().
        """
        return self.reconcile(local, case.external_chart)


def reconcile_dataset(
    local_chart,
    dataset: HumanDesignCalibrationDataset,
) -> BatchReconciliationSummary:
    """
    Run reconciliation of a single local HumanDesignChart against all cases
    in a dataset and return a BatchReconciliationSummary.

    local_chart: HumanDesignChart instance to compare against all cases.
    """
    engine = HumanDesignReconciliationEngine()
    case_reports: List[HDReconciliationReport] = []
    mostly_match = 0
    minor_diff = 0
    major_diff = 0
    insufficient = 0
    total_match = 0
    total_mismatch = 0
    total_method_diff = 0
    mismatch_category_counter: Counter = Counter()

    for case in dataset.cases:
        try:
            report = engine.reconcile_case(local_chart, case)
        except Exception as exc:
            report = HDReconciliationReport(
                overall_status="insufficient_external_data",
                summary=f"比對失敗：{exc}",
            )

        case_reports.append(report)

        if report.overall_status == "mostly_match":
            mostly_match += 1
        elif report.overall_status == "minor_difference":
            minor_diff += 1
        elif report.overall_status == "major_difference":
            major_diff += 1
        else:
            insufficient += 1

        total_match += report.match_count
        total_mismatch += report.mismatch_count
        total_method_diff += report.method_difference_count

        for item in report.items:
            if item.status == "mismatch":
                mismatch_category_counter[item.category] += 1

    total = len(dataset.cases)
    processed = sum(
        1 for r in case_reports if r.overall_status != "insufficient_external_data"
    )

    # Most common mismatch categories (top 5)
    most_common = [cat for cat, _ in mismatch_category_counter.most_common(5)]

    # Design date method notes
    design_method = getattr(local_chart, "design_date_method", "unknown")
    wheel_offset = getattr(local_chart, "gate_wheel_offset_degrees", 0.0)
    design_date_notes = [
        f"本機 Design Date Method: {design_method}",
        f"Solar arc 誤差: {getattr(local_chart, 'design_solar_arc_error_degrees', None)}°"
        if getattr(local_chart, "design_solar_arc_error_degrees", None) is not None
        else "Solar arc 誤差: 未記錄（mock 或 fallback 模式）",
    ]
    gate_offset_notes = [
        f"本機 Gate Wheel Offset: {wheel_offset:+.3f}°",
        "Offset 0° = Phase 1 預設（無偏移）" if wheel_offset == 0.0
        else f"Offset {wheel_offset:+.3f}° 已套用至所有行星計算",
    ]

    if total_mismatch > 0 and most_common:
        summary_text = (
            f"共 {total} 案例，已處理 {processed} 案例。"
            f"一致 {mostly_match}，輕微差異 {minor_diff}，重大差異 {major_diff}，資料不足 {insufficient}。"
            f"最常見差異：{', '.join(most_common)}。"
        )
    elif processed > 0:
        summary_text = f"共 {total} 案例，已處理 {processed} 案例。整體差異偏少。"
    else:
        summary_text = "無案例可處理，請確認資料集是否含有效外部資料。"

    return BatchReconciliationSummary(
        total_cases=total,
        processed_cases=processed,
        mostly_match_count=mostly_match,
        minor_difference_count=minor_diff,
        major_difference_count=major_diff,
        insufficient_data_count=insufficient,
        total_match_items=total_match,
        total_mismatch_items=total_mismatch,
        total_method_difference_items=total_method_diff,
        most_common_mismatch_categories=most_common,
        design_date_method_notes=design_date_notes,
        gate_offset_notes=gate_offset_notes,
        case_reports=case_reports,
        summary=summary_text,
    )
