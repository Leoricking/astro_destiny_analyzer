"""
Astro Destiny Analyzer — Human Design Calibration Exporters (V1.9.4)

Export reconciliation reports and batch summaries in Markdown, HTML, and JSON.
"""
from __future__ import annotations

import re
from datetime import date
from typing import Optional

from human_design_reconciliation.models import HDReconciliationReport, BatchReconciliationSummary
from human_design_reconciliation.templates import render_reconciliation_markdown
from human_design_reconciliation.dataset import dataset_to_json


# ── Single report export ──────────────────────────────────────────────────────

def export_reconciliation_markdown(report: HDReconciliationReport) -> str:
    """Export a single reconciliation report as Markdown."""
    return render_reconciliation_markdown(report)


def export_reconciliation_html(markdown_text: str) -> str:
    """
    Wrap a Markdown string in a minimal HTML document.
    No JS, no CDN. Simple inline CSS only.
    """
    # Minimal markdown-to-HTML: convert headings, bold, bullet points
    html_body = _md_to_html(markdown_text)

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Human Design Calibration Report</title>
<style>
  body {{ font-family: Arial, "Microsoft JhengHei", sans-serif; max-width: 900px; margin: 2em auto; padding: 0 1em; color: #222; }}
  h1 {{ color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 0.3em; }}
  h2 {{ color: #34495e; border-bottom: 1px solid #ccc; padding-bottom: 0.2em; }}
  h3 {{ color: #555; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
  th, td {{ border: 1px solid #ccc; padding: 0.4em 0.7em; text-align: left; }}
  th {{ background: #f4f4f4; }}
  blockquote {{ border-left: 4px solid #ccc; margin-left: 0; padding-left: 1em; color: #555; }}
  code {{ background: #f4f4f4; padding: 0.1em 0.3em; border-radius: 3px; }}
  hr {{ border: none; border-top: 1px solid #ddd; margin: 1.5em 0; }}
  .footer {{ font-size: 0.85em; color: #888; border-top: 1px solid #ddd; margin-top: 2em; padding-top: 0.5em; }}
</style>
</head>
<body>
{html_body}
<div class="footer">Astro Destiny Analyzer &middot; Human Design Calibration</div>
</body>
</html>"""


def _md_to_html(text: str) -> str:
    """Minimal Markdown to HTML converter (no external dependencies)."""
    lines = text.splitlines()
    out = []
    in_table = False
    in_blockquote = False

    for line in lines:
        # Horizontal rule
        if re.match(r"^-{3,}$", line.strip()):
            if in_blockquote:
                out.append("</blockquote>")
                in_blockquote = False
            out.append("<hr>")
            continue

        # Blockquote
        if line.startswith("> "):
            if not in_blockquote:
                out.append("<blockquote>")
                in_blockquote = True
            out.append(f"<p>{_inline_md(line[2:])}</p>")
            continue
        elif in_blockquote and not line.startswith(">"):
            out.append("</blockquote>")
            in_blockquote = False

        # Table row
        if "|" in line and line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            # Skip separator row
            if all(re.match(r"^[-:]+$", c.replace(" ", "")) for c in cells if c):
                if not in_table:
                    out.append("<table>")
                    in_table = True
                continue
            if not in_table:
                out.append("<table>")
                in_table = True
                row = "".join(f"<th>{_inline_md(c)}</th>" for c in cells)
            else:
                row = "".join(f"<td>{_inline_md(c)}</td>" for c in cells)
            out.append(f"<tr>{row}</tr>")
            continue
        elif in_table:
            out.append("</table>")
            in_table = False

        # Headings
        m = re.match(r"^(#{1,3})\s+(.*)", line)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline_md(m.group(2))}</h{level}>")
            continue

        # Bullet list
        m = re.match(r"^[-*]\s+(.*)", line)
        if m:
            out.append(f"<p>&bull; {_inline_md(m.group(1))}</p>")
            continue

        # Sub-bullet
        m = re.match(r"^\s{2,}[-*]\s+(.*)", line)
        if m:
            out.append(f"<p>&nbsp;&nbsp;&bull; {_inline_md(m.group(1))}</p>")
            continue

        # Empty line
        if not line.strip():
            out.append("")
            continue

        # Paragraph
        out.append(f"<p>{_inline_md(line)}</p>")

    if in_table:
        out.append("</table>")
    if in_blockquote:
        out.append("</blockquote>")

    return "\n".join(out)


def _inline_md(text: str) -> str:
    """Convert inline Markdown (bold, italic, code) to HTML."""
    # Bold **text**
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic *text*
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Inline code `text`
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text


# ── Batch summary export ──────────────────────────────────────────────────────

def export_batch_summary_markdown(summary: BatchReconciliationSummary) -> str:
    """Export a BatchReconciliationSummary as a Markdown string."""
    lines = [
        "# 人類圖多案例校準摘要",
        "",
        "> 此報告為開發者工具輸出，不應直接提供給客戶。",
        "",
        "---",
        "",
        "## Dataset 概覽",
        "",
        f"| 項目 | 數量 |",
        f"|------|------|",
        f"| 案例總數 | {summary.total_cases} |",
        f"| 已處理 | {summary.processed_cases} |",
        f"| 外部資料不足 | {summary.insufficient_data_count} |",
        "",
        "## 案例狀態分布",
        "",
        f"| 狀態 | 案例數 |",
        f"|------|--------|",
        f"| ✅ 大致一致 | {summary.mostly_match_count} |",
        f"| ⚠️ 輕微差異 | {summary.minor_difference_count} |",
        f"| ❌ 重大差異 | {summary.major_difference_count} |",
        f"| ⬜ 資料不足 | {summary.insufficient_data_count} |",
        "",
        "## 比對項目統計",
        "",
        f"| 類型 | 數量 |",
        f"|------|------|",
        f"| ✅ 一致 | {summary.total_match_items} |",
        f"| ❌ 不一致 | {summary.total_mismatch_items} |",
        f"| 🏫 方法差異 | {summary.total_method_difference_items} |",
        "",
    ]

    if summary.most_common_mismatch_categories:
        lines += [
            "## 最常見差異類別",
            "",
        ]
        for cat in summary.most_common_mismatch_categories:
            lines.append(f"- {cat}")
        lines.append("")

    if summary.design_date_method_notes:
        lines += [
            "## Design Date Method 發現",
            "",
        ]
        for note in summary.design_date_method_notes:
            lines.append(f"- {note}")
        lines.append("")

    if summary.gate_offset_notes:
        lines += [
            "## Gate Wheel Offset 發現",
            "",
        ]
        for note in summary.gate_offset_notes:
            lines.append(f"- {note}")
        lines.append("")

    # Per-case summary table
    if summary.case_reports:
        lines += [
            "## 逐案摘要",
            "",
            "| # | 整體狀態 | 一致 | 不一致 | 方法差異 |",
            "|---|----------|------|--------|----------|",
        ]
        for i, report in enumerate(summary.case_reports, start=1):
            from human_design_reconciliation.models import OVERALL_STATUS_ZH
            status_zh = OVERALL_STATUS_ZH.get(report.overall_status, report.overall_status)
            lines.append(
                f"| {i} | {status_zh} | {report.match_count} | "
                f"{report.mismatch_count} | {report.method_difference_count} |"
            )
        lines.append("")

    # Next actions
    all_actions: list[str] = []
    for report in summary.case_reports:
        for action in report.next_actions:
            if action not in all_actions:
                all_actions.append(action)

    if all_actions:
        lines += [
            "## 下一步建議（彙整）",
            "",
        ]
        for action in all_actions[:10]:  # cap at 10
            lines.append(f"- {action}")
        lines.append("")

    if summary.summary:
        lines += [
            "## 摘要",
            "",
            summary.summary,
            "",
        ]

    lines += [
        "---",
        "",
        "> **聲明**：此批次校準摘要為 V1.9.4 開發者工具輸出，僅供內部診斷使用。",
        "> 差異需人工審核。本工具不自動修正核心演算法。",
    ]

    return "\n".join(lines)


# ── Dataset JSON export ───────────────────────────────────────────────────────

def export_dataset_json(dataset) -> str:
    """Export a HumanDesignCalibrationDataset as a JSON string."""
    return dataset_to_json(dataset)


# ── Filename helper ───────────────────────────────────────────────────────────

_ILLEGAL_CHARS = re.compile(r'[\\/:*?"<>|\x00-\x1f]')
_EMOJI = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)


def safe_calibration_filename(label: str, suffix: str) -> str:
    """
    Generate a safe filename for calibration export.
    Format: human_design_calibration_{label}_{YYYYMMDD}.{suffix}
    Strips illegal chars and emoji from label.
    """
    clean = _EMOJI.sub("", label)
    clean = _ILLEGAL_CHARS.sub("_", clean)
    clean = re.sub(r"\s+", "_", clean.strip())
    clean = re.sub(r"_+", "_", clean).strip("_")
    clean = clean[:40] if clean else "export"
    today = date.today().strftime("%Y%m%d")
    ext = suffix.lstrip(".")
    return f"human_design_calibration_{clean}_{today}.{ext}"
