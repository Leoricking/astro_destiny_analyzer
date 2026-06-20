from pathlib import Path


def test_bazi_components_accept_language_keyword():
    source = Path("ui/components.py").read_text(encoding="utf-8")
    assert 'def render_bazi_pillars(bazi_chart, language="zh-TW")' in source
    assert 'def render_five_element_chart(bazi_chart, language="zh-TW")' in source


def test_edit_navigation_uses_pending_profile_hydration():
    source = Path("ui/streamlit_app.py").read_text(encoding="utf-8")
    assert 'st.session_state["_pending_profile_edit"] = True' in source
    assert 'st.session_state.pop("_pending_profile_edit", False)' in source
    assert '_sync_input_state_from_profile(_edit_profile)' in source


def test_profile_restore_populates_smart_location_state():
    source = Path("ui/streamlit_app.py").read_text(encoding="utf-8")
    for token in (
        'st.session_state["input_country_code"]',
        'st.session_state["input_city_query"]',
        'st.session_state["input_city_candidates"]',
        'st.session_state["input_location_confirmed"]',
    ):
        assert token in source
