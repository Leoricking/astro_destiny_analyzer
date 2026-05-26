"""
Astro Destiny Analyzer — Markdown Exporter
"""
from core.models import FullReport
from reports.templates import render_report
from config import APP_VERSION


class MarkdownExporter:
    def export(self, report: FullReport) -> str:
        return render_report(report, version=APP_VERSION)

    def save(self, report: FullReport, path: str) -> None:
        content = self.export(report)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
