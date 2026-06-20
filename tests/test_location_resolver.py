from location.resolver import search_cities, resolve_birth_location

def test_tw_taipei():
    results = search_cities("TW", "Taipei", "en")
    assert len(results) > 0
    assert results[0].country_code == "TW"
    assert abs(results[0].latitude - 25.033) < 0.1
    assert abs(results[0].longitude - 121.565) < 0.5
    assert results[0].timezone == "Asia/Taipei"
    assert 0 < results[0].confidence <= 1

def test_jp_tokyo():
    results = search_cities("JP", "Tokyo", "en")
    assert len(results) > 0
    assert results[0].timezone == "Asia/Tokyo"

def test_th_bangkok():
    results = search_cities("TH", "Bangkok", "en")
    assert len(results) > 0
    assert results[0].timezone == "Asia/Bangkok"

def test_us_new_york():
    results = search_cities("US", "New York", "en")
    assert len(results) > 0
    assert results[0].timezone == "America/New_York"

def test_country_code_canonical():
    results = search_cities("TW", "", "en")
    for r in results:
        assert r.country_code == "TW"

def test_latitude_range():
    results = search_cities("TW", "", "en")
    for r in results:
        assert -90 <= r.latitude <= 90

def test_longitude_range():
    results = search_cities("TW", "", "en")
    for r in results:
        assert -180 <= r.longitude <= 180

def test_timezone_iana():
    results = search_cities("TW", "", "en")
    for r in results:
        assert "/" in r.timezone or r.timezone == "UTC"

def test_confidence_range():
    results = search_cities("TW", "", "en")
    for r in results:
        assert 0 <= r.confidence <= 1

def test_manual_fallback():
    results = resolve_birth_location("TW", "", manual_lat=25.0, manual_lon=121.5, use_manual=True)
    assert len(results) > 0
    assert results[0].source == "manual"
    assert results[0].latitude == 25.0

def test_invalid_city_no_crash():
    results = search_cities("TW", "xyznotacity123", "en")
    assert isinstance(results, list)

def test_online_disabled_fallback():
    results = search_cities("TW", "Taipei", "en", enable_online=False)
    assert isinstance(results, list)
