"""
Display name translations for canonical enum values.
Never mutate the stored canonical values — only translate at display layer.
"""
from .translator import get_translation

# Canonical → translation key mapping
_GENDER_KEYS = {
    "male": "display.gender.male",
    "female": "display.gender.female",
    "other": "display.gender.other",
    "unknown": "display.gender.unknown",
}

_HD_TYPE_KEYS = {
    "Manifestor": "display.hd_type.manifestor",
    "Generator": "display.hd_type.generator",
    "Manifesting Generator": "display.hd_type.manifesting_generator",
    "Projector": "display.hd_type.projector",
    "Reflector": "display.hd_type.reflector",
}

_AUTHORITY_KEYS = {
    "Emotional": "display.authority.emotional",
    "Sacral": "display.authority.sacral",
    "Splenic": "display.authority.splenic",
    "Ego": "display.authority.ego",
    "Self-Projected": "display.authority.self_projected",
    "Mental / Environmental": "display.authority.mental_environmental",
    "Lunar": "display.authority.lunar",
}

_CENTER_KEYS = {
    "Head": "display.center.head",
    "Ajna": "display.center.ajna",
    "Throat": "display.center.throat",
    "G": "display.center.g",
    "Heart": "display.center.heart",
    "Sacral": "display.center.sacral",
    "Solar Plexus": "display.center.solar_plexus",
    "Spleen": "display.center.spleen",
    "Root": "display.center.root",
}

_ZODIAC_KEYS = {
    "Aries": "display.zodiac.aries",
    "Taurus": "display.zodiac.taurus",
    "Gemini": "display.zodiac.gemini",
    "Cancer": "display.zodiac.cancer",
    "Leo": "display.zodiac.leo",
    "Virgo": "display.zodiac.virgo",
    "Libra": "display.zodiac.libra",
    "Scorpio": "display.zodiac.scorpio",
    "Sagittarius": "display.zodiac.sagittarius",
    "Capricorn": "display.zodiac.capricorn",
    "Aquarius": "display.zodiac.aquarius",
    "Pisces": "display.zodiac.pisces",
}


def _translate(key_map: dict, value: str, language: str) -> str:
    key = key_map.get(value)
    if key is None:
        return value
    result = get_translation(language, key)
    return result if result != key else value


def translate_gender(value: str, language: str) -> str:
    return _translate(_GENDER_KEYS, value, language)


_HD_TYPE_ALIASES = {
    "顯示者": "Manifestor", "显示者": "Manifestor",
    "生產者": "Generator", "生产者": "Generator",
    "顯示生產者": "Manifesting Generator", "显示生产者": "Manifesting Generator",
    "投射者": "Projector", "反映者": "Reflector",
}

def translate_hd_type(value: str, language: str) -> str:
    canonical = _HD_TYPE_ALIASES.get(str(value), str(value))
    return _translate(_HD_TYPE_KEYS, canonical, language)


def translate_authority(value: str, language: str) -> str:
    return _translate(_AUTHORITY_KEYS, value, language)


def translate_center(value: str, language: str) -> str:
    return _translate(_CENTER_KEYS, value, language)


def translate_zodiac(value: str, language: str) -> str:
    return _translate(_ZODIAC_KEYS, value, language)


_ZODIAC_ALIASES = {
    "牡羊座": "Aries", "白羊座": "Aries", "Aries": "Aries",
    "金牛座": "Taurus", "Taurus": "Taurus",
    "雙子座": "Gemini", "双子座": "Gemini", "Gemini": "Gemini",
    "巨蟹座": "Cancer", "Cancer": "Cancer",
    "獅子座": "Leo", "狮子座": "Leo", "Leo": "Leo",
    "處女座": "Virgo", "处女座": "Virgo", "Virgo": "Virgo",
    "天秤座": "Libra", "Libra": "Libra",
    "天蠍座": "Scorpio", "天蝎座": "Scorpio", "Scorpio": "Scorpio",
    "射手座": "Sagittarius", "Sagittarius": "Sagittarius",
    "摩羯座": "Capricorn", "山羊座": "Capricorn", "Capricorn": "Capricorn",
    "水瓶座": "Aquarius", "Aquarius": "Aquarius",
    "雙魚座": "Pisces", "双鱼座": "Pisces", "Pisces": "Pisces",
}

def normalize_zodiac_value(value: str) -> str:
    """Normalize legacy localized zodiac labels to canonical English values."""
    return _ZODIAC_ALIASES.get(str(value).strip(), str(value).strip())

_ANALYSIS_THEME_KEYS = {
    "overall_personality": "analysis_theme.overall_personality",
    "relationships": "analysis_theme.relationships",
    "career": "analysis_theme.career",
    "wealth": "analysis_theme.wealth",
    "social": "analysis_theme.social",
    "family": "analysis_theme.family",
    "current_year": "analysis_theme.current_year",
    "next_three_years": "analysis_theme.next_three_years",
}

_LEGACY_THEME_TO_ID = {
    "總體人格": "overall_personality",
    "感情": "relationships",
    "事業": "career",
    "財富": "wealth",
    "人際": "social",
    "家庭": "family",
    "今年運勢": "current_year",
    "未來三年": "next_three_years",
}

_REPORT_LENGTH_KEYS = {
    "short": "report_length.short",
    "standard": "report_length.standard",
    "full": "report_length.full",
    "complete_10k": "report_length.ten_thousand",
}

_LEGACY_REPORT_LENGTH_TO_ID = {
    "簡短版": "short",
    "精簡版": "short",
    "Short": "short",
    "標準版": "standard",
    "Standard": "standard",
    "完整版": "full",
    "Full": "full",
    "萬字完整版": "complete_10k",
    "Complete 10K": "complete_10k",
}


def normalize_analysis_theme(value: str) -> str:
    value = str(value)
    return _LEGACY_THEME_TO_ID.get(value, value)


def translate_analysis_theme(value: str, language: str) -> str:
    canonical = normalize_analysis_theme(value)
    key = _ANALYSIS_THEME_KEYS.get(canonical)
    if key is None:
        return value
    translated = get_translation(language, key)
    return translated if translated != key else value


def normalize_report_length(value: str) -> str:
    value = str(value)
    return _LEGACY_REPORT_LENGTH_TO_ID.get(value, value)


def translate_report_length(value: str, language: str) -> str:
    canonical = normalize_report_length(value)
    key = _REPORT_LENGTH_KEYS.get(canonical, "report_length.unknown")
    translated = get_translation(language, key)
    return translated if translated != key else value

# Additional display-only mappings used by the V2.0.6 multilingual runtime.
_BAZI_STEMS = {
    "甲": {"en":"Jia (Yang Wood)","ja":"甲（陽の木）","th":"甲 (ไม้หยาง)","es":"Jia (Madera Yang)","ar":"Jia (خشب يانغ)"},
    "乙": {"en":"Yi (Yin Wood)","ja":"乙（陰の木）","th":"乙 (ไม้หยิน)","es":"Yi (Madera Yin)","ar":"Yi (خشب يِن)"},
    "丙": {"en":"Bing (Yang Fire)","ja":"丙（陽の火）","th":"丙 (ไฟหยาง)","es":"Bing (Fuego Yang)","ar":"Bing (نار يانغ)"},
    "丁": {"en":"Ding (Yin Fire)","ja":"丁（陰の火）","th":"丁 (ไฟหยิน)","es":"Ding (Fuego Yin)","ar":"Ding (نار يِن)"},
    "戊": {"en":"Wu (Yang Earth)","ja":"戊（陽の土）","th":"戊 (ดินหยาง)","es":"Wu (Tierra Yang)","ar":"Wu (أرض يانغ)"},
    "己": {"en":"Ji (Yin Earth)","ja":"己（陰の土）","th":"己 (ดินหยิน)","es":"Ji (Tierra Yin)","ar":"Ji (أرض يِن)"},
    "庚": {"en":"Geng (Yang Metal)","ja":"庚（陽の金）","th":"庚 (โลหะหยาง)","es":"Geng (Metal Yang)","ar":"Geng (معدن يانغ)"},
    "辛": {"en":"Xin (Yin Metal)","ja":"辛（陰の金）","th":"辛 (โลหะหยิน)","es":"Xin (Metal Yin)","ar":"Xin (معدن يِن)"},
    "壬": {"en":"Ren (Yang Water)","ja":"壬（陽の水）","th":"壬 (น้ำหยาง)","es":"Ren (Agua Yang)","ar":"Ren (ماء يانغ)"},
    "癸": {"en":"Gui (Yin Water)","ja":"癸（陰の水）","th":"癸 (น้ำหยิน)","es":"Gui (Agua Yin)","ar":"Gui (ماء يِن)"},
}
_ELEMENT_NAMES = {
    "木": {"en":"Wood","ja":"木","th":"ไม้","es":"Madera","ar":"الخشب"},
    "火": {"en":"Fire","ja":"火","th":"ไฟ","es":"Fuego","ar":"النار"},
    "土": {"en":"Earth","ja":"土","th":"ดิน","es":"Tierra","ar":"الأرض"},
    "金": {"en":"Metal","ja":"金","th":"โลหะ","es":"Metal","ar":"المعدن"},
    "水": {"en":"Water","ja":"水","th":"น้ำ","es":"Agua","ar":"الماء"},
}
_HD_STRATEGY_ALIASES = {
    "等待回應": "respond", "等待邀請": "wait_invitation", "告知後行動": "inform",
    "等待月亮週期": "lunar_cycle", "回應": "respond", "邀請": "wait_invitation",
}
_HD_STRATEGY_LABELS = {
    "respond": {"en":"Wait to Respond","ja":"反応を待つ","th":"รอการตอบสนอง","es":"Esperar para responder","ar":"انتظار الاستجابة"},
    "wait_invitation": {"en":"Wait for the Invitation","ja":"招待を待つ","th":"รอคำเชิญ","es":"Esperar la invitación","ar":"انتظار الدعوة"},
    "inform": {"en":"Inform Before Acting","ja":"行動前に知らせる","th":"แจ้งก่อนลงมือ","es":"Informar antes de actuar","ar":"الإبلاغ قبل التصرف"},
    "lunar_cycle": {"en":"Wait Through a Lunar Cycle","ja":"月の周期を待つ","th":"รอหนึ่งรอบดวงจันทร์","es":"Esperar un ciclo lunar","ar":"انتظار دورة قمرية"},
}
_HD_AUTHORITY_ALIASES = {
    "情緒權威": "Emotional", "薦骨權威": "Sacral", "直覺權威": "Splenic",
    "意志權威": "Ego", "自我投射權威": "Self-Projected", "環境權威": "Mental / Environmental",
    "月亮權威": "Lunar",
}


def translate_bazi_stem(value: str, language: str) -> str:
    if language == "zh-TW":
        return value
    return _BAZI_STEMS.get(str(value), {}).get(language, str(value))


def translate_element(value: str, language: str) -> str:
    if language == "zh-TW":
        return value
    return _ELEMENT_NAMES.get(str(value), {}).get(language, str(value))


def translate_hd_strategy(value: str, language: str) -> str:
    if language == "zh-TW":
        return value
    canonical = _HD_STRATEGY_ALIASES.get(str(value), str(value))
    return _HD_STRATEGY_LABELS.get(canonical, {}).get(language, str(value))


def translate_hd_authority(value: str, language: str) -> str:
    canonical = _HD_AUTHORITY_ALIASES.get(str(value).split(" (")[0].split(" —")[0], str(value))
    return translate_authority(canonical, language)

# V2.0.6.1: comprehensive display-only localization for calculated tables.
_PLANET_ALIASES = {
    # Core planets / chart angles
    "太陽": "Sun", "Sun": "Sun",
    "月亮": "Moon", "Moon": "Moon",
    "水星": "Mercury", "Mercury": "Mercury",
    "金星": "Venus", "Venus": "Venus",
    "火星": "Mars", "Mars": "Mars",
    "木星": "Jupiter", "Jupiter": "Jupiter",
    "土星": "Saturn", "Saturn": "Saturn",
    "天王星": "Uranus", "Uranus": "Uranus",
    "海王星": "Neptune", "Neptune": "Neptune",
    "冥王星": "Pluto", "Pluto": "Pluto",
    "上升": "Ascendant", "上升點": "Ascendant", "Ascendant": "Ascendant", "ASC": "Ascendant",
    "天頂": "MC", "中天": "MC", "MC": "MC", "Midheaven": "MC",

    # Calculated points used by the Western Astrology engine.
    "北交點": "North Node", "北交点": "North Node", "North Node": "North Node",
    "True North Node": "North Node", "Mean North Node": "North Node",
    "南交點": "South Node", "南交点": "South Node", "South Node": "South Node",
    "True South Node": "South Node", "Mean South Node": "South Node",
    "凱龍星": "Chiron", "凯龙星": "Chiron", "Chiron": "Chiron",
    "莉莉絲": "Lilith", "莉莉丝": "Lilith", "Lilith": "Lilith", "Black Moon Lilith": "Lilith",
    "福點": "Part of Fortune", "福点": "Part of Fortune", "幸運點": "Part of Fortune",
    "幸运点": "Part of Fortune", "Part of Fortune": "Part of Fortune", "Fortuna": "Part of Fortune",
}
_PLANET_LABELS = {
    "Sun": {"zh-TW":"太陽","en":"Sun","ja":"太陽","th":"ดวงอาทิตย์","es":"Sol","ar":"الشمس"},
    "Moon": {"zh-TW":"月亮","en":"Moon","ja":"月","th":"ดวงจันทร์","es":"Luna","ar":"القمر"},
    "Mercury": {"zh-TW":"水星","en":"Mercury","ja":"水星","th":"ดาวพุธ","es":"Mercurio","ar":"عطارد"},
    "Venus": {"zh-TW":"金星","en":"Venus","ja":"金星","th":"ดาวศุกร์","es":"Venus","ar":"الزهرة"},
    "Mars": {"zh-TW":"火星","en":"Mars","ja":"火星","th":"ดาวอังคาร","es":"Marte","ar":"المريخ"},
    "Jupiter": {"zh-TW":"木星","en":"Jupiter","ja":"木星","th":"ดาวพฤหัสบดี","es":"Júpiter","ar":"المشتري"},
    "Saturn": {"zh-TW":"土星","en":"Saturn","ja":"土星","th":"ดาวเสาร์","es":"Saturno","ar":"زحل"},
    "Uranus": {"zh-TW":"天王星","en":"Uranus","ja":"天王星","th":"ดาวยูเรนัส","es":"Urano","ar":"أورانوس"},
    "Neptune": {"zh-TW":"海王星","en":"Neptune","ja":"海王星","th":"ดาวเนปจูน","es":"Neptuno","ar":"نبتون"},
    "Pluto": {"zh-TW":"冥王星","en":"Pluto","ja":"冥王星","th":"ดาวพลูโต","es":"Plutón","ar":"بلوتو"},
    "Ascendant": {"zh-TW":"上升","en":"Ascendant","ja":"アセンダント","th":"ลัคนา","es":"Ascendente","ar":"الطالع"},
    "MC": {"zh-TW":"天頂","en":"MC","ja":"MC","th":"MC","es":"MC","ar":"MC"},
    "North Node": {
        "zh-TW":"北交點", "en":"North Node", "ja":"ドラゴンヘッド",
        "th":"โหนดเหนือ", "es":"Nodo Norte", "ar":"العقدة الشمالية",
    },
    "South Node": {
        "zh-TW":"南交點", "en":"South Node", "ja":"ドラゴンテイル",
        "th":"โหนดใต้", "es":"Nodo Sur", "ar":"العقدة الجنوبية",
    },
    "Chiron": {
        "zh-TW":"凱龍星", "en":"Chiron", "ja":"キロン",
        "th":"ไครอน", "es":"Quirón", "ar":"كيرون",
    },
    "Lilith": {
        "zh-TW":"莉莉絲", "en":"Lilith", "ja":"リリス",
        "th":"ลิลิธ", "es":"Lilith", "ar":"ليليث",
    },
    "Part of Fortune": {
        "zh-TW":"福點", "en":"Part of Fortune", "ja":"パート・オブ・フォーチュン",
        "th":"จุดโชคลาภ", "es":"Parte de la Fortuna", "ar":"سهم السعادة",
    },
}
_ASPECT_ALIASES = {
    "合相 0°": "Conjunction", "合相": "Conjunction", "Conjunction": "Conjunction",
    "對分 180°": "Opposition", "對分": "Opposition", "Opposition": "Opposition",
    "三分 120°": "Trine", "三分": "Trine", "Trine": "Trine",
    "四分 90°": "Square", "四分": "Square", "Square": "Square",
    "六合 60°": "Sextile", "六合": "Sextile", "Sextile": "Sextile",
    "梅花相 150°": "Quincunx", "梅花相": "Quincunx", "Quincunx": "Quincunx",
}
_ASPECT_LABELS = {
    "Conjunction": {"zh-TW":"合相 0°","en":"Conjunction 0°","ja":"コンジャンクション 0°","th":"กุม 0°","es":"Conjunción 0°","ar":"اقتران 0°"},
    "Opposition": {"zh-TW":"對分 180°","en":"Opposition 180°","ja":"オポジション 180°","th":"เล็ง 180°","es":"Oposición 180°","ar":"مقابلة 180°"},
    "Trine": {"zh-TW":"三分 120°","en":"Trine 120°","ja":"トライン 120°","th":"ตรีโกณ 120°","es":"Trígono 120°","ar":"تثليث 120°"},
    "Square": {"zh-TW":"四分 90°","en":"Square 90°","ja":"スクエア 90°","th":"ฉาก 90°","es":"Cuadratura 90°","ar":"تربيع 90°"},
    "Sextile": {"zh-TW":"六合 60°","en":"Sextile 60°","ja":"セクスタイル 60°","th":"เซ็กส์ไทล์ 60°","es":"Sextil 60°","ar":"تسديس 60°"},
    "Quincunx": {"zh-TW":"梅花相 150°","en":"Quincunx 150°","ja":"クインカンクス 150°","th":"ควินคังซ์ 150°","es":"Quincuncio 150°","ar":"كوينكونكس 150°"},
}
_BRANCH_LABELS = {
    "子": {"zh-TW":"子","en":"Zi (Rat)","ja":"子","th":"จื่อ (ชวด)","es":"Zi (Rata)","ar":"Zi (الجرذ)"},
    "丑": {"zh-TW":"丑","en":"Chou (Ox)","ja":"丑","th":"โฉ่ว (ฉลู)","es":"Chou (Buey)","ar":"Chou (الثور)"},
    "寅": {"zh-TW":"寅","en":"Yin (Tiger)","ja":"寅","th":"อิ๋น (ขาล)","es":"Yin (Tigre)","ar":"Yin (النمر)"},
    "卯": {"zh-TW":"卯","en":"Mao (Rabbit)","ja":"卯","th":"เหม่า (เถาะ)","es":"Mao (Conejo)","ar":"Mao (الأرنب)"},
    "辰": {"zh-TW":"辰","en":"Chen (Dragon)","ja":"辰","th":"เฉิน (มะโรง)","es":"Chen (Dragón)","ar":"Chen (التنين)"},
    "巳": {"zh-TW":"巳","en":"Si (Snake)","ja":"巳","th":"ซื่อ (มะเส็ง)","es":"Si (Serpiente)","ar":"Si (الأفعى)"},
    "午": {"zh-TW":"午","en":"Wu (Horse)","ja":"午","th":"อู่ (มะเมีย)","es":"Wu (Caballo)","ar":"Wu (الحصان)"},
    "未": {"zh-TW":"未","en":"Wei (Goat)","ja":"未","th":"เว่ย (มะแม)","es":"Wei (Cabra)","ar":"Wei (الماعز)"},
    "申": {"zh-TW":"申","en":"Shen (Monkey)","ja":"申","th":"เซิน (วอก)","es":"Shen (Mono)","ar":"Shen (القرد)"},
    "酉": {"zh-TW":"酉","en":"You (Rooster)","ja":"酉","th":"โหย่ว (ระกา)","es":"You (Gallo)","ar":"You (الديك)"},
    "戌": {"zh-TW":"戌","en":"Xu (Dog)","ja":"戌","th":"ซวี (จอ)","es":"Xu (Perro)","ar":"Xu (الكلب)"},
    "亥": {"zh-TW":"亥","en":"Hai (Pig)","ja":"亥","th":"ไห่ (กุน)","es":"Hai (Cerdo)","ar":"Hai (الخنزير)"},
}
_PILLAR_LABELS = {
    "年柱":{"zh-TW":"年柱","en":"Year Pillar","ja":"年柱","th":"เสาปี","es":"Pilar del año","ar":"عمود السنة"},
    "月柱":{"zh-TW":"月柱","en":"Month Pillar","ja":"月柱","th":"เสาเดือน","es":"Pilar del mes","ar":"عمود الشهر"},
    "日柱":{"zh-TW":"日柱","en":"Day Pillar","ja":"日柱","th":"เสาวัน","es":"Pilar del día","ar":"عمود اليوم"},
    "時柱":{"zh-TW":"時柱","en":"Hour Pillar","ja":"時柱","th":"เสาชั่วโมง","es":"Pilar de la hora","ar":"عمود الساعة"},
}
_STRENGTH_LABELS = {
    "旺":{"zh-TW":"旺","en":"Strong","ja":"強い","th":"แข็งแรง","es":"Fuerte","ar":"قوي"},
    "弱":{"zh-TW":"弱","en":"Weak","ja":"弱い","th":"อ่อน","es":"Débil","ar":"ضعيف"},
    "平":{"zh-TW":"平","en":"Balanced","ja":"均衡","th":"สมดุล","es":"Equilibrado","ar":"متوازن"},
}


def translate_planet(value: str, language: str) -> str:
    canonical = _PLANET_ALIASES.get(str(value), str(value))
    return _PLANET_LABELS.get(canonical, {}).get(language, canonical)


def translate_aspect(value: str, language: str) -> str:
    raw = str(value)
    canonical = _ASPECT_ALIASES.get(raw, _ASPECT_ALIASES.get(raw.split(" ")[0], raw))
    return _ASPECT_LABELS.get(canonical, {}).get(language, raw)


def translate_branch(value: str, language: str) -> str:
    return _BRANCH_LABELS.get(str(value), {}).get(language, str(value))


def translate_pillar_label(value: str, language: str) -> str:
    return _PILLAR_LABELS.get(str(value), {}).get(language, str(value))


def translate_strength(value: str, language: str) -> str:
    return _STRENGTH_LABELS.get(str(value), {}).get(language, str(value))
