"""
V1.9.8 Consultant Workflow — Business Logic Engine.
"""
from __future__ import annotations
from datetime import date
from typing import Optional

from consultant_workflow.models import (
    ClientCase, ClientProfile, ClientCaseSnapshot,
)


_REPORT_TYPE_MAP: dict[str, list[str]] = {
    "zodiac_free_summary": ["natal", "integrated"],
    "human_design_free_summary": ["human_design"],
    "compatibility_free_summary": ["compatibility"],
    "integrated_free_summary": ["integrated"],
}

_NEXT_ACTION_TEMPLATES: dict[str, str] = {
    "new_lead": "聯繫客戶確認需求與出生資料。",
    "contacted": "補齊出生日期、時間、城市等完整資料。",
    "data_collected": "產生報告草稿，選擇分析主題。",
    "report_generated": "人工校對報告內容，確認品質。",
    "delivered": "安排 follow-up，確認客戶是否有疑問。",
    "follow_up": "完成回訪，決定是否結案或繼續服務。",
    "closed": "",
}


def create_case_from_lead(lead) -> ClientCase:
    """
    Build a ClientCase from a LeadCapture object.

    lead: lead_magnet.models.LeadCapture
    """
    birth_country = (
        getattr(lead.profile, "birth_country", None) or "台灣"
    )
    requested = _REPORT_TYPE_MAP.get(lead.report_type, ["integrated"])

    client = ClientProfile(
        name=lead.profile.name,
        email=lead.profile.email,
        birth_date=lead.profile.birth_date or "",
        birth_time=lead.profile.birth_time or "",
        birth_country=birth_country,
        birth_city=lead.profile.birth_location or "",
        source=lead.source_page_slug or "lead_magnet",
    )

    return ClientCase(
        client=client,
        case_status="new_lead",
        report_status="not_started",
        requested_report_types=requested,
        source_lead_id=lead.lead_id,
        source_page_slug=lead.source_page_slug,
        next_action="Contact client and confirm birth data.",
        tags=["from_lead"],
    )


def suggest_next_action(case: ClientCase) -> str:
    return _NEXT_ACTION_TEMPLATES.get(case.case_status, "")


def summarize_case(case: ClientCase) -> str:
    lines = [
        f"個案 ID: {case.case_id}",
        f"客戶: {case.client.name} ({case.client.email})",
        f"個案狀態: {case.case_status}",
        f"報告狀態: {case.report_status}",
        f"申請報告: {', '.join(case.requested_report_types) or '未指定'}",
        f"備註數: {len(case.notes)}",
        f"待辦數: {len(case.tasks)}",
        f"交付記錄: {len(case.deliveries)}",
        f"下一步: {case.next_action or suggest_next_action(case)}",
    ]
    return "\n".join(lines)


def compute_case_metrics(snapshot: ClientCaseSnapshot) -> dict:
    cases = snapshot.cases
    total = len(cases)

    by_case_status: dict[str, int] = {}
    by_report_status: dict[str, int] = {}
    open_tasks = 0
    overdue_tasks = 0
    delivered_count = 0
    follow_up_count = 0
    today_str = date.today().isoformat()

    for c in cases:
        by_case_status[c.case_status] = by_case_status.get(c.case_status, 0) + 1
        by_report_status[c.report_status] = by_report_status.get(c.report_status, 0) + 1
        if c.case_status == "delivered":
            delivered_count += 1
        if c.case_status == "follow_up":
            follow_up_count += 1
        for t in c.tasks:
            if t.status not in ("done", "canceled"):
                open_tasks += 1
                if t.due_date and t.due_date < today_str:
                    overdue_tasks += 1

    return {
        "total": total,
        "by_case_status": by_case_status,
        "by_report_status": by_report_status,
        "open_tasks": open_tasks,
        "overdue_tasks": overdue_tasks,
        "delivered_count": delivered_count,
        "follow_up_count": follow_up_count,
    }


def filter_cases(
    snapshot: ClientCaseSnapshot,
    status: Optional[str] = None,
    report_type: Optional[str] = None,
    keyword: Optional[str] = None,
) -> list[ClientCase]:
    results = snapshot.cases
    if status:
        results = [c for c in results if c.case_status == status]
    if report_type:
        results = [c for c in results if report_type in c.requested_report_types]
    if keyword:
        kw = keyword.lower()
        results = [
            c for c in results
            if kw in c.client.name.lower()
            or kw in c.client.email.lower()
            or kw in c.case_id.lower()
            or kw in c.next_action.lower()
        ]
    return results
