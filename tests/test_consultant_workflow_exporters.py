"""
Tests for V1.9.8 Consultant Workflow Exporters.
"""
import pytest
from consultant_workflow.models import (
    ClientCase, ClientProfile, ClientCaseSnapshot,
    CaseNote, CaseTask, ReportDelivery,
)
from consultant_workflow.exporters import (
    export_case_markdown, export_case_html,
    export_cases_csv, export_case_metrics_markdown,
    safe_case_filename,
)
from consultant_workflow.storage import export_cases_csv as _storage_csv


def _basic_case():
    return ClientCase(
        case_id="case_test_001",
        client=ClientProfile(name="Alice", email="a@a.com", birth_country="台灣"),
        case_status="data_collected",
        report_status="draft",
        requested_report_types=["natal", "integrated"],
        next_action="Review data",
    )


class TestExportCaseMarkdown:
    def test_contains_title(self):
        md = export_case_markdown(_basic_case())
        assert "Client Case Summary" in md

    def test_contains_case_status(self):
        md = export_case_markdown(_basic_case())
        assert "Case Status" in md

    def test_contains_report_status(self):
        md = export_case_markdown(_basic_case())
        assert "Report Status" in md

    def test_contains_client_name(self):
        md = export_case_markdown(_basic_case())
        assert "Alice" in md

    def test_contains_requested_reports(self):
        md = export_case_markdown(_basic_case())
        assert "natal" in md
        assert "integrated" in md

    def test_contains_next_action(self):
        md = export_case_markdown(_basic_case())
        assert "Next Action" in md

    def test_contains_tasks_section(self):
        md = export_case_markdown(_basic_case())
        assert "Tasks" in md

    def test_contains_deliveries_section(self):
        md = export_case_markdown(_basic_case())
        assert "Deliveries" in md

    def test_contains_notes_section(self):
        md = export_case_markdown(_basic_case())
        assert "Notes" in md

    def test_empty_notes_no_crash(self):
        c = _basic_case()
        c.notes = []
        md = export_case_markdown(c)
        assert "Notes" in md

    def test_empty_tasks_no_crash(self):
        c = _basic_case()
        c.tasks = []
        md = export_case_markdown(c)
        assert "Tasks" in md


class TestExportCaseHTML:
    def test_contains_meta_charset_utf8(self):
        html = export_case_html(_basic_case())
        assert 'meta charset="utf-8"' in html

    def test_no_script_tags(self):
        html = export_case_html(_basic_case())
        assert "<script" not in html

    def test_no_cdn_links(self):
        html = export_case_html(_basic_case())
        assert "cdn." not in html.lower()

    def test_has_footer(self):
        html = export_case_html(_basic_case())
        assert "footer" in html.lower()

    def test_contains_client_name(self):
        html = export_case_html(_basic_case())
        assert "Alice" in html

    def test_deliveries_section_present(self):
        html = export_case_html(_basic_case())
        assert "Deliveries" in html


class TestExportCasesCSV:
    def test_csv_works(self):
        snap = ClientCaseSnapshot(cases=[_basic_case()])
        csv_str = export_cases_csv(snap)
        assert "case_id" in csv_str
        assert "case_test_001" in csv_str

    def test_csv_has_expected_headers(self):
        snap = ClientCaseSnapshot(cases=[])
        csv_str = export_cases_csv(snap)
        for col in ("case_id", "client_name", "client_email", "case_status", "report_status"):
            assert col in csv_str


class TestExportCaseMetricsMarkdown:
    def test_works(self):
        metrics = {
            "total": 3,
            "by_case_status": {"new_lead": 2, "delivered": 1},
            "by_report_status": {"not_started": 2, "delivered": 1},
            "open_tasks": 5,
            "overdue_tasks": 1,
            "delivered_count": 1,
            "follow_up_count": 0,
        }
        result = export_case_metrics_markdown(metrics)
        assert "Case Metrics" in result
        assert "3" in result
        assert "new_lead" in result


class TestSafeCaseFilename:
    def test_no_illegal_chars(self):
        name = safe_case_filename("Alice<>:/\\", "md")
        for ch in '<>:/\\|?*"':
            assert ch not in name

    def test_no_emoji(self):
        name = safe_case_filename("Alice 🎉 Test", "md")
        assert "🎉" not in name

    def test_has_correct_suffix(self):
        name = safe_case_filename("Alice", "md")
        assert name.endswith(".md")

    def test_html_suffix(self):
        name = safe_case_filename("Bob", "html")
        assert name.endswith(".html")

    def test_csv_suffix(self):
        name = safe_case_filename("all", "csv")
        assert name.endswith(".csv")

    def test_starts_with_client_case(self):
        name = safe_case_filename("Alice", "md")
        assert name.startswith("client_case_")
