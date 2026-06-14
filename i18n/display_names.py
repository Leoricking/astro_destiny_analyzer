"""
Display name translations for canonical enum values.
Never mutate the stored canonical values — only translate at display layer.
"""
from .translator import get_translation

# Canonical → translation key mapping
_GENDER_KEYS = {
    "male": "display.gender.male",
    "female": "display.gender.female",
    "other": "display.gender.other",
    "unknown": "display.gender.unknown",
}

_HD_TYPE_KEYS = {
    "Manifestor": "display.hd_type.manifestor",
    "Generator": "display.hd_type.generator",
    "Manifesting Generator": "display.hd_type.manifesting_generator",
    "Projector": "display.hd_type.projector",
    "Reflector": "display.hd_type.reflector",
}

_AUTHORITY_KEYS = {
    "Emotional": "display.authority.emotional",
    "Sacral": "display.authority.sacral",
    "Splenic": "display.authority.splenic",
    "Ego": "display.authority.ego",
    "Self-Projected": "display.authority.self_projected",
    "Mental / Environmental": "display.authority.mental_environmental",
    "Lunar": "display.authority.lunar",
}

_CENTER_KEYS = {
    "Head": "display.center.head",
    "Ajna": "display.center.ajna",
    "Throat": "display.center.throat",
    "G": "display.center.g",
    "Heart": "display.center.heart",
    "Sacral": "display.center.sacral",
    "Solar Plexus": "display.center.solar_plexus",
    "Spleen": "display.center.spleen",
    "Root": "display.center.root",
}

_ZODIAC_KEYS = {
    "Aries": "display.zodiac.aries",
    "Taurus": "display.zodiac.taurus",
    "Gemini": "display.zodiac.gemini",
    "Cancer": "display.zodiac.cancer",
    "Leo": "display.zodiac.leo",
    "Virgo": "display.zodiac.virgo",
    "Libra": "display.zodiac.libra",
    "Scorpio": "display.zodiac.scorpio",
    "Sagittarius": "display.zodiac.sagittarius",
    "Capricorn": "display.zodiac.capricorn",
    "Aquarius": "display.zodiac.aquarius",
    "Pisces": "display.zodiac.pisces",
}


def _translate(key_map: dict, value: str, language: str) -> str:
    key = key_map.get(value)
    if key is None:
        return value
    result = get_translation(language, key)
    return result if result != key else value


def translate_gender(value: str, language: str) -> str:
    return _translate(_GENDER_KEYS, value, language)


def translate_hd_type(value: str, language: str) -> str:
    return _translate(_HD_TYPE_KEYS, value, language)


def translate_authority(value: str, language: str) -> str:
    return _translate(_AUTHORITY_KEYS, value, language)


def translate_center(value: str, language: str) -> str:
    return _translate(_CENTER_KEYS, value, language)


def translate_zodiac(value: str, language: str) -> str:
    return _translate(_ZODIAC_KEYS, value, language)
