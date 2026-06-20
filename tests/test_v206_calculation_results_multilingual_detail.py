from pathlib import Path

from i18n.display_names import (
    translate_planet, translate_aspect, translate_branch,
    translate_bazi_stem, translate_element,
)


def test_planet_names_translate_to_english():
    assert translate_planet('太陽', 'en') == 'Sun'
    assert translate_planet('月亮', 'en') == 'Moon'


def test_aspects_translate_to_english():
    assert translate_aspect('合相 0°', 'en') == 'Conjunction 0°'
    assert translate_aspect('對分 180°', 'en') == 'Opposition 180°'


def test_bazi_values_translate_to_english():
    assert 'Wood' in translate_bazi_stem('乙', 'en')
    assert translate_element('水', 'en') == 'Water'
    assert 'Rat' in translate_branch('子', 'en')


def test_components_are_language_aware():
    text = Path('ui/components.py').read_text(encoding='utf-8')
    for signature in (
        'def render_planet_table(planet_positions, language="zh-TW")',
        'def render_house_table(houses, language="zh-TW")',
        'def render_aspect_table(aspects, language="zh-TW")',
        'def render_bazi_pillars(bazi_chart, language="zh-TW")',
        'def render_ziwei_formal_table(ziwei_chart, language="zh-TW")',
        'def render_daxian_table(ziwei_chart, language="zh-TW")',
    ):
        assert signature in text


def test_report_preview_uses_detailed_localized_renderer():
    text = Path('ui/components.py').read_text(encoding='utf-8')
    assert 'from reports.localized_renderer import localized_section_bodies' in text
    renderer = Path('reports/localized_renderer.py').read_text(encoding='utf-8')
    assert '_detailed_evidence_blocks' in renderer
    assert '**Evidence used**' in renderer
    assert '**使用した根拠**' in renderer
