"""
Tests for V1.5.1 — Zi Wei UI & Report Interpretation Polish.

Coverage:
1. formal_layout_phase1 chart produces non-empty accuracy_note.
2. render_ziwei_formal_table does not crash with a formal chart.
3. _MAIN_STARS_14 helper returns 14 stars.
4. auxiliary star (輔星) four_transformations preserved.
5. _interpret_main_star returns non-empty for at least 5 key stars.
6. Report template output contains required keywords.
7. All existing tests still pass (integration check via import).
8. _interpret_palace returns non-empty for major palaces.
9. _build_ziwei_summary returns a non-empty string for formal layout.
"""
import pytest
from datetime import date, time
from unittest.mock import patch, MagicMock

from engines.ziwei import (
    ZiWeiEngine,
    _interpret_main_star,
    _interpret_palace,
    _build_ziwei_summary,
    _MAIN_STARS_14,
    _YEAR_STEM_SIHUA,
)

ENGINE = ZiWeiEngine()
_DATE = date(1989, 9, 21)
_TIME_KNOWN = time(11, 5)


# ── 1. formal_layout_phase1 accuracy_note ────────────────────────────────────

def test_formal_layout_accuracy_note_nonempty():
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    if chart.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    assert chart.calculation_mode == "formal_layout_phase1"
    assert len(chart.accuracy_note) > 0


# ── 2. render_ziwei_formal_table does not crash ───────────────────────────────

def test_render_ziwei_formal_table_no_crash():
    """render_ziwei_formal_table should work without raising on a formal chart."""
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    # Import the component and mock streamlit
    import unittest.mock as mock
    with mock.patch.dict("sys.modules", {
        "streamlit": mock.MagicMock(),
        "pandas": __import__("pandas"),
    }):
        from ui.components import render_ziwei_formal_table
        # Should not raise
        try:
            render_ziwei_formal_table(chart)
        except Exception as e:
            # Only fail if it's not a streamlit rendering issue
            if "streamlit" not in str(type(e).__module__).lower():
                raise


# ── 3. _MAIN_STARS_14 has exactly 14 stars ───────────────────────────────────

def test_main_stars_14_count():
    assert len(_MAIN_STARS_14) == 14


def test_main_stars_14_contains_expected():
    expected = {"紫微", "天府", "武曲", "七殺", "破軍", "太陽", "太陰"}
    for s in expected:
        assert s in _MAIN_STARS_14, f"{s} not in _MAIN_STARS_14"


# ── 4. Auxiliary star in four_transformations ─────────────────────────────────

def test_auxiliary_star_four_transformations_preserved():
    """文昌 (auxiliary star) should appear in four_transformations for 丙年."""
    chart = ENGINE.calculate(date(1986, 6, 15), time(12, 0))  # 丙年
    assert "文昌" in chart.four_transformations, \
        "輔星四化（文昌化科）should be preserved in four_transformations"


# ── 5. _interpret_main_star for 5 key stars ───────────────────────────────────

@pytest.mark.parametrize("star", ["紫微", "天府", "武曲", "七殺", "破軍"])
def test_interpret_main_star_nonempty(star):
    result = _interpret_main_star(star)
    assert len(result) > 0, f"_interpret_main_star('{star}') returned empty string"


def test_interpret_main_star_unknown_returns_empty():
    result = _interpret_main_star("不存在的星")
    assert result == ""


# ── 6. Report template contains required keywords ─────────────────────────────

def test_report_template_full_contains_ziwei_keywords():
    from reports.templates import TEMPLATE_FULL
    required = ["紫微斗數", "命宮", "身宮", "四化", "formal_layout_phase1"]
    for kw in required:
        assert kw in TEMPLATE_FULL, f"TEMPLATE_FULL missing keyword: {kw}"


def test_report_template_full_contains_limitation_note():
    from reports.templates import TEMPLATE_FULL
    assert "輔星" in TEMPLATE_FULL or "大限" in TEMPLATE_FULL, \
        "TEMPLATE_FULL should mention V1.5 limitations"


# ── 7. _interpret_palace returns non-empty for known palaces ──────────────────

@pytest.mark.parametrize("palace_name,stars", [
    ("命宮", ["紫微"]),
    ("官祿宮", ["武曲"]),
    ("財帛宮", ["天府"]),
    ("夫妻宮", ["七殺"]),
    ("福德宮", ["破軍"]),
])
def test_interpret_palace_nonempty(palace_name, stars):
    result = _interpret_palace(palace_name, stars, {})
    assert len(result) > 0, f"_interpret_palace('{palace_name}', {stars}) returned empty"


def test_interpret_palace_with_sihua():
    """_interpret_palace should include sihua info when transformations dict contains the star."""
    result = _interpret_palace("命宮", ["紫微"], {"紫微": "化祿"})
    assert "化祿" in result or "資源" in result, \
        "Sihua info should appear in palace interpretation"


def test_interpret_palace_empty_stars():
    """Empty stars list should still return base palace description."""
    result = _interpret_palace("命宮", [], {})
    assert len(result) > 0, "Even with no stars, base palace description should be non-empty"


# ── 8. _build_ziwei_summary ───────────────────────────────────────────────────

def test_build_ziwei_summary_formal_nonempty():
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    if chart.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    summary = _build_ziwei_summary(chart)
    assert len(summary) > 0


def test_build_ziwei_summary_contains_mode_info():
    chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
    if chart.calculation_mode == "mock_fallback":
        pytest.skip("lunardate unavailable")
    summary = _build_ziwei_summary(chart)
    assert "正式排盤" in summary or "V1.5" in summary


def test_build_ziwei_summary_mock_fallback():
    """_build_ziwei_summary should work on mock_fallback charts."""
    import engines.ziwei as _zw
    original = _zw._LUNARDATE_AVAILABLE
    _zw._LUNARDATE_AVAILABLE = False
    try:
        chart = ENGINE.calculate(_DATE, _TIME_KNOWN)
        summary = _build_ziwei_summary(chart)
        assert len(summary) > 0
        assert "fallback" in summary or "mock" in summary.lower()
    finally:
        _zw._LUNARDATE_AVAILABLE = original


# ── 9. Synthesis engine imports without error ─────────────────────────────────

def test_synthesis_engine_imports():
    from engines.synthesis import SynthesisEngine
    assert SynthesisEngine is not None


# ── 10. components import without error ──────────────────────────────────────

def test_components_import():
    import unittest.mock as mock
    with mock.patch.dict("sys.modules", {"streamlit": mock.MagicMock()}):
        import importlib
        import ui.components as comp
        assert hasattr(comp, "render_ziwei_formal_table"), \
            "render_ziwei_formal_table should be defined in ui.components"
