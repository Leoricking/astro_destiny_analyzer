"""
Astro Destiny Analyzer — Zi Wei Dou Shu (紫微斗數) Engine
V1.5.0: Formal Layout Phase 1.
  - Lunar date conversion via lunardate package (fallback to mock if unavailable).
  - 命宮 / 身宮 from lunar month + birth hour.
  - 五行局 from 命宮 stem/branch nayin.
  - 紫微 / 天府 placement.
  - 十四主星 安星.
  - 生年四化.
  - calculation_mode: "formal_layout_phase1" | "partial_lunar_only" | "mock_fallback"

Limitations (TODO for future versions):
  - 輔星 / 煞星 not yet placed.
  - 大限 / 流年 / 流月 not yet implemented.
  - 閏月 treated conservatively (is_leap_month recorded but no special handling).
  - 宮干四化 not yet implemented (only 生年四化).
  - Star placement follows common Phase 1 rules; exact flow-school variants TBD.
"""
import math
import hashlib
from datetime import date, time
from typing import Optional, List, Dict, Tuple

from core.models import ZiWeiChart, ZiWeiPalace, DaXianPeriod, Gender

try:
    from lunardate import LunarDate as _LunarDate
    _LUNARDATE_AVAILABLE = True
except ImportError:
    _LUNARDATE_AVAILABLE = False

# ── Earthly Branch order ──────────────────────────────────────────────────────

_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
_STEMS    = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# Branch index helpers
_BI = {b: i for i, b in enumerate(_BRANCHES)}


# ── Palace names (順序定義) ────────────────────────────────────────────────────
# 命宮開始，依序逆時針（地支遞增）排列。
# Palace index i is at branch (ming_idx + i) % 12.

_PALACE_NAMES = [
    "命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
    "遷移宮", "交友宮", "官祿宮", "田宅宮", "福德宮", "父母宮",
]

_PALACE_INTERPRETATIONS = {
    "命宮": "命宮是紫微命盤的核心，代表你的根本個性、外在氣質與人生主軸。",
    "兄弟宮": "兄弟宮代表手足關係、平輩緣分，以及你與同儕的互動模式。",
    "夫妻宮": "夫妻宮顯示你在婚姻或長期伴侶關係中的模式與運勢。",
    "子女宮": "子女宮代表子息緣分、部屬關係，以及你的創造力展現。",
    "財帛宮": "財帛宮揭示你的財富獲取方式、金錢觀與理財模式。",
    "疾厄宮": "疾厄宮代表身體健康、挫折承受力，以及生命中的考驗模式。",
    "遷移宮": "遷移宮代表你在外部世界的表現、異鄉發展潛力與外緣。",
    "交友宮": "交友宮顯示你的友情模式、貴人小人，以及社交場域中的能量。",
    "官祿宮": "官祿宮是事業格局的核心，揭示你的職涯走向、工作模式與成就方式。",
    "田宅宮": "田宅宮代表家庭環境、不動產運與你對安全感的追求方式。",
    "福德宮": "福德宮顯示你的內在精神世界、享樂方式，以及前世業力帶來的福分。",
    "父母宮": "父母宮代表與父母的關係、長輩緣分，以及你在社會中接受規範的模式。",
}

# ── 14 Main Stars ─────────────────────────────────────────────────────────────

_MAIN_STARS_14 = [
    "紫微", "天機", "太陽", "武曲", "天同", "廉貞",   # 紫微系
    "天府", "太陰", "貪狼", "巨門", "天相", "天梁", "七殺", "破軍",  # 天府系
]

_MINOR_STARS = [
    "文昌", "文曲", "左輔", "右弼", "天魁", "天鉞",
    "祿存", "天馬", "擎羊", "陀羅", "火星", "鈴星",
]

# ── 生年四化表 ────────────────────────────────────────────────────────────────

_YEAR_STEM_SIHUA: Dict[str, Dict[str, str]] = {
    "甲": {"廉貞": "化祿", "破軍": "化權", "武曲": "化科", "太陽": "化忌"},
    "乙": {"天機": "化祿", "天梁": "化權", "紫微": "化科", "太陰": "化忌"},
    "丙": {"天同": "化祿", "天機": "化權", "文昌": "化科", "廉貞": "化忌"},
    "丁": {"太陰": "化祿", "天同": "化權", "天機": "化科", "巨門": "化忌"},
    "戊": {"貪狼": "化祿", "太陰": "化權", "右弼": "化科", "天機": "化忌"},
    "己": {"武曲": "化祿", "貪狼": "化權", "天梁": "化科", "文曲": "化忌"},
    "庚": {"太陽": "化祿", "武曲": "化權", "太陰": "化科", "天同": "化忌"},
    "辛": {"巨門": "化祿", "太陽": "化權", "文曲": "化科", "文昌": "化忌"},
    "壬": {"天梁": "化祿", "紫微": "化權", "左輔": "化科", "武曲": "化忌"},
    "癸": {"破軍": "化祿", "巨門": "化權", "太陰": "化科", "貪狼": "化忌"},
}

# ── 五行局 nayin table ────────────────────────────────────────────────────────
# Maps (stem, branch) → bureau_number  (2=水, 3=木, 4=金, 5=土, 6=火)

_NAYIN_BUREAU: Dict[Tuple[str, str], int] = {
    ("甲", "子"): 4, ("乙", "丑"): 4,   # 海中金
    ("丙", "寅"): 6, ("丁", "卯"): 6,   # 爐中火
    ("戊", "辰"): 3, ("己", "巳"): 3,   # 大林木
    ("庚", "午"): 5, ("辛", "未"): 5,   # 路旁土
    ("壬", "申"): 4, ("癸", "酉"): 4,   # 劍鋒金
    ("甲", "戌"): 6, ("乙", "亥"): 6,   # 山頭火
    ("丙", "子"): 2, ("丁", "丑"): 2,   # 澗下水
    ("戊", "寅"): 5, ("己", "卯"): 5,   # 城頭土
    ("庚", "辰"): 4, ("辛", "巳"): 4,   # 白蠟金
    ("壬", "午"): 3, ("癸", "未"): 3,   # 楊柳木
    ("甲", "申"): 2, ("乙", "酉"): 2,   # 泉中水
    ("丙", "戌"): 5, ("丁", "亥"): 5,   # 屋上土
    ("戊", "子"): 6, ("己", "丑"): 6,   # 霹靂火
    ("庚", "寅"): 3, ("辛", "卯"): 3,   # 松柏木
    ("壬", "辰"): 2, ("癸", "巳"): 2,   # 長流水
    ("甲", "午"): 4, ("乙", "未"): 4,   # 沙中金
    ("丙", "申"): 6, ("丁", "酉"): 6,   # 山下火
    ("戊", "戌"): 3, ("己", "亥"): 3,   # 平地木
    ("庚", "子"): 5, ("辛", "丑"): 5,   # 壁上土
    ("壬", "寅"): 4, ("癸", "卯"): 4,   # 金箔金
    ("甲", "辰"): 6, ("乙", "巳"): 6,   # 覆燈火
    ("丙", "午"): 2, ("丁", "未"): 2,   # 天河水
    ("戊", "申"): 5, ("己", "酉"): 5,   # 大驛土
    ("庚", "戌"): 4, ("辛", "亥"): 4,   # 釵釧金
    ("壬", "子"): 3, ("癸", "丑"): 3,   # 桑柘木
    ("甲", "寅"): 2, ("乙", "卯"): 2,   # 大溪水
    ("丙", "辰"): 5, ("丁", "巳"): 5,   # 沙中土
    ("戊", "午"): 6, ("己", "未"): 6,   # 天上火
    ("庚", "申"): 3, ("辛", "酉"): 3,   # 石榴木
    ("壬", "戌"): 2, ("癸", "亥"): 2,   # 大海水
}

_BUREAU_NAME = {2: "水二局", 3: "木三局", 4: "金四局", 5: "土五局", 6: "火六局"}

# Starting stem of 寅月 (same rule as BaZi month stems) indexed by year_stem_idx % 5
# 甲己→丙(2), 乙庚→戊(4), 丙辛→庚(6), 丁壬→壬(8), 戊癸→甲(0)
_MONTH_STEM_BASE = [2, 4, 6, 8, 0]


# ── Hour-branch helper ────────────────────────────────────────────────────────

def _get_ziwei_hour_branch(hour: int, minute: int) -> str:
    """
    Map (hour, minute) to earthly branch string for Zi Wei.
    Identical rule to BaZi: 子=23:00-00:59, etc.
    """
    if hour == 23 or hour == 0:   return "子"
    elif 1  <= hour < 3:          return "丑"
    elif 3  <= hour < 5:          return "寅"
    elif 5  <= hour < 7:          return "卯"
    elif 7  <= hour < 9:          return "辰"
    elif 9  <= hour < 11:         return "巳"
    elif 11 <= hour < 13:         return "午"
    elif 13 <= hour < 15:         return "未"
    elif 15 <= hour < 17:         return "申"
    elif 17 <= hour < 19:         return "酉"
    elif 19 <= hour < 21:         return "戌"
    else:                         return "亥"


# ── 命宮 / 身宮 ───────────────────────────────────────────────────────────────

def _calc_ming_shen(lunar_month: int, hour_branch: str) -> Tuple[int, int]:
    """
    Calculate 命宮 and 身宮 branch indices.

    Rule (common single-school formula, V1.5 Phase 1):
      - Start at 寅 (index 2), advance by (lunar_month - 1) for month position.
      - 命宮: step backward by hour_branch index.
      - 身宮: step forward by hour_branch index.

    Returns: (ming_idx, shen_idx) where 0=子 … 11=亥.
    """
    month_branch_idx = (2 + lunar_month - 1) % 12
    hour_idx = _BI[hour_branch]
    ming_idx = (month_branch_idx - hour_idx) % 12
    shen_idx = (month_branch_idx + hour_idx) % 12
    return ming_idx, shen_idx


# ── 命宮 stem ─────────────────────────────────────────────────────────────────

def _calc_ming_stem(lunar_year_stem: str, ming_idx: int) -> str:
    """
    Derive 命宮 heavenly stem using the same formula as BaZi month stems.
    Year stem determines the stem of 寅月; subsequent branches step +1 stem.
    """
    year_stem_idx = _STEMS.index(lunar_year_stem)
    base = _MONTH_STEM_BASE[year_stem_idx % 5]
    stem_idx = (base + (ming_idx - 2) % 12) % 10
    return _STEMS[stem_idx]


# ── 五行局 ────────────────────────────────────────────────────────────────────

def _calculate_five_element_bureau(
    ming_stem: str, ming_branch: str
) -> Tuple[str, int]:
    """
    Determine 五行局 from the nayin of (命宮 stem, 命宮 branch).
    Returns ("水二局", 2) etc.
    V1.5 Phase 1: uses complete 納音 table; flows/schools may vary.
    """
    bureau_num = _NAYIN_BUREAU.get((ming_stem, ming_branch), 5)  # default 土五局
    return _BUREAU_NAME[bureau_num], bureau_num


# ── 紫微 / 天府 placement ─────────────────────────────────────────────────────

def _place_ziwei_star(lunar_day: int, bureau_number: int) -> int:
    """
    Place 紫微 star.
    Algorithm (V1.7.4 — corrected 飛宮訣, validated against external chart):
      Days are grouped in batches of bureau_number.
      Formula: branch = (5 + 2*(group-1)*N - D) % 12
      where group = ceil(D / N), N = bureau_number, D = lunar_day.
      Base 5 (巳) validated for 六局 day-22 → 未(7) matching external chart.
    Returns branch index (0=子).
    """
    d = max(1, min(30, lunar_day))
    n = bureau_number
    group = math.ceil(d / n)
    return (5 + 2 * (group - 1) * n - d) % 12


def _place_tianfu_star(ziwei_idx: int) -> int:
    """
    Place 天府 star symmetrically to 紫微 around the 子-辰 axis.
    Formula: tianfu = (4 - ziwei_idx) % 12
    e.g. 紫微=子(0)→天府=辰(4); 紫微=寅(2)→天府=寅(2); 紫微=午(6)→天府=戌(10).
    """
    return (4 - ziwei_idx) % 12


# ── 十四主星安星 ──────────────────────────────────────────────────────────────

# 紫微系: offsets from 紫微 going backward (逆時針 = decreasing branch index).
# 紫微(0) 天機(-1) 太陽(-3) 武曲(-4) 天同(-5) 廉貞(-8)
_ZIWEI_GROUP_OFFSETS = [
    ("紫微", 0), ("天機", -1), ("太陽", -3),
    ("武曲", -4), ("天同", -5), ("廉貞", -8),
]

# 天府系: offsets from 天府 going forward (順時針 = increasing branch index).
# 天府(0) 太陰(+1) 貪狼(+2) 巨門(+3) 天相(+4) 天梁(+5) 七殺(+6) 破軍(+10)
_TIANFU_GROUP_OFFSETS = [
    ("天府", 0), ("太陰", 1), ("貪狼", 2), ("巨門", 3),
    ("天相", 4), ("天梁", 5), ("七殺", 6), ("破軍", 10),
]


def _place_main_stars(ziwei_idx: int, tianfu_idx: int) -> Dict[int, List[str]]:
    """
    Place all 14 main stars. Returns dict {branch_idx: [star_names]}.
    V1.5 Phase 1: standard offset rules; exact table verification TODO.
    """
    placement: Dict[int, List[str]] = {i: [] for i in range(12)}
    for name, offset in _ZIWEI_GROUP_OFFSETS:
        placement[(ziwei_idx + offset) % 12].append(name)
    for name, offset in _TIANFU_GROUP_OFFSETS:
        placement[(tianfu_idx + offset) % 12].append(name)
    return placement


# ── Auxiliary & Malefic Star Placement (V1.5.5) ──────────────────────────────
# Phase 1 — common table method.  Flow-school variants can be configured in
# future versions.  All placements are deterministic; no randomness.

# Yang stems (陽干)
_YANG_STEMS = {"甲", "丙", "戊", "庚", "壬"}

# 天魁 / 天鉞 by year stem (common 資治通鑑 table, Phase 1)
# 甲戊庚: 魁丑 鉞未 | 乙己: 魁子 鉞申 | 丙丁: 魁亥 鉞酉
# 壬癸: 魁卯 鉞巳 | 辛: 魁午 鉞寅
_KUI_YUE_TABLE: Dict[str, Tuple[int, int]] = {
    "甲": (1, 7), "戊": (1, 7), "庚": (1, 7),   # 魁=丑(1) 鉞=未(7)
    "乙": (0, 8), "己": (0, 8),                   # 魁=子(0) 鉞=申(8)
    "丙": (11, 9), "丁": (11, 9),                 # 魁=亥(11) 鉞=酉(9)
    "壬": (3, 5), "癸": (3, 5),                   # 魁=卯(3) 鉞=巳(5)
    "辛": (6, 2),                                  # 魁=午(6) 鉞=寅(2)
}

# 祿存 / 擎羊 / 陀羅 by year stem (standard rule: 羊 = 祿存+1, 陀 = 祿存-1)
_LUCUN_TABLE: Dict[str, int] = {
    "甲": 2, "乙": 3, "丙": 5, "丁": 6,
    "戊": 5, "己": 6, "庚": 8, "辛": 9,
    "壬": 11, "癸": 0,
}

# 火星 / 鈴星 base indices by year-branch group (Phase 1 common table)
# key = year_branch, value = (火星_base_idx, 鈴星_base_idx) for 子時
# 火星 = (base + hour_idx) % 12; 鈴星 = (ling_base + hour_idx) % 12
_HUO_LING_BASE: Dict[str, Tuple[int, int]] = {
    "寅": (2, 3), "午": (2, 3), "戌": (2, 3),   # 火起寅(2) 鈴起卯(3)
    "申": (10, 11), "子": (10, 11), "辰": (10, 11),  # 火起戌(10) 鈴起亥(11)
    "巳": (6, 10), "酉": (6, 10), "丑": (6, 10),    # 火起午(6) 鈴起戌(10)
    "亥": (9, 3), "卯": (9, 3), "未": (9, 3),       # 火起酉(9) 鈴起卯(3)
}

# 大限 palace interpretation themes
_PALACE_DA_XIAN_THEMES: Dict[str, str] = {
    "命宮": "自我定位、身份認同與人生主軸",
    "兄弟宮": "手足情誼、平輩人際與同儕合作",
    "夫妻宮": "親密關係、婚姻合作與對等連結",
    "子女宮": "子嗣緣分、創造力與部屬管理",
    "財帛宮": "財務積累、資源取得與金錢流動",
    "疾厄宮": "健康管理、承壓能力與身心調適",
    "遷移宮": "外部環境、移動發展與社會接觸",
    "交友宮": "社交圈、貴人小人與群體關係",
    "官祿宮": "事業格局、社會定位與職涯成就",
    "田宅宮": "居家環境、不動產與安全感基礎",
    "福德宮": "精神生活、內在滋養與享受模式",
    "父母宮": "長輩關係、上司緣與社會規範適應",
}


def _place_left_right(lunar_month: int) -> Dict[str, str]:
    """
    左輔 / 右弼 placement by lunar month (V1.5.5 Phase 1).
    左輔: 辰(4) + month - 1 (forward).
    右弼: 戌(10) - (month - 1) (backward).
    """
    zuo_idx = (4 + lunar_month - 1) % 12     # 辰 = index 4
    you_idx = (10 - (lunar_month - 1)) % 12  # 戌 = index 10
    return {"左輔": _BRANCHES[zuo_idx], "右弼": _BRANCHES[you_idx]}


def _place_chang_qu(hour_branch: str) -> Dict[str, str]:
    """
    文昌 / 文曲 placement by hour branch (V1.5.5 Phase 1).
    文昌: 戌(10) backwards from 子時 → idx = (10 - hour_idx) % 12.
    文曲: 辰(4) forwards from 子時 → idx = (4 + hour_idx) % 12.
    """
    h = _BI[hour_branch]
    chang_idx = (10 - h) % 12
    qu_idx    = (4 + h) % 12
    return {"文昌": _BRANCHES[chang_idx], "文曲": _BRANCHES[qu_idx]}


def _place_kui_yue(year_stem: str) -> Dict[str, str]:
    """
    天魁 / 天鉞 placement by year stem (V1.5.5 Phase 1, common table).
    """
    kui_idx, yue_idx = _KUI_YUE_TABLE.get(year_stem, (1, 7))
    return {"天魁": _BRANCHES[kui_idx], "天鉞": _BRANCHES[yue_idx]}


def _place_lucun_yang_tuo(year_stem: str) -> Dict[str, str]:
    """
    祿存 / 擎羊 / 陀羅 placement by year stem (V1.5.5 Phase 1).
    祿存 at standard position; 擎羊 = +1; 陀羅 = -1.
    """
    lu_idx  = _LUCUN_TABLE.get(year_stem, 0)
    yang_idx = (lu_idx + 1) % 12
    tuo_idx  = (lu_idx - 1) % 12
    return {
        "祿存": _BRANCHES[lu_idx],
        "擎羊": _BRANCHES[yang_idx],
        "陀羅": _BRANCHES[tuo_idx],
    }


def _place_huo_ling(year_branch: str, hour_branch: str) -> Dict[str, str]:
    """
    火星 / 鈴星 placement by year branch group + hour branch (V1.5.5 Phase 1).
    火星 = (huo_base + hour_idx) % 12.
    鈴星 = (ling_base + hour_idx) % 12.
    """
    huo_base, ling_base = _HUO_LING_BASE.get(year_branch, (2, 3))
    h = _BI[hour_branch]
    huo_idx  = (huo_base + h) % 12
    ling_idx = (ling_base + h) % 12
    return {"火星": _BRANCHES[huo_idx], "鈴星": _BRANCHES[ling_idx]}


def _place_kong_jie(hour_branch: str) -> Dict[str, str]:
    """
    地空 / 地劫 placement by hour branch (V1.5.5 Phase 1).
    地空: 亥(11) backwards from 子時 → idx = (11 - hour_idx) % 12.
    地劫: 亥(11) forwards from 子時 → idx = (11 + hour_idx) % 12.
    """
    h = _BI[hour_branch]
    kong_idx = (11 - h) % 12
    jie_idx  = (11 + h) % 12
    return {"地空": _BRANCHES[kong_idx], "地劫": _BRANCHES[jie_idx]}


def _calc_da_xian(
    ming_idx: int,
    bureau_number: int,
    year_stem: str,
    gender: Optional[Gender],
    palaces: List[ZiWeiPalace],
) -> Tuple[str, int, List[DaXianPeriod]]:
    """
    Calculate Da Xian (大限) 10-year periods — Phase 1.

    Direction rules (V1.5.5):
      陽男 / 陰女 → forward (順行)
      陰男 / 陽女 → backward (逆行)
      Unknown gender → direction = "unknown", palaces assigned forward as fallback.

    Start age = five_element_bureau_number (水二=2, 木三=3, 金四=4, 土五=5, 火六=6).
    Each period = 10 years.  Returns (direction, start_age, [DaXianPeriod x 12]).
    """
    is_yang_stem = year_stem in _YANG_STEMS

    if gender == Gender.MALE:
        direction = "forward" if is_yang_stem else "backward"
    elif gender == Gender.FEMALE:
        direction = "backward" if is_yang_stem else "forward"
    else:
        direction = "unknown"

    start_age = bureau_number

    periods: List[DaXianPeriod] = []
    for i in range(12):
        if direction == "backward":
            p_idx = i % 12              # 逆: forward through counterclockwise palace list
        else:
            p_idx = (12 - i) % 12      # 順/unknown: backward through counterclockwise list

        p = palaces[p_idx]
        age_s = start_age + i * 10
        age_e = age_s + 9
        theme = _PALACE_DA_XIAN_THEMES.get(p.name, "此宮位相關課題")
        interp = f"此大限落於{p.name}（{p.earthly_branch}），代表此十年{theme}議題被放大。"

        periods.append(DaXianPeriod(
            start_age=age_s,
            end_age=age_e,
            palace_name=p.name,
            branch=p.earthly_branch,
            main_stars=list(p.main_stars),
            auxiliary_stars=list(p.minor_stars),
            interpretation=interp,
        ))

    return direction, start_age, periods


# ── 命主 / 身主 (V1.7.5) ──────────────────────────────────────────────────────

_MING_ZHU_TABLE: Dict[str, str] = {
    "子": "貪狼", "丑": "巨門", "寅": "祿存", "卯": "文曲",
    "辰": "廉貞", "巳": "武曲", "午": "破軍", "未": "武曲",
    "申": "廉貞", "酉": "文曲", "戌": "祿存", "亥": "巨門",
}

_SHEN_ZHU_TABLE: Dict[str, str] = {
    "子": "火星", "丑": "天相", "寅": "天梁", "卯": "天同",
    "辰": "文昌", "巳": "天機", "午": "火星", "未": "天相",
    "申": "天梁", "酉": "天同", "戌": "文昌", "亥": "天機",
}


def _calc_ming_zhu(ming_branch: str) -> Optional[str]:
    """命主：依命宮地支查表。卯 → 文曲。"""
    return _MING_ZHU_TABLE.get(ming_branch)


def _calc_shen_zhu(year_branch: str) -> Optional[str]:
    """身主：依生年地支查表。巳年 → 天機。"""
    return _SHEN_ZHU_TABLE.get(year_branch)


# ── 天馬 (V1.7.5) ────────────────────────────────────────────────────────────

_TIAN_MA_TABLE: Dict[str, str] = {
    "寅": "申", "午": "申", "戌": "申",
    "申": "寅", "子": "寅", "辰": "寅",
    "巳": "亥", "酉": "亥", "丑": "亥",
    "亥": "巳", "卯": "巳", "未": "巳",
}


def _calc_tian_ma_branch(year_branch: str) -> Optional[str]:
    """天馬：依年支三合局查表。巳年 → 亥。"""
    return _TIAN_MA_TABLE.get(year_branch)


# ── 廟旺利陷 (V1.7.5 Phase 1) ────────────────────────────────────────────────
# Phase 1 table: covers 14 main stars × key branches.
# Unlisted (star, branch) combos → "平".

_STAR_BRIGHTNESS_TABLE: Dict[str, Dict[str, str]] = {
    "紫微": {"子": "廟", "丑": "廟", "寅": "得", "卯": "利", "辰": "廟", "巳": "廟",
             "午": "廟", "未": "廟", "申": "廟", "酉": "廟", "戌": "廟", "亥": "廟"},
    "天機": {"子": "廟", "丑": "陷", "寅": "廟", "卯": "旺", "辰": "陷", "巳": "陷",
             "午": "廟", "未": "陷", "申": "廟", "酉": "陷", "戌": "陷", "亥": "廟"},
    "太陽": {"子": "陷", "丑": "陷", "寅": "旺", "卯": "廟", "辰": "廟", "巳": "廟",
             "午": "廟", "未": "得", "申": "利", "酉": "陷", "戌": "陷", "亥": "陷"},
    "武曲": {"子": "廟", "丑": "廟", "寅": "得", "卯": "利", "辰": "廟", "巳": "廟",
             "午": "廟", "未": "廟", "申": "廟", "酉": "廟", "戌": "廟", "亥": "廟"},
    "天同": {"子": "廟", "丑": "陷", "寅": "利", "卯": "陷", "辰": "陷", "巳": "陷",
             "午": "陷", "未": "旺", "申": "廟", "酉": "廟", "戌": "陷", "亥": "廟"},
    "廉貞": {"子": "廟", "丑": "廟", "寅": "廟", "卯": "廟", "辰": "廟", "巳": "廟",
             "午": "廟", "未": "廟", "申": "廟", "酉": "廟", "戌": "廟", "亥": "陷"},
    "天府": {"子": "廟", "丑": "廟", "寅": "廟", "卯": "廟", "辰": "廟", "巳": "廟",
             "午": "廟", "未": "廟", "申": "廟", "酉": "旺", "戌": "廟", "亥": "廟"},
    "太陰": {"子": "廟", "丑": "旺", "寅": "陷", "卯": "陷", "辰": "陷", "巳": "陷",
             "午": "陷", "未": "廟", "申": "旺", "酉": "廟", "戌": "旺", "亥": "廟"},
    "貪狼": {"子": "旺", "丑": "廟", "寅": "廟", "卯": "廟", "辰": "廟", "巳": "廟",
             "午": "廟", "未": "廟", "申": "廟", "酉": "廟", "戌": "廟", "亥": "陷"},
    "巨門": {"子": "廟", "丑": "廟", "寅": "陷", "卯": "旺", "辰": "廟", "巳": "廟",
             "午": "廟", "未": "陷", "申": "廟", "酉": "廟", "戌": "陷", "亥": "廟"},
    "天相": {"子": "廟", "丑": "廟", "寅": "廟", "卯": "廟", "辰": "廟", "巳": "廟",
             "午": "廟", "未": "廟", "申": "廟", "酉": "廟", "戌": "廟", "亥": "廟"},
    "天梁": {"子": "廟", "丑": "廟", "寅": "廟", "卯": "廟", "辰": "廟", "巳": "廟",
             "午": "廟", "未": "旺", "申": "廟", "酉": "廟", "戌": "廟", "亥": "廟"},
    "七殺": {"子": "廟", "丑": "廟", "寅": "廟", "卯": "旺", "辰": "廟", "巳": "廟",
             "午": "廟", "未": "廟", "申": "廟", "酉": "廟", "戌": "廟", "亥": "廟"},
    "破軍": {"子": "廟", "丑": "廟", "寅": "廟", "卯": "廟", "辰": "廟", "巳": "廟",
             "午": "廟", "未": "旺", "申": "廟", "酉": "廟", "戌": "廟", "亥": "廟"},
}


def _get_star_brightness(star: str, branch: str) -> str:
    """Return brightness label for (star, branch). Defaults to '平' if not in table."""
    return _STAR_BRIGHTNESS_TABLE.get(star, {}).get(branch, "平")


def _calc_brightness_map(palaces: list) -> Dict[str, Dict[str, str]]:
    """Build {palace_name: {star: brightness}} for all 12 palaces."""
    result: Dict[str, Dict[str, str]] = {}
    for p in palaces:
        if p.main_stars:
            result[p.name] = {
                star: _get_star_brightness(star, p.earthly_branch)
                for star in p.main_stars
            }
    return result


# ── 盤面結構支援度 Phase 1 (V1.7.6 calibrated) ───────────────────────────────

_SCORE_BRIGHTNESS_CALIBRATED: Dict[str, int] = {
    "廟": 5, "旺": 4, "利": 3, "得": 2, "平": 0, "陷": -3,
}

_SCORE_LABELS: list = [
    (85, "高支援但需承載張力"),
    (75, "結構良好"),
    (60, "中性可塑"),
    (45, "張力偏高"),
    (30, "高壓磨練盤"),
]


def _calc_ziwei_score(
    palaces: list,
    brightness_map: Dict[str, Dict[str, str]],
    four_trans: Dict[str, str],
) -> Tuple[int, str, str, Dict[str, int]]:
    """
    Calculate Phase 1 盤面結構支援度 (30–92, calibrated V1.7.6).
    Deterministic. NOT equivalent to any external site's 好運指數.
    Returns (score, label, explanation, components).
    """
    score = 50  # base
    components: Dict[str, int] = {"base": 50}

    _key_palaces = {"命宮", "官祿宮", "財帛宮", "遷移宮"}
    _key_palaces_cwf = {"命宮", "官祿宮", "財帛宮"}
    _malefic_stars = {"擎羊", "陀羅", "火星", "鈴星", "地空", "地劫"}
    _auspicious_stars = {"左輔", "右弼", "文昌", "文曲", "天魁", "天鉞", "祿存"}

    # 1. 命宮結構 max +14
    ming = next((p for p in palaces if p.name == "命宮"), None)
    ming_bonus = 0
    if ming and ming.main_stars:
        ming_bonus += 4
        if len(ming.main_stars) >= 2:
            ming_bonus += 2
        bright_sum = sum(
            _SCORE_BRIGHTNESS_CALIBRATED.get(
                brightness_map.get("命宮", {}).get(s, "平"), 0
            )
            for s in ming.main_stars
        )
        ming_bonus += max(-8, min(bright_sum, 8))
    ming_bonus = min(ming_bonus, 14)
    score += ming_bonus
    components["ming_palace"] = ming_bonus

    # 2. 官祿 / 財帛 / 福德 + 三方四正 max +16
    career = next((p for p in palaces if p.name == "官祿宮"), None)
    wealth = next((p for p in palaces if p.name == "財帛宮"), None)
    fortune = next((p for p in palaces if p.name == "福德宮"), None)
    cwf_bonus = 0
    if career and career.main_stars:
        cwf_bonus += 4
    if wealth and wealth.main_stars:
        cwf_bonus += 4
    if fortune and fortune.main_stars:
        cwf_bonus += 3
    strong_bonus = 0
    for p in palaces:
        if p.name in _key_palaces and p.main_stars:
            for s in p.main_stars:
                b = brightness_map.get(p.name, {}).get(s, "平")
                if b in ("廟", "旺"):
                    strong_bonus += 2
                elif b in ("利", "得"):
                    strong_bonus += 1
    cwf_bonus += min(strong_bonus, 5)
    cwf_bonus = min(cwf_bonus, 16)
    score += cwf_bonus
    components["career_wealth_fortune"] = cwf_bonus

    # 3. 四化 max ±12
    sihua_bonus = 0
    for p in palaces:
        is_key = p.name in _key_palaces
        for s in p.main_stars:
            trans = four_trans.get(s)
            if trans == "化祿":
                sihua_bonus += 5 if is_key else 2
            elif trans == "化權":
                sihua_bonus += 4 if is_key else 2
            elif trans == "化科":
                sihua_bonus += 3 if is_key else 1
            elif trans == "化忌":
                sihua_bonus -= 5 if is_key else 2
    sihua_bonus = max(-12, min(sihua_bonus, 12))
    score += sihua_bonus
    components["transformations"] = sihua_bonus

    # 4. 天馬 / 輔星 max +5
    aux_bonus = 0
    _tian_ma_palaces = {"財帛宮", "遷移宮", "官祿宮"}
    for p in palaces:
        if p.name in _tian_ma_palaces and "天馬" in p.minor_stars:
            aux_bonus += 2
            break
    aux_star = sum(
        1
        for p in palaces if p.name in _key_palaces_cwf
        for s in p.minor_stars if s in _auspicious_stars
    )
    aux_bonus += min(aux_star, 3)
    aux_bonus = min(aux_bonus, 5)
    score += aux_bonus
    components["auxiliary_support"] = aux_bonus

    # 5. 六煞張力 max -10
    has_ji_hua_in_key = any(
        four_trans.get(s) in ("化祿", "化科", "化權")
        for p in palaces if p.name in _key_palaces
        for s in p.main_stars
    )
    malefic_penalty = 0
    for p in palaces:
        if p.name in _key_palaces:
            for s in p.minor_stars:
                if s in _malefic_stars:
                    malefic_penalty += max(0, 2 - (1 if has_ji_hua_in_key else 0))
    malefic_penalty = min(malefic_penalty, 10)
    score -= malefic_penalty
    components["malefic_tension"] = -malefic_penalty

    # 6. 平衡校正（過度集中 / overconfidence penalty）
    balance_adj = 0
    if score > 86:
        has_any_malefic = any(
            s in _malefic_stars
            for p in palaces if p.name in _key_palaces
            for s in p.minor_stars
        )
        has_hua_ji = any(
            four_trans.get(s) == "化忌"
            for p in palaces if p.name in _key_palaces
            for s in p.main_stars
        )
        if has_any_malefic or has_hua_ji:
            balance_adj -= 5
    score += balance_adj
    components["balance_adjustment"] = balance_adj

    # Clamp
    score = max(30, min(92, score))

    # Label
    label = "高壓磨練盤"
    for threshold, lbl in _SCORE_LABELS:
        if score >= threshold:
            label = lbl
            break

    # Explanation
    explanation = (
        "這是盤面結構支援度，不是命運好壞分數。"
        "不等同外部網站好運指數。"
        "主要參考命宮、官祿、財帛、福德、四化、廟旺陷、天馬與輔煞張力。"
    )
    if score >= 85:
        explanation += "高分也代表責任與壓力承載度較高。"
    explanation += "應搭配實際行動、環境、選擇與長期習慣，而非單靠命盤下結論。"

    return score, label, explanation, components


# ── Interpretation helpers (V1.5.1) ──────────────────────────────────────────

_MAIN_STAR_INTERPRETATIONS: Dict[str, str] = {
    "紫微": "紫微是帝星，象徵主導、整合與尊貴。命宮有紫微者，天生具備領導格局與統御意識，傾向獨立自主，重視身份認同，最佳發展方向是成為某一領域的主心骨。",
    "天機": "天機是智謀之星，善於思考、策劃與變通。命宮有天機者，腦筋靈活、愛好學習，擅長找尋系統中的漏洞與機遇，適合智識型或需要靈活應對的工作。",
    "太陽": "太陽是光明之星，代表外放、責任與名聲。命宮有太陽者，天生具有公眾魅力，喜歡照亮他人，適合需要曝光的工作，但也容易過度付出而忽略自身需求。",
    "武曲": "武曲是財星兼將星，象徵執行力、紀律與資源掌控。命宮有武曲者，行事果斷、重實際，財務觀念強，適合金融、管理或需要強大執行力的職場。",
    "天同": "天同是福星，象徵福氣、享受與柔和。命宮有天同者，天生散發親和力，重視生活品質與內心平靜，適合服務業、福利型工作，或能帶給他人輕鬆感的職位。",
    "廉貞": "廉貞是規範之星，兼具魅力與原則。命宮有廉貞者，具有界線意識與競爭心，吸引力強但不輕易妥協，適合法律、軍警、藝術或需要嚴格自律的工作。",
    "天府": "天府是財庫星，象徵穩定、管理與資源累積。命宮有天府者，天生具備守成與管理才能，重視安全感，適合財務、行政、資源型管理工作，善於建構穩定的基礎。",
    "太陰": "太陰是月亮之星，象徵內斂、情緒感知與細膩。命宮有太陰者，細膩敏感、直覺強，適合藝術、教育、後台支持工作，在安靜環境中發揮最大潛力。",
    "貪狼": "貪狼是慾望與才藝之星，象徵擴張、人際與多元能力。命宮有貪狼者，魅力十足，才藝廣博，善於社交，但需注意慾望過旺帶來的能量分散。",
    "巨門": "巨門是語言與辯證之星，善言辭但也帶口舌之象。命宮有巨門者，表達能力強，邏輯清晰，適合律師、教師、媒體工作，但需注意言語帶來的誤解。",
    "天相": "天相是輔佐之星，象徵協調、制度與公正。命宮有天相者，擅長在組織中扮演關鍵的溝通橋樑，適合行政、幕僚、協調型主管職位。",
    "天梁": "天梁是蔭護之星，象徵保護、道德與長輩緣。命宮有天梁者，具有被保護或保護他人的特質，醫療、社工、監督等領域最能展現其價值。",
    "七殺": "七殺是殺將之星，象徵決斷、壓力承受與破局能力。命宮有七殺者，具有強烈的行動力和競爭意識，不怕壓力，適合創業、軍警、體育或高度競爭的行業。",
    "破軍": "破軍是變革之星，象徵破壞重建、冒險與重新開始。命宮有破軍者，不拘常規，喜歡突破既有框架，適合改革性工作、創業或需要開創新局面的環境。",
}

_SIHUA_LABELS: Dict[str, str] = {
    "化祿": "資源流入與機會",
    "化權": "主導力與掌控感",
    "化科": "名聲、學習與形象光環",
    "化忌": "壓力與執念，也是深化的課題",
}


def _interpret_main_star(star: str) -> str:
    """Return interpretation string for a main star. Empty string if unknown."""
    return _MAIN_STAR_INTERPRETATIONS.get(star, "")


def _interpret_palace(
    palace_name: str,
    main_stars: List[str],
    transformations: Dict[str, str],
) -> str:
    """
    Build interpretation text for a palace given its name, stars, and transformations.
    Returns a composed paragraph suitable for reports and UI display.
    """
    base = _PALACE_INTERPRETATIONS.get(palace_name, "")
    star_parts = []
    for s in main_stars:
        interp = _MAIN_STAR_INTERPRETATIONS.get(s, "")
        if interp:
            star_parts.append(f"主星{s}：{interp}")
    sihua_parts = []
    for s in main_stars:
        if s in transformations:
            tx = transformations[s]
            label = _SIHUA_LABELS.get(tx, "")
            if label:
                sihua_parts.append(f"{s}{tx}（{label}）")
    result = base
    if star_parts:
        result += "\n\n" + "\n\n".join(star_parts)
    if sihua_parts:
        result += "\n\n**四化影響**：" + "；".join(sihua_parts) + "。"
    return result.strip()


def _build_ziwei_summary(chart: "ZiWeiChart") -> str:
    """
    Build a concise summary of the ZiWeiChart for synthesis/report use.
    Returns a markdown-formatted string.
    """
    lines: List[str] = []
    mode = getattr(chart, "calculation_mode", "mock_fallback")
    if mode == "formal_layout_phase1":
        lines.append(
            "紫微斗數 V1.5 第一階段正式排盤已完成，命宮、身宮、十四主星與生年四化均已安置。"
        )
    elif mode == "partial_lunar_only":
        lines.append(
            "紫微斗數已完成農曆轉換，但因出生時辰未知，命宮與身宮不可視為精準。"
        )
    else:
        lines.append("紫微斗數目前使用 mock fallback，排盤資料僅供參考架構。")

    ming = chart.ming_palace
    if ming:
        stars = "、".join(ming.main_stars) if ming.main_stars else "無主星"
        lines.append(f"命宮位於{ming.earthly_branch}，主星：{stars}。")
        if ming.main_stars:
            first_star_interp = _interpret_main_star(ming.main_stars[0])
            if first_star_interp:
                lines.append(first_star_interp.split("。")[0] + "。")

    shen_branch = getattr(chart, "shen_branch", None)
    if shen_branch:
        lines.append(f"身宮位於{shen_branch}，代表後天行動重心，中年後越來越明顯的生命著力點。")

    bureau = getattr(chart, "five_element_bureau", None)
    if bureau:
        lines.append(f"五行局為{bureau}，是紫微星落宮的計算基礎。")

    return "\n".join(lines)


# ── Mock fallback (preserved from V1) ────────────────────────────────────────

def _seed(birth_date: date, birth_time: Optional[time]) -> int:
    raw = f"{birth_date.isoformat()}:{birth_time.isoformat() if birth_time else 'noon'}"
    return int(hashlib.md5(raw.encode()).hexdigest(), 16) % 10000


def _layout_mock(birth_date: date, birth_time: Optional[time]) -> ZiWeiChart:
    """Original mock layout — used when lunardate unavailable or conversion fails."""
    s = _seed(birth_date, birth_time)
    year_stem = _STEMS[(birth_date.year - 4) % 10]
    sihua_map = _YEAR_STEM_SIHUA.get(year_stem, {})

    ming_branch_idx = (birth_date.month + (birth_time.hour // 2 if birth_time else 0)) % 12
    ming_branch = _BRANCHES[ming_branch_idx]

    star_palace: Dict[int, List[str]] = {i: [] for i in range(12)}
    for i, star in enumerate(_MAIN_STARS_14):
        star_palace[(s // (i + 1) + i * 13) % 12].append(star)

    minor_palace: Dict[int, List[str]] = {i: [] for i in range(12)}
    for i, star in enumerate(_MINOR_STARS):
        minor_palace[(s * (i + 2) + i * 7) % 12].append(star)

    four_trans: Dict[str, str] = dict(sihua_map)

    def _palace_transforms(stars: List[str]) -> List[str]:
        return [f"{st}{sihua_map[st]}" for st in stars if st in sihua_map]

    def _build_palace(idx: int, name: str) -> ZiWeiPalace:
        branch = _BRANCHES[(ming_branch_idx + idx) % 12]
        mstars = star_palace[idx]
        mnstars = minor_palace[idx]
        return ZiWeiPalace(
            name=name,
            earthly_branch=branch,
            main_stars=mstars,
            minor_stars=mnstars,
            transformations=_palace_transforms(mstars + mnstars),
            interpretation=_PALACE_INTERPRETATIONS.get(name, ""),
        )

    palaces = [_build_palace(i, _PALACE_NAMES[i]) for i in range(12)]
    shen_palace = _build_palace((ming_branch_idx + 6) % 12, "身宮")
    all_main = [s for stars in star_palace.values() for s in stars]

    return ZiWeiChart(
        ming_palace=palaces[0],
        shen_palace=shen_palace,
        brother_palace=palaces[1],
        spouse_palace=palaces[2],
        children_palace=palaces[3],
        wealth_palace=palaces[4],
        health_palace=palaces[5],
        travel_palace=palaces[6],
        friends_palace=palaces[7],
        career_palace=palaces[8],
        property_palace=palaces[9],
        fortune_palace=palaces[10],
        parents_palace=palaces[11],
        main_stars=all_main,
        four_transformations=four_trans,
        is_mock=True,
        calculation_mode="mock_fallback",
        accuracy_note="農曆轉換套件不可用，紫微斗數使用 mock fallback。",
        ming_branch=ming_branch,
    )


# ── Main Engine ───────────────────────────────────────────────────────────────

class ZiWeiEngine:
    def calculate(self, birth_date: date,
                  birth_time: Optional[time] = None,
                  gender: Optional[Gender] = None) -> ZiWeiChart:
        """
        Calculate Zi Wei chart.
        Attempts formal Phase 1 layout when lunardate is available and
        birth_time is known; falls back gracefully otherwise.
        """
        # 1. Lunar date conversion
        if not _LUNARDATE_AVAILABLE:
            return _layout_mock(birth_date, birth_time)

        try:
            ld = _LunarDate.fromSolarDate(
                birth_date.year, birth_date.month, birth_date.day
            )
            lunar_year  = ld.year
            lunar_month = ld.month
            lunar_day   = ld.day
            is_leap     = ld.isLeapMonth
        except Exception:
            return _layout_mock(birth_date, birth_time)

        # 2. Year stem (from lunar year)
        year_stem = _STEMS[(lunar_year - 4) % 10]
        sihua_map = _YEAR_STEM_SIHUA.get(year_stem, {})

        # 3. Hour branch
        if birth_time is not None:
            hour_branch = _get_ziwei_hour_branch(birth_time.hour, birth_time.minute)
            time_known  = True
        else:
            hour_branch = None
            time_known  = False

        # 4. 命宮 / 身宮
        if time_known:
            ming_idx, shen_idx = _calc_ming_shen(lunar_month, hour_branch)
            ming_branch_str = _BRANCHES[ming_idx]
            shen_branch_str = _BRANCHES[shen_idx]
        else:
            ming_idx = (2 + lunar_month - 1) % 12  # partial: only month
            shen_idx = ming_idx
            ming_branch_str = _BRANCHES[ming_idx]
            shen_branch_str = None

        # 5. 命宮 stem & 五行局
        ming_stem = _calc_ming_stem(year_stem, ming_idx)
        bureau_name, bureau_num = _calculate_five_element_bureau(
            ming_stem, ming_branch_str
        )

        # 6. 紫微 / 天府 / 14 main stars
        ziwei_idx  = _place_ziwei_star(lunar_day, bureau_num)
        tianfu_idx = _place_tianfu_star(ziwei_idx)
        star_placement = _place_main_stars(ziwei_idx, tianfu_idx)

        # 7. 四化
        four_trans: Dict[str, str] = dict(sihua_map)

        # 8. Build palaces
        def _palace_transforms(stars: List[str]) -> List[str]:
            return [f"{st}{sihua_map[st]}" for st in stars if st in sihua_map]

        def _build_palace(palace_idx: int, name: str) -> ZiWeiPalace:
            branch_idx = (ming_idx - palace_idx) % 12
            branch     = _BRANCHES[branch_idx]
            mstars     = star_placement.get(branch_idx, [])
            transforms = _palace_transforms(mstars)
            return ZiWeiPalace(
                name=name,
                earthly_branch=branch,
                main_stars=mstars,
                minor_stars=[],   # auxiliary stars: future version
                transformations=transforms,
                interpretation=_PALACE_INTERPRETATIONS.get(name, ""),
            )

        palaces = [_build_palace(i, _PALACE_NAMES[i]) for i in range(12)]

        # 身宮 palace object — find which named palace it belongs to
        shen_offset = (ming_idx - shen_idx) % 12
        shen_palace = _build_palace(shen_offset, "身宮")

        all_main = [s for stars in star_placement.values() for s in stars]

        # 9. Auxiliary & malefic star placement (V1.5.5)
        aux_map: Dict[str, str] = {}
        malefic_map: Dict[str, str] = {}
        star_cat: Dict[str, str] = {}
        aux_accuracy_note = (
            "V1.5.5 輔星、煞星採 Phase 1 常見表法；流派差異後續版本可配置。"
        )
        year_branch_str = _BRANCHES[(lunar_year - 4) % 12]

        # Stars that only need lunar_month (available even without time)
        _lr = _place_left_right(lunar_month)
        _ky = _place_kui_yue(year_stem)
        _lu = _place_lucun_yang_tuo(year_stem)

        aux_map["左輔"] = _lr["左輔"]
        aux_map["右弼"] = _lr["右弼"]
        aux_map["天魁"] = _ky["天魁"]
        aux_map["天鉞"] = _ky["天鉞"]
        aux_map["祿存"] = _lu["祿存"]
        malefic_map["擎羊"] = _lu["擎羊"]
        malefic_map["陀羅"] = _lu["陀羅"]

        if time_known:
            _cq = _place_chang_qu(hour_branch)
            _hl = _place_huo_ling(year_branch_str, hour_branch)
            _kj = _place_kong_jie(hour_branch)
            aux_map["文昌"] = _cq["文昌"]
            aux_map["文曲"] = _cq["文曲"]
            malefic_map["火星"] = _hl["火星"]
            malefic_map["鈴星"] = _hl["鈴星"]
            malefic_map["地空"] = _kj["地空"]
            malefic_map["地劫"] = _kj["地劫"]
        else:
            aux_accuracy_note += " 文昌、文曲、火星、鈴星、地空、地劫需出生時辰，本次未計算。"

        # Star categories
        for s in ["左輔", "右弼", "文昌", "文曲", "天魁", "天鉞", "祿存"]:
            star_cat[s] = "auspicious"
        for s in ["擎羊", "陀羅", "火星", "鈴星", "地空", "地劫"]:
            star_cat[s] = "malefic"

        # Apply auxiliary/malefic stars to palaces' minor_stars
        branch_to_palace_idx: Dict[str, int] = {
            p.earthly_branch: i for i, p in enumerate(palaces)
        }
        all_aux = {**aux_map, **malefic_map}
        for star, branch in all_aux.items():
            p_idx = branch_to_palace_idx.get(branch)
            if p_idx is not None:
                if star not in palaces[p_idx].minor_stars:
                    palaces[p_idx].minor_stars.append(star)

        # 10b. V1.7.5: Ming Zhu / Shen Zhu / Tian Ma / Brightness / Score
        ming_zhu_val = _calc_ming_zhu(ming_branch_str) if time_known else None
        shen_zhu_val = _calc_shen_zhu(year_branch_str)
        tian_ma_branch_val = _calc_tian_ma_branch(year_branch_str)
        tian_ma_palace_val: Optional[str] = None
        if tian_ma_branch_val:
            for _p in palaces:
                if _p.earthly_branch == tian_ma_branch_val:
                    tian_ma_palace_val = _p.name
                    break
            # Add 天馬 to aux_map so it appears in auxiliary_star_map
            aux_map["天馬"] = tian_ma_branch_val
            star_cat["天馬"] = "auspicious"
            # Also add to palace minor_stars
            _tm_p_idx = branch_to_palace_idx.get(tian_ma_branch_val)
            if _tm_p_idx is not None and "天馬" not in palaces[_tm_p_idx].minor_stars:
                palaces[_tm_p_idx].minor_stars.append("天馬")
        brightness_map_val = _calc_brightness_map(palaces)
        ziwei_score_val, ziwei_score_label_val, ziwei_score_expl, ziwei_score_comps = _calc_ziwei_score(
            palaces, brightness_map_val, four_trans
        )

        # 10. Da Xian (V1.5.5)
        da_xian_direction, da_xian_start_age, da_xian_list = _calc_da_xian(
            ming_idx=ming_idx,
            bureau_number=bureau_num,
            year_stem=year_stem,
            gender=gender,
            palaces=palaces,
        )
        da_xian_accuracy = "phase1"
        da_xian_note = (
            "V1.5.5 大限為 Phase 1 骨架，依五行局數起大限，陽男陰女順行；"
            "尚未加入大限四化與流年飛化。"
        )

        # 11. calculation_mode
        if time_known:
            mode = "formal_layout_phase1"
            note = (
                "V1.7.5 已依農曆生日與出生時辰進行正式排盤，含十四主星、四化、"
                "核心輔星（左輔右弼、文昌文曲、天魁天鉞、祿存、天馬）、"
                "六煞（擎羊、陀羅、火星、鈴星、地空、地劫）與大限 Phase 1。"
                " V1.7.5 新增命主、身主、天馬、廟旺陷 Phase 1、盤面強度分數 Phase 1。"
                " 盤面強度分數不等同外部網站好運指數。"
            )
        else:
            mode = "partial_lunar_only"
            note = (
                "出生時間未知，紫微命宮、身宮與主星位置不可視為精準結果。"
                "已完成農曆轉換、天魁天鉞、祿存羊陀與左輔右弼基礎安星；"
                "文昌文曲、火鈴空劫需補填出生時辰。"
                " 命主需命宮地支，身主依年支計算。"
            )

        return ZiWeiChart(
            ming_palace=palaces[0],
            shen_palace=shen_palace,
            brother_palace=palaces[1],
            spouse_palace=palaces[2],
            children_palace=palaces[3],
            wealth_palace=palaces[4],
            health_palace=palaces[5],
            travel_palace=palaces[6],
            friends_palace=palaces[7],
            career_palace=palaces[8],
            property_palace=palaces[9],
            fortune_palace=palaces[10],
            parents_palace=palaces[11],
            main_stars=all_main,
            four_transformations=four_trans,
            is_mock=False,
            calculation_mode=mode,
            accuracy_note=note,
            lunar_year=lunar_year,
            lunar_month=lunar_month,
            lunar_day=lunar_day,
            lunar_is_leap_month=is_leap,
            birth_hour_branch=hour_branch,
            ming_branch=ming_branch_str,
            shen_branch=shen_branch_str,
            five_element_bureau=bureau_name,
            five_element_bureau_number=bureau_num,
            auxiliary_star_map=aux_map,
            malefic_star_map=malefic_map,
            star_categories=star_cat,
            da_xian=da_xian_list,
            da_xian_direction=da_xian_direction,
            da_xian_start_age=da_xian_start_age,
            da_xian_accuracy=da_xian_accuracy,
            auxiliary_accuracy_note=aux_accuracy_note,
            ming_zhu=ming_zhu_val,
            shen_zhu=shen_zhu_val,
            tian_ma_branch=tian_ma_branch_val,
            tian_ma_palace=tian_ma_palace_val,
            brightness_map=brightness_map_val,
            ziwei_score=ziwei_score_val,
            ziwei_score_label=ziwei_score_label_val,
            ziwei_score_explanation=ziwei_score_expl,
            ziwei_score_version="phase1_calibrated_v1",
            ziwei_score_components=ziwei_score_comps,
        )
