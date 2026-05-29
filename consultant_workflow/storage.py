"""
V1.9.8 Consultant Workflow — Local JSON Storage.
"""
from __future__ import annotations
import csv
import io
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from consultant_workflow.models import (
    ClientCase, ClientCaseSnapshot, CaseNote, CaseTask, ReportDelivery,
)

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as _cfg

_DEFAULT_PATH = _cfg.CLIENT_CASE_STORAGE_PATH


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _short_hash(text: str, length: int = 6) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:length]


def make_case_id(name: str, email: str = "") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    safe_name = name.strip()[:10].replace(" ", "_") if name.strip() else "noname"
    h = _short_hash(f"{name}{email}{ts}")
    return f"case_{ts}_{safe_name}_{h}"


def make_note_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"note_{ts}"


def make_task_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"task_{ts}"


def make_delivery_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"del_{ts}"


def load_cases(path=None) -> ClientCaseSnapshot:
    if path is None:
        path = _DEFAULT_PATH
    path = Path(path)
    if not path.exists():
        return ClientCaseSnapshot()
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return ClientCaseSnapshot()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"client_cases.json is malformed: {e}") from e
    return ClientCaseSnapshot.model_validate(data)


def save_cases(snapshot: ClientCaseSnapshot, path=None) -> None:
    if path is None:
        path = _DEFAULT_PATH
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    snapshot.updated_at = _now_iso()
    path.write_text(
        snapshot.model_dump_json(indent=2),
        encoding="utf-8",
    )


def append_case(case: ClientCase, path=None) -> ClientCase:
    if path is None:
        path = _DEFAULT_PATH
    now = _now_iso()
    if not case.case_id:
        case.case_id = make_case_id(case.client.name, case.client.email)
    if not case.created_at:
        case.created_at = now
    case.updated_at = now
    if not case.client.birth_country:
        case.client.birth_country = "台灣"
    snapshot = load_cases(path)
    snapshot.cases.append(case)
    save_cases(snapshot, path)
    return case


def update_case(case_id: str, updated_case: ClientCase, path=None) -> ClientCaseSnapshot:
    if path is None:
        path = _DEFAULT_PATH
    snapshot = load_cases(path)
    for i, c in enumerate(snapshot.cases):
        if c.case_id == case_id:
            updated_case.updated_at = _now_iso()
            snapshot.cases[i] = updated_case
            save_cases(snapshot, path)
            return snapshot
    raise ValueError(f"Case '{case_id}' not found.")


def get_case(case_id: str, path=None) -> Optional[ClientCase]:
    if path is None:
        path = _DEFAULT_PATH
    snapshot = load_cases(path)
    for c in snapshot.cases:
        if c.case_id == case_id:
            return c
    return None


def add_note(case_id: str, note: CaseNote, path=None) -> ClientCase:
    if path is None:
        path = _DEFAULT_PATH
    snapshot = load_cases(path)
    for i, c in enumerate(snapshot.cases):
        if c.case_id == case_id:
            if not note.note_id:
                note.note_id = make_note_id()
            if not note.created_at:
                note.created_at = _now_iso()
            snapshot.cases[i].notes.append(note)
            snapshot.cases[i].updated_at = _now_iso()
            save_cases(snapshot, path)
            return snapshot.cases[i]
    raise ValueError(f"Case '{case_id}' not found.")


def add_task(case_id: str, task: CaseTask, path=None) -> ClientCase:
    if path is None:
        path = _DEFAULT_PATH
    snapshot = load_cases(path)
    for i, c in enumerate(snapshot.cases):
        if c.case_id == case_id:
            if not task.task_id:
                task.task_id = make_task_id()
            if not task.created_at:
                task.created_at = _now_iso()
            snapshot.cases[i].tasks.append(task)
            snapshot.cases[i].updated_at = _now_iso()
            save_cases(snapshot, path)
            return snapshot.cases[i]
    raise ValueError(f"Case '{case_id}' not found.")


def update_task_status(case_id: str, task_id: str, status: str, path=None) -> ClientCase:
    if path is None:
        path = _DEFAULT_PATH
    snapshot = load_cases(path)
    for i, c in enumerate(snapshot.cases):
        if c.case_id == case_id:
            for j, t in enumerate(c.tasks):
                if t.task_id == task_id:
                    snapshot.cases[i].tasks[j].status = status
                    if status == "done" and not snapshot.cases[i].tasks[j].completed_at:
                        snapshot.cases[i].tasks[j].completed_at = _now_iso()
                    snapshot.cases[i].updated_at = _now_iso()
                    save_cases(snapshot, path)
                    return snapshot.cases[i]
            raise ValueError(f"Task '{task_id}' not found in case '{case_id}'.")
    raise ValueError(f"Case '{case_id}' not found.")


def add_delivery(case_id: str, delivery: ReportDelivery, path=None) -> ClientCase:
    if path is None:
        path = _DEFAULT_PATH
    snapshot = load_cases(path)
    for i, c in enumerate(snapshot.cases):
        if c.case_id == case_id:
            if not delivery.delivery_id:
                delivery.delivery_id = make_delivery_id()
            if not delivery.delivered_at:
                delivery.delivered_at = _now_iso()
            snapshot.cases[i].deliveries.append(delivery)
            snapshot.cases[i].updated_at = _now_iso()
            save_cases(snapshot, path)
            return snapshot.cases[i]
    raise ValueError(f"Case '{case_id}' not found.")


def export_cases_csv(snapshot: ClientCaseSnapshot) -> str:
    """Export case list as CSV. Excludes birth_time, lat/lon, notes content."""
    buf = io.StringIO()
    fieldnames = [
        "case_id", "client_name", "client_email",
        "case_status", "report_status",
        "requested_report_types",
        "source_lead_id", "source_page_slug",
        "created_at", "updated_at",
        "next_action", "next_action_due",
    ]
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for c in snapshot.cases:
        writer.writerow({
            "case_id": c.case_id,
            "client_name": c.client.name,
            "client_email": c.client.email,
            "case_status": c.case_status,
            "report_status": c.report_status,
            "requested_report_types": "|".join(c.requested_report_types),
            "source_lead_id": c.source_lead_id,
            "source_page_slug": c.source_page_slug,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
            "next_action": c.next_action,
            "next_action_due": c.next_action_due,
        })
    return buf.getvalue()


def delete_all_cases(path=None) -> None:
    if path is None:
        path = _DEFAULT_PATH
    path = Path(path)
    empty = ClientCaseSnapshot()
    save_cases(empty, path)
