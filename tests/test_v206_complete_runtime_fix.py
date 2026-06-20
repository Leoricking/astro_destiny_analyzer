from pathlib import Path

APP = Path('ui/streamlit_app.py').read_text(encoding='utf-8')
COMP = Path('ui/components.py').read_text(encoding='utf-8')
LEAD = Path('lead_magnet/templates.py').read_text(encoding='utf-8')
DISPLAY = Path('i18n/display_names.py').read_text(encoding='utf-8')


def test_programmatic_navigation_clears_sidebar_widget_state():
    assert 'st.session_state.pop("_nav_radio", None)' in APP
    assert '_go_to_page(_fp.cta_target)' in APP
    assert '_go_to_page(_sel_page.cta_target)' in APP


def test_input_snapshot_is_continuously_preserved_and_restored():
    assert 'st.session_state["_last_input_snapshot"] = _capture_input_snapshot()' in APP
    assert '_edit_state = st.session_state.get("_last_input_snapshot") or _capture_input_snapshot()' in APP
    assert '_pending_profile_edit' in APP


def test_free_report_copy_is_language_aware():
    assert 'def render_lead_capture_copy(report_type: str, language: str = "zh-TW")' in LEAD
    assert '_CAPTURE_COPY_I18N' in LEAD
    for lang in ('"en"', '"ja"', '"th"', '"es"', '"ar"'):
        assert lang in LEAD


def test_non_chinese_calculation_summaries_do_not_only_show_placeholder_notices():
    assert '_localized_synthesis_bodies' in COMP
    assert 'render_numerology_card(num_chart, language="zh-TW")' in COMP
    assert 'translate_hd_strategy' in APP
    assert 'translate_hd_authority' in APP
    assert 'Detailed center, gate, and channel interpretations are not yet translated.' not in APP
    assert 'Detailed Zi Wei narrative is not yet translated.' not in APP


def test_hd_and_bazi_legacy_values_have_display_aliases():
    assert '"反映者": "Reflector"' in DISPLAY
    assert 'translate_bazi_stem' in DISPLAY
    assert 'translate_element' in DISPLAY
