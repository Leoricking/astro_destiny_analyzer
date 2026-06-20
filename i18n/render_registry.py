"""Registry of customer-visible translation keys per page."""
from typing import Optional

_REGISTRY: dict = {}


def register_render_key(page_id: str, component_type: str, key: str) -> None:
    if page_id not in _REGISTRY:
        _REGISTRY[page_id] = []
    _REGISTRY[page_id].append({"component_type": component_type, "key": key})


def get_page_keys(page_id: str) -> list:
    return _REGISTRY.get(page_id, [])


def get_all_registered_pages() -> list:
    return list(_REGISTRY.keys())


def verify_page_coverage(page_id: str, language: str) -> tuple:
    """Check what % of registered keys have non-fallback translations."""
    from i18n.translator import get_translation
    keys = get_page_keys(page_id)
    if not keys:
        return 1.0, []
    missing = []
    for entry in keys:
        k = entry["key"]
        val = get_translation(language, k)
        if val == k:
            missing.append(k)
    coverage = 1.0 - len(missing) / len(keys)
    return coverage, missing


# Pre-register known customer-visible keys
_HOME_KEYS = [
    "app.title", "app.subtitle", "home.welcome", "home.metric_systems",
    "home.btn_start_chart", "home.btn_compatibility", "home.btn_history",
    "home.quick_start.title",
]
for _k in _HOME_KEYS:
    register_render_key("home", "title" if "title" in _k else "label", _k)

_INPUT_KEYS = [
    "input.title", "input.basic_info", "input.name", "input.gender",
    "input.birth_date", "input.birth_time_section", "input.submit", "input.clear",
    "location.country_label", "location.city_search_label", "location.confirm_label",
]
for _k in _INPUT_KEYS:
    register_render_key("input", "label", _k)

_CALCULATE_KEYS = [
    "calculate.title", "calculate.no_profile", "calculate.btn_start",
    "calculate.overview", "calculate.tab_western", "calculate.tab_bazi",
    "calculate.tab_ziwei", "calculate.tab_numerology", "calculate.tab_hd",
]
for _k in _CALCULATE_KEYS:
    register_render_key("calculate", "label", _k)

_COMPATIBILITY_KEYS = [
    "compatibility.title", "compatibility.person_a", "compatibility.person_b",
    "compatibility.generate", "compatibility.not_ready",
]
for _k in _COMPATIBILITY_KEYS:
    register_render_key("compatibility", "label", _k)

_SETTINGS_KEYS = [
    "settings.title", "settings.mode_status", "settings.system_info",
    "settings.features", "settings.export_formats",
]
for _k in _SETTINGS_KEYS:
    register_render_key("settings", "label", _k)
