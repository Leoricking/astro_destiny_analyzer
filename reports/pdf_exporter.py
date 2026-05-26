"""
Astro Destiny Analyzer — PDF Exporter
Interface reserved for future implementation.

Option A (recommended): WeasyPrint — renders HTML/CSS to PDF with CJK font support.
  pip install weasyprint
  Requires: libpango, libcairo, and a CJK font (e.g. Noto Serif TC).

Option B: ReportLab — lower-level, more control, needs manual CJK font registration.
  pip install reportlab

Option C: Use html2pdf via Playwright (headless Chrome) for best CSS fidelity.
  pip install playwright && playwright install chromium
"""
from core.models import FullReport


class PdfExporter:
    """
    PDF export — reserved interface.
    Calling export() or save() will raise NotImplementedError until implemented.
    """

    def is_available(self) -> bool:
        """Return True if a PDF backend is installed."""
        try:
            import weasyprint  # noqa: F401
            return True
        except ImportError:
            pass
        try:
            import reportlab  # noqa: F401
            return True
        except ImportError:
            pass
        return False

    def export(self, report: FullReport) -> bytes:
        """
        TODO: Implement PDF export.

        WeasyPrint example:
            from weasyprint import HTML
            from reports.html_exporter import HtmlExporter
            html_content = HtmlExporter().export(report)
            return HTML(string=html_content).write_pdf()
        """
        if not self.is_available():
            raise NotImplementedError(
                "PDF export requires WeasyPrint or ReportLab. "
                "Run: pip install weasyprint"
            )
        raise NotImplementedError("PDF export backend not yet configured.")

    def save(self, report: FullReport, path: str) -> None:
        """Save PDF to path."""
        pdf_bytes = self.export(report)
        with open(path, "wb") as f:
            f.write(pdf_bytes)
