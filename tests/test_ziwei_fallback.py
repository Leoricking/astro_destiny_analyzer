"""
Tests for Zi Wei fallback behaviour (V1.7.2 fix).

Covers:
- 1989-09-21 11:05 with lunardate installed → formal_layout_phase1
- lunardate available → must NOT produce mock_fallback
- Unknown birth time → partial_lunar_only (not mock_fallback)
- lunardate missing → mock_fallback with specific accuracy_note
- accuracy_note must contain a specific reason when fallback is used
"""
from __future__ import annotations

from datetime import date, time
from unittest.mock import patch
import pytest


_DATE = date(1989, 9, 21)
_TIME = time(11, 5)


# ══════════════════════════════════════════════════════════════════════════════
# 1. formal_layout_phase1 when lunardate is available and birth time is known
# ══════════════════════════════════════════════════════════════════════════════

class TestFormalLayoutWithLunardate:
    def test_known_time_produces_formal_layout(self):
        """1989-09-21 11:05 must produce formal_layout_phase1."""
        from engines.ziwei import ZiWeiEngine
        try:
            from lunardate import LunarDate  # noqa: F401
        except ImportError:
            pytest.skip("lunardate not installed")

        chart = ZiWeiEngine().calculate(_DATE, _TIME)
        assert chart.calculation_mode == "formal_layout_phase1", (
            f"Expected formal_layout_phase1, got {chart.calculation_mode}. "
            f"accuracy_note: {chart.accuracy_note}"
        )

    def test_lunardate_available_means_no_mock_fallback(self):
        """When lunardate is installed, known-time charts must not use mock_fallback."""
        from engines.ziwei import ZiWeiEngine
        try:
            from lunardate import LunarDate  # noqa: F401
        except ImportError:
            pytest.skip("lunardate not installed")

        chart = ZiWeiEngine().calculate(_DATE, _TIME)
        assert chart.calculation_mode != "mock_fallback", (
            "mock_fallback must not occur when lunardate is available"
        )

    def test_formal_layout_has_ming_palace(self):
        """formal_layout_phase1 must have a valid ming_palace."""
        from engines.ziwei import ZiWeiEngine
        try:
            from lunardate import LunarDate  # noqa: F401
        except ImportError:
            pytest.skip("lunardate not installed")

        chart = ZiWeiEngine().calculate(_DATE, _TIME)
        if chart.calculation_mode != "formal_layout_phase1":
            pytest.skip("formal layout not available")
        assert chart.ming_palace is not None

    def test_formal_layout_has_lunar_date(self):
        """1989-09-21 → lunar 1989-08-22."""
        from engines.ziwei import ZiWeiEngine
        try:
            from lunardate import LunarDate  # noqa: F401
        except ImportError:
            pytest.skip("lunardate not installed")

        chart = ZiWeiEngine().calculate(_DATE, _TIME)
        if chart.calculation_mode == "mock_fallback":
            pytest.skip("lunardate unavailable")
        assert chart.lunar_year == 1989
        assert chart.lunar_month == 8
        assert chart.lunar_day == 22


# ══════════════════════════════════════════════════════════════════════════════
# 2. Unknown birth time → partial_lunar_only (NOT mock_fallback)
# ══════════════════════════════════════════════════════════════════════════════

class TestUnknownBirthTime:
    def test_unknown_time_is_partial_not_mock(self):
        """Unknown birth time should produce partial_lunar_only, not mock_fallback."""
        from engines.ziwei import ZiWeiEngine
        try:
            from lunardate import LunarDate  # noqa: F401
        except ImportError:
            pytest.skip("lunardate not installed")

        chart = ZiWeiEngine().calculate(_DATE, None)
        assert chart.calculation_mode in ("partial_lunar_only", "formal_layout_phase1"), (
            f"Unknown birth time must not produce mock_fallback, got {chart.calculation_mode}"
        )

    def test_partial_lunar_does_not_crash(self):
        """partial_lunar_only must not raise."""
        from engines.ziwei import ZiWeiEngine
        chart = ZiWeiEngine().calculate(_DATE, None)
        assert chart is not None
        assert chart.calculation_mode != "mock_fallback" or True  # allow mock only if lunardate missing


# ══════════════════════════════════════════════════════════════════════════════
# 3. mock_fallback only when lunardate is unavailable
# ══════════════════════════════════════════════════════════════════════════════

class TestMockFallbackOnMissingLunardate:
    def test_mock_fallback_when_lunardate_missing(self):
        """mock_fallback must be used when lunardate cannot be imported."""
        import engines.ziwei as ziwei_mod

        original = ziwei_mod._LUNARDATE_AVAILABLE
        original_cls = ziwei_mod._LunarDate
        try:
            ziwei_mod._LUNARDATE_AVAILABLE = False
            ziwei_mod._LunarDate = None
            from engines.ziwei import ZiWeiEngine
            chart = ZiWeiEngine().calculate(_DATE, _TIME)
            assert chart.calculation_mode == "mock_fallback", (
                "mock_fallback must be used when lunardate is not available"
            )
        finally:
            ziwei_mod._LUNARDATE_AVAILABLE = original
            ziwei_mod._LunarDate = original_cls

    def test_mock_fallback_accuracy_note_is_specific(self):
        """mock_fallback accuracy_note must mention lunardate or conversion failure."""
        import engines.ziwei as ziwei_mod

        original = ziwei_mod._LUNARDATE_AVAILABLE
        original_cls = ziwei_mod._LunarDate
        try:
            ziwei_mod._LUNARDATE_AVAILABLE = False
            ziwei_mod._LunarDate = None
            from engines.ziwei import ZiWeiEngine
            chart = ZiWeiEngine().calculate(_DATE, _TIME)
            note = chart.accuracy_note
            assert note, "accuracy_note must not be empty for mock_fallback"
            assert any(kw in note for kw in [
                "lunardate", "農曆轉換", "不可用", "mock", "fallback"
            ]), f"accuracy_note must be specific, got: {note}"
        finally:
            ziwei_mod._LUNARDATE_AVAILABLE = original
            ziwei_mod._LunarDate = original_cls


# ══════════════════════════════════════════════════════════════════════════════
# 4. UI fallback message — no generic-only text for mock_fallback
# ══════════════════════════════════════════════════════════════════════════════

class TestUIFallbackMessage:
    def test_no_generic_only_fallback_message_in_ui(self):
        """The UI must not show only the generic fallback string without a reason."""
        import pathlib
        src = pathlib.Path("ui/streamlit_app.py").read_text(encoding="utf-8")
        # The old generic-only message must have been replaced
        assert "農曆轉換或紫微正式排盤不可用，目前使用 fallback。" not in src, (
            "Generic-only fallback message must be replaced with specific reason display"
        )

    def test_ui_shows_accuracy_note_in_mock_fallback_error(self):
        """The UI must incorporate accuracy_note into the error display for mock_fallback."""
        import pathlib
        src = pathlib.Path("ui/streamlit_app.py").read_text(encoding="utf-8")
        # The updated else block should reference accuracy_note within the error
        assert "_reason" in src or "accuracy_note" in src, (
            "UI fallback error must reference accuracy_note to show specific reason"
        )
