"""
Astro Destiny Analyzer — BaZi (Eight Characters) Engine
Implements genuine sexagenary-cycle calculations.
Solar term boundaries are approximated to the 4th/6th of each month for V1.
TODO: Replace solar term dates with precise 節氣 table for production accuracy.
"""
from datetime import date, time
from typing import Optional, List, Dict, Tuple
from core.models import (
    BaZiChart, Pillar, LuckPeriod, AnnualLuck,
    HeavenlyStem, EarthlyBranch, FiveElement, TenGod,
)

# ── Reference Tables ──────────────────────────────────────────────────────────

STEMS: List[HeavenlyStem] = list(HeavenlyStem)       # 甲乙丙丁戊己庚辛壬癸
BRANCHES: List[EarthlyBranch] = list(EarthlyBranch)  # 子丑寅卯辰巳午未申酉戌亥

STEM_ELEMENT: Dict[HeavenlyStem, FiveElement] = {
    HeavenlyStem.JIA:  FiveElement.WOOD,
    HeavenlyStem.YI:   FiveElement.WOOD,
    HeavenlyStem.BING: FiveElement.FIRE,
    HeavenlyStem.DING: FiveElement.FIRE,
    HeavenlyStem.WU:   FiveElement.EARTH,
    HeavenlyStem.JI:   FiveElement.EARTH,
    HeavenlyStem.GENG: FiveElement.METAL,
    HeavenlyStem.XIN:  FiveElement.METAL,
    HeavenlyStem.REN:  FiveElement.WATER,
    HeavenlyStem.GUI:  FiveElement.WATER,
}

BRANCH_ELEMENT: Dict[EarthlyBranch, FiveElement] = {
    EarthlyBranch.ZI:   FiveElement.WATER,
    EarthlyBranch.CHOU: FiveElement.EARTH,
    EarthlyBranch.YIN:  FiveElement.WOOD,
    EarthlyBranch.MAO:  FiveElement.WOOD,
    EarthlyBranch.CHEN: FiveElement.EARTH,
    EarthlyBranch.SI:   FiveElement.FIRE,
    EarthlyBranch.WU_:  FiveElement.FIRE,
    EarthlyBranch.WEI:  FiveElement.EARTH,
    EarthlyBranch.SHEN: FiveElement.METAL,
    EarthlyBranch.YOU:  FiveElement.METAL,
    EarthlyBranch.XU:   FiveElement.EARTH,
    EarthlyBranch.HAI:  FiveElement.WATER,
}

# yin/yang: even index = yang (甲丙戊庚壬) / odd = yin (乙丁己辛癸)
def _stem_yang(s: HeavenlyStem) -> bool:
    return STEMS.index(s) % 2 == 0

# Five-element generation order: WOOD→FIRE→EARTH→METAL→WATER
_GEN_ORDER = [FiveElement.WOOD, FiveElement.FIRE, FiveElement.EARTH,
              FiveElement.METAL, FiveElement.WATER]

def _generates(a: FiveElement, b: FiveElement) -> bool:
    """Returns True if element a generates element b."""
    i = _GEN_ORDER.index(a)
    return _GEN_ORDER[(i + 1) % 5] == b

def _controls(a: FiveElement, b: FiveElement) -> bool:
    """Returns True if element a controls element b (克)."""
    i = _GEN_ORDER.index(a)
    return _GEN_ORDER[(i + 2) % 5] == b


# ── Pillar Calculations ───────────────────────────────────────────────────────

def _year_pillar(birth_date: date) -> Pillar:
    """
    Year pillar based on Gregorian year.
    Strict BaZi uses Lichun (~Feb 4) as the year boundary.
    TODO: Use exact Lichun date for the given year for production accuracy.
    """
    year = birth_date.year
    # Approximate: if born before Feb 4, use previous year's stem/branch
    if (birth_date.month == 1) or (birth_date.month == 2 and birth_date.day < 4):
        year -= 1
    stem_idx   = (year - 4) % 10
    branch_idx = (year - 4) % 12
    stem   = STEMS[stem_idx]
    branch = BRANCHES[branch_idx]
    return Pillar(heavenly_stem=stem, earthly_branch=branch,
                  element=STEM_ELEMENT[stem], label="年柱")


# Month branch table (0-indexed from Jan)
# Jan→丑, Feb→寅, Mar→卯, Apr→辰, May→巳, Jun→午,
# Jul→未, Aug→申, Sep→酉, Oct→戌, Nov→亥, Dec→子
_MONTH_BRANCH = [
    EarthlyBranch.CHOU,  # Jan  (1)
    EarthlyBranch.YIN,   # Feb  (2)
    EarthlyBranch.MAO,   # Mar  (3)
    EarthlyBranch.CHEN,  # Apr  (4)
    EarthlyBranch.SI,    # May  (5)
    EarthlyBranch.WU_,   # Jun  (6)
    EarthlyBranch.WEI,   # Jul  (7)
    EarthlyBranch.SHEN,  # Aug  (8)
    EarthlyBranch.YOU,   # Sep  (9)
    EarthlyBranch.XU,    # Oct  (10)
    EarthlyBranch.HAI,   # Nov  (11)
    EarthlyBranch.ZI,    # Dec  (12)
]

# Starting stem of 寅月 indexed by (year_stem_index % 5)
# 甲己→丙, 乙庚→戊, 丙辛→庚, 丁壬→壬, 戊癸→甲
_MONTH_STEM_BASE = [2, 4, 6, 8, 0]  # index into STEMS for 寅月

def _month_pillar(birth_date: date, year_stem: HeavenlyStem) -> Pillar:
    """
    Month pillar.
    Strict BaZi uses actual 節氣 dates (approx every 15° of solar longitude).
    TODO: Use precise 節氣 table for production accuracy.
    """
    month = birth_date.month
    # Approximate: transition around the 6th of each month
    if birth_date.day < 6:
        month -= 1
        if month == 0:
            month = 12

    branch = _MONTH_BRANCH[month - 1]
    branch_idx = BRANCHES.index(branch)  # 0-based index, 寅=2

    year_stem_idx = STEMS.index(year_stem)
    base_stem_idx = _MONTH_STEM_BASE[year_stem_idx % 5]
    # 寅月 has base stem; each subsequent branch adds 1 stem
    # branch_idx relative to 寅 (index 2)
    stem_offset = (branch_idx - 2) % 12
    stem = STEMS[(base_stem_idx + stem_offset) % 10]
    return Pillar(heavenly_stem=stem, earthly_branch=branch,
                  element=STEM_ELEMENT[stem], label="月柱")


# Reference: JDN 2415080 (1900-01-31) = 甲子日 (cycle index 0)
_BAZI_JDN_REF = 2415080

def _jdn(d: date) -> int:
    """Compute Julian Day Number for a date."""
    a = (14 - d.month) // 12
    y = d.year + 4800 - a
    m = d.month + 12 * a - 3
    return (d.day + (153 * m + 2) // 5 + 365 * y
            + y // 4 - y // 100 + y // 400 - 32045)

def _day_pillar(birth_date: date) -> Pillar:
    jdn = _jdn(birth_date)
    idx = (jdn - _BAZI_JDN_REF) % 60
    stem   = STEMS[idx % 10]
    branch = BRANCHES[idx % 12]
    return Pillar(heavenly_stem=stem, earthly_branch=branch,
                  element=STEM_ELEMENT[stem], label="日柱")


# Hour branch: 子時=23-1, 丑=1-3, 寅=3-5, 卯=5-7, 辰=7-9, 巳=9-11,
#              午=11-13, 未=13-15, 申=15-17, 酉=17-19, 戌=19-21, 亥=21-23
def _hour_branch(t: time) -> EarthlyBranch:
    h = t.hour
    if h == 23 or h == 0:    return EarthlyBranch.ZI
    elif 1 <= h < 3:          return EarthlyBranch.CHOU
    elif 3 <= h < 5:          return EarthlyBranch.YIN
    elif 5 <= h < 7:          return EarthlyBranch.MAO
    elif 7 <= h < 9:          return EarthlyBranch.CHEN
    elif 9 <= h < 11:         return EarthlyBranch.SI
    elif 11 <= h < 13:        return EarthlyBranch.WU_
    elif 13 <= h < 15:        return EarthlyBranch.WEI
    elif 15 <= h < 17:        return EarthlyBranch.SHEN
    elif 17 <= h < 19:        return EarthlyBranch.YOU
    elif 19 <= h < 21:        return EarthlyBranch.XU
    else:                     return EarthlyBranch.HAI

# Starting stem of 子時 indexed by (day_stem_index % 5)
# 甲己→甲, 乙庚→丙, 丙辛→戊, 丁壬→庚, 戊癸→壬
_HOUR_STEM_BASE = [0, 2, 4, 6, 8]

def _hour_pillar(birth_time: time, day_stem: HeavenlyStem) -> Pillar:
    branch = _hour_branch(birth_time)
    branch_idx = BRANCHES.index(branch)
    day_stem_idx = STEMS.index(day_stem)
    base = _HOUR_STEM_BASE[day_stem_idx % 5]
    stem = STEMS[(base + branch_idx) % 10]
    return Pillar(heavenly_stem=stem, earthly_branch=branch,
                  element=STEM_ELEMENT[stem], label="時柱")


# ── Ten Gods ──────────────────────────────────────────────────────────────────

def _ten_god(day_master: HeavenlyStem, other: HeavenlyStem) -> TenGod:
    dm_elem   = STEM_ELEMENT[day_master]
    oth_elem  = STEM_ELEMENT[other]
    dm_yang   = _stem_yang(day_master)
    oth_yang  = _stem_yang(other)
    same_polarity = dm_yang == oth_yang

    if dm_elem == oth_elem:
        return TenGod.BIJIAN if same_polarity else TenGod.JIECAI
    if _generates(dm_elem, oth_elem):
        return TenGod.SHISHEN if same_polarity else TenGod.SHANGGUAN
    if _generates(oth_elem, dm_elem):
        return TenGod.PIANYIN if same_polarity else TenGod.ZHENGYIN
    if _controls(dm_elem, oth_elem):
        return TenGod.PIANCAI if same_polarity else TenGod.ZHENGCAI
    if _controls(oth_elem, dm_elem):
        return TenGod.QIANGUAN if same_polarity else TenGod.ZHENGGUAN
    return TenGod.BIJIAN  # fallback


# ── Five-element Ratio ────────────────────────────────────────────────────────

def _five_element_ratio(pillars: List[Pillar], hour_pillar: Optional[Pillar]) -> Dict[str, float]:
    counts: Dict[str, float] = {e.value: 0.0 for e in FiveElement}
    all_pillars = [p for p in pillars if p is not None]
    if hour_pillar:
        all_pillars.append(hour_pillar)
    for p in all_pillars:
        stem_elem   = STEM_ELEMENT[p.heavenly_stem].value
        branch_elem = BRANCH_ELEMENT[p.earthly_branch].value
        counts[stem_elem]   += 1.0
        counts[branch_elem] += 0.5   # branch hidden stems weighted lower
    total = sum(counts.values()) or 1.0
    return {k: round(v / total * 100, 1) for k, v in counts.items()}


def _five_element_strength(ratio: Dict[str, float]) -> Dict[str, str]:
    avg = sum(ratio.values()) / len(ratio)
    result = {}
    for k, v in ratio.items():
        if v >= avg * 1.4:
            result[k] = "強"
        elif v <= avg * 0.6:
            result[k] = "弱"
        else:
            result[k] = "均衡"
    return result


# ── Favorable / Unfavorable Elements ─────────────────────────────────────────

def _favorable_elements(day_master: HeavenlyStem,
                         ratio: Dict[str, float]) -> Tuple[List[FiveElement], List[FiveElement]]:
    """
    Simplified 喜用神 algorithm.
    TODO: Replace with a full 格局分析 algorithm for production accuracy.
    Heuristic: identify the day master's element; find what's weak and needs support
    versus what's over-strong and needs control.
    """
    dm_elem = STEM_ELEMENT[day_master]
    dm_pct  = ratio.get(dm_elem.value, 0.0)

    # Determine if day master is "strong" (旺) or "weak" (弱)
    strong_threshold = 25.0
    dm_is_strong = dm_pct >= strong_threshold

    if dm_is_strong:
        # Need output/control elements: what dm generates (food/hurt gods)
        dm_idx  = _GEN_ORDER.index(dm_elem)
        outlet  = _GEN_ORDER[(dm_idx + 1) % 5]   # 食傷: what dm generates
        control = _GEN_ORDER[(dm_idx + 2) % 5]   # 財: what outlet generates
        fav = [outlet, control]
        unfav = [_GEN_ORDER[(dm_idx + 3) % 5]]   # 官殺: controls dm
    else:
        # Need support: what generates dm (印) and same element (比劫)
        dm_idx = _GEN_ORDER.index(dm_elem)
        support = _GEN_ORDER[(dm_idx - 1) % 5]   # 印: generates dm
        fav = [support, dm_elem]
        unfav = [_GEN_ORDER[(dm_idx + 2) % 5]]   # 財: exhausted by dm's output

    return fav, unfav


# ── Main Engine ───────────────────────────────────────────────────────────────

class BaZiEngine:
    def calculate(self, birth_date: date,
                  birth_time: Optional[time] = None,
                  current_year: Optional[int] = None) -> BaZiChart:
        if current_year is None:
            from datetime import date as _d
            current_year = _d.today().year

        yp = _year_pillar(birth_date)
        mp = _month_pillar(birth_date, yp.heavenly_stem)
        dp = _day_pillar(birth_date)
        hp = _hour_pillar(birth_time, dp.heavenly_stem) if birth_time else None

        day_master = dp.heavenly_stem
        dm_elem    = STEM_ELEMENT[day_master]

        # Five-element ratio
        base_pillars = [yp, mp, dp]
        ratio    = _five_element_ratio(base_pillars, hp)
        strength = _five_element_strength(ratio)
        fav, unfav = _favorable_elements(day_master, ratio)

        # Ten gods map (over all non-day stems)
        ten_gods: Dict[str, str] = {}
        for s in STEMS:
            if s != day_master:
                ten_gods[s.value] = _ten_god(day_master, s).value

        # Star categories (from ten gods)
        def _first_tg(*tgs: TenGod) -> Optional[TenGod]:
            for tg in tgs:
                if tg.value in ten_gods.values():
                    return tg
            return None

        wealth_star = _first_tg(TenGod.ZHENGCAI, TenGod.PIANCAI)
        power_star  = _first_tg(TenGod.ZHENGGUAN, TenGod.QIANGUAN)
        print_star  = _first_tg(TenGod.ZHENGYIN,  TenGod.PIANYIN)
        output_star = _first_tg(TenGod.SHISHEN,   TenGod.SHANGGUAN)
        sibling_star = _first_tg(TenGod.BIJIAN,   TenGod.JIECAI)

        # Da Yun (major luck periods, 10-year cycles)
        # Direction: yang male / yin female = forward; yang female / yin male = backward
        # TODO: Use gender for direction in production; here default to forward.
        da_yun = self._calc_da_yun(mp, start_age=8, count=8)

        # Annual luck for next 10 years
        liu_nian = self._calc_liu_nian(current_year, count=10)

        return BaZiChart(
            year_pillar=yp,
            month_pillar=mp,
            day_pillar=dp,
            hour_pillar=hp,
            day_master=day_master,
            day_master_element=dm_elem,
            five_element_ratio=ratio,
            five_element_strength=strength,
            favorable_elements=fav,
            unfavorable_elements=unfav,
            wealth_star=wealth_star,
            power_star=power_star,
            print_star=print_star,
            output_star=output_star,
            sibling_star=sibling_star,
            ten_gods_map=ten_gods,
            da_yun=da_yun,
            liu_nian=liu_nian,
            is_mock=False,
        )

    def _calc_da_yun(self, month_pillar: Pillar,
                     start_age: int, count: int) -> List[LuckPeriod]:
        """Generate major luck periods forward from month pillar."""
        mp_idx_stem   = STEMS.index(month_pillar.heavenly_stem)
        mp_idx_branch = BRANCHES.index(month_pillar.earthly_branch)
        periods = []
        for i in range(count):
            s_idx = (mp_idx_stem   + i + 1) % 10
            b_idx = (mp_idx_branch + i + 1) % 12
            s = STEMS[s_idx]
            b = BRANCHES[b_idx]
            age_start = start_age + i * 10
            periods.append(LuckPeriod(
                start_age=age_start,
                end_age=age_start + 9,
                stem=s,
                branch=b,
                label=f"{s.value}{b.value}",
            ))
        return periods

    def _calc_liu_nian(self, current_year: int, count: int) -> List[AnnualLuck]:
        records = []
        for offset in range(count):
            y = current_year + offset
            s_idx = (y - 4) % 10
            b_idx = (y - 4) % 12
            records.append(AnnualLuck(
                year=y,
                stem=STEMS[s_idx],
                branch=BRANCHES[b_idx],
            ))
        return records
