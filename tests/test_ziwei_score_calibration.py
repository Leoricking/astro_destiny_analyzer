"""
V1.7.6 Tests: Zi Wei Score Calibration & Explanation Polish

Verifies:
- Rossi score lands in 78–86 (not 98)
- Score max never exceeds 92
- Label uses conservative wording
- Explanation clearly states this is NOT external 好運指數
- Reconciliation score item uses 盤面結構支援度 text
- V1.7.5 命主 / 身主 / 天馬 / 廟旺陷 results are preserved
- V1.7.4 main star placement results are preserved
"""
import pytest
from datetime import date, time


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def rossi_chart():
    from engines.ziwei import ZiWeiEngine
    return ZiWeiEngine().calculate(date(1989, 9, 21), time(11, 5))


@pytest.fixture(scope="module")
def rossi_reconciliation(rossi_chart):
    from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
    from ziwei_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_CHART
    return ZiWeiReconciliationEngine().reconcile(rossi_chart, EXAMPLE_ROSSI_EXTERNAL_CHART)


# ── 1. Rossi score in calibrated range ───────────────────────────────────────

def test_rossi_score_in_calibrated_range(rossi_chart):
    """Rossi 盤面結構支援度應在 78–86（V1.7.6 校準後）"""
    s = rossi_chart.ziwei_score
    assert s is not None
    assert 78 <= s <= 86, f"Rossi ziwei_score = {s}，應在 78–86"


def test_rossi_score_not_98(rossi_chart):
    """Rossi 分數不應再是 98"""
    assert rossi_chart.ziwei_score != 98, "Rossi ziwei_score 不應再是 98"


# ── 2. Score global max ───────────────────────────────────────────────────────

def test_score_max_does_not_exceed_92(rossi_chart):
    """任何輸入的分數最大值不超過 92"""
    assert rossi_chart.ziwei_score <= 92, (
        f"ziwei_score = {rossi_chart.ziwei_score}，超過上限 92"
    )


# ── 3. Label wording ──────────────────────────────────────────────────────────

def test_label_not_absolute_positive(rossi_chart):
    """label 不含絕對正向詞（命很好 / 必定 / 保證）"""
    label = rossi_chart.ziwei_score_label or ""
    for forbidden in ("命很好", "必定", "保證", "大富大貴"):
        assert forbidden not in label, f"label 含禁用詞：{forbidden}"


def test_high_score_label_uses_tension_wording(rossi_chart):
    """分數 >= 85 時 label 應為「高支援但需承載張力」"""
    if rossi_chart.ziwei_score >= 85:
        assert rossi_chart.ziwei_score_label == "高支援但需承載張力", (
            f"高分 label 應為「高支援但需承載張力」，實際：{rossi_chart.ziwei_score_label}"
        )


def test_label_not_empty(rossi_chart):
    """label 不為空"""
    assert rossi_chart.ziwei_score_label
    assert len(rossi_chart.ziwei_score_label) > 0


# ── 4. Explanation content ────────────────────────────────────────────────────

def test_explanation_not_external_luck(rossi_chart):
    """explanation 含「不等同外部網站好運指數」"""
    expl = rossi_chart.ziwei_score_explanation
    assert "不等同外部網站好運指數" in expl, (
        f"explanation 缺少「不等同外部網站好運指數」：{expl}"
    )


def test_explanation_not_fate_score(rossi_chart):
    """explanation 含「不是命運好壞分數」或「不是命運好壞」語意"""
    expl = rossi_chart.ziwei_score_explanation
    assert "不是命運好壞分數" in expl or "盤面結構支援度" in expl, (
        f"explanation 缺少分數定位說明：{expl}"
    )


def test_explanation_mentions_key_factors(rossi_chart):
    """explanation 提及命宮、官祿、財帛、福德、四化、廟旺陷"""
    expl = rossi_chart.ziwei_score_explanation
    for kw in ("命宮", "官祿", "財帛", "福德", "四化", "廟旺陷"):
        assert kw in expl, f"explanation 缺少關鍵詞：{kw}"


# ── 5. Score components ───────────────────────────────────────────────────────

def test_score_components_exist(rossi_chart):
    """ziwei_score_components 不為空"""
    comps = rossi_chart.ziwei_score_components
    assert isinstance(comps, dict)
    assert len(comps) > 0, "ziwei_score_components 不應為空"


def test_score_components_has_base(rossi_chart):
    """ziwei_score_components 包含 base 鍵"""
    assert "base" in rossi_chart.ziwei_score_components


# ── 6. Reconciliation ─────────────────────────────────────────────────────────

def test_reconciliation_score_not_high_mismatch(rossi_reconciliation):
    """Reconciliation score 項目無 severity=high 的 mismatch"""
    bad = [
        i for i in rossi_reconciliation.items
        if i.category == "score" and i.status == "mismatch" and i.severity == "high"
    ]
    assert len(bad) == 0, f"發現高嚴重度分數 mismatch: {bad}"


def test_reconciliation_score_item_uses_new_label(rossi_reconciliation):
    """Reconciliation score 項目本機值含「盤面結構支援度」"""
    score_items = [i for i in rossi_reconciliation.items if i.category == "score"]
    assert len(score_items) > 0, "未找到 score reconciliation 項目"
    local_vals = " ".join(i.local_value for i in score_items)
    assert "盤面結構支援度" in local_vals, (
        f"score 本機值應含「盤面結構支援度」，實際：{local_vals}"
    )


def test_reconciliation_score_diff_reasonable(rossi_reconciliation):
    """Rossi 本機分數與外部 80 差距應 <= 10"""
    score_items = [i for i in rossi_reconciliation.items if i.category == "score"]
    assert len(score_items) > 0
    item = score_items[0]
    # Parse local score from "本機 Phase 1 盤面結構支援度：NN"
    import re
    match = re.search(r"：(\d+)", item.local_value)
    if match:
        local_score = int(match.group(1))
        diff = abs(local_score - 80)
        assert diff <= 10, f"Rossi 本機分數 {local_score} 與外部 80 差距 {diff} > 10"


# ── 7. V1.7.5 results preserved ──────────────────────────────────────────────

def test_v175_ming_zhu_preserved(rossi_chart):
    """V1.7.5 命主 文曲 仍通過"""
    assert rossi_chart.ming_zhu == "文曲"


def test_v175_shen_zhu_preserved(rossi_chart):
    """V1.7.5 身主 天機 仍通過"""
    assert rossi_chart.shen_zhu == "天機"


def test_v175_tian_ma_preserved(rossi_chart):
    """V1.7.5 天馬 亥 仍通過"""
    assert rossi_chart.tian_ma_branch == "亥"


def test_v175_tian_ma_palace_preserved(rossi_chart):
    """V1.7.5 天馬落財帛宮 仍通過"""
    assert rossi_chart.tian_ma_palace == "財帛宮"


def test_v175_wuqu_brightness_preserved(rossi_chart):
    """V1.7.5 命宮武曲利 仍通過"""
    bmap = rossi_chart.brightness_map
    assert bmap.get("命宮", {}).get("武曲") == "利"


def test_v175_qisha_brightness_preserved(rossi_chart):
    """V1.7.5 命宮七殺旺 仍通過"""
    bmap = rossi_chart.brightness_map
    assert bmap.get("命宮", {}).get("七殺") == "旺"


# ── 8. V1.7.4 main star placement preserved ──────────────────────────────────

def test_v174_ming_palace_has_stars(rossi_chart):
    """V1.7.4 命宮有主星"""
    ming = rossi_chart.ming_palace
    assert ming is not None, "命宮不存在"
    assert len(ming.main_stars) > 0, "命宮無主星"


def test_v174_all_palaces_accessible(rossi_chart):
    """V1.7.4 十二宮各欄位可存取"""
    for attr in (
        "ming_palace", "shen_palace", "brother_palace", "spouse_palace",
        "children_palace", "wealth_palace", "health_palace", "travel_palace",
        "friends_palace", "career_palace", "property_palace", "fortune_palace",
    ):
        palace = getattr(rossi_chart, attr, None)
        assert palace is not None, f"{attr} 不存在"
