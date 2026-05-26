"""
Astro Destiny Analyzer — Western Astrology Engine
V1.3.5: Accurate ASC/MC via swe.houses() when birth time + lat/lon are known.

Calculation modes:
  swiss_ephemeris : all planets + ASC/MC from real ephemeris (needs time + lat/lon)
  partial_real    : planets from swisseph; ASC/MC placeholder (missing time or location)
  mock_fallback   : swisseph unavailable or calculation failed entirely

ASC/MC accuracy:
  "precise" : computed with swe.houses() (requires time + lat/lon)
  "unknown" : placeholder only — do NOT display as a real result to the user
"""
import hashlib
from datetime import date, time, datetime, timedelta
from typing import Optional, List

from core.models import (
    WesternChart, PlanetPosition, HousePosition, Aspect,
    Planet, ZodiacSign, AspectType,
)
from config import (
    SWISSEPH_DATA_PATH, USE_SWISS_EPHEMERIS,
    DEFAULT_TIMEZONE_OFFSET, HOUSE_SYSTEM,
)

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
    # LILITH and PART_OF_FORTUNE: not mapped → mock
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
    """Approximate solar longitude (Jean Meeus, error ≈ ±1°). Mock layer only."""
    import math
    n = (d - date(2000, 1, 1)).days
    L = (280.460 + 0.9856474 * n) % 360
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    lam = L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)
    return lam % 360


def _planet_house_from_cusps(planet_lon: float, cusps: tuple) -> int:
    """
    Determine house number 1-12 for a planet longitude given Placidus house cusps.
    pyswisseph swe.houses() returns cusps as a 12-element tuple: cusps[0]=house1, cusps[11]=house12.
    """
    lon = planet_lon % 360
    for h in range(12):
        start = cusps[h] % 360
        end = cusps[(h + 1) % 12] % 360
        if start <= end:
            if start <= lon < end:
                return h + 1
        else:  # cusp crosses 0°/360°
            if lon >= start or lon < end:
                return h + 1
    return 1


# ── Engine ────────────────────────────────────────────────────────────────────

class WesternAstrologyEngine:
    """
    Western astrology engine.

    V1.3.5 rules:
    - ASC/MC are computed ONLY when birth_time AND lat/lon are all provided.
    - When any is missing, ASC/MC fields contain placeholder values and are
      marked ascendant_accuracy="unknown" / mc_accuracy="unknown".
    - Never show unknown ASC/MC as if they were real results.
    """

    def calculate(self, birth_date: date,
                  birth_time: Optional[time] = None,
                  birth_city: str = "",
                  birth_country: str = "",
                  birth_latitude: Optional[float] = None,
                  birth_longitude: Optional[float] = None,
                  birth_timezone_offset: Optional[float] = None) -> WesternChart:
        if _SWE_AVAILABLE and USE_SWISS_EPHEMERIS:
            try:
                return self._calculate_real(
                    birth_date, birth_time,
                    birth_latitude, birth_longitude, birth_timezone_offset,
                )
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
            ascendant=asc, descendant=desc, mc=mc, ic=ic,
            is_mock=True,
            calculation_mode="mock_fallback",
            accuracy_note="",
            ascendant_accuracy="unknown",
            mc_accuracy="unknown",
            location_source="not_provided",
            timezone_source="default_utc8",
        )

    # ── Real Layer (Swiss Ephemeris) ──────────────────────────────────────────

    def _calculate_real(self, birth_date: date,
                        birth_time: Optional[time],
                        birth_latitude: Optional[float],
                        birth_longitude: Optional[float],
                        birth_timezone_offset: Optional[float]) -> WesternChart:
        """
        Real Swiss Ephemeris calculation.
        - All 10 main planets always calculated.
        - ASC/MC only when birth_time AND lat/lon are all provided.
        """
        accuracy_notes: List[str] = []
        tz_offset = birth_timezone_offset if birth_timezone_offset is not None else DEFAULT_TIMEZONE_OFFSET
        timezone_source = "provided" if birth_timezone_offset is not None else "default_utc8"

        # Time handling
        time_is_known = birth_time is not None
        if not time_is_known:
            hour_local = 12.0
            accuracy_notes.append(
                "出生時間未知，月亮可能有些微誤差；上升、天頂與宮位不可精準計算。"
            )
        else:
            hour_local = birth_time.hour + birth_time.minute / 60.0

        # Local → UT conversion
        hour_ut = hour_local - tz_offset
        calc_date = birth_date
        if hour_ut < 0:
            calc_date = (datetime(birth_date.year, birth_date.month, birth_date.day)
                         - timedelta(days=1)).date()
            hour_ut += 24.0
        elif hour_ut >= 24:
            calc_date = (datetime(birth_date.year, birth_date.month, birth_date.day)
                         + timedelta(days=1)).date()
            hour_ut -= 24.0

        if SWISSEPH_DATA_PATH:
            swe.set_ephe_path(SWISSEPH_DATA_PATH)

        jd_ut = swe.julday(calc_date.year, calc_date.month, calc_date.day, hour_ut)
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED

        # ── Planet positions ──────────────────────────────────────────────────
        planet_positions: List[PlanetPosition] = []
        for i, planet in enumerate(_PLANETS):
            lon, retro = self._get_planet_lon(jd_ut, flags, planet, i,
                                              birth_date, birth_time)
            planet_positions.append(PlanetPosition(
                planet=planet,
                sign=_degree_to_sign(lon),
                degree=round(lon, 4),
                sign_degree=round(lon % 30, 4),
                house=1,      # updated below if lat/lon known
                retrograde=retro,
            ))

        # ── ASC/MC & houses ───────────────────────────────────────────────────
        has_location = birth_latitude is not None and birth_longitude is not None
        location_source = "provided" if has_location else "not_provided"

        if time_is_known and has_location:
            # Full calculation with swe.houses()
            try:
                cusps, ascmc = swe.houses(
                    jd_ut, birth_latitude, birth_longitude, HOUSE_SYSTEM
                )
                asc_lon = ascmc[0]
                mc_lon  = ascmc[1]

                # Assign planets to houses
                house_planets: dict[int, List[Planet]] = {i: [] for i in range(1, 13)}
                for pp in planet_positions:
                    h = _planet_house_from_cusps(pp.degree, cusps)
                    pp.house = h
                    house_planets[h].append(pp.planet)

                houses: List[HousePosition] = [
                    HousePosition(
                        house_number=i + 1,
                        sign=_degree_to_sign(cusps[i]),
                        cusp_degree=round(cusps[i], 4),
                        planets=house_planets.get(i + 1, []),
                    )
                    for i in range(12)
                ]

                asc  = _degree_to_sign(asc_lon)
                desc = _degree_to_sign((asc_lon + 180) % 360)
                mc   = _degree_to_sign(mc_lon)
                ic   = _degree_to_sign((mc_lon + 180) % 360)

                ascendant_accuracy = "precise"
                mc_accuracy = "precise"
                calculation_mode = "swiss_ephemeris"

            except Exception:
                # swe.houses() failed — fall back to placeholder ASC/MC
                asc_lon, houses, asc, desc, mc, ic = self._placeholder_houses(planet_positions)
                ascendant_accuracy = "unknown"
                mc_accuracy = "unknown"
                calculation_mode = "partial_real"
                accuracy_notes.append(
                    "宮位計算失敗，上升與天頂為佔位值，不代表真實結果。"
                )
        else:
            # Missing time or location — placeholder only
            if not time_is_known and has_location:
                accuracy_notes.append(
                    "出生地已知，但出生時間未知，上升與天頂無法精確計算。"
                )
            elif time_is_known and not has_location:
                accuracy_notes.append(
                    "主要行星已使用 Swiss Ephemeris 計算；"
                    "上升與天頂需要精確出生時間與出生地經緯度，目前不可視為精準結果。"
                )
            else:
                accuracy_notes.append(
                    "主要行星已使用 Swiss Ephemeris 計算；"
                    "上升與天頂需要精確出生時間與出生地經緯度，目前不可視為精準結果。"
                )

            _, houses, asc, desc, mc, ic = self._placeholder_houses(planet_positions)
            ascendant_accuracy = "unknown"
            mc_accuracy = "unknown"
            calculation_mode = "partial_real"

        aspects = self._compute_aspects(planet_positions[:10])

        return WesternChart(
            planet_positions=planet_positions,
            houses=houses,
            aspects=aspects,
            ascendant=asc, descendant=desc, mc=mc, ic=ic,
            is_mock=False,
            calculation_mode=calculation_mode,
            accuracy_note=" | ".join(accuracy_notes),
            ascendant_accuracy=ascendant_accuracy,
            mc_accuracy=mc_accuracy,
            location_source=location_source,
            timezone_source=timezone_source,
        )

    def _placeholder_houses(self, planet_positions: List[PlanetPosition]):
        """Generate placeholder houses based on Sun longitude. Used when ASC/MC cannot be real."""
        sun_pos = next(p for p in planet_positions if p.planet == Planet.SUN)
        asc_lon = sun_pos.degree
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
        return asc_lon, houses, asc, desc, mc, ic

    def _get_planet_lon(self, jd: float, flags: int, planet: Planet,
                        idx: int, birth_date: date,
                        birth_time: Optional[time]) -> tuple[float, bool]:
        """Return (ecliptic_longitude, is_retrograde). Falls back to mock on error."""
        swe_id = _SWE_PLANET_IDS.get(planet)

        if planet == Planet.SOUTH_NODE:
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

        # Deterministic mock fallback for this planet
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
                            planet1=p1.planet, planet2=p2.planet,
                            aspect_type=atype, orb=round(orb, 2), applying=False,
                        ))
                        break
        return aspects

    @staticmethod
    def _seed(birth_date: date, birth_time: Optional[time]) -> int:
        raw = (f"{birth_date.isoformat()}:"
               f"{birth_time.isoformat() if birth_time else 'unknown'}")
        return int(hashlib.md5(raw.encode()).hexdigest(), 16) % 10000
