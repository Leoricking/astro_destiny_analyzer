"""
Tests for V1.9.2 Human Design External Chart Reconciliation module.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import date, time


def _make_local_chart():
    from human_design.engine import HumanDesignEngine
    from core.models import BirthProfile, AnalysisTheme, ReportLanguage, ReportLength
    profile = BirthProfile(
        name="RecTest",
        birth_date=date(1990, 6, 15),
        birth_time=time(12, 0),
        birth_city="台北",
        birth_country="台灣",
        themes=list(AnalysisTheme),
        report_language=ReportLanguage.TRADITIONAL_CHINESE,
        report_length=ReportLength.FULL,
        birth_latitude=25.0330,
        birth_longitude=121.5654,
        birth_timezone_offset=8.0,
        birth_time_is_known=True,
    )
    return HumanDesignEngine().calculate(profile)


# ── A. Models ─────────────────────────────────────────────────────────────────

class TestExternalHDChart:
    def test_empty_chart_can_be_created(self):
        from human_design_reconciliation.models import ExternalHumanDesignChart
        chart = ExternalHumanDesignChart()
        assert chart.source_name == "manual_external"
        assert chart.type_name is None

    def test_chart_with_partial_data(self):
        from human_design_reconciliation.models import ExternalHumanDesignChart
        chart = ExternalHumanDesignChart(type_name="Projector", profile="4/6")
        assert chart.type_name == "Projector"
        assert chart.profile == "4/6"
        assert chart.authority is None


# ── B. Examples ───────────────────────────────────────────────────────────────

class TestExamples:
    def test_blank_template_not_validated(self):
        from human_design_reconciliation.examples import BLANK_EXTERNAL_HD_TEMPLATE
        assert "fill" in BLANK_EXTERNAL_HD_TEMPLATE.raw_notes.lower() or \
               "blank" in BLANK_EXTERNAL_HD_TEMPLATE.raw_notes.lower()

    def test_blank_template_has_no_type(self):
        from human_design_reconciliation.examples import BLANK_EXTERNAL_HD_TEMPLATE
        assert BLANK_EXTERNAL_HD_TEMPLATE.type_name is None

    def test_rossi_template_raw_notes_contains_pending(self):
        from human_design_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_HD_TEMPLATE
        assert "pending" in EXAMPLE_ROSSI_EXTERNAL_HD_TEMPLATE.raw_notes.lower() or \
               "Pending" in EXAMPLE_ROSSI_EXTERNAL_HD_TEMPLATE.raw_notes

    def test_rossi_template_has_no_type(self):
        from human_design_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_HD_TEMPLATE
        assert EXAMPLE_ROSSI_EXTERNAL_HD_TEMPLATE.type_name is None

    def test_blank_json_is_valid_json(self):
        import json
        from human_design_reconciliation.examples import BLANK_EXTERNAL_HD_JSON
        parsed = json.loads(BLANK_EXTERNAL_HD_JSON)
        assert isinstance(parsed, dict)

    def test_rossi_json_is_valid_json(self):
        import json
        from human_design_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_HD_JSON
        parsed = json.loads(EXAMPLE_ROSSI_EXTERNAL_HD_JSON)
        assert isinstance(parsed, dict)


# ── C. Normalize functions ────────────────────────────────────────────────────

class TestNormalizeFunctions:
    def test_normalize_type_projector_english(self):
        from human_design_reconciliation.engine import normalize_type
        assert normalize_type("Projector") == "Projector"

    def test_normalize_type_projector_chinese(self):
        from human_design_reconciliation.engine import normalize_type
        assert normalize_type("投射者") == "Projector"

    def test_normalize_type_generator_chinese(self):
        from human_design_reconciliation.engine import normalize_type
        assert normalize_type("生產者") == "Generator"

    def test_normalize_authority_environmental(self):
        from human_design_reconciliation.engine import normalize_authority
        assert normalize_authority("Environmental") == "Environmental"

    def test_normalize_authority_environmental_chinese(self):
        from human_design_reconciliation.engine import normalize_authority
        assert normalize_authority("環境權威") == "Environmental"

    def test_normalize_profile_dash(self):
        from human_design_reconciliation.engine import normalize_profile
        assert normalize_profile("4-6") == "4/6"

    def test_normalize_profile_pipe(self):
        from human_design_reconciliation.engine import normalize_profile
        assert normalize_profile("4｜6") == "4/6"

    def test_normalize_profile_same(self):
        from human_design_reconciliation.engine import normalize_profile
        assert normalize_profile("4/6") == "4/6"

    def test_normalize_channel_sorted(self):
        from human_design_reconciliation.engine import normalize_channel
        assert normalize_channel("34-20") == "20-34"

    def test_normalize_channel_already_sorted(self):
        from human_design_reconciliation.engine import normalize_channel
        assert normalize_channel("20-34") == "20-34"

    def test_normalize_center_g_chinese(self):
        from human_design_reconciliation.engine import normalize_center
        assert normalize_center("G中心") == "G"

    def test_normalize_center_g_english(self):
        from human_design_reconciliation.engine import normalize_center
        assert normalize_center("G") == "G"

    def test_normalize_center_solar_plexus(self):
        from human_design_reconciliation.engine import normalize_center
        assert normalize_center("情緒中心") == "Solar Plexus"


# ── D. Reconciliation results ─────────────────────────────────────────────────

class TestReconciliationEngine:
    def test_empty_external_gives_insufficient_data(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        from human_design_reconciliation.models import ExternalHumanDesignChart
        local = _make_local_chart()
        external = ExternalHumanDesignChart()
        report = HumanDesignReconciliationEngine().reconcile(local, external)
        assert report.overall_status == "insufficient_external_data"

    def test_identical_external_gives_mostly_match(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        from human_design_reconciliation.models import ExternalHumanDesignChart
        local = _make_local_chart()
        external = ExternalHumanDesignChart(
            type_name=local.type_name,
            strategy=local.strategy,
            authority=local.authority,
            profile=local.profile,
            defined_centers=list(local.defined_centers),
            activated_gates=[g.gate for g in local.activated_gates],
            defined_channels=[ch.channel for ch in local.defined_channels],
        )
        report = HumanDesignReconciliationEngine().reconcile(local, external)
        assert report.overall_status == "mostly_match"

    def test_type_mismatch_gives_mismatch_item(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        from human_design_reconciliation.models import ExternalHumanDesignChart
        local = _make_local_chart()
        # Deliberately use a wrong type
        wrong_type = "Reflector" if local.type_name != "Reflector" else "Projector"
        external = ExternalHumanDesignChart(type_name=wrong_type)
        report = HumanDesignReconciliationEngine().reconcile(local, external)
        type_items = [i for i in report.items if i.category == "type" and i.status == "mismatch"]
        assert len(type_items) >= 1

    def test_authority_mismatch_gives_mismatch_item(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        from human_design_reconciliation.models import ExternalHumanDesignChart
        local = _make_local_chart()
        wrong_authority = "Lunar"  # uncommon, unlikely to match local
        external = ExternalHumanDesignChart(
            type_name=local.type_name,
            authority=wrong_authority,
        )
        report = HumanDesignReconciliationEngine().reconcile(local, external)
        auth_items = [i for i in report.items if i.category == "authority" and i.status == "mismatch"]
        # Only assert mismatch if local authority is not Lunar
        if local.authority and "Lunar" not in local.authority and "月亮" not in local.authority:
            assert len(auth_items) >= 1

    def test_profile_mismatch_gives_mismatch_item(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        from human_design_reconciliation.models import ExternalHumanDesignChart
        local = _make_local_chart()
        wrong_profile = "6/3" if local.profile != "6/3" else "1/3"
        external = ExternalHumanDesignChart(
            type_name=local.type_name,
            profile=wrong_profile,
        )
        report = HumanDesignReconciliationEngine().reconcile(local, external)
        profile_items = [i for i in report.items if i.category == "profile" and i.status == "mismatch"]
        assert len(profile_items) >= 1

    def test_conscious_sun_gate_mismatch_severity_high(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        from human_design_reconciliation.models import ExternalHumanDesignChart, ExternalHDPlanetActivation
        local = _make_local_chart()
        # Provide a conscious sun with a wrong gate
        external = ExternalHumanDesignChart(
            type_name=local.type_name,
            conscious_activations=[
                ExternalHDPlanetActivation(planet="Sun", side="conscious", gate=99, line=1),
            ],
        )
        report = HumanDesignReconciliationEngine().reconcile(local, external)
        sun_items = [
            i for i in report.items
            if i.category == "conscious_planets" and "sun" in i.field.lower() and i.status == "mismatch"
        ]
        assert len(sun_items) >= 1
        assert sun_items[0].severity == "high"

    def test_design_sun_gate_mismatch_explanation_mentions_88_days(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        from human_design_reconciliation.models import ExternalHumanDesignChart, ExternalHDPlanetActivation
        local = _make_local_chart()
        external = ExternalHumanDesignChart(
            type_name=local.type_name,
            design_activations=[
                ExternalHDPlanetActivation(planet="Sun", side="design", gate=99, line=1),
            ],
        )
        report = HumanDesignReconciliationEngine().reconcile(local, external)
        design_sun_items = [
            i for i in report.items
            if i.category == "design_planets" and "sun" in i.field.lower() and i.status == "mismatch"
        ]
        assert len(design_sun_items) >= 1
        explanation = design_sun_items[0].explanation
        assert "88" in explanation or "solar arc" in explanation.lower()

    def test_gates_set_diff_reports_missing_and_extra(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        from human_design_reconciliation.models import ExternalHumanDesignChart
        local = _make_local_chart()
        # Provide some gates that are wrong
        external = ExternalHumanDesignChart(
            type_name=local.type_name,
            activated_gates=[1, 2, 3, 4, 5],  # very different from real
        )
        report = HumanDesignReconciliationEngine().reconcile(local, external)
        gate_items = [i for i in report.items if i.category == "gates"]
        assert len(gate_items) >= 1
        # The explanation should mention missing/extra
        gate_item = gate_items[0]
        assert "外部有本機無" in gate_item.explanation or "本機有外部無" in gate_item.explanation

    def test_channels_set_diff_reports_normalized_names(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        from human_design_reconciliation.models import ExternalHumanDesignChart
        local = _make_local_chart()
        # Use reversed channel notation — should normalize correctly
        external = ExternalHumanDesignChart(
            type_name=local.type_name,
            defined_channels=["99-1"],  # non-existent channel
        )
        report = HumanDesignReconciliationEngine().reconcile(local, external)
        ch_items = [i for i in report.items if i.category == "channels"]
        assert len(ch_items) >= 1
        # The local_value should contain normalized channel names
        assert "-" in ch_items[0].local_value or "[]" in ch_items[0].local_value

    def test_centers_diff_reports_center_names(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        from human_design_reconciliation.models import ExternalHumanDesignChart
        local = _make_local_chart()
        # Use Chinese center names — should normalize
        external = ExternalHumanDesignChart(
            type_name=local.type_name,
            defined_centers=["頭頂中心", "邏輯中心"],  # might differ from local
        )
        report = HumanDesignReconciliationEngine().reconcile(local, external)
        center_items = [i for i in report.items if i.category == "centers"]
        assert len(center_items) >= 1

    def test_no_crash_with_only_type_and_profile(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        from human_design_reconciliation.models import ExternalHumanDesignChart
        local = _make_local_chart()
        external = ExternalHumanDesignChart(
            type_name=local.type_name,
            profile=local.profile,
        )
        report = HumanDesignReconciliationEngine().reconcile(local, external)
        assert report is not None
        assert report.overall_status in (
            "mostly_match", "minor_difference", "major_difference", "insufficient_external_data"
        )


# ── E. Render template ────────────────────────────────────────────────────────

class TestRenderReconciliationMarkdown:
    def test_render_returns_string(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        from human_design_reconciliation.models import ExternalHumanDesignChart
        from human_design_reconciliation.templates import render_reconciliation_markdown
        local = _make_local_chart()
        external = ExternalHumanDesignChart()
        report = HumanDesignReconciliationEngine().reconcile(local, external)
        result = render_reconciliation_markdown(report)
        assert isinstance(result, str)

    def test_render_contains_title(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        from human_design_reconciliation.models import ExternalHumanDesignChart
        from human_design_reconciliation.templates import render_reconciliation_markdown
        local = _make_local_chart()
        external = ExternalHumanDesignChart(type_name=local.type_name)
        report = HumanDesignReconciliationEngine().reconcile(local, external)
        result = render_reconciliation_markdown(report)
        assert "人類圖外部排盤校準報告" in result

    def test_render_contains_overall_status(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        from human_design_reconciliation.models import ExternalHumanDesignChart
        from human_design_reconciliation.templates import render_reconciliation_markdown
        local = _make_local_chart()
        external = ExternalHumanDesignChart()
        report = HumanDesignReconciliationEngine().reconcile(local, external)
        result = render_reconciliation_markdown(report)
        assert "整體狀態" in result
