"""
Tests for V2.0.0 Release Documentation.
"""
import pathlib

ROOT = pathlib.Path(__file__).parent.parent


def _read(filename: str) -> str:
    return (ROOT / filename).read_text(encoding="utf-8")


class TestCustomerReadme:
    def test_contains_setup_bat(self):
        assert "setup.bat" in _read("CUSTOMER_README.md")

    def test_contains_run_bat(self):
        assert "run.bat" in _read("CUSTOMER_README.md")

    def test_contains_customer_mode(self):
        text = _read("CUSTOMER_README.md")
        assert "客戶模式" in text

    def test_contains_disclaimer(self):
        text = _read("CUSTOMER_README.md")
        assert "免責聲明" in text

    def test_does_not_contain_golden_case(self):
        assert "golden case" not in _read("CUSTOMER_README.md").lower()

    def test_does_not_contain_rossi(self):
        assert "rossi" not in _read("CUSTOMER_README.md").lower()

    def test_run_dev_bat_not_promoted_as_normal_flow(self):
        text = _read("CUSTOMER_README.md")
        if "run_dev.bat" in text:
            lines = [l for l in text.splitlines() if "run_dev.bat" in l]
            for line in lines:
                # Must only appear in a developer/dev-marked context
                assert any(kw in line.lower() for kw in ["開發", "developer", "dev"]), (
                    f"run_dev.bat appears in non-developer context: {line}"
                )

    def test_does_not_contain_debug_term(self):
        # "debug" as internal keyword
        text = _read("CUSTOMER_README.md")
        assert "debug" not in text.lower()

    def test_does_not_contain_api_key(self):
        assert "api_key" not in _read("CUSTOMER_README.md").lower()

    def test_contains_privacy_info(self):
        text = _read("CUSTOMER_README.md")
        assert "本機" in text or "local" in text.lower() or "隱私" in text


class TestCustomerOnboardingDocExists:
    def test_customer_onboarding_exists(self):
        import pathlib
        assert (pathlib.Path(__file__).parent.parent / "CUSTOMER_ONBOARDING.md").is_file()

    def test_customer_onboarding_no_run_dev_bat(self):
        assert "run_dev.bat" not in _read("CUSTOMER_ONBOARDING.md")

    def test_customer_onboarding_no_rossi(self):
        assert "rossi" not in _read("CUSTOMER_ONBOARDING.md").lower()

    def test_release_qa_checklist_exists(self):
        import pathlib
        assert (pathlib.Path(__file__).parent.parent / "RELEASE_QA_CHECKLIST.md").is_file()


class TestReleaseNotes:
    def test_contains_version_202(self):
        assert "2.0.2" in _read("RELEASE_NOTES.md")

    def test_contains_version_200(self):
        assert "2.0.0" in _read("RELEASE_NOTES.md")

    def test_contains_privacy_section(self):
        text = _read("RELEASE_NOTES.md")
        assert "Privacy" in text or "隱私" in text

    def test_contains_known_limitations(self):
        text = _read("RELEASE_NOTES.md")
        assert "Known Limitations" in text or "限制" in text or "PDF" in text

    def test_contains_version_summary(self):
        text = _read("RELEASE_NOTES.md")
        assert "Version" in text or "版本" in text

    def test_does_not_contain_rossi(self):
        assert "rossi" not in _read("RELEASE_NOTES.md").lower()


class TestVersionTxt:
    def test_contains_version_203(self):
        assert "Version: 2.0.3" in _read("VERSION.txt")

    def test_contains_version_200_or_203(self):
        text = _read("VERSION.txt")
        assert "2.0.0" in text or "2.0.3" in text

    def test_contains_build_profiles(self):
        text = _read("VERSION.txt")
        assert "Build Profiles" in text or "customer" in text.lower()

    def test_contains_features(self):
        text = _read("VERSION.txt")
        assert "Features:" in text or "features" in text.lower()

    def test_contains_privacy_section(self):
        text = _read("VERSION.txt")
        assert "Privacy:" in text or "privacy" in text.lower()

    def test_not_empty(self):
        assert len(_read("VERSION.txt").strip()) > 50


class TestConsultantReadmeExists:
    def test_consultant_readme_exists(self):
        import pathlib
        assert (pathlib.Path(__file__).parent.parent / "CONSULTANT_README.md").is_file()

    def test_consultant_readme_has_version(self):
        text = _read("CONSULTANT_README.md")
        assert "2.0" in text

    def test_consultant_readme_no_rossi(self):
        assert "rossi" not in _read("CONSULTANT_README.md").lower()
