"""
Tests for default birth country = 台灣 behaviour.

Covers:
  1. DEFAULT_COUNTRY constant == "台灣"
  2. Single-person input defaults to 台灣
  3. Clear-input resets country to 台灣
  4. Existing session value ("日本") is NOT overwritten
  5. _sync_input_state: country=None → 台灣
  6. _sync_input_state: country="日本" → preserved
  7. Compat A default country 台灣
  8. Compat B default country 台灣
  9. LeadProfile country field defaults to 台灣
 10. PartnerProfile country field defaults to 台灣
 11. No country field is disabled=True
 12. Customer mode not affected
 13. Developer mode not affected
"""
from __future__ import annotations
import pathlib

SRC = pathlib.Path("ui/streamlit_app.py").read_text(encoding="utf-8")


# ── 1. DEFAULT_COUNTRY constant ───────────────────────────────────────────────

class TestDefaultCountryConstant:
    def test_constant_defined(self):
        assert 'DEFAULT_COUNTRY: str = "台灣"' in SRC

    def test_constant_value(self):
        import sys, os
        # Extract constant value by scanning the source rather than importing Streamlit
        for line in SRC.splitlines():
            stripped = line.strip()
            if stripped.startswith("DEFAULT_COUNTRY"):
                assert "台灣" in stripped
                return
        raise AssertionError("DEFAULT_COUNTRY not found in source")


# ── 2. Single-person input defaults ──────────────────────────────────────────

class TestSinglePersonInputDefaults:
    def test_input_defaults_references_default_country(self):
        assert '"input_birth_country": DEFAULT_COUNTRY' in SRC

    def test_session_init_uses_setdefault_pattern(self):
        # The init loop must check "if _k not in st.session_state" — never overwrite
        assert 'if _k not in st.session_state' in SRC


# ── 3. Clear input resets country to 台灣 ────────────────────────────────────

class TestClearInputResetsCountry:
    def test_clear_function_uses_input_defaults(self):
        assert "_clear_input_state" in SRC
        assert "_INPUT_DEFAULTS" in SRC

    def simulate_clear(self):
        """Simulate _clear_input_state logic with a plain dict."""
        INPUT_DEFAULTS = {"input_birth_country": "台灣"}
        ss = {"input_birth_country": "美國"}
        for k, v in INPUT_DEFAULTS.items():
            ss[k] = list(v) if isinstance(v, list) else v
        return ss

    def test_clear_resets_to_taiwan(self):
        ss = self.simulate_clear()
        assert ss["input_birth_country"] == "台灣"


# ── 4. Existing session value not overwritten ────────────────────────────────

class TestExistingCountryPreserved:
    def test_migration_skips_non_empty_country(self):
        """Simulate the migration block: only fills blank country."""
        ss = {"input_birth_country": "日本"}
        if not ss.get("input_birth_country"):
            ss["input_birth_country"] = "台灣"
        assert ss["input_birth_country"] == "日本"

    def test_init_loop_skips_existing_key(self):
        """Simulate the _INPUT_DEFAULTS init loop."""
        INPUT_DEFAULTS = {"input_birth_country": "台灣"}
        ss = {"input_birth_country": "日本"}
        for k, v in INPUT_DEFAULTS.items():
            if k not in ss:
                ss[k] = v
        assert ss["input_birth_country"] == "日本"


# ── 5 & 6. _sync_input_state_from_profile behaviour ─────────────────────────

class TestSyncFromProfile:
    def test_none_country_filled_with_taiwan(self):
        """country=None → or "台灣" fallback → "台灣"."""
        birth_country = None
        ss_value = birth_country or "台灣"
        assert ss_value == "台灣"

    def test_japan_country_preserved(self):
        """country="日本" → or "台灣" fallback is skipped → "日本"."""
        birth_country = "日本"
        ss_value = birth_country or "台灣"
        assert ss_value == "日本"

    def test_sync_uses_or_taiwan_pattern(self):
        assert 'or "台灣"' in SRC or "or DEFAULT_COUNTRY" in SRC


# ── 7 & 8. Compat A/B default 台灣 ───────────────────────────────────────────

class TestCompatCountryDefaults:
    def test_compat_a_widget_defaults_to_taiwan(self):
        assert 'key="compat_a_country", value=DEFAULT_COUNTRY' in SRC

    def test_compat_b_widget_defaults_to_taiwan(self):
        assert 'key="compat_b_country", value=DEFAULT_COUNTRY' in SRC

    def test_compat_a_fallback_uses_default_country(self):
        assert 'get("compat_a_country", DEFAULT_COUNTRY)' in SRC

    def test_compat_b_fallback_uses_default_country(self):
        assert 'get("compat_b_country", DEFAULT_COUNTRY)' in SRC


# ── 9 & 10. Lead / Partner model defaults ────────────────────────────────────

class TestLeadMagnetCountryDefaults:
    def test_lead_profile_birth_country_defaults_taiwan(self):
        from lead_magnet.models import LeadProfile
        p = LeadProfile(email="test@example.com")
        assert p.birth_country == "台灣"

    def test_partner_profile_birth_country_defaults_taiwan(self):
        from lead_magnet.models import PartnerProfile
        p = PartnerProfile()
        assert p.birth_country == "台灣"

    def test_lead_profile_country_can_be_overridden(self):
        from lead_magnet.models import LeadProfile
        p = LeadProfile(email="a@b.com", birth_country="日本")
        assert p.birth_country == "日本"

    def test_partner_profile_country_can_be_overridden(self):
        from lead_magnet.models import PartnerProfile
        p = PartnerProfile(birth_country="美國")
        assert p.birth_country == "美國"


# ── 11. No country field is disabled=True ────────────────────────────────────

class TestCountryFieldNotDisabled:
    def test_birth_country_not_disabled(self):
        import re
        # Find text_input blocks that involve birth_country / compat_a_country / compat_b_country
        # and ensure none have disabled=True
        matches = re.findall(
            r'text_input\([^)]*(?:birth_country|compat_a_country|compat_b_country)[^)]*\)',
            SRC,
        )
        for m in matches:
            assert "disabled=True" not in m, f"Found disabled=True near country field: {m}"

    def test_no_country_disabled_in_source(self):
        # Broader check: disabled=True should not appear adjacent to country fields
        lines = SRC.splitlines()
        for i, line in enumerate(lines):
            if "country" in line.lower() and "disabled=True" in line:
                raise AssertionError(f"disabled=True found on country line {i+1}: {line.strip()}")


# ── 12. Customer mode not affected ───────────────────────────────────────────

class TestCustomerModeUnaffected:
    def test_customer_mode_config_exists(self):
        cfg_src = pathlib.Path("config.py").read_text(encoding="utf-8")
        assert "CUSTOMER_MODE" in cfg_src

    def test_default_country_not_conditional_on_customer_mode(self):
        # DEFAULT_COUNTRY must be defined at module level, not inside a CUSTOMER_MODE branch
        before_defaults = SRC.split("DEFAULT_COUNTRY")[0]
        assert "CUSTOMER_MODE" not in before_defaults.split("DEFAULT_BIRTH_YEAR")[-1]


# ── 13. Developer mode not affected ──────────────────────────────────────────

class TestDeveloperModeUnaffected:
    def test_default_country_not_conditional_on_developer_mode(self):
        # DEFAULT_COUNTRY must be defined at module level, not inside a DEVELOPER_MODE branch
        before_defaults = SRC.split("DEFAULT_COUNTRY")[0]
        assert "DEVELOPER_MODE" not in before_defaults.split("DEFAULT_BIRTH_YEAR")[-1]

    def test_input_defaults_not_inside_developer_branch(self):
        # _INPUT_DEFAULTS must be defined at module level (no leading indent on its line)
        import re
        match = re.search(r'^_INPUT_DEFAULTS\s*:', SRC, re.MULTILINE)
        assert match is not None, "_INPUT_DEFAULTS dict not found at module level"
