# -*- coding: utf-8 -*-
"""Full UI coverage tests for V2.0.5."""
from pathlib import Path
import pytest


def _read_app():
    return Path("ui/streamlit_app.py").read_text(encoding="utf-8")


# ── Required key sets per page ────────────────────────────────────────────────
HOME_REQUIRED = [
    "app.title", "app.subtitle",
    "home.metric_systems", "home.metric_sections", "home.metric_formats",
    "home.btn_start_chart", "home.btn_compatibility", "home.btn_history",
    "home.btn_input", "home.btn_compat", "home.btn_content", "home.btn_free",
    "home.quick_start.title",
    "home.quick_start.step1.title", "home.quick_start.step2.title", "home.quick_start.step3.title",
]

INPUT_REQUIRED = [
    "input.title", "input.basic_info", "input.name", "input.gender",
    "input.birth_date", "input.birth_time_section", "input.birth_time_known",
    "input.birth_place", "input.country", "input.submit", "input.clear",
    "input.error_country_required", "input.saved",
]

CALCULATE_REQUIRED = [
    "calculate.title", "calculate.no_profile", "calculate.btn_go_input",
    "calculate.btn_edit", "calculate.btn_clear", "calculate.done",
    "calculate.btn_recalc", "calculate.btn_preview", "calculate.btn_start",
    "calculate.spinner", "calculate.overview",
    "calculate.tab_western", "calculate.tab_bazi", "calculate.tab_ziwei",
    "calculate.tab_numerology", "calculate.tab_hd",
    "calculate.western_sun", "calculate.western_moon", "calculate.western_asc", "calculate.western_mc",
    "calculate.bazi_day_master", "calculate.bazi_favorable",
    "calculate.hd_type", "calculate.hd_strategy", "calculate.hd_authority", "calculate.hd_profile",
]

FREE_CONTENT_REQUIRED = [
    "free_content.title", "free_content.subtitle",
    "free_content.no_content",
]

REPORT_REQUIRED = [
    "report.not_ready", "report.export",
    "report.language_selector", "report.language_auto",
    "report.partial_translation_notice",
]

HISTORY_REQUIRED = [
    "history.title", "history.no_reports",
]

EXPORT_REQUIRED = [
    "export.title", "export.no_report",
]

COMPATIBILITY_REQUIRED = [
    "compatibility.title", "compatibility.person_a", "compatibility.person_b",
    "compatibility.generate", "compatibility.not_ready",
]

SETTINGS_REQUIRED = [
    "settings.title", "settings.mode_status",
    "settings.system_info", "settings.version",
]

FREE_REPORT_REQUIRED = [
    "free_report.title", "free_report.subtitle",
]

ALL_LOCALES = ["zh-TW", "en", "th", "ja", "es", "ar"]


def _get_translation_for(language: str, key: str) -> str:
    from i18n.translator import get_translation
    return get_translation(language, key)


def _all_locales_have_key(key: str) -> bool:
    for lang in ALL_LOCALES:
        val = _get_translation_for(lang, key)
        if val == key:  # fallback to key means missing
            return False
    return True


@pytest.mark.parametrize("key", HOME_REQUIRED)
def test_home_required_keys_all_locales(key):
    for lang in ALL_LOCALES:
        val = _get_translation_for(lang, key)
        assert val != key, f"Missing key {key!r} for language {lang!r}"


@pytest.mark.parametrize("key", INPUT_REQUIRED)
def test_input_required_keys_all_locales(key):
    for lang in ALL_LOCALES:
        val = _get_translation_for(lang, key)
        assert val != key, f"Missing key {key!r} for language {lang!r}"


@pytest.mark.parametrize("key", CALCULATE_REQUIRED)
def test_calculate_required_keys_all_locales(key):
    for lang in ALL_LOCALES:
        val = _get_translation_for(lang, key)
        assert val != key, f"Missing key {key!r} for language {lang!r}"


@pytest.mark.parametrize("key", FREE_CONTENT_REQUIRED)
def test_free_content_required_keys_all_locales(key):
    for lang in ALL_LOCALES:
        val = _get_translation_for(lang, key)
        assert val != key, f"Missing key {key!r} for language {lang!r}"


@pytest.mark.parametrize("key", REPORT_REQUIRED)
def test_report_required_keys_all_locales(key):
    for lang in ALL_LOCALES:
        val = _get_translation_for(lang, key)
        assert val != key, f"Missing key {key!r} for language {lang!r}"


@pytest.mark.parametrize("key", HISTORY_REQUIRED)
def test_history_required_keys_all_locales(key):
    for lang in ALL_LOCALES:
        val = _get_translation_for(lang, key)
        assert val != key, f"Missing key {key!r} for language {lang!r}"


@pytest.mark.parametrize("key", EXPORT_REQUIRED)
def test_export_required_keys_all_locales(key):
    for lang in ALL_LOCALES:
        val = _get_translation_for(lang, key)
        assert val != key, f"Missing key {key!r} for language {lang!r}"


@pytest.mark.parametrize("key", COMPATIBILITY_REQUIRED)
def test_compatibility_required_keys_all_locales(key):
    for lang in ALL_LOCALES:
        val = _get_translation_for(lang, key)
        assert val != key, f"Missing key {key!r} for language {lang!r}"


@pytest.mark.parametrize("key", SETTINGS_REQUIRED)
def test_settings_required_keys_all_locales(key):
    for lang in ALL_LOCALES:
        val = _get_translation_for(lang, key)
        assert val != key, f"Missing key {key!r} for language {lang!r}"


@pytest.mark.parametrize("key", FREE_REPORT_REQUIRED)
def test_free_report_required_keys_all_locales(key):
    for lang in ALL_LOCALES:
        val = _get_translation_for(lang, key)
        assert val != key, f"Missing key {key!r} for language {lang!r}"


def test_tr_helper_usage_significantly_increased():
    content = _read_app()
    tr_count = content.count("_tr(")
    assert tr_count >= 50, f"Expected >= 50 _tr() calls, got {tr_count}"


def test_home_metric_labels_use_tr():
    content = _read_app()
    assert '"支援命理系統"' not in content

def test_input_page_subheader_uses_tr():
    content = _read_app()
    assert 'st.subheader("基本資料")' not in content

def test_calculate_page_title_uses_tr():
    content = _read_app()
    assert 'st.title("🔮 計算命盤")' not in content

def test_input_title_uses_tr():
    content = _read_app()
    assert 'st.title("📝 輸入出生資料")' not in content

def test_free_content_title_uses_tr():
    content = _read_app()
    assert 'st.title("🌐 免費內容入口")' not in content

def test_home_page_title_not_hardcoded():
    content = _read_app()
    assert 'st.subheader(APP_SUBTITLE)' not in content

def test_rtl_apply_called():
    content = _read_app()
    assert "apply_streamlit_direction" in content

def test_canonical_page_ids_still_intact():
    content = _read_app()
    assert 'PAGE_HOME = "home"' in content
    assert 'PAGE_INPUT = "input"' in content

def test_six_languages_supported():
    from i18n.translator import SUPPORTED_LANGUAGES
    assert len(SUPPORTED_LANGUAGES) >= 6
    assert "es" in SUPPORTED_LANGUAGES
    assert "ar" in SUPPORTED_LANGUAGES

def test_rtl_module_importable():
    from i18n.rtl import is_rtl, apply_streamlit_direction
    assert callable(is_rtl)
    assert callable(apply_streamlit_direction)

def test_arabic_display_name_correct():
    from i18n.translator import SUPPORTED_LANGUAGES
    assert SUPPORTED_LANGUAGES.get("ar") == "العربية"

def test_arabic_display_name_not_reversed():
    from i18n.translator import SUPPORTED_LANGUAGES
    assert SUPPORTED_LANGUAGES.get("ar") != "ةيبرعلا"
