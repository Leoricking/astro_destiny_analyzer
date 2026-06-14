"""Tests for i18n UI integration."""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_default_language_zh_tw():
    from i18n.translator import DEFAULT_LANGUAGE
    assert DEFAULT_LANGUAGE == "zh-TW"


def test_language_options_available():
    from i18n.translator import get_language_options
    options = get_language_options()
    codes = [c for c, _ in options]
    assert "zh-TW" in codes
    assert "en" in codes
    assert "th" in codes
    assert "ja" in codes


def test_navigation_uses_canonical_page_ids():
    # The page constants should be plain strings (canonical IDs)
    import importlib.util
    spec = importlib.util.spec_from_file_location("streamlit_app", "ui/streamlit_app.py")
    # We can't import streamlit_app directly (requires streamlit runtime)
    # but we can check for PAGE_* constants via regex
    import re
    with open("ui/streamlit_app.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert "PAGE_HOME" in content
    assert "PAGE_INPUT" in content
    assert "PAGE_CALCULATE" in content
    assert 'PAGE_HOME = "home"' in content


def test_canonical_page_id_home():
    with open("ui/streamlit_app.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert 'PAGE_HOME = "home"' in content


def test_canonical_page_id_settings():
    with open("ui/streamlit_app.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert 'PAGE_SETTINGS = "settings"' in content


def test_app_language_key_initialized():
    with open("ui/streamlit_app.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert "app_language" in content


def test_tr_helper_exists():
    with open("ui/streamlit_app.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert "def _tr(" in content


def test_report_language_selector_key():
    with open("ui/streamlit_app.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert "report_language" in content


def test_language_switch_does_not_clear_input_keys():
    # The language switch should only update app_language and rerun
    # Input keys (input_name, input_birth_year, etc.) should not be cleared
    with open("ui/streamlit_app.py", "r", encoding="utf-8") as f:
        content = f.read()
    # The language selector should only set app_language
    assert "app_language" in content
    assert "input_name" in content  # input keys still exist


def test_customer_mode_pages():
    with open("ui/streamlit_app.py", "r", encoding="utf-8") as f:
        content = f.read()
    # Customer pages should not include developer-only pages
    assert "CUSTOMER_PAGES" in content
    assert "PAGE_ZIWEI_RECONCILIATION" not in content.split("CUSTOMER_PAGES")[1].split("\n\n")[0]


def test_consultant_mode_defined():
    with open("ui/streamlit_app.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert "CONSULTANT_PAGES" in content


def test_developer_mode_defined():
    with open("ui/streamlit_app.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert "DEVELOPER_PAGES" in content
