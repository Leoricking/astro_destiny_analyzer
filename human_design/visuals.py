"""
Astro Destiny Analyzer — Human Design Visuals Module (V1.9.1)

Provides Centers visualization data and table renderers.
No external JS / CDN required.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List

from human_design.constants import CENTER_INFO

# Fixed display order for the 9 centers (top to bottom, head to root)
_CENTER_ORDER = [
    "Head", "Ajna", "Throat", "G", "Heart",
    "Sacral", "Spleen", "Solar Plexus", "Root",
]


class HDCenterVisual(BaseModel):
    center: str
    center_zh: str
    is_defined: bool
    state_label: str          # "已定義" | "開放"
    theme: str
    active_gates: List[int] = Field(default_factory=list)
    defined_by_channels: List[str] = Field(default_factory=list)
    display_order: int = 0
    interpretation_short: str = ""


class HDVisualBundle(BaseModel):
    centers: List[HDCenterVisual] = Field(default_factory=list)
    defined_count: int = 0
    open_count: int = 0
    defined_percentage: float = 0.0
    summary: str = ""


def build_hd_visuals(chart) -> HDVisualBundle:
    """
    Build a HDVisualBundle from a HumanDesignChart.
    chart: HumanDesignChart instance (typed as Any to avoid circular import)
    """
    center_map = {c.name: c for c in chart.centers}

    visuals: List[HDCenterVisual] = []
    for order, name in enumerate(_CENTER_ORDER, start=1):
        ci = CENTER_INFO.get(name, {})
        hdc = center_map.get(name)

        is_defined = hdc.is_defined if hdc else False
        active_gates = sorted(hdc.activated_gates) if hdc else []
        defined_by = list(hdc.defined_by_channels) if hdc else []

        if is_defined:
            interp_short = ci.get("defined_interpretation", "")
        else:
            interp_short = ci.get("open_interpretation", "")

        visuals.append(HDCenterVisual(
            center=name,
            center_zh=ci.get("zh", name),
            is_defined=is_defined,
            state_label="已定義" if is_defined else "開放",
            theme=ci.get("theme", ""),
            active_gates=active_gates,
            defined_by_channels=defined_by,
            display_order=order,
            interpretation_short=interp_short,
        ))

    defined_count = sum(1 for v in visuals if v.is_defined)
    open_count = 9 - defined_count
    defined_pct = round(defined_count / 9 * 100, 1)

    if defined_count == 0:
        summary = (
            "此圖所有 9 個中心皆為開放狀態，這是反映者（Reflector）的特徵。"
            "開放中心並非缺陷，而是高度感知環境能量的天賦。"
            "建議在支持性環境中生活，並練習辨識哪些感受來自外界而非本身。"
        )
    elif defined_count == 9:
        summary = (
            "此圖所有 9 個中心皆已定義，能量輸出高度一致穩定。"
            "已定義中心代表穩定的能量模式，但也可能在互動中對他人產生較強影響。"
            "建議注意與開放中心他人的互動彈性。"
        )
    else:
        summary = (
            f"此圖有 {defined_count} 個已定義中心與 {open_count} 個開放中心。"
            "已定義中心代表較穩定的能量運作方式，是你一致對外輸出的特質；"
            "開放中心代表容易接收與放大環境能量，同時也是學習與成長的區域。"
            "兩者沒有優劣之分，都是完整人類圖的組成部分。"
        )

    return HDVisualBundle(
        centers=visuals,
        defined_count=defined_count,
        open_count=open_count,
        defined_percentage=defined_pct,
        summary=summary,
    )


def render_centers_markdown_table(bundle: HDVisualBundle) -> str:
    """Render centers as a Markdown table."""
    lines = [
        "| 中心 | 狀態 | 主題 | 啟動閘門 | 定義通道 | 簡短解讀 |",
        "|------|------|------|----------|----------|----------|",
    ]
    for v in bundle.centers:
        gates_str = ", ".join(str(g) for g in v.active_gates) if v.active_gates else "─"
        channels_str = ", ".join(v.defined_by_channels) if v.defined_by_channels else "─"
        interp = v.interpretation_short.replace("|", "｜")
        lines.append(
            f"| {v.center_zh}（{v.center}）| {v.state_label} | {v.theme} "
            f"| {gates_str} | {channels_str} | {interp} |"
        )
    return "\n".join(lines)


def render_centers_html(bundle: HDVisualBundle) -> str:
    """Render centers as a self-contained HTML table (no JS / CDN)."""
    rows = []
    for v in bundle.centers:
        css_class = "hd-defined" if v.is_defined else "hd-open"
        gates_str = ", ".join(str(g) for g in v.active_gates) if v.active_gates else "─"
        channels_str = ", ".join(v.defined_by_channels) if v.defined_by_channels else "─"
        rows.append(
            f'<tr class="{css_class}">'
            f'<td><strong>{v.center_zh}</strong><br><small>{v.center}</small></td>'
            f'<td><span class="hd-badge-{("defined" if v.is_defined else "open")}">{v.state_label}</span></td>'
            f'<td>{v.theme}</td>'
            f'<td>{gates_str}</td>'
            f'<td>{channels_str}</td>'
            f'<td>{v.interpretation_short}</td>'
            f'</tr>'
        )

    style = (
        '<style>'
        '.hd-centers-table { border-collapse: collapse; width: 100%; margin: 16px 0; }'
        '.hd-centers-table th, .hd-centers-table td { border: 1px solid #d4c5b0; padding: 8px 12px; text-align: left; }'
        '.hd-centers-table th { background: #f0e8d8; font-weight: bold; }'
        '.hd-defined { background: #eef7ee; }'
        '.hd-open { background: #f9f9f9; }'
        '.hd-badge-defined { background: #4caf50; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; }'
        '.hd-badge-open { background: #9e9e9e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; }'
        '</style>'
    )

    header = (
        '<tr>'
        '<th>中心</th><th>狀態</th><th>主題</th>'
        '<th>啟動閘門</th><th>定義通道</th><th>簡短解讀</th>'
        '</tr>'
    )

    return (
        style
        + f'<table class="hd-centers-table">{header}'
        + "".join(rows)
        + '</table>'
    )
