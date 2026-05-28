"""
Astro Destiny Analyzer — Human Design Engine (V1.9.0 MVP)

Calculation flow:
  1. Conscious planets: birth datetime via Swiss Ephemeris
  2. Design planets: birth datetime − 88 days (MVP approximation)
  3. longitude → gate / line via I-Ching wheel
  4. Activated gates → defined channels → defined centers
  5. Type / Strategy / Authority / Profile / Incarnation Cross

Accuracy notes:
  - Design date uses birth_time − 88 days (not exact solar arc).
  - Gate wheel table is Phase 1 — external validation recommended.
  - birth_time_is_known=False → calculation_mode="partial"
"""
from __future__ import annotations

from datetime import date, time, datetime, timedelta
from typing import Optional, List, Set, Dict, Tuple

from human_design.models import (
    HumanDesignChart, HDPlanetActivation, HDGate, HDChannel, HDCenter,
)
from human_design.constants import (
    I_CHING_WHEEL_ORDER_PHASE1,
    GATE_INFO, CHANNEL_INFO, CENTER_INFO, TYPE_INFO, AUTHORITY_PRIORITY,
    PROFILE_DESCRIPTIONS,
)

# ── Optional Swiss Ephemeris import ───────────────────────────────────────────
try:
    import swisseph as _swe
    _SWE_AVAILABLE = True
except ImportError:
    _swe = None
    _SWE_AVAILABLE = False

from config import SWISSEPH_DATA_PATH, DEFAULT_TIMEZONE_OFFSET

# ── Planet mapping to Swiss Ephemeris IDs ─────────────────────────────────────
_HD_PLANETS = [
    "Sun", "Earth", "Moon", "North Node", "South Node",
    "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
    "Uranus", "Neptune", "Pluto",
]

_SWE_IDS = {
    "Sun":        0,
    "Moon":       1,
    "Mercury":    2,
    "Venus":      3,
    "Mars":       4,
    "Jupiter":    5,
    "Saturn":     6,
    "Uranus":     7,
    "Neptune":    8,
    "Pluto":      9,
    "North Node": 11,
}

_SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


# ── Gate / Line calculation ───────────────────────────────────────────────────

def longitude_to_gate_line(longitude: float) -> Tuple[int, int]:
    """
    Convert ecliptic longitude (0–360) to (gate, line).
    gate_size = 360/64 = 5.625°, line_size = 5.625/6 = 0.9375°
    """
    lon = longitude % 360.0
    gate_size = 360.0 / 64.0        # 5.625
    line_size = gate_size / 6.0     # 0.9375
    idx = int(lon / gate_size) % 64
    gate = I_CHING_WHEEL_ORDER_PHASE1[idx]
    raw_line = int((lon % gate_size) / line_size) + 1
    line = max(1, min(6, raw_line))
    return gate, line


def _longitude_to_sign(lon: float) -> str:
    return _SIGN_NAMES[int(lon % 360 / 30) % 12]


# ── Swiss Ephemeris helpers ───────────────────────────────────────────────────

def _get_julian_day(dt: datetime, tz_offset: float) -> float:
    hour_ut = dt.hour + dt.minute / 60.0 + dt.second / 3600.0 - tz_offset
    d = dt.date()
    if hour_ut < 0:
        d = (dt - timedelta(days=1)).date()
        hour_ut += 24.0
    elif hour_ut >= 24:
        d = (dt + timedelta(days=1)).date()
        hour_ut -= 24.0
    return _swe.julday(d.year, d.month, d.day, hour_ut)


def _calc_planet_longitude(jd: float, planet_name: str) -> Optional[float]:
    """Return ecliptic longitude for a planet at given Julian Day."""
    if planet_name == "Earth":
        sun_lon = _calc_planet_longitude(jd, "Sun")
        return (sun_lon + 180.0) % 360.0 if sun_lon is not None else None
    if planet_name == "South Node":
        nn_lon = _calc_planet_longitude(jd, "North Node")
        return (nn_lon + 180.0) % 360.0 if nn_lon is not None else None
    swe_id = _SWE_IDS.get(planet_name)
    if swe_id is None:
        return None
    try:
        result, _ = _swe.calc_ut(jd, swe_id, _swe.FLG_SWIEPH)
        return result[0] % 360.0
    except Exception:
        return None


def _calc_all_planets(jd: float, side: str) -> List[HDPlanetActivation]:
    activations = []
    for planet in _HD_PLANETS:
        lon = _calc_planet_longitude(jd, planet)
        if lon is None:
            continue
        gate, line = longitude_to_gate_line(lon)
        sign = _longitude_to_sign(lon)
        gate_info = GATE_INFO.get(gate, {})
        interp = gate_info.get("interpretation", "")
        activations.append(HDPlanetActivation(
            planet=planet,
            longitude=round(lon, 4),
            sign=sign,
            gate=gate,
            line=line,
            side=side,
            is_personality=(side == "conscious"),
            is_design=(side == "design"),
            interpretation=interp,
        ))
    return activations


# ── Mock layer ────────────────────────────────────────────────────────────────

def _mock_activations(birth_date: date, side: str) -> List[HDPlanetActivation]:
    """Deterministic mock when swe not available."""
    import hashlib
    seed_str = f"{birth_date.isoformat()}{side}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    activations = []
    for i, planet in enumerate(_HD_PLANETS):
        lon = ((seed * (i + 1) * 37 + i * 53) % 36000) / 100.0
        gate, line = longitude_to_gate_line(lon)
        sign = _longitude_to_sign(lon)
        gate_info = GATE_INFO.get(gate, {})
        activations.append(HDPlanetActivation(
            planet=planet,
            longitude=round(lon, 4),
            sign=sign,
            gate=gate,
            line=line,
            side=side,
            is_personality=(side == "conscious"),
            is_design=(side == "design"),
            interpretation=gate_info.get("interpretation", ""),
        ))
    return activations


# ── Channel / Center / Type logic ─────────────────────────────────────────────

def _build_activated_gates(
    conscious: List[HDPlanetActivation],
    design: List[HDPlanetActivation],
) -> Dict[int, List[str]]:
    """Return {gate_number: [source_strings]} for all activated gates."""
    gate_sources: Dict[int, List[str]] = {}
    for act in conscious:
        gate_sources.setdefault(act.gate, []).append(f"Conscious {act.planet}")
    for act in design:
        gate_sources.setdefault(act.gate, []).append(f"Design {act.planet}")
    return gate_sources


def _build_defined_channels(activated_gates: Set[int]) -> List[HDChannel]:
    defined = []
    for key, info in CHANNEL_INFO.items():
        g1, g2 = info["gates"]
        if g1 in activated_gates and g2 in activated_gates:
            c1, c2 = info["centers"]
            defined.append(HDChannel(
                channel=key,
                gates=(g1, g2),
                name=info["name"],
                centers=(c1, c2),
                circuit=info.get("circuit", ""),
                is_defined=True,
                interpretation=info.get("interpretation", ""),
            ))
    return defined


def _build_centers(
    defined_channels: List[HDChannel],
    all_activated_gates: Dict[int, List[str]],
) -> List[HDCenter]:
    center_channel_map: Dict[str, List[str]] = {c: [] for c in CENTER_INFO}
    center_gate_map: Dict[str, List[int]] = {c: [] for c in CENTER_INFO}

    for ch in defined_channels:
        for c in ch.centers:
            if c in center_channel_map:
                center_channel_map[c].append(ch.channel)

    for gate, sources in all_activated_gates.items():
        gi = GATE_INFO.get(gate)
        if gi:
            center = gi["center"]
            if center in center_gate_map:
                center_gate_map[center].append(gate)

    centers = []
    for name, info in CENTER_INFO.items():
        is_defined = len(center_channel_map[name]) > 0
        centers.append(HDCenter(
            name=name,
            is_defined=is_defined,
            defined_by_channels=center_channel_map[name],
            activated_gates=sorted(set(center_gate_map[name])),
            theme=info["theme"],
            defined_interpretation=info["defined_interpretation"],
            open_interpretation=info["open_interpretation"],
        ))
    return centers


def _has_motor_to_throat(defined_channels: List[HDChannel]) -> bool:
    """
    Check if any motor center (Sacral, Heart, Solar Plexus, Root)
    is connected to Throat via defined channels using BFS.
    """
    motors = {"Sacral", "Heart", "Solar Plexus", "Root"}
    # Build adjacency from defined channels
    graph: Dict[str, Set[str]] = {}
    for ch in defined_channels:
        c1, c2 = ch.centers
        graph.setdefault(c1, set()).add(c2)
        graph.setdefault(c2, set()).add(c1)

    # BFS from each motor to find Throat
    for motor in motors:
        if motor not in graph:
            continue
        visited: Set[str] = set()
        queue = [motor]
        while queue:
            node = queue.pop(0)
            if node == "Throat":
                return True
            if node in visited:
                continue
            visited.add(node)
            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    queue.append(neighbor)
    return False


def _determine_type(
    defined_centers: Set[str],
    defined_channels: List[HDChannel],
) -> Tuple[str, str]:
    """Return (type_name, type_name_zh)."""
    sacral_defined = "Sacral" in defined_centers
    throat_defined = "Throat" in defined_centers
    motor_to_throat = _has_motor_to_throat(defined_channels)

    if not defined_centers:
        return "Reflector", TYPE_INFO["Reflector"]["zh"]

    if sacral_defined:
        if motor_to_throat:
            return "Manifesting Generator", TYPE_INFO["Manifesting Generator"]["zh"]
        return "Generator", TYPE_INFO["Generator"]["zh"]

    # Sacral open
    if motor_to_throat:
        return "Manifestor", TYPE_INFO["Manifestor"]["zh"]

    return "Projector", TYPE_INFO["Projector"]["zh"]


def _determine_authority(type_name: str, defined_centers: Set[str]) -> str:
    if type_name == "Reflector":
        return "月亮權威 (Lunar Authority) — 等待 28 天月亮週期後再做重大決策。"
    for center, label, desc in AUTHORITY_PRIORITY:
        if center in defined_centers:
            return f"{label} — {desc}"
    return "環境權威 (Mental / Environmental Authority) — 在支持的環境中傾聽他人的聲音，以獲得清晰。"


def _determine_profile(
    conscious: List[HDPlanetActivation],
    design: List[HDPlanetActivation],
) -> str:
    c_sun = next((a for a in conscious if a.planet == "Sun"), None)
    d_sun = next((a for a in design if a.planet == "Sun"), None)
    if c_sun and d_sun:
        return f"{c_sun.line}/{d_sun.line}"
    if c_sun:
        return f"{c_sun.line}/─"
    return "─/─"


def _determine_incarnation_cross(
    conscious: List[HDPlanetActivation],
    design: List[HDPlanetActivation],
) -> str:
    c_sun = next((a for a in conscious if a.planet == "Sun"), None)
    c_earth = next((a for a in conscious if a.planet == "Earth"), None)
    d_sun = next((a for a in design if a.planet == "Sun"), None)
    d_earth = next((a for a in design if a.planet == "Earth"), None)
    parts = [
        f"意識太陽 Gate {c_sun.gate}" if c_sun else "意識太陽 ─",
        f"意識地球 Gate {c_earth.gate}" if c_earth else "意識地球 ─",
        f"設計太陽 Gate {d_sun.gate}" if d_sun else "設計太陽 ─",
        f"設計地球 Gate {d_earth.gate}" if d_earth else "設計地球 ─",
    ]
    return " / ".join(parts)


def _build_interpretation(
    type_name: str,
    authority: str,
    profile: str,
    defined_centers: List[str],
    open_centers: List[str],
    defined_channels: List[HDChannel],
) -> Tuple[str, str, List[str], List[str], List[str]]:
    """Return (decision_guidance, energy_summary, conditioning_risks, strengths, growth_advice)."""
    ti = TYPE_INFO.get(type_name, TYPE_INFO["Unknown"])
    strategy = ti.get("strategy_zh", "")
    description = ti.get("description", "")

    decision_guidance = (
        f"**{type_name}（{ti['zh']}）** — {description}\n\n"
        f"**策略**：{strategy}\n\n"
        f"**內在權威**：{authority}"
    )

    if defined_centers:
        energy_summary = (
            f"你有 {len(defined_centers)} 個已定義中心（{', '.join(defined_centers)}），"
            f"這些是你穩定、一致的能量來源，也是你對他人影響力的主要來源。"
        )
    else:
        energy_summary = "所有中心皆開放，你如同一面鏡子，反映出周遭環境的能量狀態。"

    conditioning_risks = []
    for c in open_centers:
        ci = CENTER_INFO.get(c, {})
        if ci.get("open_interpretation"):
            conditioning_risks.append(f"**{ci.get('zh', c)}**：{ci['open_interpretation']}")

    strengths = []
    for ch in defined_channels[:5]:
        strengths.append(f"通道 {ch.channel}（{ch.name}）：{ch.interpretation}")

    profile_desc = PROFILE_DESCRIPTIONS.get(profile, "")
    growth_advice = [
        f"人生角色 {profile}：{profile_desc}" if profile_desc else f"人生角色 {profile}：繼續探索屬於你的人生主題。",
        "人類圖是自我探索工具，而非絕對命運。建議以實驗心態觀察策略與權威在生活中的實際作用。",
        "出生時間需精確才能確保閘門與通道的正確性，若有疑問建議以多個出生時間比對。",
    ]

    return decision_guidance, energy_summary, conditioning_risks, strengths, growth_advice


# ── Main Engine ───────────────────────────────────────────────────────────────

class HumanDesignEngine:
    """
    V1.9.0 MVP Human Design engine.
    Uses Swiss Ephemeris when available; falls back to deterministic mock.
    """

    def calculate(self, profile) -> HumanDesignChart:
        """
        Calculate a HumanDesignChart from a BirthProfile.
        Never raises — returns partial/fallback on any error.
        """
        try:
            return self._calculate(profile)
        except Exception as exc:
            return self._fallback(profile, str(exc))

    def _calculate(self, profile) -> HumanDesignChart:
        birth_date: date = profile.birth_date
        birth_time_val: Optional[time] = profile.birth_time
        tz_offset: float = (
            profile.birth_timezone_offset
            if profile.birth_timezone_offset is not None
            else DEFAULT_TIMEZONE_OFFSET
        )
        time_is_known: bool = getattr(profile, "birth_time_is_known", False) and birth_time_val is not None

        if time_is_known:
            birth_dt = datetime(
                birth_date.year, birth_date.month, birth_date.day,
                birth_time_val.hour, birth_time_val.minute, 0,
            )
        else:
            birth_dt = datetime(birth_date.year, birth_date.month, birth_date.day, 12, 0, 0)

        design_dt = birth_dt - timedelta(days=88)

        accuracy_notes = []
        if not time_is_known:
            accuracy_notes.append(
                "出生時間未知，使用中午 12:00 作為近似值。Human Design 需要精確出生時間，"
                "Type / Authority / Centers 可能出現偏差。"
            )

        accuracy_notes.append(
            "Design planets use MVP approximation: birth time minus 88 days. "
            "Future versions may refine by exact solar arc."
        )
        accuracy_notes.append(
            "Gate wheel uses Phase 1 I-Ching order table and should be externally validated."
        )

        # ── Calculate planet activations ──────────────────────────────────────
        if _SWE_AVAILABLE:
            if SWISSEPH_DATA_PATH:
                _swe.set_ephe_path(SWISSEPH_DATA_PATH)
            try:
                jd_conscious = _get_julian_day(birth_dt, tz_offset)
                jd_design = _get_julian_day(design_dt, tz_offset)
                conscious = _calc_all_planets(jd_conscious, "conscious")
                design = _calc_all_planets(jd_design, "design")
                calc_mode = "swiss_ephemeris_phase1" if time_is_known else "partial"
            except Exception as exc:
                accuracy_notes.append(f"Swiss Ephemeris error: {exc}. Using mock fallback.")
                conscious = _mock_activations(birth_date, "conscious")
                design = _mock_activations(design_dt.date(), "design")
                calc_mode = "mock_fallback"
        else:
            conscious = _mock_activations(birth_date, "conscious")
            design = _mock_activations(design_dt.date(), "design")
            calc_mode = "mock_fallback" if time_is_known else "partial"

        # ── Build chart ───────────────────────────────────────────────────────
        gate_sources = _build_activated_gates(conscious, design)
        activated_gate_set = set(gate_sources.keys())

        # HDGate objects
        hd_gates = []
        for gate_num, sources in sorted(gate_sources.items()):
            gi = GATE_INFO.get(gate_num, {})
            sides = []
            if any("Conscious" in s for s in sources):
                sides.append("conscious")
            if any("Design" in s for s in sources):
                sides.append("design")
            hd_gates.append(HDGate(
                gate=gate_num,
                name=gi.get("name", f"Gate {gate_num}"),
                center=gi.get("center", "─"),
                theme=gi.get("theme", ""),
                activated_by=sources,
                side_sources=sides,
                interpretation=gi.get("interpretation", ""),
            ))

        defined_channels = _build_defined_channels(activated_gate_set)
        centers = _build_centers(defined_channels, gate_sources)
        defined_center_names = [c.name for c in centers if c.is_defined]
        open_center_names = [c.name for c in centers if not c.is_defined]
        defined_center_set = set(defined_center_names)

        type_name, type_name_zh = _determine_type(defined_center_set, defined_channels)
        strategy = TYPE_INFO.get(type_name, TYPE_INFO["Unknown"])["strategy"]
        authority = _determine_authority(type_name, defined_center_set)
        profile_str = _determine_profile(conscious, design)
        incarnation_cross = _determine_incarnation_cross(conscious, design)

        decision_guidance, energy_summary, conditioning_risks, strengths, growth_advice = (
            _build_interpretation(
                type_name, authority, profile_str,
                defined_center_names, open_center_names, defined_channels,
            )
        )

        return HumanDesignChart(
            calculation_mode=calc_mode,
            type_name=type_name,
            type_name_zh=type_name_zh,
            strategy=strategy,
            authority=authority,
            profile=profile_str,
            incarnation_cross=incarnation_cross,
            conscious_activations=conscious,
            design_activations=design,
            activated_gates=hd_gates,
            defined_channels=defined_channels,
            centers=centers,
            defined_centers=defined_center_names,
            open_centers=open_center_names,
            decision_guidance=decision_guidance,
            energy_summary=energy_summary,
            conditioning_risks=conditioning_risks,
            strengths=strengths,
            growth_advice=growth_advice,
            accuracy_note=" | ".join(accuracy_notes),
            design_datetime=design_dt.strftime("%Y-%m-%d %H:%M"),
            birth_datetime=birth_dt.strftime("%Y-%m-%d %H:%M"),
        )

    def _fallback(self, profile, error_msg: str) -> HumanDesignChart:
        """Return a safe empty chart on catastrophic error."""
        centers = [
            HDCenter(
                name=n,
                is_defined=False,
                theme=CENTER_INFO.get(n, {}).get("theme", ""),
                defined_interpretation=CENTER_INFO.get(n, {}).get("defined_interpretation", ""),
                open_interpretation=CENTER_INFO.get(n, {}).get("open_interpretation", ""),
            )
            for n in CENTER_INFO
        ]
        return HumanDesignChart(
            calculation_mode="mock_fallback",
            type_name="Unknown",
            type_name_zh="未知",
            strategy="─",
            authority="─",
            profile="─/─",
            incarnation_cross="─",
            centers=centers,
            defined_centers=[],
            open_centers=list(CENTER_INFO.keys()),
            accuracy_note=f"計算失敗，使用空白 fallback。原因：{error_msg}",
        )
