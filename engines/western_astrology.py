"""
Astro Destiny Analyzer — Western Astrology Engine
V1: Mock calculation layer.
TODO: Replace _calculate_real() stub with pyswisseph / ephem calls when
      SWISSEPH_DATA_PATH is configured (see config.py).
The data structures are already Swiss-Ephemeris-compatible.
"""
import hashlib
from datetime import date, time
from typing import Optional, List
from core.models import (
    WesternChart, PlanetPosition, HousePosition, Aspect,
    Planet, ZodiacSign, AspectType,
)
from config import SWISSEPH_DATA_PATH


_SIGNS = list(ZodiacSign)
_PLANETS = list(Planet)

_ASPECT_ORBS = {
    AspectType.CONJUNCTION: 8.0,
    AspectType.SEXTILE:     6.0,
    AspectType.SQUARE:      8.0,
    AspectType.TRINE:       8.0,
    AspectType.QUINCUNX:    3.0,
    AspectType.OPPOSITION:  8.0,
}

_ASPECT_DEGREES = {
    AspectType.CONJUNCTION: 0.0,
    AspectType.SEXTILE:    60.0,
    AspectType.SQUARE:     90.0,
    AspectType.TRINE:     120.0,
    AspectType.QUINCUNX:  150.0,
    AspectType.OPPOSITION:180.0,
}

# Approximate Sun sign boundaries (degree ranges in ecliptic longitude)
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
    for lo, hi, sign in _SUN_SIGN_BOUNDARIES:
        if lo <= deg < hi:
            return sign
    return ZodiacSign.PISCES


def _sun_longitude(d: date) -> float:
    """
    Approximate solar longitude using a simplified mean-longitude formula.
    Error ≈ ±1°. Suitable for mock layer only.
    TODO: Replace with pyswisseph swe_calc_ut() for sub-arcminute accuracy.
    """
    # Days since J2000.0
    jdn = (d.year, d.month, d.day)
    # Approximate algorithm (Jean Meeus, Astronomical Algorithms ch.25 low-precision)
    import math
    n = (date(*jdn) - date(2000, 1, 1)).days
    L = (280.460 + 0.9856474 * n) % 360          # mean longitude
    g = math.radians((357.528 + 0.9856003 * n) % 360)  # mean anomaly
    lam = L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)
    return lam % 360


class WesternAstrologyEngine:
    """
    Western astrology engine.
    Uses real approximate solar longitude for the Sun sign.
    All other planetary positions are seeded deterministically from the birth data
    so that the same birth data always returns the same chart (mock consistency).

    TODO (production upgrade path):
      1. pip install pyswisseph
      2. Set SWISSEPH_DATA_PATH in .env or config.py
      3. Implement _calculate_real() below using swe_calc_ut()
      4. Switch is_mock=False in the returned WesternChart
    """

    def calculate(self, birth_date: date,
                  birth_time: Optional[time] = None,
                  birth_city: str = "",
                  birth_country: str = "") -> WesternChart:
        if SWISSEPH_DATA_PATH:
            return self._calculate_real(birth_date, birth_time,
                                        birth_city, birth_country)
        return self._calculate_mock(birth_date, birth_time)

    # ── Mock Layer ────────────────────────────────────────────────────────────

    def _calculate_mock(self, birth_date: date,
                        birth_time: Optional[time]) -> WesternChart:
        seed = self._seed(birth_date, birth_time)

        # Sun uses real approximate longitude
        sun_lon = _sun_longitude(birth_date)

        planet_positions: List[PlanetPosition] = []
        for i, planet in enumerate(_PLANETS):
            if planet == Planet.SUN:
                lon = sun_lon
            else:
                # Pseudo-random but deterministic longitude seeded from birth data
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

        # Houses
        asc_lon = (sun_lon + seed * 17) % 360
        houses: List[HousePosition] = []
        house_planets: dict[int, List[Planet]] = {i: [] for i in range(1, 13)}
        for pp in planet_positions:
            house_planets[pp.house].append(pp.planet)
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

        # Aspects (major only, between first 10 planets)
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
        )

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
        raw = f"{birth_date.isoformat()}:{birth_time.isoformat() if birth_time else 'unknown'}"
        return int(hashlib.md5(raw.encode()).hexdigest(), 16) % 10000

    # ── Real Layer (stub) ─────────────────────────────────────────────────────

    def _calculate_real(self, birth_date: date,
                        birth_time: Optional[time],
                        birth_city: str,
                        birth_country: str) -> WesternChart:
        """
        TODO: Implement using pyswisseph for production accuracy.

        Example sketch:
            import swisseph as swe
            swe.set_ephe_path(SWISSEPH_DATA_PATH)
            jd = swe.julday(birth_date.year, birth_date.month, birth_date.day,
                            birth_time.hour + birth_time.minute/60 if birth_time else 12)
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
            for planet_id in PLANET_IDS:
                xx, ret = swe.calc_ut(jd, planet_id, flags)
                longitude = xx[0]
                ...
        """
        raise NotImplementedError(
            "Real Swiss Ephemeris calculation not yet implemented. "
            "Set SWISSEPH_DATA_PATH and implement _calculate_real()."
        )
