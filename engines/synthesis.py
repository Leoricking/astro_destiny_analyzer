"""
Astro Destiny Analyzer — Synthesis Engine
Integrates Western astrology, BaZi, Zi Wei, blood type, and numerology
into a coherent narrative. Each sub-engine's output feeds into a shared
interpretation framework. Contradictions between systems are surfaced
explicitly rather than glossed over.
"""
from typing import Optional, List, Tuple
from core.models import (
    BirthProfile, WesternChart, BaZiChart, ZiWeiChart,
    BloodTypeAnalysis, NumerologyChart, SynthesisResult,
    ZodiacSign, FiveElement, TenGod,
)


# ── Zodiac descriptors ────────────────────────────────────────────────────────

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

        contradictions: List[str] = []
        integration_suggestions: List[str] = []

        # ── Core Personality ─────────────────────────────────────────────────
        core_parts: List[str] = []
        sun_sign = None
        asc_sign = None

        if western:
            for pp in western.planet_positions:
                if pp.planet.value == "太陽":
                    sun_sign = pp.sign.value
                elif pp.planet.value == "月亮":
                    moon_sign = pp.sign.value
            asc_sign = western.ascendant.value
            sun_kw = _SIGN_KEYWORDS.get(sun_sign, ("", "", ""))
            core_parts.append(
                f"從西洋占星的角度，你的太陽星座位於{sun_sign}，"
                f"核心特質為「{sun_kw[0]}」，代表你在生命中追求展現的本質自我。"
                f"上升星座{asc_sign}則是你展現給外界的第一印象與外在氣質，"
                "形塑了他人對你的初始認知。"
            )

        if bazi:
            dm = bazi.day_master.value
            dm_elem = bazi.day_master_element.value
            fav = "、".join(e.value for e in bazi.favorable_elements)
            unfav = "、".join(e.value for e in bazi.unfavorable_elements)
            core_parts.append(
                f"在八字命盤中，你的日主為「{dm}」，屬{dm_elem}性，"
                f"{_ELEMENT_DESC.get(dm_elem, '')} "
                f"喜用神為{fav}，忌神為{unfav}。"
                "這揭示了你天生的能量底色：你在什麼樣的環境中如魚得水，"
                "以及什麼樣的能量組合會為你帶來阻力。"
            )

        if ziwei:
            ming_stars = "、".join(ziwei.ming_palace.main_stars) if ziwei.ming_palace.main_stars else "無主星"
            core_parts.append(
                f"紫微命宮位於{ziwei.ming_palace.earthly_branch}宮，"
                f"入宮主星：{ming_stars}。"
                f"{ziwei.ming_palace.interpretation}"
            )

        if numerology:
            core_parts.append(
                f"生命靈數{numerology.life_path_number}的你，"
                f"{numerology.life_path_description}"
            )

        core_personality = "\n\n".join(core_parts) or "（請至少輸入出生日期以產生分析）"

        # ── Emotional Pattern ────────────────────────────────────────────────
        emotional_parts: List[str] = []
        if western:
            moon_kw = _SIGN_KEYWORDS.get(getattr(western, "_moon_sign", ""), None)
            moon_positions = [pp for pp in western.planet_positions if pp.planet.value == "月亮"]
            if moon_positions:
                msign = moon_positions[0].sign.value
                mkw = _SIGN_KEYWORDS.get(msign, ("", "", ""))
                emotional_parts.append(
                    f"月亮位於{msign}，揭示你的情緒底層需求：{mkw[0]}。"
                    "月亮代表的是你在私下最真實的情感反應模式，"
                    "以及你從小建立起的安全感藍圖。"
                )
        if bazi and bazi.five_element_strength:
            water_str = bazi.five_element_strength.get("水", "均衡")
            fire_str  = bazi.five_element_strength.get("火", "均衡")
            emotional_parts.append(
                f"八字五行中，水（情感直覺）{water_str}，火（熱情表達）{fire_str}。"
                "水強者情感豐富細膩，但容易多愁善感；水弱者情感偏理性，需要刻意練習情感表達。"
            )
        emotional_pattern = "\n\n".join(emotional_parts) or "情緒模式分析需要更完整的出生資料。"

        # ── Action Pattern ───────────────────────────────────────────────────
        action_parts: List[str] = []
        if western:
            mars_positions = [pp for pp in western.planet_positions if pp.planet.value == "火星"]
            if mars_positions:
                msign = mars_positions[0].sign.value
                mkw = _SIGN_KEYWORDS.get(msign, ("", "", ""))
                action_parts.append(
                    f"火星位於{msign}，決定了你的行動驅動力與執行風格：{mkw[0]}。"
                    "當你面對挑戰時，火星所在星座決定了你傾向以什麼方式回應。"
                )
        if bazi:
            metal_str = bazi.five_element_strength.get("金", "均衡")
            action_parts.append(
                f"金（決斷力）在你的五行中屬{metal_str}狀態，"
                "這影響了你在需要做出決定時的果斷程度與執行速度。"
            )
        action_pattern = "\n\n".join(action_parts) or "行動模式分析需要更完整的出生資料。"

        # ── Love Pattern ─────────────────────────────────────────────────────
        love_parts: List[str] = []
        if western:
            venus_positions = [pp for pp in western.planet_positions if pp.planet.value == "金星"]
            if venus_positions:
                vsign = venus_positions[0].sign.value
                vkw = _SIGN_KEYWORDS.get(vsign, ("", "", ""))
                love_parts.append(
                    f"金星位於{vsign}，是你愛與美的語言：{vkw[1]}。"
                    "金星代表你在感情中吸引他人的方式，以及你對愛的想像與期待。"
                    f"夫妻宮（第七宮）落在{western.descendant.value}，"
                    "揭示了你在長期關係中需要的特質以及容易吸引的對象類型。"
                )
        if bazi and bazi.wealth_star:
            love_parts.append(
                f"在八字中，正財/偏財（{bazi.wealth_star.value}）的狀態，"
                "在感情分析中（尤其對男命）代表緣分與伴侶特質。"
                "建議進一步確認財星在命盤中的強弱位置以深化分析。"
            )
        if ziwei:
            sp_stars = "、".join(ziwei.spouse_palace.main_stars) if ziwei.spouse_palace.main_stars else "無主星"
            love_parts.append(
                f"紫微夫妻宮入宮星曜：{sp_stars}。"
                "夫妻宮揭示婚姻或長期伴侶關係的核心模式與磁場。"
            )
        if blood:
            love_parts.append(f"血型輔助觀點：{blood.love_response}")
        love_pattern = "\n\n".join(love_parts) or "感情模式分析需要更完整的出生資料。"

        # ── Career Pattern ───────────────────────────────────────────────────
        career_parts: List[str] = []
        suitable_careers: List[str] = []

        if western and sun_sign:
            sun_kw = _SIGN_KEYWORDS.get(sun_sign, ("", "", ""))
            career_parts.append(f"太陽在{sun_sign}的你，事業能量方向：{sun_kw[2]}。")
            mc_kw = _SIGN_KEYWORDS.get(western.mc.value, ("", "", ""))
            career_parts.append(
                f"天頂（MC）落在{western.mc.value}，代表你在職業舞台上渴望展現的形象，"
                f"以及最能讓你獲得社會認可的工作方向：{mc_kw[2]}。"
            )

        if bazi and bazi.power_star:
            career_parts.append(
                f"八字官殺（{bazi.power_star.value}）揭示你與職場權威、規範、競爭的關係。"
                "官殺旺者通常事業心強，但也需要注意與上司或體制的摩擦。"
            )

        if ziwei:
            career_stars = ziwei.career_palace.main_stars
            for star in career_stars:
                desc = _ZIWEI_CAREER_STARS.get(star, "")
                if desc:
                    career_parts.append(f"紫微官祿宮——{desc}")

        if numerology:
            lp = numerology.life_path_number
            lp_careers = _LIFE_PATH_CAREER.get(lp, [])
            suitable_careers.extend(lp_careers)
            if lp_careers:
                career_parts.append(
                    f"生命靈數{lp}建議的職業方向：{'、'.join(lp_careers[:4])}等。"
                )

        # Add sun sign career suggestions
        if sun_sign:
            suitable_careers.append(_SIGN_KEYWORDS.get(sun_sign, ("", "", ""))[2])

        career_pattern = "\n\n".join(career_parts) or "事業模式分析需要更完整的出生資料。"

        # ── Wealth Pattern ───────────────────────────────────────────────────
        wealth_parts: List[str] = []
        if bazi:
            metal_pct = bazi.five_element_ratio.get("金", 0.0)
            water_pct = bazi.five_element_ratio.get("水", 0.0)
            wealth_parts.append(
                f"八字財帛分析：金（{metal_pct}%）、水（{water_pct}%）在五行中的佔比，"
                "反映了你天生的財富能量強弱。"
            )
            if bazi.wealth_star:
                wealth_parts.append(
                    f"財星（{bazi.wealth_star.value}）的狀態，"
                    "決定了你獲取財富的主要模式是主動攬財還是等待時機。"
                )
        if ziwei:
            wealth_stars = "、".join(ziwei.wealth_palace.main_stars) if ziwei.wealth_palace.main_stars else "無主星"
            wealth_parts.append(
                f"紫微財帛宮入宮星曜：{wealth_stars}。"
                "財帛宮揭示你賺錢的方式、財富觀念，以及金錢流動的模式。"
            )
        if blood:
            wealth_parts.append(f"血型財富觀輔助：{blood.money_attitude}")
        wealth_pattern = "\n\n".join(wealth_parts) or "財富模式分析需要更完整的出生資料。"

        # ── Social Pattern ───────────────────────────────────────────────────
        social_parts: List[str] = []
        if western:
            for pp in western.planet_positions:
                if pp.planet.value == "水星":
                    mkw = _SIGN_KEYWORDS.get(pp.sign.value, ("", "", ""))
                    social_parts.append(
                        f"水星位於{pp.sign.value}，影響你的溝通方式、思維表達與人際交流風格：{mkw[0]}。"
                    )
                    break
        if blood:
            social_parts.append(f"血型人際輔助：{blood.interpersonal_style}")
        social_pattern = "\n\n".join(social_parts) or "人際模式分析需要更完整的出生資料。"

        # ── Family & Security ────────────────────────────────────────────────
        family_parts: List[str] = []
        if western:
            ic_kw = _SIGN_KEYWORDS.get(western.ic.value, ("", "", ""))
            family_parts.append(
                f"天底（IC）落在{western.ic.value}，代表你的心理根基、家庭背景與安全感模式：{ic_kw[0]}。"
                "IC是你最私密的內在需求，影響你如何建立屬於自己的家園與安全感。"
            )
        if ziwei:
            prop_stars = "、".join(ziwei.property_palace.main_stars) if ziwei.property_palace.main_stars else "無主星"
            family_parts.append(
                f"紫微田宅宮（{prop_stars}）代表家庭能量與不動產運勢。"
            )
        family_security = "\n\n".join(family_parts) or "家庭安全感分析需要更完整的出生資料。"

        # ── Stress & Shadow ──────────────────────────────────────────────────
        stress_parts: List[str] = []
        if western:
            saturn_positions = [pp for pp in western.planet_positions if pp.planet.value == "土星"]
            if saturn_positions:
                ssign = saturn_positions[0].sign.value
                skw = _SIGN_KEYWORDS.get(ssign, ("", "", ""))
                stress_parts.append(
                    f"土星位於{ssign}，標記了你人生中最需要學習的功課與阻力所在。"
                    f"土星的能量：{skw[0]}。土星的課題不是懲罰，而是通過在這個領域持續努力來獲得真正的精熟。"
                )
            chiron_positions = [pp for pp in western.planet_positions if pp.planet.value == "凱龍星"]
            if chiron_positions:
                csign = chiron_positions[0].sign.value
                stress_parts.append(
                    f"凱龍星位於{csign}，是你深層的「受傷之處」，同時也是你最強大的療癒能力的來源。"
                    "接觸並整合凱龍的傷，往往能開啟你獨特的人生使命。"
                )
        if blood:
            stress_parts.append(f"壓力反應（血型輔助）：{blood.stress_response}")
        stress_shadow = "\n\n".join(stress_parts) or "壓力與陰影分析需要更完整的出生資料。"

        # ── Life Lessons ─────────────────────────────────────────────────────
        lesson_parts: List[str] = []
        if western:
            north_positions = [pp for pp in western.planet_positions if pp.planet.value == "北交點"]
            if north_positions:
                nsign = north_positions[0].sign.value
                nkw = _SIGN_KEYWORDS.get(nsign, ("", "", ""))
                lesson_parts.append(
                    f"北交點位於{nsign}，是你靈魂此生的進化方向與功課。"
                    f"要向{nsign}的能量學習：{nkw[0]}，才能在這一生達到靈魂的真正成長。"
                    "南交點所在則代表你已熟悉的舒適區，需要有意識地離開它。"
                )
        if numerology:
            lesson_parts.append(
                f"生命靈數{numerology.life_path_number}的人生課題：{numerology.life_path_description}"
            )
        life_lessons = "\n\n".join(lesson_parts) or "人生課題分析需要更完整的出生資料。"

        # ── Innate Gifts ─────────────────────────────────────────────────────
        gifts_parts: List[str] = []
        if bazi:
            fav_desc = "、".join(e.value for e in bazi.favorable_elements)
            gifts_parts.append(
                f"喜用神（{fav_desc}）揭示了你天生就能輕鬆駕馭的能量頻率，"
                "這是你的內在資源，在順境中自然顯現。"
            )
        if numerology:
            gifts_parts.append(
                f"天賦數{numerology.talent_number}：{numerology.talent_description}"
            )
        innate_gifts = "\n\n".join(gifts_parts) or "天賦優勢分析需要更完整的出生資料。"

        # ── Recurring Challenges ─────────────────────────────────────────────
        recurring_parts: List[str] = []
        if bazi and bazi.unfavorable_elements:
            unfav_desc = "、".join(e.value for e in bazi.unfavorable_elements)
            recurring_parts.append(
                f"忌神（{unfav_desc}）代表你在人生中容易遭遇阻力的能量模式。"
                "忌神旺盛的流年往往是挑戰較多的時期，但也是成長最快速的時機。"
            )
        recurring_challenges = "\n\n".join(recurring_parts) or "反覆模式分析需要更完整的出生資料。"

        # ── Love Styles ──────────────────────────────────────────────────────
        suitable_love_styles: List[str] = []
        if western:
            desc = western.descendant.value
            suitable_love_styles.append(f"第七宮（{desc}）特質的伴侶")
        if blood:
            suitable_love_styles.append(f"能理解{profile.blood_type.value}型特質的伴侶")

        # ── Temporal Advice ──────────────────────────────────────────────────
        from datetime import date as _date
        current_year = _date.today().year

        year_advice_parts: List[str] = []
        three_year_parts: List[str] = []

        if bazi and bazi.liu_nian:
            nian = bazi.liu_nian[0]
            year_advice_parts.append(
                f"{nian.year}年（{nian.stem.value}{nian.branch.value}年）流年運勢："
                "請結合喜用神與忌神判斷此流年能量是否順應你的命格。"
                "若流年五行為喜用神，宜積極開展新計畫；若為忌神，則宜守成、避免重大決策。"
            )
            if len(bazi.liu_nian) >= 3:
                years = "、".join(str(n.year) for n in bazi.liu_nian[:3])
                year_stems = "、".join(n.stem.value + n.branch.value for n in bazi.liu_nian[:3])
                three_year_parts.append(
                    f"未來三年（{years}，{year_stems}）的流年趨勢，"
                    "需持續檢視每年流年五行與你的喜忌神是否相合。"
                )

        if numerology:
            year_advice_parts.append(
                f"今年個人年數為{numerology.personal_year}：{numerology.personal_year_description}"
            )

        one_year_advice  = "\n\n".join(year_advice_parts)  or "需要出生資料以計算流年建議。"
        three_year_advice = "\n\n".join(three_year_parts) or "需要出生資料以計算三年趨勢。"

        # ── Contradiction Detection ───────────────────────────────────────────
        if western and bazi:
            # Example: High fire in BaZi but water-dominant western chart
            fire_str = bazi.five_element_strength.get("火", "均衡")
            sun_water = sun_sign in ("天蠍座", "雙魚座", "巨蟹座") if sun_sign else False
            if fire_str == "強" and sun_water:
                contradictions.append(
                    "內在矛盾點：八字火旺（熱情外向），但西洋占星太陽星座屬水象（內省敏感），"
                    "這可能形成外熱內冷的雙重性格——表面積極主動，內心卻需要大量獨處充電。"
                )
                integration_suggestions.append(
                    "整合建議：接受自己的雙重性，為外向互動與獨處充電分別預留空間。不需要強迫自己只選一種模式。"
                )

        if numerology and bazi:
            lp = numerology.life_path_number
            dm_is_strong = bazi.five_element_ratio.get(bazi.day_master_element.value, 0) >= 25.0
            if lp in (1, 8) and not dm_is_strong:
                contradictions.append(
                    f"內在矛盾點：生命靈數{lp}具有強烈的成就與獨立傾向，"
                    "但八字日主偏弱，可能讓你在追求目標時感到能量不足或缺乏支撐。"
                )
                integration_suggestions.append(
                    "整合建議：優先培養喜用神能量（環境、食物、顏色、方位），為你的雄心抱負打造更穩固的底層能量。"
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
