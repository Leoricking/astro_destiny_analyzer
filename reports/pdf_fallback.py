"""
ReportLab fallback PDF renderer used when WeasyPrint is unavailable.

It uses fonts already installed on the user's system and never bundles or
redistributes font files.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import os
import re
from typing import Iterable


def _candidate_fonts(language: str):
    win = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    mapping = {
        "zh-TW": ["msjh.ttc","msjh.ttf","mingliu.ttc","arialuni.ttf"],
        "ja": ["YuGothR.ttc","msgothic.ttc","meiryo.ttc","arialuni.ttf"],
        "th": ["LeelawUI.ttf","LeelawUIb.ttf","Tahoma.ttf","arialuni.ttf"],
        "ar": ["arial.ttf","segoeui.ttf","tahoma.ttf","arialuni.ttf"],
        "es": ["arial.ttf","segoeui.ttf"],
        "en": ["arial.ttf","segoeui.ttf"],
    }
    for name in mapping.get(language, mapping["en"]):
        path = win / name
        if path.exists():
            yield path


def _register_font(language: str) -> str:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    for path in _candidate_fonts(language):
        try:
            name = f"AstroFont_{language.replace('-','_')}"
            pdfmetrics.registerFont(TTFont(name, str(path)))
            return name
        except Exception:
            continue
    return "Helvetica"


def markdown_to_pdf_bytes(markdown_text: str, language: str = "zh-TW") -> bytes:
    from reportlab.lib.enums import TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from xml.sax.saxutils import escape

    font = _register_font(language)
    align = TA_RIGHT if language == "ar" else TA_LEFT
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "AstroBody", parent=styles["BodyText"], fontName=font,
        fontSize=10, leading=15, alignment=align, wordWrap="CJK",
    )
    h1 = ParagraphStyle("AstroH1", parent=styles["Heading1"], fontName=font, alignment=align)
    h2 = ParagraphStyle("AstroH2", parent=styles["Heading2"], fontName=font, alignment=align)
    h3 = ParagraphStyle("AstroH3", parent=styles["Heading3"], fontName=font, alignment=align)

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
        topMargin=18*mm, bottomMargin=18*mm,
        title="Astro Destiny Analyzer Report",
    )
    story = []
    in_front_matter = False
    for raw in markdown_text.splitlines():
        line = raw.rstrip()
        if line == "---":
            in_front_matter = not in_front_matter
            continue
        if in_front_matter or not line:
            if not line:
                story.append(Spacer(1, 4))
            continue
        if line.startswith("# "):
            story.append(Paragraph(escape(line[2:]), h1))
        elif line.startswith("## "):
            story.append(Paragraph(escape(line[3:]), h2))
        elif line.startswith("### "):
            story.append(Paragraph(escape(line[4:]), h3))
        elif line.startswith("- "):
            story.append(Paragraph("• " + escape(line[2:]), body))
        elif re.match(r"^\d+\.\s", line):
            story.append(Paragraph(escape(line), body))
        elif line.startswith("|"):
            story.append(Paragraph(escape(line.replace("|","  ")), body))
        else:
            # Basic markdown cleanup.
            clean = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", escape(line))
            story.append(Paragraph(clean, body))
    doc.build(story)
    return buf.getvalue()
