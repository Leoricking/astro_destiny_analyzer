from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "ui" / "streamlit_app.py"


def test_input_clear_button_is_excluded_from_snapshot():
    source = APP.read_text(encoding="utf-8")
    assert '"input_clear_all"' in source
    assert "_INPUT_SNAPSHOT_EXCLUDED_KEYS" in source
    assert "if key in _INPUT_SNAPSHOT_EXCLUDED_KEYS" in source


def test_restore_skips_transient_widget_keys():
    source = APP.read_text(encoding="utf-8")
    restore_start = source.index("def _restore_input_snapshot")
    restore_end = source.index("def _sync_input_state_from_profile", restore_start)
    restore_source = source[restore_start:restore_end]
    assert "if key in _INPUT_SNAPSHOT_EXCLUDED_KEYS" in restore_source


def test_clear_button_remains_a_widget_action_only():
    source = APP.read_text(encoding="utf-8")
    assert 'st.button(_tr("calculate.btn_clear"), key="input_clear_all"' in source
    assert 'st.session_state["input_clear_all"]' not in source
