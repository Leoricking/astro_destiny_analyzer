"""
Astro Destiny Analyzer — Human Design Reconciliation Templates (V1.9.2)

Renders HDReconciliationReport to Markdown.
"""
from __future__ import annotations
from human_design_reconciliation.models import HDReconciliationReport, STATUS_ZH, SEVERITY_ZH, OVERALL_STATUS_ZH


def render_reconciliation_markdown(report: HDReconciliationReport) -> str:
    """Render a HDReconciliationReport as a Markdown string."""
    lines = [
        "# 人類圖外部排盤校準報告",
        "",
        "> **說明**：此報告為開發者校準工具，不應直接提供給客戶。",
        "> 本工具不代表已完成外部校準；需使用者輸入外部資料後才能進行比對。",
        "",
        "---",
        "",
        "## 總覽",
        "",
        f"**整體狀態**：{OVERALL_STATUS_ZH.get(report.overall_status, report.overall_status)}",
        "",
        f"| 比對類型 | 數量 |",
        f"|----------|------|",
        f"| ✅ 一致 | {report.match_count} |",
        f"| ❌ 不一致 | {report.mismatch_count} |",
        f"| 🏫 方法差異 | {report.method_difference_count} |",
        f"| ⬜ 外部未提供 | {report.missing_count} |",
        "",
        f"**摘要**：{report.summary}",
        "",
    ]

    if report.external_source_note:
        lines += [f"**外部資料來源**：{report.external_source_note}", ""]

    if report.local_accuracy_note:
        lines += [f"**本機準確度說明**：{report.local_accuracy_note}", ""]

    lines += ["---", ""]

    # ── Group items by category ────────────────────────────────────────────────
    _CATEGORY_ZH = {
        "type": "類型 Type",
        "strategy": "策略 Strategy",
        "authority": "內在權威 Authority",
        "profile": "人生角色 Profile",
        "incarnation_cross": "輪迴交叉 Incarnation Cross",
        "conscious_planets": "Conscious 行星（意識面）",
        "design_planets": "Design 行星（設計面）",
        "gates": "啟動閘門 Gates",
        "channels": "定義通道 Channels",
        "centers": "定義中心 Centers",
        "validation": "校準資訊",
    }

    _CATEGORY_ORDER = [
        "type", "strategy", "authority", "profile", "incarnation_cross",
        "conscious_planets", "design_planets", "gates", "channels", "centers", "validation",
    ]

    from collections import defaultdict
    grouped = defaultdict(list)
    for item in report.items:
        grouped[item.category].append(item)

    for cat in _CATEGORY_ORDER:
        cat_items = grouped.get(cat)
        if not cat_items:
            continue
        cat_zh = _CATEGORY_ZH.get(cat, cat)
        lines += [f"## {cat_zh}", ""]
        lines += [
            "| 欄位 | 本機值 | 外部值 | 狀態 | 嚴重度 |",
            "|------|--------|--------|------|--------|",
        ]
        for item in cat_items:
            status_zh = STATUS_ZH.get(item.status, item.status)
            severity_zh = SEVERITY_ZH.get(item.severity, item.severity)
            lv = item.local_value.replace("|", "｜")
            ev = item.external_value.replace("|", "｜")
            lines.append(f"| {item.field} | {lv} | {ev} | {status_zh} | {severity_zh} |")

        # Show explanations for non-match items
        notable = [i for i in cat_items if i.status not in ("match", "missing_external")]
        if notable:
            lines.append("")
            for item in notable:
                if item.explanation:
                    lines.append(f"- **{item.field}**：{item.explanation}")
                if item.suggestion:
                    lines.append(f"  - 建議：{item.suggestion}")
        lines += ["", "---", ""]

    # ── Mismatch detail section ────────────────────────────────────────────────
    mismatch_items = [i for i in report.items if i.status == "mismatch"]
    if mismatch_items:
        lines += ["## 差異原因推測", ""]
        for item in mismatch_items:
            lines.append(f"### {item.category} — {item.field}")
            lines.append("")
            lines.append(f"- **本機**：{item.local_value}")
            lines.append(f"- **外部**：{item.external_value}")
            lines.append(f"- **嚴重度**：{SEVERITY_ZH.get(item.severity, item.severity)}")
            if item.explanation:
                lines.append(f"- **推測原因**：{item.explanation}")
            if item.suggestion:
                lines.append(f"- **建議**：{item.suggestion}")
            lines.append("")
        lines += ["---", ""]

    # ── Next actions ──────────────────────────────────────────────────────────
    if report.next_actions:
        lines += ["## 下一步建議", ""]
        for action in report.next_actions:
            lines.append(f"- {action}")
        lines.append("")

    lines += [
        "---",
        "",
        "> **聲明**：此校準報告為 V1.9.2 開發者工具輸出，僅供內部校準與診斷使用。",
        "> 不代表本系統已通過完整外部驗證。",
        "> 如需正式商業人類圖，請參考 Jovian Archive / Genetic Matrix / MyBodyGraph。",
    ]

    return "\n".join(lines)
