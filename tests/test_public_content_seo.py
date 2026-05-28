"""
Tests for V1.9.5 Public Content SEO Helpers.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


def _make_good_page():
    from public_content.models import PublicContentPage, SEOData
    return PublicContentPage(
        slug="test-seo-page",
        title="測試 SEO 頁面",
        category="guide",
        summary="摘要文字用於 SEO 測試。",
        cta_button_label="行動",
        cta_target="📝 輸入資料",
        seo=SEOData(
            meta_title="測試 SEO | Astro",
            meta_description="這是超過五十字元的 meta description，用於 SEO 驗證測試使用，確保長度合格符合要求。",
            keywords=["test", "seo"],
            canonical_slug="test-seo-page",
            og_title="測試 OG 標題",
            og_description="測試 OG 描述",
        ),
    )


class TestMakeSlug:
    def test_no_emoji(self):
        from public_content.seo import make_slug
        result = make_slug("test 🔷 slug")
        assert "🔷" not in result

    def test_no_illegal_chars(self):
        from public_content.seo import make_slug
        result = make_slug('test/slug:name*"<>|')
        for ch in r'\/:*?"<>|':
            assert ch not in result

    def test_spaces_to_hyphens(self):
        from public_content.seo import make_slug
        result = make_slug("hello world")
        assert " " not in result
        assert "-" in result or "helloworld" in result

    def test_lowercase(self):
        from public_content.seo import make_slug
        result = make_slug("Hello World")
        assert result == result.lower()

    def test_empty_string(self):
        from public_content.seo import make_slug
        result = make_slug("")
        assert isinstance(result, str)


class TestValidateSeoData:
    def test_good_page_no_critical_warnings(self):
        from public_content.seo import validate_seo_data
        page = _make_good_page()
        warnings = validate_seo_data(page)
        assert len(warnings) == 0

    def test_missing_meta_description_has_warning(self):
        from public_content.seo import validate_seo_data
        from public_content.models import PublicContentPage, SEOData
        page = PublicContentPage(
            slug="x", title="T", category="guide", summary="s",
            cta_button_label="CTA", cta_target="page",
            seo=SEOData(meta_title="Title", meta_description=""),
        )
        warnings = validate_seo_data(page)
        assert any("meta_description" in w for w in warnings)

    def test_missing_cta_has_warning(self):
        from public_content.seo import validate_seo_data
        from public_content.models import PublicContentPage, SEOData
        page = PublicContentPage(
            slug="x", title="T", category="guide", summary="s",
            seo=SEOData(
                meta_title="Title",
                meta_description="長度超過五十字元的 meta description 用於測試。這是額外的文字。",
            ),
        )
        warnings = validate_seo_data(page)
        assert any("CTA" in w for w in warnings)

    def test_missing_slug_has_warning(self):
        from public_content.seo import validate_seo_data
        from public_content.models import PublicContentPage, SEOData
        page = PublicContentPage(
            slug="", title="T", category="guide", summary="s",
            cta_button_label="CTA", cta_target="page",
            seo=SEOData(
                meta_title="Title",
                meta_description="長度超過五十字元的 meta description 用於測試。這是額外文字。",
            ),
        )
        warnings = validate_seo_data(page)
        assert any("slug" in w for w in warnings)


class TestBuildMetaTags:
    def test_contains_description(self):
        from public_content.seo import build_meta_tags
        tags = build_meta_tags(_make_good_page())
        assert "description" in tags

    def test_contains_og(self):
        from public_content.seo import build_meta_tags
        tags = build_meta_tags(_make_good_page())
        assert "og:" in tags

    def test_returns_string(self):
        from public_content.seo import build_meta_tags
        assert isinstance(build_meta_tags(_make_good_page()), str)

    def test_no_page_seo_returns_empty(self):
        from public_content.seo import build_meta_tags
        from public_content.models import PublicContentPage
        page = PublicContentPage(slug="x", title="T", category="guide", summary="s")
        result = build_meta_tags(page)
        assert result == ""


class TestCheckForbiddenPhrases:
    def test_catches_yiding_chenggong(self):
        from public_content.seo import check_forbidden_phrases
        found = check_forbidden_phrases("這個系統一定成功帶給你財富")
        assert "一定成功" in found

    def test_no_forbidden_in_clean_text(self):
        from public_content.seo import check_forbidden_phrases
        found = check_forbidden_phrases("星座提供探索視角，不構成命運斷語。")
        assert found == []

    def test_catches_biran(self):
        from public_content.seo import check_forbidden_phrases
        found = check_forbidden_phrases("你必然會成功的")
        assert "必然" in found


class TestSafePublicContentFilename:
    def test_no_illegal_chars(self):
        from public_content.exporters import safe_public_content_filename
        fn = safe_public_content_filename("test-page", "html")
        for ch in r'\/:*?"<>|':
            assert ch not in fn

    def test_no_emoji(self):
        from public_content.exporters import safe_public_content_filename
        fn = safe_public_content_filename("test 🔷 page", "md")
        assert "🔷" not in fn

    def test_correct_suffix_html(self):
        from public_content.exporters import safe_public_content_filename
        fn = safe_public_content_filename("page", "html")
        assert fn.endswith(".html")

    def test_correct_suffix_md(self):
        from public_content.exporters import safe_public_content_filename
        fn = safe_public_content_filename("page", "md")
        assert fn.endswith(".md")

    def test_prefix_format(self):
        from public_content.exporters import safe_public_content_filename
        fn = safe_public_content_filename("my-page", "html")
        assert fn.startswith("public_content_")

    def test_empty_slug_safe(self):
        from public_content.exporters import safe_public_content_filename
        fn = safe_public_content_filename("", "md")
        assert fn.endswith(".md")
        assert "public_content_" in fn
