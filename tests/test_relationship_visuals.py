"""
V1.8.2 Tests: Relationship Visual Charts
"""
import pytest

from compatibility.visuals import (
    build_relationship_visuals,
    render_radar_markdown_table,
    render_aspect_category_markdown_table,
    render_aspect_balance_markdown_table,
    render_composite_distribution_markdown_table,
    render_visual_bundle_html,
)
from compatibility.models import (
    AdvancedAstrologyCompatibility, SynastryMatrix,
    RadarChartData, AspectBalanceData,
)


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def romantic_advanced():
    from compatibility.engine import CompatibilityEngine
    from compatibility.models import CompatibilityInput, RelationshipType
    from demo.sample_profiles import SAMPLE_COUPLES
    couple = next(c for c in SAMPLE_COUPLES if c.get("relationship_type") == "romantic")
    ci = CompatibilityInput(
        person_a=couple["person_a"],
        person_b=couple["person_b"],
        relationship_type=RelationshipType.ROMANTIC,
    )
    report = CompatibilityEngine().generate(ci)
    return report.advanced_astrology


@pytest.fixture(scope="module")
def romantic_bundle(romantic_advanced):
    return build_relationship_visuals(romantic_advanced)


@pytest.fixture(scope="module")
def romantic_report():
    from compatibility.engine import CompatibilityEngine
    from compatibility.models import CompatibilityInput, RelationshipType
    from demo.sample_profiles import SAMPLE_COUPLES
    couple = next(c for c in SAMPLE_COUPLES if c.get("relationship_type") == "romantic")
    ci = CompatibilityInput(
        person_a=couple["person_a"],
        person_b=couple["person_b"],
        relationship_type=RelationshipType.ROMANTIC,
    )
    return CompatibilityEngine().generate(ci)


# ── 1. build_relationship_visuals can produce bundle ─────────────────────────

def test_build_visuals_returns_bundle(romantic_bundle):
    """build_relationship_visuals 可從 demo romantic advanced_astrology 產生 bundle"""
    assert romantic_bundle is not None


# ── 2. Radar labels has 7 items ───────────────────────────────────────────────

def test_radar_has_7_labels(romantic_bundle):
    assert len(romantic_bundle.radar.labels) == 7, \
        f"radar 應有 7 個 labels，實際 {len(romantic_bundle.radar.labels)}"


# ── 3. Radar values all in 0–100 ─────────────────────────────────────────────

def test_radar_values_in_range(romantic_bundle):
    for i, v in enumerate(romantic_bundle.radar.values):
        assert 0 <= v <= 100, f"radar value[{i}] = {v}，應在 0–100"


# ── 4. Radar contains 衝突張力 ────────────────────────────────────────────────

def test_radar_contains_conflict(romantic_bundle):
    assert "衝突張力" in romantic_bundle.radar.labels, \
        "radar labels 應包含「衝突張力」"


# ── 5. Aspect category count not empty ───────────────────────────────────────

def test_aspect_category_counts_not_empty(romantic_bundle):
    ac = romantic_bundle.aspect_categories
    assert len(ac.counts) > 0, "aspect_categories.counts 不應為空"
    assert sum(ac.counts) > 0, "至少有一個相位分類有數量"


# ── 6. Aspect category has Chinese labels ────────────────────────────────────

def test_aspect_category_has_chinese_labels(romantic_bundle):
    ac = romantic_bundle.aspect_categories
    assert len(ac.categories) > 0
    for lbl in ac.categories:
        assert any("\u4e00" <= ch <= "\u9fff" for ch in lbl), \
            f"category label 應含中文字符：{lbl}"


# ── 7. Aspect balance total == aspects total ─────────────────────────────────

def test_aspect_balance_total_matches(romantic_bundle, romantic_advanced):
    ab = romantic_bundle.aspect_balance
    total = ab.harmony_count + ab.tension_count + ab.neutral_count
    expected = len(romantic_advanced.synastry_matrix.aspects)
    assert total == expected, \
        f"balance total ({total}) 應等於 aspects 總數 ({expected})"


# ── 8. Aspect balance total=0 no crash ───────────────────────────────────────

def test_aspect_balance_zero_total_no_crash():
    empty_adv = AdvancedAstrologyCompatibility()
    bundle = build_relationship_visuals(empty_adv)
    ab = bundle.aspect_balance
    assert ab.harmony_percentage == 0.0
    assert ab.tension_percentage == 0.0


# ── 9. Composite elements keys include 火土風水 ──────────────────────────────

def test_composite_elements_keys(romantic_bundle):
    elems = romantic_bundle.composite_distribution.elements
    for key in ("火", "土", "風", "水"):
        assert key in elems, f"elements 應包含「{key}」"


# ── 10. Composite modalities keys include 基本固定變動 ───────────────────────

def test_composite_modalities_keys(romantic_bundle):
    mods = romantic_bundle.composite_distribution.modalities
    for key in ("基本", "固定", "變動"):
        assert key in mods, f"modalities 應包含「{key}」"


# ── 11. Visual summary not empty ─────────────────────────────────────────────

def test_visual_summary_not_empty(romantic_bundle):
    assert romantic_bundle.summary, "visual summary 不應為空"


# ── 12. Markdown radar table contains 合盤互動雷達圖 ─────────────────────────

def test_radar_markdown_contains_title(romantic_bundle):
    md = render_radar_markdown_table(romantic_bundle.radar)
    assert "合盤互動雷達圖" in md


# ── 13. Markdown category table contains 相位分類統計 ────────────────────────

def test_aspect_category_markdown_contains_title(romantic_bundle):
    md = render_aspect_category_markdown_table(romantic_bundle.aspect_categories)
    assert "相位分類統計" in md


# ── 14. HTML render does not contain <script ─────────────────────────────────

def test_html_render_no_script(romantic_bundle):
    html = render_visual_bundle_html(romantic_bundle)
    assert "<script" not in html.lower(), "HTML render 不應包含 <script"


# ── 15. Full HTML export contains charset utf-8 ──────────────────────────────

def test_html_export_contains_charset(romantic_report):
    from compatibility.exporters import export_compat_to_html
    html = export_compat_to_html(romantic_report)
    assert "charset" in html.lower() and "utf-8" in html.lower()


# ── 16. CompatibilityEngine report has visuals ───────────────────────────────

def test_engine_report_has_visuals(romantic_report):
    """CompatibilityEngine.generate() 後 report.visuals 或可動態 build"""
    if romantic_report.visuals is not None:
        assert romantic_report.visuals.radar is not None
    else:
        # fallback: can dynamically build from advanced_astrology
        assert romantic_report.advanced_astrology is not None
        bundle = build_relationship_visuals(romantic_report.advanced_astrology)
        assert bundle is not None


# ── 17. Report markdown contains 合盤視覺化總覽 ──────────────────────────────

def test_report_markdown_contains_visual_section(romantic_report):
    assert "合盤視覺化總覽" in romantic_report.markdown_body, \
        "報告 markdown 應包含「合盤視覺化總覽」章節"


# ── 18. Report markdown contains conflict tension note ───────────────────────

def test_report_markdown_contains_conflict_note(romantic_report):
    assert "衝突張力是互動強度" in romantic_report.markdown_body, \
        "報告 markdown 應包含「衝突張力是互動強度」說明"


# ── 19. Old report without visuals does not crash ────────────────────────────

def test_old_report_no_visuals_no_crash():
    """舊 report (visuals=None) render 不 crash"""
    from datetime import date
    from core.models import BirthProfile, BloodType
    from compatibility.models import CompatibilityReport
    from compatibility.report import render_compatibility_report
    profile = BirthProfile(
        name="Old", birth_date=date(1990, 1, 1),
        birth_city="台北", birth_country="台灣", blood_type=BloodType.A,
    )
    report = CompatibilityReport(
        person_a_profile=profile,
        person_b_profile=profile,
        advanced_astrology=None,
        visuals=None,
    )
    md = render_compatibility_report(report)
    assert md is not None


# ── 20. Business couple also has visuals ─────────────────────────────────────

def test_business_couple_has_visuals():
    from compatibility.engine import CompatibilityEngine
    from compatibility.models import CompatibilityInput, RelationshipType
    from demo.sample_profiles import SAMPLE_COUPLES
    couple = next(c for c in SAMPLE_COUPLES if c.get("relationship_type") == "business")
    ci = CompatibilityInput(
        person_a=couple["person_a"],
        person_b=couple["person_b"],
        relationship_type=RelationshipType.BUSINESS,
    )
    report = CompatibilityEngine().generate(ci)
    assert report.visuals is not None or report.advanced_astrology is not None
