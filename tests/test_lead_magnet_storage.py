"""
Tests for V1.9.6 Lead Magnet Storage.
"""
import sys
import os
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


def _make_lead(email="test@example.com", report_type="zodiac_free_summary", consent=True):
    from lead_magnet.models import LeadCapture, LeadProfile
    return LeadCapture(
        profile=LeadProfile(name="Test User", email=email),
        report_type=report_type,
        consent_given=consent,
    )


class TestValidateEmail:
    def test_valid_email(self):
        from lead_magnet.storage import validate_email
        assert validate_email("user@example.com") is True

    def test_valid_email_with_subdomain(self):
        from lead_magnet.storage import validate_email
        assert validate_email("user@mail.example.com") is True

    def test_invalid_no_at(self):
        from lead_magnet.storage import validate_email
        assert validate_email("userexample.com") is False

    def test_invalid_no_domain_dot(self):
        from lead_magnet.storage import validate_email
        assert validate_email("user@nodot") is False

    def test_invalid_empty_string(self):
        from lead_magnet.storage import validate_email
        assert validate_email("") is False

    def test_invalid_with_space(self):
        from lead_magnet.storage import validate_email
        assert validate_email("user @example.com") is False


class TestMakeLeadId:
    def test_does_not_contain_full_email(self):
        from lead_magnet.storage import make_lead_id
        lid = make_lead_id("secret@email.com", "zodiac_free_summary")
        assert "secret@email.com" not in lid

    def test_starts_with_lead_prefix(self):
        from lead_magnet.storage import make_lead_id
        lid = make_lead_id("a@b.com", "zodiac_free_summary")
        assert lid.startswith("lead_")

    def test_unique_ids(self):
        from lead_magnet.storage import make_lead_id
        import time
        id1 = make_lead_id("a@b.com", "zodiac_free_summary")
        time.sleep(0.01)
        id2 = make_lead_id("a@b.com", "zodiac_free_summary")
        assert id1 != id2


class TestLoadSaveLeads:
    def test_load_missing_returns_empty_snapshot(self):
        from lead_magnet.storage import load_leads
        result = load_leads(Path("/nonexistent/leads.json"))
        assert result.leads == []

    def test_save_load_roundtrip(self):
        from lead_magnet.storage import save_leads, load_leads
        from lead_magnet.models import LeadStorageSnapshot
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "leads.json"
            snap = LeadStorageSnapshot(leads=[_make_lead()])
            save_leads(snap, path)
            loaded = load_leads(path)
            assert len(loaded.leads) == 1
            assert loaded.leads[0].profile.email == "test@example.com"


class TestAppendLead:
    def test_requires_consent(self):
        from lead_magnet.storage import append_lead
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "leads.json"
            with pytest.raises(ValueError, match="consent"):
                append_lead(_make_lead(consent=False), path)

    def test_requires_valid_email(self):
        from lead_magnet.storage import append_lead
        from lead_magnet.models import LeadCapture, LeadProfile
        bad = LeadCapture(
            profile=LeadProfile(email="not-an-email"),
            consent_given=True,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "leads.json"
            with pytest.raises(ValueError, match="email"):
                append_lead(bad, path)

    def test_saves_file(self):
        from lead_magnet.storage import append_lead, load_leads
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "leads.json"
            append_lead(_make_lead(), path)
            assert path.exists()
            snap = load_leads(path)
            assert len(snap.leads) == 1

    def test_duplicate_email_report_type_tags(self):
        from lead_magnet.storage import append_lead, load_leads
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "leads.json"
            append_lead(_make_lead("dup@test.com", "zodiac_free_summary"), path)
            result = append_lead(_make_lead("dup@test.com", "zodiac_free_summary"), path)
            assert "duplicate_possible" in result.tags


class TestExportLeadsCsv:
    def test_contains_headers(self):
        from lead_magnet.storage import export_leads_csv
        from lead_magnet.models import LeadStorageSnapshot
        snap = LeadStorageSnapshot(leads=[_make_lead()])
        csv_str = export_leads_csv(snap)
        assert "lead_id" in csv_str
        assert "email" in csv_str
        assert "report_type" in csv_str

    def test_does_not_contain_birth_time(self):
        from lead_magnet.storage import export_leads_csv
        from lead_magnet.models import LeadStorageSnapshot, LeadCapture, LeadProfile
        lc = LeadCapture(
            profile=LeadProfile(email="a@b.com", birth_time="12:00"),
            consent_given=True,
        )
        snap = LeadStorageSnapshot(leads=[lc])
        csv_str = export_leads_csv(snap)
        assert "birth_time" not in csv_str


class TestDeleteAllLeads:
    def test_delete_removes_file(self):
        from lead_magnet.storage import append_lead, delete_all_leads
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "leads.json"
            append_lead(_make_lead(), path)
            assert path.exists()
            delete_all_leads(path)
            assert not path.exists()

    def test_delete_missing_no_crash(self):
        from lead_magnet.storage import delete_all_leads
        delete_all_leads(Path("/nonexistent/leads.json"))
