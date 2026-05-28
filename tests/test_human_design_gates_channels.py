"""
Tests for V1.9.0 Human Design gates, channels, and center constants.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


# ── A. I-Ching wheel ──────────────────────────────────────────────────────────

class TestIChingWheel:
    def test_wheel_has_64_entries(self):
        from human_design.constants import I_CHING_WHEEL_ORDER_PHASE1
        assert len(I_CHING_WHEEL_ORDER_PHASE1) == 64

    def test_wheel_gates_all_unique(self):
        from human_design.constants import I_CHING_WHEEL_ORDER_PHASE1
        assert len(set(I_CHING_WHEEL_ORDER_PHASE1)) == 64

    def test_wheel_all_values_1_to_64(self):
        from human_design.constants import I_CHING_WHEEL_ORDER_PHASE1
        assert set(I_CHING_WHEEL_ORDER_PHASE1) == set(range(1, 65))


# ── B. longitude_to_gate_line ─────────────────────────────────────────────────

class TestLongitudeToGateLine:
    def test_zero_returns_valid(self):
        from human_design.engine import longitude_to_gate_line
        gate, line = longitude_to_gate_line(0.0)
        assert 1 <= gate <= 64
        assert 1 <= line <= 6

    def test_near_360_does_not_crash(self):
        from human_design.engine import longitude_to_gate_line
        gate, line = longitude_to_gate_line(359.999)
        assert 1 <= gate <= 64
        assert 1 <= line <= 6

    def test_line_always_1_to_6(self):
        from human_design.engine import longitude_to_gate_line
        for lon in range(0, 360, 5):
            _, line = longitude_to_gate_line(float(lon))
            assert 1 <= line <= 6, f"line={line} for lon={lon}"

    def test_gate_always_1_to_64(self):
        from human_design.engine import longitude_to_gate_line
        for lon in range(0, 360, 5):
            gate, _ = longitude_to_gate_line(float(lon))
            assert 1 <= gate <= 64, f"gate={gate} for lon={lon}"

    def test_wraps_correctly(self):
        from human_design.engine import longitude_to_gate_line
        g1, l1 = longitude_to_gate_line(10.0)
        g2, l2 = longitude_to_gate_line(370.0)
        assert g1 == g2
        assert l1 == l2


# ── C. GATE_INFO completeness ─────────────────────────────────────────────────

class TestGateInfo:
    def test_gate_info_has_all_64(self):
        from human_design.constants import GATE_INFO
        assert set(GATE_INFO.keys()) == set(range(1, 65))

    def test_all_gates_have_name(self):
        from human_design.constants import GATE_INFO
        for g, info in GATE_INFO.items():
            assert "name" in info and info["name"], f"Gate {g} missing name"

    def test_all_gates_have_center(self):
        from human_design.constants import GATE_INFO
        valid_centers = {"Head", "Ajna", "Throat", "G", "Heart", "Sacral", "Spleen", "Solar Plexus", "Root"}
        for g, info in GATE_INFO.items():
            assert info.get("center") in valid_centers, f"Gate {g} has invalid center: {info.get('center')}"

    def test_all_gates_have_interpretation(self):
        from human_design.constants import GATE_INFO
        for g, info in GATE_INFO.items():
            assert "interpretation" in info and info["interpretation"], f"Gate {g} missing interpretation"


# ── D. CHANNEL_INFO ───────────────────────────────────────────────────────────

class TestChannelInfo:
    def test_channel_info_not_empty(self):
        from human_design.constants import CHANNEL_INFO
        assert len(CHANNEL_INFO) > 0

    def test_channel_gates_in_valid_range(self):
        from human_design.constants import CHANNEL_INFO
        for key, info in CHANNEL_INFO.items():
            g1, g2 = info["gates"]
            assert 1 <= g1 <= 64, f"Channel {key}: gate {g1} out of range"
            assert 1 <= g2 <= 64, f"Channel {key}: gate {g2} out of range"

    def test_channel_centers_are_valid(self):
        from human_design.constants import CHANNEL_INFO
        valid = {"Head", "Ajna", "Throat", "G", "Heart", "Sacral", "Spleen", "Solar Plexus", "Root"}
        for key, info in CHANNEL_INFO.items():
            c1, c2 = info["centers"]
            assert c1 in valid, f"Channel {key}: center '{c1}' invalid"
            assert c2 in valid, f"Channel {key}: center '{c2}' invalid"

    def test_channel_has_name(self):
        from human_design.constants import CHANNEL_INFO
        for key, info in CHANNEL_INFO.items():
            assert info.get("name"), f"Channel {key} missing name"

    def test_36_channels(self):
        from human_design.constants import CHANNEL_INFO
        assert len(CHANNEL_INFO) == 36


# ── E. Channel logic ──────────────────────────────────────────────────────────

class TestChannelLogic:
    def test_defined_channel_needs_both_gates(self):
        from human_design.engine import _build_defined_channels
        # Channel 20-34 (Charisma) needs gates 20 and 34
        channels = _build_defined_channels({34, 20})
        channel_keys = [c.channel for c in channels]
        assert "20-34" in channel_keys

    def test_only_one_gate_not_enough(self):
        from human_design.engine import _build_defined_channels
        channels = _build_defined_channels({34})
        channel_keys = [c.channel for c in channels]
        assert "34-20" not in channel_keys

    def test_empty_gates_gives_no_channels(self):
        from human_design.engine import _build_defined_channels
        assert _build_defined_channels(set()) == []


# ── F. Center definition logic ────────────────────────────────────────────────

class TestCenterLogic:
    def test_center_defined_by_complete_channel(self):
        from human_design.engine import _build_activated_gates, _build_defined_channels, _build_centers
        # Gates 34 and 20 define channel 34-20 connecting Sacral and Throat
        gate_sources = {34: ["Conscious Sun"], 20: ["Design Moon"]}
        gate_set = set(gate_sources.keys())
        channels = _build_defined_channels(gate_set)
        centers = _build_centers(channels, gate_sources)
        defined_names = {c.name for c in centers if c.is_defined}
        assert "Sacral" in defined_names
        assert "Throat" in defined_names

    def test_incomplete_channel_does_not_define_center(self):
        from human_design.engine import _build_activated_gates, _build_defined_channels, _build_centers
        gate_sources = {34: ["Conscious Sun"]}  # only one gate of 34-20
        gate_set = set(gate_sources.keys())
        channels = _build_defined_channels(gate_set)
        centers = _build_centers(channels, gate_sources)
        # Sacral should NOT be defined (channel incomplete)
        sacral = next(c for c in centers if c.name == "Sacral")
        assert not sacral.is_defined


# ── G. Type determination ─────────────────────────────────────────────────────

class TestTypeDetermination:
    def test_all_open_is_reflector(self):
        from human_design.engine import _determine_type
        t, _ = _determine_type(set(), [])
        assert t == "Reflector"

    def test_sacral_defined_no_motor_throat_is_generator(self):
        from human_design.engine import _determine_type
        t, _ = _determine_type({"Sacral", "Ajna"}, [])
        assert t == "Generator"

    def test_sacral_with_motor_to_throat_is_mangen(self):
        from human_design.engine import _determine_type, _build_defined_channels
        # Channel 34-20 connects Sacral → Throat
        channels = _build_defined_channels({34, 20})
        t, _ = _determine_type({"Sacral", "Throat"}, channels)
        assert t == "Manifesting Generator"

    def test_no_sacral_no_motor_throat_projector(self):
        from human_design.engine import _determine_type
        t, _ = _determine_type({"Ajna", "G"}, [])
        assert t == "Projector"


# ── H. CENTER_INFO completeness (V1.9.1) ─────────────────────────────────────

class TestCenterInfo:
    def test_center_info_has_9_entries(self):
        from human_design.constants import CENTER_INFO
        assert len(CENTER_INFO) == 9

    def test_center_info_has_zh_names(self):
        from human_design.constants import CENTER_INFO
        for name, info in CENTER_INFO.items():
            assert "zh" in info and info["zh"], f"CENTER_INFO[{name}] missing 'zh'"

    def test_center_info_has_defined_interpretation(self):
        from human_design.constants import CENTER_INFO
        for name, info in CENTER_INFO.items():
            assert "defined_interpretation" in info and info["defined_interpretation"], \
                f"CENTER_INFO[{name}] missing 'defined_interpretation'"

    def test_center_info_has_open_interpretation(self):
        from human_design.constants import CENTER_INFO
        for name, info in CENTER_INFO.items():
            assert "open_interpretation" in info and info["open_interpretation"], \
                f"CENTER_INFO[{name}] missing 'open_interpretation'"
