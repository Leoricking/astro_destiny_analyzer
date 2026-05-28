"""
Tests for V1.9.5 Public Content Templates.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

_FORBIDDEN_PHRASES = ["一定成功", "一定分手", "必然大富大貴", "保證成功", "絕對命運"]


def _make_page():
    from public_content.models import PublicContentPage, PublicContentSection, SEOData
    return PublicContentPage(
        slug="test-page",
        title="測試頁面標題",
        subtitle="副標題",
        category="guide",
        summary="這是測試頁面的摘要文字。",
        hero_points=["重點一", "重點二"],
        sections=[
            PublicContentSection(
                heading="第一節",
                body="節的內容文字。",
                bullets=["項目 A", "項目 B"],
                warning="注意事項",
            ),
        ],
        cta_title="行動呼籲",
        cta_description="描述",
        cta_button_label="立即行動",
        cta_target="📝 輸入資料",
        seo=SEOData(
            meta_title="測試頁面 | Astro Destiny Analyzer",
            meta_description="這是測試頁面的 meta description，長度超過 50 字元以符合 SEO 要求。",
            keywords=["測試", "占星"],
            canonical_slug="test-page",
        ),
        is_public=True,
        is_featured=True,
        tags=["test"],
    )


def _make_catalog():
    from public_content.models import PublicContentCatalog
    from public_content.content_registry import get_public_content_catalog
    return get_public_content_catalog()


class TestRenderPublicPageMarkdown:
    def test_contains_title(self):
        from public_content.templates import render_public_page_markdown
        md = render_public_page_markdown(_make_page())
        assert "測試頁面標題" in md

    def test_contains_cta(self):
        from public_content.templates import render_public_page_markdown
        md = render_public_page_markdown(_make_page())
        assert "立即行動" in md

    def test_contains_summary(self):
        from public_content.templates import render_public_page_markdown
        md = render_public_page_markdown(_make_page())
        assert "摘要文字" in md

    def test_contains_hero_points(self):
        from public_content.templates import render_public_page_markdown
        md = render_public_page_markdown(_make_page())
        assert "重點一" in md

    def test_contains_disclaimer(self):
        from public_content.templates import render_public_page_markdown
        md = render_public_page_markdown(_make_page())
        assert "命運斷語" in md or "參考" in md

    def test_no_forbidden_phrases(self):
        from public_content.templates import render_public_page_markdown
        md = render_public_page_markdown(_make_page())
        for phrase in _FORBIDDEN_PHRASES:
            assert phrase not in md

    def test_returns_string(self):
        from public_content.templates import render_public_page_markdown
        assert isinstance(render_public_page_markdown(_make_page()), str)


class TestRenderPublicCatalogMarkdown:
    def test_contains_featured(self):
        from public_content.templates import render_public_catalog_markdown
        md = render_public_catalog_markdown(_make_catalog())
        assert "精選" in md

    def test_returns_string(self):
        from public_content.templates import render_public_catalog_markdown
        assert isinstance(render_public_catalog_markdown(_make_catalog()), str)

    def test_contains_footer(self):
        from public_content.templates import render_public_catalog_markdown
        md = render_public_catalog_markdown(_make_catalog())
        assert "Astro Destiny Analyzer" in md


class TestRenderPublicPageHtml:
    def test_contains_meta_charset_utf8(self):
        from public_content.templates import render_public_page_html
        html = render_public_page_html(_make_page())
        assert "charset=utf-8" in html.lower() or 'charset="utf-8"' in html.lower()

    def test_contains_meta_description(self):
        from public_content.templates import render_public_page_html
        html = render_public_page_html(_make_page())
        assert "meta" in html and "description" in html

    def test_no_script_tag(self):
        from public_content.templates import render_public_page_html
        html = render_public_page_html(_make_page())
        assert "<script" not in html.lower()

    def test_no_cdn(self):
        from public_content.templates import render_public_page_html
        html = render_public_page_html(_make_page())
        assert "cdn." not in html.lower()

    def test_contains_footer_branding(self):
        from public_content.templates import render_public_page_html
        html = render_public_page_html(_make_page())
        assert "Astro Destiny Analyzer" in html

    def test_contains_title(self):
        from public_content.templates import render_public_page_html
        html = render_public_page_html(_make_page())
        assert "測試頁面標題" in html

    def test_returns_string(self):
        from public_content.templates import render_public_page_html
        assert isinstance(render_public_page_html(_make_page()), str)


class TestRenderPublicCatalogHtml:
    def test_no_script_tag(self):
        from public_content.templates import render_public_catalog_html
        html = render_public_catalog_html(_make_catalog())
        assert "<script" not in html.lower()

    def test_contains_footer(self):
        from public_content.templates import render_public_catalog_html
        html = render_public_catalog_html(_make_catalog())
        assert "Astro Destiny Analyzer" in html

    def test_returns_string(self):
        from public_content.templates import render_public_catalog_html
        assert isinstance(render_public_catalog_html(_make_catalog()), str)


class TestRenderPublicPageExcerpt:
    def test_not_empty(self):
        from public_content.templates import render_public_page_excerpt
        excerpt = render_public_page_excerpt(_make_page())
        assert excerpt and len(excerpt) > 0

    def test_contains_title(self):
        from public_content.templates import render_public_page_excerpt
        excerpt = render_public_page_excerpt(_make_page())
        assert "測試頁面標題" in excerpt
