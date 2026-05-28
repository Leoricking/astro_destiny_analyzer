"""
Tests for V1.9.3 Human Design Gate Wheel Offset functionality.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


# ── A. calibration module ────────────────────────────────────────────────────

class TestSimulateGateOffsetForActivations:
    def test_returns_list(self):
        from human_design.calibration import simulate_gate_offset_for_activations
        results = simulate_gate_offset_for_activations({"Sun": 100.0}, [0.0])
        assert isinstance(results, list)

    def test_result_count_matches_planets_times_offsets(self):
        from human_design.calibration import simulate_gate_offset_for_activations
        lons = {"Sun": 100.0, "Moon": 200.0}
        offsets = [-1.0, 0.0, 1.0]
        results = simulate_gate_offset_for_activations(lons, offsets)
        assert len(results) == len(lons) * len(offsets)

    def test_result_has_required_keys(self):
        from human_design.calibration import simulate_gate_offset_for_activations
        results = simulate_gate_offset_for_activations({"Earth": 50.0}, [0.0])
        assert len(results) == 1
        r = results[0]
        assert "planet" in r
        assert "longitude" in r
        assert "offset" in r
        assert "gate" in r
        assert "line" in r

    def test_zero_offset_produces_valid_gate(self):
        from human_design.calibration import simulate_gate_offset_for_activations
        results = simulate_gate_offset_for_activations({"Sun": 150.0}, [0.0])
        assert 1 <= results[0]["gate"] <= 64
        assert 1 <= results[0]["line"] <= 6

    def test_empty_offsets_returns_empty(self):
        from human_design.calibration import simulate_gate_offset_for_activations
        results = simulate_gate_offset_for_activations({"Sun": 100.0}, [])
        assert results == []

    def test_empty_longitudes_returns_empty(self):
        from human_design.calibration import simulate_gate_offset_for_activations
        results = simulate_gate_offset_for_activations({}, [0.0, 1.0])
        assert results == []

    def test_planet_name_preserved(self):
        from human_design.calibration import simulate_gate_offset_for_activations
        results = simulate_gate_offset_for_activations({"Design Sun": 100.0}, [0.0])
        assert results[0]["planet"] == "Design Sun"

    def test_longitude_rounded_to_4dp(self):
        from human_design.calibration import simulate_gate_offset_for_activations
        results = simulate_gate_offset_for_activations({"Sun": 100.123456789}, [0.0])
        # Longitude should be rounded
        assert abs(results[0]["longitude"] - 100.1235) < 0.0001

    def test_different_offsets_may_produce_different_gates(self):
        from human_design.calibration import simulate_gate_offset_for_activations
        # Test a longitude near a gate boundary
        # Offset of 0 and 5.625 (one full gate) should both be valid
        results_0 = simulate_gate_offset_for_activations({"Sun": 1.0}, [0.0])
        results_shifted = simulate_gate_offset_for_activations({"Sun": 1.0}, [5.625])
        assert 1 <= results_0[0]["gate"] <= 64
        assert 1 <= results_shifted[0]["gate"] <= 64

    def test_full_range_of_offsets(self):
        from human_design.calibration import simulate_gate_offset_for_activations
        offsets = [-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0]
        results = simulate_gate_offset_for_activations({"Sun": 100.0}, offsets)
        assert len(results) == len(offsets)
        for r in results:
            assert 1 <= r["gate"] <= 64
            assert 1 <= r["line"] <= 6


# ── B. config settings ────────────────────────────────────────────────────────

class TestConfigCalibrationSettings:
    def test_design_date_method_setting_exists(self, monkeypatch):
        monkeypatch.delenv("HUMAN_DESIGN_DESIGN_DATE_METHOD", raising=False)
        import importlib, config
        importlib.reload(config)
        assert hasattr(config, "HUMAN_DESIGN_DESIGN_DATE_METHOD")
        assert config.HUMAN_DESIGN_DESIGN_DATE_METHOD == "solar_arc_88"

    def test_design_date_method_env_override(self, monkeypatch):
        monkeypatch.setenv("HUMAN_DESIGN_DESIGN_DATE_METHOD", "minus_88_days")
        import importlib, config
        importlib.reload(config)
        assert config.HUMAN_DESIGN_DESIGN_DATE_METHOD == "minus_88_days"

    def test_gate_wheel_offset_default_zero(self, monkeypatch):
        monkeypatch.delenv("HUMAN_DESIGN_GATE_WHEEL_OFFSET_DEGREES", raising=False)
        import importlib, config
        importlib.reload(config)
        assert config.HUMAN_DESIGN_GATE_WHEEL_OFFSET_DEGREES == 0.0

    def test_gate_wheel_offset_env_override(self, monkeypatch):
        monkeypatch.setenv("HUMAN_DESIGN_GATE_WHEEL_OFFSET_DEGREES", "1.5")
        import importlib, config
        importlib.reload(config)
        assert config.HUMAN_DESIGN_GATE_WHEEL_OFFSET_DEGREES == pytest.approx(1.5)

    def test_offset_debug_default_false(self, monkeypatch):
        monkeypatch.delenv("HUMAN_DESIGN_ENABLE_OFFSET_DEBUG", raising=False)
        monkeypatch.delenv("ASTRO_DEVELOPER_MODE", raising=False)
        import importlib, config
        importlib.reload(config)
        assert config.HUMAN_DESIGN_ENABLE_OFFSET_DEBUG is False

    def test_offset_debug_true_when_developer_mode(self, monkeypatch):
        monkeypatch.setenv("ASTRO_DEVELOPER_MODE", "1")
        monkeypatch.delenv("HUMAN_DESIGN_ENABLE_OFFSET_DEBUG", raising=False)
        import importlib, config
        importlib.reload(config)
        assert config.HUMAN_DESIGN_ENABLE_OFFSET_DEBUG is True


# ── C. HumanDesignChart model fields ─────────────────────────────────────────

class TestHumanDesignChartCalibrationFields:
    def _make_minimal_chart(self, **kwargs):
        from human_design.models import HumanDesignChart
        defaults = {
            "calculation_mode": "mock_fallback",
            "type_name": "Generator",
            "type_name_zh": "生產者",
            "strategy": "等待回應",
            "authority": "薦骨權威",
            "profile": "1/3",
            "incarnation_cross": "─",
        }
        defaults.update(kwargs)
        return HumanDesignChart(**defaults)

    def test_default_design_date_method(self):
        chart = self._make_minimal_chart()
        assert chart.design_date_method == "solar_arc_88"

    def test_default_design_date_fallback_used(self):
        chart = self._make_minimal_chart()
        assert chart.design_date_fallback_used is False

    def test_default_solar_arc_fields_none(self):
        chart = self._make_minimal_chart()
        assert chart.design_solar_arc_target_longitude is None
        assert chart.design_solar_arc_actual_longitude is None
        assert chart.design_solar_arc_error_degrees is None

    def test_default_gate_wheel_offset_zero(self):
        chart = self._make_minimal_chart()
        assert chart.gate_wheel_offset_degrees == 0.0

    def test_default_gate_wheel_version(self):
        chart = self._make_minimal_chart()
        assert chart.gate_wheel_version == "phase1_i_ching_order_offset_0"

    def test_default_calibration_notes_empty(self):
        chart = self._make_minimal_chart()
        assert chart.calibration_notes == []

    def test_set_solar_arc_error(self):
        chart = self._make_minimal_chart(design_solar_arc_error_degrees=0.0234)
        assert chart.design_solar_arc_error_degrees == pytest.approx(0.0234)

    def test_set_gate_wheel_offset(self):
        chart = self._make_minimal_chart(gate_wheel_offset_degrees=1.5)
        assert chart.gate_wheel_offset_degrees == pytest.approx(1.5)

    def test_calibration_notes_list(self):
        chart = self._make_minimal_chart(calibration_notes=["note1", "note2"])
        assert len(chart.calibration_notes) == 2
        assert "note1" in chart.calibration_notes


# ── D. validation.py new fields ───────────────────────────────────────────────

class TestHDValidationStatusCalibrationFields:
    def _make_chart(self, **kwargs):
        from human_design.models import HumanDesignChart
        defaults = {
            "calculation_mode": "mock_fallback",
            "type_name": "Generator",
            "type_name_zh": "生產者",
            "strategy": "等待回應",
            "authority": "薦骨",
            "profile": "1/3",
            "incarnation_cross": "─",
        }
        defaults.update(kwargs)
        return HumanDesignChart(**defaults)

    def test_validation_status_has_design_date_method(self):
        from human_design.validation import build_validation_status
        chart = self._make_chart()
        status = build_validation_status(chart)
        assert hasattr(status, "design_date_method")

    def test_validation_status_has_gate_wheel_offset(self):
        from human_design.validation import build_validation_status
        chart = self._make_chart()
        status = build_validation_status(chart)
        assert hasattr(status, "gate_wheel_offset_degrees")

    def test_validation_status_has_solar_arc_error(self):
        from human_design.validation import build_validation_status
        chart = self._make_chart()
        status = build_validation_status(chart)
        assert hasattr(status, "solar_arc_error_degrees")

    def test_offset_warning_when_nonzero(self):
        from human_design.validation import build_validation_status
        chart = self._make_chart(gate_wheel_offset_degrees=1.5)
        status = build_validation_status(chart)
        all_warnings = " ".join(status.warnings)
        assert "offset" in all_warnings.lower() or "1.5" in all_warnings

    def test_no_offset_warning_when_zero(self):
        from human_design.validation import build_validation_status
        chart = self._make_chart(gate_wheel_offset_degrees=0.0)
        status = build_validation_status(chart)
        all_warnings = " ".join(status.warnings)
        # Should not have offset-specific warning
        assert "+1.5" not in all_warnings

    def test_render_contains_method_info_section(self):
        from human_design.validation import build_validation_status, render_validation_markdown
        chart = self._make_chart()
        status = build_validation_status(chart)
        result = render_validation_markdown(status)
        assert "方法資訊" in result

    def test_render_contains_offset_value(self):
        from human_design.validation import build_validation_status, render_validation_markdown
        chart = self._make_chart()
        status = build_validation_status(chart)
        result = render_validation_markdown(status)
        assert "Gate Wheel Offset" in result


# ── E. reconciliation method info ─────────────────────────────────────────────

class TestReconciliationMethodInfo:
    def _make_local_chart(self):
        from human_design.models import HumanDesignChart
        return HumanDesignChart(
            calculation_mode="mock_fallback",
            type_name="Generator",
            type_name_zh="生產者",
            strategy="等待回應",
            authority="薦骨",
            profile="1/3",
            incarnation_cross="─",
            design_date_method="solar_arc_88",
            gate_wheel_offset_degrees=0.0,
        )

    def test_report_has_method_info_note(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        from human_design_reconciliation.models import ExternalHumanDesignChart
        local = self._make_local_chart()
        ext = ExternalHumanDesignChart(type_name="Generator", authority="Sacral", profile="1/3")
        report = HumanDesignReconciliationEngine().reconcile(local, ext)
        assert hasattr(report, "method_info_note")
        assert "solar_arc_88" in report.method_info_note

    def test_method_info_note_shows_offset(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        from human_design_reconciliation.models import ExternalHumanDesignChart
        from human_design.models import HumanDesignChart
        local = HumanDesignChart(
            calculation_mode="mock_fallback",
            type_name="Generator", type_name_zh="生產者",
            strategy="等待回應", authority="薦骨", profile="1/3",
            incarnation_cross="─",
            design_date_method="solar_arc_88",
            gate_wheel_offset_degrees=1.5,
        )
        ext = ExternalHumanDesignChart(type_name="Generator")
        report = HumanDesignReconciliationEngine().reconcile(local, ext)
        assert "1.5" in report.method_info_note or "+1.500" in report.method_info_note

    def test_render_contains_method_info(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        from human_design_reconciliation.models import ExternalHumanDesignChart
        from human_design_reconciliation.templates import render_reconciliation_markdown
        local = self._make_local_chart()
        ext = ExternalHumanDesignChart(type_name="Generator", authority="Sacral")
        report = HumanDesignReconciliationEngine().reconcile(local, ext)
        md = render_reconciliation_markdown(report)
        assert "方法資訊" in md or "solar_arc_88" in md
