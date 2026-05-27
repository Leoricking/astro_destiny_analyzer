"""
Tests for birth year state management (V1.7.2 fix).

Covers:
- DEFAULT_BIRTH_YEAR = 1990
- MIN_BIRTH_YEAR = 1900
- _normalize_birth_year_state() logic (simulated, no Streamlit runtime)
- _clear_input_state() resets year and touched flag
"""
from __future__ import annotations

import pytest


# ── Helpers ────────────────────────────────────────────────────────────────────

def _simulate_normalize(ss: dict) -> None:
    """
    Replicate the logic of _normalize_birth_year_state() without Streamlit.
    ss is used as a stand-in for st.session_state.
    """
    DEFAULT_BIRTH_YEAR = 1990
    MIN_BIRTH_YEAR = 1900

    year = ss.get("input_birth_year")
    touched = ss.get("input_birth_year_user_touched", False)
    has_profile = bool(ss.get("profile") or ss.get("current_profile"))
    has_report = bool(ss.get("report"))

    if year is None:
        ss["input_birth_year"] = DEFAULT_BIRTH_YEAR
        ss["input_birth_year_user_touched"] = False
        return

    try:
        year_int = int(year)
    except Exception:
        ss["input_birth_year"] = DEFAULT_BIRTH_YEAR
        ss["input_birth_year_user_touched"] = False
        return

    if year_int < MIN_BIRTH_YEAR or year_int > 2100:
        ss["input_birth_year"] = DEFAULT_BIRTH_YEAR
        ss["input_birth_year_user_touched"] = False
        return

    if (year_int == MIN_BIRTH_YEAR
            and not touched
            and not has_profile
            and not has_report):
        ss["input_birth_year"] = DEFAULT_BIRTH_YEAR
        ss["input_birth_year_user_touched"] = False


# ══════════════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════════════

class TestConstants:
    def test_default_birth_year_is_1990(self):
        import pathlib
        src = pathlib.Path("ui/streamlit_app.py").read_text(encoding="utf-8")
        assert "DEFAULT_BIRTH_YEAR: int = 1990" in src or \
               "DEFAULT_BIRTH_YEAR = 1990" in src

    def test_min_birth_year_is_1900(self):
        import pathlib, re
        src = pathlib.Path("ui/streamlit_app.py").read_text(encoding="utf-8")
        assert re.search(r"MIN_BIRTH_YEAR\s*[:=][^=].*1900", src), (
            "MIN_BIRTH_YEAR must be defined as 1900"
        )

    def test_input_defaults_birth_year_uses_constant(self):
        import pathlib
        src = pathlib.Path("ui/streamlit_app.py").read_text(encoding="utf-8")
        assert '"input_birth_year": DEFAULT_BIRTH_YEAR' in src

    def test_number_input_uses_min_birth_year_constant(self):
        import pathlib
        src = pathlib.Path("ui/streamlit_app.py").read_text(encoding="utf-8")
        assert "min_value=MIN_BIRTH_YEAR" in src

    def test_number_input_has_on_change_callback(self):
        import pathlib
        src = pathlib.Path("ui/streamlit_app.py").read_text(encoding="utf-8")
        assert "on_change=_mark_birth_year_touched" in src


# ══════════════════════════════════════════════════════════════════════════════
# _normalize_birth_year_state logic
# ══════════════════════════════════════════════════════════════════════════════

class TestNormalizeBirthYearState:
    def test_default_year_is_1990_for_fresh_session(self):
        """Fresh session (no year key) → 1990."""
        ss = {}
        _simulate_normalize(ss)
        assert ss["input_birth_year"] == 1990

    def test_none_year_resets_to_1990(self):
        ss = {"input_birth_year": None}
        _simulate_normalize(ss)
        assert ss["input_birth_year"] == 1990

    def test_min_value_1900_untouched_no_profile_resets_to_1990(self):
        """Streamlit artefact: 1900 set as min_value, user never touched."""
        ss = {
            "input_birth_year": 1900,
            "input_birth_year_user_touched": False,
            "profile": None,
            "report": None,
        }
        _simulate_normalize(ss)
        assert ss["input_birth_year"] == 1990

    def test_touched_1900_stays_1900(self):
        """User explicitly set 1900 → must NOT be overridden."""
        ss = {
            "input_birth_year": 1900,
            "input_birth_year_user_touched": True,
            "profile": None,
            "report": None,
        }
        _simulate_normalize(ss)
        assert ss["input_birth_year"] == 1900

    def test_1900_with_existing_profile_stays_1900(self):
        """Profile exists → 1900 is preserved even if not marked touched."""
        from core.models import BirthProfile
        from datetime import date
        profile = BirthProfile(
            name="X", birth_date=date(1900, 1, 1),
            birth_city="台北", birth_country="台灣",
        )
        ss = {
            "input_birth_year": 1900,
            "input_birth_year_user_touched": False,
            "profile": profile,
            "report": None,
        }
        _simulate_normalize(ss)
        assert ss["input_birth_year"] == 1900

    def test_1900_with_existing_report_stays_1900(self):
        """Report exists → 1900 is preserved even if not marked touched."""
        ss = {
            "input_birth_year": 1900,
            "input_birth_year_user_touched": False,
            "profile": None,
            "report": object(),  # any truthy object
        }
        _simulate_normalize(ss)
        assert ss["input_birth_year"] == 1900

    def test_sub_1900_year_resets_to_1990(self):
        """Old stale value like 1800 → 1990."""
        ss = {"input_birth_year": 1800}
        _simulate_normalize(ss)
        assert ss["input_birth_year"] == 1990

    def test_invalid_string_resets_to_1990(self):
        ss = {"input_birth_year": "abc"}
        _simulate_normalize(ss)
        assert ss["input_birth_year"] == 1990

    def test_valid_1990_untouched_stays_1990(self):
        ss = {"input_birth_year": 1990, "input_birth_year_user_touched": False}
        _simulate_normalize(ss)
        assert ss["input_birth_year"] == 1990

    def test_valid_1975_stays_1975(self):
        ss = {
            "input_birth_year": 1975,
            "input_birth_year_user_touched": True,
        }
        _simulate_normalize(ss)
        assert ss["input_birth_year"] == 1975

    def test_valid_2000_stays_2000(self):
        ss = {"input_birth_year": 2000}
        _simulate_normalize(ss)
        assert ss["input_birth_year"] == 2000

    def test_normalize_resets_touched_flag_when_resetting_year(self):
        """When year is reset to default, touched flag is also cleared."""
        ss = {
            "input_birth_year": 1800,
            "input_birth_year_user_touched": True,  # shouldn't matter for sub-1900
        }
        _simulate_normalize(ss)
        assert ss["input_birth_year"] == 1990
        assert ss["input_birth_year_user_touched"] is False


# ══════════════════════════════════════════════════════════════════════════════
# _clear_input_state resets birth year
# ══════════════════════════════════════════════════════════════════════════════

class TestClearInputState:
    def test_clear_resets_birth_year_to_1990(self):
        """_clear_input_state must set input_birth_year to DEFAULT_BIRTH_YEAR."""
        import pathlib
        src = pathlib.Path("ui/streamlit_app.py").read_text(encoding="utf-8")
        assert 'st.session_state["input_birth_year"] = DEFAULT_BIRTH_YEAR' in src

    def test_clear_resets_touched_flag(self):
        """_clear_input_state must reset input_birth_year_user_touched = False."""
        import pathlib
        src = pathlib.Path("ui/streamlit_app.py").read_text(encoding="utf-8")
        assert 'st.session_state["input_birth_year_user_touched"] = False' in src

    def test_simulate_clear_then_year_is_1990(self):
        """Simulate clear: set year to 1900 then clear → 1990."""
        DEFAULT_BIRTH_YEAR = 1990
        ss = {
            "input_birth_year": 1900,
            "input_birth_year_user_touched": True,
            "profile": None,
            "report": None,
        }
        # Simulate _clear_input_state
        ss["input_birth_year"] = DEFAULT_BIRTH_YEAR
        ss["input_birth_year_user_touched"] = False

        # After clear, normalize should leave it at 1990
        _simulate_normalize(ss)
        assert ss["input_birth_year"] == 1990

    def test_simulate_clear_then_1900_not_preserved(self):
        """After clear, entering 1900 only works if user re-touches the field."""
        ss = {
            "input_birth_year": 1990,
            "input_birth_year_user_touched": False,
        }
        # Without touching, normalize brings 1900 back to 1990
        ss["input_birth_year"] = 1900
        _simulate_normalize(ss)
        assert ss["input_birth_year"] == 1990

        # With touching (user manually entered 1900), 1900 is preserved
        ss["input_birth_year"] = 1900
        ss["input_birth_year_user_touched"] = True
        _simulate_normalize(ss)
        assert ss["input_birth_year"] == 1900


# ══════════════════════════════════════════════════════════════════════════════
# _mark_birth_year_touched logic
# ══════════════════════════════════════════════════════════════════════════════

class TestMarkBirthYearTouched:
    def test_mark_sets_touched_true(self):
        """Simulates the on_change callback."""
        ss = {"input_birth_year_user_touched": False}
        # Simulate callback
        ss["input_birth_year_user_touched"] = True
        assert ss["input_birth_year_user_touched"] is True

    def test_after_marking_1900_preserved(self):
        ss = {
            "input_birth_year": 1900,
            "input_birth_year_user_touched": False,
        }
        # User changes year field (triggers on_change)
        ss["input_birth_year_user_touched"] = True
        # Normalize should now keep 1900
        _simulate_normalize(ss)
        assert ss["input_birth_year"] == 1900
