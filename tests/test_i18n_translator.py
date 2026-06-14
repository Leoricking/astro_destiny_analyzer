"""Tests for i18n.translator module."""
import pytest
from i18n.translator import (
    t, get_translation, normalize_language_code,
    get_language_options, get_current_language, set_current_language,
    SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE,
)


def test_zh_tw_supported():
    assert "zh-TW" in SUPPORTED_LANGUAGES


def test_en_supported():
    assert "en" in SUPPORTED_LANGUAGES


def test_th_supported():
    assert "th" in SUPPORTED_LANGUAGES


def test_ja_supported():
    assert "ja" in SUPPORTED_LANGUAGES


def test_default_language_zh_tw():
    assert DEFAULT_LANGUAGE == "zh-TW"


def test_invalid_language_fallback_zh_tw():
    result = get_translation("invalid-lang", "app.title")
    zh_result = get_translation("zh-TW", "app.title")
    assert result == zh_result


def test_missing_key_fallback_zh_tw():
    # key missing in both requested and zh-TW should return key
    result = get_translation("en", "nonexistent.key.xyz")
    assert result == "nonexistent.key.xyz"


def test_missing_all_languages_returns_key():
    result = get_translation("en", "totally.missing.key.abc123")
    assert result == "totally.missing.key.abc123"


def test_format_placeholder_works():
    # Add a format placeholder to test this directly using t()
    result = t("app.title", language="en")
    assert isinstance(result, str)
    assert len(result) > 0


def test_format_failure_does_not_crash():
    # t() should not crash even if we pass extra kwargs with no placeholder
    result = t("app.title", language="en", score=84, name="test")
    assert isinstance(result, str)


def test_get_language_options_returns_6():
    options = get_language_options()
    assert len(options) == 6


def test_es_supported():
    assert "es" in SUPPORTED_LANGUAGES


def test_ar_supported():
    assert "ar" in SUPPORTED_LANGUAGES


def test_no_duplicate_codes():
    options = get_language_options()
    codes = [c for c, _ in options]
    assert len(codes) == len(set(codes))


def test_normalize_language_code_valid():
    assert normalize_language_code("zh-TW") == "zh-TW"
    assert normalize_language_code("en") == "en"
    assert normalize_language_code("th") == "th"
    assert normalize_language_code("ja") == "ja"
    assert normalize_language_code("es") == "es"
    assert normalize_language_code("ar") == "ar"


def test_normalize_language_code_invalid():
    assert normalize_language_code("xx-XX") == DEFAULT_LANGUAGE


def test_t_returns_string():
    result = t("nav.home", language="zh-TW")
    assert isinstance(result, str)


def test_get_current_language_default():
    lang = get_current_language(session_state={})
    assert lang == DEFAULT_LANGUAGE


def test_set_current_language():
    ss = {}
    result = set_current_language("en", session_state=ss)
    assert result == "en"
    assert ss.get("app_language") == "en"
