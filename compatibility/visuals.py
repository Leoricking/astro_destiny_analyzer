"""
Astro Destiny Analyzer — Relationship Visual Charts
V1.8.2: Build and render visual chart data for compatibility reports.

Provides:
  - build_relationship_visuals(): AdvancedAstrologyCompatibility → RelationshipVisualBundle
  - render_*_markdown_table(): markdown table strings
  - render_visual_bundle_html(): pure HTML section (no JS, no CDN)

Visual data is an observational aid for interaction patterns, NOT an
absolute compatibility score or fate judgment.
"""
from __future__ import annotations

from compatibility.models import (
    AdvancedAstrologyCompatibility,
    RadarChartData, AspectCategoryBarData, AspectBalanceData,
    CompositeDistributionData, RelationshipVisualBundle,
)

# ── Element / modality sets ───────────────────────────────────────────────────

_FIRE_SIGNS    = {"牡羊座", "獅子座", "射手座"}
_EARTH_SIGNS   = {"金牛座", "處女座", "摩羯座"}
_AIR_SIGNS     = {"雙子座", "天秤座", "水瓶座"}
_WATER_SIGNS   = {"巨蟹座", "天蠍座", "雙魚座"}
_CARDINAL_SIGNS = {"牡羊座", "巨蟹座", "天秤座", "摩羯座"}
_FIXED_SIGNS   = {"金牛座", "獅子座", "天蠍座", "水瓶座"}
_MUTABLE_SIGNS = {"雙子座", "處女座", "射手座", "雙魚座"}

_CATEGORY_ORDER = ["emotional", "communication", "attraction", "stability", "growth", "conflict"]
_CATEGORY_ZH_MAP = {
    "emotional":     "情緒連結",
    "communication": "溝通理解",
    "attraction":    "吸引力",
    "stability":     "穩定責任",
    "growth":        "成長推進",
    "conflict":      "衝突張力",
}


# ── Main build function ───────────────────────────────────────────────────────

def build_relationship_visuals(adv: AdvancedAstrologyCompatibility) -> RelationshipVisualBundle:
    """Build RelationshipVisualBundle from AdvancedAstrologyCompatibility."""

    # A. Radar chart data
    sc = adv.advanced_scores
    radar = RadarChartData(
        labels=["情緒連結", "溝通理解", "吸引力", "穩定度", "成長張力", "衝突張力", "長期潛力"],
        values=[
            sc.emotional_bond,
            sc.communication_flow,
            sc.attraction_chemistry,
            sc.stability_potential,
            sc.growth_intensity,
            sc.conflict_intensity,
            sc.long_term_potential,
        ],
        max_value=100,
        title="合盤互動雷達圖",
        description=(
            "衝突張力高代表互動強度與磨合需求，不代表不適合。"
            "各項分數反映互動模式，非絕對優劣評分。"
        ),
    )

    # B. Aspect category bar data
    aspects = adv.synastry_matrix.aspects
    cat_counts: dict[str, int]      = {c: 0 for c in _CATEGORY_ORDER}
    cat_strength_sum: dict[str, int] = {c: 0 for c in _CATEGORY_ORDER}
    for a in aspects:
        cat = a.category if a.category in cat_counts else None
        if cat:
            cat_counts[cat] += 1
            cat_strength_sum[cat] += a.strength

    aspect_categories = AspectCategoryBarData(
        categories=[_CATEGORY_ZH_MAP[c] for c in _CATEGORY_ORDER],
        counts=[cat_counts[c] for c in _CATEGORY_ORDER],
        strengths=[
            round(cat_strength_sum[c] / cat_counts[c]) if cat_counts[c] > 0 else 0
            for c in _CATEGORY_ORDER
        ],
        title="相位分類統計",
        description="各類相位數量與平均強度，反映兩人互動的主要能量分布。",
    )

    # C. Aspect balance (harmony / tension / neutral)
    sm = adv.synastry_matrix
    h_count = len(sm.harmony_aspects)
    t_count = len(sm.tension_aspects)
    total   = len(sm.aspects)
    n_count = max(0, total - h_count - t_count)
    if total > 0:
        h_pct = round(h_count / total * 100, 1)
        t_pct = round(t_count / total * 100, 1)
    else:
        h_pct = 0.0
        t_pct = 0.0

    aspect_balance = AspectBalanceData(
        harmony_count=h_count,
        tension_count=t_count,
        neutral_count=n_count,
        harmony_percentage=h_pct,
        tension_percentage=t_pct,
    )

    # D. Composite distribution (elements + modalities)
    cc = adv.composite_chart
    planets_list = [p.planet for p in cc.planets]
    signs_list   = [p.sign   for p in cc.planets]

    elements:   dict[str, int] = {"火": 0, "土": 0, "風": 0, "水": 0}
    modalities: dict[str, int] = {"基本": 0, "固定": 0, "變動": 0}
    for sign in signs_list:
        if sign in _FIRE_SIGNS:      elements["火"] += 1
        elif sign in _EARTH_SIGNS:   elements["土"] += 1
        elif sign in _AIR_SIGNS:     elements["風"] += 1
        elif sign in _WATER_SIGNS:   elements["水"] += 1
        if sign in _CARDINAL_SIGNS:  modalities["基本"] += 1
        elif sign in _FIXED_SIGNS:   modalities["固定"] += 1
        elif sign in _MUTABLE_SIGNS: modalities["變動"] += 1

    composite_distribution = CompositeDistributionData(
        planets=planets_list,
        signs=signs_list,
        elements=elements,
        modalities=modalities,
        title="Composite Chart 元素分布",
        description="Composite 分布觀察關係本身的共同場域，不代表任何一方個人命盤。",
    )

    # E. Visual summary
    dominant_elem = max(elements, key=lambda k: elements[k]) if any(elements.values()) else "─"
    top_cat_idx   = max(range(len(_CATEGORY_ORDER)), key=lambda i: cat_counts[_CATEGORY_ORDER[i]])
    top_cat_zh    = _CATEGORY_ZH_MAP[_CATEGORY_ORDER[top_cat_idx]]
    top_cat_cnt   = cat_counts[_CATEGORY_ORDER[top_cat_idx]]

    summary_parts = [
        f"這段關係的相位分布以「{top_cat_zh}」最為突出（{top_cat_cnt} 個相位）。",
    ]
    if sc.conflict_intensity >= 65:
        summary_parts.append("衝突張力是互動強度的體現，重點不是避免衝突，而是建立清楚的修復流程。")
    if sc.attraction_chemistry >= 70:
        summary_parts.append("吸引力與化學反應強，關係有自然的磁場張力。")
    if dominant_elem != "─":
        summary_parts.append(f"Composite 行星以{dominant_elem}象為主，提示關係共同場域的氛圍。")
    summary_parts.append("視覺圖表是互動模式的輔助觀察，不是適合度的絕對評分。")

    return RelationshipVisualBundle(
        radar=radar,
        aspect_categories=aspect_categories,
        aspect_balance=aspect_balance,
        composite_distribution=composite_distribution,
        summary="".join(summary_parts),
    )


# ── Markdown render helpers ───────────────────────────────────────────────────

def render_radar_markdown_table(radar: RadarChartData) -> str:
    """Render RadarChartData as a Markdown table with ASCII bar indicators."""
    lines = [f"### {radar.title}", ""]
    if radar.description:
        lines += [f"> {radar.description}", ""]
    lines += ["| 維度 | 分數 | 視覺 |", "|------|------|------|"]
    for label, value in zip(radar.labels, radar.values):
        filled = value // 10
        bar = "█" * filled + "░" * (10 - filled)
        lines.append(f"| {label} | {value} | {bar} |")
    lines.append("")
    return "\n".join(lines)


def render_aspect_category_markdown_table(data: AspectCategoryBarData) -> str:
    """Render AspectCategoryBarData as a Markdown table."""
    lines = [f"### {data.title}", ""]
    if data.description:
        lines += [f"> {data.description}", ""]
    lines += ["| 分類 | 相位數 | 平均強度 |", "|------|--------|----------|"]
    for cat, cnt, str_val in zip(data.categories, data.counts, data.strengths):
        lines.append(f"| {cat} | {cnt} | {str_val} |")
    lines.append("")
    return "\n".join(lines)


def render_aspect_balance_markdown_table(data: AspectBalanceData) -> str:
    """Render AspectBalanceData as a Markdown table."""
    neutral_pct = round(100 - data.harmony_percentage - data.tension_percentage, 1)
    lines = [
        f"### {data.title}", "",
        "| 性質 | 數量 | 比例 |", "|------|------|------|",
        f"| 和諧相位 | {data.harmony_count} | {data.harmony_percentage}% |",
        f"| 張力相位 | {data.tension_count} | {data.tension_percentage}% |",
        f"| 混合 / 其他 | {data.neutral_count} | {neutral_pct}% |",
        "",
    ]
    return "\n".join(lines)


def render_composite_distribution_markdown_table(data: CompositeDistributionData) -> str:
    """Render CompositeDistributionData as Markdown tables."""
    lines = [f"### {data.title}", ""]
    if data.description:
        lines += [f"> {data.description}", ""]
    lines += ["**元素分布：**", "", "| 元素 | 行星數 |", "|------|--------|"]
    for elem, cnt in data.elements.items():
        lines.append(f"| {elem}象 | {cnt} |")
    lines += ["", "**星座模式：**", "", "| 模式 | 行星數 |", "|------|--------|"]
    for mod, cnt in data.modalities.items():
        lines.append(f"| {mod} | {cnt} |")
    lines.append("")
    return "\n".join(lines)


# ── HTML render helpers (no JS, no CDN, offline-safe) ────────────────────────

def render_score_bar_html(label: str, value: int, max_value: int = 100) -> str:
    """Render one score as an HTML table row with a CSS progress bar."""
    pct = min(100, max(0, int(value / max_value * 100)))
    return (
        f'<tr><td style="padding:4px 8px;min-width:110px">{label}</td>'
        f'<td style="padding:4px 8px;width:220px">'
        f'<div style="background:#e0e0e0;border-radius:4px;height:16px">'
        f'<div style="background:#5b8dee;width:{pct}%;height:100%;border-radius:4px"></div>'
        f'</div></td>'
        f'<td style="padding:4px 8px">{value}</td></tr>\n'
    )


def render_visual_bundle_html(bundle: RelationshipVisualBundle) -> str:
    """Render full RelationshipVisualBundle as an HTML section (no JS, no CDN)."""
    r = bundle.radar
    parts = [
        '<div class="visual-bundle" style="font-family:sans-serif;margin:1em 0">',
        f'<h2>{r.title}</h2>',
    ]
    if r.description:
        parts.append(f'<p><em>{r.description}</em></p>')
    parts += [
        '<table style="border-collapse:collapse;width:100%">',
        '<thead><tr><th style="text-align:left;padding:4px 8px">維度</th>'
        '<th style="text-align:left;padding:4px 8px">分佈</th>'
        '<th style="text-align:left;padding:4px 8px">分數</th></tr></thead>',
        '<tbody>',
    ]
    for label, value in zip(r.labels, r.values):
        parts.append(render_score_bar_html(label, value))
    parts += ['</tbody></table>']

    ab = bundle.aspect_balance
    neutral_pct = round(100 - ab.harmony_percentage - ab.tension_percentage, 1)
    parts += [
        f'<h3>{ab.title}</h3>',
        '<table style="border-collapse:collapse;width:100%">',
        '<thead><tr><th style="padding:4px 8px">性質</th>'
        '<th style="padding:4px 8px">數量</th>'
        '<th style="padding:4px 8px">比例</th></tr></thead><tbody>',
        f'<tr><td style="padding:4px 8px">和諧相位</td>'
        f'<td style="padding:4px 8px">{ab.harmony_count}</td>'
        f'<td style="padding:4px 8px">{ab.harmony_percentage}%</td></tr>',
        f'<tr><td style="padding:4px 8px">張力相位</td>'
        f'<td style="padding:4px 8px">{ab.tension_count}</td>'
        f'<td style="padding:4px 8px">{ab.tension_percentage}%</td></tr>',
        f'<tr><td style="padding:4px 8px">混合/其他</td>'
        f'<td style="padding:4px 8px">{ab.neutral_count}</td>'
        f'<td style="padding:4px 8px">{neutral_pct}%</td></tr>',
        '</tbody></table>',
    ]

    ac = bundle.aspect_categories
    parts += [f'<h3>{ac.title}</h3>']
    if ac.description:
        parts.append(f'<p><em>{ac.description}</em></p>')
    parts += [
        '<table style="border-collapse:collapse;width:100%">',
        '<thead><tr><th style="padding:4px 8px">分類</th>'
        '<th style="padding:4px 8px">數量</th>'
        '<th style="padding:4px 8px">平均強度</th></tr></thead><tbody>',
    ]
    for cat, cnt, str_val in zip(ac.categories, ac.counts, ac.strengths):
        parts.append(
            f'<tr><td style="padding:4px 8px">{cat}</td>'
            f'<td style="padding:4px 8px">{cnt}</td>'
            f'<td style="padding:4px 8px">{str_val}</td></tr>'
        )
    parts += ['</tbody></table>']

    cd = bundle.composite_distribution
    parts += [f'<h3>{cd.title}</h3>']
    if cd.description:
        parts.append(f'<p><em>{cd.description}</em></p>')
    parts += [
        '<table style="border-collapse:collapse;width:100%">',
        '<thead><tr><th style="padding:4px 8px">元素</th>'
        '<th style="padding:4px 8px">行星數</th></tr></thead><tbody>',
    ]
    for elem, cnt in cd.elements.items():
        parts.append(
            f'<tr><td style="padding:4px 8px">{elem}象</td>'
            f'<td style="padding:4px 8px">{cnt}</td></tr>'
        )
    parts += [
        '</tbody></table>',
        f'<p style="color:#555;margin-top:1em"><em>{bundle.summary}</em></p>',
        '</div>',
    ]
    return "\n".join(parts)
