# -*- coding: utf-8 -*-
"""UI i18n helper utilities."""
from i18n.translator import t, DEFAULT_LANGUAGE


def translated_boolean(value: bool, language: str) -> str:
    return t("common.yes" if value else "common.no", language=language)


def translated_mode_name(mode: str, language: str) -> str:
    key_map = {"customer": "mode.customer", "consultant": "mode.consultant", "developer": "mode.developer"}
    return t(key_map.get(mode, f"mode.{mode}"), language=language, default=mode)


def translated_page_label(page_id: str, language: str) -> str:
    return t(f"nav.{page_id}", language=language, default=page_id)
