"""
Tests for V1.9.4 Human Design Case Import (dataset.py).
"""
import sys
import os
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _blank_ext_json():
    return json.dumps({
        "source_name": "test",
        "type_name": "Generator",
        "authority": "Sacral",
        "profile": "1/3",
    })


def _full_case_json(case_id="case001", label="Test Case"):
    return json.dumps({
        "case_id": case_id,
        "label": label,
        "birth_date": "1990-06-15",
        "birth_time": "12:00",
        "birth_location": "台北",
        "timezone": "Asia/Taipei",
        "external_chart": {
            "source_name": "test_source",
            "chart_owner_label": "Test Person",
            "type_name": "Generator",
            "authority": "Sacral",
            "profile": "1/3",
        },
    })


# ── A. parse_external_chart_json ──────────────────────────────────────────────

class TestParseExternalChartJson:
    def test_parses_valid_json(self):
        from human_design_reconciliation.dataset import parse_external_chart_json
        result = parse_external_chart_json(_blank_ext_json())
        assert result.type_name == "Generator"

    def test_supports_external_chart_wrapper(self):
        from human_design_reconciliation.dataset import parse_external_chart_json
        wrapped = json.dumps({"external_chart": {"type_name": "Projector", "authority": "Splenic"}})
        result = parse_external_chart_json(wrapped)
        assert result.type_name == "Projector"

    def test_invalid_json_raises_value_error(self):
        from human_design_reconciliation.dataset import parse_external_chart_json
        with pytest.raises(ValueError):
            parse_external_chart_json("{not valid json")

    def test_empty_string_raises_value_error(self):
        from human_design_reconciliation.dataset import parse_external_chart_json
        with pytest.raises(ValueError):
            parse_external_chart_json("")

    def test_blank_fields_allowed(self):
        from human_design_reconciliation.dataset import parse_external_chart_json
        result = parse_external_chart_json(json.dumps({"source_name": "test"}))
        assert result is not None
        assert result.type_name is None

    def test_list_input_raises_value_error(self):
        from human_design_reconciliation.dataset import parse_external_chart_json
        with pytest.raises(ValueError):
            parse_external_chart_json(json.dumps([1, 2, 3]))


# ── B. parse_calibration_case_json ────────────────────────────────────────────

class TestParseCalibrationCaseJson:
    def test_parses_full_case(self):
        from human_design_reconciliation.dataset import parse_calibration_case_json
        result = parse_calibration_case_json(_full_case_json())
        assert result.case_id == "case001"
        assert result.label == "Test Case"
        assert result.external_chart.type_name == "Generator"

    def test_missing_case_id_auto_generated(self):
        from human_design_reconciliation.dataset import parse_calibration_case_json
        data = json.dumps({
            "label": "AutoID Test",
            "birth_date": "1990-01-01",
            "external_chart": {"type_name": "Projector"},
        })
        result = parse_calibration_case_json(data)
        assert result.case_id != ""
        assert result.case_id.startswith("case_")

    def test_missing_label_auto_filled(self):
        from human_design_reconciliation.dataset import parse_calibration_case_json
        data = json.dumps({
            "birth_date": "1990-01-01",
            "external_chart": {"chart_owner_label": "Jane", "type_name": "Projector"},
        })
        result = parse_calibration_case_json(data)
        assert result.label in ("Jane", "Untitled Case") or result.label != ""

    def test_missing_both_id_and_label_uses_untitled(self):
        from human_design_reconciliation.dataset import parse_calibration_case_json
        data = json.dumps({"birth_date": "1990-01-01", "external_chart": {}})
        result = parse_calibration_case_json(data)
        assert result.label != ""
        assert result.case_id != ""

    def test_invalid_json_raises_value_error(self):
        from human_design_reconciliation.dataset import parse_calibration_case_json
        with pytest.raises(ValueError):
            parse_calibration_case_json("not json")

    def test_empty_string_raises_value_error(self):
        from human_design_reconciliation.dataset import parse_calibration_case_json
        with pytest.raises(ValueError):
            parse_calibration_case_json("")


# ── C. parse_calibration_dataset_json ────────────────────────────────────────

class TestParseCalibrationDatasetJson:
    def test_supports_dataset_object(self):
        from human_design_reconciliation.dataset import parse_calibration_dataset_json
        data = json.dumps({
            "dataset_version": "1.9.4",
            "cases": [
                {"case_id": "c1", "label": "Case 1", "birth_date": "1990-01-01",
                 "external_chart": {"type_name": "Generator"}},
            ],
        })
        result = parse_calibration_dataset_json(data)
        assert len(result.cases) == 1

    def test_supports_list_of_cases(self):
        from human_design_reconciliation.dataset import parse_calibration_dataset_json
        data = json.dumps([
            {"case_id": "c1", "label": "A", "birth_date": "1990-01-01", "external_chart": {}},
            {"case_id": "c2", "label": "B", "birth_date": "1991-01-01", "external_chart": {}},
        ])
        result = parse_calibration_dataset_json(data)
        assert len(result.cases) == 2

    def test_supports_single_case(self):
        from human_design_reconciliation.dataset import parse_calibration_dataset_json
        result = parse_calibration_dataset_json(_full_case_json())
        assert len(result.cases) == 1

    def test_invalid_json_raises_value_error(self):
        from human_design_reconciliation.dataset import parse_calibration_dataset_json
        with pytest.raises(ValueError):
            parse_calibration_dataset_json("{broken")

    def test_empty_string_raises_value_error(self):
        from human_design_reconciliation.dataset import parse_calibration_dataset_json
        with pytest.raises(ValueError):
            parse_calibration_dataset_json("")

    def test_does_not_crash_on_malformed_case(self):
        from human_design_reconciliation.dataset import parse_calibration_dataset_json
        data = json.dumps({
            "cases": [
                {"case_id": "good", "label": "Good", "birth_date": "1990-01-01", "external_chart": {}},
                "not a dict",  # malformed — should be skipped
            ]
        })
        result = parse_calibration_dataset_json(data)
        assert len(result.cases) >= 1  # good case survives


# ── D. dataset_to_json ────────────────────────────────────────────────────────

class TestDatasetToJson:
    def test_ensure_ascii_false(self):
        from human_design_reconciliation.dataset import parse_calibration_dataset_json, dataset_to_json
        ds = parse_calibration_dataset_json(_full_case_json())
        output = dataset_to_json(ds)
        assert isinstance(output, str)
        # ensure_ascii=False: Chinese characters should NOT be escaped
        assert "\\u" not in output or "台北" in output

    def test_valid_json_output(self):
        from human_design_reconciliation.dataset import parse_calibration_dataset_json, dataset_to_json
        ds = parse_calibration_dataset_json(_full_case_json())
        output = dataset_to_json(ds)
        parsed = json.loads(output)
        assert "cases" in parsed


# ── E. append_case_to_dataset ─────────────────────────────────────────────────

class TestAppendCaseToDataset:
    def _make_dataset(self):
        from human_design_reconciliation.models import HumanDesignCalibrationDataset
        return HumanDesignCalibrationDataset()

    def _make_case(self, case_id="c1"):
        from human_design_reconciliation.dataset import parse_calibration_case_json
        return parse_calibration_case_json(_full_case_json(case_id=case_id, label=f"Case {case_id}"))

    def test_append_adds_case(self):
        from human_design_reconciliation.dataset import append_case_to_dataset
        ds = self._make_dataset()
        case = self._make_case("c1")
        ds = append_case_to_dataset(ds, case)
        assert len(ds.cases) == 1

    def test_duplicate_case_id_not_overwritten_by_default(self):
        from human_design_reconciliation.dataset import append_case_to_dataset
        ds = self._make_dataset()
        c1 = self._make_case("c1")
        c1_dup = self._make_case("c1")
        ds = append_case_to_dataset(ds, c1)
        ds = append_case_to_dataset(ds, c1_dup)
        assert len(ds.cases) == 2
        ids = [c.case_id for c in ds.cases]
        assert "c1" in ids
        assert "c1-2" in ids

    def test_multiple_appends(self):
        from human_design_reconciliation.dataset import append_case_to_dataset
        ds = self._make_dataset()
        for i in range(3):
            ds = append_case_to_dataset(ds, self._make_case(f"c{i}"))
        assert len(ds.cases) == 3


# ── F. load_dataset / save_dataset ────────────────────────────────────────────

class TestLoadSaveDataset:
    def test_load_missing_dataset_returns_empty(self):
        from human_design_reconciliation.dataset import load_dataset
        result = load_dataset(Path("/nonexistent/path/dataset.json"))
        assert result.cases == []

    def test_save_load_roundtrip(self):
        from human_design_reconciliation.dataset import (
            parse_calibration_dataset_json, save_dataset, load_dataset,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_dataset.json"
            ds = parse_calibration_dataset_json(_full_case_json())
            save_dataset(ds, path)
            loaded = load_dataset(path)
            assert len(loaded.cases) == 1
            assert loaded.cases[0].case_id == "case001"
