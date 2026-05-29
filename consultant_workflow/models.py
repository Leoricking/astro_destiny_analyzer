"""
V1.9.8 Consultant Workflow — Data Models.

ClientProfile / CaseNote / CaseTask / ReportDelivery / ClientCase / ClientCaseSnapshot
"""
from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


CaseStatus = Literal[
    "new_lead",
    "contacted",
    "data_collected",
    "report_generated",
    "delivered",
    "follow_up",
    "closed",
]

CASE_STATUS_VALUES: tuple[str, ...] = (
    "new_lead", "contacted", "data_collected",
    "report_generated", "delivered", "follow_up", "closed",
)

ReportStatus = Literal[
    "not_started",
    "draft",
    "generated",
    "reviewed",
    "delivered",
    "revised",
]

REPORT_STATUS_VALUES: tuple[str, ...] = (
    "not_started", "draft", "generated", "reviewed", "delivered", "revised",
)

NoteType = Literal[
    "general", "consultation", "follow_up", "report_revision", "payment_note",
]

TaskStatus = Literal["todo", "doing", "done", "canceled"]

TaskPriority = Literal["low", "medium", "high"]

DeliveryFormat = Literal["markdown", "html", "docx", "pdf", "consultation"]

ReportType = Literal["natal", "compatibility", "human_design", "integrated", "free_summary"]


class ClientProfile(BaseModel):
    client_id: str = ""
    name: str = ""
    email: str = ""
    phone: str = ""
    birth_date: str = ""
    birth_time: str = ""
    birth_country: str = "台灣"
    birth_city: str = ""
    timezone: str = "Asia/Taipei"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    tags: List[str] = Field(default_factory=list)
    source: str = ""
    created_at: str = ""
    updated_at: str = ""


class CaseNote(BaseModel):
    note_id: str = ""
    created_at: str = ""
    author: str = "consultant"
    note_type: str = "general"
    content: str = ""
    tags: List[str] = Field(default_factory=list)


class CaseTask(BaseModel):
    task_id: str = ""
    title: str = ""
    description: str = ""
    due_date: str = ""
    status: str = "todo"
    priority: str = "medium"
    created_at: str = ""
    completed_at: str = ""


class ReportDelivery(BaseModel):
    delivery_id: str = ""
    report_type: str = ""
    format: str = ""
    file_path: str = ""
    delivered_at: str = ""
    delivery_note: str = ""
    status: str = "delivered"


class ClientCase(BaseModel):
    case_id: str = ""
    client: ClientProfile = Field(default_factory=ClientProfile)
    partner: Optional[ClientProfile] = None
    case_status: str = "new_lead"
    report_status: str = "not_started"
    requested_report_types: List[str] = Field(default_factory=list)
    notes: List[CaseNote] = Field(default_factory=list)
    tasks: List[CaseTask] = Field(default_factory=list)
    deliveries: List[ReportDelivery] = Field(default_factory=list)
    source_lead_id: str = ""
    source_page_slug: str = ""
    created_at: str = ""
    updated_at: str = ""
    next_action: str = ""
    next_action_due: str = ""
    tags: List[str] = Field(default_factory=list)


class ClientCaseSnapshot(BaseModel):
    version: str = "1.9.8"
    cases: List[ClientCase] = Field(default_factory=list)
    updated_at: str = ""
