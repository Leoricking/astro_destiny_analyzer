"""Location input validation."""

def validate_country_code(code: str) -> tuple:
    from .countries import COUNTRIES
    if not code:
        return False, "Country is required."
    if code.upper() not in COUNTRIES:
        return False, f"Unknown country code: {code!r}"
    return True, ""

def validate_coordinates(lat: float, lon: float) -> tuple:
    if not (-90 <= lat <= 90):
        return False, f"Latitude must be between -90 and 90, got {lat}"
    if not (-180 <= lon <= 180):
        return False, f"Longitude must be between -180 and 180, got {lon}"
    return True, ""
