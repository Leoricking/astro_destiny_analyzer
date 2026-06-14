"""Tests for locale completeness across all supported languages."""
import pytest
from i18n.locales.zh_TW import TRANSLATIONS as ZH_TW
from i18n.locales.en import TRANSLATIONS as EN
from i18n.locales.th import TRANSLATIONS as TH
from i18n.locales.ja import TRANSLATIONS as JA
from i18n.locales.es import TRANSLATIONS as ES
from i18n.locales.ar import TRANSLATIONS as AR

REQUIRED_NAV_KEYS = [
    "nav.home", "nav.public_content", "nav.free_report", "nav.input",
    "nav.calculate", "nav.report_preview", "nav.history", "nav.export",
    "nav.compatibility", "nav.settings",
]
REQUIRED_COMMON_KEYS = [
    "common.yes", "common.no", "common.save", "common.cancel",
    "common.delete", "common.download", "common.loading",
    "common.success", "common.warning", "common.error", "common.no_data",
]
REQUIRED_REPORT_KEYS = [
    "report.preview", "report.not_ready", "report.export",
    "report.partial_translation_notice",
]


def test_zh_tw_locale_non_empty():
    assert len(ZH_TW) > 0


def test_en_locale_non_empty():
    assert len(EN) > 0


def test_th_locale_non_empty():
    assert len(TH) > 0


def test_ja_locale_non_empty():
    assert len(JA) > 0


def test_es_locale_non_empty():
    assert len(ES) > 0


def test_ar_locale_non_empty():
    assert len(AR) > 0


@pytest.mark.parametrize("key", REQUIRED_NAV_KEYS)
def test_all_required_navigation_keys_exist(key):
    for name, locale in [("zh-TW", ZH_TW), ("en", EN), ("th", TH), ("ja", JA), ("es", ES), ("ar", AR)]:
        assert key in locale, f"Missing nav key '{key}' in {name}"


@pytest.mark.parametrize("key", REQUIRED_COMMON_KEYS)
def test_all_required_common_keys_exist(key):
    for name, locale in [("zh-TW", ZH_TW), ("en", EN), ("th", TH), ("ja", JA), ("es", ES), ("ar", AR)]:
        assert key in locale, f"Missing common key '{key}' in {name}"


@pytest.mark.parametrize("key", REQUIRED_REPORT_KEYS)
def test_all_required_report_keys_exist(key):
    for name, locale in [("zh-TW", ZH_TW), ("en", EN), ("th", TH), ("ja", JA), ("es", ES), ("ar", AR)]:
        assert key in locale, f"Missing report key '{key}' in {name}"


def test_thai_strings_contain_thai_unicode():
    thai_nav = TH.get("nav.home", "")
    # Thai Unicode range U+0E00–U+0E7F
    assert any("\u0e00" <= c <= "\u0e7f" for c in "".join(TH.values())), \
        "Thai locale should contain Thai Unicode characters"


def test_japanese_strings_contain_japanese_unicode():
    ja_values = "".join(JA.values())
    # Hiragana U+3040–U+309F or Katakana U+30A0–U+30FF or CJK
    has_japanese = any(
        ("\u3040" <= c <= "\u309f") or ("\u30a0" <= c <= "\u30ff")
        for c in ja_values
    )
    assert has_japanese, "Japanese locale should contain Hiragana or Katakana"


def test_english_strings_no_accidental_chinese_for_core_keys():
    for key in ["nav.home", "nav.input", "nav.calculate", "nav.export"]:
        val = EN.get(key, "")
        assert not any("\u4e00" <= c <= "\u9fff" for c in val), \
            f"English key '{key}' should not contain CJK: {val!r}"


def test_zh_tw_uses_traditional_chinese():
    # 繁體 should appear in zh-TW subtitle/labels
    assert "命盤" in ZH_TW.get("app.subtitle", "") or "分析" in ZH_TW.get("app.subtitle", "")


def test_locale_values_are_strings():
    for name, locale in [("zh-TW", ZH_TW), ("en", EN), ("th", TH), ("ja", JA), ("es", ES), ("ar", AR)]:
        for k, v in locale.items():
            assert isinstance(v, str), f"{name}['{k}'] is not a string: {type(v)}"


def test_arabic_display_name_not_reversed():
    from i18n.translator import SUPPORTED_LANGUAGES
    ar = SUPPORTED_LANGUAGES.get("ar", "")
    assert ar == "العربية", f"Expected العربية, got {ar!r}"
