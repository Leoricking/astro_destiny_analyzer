"""
Tests for BaZi Engine — V1.4 Solar Term Precision.

Coverage:
1.  Before 立春 → BaZi year uses previous year stem/branch.
2.  On/after 立春 → BaZi year uses current year stem/branch.
3.  寅月 boundary: date after 立春 → branch = 寅.
4.  卯月 boundary: date after 驚蟄 → branch = 卯.
5.  酉月 boundary: 1989-09-21 is after 白露 (Sep 8) → branch = 酉, not 申.
6.  小寒後立春前: BaZi year is previous, but month branch = 丑.
7.  Unknown birth time → birth_time_accuracy="unknown", accuracy_note mentions time.
8.  Known birth time 11:05 → hour branch = 午.
9.  _bazi_year helper is consistent with year_pillar stem/branch.
10. calculation_mode and boundary rule fields always present.
"""
import pytest
from datetime import date, time

from engines.bazi import BaZiEngine, _bazi_year, _month_branch_from_solar_terms
from core.models import EarthlyBranch, HeavenlyStem


ENGINE = BaZiEngine()


# ── Helper assertions ─────────────────────────────────────────────────────────

def _year_stem_branch(bazi_year: int):
    """Return expected (stem_char, branch_char) for a given BaZi year integer."""
    from engines.bazi import STEMS, BRANCHES
    stem   = STEMS[(bazi_year - 4) % 10]
    branch = BRANCHES[(bazi_year - 4) % 12]
    return stem, branch


# ── 1. Before 立春 → previous year ───────────────────────────────────────────

def test_before_lichun_uses_previous_year():
    """1990-02-03 is before 立春 (Feb 4) → BaZi year = 1989."""
    bd = date(1990, 2, 3)
    assert _bazi_year(bd) == 1989

    chart = ENGINE.calculate(bd)
    expected_stem, expected_branch = _year_stem_branch(1989)
    assert chart.year_pillar.heavenly_stem == expected_stem
    assert chart.year_pillar.earthly_branch == expected_branch


# ── 2. On 立春 → current year ─────────────────────────────────────────────────

def test_on_lichun_uses_current_year():
    """1990-02-05 is after 立春 (Feb 4) → BaZi year = 1990."""
    bd = date(1990, 2, 5)
    assert _bazi_year(bd) == 1990

    chart = ENGINE.calculate(bd)
    expected_stem, expected_branch = _year_stem_branch(1990)
    assert chart.year_pillar.heavenly_stem == expected_stem
    assert chart.year_pillar.earthly_branch == expected_branch


# ── 3. 寅月 boundary ──────────────────────────────────────────────────────────

def test_yin_month_boundary():
    """1990-02-05 is after 立春 → month branch = 寅."""
    bd = date(1990, 2, 5)
    branch = _month_branch_from_solar_terms(bd)
    assert branch == EarthlyBranch.YIN

    chart = ENGINE.calculate(bd)
    assert chart.month_pillar.earthly_branch == EarthlyBranch.YIN


# ── 4. 卯月 boundary ──────────────────────────────────────────────────────────

def test_mao_month_boundary():
    """1990-03-10 is after 驚蟄 (Mar 6) → month branch = 卯."""
    bd = date(1990, 3, 10)
    branch = _month_branch_from_solar_terms(bd)
    assert branch == EarthlyBranch.MAO

    chart = ENGINE.calculate(bd)
    assert chart.month_pillar.earthly_branch == EarthlyBranch.MAO


# ── 5. 酉月: 1989-09-21 is after 白露 (Sep 8), before 寒露 (Oct 8) ────────────

def test_you_month_after_bailu():
    """1989-09-21 is past 白露 → branch = 酉, not 申."""
    bd = date(1989, 9, 21)
    branch = _month_branch_from_solar_terms(bd)
    assert branch == EarthlyBranch.YOU, f"Expected 酉 but got {branch}"

    chart = ENGINE.calculate(bd)
    assert chart.month_pillar.earthly_branch == EarthlyBranch.YOU


# ── 6. 小寒後立春前 ────────────────────────────────────────────────────────────

def test_xiaohan_before_lichun():
    """1990-01-10 is after 小寒 (Jan 6) but before 立春 (Feb 4).
    BaZi year = 1989; month branch = 丑."""
    bd = date(1990, 1, 10)
    assert _bazi_year(bd) == 1989

    branch = _month_branch_from_solar_terms(bd)
    assert branch == EarthlyBranch.CHOU

    chart = ENGINE.calculate(bd)
    expected_stem, expected_branch = _year_stem_branch(1989)
    assert chart.year_pillar.heavenly_stem == expected_stem
    assert chart.year_pillar.earthly_branch == expected_branch
    assert chart.month_pillar.earthly_branch == EarthlyBranch.CHOU


# ── 7. Unknown birth time ─────────────────────────────────────────────────────

def test_unknown_birth_time_accuracy():
    """No birth time → birth_time_accuracy='unknown', accuracy_note mentions time."""
    chart = ENGINE.calculate(date(1989, 9, 21), birth_time=None)
    assert chart.birth_time_accuracy == "unknown"
    assert chart.hour_pillar is None
    assert "時柱" in chart.accuracy_note


# ── 8. Known birth time 11:05 → hour branch 午 ───────────────────────────────

def test_known_birth_time_hour_branch():
    """1989-09-21 11:05 → hour branch = 午 (11:00-12:59)."""
    chart = ENGINE.calculate(date(1989, 9, 21), birth_time=time(11, 5))
    assert chart.birth_time_accuracy == "known"
    assert chart.hour_pillar is not None
    assert chart.hour_pillar.earthly_branch == EarthlyBranch.WU_


# ── 9. _bazi_year consistent with year_pillar ─────────────────────────────────

def test_bazi_year_matches_pillar():
    """_bazi_year() result must agree with year_pillar stem/branch."""
    test_dates = [
        date(1990, 2, 3),
        date(1990, 2, 5),
        date(1989, 9, 21),
        date(1990, 1, 10),
        date(2000, 1, 1),
        date(2000, 2, 10),
    ]
    for bd in test_dates:
        bazi_yr = _bazi_year(bd)
        expected_stem, expected_branch = _year_stem_branch(bazi_yr)
        chart = ENGINE.calculate(bd)
        assert chart.year_pillar.heavenly_stem == expected_stem, \
            f"{bd}: stem mismatch (bazi_year={bazi_yr})"
        assert chart.year_pillar.earthly_branch == expected_branch, \
            f"{bd}: branch mismatch (bazi_year={bazi_yr})"


# ── 10. Metadata fields always present ───────────────────────────────────────

def test_metadata_fields_always_present():
    """calculation_mode, year_boundary_rule, month_boundary_rule always set."""
    chart = ENGINE.calculate(date(1990, 6, 15))
    assert chart.calculation_mode == "solar_term_approx"
    assert chart.year_boundary_rule == "lichun"
    assert chart.month_boundary_rule == "solar_terms"
    assert isinstance(chart.accuracy_note, str)
    assert len(chart.accuracy_note) > 0
