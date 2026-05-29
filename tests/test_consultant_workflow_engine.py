"""
Tests for V1.9.8 Consultant Workflow Engine.
"""
import pytest
from consultant_workflow.models import (
    ClientCase, ClientProfile, ClientCaseSnapshot,
)
from consultant_workflow.engine import (
    create_case_from_lead, suggest_next_action,
    summarize_case, compute_case_metrics, filter_cases,
)


def _make_lead(
    name="Alice", email="a@a.com", birth_date="1990-01-01",
    birth_time="10:00", birth_location="台北", birth_country="台灣",
    report_type="zodiac_free_summary", lead_id="lead_001",
    source_page_slug="free_report",
):
    from lead_magnet.models import LeadCapture, LeadProfile
    profile = LeadProfile(
        name=name,
        email=email,
        birth_date=birth_date,
        birth_time=birth_time,
        birth_location=birth_location,
        birth_country=birth_country,
    )
    return LeadCapture(
        lead_id=lead_id,
        profile=profile,
        report_type=report_type,
        source_page_slug=source_page_slug,
        consent_given=True,
    )


class TestCreateCaseFromLead:
    def test_create_case_from_lead_works(self):
        lead = _make_lead()
        case = create_case_from_lead(lead)
        assert case.client.name == "Alice"

    def test_source_lead_id_copied(self):
        lead = _make_lead(lead_id="lead_xyz")
        case = create_case_from_lead(lead)
        assert case.source_lead_id == "lead_xyz"

    def test_email_copied(self):
        lead = _make_lead(email="hello@world.com")
        case = create_case_from_lead(lead)
        assert case.client.email == "hello@world.com"

    def test_birth_country_copied(self):
        lead = _make_lead(birth_country="台灣")
        case = create_case_from_lead(lead)
        assert case.client.birth_country == "台灣"

    def test_birth_country_defaults_taiwan_when_empty(self):
        lead = _make_lead(birth_country="")
        case = create_case_from_lead(lead)
        assert case.client.birth_country == "台灣"

    def test_report_type_mapping_zodiac(self):
        lead = _make_lead(report_type="zodiac_free_summary")
        case = create_case_from_lead(lead)
        assert "natal" in case.requested_report_types
        assert "integrated" in case.requested_report_types

    def test_report_type_mapping_human_design(self):
        lead = _make_lead(report_type="human_design_free_summary")
        case = create_case_from_lead(lead)
        assert "human_design" in case.requested_report_types

    def test_report_type_mapping_compatibility(self):
        lead = _make_lead(report_type="compatibility_free_summary")
        case = create_case_from_lead(lead)
        assert "compatibility" in case.requested_report_types

    def test_report_type_mapping_integrated(self):
        lead = _make_lead(report_type="integrated_free_summary")
        case = create_case_from_lead(lead)
        assert "integrated" in case.requested_report_types

    def test_case_status_is_new_lead(self):
        lead = _make_lead()
        case = create_case_from_lead(lead)
        assert case.case_status == "new_lead"

    def test_report_status_is_not_started(self):
        lead = _make_lead()
        case = create_case_from_lead(lead)
        assert case.report_status == "not_started"

    def test_tags_includes_from_lead(self):
        lead = _make_lead()
        case = create_case_from_lead(lead)
        assert "from_lead" in case.tags


class TestSuggestNextAction:
    def test_new_lead(self):
        c = ClientCase(case_status="new_lead")
        result = suggest_next_action(c)
        assert result != ""

    def test_delivered(self):
        c = ClientCase(case_status="delivered")
        result = suggest_next_action(c)
        assert result != ""

    def test_closed_empty(self):
        c = ClientCase(case_status="closed")
        result = suggest_next_action(c)
        assert result == ""


class TestSummarizeCase:
    def test_not_empty(self):
        c = ClientCase(client=ClientProfile(name="Bob"))
        result = summarize_case(c)
        assert len(result) > 10

    def test_contains_client_name(self):
        c = ClientCase(client=ClientProfile(name="Carol"))
        result = summarize_case(c)
        assert "Carol" in result


class TestComputeCaseMetrics:
    def test_total(self):
        snap = ClientCaseSnapshot(cases=[
            ClientCase(client=ClientProfile(name="A"), case_status="new_lead"),
            ClientCase(client=ClientProfile(name="B"), case_status="delivered"),
        ])
        m = compute_case_metrics(snap)
        assert m["total"] == 2

    def test_by_case_status(self):
        snap = ClientCaseSnapshot(cases=[
            ClientCase(client=ClientProfile(name="A"), case_status="new_lead"),
            ClientCase(client=ClientProfile(name="B"), case_status="new_lead"),
            ClientCase(client=ClientProfile(name="C"), case_status="delivered"),
        ])
        m = compute_case_metrics(snap)
        assert m["by_case_status"]["new_lead"] == 2
        assert m["by_case_status"]["delivered"] == 1

    def test_empty_snap(self):
        snap = ClientCaseSnapshot()
        m = compute_case_metrics(snap)
        assert m["total"] == 0


class TestFilterCases:
    def _snap(self):
        return ClientCaseSnapshot(cases=[
            ClientCase(case_id="c1", client=ClientProfile(name="Alice", email="a@a.com"),
                       case_status="new_lead", requested_report_types=["natal"]),
            ClientCase(case_id="c2", client=ClientProfile(name="Bob", email="b@b.com"),
                       case_status="delivered", requested_report_types=["compatibility"]),
        ])

    def test_filter_by_status(self):
        results = filter_cases(self._snap(), status="new_lead")
        assert len(results) == 1
        assert results[0].client.name == "Alice"

    def test_filter_by_keyword(self):
        results = filter_cases(self._snap(), keyword="bob")
        assert len(results) == 1
        assert results[0].client.name == "Bob"

    def test_no_filter_returns_all(self):
        results = filter_cases(self._snap())
        assert len(results) == 2
