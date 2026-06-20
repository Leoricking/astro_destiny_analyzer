"""Regression coverage for complete Zi Wei display-layer localization."""
import re

from i18n.display_names import (
    translate_ziwei_bureau,
    translate_ziwei_palace,
    translate_ziwei_star,
    translate_ziwei_transformation,
)

CJK_RE = re.compile(r"[\u3400-\u9fff]")


def test_english_ziwei_palaces_are_localized():
    expected = {
        "命宮": "Life Palace",
        "兄弟宮": "Siblings Palace",
        "夫妻宮": "Relationship Palace",
        "子女宮": "Children Palace",
        "財帛宮": "Wealth Palace",
        "疾厄宮": "Health Palace",
        "遷移宮": "Travel Palace",
        "交友宮": "Friends Palace",
        "僕役宮": "Friends Palace",
        "官祿宮": "Career Palace",
        "田宅宮": "Property Palace",
        "福德宮": "Well-being Palace",
        "父母宮": "Parents Palace",
    }
    for raw, translated in expected.items():
        assert translate_ziwei_palace(raw, "en") == translated
        assert not CJK_RE.search(translated)


def test_all_engine_ziwei_stars_have_english_display_names():
    stars = [
        "紫微", "天機", "太陽", "武曲", "天同", "廉貞", "天府", "太陰",
        "貪狼", "巨門", "天相", "天梁", "七殺", "破軍", "文昌", "文曲",
        "左輔", "右弼", "天魁", "天鉞", "祿存", "天馬", "擎羊", "陀羅",
        "火星", "鈴星", "地空", "地劫",
    ]
    for star in stars:
        translated = translate_ziwei_star(star, "en")
        assert translated != star
        assert not CJK_RE.search(translated)


def test_transformations_translate_standalone_and_combined_values():
    assert translate_ziwei_transformation("化祿", "en") == "Prosperity Transformation"
    translated = translate_ziwei_transformation("太陽化祿", "en")
    assert translated == "Tai Yang — Prosperity Transformation"
    assert not CJK_RE.search(translated)


def test_bureau_translation_remains_language_aware():
    assert translate_ziwei_bureau("土五局", "en") == "Earth Five Bureau"
    assert translate_ziwei_bureau("土五局", "zh-TW") == "土五局"


def test_components_translate_every_ziwei_table_value():
    source = open("ui/components.py", encoding="utf-8").read()
    assert "translate_ziwei_palace(p.name, language)" in source
    assert "translate_ziwei_star(x, language) for x in p.main_stars" in source
    assert "translate_ziwei_star(x, language) for x in aux" in source
    assert "translate_ziwei_star(x, language) for x in sha" in source
    assert "translate_ziwei_transformation(x, language) for x in p.transformations" in source
