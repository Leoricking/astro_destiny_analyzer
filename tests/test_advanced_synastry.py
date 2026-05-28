"""
V1.8.0 Tests: Advanced Synastry Aspect Matrix
"""
import pytest
from datetime import date, time

from compatibility.advanced_astrology import (
    AdvancedAstrologyEngine, _midpoint_longitude, _lon_to_sign,
    _calculate_synastry_aspects, _calculate_composite_chart,
)
from compatibility.models import SynastryMatrix, SynastryAspect


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def romantic_charts():
    from reports.generator import ReportGenerator
    from demo.sample_profiles import SAMPLE_COUPLES
    gen = ReportGenerator()
    couple = next(c for c in SAMPLE_COUPLES if c.get("relationship_type") == "romantic")
    ra = gen.generate(couple["person_a"], persist=False)
    rb = gen.generate(couple["person_b"], persist=False)
    return ra.western_chart, rb.western_chart


@pytest.fixture(scope="module")
def synastry_matrix(romantic_charts):
    wc_a, wc_b = romantic_charts
    return _calculate_synastry_aspects(wc_a, wc_b)


@pytest.fixture(scope="module")
def advanced_result(romantic_charts):
    wc_a, wc_b = romantic_charts
    return AdvancedAstrologyEngine().calculate(wc_a, wc_b)


# ── 1. Engine instantiation ───────────────────────────────────────────────────

def test_engine_can_be_created():
    """AdvancedAstrologyEngine 可建立"""
    engine = AdvancedAstrologyEngine()
    assert engine is not None


# ── 2. Synastry aspects not empty ────────────────────────────────────────────

def test_aspects_not_empty(synastry_matrix):
    """Romantic couple synastry aspects 不為空"""
    assert len(synastry_matrix.aspects) > 0, "aspects 不應為空"


# ── 3. Strongest aspects not empty ───────────────────────────────────────────

def test_strongest_aspects_not_empty(synastry_matrix):
    """strongest_aspects 不為空"""
    assert len(synastry_matrix.strongest_aspects) > 0


# ── 4. Strongest aspects is subset of all ────────────────────────────────────

def test_strongest_aspects_max_8(synastry_matrix):
    """strongest_aspects 最多 8 個"""
    assert len(synastry_matrix.strongest_aspects) <= 8


# ── 5. Orb in reasonable range ───────────────────────────────────────────────

def test_aspect_orb_in_range(synastry_matrix):
    """所有相位 orb 在合理範圍（0–8°）"""
    for a in synastry_matrix.aspects:
        assert 0 <= a.orb <= 8, f"orb {a.orb} 超出範圍"


# ── 6. Strength in 0–100 ─────────────────────────────────────────────────────

def test_aspect_strength_in_range(synastry_matrix):
    """所有相位 strength 在 0–100"""
    for a in synastry_matrix.aspects:
        assert 0 <= a.strength <= 100, f"strength {a.strength} 超出範圍"


# ── 7. Venus/Mars or Sun/Moon categorised ────────────────────────────────────

def test_venus_mars_or_sun_moon_categorised(synastry_matrix):
    """Venus-Mars 或 Sun-Moon 類互動可被分類（非空 category）"""
    target_pairs = [
        {"金星", "火星"}, {"太陽", "月亮"}, {"金星", "太陽"}, {"火星", "月亮"},
    ]
    relevant = [
        a for a in synastry_matrix.aspects
        if {a.person_a_planet, a.person_b_planet} in target_pairs
    ]
    if relevant:
        for a in relevant:
            assert a.category != "", f"category 不應為空：{a.person_a_planet} x {a.person_b_planet}"


# ── 8. Harmony and tension aspects distinguishable ───────────────────────────

def test_harmony_tension_distinct(synastry_matrix):
    """harmony_aspects 與 tension_aspects 可區分（各自獨立列表）"""
    # harmony and tension should be based on is_harmonious / is_challenging flags
    for a in synastry_matrix.harmony_aspects:
        assert a.is_harmonious, "harmony_aspects 中有非和諧相位"
    for a in synastry_matrix.tension_aspects:
        assert a.is_challenging, "tension_aspects 中有非張力相位"


# ── 9. accuracy_note not empty ────────────────────────────────────────────────

def test_accuracy_note_not_empty(synastry_matrix):
    """accuracy_note 不為空"""
    assert synastry_matrix.accuracy_note


# ── 10. Fallback when no longitude ───────────────────────────────────────────

def test_fallback_no_longitude_no_crash():
    """缺 longitude 時 fallback 不 crash"""
    from core.models import WesternChart, PlanetPosition, Planet, ZodiacSign, HousePosition
    # Create minimal chart with no planet_positions
    empty_chart = WesternChart(
        planet_positions=[],
        houses=[],
        aspects=[],
        ascendant=ZodiacSign.ARIES,
        descendant=ZodiacSign.LIBRA,
        mc=ZodiacSign.CAPRICORN,
        ic=ZodiacSign.CANCER,
        calculation_mode="mock_fallback",
        accuracy_note="test",
    )
    result = AdvancedAstrologyEngine().calculate(empty_chart, empty_chart)
    assert result is not None
    assert result.synastry_matrix.accuracy_note != ""
