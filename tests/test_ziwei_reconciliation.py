"""
Tests for Zi Wei External Chart Reconciliation (V1.7.3).
"""
from __future__ import annotations

import json
from datetime import date, time
import pytest


# ══════════════════════════════════════════════════════════════════════════════
# A. Model instantiation
# ══════════════════════════════════════════════════════════════════════════════

class TestModels:
    def test_external_palace_can_be_created(self):
        from ziwei_reconciliation.models import ExternalZiWeiPalace
        p = ExternalZiWeiPalace(palace_name="命宮", branch="卯", main_stars=["武曲", "七殺"])
        assert p.palace_name == "命宮"
        assert p.branch == "卯"
        assert "武曲" in p.main_stars

    def test_external_palace_defaults_are_empty(self):
        from ziwei_reconciliation.models import ExternalZiWeiPalace
        p = ExternalZiWeiPalace(palace_name="財帛宮")
        assert p.auxiliary_stars == []
        assert p.malefic_stars == []
        assert p.transformations == {}
        assert p.brightness == {}

    def test_external_chart_can_be_created(self):
        from ziwei_reconciliation.models import ExternalZiWeiChart
        c = ExternalZiWeiChart(
            source_name="test",
            birth_solar_date="1989-09-21",
            five_element_bureau="火六局",
            ming_palace_branch="卯",
        )
        assert c.source_name == "test"
        assert c.five_element_bureau == "火六局"
        assert c.ming_palace_branch == "卯"
        assert c.palaces == []
        assert c.luck_score is None

    def test_external_chart_sihua_field(self):
        from ziwei_reconciliation.models import ExternalZiWeiChart
        c = ExternalZiWeiChart(sihua={"武曲": "化祿", "文曲": "化忌"})
        assert c.sihua["武曲"] == "化祿"

    def test_reconciliation_item_can_be_created(self):
        from ziwei_reconciliation.models import ReconciliationItem
        item = ReconciliationItem(
            category="basic",
            field_name="五行局",
            local_value="火六局",
            external_value="爐中火六局",
            status="match",
            severity="info",
            explanation="正規化後一致。",
        )
        assert item.status == "match"
        assert item.status_zh == "一致"
        assert item.severity_zh == "資訊"

    def test_reconciliation_report_can_be_created(self):
        from ziwei_reconciliation.models import ZiWeiReconciliationReport
        r = ZiWeiReconciliationReport(
            created_at="2026-05-28 00:00:00",
            source_name="test",
            overall_status="mostly_match",
            match_count=5,
            mismatch_count=1,
        )
        assert r.overall_status == "mostly_match"
        assert r.overall_status_zh == "大致一致"
        assert r.match_count == 5

    def test_status_zh_mapping_complete(self):
        from ziwei_reconciliation.models import STATUS_ZH
        for key in ("match", "mismatch", "missing_local", "missing_external",
                    "not_implemented", "likely_school_difference"):
            assert key in STATUS_ZH, f"STATUS_ZH missing key: {key}"

    def test_severity_zh_mapping_complete(self):
        from ziwei_reconciliation.models import SEVERITY_ZH
        for key in ("info", "low", "medium", "high"):
            assert key in SEVERITY_ZH, f"SEVERITY_ZH missing key: {key}"


# ══════════════════════════════════════════════════════════════════════════════
# B. Engine basic
# ══════════════════════════════════════════════════════════════════════════════

def _make_local_chart():
    """Generate a real local ZiWeiChart for 1989-09-21 11:05."""
    from engines.ziwei import ZiWeiEngine
    try:
        from lunardate import LunarDate  # noqa: F401
    except ImportError:
        pytest.skip("lunardate not installed")
    return ZiWeiEngine().calculate(date(1989, 9, 21), time(11, 5))


class TestEngineBasic:
    def test_reconcile_with_example_returns_report(self):
        """local chart + example external chart → valid report."""
        from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
        from ziwei_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_CHART
        local = _make_local_chart()
        report = ZiWeiReconciliationEngine().reconcile(local, EXAMPLE_ROSSI_EXTERNAL_CHART)
        assert report is not None

    def test_report_items_not_empty(self):
        from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
        from ziwei_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_CHART
        local = _make_local_chart()
        report = ZiWeiReconciliationEngine().reconcile(local, EXAMPLE_ROSSI_EXTERNAL_CHART)
        assert len(report.items) > 0

    def test_report_markdown_not_empty(self):
        from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
        from ziwei_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_CHART
        local = _make_local_chart()
        report = ZiWeiReconciliationEngine().reconcile(local, EXAMPLE_ROSSI_EXTERNAL_CHART)
        assert len(report.markdown_body) > 100

    def test_overall_status_is_valid(self):
        from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
        from ziwei_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_CHART
        from ziwei_reconciliation.models import VALID_OVERALL_STATUSES
        local = _make_local_chart()
        report = ZiWeiReconciliationEngine().reconcile(local, EXAMPLE_ROSSI_EXTERNAL_CHART)
        assert report.overall_status in VALID_OVERALL_STATUSES

    def test_counts_are_non_negative(self):
        from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
        from ziwei_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_CHART
        local = _make_local_chart()
        report = ZiWeiReconciliationEngine().reconcile(local, EXAMPLE_ROSSI_EXTERNAL_CHART)
        assert report.match_count >= 0
        assert report.mismatch_count >= 0
        assert report.not_implemented_count >= 0
        assert report.school_difference_count >= 0

    def test_summary_is_non_empty(self):
        from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
        from ziwei_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_CHART
        local = _make_local_chart()
        report = ZiWeiReconciliationEngine().reconcile(local, EXAMPLE_ROSSI_EXTERNAL_CHART)
        assert len(report.summary) > 10

    def test_recommendation_is_non_empty(self):
        from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
        from ziwei_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_CHART
        local = _make_local_chart()
        report = ZiWeiReconciliationEngine().reconcile(local, EXAMPLE_ROSSI_EXTERNAL_CHART)
        assert len(report.recommendation) > 10


# ══════════════════════════════════════════════════════════════════════════════
# C. Matching logic
# ══════════════════════════════════════════════════════════════════════════════

class TestMatchingLogic:
    def test_bureau_normalisation_fire6(self):
        """爐中火六局 should normalise to 火六局."""
        from ziwei_reconciliation.engine import _norm_bureau
        assert _norm_bureau("爐中火六局") == "火六局"
        assert _norm_bureau("火六局") == "火六局"

    def test_bureau_normalisation_wood3(self):
        from ziwei_reconciliation.engine import _norm_bureau
        assert _norm_bureau("大林木三局") == "木三局"

    def test_ming_palace_match(self):
        """命宮地支 卯 vs 卯 → match."""
        from ziwei_reconciliation.models import ExternalZiWeiChart
        from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
        local = _make_local_chart()
        # The local chart should have ming_branch set after formal layout
        if not local.ming_branch:
            pytest.skip("local chart has no ming_branch")
        ext = ExternalZiWeiChart(ming_palace_branch=local.ming_branch)
        report = ZiWeiReconciliationEngine().reconcile(local, ext)
        ming_items = [i for i in report.items if i.field_name == "命宮地支"]
        assert any(i.status == "match" for i in ming_items)

    def test_luck_score_is_not_mismatch_high(self):
        """External luck_score → score item exists and is not a high-severity mismatch (V1.7.5: likely_school_difference or not_implemented)."""
        from ziwei_reconciliation.models import ExternalZiWeiChart
        from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
        local = _make_local_chart()
        ext = ExternalZiWeiChart(luck_score=80)
        report = ZiWeiReconciliationEngine().reconcile(local, ext)
        score_items = [i for i in report.items if i.category == "score"]
        assert len(score_items) > 0, "No score items found"
        # V1.7.5: score should be likely_school_difference (since local has Phase1 score) or not_implemented
        # It should never be a high-severity mismatch
        assert not any(
            i.status == "mismatch" and i.severity == "high" for i in score_items
        ), "Score should not be a high-severity mismatch"

    def test_ming_zhu_is_computed(self):
        """V1.7.5: 命主 now computed → match (when external matches local)."""
        from ziwei_reconciliation.models import ExternalZiWeiChart
        from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
        local = _make_local_chart()
        ext = ExternalZiWeiChart(ming_zhu="文曲")
        report = ZiWeiReconciliationEngine().reconcile(local, ext)
        mingzhu_items = [i for i in report.items if i.field_name == "命主"]
        assert len(mingzhu_items) > 0, "命主 item not found"
        # V1.7.5: local now calculates ming_zhu, so status should be match or mismatch (not not_implemented)
        assert not any(i.status == "not_implemented" for i in mingzhu_items), (
            "命主 should no longer be not_implemented in V1.7.5"
        )

    def test_shen_zhu_is_computed(self):
        """V1.7.5: 身主 now computed → match (when external matches local)."""
        from ziwei_reconciliation.models import ExternalZiWeiChart
        from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
        local = _make_local_chart()
        ext = ExternalZiWeiChart(shen_zhu="天機")
        report = ZiWeiReconciliationEngine().reconcile(local, ext)
        shenzhu_items = [i for i in report.items if i.field_name == "身主"]
        assert len(shenzhu_items) > 0, "身主 item not found"
        # V1.7.5: local now calculates shen_zhu, so status should be match or mismatch (not not_implemented)
        assert not any(i.status == "not_implemented" for i in shenzhu_items), (
            "身主 should no longer be not_implemented in V1.7.5"
        )

    def test_star_order_does_not_matter(self):
        """Stars in different order should still match."""
        from ziwei_reconciliation.engine import _stars_match
        assert _stars_match(["武曲", "七殺"], ["七殺", "武曲"]) is True
        assert _stars_match(["武曲"], ["七殺"]) is False


# ══════════════════════════════════════════════════════════════════════════════
# D. Mismatch detection
# ══════════════════════════════════════════════════════════════════════════════

class TestMismatchDetection:
    def test_different_main_stars_produces_mismatch_or_school_diff(self):
        """Completely different main stars → mismatch or likely_school_difference."""
        from ziwei_reconciliation.models import ExternalZiWeiChart, ExternalZiWeiPalace
        from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
        local = _make_local_chart()
        # Use a palace name that local chart has
        palace_name = local.ming_palace.name
        ext = ExternalZiWeiChart(palaces=[
            ExternalZiWeiPalace(
                palace_name=palace_name,
                branch=local.ming_branch or "子",
                main_stars=["天同", "太陰"],  # very different stars
            )
        ])
        report = ZiWeiReconciliationEngine().reconcile(local, ext)
        star_items = [i for i in report.items if i.category == "main_stars"]
        assert any(i.status in ("mismatch", "likely_school_difference") for i in star_items)

    def test_different_palace_branch_severity_high(self):
        """Different palace branch → severity high mismatch."""
        from ziwei_reconciliation.models import ExternalZiWeiChart, ExternalZiWeiPalace
        from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
        local = _make_local_chart()
        palace_name = local.ming_palace.name
        # Use a branch that is definitely wrong
        wrong_branch = "子" if local.ming_branch != "子" else "午"
        ext = ExternalZiWeiChart(palaces=[
            ExternalZiWeiPalace(palace_name=palace_name, branch=wrong_branch)
        ])
        report = ZiWeiReconciliationEngine().reconcile(local, ext)
        branch_items = [i for i in report.items if i.category == "palace_branch"]
        high_mismatches = [i for i in branch_items if i.status == "mismatch" and i.severity == "high"]
        assert len(high_mismatches) > 0

    def test_different_sihua_severity_medium(self):
        """Different sihua → severity medium."""
        from ziwei_reconciliation.models import ExternalZiWeiChart
        from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
        local = _make_local_chart()
        # Provide sihua that conflicts with local four_transformations
        # First find what local化祿 is, then swap it
        local_luru = local.four_transformations
        if not local_luru:
            pytest.skip("local chart has no four_transformations")
        # Find 化祿 star and replace with a wrong one
        lu_star = next((s for s, l in local_luru.items() if l == "化祿"), None)
        wrong_star = "文昌" if lu_star != "文昌" else "廉貞"
        ext = ExternalZiWeiChart(sihua={wrong_star: "化祿"})
        report = ZiWeiReconciliationEngine().reconcile(local, ext)
        sihua_items = [i for i in report.items if i.category == "transformations" and i.field_name == "化祿"]
        assert any(i.status == "mismatch" and i.severity == "medium" for i in sihua_items)


# ══════════════════════════════════════════════════════════════════════════════
# E. Report / Markdown content
# ══════════════════════════════════════════════════════════════════════════════

class TestReportContent:
    def _get_markdown(self):
        from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
        from ziwei_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_CHART
        local = _make_local_chart()
        report = ZiWeiReconciliationEngine().reconcile(local, EXAMPLE_ROSSI_EXTERNAL_CHART)
        return report.markdown_body

    def test_markdown_contains_title(self):
        md = self._get_markdown()
        assert "紫微外部排盤校準報告" in md

    def test_markdown_contains_luck_score_section(self):
        md = self._get_markdown()
        assert "好運指數" in md

    def test_markdown_contains_school_difference_or_liu_pai(self):
        md = self._get_markdown()
        assert "流派差異" in md or "尚未實作" in md

    def test_markdown_contains_not_implemented(self):
        md = self._get_markdown()
        assert "尚未實作" in md

    def test_render_standalone(self):
        """render_reconciliation_markdown should work standalone."""
        from ziwei_reconciliation.models import ZiWeiReconciliationReport, ReconciliationItem
        from ziwei_reconciliation.templates import render_reconciliation_markdown
        item = ReconciliationItem(
            category="basic", field_name="五行局",
            local_value="火六局", external_value="火六局",
            status="match", severity="info",
        )
        report = ZiWeiReconciliationReport(
            created_at="2026-05-28 00:00:00",
            source_name="test",
            overall_status="mostly_match",
            match_count=1,
            items=[item],
            summary="測試摘要",
            recommendation="測試建議",
        )
        report.markdown_body = render_reconciliation_markdown(report)
        assert "紫微外部排盤校準報告" in report.markdown_body
        assert "五行局" in report.markdown_body


# ══════════════════════════════════════════════════════════════════════════════
# F. UI helpers / JSON parsing
# ══════════════════════════════════════════════════════════════════════════════

class TestUIHelpers:
    def test_blank_json_template_is_valid_json(self):
        """BLANK_EXTERNAL_CHART_JSON must be parseable JSON."""
        from ziwei_reconciliation.examples import BLANK_EXTERNAL_CHART_JSON
        parsed = json.loads(BLANK_EXTERNAL_CHART_JSON)
        assert "source_name" in parsed

    def test_example_chart_is_valid_model(self):
        """EXAMPLE_ROSSI_EXTERNAL_CHART must be a valid ExternalZiWeiChart."""
        from ziwei_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_CHART
        from ziwei_reconciliation.models import ExternalZiWeiChart
        assert isinstance(EXAMPLE_ROSSI_EXTERNAL_CHART, ExternalZiWeiChart)
        assert len(EXAMPLE_ROSSI_EXTERNAL_CHART.palaces) > 0

    def test_example_chart_json_roundtrip(self):
        """Example chart can be serialised and deserialised."""
        from ziwei_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_CHART
        from ziwei_reconciliation.models import ExternalZiWeiChart
        dumped = EXAMPLE_ROSSI_EXTERNAL_CHART.model_dump()
        restored = ExternalZiWeiChart(**dumped)
        assert restored.source_name == EXAMPLE_ROSSI_EXTERNAL_CHART.source_name

    def test_status_mapping_no_missing_keys(self):
        """STATUS_ZH must cover all VALID_STATUSES."""
        from ziwei_reconciliation.models import STATUS_ZH, VALID_STATUSES
        for s in VALID_STATUSES:
            assert s in STATUS_ZH, f"STATUS_ZH missing: {s}"

    def test_severity_mapping_no_missing_keys(self):
        """SEVERITY_ZH must cover all VALID_SEVERITIES."""
        from ziwei_reconciliation.models import SEVERITY_ZH, VALID_SEVERITIES
        for s in VALID_SEVERITIES:
            assert s in SEVERITY_ZH, f"SEVERITY_ZH missing: {s}"


# ══════════════════════════════════════════════════════════════════════════════
# G. V1.7.3.1 — Corrected external chart data validation
# ══════════════════════════════════════════════════════════════════════════════

class TestCorrectedExampleChart:
    """Validate the V1.7.3.1 corrected EXAMPLE_ROSSI_EXTERNAL_CHART."""

    def _chart(self):
        from ziwei_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_CHART
        return EXAMPLE_ROSSI_EXTERNAL_CHART

    def test_ming_palace_branch_is_mao(self):
        """命宮地支必須是卯。"""
        assert self._chart().ming_palace_branch == "卯"

    def test_five_element_bureau_is_fire6(self):
        """五行局必須是爐中火六局。"""
        assert self._chart().five_element_bureau == "爐中火六局"

    def test_lunar_date_is_correct(self):
        """農曆日期必須包含 1989-08-22。"""
        assert "1989-08-22" in self._chart().birth_lunar_date

    def test_sihua_wuqu_is_luru(self):
        """武曲四化必須是化祿。"""
        assert self._chart().sihua.get("武曲") == "化祿"

    def test_sihua_tanlang_is_quanlu(self):
        """貪狼四化必須是化權。"""
        assert self._chart().sihua.get("貪狼") == "化權"

    def test_sihua_tianliang_is_ke(self):
        """天梁四化必須是化科。"""
        assert self._chart().sihua.get("天梁") == "化科"

    def test_sihua_wenqu_is_ji(self):
        """文曲四化必須是化忌。"""
        assert self._chart().sihua.get("文曲") == "化忌"

    def test_twelve_palaces_all_present(self):
        """範例外部盤必須有 12 個宮位。"""
        assert len(self._chart().palaces) == 12

    def test_no_duplicate_branches(self):
        """十二宮地支不能互相錯位（不能重複）。"""
        branches = [p.branch for p in self._chart().palaces if p.branch]
        assert len(branches) == len(set(branches)), (
            f"有重複地支：{[b for b in branches if branches.count(b) > 1]}"
        )

    def test_all_twelve_branches_covered(self):
        """十二地支必須全部出現（十二宮全覆蓋）。"""
        expected = {"子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"}
        actual = {p.branch for p in self._chart().palaces if p.branch}
        assert expected == actual, f"缺少地支：{expected - actual}"

    def test_ming_palace_stars_correct(self):
        """命宮主星必須是武曲、七殺。"""
        ming = next(p for p in self._chart().palaces if p.palace_name == "命宮")
        assert set(ming.main_stars) == {"武曲", "七殺"}

    def test_career_palace_branch_is_wei(self):
        """官祿宮地支必須是未（辛未）。"""
        career = next(p for p in self._chart().palaces if p.palace_name == "官祿宮")
        assert career.branch == "未"

    def test_career_palace_stars_correct(self):
        """官祿宮主星必須是紫微、破軍。"""
        career = next(p for p in self._chart().palaces if p.palace_name == "官祿宮")
        assert set(career.main_stars) == {"紫微", "破軍"}

    def test_wealth_palace_branch_is_hai(self):
        """財帛宮地支必須是亥（乙亥）。"""
        wealth = next(p for p in self._chart().palaces if p.palace_name == "財帛宮")
        assert wealth.branch == "亥"

    def test_spouse_palace_branch_is_chou(self):
        """夫妻宮地支必須是丑（丁丑）。"""
        spouse = next(p for p in self._chart().palaces if p.palace_name == "夫妻宮")
        assert spouse.branch == "丑"

    def test_spouse_palace_main_star_is_tianxiang(self):
        """夫妻宮主星必須是天相。"""
        spouse = next(p for p in self._chart().palaces if p.palace_name == "夫妻宮")
        assert "天相" in spouse.main_stars

    def test_fudepalace_has_no_main_stars(self):
        """福德宮無主星。"""
        fude = next(p for p in self._chart().palaces if p.palace_name == "福德宮")
        assert fude.main_stars == []

    def test_wealth_palace_has_tanlang_quanlu(self):
        """財帛宮貪狼化權。"""
        wealth = next(p for p in self._chart().palaces if p.palace_name == "財帛宮")
        assert "貪狼" in wealth.main_stars
        assert wealth.transformations.get("貪狼") == "化權"
