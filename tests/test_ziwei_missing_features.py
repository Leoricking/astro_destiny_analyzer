"""
V1.7.5 Tests: Ming Zhu / Shen Zhu / Tian Ma / Brightness / Score / Reconciliation
"""
import pytest

# ── Helper function unit tests ────────────────────────────────────────────────

from engines.ziwei import (
    _calc_ming_zhu,
    _calc_shen_zhu,
    _calc_tian_ma_branch,
    _get_star_brightness,
)


def test_ming_zhu_mao():
    """命主：卯 → 文曲"""
    assert _calc_ming_zhu("卯") == "文曲"


def test_ming_zhu_zi():
    """命主：子 → 貪狼"""
    assert _calc_ming_zhu("子") == "貪狼"


def test_shen_zhu_si():
    """身主：巳年 → 天機"""
    assert _calc_shen_zhu("巳") == "天機"


def test_shen_zhu_zi():
    """身主：子年 → 火星"""
    assert _calc_shen_zhu("子") == "火星"


def test_tian_ma_si():
    """天馬：巳年 → 亥"""
    assert _calc_tian_ma_branch("巳") == "亥"


def test_tian_ma_yin():
    """天馬：寅年 → 申"""
    assert _calc_tian_ma_branch("寅") == "申"


def test_brightness_wuqu_mao():
    """武曲在卯宮 → 利"""
    assert _get_star_brightness("武曲", "卯") == "利"


def test_brightness_qisha_mao():
    """七殺在卯宮 → 旺"""
    assert _get_star_brightness("七殺", "卯") == "旺"


def test_brightness_ziwei_wei_not_xian():
    """紫微在未宮 → 廟/旺/得 (not 陷/平)"""
    result = _get_star_brightness("紫微", "未")
    assert result in ("廟", "旺", "得", "利"), f"Expected auspicious brightness, got {result}"


# ── Full Rossi chart tests ────────────────────────────────────────────────────

try:
    from lunardate import LunarDate as _LD  # noqa: F401
    _LUNARDATE_OK = True
except ImportError:
    _LUNARDATE_OK = False


@pytest.fixture(scope="module")
def rossi_chart():
    if not _LUNARDATE_OK:
        pytest.skip("lunardate not installed")
    from datetime import date, time
    from engines.ziwei import ZiWeiEngine
    return ZiWeiEngine().calculate(date(1989, 9, 21), time(11, 5))


def test_ming_zhu_rossi(rossi_chart):
    """Rossi 命主 == 文曲"""
    assert rossi_chart.ming_zhu == "文曲"


def test_shen_zhu_rossi(rossi_chart):
    """Rossi 身主 == 天機"""
    assert rossi_chart.shen_zhu == "天機"


def test_tian_ma_branch_rossi(rossi_chart):
    """Rossi 天馬地支 == 亥"""
    assert rossi_chart.tian_ma_branch == "亥"


def test_tian_ma_palace_rossi(rossi_chart):
    """Rossi 天馬落宮 == 財帛宮"""
    assert rossi_chart.tian_ma_palace == "財帛宮"


def test_brightness_wuqu_ming_gong_rossi(rossi_chart):
    """Rossi 命宮武曲廟旺陷 == 利"""
    bmap = rossi_chart.brightness_map
    assert bmap.get("命宮", {}).get("武曲") == "利"


def test_brightness_qisha_ming_gong_rossi(rossi_chart):
    """Rossi 命宮七殺廟旺陷 == 旺"""
    bmap = rossi_chart.brightness_map
    assert bmap.get("命宮", {}).get("七殺") == "旺"


def test_ziwei_score_range_rossi(rossi_chart):
    """Rossi 盤面結構支援度在校準後範圍 78–86（V1.7.6）"""
    assert rossi_chart.ziwei_score is not None
    assert 78 <= rossi_chart.ziwei_score <= 86, (
        f"Rossi ziwei_score 應在 78–86，實際：{rossi_chart.ziwei_score}"
    )


def test_ziwei_score_label_not_empty_rossi(rossi_chart):
    """Rossi 盤面強度分數標籤不為空"""
    assert rossi_chart.ziwei_score_label
    assert len(rossi_chart.ziwei_score_label) > 0


def test_ziwei_score_explanation_rossi(rossi_chart):
    """Rossi 分數說明含免責聲明關鍵字"""
    expl = rossi_chart.ziwei_score_explanation
    assert "不等同外部網站好運指數" in expl or "不等同" in expl


# ── Reconciliation tests ──────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def reconciliation_report(rossi_chart):
    from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
    from ziwei_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_CHART
    return ZiWeiReconciliationEngine().reconcile(rossi_chart, EXAMPLE_ROSSI_EXTERNAL_CHART)


def test_reconciliation_ming_zhu_match(reconciliation_report):
    """命主比對結果為 match"""
    items = reconciliation_report.items
    ming_zhu_items = [i for i in items if i.field_name == "命主"]
    assert len(ming_zhu_items) > 0, "命主比對項目不存在"
    assert ming_zhu_items[0].status == "match", f"命主狀態應為 match，實際：{ming_zhu_items[0].status}"


def test_reconciliation_shen_zhu_match(reconciliation_report):
    """身主比對結果為 match"""
    items = reconciliation_report.items
    shen_zhu_items = [i for i in items if i.field_name == "身主"]
    assert len(shen_zhu_items) > 0, "身主比對項目不存在"
    assert shen_zhu_items[0].status == "match", f"身主狀態應為 match，實際：{shen_zhu_items[0].status}"


def test_reconciliation_tian_ma_match(reconciliation_report):
    """天馬比對結果為 match"""
    items = reconciliation_report.items
    tian_ma_items = [i for i in items if i.field_name == "天馬位置"]
    assert len(tian_ma_items) > 0, "天馬位置比對項目不存在"
    assert tian_ma_items[0].status == "match", f"天馬狀態應為 match，實際：{tian_ma_items[0].status}"


def test_reconciliation_no_high_mismatch_score(reconciliation_report):
    """分數比對項目無 severity=high 的 mismatch"""
    items = reconciliation_report.items
    bad_items = [
        i for i in items
        if i.category == "score" and i.status == "mismatch" and i.severity == "high"
    ]
    assert len(bad_items) == 0, f"發現高嚴重度分數 mismatch: {bad_items}"


def test_reconciliation_overall_status(reconciliation_report):
    """整體狀態應為 mostly_match"""
    assert reconciliation_report.overall_status == "mostly_match", (
        f"整體狀態：{reconciliation_report.overall_status}"
    )


def test_reconciliation_brightness_not_not_implemented(reconciliation_report):
    """廟旺陷比對結果不應為 not_implemented（應為 match 或 likely_school_difference）"""
    items = reconciliation_report.items
    brightness_items = [i for i in items if i.category == "brightness"]
    for item in brightness_items:
        assert item.status != "not_implemented", (
            f"廟旺陷仍為 not_implemented: {item.field_name}"
        )
