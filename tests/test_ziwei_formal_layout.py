"""
Tests for Zi Wei Dou Shu Engine — V1.5 Formal Layout Phase 1.

Coverage:
A. Lunar date conversion.
B. Unknown birth time → partial_lunar_only or mock_fallback, no crash.
C. Known birth time → formal_layout_phase1, birth_hour_branch, ming/shen.
D. 12 palaces: count, names, unique branches.
E. 14 main stars: all present, each once, 紫微 and 天府 exist.
F. 四化: 甲/乙/庚/癸 year stems.
G. Fallback when lunardate unavailable.
H. Helper functions: _place_ziwei_star, _place_tianfu_star deterministic.
"""
import pytest
from datetime import date, time
from unittest.mock import patch

import engines.ziwei as _zw_module
from engines.ziwei import (
    ZiWeiEngine,
    _get_ziwei_hour_branch,
    _place_ziwei_star,
    _place_tianfu_star,
    _calc_ming_shen,
    _YEAR_STEM_SIHUA,
    _MAIN_STARS_14,
    _BRANCHES,
)

ENGINE = ZiWeiEngine()

# Reference birth date: 1989-09-21 (lunar 1989-8-22)
_DATE = date(1989, 9, 21)
_TIME_KNOWN = time(11, 5)


# ── A. Lunar conversion ───────────────────────────────────────────────────────

def test_lunar_conversion_fields_not_none():
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    if chart.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    assert chart.lunar_year is not None
    assert chart.lunar_month is not None
    assert chart.lunar_day is not None

def test_lunar_conversion_correct_values():
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    if chart.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    # 1989-09-21 = lunar 1989-08-22
    assert chart.lunar_year  == 1989
    assert chart.lunar_month == 8
    assert chart.lunar_day   == 22


# ── B. Unknown birth time ─────────────────────────────────────────────────────

def test_unknown_time_no_crash():
    chart = ENGINE.calculate(_DATE, birth_time=None)
    assert chart is not None

def test_unknown_time_mode():
    chart = ENGINE.calculate(_DATE, birth_time=None)
    assert chart.calculation_mode in ("partial_lunar_only", "mock_fallback")

def test_unknown_time_accuracy_note_present():
    chart = ENGINE.calculate(_DATE, birth_time=None)
    assert len(chart.accuracy_note) > 0

def test_unknown_time_shen_branch_none_or_partial():
    chart = ENGINE.calculate(_DATE, birth_time=None)
    if chart.calculation_mode == "partial_lunar_only":
        # shen_branch may be None for unknown time
        assert chart.shen_branch is None


# ── C. Known birth time ───────────────────────────────────────────────────────

def test_known_time_mode_formal():
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    if chart.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    assert chart.calculation_mode == "formal_layout_phase1"

def test_known_time_hour_branch_wu():
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    if chart.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    assert chart.birth_hour_branch == "午"

def test_known_time_ming_branch_not_none():
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    if chart.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    assert chart.ming_branch is not None
    assert chart.ming_branch in _BRANCHES

def test_known_time_shen_branch_not_none():
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    if chart.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    assert chart.shen_branch is not None


# ── D. 12 palaces ────────────────────────────────────────────────────────────

def _get_twelve_palaces(chart):
    return [
        chart.ming_palace, chart.brother_palace, chart.spouse_palace,
        chart.children_palace, chart.wealth_palace, chart.health_palace,
        chart.travel_palace, chart.friends_palace, chart.career_palace,
        chart.property_palace, chart.fortune_palace, chart.parents_palace,
    ]

def test_twelve_palaces_count():
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    assert len(_get_twelve_palaces(chart)) == 12

def test_palace_names_complete():
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    expected = {
        "命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
        "遷移宮", "交友宮", "官祿宮", "田宅宮", "福德宮", "父母宮",
    }
    actual = {p.name for p in _get_twelve_palaces(chart)}
    assert actual == expected

def test_palace_branches_unique():
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    branches = [p.earthly_branch for p in _get_twelve_palaces(chart)]
    assert len(set(branches)) == 12, f"Duplicate branches: {branches}"


# ── E. 14 main stars ─────────────────────────────────────────────────────────

def test_fourteen_stars_all_present():
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    for star in _MAIN_STARS_14:
        assert star in chart.main_stars, f"Missing star: {star}"

def test_fourteen_stars_count():
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    assert len(chart.main_stars) == 14

def test_each_main_star_appears_once():
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    from collections import Counter
    counts = Counter(chart.main_stars)
    duplicates = {s: c for s, c in counts.items() if c > 1}
    assert not duplicates, f"Duplicate stars: {duplicates}"

def test_ziwei_star_present():
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    assert "紫微" in chart.main_stars

def test_tianfu_star_present():
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    assert "天府" in chart.main_stars


# ── F. 四化 ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("year,expected_luzhu", [
    (1984, "廉貞"),  # 甲年: 廉貞化祿
    (1985, "天機"),  # 乙年: 天機化祿
    (1990, "太陽"),  # 庚年: 太陽化祿
    (1993, "破軍"),  # 癸年: 破軍化祿
])
def test_sihua_luzhu_by_year(year, expected_luzhu):
    chart = ENGINE.calculate(date(year, 6, 15), time(12, 0))
    # four_transformations maps star→化X
    lu_star = [s for s, t in chart.four_transformations.items() if t == "化祿"]
    assert expected_luzhu in lu_star, \
        f"Year {year}: expected {expected_luzhu} 化祿, got {lu_star}"

def test_sihua_table_jia():
    """甲年 四化 complete check."""
    assert _YEAR_STEM_SIHUA["甲"]["廉貞"] == "化祿"
    assert _YEAR_STEM_SIHUA["甲"]["破軍"] == "化權"
    assert _YEAR_STEM_SIHUA["甲"]["武曲"] == "化科"
    assert _YEAR_STEM_SIHUA["甲"]["太陽"] == "化忌"

def test_sihua_auxiliary_star_in_four_transformations():
    """輔星四化 (e.g. 文昌) should appear in four_transformations, not crash."""
    # 丙年: 文昌化科 — 文昌 is not a main star
    chart = ENGINE.calculate(date(1986, 6, 15), time(12, 0))  # 丙年
    # Should not crash and four_transformations should include 文昌
    assert "文昌" in chart.four_transformations


# ── G. Fallback when lunardate unavailable ───────────────────────────────────

def test_mock_fallback_no_crash(monkeypatch):
    monkeypatch.setattr(_zw_module, "_LUNARDATE_AVAILABLE", False)
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    assert chart is not None
    assert chart.calculation_mode == "mock_fallback"

def test_mock_fallback_has_main_stars(monkeypatch):
    monkeypatch.setattr(_zw_module, "_LUNARDATE_AVAILABLE", False)
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    assert len(chart.main_stars) == 14


# ── H. Helper determinism ─────────────────────────────────────────────────────

def test_place_ziwei_deterministic():
    """Same inputs always produce same branch index."""
    assert _place_ziwei_star(22, 3) == _place_ziwei_star(22, 3)
    assert _place_ziwei_star(1, 5)  == _place_ziwei_star(1, 5)

def test_place_ziwei_day1_any_bureau_is_chen():
    """Day 1 with any bureau → 辰 (index 4). Corrected base in V1.7.4."""
    for bureau in (2, 3, 4, 5, 6):
        assert _place_ziwei_star(1, bureau) == 4, \
            f"Bureau {bureau}: expected 辰(4), got {_place_ziwei_star(1, bureau)}"

def test_place_tianfu_deterministic():
    for z in range(12):
        assert _place_tianfu_star(z) == _place_tianfu_star(z)

def test_place_tianfu_ziwei_zi_gives_tianfu_chen():
    """紫微=子(0) → 天府=辰(4)."""
    assert _place_tianfu_star(0) == 4

def test_hour_branch_wu_for_1105():
    assert _get_ziwei_hour_branch(11, 5) == "午"

def test_hour_branch_zi_for_2300():
    assert _get_ziwei_hour_branch(23, 0) == "子"

def test_hour_branch_zi_for_0000():
    assert _get_ziwei_hour_branch(0, 0) == "子"

def test_calc_ming_shen_stable():
    """Same lunar_month + hour_branch always gives same result."""
    a = _calc_ming_shen(8, "午")
    b = _calc_ming_shen(8, "午")
    assert a == b
