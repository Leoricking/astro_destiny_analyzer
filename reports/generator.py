"""
Astro Destiny Analyzer — Report Generator
Orchestrates all engines and produces a FullReport.
"""
from datetime import datetime, date, time
from typing import Optional, List

from core.models import (
    BirthProfile, FullReport, AnalysisTheme,
)
from core.database import (
    save_birth_profile, save_chart_result, save_report,
)
from engines.western_astrology import WesternAstrologyEngine
from engines.bazi import BaZiEngine
from engines.ziwei import ZiWeiEngine
from engines.blood_type import BloodTypeEngine
from engines.numerology import NumerologyEngine
from engines.synthesis import SynthesisEngine
from reports.templates import render_report
from reports.markdown_exporter import MarkdownExporter
from reports.html_exporter import HtmlExporter


class ReportGenerator:
    def __init__(self):
        self._western = WesternAstrologyEngine()
        self._bazi    = BaZiEngine()
        self._ziwei   = ZiWeiEngine()
        self._blood   = BloodTypeEngine()
        self._num     = NumerologyEngine()
        self._synth   = SynthesisEngine()
        self._md      = MarkdownExporter()
        self._html    = HtmlExporter()

    def generate(self, profile: BirthProfile,
                 persist: bool = True) -> FullReport:
        """
        Run all engines and return a FullReport.
        If persist=True, saves to SQLite and attaches report_id.
        """
        birth_date = profile.birth_date
        birth_time = profile.birth_time

        # ── Run Engines ───────────────────────────────────────────────────────
        western_chart = self._western.calculate(
            birth_date=birth_date,
            birth_time=birth_time,
            birth_city=profile.birth_city,
            birth_country=profile.birth_country,
            birth_latitude=profile.birth_latitude,
            birth_longitude=profile.birth_longitude,
            birth_timezone_offset=profile.birth_timezone_offset,
        )

        bazi_chart = self._bazi.calculate(
            birth_date=birth_date,
            birth_time=birth_time,
        )

        ziwei_chart = self._ziwei.calculate(
            birth_date=birth_date,
            birth_time=birth_time,
            gender=profile.gender,
        )

        blood_analysis = self._blood.analyze(profile.blood_type)

        numerology_chart = self._num.calculate(birth_date=birth_date)

        synthesis = self._synth.synthesize(
            profile=profile,
            western=western_chart,
            bazi=bazi_chart,
            ziwei=ziwei_chart,
            blood=blood_analysis,
            numerology=numerology_chart,
        )

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = FullReport(
            profile=profile,
            western_chart=western_chart,
            bazi_chart=bazi_chart,
            ziwei_chart=ziwei_chart,
            blood_type_analysis=blood_analysis,
            numerology_chart=numerology_chart,
            synthesis=synthesis,
            created_at=created_at,
        )

        # ── Persist ───────────────────────────────────────────────────────────
        if persist:
            profile_dict = profile.model_dump(mode="json")
            profile_id = save_birth_profile(profile_dict)

            charts_dict = {
                "western_chart":      western_chart.model_dump(mode="json"),
                "bazi_chart":         bazi_chart.model_dump(mode="json"),
                "ziwei_chart":        ziwei_chart.model_dump(mode="json"),
                "blood_type_analysis": blood_analysis.model_dump(mode="json"),
                "numerology_chart":   numerology_chart.model_dump(mode="json"),
                "synthesis":          synthesis.model_dump(mode="json"),
            }
            chart_id = save_chart_result(profile_id, charts_dict)

            markdown_body = self._md.export(report)
            html_body     = self._html.export(report)
            title = f"{profile.name} 命盤分析報告 {created_at[:10]}"
            report_id = save_report(
                profile_id=profile_id,
                chart_id=chart_id,
                title=title,
                language=profile.report_language.value,
                length=profile.report_length.value,
                markdown_body=markdown_body,
                html_body=html_body,
            )
            report.report_id = report_id

        return report

    def to_markdown(self, report: FullReport) -> str:
        return self._md.export(report)

    def to_html(self, report: FullReport) -> str:
        return self._html.export(report)
