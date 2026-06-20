from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "ui" / "streamlit_app.py").read_text(encoding="utf-8")
COMP = (ROOT / "ui" / "components.py").read_text(encoding="utf-8")
DISPLAY = (ROOT / "i18n" / "display_names.py").read_text(encoding="utf-8")


def test_city_search_uses_bottom_alignment_and_full_width_button():
    assert 'vertical_alignment="bottom"' in APP
    assert 'key="loc_search_btn"' in APP
    assert 'use_container_width=True' in APP


def test_analysis_themes_are_canonical_and_translated():
    assert '"overall_personality"' in APP
    assert 'format_func=lambda value: translate_analysis_theme' in APP
    assert 'normalize_analysis_theme' in APP


def test_report_language_has_six_supported_languages_plus_auto():
    assert '["auto", "zh-TW", "en", "th", "ja", "es", "ar"]' in APP
    block = APP[APP.find('st.subheader(_tr("input.report_settings"))'):APP.find('submitted = st.button', APP.find('st.subheader(_tr("input.report_settings"))'))]
    assert 'options=_report_language_codes' in block
    assert '"zh-CN"' not in block


def test_report_length_is_canonical_and_translated():
    assert '["short", "standard", "full", "complete_10k"]' in APP
    assert 'format_func=lambda value: translate_report_length' in APP
    assert 'normalize_report_length' in DISPLAY


def test_render_planet_table_accepts_language():
    assert 'def render_planet_table(planet_positions, language="zh-TW")' in COMP
    assert 'translate_zodiac(canonical_sign, language)' in COMP


def test_report_preview_uses_selected_report_language_and_keeps_fallback_body():
    assert '_resolved_report_language' in APP
    assert 'render_synthesis_section(report.synthesis, language=_resolved_report_language)' in APP
    assert 'st.markdown(body)' in COMP
    assert 'report_preview.original_language' in COMP
