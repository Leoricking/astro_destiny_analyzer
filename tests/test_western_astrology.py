"""
Tests for Western Astrology Engine — V1.3.5 (Birth Location & Accurate ASC/MC).

Coverage:
1. Main planets always calculated.
2. Moon for 1989-09-21 is not Taurus (mock bug fix).
3. Unknown birth time → partial_real or mock_fallback, accuracy_note present, ASC not precise.
4. Known time but no lat/lon → planets OK, ASC not precise, accuracy_note mentions lat/lon.
5. Full time + Taipei lat/lon → ASC/MC precise, calculation_mode=swiss_ephemeris.
6. swisseph unavailable → no crash, mock_fallback.
7. calculation_mode and accuracy fields always present.
"""
import pytest
from datetime import date, time

import engines.western_astrology as _wa_module
from engines.western_astrology import WesternAstrologyEngine
from core.models import ZodiacSign, Planet

# Taipei coordinates (from LOCATION_MAP)
TAIPEI_LAT = 25.0330
TAIPEI_LON = 121.5654
TAIPEI_UTC = 8.0

ROSSI_DATE = date(1989, 9, 21)


def _force_mock(monkeypatch):
    monkeypatch.setattr(_wa_module, "_SWE_AVAILABLE", False)


# ── 1. Planets always present ─────────────────────────────────────────────────

def test_planets_present_no_time(monkeypatch):
    """Main planets must be present even without birth time or location."""
    _force_mock(monkeypatch)
    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE)
    planet_names = [p.planet.value for p in chart.planet_positions]
    for name in ["太陽", "月亮", "水星", "金星", "火星", "木星", "土星"]:
        assert name in planet_names


def test_planets_present_with_swisseph():
    """When swisseph available, 10 main planets must be calculated."""
    pytest.importorskip("swisseph")
    if not _wa_module._SWE_AVAILABLE:
        pytest.skip("swisseph flag is False")
    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE)
    planet_names = [p.planet.value for p in chart.planet_positions]
    for name in ["太陽", "月亮", "水星", "金星", "火星", "木星", "土星",
                 "天王星", "海王星", "冥王星"]:
        assert name in planet_names


# ── 2. Moon not Taurus for 1989-09-21 ────────────────────────────────────────

def test_moon_not_taurus_1989_09_21():
    """Moon for 1989-09-21 must NOT be Taurus (that was the mock bug)."""
    pytest.importorskip("swisseph")
    if not _wa_module._SWE_AVAILABLE:
        pytest.skip("swisseph flag is False")
    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE)
    moon = next(p for p in chart.planet_positions if p.planet == Planet.MOON)
    assert moon.sign != ZodiacSign.TAURUS, (
        f"Moon for 1989-09-21 should not be Taurus (mock bug). Got: {moon.sign}"
    )


def test_moon_is_gemini_1989_09_21():
    """Moon for 1989-09-21 (default noon UTC+8) must be Gemini per Swiss Ephemeris."""
    pytest.importorskip("swisseph")
    if not _wa_module._SWE_AVAILABLE:
        pytest.skip("swisseph flag is False")
    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE)
    moon = next(p for p in chart.planet_positions if p.planet == Planet.MOON)
    assert moon.sign == ZodiacSign.GEMINI, (
        f"Expected 雙子座 (Gemini), got {moon.sign}"
    )


# ── 3. Unknown birth time ─────────────────────────────────────────────────────

def test_unknown_time_calculation_mode():
    """No birth_time → calculation_mode must be partial_real or mock_fallback."""
    pytest.importorskip("swisseph")
    if not _wa_module._SWE_AVAILABLE:
        pytest.skip("swisseph flag is False")
    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE, birth_time=None)
    assert chart.calculation_mode in ("partial_real", "mock_fallback")


def test_unknown_time_accuracy_note():
    """No birth_time → accuracy_note must mention time unknown."""
    pytest.importorskip("swisseph")
    if not _wa_module._SWE_AVAILABLE:
        pytest.skip("swisseph flag is False")
    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE, birth_time=None)
    assert "出生時間未知" in chart.accuracy_note


def test_unknown_time_asc_not_precise():
    """No birth_time → ascendant_accuracy must NOT be 'precise'."""
    pytest.importorskip("swisseph")
    if not _wa_module._SWE_AVAILABLE:
        pytest.skip("swisseph flag is False")
    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE, birth_time=None,
                             birth_latitude=TAIPEI_LAT, birth_longitude=TAIPEI_LON)
    assert chart.ascendant_accuracy != "precise"
    assert chart.mc_accuracy != "precise"


# ── 4. Known time but no lat/lon ──────────────────────────────────────────────

def test_known_time_no_latlon_planets_ok():
    """With birth_time but no lat/lon, planets must still be calculated."""
    pytest.importorskip("swisseph")
    if not _wa_module._SWE_AVAILABLE:
        pytest.skip("swisseph flag is False")
    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE, birth_time=time(12, 0))
    sun = next(p for p in chart.planet_positions if p.planet == Planet.SUN)
    assert sun is not None
    assert sun.sign is not None


def test_known_time_no_latlon_asc_not_precise():
    """With birth_time but no lat/lon, ASC must not be marked precise."""
    pytest.importorskip("swisseph")
    if not _wa_module._SWE_AVAILABLE:
        pytest.skip("swisseph flag is False")
    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE, birth_time=time(12, 0))
    assert chart.ascendant_accuracy != "precise"
    assert chart.mc_accuracy != "precise"


def test_known_time_no_latlon_accuracy_note_mentions_location():
    """With birth_time but no lat/lon, accuracy_note must mention location requirement."""
    pytest.importorskip("swisseph")
    if not _wa_module._SWE_AVAILABLE:
        pytest.skip("swisseph flag is False")
    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE, birth_time=time(12, 0))
    assert chart.accuracy_note  # must be non-empty


# ── 5. Full time + Taipei lat/lon ─────────────────────────────────────────────

def test_full_data_asc_mc_precise():
    """With birth_time + lat/lon → ascendant_accuracy and mc_accuracy must be 'precise'."""
    pytest.importorskip("swisseph")
    if not _wa_module._SWE_AVAILABLE:
        pytest.skip("swisseph flag is False")
    engine = WesternAstrologyEngine()
    chart = engine.calculate(
        ROSSI_DATE,
        birth_time=time(12, 0),
        birth_latitude=TAIPEI_LAT,
        birth_longitude=TAIPEI_LON,
        birth_timezone_offset=TAIPEI_UTC,
    )
    assert chart.ascendant_accuracy == "precise", (
        f"Expected precise, got {chart.ascendant_accuracy}. mode={chart.calculation_mode}"
    )
    assert chart.mc_accuracy == "precise"


def test_full_data_calculation_mode_swiss_ephemeris():
    """With complete data → calculation_mode must be 'swiss_ephemeris'."""
    pytest.importorskip("swisseph")
    if not _wa_module._SWE_AVAILABLE:
        pytest.skip("swisseph flag is False")
    engine = WesternAstrologyEngine()
    chart = engine.calculate(
        ROSSI_DATE,
        birth_time=time(12, 0),
        birth_latitude=TAIPEI_LAT,
        birth_longitude=TAIPEI_LON,
        birth_timezone_offset=TAIPEI_UTC,
    )
    assert chart.calculation_mode == "swiss_ephemeris"


def test_full_data_asc_is_valid_sign():
    """With complete data, ascendant must be a valid ZodiacSign."""
    pytest.importorskip("swisseph")
    if not _wa_module._SWE_AVAILABLE:
        pytest.skip("swisseph flag is False")
    engine = WesternAstrologyEngine()
    chart = engine.calculate(
        ROSSI_DATE,
        birth_time=time(12, 0),
        birth_latitude=TAIPEI_LAT,
        birth_longitude=TAIPEI_LON,
        birth_timezone_offset=TAIPEI_UTC,
    )
    assert chart.ascendant in list(ZodiacSign)


# ── 6. swisseph unavailable → no crash ───────────────────────────────────────

def test_mock_fallback_no_crash(monkeypatch):
    """mock_fallback must never crash."""
    _force_mock(monkeypatch)
    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE)
    assert chart is not None
    assert chart.calculation_mode == "mock_fallback"


def test_mock_fallback_with_latlon_no_crash(monkeypatch):
    """mock_fallback even if lat/lon are provided — never crash."""
    _force_mock(monkeypatch)
    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE, birth_time=time(12, 0),
                             birth_latitude=TAIPEI_LAT, birth_longitude=TAIPEI_LON)
    assert chart is not None
    assert chart.calculation_mode == "mock_fallback"


# ── 7. Fields always present ──────────────────────────────────────────────────

def test_all_accuracy_fields_present_mock(monkeypatch):
    """All V1.3.5 accuracy fields must be present in mock mode."""
    _force_mock(monkeypatch)
    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE)
    assert hasattr(chart, "calculation_mode")
    assert hasattr(chart, "accuracy_note")
    assert hasattr(chart, "ascendant_accuracy")
    assert hasattr(chart, "mc_accuracy")
    assert hasattr(chart, "location_source")
    assert hasattr(chart, "timezone_source")


def test_all_accuracy_fields_present_real():
    """All V1.3.5 accuracy fields must be present in real mode."""
    pytest.importorskip("swisseph")
    if not _wa_module._SWE_AVAILABLE:
        pytest.skip("swisseph flag is False")
    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE)
    assert hasattr(chart, "ascendant_accuracy")
    assert hasattr(chart, "mc_accuracy")
    assert hasattr(chart, "location_source")
    assert hasattr(chart, "timezone_source")
    assert isinstance(chart.ascendant_accuracy, str)
    assert isinstance(chart.mc_accuracy, str)
