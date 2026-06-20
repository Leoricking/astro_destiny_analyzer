from pathlib import Path

from core.models import ReportLength
from demo.sample_profiles import SAMPLE_PROFILES
from i18n.display_names import (
    translate_ziwei_bureau,
    translate_ziwei_star,
    translate_ziwei_palace,
)
from reports.generator import ReportGenerator
from reports.markdown_exporter import MarkdownExporter


def test_ziwei_display_values_are_localized_without_mutation():
    assert translate_ziwei_bureau("土五局", "en") == "Earth Five Bureau"
    assert translate_ziwei_star("貪狼", "en") == "Tan Lang"
    assert translate_ziwei_palace("命宮", "en") == "Life Palace"
    assert translate_ziwei_bureau("土五局", "zh-TW") == "土五局"


def test_complete_10k_is_distinct_and_more_detailed_than_standard():
    p1 = SAMPLE_PROFILES[0].model_copy(deep=True)
    p1.report_length = ReportLength.STANDARD
    r1 = ReportGenerator().generate(p1, persist=False)
    standard = MarkdownExporter().export(r1, language="en")

    p2 = SAMPLE_PROFILES[0].model_copy(deep=True)
    p2.report_length = ReportLength.COMPLETE_10K
    r2 = ReportGenerator().generate(p2, persist=False)
    complete = MarkdownExporter().export(r2, language="en")

    assert len(complete) > len(standard) + 3000
    assert "Calculation evidence" in complete
    assert "Concrete validation questions" in complete


def test_input_navigation_restores_snapshot_and_has_explicit_clear():
    source = Path("ui/streamlit_app.py").read_text(encoding="utf-8")
    assert 'page == PAGE_INPUT and _previous_page not in (None, PAGE_INPUT)' in source
    assert '_restore_input_snapshot(_saved_snapshot)' in source
    assert 'key="input_clear_all"' in source


def test_human_design_summary_contains_calculated_tables():
    source = Path("ui/streamlit_app.py").read_text(encoding="utf-8")
    assert 'getattr(hd, "centers", [])' in source
    assert 'getattr(hd, "defined_channels", [])' in source
    assert 'getattr(hd, "activated_gates", [])' in source
