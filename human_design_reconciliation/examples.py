"""
Astro Destiny Analyzer — Human Design Reconciliation Examples (V1.9.4)

Provides blank and sample external HD chart templates and calibration case templates.
NOTE: These are INPUT TEMPLATES only — they do NOT represent validated external data.
"""
from __future__ import annotations
import json
from human_design_reconciliation.models import ExternalHumanDesignChart, ExternalHDPlanetActivation


# ── Blank template ────────────────────────────────────────────────────────────

BLANK_EXTERNAL_HD_TEMPLATE = ExternalHumanDesignChart(
    source_name="manual_external",
    source_url=None,
    chart_owner_label="",
    type_name=None,
    type_name_zh=None,
    strategy=None,
    authority=None,
    profile=None,
    incarnation_cross=None,
    conscious_activations=[],
    design_activations=[],
    activated_gates=[],
    defined_channels=[],
    defined_centers=[],
    open_centers=[],
    raw_notes="Blank template — fill in from external Human Design source before reconciling.",
)

BLANK_EXTERNAL_HD_JSON = json.dumps({
    "source_name": "manual_external",
    "source_url": None,
    "chart_owner_label": "",
    "type_name": None,
    "type_name_zh": None,
    "strategy": None,
    "authority": None,
    "profile": None,
    "incarnation_cross": None,
    "conscious_activations": [],
    "design_activations": [],
    "activated_gates": [],
    "defined_channels": [],
    "defined_centers": [],
    "open_centers": [],
    "raw_notes": "Blank template — fill in from external Human Design source before reconciling.",
}, ensure_ascii=False, indent=2)


# ── Rossi placeholder template ────────────────────────────────────────────────
# NOTE: This is NOT a validated external chart.
# Fields are empty pending real external input from Jovian Archive / Genetic Matrix.

EXAMPLE_ROSSI_EXTERNAL_HD_TEMPLATE = ExternalHumanDesignChart(
    source_name="rossi_placeholder_pending",
    source_url=None,
    chart_owner_label="Rossi (1989-09-21, 11:05, 台北)",
    type_name=None,
    type_name_zh=None,
    strategy=None,
    authority=None,
    profile=None,
    incarnation_cross=None,
    conscious_activations=[],
    design_activations=[],
    activated_gates=[],
    defined_channels=[],
    defined_centers=[],
    open_centers=[],
    raw_notes=(
        "Pending external Human Design chart input. Do not treat as validated. "
        "Fill in from Jovian Archive / Genetic Matrix / MyBodyGraph to begin reconciliation."
    ),
)

EXAMPLE_ROSSI_EXTERNAL_HD_JSON = json.dumps({
    "source_name": "rossi_placeholder_pending",
    "source_url": None,
    "chart_owner_label": "Rossi (1989-09-21, 11:05, 台北)",
    "type_name": None,
    "type_name_zh": None,
    "strategy": None,
    "authority": None,
    "profile": None,
    "incarnation_cross": None,
    "conscious_activations": [],
    "design_activations": [],
    "activated_gates": [],
    "defined_channels": [],
    "defined_centers": [],
    "open_centers": [],
    "raw_notes": (
        "Pending external Human Design chart input. Do not treat as validated. "
        "Fill in from Jovian Archive / Genetic Matrix / MyBodyGraph to begin reconciliation."
    ),
}, ensure_ascii=False, indent=2)


# ── V1.9.4 Calibration case templates ─────────────────────────────────────────

BLANK_CALIBRATION_CASE_TEMPLATE = json.dumps({
    "case_id": "",
    "label": "",
    "birth_date": "YYYY-MM-DD",
    "birth_time": "HH:MM",
    "birth_location": "",
    "timezone": "Asia/Taipei",
    "latitude": None,
    "longitude": None,
    "gender": None,
    "source_name": "",
    "source_url": None,
    "notes": "",
    "tags": [],
    "external_chart": {
        "source_name": "",
        "chart_owner_label": "",
        "type_name": "",
        "strategy": "",
        "authority": "",
        "profile": "",
        "incarnation_cross": "",
        "conscious_activations": [],
        "design_activations": [],
        "activated_gates": [],
        "defined_channels": [],
        "defined_centers": [],
        "open_centers": [],
        "raw_notes": "",
    },
}, ensure_ascii=False, indent=2)


BLANK_DATASET_TEMPLATE = json.dumps({
    "dataset_version": "1.9.4",
    "notes": "",
    "cases": [
        {
            "case_id": "",
            "label": "",
            "birth_date": "YYYY-MM-DD",
            "birth_time": "HH:MM",
            "birth_location": "",
            "timezone": "Asia/Taipei",
            "external_chart": {
                "source_name": "",
                "chart_owner_label": "",
                "type_name": "",
                "authority": "",
                "profile": "",
            },
        }
    ],
}, ensure_ascii=False, indent=2)


EXAMPLE_MINIMAL_EXTERNAL_CASE = json.dumps({
    "case_id": "sample_case_001",
    "label": "Sample External Case",
    "birth_date": "1990-06-15",
    "birth_time": "12:00",
    "birth_location": "台北",
    "timezone": "Asia/Taipei",
    "notes": "Example only. Replace with real external chart data.",
    "tags": ["sample", "example"],
    "external_chart": {
        "source_name": "example_source",
        "chart_owner_label": "Sample Person",
        "type_name": None,
        "strategy": None,
        "authority": None,
        "profile": None,
        "incarnation_cross": None,
        "conscious_activations": [],
        "design_activations": [],
        "activated_gates": [],
        "defined_channels": [],
        "defined_centers": [],
        "open_centers": [],
        "raw_notes": "Example only. Replace with real external chart data.",
    },
}, ensure_ascii=False, indent=2)
