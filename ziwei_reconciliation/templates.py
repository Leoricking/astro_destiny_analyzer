"""
Markdown report templates for Zi Wei Reconciliation (V1.7.3).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ziwei_reconciliation.models import ZiWeiReconciliationReport

from ziwei_reconciliation.models import STATUS_ZH, SEVERITY_ZH, OVERALL_STATUS_ZH


def render_reconciliation_markdown(report: "ZiWeiReconciliationReport") -> str:
    """Render a full Markdown report from a ZiWeiReconciliationReport."""
    from config import APP_VERSION

    lines: list[str] = []

    # 1. Title
    lines.append("# 紫微外部排盤校準報告\n")

    # 2. Source / meta
    lines.append("## 來源資訊\n")
    lines.append(f"| 項目 | 內容 |")
    lines.append(f"|------|------|")
    lines.append(f"| 本機系統版本 | V{APP_VERSION} |")
    lines.append(f"| 外部資料來源 | {report.source_name} |")
    lines.append(f"| 產生時間 | {report.created_at} |")
    lines.append("")

    # 3. Summary counts
    overall_zh = OVERALL_STATUS_ZH.get(report.overall_status, report.overall_status)
    lines.append("## 總覽\n")
    lines.append(f"**整體狀態：{overall_zh}**\n")
    lines.append(f"| 一致 | 不一致 | 尚未實作 | 可能流派差異 |")
    lines.append(f"|------|--------|----------|--------------|")
    lines.append(
        f"| {report.match_count} | {report.mismatch_count} "
        f"| {report.not_implemented_count} | {report.school_difference_count} |"
    )
    lines.append("")
    lines.append(f"**摘要：** {report.summary}\n")

    # 4. Matching items (important ones)
    match_items = [i for i in report.items if i.status == "match"]
    if match_items:
        lines.append("## 核心一致項\n")
        lines.append("| 類別 | 項目 | 本機 | 外部 |")
        lines.append("|------|------|------|------|")
        for i in match_items:
            lines.append(f"| {i.category} | {i.field_name} | {i.local_value} | {i.external_value} |")
        lines.append("")

    # 5. Mismatches (medium/high)
    mismatch_items = [
        i for i in report.items
        if i.status == "mismatch" and i.severity in ("medium", "high")
    ]
    if mismatch_items:
        lines.append("## 主要差異項\n")
        lines.append("| 類別 | 項目 | 本機 | 外部 | 嚴重度 | 說明 |")
        lines.append("|------|------|------|------|--------|------|")
        for i in mismatch_items:
            sev_zh = SEVERITY_ZH.get(i.severity, i.severity)
            lines.append(
                f"| {i.category} | {i.field_name} | {i.local_value} "
                f"| {i.external_value} | {sev_zh} | {i.explanation} |"
            )
        lines.append("")

    # 6. School differences
    school_items = [i for i in report.items if i.status == "likely_school_difference"]
    if school_items:
        lines.append("## 可能流派差異\n")
        lines.append("| 類別 | 項目 | 本機 | 外部 | 說明 |")
        lines.append("|------|------|------|------|------|")
        for i in school_items:
            lines.append(
                f"| {i.category} | {i.field_name} | {i.local_value} "
                f"| {i.external_value} | {i.explanation} |"
            )
        lines.append("")

    # 7. Not implemented
    not_impl_items = [i for i in report.items if i.status == "not_implemented"]
    if not_impl_items:
        lines.append("## 尚未實作項\n")
        lines.append(
            "> 以下項目（好運指數、廟旺陷、命主身主、完整小限）屬外部網站自家功能或"
            " V1.7.3 後續開發項，不代表本機排盤有誤。\n"
        )
        lines.append("| 類別 | 項目 | 外部值 | 說明 |")
        lines.append("|------|------|--------|------|")
        for i in not_impl_items:
            lines.append(
                f"| {i.category} | {i.field_name} | {i.external_value} | {i.explanation} |"
            )
        lines.append("")

    # 8. Full comparison table
    lines.append("## 詳細對照表\n")
    lines.append("| 類別 | 項目 | 本機結果 | 外部結果 | 狀態 | 嚴重度 | 說明 |")
    lines.append("|------|------|----------|----------|------|--------|------|")
    for i in report.items:
        status_zh = STATUS_ZH.get(i.status, i.status)
        sev_zh = SEVERITY_ZH.get(i.severity, i.severity)
        lines.append(
            f"| {i.category} | {i.field_name} | {i.local_value} "
            f"| {i.external_value} | {status_zh} | {sev_zh} | {i.explanation} |"
        )
    lines.append("")

    # 9. Recommendation
    lines.append("## 建議\n")
    for rec in report.recommendation.split(". "):
        rec = rec.strip()
        if rec:
            lines.append(f"- {rec}")
    lines.append("")

    lines.append(
        "> 報告由 Astro Destiny Analyzer 紫微外部排盤校準工具產生。"
        " 流派差異與尚未實作項不代表本機排盤錯誤。"
    )

    return "\n".join(lines)
