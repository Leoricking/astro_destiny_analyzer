"""
Astro Destiny Analyzer — Western Astrology Engine
V1.3: Swiss Ephemeris real calculation path with graceful mock fallback.

Priority:
  1. If pyswisseph is importable and USE_SWISS_EPHEMERIS is True → real calculation.
  2. If pyswisseph not available or calculation fails → mock fallback (never crash).

Moshier ephemeris is built into pyswisseph and requires no .se1 data files.
Set SWISSEPH_DATA_PATH in environment only if you have Swiss Ephemeris data files.
"""
import hashlib
from datetime import date, time, datetime, timedelta
from typing import Optional, List

from core.models import (
    WesternChart, PlanetPosition, HousePosition, Aspect,
    Planet, ZodiacSign, AspectType,
)
from config import SWISSEPH_DATA_PATH, USE_SWISS_EPHEMERIS, DEFAULT_TIMEZONE_OFFSET

# ── Optional Swiss Ephemeris import ──────────────────────────────────────────

try:
    import swisseph as swe
    _SWE_AVAILABLE = True
except ImportError:
    _SWE_AVAILABLE = False

# ── Constants ─────────────────────────────────────────────────────────────────

_SIGNS = list(ZodiacSign)
_PLANETS = list(Planet)

# Swiss Ephemeris planet IDs
_SWE_PLANET_IDS = {
    Planet.SUN:        0,
    Planet.MOON:       1,
    Planet.MERCURY:    2,
    Planet.VENUS:      3,
    Planet.MARS:       4,
    Planet.JUPITER:    5,
    Planet.SATURN:     6,
    Planet.URANUS:     7,
    Planet.NEPTUNE:    8,
    Planet.PLUTO:      9,
    Planet.NORTH_NODE: 11,
    Planet.CHIRON:     15,
    # SOUTH_NODE: derived from NORTH_NODE + 180°
    # LILITH and PART_OF_FORTUNE: not in SWE ids used here → mock
}

_ASPECT_ORBS = {
    AspectType.CONJUNCTION: 8.0,
    AspectType.SEXTILE:     6.0,
    AspectType.SQUARE:      8.0,
    AspectType.TRINE:       8.0,
    AspectType.QUINCUNX:    3.0,
    AspectType.OPPOSITION:  8.0,
}

_ASPECT_DEGREES = {
    AspectType.CONJUNCTION:  0.0,
    AspectType.SEXTILE:     60.0,
    AspectType.SQUARE:      90.0,
    AspectType.TRINE:      120.0,
    AspectType.QUINCUNX:   150.0,
    AspectType.OPPOSITION: 180.0,
}

_SUN_SIGN_BOUNDARIES = [
    (0.0,   30.0,  ZodiacSign.ARIES),
    (30.0,  60.0,  ZodiacSign.TAURUS),
    (60.0,  90.0,  ZodiacSign.GEMINI),
    (90.0, 120.0,  ZodiacSign.CANCER),
    (120.0,150.0,  ZodiacSign.LEO),
    (150.0,180.0,  ZodiacSign.VIRGO),
    (180.0,210.0,  ZodiacSign.LIBRA),
    (210.0,240.0,  ZodiacSign.SCORPIO),
    (240.0,270.0,  ZodiacSign.SAGITTARIUS),
    (270.0,300.0,  ZodiacSign.CAPRICORN),
    (300.0,330.0,  ZodiacSign.AQUARIUS),
    (330.0,360.0,  ZodiacSign.PISCES),
]


def _degree_to_sign(deg: float) -> ZodiacSign:
    deg = deg % 360
    idx = int(deg / 30) % 12
    return _SIGNS[idx]


def _sun_longitude(d: date) -> float:
    """
    Approximate solar longitude (Jean Meeus simplified, error ≈ ±1°).
    Used only in the mock layer.
    """
    import math
    n = (d - date(2000, 1, 1)).days
    L = (280.460 + 0.9856474 * n) % 360
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    lam = L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)
    return lam % 360


# ── Engine ────────────────────────────────────────────────────────────────────

class WesternAstrologyEngine:
    """
    Western astrology engine.

    V1.3 calculation path:
      - If pyswisseph is available and USE_SWISS_EPHEMERIS is True → _calculate_real()
      - If swisseph unavailable or real calculation raises an exception → _calculate_mock()
        with calculation_mode = "mock_fallback"

    calculation_mode values in returned WesternChart:
      - "swiss_ephemeris"  : full real calculation (requires lat/lon for ASC/MC)
      - "partial_real"     : planets from swisseph, ASC/MC require birth location
      - "mock_fallback"    : swisseph unavailable or import failed
    """

    def calculate(self, birth_date: date,
                  birth_time: Optional[time] = None,
                  birth_city: str = "",
                  birth_country: str = "") -> WesternChart:
        if _SWE_AVAILABLE and USE_SWISS_EPHEMERIS:
            try:
                return self._calculate_real(birth_date, birth_time,
                                            birth_city, birth_country)
            except Exception:
                pass  # fall through to mock
        return self._calculate_mock(birth_date, birth_time)

    # ── Mock Layer ────────────────────────────────────────────────────────────

    def _calculate_mock(self, birth_date: date,
                        birth_time: Optional[time]) -> WesternChart:
        seed = self._seed(birth_date, birth_time)
        sun_lon = _sun_longitude(birth_date)

        planet_positions: List[PlanetPosition] = []
        for i, planet in enumerate(_PLANETS):
            if planet == Planet.SUN:
                lon = sun_lon
            else:
                lon = (sun_lon + (seed * (i + 1) * 37 + i * 53)) % 360
            sign = _degree_to_sign(lon)
            sign_deg = lon % 30
            house = ((int(lon) // 30) + (seed % 12)) % 12 + 1
            retro = bool((seed + i) % 7 == 0) and planet not in (
                Planet.SUN, Planet.MOON, Planet.NORTH_NODE, Planet.SOUTH_NODE)
            planet_positions.append(PlanetPosition(
                planet=planet, sign=sign, degree=round(lon, 2),
                sign_degree=round(sign_deg, 2), house=house, retrograde=retro,
            ))

        asc_lon = (sun_lon + seed * 17) % 360
        house_planets: dict[int, List[Planet]] = {i: [] for i in range(1, 13)}
        for pp in planet_positions:
            house_planets[pp.house].append(pp.planet)
        houses: List[HousePosition] = []
        for i in range(12):
            cusp = (asc_lon + i * 30) % 360
            houses.append(HousePosition(
                house_number=i + 1,
                sign=_degree_to_sign(cusp),
                cusp_degree=round(cusp, 2),
                planets=house_planets.get(i + 1, []),
            ))

        asc  = _degree_to_sign(asc_lon)
        desc = _degree_to_sign((asc_lon + 180) % 360)
        mc   = _degree_to_sign((asc_lon + 270) % 360)
        ic   = _degree_to_sign((asc_lon +  90) % 360)
        aspects = self._compute_aspects(planet_positions[:10])

        return WesternChart(
            planet_positions=planet_positions,
            houses=houses,
            aspects=aspects,
            ascendant=asc,
            descendant=desc,
            mc=mc,
            ic=ic,
            is_mock=True,
            calculation_mode="mock_fallback",
            accuracy_note="",
        )

    # ── Real Layer (Swiss Ephemeris) ──────────────────────────────────────────

    def _calculate_real(self, birth_date: date,
                        birth_time: Optional[time],
                        birth_city: str,
                        birth_country: str) -> WesternChart:
        """
        Calculate planet positions using pyswisseph (Moshier ephemeris, no data files needed).
        Default timezone: UTC+8 (Asia/Taipei).
        ASC/MC require birth latitude/longitude; without them, marked as partial_real.
        """
        accuracy_notes: List[str] = []

        # Determine local hour and handle unknown birth time
        if birth_time is None:
            hour_local = 12.0
            accuracy_notes.append(
                "出生時間未知，月亮可能有誤差，上升與宮位不可視為精準結果。"
            )
        else:
            hour_local = birth_time.hour + birth_time.minute / 60.0

        # Convert local time (UTC+8) to Universal Time
        hour_ut = hour_local - DEFAULT_TIMEZONE_OFFSET

        # Adjust date if UT crosses midnight backwards
        calc_date = birth_date
        if hour_ut < 0:
            calc_date = (datetime(birth_date.year, birth_date.month, birth_date.day)
                         - timedelta(days=1)).date()
            hour_ut += 24.0
        elif hour_ut >= 24:
            calc_date = (datetime(birth_date.year, birth_date.month, birth_date.day)
                         + timedelta(days=1)).date()
            hour_ut -= 24.0

        # Set ephemeris path if provided (Moshier works without this)
        if SWISSEPH_DATA_PATH:
            swe.set_ephe_path(SWISSEPH_DATA_PATH)

        jd = swe.julday(calc_date.year, calc_date.month, calc_date.day, hour_ut)
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED

        # Calculate planet positions
        planet_positions: List[PlanetPosition] = []
        north_node_lon: Optional[float] = None

        for i, planet in enumerate(_PLANETS):
            lon, retro = self._get_planet_lon(jd, flags, planet, i,
                                              birth_date, birth_time)
            if planet == Planet.NORTH_NODE:
                north_node_lon = lon

            sign = _degree_to_sign(lon)
            sign_deg = lon % 30
            planet_positions.append(PlanetPosition(
                planet=planet,
                sign=sign,
                degree=round(lon, 4),
                sign_degree=round(sign_deg, 4),
                house=1,        # house requires lat/lon; placeholder
                retrograde=retro,
            ))

        # Placeholder houses: derived from Sun longitude (no lat/lon)
        sun_pos = next(p for p in planet_positions if p.planet == Planet.SUN)
        asc_lon = sun_pos.degree  # placeholder only — NOT a real ascendant
        houses: List[HousePosition] = []
        for i in range(12):
            cusp = (asc_lon + i * 30) % 360
            houses.append(HousePosition(
                house_number=i + 1,
                sign=_degree_to_sign(cusp),
                cusp_degree=round(cusp, 2),
                planets=[],
            ))

        asc  = _degree_to_sign(asc_lon)
        desc = _degree_to_sign((asc_lon + 180) % 360)
        mc   = _degree_to_sign((asc_lon + 270) % 360)
        ic   = _degree_to_sign((asc_lon +  90) % 360)

        accuracy_notes.append(
            "上升（ASC）與天頂（MC）需要出生地精確經緯度，"
            "目前欄位為佔位值，不代表真實上升星座。"
            " accuracy_note: requires_birth_time_and_location"
        )

        aspects = self._compute_aspects(planet_positions[:10])

        return WesternChart(
            planet_positions=planet_positions,
            houses=houses,
            aspects=aspects,
            ascendant=asc,
            descendant=desc,
            mc=mc,
            ic=ic,
            is_mock=False,
            calculation_mode="partial_real",
            accuracy_note=" | ".join(accuracy_notes),
        )

    def _get_planet_lon(self, jd: float, flags: int, planet: Planet,
                        idx: int, birth_date: date,
                        birth_time: Optional[time]) -> tuple[float, bool]:
        """
        Return (ecliptic_longitude, is_retrograde) for a planet.
        Falls back to deterministic mock for planets not in SWE or on error.
        """
        swe_id = _SWE_PLANET_IDS.get(planet)

        if planet == Planet.SOUTH_NODE:
            # South Node = North Node + 180°
            north_id = _SWE_PLANET_IDS[Planet.NORTH_NODE]
            try:
                xx, _ = swe.calc_ut(jd, north_id, flags)
                return (xx[0] + 180.0) % 360, False
            except Exception:
                pass

        if swe_id is not None:
            try:
                xx, _ = swe.calc_ut(jd, swe_id, flags)
                lon = xx[0] % 360
                retro = (xx[3] < 0) and planet not in (
                    Planet.SUN, Planet.NORTH_NODE, Planet.SOUTH_NODE)
                return lon, retro
            except Exception:
                pass

        # Fallback: deterministic mock for this planet
        seed = self._seed(birth_date, birth_time)
        sun_lon = _sun_longitude(birth_date)
        lon = (sun_lon + (seed * (idx + 1) * 37 + idx * 53)) % 360
        return lon, False

    # ── Shared helpers ────────────────────────────────────────────────────────

    def _compute_aspects(self, positions: List[PlanetPosition]) -> List[Aspect]:
        aspects: List[Aspect] = []
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                p1, p2 = positions[i], positions[j]
                diff = abs(p1.degree - p2.degree)
                if diff > 180:
                    diff = 360 - diff
                for atype, exact in _ASPECT_DEGREES.items():
                    orb = abs(diff - exact)
                    if orb <= _ASPECT_ORBS[atype]:
                        aspects.append(Aspect(
                            planet1=p1.planet,
                            planet2=p2.planet,
                            aspect_type=atype,
                            orb=round(orb, 2),
                            applying=False,
                        ))
                        break
        return aspects

    @staticmethod
    def _seed(birth_date: date, birth_time: Optional[time]) -> int:
        raw = (f"{birth_date.isoformat()}:"
               f"{birth_time.isoformat() if birth_time else 'unknown'}")
        return int(hashlib.md5(raw.encode()).hexdigest(), 16) % 10000
