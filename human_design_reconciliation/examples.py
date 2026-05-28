"""
Astro Destiny Analyzer — Human Design Reconciliation Examples (V1.9.2)

Provides blank and sample external HD chart templates.
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
