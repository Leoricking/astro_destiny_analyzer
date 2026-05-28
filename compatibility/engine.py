"""
Astro Destiny Analyzer — Compatibility Engine
V1.7.0: Phase 1 — basic multi-system relationship analysis.

Uses existing ReportGenerator to produce individual FullReports,
then builds compatibility sub-analyses from those results.
No existing engine logic is duplicated.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Tuple

from core.models import FullReport, WesternChart, BaZiChart, ZiWeiChart
from compatibility.models import (
    CompatibilityInput, CompatibilityReport,
    AstrologyCompatibility, BaziCompatibility, ZiWeiCompatibility,
    NumerologyCompatibility, BloodTypeCompatibility,
    CompatibilitySynthesis, ScoreBreakdown, RelationshipType,
    relationship_label,
)
from compatibility.report import render_compatibility_report
from compatibility.advanced_astrology import AdvancedAstrologyEngine
from compatibility.visuals import build_relationship_visuals


# ── Western element helpers ───────────────────────────────────────────────────

_FIRE_SIGNS  = {"牡羊座", "獅子座", "射手座"}
_EARTH_SIGNS = {"金牛座", "處女座", "摩羯座"}
_AIR_SIGNS   = {"雙子座", "天秤座", "水瓶座"}
_WATER_SIGNS = {"巨蟹座", "天蠍座", "雙魚座"}

_COMPLEMENTARY = {("火", "風"), ("風", "火"), ("土", "水"), ("水", "土")}
_TENSE         = {("火", "水"), ("水", "火"), ("土", "風"), ("風", "土")}


def _sign_element(sign_value: str) -> str:
    if sign_value in _FIRE_SIGNS:  return "火"
    if sign_value in _EARTH_SIGNS: return "土"
    if sign_value in _AIR_SIGNS:   return "風"
    if sign_value in _WATER_SIGNS: return "水"
    return "未知"


def _element_compat_score(e1: str, e2: str) -> Tuple[int, str]:
    """Return (score 0-100, label) for two western element names."""
    if e1 == "未知" or e2 == "未知":
        return (60, "資料不足，以中性估算")
    if e1 == e2:
        return (85, f"同為{e1}象，共鳴強")
    if (e1, e2) in _COMPLEMENTARY:
        return (75, f"{e1}象與{e2}象互補激發")
    if (e1, e2) in _TENSE:
        return (45, f"{e1}象與{e2}象對立，需要溝通")
    return (62, f"{e1}象與{e2}象中性，需要時間理解")


def _get_planet_sign(wc: Optional[WesternChart], planet_name: str) -> str:
    if not wc or not wc.planet_positions:
        return "未知"
    for pp in wc.planet_positions:
        if getattr(getattr(pp, "planet", None), "value", "") == planet_name:
            return getattr(getattr(pp, "sign", None), "value", "未知") or "未知"
    return "未知"


def _get_planet_degree(wc: Optional[WesternChart], planet_name: str) -> Optional[float]:
    if not wc or not wc.planet_positions:
        return None
    for pp in wc.planet_positions:
        if getattr(getattr(pp, "planet", None), "value", "") == planet_name:
            return getattr(pp, "degree", None)
    return None


def _aspect_name(angle: float) -> Optional[str]:
    orbs = [(0, 8, "合相"), (60, 6, "六合"), (90, 6, "刑相"),
            (120, 6, "拱相"), (180, 8, "對分")]
    for target, orb, name in orbs:
        if abs(angle - target) <= orb or abs(angle - (360 - target)) <= orb:
            return name
    return None


# ── BaZi element helpers ──────────────────────────────────────────────────────

_BAZI_GENERATES = {
    "木": "火", "火": "土", "土": "金", "金": "水", "水": "木"
}
_BAZI_CONTROLS = {
    "木": "土", "土": "水", "水": "火", "火": "金", "金": "木"
}


def _bazi_relation(e1: str, e2: str) -> str:
    if e1 == e2:
        return "同元素，價值觀相近"
    if _BAZI_GENERATES.get(e1) == e2:
        return f"{e1}生{e2}，互相滋養"
    if _BAZI_GENERATES.get(e2) == e1:
        return f"{e2}生{e1}，互相滋養"
    if _BAZI_CONTROLS.get(e1) == e2:
        return f"{e1}剋{e2}，激發成長也帶來磨合"
    if _BAZI_CONTROLS.get(e2) == e1:
        return f"{e2}剋{e1}，激發成長也帶來磨合"
    return "元素相距，各有節奏"


def _bazi_relation_score(e1: str, e2: str) -> int:
    if e1 == e2:          return 78
    if _BAZI_GENERATES.get(e1) == e2 or _BAZI_GENERATES.get(e2) == e1:
        return 82
    if _BAZI_CONTROLS.get(e1) == e2 or _BAZI_CONTROLS.get(e2) == e1:
        return 58
    return 65


# ── Life path compatibility ───────────────────────────────────────────────────

_LP_THEMES: Dict[int, str] = {
    1: "獨立與領導", 2: "照顧與協調", 3: "表達與創意",
    4: "秩序與穩定", 5: "自由與冒險", 6: "責任與承諾",
    7: "深度與探索", 8: "目標與權力", 9: "理想與包容",
    11: "直覺與啟發", 22: "宏觀建設", 33: "服務與教導",
}

_LP_COMPAT: Dict[Tuple[int, int], int] = {
    (1, 1): 65, (1, 2): 72, (1, 3): 78, (1, 4): 60,
    (1, 5): 75, (1, 6): 68, (1, 7): 62, (1, 8): 70,
    (1, 9): 65, (2, 2): 68, (2, 3): 73, (2, 4): 80,
    (2, 5): 60, (2, 6): 85, (2, 7): 70, (2, 8): 65,
    (2, 9): 75, (3, 3): 70, (3, 4): 60, (3, 5): 82,
    (3, 6): 72, (3, 7): 65, (3, 8): 68, (3, 9): 75,
    (4, 4): 72, (4, 5): 58, (4, 6): 78, (4, 7): 80,
    (4, 8): 72, (4, 9): 65, (5, 5): 65, (5, 6): 62,
    (5, 7): 72, (5, 8): 68, (5, 9): 75, (6, 6): 78,
    (6, 7): 68, (6, 8): 70, (6, 9): 80, (7, 7): 68,
    (7, 8): 62, (7, 9): 78, (8, 8): 65, (8, 9): 72,
    (9, 9): 75,
}


def _lp_compat_score(lp_a: int, lp_b: int) -> int:
    key = (min(lp_a, lp_b), max(lp_a, lp_b))
    return _LP_COMPAT.get(key, 65)


def _lp_shared_theme(lp_a: int, lp_b: int) -> str:
    ta = _LP_THEMES.get(lp_a, f"靈數{lp_a}")
    tb = _LP_THEMES.get(lp_b, f"靈數{lp_b}")
    if lp_a == lp_b:
        return f"兩人皆重視{ta}，共鳴強但可能有共同盲點"
    return f"A 重視{ta}，B 重視{tb}，可互相補足不同面向"


def _lp_challenge_theme(lp_a: int, lp_b: int) -> str:
    complementary_pairs = {(1, 2), (3, 4), (5, 6), (7, 8), (9, 1)}
    key = (min(lp_a, lp_b), max(lp_a, lp_b))
    if key in complementary_pairs or (lp_b, lp_a) in complementary_pairs:
        return "兩人語言節奏不同，需要互相翻譯彼此的表達方式"
    if lp_a == lp_b:
        return "相同靈數的兩人可能有相似盲點，需要引入外部視角平衡"
    return "差異帶來成長，也帶來溝通上需要刻意練習的地方"


# ── Blood type compatibility ──────────────────────────────────────────────────

_BT_STYLES: Dict[str, str] = {
    "A":       "注重秩序與責任，壓力易內化",
    "B":       "重視自由與彈性，隨性直接",
    "O":       "目標導向，行動力強，主導性高",
    "AB":      "理性分析，需要個人空間，矛盾整合",
    "Unknown": "血型未知，略過此維度分析",
}

_BT_CONFLICT: Dict[str, str] = {
    "A":       "遇衝突傾向壓抑，需要安全感才能開口",
    "B":       "遇衝突較直接表達，可能讓對方措手不及",
    "O":       "遇衝突容易主導立場，需要注意傾聽空間",
    "AB":      "遇衝突傾向抽離分析，可能顯得冷淡",
    "Unknown": "未知",
}


def _blood_compat(bt_a: str, bt_b: str) -> BloodTypeCompatibility:
    pair = f"{bt_a} × {bt_b}"
    if bt_a == "Unknown" or bt_b == "Unknown":
        return BloodTypeCompatibility(
            blood_pair=pair,
            interaction_style="其中一方血型未知，本維度略過。",
            conflict_style="─",
            advice="補充血型資料後可獲得更完整分析。",
        )
    style_a = _BT_STYLES.get(bt_a, "")
    style_b = _BT_STYLES.get(bt_b, "")
    conflict_a = _BT_CONFLICT.get(bt_a, "")
    conflict_b = _BT_CONFLICT.get(bt_b, "")
    interaction = f"A方（{bt_a}型）{style_a}；B方（{bt_b}型）{style_b}。"
    conflict = f"衝突時：A方傾向{conflict_a}；B方傾向{conflict_b}。"
    advice_map = {
        ("A", "A"): "兩人都需要安全感才能敞開心扉，建議建立固定溝通儀式。",
        ("A", "B"): "A型需要秩序，B型追求自由，彼此尊重節奏差異是關鍵。",
        ("A", "O"): "O型主導性與A型細膩可互補，但需避免A型壓力無出口。",
        ("A", "AB"): "兩者都傾向內化壓力，建議主動創造開放表達的機會。",
        ("B", "B"): "兩人都直接，溝通活潑，需注意不要忽略深層情感需求。",
        ("B", "O"): "都有行動力，但主導方式不同，建議輪流主導決策。",
        ("B", "AB"): "B型直接與AB型分析性互補，但需要互相理解溝通節奏。",
        ("O", "O"): "兩人主導性都強，建議明確分工，避免互相競爭控制權。",
        ("O", "AB"): "O型行動力與AB型思考力是好組合，保持彼此欣賞。",
        ("AB", "AB"): "兩人都需要空間，需刻意安排親密時光，避免漸漸疏離。",
    }
    key = (min(bt_a, bt_b), max(bt_a, bt_b))
    advice = advice_map.get(key, "互相尊重對方的情緒處理風格，是維持關係穩定的基礎。")
    return BloodTypeCompatibility(
        blood_pair=pair,
        interaction_style=interaction,
        conflict_style=conflict,
        advice=advice,
    )


# ── Main Engine ───────────────────────────────────────────────────────────────

class CompatibilityEngine:
    """
    Generates a CompatibilityReport from a CompatibilityInput.
    Calls ReportGenerator internally for individual charts.
    """

    def generate(self, compat_input: CompatibilityInput) -> CompatibilityReport:
        from reports.generator import ReportGenerator
        gen = ReportGenerator()

        report_a = gen.generate(compat_input.person_a, persist=False)
        report_b = gen.generate(compat_input.person_b, persist=False)

        astrology  = self._build_astrology(report_a, report_b)
        bazi       = self._build_bazi(report_a, report_b)
        ziwei      = self._build_ziwei(report_a, report_b, compat_input.relationship_type)
        numerology = self._build_numerology(report_a, report_b)
        blood      = _blood_compat(
            report_a.profile.blood_type.value,
            report_b.profile.blood_type.value,
        )
        scores   = self._build_scores(astrology, bazi, ziwei, numerology, blood, compat_input)
        synthesis = self._build_synthesis(compat_input, astrology, bazi, ziwei, numerology, blood, scores)

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # V1.8.0: Advanced synastry + composite chart
        advanced_astrology = None
        try:
            wc_a = report_a.western_chart
            wc_b = report_b.western_chart
            if wc_a is not None and wc_b is not None:
                advanced_astrology = AdvancedAstrologyEngine().calculate(wc_a, wc_b)
        except Exception:  # never crash the main flow
            advanced_astrology = None

        # V1.8.2: Visual chart data
        visuals = None
        if advanced_astrology is not None:
            try:
                visuals = build_relationship_visuals(advanced_astrology)
            except Exception:
                visuals = None

        report = CompatibilityReport(
            report_id=str(uuid.uuid4())[:8],
            created_at=created_at,
            person_a_profile=report_a.profile,
            person_b_profile=report_b.profile,
            person_a_chart_summary=self._chart_summary(report_a),
            person_b_chart_summary=self._chart_summary(report_b),
            relationship_type=compat_input.relationship_type,
            score_breakdown=scores,
            astrology=astrology,
            bazi=bazi,
            ziwei=ziwei,
            numerology=numerology,
            blood_type=blood,
            synthesis=synthesis,
            advanced_astrology=advanced_astrology,
            visuals=visuals,
        )
        report.markdown_body = render_compatibility_report(report)
        return report

    # ── Chart summary ─────────────────────────────────────────────────────────

    def _chart_summary(self, report: FullReport) -> Dict:
        wc = report.western_chart
        bc = report.bazi_chart
        zc = report.ziwei_chart
        nc = report.numerology_chart
        return {
            "sun":         _get_planet_sign(wc, "太陽"),
            "moon":        _get_planet_sign(wc, "月亮"),
            "mercury":     _get_planet_sign(wc, "水星"),
            "venus":       _get_planet_sign(wc, "金星"),
            "mars":        _get_planet_sign(wc, "火星"),
            "ascendant":   (wc.ascendant.value if wc and wc.ascendant_accuracy == "precise" else "未知"),
            "western_mode": getattr(wc, "calculation_mode", "─") if wc else "─",
            "day_master":  (bc.day_master.value if bc and bc.day_master else "─"),
            "day_master_element": (bc.day_master_element.value if bc and bc.day_master_element else "─"),
            "bazi_mode":   getattr(bc, "calculation_mode", "─") if bc else "─",
            "ming_stars":  ("、".join(zc.ming_palace.main_stars) if zc and zc.ming_palace and zc.ming_palace.main_stars else "未知"),
            "shen_palace": (zc.shen_palace.name if zc and zc.shen_palace else "─"),
            "life_path":   (nc.life_path_number if nc else 0),
            "ziwei_mode":  getattr(zc, "calculation_mode", "─") if zc else "─",
            "birth_time_known": report.profile.birth_time_is_known,
        }

    # ── Astrology compatibility ───────────────────────────────────────────────

    def _build_astrology(self, ra: FullReport, rb: FullReport) -> AstrologyCompatibility:
        wca, wcb = ra.western_chart, rb.western_chart

        sun_a  = _get_planet_sign(wca, "太陽")
        sun_b  = _get_planet_sign(wcb, "太陽")
        moon_a = _get_planet_sign(wca, "月亮")
        moon_b = _get_planet_sign(wcb, "月亮")
        merc_a = _get_planet_sign(wca, "水星")
        merc_b = _get_planet_sign(wcb, "水星")
        ven_a  = _get_planet_sign(wca, "金星")
        mars_b = _get_planet_sign(wcb, "火星")
        ven_b  = _get_planet_sign(wcb, "金星")
        mars_a = _get_planet_sign(wca, "火星")

        sun_e_a, sun_e_b   = _sign_element(sun_a),  _sign_element(sun_b)
        moon_e_a, moon_e_b = _sign_element(moon_a), _sign_element(moon_b)
        merc_e_a, merc_e_b = _sign_element(merc_a), _sign_element(merc_b)

        _, sun_desc   = _element_compat_score(sun_e_a, sun_e_b)
        _, moon_desc  = _element_compat_score(moon_e_a, moon_e_b)
        _, merc_desc  = _element_compat_score(merc_e_a, merc_e_b)

        # Venus-Mars cross pair
        ven_a_e  = _sign_element(ven_a)
        mars_b_e = _sign_element(mars_b)
        _, vm_desc = _element_compat_score(ven_a_e, mars_b_e)

        # Ascendant pair (only if precise)
        asc_a = (wca.ascendant.value if wca and wca.ascendant_accuracy == "precise" else "未知")
        asc_b = (wcb.ascendant.value if wcb and wcb.ascendant_accuracy == "precise" else "未知")
        if asc_a != "未知" and asc_b != "未知":
            asc_e_a, asc_e_b = _sign_element(asc_a), _sign_element(asc_b)
            _, asc_desc = _element_compat_score(asc_e_a, asc_e_b)
            asc_pair = f"A上升{asc_a}（{asc_e_a}象）× B上升{asc_b}（{asc_e_b}象）— {asc_desc}"
        else:
            asc_pair = "上升星座需精確出生時間才可計算"

        # Key aspects from degrees
        key_aspects: List[str] = []
        planets_to_check = [("太陽", "太陽"), ("月亮", "月亮"), ("太陽", "月亮"),
                            ("金星", "火星"), ("水星", "水星")]
        for pa, pb in planets_to_check:
            deg_a = _get_planet_degree(wca, pa)
            deg_b = _get_planet_degree(wcb, pb)
            if deg_a is not None and deg_b is not None:
                diff = abs(deg_a - deg_b) % 360
                if diff > 180:
                    diff = 360 - diff
                asp = _aspect_name(diff)
                if asp:
                    key_aspects.append(f"A {pa} {asp} B {pb}（orb {diff:.1f}°）")

        harmony: List[str] = []
        tension: List[str] = []

        for desc in [sun_desc, moon_desc, merc_desc]:
            if "共鳴" in desc or "互補" in desc or "滋養" in desc:
                harmony.append(desc)
            elif "對立" in desc or "磨合" in desc:
                tension.append(desc)

        # Build interpretation
        interp_parts = [
            f"**太陽配對**：A {sun_a}（{sun_e_a}象）× B {sun_b}（{sun_e_b}象）— {sun_desc}。",
            f"**月亮配對**：A {moon_a}（{moon_e_a}象）× B {moon_b}（{moon_e_b}象）— {moon_desc}。",
            f"**水星配對**：A {merc_a}（{merc_e_a}象）× B {merc_b}（{merc_e_b}象）— {merc_desc}，影響溝通節奏的協調性。",
            f"**金星火星**：A金星{ven_a}（{ven_a_e}象）× B火星{mars_b}（{mars_b_e}象）— {vm_desc}，反映吸引力模式。",
        ]
        interpretation = "\n\n".join(interp_parts)

        accuracy_notes = []
        if wca and wca.calculation_mode == "mock_fallback":
            accuracy_notes.append("A方西洋占星為 mock_fallback，行星度數為估算值")
        if wcb and wcb.calculation_mode == "mock_fallback":
            accuracy_notes.append("B方西洋占星為 mock_fallback，行星度數為估算值")
        if not ra.profile.birth_time_is_known:
            accuracy_notes.append("A方缺出生時間，月亮位置可能有誤差，上升與宮位無法精確計算")
        if not rb.profile.birth_time_is_known:
            accuracy_notes.append("B方缺出生時間，月亮位置可能有誤差，上升與宮位無法精確計算")
        accuracy_note = "；".join(accuracy_notes) if accuracy_notes else "計算模式正常"

        return AstrologyCompatibility(
            sun_pair=f"A {sun_a} × B {sun_b}（{sun_e_a}/{sun_e_b}象）",
            moon_pair=f"A {moon_a} × B {moon_b}（{moon_e_a}/{moon_e_b}象）",
            venus_mars_pair=f"A金星{ven_a} × B火星{mars_b}（{ven_a_e}/{mars_b_e}象）",
            mercury_pair=f"A {merc_a} × B {merc_b}（{merc_e_a}/{merc_e_b}象）",
            ascendant_pair=asc_pair,
            key_aspects=key_aspects,
            harmony_factors=harmony if harmony else ["元素互動中性，各有特色"],
            tension_factors=tension if tension else ["暫無明顯對立因素"],
            interpretation=interpretation,
            accuracy_note=accuracy_note,
        )

    # ── BaZi compatibility ────────────────────────────────────────────────────

    def _build_bazi(self, ra: FullReport, rb: FullReport) -> BaziCompatibility:
        bca, bcb = ra.bazi_chart, rb.bazi_chart

        dm_a = (bca.day_master.value if bca and bca.day_master else "未知")
        dm_b = (bcb.day_master.value if bcb and bcb.day_master else "未知")
        dm_e_a = (bca.day_master_element.value if bca and bca.day_master_element else "未知")
        dm_e_b = (bcb.day_master_element.value if bcb and bcb.day_master_element else "未知")

        relation = _bazi_relation(dm_e_a, dm_e_b)

        fav_a = {e.value for e in (bca.favorable_elements or [])} if bca else set()
        fav_b = {e.value for e in (bcb.favorable_elements or [])} if bcb else set()
        unf_a = {e.value for e in (bca.unfavorable_elements or [])} if bca else set()
        unf_b = {e.value for e in (bcb.unfavorable_elements or [])} if bcb else set()

        supportive: List[str] = []
        conflicting: List[str] = []

        # A's day master element in B's favorable
        if dm_e_a != "未知" and dm_e_a in fav_b:
            supportive.append(f"A日主（{dm_e_a}）正好是B的喜用元素")
        if dm_e_b != "未知" and dm_e_b in fav_a:
            supportive.append(f"B日主（{dm_e_b}）正好是A的喜用元素")

        # Unfavorable cross
        if dm_e_a != "未知" and dm_e_a in unf_b:
            conflicting.append(f"A日主（{dm_e_a}）對B而言是忌神元素，可能帶來壓力")
        if dm_e_b != "未知" and dm_e_b in unf_a:
            conflicting.append(f"B日主（{dm_e_b}）對A而言是忌神元素，可能帶來壓力")

        # Shared favorable
        shared_fav = fav_a & fav_b
        if shared_fav:
            supportive.append(f"兩人共同喜用元素：{'、'.join(shared_fav)}，互動方向一致")

        if not supportive:
            supportive = ["五行互動以元素本質定性，建議以實際相處驗證"]
        if not conflicting:
            conflicting = ["目前未偵測到明顯忌神放大問題"]

        fe_parts = []
        for elem in ["木", "火", "土", "金", "水"]:
            ratio_a = (bca.five_element_ratio.get(elem, 0) if bca else 0)
            ratio_b = (bcb.five_element_ratio.get(elem, 0) if bcb else 0)
            avg = (ratio_a + ratio_b) / 2
            fe_parts.append(f"{elem} {avg:.0f}%")
        five_element_balance = "兩人合計五行比例（平均）：" + "、".join(fe_parts)

        interp_parts = [
            f"A日主{dm_a}（{dm_e_a}），B日主{dm_b}（{dm_e_b}）。",
            f"日主關係：{relation}。",
        ]
        if supportive:
            interp_parts.append("互補之處：" + "；".join(s for s in supportive if "壓力" not in s))
        if conflicting and "未偵測" not in conflicting[0]:
            interp_parts.append("需注意之處：" + "；".join(conflicting) + "。建議化解方式：透過開放溝通表達各自的壓力來源，而非期待對方自動調整。")

        accuracy_notes = []
        if not ra.profile.birth_time_is_known:
            accuracy_notes.append("A方缺出生時間，時柱與晚年互動無法精確計算")
        if not rb.profile.birth_time_is_known:
            accuracy_notes.append("B方缺出生時間，時柱與晚年互動無法精確計算")

        return BaziCompatibility(
            person_a_day_master=f"{dm_a}（{dm_e_a}）",
            person_b_day_master=f"{dm_b}（{dm_e_b}）",
            five_element_balance=five_element_balance,
            supportive_elements=supportive,
            conflicting_elements=conflicting,
            day_master_relation=relation,
            interpretation="\n\n".join(interp_parts),
            accuracy_note="；".join(accuracy_notes) if accuracy_notes else "計算模式正常",
        )

    # ── ZiWei compatibility ───────────────────────────────────────────────────

    def _build_ziwei(
        self,
        ra: FullReport,
        rb: FullReport,
        rel_type: RelationshipType,
    ) -> ZiWeiCompatibility:
        zca, zcb = ra.ziwei_chart, rb.ziwei_chart

        def _ming_stars(zc: Optional[ZiWeiChart]) -> str:
            if not zc or not zc.ming_palace:
                return "未知"
            stars = zc.ming_palace.main_stars
            return "、".join(stars) if stars else "空宮"

        def _shen_name(zc: Optional[ZiWeiChart]) -> str:
            if not zc:
                return "─"
            if zc.shen_palace:
                return zc.shen_palace.name
            return getattr(zc, "shen_branch", "─") or "─"

        def _palace_stars(zc: Optional[ZiWeiChart], attr: str) -> List[str]:
            if not zc:
                return []
            palace = getattr(zc, attr, None)
            return (palace.main_stars or []) if palace else []

        ming_a = _ming_stars(zca)
        ming_b = _ming_stars(zcb)
        shen_a = _shen_name(zca)
        shen_b = _shen_name(zcb)

        # Stability vs change stars
        _stable_stars   = {"天府", "太陰", "天相", "天梁", "武曲", "紫微"}
        _change_stars   = {"破軍", "廉貞", "七殺", "貪狼"}
        _leader_stars   = {"紫微", "武曲", "廉貞", "七殺"}
        _coord_stars    = {"天機", "天相", "天梁", "太陰"}

        def _star_profile(stars_str: str) -> Tuple[str, str]:
            stars = set(s.strip() for s in stars_str.split("、")) if stars_str != "未知" else set()
            style = "穩定型" if stars & _stable_stars else ("變革型" if stars & _change_stars else "均衡型")
            role  = "領導型" if stars & _leader_stars else ("協調型" if stars & _coord_stars else "獨特型")
            return style, role

        style_a, role_a = _star_profile(ming_a)
        style_b, role_b = _star_profile(ming_b)

        interactions: List[str] = []
        interactions.append(f"A命宮主星：{ming_a}（{style_a}、{role_a}）")
        interactions.append(f"B命宮主星：{ming_b}（{style_b}、{role_b}）")

        if style_a != style_b:
            interactions.append(f"一方偏{style_a}、一方偏{style_b}，生活節奏可能需要協商")
        if role_a != role_b:
            interactions.append(f"一方傾向{role_a}、一方傾向{role_b}，可形成互補分工")

        # Relationship-type specific palaces
        if rel_type in (RelationshipType.ROMANTIC, RelationshipType.MARRIAGE):
            sp_a = _palace_stars(zca, "spouse_palace")
            sp_b = _palace_stars(zcb, "spouse_palace")
            if sp_a:
                interactions.append(f"A夫妻宮主星：{'、'.join(sp_a)}")
            if sp_b:
                interactions.append(f"B夫妻宮主星：{'、'.join(sp_b)}")
        elif rel_type == RelationshipType.BUSINESS:
            career_a = _palace_stars(zca, "career_palace")
            career_b = _palace_stars(zcb, "career_palace")
            if career_a:
                interactions.append(f"A官祿宮主星：{'、'.join(career_a)}")
            if career_b:
                interactions.append(f"B官祿宮主星：{'、'.join(career_b)}")
        elif rel_type == RelationshipType.PARENT_CHILD:
            parents_a = _palace_stars(zca, "parents_palace")
            children_b = _palace_stars(zcb, "children_palace")
            if parents_a:
                interactions.append(f"A父母宮：{'、'.join(parents_a)}")
            if children_b:
                interactions.append(f"B子女宮：{'、'.join(children_b)}")

        # Main star resonance
        a_stars = set(ming_a.split("、")) if ming_a != "未知" else set()
        b_stars = set(ming_b.split("、")) if ming_b != "未知" else set()
        shared = a_stars & b_stars
        resonance = (
            f"兩人命宮共有主星：{'、'.join(shared)}，互動語言相近，容易理解彼此。"
            if shared else
            f"命宮主星不同（{ming_a} vs {ming_b}），各有視角，需要主動分享彼此的思維方式。"
        )

        # Da xian context
        da_xian_ctx = "目前大限分析為 Phase 1 骨架，僅作十年焦點背景，不作流年斷事。"
        if zca and zca.da_xian:
            dx_a = zca.da_xian[0]
            da_xian_ctx += f" A方目前第一大限：{dx_a.start_age}～{dx_a.end_age}歲，宮位：{dx_a.palace_name}。"
        if zcb and zcb.da_xian:
            dx_b = zcb.da_xian[0]
            da_xian_ctx += f" B方目前第一大限：{dx_b.start_age}～{dx_b.end_age}歲，宮位：{dx_b.palace_name}。"

        interp = (
            f"A的命宮能量偏向{style_a}，B偏向{style_b}，"
            + ("兩人方向一致，容易建立共同願景。" if style_a == style_b else "兩人節奏不同，需要協商生活步調。")
            + f"\n\n{resonance}"
            + "\n\n身宮反映後天行動重心："
            + f"A身宮位於{shen_a}，B身宮位於{shen_b}，"
            + ("兩人重心相近，方向感一致。" if shen_a == shen_b else "兩人重心略有不同，理解彼此的優先順序有助於減少誤解。")
        )

        accuracy_notes = []
        if zca and zca.calculation_mode == "mock_fallback":
            accuracy_notes.append("A方紫微為 mock_fallback")
        if zcb and zcb.calculation_mode == "mock_fallback":
            accuracy_notes.append("B方紫微為 mock_fallback")
        if not ra.profile.birth_time_is_known:
            accuracy_notes.append("A方缺出生時間，命宮可能不精確")
        if not rb.profile.birth_time_is_known:
            accuracy_notes.append("B方缺出生時間，命宮可能不精確")

        return ZiWeiCompatibility(
            person_a_ming_palace=ming_a,
            person_b_ming_palace=ming_b,
            person_a_shen_palace=shen_a,
            person_b_shen_palace=shen_b,
            key_palace_interactions=interactions if interactions else ["宮位資料不足，以命宮主星作基礎比對"],
            main_star_resonance=resonance,
            da_xian_context=da_xian_ctx,
            interpretation=interp,
            accuracy_note="；".join(accuracy_notes) if accuracy_notes else "計算模式正常",
        )

    # ── Numerology compatibility ──────────────────────────────────────────────

    def _build_numerology(self, ra: FullReport, rb: FullReport) -> NumerologyCompatibility:
        nc_a, nc_b = ra.numerology_chart, rb.numerology_chart
        lp_a = (nc_a.life_path_number if nc_a else 1)
        lp_b = (nc_b.life_path_number if nc_b else 1)
        score = _lp_compat_score(lp_a, lp_b)
        shared = _lp_shared_theme(lp_a, lp_b)
        challenge = _lp_challenge_theme(lp_a, lp_b)
        ta = _LP_THEMES.get(lp_a, f"靈數{lp_a}")
        tb = _LP_THEMES.get(lp_b, f"靈數{lp_b}")
        interp = (
            f"A生命靈數{lp_a}（{ta}），B生命靈數{lp_b}（{tb}）。\n\n"
            f"{shared}\n\n"
            f"挑戰面向：{challenge}\n\n"
            f"兩人靈數相容度參考值：{score}/100。"
            "請注意靈數為輔助參考，不代表絕對。"
        )
        return NumerologyCompatibility(
            life_path_pair=f"{lp_a} × {lp_b}",
            shared_theme=shared,
            challenge_theme=challenge,
            interpretation=interp,
        )

    # ── Score ─────────────────────────────────────────────────────────────────

    def _build_scores(
        self,
        astro: AstrologyCompatibility,
        bazi: BaziCompatibility,
        ziwei: ZiWeiCompatibility,
        num: NumerologyCompatibility,
        blood: BloodTypeCompatibility,
        compat_input: CompatibilityInput,
    ) -> ScoreBreakdown:
        ra_profile = compat_input.person_a
        rb_profile = compat_input.person_b

        # Derive element scores from moon/sun/mercury pairs
        def _pair_score(pair_str: str) -> int:
            # Extract elements from pattern "A X × B Y（e1/e2象）"
            import re as _re
            m = _re.search(r"（([^/]+)/([^象]+)象）", pair_str)
            if m:
                return _element_compat_score(m.group(1), m.group(2))[0]
            return 60

        moon_s  = _pair_score(astro.moon_pair)
        sun_s   = _pair_score(astro.sun_pair)
        merc_s  = _pair_score(astro.mercury_pair)
        vm_s    = _pair_score(astro.venus_mars_pair)

        # BaZi score
        bazi_s = _bazi_relation_score(
            bazi.person_a_day_master.split("（")[-1].rstrip("）"),
            bazi.person_b_day_master.split("（")[-1].rstrip("）"),
        )

        # Numerology
        lp_pair = num.life_path_pair  # "X × Y"
        try:
            parts = lp_pair.split("×")
            lp_a, lp_b = int(parts[0].strip()), int(parts[1].strip())
            num_s = _lp_compat_score(lp_a, lp_b)
        except Exception:
            num_s = 65

        # Conflict indicators
        conflict_base = 40
        if astro.tension_factors and "暫無" not in astro.tension_factors[0]:
            conflict_base += 15 * len(astro.tension_factors)
        if bazi.conflicting_elements and "未偵測" not in bazi.conflicting_elements[0]:
            conflict_base += 10 * len(bazi.conflicting_elements)
        conflict_score = min(conflict_base, 85)

        # Supportive element bonus
        support_bonus = 0
        if bazi.supportive_elements and "建議" not in bazi.supportive_elements[0]:
            support_bonus = 8 * min(len(bazi.supportive_elements), 3)

        emotional_score    = int((moon_s * 0.5 + sun_s * 0.25 + bazi_s * 0.25) + support_bonus * 0.3)
        communication_score = int((merc_s * 0.5 + num_s * 0.3 + sun_s * 0.2))
        attraction_score   = int((vm_s * 0.6 + sun_s * 0.25 + moon_s * 0.15))
        stability_score    = int((bazi_s * 0.4 + sun_s * 0.3 + moon_s * 0.3) + support_bonus * 0.2)
        growth_score       = int(((100 - abs(sun_s - moon_s)) * 0.3 + num_s * 0.4 + bazi_s * 0.3))
        collaboration_score = int((merc_s * 0.35 + bazi_s * 0.35 + num_s * 0.3))

        # Overall: not a simple average; high conflict + high growth = "高張力高成長"
        positive_avg = int((emotional_score + communication_score + attraction_score
                            + stability_score + growth_score + collaboration_score) / 6)
        conflict_penalty = max(0, (conflict_score - 60)) // 4
        overall_score = max(20, min(98, positive_avg - conflict_penalty))

        def _clamp(v: int) -> int:
            return max(0, min(100, v))

        return ScoreBreakdown(
            emotional_score=_clamp(emotional_score),
            communication_score=_clamp(communication_score),
            attraction_score=_clamp(attraction_score),
            stability_score=_clamp(stability_score),
            growth_score=_clamp(growth_score),
            conflict_score=_clamp(conflict_score),
            collaboration_score=_clamp(collaboration_score),
            overall_score=_clamp(overall_score),
        )

    # ── Synthesis ─────────────────────────────────────────────────────────────

    def _build_synthesis(
        self,
        ci: CompatibilityInput,
        astro: AstrologyCompatibility,
        bazi: BaziCompatibility,
        ziwei: ZiWeiCompatibility,
        num: NumerologyCompatibility,
        blood: BloodTypeCompatibility,
        scores: ScoreBreakdown,
    ) -> CompatibilitySynthesis:
        name_a = ci.person_a.name
        name_b = ci.person_b.name
        rt_label = relationship_label(ci.relationship_type)
        label = scores.score_label()

        summary = (
            f"{name_a} 與 {name_b} 的{rt_label}關係，綜合評估屬於「{label}」（{scores.overall_score}/100）。\n\n"
            f"在情感共鳴層面，{astro.harmony_factors[0] if astro.harmony_factors else '元素互動中性'}；"
            f"溝通方面，{bazi.day_master_relation}；"
            f"吸引力模式以金星火星配對為主要參考。"
        )

        strengths: List[str] = []
        if astro.harmony_factors:
            strengths.append("西洋占星：" + astro.harmony_factors[0])
        if bazi.supportive_elements and "建議" not in bazi.supportive_elements[0]:
            strengths.append("八字：" + bazi.supportive_elements[0])
        if ziwei.main_star_resonance and "不同" not in ziwei.main_star_resonance:
            strengths.append("紫微：" + ziwei.main_star_resonance[:40])
        if not strengths:
            strengths.append("兩人都有意識地了解彼此是最大的優勢")
        if len(strengths) < 2:
            strengths.append("不同的背景與視角讓雙方能互相帶來新的思維與刺激")
        if len(strengths) < 3:
            strengths.append("願意進行合盤分析本身，代表雙方對關係品質的重視")

        challenges: List[str] = []
        if astro.tension_factors and "暫無" not in astro.tension_factors[0]:
            challenges.append("西洋：" + astro.tension_factors[0])
        if bazi.conflicting_elements and "未偵測" not in bazi.conflicting_elements[0]:
            challenges.append("八字：" + bazi.conflicting_elements[0])
        if num.challenge_theme:
            challenges.append("靈數：" + num.challenge_theme)
        if not challenges:
            challenges.append("目前分析未偵測到重大挑戰，維持開放溝通即可")
        if len(challenges) < 2:
            challenges.append("避免假設對方的想法與感受，多用「我感受到」取代「你都」")
        if len(challenges) < 3:
            challenges.append("在重大決策前，確保雙方都有充分表達意見與底線的空間")

        emotional_pattern = (
            f"月亮配對（{astro.moon_pair.split('（')[0].strip()}）"
            f"顯示兩人情緒安全感的語言{'相近' if '共鳴' in astro.moon_pair else '有所不同'}。"
            "建議定期確認彼此的情緒需求是否被看見。"
        )

        communication_pattern = (
            f"水星配對（{astro.mercury_pair.split('（')[0].strip()}）"
            + ("顯示溝通節奏自然，容易建立共同語言。" if scores.communication_score >= 70 else
               "顯示溝通節奏有差異，建議多使用對方習慣的表達方式。")
        )

        attraction_pattern = (
            f"金星火星配對（{astro.venus_mars_pair.split('（')[0].strip()}）"
            + ("顯示吸引力自然流動。" if scores.attraction_score >= 70 else
               "顯示吸引力需要透過了解彼此深層需求來培養。")
        )

        conflict_pattern = (
            blood.conflict_style
            if blood.conflict_style and blood.conflict_style != "─" else
            "建議在衝突時給彼此冷靜的空間，再以開放態度討論核心需求。"
        )

        long_term = (
            f"長期潛力指標：穩定性{scores.stability_score}分、成長性{scores.growth_score}分。"
            + ("\n\n兩人的差異是成長的來源，衝突強度高並不代表不適合，而是代表有更多可以一起探索的空間。"
               if scores.conflict_score >= 60 else
               "\n\n穩定的元素基礎有助於建立長期安全感，維持彼此的個人空間是維繫關係的關鍵。")
        )

        practical_advice = [
            "每週安排一次「30 分鐘關係會議」：無手機，輪流分享本週一件讓你開心的事和一件讓你困擾的事。",
            blood.advice if blood.advice else "理解彼此的壓力反應模式，衝突時先照顧情緒，再解決問題。",
            "當感受到對方行為模式令你困惑時，先好奇而非評判，問「你這樣做的原因是什麼？」",
            "衝突時先暫停 20 分鐘再繼續對話，避免在情緒最高點說出無法收回的話。",
            "用「我感受到…因為我需要…」取代「你都…你從來…」，描述自己的感受而非評判對方。",
            "重大決策前，各自先寫下自己的底線與期望，再一起討論，減少誤解與假設。",
        ]

        thirty_day = [
            "**Week 1：觀察彼此觸發點** — 各自記錄本週什麼情況讓自己感到不舒服，不評論，只觀察並寫下來。",
            "**Week 2：建立溝通規則** — 約定衝突時的「暫停信號」（如舉手或說「我需要 20 分鐘」），並建立每週固定的對話時間。",
            "**Week 3：做一次共同決策** — 選一個兩人都有意見的決定，練習先完整聽完對方說法，再說自己的立場。",
            "**Week 4：回顧與調整** — 一起回顧這個月：什麼溝通方式有效？什麼需要調整？記錄下來作為關係備忘錄。",
        ]

        warning = (
            "本報告為關係理解與溝通參考，不代表絕對適合或不適合。"
            "分數與描述皆為參考性質，最終關係品質由兩人共同創造。"
            "本報告不構成科學定論、醫療診斷、法律意見或任何形式的絕對命運預測。"
            "\n\n若現實關係中存在羞辱、操控、暴力、財務控制或長期情緒勒索，"
            "請優先尋求現實支持與專業協助，建立安全界線優先於任何命盤分析。"
        )

        return CompatibilitySynthesis(
            relationship_summary=summary,
            strengths=strengths,
            challenges=challenges,
            emotional_pattern=emotional_pattern,
            communication_pattern=communication_pattern,
            attraction_pattern=attraction_pattern,
            conflict_pattern=conflict_pattern,
            long_term_potential=long_term,
            practical_advice=practical_advice,
            thirty_day_practice=thirty_day,
            warning_note=warning,
        )
