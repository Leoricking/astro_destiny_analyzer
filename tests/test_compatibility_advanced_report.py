"""
V1.8.0 Tests: Compatibility Advanced Report (CompatibilityEngine + exports)
"""
import pytest
from datetime import date, time

from compatibility.engine import CompatibilityEngine
from compatibility.models import CompatibilityInput, RelationshipType, CompatibilityReport
from core.models import BirthProfile, BloodType


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def romantic_input():
    from demo.sample_profiles import SAMPLE_COUPLES
    couple = next(c for c in SAMPLE_COUPLES if c.get("relationship_type") == "romantic")
    return CompatibilityInput(
        person_a=couple["person_a"],
        person_b=couple["person_b"],
        relationship_type=RelationshipType.ROMANTIC,
    )


@pytest.fixture(scope="module")
def business_input():
    from demo.sample_profiles import SAMPLE_COUPLES
    couple = next(c for c in SAMPLE_COUPLES if c.get("relationship_type") == "business")
    return CompatibilityInput(
        person_a=couple["person_a"],
        person_b=couple["person_b"],
        relationship_type=RelationshipType.BUSINESS,
    )


@pytest.fixture(scope="module")
def romantic_report(romantic_input):
    return CompatibilityEngine().generate(romantic_input)


@pytest.fixture(scope="module")
def business_report(business_input):
    return CompatibilityEngine().generate(business_input)


# ── 1. Engine returns advanced_astrology ─────────────────────────────────────

def test_romantic_has_advanced_astrology(romantic_report):
    """CompatibilityEngine.generate() 回傳 advanced_astrology"""
    assert romantic_report.advanced_astrology is not None, (
        "romantic report 應有 advanced_astrology"
    )


# ── 2. Scores in 0–100 ────────────────────────────────────────────────────────

def test_advanced_scores_in_range(romantic_report):
    """advanced_scores 各項 0–100"""
    sc = romantic_report.advanced_astrology.advanced_scores
    for field_name in (
        "emotional_bond", "communication_flow", "attraction_chemistry",
        "stability_potential", "growth_intensity", "conflict_intensity",
        "long_term_potential", "overall_advanced_score",
    ):
        val = getattr(sc, field_name)
        assert 0 <= val <= 100, f"{field_name} = {val}，應在 0–100"


# ── 3. overall_advanced_score in 0–100 ───────────────────────────────────────

def test_overall_advanced_score_in_range(romantic_report):
    """overall_advanced_score 在 0–100"""
    sc = romantic_report.advanced_astrology.advanced_scores
    assert 0 <= sc.overall_advanced_score <= 100


# ── 4. Label not empty ────────────────────────────────────────────────────────

def test_label_not_empty(romantic_report):
    """label 不為空"""
    assert romantic_report.advanced_astrology.advanced_scores.label


# ── 5–7. Markdown contains required sections ──────────────────────────────────

def test_markdown_contains_advanced_astrology(romantic_report):
    """markdown 包含「進階西洋合盤」"""
    assert "進階西洋合盤" in romantic_report.markdown_body, (
        "markdown 缺少「進階西洋合盤」章節"
    )


def test_markdown_contains_synastry(romantic_report):
    """markdown 包含「Synastry」"""
    assert "Synastry" in romantic_report.markdown_body or "相位矩陣" in romantic_report.markdown_body


def test_markdown_contains_composite(romantic_report):
    """markdown 包含「Composite」"""
    assert "Composite" in romantic_report.markdown_body


# ── 8. HTML export quality ────────────────────────────────────────────────────

def test_html_export_no_crash(romantic_report):
    """HTML export 不 crash"""
    from compatibility.exporters import export_compat_to_html
    html = export_compat_to_html(romantic_report)
    assert html and len(html) > 100


def test_html_export_has_charset_utf8(romantic_report):
    """HTML export 包含 charset utf-8"""
    from compatibility.exporters import export_compat_to_html
    html = export_compat_to_html(romantic_report)
    assert "charset" in html.lower() and "utf-8" in html.lower(), \
        "HTML export 應包含 charset=utf-8"


def test_html_export_contains_advanced_astrology(romantic_report):
    """HTML export 包含進階西洋合盤章節"""
    from compatibility.exporters import export_compat_to_html
    html = export_compat_to_html(romantic_report)
    assert "進階西洋合盤" in html, "HTML export 應包含「進階西洋合盤」"


# ── 9. Save/reload advanced report ───────────────────────────────────────────

def test_save_reload_no_crash(romantic_report):
    """save/reload advanced report 不 crash (JSON round-trip)"""
    json_str = romantic_report.model_dump_json()
    reloaded = CompatibilityReport.model_validate_json(json_str)
    assert reloaded.advanced_astrology is not None
    assert reloaded.advanced_astrology.advanced_scores.overall_advanced_score >= 0


# ── 10. Old report with advanced_astrology=None no crash ─────────────────────

def test_old_report_no_advanced_astrology_no_crash():
    """舊 report advanced_astrology=None 不 crash"""
    from core.models import BirthProfile, BloodType
    profile = BirthProfile(
        name="Test", birth_date=date(1990, 1, 1),
        birth_city="台北", birth_country="台灣", blood_type=BloodType.A,
    )
    report = CompatibilityReport(
        person_a_profile=profile,
        person_b_profile=profile,
        advanced_astrology=None,
    )
    # Should not raise
    from compatibility.report import render_compatibility_report
    md = render_compatibility_report(report)
    assert md is not None


# ── 11–12. Demo couples can export ───────────────────────────────────────────

def test_romantic_couple_can_export(romantic_report):
    """demo romantic couple 可以匯出 markdown"""
    assert romantic_report.markdown_body
    assert len(romantic_report.markdown_body) > 200


def test_business_couple_has_advanced_astrology(business_report):
    """demo business couple 也有 advanced_astrology"""
    assert business_report.advanced_astrology is not None


def test_business_couple_can_export(business_report):
    """demo business couple 可以匯出 markdown"""
    assert business_report.markdown_body
    assert len(business_report.markdown_body) > 200


# ── 13–15. Markdown content quality (V1.8.1) ─────────────────────────────────

def test_markdown_contains_synastry_section(romantic_report):
    """markdown 包含 Synastry 章節"""
    assert "相位矩陣" in romantic_report.markdown_body or "Synastry" in romantic_report.markdown_body


def test_markdown_contains_composite_section(romantic_report):
    """markdown 包含 Composite Chart 章節"""
    assert "Composite Chart" in romantic_report.markdown_body


def test_markdown_score_disclaimer_present(romantic_report):
    """markdown 包含進階合盤分數免責聲明"""
    assert "不是絕對適合度" in romantic_report.markdown_body, \
        "報告應包含「不是絕對適合度」說明"


# ── 16. Word export no crash ─────────────────────────────────────────────────

def test_word_export_no_crash_if_available(romantic_report):
    """Word export 若 python-docx 可用，不 crash"""
    try:
        from compatibility.exporters import export_compat_to_docx
        docx_bytes = export_compat_to_docx(romantic_report)
        assert len(docx_bytes) > 0, "Word export 應產生非空 bytes"
    except RuntimeError:
        pytest.skip("python-docx 未安裝，跳過 Word export 測試")
