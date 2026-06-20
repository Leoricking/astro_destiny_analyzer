"""Regression tests for the Zi Wei bureau translation import hotfix."""
from pathlib import Path


def test_streamlit_app_imports_translate_ziwei_bureau():
    source = (Path(__file__).resolve().parents[1] / "ui" / "streamlit_app.py").read_text(encoding="utf-8")
    import_block = source.split("from i18n.display_names import (", 1)[1].split(")", 1)[0]
    assert "translate_ziwei_bureau" in import_block


def test_display_names_defines_translate_ziwei_bureau():
    source = (Path(__file__).resolve().parents[1] / "i18n" / "display_names.py").read_text(encoding="utf-8")
    assert "def translate_ziwei_bureau(" in source


def test_localized_ziwei_summary_uses_imported_helper():
    source = (Path(__file__).resolve().parents[1] / "ui" / "streamlit_app.py").read_text(encoding="utf-8")
    assert 'translate_ziwei_bureau(getattr(zc, "five_element_bureau"' in source
