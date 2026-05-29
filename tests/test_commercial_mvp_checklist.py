"""
Tests for V2.0.0 Commercial MVP Checklist and supporting documentation.
"""
import pathlib

ROOT = pathlib.Path(__file__).parent.parent


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class TestCommercialMvpChecklist:
    def test_checklist_exists(self):
        assert (ROOT / "COMMERCIAL_MVP_CHECKLIST.md").is_file()

    def test_contains_customer_mode(self):
        assert "Customer Mode" in _read("COMMERCIAL_MVP_CHECKLIST.md")

    def test_contains_consultant_mode(self):
        assert "Consultant Mode" in _read("COMMERCIAL_MVP_CHECKLIST.md")

    def test_contains_developer_mode(self):
        assert "Developer Mode" in _read("COMMERCIAL_MVP_CHECKLIST.md")

    def test_contains_privacy(self):
        assert "Privacy" in _read("COMMERCIAL_MVP_CHECKLIST.md")

    def test_contains_release_build(self):
        assert "Release Build" in _read("COMMERCIAL_MVP_CHECKLIST.md")

    def test_contains_go_no_go(self):
        text = _read("COMMERCIAL_MVP_CHECKLIST.md")
        assert "Go" in text and "No-Go" in text

    def test_contains_customer_delivery(self):
        text = _read("COMMERCIAL_MVP_CHECKLIST.md")
        assert "Customer Delivery" in text or "setup.bat" in text

    def test_contains_privacy_section(self):
        text = _read("COMMERCIAL_MVP_CHECKLIST.md")
        assert "no external email" in text.lower() or "email" in text.lower()

    def test_version_200_mentioned(self):
        assert "2.0.0" in _read("COMMERCIAL_MVP_CHECKLIST.md")


class TestKnownIssues:
    def test_known_issues_exists(self):
        assert (ROOT / "KNOWN_ISSUES.md").is_file()

    def test_known_issues_mentions_ziwei_snapshot(self):
        text = _read("KNOWN_ISSUES.md")
        assert "Zi Wei" in text or "ziwei" in text.lower() or "紫微" in text

    def test_known_issues_mentions_pdf_optional(self):
        text = _read("KNOWN_ISSUES.md")
        assert "PDF" in text and ("optional" in text.lower() or "WeasyPrint" in text)

    def test_known_issues_mentions_stored_snapshot(self):
        text = _read("KNOWN_ISSUES.md")
        assert "snapshot" in text.lower() or "pre-existing" in text.lower()

    def test_known_issues_version_200(self):
        assert "2.0.0" in _read("KNOWN_ISSUES.md")


class TestConsultantReadme:
    def test_consultant_readme_exists(self):
        assert (ROOT / "CONSULTANT_README.md").is_file()

    def test_consultant_readme_mentions_run_consultant_bat(self):
        assert "run_consultant.bat" in _read("CONSULTANT_README.md")

    def test_consultant_readme_mentions_lead_funnel(self):
        text = _read("CONSULTANT_README.md")
        assert "Lead Funnel" in text or "lead funnel" in text.lower()

    def test_consultant_readme_mentions_client_cases(self):
        text = _read("CONSULTANT_README.md")
        assert "客戶個案" in text or "client case" in text.lower()

    def test_consultant_readme_mentions_privacy(self):
        text = _read("CONSULTANT_README.md")
        assert "隱私" in text or "privacy" in text.lower() or "本機" in text

    def test_consultant_readme_no_rossi(self):
        assert "rossi" not in _read("CONSULTANT_README.md").lower()
