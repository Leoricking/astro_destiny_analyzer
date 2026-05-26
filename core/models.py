"""
Astro Destiny Analyzer — Core Data Models (Pydantic v2)
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date, time
from enum import Enum


# ── Input Enums ──────────────────────────────────────────────────────────────

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class BloodType(str, Enum):
    A = "A"
    B = "B"
    O = "O"
    AB = "AB"
    UNKNOWN = "Unknown"


class AnalysisTheme(str, Enum):
    PERSONALITY = "總體人格"
    LOVE = "感情"
    CAREER = "事業"
    WEALTH = "財富"
    SOCIAL = "人際"
    FAMILY = "家庭"
    CURRENT_YEAR = "今年運勢"
    THREE_YEARS = "未來三年"


class ReportLanguage(str, Enum):
    TRADITIONAL_CHINESE = "繁體中文"
    SIMPLIFIED_CHINESE = "簡體中文"
    ENGLISH = "English"


class ReportLength(str, Enum):
    SHORT = "簡短版"
    STANDARD = "標準版"
    FULL = "萬字完整版"


# ── Birth Profile ─────────────────────────────────────────────────────────────

class BirthProfile(BaseModel):
    name: str
    gender: Optional[Gender] = None
    birth_date: date
    birth_time: Optional[time] = None
    birth_city: str
    birth_country: str
    residence_city: Optional[str] = None
    residence_country: Optional[str] = None
    blood_type: BloodType = BloodType.UNKNOWN
    themes: List[AnalysisTheme] = Field(default_factory=list)
    report_language: ReportLanguage = ReportLanguage.TRADITIONAL_CHINESE
    report_length: ReportLength = ReportLength.STANDARD
    # V1.3.5: location & timezone precision fields
    birth_latitude: Optional[float] = None
    birth_longitude: Optional[float] = None
    birth_timezone: Optional[str] = None
    birth_timezone_offset: Optional[float] = None
    birth_time_is_known: bool = False


# ── Western Astrology Models ──────────────────────────────────────────────────

class ZodiacSign(str, Enum):
    ARIES = "牡羊座"
    TAURUS = "金牛座"
    GEMINI = "雙子座"
    CANCER = "巨蟹座"
    LEO = "獅子座"
    VIRGO = "處女座"
    LIBRA = "天秤座"
    SCORPIO = "天蠍座"
    SAGITTARIUS = "射手座"
    CAPRICORN = "摩羯座"
    AQUARIUS = "水瓶座"
    PISCES = "雙魚座"


class Planet(str, Enum):
    SUN = "太陽"
    MOON = "月亮"
    MERCURY = "水星"
    VENUS = "金星"
    MARS = "火星"
    JUPITER = "木星"
    SATURN = "土星"
    URANUS = "天王星"
    NEPTUNE = "海王星"
    PLUTO = "冥王星"
    NORTH_NODE = "北交點"
    SOUTH_NODE = "南交點"
    CHIRON = "凱龍星"
    LILITH = "莉莉絲"
    PART_OF_FORTUNE = "福點"


class PlanetPosition(BaseModel):
    planet: Planet
    sign: ZodiacSign
    degree: float          # 0–360 ecliptic longitude
    sign_degree: float     # 0–30 within sign
    house: int             # 1–12
    retrograde: bool = False


class AspectType(str, Enum):
    CONJUNCTION = "合相 0°"
    SEXTILE = "六合 60°"
    SQUARE = "刑相 90°"
    TRINE = "拱相 120°"
    QUINCUNX = "梅花相 150°"
    OPPOSITION = "對分 180°"


class Aspect(BaseModel):
    planet1: Planet
    planet2: Planet
    aspect_type: AspectType
    orb: float
    applying: bool = False  # True = applying, False = separating


class HousePosition(BaseModel):
    house_number: int      # 1–12
    sign: ZodiacSign
    cusp_degree: float
    planets: List[Planet] = Field(default_factory=list)


class WesternChart(BaseModel):
    """
    Western astrology chart.
    V1: mock data layer — replace calculate() with real Swiss Ephemeris calls
    when SWISSEPH_DATA_PATH is configured. See engines/western_astrology.py.
    """
    planet_positions: List[PlanetPosition]
    houses: List[HousePosition]
    aspects: List[Aspect]
    ascendant: ZodiacSign
    descendant: ZodiacSign
    mc: ZodiacSign          # 天頂 Midheaven
    ic: ZodiacSign          # 天底 Imum Coeli
    is_mock: bool = True
    calculation_mode: str = "mock_fallback"   # swiss_ephemeris | partial_real | mock_fallback
    accuracy_note: str = ""
    ascendant_accuracy: str = "unknown"       # "precise" | "unknown"
    mc_accuracy: str = "unknown"              # "precise" | "unknown"
    location_source: str = "not_provided"     # "provided" | "city_lookup" | "not_provided"
    timezone_source: str = "default_utc8"     # "provided" | "default_utc8"


# ── BaZi (Eight Characters) Models ───────────────────────────────────────────

class HeavenlyStem(str, Enum):
    JIA  = "甲"
    YI   = "乙"
    BING = "丙"
    DING = "丁"
    WU   = "戊"
    JI   = "己"
    GENG = "庚"
    XIN  = "辛"
    REN  = "壬"
    GUI  = "癸"


class EarthlyBranch(str, Enum):
    ZI   = "子"
    CHOU = "丑"
    YIN  = "寅"
    MAO  = "卯"
    CHEN = "辰"
    SI   = "巳"
    WU_  = "午"   # avoid clash with WU stem
    WEI  = "未"
    SHEN = "申"
    YOU  = "酉"
    XU   = "戌"
    HAI  = "亥"


class FiveElement(str, Enum):
    WOOD  = "木"
    FIRE  = "火"
    EARTH = "土"
    METAL = "金"
    WATER = "水"


class TenGod(str, Enum):
    ZHENGCAI  = "正財"
    PIANCAI   = "偏財"
    ZHENGGUAN = "正官"
    QIANGUAN  = "七殺"
    ZHENGYIN  = "正印"
    PIANYIN   = "偏印"
    SHISHEN   = "食神"
    SHANGGUAN = "傷官"
    BIJIAN    = "比肩"
    JIECAI    = "劫財"


class Pillar(BaseModel):
    heavenly_stem: HeavenlyStem
    earthly_branch: EarthlyBranch
    element: FiveElement           # element of the heavenly stem
    label: str                     # 年柱 / 月柱 / 日柱 / 時柱


class LuckPeriod(BaseModel):
    start_age: int
    end_age: int
    stem: HeavenlyStem
    branch: EarthlyBranch
    label: str


class AnnualLuck(BaseModel):
    year: int
    stem: HeavenlyStem
    branch: EarthlyBranch


class BaZiChart(BaseModel):
    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Optional[Pillar]
    day_master: HeavenlyStem
    day_master_element: FiveElement
    five_element_ratio: Dict[str, float]      # element.value -> percentage
    five_element_strength: Dict[str, str]     # element.value -> "強/弱/均衡"
    favorable_elements: List[FiveElement]
    unfavorable_elements: List[FiveElement]
    wealth_star: Optional[TenGod]
    power_star: Optional[TenGod]
    print_star: Optional[TenGod]
    output_star: Optional[TenGod]
    sibling_star: Optional[TenGod]
    ten_gods_map: Dict[str, str]              # stem.value -> TenGod.value
    da_yun: List[LuckPeriod] = Field(default_factory=list)
    liu_nian: List[AnnualLuck] = Field(default_factory=list)
    is_mock: bool = False


# ── Zi Wei Dou Shu Models ─────────────────────────────────────────────────────

class ZiWeiPalace(BaseModel):
    name: str
    earthly_branch: str = ""
    main_stars: List[str] = Field(default_factory=list)
    minor_stars: List[str] = Field(default_factory=list)
    transformations: List[str] = Field(default_factory=list)   # 四化
    interpretation: str = ""


class ZiWeiChart(BaseModel):
    """
    Zi Wei Dou Shu chart.
    V1: mock data layer — replace with full 紫微排盤 algorithm.
    """
    ming_palace:    ZiWeiPalace   # 命宮
    shen_palace:    ZiWeiPalace   # 身宮
    brother_palace: ZiWeiPalace   # 兄弟宮
    spouse_palace:  ZiWeiPalace   # 夫妻宮
    children_palace: ZiWeiPalace  # 子女宮
    wealth_palace:  ZiWeiPalace   # 財帛宮
    health_palace:  ZiWeiPalace   # 疾厄宮
    travel_palace:  ZiWeiPalace   # 遷移宮
    friends_palace: ZiWeiPalace   # 交友宮
    career_palace:  ZiWeiPalace   # 官祿宮
    property_palace: ZiWeiPalace  # 田宅宮
    fortune_palace: ZiWeiPalace   # 福德宮
    parents_palace: ZiWeiPalace   # 父母宮
    main_stars: List[str] = Field(default_factory=list)
    four_transformations: Dict[str, str] = Field(default_factory=dict)  # star -> 化祿/化權/化科/化忌
    is_mock: bool = True


# ── Blood Type Models ─────────────────────────────────────────────────────────

class BloodTypeAnalysis(BaseModel):
    blood_type: BloodType
    interpersonal_style: str
    love_response: str
    stress_response: str
    workplace_cooperation: str
    money_attitude: str
    integration_notes: str = ""


# ── Numerology Models ─────────────────────────────────────────────────────────

class NumerologyChart(BaseModel):
    life_path_number: int
    birthday_number: int
    talent_number: int
    personal_year: int
    personal_month: Optional[int] = None       # 保留
    challenge_numbers: List[int] = Field(default_factory=list)   # 保留
    peak_cycles: List[Dict] = Field(default_factory=list)         # 保留
    life_path_description: str = ""
    birthday_description: str = ""
    talent_description: str = ""
    personal_year_description: str = ""


# ── Synthesis Result ──────────────────────────────────────────────────────────

class SynthesisResult(BaseModel):
    core_personality: str = ""
    emotional_pattern: str = ""
    action_pattern: str = ""
    love_pattern: str = ""
    career_pattern: str = ""
    wealth_pattern: str = ""
    social_pattern: str = ""
    family_security: str = ""
    stress_shadow: str = ""
    life_lessons: str = ""
    innate_gifts: str = ""
    recurring_challenges: str = ""
    suitable_careers: List[str] = Field(default_factory=list)
    suitable_love_styles: List[str] = Field(default_factory=list)
    one_year_advice: str = ""
    three_year_advice: str = ""
    contradictions: List[str] = Field(default_factory=list)
    integration_suggestions: List[str] = Field(default_factory=list)


# ── Full Report Container ─────────────────────────────────────────────────────

class FullReport(BaseModel):
    profile: BirthProfile
    western_chart: Optional[WesternChart] = None
    bazi_chart: Optional[BaZiChart] = None
    ziwei_chart: Optional[ZiWeiChart] = None
    blood_type_analysis: Optional[BloodTypeAnalysis] = None
    numerology_chart: Optional[NumerologyChart] = None
    synthesis: Optional[SynthesisResult] = None
    created_at: Optional[str] = None
    report_id: Optional[int] = None
