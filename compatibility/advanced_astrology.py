"""
Astro Destiny Analyzer — Advanced Astrology Compatibility Engine
V1.8.0: Synastry Aspect Matrix + Composite Midpoint Chart Phase 1

Calculates:
  - Synastry aspects between two WesternCharts
  - Composite (midpoint) chart
  - Advanced compatibility sub-scores

NOT equivalent to professional astrology software. All interpretations are
relationship-understanding aids, not absolute predictions.
"""
from __future__ import annotations

from typing import Optional, List, Dict, Tuple

from core.models import WesternChart
from compatibility.models import (
    SynastryAspect, SynastryMatrix,
    CompositePlanet, CompositeChart,
    AdvancedCompatibilityScores, AdvancedAstrologyCompatibility,
)


# ── Planet name normalisation (Chinese ↔ English) ────────────────────────────

_ZH_TO_EN: Dict[str, str] = {
    "太陽": "Sun", "月亮": "Moon", "水星": "Mercury",
    "金星": "Venus", "火星": "Mars", "木星": "Jupiter",
    "土星": "Saturn", "天王星": "Uranus", "海王星": "Neptune",
    "冥王星": "Pluto",
}
_EN_TO_ZH: Dict[str, str] = {v: k for k, v in _ZH_TO_EN.items()}


def _en(name: str) -> str:
    """Normalise planet name to English."""
    return _ZH_TO_EN.get(name, name)


def _zh(name: str) -> str:
    """Normalise planet name to Chinese display."""
    return _EN_TO_ZH.get(name, name)


# ── Zodiac sign from ecliptic longitude ──────────────────────────────────────

_ZODIAC_SIGNS = [
    "牡羊座", "金牛座", "雙子座", "巨蟹座",
    "獅子座", "處女座", "天秤座", "天蠍座",
    "射手座", "摩羯座", "水瓶座", "雙魚座",
]


def _lon_to_sign(lon: float) -> str:
    """Return zodiac sign string for ecliptic longitude 0–360."""
    idx = int(lon % 360 / 30) % 12
    return _ZODIAC_SIGNS[idx]


# ── Aspect definitions and orbs ───────────────────────────────────────────────

_ASPECTS: List[Tuple[float, str, bool]] = [
    # (target_angle, aspect_type, is_harmonious_default)
    (0,   "conjunction", True),
    (60,  "sextile",     True),
    (90,  "square",      False),
    (120, "trine",       True),
    (150, "quincunx",    False),
    (180, "opposition",  False),
]

_LUMINARIES  = {"Sun", "Moon"}
_PERSONALS   = {"Sun", "Moon", "Mercury", "Venus", "Mars"}
_SOCIALS     = {"Jupiter", "Saturn"}
_OUTERS      = {"Uranus", "Neptune", "Pluto"}
_ANGLES      = {"Ascendant", "MC"}

_ASPECT_LABELS_ZH: Dict[str, str] = {
    "conjunction": "合相(0°)", "sextile": "六合(60°)",
    "square": "刑相(90°)", "trine": "三合(120°)",
    "quincunx": "補五(150°)", "opposition": "對分(180°)",
}


def _allowed_orb(planet_a: str, planet_b: str) -> float:
    """Return allowed orb in degrees for a pair of planets."""
    planets = {_en(planet_a), _en(planet_b)}
    if planets & _LUMINARIES:
        return 8.0
    if planets <= (_PERSONALS - _LUMINARIES):   # Venus/Mars/Mercury
        if {"Venus", "Mars"} & planets:
            return 7.0
        return 6.0
    if "Saturn" in planets:
        return 5.0
    if planets & (_ANGLES):
        return 5.0
    if planets & _OUTERS:
        return 4.0
    return 5.0


def _angular_diff(lon_a: float, lon_b: float) -> float:
    """Shortest angular distance between two ecliptic longitudes (0–180)."""
    diff = abs(lon_b - lon_a) % 360
    return diff if diff <= 180 else 360 - diff


def _aspect_type_orb(angle: float, orb_limit: float) -> Optional[Tuple[str, float, bool]]:
    """Return (aspect_type, actual_orb, is_harmonious) if angle is within orb, else None."""
    for target, atype, harmonious in _ASPECTS:
        orb = abs(angle - target)
        if orb <= orb_limit:
            return atype, orb, harmonious
    return None


# ── Aspect categorisation ─────────────────────────────────────────────────────

def _categorise_aspect(pa: str, pb: str, aspect_type: str) -> Tuple[str, bool, bool]:
    """
    Return (category, is_harmonious, is_challenging).
    Category: emotional / communication / attraction / stability / growth / conflict
    """
    pa_e = _en(pa)
    pb_e = _en(pb)
    pair = {pa_e, pb_e}
    hard = aspect_type in ("square", "opposition", "quincunx")
    soft = aspect_type in ("conjunction", "sextile", "trine")

    # Conflict
    if (pa_e == "Mars" and pb_e in _PERSONALS and hard) or \
       (pb_e == "Mars" and pa_e in _PERSONALS and hard) or \
       ("Saturn" in pair and {"Moon", "Venus", "Sun"} & pair and hard) or \
       ({"Mercury", "Mars"} <= pair and hard):
        return "conflict", False, True

    # Attraction
    if {"Venus", "Mars"} <= pair or \
       {"Venus", "Sun"} <= pair or \
       {"Mars", "Moon"} <= pair or \
       {"Venus", "Pluto"} <= pair:
        return "attraction", soft, hard

    # Emotional
    if "Moon" in pair and ({"Sun", "Moon", "Venus", "Saturn"} & pair):
        return "emotional", soft, hard

    # Communication
    if "Mercury" in pair and ({"Sun", "Moon", "Mercury", "Venus", "Mars"} & pair):
        return "communication", soft, hard

    # Stability
    if "Saturn" in pair and ({"Sun", "Moon", "Venus"} & pair):
        return "stability", soft, hard

    # Growth
    if pair & {"Jupiter", "Uranus", "Pluto"}:
        return "growth", not hard, False

    return "general", soft, hard


# ── Interpretation templates ──────────────────────────────────────────────────

def _build_interpretation(pa: str, pb: str, aspect_type: str, category: str,
                           is_harmonious: bool) -> str:
    """Build a concrete interpretation string for a synastry aspect."""
    pa_zh = _zh(_en(pa))
    pb_zh = _zh(_en(pb))
    aspect_zh = _ASPECT_LABELS_ZH.get(aspect_type, aspect_type)
    tone = "和諧" if is_harmonious else "緊張"

    _templates: Dict[str, Dict[bool, str]] = {
        "attraction": {
            True:  f"{pa_zh}（A）與{pb_zh}（B）形成{aspect_zh}，一方的愛情語言與另一方的行動欲望容易互相點燃，吸引力自然流動。",
            False: f"{pa_zh}（A）與{pb_zh}（B）形成{aspect_zh}，兩人吸引力強烈但張力明顯，容易在慾望與節奏上出現拉鋸。",
        },
        "emotional": {
            True:  f"{pa_zh}（A）與{pb_zh}（B）形成{aspect_zh}，情感頻率接近，一方能直覺感受另一方需求，情緒連結深。",
            False: f"{pa_zh}（A）與{pb_zh}（B）形成{aspect_zh}，容易出現一方需要情緒照顧，另一方卻以責任或規範回應的模式。",
        },
        "communication": {
            True:  f"{pa_zh}（A）與{pb_zh}（B）形成{aspect_zh}，思維模式互補，溝通順暢，想法容易互相理解與激發。",
            False: f"{pa_zh}（A）與{pb_zh}（B）形成{aspect_zh}，溝通風格差異明顯，需要刻意放慢節奏、確認理解才能避免誤會。",
        },
        "stability": {
            True:  f"{pa_zh}（A）與{pb_zh}（B）形成{aspect_zh}，結構感強，雙方在責任與承諾上方向一致，關係有穩定的骨架。",
            False: f"{pa_zh}（A）與{pb_zh}（B）形成{aspect_zh}，一方的嚴肅或限制感可能令另一方感到壓抑，需協商彼此對責任的定義。",
        },
        "growth": {
            True:  f"{pa_zh}（A）與{pb_zh}（B）形成{aspect_zh}，關係帶來擴張與成長，彼此激勵對方突破原有框架。",
            False: f"{pa_zh}（A）與{pb_zh}（B）形成{aspect_zh}，關係帶來強烈的變革壓力，成長是真實的但過程可能劇烈。",
        },
        "conflict": {
            True:  f"{pa_zh}（A）與{pb_zh}（B）有共鳴，但在邊界與主導權上需要明確協商。",
            False: f"{pa_zh}（A）與{pb_zh}（B）形成{aspect_zh}，衝突模式明顯，需建立清楚的溝通與修復流程，避免負面循環。",
        },
        "general": {
            True:  f"{pa_zh}（A）與{pb_zh}（B）形成{aspect_zh}，互動整體和諧，彼此有自然的協同感。",
            False: f"{pa_zh}（A）與{pb_zh}（B）形成{aspect_zh}，互動存在張力，需要更多耐心與理解才能找到共同頻率。",
        },
    }
    cat_templates = _templates.get(category, _templates["general"])
    return cat_templates.get(is_harmonious, "")


# ── Composite planet interpretations ─────────────────────────────────────────

_COMPOSITE_SUN_INTERP: Dict[str, str] = {
    "牡羊座": "關係的核心驅動力是行動與開拓，兩人在一起時會互相激發出勇氣與主動性。",
    "金牛座": "關係以穩定、感官享受與長期積累為核心，重視物質安全與相互滋養。",
    "雙子座": "關係以交流、好奇與多元探索為核心，互動靈活但需避免表面化。",
    "巨蟹座": "關係以情感聯繫、家庭感與相互照顧為核心，兩人共同創造歸屬感。",
    "獅子座": "關係以創意、熱情與共同展現為核心，彼此激勵對方成為更好的自己。",
    "處女座": "關係以實際支持、細節照料與持續改善為核心，注重品質與服務。",
    "天秤座": "關係以平衡、美感與公平為核心，兩人共同追求和諧的互動節奏。",
    "天蠍座": "關係以深度、轉化與情感強度為核心，觸及彼此最核心的脆弱與力量。",
    "射手座": "關係以自由、哲思與共同冒險為核心，兩人激勵彼此拓展眼界。",
    "摩羯座": "關係以目標、責任與長期共建為核心，有穩定結構但需保留情感空間。",
    "水瓶座": "關係以創新、友誼與共同理念為核心，兩人以平等姿態共同探索未知。",
    "雙魚座": "關係以共情、靈性與無條件理解為核心，彼此在精神層面高度融合。",
}

_COMPOSITE_MOON_CLIMATE: Dict[str, str] = {
    "牡羊座": "情緒氣候活躍直接，需求表達快速，容易因衝動而起爭執但也修復迅速。",
    "金牛座": "情緒氣候穩定平和，兩人共同追求安全感與舒適感，情感節奏緩慢但持久。",
    "雙子座": "情緒氣候輕盈多變，需要語言表達與溝通作為情感聯繫的主要橋樑。",
    "巨蟹座": "情緒氣候溫柔而敏感，彼此高度在意對方感受，有強烈的歸屬需求。",
    "獅子座": "情緒氣候溫暖熱情，需要被欣賞與認可，正向肯定是情感維繫的關鍵。",
    "處女座": "情緒氣候謹慎細心，傾向用實際行動表達關愛，需避免過度批評。",
    "天秤座": "情緒氣候注重和諧與公平，容易迴避衝突，需練習直接表達需求。",
    "天蠍座": "情緒氣候深沉強烈，忠誠與掌控感並存，需建立信任才能安心展露脆弱。",
    "射手座": "情緒氣候開放樂觀，需要個人空間與自由，情感聯繫以精神共鳴為主。",
    "摩羯座": "情緒氣候嚴肅保守，情感表達較為內斂，安全感來自於穩定的承諾結構。",
    "水瓶座": "情緒氣候理性獨立，偏好以友誼形式維繫情感，需平衡距離感與親密感。",
    "雙魚座": "情緒氣候溫柔夢幻，兩人容易情緒融合，需保持個人界線避免過度依賴。",
}


def _composite_venus_style(sign: str) -> str:
    fire = {"牡羊座", "獅子座", "射手座"}
    earth = {"金牛座", "處女座", "摩羯座"}
    air = {"雙子座", "天秤座", "水瓶座"}
    water = {"巨蟹座", "天蠍座", "雙魚座"}
    if sign in fire:
        return f"關係中的愛以熱情、主動的方式表達（{sign}），重視激情與共同行動。"
    if sign in earth:
        return f"關係中的愛以實際、滋養的方式表達（{sign}），重視穩定的物質與感官連結。"
    if sign in air:
        return f"關係中的愛以交流、思想的方式表達（{sign}），重視精神契合與社交共鳴。"
    if sign in water:
        return f"關係中的愛以情感、直覺的方式表達（{sign}），重視深度情緒連結與共情。"
    return f"愛的表達方式受{sign}影響，帶有獨特的色彩。"


def _composite_mars_conflict(sign: str) -> str:
    fire = {"牡羊座", "獅子座", "射手座"}
    earth = {"金牛座", "處女座", "摩羯座"}
    air = {"雙子座", "天秤座", "水瓶座"}
    water = {"巨蟹座", "天蠍座", "雙魚座"}
    if sign in fire:
        return f"衝突模式以直接、快速的方式呈現（{sign}），情緒來得快去得也快，需避免言語傷害。"
    if sign in earth:
        return f"衝突模式以固執、拖延的方式呈現（{sign}），雙方容易各持己見，需要耐心拆解分歧。"
    if sign in air:
        return f"衝突模式以辯論、理智化的方式呈現（{sign}），容易陷入言辭拉鋸，需回到感受層面溝通。"
    if sign in water:
        return f"衝突模式以情緒、沉默的方式呈現（{sign}），不滿容易積累，需創造安全表達的空間。"
    return f"衝突模式受{sign}影響，需雙方共同探索有效的修復流程。"


# ── Synastry calculation ──────────────────────────────────────────────────────

def _calculate_synastry_aspects(chart_a: WesternChart, chart_b: WesternChart) -> SynastryMatrix:
    """Build SynastryMatrix from two WesternCharts."""
    if not chart_a.planet_positions or not chart_b.planet_positions:
        return SynastryMatrix(
            accuracy_note="一方或雙方星盤缺少行星經度資料，無法計算相位矩陣。"
        )

    # Build {english_name: longitude} maps
    def _pos_map(chart: WesternChart) -> Dict[str, float]:
        result: Dict[str, float] = {}
        for pp in chart.planet_positions:
            en_name = _en(getattr(getattr(pp, "planet", None), "value", "") or "")
            deg = getattr(pp, "degree", None)
            if en_name and deg is not None:
                result[en_name] = float(deg)
        return result

    pos_a = _pos_map(chart_a)
    pos_b = _pos_map(chart_b)

    core_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    extended = ["Uranus", "Neptune", "Pluto"]

    all_aspects: List[SynastryAspect] = []

    for pa in core_planets + extended:
        if pa not in pos_a:
            continue
        lon_a = pos_a[pa]
        for pb in core_planets + extended:
            if pb == pa and pa in core_planets and pb in core_planets:
                pass  # allow same-planet cross-person aspects
            if pb not in pos_b:
                continue
            lon_b = pos_b[pb]
            angle = _angular_diff(lon_a, lon_b)
            orb_limit = _allowed_orb(pa, pb)
            result = _aspect_type_orb(angle, orb_limit)
            if result is None:
                continue
            aspect_type, actual_orb, _ = result
            strength = max(0, int(100 - actual_orb / orb_limit * 100))
            # Planet importance weighting
            if pa in _LUMINARIES or pb in _LUMINARIES:
                strength = min(100, int(strength * 1.1))
            elif pa in _OUTERS or pb in _OUTERS:
                strength = max(0, int(strength * 0.8))
            category, is_harmonious, is_challenging = _categorise_aspect(pa, pb, aspect_type)
            interp = _build_interpretation(pa, pb, aspect_type, category, is_harmonious)
            all_aspects.append(SynastryAspect(
                person_a_planet=_zh(pa),
                person_b_planet=_zh(pb),
                aspect_type=aspect_type,
                angle=round(angle, 2),
                orb=round(actual_orb, 2),
                strength=strength,
                category=category,
                interpretation=interp,
                is_harmonious=is_harmonious,
                is_challenging=is_challenging,
            ))

    all_aspects.sort(key=lambda x: -x.strength)
    strongest = all_aspects[:8]
    harmony = [a for a in all_aspects if a.is_harmonious]
    tension = [a for a in all_aspects if a.is_challenging]
    emotional = [a for a in all_aspects if a.category == "emotional"]
    attraction = [a for a in all_aspects if a.category == "attraction"]
    communication = [a for a in all_aspects if a.category == "communication"]
    stability = [a for a in all_aspects if a.category == "stability"]

    accuracy = (
        "相位計算基於本系統 Phase 1 行星黃道經度（近似值），"
        "非天文星曆精確計算。orb 採用傳統合盤標準；"
        "外行星相位作為背景因素，不納入主要分數計算。"
    )

    return SynastryMatrix(
        aspects=all_aspects,
        strongest_aspects=strongest,
        harmony_aspects=harmony,
        tension_aspects=tension,
        emotional_aspects=emotional,
        attraction_aspects=attraction,
        communication_aspects=communication,
        stability_aspects=stability,
        accuracy_note=accuracy,
    )


# ── Composite midpoint chart ──────────────────────────────────────────────────

def _midpoint_longitude(lon_a: float, lon_b: float) -> float:
    """Compute midpoint handling 0°/360° wrap-around."""
    diff = (lon_b - lon_a + 540.0) % 360.0 - 180.0
    return (lon_a + diff / 2.0) % 360.0


def _calculate_composite_chart(chart_a: WesternChart, chart_b: WesternChart) -> CompositeChart:
    """Compute composite (midpoint) chart from two WesternCharts."""
    if not chart_a.planet_positions or not chart_b.planet_positions:
        return CompositeChart(
            accuracy_note="一方或雙方星盤缺少行星位置資料，無法計算中點盤。"
        )

    def _pos_map(chart: WesternChart) -> Dict[str, float]:
        result: Dict[str, float] = {}
        for pp in chart.planet_positions:
            en_name = _en(getattr(getattr(pp, "planet", None), "value", "") or "")
            deg = getattr(pp, "degree", None)
            if en_name and deg is not None:
                result[en_name] = float(deg)
        return result

    pos_a = _pos_map(chart_a)
    pos_b = _pos_map(chart_b)

    planets_order = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
                     "Uranus", "Neptune", "Pluto"]
    composite_planets: List[CompositePlanet] = []

    for planet_en in planets_order:
        if planet_en not in pos_a or planet_en not in pos_b:
            continue
        mid_lon = _midpoint_longitude(pos_a[planet_en], pos_b[planet_en])
        sign = _lon_to_sign(mid_lon)
        interp = ""
        if planet_en == "Sun":
            interp = _COMPOSITE_SUN_INTERP.get(sign, f"關係核心受{sign}影響。")
        elif planet_en == "Moon":
            interp = _COMPOSITE_MOON_CLIMATE.get(sign, f"情緒氣候受{sign}影響。")
        elif planet_en == "Venus":
            interp = _composite_venus_style(sign)
        elif planet_en == "Mars":
            interp = _composite_mars_conflict(sign)
        elif planet_en == "Saturn":
            interp = f"關係的責任結構與承諾感受{sign}影響，是雙方共同需要面對的長期課題。"
        composite_planets.append(CompositePlanet(
            planet=_zh(planet_en),
            sign=sign,
            longitude=round(mid_lon, 2),
            interpretation=interp,
        ))

    sun_sign = next((p.sign for p in composite_planets if p.planet == "太陽"), "")
    moon_sign = next((p.sign for p in composite_planets if p.planet == "月亮"), "")
    venus_sign = next((p.sign for p in composite_planets if p.planet == "金星"), "")
    mars_sign = next((p.sign for p in composite_planets if p.planet == "火星"), "")

    # ASC/MC: only if both charts have precise ascendant
    asc_a = None
    asc_b = None
    if (getattr(chart_a, "ascendant_accuracy", "") == "precise" and
            getattr(chart_b, "ascendant_accuracy", "") == "precise"):
        a_asc_deg = getattr(chart_a, "ascendant_longitude", None)
        b_asc_deg = getattr(chart_b, "ascendant_longitude", None)
        if a_asc_deg is not None and b_asc_deg is not None:
            asc_a = _lon_to_sign(_midpoint_longitude(float(a_asc_deg), float(b_asc_deg)))
            asc_b = None  # MC skipped at Phase 1 without dual precise MC

    relationship_theme = _COMPOSITE_SUN_INTERP.get(sun_sign, "關係核心主題待深入探索。")
    emotional_climate = _COMPOSITE_MOON_CLIMATE.get(moon_sign, "情緒氣候需透過互動持續了解。")
    attraction_style = _composite_venus_style(venus_sign) if venus_sign else "吸引力風格待資料補全。"
    conflict_style = _composite_mars_conflict(mars_sign) if mars_sign else "衝突模式待資料補全。"

    accuracy_note = (
        "Composite Chart 使用中點公式（Phase 1），基於本系統行星黃道近似值。"
        "Composite ASC/MC 需要雙方精確出生時間與地點，"
        + ("本次已計算 Composite ASC。" if asc_a else "本次資料不足，Composite ASC/MC 不予計算。")
    )

    return CompositeChart(
        calculation_mode="midpoint_phase1",
        planets=composite_planets,
        sun_sign=sun_sign,
        moon_sign=moon_sign,
        venus_sign=venus_sign,
        mars_sign=mars_sign,
        ascendant_sign=asc_a,
        mc_sign=None,
        relationship_theme=relationship_theme,
        emotional_climate=emotional_climate,
        attraction_style=attraction_style,
        conflict_style=conflict_style,
        accuracy_note=accuracy_note,
    )


# ── Advanced compatibility scores ─────────────────────────────────────────────

def _clamp(v: int) -> int:
    return max(0, min(100, v))


def _calculate_advanced_scores(
    synastry: SynastryMatrix, composite: CompositeChart
) -> AdvancedCompatibilityScores:
    """Compute advanced sub-scores from synastry matrix and composite chart."""

    # A. emotional_bond
    emo = 50
    for a in synastry.emotional_aspects:
        if a.is_harmonious:
            emo += min(20, int(a.strength * 0.25))
        elif a.is_challenging:
            emo -= min(15, int(a.strength * 0.20))
    # composite Moon quality bonus
    warm_moon = {"巨蟹座", "雙魚座", "天蠍座", "金牛座", "獅子座"}
    if composite.moon_sign in warm_moon:
        emo += 6
    emotional_bond = _clamp(emo)

    # B. communication_flow
    comm = 50
    for a in synastry.communication_aspects:
        if a.is_harmonious:
            comm += min(20, int(a.strength * 0.25))
    # Mercury-Mars / Mercury-Saturn hard aspects
    for a in synastry.aspects:
        pa_set = {a.person_a_planet, a.person_b_planet}
        if a.is_challenging:
            if {"水星", "火星"} <= pa_set:
                comm -= min(12, int(a.strength * 0.15))
            if {"水星", "土星"} <= pa_set:
                comm -= min(10, int(a.strength * 0.12))
    communication_flow = _clamp(comm)

    # C. attraction_chemistry
    attr = 50
    for a in synastry.attraction_aspects:
        if a.is_harmonious:
            attr += min(25, int(a.strength * 0.30))
        elif a.is_challenging:
            attr += min(10, int(a.strength * 0.12))  # tension also creates chemistry
    # Venus/Pluto bonus
    for a in synastry.aspects:
        if {"金星", "冥王星"} <= {a.person_a_planet, a.person_b_planet}:
            attr += min(10, int(a.strength * 0.12))
    # composite Venus
    vibrant_venus = {"牡羊座", "獅子座", "天蠍座", "金牛座"}
    if composite.venus_sign in vibrant_venus:
        attr += 6
    attraction_chemistry = _clamp(attr)

    # D. stability_potential
    stab = 50
    for a in synastry.stability_aspects:
        if a.is_harmonious:
            stab += min(18, int(a.strength * 0.22))
        elif a.is_challenging:
            stab += min(5, int(a.strength * 0.06))   # hard Saturn = pressure but also commitment
            stab -= min(8, int(a.strength * 0.10))
    # Earth/fixed sign composite sun bonus
    earth_fixed = {"金牛座", "獅子座", "天蠍座", "水瓶座", "處女座", "摩羯座"}
    if composite.sun_sign in earth_fixed:
        stab += 5
    stability_potential = _clamp(stab)

    # E. growth_intensity
    growth = 50
    for a in synastry.aspects:
        if a.category == "growth":
            growth += min(20, int(a.strength * 0.20))
    growth_intensity = _clamp(growth)

    # F. conflict_intensity (tension gauge, not bad score)
    conflict = 50
    for a in synastry.aspects:
        if a.category == "conflict":
            conflict += min(30, int(a.strength * 0.30))
    conflict_intensity = _clamp(conflict)

    # G. long_term_potential
    long_term = int(
        stability_potential * 0.35
        + emotional_bond * 0.25
        + communication_flow * 0.20
        + (100 - max(0, conflict_intensity - 70)) * 0.10
        + attraction_chemistry * 0.10
    )
    # If attraction is way higher than stability, slight penalty
    if attraction_chemistry > stability_potential + 25:
        long_term = max(0, long_term - 5)
    long_term_potential = _clamp(long_term)

    # H. overall_advanced_score (weighted, not a simple average)
    raw = (
        emotional_bond * 0.22
        + communication_flow * 0.18
        + attraction_chemistry * 0.16
        + stability_potential * 0.20
        + long_term_potential * 0.16
        + growth_intensity * 0.08
        - max(0, conflict_intensity - 70) * 0.10
    )
    overall = _clamp(int(raw))

    # Label
    if overall >= 85:
        label = "高度共鳴但仍需經營"
    elif overall >= 75:
        label = "互補良好"
    elif overall >= 60:
        label = "有潛力但需溝通設計"
    elif overall >= 45:
        label = "張力明顯，需成熟互動"
    else:
        label = "高壓關係，需要清楚界線"

    explanation = (
        "此分數是互動模式的綜合參考，不是絕對適合度。"
        "衝突分數高不等於不適合，代表關係張力強，需要設計溝通與修復流程。"
        "長期關係的品質最終取決於兩人的現實選擇、溝通能力與共同成長意願。"
    )

    return AdvancedCompatibilityScores(
        emotional_bond=emotional_bond,
        communication_flow=communication_flow,
        attraction_chemistry=attraction_chemistry,
        stability_potential=stability_potential,
        growth_intensity=growth_intensity,
        conflict_intensity=conflict_intensity,
        long_term_potential=long_term_potential,
        overall_advanced_score=overall,
        label=label,
        explanation=explanation,
    )


# ── Summary / strengths / challenges / repair ─────────────────────────────────

def _build_advanced_summary(
    synastry: SynastryMatrix,
    composite: CompositeChart,
    scores: AdvancedCompatibilityScores,
) -> Tuple[str, List[str], List[str], List[str]]:
    strengths: List[str] = []
    challenges: List[str] = []
    repair_advice: List[str] = []

    if scores.emotional_bond >= 65:
        strengths.append("情緒連結深厚，雙方在情感層面有自然的共鳴與理解。")
    if scores.communication_flow >= 65:
        strengths.append("溝通流暢，思維模式互補，想法容易互相理解與激發。")
    if scores.attraction_chemistry >= 65:
        strengths.append("吸引力與化學反應強，關係有自然流動的魅力張力。")
    if scores.stability_potential >= 65:
        strengths.append("穩定結構良好，雙方在責任與承諾方向上具有共識。")
    if scores.growth_intensity >= 65:
        strengths.append("成長張力高，關係激勵雙方突破原有框架，共同進化。")

    if scores.emotional_bond < 45:
        challenges.append("情緒頻率差異明顯，需要建立主動表達感受的習慣。")
    if scores.communication_flow < 45:
        challenges.append("溝通風格落差大，需放慢節奏、確認理解後再回應。")
    if scores.conflict_intensity >= 70:
        challenges.append("衝突張力高，需建立清楚的修復流程，避免負面循環。")
    if scores.stability_potential < 45:
        challenges.append("穩定感不足，需要在日常生活中刻意建立可預測的互動結構。")

    # Add top synastry aspect info
    if synastry.strongest_aspects:
        top = synastry.strongest_aspects[0]
        strengths.append(f"最強相位：{top.person_a_planet}（A）⟷ {top.person_b_planet}（B）{_ASPECT_LABELS_ZH.get(top.aspect_type, top.aspect_type)}，{top.interpretation[:30]}…")

    # Repair advice based on challenges
    if scores.communication_flow < 55:
        repair_advice.append("每週設定 15 分鐘的「無評判聆聽」練習，輪流分享感受，不打斷、不建議。")
    if scores.conflict_intensity >= 65:
        repair_advice.append("建立衝突後的 24 小時冷靜協議：雙方各自沉澱後，再回到話題以「我感受到…」開頭表達。")
    if scores.emotional_bond < 55:
        repair_advice.append("每天進行 2 分鐘的情感確認：詢問「今天你最需要什麼？」並認真回應。")
    if scores.stability_potential < 55:
        repair_advice.append("共同建立每週一次的「關係 Check-in」：檢視各自需求是否被滿足，並調整互動節奏。")
    if not repair_advice:
        repair_advice.append("持續投入關係的日常滋養：小而持續的正向互動，比偶爾的大型補救更有效。")
        repair_advice.append("定期回顧兩人的共同目標與價值觀，確保關係在成長中保持方向一致。")

    summary = (
        f"Synastry 相位矩陣共偵測到 {len(synastry.aspects)} 個有效相位，"
        f"其中和諧相位 {len(synastry.harmony_aspects)} 個、張力相位 {len(synastry.tension_aspects)} 個。"
        f"Composite Chart 太陽落{composite.sun_sign}，月亮落{composite.moon_sign}，"
        f"顯示關係的核心場域與情緒氣候。"
        f"進階合盤總分 {scores.overall_advanced_score}，標籤：{scores.label}。"
    )
    return summary, strengths, challenges, repair_advice


# ── Display helpers (V1.8.1) ─────────────────────────────────────────────────

_ASPECT_TYPE_ZH: Dict[str, str] = {
    "conjunction": "合相",
    "sextile": "六合",
    "square": "四分相",
    "trine": "三分相",
    "quincunx": "梅花相",
    "opposition": "對分相",
}

_CATEGORY_ZH: Dict[str, str] = {
    "emotional": "情緒連結",
    "communication": "溝通理解",
    "attraction": "吸引力",
    "stability": "穩定責任",
    "growth": "成長推進",
    "conflict": "衝突張力",
    "general": "一般",
}

# Key UI text constants (used by templates, UI, and tests)
CONFLICT_CAPTION = "衝突張力高不等於不適合，而是代表需要明確修復流程。"
COMPOSITE_INTRO = (
    "Composite Chart 是兩人星盤的中點盤，用來觀察關係本身形成的共同場域；"
    "它不是任何一方個人命盤，也不是絕對結局。"
)
ADVANCED_SCORE_DISCLAIMER = (
    "進階合盤分數不是絕對適合度，不代表一定在一起或一定分開。"
    "它是兩人互動模式的結構化參考。"
)
SYNASTRY_INTRO = (
    "Synastry（星盤疊合）分析兩人行星之間的角度關係（相位），"
    "用於了解兩人互動的能量模式。相位不代表命運，而是提供理解互動風格的結構化框架。"
)


def aspect_type_zh(aspect_type: str) -> str:
    """Return Chinese display name for an aspect type."""
    return _ASPECT_TYPE_ZH.get(aspect_type, aspect_type)


def category_zh(category: str) -> str:
    """Return Chinese display name for an aspect category."""
    return _CATEGORY_ZH.get(category, category)


def aspect_nature(aspect: "SynastryAspect") -> str:
    """Return nature string: 和諧 / 張力 / 混合."""
    if aspect.is_harmonious and not aspect.is_challenging:
        return "和諧"
    if aspect.is_challenging and not aspect.is_harmonious:
        return "張力"
    return "混合"


def format_orb(orb: float) -> str:
    """Return formatted orb string, e.g. '2.3°'."""
    return f"{orb:.1f}°"


def aspect_to_display_dict(aspect: "SynastryAspect") -> Dict[str, str]:
    """Return a display dict with Chinese column names for UI/report use."""
    return {
        "A 行星": aspect.person_a_planet,
        "B 行星": aspect.person_b_planet,
        "相位": aspect_type_zh(aspect.aspect_type),
        "容許度 orb": format_orb(aspect.orb),
        "強度": str(aspect.strength),
        "分類": category_zh(aspect.category),
        "性質": aspect_nature(aspect),
        "解讀": aspect.interpretation,
    }


# ── Main engine ───────────────────────────────────────────────────────────────

class AdvancedAstrologyEngine:
    """
    Phase 1 Advanced Synastry + Composite Chart engine.

    Requires WesternChart with planet_positions (including degree).
    Falls back gracefully to sign-element analysis when longitudes are absent.
    """

    def calculate(
        self,
        chart_a: WesternChart,
        chart_b: WesternChart,
    ) -> AdvancedAstrologyCompatibility:
        """Return AdvancedAstrologyCompatibility from two WesternCharts."""

        has_degrees = (
            bool(chart_a.planet_positions) and bool(chart_b.planet_positions)
        )

        if has_degrees:
            synastry = _calculate_synastry_aspects(chart_a, chart_b)
            composite = _calculate_composite_chart(chart_a, chart_b)
        else:
            synastry = SynastryMatrix(
                accuracy_note="行星經度資料不足，相位矩陣使用元素配對 fallback。"
            )
            composite = CompositeChart(
                accuracy_note="行星經度資料不足，中點盤計算需要雙方完整行星位置。"
            )

        scores = _calculate_advanced_scores(synastry, composite)
        summary, strengths, challenges, repair_advice = _build_advanced_summary(
            synastry, composite, scores
        )

        accuracy_note = (
            "進階西洋合盤基於 Phase 1 行星黃道近似值，非天文星曆精確計算。"
            "Synastry 與 Composite Chart 是關係理解工具，不代表絕對適合度或婚姻保證。"
        )

        return AdvancedAstrologyCompatibility(
            synastry_matrix=synastry,
            composite_chart=composite,
            advanced_scores=scores,
            summary=summary,
            strengths=strengths,
            challenges=challenges,
            repair_advice=repair_advice,
            accuracy_note=accuracy_note,
        )
