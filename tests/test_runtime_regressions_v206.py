from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "ui" / "streamlit_app.py").read_text(encoding="utf-8")

def test_current_language_alias_defined():
    assert '_tr_lang = st.session_state.get("app_language", DEFAULT_LANGUAGE)' in SRC

def test_zodiac_metrics_are_localized():
    assert 'translate_zodiac(normalize_zodiac_value(sun_pos.sign.value), _tr_lang)' in SRC
    assert 'translate_zodiac(normalize_zodiac_value(moon_pos.sign.value), _tr_lang)' in SRC

def test_report_length_helper_exists():
    assert 'def _report_length_label' in SRC

def test_edit_button_uses_pending_navigation():
    assert 'st.session_state["_pending_nav_page"] = PAGE_INPUT' in SRC
