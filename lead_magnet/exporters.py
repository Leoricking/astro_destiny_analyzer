"""
V1.9.6 Lead Magnet — Exporters.
"""
from __future__ import annotations
import re
from datetime import date
from lead_magnet.models import FreeReportResult, LeadStorageSnapshot
from lead_magnet.templates import render_free_report_markdown, render_free_report_html
from lead_magnet.storage import export_leads_csv as _csv

_ILLEGAL_CHARS = re.compile(r'[\\/:*?"<>|]')
_EMOJI = re.compile(
    r"[\U00010000-\U0010ffff\U0001F300-\U0001F9FF\U00002600-\U000027BF"
    r"\U0000FE00-\U0000FE0F\U00020000-\U0002A6DF\u2600-\u27BF]",
    flags=re.UNICODE,
)


def safe_free_report_filename(name: str, report_type: str, suffix: str) -> str:
    """Return a safe filename: free_report_{report_type}_{safe_name}_{YYYYMMDD}.{suffix}"""
    clean_name = _EMOJI.sub("", name)
    clean_name = _ILLEGAL_CHARS.sub("", clean_name)
    clean_name = clean_name.strip().replace(" ", "_")[:30]
    clean_rt = _EMOJI.sub("", report_type)
    clean_rt = _ILLEGAL_CHARS.sub("", clean_rt).strip()
    today = date.today().strftime("%Y%m%d")
    ext = suffix.lstrip(".")
    parts = ["free_report", clean_rt]
    if clean_name:
        parts.append(clean_name)
    parts.append(today)
    return "_".join(parts) + f".{ext}"


def export_free_report_markdown(result: FreeReportResult) -> str:
    return render_free_report_markdown(result)


def export_free_report_html(result: FreeReportResult) -> str:
    return render_free_report_html(result)


def export_leads_csv(snapshot: LeadStorageSnapshot) -> str:
    return _csv(snapshot)
