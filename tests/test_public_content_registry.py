"""
Tests for V1.9.5 Public Content Registry.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

_FORBIDDEN = ["Rossi", "golden case", "debug", "一定成功", "一定分手", "必然", "保證", "絕對命運", "大富大貴保證"]


class TestPublicContentRegistry:
    def test_get_catalog_returns_catalog(self):
        from public_content.content_registry import get_public_content_catalog
        cat = get_public_content_catalog()
        assert cat is not None

    def test_catalog_has_enough_pages(self):
        from public_content.content_registry import get_public_content_catalog
        cat = get_public_content_catalog()
        assert len(cat.pages) >= 9

    def test_all_pages_have_title(self):
        from public_content.content_registry import get_public_content_catalog
        cat = get_public_content_catalog()
        for p in cat.pages:
            assert p.title, f"Page {p.slug} has empty title"

    def test_all_pages_have_summary(self):
        from public_content.content_registry import get_public_content_catalog
        cat = get_public_content_catalog()
        for p in cat.pages:
            assert p.summary, f"Page {p.slug} has empty summary"

    def test_all_pages_have_cta(self):
        from public_content.content_registry import get_public_content_catalog
        cat = get_public_content_catalog()
        for p in cat.pages:
            assert p.cta_button_label, f"Page {p.slug} has empty cta_button_label"

    def test_all_pages_have_seo(self):
        from public_content.content_registry import get_public_content_catalog
        cat = get_public_content_catalog()
        for p in cat.pages:
            assert p.seo is not None, f"Page {p.slug} has no SEO"
            assert p.seo.meta_title, f"Page {p.slug} has empty seo.meta_title"
            assert p.seo.meta_description, f"Page {p.slug} has empty seo.meta_description"

    def test_featured_pages_not_empty(self):
        from public_content.content_registry import list_featured_pages
        featured = list_featured_pages()
        assert len(featured) > 0

    def test_filter_zodiac_pages(self):
        from public_content.content_registry import list_public_pages
        zodiac = list_public_pages(category="zodiac")
        assert len(zodiac) >= 1
        for p in zodiac:
            assert p.category == "zodiac"

    def test_filter_human_design_pages(self):
        from public_content.content_registry import list_public_pages
        hd = list_public_pages(category="human_design")
        assert len(hd) >= 1
        for p in hd:
            assert p.category == "human_design"

    def test_filter_compatibility_pages(self):
        from public_content.content_registry import list_public_pages
        compat = list_public_pages(category="compatibility")
        assert len(compat) >= 1

    def test_get_public_page_human_design_overview(self):
        from public_content.content_registry import get_public_page
        page = get_public_page("human-design-overview")
        assert page is not None
        assert page.slug == "human-design-overview"

    def test_get_public_page_missing_returns_none(self):
        from public_content.content_registry import get_public_page
        assert get_public_page("nonexistent-slug-xyz") is None

    def test_registry_no_rossi(self):
        from public_content.content_registry import get_public_content_catalog
        cat = get_public_content_catalog()
        for p in cat.pages:
            combined = p.title + p.summary + "".join(s.body for s in p.sections)
            assert "Rossi" not in combined, f"Page {p.slug} mentions Rossi"

    def test_registry_no_golden_case(self):
        from public_content.content_registry import get_public_content_catalog
        cat = get_public_content_catalog()
        for p in cat.pages:
            combined = p.title + p.summary + "".join(s.body for s in p.sections)
            assert "golden case" not in combined.lower(), f"Page {p.slug} mentions golden case"

    def test_registry_no_debug(self):
        from public_content.content_registry import get_public_content_catalog
        cat = get_public_content_catalog()
        for p in cat.pages:
            combined = p.title + p.summary + "".join(s.body for s in p.sections)
            assert "debug" not in combined.lower(), f"Page {p.slug} mentions debug"

    def test_registry_no_forbidden_phrases(self):
        from public_content.content_registry import get_public_content_catalog
        cat = get_public_content_catalog()
        forbidden = ["一定成功", "一定分手", "必然", "保證", "絕對命運", "大富大貴保證"]
        for p in cat.pages:
            combined = p.title + p.summary + "".join(s.body + s.warning for s in p.sections)
            for phrase in forbidden:
                assert phrase not in combined, f"Page {p.slug} contains forbidden phrase: {phrase}"
