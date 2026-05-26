"""
Astro Destiny Analyzer — Word (docx) Exporter
Uses python-docx to produce a structured Word document.
"""
from typing import TYPE_CHECKING
from core.models import FullReport
from reports.templates import render_report
from config import APP_VERSION, APP_NAME


def _docx_available() -> bool:
    try:
        import docx  # noqa: F401
        return True
    except ImportError:
        return False


class DocxExporter:
    def is_available(self) -> bool:
        return _docx_available()

    def export(self, report: FullReport) -> bytes:
        """Export report as .docx bytes."""
        if not self.is_available():
            raise ImportError(
                "python-docx is required. Run: pip install python-docx"
            )
        import docx
        from docx.shared import Pt, RGBColor
        from io import BytesIO

        markdown_text = render_report(report, version=APP_VERSION)
        document = docx.Document()

        # ── Styles ────────────────────────────────────────────────────────────
        style_normal = document.styles["Normal"]
        style_normal.font.name = "Noto Serif TC"
        style_normal.font.size = Pt(11)

        # ── Title ─────────────────────────────────────────────────────────────
        doc_title = document.add_heading(
            f"{report.profile.name} 命盤整合分析報告", level=0
        )

        document.add_paragraph(f"生成時間：{report.created_at}")
        document.add_paragraph(f"系統版本：{APP_NAME} v{APP_VERSION}")
        document.add_page_break()

        # ── Parse Markdown into docx sections ────────────────────────────────
        for line in markdown_text.splitlines():
            if line.startswith("# "):
                document.add_heading(line[2:].strip(), level=1)
            elif line.startswith("## "):
                document.add_heading(line[3:].strip(), level=2)
            elif line.startswith("### "):
                document.add_heading(line[4:].strip(), level=3)
            elif line.startswith("#### "):
                document.add_heading(line[5:].strip(), level=4)
            elif line.startswith("---"):
                document.add_paragraph("─" * 40)
            elif line.startswith("| "):
                # Skip table rows (table rendering requires more complex logic)
                # TODO: implement proper table parsing for docx
                document.add_paragraph(line, style="List Bullet")
            elif line.startswith("- ") or line.startswith("* "):
                document.add_paragraph(line[2:].strip(), style="List Bullet")
            elif line.startswith("> "):
                p = document.add_paragraph(line[2:].strip())
                p.style = document.styles["Quote"] if "Quote" in document.styles else p.style
            elif line.strip():
                document.add_paragraph(line.strip())

        # ── Save to bytes ─────────────────────────────────────────────────────
        buf = BytesIO()
        document.save(buf)
        return buf.getvalue()

    def save(self, report: FullReport, path: str) -> None:
        """Save .docx file to path."""
        data = self.export(report)
        with open(path, "wb") as f:
            f.write(data)
