"""
Astro Destiny Analyzer — Human Design Calibration Dataset (V1.9.4)

Parse, save, load, and manage HumanDesignCalibrationDataset / cases.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

from human_design_reconciliation.models import (
    ExternalHumanDesignChart,
    HumanDesignCalibrationCase,
    HumanDesignCalibrationDataset,
)


# ── Parse helpers ─────────────────────────────────────────────────────────────

def parse_external_chart_json(text: str) -> ExternalHumanDesignChart:
    """
    Parse a JSON string into an ExternalHumanDesignChart.

    Supports:
    - Direct ExternalHumanDesignChart JSON
    - Wrapped: {"external_chart": {...}}

    Raises ValueError with a clear message on failure.
    """
    if not text or not text.strip():
        raise ValueError("JSON text is empty. Please paste a valid ExternalHumanDesignChart JSON.")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("JSON must be an object (dict), not a list or primitive.")

    # Unwrap {"external_chart": {...}} if present
    if "external_chart" in data and isinstance(data["external_chart"], dict):
        data = data["external_chart"]

    try:
        return ExternalHumanDesignChart(**data)
    except Exception as e:
        raise ValueError(f"Could not construct ExternalHumanDesignChart: {e}") from e


def parse_calibration_case_json(text: str) -> HumanDesignCalibrationCase:
    """
    Parse a JSON string into a HumanDesignCalibrationCase.

    Supports:
    - Full case JSON
    - Simplified JSON with only "external_chart" key

    Auto-fills missing case_id and label.
    Raises ValueError on malformed input.
    """
    if not text or not text.strip():
        raise ValueError("JSON text is empty.")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("JSON must be an object (dict).")

    # Simplified input: only contains external_chart fields (no case_id or external_chart key)
    if "external_chart" not in data and (
        "type_name" in data or "authority" in data or "profile" in data
        or "source_name" in data
    ):
        # Treat entire object as external_chart
        try:
            ext = ExternalHumanDesignChart(**data)
        except Exception as e:
            raise ValueError(f"Could not parse as ExternalHumanDesignChart: {e}") from e
        data = {"external_chart": ext.model_dump()}

    # Auto-fill case_id if missing
    if not data.get("case_id"):
        data["case_id"] = f"case_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Auto-fill label if missing
    if not data.get("label"):
        ext_data = data.get("external_chart", {})
        label = (
            ext_data.get("chart_owner_label", "") if isinstance(ext_data, dict) else ""
        )
        data["label"] = label or "Untitled Case"

    try:
        return HumanDesignCalibrationCase(**data)
    except Exception as e:
        raise ValueError(f"Could not construct HumanDesignCalibrationCase: {e}") from e


def parse_calibration_dataset_json(text: str) -> HumanDesignCalibrationDataset:
    """
    Parse a JSON string into a HumanDesignCalibrationDataset.

    Supports:
    - {"dataset_version": ..., "cases": [...]}
    - A list of cases: [...]
    - A single case object (auto-wrapped)

    Raises ValueError on malformed input.
    """
    if not text or not text.strip():
        raise ValueError("JSON text is empty.")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e

    # Handle list of cases
    if isinstance(data, list):
        cases = []
        for i, item in enumerate(data):
            try:
                cases.append(parse_calibration_case_json(json.dumps(item)))
            except Exception:
                pass  # Skip malformed individual cases
        return HumanDesignCalibrationDataset(cases=cases)

    if not isinstance(data, dict):
        raise ValueError("JSON must be an object or array.")

    # Single case wrapped into dataset
    if "cases" not in data:
        try:
            case = parse_calibration_case_json(text)
            return HumanDesignCalibrationDataset(cases=[case])
        except Exception:
            raise ValueError(
                "JSON is not a dataset (missing 'cases' key) and could not be parsed as a single case."
            )

    # Full dataset object
    raw_cases = data.pop("cases", [])
    cases = []
    for item in raw_cases:
        try:
            cases.append(parse_calibration_case_json(json.dumps(item)))
        except Exception:
            pass

    try:
        dataset = HumanDesignCalibrationDataset(cases=cases, **data)
    except Exception as e:
        raise ValueError(f"Could not construct HumanDesignCalibrationDataset: {e}") from e

    return dataset


# ── Serialization ─────────────────────────────────────────────────────────────

def dataset_to_json(dataset: HumanDesignCalibrationDataset) -> str:
    """Serialize a dataset to a JSON string (ensure_ascii=False, indent=2)."""
    return json.dumps(dataset.model_dump(), ensure_ascii=False, indent=2)


# ── Persistence ───────────────────────────────────────────────────────────────

def save_dataset(dataset: HumanDesignCalibrationDataset, path: Path) -> None:
    """Save a dataset to a JSON file. Creates parent directories if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    dataset.updated_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    path.write_text(dataset_to_json(dataset), encoding="utf-8")


def load_dataset(path: Path) -> HumanDesignCalibrationDataset:
    """
    Load a dataset from a JSON file.
    Returns an empty dataset if file does not exist.
    Raises ValueError if JSON is malformed.
    """
    path = Path(path)
    if not path.exists():
        return HumanDesignCalibrationDataset()
    text = path.read_text(encoding="utf-8")
    try:
        return parse_calibration_dataset_json(text)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Could not load dataset from {path}: {e}") from e


# ── Dataset management ────────────────────────────────────────────────────────

def append_case_to_dataset(
    dataset: HumanDesignCalibrationDataset,
    case: HumanDesignCalibrationCase,
    overwrite: bool = False,
) -> HumanDesignCalibrationDataset:
    """
    Append a case to a dataset.

    If case_id already exists:
    - overwrite=False (default): append with case_id suffixed "-2", "-3", etc.
    - overwrite=True: replace the existing case.

    Returns the updated dataset (mutates in place and returns it).
    """
    existing_ids = {c.case_id for c in dataset.cases}

    if case.case_id in existing_ids:
        if overwrite:
            dataset.cases = [c for c in dataset.cases if c.case_id != case.case_id]
            dataset.cases.append(case)
            return dataset
        # Generate unique ID
        base_id = case.case_id
        suffix = 2
        new_id = f"{base_id}-{suffix}"
        while new_id in existing_ids:
            suffix += 1
            new_id = f"{base_id}-{suffix}"
        case = case.model_copy(update={"case_id": new_id})

    dataset.cases.append(case)
    return dataset
