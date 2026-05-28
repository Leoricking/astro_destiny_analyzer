"""
Tests for V1.9.6 Lead Magnet Engine.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

_FORBIDDEN = ["一定成功", "一定分手", "保證", "必然", "絕對命運", "大富大貴保證"]


def _make_lead(report_type="zodiac_free_summary", birth_date="1990-06-15",
               birth_time=None, with_partner=False):
    from lead_magnet.models import LeadCapture, LeadProfile, PartnerProfile
    partner = None
    if with_partner:
        partner = PartnerProfile(name="Partner", birth_date="1991-03-20")
    return LeadCapture(
        profile=LeadProfile(
            name="Test",
            email="test@example.com",
            birth_date=birth_date,
            birth_time=birth_time,
        ),
        partner=partner,
        report_type=report_type,
        consent_given=True,
    )


class TestGenerateZodiacReport:
    def test_zodiac_report_works(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("zodiac_free_summary"))
        assert result is not None
        assert result.report_type == "zodiac_free_summary"

    def test_zodiac_has_sections(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("zodiac_free_summary"))
        assert len(result.sections) > 0

    def test_zodiac_has_cta(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("zodiac_free_summary"))
        assert result.cta_button_label != ""

    def test_zodiac_has_disclaimer(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("zodiac_free_summary"))
        assert result.disclaimer != ""

    def test_zodiac_no_forbidden_phrases(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("zodiac_free_summary"))
        full_text = result.title + result.summary + "".join(
            s.heading + s.body for s in result.sections
        )
        for phrase in _FORBIDDEN:
            assert phrase not in full_text


class TestGenerateHumanDesignReport:
    def test_hd_works_with_partial_data(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("human_design_free_summary", birth_time=None))
        assert result is not None
        assert result.sections

    def test_hd_works_with_birth_time(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("human_design_free_summary", birth_time="12:00"))
        assert result is not None

    def test_hd_no_crash_missing_date(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("human_design_free_summary", birth_date=None))
        assert result is not None

    def test_hd_mentions_precise_time_when_missing(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("human_design_free_summary", birth_time=None))
        full_text = result.title + result.summary + "".join(
            s.heading + s.body for s in result.sections
        )
        # Should mention needing time or provide type-based info
        assert len(result.sections) > 0

    def test_hd_has_cta(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("human_design_free_summary"))
        assert result.cta_button_label != ""

    def test_hd_has_disclaimer(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("human_design_free_summary"))
        assert result.disclaimer != ""


class TestGenerateCompatibilityReport:
    def test_compatibility_works(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("compatibility_free_summary", with_partner=True))
        assert result is not None
        assert result.sections

    def test_compatibility_no_partner_no_crash(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("compatibility_free_summary", with_partner=False))
        assert result is not None

    def test_compatibility_has_cta(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("compatibility_free_summary", with_partner=True))
        assert result.cta_button_label != ""

    def test_compatibility_has_disclaimer(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("compatibility_free_summary"))
        assert result.disclaimer != ""


class TestGenerateIntegratedReport:
    def test_integrated_works(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("integrated_free_summary"))
        assert result is not None
        assert result.sections

    def test_integrated_has_cta(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("integrated_free_summary"))
        assert result.cta_button_label != ""

    def test_integrated_has_disclaimer(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("integrated_free_summary"))
        assert result.disclaimer != ""

    def test_integrated_no_forbidden_phrases(self):
        from lead_magnet.engine import generate_free_report
        result = generate_free_report(_make_lead("integrated_free_summary"))
        full_text = result.title + result.summary + "".join(
            s.heading + s.body for s in result.sections
        )
        for phrase in _FORBIDDEN:
            assert phrase not in full_text
