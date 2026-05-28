"""
V1.8.1 Tests: Relationship Report UI Polish helpers and display quality
"""
import pytest
from datetime import date

from compatibility.advanced_astrology import (
    aspect_type_zh, category_zh, aspect_nature, format_orb, aspect_to_display_dict,
    CONFLICT_CAPTION, COMPOSITE_INTRO, ADVANCED_SCORE_DISCLAIMER, SYNASTRY_INTRO,
)
from compatibility.models import SynastryAspect


# ── 1–3. Display mapping correctness ─────────────────────────────────────────

def test_aspect_type_zh_trine():
    assert aspect_type_zh("trine") == "三分相"


def test_aspect_type_zh_square():
    assert aspect_type_zh("square") == "四分相"


def test_category_zh_attraction():
    assert category_zh("attraction") == "吸引力"


# ── 4–5. Display dict structure ───────────────────────────────────────────────

@pytest.fixture
def sample_aspect():
    return SynastryAspect(
        person_a_planet="太陽",
        person_b_planet="月亮",
        aspect_type="trine",
        angle=120.0,
        orb=1.5,
        strength=85,
        category="emotional",
        interpretation="太陽（A）與月亮（B）形成三合，情感頻率接近。",
        is_harmonious=True,
        is_challenging=False,
    )


def test_display_dict_has_chinese_columns(sample_aspect):
    d = aspect_to_display_dict(sample_aspect)
    for col in ("A 行星", "B 行星", "相位", "容許度 orb", "強度", "分類", "性質", "解讀"):
        assert col in d, f"display dict 缺少欄位：{col}"


def test_display_dict_orb_has_degree_symbol(sample_aspect):
    d = aspect_to_display_dict(sample_aspect)
    assert "°" in d["容許度 orb"], "orb 欄位應包含度數符號 °"


# ── 6. Strongest aspects sorted by strength desc ─────────────────────────────

def test_strongest_aspects_sorted_strength_desc():
    from reports.generator import ReportGenerator
    from demo.sample_profiles import SAMPLE_COUPLES
    from compatibility.advanced_astrology import _calculate_synastry_aspects
    gen = ReportGenerator()
    couple = next(c for c in SAMPLE_COUPLES if c.get("relationship_type") == "romantic")
    ra = gen.generate(couple["person_a"], persist=False)
    rb = gen.generate(couple["person_b"], persist=False)
    sm = _calculate_synastry_aspects(ra.western_chart, rb.western_chart)
    strengths = [a.strength for a in sm.strongest_aspects]
    assert strengths == sorted(strengths, reverse=True), \
        "strongest_aspects 應依 strength 由高到低排序"


# ── 7. Filter by category ─────────────────────────────────────────────────────

def test_filter_by_category():
    from reports.generator import ReportGenerator
    from demo.sample_profiles import SAMPLE_COUPLES
    from compatibility.advanced_astrology import _calculate_synastry_aspects
    gen = ReportGenerator()
    couple = next(c for c in SAMPLE_COUPLES if c.get("relationship_type") == "romantic")
    ra = gen.generate(couple["person_a"], persist=False)
    rb = gen.generate(couple["person_b"], persist=False)
    sm = _calculate_synastry_aspects(ra.western_chart, rb.western_chart)
    filtered = [a for a in sm.aspects if category_zh(a.category) == "吸引力"]
    assert all(a.category == "attraction" for a in filtered), \
        "吸引力篩選結果應全為 attraction 類別"


# ── 8. Conflict caption text exists ──────────────────────────────────────────

def test_conflict_caption_text():
    assert "衝突張力高不等於不適合" in CONFLICT_CAPTION


# ── 9. Composite explanation contains 共同場域 ────────────────────────────────

def test_composite_intro_contains_shared_domain():
    assert "共同場域" in COMPOSITE_INTRO


# ── 10. Advanced score disclaimer contains 不是絕對適合度 ──────────────────────

def test_advanced_score_disclaimer_contains_key_phrase():
    assert "不是絕對適合度" in ADVANCED_SCORE_DISCLAIMER


# ── 11–13. Report markdown contains required sections ────────────────────────

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


def test_report_markdown_contains_advanced_astrology(romantic_report):
    assert "進階西洋合盤" in romantic_report.markdown_body


def test_report_markdown_contains_synastry_section(romantic_report):
    assert "相位矩陣" in romantic_report.markdown_body or "Synastry" in romantic_report.markdown_body


def test_report_markdown_contains_composite_chart(romantic_report):
    assert "Composite Chart" in romantic_report.markdown_body


# ── 14. Report markdown does not contain forbidden absolute phrases ───────────

def test_report_markdown_no_forbidden_phrases(romantic_report):
    # These phrases should never appear in assertive positive claims.
    # Note: 「命中注定」 may appear quoted/negated in the Red Flag section
    # (e.g. "不代表任何人「命中注定」要受苦") — that usage is correct and NOT forbidden.
    forbidden = ["一定分手", "一定結婚", "天生不合"]
    for phrase in forbidden:
        assert phrase not in romantic_report.markdown_body, \
            f"報告中不應包含絕對斷言：「{phrase}」"


# ── 15. HTML export contains charset utf-8 ───────────────────────────────────

def test_html_export_contains_charset_utf8(romantic_report):
    from compatibility.exporters import export_compat_to_html
    html = export_compat_to_html(romantic_report)
    assert "charset" in html.lower() and "utf-8" in html.lower(), \
        "HTML export 應包含 charset utf-8 宣告"


# ── 16. Helper functions return non-garbled Chinese ──────────────────────────

def test_helper_returns_chinese_aspect_type():
    result = aspect_type_zh("trine")
    assert any("\u4e00" <= ch <= "\u9fff" for ch in result), \
        "aspect_type_zh 應返回含中文字符的字串"


def test_helper_returns_chinese_category():
    result = category_zh("emotional")
    assert any("\u4e00" <= ch <= "\u9fff" for ch in result), \
        "category_zh 應返回含中文字符的字串"
