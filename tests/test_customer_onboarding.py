"""
Tests for V2.0.2 Customer Onboarding Document.
"""
import pathlib

ROOT = pathlib.Path(__file__).parent.parent


def _read(filename: str) -> str:
    return (ROOT / filename).read_text(encoding="utf-8")


class TestCustomerOnboardingExists:
    def test_customer_onboarding_exists(self):
        assert (ROOT / "CUSTOMER_ONBOARDING.md").is_file()

    def test_release_qa_checklist_exists(self):
        assert (ROOT / "RELEASE_QA_CHECKLIST.md").is_file()


class TestCustomerOnboardingContent:
    def _text(self) -> str:
        return _read("CUSTOMER_ONBOARDING.md")

    def test_contains_setup_bat(self):
        assert "setup.bat" in self._text()

    def test_contains_run_bat(self):
        assert "run.bat" in self._text()

    def test_contains_input_data_step(self):
        assert "輸入資料" in self._text()

    def test_contains_export_step(self):
        assert "匯出" in self._text()

    def test_contains_privacy_section(self):
        assert "本機資料與隱私" in self._text()

    def test_contains_disclaimer(self):
        assert "免責聲明" in self._text()

    def test_does_not_contain_run_dev_bat(self):
        text = self._text()
        # run_dev.bat should not appear in customer onboarding
        assert "run_dev.bat" not in text

    def test_does_not_contain_rossi(self):
        assert "rossi" not in self._text().lower()

    def test_does_not_contain_golden_case(self):
        assert "golden case" not in self._text().lower()

    def test_does_not_contain_debug(self):
        assert "debug" not in self._text().lower()

    def test_does_not_contain_calibration_section(self):
        # "calibration" as developer term should not appear
        assert "calibration" not in self._text().lower()

    def test_contains_version_203(self):
        assert "2.0.3" in self._text()


class TestCustomerReadmeLinksOnboarding:
    def test_customer_readme_references_onboarding(self):
        text = _read("CUSTOMER_README.md")
        assert "CUSTOMER_ONBOARDING.md" in text

    def test_customer_readme_version_203(self):
        text = _read("CUSTOMER_README.md")
        assert "2.0.3" in text
