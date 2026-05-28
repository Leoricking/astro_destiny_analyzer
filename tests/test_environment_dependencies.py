"""
Tests for V1.8.3 environment dependency verification.
Validates requirements.txt content, check_env structure, and dependency categories.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_requirements() -> str:
    path = os.path.join(PROJECT_ROOT, "requirements.txt")
    with open(path, encoding="utf-8") as f:
        return f.read()


# ══════════════════════════════════════════════════════════════════════════════
# A. requirements.txt — required packages present
# ══════════════════════════════════════════════════════════════════════════════

class TestRequirementsTxt:
    def test_file_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "requirements.txt"))

    def test_contains_pydantic(self):
        assert "pydantic" in _read_requirements()

    def test_contains_python_docx(self):
        assert "python-docx" in _read_requirements()

    def test_contains_markdown(self):
        assert "Markdown" in _read_requirements() or "markdown" in _read_requirements().lower()

    def test_contains_pyswisseph(self):
        assert "pyswisseph" in _read_requirements()

    def test_contains_lunardate(self):
        assert "lunardate" in _read_requirements()

    def test_contains_streamlit(self):
        assert "streamlit" in _read_requirements()

    def test_contains_jinja2(self):
        assert "jinja2" in _read_requirements().lower()

    def test_contains_pytest(self):
        assert "pytest" in _read_requirements()

    def test_weasyprint_not_required(self):
        """WeasyPrint must NOT be an uncommented required dependency."""
        req = _read_requirements()
        lines = [l.strip() for l in req.splitlines()]
        for line in lines:
            if "weasyprint" in line.lower():
                assert line.startswith("#"), (
                    "weasyprint must not be an uncommented required dependency"
                )


# ══════════════════════════════════════════════════════════════════════════════
# B. check_env.py — structure and required/optional distinction
# ══════════════════════════════════════════════════════════════════════════════

class TestCheckEnvStructure:
    def test_importable(self):
        import scripts.check_env as ce
        assert ce is not None

    def test_has_main(self):
        import scripts.check_env as ce
        assert callable(getattr(ce, "main", None))

    def test_main_returns_0_or_1(self):
        import scripts.check_env as ce
        result = ce.main()
        assert result in (0, 1)

    def test_required_packages_listed(self):
        src_path = os.path.join(PROJECT_ROOT, "scripts", "check_env.py")
        with open(src_path, encoding="utf-8") as f:
            src = f.read()
        assert "python-docx" in src
        assert "pydantic" in src

    def test_weasyprint_is_optional_check(self):
        src_path = os.path.join(PROJECT_ROOT, "scripts", "check_env.py")
        with open(src_path, encoding="utf-8") as f:
            src = f.read()
        assert "weasyprint" in src
        assert "WARN" in src or "optional" in src.lower()

    def test_weasyprint_does_not_increment_errors(self):
        src_path = os.path.join(PROJECT_ROOT, "scripts", "check_env.py")
        with open(src_path, encoding="utf-8") as f:
            src = f.read()
        idx = src.find("weasyprint")
        weasyprint_block = src[idx: idx + 300]
        assert "errors += 1" not in weasyprint_block

    def test_docx_missing_suggests_setup_bat(self):
        src_path = os.path.join(PROJECT_ROOT, "scripts", "check_env.py")
        with open(src_path, encoding="utf-8") as f:
            src = f.read()
        assert "setup.bat" in src

    def test_weasyprint_missing_suggests_install_pdf_bat(self):
        src_path = os.path.join(PROJECT_ROOT, "scripts", "check_env.py")
        with open(src_path, encoding="utf-8") as f:
            src = f.read()
        assert "install_pdf_support.bat" in src
