"""
Tests for BaZi Engine — V1.4.5 Day/Hour Precision & Zi Hour Policy.

Coverage:
A. Hour branch mapping (all boundary times).
B. Hour stem derivation by day master.
C. Unknown birth time → accuracy fields reflect unknown.
D. Known birth time 1989-09-21 11:05 → hour_branch=午, hour_pillar_is_precise=True.
E. Zi hour policy: late_zi_same_day vs late_zi_next_day.
F. All existing tests unaffected (structural check).
"""
import pytest
from datetime import date, time

from engines.bazi import (
    BaZiEngine, _get_hour_branch, _hour_stem, _day_pillar,
    STEMS, BRANCHES,
)
from core.models import EarthlyBranch, HeavenlyStem


ENGINE = BaZiEngine()


# ── A. Hour branch mapping ────────────────────────────────────────────────────

@pytest.mark.parametrize("hour,minute,expected", [
    (0,  0,  EarthlyBranch.ZI),    # 00:00 → 子
    (0,  59, EarthlyBranch.ZI),    # 00:59 → 子
    (1,  0,  EarthlyBranch.CHOU),  # 01:00 → 丑
    (2,  59, EarthlyBranch.CHOU),  # 02:59 → 丑
    (3,  0,  EarthlyBranch.YIN),   # 03:00 → 寅
    (11, 5,  EarthlyBranch.WU_),   # 11:05 → 午
    (22, 59, EarthlyBranch.HAI),   # 22:59 → 亥
    (23, 0,  EarthlyBranch.ZI),    # 23:00 → 子
    (23, 59, EarthlyBranch.ZI),    # 23:59 → 子
])
def test_get_hour_branch(hour, minute, expected):
    assert _get_hour_branch(hour, minute) == expected


# ── B. Hour stem derivation ───────────────────────────────────────────────────

def test_hour_stem_jia_day_zi():
    """甲日子時 → 甲."""
    assert _hour_stem(HeavenlyStem.JIA, EarthlyBranch.ZI) == HeavenlyStem.JIA

def test_hour_stem_jia_day_chou():
    """甲日丑時 → 乙."""
    assert _hour_stem(HeavenlyStem.JIA, EarthlyBranch.CHOU) == HeavenlyStem.YI

def test_hour_stem_ji_day_zi():
    """己日子時 → 甲（同組甲己）."""
    assert _hour_stem(HeavenlyStem.JI, EarthlyBranch.ZI) == HeavenlyStem.JIA

def test_hour_stem_geng_day_zi():
    """庚日子時 → 丙（乙庚組）."""
    assert _hour_stem(HeavenlyStem.GENG, EarthlyBranch.ZI) == HeavenlyStem.BING

def test_hour_stem_ren_day_wu():
    """壬日午時 → 丙（丁壬組，子=庚→午=丙）."""
    result = _hour_stem(HeavenlyStem.REN, EarthlyBranch.WU_)
    # 丁壬→庚子起, 午 branch_idx=6, STEMS[(6+6)%10]=STEMS[2]=丙
    assert result == HeavenlyStem.BING


# ── C. Unknown birth time ─────────────────────────────────────────────────────

def test_unknown_time_hour_pillar_accuracy():
    chart = ENGINE.calculate(date(1989, 9, 21), birth_time=None)
    assert chart.hour_pillar_accuracy == "unknown"
    assert chart.birth_time_accuracy == "unknown"
    assert chart.hour_pillar_is_precise is False
    assert chart.hour_pillar is None

def test_unknown_time_accuracy_note_mentions_time():
    chart = ENGINE.calculate(date(1989, 9, 21), birth_time=None)
    assert "時柱" in chart.accuracy_note or "出生時間" in chart.accuracy_note


# ── D. Known birth time 1989-09-21 11:05 ─────────────────────────────────────

def test_known_time_hour_branch_wu():
    """1989-09-21 11:05 → hour branch = 午."""
    chart = ENGINE.calculate(date(1989, 9, 21), birth_time=time(11, 5))
    assert chart.hour_pillar is not None
    assert chart.hour_pillar.earthly_branch == EarthlyBranch.WU_

def test_known_time_hour_pillar_precise():
    """Known time → hour_pillar_is_precise=True, hour_pillar_accuracy='precise'."""
    chart = ENGINE.calculate(date(1989, 9, 21), birth_time=time(11, 5))
    assert chart.hour_pillar_is_precise is True
    assert chart.hour_pillar_accuracy == "precise"


# ── E. Zi hour policy ────────────────────────────────────────────────────────

def test_late_zi_same_day_uses_birth_date():
    """late_zi_same_day: 1989-09-21 23:30 → day pillar from 1989-09-21."""
    chart = ENGINE.calculate(
        date(1989, 9, 21), birth_time=time(23, 30),
        zi_hour_policy="late_zi_same_day",
    )
    reference = _day_pillar(date(1989, 9, 21))
    assert chart.day_pillar.heavenly_stem   == reference.heavenly_stem
    assert chart.day_pillar.earthly_branch  == reference.earthly_branch
    assert chart.zi_hour_policy == "late_zi_same_day"

def test_late_zi_next_day_uses_next_date():
    """late_zi_next_day: 1989-09-21 23:30 → day pillar from 1989-09-22."""
    chart = ENGINE.calculate(
        date(1989, 9, 21), birth_time=time(23, 30),
        zi_hour_policy="late_zi_next_day",
    )
    reference = _day_pillar(date(1989, 9, 22))
    assert chart.day_pillar.heavenly_stem   == reference.heavenly_stem
    assert chart.day_pillar.earthly_branch  == reference.earthly_branch
    assert chart.zi_hour_policy == "late_zi_next_day"

def test_two_policies_yield_different_day_pillars():
    """The two policies must produce different day pillars for 23:xx births."""
    same = ENGINE.calculate(
        date(1989, 9, 21), birth_time=time(23, 30),
        zi_hour_policy="late_zi_same_day",
    )
    next_ = ENGINE.calculate(
        date(1989, 9, 21), birth_time=time(23, 30),
        zi_hour_policy="late_zi_next_day",
    )
    # They reference different dates so at least one pillar field must differ
    assert (same.day_pillar.heavenly_stem  != next_.day_pillar.heavenly_stem or
            same.day_pillar.earthly_branch != next_.day_pillar.earthly_branch)

def test_late_zi_next_day_zi_note_in_accuracy():
    """late_zi_next_day with 23:xx → accuracy_note warns about policy."""
    chart = ENGINE.calculate(
        date(1989, 9, 21), birth_time=time(23, 30),
        zi_hour_policy="late_zi_next_day",
    )
    assert "晚子時" in chart.accuracy_note or "換日" in chart.accuracy_note

def test_late_zi_next_day_not_triggered_at_00():
    """Policy only shifts day for hour==23; 00:30 stays on same date."""
    chart = ENGINE.calculate(
        date(1989, 9, 21), birth_time=time(0, 30),
        zi_hour_policy="late_zi_next_day",
    )
    reference = _day_pillar(date(1989, 9, 21))
    assert chart.day_pillar.heavenly_stem  == reference.heavenly_stem
    assert chart.day_pillar.earthly_branch == reference.earthly_branch


# ── F. Structural: metadata fields always present ────────────────────────────

def test_day_hour_metadata_fields_present():
    chart = ENGINE.calculate(date(1990, 6, 15))
    assert chart.day_pillar_accuracy == "approx"
    assert chart.zi_hour_policy in ("late_zi_same_day", "late_zi_next_day")
    assert isinstance(chart.hour_pillar_is_precise, bool)
    assert isinstance(chart.hour_pillar_accuracy, str)
