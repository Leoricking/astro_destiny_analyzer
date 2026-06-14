# -*- coding: utf-8 -*-
"""Tests for Arabic (ar) locale and RTL support."""
import pytest
from i18n.locales.ar import TRANSLATIONS as AR
from i18n.translator import get_translation, SUPPORTED_LANGUAGES
from i18n.rtl import is_rtl, get_text_direction, render_direction_css


def test_ar_supported():
    assert "ar" in SUPPORTED_LANGUAGES


def test_arabic_unicode_exists():
    all_values = "".join(AR.values())
    assert any("\u0600" <= c <= "\u06ff" for c in all_values)


def test_nav_home_ar():
    result = get_translation("ar", "nav.home")
    assert result != "nav.home" and any("\u0600" <= c <= "\u06ff" for c in result)


def test_input_name_ar():
    assert get_translation("ar", "input.name") != "input.name"


def test_report_export_ar():
    assert get_translation("ar", "report.export") != "report.export"


def test_settings_title_ar():
    assert get_translation("ar", "settings.title") != "settings.title"


def test_is_rtl_ar_true():
    assert is_rtl("ar") is True


def test_is_rtl_en_false():
    assert is_rtl("en") is False


def test_is_rtl_zh_tw_false():
    assert is_rtl("zh-TW") is False


def test_is_rtl_es_false():
    assert is_rtl("es") is False


def test_get_text_direction_ar():
    assert get_text_direction("ar") == "rtl"


def test_get_text_direction_en():
    assert get_text_direction("en") == "ltr"


def test_rtl_css_contains_direction():
    css = render_direction_css("ar")
    assert "direction: rtl" in css


def test_ltr_css_empty():
    assert render_direction_css("en") == ""


def test_rtl_css_code_block_ltr():
    css = render_direction_css("ar")
    assert "direction: ltr" in css


def test_no_crash_on_arabic_formatting():
    result = get_translation("ar", "app.title")
    assert isinstance(result, str)


def test_ar_locale_non_empty():
    assert len(AR) > 50


def test_ar_home_btn_start_chart():
    result = get_translation("ar", "home.btn_start_chart")
    assert result != "home.btn_start_chart" and len(result) > 0


def test_ar_calculate_title():
    result = get_translation("ar", "calculate.title")
    assert result != "calculate.title" and len(result) > 0


def test_arabic_display_name_correct():
    """Arabic display name must be العربية (not reversed)."""
    from i18n.translator import SUPPORTED_LANGUAGES
    ar_name = SUPPORTED_LANGUAGES.get("ar", "")
    correct = "العربية"
    assert ar_name == correct, f"Arabic name should be {correct!r}, got {ar_name!r}"


def test_arabic_display_name_not_reversed():
    """Ensure the Arabic name is NOT the character-reversed version."""
    from i18n.translator import SUPPORTED_LANGUAGES
    ar_name = SUPPORTED_LANGUAGES.get("ar", "")
    reversed_wrong = "ةيبرعلا"
    assert ar_name != reversed_wrong, "Arabic name must not be manually reversed"


def test_arabic_locale_values_not_reversed():
    """No locale value should equal its own character-reversed version (for non-trivial strings)."""
    from i18n.locales.ar import TRANSLATIONS as AR
    for key, val in AR.items():
        if len(val) > 3 and any("\u0600" <= c <= "\u06ff" for c in val):
            assert val != val[::-1], f"Key {key!r} value appears to be reversed: {val!r}"


def test_no_manual_reverse_in_source():
    """Source files must not contain [::-1] applied to Arabic strings."""
    import re
    from pathlib import Path
    for f in ["i18n/locales/ar.py", "i18n/translator.py", "config.py", "i18n/rtl.py"]:
        content = Path(f).read_text(encoding="utf-8")
        assert "[::-1]" not in content, f"Found [::-1] in {f}"


def test_no_reversed_call_in_arabic_source():
    """Source files must not use reversed() on Arabic strings."""
    from pathlib import Path
    for f in ["i18n/locales/ar.py", "i18n/translator.py", "config.py", "i18n/rtl.py"]:
        content = Path(f).read_text(encoding="utf-8")
        assert "reversed(" not in content, f"Found reversed() in {f}"


def test_nav_home_arabic_correct():
    from i18n.translator import get_translation
    result = get_translation("ar", "nav.home")
    # Should contain الرئيسية
    assert "الرئيسية" in result


def test_settings_title_arabic_correct():
    from i18n.translator import get_translation
    result = get_translation("ar", "settings.title")
    assert any("\u0600" <= c <= "\u06ff" for c in result)


def test_rtl_css_exists_for_ar():
    from i18n.rtl import render_direction_css
    css = render_direction_css("ar")
    assert "direction: rtl" in css


def test_code_blocks_ltr_in_rtl_css():
    from i18n.rtl import render_direction_css
    css = render_direction_css("ar")
    assert "direction: ltr" in css


def test_ltr_restored_for_zh_tw():
    from i18n.rtl import get_text_direction
    assert get_text_direction("zh-TW") == "ltr"
