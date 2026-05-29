"""
Tests for V1.9.8 Consultant Workflow Models.
"""
import pytest
from consultant_workflow.models import (
    ClientProfile, CaseNote, CaseTask, ReportDelivery,
    ClientCase, ClientCaseSnapshot,
    CASE_STATUS_VALUES, REPORT_STATUS_VALUES,
)


class TestClientProfileModel:
    def test_createable(self):
        p = ClientProfile(name="Test", email="t@t.com")
        assert p.name == "Test"

    def test_birth_country_defaults_taiwan(self):
        p = ClientProfile()
        assert p.birth_country == "台灣"

    def test_birth_country_can_be_overridden(self):
        p = ClientProfile(birth_country="日本")
        assert p.birth_country == "日本"

    def test_email_optional(self):
        p = ClientProfile(name="A")
        assert p.email == ""

    def test_tags_default_empty(self):
        p = ClientProfile()
        assert p.tags == []

    def test_no_password_field(self):
        fields = ClientProfile.model_fields.keys()
        assert "password" not in fields
        assert "api_key" not in fields

    def test_no_payment_field(self):
        fields = ClientProfile.model_fields.keys()
        assert "payment" not in fields
        assert "credit_card" not in fields


class TestCaseNoteModel:
    def test_createable(self):
        n = CaseNote(content="test note")
        assert n.content == "test note"

    def test_author_default(self):
        n = CaseNote()
        assert n.author == "consultant"

    def test_note_type_default_general(self):
        n = CaseNote()
        assert n.note_type == "general"

    def test_tags_default_empty(self):
        n = CaseNote()
        assert n.tags == []


class TestCaseTaskModel:
    def test_createable(self):
        t = CaseTask(title="Do something")
        assert t.title == "Do something"

    def test_status_default_todo(self):
        t = CaseTask(title="X")
        assert t.status == "todo"

    def test_priority_default_medium(self):
        t = CaseTask(title="X")
        assert t.priority == "medium"

    def test_completed_at_default_empty(self):
        t = CaseTask(title="X")
        assert t.completed_at == ""


class TestReportDeliveryModel:
    def test_createable(self):
        d = ReportDelivery(report_type="natal", format="html")
        assert d.report_type == "natal"
        assert d.format == "html"

    def test_status_default_delivered(self):
        d = ReportDelivery()
        assert d.status == "delivered"

    def test_delivery_id_default_empty(self):
        d = ReportDelivery()
        assert d.delivery_id == ""


class TestClientCaseModel:
    def test_createable(self):
        c = ClientCase(client=ClientProfile(name="Test"))
        assert c.client.name == "Test"

    def test_case_status_default_new_lead(self):
        c = ClientCase()
        assert c.case_status == "new_lead"

    def test_report_status_default_not_started(self):
        c = ClientCase()
        assert c.report_status == "not_started"

    def test_notes_default_empty(self):
        c = ClientCase()
        assert c.notes == []

    def test_tasks_default_empty(self):
        c = ClientCase()
        assert c.tasks == []

    def test_deliveries_default_empty(self):
        c = ClientCase()
        assert c.deliveries == []

    def test_tags_default_empty(self):
        c = ClientCase()
        assert c.tags == []

    def test_partner_optional(self):
        c = ClientCase()
        assert c.partner is None


class TestClientCaseSnapshotModel:
    def test_createable(self):
        s = ClientCaseSnapshot()
        assert s.cases == []

    def test_version_default(self):
        s = ClientCaseSnapshot()
        assert s.version == "1.9.8"


class TestStatusValues:
    def test_case_status_includes_new_lead(self):
        assert "new_lead" in CASE_STATUS_VALUES

    def test_case_status_includes_all_expected(self):
        for s in ("contacted", "data_collected", "report_generated", "delivered", "follow_up", "closed"):
            assert s in CASE_STATUS_VALUES

    def test_report_status_includes_delivered(self):
        assert "delivered" in REPORT_STATUS_VALUES

    def test_report_status_includes_all_expected(self):
        for s in ("not_started", "draft", "generated", "reviewed", "revised"):
            assert s in REPORT_STATUS_VALUES
