from .translator import (
    t, get_translation, normalize_language_code, get_language_options,
    get_current_language, set_current_language,
)

try:
    from i18n.rtl import is_rtl, get_text_direction, apply_streamlit_direction
except ModuleNotFoundError:
    def is_rtl(language: str) -> bool:
        return str(language).lower() == "ar"
    def get_text_direction(language: str) -> str:
        return "rtl" if is_rtl(language) else "ltr"
    def apply_streamlit_direction(language: str) -> None:
        return None
