"""Built-in country list with localized names."""

# Format: code -> {en, zh_tw, th, ja, es, ar}
COUNTRIES = {
    "TW": {"en": "Taiwan", "zh_tw": "台灣", "th": "ไต้หวัน", "ja": "台湾", "es": "Taiwán", "ar": "تايوان"},
    "JP": {"en": "Japan", "zh_tw": "日本", "th": "ญี่ปุ่น", "ja": "日本", "es": "Japón", "ar": "اليابان"},
    "TH": {"en": "Thailand", "zh_tw": "泰國", "th": "ไทย", "ja": "タイ", "es": "Tailandia", "ar": "تايلاند"},
    "US": {"en": "United States", "zh_tw": "美國", "th": "สหรัฐอเมริกา", "ja": "アメリカ", "es": "Estados Unidos", "ar": "الولايات المتحدة"},
    "CA": {"en": "Canada", "zh_tw": "加拿大", "th": "แคนาดา", "ja": "カナダ", "es": "Canadá", "ar": "كندا"},
    "GB": {"en": "United Kingdom", "zh_tw": "英國", "th": "สหราชอาณาจักร", "ja": "イギリス", "es": "Reino Unido", "ar": "المملكة المتحدة"},
    "AU": {"en": "Australia", "zh_tw": "澳洲", "th": "ออสเตรเลีย", "ja": "オーストラリア", "es": "Australia", "ar": "أستراليا"},
    "NZ": {"en": "New Zealand", "zh_tw": "紐西蘭", "th": "นิวซีแลนด์", "ja": "ニュージーランド", "es": "Nueva Zelanda", "ar": "نيوزيلندا"},
    "CN": {"en": "China", "zh_tw": "中國", "th": "จีน", "ja": "中国", "es": "China", "ar": "الصين"},
    "HK": {"en": "Hong Kong", "zh_tw": "香港", "th": "ฮ่องกง", "ja": "香港", "es": "Hong Kong", "ar": "هونغ كونغ"},
    "MO": {"en": "Macao", "zh_tw": "澳門", "th": "มาเก๊า", "ja": "マカオ", "es": "Macao", "ar": "ماكاو"},
    "SG": {"en": "Singapore", "zh_tw": "新加坡", "th": "สิงคโปร์", "ja": "シンガポール", "es": "Singapur", "ar": "سنغافورة"},
    "MY": {"en": "Malaysia", "zh_tw": "馬來西亞", "th": "มาเลเซีย", "ja": "マレーシア", "es": "Malasia", "ar": "ماليزيا"},
    "PH": {"en": "Philippines", "zh_tw": "菲律賓", "th": "ฟิลิปปินส์", "ja": "フィリピン", "es": "Filipinas", "ar": "الفلبين"},
    "VN": {"en": "Vietnam", "zh_tw": "越南", "th": "เวียดนาม", "ja": "ベトナム", "es": "Vietnam", "ar": "فيتنام"},
    "KR": {"en": "South Korea", "zh_tw": "韓國", "th": "เกาหลีใต้", "ja": "韓国", "es": "Corea del Sur", "ar": "كوريا الجنوبية"},
    "ID": {"en": "Indonesia", "zh_tw": "印尼", "th": "อินโดนีเซีย", "ja": "インドネシア", "es": "Indonesia", "ar": "إندونيسيا"},
    "IN": {"en": "India", "zh_tw": "印度", "th": "อินเดีย", "ja": "インド", "es": "India", "ar": "الهند"},
    "FR": {"en": "France", "zh_tw": "法國", "th": "ฝรั่งเศส", "ja": "フランス", "es": "Francia", "ar": "فرنسا"},
    "DE": {"en": "Germany", "zh_tw": "德國", "th": "เยอรมนี", "ja": "ドイツ", "es": "Alemania", "ar": "ألمانيا"},
    "ES": {"en": "Spain", "zh_tw": "西班牙", "th": "สเปน", "ja": "スペイン", "es": "España", "ar": "إسبانيا"},
    "IT": {"en": "Italy", "zh_tw": "義大利", "th": "อิตาลี", "ja": "イタリア", "es": "Italia", "ar": "إيطاليا"},
    "BR": {"en": "Brazil", "zh_tw": "巴西", "th": "บราซิล", "ja": "ブラジル", "es": "Brasil", "ar": "البرازيل"},
    "MX": {"en": "Mexico", "zh_tw": "墨西哥", "th": "เม็กซิโก", "ja": "メキシコ", "es": "México", "ar": "المكسيك"},
    "AE": {"en": "UAE", "zh_tw": "阿聯酋", "th": "สหรัฐอาหรับเอมิเรตส์", "ja": "アラブ首長国連邦", "es": "Emiratos Árabes Unidos", "ar": "الإمارات العربية المتحدة"},
    "SA": {"en": "Saudi Arabia", "zh_tw": "沙烏地阿拉伯", "th": "ซาอุดีอาระเบีย", "ja": "サウジアラビア", "es": "Arabia Saudita", "ar": "المملكة العربية السعودية"},
    "EG": {"en": "Egypt", "zh_tw": "埃及", "th": "อียิปต์", "ja": "エジプト", "es": "Egipto", "ar": "مصر"},
    "OTHER": {"en": "Other", "zh_tw": "其他", "th": "อื่นๆ", "ja": "その他", "es": "Otro", "ar": "أخرى"},
}

_LANG_MAP = {
    "zh-TW": "zh_tw", "en": "en", "th": "th", "ja": "ja", "es": "es", "ar": "ar"
}

def get_country_display_name(country_code: str, language: str = "zh-TW") -> str:
    lang_key = _LANG_MAP.get(language, "en")
    entry = COUNTRIES.get(country_code.upper(), {})
    return entry.get(lang_key) or entry.get("en") or country_code

def get_country_options(language: str = "zh-TW") -> list:
    """Returns list of (code, display_name) sorted by display name, OTHER last."""
    lang_key = _LANG_MAP.get(language, "en")
    result = []
    for code, names in COUNTRIES.items():
        if code == "OTHER":
            continue
        display = names.get(lang_key) or names.get("en") or code
        result.append((code, display))
    result.sort(key=lambda x: x[1])
    other_display = COUNTRIES["OTHER"].get(lang_key) or "Other"
    result.append(("OTHER", other_display))
    return result
