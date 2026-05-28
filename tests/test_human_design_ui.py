"""
Tests for V1.9.0 Human Design UI integration.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(rel: str) -> str:
    with open(os.path.join(PROJECT_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def _app_src() -> str:
    return _read("ui/streamlit_app.py")


# ── A. UI page / tab label ────────────────────────────────────────────────────

class TestUILabels:
    def test_app_has_human_design_tab(self):
        src = _app_src()
        assert "人類圖" in src

    def test_tab_label_contains_hd(self):
        src = _app_src()
        assert "🔷 人類圖" in src or "人類圖" in src

    def test_hd_tab_variable_present(self):
        src = _app_src()
        assert "tab_hd" in src


# ── B. Customer mode can see HD ───────────────────────────────────────────────

class TestCustomerModeHD:
    def test_hd_tab_not_gated_by_developer_mode(self):
        """Human Design should be accessible in customer mode."""
        src = _app_src()
        # Find tab_hd block — it should NOT be inside a DEVELOPER_MODE if-guard
        hd_start = src.find("with tab_hd:")
        assert hd_start != -1
        # The HD tab should be present regardless of DEVELOPER_MODE
        # (it's a customer feature, not a dev-only feature)
        snippet = src[hd_start: hd_start + 200]
        # The tab block itself should not start with a DEVELOPER_MODE check
        assert "if DEVELOPER_MODE" not in snippet[:100]

    def test_hd_metric_cards_present(self):
        src = _app_src()
        assert "類型 Type" in src
        assert "已定義中心" in src


# ── C. Developer mode shows debug ────────────────────────────────────────────

class TestDeveloperModeHD:
    def test_developer_debug_block_present(self):
        src = _app_src()
        hd_section_start = src.find("with tab_hd:")
        hd_section_end = src.find("# PAGE:", hd_section_start)
        hd_section = src[hd_section_start:hd_section_end]
        assert "DEVELOPER_MODE" in hd_section

    def test_developer_debug_mentions_raw_data(self):
        src = _app_src()
        hd_idx = src.find("with tab_hd:")
        end_idx = src.find("# PAGE:", hd_idx)
        hd_block = src[hd_idx:end_idx]
        assert "HD Debug" in hd_block or "debug" in hd_block.lower()


# ── D. Client mode does not see raw gate order debug ─────────────────────────

class TestClientModeNoDebug:
    def test_raw_gate_debug_inside_developer_check(self):
        src = _app_src()
        hd_idx = src.find("with tab_hd:")
        end_idx = src.find("# PAGE:", hd_idx)
        hd_block = src[hd_idx:end_idx]
        # The raw debug expander must be inside a DEVELOPER_MODE guard
        debug_idx = hd_block.find("HD Debug")
        if debug_idx == -1:
            return  # no debug block → ok
        # Find the if DEVELOPER_MODE check before the debug
        before_debug = hd_block[:debug_idx]
        assert "DEVELOPER_MODE" in before_debug


# ── E. HD helper table functions ─────────────────────────────────────────────

class TestHDHelperFunctions:
    def test_longitude_to_gate_line_does_not_crash(self):
        from human_design.engine import longitude_to_gate_line
        for lon in [0.0, 90.0, 180.0, 270.0, 359.9]:
            gate, line = longitude_to_gate_line(lon)
            assert 1 <= gate <= 64
            assert 1 <= line <= 6

    def test_center_info_accessible(self):
        from human_design.constants import CENTER_INFO
        assert len(CENTER_INFO) == 9

    def test_type_info_accessible(self):
        from human_design.constants import TYPE_INFO
        assert "Generator" in TYPE_INFO
        assert "Projector" in TYPE_INFO
        assert "Reflector" in TYPE_INFO

    def test_gate_info_accessible(self):
        from human_design.constants import GATE_INFO
        assert len(GATE_INFO) == 64

    def test_channel_info_accessible(self):
        from human_design.constants import CHANNEL_INFO
        assert len(CHANNEL_INFO) > 0
