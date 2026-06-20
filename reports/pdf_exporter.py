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
        """Return True when either WeasyPrint or the ReportLab fallback is available."""
        if _weasyprint_available():
            return True
        try:
            import reportlab  # noqa: F401
            return True
        except ImportError:
            return False

    def export(self, report: FullReport, language: str = "zh-TW") -> bytes:
        """
        Generate PDF bytes from the HTML report via WeasyPrint.
        Raises RuntimeError (not crash) if WeasyPrint is unavailable.
        """
        from reports.markdown_exporter import MarkdownExporter
        if _weasyprint_available():
            from weasyprint import HTML
            from reports.html_exporter import HtmlExporter
            html_content = HtmlExporter().export(report, language=language)
            return HTML(string=html_content).write_pdf()
        try:
            from reports.pdf_fallback import markdown_to_pdf_bytes
            markdown_text = MarkdownExporter().export(report, language=language)
            return markdown_to_pdf_bytes(markdown_text, language=language)
        except Exception as exc:
            raise RuntimeError(
                "PDF export requires either WeasyPrint or ReportLab."
            ) from exc

    def save(self, report: FullReport, path: str, language: str = "zh-TW") -> None:
        """Save PDF to path."""
        pdf_bytes = self.export(report, language=language)
        with open(path, "wb") as f:
            f.write(pdf_bytes)
