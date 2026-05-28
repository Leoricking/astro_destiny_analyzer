"""
Astro Destiny Analyzer — Compatibility Exporters
V1.7.1

Provides HTML and DOCX export for CompatibilityReport.
Reuses _CSS from reports.html_exporter and sanitize_filename from reports.utils.
Does NOT modify existing single-person export paths.
"""
from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

import re as _re
from reports.utils import sanitize_filename

if TYPE_CHECKING:
    from compatibility.models import CompatibilityReport


def _sanitize_compat_name(name: str) -> str:
    """Sanitize a name for use in compatibility export filenames.
    Strips emoji, converts spaces to underscores, removes Windows-illegal chars,
    truncates to 40 chars.
    """
    # Strip emoji and non-printable symbols (Unicode category So/Sm above U+2600)
    cleaned = _re.sub(r'[\U0001F000-\U0001FFFF\U00002600-\U000027FF\U00002B00-\U00002BFF'
                      r'\U0000FE00-\U0000FEFF\U000E0000-\U000E01FF]', '', name)
    # Remove Windows-illegal filename chars
    cleaned = _re.sub(r'[\\/:*?"<>|\r\n\t]', '', cleaned)
    # Replace spaces/hyphens with underscores
    cleaned = _re.sub(r'[\s\-]+', '_', cleaned)
    cleaned = cleaned.strip('_')
    if not cleaned:
        return "person"
    return cleaned[:40]


def make_compat_filename(name_a: str, name_b: str, ext: str, rel_type: str = "") -> str:
    """Build: relationship_report_{safe_a}_{safe_b}_{YYYYMMDD}.{ext}"""
    safe_a = _sanitize_compat_name(name_a)
    safe_b = _sanitize_compat_name(name_b)
    ts = datetime.now().strftime("%Y%m%d")
    return f"relationship_report_{safe_a}_{safe_b}_{ts}.{ext}"


def export_compat_to_html(report: "CompatibilityReport") -> str:
    """
    Export CompatibilityReport to a self-contained HTML string.
    Reuses the CSS from reports.html_exporter.
    """
    from reports.html_exporter import _CSS  # reuse existing CSS constant

    try:
        import markdown as _md_lib
        body_html = _md_lib.markdown(
            report.markdown_body,
            extensions=["tables", "fenced_code"],
        )
    except ImportError:
        # Minimal fallback: wrap paragraphs
        import re
        text = report.markdown_body
        text = re.sub(r"&", "&amp;", text)
        text = re.sub(r"<", "&lt;", text)
        text = re.sub(r">", "&gt;", text)
        text = re.sub(r"\n\n", "</p><p>", text)
        body_html = f"<p>{text}</p>"

    from config import APP_VERSION, BRAND_NAME, REPORT_WATERMARK

    pa = report.person_a_profile
    pb = report.person_b_profile
    from compatibility.models import relationship_label
    rt_label_str = relationship_label(report.relationship_type)
    title_text = f"{pa.name} × {pb.name} {rt_label_str} 合盤分析報告"
    footer_txt = f"{REPORT_WATERMARK} · v{APP_VERSION}"

    html = (
        "<!DOCTYPE html>\n"
        "<html lang=\"zh-Hant\">\n"
        "<head>\n"
        "<meta charset=\"UTF-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        f"<title>{title_text}</title>\n"
        "<style>\n"
        + _CSS + "\n"
        "</style>\n"
        "</head>\n"
        "<body>\n"
        + body_html + "\n"
        f'<div class="footer">{footer_txt}</div>\n'
        "</body>\n"
        "</html>"
    )
    return html


def _docx_available() -> bool:
    try:
        import docx  # noqa: F401
        return True
    except ImportError:
        return False


def export_compat_to_docx(report: "CompatibilityReport") -> bytes:
    """
    Export CompatibilityReport to a Word (.docx) bytes object.
    Raises RuntimeError if python-docx is not installed.
    """
    if not _docx_available():
        raise RuntimeError("Word 匯出需要安裝 python-docx：pip install python-docx")

    from docx import Document  # type: ignore
    from docx.shared import Pt, RGBColor  # type: ignore
    import io

    doc = Document()

    # Title
    title = doc.add_heading("", level=0)
    title_run = title.add_run("關係合盤分析報告")
    title_run.font.size = Pt(24)

    pa = report.person_a_profile
    pb = report.person_b_profile
    doc.add_heading(f"{pa.name} × {pb.name}", level=1)

    from compatibility.models import relationship_label
    info_table = doc.add_table(rows=4, cols=2)
    info_table.style = "Table Grid"
    rows_data = [
        ("關係類型", relationship_label(report.relationship_type)),
        ("A方", f"{pa.name}（{pa.birth_date}，{pa.birth_city}）"),
        ("B方", f"{pb.name}（{pb.birth_date}，{pb.birth_city}）"),
        ("產生時間", report.created_at),
    ]
    for i, (k, v) in enumerate(rows_data):
        info_table.rows[i].cells[0].text = k
        info_table.rows[i].cells[1].text = v
    doc.add_paragraph()

    # Score section
    sc = report.score_breakdown
    doc.add_heading("關係總分", level=2)
    doc.add_paragraph(f"綜合評分：{sc.overall_score}/100 — {sc.score_label()}")
    score_table = doc.add_table(rows=8, cols=2)
    score_table.style = "Table Grid"
    score_data = [
        ("情感共鳴", sc.emotional_score),
        ("溝通契合", sc.communication_score),
        ("吸引力", sc.attraction_score),
        ("穩定性", sc.stability_score),
        ("成長潛力", sc.growth_score),
        ("衝突強度", sc.conflict_score),
        ("協作效能", sc.collaboration_score),
        ("整體評分", sc.overall_score),
    ]
    for i, (k, v) in enumerate(score_data):
        score_table.rows[i].cells[0].text = k
        score_table.rows[i].cells[1].text = str(v)
    doc.add_paragraph()

    # Markdown body as plain paragraphs
    syn = report.synthesis
    doc.add_heading("關係總論", level=2)
    doc.add_paragraph(syn.relationship_summary)

    doc.add_heading("關係優勢", level=2)
    for s in syn.strengths:
        doc.add_paragraph(f"✅ {s}", style="List Bullet")

    doc.add_heading("關係挑戰", level=2)
    for c in syn.challenges:
        doc.add_paragraph(f"⚡ {c}", style="List Bullet")

    doc.add_heading("溝通建議", level=2)
    for i, a in enumerate(syn.practical_advice, 1):
        doc.add_paragraph(f"{i}. {a}")

    doc.add_heading("30 天關係練習", level=2)
    for p in syn.thirty_day_practice:
        doc.add_paragraph(p, style="List Bullet")

    doc.add_heading("長期關係建議", level=2)
    doc.add_paragraph(syn.long_term_potential)

    doc.add_heading("免責聲明", level=2)
    doc.add_paragraph(syn.warning_note)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
