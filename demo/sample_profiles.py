"""
Astro Destiny Analyzer — Demo Sample Profiles
Ready-to-use BirthProfile instances for quick demo and testing.
These profiles are NOT written to the database unless the user clicks Calculate.
V1.7.0: Added SAMPLE_COUPLES for compatibility demo.
"""
from datetime import date, time
from typing import List, Dict

from core.models import (
    BirthProfile, BloodType, AnalysisTheme, Gender,
    ReportLanguage, ReportLength,
)


# ── Sample 1: 台北精準時間 (known birth time + location) ──────────────────────
sample_taipei_known_time = BirthProfile(
    name="Demo 台北精準時間",
    gender=None,
    birth_date=date(1990, 2, 5),
    birth_time=time(12, 30),
    birth_city="台北",
    birth_country="台灣",
    blood_type=BloodType.O,
    themes=list(AnalysisTheme),
    report_language=ReportLanguage.TRADITIONAL_CHINESE,
    report_length=ReportLength.STANDARD,
    birth_latitude=25.0330,
    birth_longitude=121.5654,
    birth_timezone_offset=8.0,
    birth_time_is_known=True,
)

# ── Sample 2: 新竹科技職涯 (career / wealth focused, full report) ─────────────
sample_hsinchu_tech_career = BirthProfile(
    name="Demo 新竹科技職涯",
    gender=None,
    birth_date=date(1989, 9, 21),
    birth_time=time(11, 5),
    birth_city="新竹",
    birth_country="台灣",
    blood_type=BloodType.A,
    themes=[
        AnalysisTheme.PERSONALITY,
        AnalysisTheme.CAREER,
        AnalysisTheme.WEALTH,
        AnalysisTheme.CURRENT_YEAR,
        AnalysisTheme.THREE_YEARS,
    ],
    report_language=ReportLanguage.TRADITIONAL_CHINESE,
    report_length=ReportLength.FULL,
    birth_latitude=24.8138,
    birth_longitude=120.9675,
    birth_timezone_offset=8.0,
    birth_time_is_known=True,
)

# ── Sample 3: 未知出生時間 (no birth time, tests partial-layout path) ─────────
sample_unknown_time = BirthProfile(
    name="Demo 未知出生時間",
    gender=None,
    birth_date=date(1995, 6, 15),
    birth_time=None,
    birth_city="台中",
    birth_country="台灣",
    blood_type=BloodType.UNKNOWN,
    themes=list(AnalysisTheme),
    report_language=ReportLanguage.TRADITIONAL_CHINESE,
    report_length=ReportLength.STANDARD,
    birth_latitude=24.1477,
    birth_longitude=120.6736,
    birth_timezone_offset=8.0,
    birth_time_is_known=False,
)

# ── Ordered list for UI iteration ─────────────────────────────────────────────
SAMPLE_PROFILES: List[BirthProfile] = [
    sample_taipei_known_time,
    sample_hsinchu_tech_career,
    sample_unknown_time,
]

# Human-readable labels for UI buttons (same order as SAMPLE_PROFILES)
SAMPLE_LABELS: List[str] = [
    "Demo 台北精準時間",
    "Demo 新竹科技職涯",
    "Demo 未知出生時間",
]


# ══════════════════════════════════════════════════════════════════════════════
# Compatibility demo profiles
# ══════════════════════════════════════════════════════════════════════════════

# Romantic couple — A: sample_hsinchu_tech_career, B: new profile
sample_romantic_partner_b = BirthProfile(
    name="Demo 情侶B 高雄創意",
    gender=Gender.FEMALE,
    birth_date=date(1991, 3, 8),
    birth_time=time(9, 45),
    birth_city="高雄",
    birth_country="台灣",
    blood_type=BloodType.B,
    themes=list(AnalysisTheme),
    report_language=ReportLanguage.TRADITIONAL_CHINESE,
    report_length=ReportLength.STANDARD,
    birth_latitude=22.6273,
    birth_longitude=120.3014,
    birth_timezone_offset=8.0,
    birth_time_is_known=True,
)

# Business partners — two distinct profiles
sample_business_partner_a = BirthProfile(
    name="Demo 合夥人A 台北策略",
    gender=None,
    birth_date=date(1985, 11, 14),
    birth_time=time(8, 20),
    birth_city="台北",
    birth_country="台灣",
    blood_type=BloodType.A,
    themes=[
        AnalysisTheme.PERSONALITY,
        AnalysisTheme.CAREER,
        AnalysisTheme.WEALTH,
        AnalysisTheme.SOCIAL,
    ],
    report_language=ReportLanguage.TRADITIONAL_CHINESE,
    report_length=ReportLength.STANDARD,
    birth_latitude=25.0330,
    birth_longitude=121.5654,
    birth_timezone_offset=8.0,
    birth_time_is_known=True,
)

sample_business_partner_b = BirthProfile(
    name="Demo 合夥人B 台中執行",
    gender=None,
    birth_date=date(1987, 5, 2),
    birth_time=time(14, 30),
    birth_city="台中",
    birth_country="台灣",
    blood_type=BloodType.O,
    themes=[
        AnalysisTheme.PERSONALITY,
        AnalysisTheme.CAREER,
        AnalysisTheme.WEALTH,
        AnalysisTheme.SOCIAL,
    ],
    report_language=ReportLanguage.TRADITIONAL_CHINESE,
    report_length=ReportLength.STANDARD,
    birth_latitude=24.1477,
    birth_longitude=120.6736,
    birth_timezone_offset=8.0,
    birth_time_is_known=True,
)

# ── Parent-child demo profiles ─────────────────────────────────────────────────
sample_parent_a = BirthProfile(
    name="Demo 親A 台北父母",
    gender=None,
    birth_date=date(1965, 7, 20),
    birth_time=time(6, 30),
    birth_city="台北",
    birth_country="台灣",
    blood_type=BloodType.A,
    themes=list(AnalysisTheme),
    report_language=ReportLanguage.TRADITIONAL_CHINESE,
    report_length=ReportLength.STANDARD,
    birth_latitude=25.0330,
    birth_longitude=121.5654,
    birth_timezone_offset=8.0,
    birth_time_is_known=True,
)

sample_child_b = BirthProfile(
    name="Demo 子B 台北子女",
    gender=None,
    birth_date=date(1995, 4, 10),
    birth_time=time(15, 0),
    birth_city="台北",
    birth_country="台灣",
    blood_type=BloodType.B,
    themes=list(AnalysisTheme),
    report_language=ReportLanguage.TRADITIONAL_CHINESE,
    report_length=ReportLength.STANDARD,
    birth_latitude=25.0330,
    birth_longitude=121.5654,
    birth_timezone_offset=8.0,
    birth_time_is_known=True,
)

# ── Sample couples list ────────────────────────────────────────────────────────
# Each entry: {"label", "description", "best_for_demo", "talking_points",
#              "relationship_type", "person_a", "person_b"}
SAMPLE_COUPLES: List[Dict] = [
    {
        "label": "Demo 情侶合盤：高張力高成長型",
        "description": "用來展示情緒安全感、吸引力、衝突修復與長期磨合。適合示範合盤分析的核心價值。",
        "best_for_demo": "romantic",
        "talking_points": [
            "看 overall_score 不夠，要看 conflict_score + growth_score 的組合。",
            "月亮與金星火星代表親密節奏與情緒安全感的語言。",
            "八字五行互補代表生活能量是否互相滋養。",
            "紫微命宮 / 夫妻宮提示長期互動模式與角色傾向。",
        ],
        "person_a": sample_hsinchu_tech_career,
        "person_b": sample_romantic_partner_b,
        "relationship_type": "romantic",
    },
    {
        "label": "Demo 合作夥伴：策略 × 執行互補型",
        "description": "用來展示決策分工、權責界線、財務風險與合作節奏。適合展示商業合夥場景。",
        "best_for_demo": "business",
        "talking_points": [
            "合作不只看合不合，而是看分工能否清楚、決策流程是否順暢。",
            "衝突分數高可能代表決策張力，在合作關係中不一定是壞事。",
            "官祿宮 / 財帛宮 / 交友宮適合看合作模式與財務互動。",
            "30 天練習可轉成合作規則文件，建立書面共識。",
        ],
        "person_a": sample_business_partner_a,
        "person_b": sample_business_partner_b,
        "relationship_type": "business",
    },
    {
        "label": "Demo 親子關係：支持與界線型",
        "description": "用來展示親子期待落差、支持與控制的界線、成長節奏的差異。",
        "best_for_demo": "parent_child",
        "talking_points": [
            "親子合盤重點不在「合不合」，而在理解期待落差的來源。",
            "父母的喜用神與孩子的日主是否相剋，反映壓力互動模式。",
            "紫微父母宮 / 子女宮可以看雙方的互動期待。",
            "30 天練習可以幫助親子建立更清楚的溝通節奏。",
        ],
        "person_a": sample_parent_a,
        "person_b": sample_child_b,
        "relationship_type": "parent_child",
    },
]
