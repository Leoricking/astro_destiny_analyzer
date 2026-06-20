"""IANA timezone resolution and historical UTC offset calculation."""
from datetime import datetime
from typing import Optional
try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:
    from backports.zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def resolve_utc_offset(
    birth_datetime_local: datetime,
    timezone_name: str,
) -> dict:
    """
    Calculate UTC offset for a given local datetime in a given IANA timezone.
    Handles historical DST correctly.
    Returns dict with: utc_offset (float hours), dst_active (bool), warnings (list)
    """
    warnings = []
    try:
        tz = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, Exception):
        warnings.append(f"Unknown timezone: {timezone_name!r}. Using UTC+0.")
        return {"utc_offset": 0.0, "dst_active": False, "warnings": warnings}

    # Attach timezone to the naive datetime
    try:
        aware_dt = birth_datetime_local.replace(tzinfo=tz)
        utc_offset_td = aware_dt.utcoffset()
        if utc_offset_td is None:
            warnings.append("Could not determine UTC offset.")
            return {"utc_offset": 0.0, "dst_active": False, "warnings": warnings}

        utc_offset_hours = utc_offset_td.total_seconds() / 3600.0

        # Check DST
        dst = aware_dt.dst()
        dst_active = dst is not None and dst.total_seconds() != 0

        # Check for potentially ambiguous time (near DST transition)
        # Try fold=1 and see if offset differs
        aware_dt_fold1 = birth_datetime_local.replace(tzinfo=tz, fold=1)
        utc_offset_fold1 = aware_dt_fold1.utcoffset()
        if utc_offset_fold1 != utc_offset_td:
            warnings.append(
                f"This local time is ambiguous (DST transition). "
                f"Using earlier interpretation (UTC{utc_offset_hours:+.1f}). "
                f"Alternative: UTC{utc_offset_fold1.total_seconds()/3600:+.1f}."
            )

        return {
            "utc_offset": utc_offset_hours,
            "dst_active": dst_active,
            "warnings": warnings,
        }
    except Exception as e:
        warnings.append(f"Error calculating UTC offset: {e}")
        return {"utc_offset": 0.0, "dst_active": False, "warnings": warnings}


def get_available_timezones_for_country(country_code: str) -> list:
    """Return common IANA timezones for a country code."""
    _TZ_MAP = {
        "TW": ["Asia/Taipei"],
        "JP": ["Asia/Tokyo"],
        "TH": ["Asia/Bangkok"],
        "US": ["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles", "America/Anchorage", "Pacific/Honolulu"],
        "CA": ["America/Toronto", "America/Vancouver", "America/Edmonton", "America/Winnipeg", "America/Halifax"],
        "GB": ["Europe/London"],
        "AU": ["Australia/Sydney", "Australia/Melbourne", "Australia/Brisbane", "Australia/Perth", "Australia/Adelaide"],
        "NZ": ["Pacific/Auckland"],
        "CN": ["Asia/Shanghai"],
        "HK": ["Asia/Hong_Kong"],
        "MO": ["Asia/Macau"],
        "SG": ["Asia/Singapore"],
        "KR": ["Asia/Seoul"],
        "IN": ["Asia/Kolkata"],
        "FR": ["Europe/Paris"],
        "DE": ["Europe/Berlin"],
        "ES": ["Europe/Madrid"],
        "IT": ["Europe/Rome"],
        "BR": ["America/Sao_Paulo", "America/Manaus", "America/Fortaleza"],
        "MX": ["America/Mexico_City"],
        "AE": ["Asia/Dubai"],
        "SA": ["Asia/Riyadh"],
        "EG": ["Africa/Cairo"],
        "MY": ["Asia/Kuala_Lumpur"],
        "PH": ["Asia/Manila"],
        "VN": ["Asia/Ho_Chi_Minh"],
        "ID": ["Asia/Jakarta", "Asia/Makassar", "Asia/Jayapura"],
    }
    return _TZ_MAP.get(country_code, ["UTC"])


def try_infer_timezone_from_coordinates(lat: float, lon: float) -> Optional[str]:
    """Try to infer IANA timezone from coordinates using timezonefinder if available."""
    try:
        from timezonefinder import TimezoneFinder
        tf = TimezoneFinder()
        result = tf.timezone_at(lat=lat, lng=lon)
        return result
    except ImportError:
        return None
    except Exception:
        return None
