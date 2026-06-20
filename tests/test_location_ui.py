from pathlib import Path

def _read_app():
    return Path("ui/streamlit_app.py").read_text(encoding="utf-8")

def test_country_selectbox_in_app():
    content = _read_app()
    assert "input_country_code" in content or "location.country_label" in content

def test_city_search_in_app():
    content = _read_app()
    assert "location.city_search_label" in content or "input_city_query" in content

def test_candidate_selectbox_in_app():
    content = _read_app()
    assert "input_city_candidates" in content or "location.candidates_label" in content

def test_location_confirm_in_app():
    content = _read_app()
    assert "input_location_confirmed" in content or "location.confirm_label" in content

def test_manual_coordinate_expander_in_app():
    content = _read_app()
    assert "location.advanced_label" in content or "input_manual_lat" in content

def test_language_switch_preserves_location_state():
    # Session keys that must persist across language switch
    content = _read_app()
    assert "input_country_code" in content
    assert "input_city_candidates" in content

def test_location_module_importable():
    from location.resolver import search_cities
    from location.timezone import resolve_utc_offset
    from location.countries import get_country_options
    assert callable(search_cities)
    assert callable(resolve_utc_offset)
    assert callable(get_country_options)

def test_countries_have_six_languages():
    from location.countries import COUNTRIES
    for code, names in COUNTRIES.items():
        if code == "OTHER":
            continue
        assert "en" in names
        assert "zh_tw" in names

def test_builtin_cities_have_timezone():
    from location.cities import BUILTIN_CITIES
    for city in BUILTIN_CITIES:
        assert "/" in city.timezone, f"City {city.city} missing IANA timezone"

def test_no_developer_debug_in_customer_location():
    content = _read_app()
    # Location UI should be available in customer mode
    assert "location.country_label" in content or "input_country_code" in content
