from core.models import Planet
from i18n.display_names import translate_planet


EXPECTED = {
    "en": {
        Planet.NORTH_NODE.value: "North Node",
        Planet.SOUTH_NODE.value: "South Node",
        Planet.CHIRON.value: "Chiron",
        Planet.LILITH.value: "Lilith",
        Planet.PART_OF_FORTUNE.value: "Part of Fortune",
    },
    "ja": {
        Planet.NORTH_NODE.value: "ドラゴンヘッド",
        Planet.SOUTH_NODE.value: "ドラゴンテイル",
        Planet.CHIRON.value: "キロン",
        Planet.LILITH.value: "リリス",
        Planet.PART_OF_FORTUNE.value: "パート・オブ・フォーチュン",
    },
    "th": {
        Planet.NORTH_NODE.value: "โหนดเหนือ",
        Planet.SOUTH_NODE.value: "โหนดใต้",
        Planet.CHIRON.value: "ไครอน",
        Planet.LILITH.value: "ลิลิธ",
        Planet.PART_OF_FORTUNE.value: "จุดโชคลาภ",
    },
    "es": {
        Planet.NORTH_NODE.value: "Nodo Norte",
        Planet.SOUTH_NODE.value: "Nodo Sur",
        Planet.CHIRON.value: "Quirón",
        Planet.LILITH.value: "Lilith",
        Planet.PART_OF_FORTUNE.value: "Parte de la Fortuna",
    },
    "ar": {
        Planet.NORTH_NODE.value: "العقدة الشمالية",
        Planet.SOUTH_NODE.value: "العقدة الجنوبية",
        Planet.CHIRON.value: "كيرون",
        Planet.LILITH.value: "ليليث",
        Planet.PART_OF_FORTUNE.value: "سهم السعادة",
    },
}


def test_all_planet_enum_values_have_nonempty_labels_for_all_locales():
    for language in ("zh-TW", "en", "ja", "th", "es", "ar"):
        for planet in Planet:
            assert translate_planet(planet.value, language).strip()


def test_special_points_are_localized_in_every_non_chinese_locale():
    for language, mapping in EXPECTED.items():
        for raw, expected in mapping.items():
            assert translate_planet(raw, language) == expected


def test_english_special_points_do_not_fall_back_to_chinese():
    chinese_values = {p.value for p in Planet}
    for planet in (
        Planet.NORTH_NODE,
        Planet.SOUTH_NODE,
        Planet.CHIRON,
        Planet.LILITH,
        Planet.PART_OF_FORTUNE,
    ):
        rendered = translate_planet(planet.value, "en")
        assert rendered not in chinese_values


def test_common_aliases_resolve_to_same_canonical_label():
    assert translate_planet("True North Node", "en") == "North Node"
    assert translate_planet("Black Moon Lilith", "es") == "Lilith"
    assert translate_planet("Fortuna", "ja") == "パート・オブ・フォーチュン"
