"""
V1.9.8 Consultant Workflow — Exporters.

export_case_markdown / export_case_html / export_cases_csv /
export_case_metrics_markdown / safe_case_filename
"""
from __future__ import annotations
import re
from datetime import date

from consultant_workflow.models import ClientCase, ClientCaseSnapshot
from consultant_workflow.storage import export_cases_csv


def safe_case_filename(label: str, suffix: str) -> str:
    """Return a safe filename like client_case_{label}_{YYYYMMDD}.{suffix}."""
    today = date.today().strftime("%Y%m%d")
    # Remove illegal filesystem chars and emoji (non-ASCII)
    clean = re.sub(r"[^\w\- ]", "", label, flags=re.ASCII)
    clean = clean.strip().replace(" ", "_")
    if not clean:
        clean = "case"
    return f"client_case_{clean}_{today}.{suffix}"


def export_case_markdown(case: ClientCase) -> str:
    lines = [
        f"# Client Case Summary",
        f"",
        f"**Case ID**: {case.case_id}",
        f"",
        f"## Client",
        f"- **Name**: {case.client.name}",
        f"- **Email**: {case.client.email}",
        f"- **Phone**: {case.client.phone or '—'}",
        f"- **Birth Country**: {case.client.birth_country}",
        f"- **Birth City**: {case.client.birth_city or '—'}",
        f"- **Birth Date**: {case.client.birth_date or '—'}",
        f"- **Source**: {case.client.source or '—'}",
        f"",
    ]

    if case.partner:
        lines += [
            f"## Partner",
            f"- **Name**: {case.partner.name}",
            f"- **Birth Country**: {case.partner.birth_country}",
            f"- **Birth City**: {case.partner.birth_city or '—'}",
            f"- **Birth Date**: {case.partner.birth_date or '—'}",
            f"",
        ]

    lines += [
        f"## Case Status",
        f"- **Case Status**: {case.case_status}",
        f"- **Created At**: {case.created_at or '—'}",
        f"- **Updated At**: {case.updated_at or '—'}",
        f"",
        f"## Report Status",
        f"- **Report Status**: {case.report_status}",
        f"",
        f"## Requested Reports",
    ]
    if case.requested_report_types:
        for rt in case.requested_report_types:
            lines.append(f"- {rt}")
    else:
        lines.append("- (none)")
    lines.append("")

    lines += [
        f"## Next Action",
        f"{case.next_action or '—'}",
        f"",
        f"*Due*: {case.next_action_due or '—'}",
        f"",
        f"## Tasks",
    ]
    if case.tasks:
        for t in case.tasks:
            status_mark = "✅" if t.status == "done" else "⬜"
            lines.append(f"- [{status_mark}] **{t.title}** ({t.priority}) — {t.status}"
                         + (f" | Due: {t.due_date}" if t.due_date else ""))
    else:
        lines.append("- (no tasks)")
    lines.append("")

    lines += [f"## Deliveries"]
    if case.deliveries:
        for d in case.deliveries:
            lines.append(f"- {d.report_type} / {d.format} — {d.delivered_at or '—'}"
                         + (f" | {d.delivery_note}" if d.delivery_note else ""))
    else:
        lines.append("- (no deliveries)")
    lines.append("")

    lines += [
        f"## Notes Summary",
        f"> ⚠️ *For developer / consultant internal use only. Not for client delivery.*",
        f"",
    ]
    if case.notes:
        for n in case.notes:
            lines.append(f"- **[{n.note_type}]** {n.created_at or ''} — {n.content[:120]}"
                         + ("…" if len(n.content) > 120 else ""))
    else:
        lines.append("- (no notes)")

    return "\n".join(lines)


def export_case_html(case: ClientCase) -> str:
    md_body = export_case_markdown(case)
    # Basic HTML escaping
    def esc(s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    md_escaped = esc(md_body).replace("\n", "<br>\n")

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Client Case — {esc(case.client.name)}</title>
<style>
  body {{ font-family: sans-serif; max-width: 860px; margin: 40px auto; padding: 0 20px; color: #222; }}
  h1, h2, h3 {{ color: #1a3a5c; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.85em;
            background: #e8f0fe; color: #1a3a5c; margin: 2px; }}
  .internal-note {{ background: #fff8e1; border-left: 4px solid #f9a825; padding: 8px 12px;
                    font-size: 0.9em; margin: 8px 0; }}
  footer {{ margin-top: 40px; font-size: 0.8em; color: #888; border-top: 1px solid #ddd; padding-top: 8px; }}
  pre {{ white-space: pre-wrap; word-break: break-word; }}
</style>
</head>
<body>
<h1>Client Case Summary</h1>
<p><strong>Case ID</strong>: {esc(case.case_id)}</p>
<h2>Client</h2>
<ul>
  <li><strong>Name</strong>: {esc(case.client.name)}</li>
  <li><strong>Email</strong>: {esc(case.client.email)}</li>
  <li><strong>Birth Country</strong>: {esc(case.client.birth_country)}</li>
  <li><strong>Birth City</strong>: {esc(case.client.birth_city or "—")}</li>
  <li><strong>Birth Date</strong>: {esc(case.client.birth_date or "—")}</li>
  <li><strong>Source</strong>: {esc(case.client.source or "—")}</li>
</ul>
<h2>Case Status</h2>
<p><span class="badge">{esc(case.case_status)}</span></p>
<h2>Report Status</h2>
<p><span class="badge">{esc(case.report_status)}</span></p>
<h2>Requested Reports</h2>
<ul>
{"".join(f"  <li>{esc(rt)}</li>" for rt in case.requested_report_types) or "  <li>(none)</li>"}
</ul>
<h2>Next Action</h2>
<p>{esc(case.next_action or "—")}</p>
<h2>Tasks</h2>
<ul>
{"".join(f'  <li>{esc(t.title)} — <span class="badge">{esc(t.status)}</span></li>' for t in case.tasks) or "  <li>(no tasks)</li>"}
</ul>
<h2>Deliveries</h2>
<ul>
{"".join(f'  <li>{esc(d.report_type)}/{esc(d.format)} — {esc(d.delivered_at or "—")}</li>' for d in case.deliveries) or "  <li>(no deliveries)</li>"}
</ul>
<div class="internal-note">
  <strong>⚠️ Notes — Developer / Consultant Internal Only. Not for client delivery.</strong>
</div>
<ul>
{"".join(f'  <li>[{esc(n.note_type)}] {esc(n.content[:120])}</li>' for n in case.notes) or "  <li>(no notes)</li>"}
</ul>
<footer>
  Generated by Astro Destiny Analyzer V1.9.8 — Consultant Internal Document
</footer>
</body>
</html>"""


def export_case_metrics_markdown(metrics: dict) -> str:
    lines = [
        "# Case Metrics",
        "",
        f"- **Total Cases**: {metrics.get('total', 0)}",
        f"- **Open Tasks**: {metrics.get('open_tasks', 0)}",
        f"- **Overdue Tasks**: {metrics.get('overdue_tasks', 0)}",
        f"- **Delivered Cases**: {metrics.get('delivered_count', 0)}",
        f"- **Follow-up Cases**: {metrics.get('follow_up_count', 0)}",
        "",
        "## By Case Status",
    ]
    for k, v in sorted(metrics.get("by_case_status", {}).items()):
        lines.append(f"- {k}: {v}")
    lines += ["", "## By Report Status"]
    for k, v in sorted(metrics.get("by_report_status", {}).items()):
        lines.append(f"- {k}: {v}")
    return "\n".join(lines)
