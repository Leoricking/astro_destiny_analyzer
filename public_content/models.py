"""
V1.9.5 Public Content Landing Pages — Data Models.
"""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

VALID_CATEGORIES = {
    "zodiac", "human_design", "compatibility",
    "ziwei", "bazi", "numerology", "astrology", "guide",
}


class SEOData(BaseModel):
    meta_title: str = ""
    meta_description: str = ""
    keywords: List[str] = Field(default_factory=list)
    canonical_slug: str = ""
    og_title: str = ""
    og_description: str = ""


class PublicContentSection(BaseModel):
    heading: str = ""
    body: str = ""
    bullets: List[str] = Field(default_factory=list)
    warning: str = ""
    cta: str = ""


class PublicContentPage(BaseModel):
    slug: str = ""
    title: str = ""
    subtitle: str = ""
    category: str = "guide"
    summary: str = ""
    hero_points: List[str] = Field(default_factory=list)
    sections: List[PublicContentSection] = Field(default_factory=list)
    cta_title: str = ""
    cta_description: str = ""
    cta_button_label: str = ""
    cta_target: str = ""
    seo: Optional[SEOData] = None
    is_public: bool = True
    is_featured: bool = False
    tags: List[str] = Field(default_factory=list)
    free_report_cta_slug: str = ""


class PublicContentCatalog(BaseModel):
    pages: List[PublicContentPage] = Field(default_factory=list)
    featured_slugs: List[str] = Field(default_factory=list)
    updated_at: str = ""
    version: str = "1.9.5"
