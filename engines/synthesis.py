"""
Astro Destiny Analyzer — Synthesis Engine V1.2
Integrates Western astrology, BaZi, Zi Wei, blood type, and numerology
into a coherent narrative.

V1.2 changes (relative to V1.0):
  - Delegates love / career / stress narrative construction to narrative_rules.py
  - Richer paragraph-form text for all major sections
  - Expanded contradiction detection with integration suggestions
  - Fixed kwarg syntax: intimacy_boundary= / communication_advice= (not ':')
"""
from typing import Optional, List, Tuple
from core.models import (
    BirthProfile, WesternChart, BaZiChart, ZiWeiChart,
    BloodTypeAnalysis, NumerologyChart, SynthesisResult,
    ZodiacSign, FiveElement, TenGod,
)
from engines.narrative_rules import (
    get_sign_profile,
    build_love_narrative,
    build_career_narrative,
    build_stress_narrative,
    build_contradiction_analysis,
)


# ── Zodiac quick-access descriptors (kept for non-narrative sections) ─────────

_SIGN_KEYWORDS: dict[str, Tuple[str, str, str]] = {
    # (core traits, love style, career energy)
    "牡羊座": ("主動、果斷、充滿開創能量", "熱情直接，需要刺激與追逐感", "適合開拓型、競爭性強的工作"),
    "金牛座": ("穩定、務實、重視感官享受", "慢熱卻深情，重視安全感與物質基礎", "適合有長期積累回報的工作"),
    "雙子座": ("靈活、好奇、溝通能力強", "多變迷人，需要智識的碰撞", "適合溝通、媒體、多元事業"),
    "巨蟹座": ("敏感、直覺強、保護欲強烈", "需要安全感，以照顧表達愛", "適合照護、教育、家庭相關領域"),
    "獅子座": ("自信、慷慨、渴望被看見", "熱情大方，需要被欣賞", "適合表演、領導、創意產業"),
    "處女座": ("分析、細膩、追求完美", "謹慎而服務型，以實際行動表達愛", "適合分析、醫療、精密作業"),
    "天秤座": ("公平、優雅、重視和諧", "需要平衡與美感，重視伴侶關係", "適合藝術、公關、法律"),
    "天蠍座": ("深刻、強烈、掌握核心力量", "全情投入，對背叛零容忍", "適合研究、投資、心理領域"),
    "射手座": ("自由、樂觀、渴望擴展視野", "需要思想共鳴與精神自由", "適合教育、旅遊、哲學探索"),
    "摩羯座": ("紀律、雄心、長遠規劃", "謹慎投入，以責任感表達愛", "適合管理、政商、長期建設"),
    "水瓶座": ("獨立、前衛、人道主義", "需要精神自由，重視友誼平等", "適合科技、社會改革、創新"),
    "雙魚座": ("直覺、同理心、靈性敏感", "浪漫夢幻，容易感情融合", "適合藝術、靈性、醫療服務"),
}

_ELEMENT_DESC: dict[str, str] = {
    "木": "木代表生長、擴展與仁慈。強木命格具有開創力與同理心，但過旺時容易執念過深。",
    "火": "火代表熱情、智慧與光芒。強火命格具有領導力與感染力，但過旺時容易急躁衝動。",
    "土": "土代表穩定、承載與信用。強土命格踏實可靠，但過旺時容易守舊固執。",
    "金": "金代表決斷、義氣與精準。強金命格行事俐落、有原則，但過旺時容易過於嚴苛。",
    "水": "水代表智慧、流動與內省。強水命格思維靈活、洞察力深，但過旺時容易多慮優柔。",
}

_LIFE_PATH_CAREER: dict[int, List[str]] = {
    1: ["創業家", "CEO", "先鋒型領導者", "獨立顧問"],
    2: ["調解員", "外交官", "心理師", "HR", "行政協調"],
    3: ["作家", "演員", "行銷人", "教師", "公關"],
    4: ["工程師", "建築師", "財務規劃師", "專案管理師"],
    5: ["記者", "業務", "旅遊業", "翻譯", "自由工作者"],
    6: ["醫師", "社工", "教師", "家庭治療師", "設計師"],
    7: ["研究員", "分析師", "作家", "靈性導師", "哲學家"],
    8: ["企業家", "CFO", "投資人", "房地產", "律師"],
    9: ["NGO工作者", "藝術家", "教育家", "醫療志工", "社會改革者"],
    11: ["心靈導師", "藝術家", "直覺型顧問", "靈性治療師"],
    22: ["建築師", "社會企業家", "系統設計師", "跨國專案領導"],
    33: ["教育家", "療癒師", "心理師", "社區建設者"],
}

_ZIWEI_CAREER_STARS = {
    "紫微": "紫微入官祿，格局高、適合領導或獨當一面的工作。",
    "天府": "天府入財帛，財庫穩固，適合管理財務或資源型工作。",
    "太陽": "太陽代表外顯能量，適合公開場合、政治、媒體或教育工作。",
    "武曲": "武曲象徵執行力與財星，適合金融、軍事或商業實務。",
    "廉貞": "廉貞具競爭色彩，適合法律、軍警或需要決斷力的工作。",
    "天同": "天同偏向服務與福利，適合服務業、社福或輔助性工作。",
    "天機": "天機善謀略，適合策略規劃、諮詢、研究或IT。",
    "太陰": "太陰陰柔細膩，適合藝術、教育、後台支援工作。",
    "貪狼": "貪狼多才多藝，適合藝術、公關、業務或社交頻繁的工作。",
    "巨門": "巨門擅言辭，適合律師、老師、媒體或口才相關工作。",
    "天相": "天相具輔佐才，適合幕僚、行政、輔助型主管。",
    "天梁": "天梁具蔭護力，適合醫療、社工、監督、宗教領域。",
    "七殺": "七殺具霸氣，適合創業、軍警、體育或競爭激烈的行業。",
    "破軍": "破軍具破舊立新能量，適合改革性工作、創業或高風險高報酬行業。",
}


# ── Helper: extract planet sign ───────────────────────────────────────────────

def _planet_sign(western: WesternChart, planet_name: str) -> Optional[str]:
    for pp in western.planet_positions:
        if pp.planet.value == planet_name:
            return pp.sign.value
    return None


class SynthesisEngine:
    def synthesize(
        self,
        profile: BirthProfile,
        western: Optional[WesternChart],
        bazi: Optional[BaZiChart],
        ziwei: Optional[ZiWeiChart],
        blood: Optional[BloodTypeAnalysis],
        numerology: Optional[NumerologyChart],
    ) -> SynthesisResult:

        # ── Extract key chart values ──────────────────────────────────────────
        sun_sign  = _planet_sign(western, "太陽")  if western else None
        moon_sign = _planet_sign(western, "月亮")  if western else None
        venus_sign= _planet_sign(western, "金星")  if western else None
        mars_sign = _planet_sign(western, "火星")  if western else None
        mercury_sign = _planet_sign(western, "水星") if western else None
        saturn_sign  = _planet_sign(western, "土星") if western else None
        chiron_sign  = _planet_sign(western, "凱龍星") if western else None
        north_sign   = _planet_sign(western, "北交點") if western else None
        asc_sign  = western.ascendant.value if western else None
        desc_sign = western.descendant.value if western else None
        mc_sign   = western.mc.value if western else None
        ic_sign   = western.ic.value if western else None

        # ── Core Personality ──────────────────────────────────────────────────
        core_parts: List[str] = []

        if western and sun_sign:
            sp = get_sign_profile(sun_sign)
            sun_kw = _SIGN_KEYWORDS.get(sun_sign, ("", "", ""))
            asc_kw = _SIGN_KEYWORDS.get(asc_sign, ("", "", "")) if asc_sign else ("", "", "")
            core_parts.append(
                f"**西洋占星核心三角——太陽 / 月亮 / 上升**\n\n"
                f"太陽落在{sun_sign}，是你在這一生中渴望展現的本質自我。"
                f"{sp['personality']}\n\n"
                f"上升星座{asc_sign}是你呈現給世界的第一印象與外在氣質——"
                f"核心特質為「{asc_kw[0]}」，決定了他人對你最初的認知框架。"
            )
            if moon_sign:
                mp = get_sign_profile(moon_sign)
                moon_kw = _SIGN_KEYWORDS.get(moon_sign, ("", "", ""))
                core_parts.append(
                    f"月亮位於{moon_sign}，揭示你的私下本色與情緒安全感模式——"
                    f"核心特質：「{moon_kw[0]}」。{mp['personality']}"
                )

        if bazi:
            dm = bazi.day_master.value
            dm_elem = bazi.day_master_element.value
            fav = "、".join(e.value for e in bazi.favorable_elements)
            unfav = "、".join(e.value for e in bazi.unfavorable_elements)
            core_parts.append(
                f"**八字日主——{dm}（{dm_elem}）**\n\n"
                f"{_ELEMENT_DESC.get(dm_elem, '')}\n\n"
                f"你的喜用神為{fav}，忌神為{unfav}。"
                "這揭示了你天生的能量底色：在什麼樣的環境中你如魚得水，"
                "以及什麼樣的能量組合會為你帶來阻力。"
                "了解喜忌神是命盤實際應用的核心，"
                "能夠指引你在工作環境、居住方位、日常習慣等面向做出更符合天性的選擇。"
            )

        if ziwei:
            ming_stars = "、".join(ziwei.ming_palace.main_stars) if ziwei.ming_palace.main_stars else "無主星"
            ziwei_mode = getattr(ziwei, "calculation_mode", "mock_fallback")
            formal_note = ""
            if ziwei_mode == "formal_layout_phase1":
                formal_note = (
                    "\n\n（紫微正式盤已完成命宮 / 身宮 / 主星定位，"
                    "因此紫微結論可作為人格與宮位領域的重要參考。）"
                )
            elif ziwei_mode == "mock_fallback":
                formal_note = "\n\n（紫微目前為 fallback 資料，請以西洋占星與八字結論為主要參考。）"
            core_parts.append(
                f"**紫微命宮——{ziwei.ming_palace.earthly_branch}宮，主星：{ming_stars}**\n\n"
                f"{ziwei.ming_palace.interpretation}{formal_note}"
            )

        if numerology:
            core_parts.append(
                f"**生命靈數 {numerology.life_path_number}**\n\n"
                f"{numerology.life_path_description}"
            )

        core_personality = "\n\n---\n\n".join(core_parts) or "（請至少輸入出生日期以產生分析）"

        # ── Emotional Pattern ─────────────────────────────────────────────────
        emotional_parts: List[str] = []

        if western and moon_sign:
            mp = get_sign_profile(moon_sign)
            emotional_parts.append(
                f"**月亮（{moon_sign}）——情緒底層語言**\n\n"
                f"{mp['love']}\n\n"
                "月亮是你內在小孩的棲居之所。在親密關係中，"
                "它揭示了你最真實的安全感需求，以及你在感到威脅時的本能反應。"
                "理解你的月亮星座，是與自己建立更深慈悲的第一步。"
            )

        if bazi and bazi.five_element_strength:
            water_str = bazi.five_element_strength.get("水", "均衡")
            fire_str  = bazi.five_element_strength.get("火", "均衡")
            wood_str  = bazi.five_element_strength.get("木", "均衡")
            emotional_parts.append(
                f"**八字情感五行分析**\n\n"
                f"水（情感直覺與內省）：{water_str}\n"
                f"火（熱情外顯與溝通欲）：{fire_str}\n"
                f"木（感情中的成長欲與同理心）：{wood_str}\n\n"
                "水強者情感豐富細膩，直覺準確，但需注意避免多愁善感與過度思慮。\n"
                "水弱者情感表達偏理性，需要刻意練習說出感受，而非等待對方自己察覺。\n"
                "火強者情感熱烈易於表達，但需注意衝動之後的情緒管理。\n"
                "火弱者內心豐富卻難以外顯，需要一個安全的環境才能充分開放。"
            )

        emotional_pattern = "\n\n---\n\n".join(emotional_parts) or "情緒模式分析需要更完整的出生資料。"

        # ── Action Pattern ────────────────────────────────────────────────────
        action_parts: List[str] = []

        if western and mars_sign:
            mp = get_sign_profile(mars_sign)
            action_parts.append(
                f"**火星（{mars_sign}）——行動驅動力**\n\n"
                f"{mp['career']}\n\n"
                "火星決定了你面對挑戰時的本能反應：是衝鋒、是策謀、是協作，還是等待時機。"
                "了解火星所在星座，能讓你更有意識地部署自己的行動能量，"
                "而非在衝動和消極之間漫無目的地擺盪。"
            )

        if bazi:
            metal_str = bazi.five_element_strength.get("金", "均衡")
            wood_str2 = bazi.five_element_strength.get("木", "均衡")
            action_parts.append(
                f"**八字行動五行分析**\n\n"
                f"金（決斷力與執行力）：{metal_str}\n"
                f"木（行動力與開創欲）：{wood_str2}\n\n"
                "金強者決策果斷、執行力強，但需注意過度強硬帶來的人際摩擦。\n"
                "金弱者決策過程較長，優柔寡斷可能是需要刻意突破的模式。\n"
                "木強者行動積極、計畫層出不窮，但需注意執行力是否跟上創意速度。"
            )

        action_pattern = "\n\n---\n\n".join(action_parts) or "行動模式分析需要更完整的出生資料。"

        # ── Love Pattern (using V1.2 narrative builder) ───────────────────────
        # Resolve per-sign intimacy boundary and communication advice from narrative_rules
        ib = ""
        ca = ""
        if venus_sign:
            vp = get_sign_profile(venus_sign)
            ib = vp.get("intimacy_boundary", "")
            ca = vp.get("communication_advice", "")

        love_pattern = build_love_narrative(
            sun_sign=sun_sign,
            venus_sign=venus_sign,
            moon_sign=moon_sign,
            descendant=desc_sign,
            bazi_wealth_star=bazi.wealth_star.value if bazi and bazi.wealth_star else None,
            ziwei_spouse_stars=ziwei.spouse_palace.main_stars if ziwei else None,
            blood_love=blood.love_response if blood else None,
            intimacy_boundary=ib,
            communication_advice=ca,
        )

        # ── Career Pattern (using V1.2 narrative builder) ─────────────────────
        lp = numerology.life_path_number if numerology else None
        lp_careers = _LIFE_PATH_CAREER.get(lp, []) if lp else []

        ziwei_mode_for_career = getattr(ziwei, "calculation_mode", "mock_fallback") if ziwei else None
        career_pattern = build_career_narrative(
            sun_sign=sun_sign,
            mc_sign=mc_sign,
            mars_sign=mars_sign,
            bazi_power_star=bazi.power_star.value if bazi and bazi.power_star else None,
            ziwei_career_stars=ziwei.career_palace.main_stars if ziwei else None,
            lp_careers=lp_careers,
            life_path_number=lp,
            career_star_descs=_ZIWEI_CAREER_STARS,
        )
        if ziwei_mode_for_career == "formal_layout_phase1":
            career_pattern += (
                "\n\n---\n\n（紫微正式盤已完成官祿宮定位，以上紫微事業分析可作為正式參考。）"
            )

        suitable_careers: List[str] = list(lp_careers)
        if sun_sign:
            suitable_careers.append(_SIGN_KEYWORDS.get(sun_sign, ("", "", ""))[2])

        # ── Wealth Pattern ────────────────────────────────────────────────────
        wealth_parts: List[str] = []

        if bazi:
            metal_pct = bazi.five_element_ratio.get("金", 0.0)
            water_pct = bazi.five_element_ratio.get("水", 0.0)
            earth_pct = bazi.five_element_ratio.get("土", 0.0)
            wealth_parts.append(
                f"**八字財富五行**\n\n"
                f"金（{metal_pct}%）、水（{water_pct}%）、土（{earth_pct}%）在五行中的佔比，"
                "反映了你先天的財富能量底色。\n\n"
                "金代表決斷與資本化能力，水代表財富的流動性與機遇感知，"
                "土代表財富的積累與保守能力。三者的平衡決定了你的財富風格：\n"
                "金旺者善於果斷入市，水旺者能感知財富機遇，土旺者善於守財建資產。"
            )
            if bazi.wealth_star:
                wealth_parts.append(
                    f"**財星（{bazi.wealth_star.value}）**\n\n"
                    f"你的命盤中財星為{bazi.wealth_star.value}，"
                    "這決定了你獲取財富的主要模式。"
                    "正財代表穩定薪資型收入，偏財代表機遇型與投機型收入。"
                    "了解財星的強弱，能夠指引你選擇最符合天性的財富積累策略。"
                )

        if ziwei:
            wealth_stars = "、".join(ziwei.wealth_palace.main_stars) if ziwei.wealth_palace.main_stars else "無主星"
            wealth_parts.append(
                f"**紫微財帛宮（{wealth_stars}）**\n\n"
                "紫微財帛宮揭示你的財富來源類型、金錢觀念，以及你與財富之間的能量流動模式。"
                "財帛宮吉星多者，財路較廣；煞星重者，需更謹慎規避財務風險。"
            )

        if blood:
            wealth_parts.append(f"**血型財富觀輔助**\n\n{blood.money_attitude}")

        wealth_pattern = "\n\n---\n\n".join(wealth_parts) or "財富模式分析需要更完整的出生資料。"

        # ── Social Pattern ────────────────────────────────────────────────────
        social_parts: List[str] = []

        if western and mercury_sign:
            mp = get_sign_profile(mercury_sign)
            mercury_kw = _SIGN_KEYWORDS.get(mercury_sign, ("", "", ""))
            social_parts.append(
                f"**水星（{mercury_sign}）——溝通風格**\n\n"
                f"水星決定了你的思維模式、溝通方式與資訊處理節奏。"
                f"水星在{mercury_sign}：{mercury_kw[0]}。{mp['personality']}"
            )

        if blood:
            social_parts.append(f"**血型人際輔助**\n\n{blood.interpersonal_style}")

        if ziwei:
            friend_stars = "、".join(ziwei.friends_palace.main_stars) if ziwei.friends_palace.main_stars else "無主星"
            social_parts.append(
                f"**紫微交友宮（{friend_stars}）**\n\n"
                "交友宮揭示你與友人、同儕、部屬的互動模式，以及在你生命中出現的貴人與小人特質。"
            )

        social_pattern = "\n\n---\n\n".join(social_parts) or "人際模式分析需要更完整的出生資料。"

        # ── Family & Security ─────────────────────────────────────────────────
        family_parts: List[str] = []

        if western and ic_sign:
            ip = get_sign_profile(ic_sign)
            ic_kw = _SIGN_KEYWORDS.get(ic_sign, ("", "", ""))
            family_parts.append(
                f"**天底 IC（{ic_sign}）——心理根基與安全感模式**\n\n"
                f"天底是你命盤中最私密的軸點，代表你的心理根基、家庭背景，"
                f"以及你在最深層最需要的安全感是什麼。"
                f"IC在{ic_sign}：核心特質為「{ic_kw[0]}」。{ip['personality']}\n\n"
                "了解自己的 IC，能夠幫助你明白為什麼某些環境讓你感到安全，"
                "而某些環境卻讓你感到如履薄冰。"
            )

        if ziwei:
            prop_stars = "、".join(ziwei.property_palace.main_stars) if ziwei.property_palace.main_stars else "無主星"
            family_parts.append(
                f"**紫微田宅宮（{prop_stars}）**\n\n"
                "田宅宮代表家庭環境、不動產運勢，以及你對「家」這個概念的內在詮釋。"
                "田宅宮吉星入宮者，家庭環境較和諧、不動產緣較佳；"
                "煞星重者，可能在家庭議題上有較多需要處理的能量。"
            )

        family_security = "\n\n---\n\n".join(family_parts) or "家庭安全感分析需要更完整的出生資料。"

        # ── Stress & Shadow (using V1.2 narrative builder) ────────────────────
        stress_shadow = build_stress_narrative(
            saturn_sign=saturn_sign,
            chiron_sign=chiron_sign,
            unfav_elements=[e.value for e in bazi.unfavorable_elements] if bazi else None,
            blood_stress=blood.stress_response if blood else None,
        )

        # ── Life Lessons ──────────────────────────────────────────────────────
        lesson_parts: List[str] = []

        if western and north_sign:
            np = get_sign_profile(north_sign)
            north_kw = _SIGN_KEYWORDS.get(north_sign, ("", "", ""))
            lesson_parts.append(
                f"**北交點（{north_sign}）——靈魂進化方向**\n\n"
                f"北交點是你此生靈魂的進化箭頭，指向你需要刻意向其學習的能量方向。"
                f"北交點在{north_sign}：{np['personality']}\n\n"
                f"朝向{north_sign}的特質：「{north_kw[0]}」努力，雖然不自然，卻是真正成長的路徑。"
                "南交點所在則代表你過去世（或童年）已熟悉的舒適區——"
                "它是你的避風港，但若過度倚賴，便成為阻礙進化的執念。"
            )

        if numerology:
            lesson_parts.append(
                f"**生命靈數 {numerology.life_path_number} 人生課題**\n\n"
                f"{numerology.life_path_description}"
            )

        life_lessons = "\n\n---\n\n".join(lesson_parts) or "人生課題分析需要更完整的出生資料。"

        # ── Innate Gifts ──────────────────────────────────────────────────────
        gifts_parts: List[str] = []

        if bazi:
            fav_desc = "、".join(e.value for e in bazi.favorable_elements)
            gifts_parts.append(
                f"**喜用神（{fav_desc}）——你的天賦能量頻率**\n\n"
                "喜用神是你天生就能輕鬆駕馭的能量，是你在順境中自然湧現的內在資源。"
                "當生活環境、工作性質、人際關係的五行屬性符合你的喜用神時，"
                "你會感到一種「本來如此」的輕鬆感。\n\n"
                "實際應用：在選擇工作、居住地、合作夥伴甚至飲食習慣時，"
                "有意識地引入喜用神對應的五行能量，能夠為你的人生帶來長期的順流感。"
            )

        if numerology:
            gifts_parts.append(
                f"**天賦數 {numerology.talent_number}**\n\n"
                f"{numerology.talent_description}"
            )

        if western and sun_sign:
            sp = get_sign_profile(sun_sign)
            gifts_parts.append(
                f"**太陽天賦（{sun_sign}）**\n\n{sp['career']}"
            )

        innate_gifts = "\n\n---\n\n".join(gifts_parts) or "天賦優勢分析需要更完整的出生資料。"

        # ── Recurring Challenges ──────────────────────────────────────────────
        recurring_parts: List[str] = []

        if bazi and bazi.unfavorable_elements:
            unfav_desc = "、".join(e.value for e in bazi.unfavorable_elements)
            recurring_parts.append(
                f"**忌神（{unfav_desc}）——反覆出現的阻力模式**\n\n"
                "忌神旺盛的流年往往是挑戰集中的時期。"
                "但了解忌神的意義在於：它不是命運的詛咒，而是一種特定頻率的能量挑戰。"
                "當你意識到「又來了」，便能更快從受害者模式轉換到策略應對模式——"
                "守成、簡化、暫緩重大決策，等待喜用神流年的到來再積極部署。"
            )

        if saturn_sign:
            sp = get_sign_profile(saturn_sign)
            recurring_parts.append(
                f"**土星反覆課題（{saturn_sign}）**\n\n"
                f"土星在{saturn_sign}的課題會在你的人生中反覆出現，直到你真正精熟為止。"
                f"{sp['personality']}\n\n"
                "每一次遭遇這個主題的困境，都是土星在邀請你再往深一層。"
            )

        recurring_challenges = "\n\n---\n\n".join(recurring_parts) or "反覆模式分析需要更完整的出生資料。"

        # ── Love Styles ───────────────────────────────────────────────────────
        suitable_love_styles: List[str] = []
        if desc_sign:
            suitable_love_styles.append(f"具有{desc_sign}特質的伴侶（第七宮能量互補）")
        if venus_sign:
            vp = get_sign_profile(venus_sign)
            suitable_love_styles.append(f"能理解{venus_sign}式愛語的伴侶")
        if blood:
            suitable_love_styles.append(f"能接納{profile.blood_type.value}型特質的伴侶")

        # ── Temporal Advice ───────────────────────────────────────────────────
        from datetime import date as _date
        current_year = _date.today().year

        year_advice_parts: List[str] = []
        three_year_parts: List[str] = []

        if bazi and bazi.liu_nian:
            nian = bazi.liu_nian[0]
            nian_elem_stem = None
            # Determine if this year's stem element is favorable or unfavorable
            from engines.bazi import STEM_ELEMENT
            from core.models import FiveElement as FE
            nian_elem = STEM_ELEMENT[nian.stem].value
            is_fav = any(e.value == nian_elem for e in bazi.favorable_elements)
            is_unfav = any(e.value == nian_elem for e in bazi.unfavorable_elements)
            assessment = "屬於你的喜用神——宜積極開展新計畫、拓展機會" if is_fav else (
                "屬於你的忌神——宜守成、聚焦核心、避免高風險決策" if is_unfav else
                "為中性能量——宜保持穩定步伐"
            )
            year_advice_parts.append(
                f"**{nian.year}年（{nian.stem.value}{nian.branch.value}年）流年分析**\n\n"
                f"今年流年天干五行屬「{nian_elem}」，{assessment}。\n\n"
                "流年是大運與命盤五行的交互作用，本年的機遇或挑戰將在此框架內展開。"
                "建議結合大運的整體趨勢，判斷本年是「擴張年」還是「整固年」。"
            )

            if len(bazi.liu_nian) >= 3:
                three_yr_data = []
                for n in bazi.liu_nian[:3]:
                    ne = STEM_ELEMENT[n.stem].value
                    tone = "順" if any(e.value == ne for e in bazi.favorable_elements) else (
                        "逆" if any(e.value == ne for e in bazi.unfavorable_elements) else "平"
                    )
                    three_yr_data.append(f"{n.year}年（{n.stem.value}{n.branch.value}，{ne}，{tone}年）")
                three_year_parts.append(
                    f"**未來三年趨勢**\n\n"
                    + "\n".join(f"- {d}" for d in three_yr_data) + "\n\n"
                    "順年：宜擴張、投資、拓展新領域；逆年：宜整固、沉澱、處理遺留問題；"
                    "平年：宜維持現有節奏，穩中求進。\n\n"
                    "建議每年年初重新評估流年能量與你的喜忌神關係，動態調整年度計畫。"
                )

        if numerology:
            py = numerology.personal_year
            year_advice_parts.append(
                f"**個人年數 {py}**\n\n{numerology.personal_year_description}"
            )

        one_year_advice  = "\n\n---\n\n".join(year_advice_parts) or "需要出生資料以計算流年建議。"
        three_year_advice = "\n\n---\n\n".join(three_year_parts)  or "需要出生資料以計算三年趨勢。"

        # ── Contradiction Detection (using V1.2 builder) ──────────────────────
        dm_is_strong = False
        if bazi:
            dm_is_strong = bazi.five_element_ratio.get(
                bazi.day_master_element.value, 0.0
            ) >= 25.0

        contradictions, integration_suggestions = build_contradiction_analysis(
            bazi_element_strength=bazi.five_element_strength if bazi else None,
            sun_sign=sun_sign,
            life_path_number=lp,
            dm_is_strong=dm_is_strong,
        )

        return SynthesisResult(
            core_personality=core_personality,
            emotional_pattern=emotional_pattern,
            action_pattern=action_pattern,
            love_pattern=love_pattern,
            career_pattern=career_pattern,
            wealth_pattern=wealth_pattern,
            social_pattern=social_pattern,
            family_security=family_security,
            stress_shadow=stress_shadow,
            life_lessons=life_lessons,
            innate_gifts=innate_gifts,
            recurring_challenges=recurring_challenges,
            suitable_careers=suitable_careers,
            suitable_love_styles=suitable_love_styles,
            one_year_advice=one_year_advice,
            three_year_advice=three_year_advice,
            contradictions=contradictions,
            integration_suggestions=integration_suggestions,
        )
