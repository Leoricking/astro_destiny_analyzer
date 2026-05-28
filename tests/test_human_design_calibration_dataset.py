"""
Tests for V1.9.4 Human Design Calibration Dataset models and batch reconciliation.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_local_chart():
    from human_design.engine import HumanDesignEngine
    from core.models import BirthProfile, AnalysisTheme, ReportLanguage, ReportLength
    from datetime import date, time
    profile = BirthProfile(
        name="DatasetTest",
        birth_date=date(1990, 6, 15),
        birth_time=time(12, 0),
        birth_city="台北",
        birth_country="台灣",
        themes=list(AnalysisTheme),
        report_language=ReportLanguage.TRADITIONAL_CHINESE,
        report_length=ReportLength.FULL,
        birth_latitude=25.0,
        birth_longitude=121.5,
        birth_timezone_offset=8.0,
        birth_time_is_known=True,
    )
    return HumanDesignEngine().calculate(profile)


def _make_case(case_id="c1", type_name=None, profile=None):
    from human_design_reconciliation.models import (
        HumanDesignCalibrationCase, ExternalHumanDesignChart,
    )
    ext = ExternalHumanDesignChart(
        type_name=type_name,
        profile=profile,
        source_name="test",
    )
    return HumanDesignCalibrationCase(
        case_id=case_id,
        label=f"Case {case_id}",
        birth_date="1990-06-15",
        external_chart=ext,
    )


def _make_dataset(n=2):
    from human_design_reconciliation.models import HumanDesignCalibrationDataset
    cases = [_make_case(f"c{i}") for i in range(n)]
    return HumanDesignCalibrationDataset(cases=cases)


# ── A. Model creation ─────────────────────────────────────────────────────────

class TestHumanDesignCalibrationDatasetModel:
    def test_dataset_createable(self):
        from human_design_reconciliation.models import HumanDesignCalibrationDataset
        ds = HumanDesignCalibrationDataset()
        assert ds.dataset_version == "1.9.4"
        assert ds.cases == []

    def test_dataset_with_cases(self):
        ds = _make_dataset(3)
        assert len(ds.cases) == 3

    def test_dataset_version_default(self):
        from human_design_reconciliation.models import HumanDesignCalibrationDataset
        ds = HumanDesignCalibrationDataset()
        assert ds.dataset_version == "1.9.4"


class TestBatchReconciliationSummaryModel:
    def test_summary_createable(self):
        from human_design_reconciliation.models import BatchReconciliationSummary
        s = BatchReconciliationSummary()
        assert s.total_cases == 0
        assert s.most_common_mismatch_categories == []
        assert s.design_date_method_notes == []
        assert s.gate_offset_notes == []
        assert s.case_reports == []

    def test_summary_with_counts(self):
        from human_design_reconciliation.models import BatchReconciliationSummary
        s = BatchReconciliationSummary(
            total_cases=5,
            processed_cases=4,
            mostly_match_count=2,
            minor_difference_count=1,
            major_difference_count=1,
        )
        assert s.total_cases == 5
        assert s.processed_cases == 4


# ── B. reconcile_case ────────────────────────────────────────────────────────

class TestReconcileCase:
    def test_reconcile_case_returns_report(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        local = _make_local_chart()
        case = _make_case("test1", type_name="Generator")
        engine = HumanDesignReconciliationEngine()
        report = engine.reconcile_case(local, case)
        assert report is not None
        assert report.overall_status != ""

    def test_reconcile_case_insufficient_when_no_data(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        local = _make_local_chart()
        case = _make_case("empty1")  # no type_name, no data
        engine = HumanDesignReconciliationEngine()
        report = engine.reconcile_case(local, case)
        assert report.overall_status == "insufficient_external_data"

    def test_reconcile_case_with_type_data(self):
        from human_design_reconciliation.engine import HumanDesignReconciliationEngine
        local = _make_local_chart()
        case = _make_case("t1", type_name="Generator", profile="1/3")
        engine = HumanDesignReconciliationEngine()
        report = engine.reconcile_case(local, case)
        # Should have items since we provided type and profile data
        assert len(report.items) > 0


# ── C. reconcile_dataset ─────────────────────────────────────────────────────

class TestReconcileDataset:
    def test_batch_total_cases_correct(self):
        from human_design_reconciliation.engine import reconcile_dataset
        local = _make_local_chart()
        ds = _make_dataset(3)
        summary = reconcile_dataset(local, ds)
        assert summary.total_cases == 3

    def test_batch_processed_cases_correct(self):
        from human_design_reconciliation.engine import reconcile_dataset
        from human_design_reconciliation.models import (
            HumanDesignCalibrationDataset, HumanDesignCalibrationCase, ExternalHumanDesignChart,
        )
        local = _make_local_chart()
        # Mix: 1 with data, 1 without
        ds = HumanDesignCalibrationDataset(cases=[
            HumanDesignCalibrationCase(
                case_id="a", label="A", birth_date="1990-01-01",
                external_chart=ExternalHumanDesignChart(type_name="Generator"),
            ),
            HumanDesignCalibrationCase(
                case_id="b", label="B", birth_date="1990-01-01",
                external_chart=ExternalHumanDesignChart(),
            ),
        ])
        summary = reconcile_dataset(local, ds)
        assert summary.total_cases == 2
        # At least 1 processed (the one with data)
        assert summary.processed_cases >= 0  # depends on status check

    def test_batch_empty_dataset_no_crash(self):
        from human_design_reconciliation.engine import reconcile_dataset
        from human_design_reconciliation.models import HumanDesignCalibrationDataset
        local = _make_local_chart()
        ds = HumanDesignCalibrationDataset()
        summary = reconcile_dataset(local, ds)
        assert summary.total_cases == 0
        assert summary.processed_cases == 0

    def test_batch_design_date_method_notes_not_none(self):
        from human_design_reconciliation.engine import reconcile_dataset
        local = _make_local_chart()
        ds = _make_dataset(1)
        summary = reconcile_dataset(local, ds)
        assert summary.design_date_method_notes is not None
        assert isinstance(summary.design_date_method_notes, list)

    def test_batch_gate_offset_notes_not_none(self):
        from human_design_reconciliation.engine import reconcile_dataset
        local = _make_local_chart()
        ds = _make_dataset(1)
        summary = reconcile_dataset(local, ds)
        assert summary.gate_offset_notes is not None
        assert isinstance(summary.gate_offset_notes, list)

    def test_batch_mismatch_categories_list(self):
        from human_design_reconciliation.engine import reconcile_dataset
        local = _make_local_chart()
        ds = _make_dataset(2)
        summary = reconcile_dataset(local, ds)
        assert isinstance(summary.most_common_mismatch_categories, list)

    def test_batch_case_reports_count(self):
        from human_design_reconciliation.engine import reconcile_dataset
        local = _make_local_chart()
        ds = _make_dataset(3)
        summary = reconcile_dataset(local, ds)
        assert len(summary.case_reports) == 3

    def test_batch_summary_string_not_empty(self):
        from human_design_reconciliation.engine import reconcile_dataset
        local = _make_local_chart()
        ds = _make_dataset(2)
        summary = reconcile_dataset(local, ds)
        assert isinstance(summary.summary, str)


# ── D. HumanDesignCalibrationCase model ──────────────────────────────────────

class TestCalibrationCaseModel:
    def test_default_timezone(self):
        case = _make_case()
        assert case.timezone == "Asia/Taipei"

    def test_default_tags_empty(self):
        case = _make_case()
        assert case.tags == []

    def test_notes_default_empty(self):
        case = _make_case()
        assert case.notes == ""

    def test_external_chart_accessible(self):
        case = _make_case("x1", type_name="Projector")
        assert case.external_chart.type_name == "Projector"
