"""
V1.9.5 Public Content Landing Pages — Rendering Templates.
"""
from __future__ import annotations
from public_content.models import PublicContentPage, PublicContentCatalog

_DISCLAIMER = (
    "> 本頁內容僅供探索參考，不構成命運斷語、生活決策依據或個人諮詢建議。"
)

_FOOTER = "Astro Destiny Analyzer · 整合命盤分析系統"


def render_public_page_markdown(page: PublicContentPage) -> str:
    """Render a PublicContentPage as Markdown."""
    parts = []
    parts.append(f"# {page.title}")
    if page.subtitle:
        parts.append(f"*{page.subtitle}*")
    parts.append("")
    if page.summary:
        parts.append(page.summary)
        parts.append("")
    if page.hero_points:
        for pt in page.hero_points:
            parts.append(f"- {pt}")
        parts.append("")
    for section in page.sections:
        if section.heading:
            parts.append(f"## {section.heading}")
        if section.body:
            parts.append(section.body)
            parts.append("")
        if section.bullets:
            for b in section.bullets:
                parts.append(f"- {b}")
            parts.append("")
        if section.warning:
            parts.append(f"> ⚠️ {section.warning}")
            parts.append("")
        if section.cta:
            parts.append(f"**{section.cta}**")
            parts.append("")
    if page.cta_title or page.cta_description or page.cta_button_label:
        parts.append("---")
        parts.append("")
        if page.cta_title:
            parts.append(f"### {page.cta_title}")
        if page.cta_description:
            parts.append(page.cta_description)
            parts.append("")
        if page.cta_button_label:
            parts.append(f"**→ {page.cta_button_label}**")
            parts.append("")
    parts.append(_DISCLAIMER)
    parts.append("")
    parts.append(f"---\n*{_FOOTER}*")
    return "\n".join(parts)


def render_public_catalog_markdown(catalog: PublicContentCatalog) -> str:
    """Render the full PublicContentCatalog as Markdown."""
    parts = []
    parts.append("# Astro Destiny Analyzer — 免費內容入口")
    parts.append("")
    # Featured pages
    featured_slugs = set(catalog.featured_slugs)
    featured = [p for p in catalog.pages if p.slug in featured_slugs]
    if featured:
        parts.append("## 精選內容")
        parts.append("")
        for p in featured:
            parts.append(f"### {p.title}")
            if p.summary:
                parts.append(p.summary[:200])
            if p.cta_button_label:
                parts.append(f"**→ {p.cta_button_label}**")
            parts.append("")
    # By category
    categories = {}
    for p in catalog.pages:
        categories.setdefault(p.category, []).append(p)
    category_labels = {
        "zodiac": "星座",
        "human_design": "人類圖",
        "compatibility": "合盤",
        "ziwei": "紫微",
        "bazi": "八字",
        "numerology": "靈數",
        "astrology": "占星",
        "guide": "指南",
    }
    parts.append("## 分類內容")
    parts.append("")
    for cat, pages in categories.items():
        label = category_labels.get(cat, cat)
        parts.append(f"### {label}")
        for p in pages:
            parts.append(f"- [{p.title}](/{p.slug})")
        parts.append("")
    parts.append("---")
    parts.append(f"*{_FOOTER}*")
    return "\n".join(parts)


def render_public_page_html(page: PublicContentPage) -> str:
    """Render a PublicContentPage as a self-contained HTML page."""
    from public_content.seo import build_meta_tags
    meta = build_meta_tags(page)
    meta_title = (page.seo.meta_title if page.seo and page.seo.meta_title else page.title)
    body_parts = []

    body_parts.append(f'<h1>{_esc(page.title)}</h1>')
    if page.subtitle:
        body_parts.append(f'<p class="subtitle">{_esc(page.subtitle)}</p>')
    if page.summary:
        body_parts.append(f'<p class="summary">{_esc(page.summary)}</p>')
    if page.hero_points:
        body_parts.append('<ul class="hero-points">')
        for pt in page.hero_points:
            body_parts.append(f'  <li>{_esc(pt)}</li>')
        body_parts.append('</ul>')

    for section in page.sections:
        body_parts.append('<div class="section">')
        if section.heading:
            body_parts.append(f'  <h2>{_esc(section.heading)}</h2>')
        if section.body:
            body_parts.append(f'  <p>{_esc(section.body)}</p>')
        if section.bullets:
            body_parts.append('  <ul>')
            for b in section.bullets:
                body_parts.append(f'    <li>{_esc(b)}</li>')
            body_parts.append('  </ul>')
        if section.warning:
            body_parts.append(f'  <p class="warning">⚠️ {_esc(section.warning)}</p>')
        body_parts.append('</div>')

    if page.cta_button_label or page.cta_title:
        body_parts.append('<div class="cta-block">')
        if page.cta_title:
            body_parts.append(f'  <h3>{_esc(page.cta_title)}</h3>')
        if page.cta_description:
            body_parts.append(f'  <p>{_esc(page.cta_description)}</p>')
        if page.cta_button_label:
            body_parts.append(f'  <p class="cta-btn">{_esc(page.cta_button_label)}</p>')
        body_parts.append('</div>')

    body_parts.append(f'<p class="disclaimer">{_esc(_DISCLAIMER.lstrip("> "))}</p>')
    body_html = "\n".join(body_parts)

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(meta_title)}</title>
{meta}
<style>
body{{font-family:sans-serif;max-width:800px;margin:2rem auto;padding:0 1rem;color:#222;line-height:1.7}}
h1{{font-size:1.8rem;margin-bottom:.5rem}}
h2{{font-size:1.3rem;margin-top:1.5rem}}
h3{{font-size:1.1rem}}
.subtitle{{color:#555;font-style:italic}}
.summary{{font-size:1.05rem;background:#f8f8f8;padding:1rem;border-left:4px solid #ccc}}
.hero-points{{margin:.5rem 0 1rem 1rem}}
.section{{margin:1.5rem 0}}
.warning{{color:#a05000;background:#fff8e1;border-left:4px solid #ffa000;padding:.5rem .75rem}}
.cta-block{{background:#f0f4ff;border:1px solid #c0c8e8;border-radius:6px;padding:1rem 1.5rem;margin:2rem 0}}
.cta-btn{{font-weight:bold;color:#1a3a8f}}
.disclaimer{{font-size:.85rem;color:#888;margin-top:2rem;border-top:1px solid #eee;padding-top:.75rem}}
footer{{margin-top:3rem;padding-top:1rem;border-top:1px solid #ddd;color:#999;font-size:.8rem;text-align:center}}
</style>
</head>
<body>
{body_html}
<footer>{_esc(_FOOTER)}</footer>
</body>
</html>"""


def render_public_catalog_html(catalog: PublicContentCatalog) -> str:
    """Render the full PublicContentCatalog as a self-contained HTML page."""
    featured_slugs = set(catalog.featured_slugs)
    featured = [p for p in catalog.pages if p.slug in featured_slugs]
    category_labels = {
        "zodiac": "星座", "human_design": "人類圖", "compatibility": "合盤",
        "ziwei": "紫微", "bazi": "八字", "numerology": "靈數",
        "astrology": "占星", "guide": "指南",
    }
    body_parts = []
    body_parts.append('<h1>免費內容入口</h1>')
    body_parts.append('<p class="subtitle">從星座、人類圖、合盤、紫微、八字開始，快速了解自己。</p>')
    if featured:
        body_parts.append('<h2>精選內容</h2>')
        body_parts.append('<div class="card-grid">')
        for p in featured:
            body_parts.append('<div class="card">')
            body_parts.append(f'<h3>{_esc(p.title)}</h3>')
            if p.summary:
                body_parts.append(f'<p>{_esc(p.summary[:150])}…</p>')
            if p.tags:
                body_parts.append('<p class="tags">' + " ".join(f'<span class="tag">{_esc(t)}</span>' for t in p.tags) + '</p>')
            if p.cta_button_label:
                body_parts.append(f'<p class="cta-btn">{_esc(p.cta_button_label)}</p>')
            body_parts.append('</div>')
        body_parts.append('</div>')
    categories: dict = {}
    for p in catalog.pages:
        categories.setdefault(p.category, []).append(p)
    body_parts.append('<h2>分類瀏覽</h2>')
    for cat, pages in categories.items():
        label = category_labels.get(cat, cat)
        body_parts.append(f'<h3>{_esc(label)}</h3>')
        body_parts.append('<ul>')
        for p in pages:
            body_parts.append(f'  <li><strong>{_esc(p.title)}</strong> — {_esc(p.summary[:80])}…</li>')
        body_parts.append('</ul>')
    body_html = "\n".join(body_parts)
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>免費內容入口 | Astro Destiny Analyzer</title>
<meta name="description" content="從星座、人類圖、合盤、紫微、八字開始了解自己，建立完整整合命盤報告。">
<style>
body{{font-family:sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem;color:#222;line-height:1.7}}
h1{{font-size:1.8rem}} h2{{font-size:1.3rem;margin-top:1.5rem}} h3{{font-size:1.1rem}}
.subtitle{{color:#555;font-style:italic}}
.card-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem;margin:1rem 0}}
.card{{background:#f8f9ff;border:1px solid #dde;border-radius:8px;padding:1rem}}
.tag{{background:#e8eaf6;border-radius:3px;padding:2px 6px;font-size:.8rem;margin-right:4px}}
.cta-btn{{font-weight:bold;color:#1a3a8f}}
footer{{margin-top:3rem;padding-top:1rem;border-top:1px solid #ddd;color:#999;font-size:.8rem;text-align:center}}
</style>
</head>
<body>
{body_html}
<footer>{_esc(_FOOTER)}</footer>
</body>
</html>"""


def render_public_page_excerpt(page: PublicContentPage) -> str:
    """Return a short card-sized excerpt of the page."""
    summary = page.summary[:150] + "…" if len(page.summary) > 150 else page.summary
    tags = " · ".join(page.tags) if page.tags else ""
    parts = [f"**{page.title}**"]
    if page.subtitle:
        parts.append(f"*{page.subtitle}*")
    if summary:
        parts.append(summary)
    if tags:
        parts.append(f"標籤：{tags}")
    if page.cta_button_label:
        parts.append(f"→ {page.cta_button_label}")
    return "\n".join(parts)


def _esc(text: str) -> str:
    """Minimal HTML escaping."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )
