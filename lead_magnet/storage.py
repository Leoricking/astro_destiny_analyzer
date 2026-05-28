"""
V1.9.6 Lead Magnet — Local JSON Storage.
No data is sent to external services.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

import config as _cfg
from lead_magnet.models import LeadCapture, LeadStorageSnapshot


def validate_email(email: str) -> bool:
    """Basic email validation — no external dependencies."""
    if not email or " " in email:
        return False
    parts = email.split("@")
    if len(parts) != 2:
        return False
    local, domain = parts
    if not local or not domain:
        return False
    if "." not in domain:
        return False
    return True


def make_lead_id(email: str, report_type: str) -> str:
    """Create a lead ID using timestamp + short hash. Does not expose full email."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    raw = f"{email}|{report_type}|{ts}"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:8]
    return f"lead_{ts}_{digest}"


def load_leads(path: Path = None) -> LeadStorageSnapshot:
    """Load leads from local JSON file. Returns empty snapshot if file missing."""
    if path is None:
        path = _cfg.LEAD_STORAGE_PATH
    if not path.exists():
        return LeadStorageSnapshot()
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
        return LeadStorageSnapshot.model_validate(data)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Lead storage JSON is malformed: {exc}") from exc


def save_leads(snapshot: LeadStorageSnapshot, path: Path = None) -> None:
    """Save leads snapshot to local JSON. ensure_ascii=False, indent=2."""
    if path is None:
        path = _cfg.LEAD_STORAGE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    snapshot.updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    path.write_text(
        json.dumps(snapshot.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def append_lead(lead: LeadCapture, path: Path = None) -> LeadCapture:
    """Append a lead to storage. Requires consent_given=True and valid email.
    Marks potential duplicates. Does NOT send data externally."""
    if path is None:
        path = _cfg.LEAD_STORAGE_PATH
    if not lead.consent_given:
        raise ValueError("consent_given must be True before storing a lead.")
    if not validate_email(lead.profile.email):
        raise ValueError(f"Invalid email: {lead.profile.email!r}")
    if not lead.lead_id:
        lead.lead_id = make_lead_id(lead.profile.email, lead.report_type)
    if not lead.created_at:
        lead.created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    snapshot = load_leads(path)

    # Check for duplicate email + report_type
    for existing in snapshot.leads:
        if (
            existing.profile.email == lead.profile.email
            and existing.report_type == lead.report_type
        ):
            if "duplicate_possible" not in lead.tags:
                lead.tags.append("duplicate_possible")
            if not lead.notes:
                lead.notes = "可能重複提交（相同 email 與報告類型）"
            break

    snapshot.leads.append(lead)
    save_leads(snapshot, path)
    return lead


def export_leads_csv(snapshot: LeadStorageSnapshot) -> str:
    """Export leads to CSV string. Excludes sensitive birth details."""
    output = io.StringIO()
    writer = csv.writer(output)
    headers = [
        "lead_id", "name", "email", "report_type", "source_page_slug",
        "created_at", "consent_given", "marketing_consent",
    ]
    writer.writerow(headers)
    for lead in snapshot.leads:
        writer.writerow([
            lead.lead_id,
            lead.profile.name,
            lead.profile.email,
            lead.report_type,
            lead.source_page_slug,
            lead.created_at,
            lead.consent_given,
            lead.marketing_consent,
        ])
    return output.getvalue()


def delete_all_leads(path: Path = None) -> None:
    """Delete all leads. Developer mode only. Requires explicit call."""
    if path is None:
        path = _cfg.LEAD_STORAGE_PATH
    if path.exists():
        path.unlink()
