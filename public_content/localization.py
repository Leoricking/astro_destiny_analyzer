"""Localized display content for public landing pages.

The registry keeps Traditional Chinese source content for backward compatibility.
This module provides language-aware display copies without mutating canonical page
objects.  Long-form copy is intentionally concise in non-Chinese locales so the
UI never silently mixes Traditional Chinese into another language.
"""
from __future__ import annotations

from copy import deepcopy
from public_content.models import PublicContentPage, PublicContentSection

_TRANSLATIONS = {
    "zodiac-overview": {
        "en": ("12 Zodiac Signs: Personality and Relationships", "A concise guide to the twelve zodiac signs and their relationship styles.", "Why the Sun sign is only the beginning", "The Sun sign describes a central style, while the Moon, Ascendant, Venus, Mars, houses, and aspects add important emotional and relational context.", "Create a Complete Birth Chart Report"),
        "ja": ("12星座の性格と人間関係ガイド", "12星座の基本傾向と人間関係の特徴を簡潔に紹介します。", "太陽星座だけでは不十分な理由", "太陽星座は中心的な傾向を示しますが、月、アセンダント、金星、火星、ハウス、アスペクトも感情や対人関係を理解するうえで重要です。", "完全な出生図レポートを作成"),
        "th": ("ภาพรวมบุคลิกและความสัมพันธ์ของ 12 ราศี", "คู่มือย่อเกี่ยวกับแนวโน้มพื้นฐานและรูปแบบความสัมพันธ์ของทั้ง 12 ราศี", "เหตุใดการดูเพียงราศีอาทิตย์จึงไม่เพียงพอ", "ราศีอาทิตย์สะท้อนแนวโน้มหลัก แต่ดวงจันทร์ ลัคนา ดาวศุกร์ ดาวอังคาร เรือน และมุมดาวช่วยเติมบริบทด้านอารมณ์และความสัมพันธ์", "สร้างรายงานดวงกำเนิดฉบับเต็ม"),
        "es": ("Los 12 signos: personalidad y relaciones", "Guía breve sobre las tendencias y estilos de relación de los doce signos.", "Por qué el signo solar es solo el comienzo", "El signo solar describe una tendencia central, pero la Luna, el Ascendente, Venus, Marte, las casas y los aspectos aportan contexto emocional y relacional.", "Crear un informe natal completo"),
        "ar": ("الأبراج الاثنا عشر: الشخصية والعلاقات", "دليل موجز لاتجاهات الأبراج وأنماط العلاقات.", "لماذا لا تكفي الشمس وحدها", "يعرض برج الشمس الاتجاه الأساسي، بينما يضيف القمر والطالع والزهرة والمريخ والبيوت والزوايا سياقًا مهمًا لفهم المشاعر والعلاقات.", "إنشاء تقرير ميلاد كامل"),
    },
    "zodiac-compatibility": {
        "en": ("Zodiac Matching Is Only the Start", "Real compatibility looks beyond Sun signs to Synastry and Composite patterns.", "Compatibility beyond sign matching", "Two people can share a sign yet interact very differently. Synastry describes how two charts connect, while a Composite chart describes the relationship as a shared system.", "Create a Compatibility Report"),
        "ja": ("星座相性は出発点にすぎません", "本格的な相性分析ではシナストリーとコンポジットを確認します。", "星座だけでは分からない相性", "同じ星座でも関係性は大きく異なります。シナストリーは二人の相互作用を、コンポジットは関係そのものの性質を示します。", "相性レポートを作成"),
        "th": ("การจับคู่ราศีเป็นเพียงจุดเริ่มต้น", "การวิเคราะห์ความเข้ากันได้ควรดู Synastry และ Composite เพิ่มเติม", "มากกว่าการจับคู่ราศี", "แม้คนสองคนจะมีราศีเดียวกัน รูปแบบปฏิสัมพันธ์ก็อาจต่างกันมาก Synastry แสดงการเชื่อมโยงของดวงสองคน ส่วน Composite อธิบายความสัมพันธ์ในฐานะระบบร่วม", "สร้างรายงานความเข้ากันได้"),
        "es": ("La compatibilidad zodiacal es solo el comienzo", "La compatibilidad real analiza la sinastría y la carta compuesta.", "Más allá de comparar signos", "Dos personas del mismo signo pueden relacionarse de maneras muy distintas. La sinastría muestra la interacción y la carta compuesta describe la relación como un sistema compartido.", "Crear informe de compatibilidad"),
        "ar": ("توافق الأبراج ليس سوى البداية", "التحليل الأعمق يشمل التوافق بين الخريطتين والخريطة المركبة.", "ما وراء مقارنة الأبراج", "قد يتفاعل شخصان من البرج نفسه بطرق مختلفة جدًا. يوضح التوافق بين الخريطتين نقاط الاتصال، بينما تصف الخريطة المركبة العلاقة كنظام مشترك.", "إنشاء تقرير توافق"),
    },
    "human-design-overview": {
        "en": ("What Is Human Design?", "An introduction to Type, Strategy, Authority, and decision patterns.", "Human Design as a reflection tool", "Type describes an energy pattern, Strategy suggests how to engage with situations, and Authority offers a decision-making reference. It is a self-reflection framework, not a fixed fate statement.", "Create a Complete Human Design Report"),
        "ja": ("ヒューマンデザインとは", "Type・Strategy・Authority と意思決定パターンの入門です。", "自己理解のためのヒューマンデザイン", "Type はエネルギー傾向、Strategy は状況への関わり方、Authority は意思決定の参考軸を示します。宿命を断定するものではありません。", "完全なヒューマンデザインレポートを作成"),
        "th": ("Human Design คืออะไร", "บทนำเกี่ยวกับ Type, Strategy, Authority และรูปแบบการตัดสินใจ", "Human Design เพื่อการสะท้อนตนเอง", "Type อธิบายรูปแบบพลังงาน Strategy เสนอแนวทางการมีปฏิสัมพันธ์ และ Authority เป็นกรอบอ้างอิงในการตัดสินใจ ไม่ใช่คำตัดสินชะตาชีวิต", "สร้างรายงาน Human Design ฉบับเต็ม"),
        "es": ("¿Qué es Human Design?", "Introducción al Tipo, la Estrategia, la Autoridad y los patrones de decisión.", "Human Design como herramienta de reflexión", "El Tipo describe un patrón energético, la Estrategia orienta la interacción y la Autoridad ofrece una referencia para decidir. No es una sentencia de destino.", "Crear informe completo de Human Design"),
        "ar": ("ما هو Human Design؟", "مقدمة إلى النوع والاستراتيجية والسلطة الداخلية وأنماط اتخاذ القرار.", "Human Design كأداة للتأمل", "يصف النوع نمط الطاقة، وتقترح الاستراتيجية طريقة التفاعل، وتقدم السلطة الداخلية مرجعًا لاتخاذ القرار. وهو ليس حكمًا ثابتًا على المصير.", "إنشاء تقرير Human Design كامل"),
    },
    "human-design-types": {
        "en": ("The Five Human Design Types", "Manifestor, Generator, Manifesting Generator, Projector, and Reflector.", "Understanding Type", "Each Type describes a different way of using energy and interacting with the environment. No Type is better than another; the value is in observing which patterns feel consistent in daily life.", "Find Your Human Design Type"),
        "ja": ("ヒューマンデザインの5タイプ", "マニフェスター、ジェネレーター、マニフェスティング・ジェネレーター、プロジェクター、リフレクター。", "タイプを理解する", "各タイプはエネルギーの使い方と環境との関わり方の違いを示します。優劣ではなく、日常で一貫して感じられるパターンを観察するためのものです。", "自分のタイプを確認"),
        "th": ("Human Design ทั้ง 5 ประเภท", "Manifestor, Generator, Manifesting Generator, Projector และ Reflector", "ทำความเข้าใจ Type", "แต่ละ Type อธิบายวิธีใช้พลังงานและปฏิสัมพันธ์กับสิ่งแวดล้อมที่ต่างกัน ไม่มี Type ใดดีกว่าอีกแบบ", "ค้นหา Human Design Type ของคุณ"),
        "es": ("Los cinco tipos de Human Design", "Manifestor, Generator, Generador Manifestante, Proyector y Reflector.", "Comprender el Tipo", "Cada Tipo describe una forma distinta de utilizar la energía e interactuar con el entorno. Ninguno es superior a otro.", "Descubrir tu Tipo"),
        "ar": ("الأنواع الخمسة في Human Design", "Manifestor وGenerator وManifesting Generator وProjector وReflector.", "فهم النوع", "يصف كل نوع طريقة مختلفة لاستخدام الطاقة والتفاعل مع البيئة. لا يوجد نوع أفضل من غيره.", "اكتشاف نوعك"),
    },
    "relationship-compatibility": {
        "en": ("Compatibility Is More Than Sun Signs", "Explore emotional, cooperative, family, and partnership interaction patterns.", "A multi-system view of relationships", "Compatibility analysis can combine chart interaction, communication patterns, emotional needs, and long-term dynamics. A score is a summary, not a judgment of relationship value.", "Create a Compatibility Analysis"),
        "ja": ("相性は星座だけでは決まりません", "恋愛・協力・親子・友人関係の相互作用を多角的に見ます。", "関係性を複数の視点から見る", "相性分析では、チャート間の作用、コミュニケーション、感情的ニーズ、長期的な関係性を組み合わせて確認します。スコアは要約であり、関係の価値を決めるものではありません。", "相性分析を作成"),
        "th": ("ความเข้ากันได้ไม่ได้ดูเพียงราศี", "สำรวจรูปแบบด้านอารมณ์ การร่วมมือ ครอบครัว และคู่ชีวิต", "มองความสัมพันธ์แบบหลายระบบ", "การวิเคราะห์สามารถรวมปฏิสัมพันธ์ของดวง การสื่อสาร ความต้องการทางอารมณ์ และแนวโน้มระยะยาว คะแนนเป็นเพียงสรุป ไม่ใช่คำตัดสินคุณค่าความสัมพันธ์", "สร้างการวิเคราะห์ความเข้ากันได้"),
        "es": ("La compatibilidad va más allá de los signos", "Explora patrones emocionales, de cooperación, familiares y de pareja.", "Una visión multidimensional de la relación", "El análisis puede combinar interacción de cartas, comunicación, necesidades emocionales y dinámica a largo plazo. La puntuación es un resumen, no un juicio sobre la relación.", "Crear análisis de compatibilidad"),
        "ar": ("التوافق يتجاوز الأبراج", "استكشاف الأنماط العاطفية والتعاونية والعائلية وأنماط الشراكة.", "رؤية متعددة الأبعاد للعلاقة", "يمكن للتحليل الجمع بين تفاعل الخرائط والتواصل والاحتياجات العاطفية والديناميكيات طويلة الأمد. الدرجة ملخص وليست حكمًا على قيمة العلاقة.", "إنشاء تحليل توافق"),
    },
    "ziwei-overview": {
        "en": ("Zi Wei Dou Shu Basics", "Life Palace, Body Palace, major stars, and life-cycle periods.", "What Zi Wei Dou Shu describes", "Zi Wei Dou Shu organizes life themes through palaces and star configurations. It can be used to explore personality, career, relationships, resources, and changing life stages.", "Create a Zi Wei Integrated Report"),
        "ja": ("紫微斗数の基礎", "命宮・身宮・主星・大限の基本を紹介します。", "紫微斗数が示すもの", "紫微斗数は宮位と星の配置を通じて、人格、仕事、関係、資源、人生段階を整理して考えるための体系です。", "紫微統合レポートを作成"),
        "th": ("พื้นฐาน Zi Wei Dou Shu", "ทำความเข้าใจ Life Palace, Body Palace, ดาวหลัก และช่วงวัย", "Zi Wei Dou Shu อธิบายอะไร", "ระบบนี้จัดระเบียบหัวข้อชีวิตผ่านเรือนและตำแหน่งดาว เพื่อสำรวจบุคลิก งาน ความสัมพันธ์ ทรัพยากร และช่วงชีวิต", "สร้างรายงาน Zi Wei แบบบูรณาการ"),
        "es": ("Fundamentos de Zi Wei Dou Shu", "Palacio de Vida, Palacio del Cuerpo, estrellas principales y ciclos.", "Qué describe Zi Wei Dou Shu", "Zi Wei Dou Shu organiza los temas vitales mediante palacios y configuraciones estelares para explorar personalidad, trabajo, relaciones, recursos y etapas de vida.", "Crear informe integrado de Zi Wei"),
        "ar": ("أساسيات Zi Wei Dou Shu", "قصر الحياة وقصر الجسد والنجوم الرئيسية ودورات العمر.", "ما الذي يصفه Zi Wei Dou Shu", "ينظم هذا النظام موضوعات الحياة عبر القصور وتوزيع النجوم لاستكشاف الشخصية والعمل والعلاقات والموارد ومراحل الحياة.", "إنشاء تقرير Zi Wei متكامل"),
    },
    "bazi-overview": {
        "en": ("BaZi Basics", "Four Pillars, Five Elements, and solar-term boundaries.", "More than the birth-year animal", "BaZi uses the year, month, day, and hour pillars to examine the balance of the Five Elements and the Day Master. Accurate date, time, and timezone improve precision.", "Create a BaZi Integrated Report"),
        "ja": ("八字の基礎", "四柱・五行・節気の基本を紹介します。", "生肖だけではない八字", "八字は年・月・日・時の四柱から五行バランスと日主を確認します。正確な日時とタイムゾーンが精度を高めます。", "八字統合レポートを作成"),
        "th": ("พื้นฐาน BaZi", "เสาหลักทั้งสี่ ธาตุทั้งห้า และขอบเขตฤดูกาล", "BaZi ไม่ได้ดูเพียงนักษัตรปีเกิด", "BaZi ใช้เสาปี เดือน วัน และเวลาเพื่อพิจารณาสมดุลธาตุทั้งห้าและ Day Master ความแม่นยำเพิ่มขึ้นเมื่อมีวัน เวลา และเขตเวลาที่ถูกต้อง", "สร้างรายงาน BaZi แบบบูรณาการ"),
        "es": ("Fundamentos de BaZi", "Cuatro Pilares, Cinco Elementos y límites de términos solares.", "BaZi es más que el animal del año", "BaZi utiliza los pilares de año, mes, día y hora para analizar el equilibrio de los Cinco Elementos y el Maestro del Día.", "Crear informe integrado de BaZi"),
        "ar": ("أساسيات BaZi", "الأعمدة الأربعة والعناصر الخمسة وحدود الفصول الشمسية.", "BaZi أكثر من حيوان سنة الميلاد", "يستخدم BaZi أعمدة السنة والشهر واليوم والساعة لفحص توازن العناصر الخمسة وسيد اليوم. تزيد الدقة مع التاريخ والوقت والمنطقة الزمنية الصحيحة.", "إنشاء تقرير BaZi متكامل"),
    },
    "numerology-overview": {
        "en": ("Numerology Overview", "A quick way to explore central life themes and recurring patterns.", "How numerology is used", "Life Path numbers can be used as a concise reflection tool. They do not replace broader chart analysis or real-world context.", "Create an Integrated Report"),
        "ja": ("数秘術の概要", "人生の中心テーマや繰り返しやすいパターンを簡潔に確認します。", "数秘術の使い方", "ライフパスナンバーは自己理解のための簡潔な手掛かりです。総合的な命盤や現実の状況に代わるものではありません。", "統合レポートを作成"),
        "th": ("ภาพรวมเลขศาสตร์", "สำรวจธีมหลักของชีวิตและรูปแบบที่เกิดซ้ำอย่างรวดเร็ว", "การใช้เลขศาสตร์", "เลขเส้นทางชีวิตเป็นเครื่องมือสะท้อนตนเองแบบกระชับ และไม่ควรใช้แทนการวิเคราะห์โดยรวม", "สร้างรายงานแบบบูรณาการ"),
        "es": ("Introducción a la numerología", "Explora de forma rápida temas vitales y patrones recurrentes.", "Cómo usar la numerología", "El número de Camino de Vida es una herramienta breve de reflexión y no sustituye un análisis integral.", "Crear informe integrado"),
        "ar": ("نظرة عامة على علم الأعداد", "طريقة سريعة لاستكشاف موضوعات الحياة والأنماط المتكررة.", "كيفية استخدام علم الأعداد", "يمكن استخدام رقم مسار الحياة كأداة مختصرة للتأمل، ولا يحل محل التحليل الشامل.", "إنشاء تقرير متكامل"),
    },
    "full-report-guide": {
        "en": ("Why Use an Integrated Report?", "Western Astrology, BaZi, Zi Wei, and Human Design describe different dimensions.", "How the systems complement one another", "Each system highlights different layers: psychological tendencies, timing and elemental structure, life-palace themes, and decision patterns. Integration helps compare recurring themes without treating any one system as absolute.", "Start a Complete Integrated Report"),
        "ja": ("なぜ統合命盤を作るのか", "西洋占星術・八字・紫微斗数・ヒューマンデザインは異なる側面を扱います。", "複数体系を組み合わせる意味", "各体系は心理傾向、時期と五行構造、宮位テーマ、意思決定パターンなど異なる層を示します。統合することで共通テーマを比較できます。", "完全な統合レポートを開始"),
        "th": ("ทำไมจึงควรใช้รายงานแบบบูรณาการ", "โหราศาสตร์ตะวันตก BaZi, Zi Wei และ Human Design อธิบายคนละมิติ", "ระบบต่าง ๆ เสริมกันอย่างไร", "แต่ละระบบเน้นมุมที่ต่างกัน เช่น แนวโน้มทางจิตใจ โครงสร้างเวลาและธาตุ หัวข้อเรือนชีวิต และรูปแบบการตัดสินใจ การบูรณาการช่วยเปรียบเทียบธีมที่เกิดซ้ำ", "เริ่มสร้างรายงานแบบบูรณาการ"),
        "es": ("¿Por qué usar un informe integrado?", "Astrología occidental, BaZi, Zi Wei y Human Design describen dimensiones distintas.", "Cómo se complementan los sistemas", "Cada sistema resalta capas diferentes: tendencias psicológicas, estructura temporal y elemental, temas de palacios y patrones de decisión.", "Iniciar informe integrado completo"),
        "ar": ("لماذا نستخدم تقريرًا متكاملًا؟", "يصف علم التنجيم الغربي وBaZi وZi Wei وHuman Design أبعادًا مختلفة.", "كيف تكمل الأنظمة بعضها", "يسلط كل نظام الضوء على طبقة مختلفة: الاتجاهات النفسية، وبنية الوقت والعناصر، وموضوعات القصور، وأنماط اتخاذ القرار. يساعد الدمج على مقارنة الموضوعات المتكررة.", "بدء تقرير متكامل كامل"),
    },
}


def localize_public_page(page: PublicContentPage, language: str) -> tuple[PublicContentPage, bool]:
    """Return a localized copy and whether the original long-form body was replaced."""
    if language == "zh-TW":
        return page, False
    data = _TRANSLATIONS.get(page.slug, {}).get(language)
    if not data:
        return page, True
    title, summary, heading, body, cta = data
    clone = deepcopy(page)
    clone.title = title
    clone.subtitle = ""
    clone.summary = summary
    clone.hero_points = []
    clone.sections = [PublicContentSection(heading=heading, body=body)]
    clone.cta_title = cta
    clone.cta_description = summary
    clone.cta_button_label = cta
    # Keep tags canonical/technical to avoid misleading translation.
    return clone, False
