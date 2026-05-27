"""
Astro Destiny Analyzer — PDF Exporter
Uses WeasyPrint (if available) to render HTML → PDF.

Installation (optional):
  pip install weasyprint
  Windows: may require additional system dependencies (GTK, Pango).

V1.6 recommendation:
  Use HTML or Word for delivery; PDF after WeasyPrint environment is configured.
  See README for details.
"""
from core.models import FullReport


def _weasyprint_available() -> bool:
    try:
        import weasyprint  # noqa: F401
        return True
    except (ImportError, OSError):
        return False


class PdfExporter:
    """
    PDF export via WeasyPrint.
    Gracefully unavailable (is_available() → False) when WeasyPrint is not installed.
    """

    def is_available(self) -> bool:
        """Return True only if WeasyPrint is installed and importable."""
        return _weasyprint_available()

    def export(self, report: FullReport) -> bytes:
        """
        Generate PDF bytes from the HTML report via WeasyPrint.
        Raises RuntimeError (not crash) if WeasyPrint is unavailable.
        """
        if not self.is_available():
            raise RuntimeError(
                "PDF 匯出需要安裝 WeasyPrint。\n"
                "執行：pip install weasyprint\n"
                "Windows 可能需要額外系統依賴（GTK / Pango / libpango）。\n"
                "建議優先使用 HTML 或 Word 格式交付。"
            )
        from weasyprint import HTML
        from reports.html_exporter import HtmlExporter
        html_content = HtmlExporter().export(report)
        return HTML(string=html_content).write_pdf()

    def save(self, report: FullReport, path: str) -> None:
        """Save PDF to path."""
        pdf_bytes = self.export(report)
        with open(path, "wb") as f:
            f.write(pdf_bytes)
