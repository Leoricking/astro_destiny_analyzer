"""
V1.9.5 Public Content Landing Pages — SEO Helpers.
"""
from __future__ import annotations
import re
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from public_content.models import PublicContentPage

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
_FORBIDDEN_PHRASES = [
    "一定成功", "一定分手", "必然", "保證", "絕對命運", "大富大貴保證",
]


def make_slug(text: str) -> str:
    """Convert text to a URL-safe slug."""
    # Remove emoji
    text = _EMOJI.sub("", text)
    # Lowercase
    text = text.lower()
    # Replace spaces with hyphens
    text = text.replace(" ", "-")
    # Remove illegal chars
    text = _ILLEGAL_CHARS.sub("", text)
    # Remove non-ASCII except hyphens and Chinese characters
    text = re.sub(r"[^\w\-\u4e00-\u9fff\u3400-\u4dbf]", "", text)
    # Collapse multiple hyphens
    text = re.sub(r"-+", "-", text)
    text = text.strip("-")
    return text


def validate_seo_data(page: "PublicContentPage") -> List[str]:
    """Return a list of SEO warning strings for the given page."""
    warnings: List[str] = []
    if not page.seo or not page.seo.meta_title:
        warnings.append("meta_title missing")
    if not page.seo or not page.seo.meta_description:
        warnings.append("meta_description missing")
    elif len(page.seo.meta_description) < 50:
        warnings.append("meta_description too short (< 50 chars)")
    if not page.slug:
        warnings.append("slug missing")
    if not page.cta_button_label or not page.cta_target:
        warnings.append("CTA missing (cta_button_label or cta_target empty)")
    if page.title and len(page.title) > 70:
        warnings.append("title too long (> 70 chars)")
    return warnings


def build_meta_tags(page: "PublicContentPage") -> str:
    """Build HTML meta tag string for the given page."""
    seo = page.seo
    if seo is None:
        return ""
    lines = []
    if seo.meta_title:
        lines.append(f'<meta name="title" content="{seo.meta_title}">')
    if seo.meta_description:
        lines.append(f'<meta name="description" content="{seo.meta_description}">')
    if seo.keywords:
        kw = ", ".join(seo.keywords)
        lines.append(f'<meta name="keywords" content="{kw}">')
    if seo.canonical_slug:
        lines.append(f'<link rel="canonical" href="/{seo.canonical_slug}">')
    og_title = seo.og_title or seo.meta_title
    if og_title:
        lines.append(f'<meta property="og:title" content="{og_title}">')
    og_desc = seo.og_description or seo.meta_description
    if og_desc:
        lines.append(f'<meta property="og:description" content="{og_desc}">')
    return "\n".join(lines)


def check_forbidden_phrases(text: str) -> List[str]:
    """Return list of forbidden phrases found in text."""
    found = []
    for phrase in _FORBIDDEN_PHRASES:
        if phrase in text:
            found.append(phrase)
    return found
