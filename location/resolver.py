"""Location resolution — combines builtin data + optional online geocoding."""
from .models import LocationCandidate
from .cities import search_builtin_cities, get_city_display_name, BUILTIN_CITIES
from .countries import COUNTRIES


def search_cities(
    country_code: str,
    query: str = "",
    language: str = "en",
    enable_online: bool = False,
) -> list:
    """Search for cities. Returns list of LocationCandidate."""
    candidates = []

    # First: search built-in data
    builtin_results = search_builtin_cities(country_code, query, language)
    for r in builtin_results:
        display = get_city_display_name(r, language)
        country_names = COUNTRIES.get(country_code.upper(), {})
        lang_key_map = {"zh-TW": "zh_tw", "en": "en", "th": "th", "ja": "ja", "es": "es", "ar": "ar"}
        lk = lang_key_map.get(language, "en")
        candidates.append(LocationCandidate(
            country_code=country_code.upper(),
            country_name=country_names.get("en", country_code),
            country_display_name=country_names.get(lk) or country_names.get("en") or country_code,
            city=r.city,
            city_display_name=display,
            region=r.region,
            latitude=r.latitude,
            longitude=r.longitude,
            timezone=r.timezone,
            source="builtin",
            confidence=0.9,
            formatted_address=f"{display}, {country_names.get(lk) or country_code}",
        ))

    # Optional: online geocoding (Nominatim)
    if enable_online and not candidates:
        try:
            candidates.extend(_search_nominatim(country_code, query, language))
        except Exception:
            pass  # fail silently, fallback to empty

    return candidates


def _search_nominatim(country_code: str, query: str, language: str) -> list:
    """Optional Nominatim geocoding. Only called when enable_online=True."""
    import urllib.request
    import urllib.parse
    import json

    params = urllib.parse.urlencode({
        "q": f"{query}, {country_code}",
        "countrycodes": country_code.lower(),
        "format": "json",
        "limit": 5,
        "addressdetails": 1,
        "accept-language": language[:2],
    })
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "AstroDestinyAnalyzer/2.0.6"})

    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    results = []
    country_names = COUNTRIES.get(country_code.upper(), {})
    for item in data[:5]:
        try:
            lat = float(item["lat"])
            lon = float(item["lon"])
            display_name = item.get("display_name", query)
            city = item.get("address", {}).get("city") or item.get("address", {}).get("town") or query
            results.append(LocationCandidate(
                country_code=country_code.upper(),
                country_name=country_names.get("en", country_code),
                country_display_name=country_names.get("en", country_code),
                city=city,
                city_display_name=city,
                latitude=lat,
                longitude=lon,
                timezone="",  # will be inferred later
                source="geocoding",
                confidence=0.7,
                formatted_address=display_name,
            ))
        except Exception:
            continue
    return results


def resolve_birth_location(
    country_code: str,
    city_query: str,
    manual_lat: float = 0.0,
    manual_lon: float = 0.0,
    manual_tz: str = "",
    use_manual: bool = False,
    language: str = "en",
    enable_online: bool = False,
) -> list:
    """Main entry point: resolve birth location to candidates."""
    if use_manual and (manual_lat != 0.0 or manual_lon != 0.0):
        from .timezone import try_infer_timezone_from_coordinates
        tz = manual_tz or try_infer_timezone_from_coordinates(manual_lat, manual_lon) or "UTC"
        country_names = COUNTRIES.get(country_code.upper(), {})
        lk = {"zh-TW": "zh_tw", "en": "en", "th": "th", "ja": "ja", "es": "es", "ar": "ar"}.get(language, "en")
        return [LocationCandidate(
            country_code=country_code.upper(),
            country_name=country_names.get("en", country_code),
            country_display_name=country_names.get(lk) or country_code,
            city=city_query or "Custom",
            city_display_name=city_query or "Custom",
            latitude=manual_lat,
            longitude=manual_lon,
            timezone=tz,
            source="manual",
            confidence=0.95,
            formatted_address=f"{city_query or 'Custom'}, {country_code}",
        )]

    return search_cities(country_code, city_query, language, enable_online)
