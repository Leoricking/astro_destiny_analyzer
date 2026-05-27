"""
Astro Destiny Analyzer — Compatibility Report Renderer
V1.7.0
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from compatibility.models import CompatibilityReport


def render_compatibility_report(report: "CompatibilityReport") -> str:
    """
    Render a full Markdown string from a CompatibilityReport.
    Delegates to compatibility.templates.build_compatibility_markdown.
    """
    from compatibility.templates import build_compatibility_markdown
    return build_compatibility_markdown(report)
