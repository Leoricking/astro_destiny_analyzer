"""Display helpers for location accuracy card."""
from i18n.translator import get_translation

def get_accuracy_level(confidence: float, has_city: bool, has_coords: bool, user_confirmed: bool) -> str:
    if confidence >= 0.85 and has_coords and user_confirmed:
        return "high"
    elif confidence >= 0.5 and has_city:
        return "medium"
    else:
        return "low"

def get_accuracy_label(level: str, language: str) -> str:
    key = f"location.accuracy_{level}"
    return get_translation(language, key)

def format_location_summary(candidate, language: str) -> str:
    parts = []
    if candidate.city_display_name:
        parts.append(candidate.city_display_name)
    if candidate.country_display_name:
        parts.append(candidate.country_display_name)
    return ", ".join(parts)
