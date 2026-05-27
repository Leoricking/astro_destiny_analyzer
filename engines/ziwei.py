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

from core.models import ZiWeiChart, ZiWeiPalace

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
    Algorithm (V1.5 Phase 1 — common 飛宮訣):
      Days are grouped in batches of bureau_number starting at 寅(2).
      Within each group the days count backwards from the next group's anchor.
      Formula: branch = (3 + 2*(group-1)*N - D) % 12
      where group = ceil(D / N), N = bureau_number, D = lunar_day.
    Returns branch index (0=子).
    """
    d = max(1, min(30, lunar_day))
    n = bureau_number
    group = math.ceil(d / n)
    return (3 + 2 * (group - 1) * n - d) % 12


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
                  birth_time: Optional[time] = None) -> ZiWeiChart:
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
            branch_idx = (ming_idx + palace_idx) % 12
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
        shen_offset = (shen_idx - ming_idx) % 12
        shen_palace = _build_palace(shen_offset, "身宮")

        all_main = [s for stars in star_placement.values() for s in stars]

        # 9. calculation_mode
        if time_known:
            mode = "formal_layout_phase1"
            note = (
                "V1.5 已依農曆生日與出生時辰進行紫微斗數第一階段正式排盤；"
                "十四主星與四化已安置，輔星、煞星、大限與流年將於後續版本補齊。"
                " V1.5 對閏月採保守處理，後續版本將加入精準閏月流派設定。"
            )
        else:
            mode = "partial_lunar_only"
            note = (
                "出生時間未知，紫微命宮、身宮與主星位置不可視為精準結果。"
                "已完成農曆轉換；命宮僅依農曆月份估算，時辰資料需補充。"
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
        )
