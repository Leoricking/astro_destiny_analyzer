"""
Tests for Zi Wei Dou Shu main star placement — V1.7.4 layout fix validation.

Validates that after the V1.7.4 corrections (backward palace direction + corrected
紫微 placement formula), the 14 main stars land in the correct palaces for Rossi's
chart (1989-09-21 11:05, 命宮卯, 六局, 陰男), cross-validated against the external
screenshot chart (EXAMPLE_ROSSI_EXTERNAL_CHART).
"""
from __future__ import annotations

import pytest
from datetime import date, time

from engines.ziwei import (
    ZiWeiEngine,
    _place_ziwei_star,
    _place_tianfu_star,
)

ENGINE = ZiWeiEngine()
_DATE = date(1989, 9, 21)
_TIME = time(11, 5)


def _get_chart():
    try:
        from lunardate import LunarDate  # noqa: F401
    except ImportError:
        pytest.skip("lunardate not installed")
    chart = ENGINE.calculate(_DATE, _TIME)
    if chart.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    return chart


def _palace_by_name(chart, name: str):
    palaces = [
        chart.ming_palace, chart.brother_palace, chart.spouse_palace,
        chart.children_palace, chart.wealth_palace, chart.health_palace,
        chart.travel_palace, chart.friends_palace, chart.career_palace,
        chart.property_palace, chart.fortune_palace, chart.parents_palace,
    ]
    return next((p for p in palaces if p.name == name), None)


# ── 1. 紫微 placement helper ──────────────────────────────────────────────────

def test_place_ziwei_day22_bureau6_is_wei():
    """_place_ziwei_star(22, 6) must return 7 (未) — Rossi's chart, V1.7.4 formula."""
    assert _place_ziwei_star(22, 6) == 7, (
        f"Expected 未(7), got {_place_ziwei_star(22, 6)}"
    )


def test_place_tianfu_from_wei_is_you():
    """If 紫微=未(7), then 天府=(4-7)%12=9=酉."""
    assert _place_tianfu_star(7) == 9


# ── 2. Palace branches match external chart ───────────────────────────────────

def test_ming_palace_branch_is_mao():
    """命宮 must be at 卯 (index 3)."""
    chart = _get_chart()
    assert chart.ming_palace.earthly_branch == "卯"


def test_career_palace_branch_is_wei():
    """官祿宮 must be at 未 (V1.7.4 fix: was wrong before)."""
    chart = _get_chart()
    career = _palace_by_name(chart, "官祿宮")
    assert career is not None
    assert career.earthly_branch == "未", (
        f"官祿宮 expected 未, got {career.earthly_branch}"
    )


def test_travel_palace_branch_is_you():
    """遷移宮 must be at 酉."""
    chart = _get_chart()
    travel = _palace_by_name(chart, "遷移宮")
    assert travel is not None
    assert travel.earthly_branch == "酉", (
        f"遷移宮 expected 酉, got {travel.earthly_branch}"
    )


def test_wealth_palace_branch_is_hai():
    """財帛宮 must be at 亥."""
    chart = _get_chart()
    wealth = _palace_by_name(chart, "財帛宮")
    assert wealth is not None
    assert wealth.earthly_branch == "亥", (
        f"財帛宮 expected 亥, got {wealth.earthly_branch}"
    )


def test_parents_palace_branch_is_chen():
    """父母宮 must be at 辰."""
    chart = _get_chart()
    parents = _palace_by_name(chart, "父母宮")
    assert parents is not None
    assert parents.earthly_branch == "辰", (
        f"父母宮 expected 辰, got {parents.earthly_branch}"
    )


# ── 3. Main stars in correct palaces (cross-validated vs external chart) ──────

def test_ziwei_and_pojun_in_career_palace():
    """紫微+破軍 must be in 官祿宮 (未)."""
    chart = _get_chart()
    career = _palace_by_name(chart, "官祿宮")
    assert career is not None
    assert "紫微" in career.main_stars, f"紫微 not in 官祿宮: {career.main_stars}"
    assert "破軍" in career.main_stars, f"破軍 not in 官祿宮: {career.main_stars}"


def test_wuqu_and_qisha_in_ming_palace():
    """武曲+七殺 must be in 命宮 (卯)."""
    chart = _get_chart()
    assert "武曲" in chart.ming_palace.main_stars, (
        f"武曲 not in 命宮: {chart.ming_palace.main_stars}"
    )
    assert "七殺" in chart.ming_palace.main_stars, (
        f"七殺 not in 命宮: {chart.ming_palace.main_stars}"
    )


def test_tianfu_in_travel_palace():
    """天府 must be in 遷移宮 (酉)."""
    chart = _get_chart()
    travel = _palace_by_name(chart, "遷移宮")
    assert travel is not None
    assert "天府" in travel.main_stars, f"天府 not in 遷移宮: {travel.main_stars}"


def test_lianzhen_and_tanlang_in_wealth_palace():
    """廉貞+貪狼 must be in 財帛宮 (亥)."""
    chart = _get_chart()
    wealth = _palace_by_name(chart, "財帛宮")
    assert wealth is not None
    assert "廉貞" in wealth.main_stars, f"廉貞 not in 財帛宮: {wealth.main_stars}"
    assert "貪狼" in wealth.main_stars, f"貪狼 not in 財帛宮: {wealth.main_stars}"


def test_tianshu_in_property_palace():
    """天機 must be in 田宅宮 (午)."""
    chart = _get_chart()
    prop = _palace_by_name(chart, "田宅宮")
    assert prop is not None
    assert "天機" in prop.main_stars, f"天機 not in 田宅宮: {prop.main_stars}"


def test_taiyang_in_parents_palace():
    """太陽 must be in 父母宮 (辰)."""
    chart = _get_chart()
    parents = _palace_by_name(chart, "父母宮")
    assert parents is not None
    assert "太陽" in parents.main_stars, f"太陽 not in 父母宮: {parents.main_stars}"


def test_tiantong_and_tianliang_in_brother_palace():
    """天同+天梁 must be in 兄弟宮 (寅)."""
    chart = _get_chart()
    bro = _palace_by_name(chart, "兄弟宮")
    assert bro is not None
    assert "天同" in bro.main_stars, f"天同 not in 兄弟宮: {bro.main_stars}"
    assert "天梁" in bro.main_stars, f"天梁 not in 兄弟宮: {bro.main_stars}"
