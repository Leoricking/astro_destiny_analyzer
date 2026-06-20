from pathlib import Path

APP = Path("ui/streamlit_app.py").read_text(encoding="utf-8")


def test_programmatic_navigation_rotates_sidebar_widget_generation():
    assert 'st.session_state["_nav_radio_generation"] = (' in APP
    assert '_nav_widget_key = f"_nav_radio_{_nav_generation}"' in APP


def test_sidebar_navigation_stores_canonical_page_ids():
    assert 'page = st.radio(' in APP
    assert 'format_func=page_label' in APP
    assert '"nav",\n        _cur_pages,' in APP


def test_free_content_cta_uses_safe_navigation():
    assert '_go_to_page(_fp.cta_target)' in APP
    assert '_go_to_page(_sel_page.cta_target)' in APP


def test_free_report_upgrade_cta_uses_safe_navigation():
    assert '_go_to_page(_ucta["target"])' in APP


def test_legacy_fixed_nav_key_is_not_used_by_sidebar_radio():
    sidebar_fragment = APP[APP.index("# Navigation — store canonical page IDs"):APP.index("_previous_page =", APP.index("# Navigation — store canonical page IDs"))]
    assert 'key="_nav_radio"' not in sidebar_fragment
