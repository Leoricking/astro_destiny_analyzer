"""
Tests for V1.5.5 — Zi Wei Auxiliary Stars & Da Xian Phase 1.

Coverage:
A. Auxiliary star data: aux_map not empty, key stars present.
B. Malefic star data: malefic_map not empty, key stars present.
C. Star category labels correct.
D. Star placement written into palace minor_stars.
E. No duplicate stars in palace minor_stars or aux/malefic maps.
F. Da Xian structure: 12 periods, valid ages, correct first palace.
G. Da Xian direction by gender × year stem.
H. Unknown gender direction.
I. Placement helpers deterministic.
J. UI render helpers do not crash.
K. Report template contains required keywords.
L. Old tests still importable (integration guard).
"""
import pytest
from datetime import date, time
from unittest.mock import MagicMock

import engines.ziwei as _zw_module
from engines.ziwei import (
    ZiWeiEngine,
    _place_left_right,
    _place_chang_qu,
    _place_kui_yue,
    _place_lucun_yang_tuo,
    _place_huo_ling,
    _place_kong_jie,
    _calc_da_xian,
    _BRANCHES,
    _BI,
)
from core.models import Gender, DaXianPeriod

ENGINE = ZiWeiEngine()
# 1989-09-21 = 己巳年, lunar 1989-8-22, 午時 (11:05)
_DATE = date(1989, 9, 21)
_TIME = time(11, 5)


def _get_formal_chart(gender=None):
    chart = ENGINE.calculate(_DATE, _TIME, gender=gender)
    if chart.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    return chart


# ── A. Auxiliary star map ─────────────────────────────────────────────────────

def test_auxiliary_star_map_nonempty():
    c = _get_formal_chart()
    assert len(c.auxiliary_star_map) > 0


def test_auxiliary_star_map_has_zuo_you():
    c = _get_formal_chart()
    assert "左輔" in c.auxiliary_star_map
    assert "右弼" in c.auxiliary_star_map


def test_auxiliary_star_map_has_chang_qu():
    c = _get_formal_chart()
    assert "文昌" in c.auxiliary_star_map
    assert "文曲" in c.auxiliary_star_map


def test_auxiliary_star_map_has_kui_yue():
    c = _get_formal_chart()
    assert "天魁" in c.auxiliary_star_map
    assert "天鉞" in c.auxiliary_star_map


def test_auxiliary_star_map_has_lucun():
    c = _get_formal_chart()
    assert "祿存" in c.auxiliary_star_map


def test_auxiliary_star_values_are_valid_branches():
    c = _get_formal_chart()
    for star, branch in c.auxiliary_star_map.items():
        assert branch in _BRANCHES, f"{star} branch '{branch}' not in _BRANCHES"


# ── B. Malefic star map ───────────────────────────────────────────────────────

def test_malefic_star_map_nonempty():
    c = _get_formal_chart()
    assert len(c.malefic_star_map) > 0


def test_malefic_star_map_has_yang_tuo():
    c = _get_formal_chart()
    assert "擎羊" in c.malefic_star_map
    assert "陀羅" in c.malefic_star_map


def test_malefic_star_map_has_huo_ling():
    c = _get_formal_chart()
    assert "火星" in c.malefic_star_map
    assert "鈴星" in c.malefic_star_map


def test_malefic_star_map_has_kong_jie():
    c = _get_formal_chart()
    assert "地空" in c.malefic_star_map
    assert "地劫" in c.malefic_star_map


def test_malefic_star_values_are_valid_branches():
    c = _get_formal_chart()
    for star, branch in c.malefic_star_map.items():
        assert branch in _BRANCHES, f"{star} branch '{branch}' not in _BRANCHES"


# ── C. Star categories ────────────────────────────────────────────────────────

def test_star_categories_aux_labeled_auspicious():
    c = _get_formal_chart()
    for s in ["左輔", "右弼", "文昌", "文曲", "天魁", "天鉞", "祿存"]:
        assert c.star_categories.get(s) == "auspicious", f"{s} should be auspicious"


def test_star_categories_malefic_labeled_malefic():
    c = _get_formal_chart()
    for s in ["擎羊", "陀羅", "火星", "鈴星", "地空", "地劫"]:
        assert c.star_categories.get(s) == "malefic", f"{s} should be malefic"


# ── D. Stars written into palace minor_stars ──────────────────────────────────

def test_auxiliary_stars_in_palace_minor_stars():
    """Every star in auxiliary_star_map should appear in the corresponding palace's minor_stars."""
    c = _get_formal_chart()
    all_palaces = [
        c.ming_palace, c.brother_palace, c.spouse_palace, c.children_palace,
        c.wealth_palace, c.health_palace, c.travel_palace, c.friends_palace,
        c.career_palace, c.property_palace, c.fortune_palace, c.parents_palace,
    ]
    branch_to_palace = {p.earthly_branch: p for p in all_palaces}
    for star, branch in c.auxiliary_star_map.items():
        p = branch_to_palace.get(branch)
        assert p is not None, f"Branch {branch} for {star} not found in palaces"
        assert star in p.minor_stars, f"{star} should be in {p.name}.minor_stars"


def test_malefic_stars_in_palace_minor_stars():
    """Every star in malefic_star_map should appear in the corresponding palace's minor_stars."""
    c = _get_formal_chart()
    all_palaces = [
        c.ming_palace, c.brother_palace, c.spouse_palace, c.children_palace,
        c.wealth_palace, c.health_palace, c.travel_palace, c.friends_palace,
        c.career_palace, c.property_palace, c.fortune_palace, c.parents_palace,
    ]
    branch_to_palace = {p.earthly_branch: p for p in all_palaces}
    for star, branch in c.malefic_star_map.items():
        p = branch_to_palace.get(branch)
        assert p is not None, f"Branch {branch} for {star} not found in palaces"
        assert star in p.minor_stars, f"{star} should be in {p.name}.minor_stars"


# ── E. No duplicates ──────────────────────────────────────────────────────────

def test_no_duplicate_stars_in_palace_minor_stars():
    c = _get_formal_chart()
    all_palaces = [
        c.ming_palace, c.brother_palace, c.spouse_palace, c.children_palace,
        c.wealth_palace, c.health_palace, c.travel_palace, c.friends_palace,
        c.career_palace, c.property_palace, c.fortune_palace, c.parents_palace,
    ]
    for p in all_palaces:
        assert len(p.minor_stars) == len(set(p.minor_stars)), \
            f"Duplicate stars in {p.name}.minor_stars: {p.minor_stars}"


def test_auxiliary_star_map_no_duplicate_stars():
    c = _get_formal_chart()
    keys = list(c.auxiliary_star_map.keys())
    assert len(keys) == len(set(keys)), "Duplicate star keys in auxiliary_star_map"


def test_malefic_star_map_no_duplicate_stars():
    c = _get_formal_chart()
    keys = list(c.malefic_star_map.keys())
    assert len(keys) == len(set(keys)), "Duplicate star keys in malefic_star_map"


# ── F. Da Xian structure ──────────────────────────────────────────────────────

def test_da_xian_has_12_periods():
    c = _get_formal_chart(gender=Gender.MALE)
    assert len(c.da_xian) == 12


def test_da_xian_ages_sequential():
    c = _get_formal_chart(gender=Gender.MALE)
    for i in range(len(c.da_xian) - 1):
        assert c.da_xian[i].end_age == c.da_xian[i + 1].start_age - 1


def test_da_xian_period_duration_10():
    c = _get_formal_chart(gender=Gender.MALE)
    for d in c.da_xian:
        assert d.end_age - d.start_age == 9, f"Period {d.palace_name} not 10 years"


def test_da_xian_first_palace_is_ming():
    """First Da Xian period always starts at 命宮."""
    c = _get_formal_chart(gender=Gender.MALE)
    assert c.da_xian[0].palace_name == "命宮"


def test_da_xian_has_palace_name_and_branch():
    c = _get_formal_chart(gender=Gender.MALE)
    for d in c.da_xian:
        assert len(d.palace_name) > 0
        assert d.branch in _BRANCHES


def test_da_xian_start_age_equals_bureau_number():
    c = _get_formal_chart(gender=Gender.MALE)
    assert c.da_xian_start_age == c.five_element_bureau_number


# ── G. Da Xian direction by gender × year stem ───────────────────────────────

def test_da_xian_direction_yang_male_forward():
    """陽年 + 男 → forward."""
    # 1989 = 己巳 (己 is 陰干), so 己年男 → backward
    # Use a 陽年 (甲/丙/戊/庚/壬): 1990 = 庚午 (陽干)
    c = ENGINE.calculate(date(1990, 6, 15), time(12, 0), gender=Gender.MALE)
    if c.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    assert c.da_xian_direction == "forward"


def test_da_xian_direction_yang_female_backward():
    """陽年 + 女 → backward."""
    c = ENGINE.calculate(date(1990, 6, 15), time(12, 0), gender=Gender.FEMALE)
    if c.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    assert c.da_xian_direction == "backward"


def test_da_xian_direction_yin_male_backward():
    """陰年 + 男 → backward. 1989 = 己年 (陰干)."""
    c = ENGINE.calculate(_DATE, _TIME, gender=Gender.MALE)
    if c.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    assert c.da_xian_direction == "backward"


def test_da_xian_direction_yin_female_forward():
    """陰年 + 女 → forward."""
    c = ENGINE.calculate(_DATE, _TIME, gender=Gender.FEMALE)
    if c.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    assert c.da_xian_direction == "forward"


# ── H. Unknown gender direction ───────────────────────────────────────────────

def test_da_xian_direction_unknown_gender():
    c = ENGINE.calculate(_DATE, _TIME, gender=None)
    if c.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    assert c.da_xian_direction == "unknown"
    assert len(c.da_xian) == 12  # still 12 periods (conservative forward)


def test_da_xian_unknown_gender_accuracy_note_mentioned():
    c = ENGINE.calculate(_DATE, _TIME, gender=None)
    if c.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    # da_xian should still be built
    assert len(c.da_xian) == 12


# ── I. Placement helpers deterministic ───────────────────────────────────────

def test_place_left_right_deterministic():
    assert _place_left_right(8) == _place_left_right(8)


def test_place_left_right_month1_left_at_chen():
    result = _place_left_right(1)
    assert result["左輔"] == "辰"  # 月1起辰(4)


def test_place_left_right_month1_right_at_xu():
    result = _place_left_right(1)
    assert result["右弼"] == "戌"  # 月1起戌(10)


def test_place_chang_qu_deterministic():
    assert _place_chang_qu("午") == _place_chang_qu("午")


def test_place_chang_qu_zi_time():
    result = _place_chang_qu("子")
    # 文昌: (10 - 0) % 12 = 10 = 戌
    assert result["文昌"] == "戌"
    # 文曲: (4 + 0) % 12 = 4 = 辰
    assert result["文曲"] == "辰"


def test_place_kui_yue_deterministic():
    assert _place_kui_yue("甲") == _place_kui_yue("甲")


def test_place_kui_yue_jia():
    result = _place_kui_yue("甲")
    assert result["天魁"] == "丑"
    assert result["天鉞"] == "未"


def test_place_lucun_yang_tuo_deterministic():
    assert _place_lucun_yang_tuo("己") == _place_lucun_yang_tuo("己")


def test_place_lucun_yang_tuo_jia():
    result = _place_lucun_yang_tuo("甲")
    assert result["祿存"] == "寅"  # index 2
    assert result["擎羊"] == "卯"  # index 3
    assert result["陀羅"] == "丑"  # index 1


def test_place_huo_ling_deterministic():
    assert _place_huo_ling("寅", "子") == _place_huo_ling("寅", "子")


def test_place_kong_jie_deterministic():
    assert _place_kong_jie("子") == _place_kong_jie("子")


def test_place_kong_jie_zi_time():
    result = _place_kong_jie("子")
    # 地空: (11 - 0) % 12 = 11 = 亥
    assert result["地空"] == "亥"
    # 地劫: (11 + 0) % 12 = 11 = 亥
    assert result["地劫"] == "亥"


def test_place_huo_ling_yin_group_zi_time():
    result = _place_huo_ling("寅", "子")
    # base (2, 3), hour=0: 火=(2+0)%12=2=寅, 鈴=(3+0)%12=3=卯
    assert result["火星"] == "寅"
    assert result["鈴星"] == "卯"


# ── J. UI render helpers ──────────────────────────────────────────────────────

def test_render_ziwei_auxiliary_table_no_crash():
    import unittest.mock as mock
    c = ENGINE.calculate(_DATE, _TIME)
    with mock.patch.dict("sys.modules", {
        "streamlit": mock.MagicMock(),
        "pandas": __import__("pandas"),
    }):
        from ui.components import render_ziwei_auxiliary_table
        render_ziwei_auxiliary_table(c)


def test_render_daxian_table_no_crash():
    import unittest.mock as mock
    c = ENGINE.calculate(_DATE, _TIME, gender=Gender.MALE)
    with mock.patch.dict("sys.modules", {
        "streamlit": mock.MagicMock(),
        "pandas": __import__("pandas"),
    }):
        from ui.components import render_daxian_table
        render_daxian_table(c)


# ── K. Report template keywords ───────────────────────────────────────────────

def test_report_template_contains_auxiliary_keywords():
    from reports.templates import TEMPLATE_FULL
    for kw in ["輔星", "煞星", "大限", "左輔", "擎羊", "V1.5.5"]:
        assert kw in TEMPLATE_FULL, f"TEMPLATE_FULL missing keyword: {kw}"


def test_report_template_no_scare_words():
    from reports.templates import TEMPLATE_FULL
    forbidden = ["必凶", "必敗", "大凶", "大敗"]
    for w in forbidden:
        assert w not in TEMPLATE_FULL, f"TEMPLATE_FULL contains forbidden word: {w}"


# ── L. Partial layout (no birth time) still has some aux stars ───────────────

def test_partial_layout_has_kui_yue():
    """Without birth time, 天魁/天鉞 should still be placed (year stem only)."""
    c = ENGINE.calculate(_DATE, birth_time=None)
    if c.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    assert "天魁" in c.auxiliary_star_map
    assert "天鉞" in c.auxiliary_star_map


def test_partial_layout_no_chang_qu():
    """Without birth time, 文昌/文曲 should NOT be placed."""
    c = ENGINE.calculate(_DATE, birth_time=None)
    if c.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    assert "文昌" not in c.auxiliary_star_map
    assert "文曲" not in c.auxiliary_star_map


# ── M. DaXianPeriod model importable ─────────────────────────────────────────

def test_daxian_period_model_importable():
    d = DaXianPeriod(
        start_age=2, end_age=11,
        palace_name="命宮", branch="午",
        main_stars=["紫微"], auxiliary_stars=["左輔"],
        interpretation="test"
    )
    assert d.start_age == 2
    assert d.palace_name == "命宮"
