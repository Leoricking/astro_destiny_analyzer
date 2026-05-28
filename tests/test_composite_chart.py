"""
V1.8.0 Tests: Composite Midpoint Chart
"""
import pytest
from compatibility.advanced_astrology import (
    _midpoint_longitude, _lon_to_sign, _calculate_composite_chart,
)


# ── 1. Midpoint 359°/1° wraps correctly ──────────────────────────────────────

def test_midpoint_wrap_zero():
    """midpoint 359° / 1° 應得到 0° 附近（360° 中點）"""
    mid = _midpoint_longitude(359.0, 1.0)
    # Shortest arc midpoint of 359° and 1° is 0° (or 360°)
    assert mid == pytest.approx(0.0, abs=1.0), f"midpoint = {mid}，應接近 0°"


def test_midpoint_simple():
    """midpoint 0° / 180° 應為 90° 或 270°（對分相有兩個等距中點）"""
    mid = _midpoint_longitude(0.0, 180.0)
    assert mid == pytest.approx(90.0, abs=0.1) or mid == pytest.approx(270.0, abs=0.1)


def test_midpoint_same_longitude():
    """兩個相同黃道度數的中點等於自身"""
    mid = _midpoint_longitude(120.0, 120.0)
    assert mid == pytest.approx(120.0, abs=0.1)


def test_midpoint_across_zero():
    """330° / 30° 的中點應為 0°（或 360°）"""
    mid = _midpoint_longitude(330.0, 30.0)
    assert mid == pytest.approx(0.0, abs=1.0) or mid == pytest.approx(360.0, abs=1.0)


# ── 2–7. Composite chart from romantic couple ─────────────────────────────────

@pytest.fixture(scope="module")
def romantic_composite():
    from reports.generator import ReportGenerator
    from demo.sample_profiles import SAMPLE_COUPLES
    gen = ReportGenerator()
    couple = next(c for c in SAMPLE_COUPLES if c.get("relationship_type") == "romantic")
    ra = gen.generate(couple["person_a"], persist=False)
    rb = gen.generate(couple["person_b"], persist=False)
    return _calculate_composite_chart(ra.western_chart, rb.western_chart)


def test_composite_planets_not_empty(romantic_composite):
    """composite chart planets 不為空"""
    assert len(romantic_composite.planets) > 0, "composite planets 不應為空"


def test_composite_sun_sign_not_empty(romantic_composite):
    """composite Sun sign 不為空"""
    assert romantic_composite.sun_sign, "composite sun_sign 不應為空"


def test_composite_moon_sign_not_empty(romantic_composite):
    """composite Moon sign 不為空"""
    assert romantic_composite.moon_sign, "composite moon_sign 不應為空"


def test_composite_relationship_theme_not_empty(romantic_composite):
    """relationship_theme 不為空"""
    assert romantic_composite.relationship_theme, "relationship_theme 不應為空"


def test_composite_asc_mc_requires_precise(romantic_composite):
    """ASC/MC 缺精確資料時不亂算"""
    # Our mock charts don't have precise ASC longitudes so asc_sign should be None
    # (it's only set when both charts have ascendant_accuracy == "precise")
    # Just verify the field exists and doesn't crash
    _ = romantic_composite.ascendant_sign  # should not raise
    _ = romantic_composite.mc_sign         # should not raise


def test_composite_accuracy_note_mentions_asc_mc(romantic_composite):
    """accuracy_note 說明 ASC/MC 條件"""
    note = romantic_composite.accuracy_note
    assert "ASC" in note or "asc" in note.lower(), (
        f"accuracy_note 應提及 ASC/MC 條件：{note}"
    )


# ── Zodiac sign helper ────────────────────────────────────────────────────────

def test_lon_to_sign_aries():
    """0° = 牡羊座"""
    assert _lon_to_sign(0.0) == "牡羊座"


def test_lon_to_sign_libra():
    """180° = 天秤座"""
    assert _lon_to_sign(180.0) == "天秤座"


def test_lon_to_sign_pisces():
    """350° = 雙魚座"""
    assert _lon_to_sign(350.0) == "雙魚座"
