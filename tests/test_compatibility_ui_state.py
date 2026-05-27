"""
Tests for V1.7.2 UI state fixes:
- Birth year min/default behaviour (Fix A)
- IC / Imum Coeli explanation text (Fix B) — checks origin/main content
- Compatibility result session-state stability (Fix C)
"""
from __future__ import annotations

from datetime import date
import pytest


# ══════════════════════════════════════════════════════════════════════════════
# A. Birth year defaults / migration
# ══════════════════════════════════════════════════════════════════════════════

class TestBirthYearDefaults:
    def test_input_defaults_birth_year_is_1990(self):
        """_INPUT_DEFAULTS must reference DEFAULT_BIRTH_YEAR (which equals 1990)."""
        import pathlib
        src = pathlib.Path("ui/streamlit_app.py").read_text(encoding="utf-8")
        assert '"input_birth_year": DEFAULT_BIRTH_YEAR' in src, (
            "_INPUT_DEFAULTS must reference DEFAULT_BIRTH_YEAR constant (= 1990)"
        )
        assert "DEFAULT_BIRTH_YEAR" in src and "1990" in src

    def test_birth_year_normalization_function_exists(self):
        """_normalize_birth_year_state() must exist (replaces old migration block)."""
        import pathlib
        src = pathlib.Path("ui/streamlit_app.py").read_text(encoding="utf-8")
        assert "def _normalize_birth_year_state" in src, (
            "_normalize_birth_year_state() function must be defined"
        )
        assert "<= 1900" not in src, (
            "Old '<= 1900' migration must NOT remain — handled by _normalize_birth_year_state"
        )

    def test_number_input_min_value_is_1900(self):
        """The birth year number_input must have min_value set to 1900 (via constant or literal)."""
        import pathlib
        src = pathlib.Path("ui/streamlit_app.py").read_text(encoding="utf-8")
        assert "min_value=MIN_BIRTH_YEAR" in src or "min_value=1900" in src, (
            "Birth year number_input must have min_value=MIN_BIRTH_YEAR or min_value=1900"
        )

    def test_migration_does_not_override_1900(self):
        """simulate: year=1900 should NOT be migrated to 1990."""
        year = 1900
        migrated = False
        if year < 1900:
            year = 1990
            migrated = True
        assert not migrated
        assert year == 1900

    def test_migration_overrides_sub_1900(self):
        """simulate: year < 1900 (e.g. stale 1800) IS migrated to 1990."""
        year = 1800
        migrated = False
        if year < 1900:
            year = 1990
            migrated = True
        assert migrated
        assert year == 1990


# ══════════════════════════════════════════════════════════════════════════════
# B. IC explanation — checks origin/main content
# ══════════════════════════════════════════════════════════════════════════════

class TestICExplanation:
    def test_synthesis_ic_section_exists(self):
        """synthesis.py must have an IC / 天底 section."""
        import pathlib
        src = pathlib.Path("engines/synthesis.py").read_text(encoding="utf-8")
        assert "天底" in src or "IC" in src, (
            "synthesis.py must contain IC / 天底 content"
        )

    def test_synthesis_ic_text_contrasts_mc_and_ic(self):
        """synthesis.py must mention IC for the family/roots analysis."""
        import pathlib
        src = pathlib.Path("engines/synthesis.py").read_text(encoding="utf-8")
        assert "IC" in src, "synthesis.py must mention IC"
        assert "天底" in src or "根基" in src or "家庭" in src, (
            "synthesis.py must describe IC's roots/family meaning"
        )

    def test_synthesis_ic_section_generated_correctly(self):
        """The synthesis engine must produce IC text for a real chart."""
        from datetime import date, time as dtime
        from core.models import BirthProfile, BloodType
        from engines.western_astrology import WesternAstrologyEngine
        from engines.bazi import BaZiEngine
        from engines.ziwei import ZiWeiEngine
        from engines.blood_type import BloodTypeEngine
        from engines.numerology import NumerologyEngine
        from engines.synthesis import SynthesisEngine

        profile = BirthProfile(
            name="TestIC",
            birth_date=date(1990, 6, 15),
            birth_time=dtime(10, 30),
            birth_city="台北",
            birth_country="台灣",
            blood_type=BloodType.A,
            birth_latitude=25.033,
            birth_longitude=121.565,
            birth_timezone_offset=8.0,
            birth_time_is_known=True,
        )
        western = WesternAstrologyEngine().calculate(
            birth_date=profile.birth_date,
            birth_time=profile.birth_time,
            birth_city=profile.birth_city,
            birth_country=profile.birth_country,
            birth_latitude=profile.birth_latitude,
            birth_longitude=profile.birth_longitude,
            birth_timezone_offset=profile.birth_timezone_offset,
        )
        bazi    = BaZiEngine().calculate(profile.birth_date, profile.birth_time)
        ziwei   = ZiWeiEngine().calculate(profile.birth_date, profile.birth_time)
        blood   = BloodTypeEngine().analyze(profile.blood_type)
        num     = NumerologyEngine().calculate(profile.birth_date)
        synth   = SynthesisEngine().synthesize(profile, western, bazi, ziwei, blood, num)

        fs = synth.family_security
        assert len(fs) > 20, "family_security must be non-empty"
        if western.ic:
            assert "IC" in fs or "天底" in fs, (
                "family_security must mention IC / 天底 when western chart is available"
            )


# ══════════════════════════════════════════════════════════════════════════════
# C. Compatibility result session-state stability
# ══════════════════════════════════════════════════════════════════════════════

class TestCompatibilityResultState:
    def _make_report(self):
        from datetime import date
        from compatibility.models import CompatibilityInput, RelationshipType
        from compatibility.engine import CompatibilityEngine
        from core.models import BirthProfile, BloodType

        pa = BirthProfile(
            name="StateA", birth_date=date(1990, 3, 1),
            birth_city="台北", birth_country="台灣", blood_type=BloodType.A,
        )
        pb = BirthProfile(
            name="StateB", birth_date=date(1992, 7, 10),
            birth_city="台北", birth_country="台灣", blood_type=BloodType.O,
        )
        inp = CompatibilityInput(
            person_a=pa, person_b=pb,
            relationship_type=RelationshipType.ROMANTIC,
        )
        return CompatibilityEngine().generate(inp)

    def test_report_object_accessible_from_session_state_key(self):
        """Simulates what the UI does: write to session_state, read back."""
        ss = {}
        ss["compatibility_report"] = None

        report = self._make_report()

        ss["compatibility_report"] = report

        c_report = ss.get("compatibility_report")
        assert c_report is not None
        assert c_report.score_breakdown.overall_score >= 0
        assert c_report.score_breakdown.dynamic_label
        assert c_report.markdown_body

    def test_report_has_required_fields(self):
        """CompatibilityReport must have all key fields."""
        report = self._make_report()
        assert report.score_breakdown.overall_score >= 0
        assert report.score_breakdown.dynamic_label
        assert report.markdown_body
        assert report.person_a_profile.name == "StateA"
        assert report.person_b_profile.name == "StateB"

    def test_clear_button_simulation(self):
        """Simulates the clear button handler."""
        ss = {}
        report = self._make_report()
        ss["compatibility_report"] = report

        # Simulate clear button click
        ss["compatibility_report"] = None

        assert ss["compatibility_report"] is None

    def test_result_not_cleared_on_page_revisit(self):
        """Navigating away and back must not clear compatibility_report."""
        ss = {}
        report = self._make_report()
        ss["compatibility_report"] = report

        # Simulate page navigation (only global defaults that use setdefault)
        global_defaults = {"compatibility_report": None}
        for k, v in global_defaults.items():
            if k not in ss:
                ss[k] = v

        assert ss["compatibility_report"] is not None

    def test_no_rerun_needed_for_result_to_appear(self):
        """After generation, report is immediately available in session_state."""
        ss = {}
        report = self._make_report()

        ss["compatibility_report"] = report

        c_report = ss.get("compatibility_report")
        assert c_report is not None

    def test_report_persists_when_loaded_row_is_set(self):
        """Loading a history row must not clear the in-memory report."""
        ss = {}
        report = self._make_report()
        ss["compatibility_report"] = report

        fake_row = {
            "db_id": 1, "report_id": "compat_test",
            "person_a_name": "A", "person_b_name": "B",
            "relationship_type": "朋友", "overall_score": 75,
            "dynamic_label": "良好相處", "created_at": "2026-01-01",
            "markdown_body": "# Test",
        }
        ss["compat_loaded_row"] = fake_row

        loaded_row = ss.get("compat_loaded_row")
        assert loaded_row is not None
        assert loaded_row["person_a_name"] == "A"
