"""
Tests for V1.9.6 Lead Magnet Models.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


class TestLeadProfileModel:
    def test_lead_profile_createable(self):
        from lead_magnet.models import LeadProfile
        p = LeadProfile(email="test@example.com")
        assert p.email == "test@example.com"

    def test_lead_profile_name_default_empty(self):
        from lead_magnet.models import LeadProfile
        p = LeadProfile(email="a@b.com")
        assert p.name == ""

    def test_lead_profile_timezone_default(self):
        from lead_magnet.models import LeadProfile
        p = LeadProfile(email="a@b.com")
        assert p.timezone == "Asia/Taipei"

    def test_lead_profile_no_password_field(self):
        from lead_magnet.models import LeadProfile
        fields = LeadProfile.model_fields.keys()
        assert "password" not in fields
        assert "api_key" not in fields
        assert "payment" not in fields


class TestPartnerProfileModel:
    def test_partner_profile_createable(self):
        from lead_magnet.models import PartnerProfile
        p = PartnerProfile(name="Partner")
        assert p.name == "Partner"

    def test_partner_profile_birth_date_optional(self):
        from lead_magnet.models import PartnerProfile
        p = PartnerProfile()
        assert p.birth_date is None

    def test_partner_profile_timezone_default(self):
        from lead_magnet.models import PartnerProfile
        p = PartnerProfile()
        assert p.timezone == "Asia/Taipei"


class TestLeadCaptureModel:
    def test_lead_capture_createable(self):
        from lead_magnet.models import LeadCapture, LeadProfile
        lc = LeadCapture(profile=LeadProfile(email="a@b.com"))
        assert lc.profile.email == "a@b.com"

    def test_consent_given_default_false(self):
        from lead_magnet.models import LeadCapture
        lc = LeadCapture()
        assert lc.consent_given is False

    def test_marketing_consent_default_false(self):
        from lead_magnet.models import LeadCapture
        lc = LeadCapture()
        assert lc.marketing_consent is False

    def test_report_type_default(self):
        from lead_magnet.models import LeadCapture
        lc = LeadCapture()
        assert lc.report_type == "zodiac_free_summary"

    def test_tags_default_empty(self):
        from lead_magnet.models import LeadCapture
        lc = LeadCapture()
        assert lc.tags == []

    def test_email_field_exists(self):
        from lead_magnet.models import LeadProfile
        p = LeadProfile(email="hello@world.com")
        assert p.email == "hello@world.com"


class TestFreeReportResultModel:
    def test_free_report_result_createable(self):
        from lead_magnet.models import FreeReportResult
        r = FreeReportResult(title="Test", report_type="zodiac_free_summary")
        assert r.title == "Test"

    def test_sections_default_empty(self):
        from lead_magnet.models import FreeReportResult
        r = FreeReportResult()
        assert r.sections == []

    def test_disclaimer_default_not_empty(self):
        from lead_magnet.models import FreeReportResult
        r = FreeReportResult()
        assert r.disclaimer != ""

    def test_no_password_payment_fields(self):
        from lead_magnet.models import FreeReportResult
        fields = FreeReportResult.model_fields.keys()
        assert "password" not in fields
        assert "payment" not in fields


class TestFreeReportSectionModel:
    def test_section_createable(self):
        from lead_magnet.models import FreeReportSection
        s = FreeReportSection(heading="H", body="B")
        assert s.heading == "H"

    def test_bullets_default_empty(self):
        from lead_magnet.models import FreeReportSection
        s = FreeReportSection()
        assert s.bullets == []


class TestLeadStorageSnapshotModel:
    def test_snapshot_createable(self):
        from lead_magnet.models import LeadStorageSnapshot
        snap = LeadStorageSnapshot()
        assert snap.leads == []
        assert snap.version == "1.9.6"
