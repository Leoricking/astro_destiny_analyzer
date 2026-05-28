"""
lead_magnet — V1.9.6 Free Report Lead Magnet & Email Capture Mock.
Local mock only. No data is sent to external services.
"""
from lead_magnet.models import (
    LeadProfile, PartnerProfile, LeadCapture,
    FreeReportResult, FreeReportSection, LeadStorageSnapshot,
    FREE_REPORT_TYPES,
)
from lead_magnet.storage import (
    validate_email, make_lead_id,
    load_leads, save_leads, append_lead,
    export_leads_csv, delete_all_leads,
)
from lead_magnet.engine import generate_free_report
from lead_magnet.templates import (
    render_free_report_markdown, render_free_report_html,
    render_lead_capture_copy, render_upgrade_cta,
)
from lead_magnet.exporters import (
    export_free_report_markdown, export_free_report_html,
    safe_free_report_filename,
)

__all__ = [
    "LeadProfile", "PartnerProfile", "LeadCapture",
    "FreeReportResult", "FreeReportSection", "LeadStorageSnapshot",
    "FREE_REPORT_TYPES",
    "validate_email", "make_lead_id",
    "load_leads", "save_leads", "append_lead",
    "export_leads_csv", "delete_all_leads",
    "generate_free_report",
    "render_free_report_markdown", "render_free_report_html",
    "render_lead_capture_copy", "render_upgrade_cta",
    "export_free_report_markdown", "export_free_report_html",
    "safe_free_report_filename",
]
