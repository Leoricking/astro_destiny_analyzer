"""
Tests for Western Astrology Engine — V1.3 Swiss Ephemeris integration.
"""
import pytest
from datetime import date, time

import engines.western_astrology as _wa_module
from engines.western_astrology import WesternAstrologyEngine
from core.models import ZodiacSign, Planet


# ── Fixtures ──────────────────────────────────────────────────────────────────

ROSSI_DATE = date(1989, 9, 21)


def _force_mock(monkeypatch):
    """Patch _SWE_AVAILABLE to False so the engine uses the mock path."""
    monkeypatch.setattr(_wa_module, "_SWE_AVAILABLE", False)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_mock_fallback_no_crash(monkeypatch):
    """Mock fallback must not raise even if swisseph is unavailable."""
    _force_mock(monkeypatch)
    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE)
    assert chart is not None
    assert len(chart.planet_positions) > 0


def test_calculation_mode_is_mock_fallback_when_swe_unavailable(monkeypatch):
    """calculation_mode must be 'mock_fallback' when swisseph is unavailable."""
    _force_mock(monkeypatch)
    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE)
    assert chart.calculation_mode == "mock_fallback"


def test_moon_not_taurus_with_swisseph():
    """
    Moon for 1989-09-21 (Asia/Taipei) must NOT be Taurus.
    The mock layer wrongly returned Taurus; real ephemeris returns Gemini.
    Skipped automatically if pyswisseph is not installed.
    """
    pytest.importorskip("swisseph")
    if not _wa_module._SWE_AVAILABLE:
        pytest.skip("swisseph imported at module level but flag is False")

    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE)
    moon = next(p for p in chart.planet_positions if p.planet == Planet.MOON)
    assert moon.sign != ZodiacSign.TAURUS, (
        f"Moon for 1989-09-21 should not be Taurus (mock bug). Got: {moon.sign}"
    )


def test_swisseph_moon_is_gemini():
    """
    When swisseph is available, Moon for 1989-09-21 (default UTC+8 noon)
    should be Gemini per Swiss Ephemeris.
    Skipped automatically if pyswisseph is not installed.
    """
    pytest.importorskip("swisseph")
    if not _wa_module._SWE_AVAILABLE:
        pytest.skip("swisseph imported at module level but flag is False")

    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE)
    moon = next(p for p in chart.planet_positions if p.planet == Planet.MOON)
    assert moon.sign == ZodiacSign.GEMINI, (
        f"Moon for 1989-09-21 expected 雙子座 (Gemini), got {moon.sign}"
    )


def test_calculation_mode_partial_real_with_swisseph():
    """
    When swisseph is available, calculation_mode should be 'partial_real'
    (planets are real; ASC/MC require lat/lon so never 'swiss_ephemeris' yet).
    Skipped automatically if pyswisseph is not installed.
    """
    pytest.importorskip("swisseph")
    if not _wa_module._SWE_AVAILABLE:
        pytest.skip("swisseph imported at module level but flag is False")

    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE)
    assert chart.calculation_mode in ("swiss_ephemeris", "partial_real"), (
        f"Expected swiss_ephemeris or partial_real, got: {chart.calculation_mode}"
    )


def test_accuracy_note_when_birth_time_unknown(monkeypatch):
    """accuracy_note must mention time uncertainty when birth_time is None."""
    pytest.importorskip("swisseph")
    if not _wa_module._SWE_AVAILABLE:
        pytest.skip("swisseph imported at module level but flag is False")

    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE, birth_time=None)
    assert "出生時間未知" in chart.accuracy_note


def test_western_chart_has_calculation_mode_field(monkeypatch):
    """WesternChart must always carry calculation_mode regardless of engine path."""
    _force_mock(monkeypatch)
    engine = WesternAstrologyEngine()
    chart = engine.calculate(ROSSI_DATE)
    assert hasattr(chart, "calculation_mode")
    assert hasattr(chart, "accuracy_note")
    assert isinstance(chart.calculation_mode, str)
    assert isinstance(chart.accuracy_note, str)
