"""
V1.9.5 Public Content Landing Pages — Exporters.
"""
from __future__ import annotations
import re
from datetime import date
from public_content.models import PublicContentPage, PublicContentCatalog
from public_content.templates import (
    render_public_page_markdown,
    render_public_catalog_markdown,
    render_public_page_html,
    render_public_catalog_html,
)

_ILLEGAL_CHARS = re.compile(r'[\\/:*?"<>|]')
_EMOJI = re.compile(
    r"[\U00010000-\U0010ffff"
    r"\U0001F300-\U0001F9FF"
    r"\U00002600-\U000027BF"
    r"\U0000FE00-\U0000FE0F"
    r"\U00020000-\U0002A6DF"
    r"\u2600-\u27BF]",
    flags=re.UNICODE,
)


def safe_public_content_filename(slug: str, suffix: str) -> str:
    """Return a safe filename: public_content_{slug}_{YYYYMMDD}.{suffix}"""
    clean = _EMOJI.sub("", slug)
    clean = _ILLEGAL_CHARS.sub("", clean)
    clean = clean.strip().replace(" ", "_")
    if not clean:
        clean = "page"
    today = date.today().strftime("%Y%m%d")
    ext = suffix.lstrip(".")
    return f"public_content_{clean}_{today}.{ext}"


def export_public_page_markdown(page: PublicContentPage) -> str:
    return render_public_page_markdown(page)


def export_public_page_html(page: PublicContentPage) -> str:
    return render_public_page_html(page)


def export_public_catalog_markdown(catalog: PublicContentCatalog) -> str:
    return render_public_catalog_markdown(catalog)


def export_public_catalog_html(catalog: PublicContentCatalog) -> str:
    return render_public_catalog_html(catalog)
