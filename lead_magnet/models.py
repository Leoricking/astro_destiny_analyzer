"""
V1.9.6 Lead Magnet — Data Models.
"""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

FREE_REPORT_TYPES = {
    "zodiac_free_summary",
    "human_design_free_summary",
    "compatibility_free_summary",
    "integrated_free_summary",
}


class LeadProfile(BaseModel):
    name: str = ""
    email: str = ""
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_location: str = ""
    birth_country: str = "台灣"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: str = "Asia/Taipei"


class PartnerProfile(BaseModel):
    name: str = ""
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_location: str = ""
    birth_country: str = "台灣"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: str = "Asia/Taipei"


class LeadCapture(BaseModel):
    lead_id: str = ""
    profile: LeadProfile = Field(default_factory=LeadProfile)
    partner: Optional[PartnerProfile] = None
    report_type: str = "zodiac_free_summary"
    source_page_slug: str = ""
    consent_given: bool = False
    marketing_consent: bool = False
    created_at: str = ""
    tags: List[str] = Field(default_factory=list)
    notes: str = ""


class FreeReportSection(BaseModel):
    heading: str = ""
    body: str = ""
    bullets: List[str] = Field(default_factory=list)


class FreeReportResult(BaseModel):
    lead_id: str = ""
    report_type: str = ""
    title: str = ""
    summary: str = ""
    sections: List[FreeReportSection] = Field(default_factory=list)
    cta_title: str = ""
    cta_description: str = ""
    cta_button_label: str = ""
    cta_target: str = ""
    disclaimer: str = (
        "本報告為免費初步摘要，僅供探索參考，不構成命運斷語或生活決策依據。"
        "完整整合命盤報告包含更詳細的多系統解讀。"
    )
    generated_at: str = ""


class LeadStorageSnapshot(BaseModel):
    version: str = "1.9.6"
    leads: List[LeadCapture] = Field(default_factory=list)
    updated_at: str = ""
