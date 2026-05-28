"""
Astro Destiny Analyzer — Human Design Gate Wheel Calibration (V1.9.3)

Provides simulation tools for testing gate wheel offset effects on planet activations.
"""
from __future__ import annotations
from typing import List, Dict

from human_design.engine import longitude_to_gate_line


def simulate_gate_offset_for_activations(
    longitudes: Dict[str, float],
    offsets: List[float],
) -> List[Dict]:
    """
    Simulate how gate and line assignments change for each planet longitude
    across a list of gate wheel offset values.

    Args:
        longitudes: dict of {planet_name: ecliptic_longitude}
        offsets: list of offset_degrees values to test (e.g. [-2.0, -1.0, 0.0, 1.0, 2.0])

    Returns:
        List of dicts, one per (planet, offset) combination:
        {
            "planet": str,
            "longitude": float,
            "offset": float,
            "gate": int,
            "line": int,
        }
    """
    results = []
    for offset in offsets:
        for planet, lon in longitudes.items():
            gate, line = longitude_to_gate_line(lon, offset)
            results.append({
                "planet": planet,
                "longitude": round(lon, 4),
                "offset": offset,
                "gate": gate,
                "line": line,
            })
    return results
