"""
Language-aware report rendering helpers.

This module keeps calculation models canonical and localizes only the rendered
report. Traditional Chinese continues to use the existing full narrative.
Other languages receive a structured, factual report generated from canonical
chart values, avoiding mixed-language output.
"""
from __future__ import annotations

from html import escape
from typing import Any, Dict, List

from i18n.display_names import (
    normalize_zodiac_value,
    translate_zodiac,
    translate_bazi_stem,
    translate_element,
    translate_hd_type,
    translate_hd_strategy,
    translate_hd_authority,
)

SUPPORTED_REPORT_LANGUAGES = ("zh-TW", "en", "th", "ja", "es", "ar")

_LANG_META = {
    "zh-TW": {"html_lang": "zh-TW", "dir": "ltr"},
    "en": {"html_lang": "en", "dir": "ltr"},
    "th": {"html_lang": "th", "dir": "ltr"},
    "ja": {"html_lang": "ja", "dir": "ltr"},
    "es": {"html_lang": "es", "dir": "ltr"},
    "ar": {"html_lang": "ar", "dir": "rtl"},
}

_TEXT = {
    "zh-TW": {
        "title": "命盤整合分析報告", "basic": "基本資料", "name": "姓名",
        "birth_date": "出生日期", "birth_time": "出生時間", "location": "出生地",
        "version": "系統版本", "created": "產生時間", "overview": "命盤重點總覽",
        "western": "西洋占星", "bazi": "八字", "ziwei": "紫微斗數",
        "numerology": "生命靈數", "human_design": "人類圖",
        "core": "核心人格", "emotion": "情緒與行動", "relationship": "感情與關係",
        "career": "事業", "wealth": "財富", "social": "人際", "family": "家庭",
        "shadow": "陰影課題", "talent": "天賦", "advice": "建議",
        "accuracy": "準確度與限制", "disclaimer": "免責聲明",
        "sun": "太陽星座", "moon": "月亮星座", "asc": "上升星座",
        "day_master": "日主", "fav_elements": "有利五行", "life_path": "生命靈數",
        "hd_type": "類型", "hd_strategy": "策略", "hd_authority": "內在權威",
        "fallback": "部分低優先長篇解讀仍沿用繁體中文來源。",
    },
    "en": {
        "title": "Integrated Destiny & Personality Report", "basic": "Basic Information",
        "name": "Name", "birth_date": "Birth Date", "birth_time": "Birth Time",
        "location": "Birth Place", "version": "Version", "created": "Created",
        "overview": "Chart Overview", "western": "Western Astrology", "bazi": "BaZi",
        "ziwei": "Zi Wei Dou Shu", "numerology": "Numerology", "human_design": "Human Design",
        "core": "Core Personality", "emotion": "Emotions & Action",
        "relationship": "Relationships", "career": "Career", "wealth": "Wealth",
        "social": "Social Life", "family": "Family", "shadow": "Shadow Themes",
        "talent": "Talents", "advice": "Advice", "accuracy": "Accuracy & Limitations",
        "disclaimer": "Disclaimer", "sun": "Sun Sign", "moon": "Moon Sign",
        "asc": "Ascendant", "day_master": "Day Master", "fav_elements": "Favorable Elements",
        "life_path": "Life Path", "hd_type": "Type", "hd_strategy": "Strategy",
        "hd_authority": "Authority",
        "fallback": "Some lower-priority long-form interpretations still use the Traditional Chinese source.",
    },
    "ja": {
        "title": "統合命盤・パーソナリティ分析レポート", "basic": "基本情報",
        "name": "名前", "birth_date": "生年月日", "birth_time": "出生時刻",
        "location": "出生地", "version": "バージョン", "created": "作成日時",
        "overview": "命盤概要", "western": "西洋占星術", "bazi": "八字",
        "ziwei": "紫微斗数", "numerology": "数秘術", "human_design": "ヒューマンデザイン",
        "core": "核心人格", "emotion": "感情と行動", "relationship": "恋愛・関係性",
        "career": "仕事・キャリア", "wealth": "金運・財運", "social": "対人関係",
        "family": "家庭", "shadow": "影のテーマ", "talent": "才能", "advice": "アドバイス",
        "accuracy": "精度と制限", "disclaimer": "免責事項", "sun": "太陽星座",
        "moon": "月星座", "asc": "アセンダント", "day_master": "日主",
        "fav_elements": "有利な五行", "life_path": "ライフパス", "hd_type": "タイプ",
        "hd_strategy": "ストラテジー", "hd_authority": "オーソリティ",
        "fallback": "一部の低優先度の長文解説は繁体字中国語の原文を使用しています。",
    },
    "th": {
        "title": "รายงานวิเคราะห์ดวงชะตาและบุคลิกภาพแบบบูรณาการ", "basic": "ข้อมูลพื้นฐาน",
        "name": "ชื่อ", "birth_date": "วันเกิด", "birth_time": "เวลาเกิด",
        "location": "สถานที่เกิด", "version": "เวอร์ชัน", "created": "สร้างเมื่อ",
        "overview": "ภาพรวมดวงชะตา", "western": "โหราศาสตร์ตะวันตก", "bazi": "BaZi",
        "ziwei": "Zi Wei Dou Shu", "numerology": "เลขศาสตร์", "human_design": "Human Design",
        "core": "บุคลิกภาพหลัก", "emotion": "อารมณ์และการลงมือทำ",
        "relationship": "ความสัมพันธ์", "career": "การงาน", "wealth": "การเงิน",
        "social": "สังคม", "family": "ครอบครัว", "shadow": "เงาและความท้าทาย",
        "talent": "พรสวรรค์", "advice": "คำแนะนำ", "accuracy": "ความแม่นยำและข้อจำกัด",
        "disclaimer": "ข้อจำกัดความรับผิดชอบ", "sun": "ราศีอาทิตย์",
        "moon": "ราศีจันทร์", "asc": "ลัคนา", "day_master": "Day Master",
        "fav_elements": "ธาตุที่ส่งเสริม", "life_path": "เลขเส้นทางชีวิต",
        "hd_type": "ประเภท", "hd_strategy": "กลยุทธ์", "hd_authority": "Authority",
        "fallback": "คำอธิบายเชิงลึกบางส่วนยังใช้ต้นฉบับภาษาจีนตัวเต็ม",
    },
    "es": {
        "title": "Informe integrado de destino y personalidad", "basic": "Información básica",
        "name": "Nombre", "birth_date": "Fecha de nacimiento", "birth_time": "Hora de nacimiento",
        "location": "Lugar de nacimiento", "version": "Versión", "created": "Creado",
        "overview": "Resumen de la carta", "western": "Astrología occidental", "bazi": "BaZi",
        "ziwei": "Zi Wei Dou Shu", "numerology": "Numerología", "human_design": "Human Design",
        "core": "Personalidad central", "emotion": "Emociones y acción",
        "relationship": "Relaciones", "career": "Carrera", "wealth": "Finanzas",
        "social": "Vida social", "family": "Familia", "shadow": "Temas de sombra",
        "talent": "Talentos", "advice": "Consejos", "accuracy": "Precisión y limitaciones",
        "disclaimer": "Descargo de responsabilidad", "sun": "Signo solar",
        "moon": "Signo lunar", "asc": "Ascendente", "day_master": "Maestro del Día",
        "fav_elements": "Elementos favorables", "life_path": "Camino de Vida",
        "hd_type": "Tipo", "hd_strategy": "Estrategia", "hd_authority": "Autoridad",
        "fallback": "Algunas interpretaciones extensas de menor prioridad aún usan la fuente en chino tradicional.",
    },
    "ar": {
        "title": "تقرير متكامل للمصير والشخصية", "basic": "المعلومات الأساسية",
        "name": "الاسم", "birth_date": "تاريخ الميلاد", "birth_time": "وقت الميلاد",
        "location": "مكان الميلاد", "version": "الإصدار", "created": "تاريخ الإنشاء",
        "overview": "نظرة عامة على الخريطة", "western": "التنجيم الغربي", "bazi": "BaZi",
        "ziwei": "Zi Wei Dou Shu", "numerology": "علم الأعداد", "human_design": "Human Design",
        "core": "الشخصية الأساسية", "emotion": "العاطفة والفعل",
        "relationship": "العلاقات", "career": "المسار المهني", "wealth": "المال",
        "social": "الحياة الاجتماعية", "family": "الأسرة", "shadow": "موضوعات الظل",
        "talent": "المواهب", "advice": "النصيحة", "accuracy": "الدقة والقيود",
        "disclaimer": "إخلاء المسؤولية", "sun": "برج الشمس", "moon": "برج القمر",
        "asc": "الطالع", "day_master": "سيد اليوم", "fav_elements": "العناصر الداعمة",
        "life_path": "مسار الحياة", "hd_type": "النوع", "hd_strategy": "الاستراتيجية",
        "hd_authority": "السلطة الداخلية",
        "fallback": "لا تزال بعض التفسيرات المطولة الأقل أولوية تستخدم المصدر الصيني التقليدي.",
    },
}

_SECTION_TEMPLATES = {
    "en": [
        "Your chart combines Sun {sun}, Moon {moon}, Ascendant {asc}, BaZi Day Master {day_master}, Life Path {life_path}, and Human Design Type {hd_type}. Read these as complementary patterns rather than fixed judgments.",
        "Moon {moon} describes emotional needs, while Day Master {day_master} adds an elemental view of how you process energy. Notice which reactions repeat under pressure.",
        "Relationship patterns become clearer when emotional needs, communication, timing, and personal boundaries are considered together.",
        "Career direction is strongest where recurring chart strengths meet a sustainable environment. Favorable BaZi elements: {fav}.",
        "Financial patterns reflect decision style, risk tolerance, and resource habits. This is not financial advice.",
        "Social expression combines the visible Ascendant {asc} with deeper emotional and decision-making tendencies.",
        "Family themes often show where security, duty, belonging, and inherited expectations intersect.",
        "Shadow themes are usually overused strengths or protective habits. Awareness expands choice.",
        "Talents tend to appear where several systems point in the same direction. Life Path {life_path} and Type {hd_type} are useful lenses.",
        "Apply one insight at a time, record what changes, and keep important decisions grounded in real-world evidence.",
    ],
    "ja": [
        "太陽は{sun}、月は{moon}、アセンダントは{asc}です。八字の日主は{day_master}、ライフパスは{life_path}、Human Design Type は{hd_type}です。固定的な運命判断ではなく、複数の視点として活用してください。",
        "月（{moon}）は感情的ニーズを、日主（{day_master}）はエネルギー処理の傾向を示します。プレッシャー下で繰り返す反応を観察しましょう。",
        "関係性は感情ニーズ、対話、タイミング、境界線を組み合わせて見ると理解しやすくなります。",
        "仕事では、繰り返し示される強みと持続可能な環境の一致が重要です。有利な五行は{fav}です。",
        "財運は意思決定、リスク許容度、資源管理の傾向を考える参考です。投資助言ではありません。",
        "対人表現はアセンダント（{asc}）と内面的な感情・判断傾向の組み合わせで現れます。",
        "家庭テーマでは安心感、責任、所属感、受け継いだ期待が交差します。",
        "影のテーマは、強みの使い過ぎや防衛反応として現れることがあります。気づきは選択肢を増やします。",
        "才能は複数の体系が同じ方向を示すところに現れやすいです。ライフパス{life_path}とType {hd_type}を実生活で検証してください。",
        "一度に一つの示唆を試し、変化を記録し、重要な判断は現実の情報に基づいて行ってください。",
    ],
    "th": [
        "ดวงนี้รวมดวงอาทิตย์ {sun} ดวงจันทร์ {moon} ลัคนา {asc} Day Master {day_master} เลขเส้นทางชีวิต {life_path} และ Human Design Type {hd_type} ควรใช้เป็นมุมมองประกอบ ไม่ใช่คำตัดสินตายตัว",
        "ดวงจันทร์ ({moon}) สะท้อนความต้องการทางอารมณ์ ส่วน Day Master ({day_master}) แสดงรูปแบบการใช้พลังงาน ควรสังเกตปฏิกิริยาที่เกิดซ้ำเมื่อมีแรงกดดัน",
        "ความสัมพันธ์จะชัดขึ้นเมื่อพิจารณาความต้องการทางอารมณ์ การสื่อสาร จังหวะเวลา และขอบเขตส่วนตัวร่วมกัน",
        "ทิศทางงานแข็งแรงที่สุดเมื่อจุดเด่นที่เกิดซ้ำสอดคล้องกับสภาพแวดล้อมที่ยั่งยืน ธาตุที่ส่งเสริมคือ {fav}",
        "รูปแบบการเงินสะท้อนวิธีตัดสินใจ ความเสี่ยง และการจัดการทรัพยากร ไม่ใช่คำแนะนำการลงทุน",
        "การแสดงออกทางสังคมเกิดจากลัคนา {asc} ร่วมกับแนวโน้มทางอารมณ์และการตัดสินใจภายใน",
        "เรื่องครอบครัวมักเชื่อมโยงความมั่นคง หน้าที่ ความรู้สึกเป็นส่วนหนึ่ง และความคาดหวังที่สืบทอดมา",
        "เงาหรือความท้าทายมักเป็นจุดแข็งที่ใช้มากเกินไปหรือกลไกป้องกันตนเอง การตระหนักรู้เพิ่มทางเลือก",
        "พรสวรรค์มักชัดเมื่อหลายระบบชี้ไปในทิศทางเดียวกัน ลองสังเกตเลขเส้นทางชีวิต {life_path} และ Type {hd_type}",
        "ทดลองทีละข้อ บันทึกผล และยึดข้อมูลจริงในการตัดสินใจสำคัญ",
    ],
    "es": [
        "La carta combina Sol {sun}, Luna {moon}, Ascendente {asc}, Maestro del Día {day_master}, Camino de Vida {life_path} y Tipo de Human Design {hd_type}. Úsalos como perspectivas complementarias, no como juicios fijos.",
        "La Luna ({moon}) describe necesidades emocionales y el Maestro del Día ({day_master}) aporta una visión elemental. Observa las reacciones que se repiten bajo presión.",
        "Las relaciones se comprenden mejor al integrar necesidades emocionales, comunicación, tiempos y límites personales.",
        "La dirección profesional es más sólida cuando las fortalezas recurrentes coinciden con un entorno sostenible. Elementos favorables: {fav}.",
        "Los patrones financieros reflejan decisiones, tolerancia al riesgo y hábitos de recursos. No constituyen asesoramiento financiero.",
        "La expresión social combina el Ascendente {asc} con tendencias emocionales y de decisión más profundas.",
        "Los temas familiares muestran dónde se cruzan seguridad, deber, pertenencia y expectativas heredadas.",
        "Las sombras suelen ser fortalezas usadas en exceso o hábitos protectores. La conciencia amplía las opciones.",
        "Los talentos aparecen donde varios sistemas coinciden. El Camino de Vida {life_path} y el Tipo {hd_type} son lentes prácticos.",
        "Aplica una idea cada vez, registra los cambios y basa las decisiones importantes en evidencia real.",
    ],
    "ar": [
        "تجمع الخريطة بين الشمس {sun} والقمر {moon} والطالع {asc} وسيد اليوم {day_master} ومسار الحياة {life_path} ونوع Human Design {hd_type}. استخدمها كوجهات نظر متكاملة لا كأحكام ثابتة.",
        "يعكس القمر ({moon}) الاحتياجات العاطفية، بينما يضيف سيد اليوم ({day_master}) منظورًا عن معالجة الطاقة. راقب ردود الفعل المتكررة تحت الضغط.",
        "تُفهم العلاقات بصورة أفضل عند جمع الاحتياجات العاطفية والتواصل والتوقيت والحدود الشخصية.",
        "يكون المسار المهني أقوى عندما تلتقي نقاط القوة المتكررة ببيئة مستدامة. العناصر الداعمة: {fav}.",
        "تعكس أنماط المال أسلوب القرار وتحمل المخاطر وإدارة الموارد. وهي ليست نصيحة مالية.",
        "تجمع الصورة الاجتماعية بين الطالع {asc} والميول العاطفية وطرق اتخاذ القرار الأعمق.",
        "توضح موضوعات الأسرة تداخل الأمان والمسؤولية والانتماء والتوقعات الموروثة.",
        "غالبًا ما تكون موضوعات الظل نقاط قوة أُفرط في استخدامها أو عادات دفاعية. الوعي يوسّع الاختيار.",
        "تظهر المواهب حين تشير عدة أنظمة إلى الاتجاه نفسه. مسار الحياة {life_path} والنوع {hd_type} عدستان عمليتان.",
        "طبّق ملاحظة واحدة في كل مرة، وسجّل النتائج، واجعل القرارات المهمة قائمة على الواقع.",
    ],
}


def normalize_report_language(language: str | None) -> str:
    value = str(language or "zh-TW").strip()
    aliases = {
        "zh": "zh-TW", "zh_tw": "zh-TW", "zh-Hant": "zh-TW",
        "English": "en", "日本語": "ja", "ไทย": "th",
        "Español": "es", "العربية": "ar",
    }
    value = aliases.get(value, value)
    return value if value in SUPPORTED_REPORT_LANGUAGES else "zh-TW"


def report_html_meta(language: str) -> Dict[str, str]:
    return _LANG_META[normalize_report_language(language)]


def report_text(language: str) -> Dict[str, str]:
    return _TEXT[normalize_report_language(language)]


def _profile_value(profile: Any, name: str, default: str = "—") -> str:
    value = getattr(profile, name, None)
    if value in (None, ""):
        return default
    return str(value)


def canonical_report_facts(report: Any, language: str) -> Dict[str, str]:
    language = normalize_report_language(language)
    wc = getattr(report, "western_chart", None)
    bc = getattr(report, "bazi_chart", None)
    nc = getattr(report, "numerology_chart", None)
    hd = getattr(report, "human_design_chart", None)

    sun = moon = asc = "—"
    if wc:
        for pp in getattr(wc, "planet_positions", []) or []:
            planet_name = getattr(getattr(pp, "planet", None), "value", "")
            if planet_name in ("太陽", "Sun"):
                sun = translate_zodiac(normalize_zodiac_value(getattr(getattr(pp, "sign", None), "value", "—")), language)
            elif planet_name in ("月亮", "Moon"):
                moon = translate_zodiac(normalize_zodiac_value(getattr(getattr(pp, "sign", None), "value", "—")), language)
        if getattr(wc, "ascendant_accuracy", "") == "precise":
            asc = translate_zodiac(normalize_zodiac_value(getattr(getattr(wc, "ascendant", None), "value", "—")), language)

    day_master = "—"
    fav = "—"
    if bc:
        day_master = translate_bazi_stem(getattr(getattr(bc, "day_master", None), "value", "—"), language)
        elements = getattr(bc, "favorable_elements", []) or []
        fav = ", ".join(translate_element(getattr(x, "value", str(x)), language) for x in elements) or "—"

    life_path = str(getattr(nc, "life_path_number", "—")) if nc else "—"
    hd_type = hd_strategy = hd_authority = "—"
    if hd:
        hd_type = translate_hd_type(getattr(hd, "type_name", getattr(hd, "type_name_zh", "—")), language)
        hd_strategy = translate_hd_strategy(getattr(hd, "strategy", "—"), language)
        hd_authority = translate_hd_authority(getattr(hd, "authority", "—"), language)

    return {
        "sun": sun, "moon": moon, "asc": asc, "day_master": day_master,
        "fav": fav, "life_path": life_path, "hd_type": hd_type,
        "hd_strategy": hd_strategy, "hd_authority": hd_authority,
    }




def _detailed_evidence_blocks(report: Any, language: str, facts: Dict[str, str]) -> List[str]:
    """Return ten section-specific evidence blocks for non-Chinese reports.

    The text is generated from canonical calculation facts. It intentionally
    mirrors the structure of the full Traditional-Chinese report without
    changing the calculation model or inventing deterministic outcomes.
    """
    language = normalize_report_language(language)
    wc = getattr(report, "western_chart", None)
    bc = getattr(report, "bazi_chart", None)
    nc = getattr(report, "numerology_chart", None)
    hd = getattr(report, "human_design_chart", None)
    zc = getattr(report, "ziwei_chart", None)
    houses = getattr(wc, "houses", []) or [] if wc else []
    aspects = getattr(wc, "aspects", []) or [] if wc else []
    aspect_count = len(aspects)
    defined_centers = len(getattr(hd, "defined_centers", []) or []) if hd else 0
    channel_count = len(getattr(hd, "defined_channels", []) or []) if hd else 0
    ziwei_mode = getattr(zc, "calculation_mode", "—") if zc else "—"
    house_count = len(houses)
    data = dict(facts)
    data.update({
        "aspect_count": aspect_count, "house_count": house_count,
        "defined_centers": defined_centers, "channel_count": channel_count,
        "ziwei_mode": ziwei_mode,
    })
    blocks = {
        "en": [
            "**Evidence used**\n- Sun: {sun}; Moon: {moon}; Ascendant: {asc}.\n- BaZi Day Master: {day_master}; favorable elements: {fav}.\n- Life Path: {life_path}; Human Design Type: {hd_type}.\n\nThis combination describes the tension between visible identity, private needs, and habitual decision style. Compare repeated signals across systems before drawing conclusions.",
            "**Emotional and action pattern**\n- Moon {moon} is the main emotional reference.\n- Day Master {day_master} describes how pressure is processed through the Five Elements.\n- Human Design Strategy and Authority add timing and decision cues.\n\nLook for the difference between an immediate reaction and a decision that still feels correct after emotional intensity settles.",
            "**Relationship evidence**\n- Emotional needs: Moon {moon}.\n- Social presentation: Ascendant {asc}.\n- Decision pattern: Human Design Type {hd_type}.\n\nThe practical focus is communication rhythm, boundaries, repair after conflict, and whether both people can state needs without over-adapting.",
            "**Career evidence**\n- Sun {sun} shows the style of purposeful expression.\n- Ascendant {asc} shapes first impressions and role fit.\n- Favorable BaZi elements: {fav}.\n- Zi Wei calculation mode: {ziwei_mode}.\n\nPrefer work environments that reward the repeated strengths shown across systems and allow sustainable pacing rather than constant compensation.",
            "**Wealth evidence**\n- Day Master: {day_master}.\n- Favorable elements: {fav}.\n- Life Path: {life_path}.\n\nUse these factors to review earning style, spending triggers, tolerance for uncertainty, and resource discipline. This is reflective material, not financial advice.",
            "**Social evidence**\n- Ascendant {asc} describes the visible interface with others.\n- Moon {moon} describes what is needed to feel safe enough to connect.\n- Human Design Type {hd_type} describes a recurring interaction pattern.\n\nNotice where you become overly accommodating, overly distant, or clearer when roles and expectations are explicit.",
            "**Family evidence**\n- Moon {moon} relates to emotional security.\n- BaZi Day Master {day_master} adds duty and adaptation themes.\n- The chart contains {house_count} calculated houses and {aspect_count} major aspects.\n\nSeparate inherited expectations from present-day choices, and make responsibilities discussable rather than assumed.",
            "**Shadow and pressure points**\n- Strong traits can become rigid when overused.\n- Open or undefined Human Design areas may amplify environmental pressure.\n- This chart has {defined_centers} defined centers and {channel_count} defined channels.\n\nThe goal is not to label weakness, but to identify when protection, urgency, control, or withdrawal replaces flexible choice.",
            "**Talent evidence**\n- Sun {sun} and Ascendant {asc} show expression and presentation.\n- Life Path {life_path} highlights recurring learning and contribution themes.\n- Favorable elements {fav} indicate supportive modes of development.\n\nTalents are strongest where interest, repeated practice, feedback, and real-world results agree.",
            "**Practical plan**\n1. Test one insight for two weeks.\n2. Record situations, reactions, and outcomes.\n3. Keep what improves clarity or relationships.\n4. Discard interpretations that do not match lived evidence.\n\nRevisit major decisions only after checking facts, timing, and personal responsibility.",
        ],
        "ja": [
            "**使用した根拠**\n- 太陽：{sun}、月：{moon}、アセンダント：{asc}。\n- 八字の日主：{day_master}、有利な五行：{fav}。\n- ライフパス：{life_path}、Human Design Type：{hd_type}。\n\n外向きの自己像、内面的ニーズ、意思決定の癖を統合して読みます。単一の要素ではなく、複数体系で重なる傾向を確認してください。",
            "**感情と行動の根拠**\n- 月{moon}は感情的安心感の基準です。\n- 日主{day_master}はプレッシャー処理の五行傾向を示します。\n- Human Design は行動のタイミングと決断方法を補足します。\n\n即時反応と、時間を置いても納得できる判断を区別して観察しましょう。",
            "**関係性の根拠**\n- 感情ニーズ：月{moon}。\n- 第一印象：アセンダント{asc}。\n- 相互作用の型：{hd_type}。\n\n対話のリズム、境界線、衝突後の修復、必要を言語化できるかが実践上の焦点です。",
            "**仕事の根拠**\n- 太陽{sun}は目的意識の表し方。\n- アセンダント{asc}は役割適合と第一印象。\n- 有利な五行：{fav}。\n- 紫微計算モード：{ziwei_mode}。\n\n複数体系で繰り返し示される強みを、持続可能な環境で活かせる仕事を優先してください。",
            "**財運の根拠**\n- 日主：{day_master}。\n- 有利な五行：{fav}。\n- ライフパス：{life_path}。\n\n収入の作り方、支出の引き金、不確実性への耐性、資源管理を見直す材料です。投資助言ではありません。",
            "**対人関係の根拠**\n- アセンダント{asc}は外向きの接点。\n- 月{moon}は安心して関われる条件。\n- {hd_type}は反復しやすい交流パターン。\n\n過剰適応、早すぎる距離化、役割が曖昧な時の反応を観察してください。",
            "**家庭の根拠**\n- 月{moon}は安心感。\n- 日主{day_master}は責任と適応。\n- 計算済みハウスは{house_count}、主要アスペクトは{aspect_count}です。\n\n受け継いだ期待と現在の選択を分け、責任を暗黙ではなく対話可能にしてください。",
            "**影とプレッシャー**\n- 強みは使い過ぎると硬直します。\n- Human Design の未定義領域は環境圧を増幅する場合があります。\n- 定義センター{defined_centers}、定義チャネル{channel_count}。\n\n弱点を決めつけず、焦り・支配・撤退が柔軟な選択を置き換える場面を見つけます。",
            "**才能の根拠**\n- 太陽{sun}とアセンダント{asc}は表現と見せ方。\n- ライフパス{life_path}は学習と貢献の反復テーマ。\n- 有利な五行{fav}は育てやすい方法を示します。\n\n関心、反復練習、他者からのフィードバック、実際の成果が一致する領域を重視してください。",
            "**実践プラン**\n1. 一つの示唆を2週間試す。\n2. 状況・反応・結果を記録する。\n3. 明確さや関係改善につながるものを残す。\n4. 実体験に合わない解釈は手放す。\n\n重要な判断は事実、タイミング、自己責任を確認してから行ってください。",
        ],
    }
    # Other languages keep the translated base narrative plus a localized
    # evidence appendix rather than falling back to Chinese prose.
    if language in blocks:
        return [item.format(**data) for item in blocks[language]]
    generic = {
        "th": "\n\n**ข้อมูลอ้างอิงจากผลคำนวณ**\n- ดวงอาทิตย์: {sun}; ดวงจันทร์: {moon}; ลัคนา: {asc}\n- Day Master: {day_master}; ธาตุที่ส่งเสริม: {fav}\n- Life Path: {life_path}; Human Design: {hd_type}\n- ศูนย์ที่นิยาม: {defined_centers}; ช่อง: {channel_count}",
        "es": "\n\n**Evidencia del cálculo**\n- Sol: {sun}; Luna: {moon}; Ascendente: {asc}\n- Maestro del Día: {day_master}; elementos favorables: {fav}\n- Camino de Vida: {life_path}; Human Design: {hd_type}\n- Centros definidos: {defined_centers}; canales: {channel_count}",
        "ar": "\n\n**أدلة الحساب**\n- الشمس: {sun}؛ القمر: {moon}؛ الطالع: {asc}\n- سيد اليوم: {day_master}؛ العناصر الداعمة: {fav}\n- مسار الحياة: {life_path}؛ Human Design: {hd_type}\n- المراكز المحددة: {defined_centers}؛ القنوات: {channel_count}",
    }.get(language, "")
    return [generic.format(**data) for _ in range(10)]


def localized_section_bodies(report: Any, language: str) -> List[str]:
    language = normalize_report_language(language)
    facts = canonical_report_facts(report, language)
    if language == "zh-TW":
        synthesis = getattr(report, "synthesis", None)
        if synthesis is not None:
            return [
                getattr(synthesis, "core_personality", ""),
                "\n\n".join(filter(None, [getattr(synthesis, "emotional_pattern", ""), getattr(synthesis, "action_pattern", "")])),
                getattr(synthesis, "love_pattern", ""),
                getattr(synthesis, "career_pattern", ""),
                getattr(synthesis, "wealth_pattern", ""),
                getattr(synthesis, "social_pattern", ""),
                getattr(synthesis, "family_security", ""),
                "\n\n".join(filter(None, [getattr(synthesis, "stress_shadow", ""), getattr(synthesis, "life_lessons", "")])),
                "\n\n".join(filter(None, [getattr(synthesis, "innate_gifts", ""), getattr(synthesis, "recurring_challenges", "")])),
                "\n\n".join(filter(None, [getattr(synthesis, "one_year_advice", ""), getattr(synthesis, "three_year_advice", "")])),
            ]
    templates = _SECTION_TEMPLATES.get(language, _SECTION_TEMPLATES["en"])
    base = [item.format(**facts) for item in templates]
    detail = _detailed_evidence_blocks(report, language, facts)
    return [f"{intro}\n\n{extra}" if extra else intro for intro, extra in zip(base, detail)]


def render_localized_markdown(report: Any, language: str = "zh-TW", version: str = "") -> str:
    language = normalize_report_language(language)
    text = report_text(language)
    profile = getattr(report, "profile", None)
    facts = canonical_report_facts(report, language)
    bodies = localized_section_bodies(report, language)
    headings = [
        text["core"], text["emotion"], text["relationship"], text["career"],
        text["wealth"], text["social"], text["family"], text["shadow"],
        text["talent"], text["advice"],
    ]
    created = getattr(report, "created_at", "—")
    version = version or getattr(report, "version", "—")
    lines = [
        "---", f"language: {language}", f"direction: {_LANG_META[language]['dir']}",
        f"version: {version}", "---", "",
        f"# {text['title']}", "",
        f"## {text['basic']}", "",
        f"- **{text['name']}**: {_profile_value(profile, 'name')}",
        f"- **{text['birth_date']}**: {_profile_value(profile, 'birth_date')}",
        f"- **{text['birth_time']}**: {_profile_value(profile, 'birth_time')}",
        f"- **{text['location']}**: {_profile_value(profile, 'birth_city')}, {_profile_value(profile, 'birth_country')}",
        f"- **{text['created']}**: {created}", f"- **{text['version']}**: {version}", "",
        f"## {text['overview']}", "",
        f"| {text['western']} | {text['bazi']} | {text['numerology']} | {text['human_design']} |",
        "|---|---|---|---|",
        f"| {text['sun']}: {facts['sun']}<br>{text['moon']}: {facts['moon']}<br>{text['asc']}: {facts['asc']} | "
        f"{text['day_master']}: {facts['day_master']}<br>{text['fav_elements']}: {facts['fav']} | "
        f"{text['life_path']}: {facts['life_path']} | "
        f"{text['hd_type']}: {facts['hd_type']}<br>{text['hd_strategy']}: {facts['hd_strategy']}<br>{text['hd_authority']}: {facts['hd_authority']} |",
        "",
    ]
    for heading, body in zip(headings, bodies):
        lines += [f"## {heading}", "", body or "—", ""]
    lines += [
        f"## {text['accuracy']}", "",
        text["fallback"] if language != "zh-TW" else "本報告依輸入的出生日期、時間、地點與可用星曆資料計算；出生時間未知時，上升星座、宮位與部分人類圖結果僅供參考。",
        "",
        f"## {text['disclaimer']}", "",
        {
            "zh-TW": "本報告僅供自我探索與關係理解參考，不構成醫療、法律、投資或重大人生決策建議。",
            "en": "This report is for self-reflection only and is not medical, legal, financial, or major life-decision advice.",
            "ja": "本レポートは自己理解の参考であり、医療・法律・投資・重大な人生判断の助言ではありません。",
            "th": "รายงานนี้ใช้เพื่อการสำรวจตนเองเท่านั้น ไม่ใช่คำแนะนำด้านการแพทย์ กฎหมาย การเงิน หรือการตัดสินใจสำคัญ",
            "es": "Este informe es solo para reflexión personal y no constituye asesoramiento médico, legal, financiero ni para decisiones vitales importantes.",
            "ar": "هذا التقرير مخصص للتأمل الذاتي فقط ولا يُعد نصيحة طبية أو قانونية أو مالية أو لاتخاذ قرارات مصيرية.",
        }[language],
    ]
    return "\n".join(lines)
