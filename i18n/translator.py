"""
Astro Destiny Analyzer — i18n translator  (V2.0.5)
"""
import warnings

SUPPORTED_LANGUAGES: dict = {
    "zh-TW": "繁體中文",
    "en": "English",
    "th": "ไทย",
    "ja": "日本語",
    "es": "Español",
    "ar": "العربية",
}
DEFAULT_LANGUAGE: str = "zh-TW"

# Lazy-loaded locale cache
_LOCALE_CACHE: dict[str, dict] = {}


def _load_locale(language: str) -> dict:
    """Load and cache the translations dict for the given language code."""
    if language in _LOCALE_CACHE:
        return _LOCALE_CACHE[language]

    try:
        if language == "zh-TW":
            from i18n.locales.zh_TW import TRANSLATIONS
        elif language == "en":
            from i18n.locales.en import TRANSLATIONS
        elif language == "th":
            from i18n.locales.th import TRANSLATIONS
        elif language == "ja":
            from i18n.locales.ja import TRANSLATIONS
        elif language == "es":
            from i18n.locales.es import TRANSLATIONS
        elif language == "ar":
            from i18n.locales.ar import TRANSLATIONS
        else:
            TRANSLATIONS = {}
        _LOCALE_CACHE[language] = TRANSLATIONS
        return TRANSLATIONS
    except Exception:
        _LOCALE_CACHE[language] = {}
        return {}


def normalize_language_code(code: str) -> str:
    """Normalize to a supported language code, or return DEFAULT_LANGUAGE."""
    if code in SUPPORTED_LANGUAGES:
        return code
    return DEFAULT_LANGUAGE


def get_translation(language: str, key: str, default: str | None = None) -> str:
    """Look up a translation key with fallback chain:
    requested language → zh-TW → default argument → key itself.
    """
    lang = normalize_language_code(language)

    # Try requested language
    translations = _load_locale(lang)
    if key in translations:
        return translations[key]

    # Fallback to zh-TW
    if lang != DEFAULT_LANGUAGE:
        zh_translations = _load_locale(DEFAULT_LANGUAGE)
        if key in zh_translations:
            return zh_translations[key]

    # Fallback to default argument, then key itself
    if default is not None:
        return default
    return key


def t(key: str, language: str | None = None, **kwargs) -> str:
    """Translate a key, optionally formatting with kwargs.

    Supports format placeholders: t("greeting", name="World") with key "Hello, {name}!"
    Returns unformatted string + warns on missing placeholder — never crashes.
    """
    lang = language if language else DEFAULT_LANGUAGE
    text = get_translation(lang, key)

    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError) as exc:
            warnings.warn(
                f"i18n: format placeholder error for key={key!r} lang={lang!r}: {exc}",
                stacklevel=2,
            )
            return text

    return text


def get_language_options() -> list[tuple[str, str]]:
    """Return [(code, display_name), ...] for all supported languages."""
    return list(SUPPORTED_LANGUAGES.items())


def get_current_language(session_state=None) -> str:
    """Return the current language from session_state, or DEFAULT_LANGUAGE."""
    if session_state is None:
        try:
            import streamlit as st
            return st.session_state.get("app_language", DEFAULT_LANGUAGE)
        except Exception:
            return DEFAULT_LANGUAGE
    return session_state.get("app_language", DEFAULT_LANGUAGE)


def set_current_language(language: str, session_state=None) -> str:
    """Set the current language in session_state and return the normalized code."""
    lang = normalize_language_code(language)
    if session_state is not None:
        session_state["app_language"] = lang
    else:
        try:
            import streamlit as st
            st.session_state["app_language"] = lang
        except Exception:
            pass
    return lang
