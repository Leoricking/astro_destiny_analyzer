"""
Tests for V1.9.4 Human Design Calibration Exporters.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_reconciliation_report():
    from human_design_reconciliation.engine import HumanDesignReconciliationEngine
    from human_design_reconciliation.models import ExternalHumanDesignChart
    from human_design.engine import HumanDesignEngine
    from core.models import BirthProfile, AnalysisTheme, ReportLanguage, ReportLength
    from datetime import date, time
    profile = BirthProfile(
        name="ExportTest",
        birth_date=date(1990, 6, 15),
        birth_time=time(12, 0),
        birth_city="台北",
        birth_country="台灣",
        themes=list(AnalysisTheme),
        report_language=ReportLanguage.TRADITIONAL_CHINESE,
        report_length=ReportLength.FULL,
        birth_latitude=25.0, birth_longitude=121.5,
        birth_timezone_offset=8.0, birth_time_is_known=True,
    )
    local = HumanDesignEngine().calculate(profile)
    ext = ExternalHumanDesignChart(type_name="Generator", authority="Sacral", profile="1/3")
    return HumanDesignReconciliationEngine().reconcile(local, ext)


def _make_batch_summary():
    from human_design_reconciliation.models import BatchReconciliationSummary
    return BatchReconciliationSummary(
        total_cases=3,
        processed_cases=2,
        mostly_match_count=1,
        minor_difference_count=1,
        major_difference_count=0,
        insufficient_data_count=1,
        total_match_items=5,
        total_mismatch_items=2,
        total_method_difference_items=1,
        most_common_mismatch_categories=["gates", "profile"],
        design_date_method_notes=["Method: solar_arc_88"],
        gate_offset_notes=["Offset: +0.000°"],
        case_reports=[_make_reconciliation_report()],
        summary="Test batch summary",
    )


def _make_dataset():
    from human_design_reconciliation.models import (
        HumanDesignCalibrationDataset, HumanDesignCalibrationCase, ExternalHumanDesignChart,
    )
    return HumanDesignCalibrationDataset(
        cases=[
            HumanDesignCalibrationCase(
                case_id="c1",
                label="測試案例",
                birth_date="1990-06-15",
                external_chart=ExternalHumanDesignChart(type_name="Generator"),
            )
        ]
    )


# ── A. export_reconciliation_markdown ─────────────────────────────────────────

class TestExportReconciliationMarkdown:
    def test_contains_title(self):
        from human_design_reconciliation.exporters import export_reconciliation_markdown
        md = export_reconciliation_markdown(_make_reconciliation_report())
        assert "人類圖" in md or "校準" in md or "Human Design" in md

    def test_returns_string(self):
        from human_design_reconciliation.exporters import export_reconciliation_markdown
        result = export_reconciliation_markdown(_make_reconciliation_report())
        assert isinstance(result, str)

    def test_not_crash_on_empty_report(self):
        from human_design_reconciliation.exporters import export_reconciliation_markdown
        from human_design_reconciliation.models import HDReconciliationReport
        md = export_reconciliation_markdown(HDReconciliationReport())
        assert isinstance(md, str)


# ── B. export_batch_summary_markdown ──────────────────────────────────────────

class TestExportBatchSummaryMarkdown:
    def test_contains_multi_case_heading(self):
        from human_design_reconciliation.exporters import export_batch_summary_markdown
        md = export_batch_summary_markdown(_make_batch_summary())
        assert "多案例校準摘要" in md

    def test_returns_string(self):
        from human_design_reconciliation.exporters import export_batch_summary_markdown
        result = export_batch_summary_markdown(_make_batch_summary())
        assert isinstance(result, str)

    def test_contains_case_counts(self):
        from human_design_reconciliation.exporters import export_batch_summary_markdown
        md = export_batch_summary_markdown(_make_batch_summary())
        assert "3" in md  # total_cases

    def test_empty_batch_summary_not_crash(self):
        from human_design_reconciliation.exporters import export_batch_summary_markdown
        from human_design_reconciliation.models import BatchReconciliationSummary
        md = export_batch_summary_markdown(BatchReconciliationSummary())
        assert isinstance(md, str)


# ── C. export_reconciliation_html ────────────────────────────────────────────

class TestExportReconciliationHtml:
    def test_contains_meta_charset_utf8(self):
        from human_design_reconciliation.exporters import (
            export_reconciliation_markdown, export_reconciliation_html,
        )
        md = export_reconciliation_markdown(_make_reconciliation_report())
        html = export_reconciliation_html(md)
        assert "charset=utf-8" in html.lower() or 'charset="utf-8"' in html.lower()

    def test_no_script_tag(self):
        from human_design_reconciliation.exporters import (
            export_reconciliation_markdown, export_reconciliation_html,
        )
        md = export_reconciliation_markdown(_make_reconciliation_report())
        html = export_reconciliation_html(md)
        assert "<script" not in html.lower()

    def test_contains_footer(self):
        from human_design_reconciliation.exporters import (
            export_reconciliation_markdown, export_reconciliation_html,
        )
        md = export_reconciliation_markdown(_make_reconciliation_report())
        html = export_reconciliation_html(md)
        assert "Astro Destiny Analyzer" in html

    def test_returns_string(self):
        from human_design_reconciliation.exporters import export_reconciliation_html
        html = export_reconciliation_html("# Test")
        assert isinstance(html, str)

    def test_no_cdn_links(self):
        from human_design_reconciliation.exporters import (
            export_reconciliation_markdown, export_reconciliation_html,
        )
        md = export_reconciliation_markdown(_make_reconciliation_report())
        html = export_reconciliation_html(md)
        assert "cdn." not in html.lower()

    def test_html_title(self):
        from human_design_reconciliation.exporters import export_reconciliation_html
        html = export_reconciliation_html("# Test")
        assert "Human Design Calibration Report" in html


# ── D. export_dataset_json ────────────────────────────────────────────────────

class TestExportDatasetJson:
    def test_output_is_valid_json(self):
        from human_design_reconciliation.exporters import export_dataset_json
        ds = _make_dataset()
        output = export_dataset_json(ds)
        parsed = json.loads(output)
        assert "cases" in parsed

    def test_output_contains_chinese(self):
        from human_design_reconciliation.exporters import export_dataset_json
        ds = _make_dataset()
        output = export_dataset_json(ds)
        # ensure_ascii=False: Chinese should appear directly
        assert "測試案例" in output or "\\u" not in output

    def test_returns_string(self):
        from human_design_reconciliation.exporters import export_dataset_json
        ds = _make_dataset()
        assert isinstance(export_dataset_json(ds), str)


# ── E. safe_calibration_filename ──────────────────────────────────────────────

class TestSafeCalibrationFilename:
    def test_no_illegal_chars(self):
        from human_design_reconciliation.exporters import safe_calibration_filename
        fn = safe_calibration_filename("test report", "md")
        for ch in r'\/:*?"<>|':
            assert ch not in fn

    def test_no_emoji(self):
        from human_design_reconciliation.exporters import safe_calibration_filename
        fn = safe_calibration_filename("test 🔷 report", "md")
        assert "🔷" not in fn

    def test_correct_suffix(self):
        from human_design_reconciliation.exporters import safe_calibration_filename
        fn = safe_calibration_filename("test", "md")
        assert fn.endswith(".md")
        fn2 = safe_calibration_filename("test", "html")
        assert fn2.endswith(".html")

    def test_prefix_format(self):
        from human_design_reconciliation.exporters import safe_calibration_filename
        fn = safe_calibration_filename("my_case", "json")
        assert fn.startswith("human_design_calibration_")

    def test_empty_label_safe(self):
        from human_design_reconciliation.exporters import safe_calibration_filename
        fn = safe_calibration_filename("", "md")
        assert fn.endswith(".md")
        assert "human_design_calibration_" in fn

    def test_chinese_label_safe(self):
        from human_design_reconciliation.exporters import safe_calibration_filename
        fn = safe_calibration_filename("測試校準", "md")
        assert isinstance(fn, str)
        assert fn.endswith(".md")
