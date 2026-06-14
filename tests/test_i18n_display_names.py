"""Tests for i18n display name translation functions."""
import pytest
from i18n.display_names import (
    translate_gender, translate_hd_type, translate_authority,
    translate_center, translate_zodiac,
)


def test_gender_male_zh_tw():
    assert translate_gender("male", "zh-TW") == "男"


def test_gender_male_en():
    assert translate_gender("male", "en") == "Male"


def test_gender_female_zh_tw():
    assert translate_gender("female", "zh-TW") == "女"


def test_gender_female_en():
    assert translate_gender("female", "en") == "Female"


def test_hd_projector_zh_tw():
    result = translate_hd_type("Projector", "zh-TW")
    assert result == "投射者"


def test_hd_projector_en():
    result = translate_hd_type("Projector", "en")
    assert result == "Projector"


def test_emotional_authority_zh_tw():
    result = translate_authority("Emotional", "zh-TW")
    assert result == "情緒"


def test_emotional_authority_en():
    result = translate_authority("Emotional", "en")
    assert result == "Emotional"


def test_head_center_zh_tw():
    result = translate_center("Head", "zh-TW")
    assert result == "頭腦"


def test_head_center_en():
    result = translate_center("Head", "en")
    assert result == "Head"


def test_aries_zh_tw():
    result = translate_zodiac("Aries", "zh-TW")
    assert result == "牡羊座"


def test_aries_en():
    result = translate_zodiac("Aries", "en")
    assert result == "Aries"


def test_unknown_value_passthrough():
    assert translate_gender("nonexistent", "en") == "nonexistent"
    assert translate_hd_type("UnknownType", "en") == "UnknownType"
    assert translate_zodiac("NotAStar", "en") == "NotAStar"


def test_canonical_value_unchanged():
    # translate_* should never modify the input string, only return translated
    original = "Projector"
    translate_hd_type(original, "zh-TW")
    assert original == "Projector"  # original not mutated
