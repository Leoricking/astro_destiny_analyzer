"""
Tests for V1.9.5 Public Content Models.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


class TestPublicContentPageModel:
    def test_page_createable(self):
        from public_content.models import PublicContentPage
        p = PublicContentPage(slug="test", title="Test", category="guide", summary="A summary.")
        assert p.slug == "test"

    def test_page_default_is_public_true(self):
        from public_content.models import PublicContentPage
        p = PublicContentPage(slug="x", title="X", category="guide", summary="s")
        assert p.is_public is True

    def test_page_default_is_featured_false(self):
        from public_content.models import PublicContentPage
        p = PublicContentPage(slug="x", title="X", category="guide", summary="s")
        assert p.is_featured is False

    def test_page_cta_fields_accessible(self):
        from public_content.models import PublicContentPage
        p = PublicContentPage(
            slug="x", title="X", category="guide", summary="s",
            cta_title="CTA Title", cta_description="desc",
            cta_button_label="Click", cta_target="page",
        )
        assert p.cta_title == "CTA Title"
        assert p.cta_button_label == "Click"

    def test_page_hero_points_default_empty(self):
        from public_content.models import PublicContentPage
        p = PublicContentPage(slug="x", title="X", category="guide", summary="s")
        assert p.hero_points == []

    def test_page_sections_default_empty(self):
        from public_content.models import PublicContentPage
        p = PublicContentPage(slug="x", title="X", category="guide", summary="s")
        assert p.sections == []

    def test_page_tags_default_empty(self):
        from public_content.models import PublicContentPage
        p = PublicContentPage(slug="x", title="X", category="guide", summary="s")
        assert p.tags == []

    def test_page_category_zodiac(self):
        from public_content.models import PublicContentPage
        p = PublicContentPage(slug="x", title="X", category="zodiac", summary="s")
        assert p.category == "zodiac"

    def test_page_category_human_design(self):
        from public_content.models import PublicContentPage
        p = PublicContentPage(slug="x", title="X", category="human_design", summary="s")
        assert p.category == "human_design"

    def test_page_slug_not_empty_when_set(self):
        from public_content.models import PublicContentPage
        p = PublicContentPage(slug="my-slug", title="T", category="guide", summary="s")
        assert p.slug == "my-slug"


class TestPublicContentSectionModel:
    def test_section_createable(self):
        from public_content.models import PublicContentSection
        s = PublicContentSection(heading="H", body="B")
        assert s.heading == "H"

    def test_section_bullets_default_empty(self):
        from public_content.models import PublicContentSection
        s = PublicContentSection()
        assert s.bullets == []

    def test_section_warning_default_empty(self):
        from public_content.models import PublicContentSection
        s = PublicContentSection()
        assert s.warning == ""

    def test_section_cta_default_empty(self):
        from public_content.models import PublicContentSection
        s = PublicContentSection()
        assert s.cta == ""


class TestSEODataModel:
    def test_seodata_createable(self):
        from public_content.models import SEOData
        s = SEOData(meta_title="Title", meta_description="Description here for test.")
        assert s.meta_title == "Title"

    def test_seodata_keywords_default_empty(self):
        from public_content.models import SEOData
        s = SEOData()
        assert s.keywords == []

    def test_seodata_og_fields_default_empty(self):
        from public_content.models import SEOData
        s = SEOData()
        assert s.og_title == ""
        assert s.og_description == ""


class TestPublicContentCatalogModel:
    def test_catalog_createable(self):
        from public_content.models import PublicContentCatalog
        c = PublicContentCatalog()
        assert c.pages == []
        assert c.version == "1.9.5"

    def test_catalog_with_pages(self):
        from public_content.models import PublicContentCatalog, PublicContentPage
        p = PublicContentPage(slug="x", title="X", category="guide", summary="s")
        c = PublicContentCatalog(pages=[p])
        assert len(c.pages) == 1

    def test_catalog_featured_slugs_default_empty(self):
        from public_content.models import PublicContentCatalog
        c = PublicContentCatalog()
        assert c.featured_slugs == []
