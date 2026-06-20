from dataclasses import dataclass, field
from typing import Optional

@dataclass
class LocationCandidate:
    country_code: str          # ISO 3166-1 alpha-2, e.g. "TW"
    country_name: str          # English canonical
    country_display_name: str  # localized display
    city: str                  # canonical city name
    city_display_name: str     # localized display
    region: Optional[str] = None
    latitude: float = 0.0
    longitude: float = 0.0
    timezone: str = ""         # IANA, e.g. "Asia/Taipei"
    source: str = "builtin"    # "builtin", "geocoding", "manual"
    confidence: float = 1.0    # 0-1
    formatted_address: str = ""
    is_confirmed: bool = False

@dataclass
class ResolvedBirthLocation:
    country_code: str
    city: str
    region: Optional[str]
    latitude: float
    longitude: float
    timezone: str              # IANA
    utc_offset_at_birth: float # hours, e.g. 8.0 or -5.0
    source: str
    confidence: float
    user_confirmed: bool
    resolution_notes: str = ""
    warnings: list = field(default_factory=list)
