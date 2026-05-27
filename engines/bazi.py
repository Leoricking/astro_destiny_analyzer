"""
Astro Destiny Analyzer — BaZi (Eight Characters) Engine
Implements genuine sexagenary-cycle calculations.
V1.4: Solar term driven year/month pillar calculation.
  - Year boundary: 立春 (~Feb 4).
  - Month boundary: 12 solar terms (節令) with approximate dates.
  - calculation_mode = "solar_term_approx"; future versions may use
    precise astronomical solar longitudes.
V1.4.5: Day/hour pillar precision & 子時 policy.
  - _get_hour_branch(hour, minute): explicit time-branch mapping.
  - _hour_stem(day_stem, hour_branch): explicit hour-stem derivation.
  - zi_hour_policy: "late_zi_same_day" (default) | "late_zi_next_day".
  - day_pillar_accuracy, hour_pillar_accuracy, hour_pillar_is_precise fields.
"""
from datetime import date, time, timedelta
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


# ── Solar Term Tables (V1.4) ──────────────────────────────────────────────────

# 12 節令 approximate dates (month, day, resulting branch).
# Ordered within a calendar year (Jan→Dec).
# Before Jan 6 (小寒) the active branch is 子 (carried from Dec 7 大雪 of prev year).
_SOLAR_TERMS_APPROX: List[Tuple[int, int, EarthlyBranch]] = [
    (1,  6,  EarthlyBranch.CHOU),   # 小寒  → 丑月
    (2,  4,  EarthlyBranch.YIN),    # 立春  → 寅月 (also BaZi year boundary)
    (3,  6,  EarthlyBranch.MAO),    # 驚蟄  → 卯月
    (4,  5,  EarthlyBranch.CHEN),   # 清明  → 辰月
    (5,  6,  EarthlyBranch.SI),     # 立夏  → 巳月
    (6,  6,  EarthlyBranch.WU_),    # 芒種  → 午月
    (7,  7,  EarthlyBranch.WEI),    # 小暑  → 未月
    (8,  8,  EarthlyBranch.SHEN),   # 立秋  → 申月
    (9,  8,  EarthlyBranch.YOU),    # 白露  → 酉月
    (10, 8,  EarthlyBranch.XU),     # 寒露  → 戌月
    (11, 7,  EarthlyBranch.HAI),    # 立冬  → 亥月
    (12, 7,  EarthlyBranch.ZI),     # 大雪  → 子月
]

# 立春 approximate date (BaZi year boundary)
_LICHUN_MONTH = 2
_LICHUN_DAY   = 4


def _bazi_year(birth_date: date) -> int:
    """Return BaZi year integer; switches at 立春 (approx Feb 4)."""
    year = birth_date.year
    if birth_date < date(year, _LICHUN_MONTH, _LICHUN_DAY):
        year -= 1
    return year


def _month_branch_from_solar_terms(birth_date: date) -> EarthlyBranch:
    """
    Determine BaZi month branch using approximate solar term dates.
    Default is 子月 (carried from the previous year's 大雪 Dec 7)
    for dates before Jan 6 小寒.
    calculation_mode = "solar_term_approx"
    """
    year = birth_date.year
    current_branch: EarthlyBranch = EarthlyBranch.ZI  # pre-小寒 default
    for month, day, branch in _SOLAR_TERMS_APPROX:
        if birth_date >= date(year, month, day):
            current_branch = branch
    return current_branch


# ── Pillar Calculations ───────────────────────────────────────────────────────

def _year_pillar(birth_date: date) -> Pillar:
    """
    Year pillar.  V1.4: boundary is 立春 (~Feb 4) via _bazi_year().
    calculation_mode = "solar_term_approx"
    """
    year = _bazi_year(birth_date)
    stem_idx   = (year - 4) % 10
    branch_idx = (year - 4) % 12
    stem   = STEMS[stem_idx]
    branch = BRANCHES[branch_idx]
    return Pillar(heavenly_stem=stem, earthly_branch=branch,
                  element=STEM_ELEMENT[stem], label="年柱")


# Starting stem of 寅月 indexed by (year_stem_index % 5)
# 甲己→丙, 乙庚→戊, 丙辛→庚, 丁壬→壬, 戊癸→甲
_MONTH_STEM_BASE = [2, 4, 6, 8, 0]  # index into STEMS for 寅月

def _month_pillar(birth_date: date, year_stem: HeavenlyStem) -> Pillar:
    """
    Month pillar.  V1.4: boundary determined by solar terms via
    _month_branch_from_solar_terms().
    calculation_mode = "solar_term_approx"
    """
    branch = _month_branch_from_solar_terms(birth_date)
    branch_idx = BRANCHES.index(branch)  # 0-based index, 寅=2

    year_stem_idx = STEMS.index(year_stem)
    base_stem_idx = _MONTH_STEM_BASE[year_stem_idx % 5]
    # 寅月 has base stem; each subsequent branch adds 1 stem
    stem_offset = (branch_idx - 2) % 12
    stem = STEMS[(base_stem_idx + stem_offset) % 10]
    return Pillar(heavenly_stem=stem, earthly_branch=branch,
                  element=STEM_ELEMENT[stem], label="月柱")


# Reference: JDN 2415080 (1900-01-31) = 甲子日 (cycle index 0)
# Formula: standard proleptic Gregorian JDN computation.
_BAZI_JDN_REF = 2415080

def _jdn(d: date) -> int:
    """Compute Julian Day Number for a date."""
    a = (14 - d.month) // 12
    y = d.year + 4800 - a
    m = d.month + 12 * a - 3
    return (d.day + (153 * m + 2) // 5 + 365 * y
            + y // 4 - y // 100 + y // 400 - 32045)

def _day_pillar(effective_date: date) -> Pillar:
    """
    Day pillar via JDN sexagenary cycle.
    day_pillar_accuracy = "approx": the JDN reference (1900-01-31 = 甲子日)
    is widely used but not universally agreed; treat as approximate until
    verified against a canonical reference table.
    When zi_hour_policy = "late_zi_next_day", effective_date may differ
    from the actual birth date (see BaZiEngine.calculate).
    """
    jdn = _jdn(effective_date)
    idx = (jdn - _BAZI_JDN_REF) % 60
    stem   = STEMS[idx % 10]
    branch = BRANCHES[idx % 12]
    return Pillar(heavenly_stem=stem, earthly_branch=branch,
                  element=STEM_ELEMENT[stem], label="日柱")


# ── Hour Branch & Stem (V1.4.5) ───────────────────────────────────────────────

def _get_hour_branch(hour: int, minute: int) -> EarthlyBranch:
    """
    Map (hour, minute) to EarthlyBranch.
    子：23:00-00:59  丑：01:00-02:59  寅：03:00-04:59
    卯：05:00-06:59  辰：07:00-08:59  巳：09:00-10:59
    午：11:00-12:59  未：13:00-14:59  申：15:00-16:59
    酉：17:00-18:59  戌：19:00-20:59  亥：21:00-22:59
    minute is accepted for API completeness; branching is by hour only.
    """
    if hour == 23 or hour == 0:   return EarthlyBranch.ZI
    elif 1  <= hour < 3:          return EarthlyBranch.CHOU
    elif 3  <= hour < 5:          return EarthlyBranch.YIN
    elif 5  <= hour < 7:          return EarthlyBranch.MAO
    elif 7  <= hour < 9:          return EarthlyBranch.CHEN
    elif 9  <= hour < 11:         return EarthlyBranch.SI
    elif 11 <= hour < 13:         return EarthlyBranch.WU_
    elif 13 <= hour < 15:         return EarthlyBranch.WEI
    elif 15 <= hour < 17:         return EarthlyBranch.SHEN
    elif 17 <= hour < 19:         return EarthlyBranch.YOU
    elif 19 <= hour < 21:         return EarthlyBranch.XU
    else:                         return EarthlyBranch.HAI  # 21-22


def _hour_branch(t: time) -> EarthlyBranch:
    """Thin wrapper around _get_hour_branch for backward compatibility."""
    return _get_hour_branch(t.hour, t.minute)


# Starting stem of 子時 indexed by (day_stem_index % 5)
# 甲己→甲(0), 乙庚→丙(2), 丙辛→戊(4), 丁壬→庚(6), 戊癸→壬(8)
_HOUR_STEM_BASE = [0, 2, 4, 6, 8]


def _hour_stem(day_stem: HeavenlyStem, hour_branch: EarthlyBranch) -> HeavenlyStem:
    """
    Derive hour heavenly stem from day master and hour branch.
    Rule: 甲己→甲子起, 乙庚→丙子起, 丙辛→戊子起, 丁壬→庚子起, 戊癸→壬子起.
    Each subsequent branch increments the stem by 1.
    """
    day_stem_idx  = STEMS.index(day_stem)
    base          = _HOUR_STEM_BASE[day_stem_idx % 5]
    branch_idx    = BRANCHES.index(hour_branch)
    return STEMS[(base + branch_idx) % 10]


def _hour_pillar(birth_time: time, day_stem: HeavenlyStem) -> Pillar:
    branch = _get_hour_branch(birth_time.hour, birth_time.minute)
    stem   = _hour_stem(day_stem, branch)
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
                  current_year: Optional[int] = None,
                  zi_hour_policy: Optional[str] = None) -> BaZiChart:
        if current_year is None:
            from datetime import date as _d
            current_year = _d.today().year

        from config import ZI_HOUR_POLICY as _DEFAULT_ZI_POLICY
        policy = zi_hour_policy if zi_hour_policy is not None else _DEFAULT_ZI_POLICY

        # Year and month pillars always use the original birth date + solar terms.
        yp = _year_pillar(birth_date)
        mp = _month_pillar(birth_date, yp.heavenly_stem)

        # Day pillar: may shift one day forward when zi_hour_policy = late_zi_next_day
        # and the birth hour is 23:xx (晚子時).  Only the day/hour pillars are affected;
        # year and month boundaries remain tied to the actual birth date.
        time_known = birth_time is not None
        day_date = birth_date
        zi_note = ""
        if time_known and birth_time.hour == 23 and policy == "late_zi_next_day":
            day_date = birth_date + timedelta(days=1)
            zi_note = "晚子時換日派別會影響日柱與時柱，請依命理師習慣選擇。"

        dp = _day_pillar(day_date)
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

        accuracy_parts = [
            "V1.4 使用節氣近似日期切年切月；若需專業級精準，後續版本將導入天文節氣精確時刻。"
        ]
        if not time_known:
            accuracy_parts.append("時柱需精確出生時間，當前不可視為精準。")
        if zi_note:
            accuracy_parts.append(zi_note)

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
            calculation_mode="solar_term_approx",
            accuracy_note=" ".join(accuracy_parts),
            year_boundary_rule="lichun",
            month_boundary_rule="solar_terms",
            birth_time_accuracy="known" if time_known else "unknown",
            day_pillar_accuracy="approx",
            hour_pillar_accuracy="precise" if time_known else "unknown",
            zi_hour_policy=policy,
            hour_pillar_is_precise=time_known,
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
