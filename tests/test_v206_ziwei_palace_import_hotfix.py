from pathlib import Path


def test_components_imports_ziwei_display_helpers():
    source = Path('ui/components.py').read_text(encoding='utf-8')
    assert 'translate_ziwei_palace' in source
    assert 'translate_ziwei_star' in source


def test_ziwei_display_helpers_importable():
    from i18n.display_names import translate_ziwei_palace, translate_ziwei_star

    assert translate_ziwei_palace('命宮', 'en') == 'Life Palace'
    assert translate_ziwei_star('貪狼', 'en')


def test_renderers_reference_imported_helpers():
    source = Path("ui/components.py").read_text(encoding="utf-8")
    import_block = source.split("from core.models", 1)[0]
    assert "translate_ziwei_palace" in import_block
    assert "translate_ziwei_star" in import_block
    assert "def render_daxian_table" in source
    assert "def render_ziwei_formal_table" in source
