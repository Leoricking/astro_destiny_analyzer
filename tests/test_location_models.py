from location.models import LocationCandidate, ResolvedBirthLocation

def test_location_candidate_fields():
    c = LocationCandidate(country_code="TW", country_name="Taiwan", country_display_name="台灣",
                          city="Taipei", city_display_name="台北", latitude=25.033, longitude=121.565, timezone="Asia/Taipei")
    assert c.country_code == "TW"
    assert c.latitude == 25.033
    assert c.timezone == "Asia/Taipei"
    assert c.source == "builtin"
    assert 0 <= c.confidence <= 1

def test_resolved_birth_location_fields():
    r = ResolvedBirthLocation(country_code="TW", city="Taipei", region=None,
                               latitude=25.033, longitude=121.565, timezone="Asia/Taipei",
                               utc_offset_at_birth=8.0, source="builtin", confidence=0.9, user_confirmed=True)
    assert r.timezone == "Asia/Taipei"
    assert r.utc_offset_at_birth == 8.0
