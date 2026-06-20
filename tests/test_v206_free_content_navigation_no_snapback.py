from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "ui" / "streamlit_app.py"


def _source() -> str:
    return SOURCE.read_text(encoding="utf-8")


def test_programmatic_navigation_rotates_radio_generation():
    src = _source()
    assert 'st.session_state["_pending_nav_page"] = page_id' in src
    assert 'st.session_state["_nav_radio_generation"]' in src
    assert '+ 1' in src


def test_sidebar_radio_uses_canonical_ids_and_generation_key():
    src = _source()
    assert '_nav_widget_key = f"_nav_radio_{_nav_generation}"' in src
    assert 'options=_cur_pages' not in src  # positional canonical options are used
    assert '        _cur_pages,\n' in src
    assert 'format_func=page_label' in src
    assert 'key=_nav_widget_key' in src
    assert 'key="_nav_radio"' not in src


def test_input_page_restores_partial_snapshot_on_direct_or_cta_navigation():
    src = _source()
    assert 'if page == PAGE_INPUT and _previous_page not in (None, PAGE_INPUT):' in src
    assert '_saved_snapshot = st.session_state.get("_last_input_snapshot")' in src
    assert '_restore_input_snapshot(_saved_snapshot)' in src
    assert 'st.session_state["_last_rendered_page"] = page' in src


def test_free_content_cta_uses_safe_navigation_helper():
    src = _source()
    assert '_go_to_page(_fp.cta_target)' in src
    assert '_go_to_page(_sel_page.cta_target)' in src
