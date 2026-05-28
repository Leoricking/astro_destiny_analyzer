"""
Astro Destiny Analyzer — Human Design Data Models (V1.9.0)
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List, Tuple


class HDPlanetActivation(BaseModel):
    planet: str
    longitude: float
    sign: str
    gate: int
    line: int
    color: Optional[int] = None
    tone: Optional[int] = None
    base: Optional[int] = None
    side: str                   # "conscious" | "design"
    is_personality: bool = False
    is_design: bool = False
    interpretation: str = ""


class HDGate(BaseModel):
    gate: int
    name: str
    center: str
    theme: str
    activated_by: List[str] = Field(default_factory=list)
    side_sources: List[str] = Field(default_factory=list)
    interpretation: str = ""


class HDChannel(BaseModel):
    channel: str                # e.g. "34-20"
    gates: Tuple[int, int]
    name: str
    centers: Tuple[str, str]
    circuit: str = ""
    is_defined: bool = False
    interpretation: str = ""


class HDCenter(BaseModel):
    name: str
    is_defined: bool
    defined_by_channels: List[str] = Field(default_factory=list)
    activated_gates: List[int] = Field(default_factory=list)
    theme: str = ""
    defined_interpretation: str = ""
    open_interpretation: str = ""


class HumanDesignChart(BaseModel):
    calculation_mode: str       # "swiss_ephemeris_phase1" | "mock_fallback" | "partial"
    type_name: str              # "Generator" | "Manifesting Generator" | "Projector" | "Manifestor" | "Reflector" | "Unknown"
    type_name_zh: str
    strategy: str
    authority: str
    profile: str                # e.g. "1/3"
    incarnation_cross: str
    conscious_activations: List[HDPlanetActivation] = Field(default_factory=list)
    design_activations: List[HDPlanetActivation] = Field(default_factory=list)
    activated_gates: List[HDGate] = Field(default_factory=list)
    defined_channels: List[HDChannel] = Field(default_factory=list)
    centers: List[HDCenter] = Field(default_factory=list)
    defined_centers: List[str] = Field(default_factory=list)
    open_centers: List[str] = Field(default_factory=list)
    decision_guidance: str = ""
    energy_summary: str = ""
    conditioning_risks: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    growth_advice: List[str] = Field(default_factory=list)
    accuracy_note: str = ""
    design_datetime: Optional[str] = None
    birth_datetime: Optional[str] = None
    # V1.9.3 calibration fields
    design_date_method: str = "solar_arc_88"
    design_date_fallback_used: bool = False
    design_solar_arc_target_longitude: Optional[float] = None
    design_solar_arc_actual_longitude: Optional[float] = None
    design_solar_arc_error_degrees: Optional[float] = None
    gate_wheel_offset_degrees: float = 0.0
    gate_wheel_version: str = "phase1_i_ching_order_offset_0"
    calibration_notes: List[str] = Field(default_factory=list)
