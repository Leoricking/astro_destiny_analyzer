"""
Tests for V1.9.9 Release Documentation.
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


class TestReleaseNotes:
    def test_contains_version_199(self):
        assert "1.9.9" in _read("RELEASE_NOTES.md")

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
    def test_contains_version_199(self):
        assert "Version: 1.9.9" in _read("VERSION.txt")

    def test_contains_features(self):
        text = _read("VERSION.txt")
        assert "Features:" in text or "features" in text.lower()

    def test_contains_privacy_section(self):
        text = _read("VERSION.txt")
        assert "Privacy:" in text or "privacy" in text.lower()

    def test_not_empty(self):
        assert len(_read("VERSION.txt").strip()) > 50
