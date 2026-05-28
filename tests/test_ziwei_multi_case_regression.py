"""
V1.7.7 Tests: Zi Wei Multi-Case Regression & Accuracy Guardrails

Prevents overfitting to Rossi-only case. Tests multiple birth date/time/gender
combinations for correctness, completeness, and non-crash guarantees.
"""
import pytest
from datetime import date, time

from engines.ziwei import ZiWeiEngine
from core.models import Gender

_ENGINE = ZiWeiEngine()

_VALID_BRANCHES = {"子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"}
_VALID_BRIGHTNESS = {"廟", "旺", "得", "利", "平", "陷"}


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def rossi_chart():
    """Golden case: Rossi 1989-09-21 11:05"""
    return _ENGINE.calculate(date(1989, 9, 21), time(11, 5))


@pytest.fixture(scope="module")
def same_date_diff_time_chart():
    """Same date as Rossi but 亥時 (22:30) — 命宮 / 身宮 should differ"""
    return _ENGINE.calculate(date(1989, 9, 21), time(22, 30))


@pytest.fixture(scope="module")
def diff_year_chart():
    """Different year: 1995-03-15 08:30 — tests 命主 / 身主 / 天馬 for different year branch"""
    return _ENGINE.calculate(date(1995, 3, 15), time(8, 30))


@pytest.fixture(scope="module")
def female_chart():
    """Female gender: same date/time as Rossi — tests 大限 direction logic"""
    return _ENGINE.calculate(date(1989, 9, 21), time(11, 5), gender=Gender.FEMALE)


@pytest.fixture(scope="module")
def no_time_chart():
    """Unknown birth time — should be partial_lunar_only, not formal_layout_phase1"""
    return _ENGINE.calculate(date(1985, 6, 20))


@pytest.fixture(scope="module")
def no_gender_chart():
    """No gender provided — 大限 direction should be 'unknown'"""
    return _ENGINE.calculate(date(1990, 4, 10), time(14, 0))


# ── 1–6. Rossi golden case preservation ──────────────────────────────────────

def test_rossi_ming_palace_direction(rossi_chart):
    """Rossi 命宮地支仍為卯"""
    assert rossi_chart.ming_branch == "卯", (
        f"Rossi ming_branch = {rossi_chart.ming_branch}，應為卯"
    )


def test_rossi_main_stars_in_ming(rossi_chart):
    """Rossi 命宮主星仍為武曲 + 七殺"""
    stars = rossi_chart.ming_palace.main_stars
    assert "武曲" in stars, f"命宮缺武曲，實際：{stars}"
    assert "七殺" in stars, f"命宮缺七殺，實際：{stars}"


def test_rossi_ming_zhu(rossi_chart):
    """Rossi 命主仍為文曲"""
    assert rossi_chart.ming_zhu == "文曲"


def test_rossi_shen_zhu(rossi_chart):
    """Rossi 身主仍為天機"""
    assert rossi_chart.shen_zhu == "天機"


def test_rossi_tian_ma(rossi_chart):
    """Rossi 天馬仍在亥 / 財帛宮"""
    assert rossi_chart.tian_ma_branch == "亥"
    assert rossi_chart.tian_ma_palace == "財帛宮"


def test_rossi_score_still_in_range(rossi_chart):
    """Rossi 盤面結構支援度仍在 78–86"""
    s = rossi_chart.ziwei_score
    assert s is not None
    assert 78 <= s <= 86, f"Rossi score = {s}，應在 78–86"


# ── 7. Same date / different time — no crash, data complete ──────────────────

def test_diff_time_no_crash(same_date_diff_time_chart):
    """不同時辰不 crash"""
    assert same_date_diff_time_chart is not None


def test_diff_time_is_formal(same_date_diff_time_chart):
    """不同時辰 (有 birth_time) 應為 formal_layout_phase1"""
    assert same_date_diff_time_chart.calculation_mode == "formal_layout_phase1"


def test_diff_time_ming_palace_differs_from_rossi(same_date_diff_time_chart):
    """亥時命宮地支應與卯時 Rossi 不同"""
    assert same_date_diff_time_chart.ming_branch != "卯", (
        "同日期但不同時辰，命宮地支應不同"
    )


def test_diff_time_twelve_palaces(same_date_diff_time_chart):
    """不同時辰仍有完整十二宮"""
    _assert_twelve_palaces(same_date_diff_time_chart)


# ── 8. Different year — no crash ─────────────────────────────────────────────

def test_diff_year_no_crash(diff_year_chart):
    """不同年份不 crash"""
    assert diff_year_chart is not None


def test_diff_year_ming_zhu_computable(diff_year_chart):
    """不同年份命主可算"""
    assert diff_year_chart.ming_zhu is not None
    assert len(diff_year_chart.ming_zhu) > 0


def test_diff_year_shen_zhu_computable(diff_year_chart):
    """不同年份身主可算"""
    assert diff_year_chart.shen_zhu is not None


def test_diff_year_tian_ma_valid(diff_year_chart):
    """不同年份天馬地支為合法地支"""
    if diff_year_chart.tian_ma_branch:
        assert diff_year_chart.tian_ma_branch in _VALID_BRANCHES, (
            f"天馬地支 {diff_year_chart.tian_ma_branch} 不合法"
        )


# ── 9. Different gender — no crash ────────────────────────────────────────────

def test_female_no_crash(female_chart):
    """女性不 crash"""
    assert female_chart is not None


def test_female_daxian_direction_is_forward(female_chart):
    """陰年女性大限方向為順行（forward）"""
    # 己巳年（1989）屬陰年，陰年女命順行
    assert female_chart.da_xian_direction == "forward", (
        f"陰年女命大限方向應為 forward，實際：{female_chart.da_xian_direction}"
    )


def test_female_differs_from_male_daxian(rossi_chart, female_chart):
    """男女大限方向不同"""
    assert rossi_chart.da_xian_direction != female_chart.da_xian_direction, (
        "男女大限方向應不同"
    )


# ── 10. Unknown gender — da_xian_direction = "unknown" ───────────────────────

def test_no_gender_daxian_direction_unknown(no_gender_chart):
    """未知性別時大限方向為 unknown"""
    assert no_gender_chart.da_xian_direction == "unknown", (
        f"未知性別大限方向應為 unknown，實際：{no_gender_chart.da_xian_direction}"
    )


# ── 11. Unknown birth time — not formal_layout_phase1 ────────────────────────

def test_no_time_not_formal(no_time_chart):
    """未知出生時間不應為 formal_layout_phase1"""
    assert no_time_chart.calculation_mode != "formal_layout_phase1", (
        f"未知時辰不應標為 formal_layout_phase1，實際：{no_time_chart.calculation_mode}"
    )


def test_no_time_is_partial_lunar(no_time_chart):
    """未知出生時間應為 partial_lunar_only"""
    assert no_time_chart.calculation_mode == "partial_lunar_only", (
        f"未知時辰應為 partial_lunar_only，實際：{no_time_chart.calculation_mode}"
    )


# ── 12–13. Formal charts: 12 palaces, unique branches ────────────────────────

def _assert_twelve_palaces(zc):
    """Helper: verify all 12 canonical palace fields exist and are non-None."""
    palace_attrs = [
        "ming_palace", "brother_palace", "spouse_palace", "children_palace",
        "wealth_palace", "health_palace", "travel_palace", "friends_palace",
        "career_palace", "property_palace", "fortune_palace", "parents_palace",
    ]
    for attr in palace_attrs:
        p = getattr(zc, attr, None)
        assert p is not None, f"{attr} 不存在"


def _assert_no_duplicate_branches(zc):
    """Helper: verify 12 canonical palace branches are all distinct.
    Note: shen_palace shares a branch with one of the 12 and is excluded here.
    """
    palace_attrs = [
        "ming_palace", "brother_palace", "spouse_palace", "children_palace",
        "wealth_palace", "health_palace", "travel_palace", "friends_palace",
        "career_palace", "property_palace", "fortune_palace", "parents_palace",
    ]
    branches = [getattr(zc, attr).earthly_branch for attr in palace_attrs]
    assert len(set(branches)) == 12, f"十二宮地支有重複或缺漏：{branches}"


@pytest.mark.parametrize("fixture_name", [
    "rossi_chart", "same_date_diff_time_chart", "diff_year_chart", "female_chart",
])
def test_formal_chart_has_twelve_palaces(fixture_name, request):
    """所有 formal chart 都有完整十二宮"""
    zc = request.getfixturevalue(fixture_name)
    _assert_twelve_palaces(zc)


@pytest.mark.parametrize("fixture_name", [
    "rossi_chart", "same_date_diff_time_chart", "diff_year_chart", "female_chart",
])
def test_formal_chart_no_duplicate_branches(fixture_name, request):
    """所有 formal chart 十二宮地支不重複不缺漏"""
    zc = request.getfixturevalue(fixture_name)
    _assert_no_duplicate_branches(zc)


# ── 14. Main stars not all empty ──────────────────────────────────────────────

@pytest.mark.parametrize("fixture_name", [
    "rossi_chart", "same_date_diff_time_chart", "diff_year_chart",
])
def test_main_stars_not_all_empty(fixture_name, request):
    """所有 formal chart 主星總數合理，不全空宮"""
    zc = request.getfixturevalue(fixture_name)
    palace_attrs = [
        "ming_palace", "brother_palace", "spouse_palace", "children_palace",
        "wealth_palace", "health_palace", "travel_palace", "friends_palace",
        "career_palace", "property_palace", "fortune_palace", "parents_palace",
    ]
    total_stars = sum(len(getattr(zc, a).main_stars) for a in palace_attrs)
    assert total_stars >= 10, f"主星總數 {total_stars} 過少，疑似全空宮"


# ── 15. 天馬 is a valid branch ────────────────────────────────────────────────

@pytest.mark.parametrize("fixture_name", [
    "rossi_chart", "diff_year_chart", "female_chart",
])
def test_tian_ma_branch_is_valid(fixture_name, request):
    """天馬地支必須為合法地支"""
    zc = request.getfixturevalue(fixture_name)
    if zc.tian_ma_branch:
        assert zc.tian_ma_branch in _VALID_BRANCHES, (
            f"天馬地支 {zc.tian_ma_branch} 不合法"
        )


# ── 16. 廟旺陷 values are valid ───────────────────────────────────────────────

@pytest.mark.parametrize("fixture_name", [
    "rossi_chart", "diff_year_chart",
])
def test_brightness_values_valid(fixture_name, request):
    """廟旺陷值只允許：廟、旺、得、利、平、陷"""
    zc = request.getfixturevalue(fixture_name)
    bmap = getattr(zc, "brightness_map", {}) or {}
    for palace_name, star_map in bmap.items():
        for star, bv in star_map.items():
            assert bv in _VALID_BRIGHTNESS, (
                f"{palace_name} {star} 廟旺陷值 '{bv}' 不合法"
            )


# ── 17. ziwei_score in 30–92 ──────────────────────────────────────────────────

@pytest.mark.parametrize("fixture_name", [
    "rossi_chart", "same_date_diff_time_chart", "diff_year_chart", "female_chart",
])
def test_ziwei_score_in_global_range(fixture_name, request):
    """ziwei_score 必須在 30–92"""
    zc = request.getfixturevalue(fixture_name)
    s = zc.ziwei_score
    if s is not None:
        assert 30 <= s <= 92, f"{fixture_name} ziwei_score = {s}，應在 30–92"


# ── 18. explanation contains required text ────────────────────────────────────

@pytest.mark.parametrize("fixture_name", [
    "rossi_chart", "diff_year_chart",
])
def test_explanation_contains_not_fate_score(fixture_name, request):
    """ziwei_score_explanation 包含「不是命運好壞分數」"""
    zc = request.getfixturevalue(fixture_name)
    expl = zc.ziwei_score_explanation
    assert "不是命運好壞分數" in expl, (
        f"{fixture_name} explanation 缺少「不是命運好壞分數」：{expl}"
    )


# ── 19. Reconciliation golden case ───────────────────────────────────────────

def test_reconciliation_golden_case(rossi_chart):
    """Reconciliation golden case (Rossi) 仍是 mostly_match"""
    from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
    from ziwei_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_CHART
    report = ZiWeiReconciliationEngine().reconcile(rossi_chart, EXAMPLE_ROSSI_EXTERNAL_CHART)
    assert report.overall_status == "mostly_match", (
        f"Rossi reconciliation 整體狀態應為 mostly_match，實際：{report.overall_status}"
    )
