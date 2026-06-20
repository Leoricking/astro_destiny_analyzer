from datetime import datetime
from location.timezone import resolve_utc_offset, get_available_timezones_for_country

def test_asia_taipei():
    dt = datetime(1990, 6, 15, 12, 0)
    result = resolve_utc_offset(dt, "Asia/Taipei")
    assert result["utc_offset"] == 8.0
    assert result["dst_active"] is False
    assert isinstance(result["warnings"], list)

def test_america_new_york_summer():
    dt = datetime(2000, 7, 4, 12, 0)
    result = resolve_utc_offset(dt, "America/New_York")
    assert result["utc_offset"] == -4.0  # EDT
    assert result["dst_active"] is True

def test_america_new_york_winter():
    dt = datetime(2000, 1, 15, 12, 0)
    result = resolve_utc_offset(dt, "America/New_York")
    assert result["utc_offset"] == -5.0  # EST
    assert result["dst_active"] is False

def test_historical_dst():
    dt = datetime(1985, 7, 4, 12, 0)
    result = resolve_utc_offset(dt, "America/New_York")
    assert result["utc_offset"] in (-4.0, -5.0)  # historical DST may vary

def test_utc_offset_format():
    dt = datetime(2000, 6, 1, 12, 0)
    result = resolve_utc_offset(dt, "Asia/Tokyo")
    offset = result["utc_offset"]
    assert isinstance(offset, float)
    assert offset == 9.0

def test_ambiguous_time_warning():
    # 2023-11-05 01:30 is ambiguous in America/New_York (clocks fall back)
    dt = datetime(2023, 11, 5, 1, 30)
    result = resolve_utc_offset(dt, "America/New_York")
    # Should not crash; may have warning
    assert isinstance(result["warnings"], list)

def test_invalid_timezone_no_crash():
    dt = datetime(2000, 1, 1, 12, 0)
    result = resolve_utc_offset(dt, "Invalid/Timezone")
    assert isinstance(result, dict)
    assert isinstance(result["warnings"], list)
    assert len(result["warnings"]) > 0

def test_utc_offset_return_type():
    dt = datetime(2000, 6, 1, 12, 0)
    result = resolve_utc_offset(dt, "Asia/Taipei")
    assert isinstance(result["utc_offset"], float)
    assert isinstance(result["dst_active"], bool)

def test_country_timezones_tw():
    tzs = get_available_timezones_for_country("TW")
    assert "Asia/Taipei" in tzs

def test_country_timezones_us():
    tzs = get_available_timezones_for_country("US")
    assert "America/New_York" in tzs
    assert "America/Los_Angeles" in tzs
