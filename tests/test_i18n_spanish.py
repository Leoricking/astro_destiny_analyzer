# -*- coding: utf-8 -*-
"""Tests for Spanish (es) locale."""
import pytest
from i18n.locales.es import TRANSLATIONS as ES
from i18n.translator import get_translation, SUPPORTED_LANGUAGES


def test_es_supported():
    assert "es" in SUPPORTED_LANGUAGES


def test_nav_home_es():
    result = get_translation("es", "nav.home")
    assert "Inicio" in result


def test_input_name_es():
    result = get_translation("es", "input.name")
    assert result != "input.name" and len(result) > 0


def test_report_export_es():
    assert get_translation("es", "report.export") != "report.export"


def test_compatibility_title_es():
    assert get_translation("es", "compatibility.title") != "compatibility.title"


def test_settings_title_es():
    assert get_translation("es", "settings.title") != "settings.title"


def test_no_accidental_chinese_in_core_keys():
    for key in ["nav.home", "nav.input", "nav.calculate", "nav.export", "nav.settings"]:
        val = ES.get(key, "")
        assert not any("\u4e00" <= c <= "\u9fff" for c in val)


def test_utf8_spanish_characters():
    all_values = "".join(ES.values())
    assert any(c in all_values for c in "áéíóúñüÁÉÍÓÚÑÜ")


def test_es_locale_non_empty():
    assert len(ES) > 50


def test_es_home_btn_start_chart():
    result = get_translation("es", "home.btn_start_chart")
    assert result != "home.btn_start_chart" and len(result) > 0


def test_es_input_title():
    result = get_translation("es", "input.title")
    assert result != "input.title" and len(result) > 0


def test_es_calculate_title():
    result = get_translation("es", "calculate.title")
    assert result != "calculate.title" and len(result) > 0
