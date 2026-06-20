"""
Astro Destiny Analyzer — Reusable Streamlit UI Components
"""
import streamlit as st
from i18n.translator import t
from i18n.display_names import (
    translate_zodiac, normalize_zodiac_value, translate_bazi_stem, translate_element,
    translate_hd_type, translate_hd_strategy, translate_hd_authority,
    translate_planet, translate_aspect, translate_branch, translate_pillar_label,
    translate_strength,
)
from core.models import ZodiacSign, FiveElement


def render_planet_table(planet_positions, language="zh-TW"):
    """Render planet positions using localized labels without mutating models."""
    import pandas as pd
    headers = {
        "planet": t("planet_table.planet", language=language, default="行星"),
        "sign": t("planet_table.sign", language=language, default="星座"),
        "house": t("planet_table.house", language=language, default="宮位"),
        "degree": t("planet_table.degree", language=language, default="黃道度數"),
        "retrograde": t("planet_table.retrograde", language=language, default="逆行"),
    }
    rows = []
    for pp in planet_positions:
        canonical_sign = normalize_zodiac_value(pp.sign.value)
        rows.append({
            headers["planet"]: translate_planet(pp.planet.value, language),
            headers["sign"]: translate_zodiac(canonical_sign, language),
            headers["house"]: pp.house if pp.house is not None else "—",
            headers["degree"]: f"{pp.sign_degree:.1f}°",
            headers["retrograde"]: t("common.yes", language=language, default="Yes") if pp.retrograde else t("common.no", language=language, default="No"),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_house_table(houses, language="zh-TW"):
    import pandas as pd
    labels = {
        "zh-TW": ("宮位", "星座", "入宮行星", "第 {n} 宮"),
        "en": ("House", "Sign", "Planets", "House {n}"),
        "ja": ("ハウス", "星座", "在室天体", "第{n}ハウス"),
        "th": ("เรือน", "ราศี", "ดาวในเรือน", "เรือนที่ {n}"),
        "es": ("Casa", "Signo", "Planetas", "Casa {n}"),
        "ar": ("البيت", "البرج", "الكواكب", "البيت {n}"),
    }.get(language, ("House", "Sign", "Planets", "House {n}"))
    rows=[]
    for h in houses:
        rows.append({
            labels[0]: labels[3].format(n=h.house_number),
            labels[1]: translate_zodiac(normalize_zodiac_value(h.sign.value), language),
            labels[2]: ", ".join(translate_planet(p.value, language) for p in h.planets) if h.planets else "—",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_aspect_table(aspects, language="zh-TW"):
    import pandas as pd
    labels = {
        "zh-TW": ("行星1", "相位", "行星2", "容許度"),
        "en": ("Planet 1", "Aspect", "Planet 2", "Orb"),
        "ja": ("天体1", "アスペクト", "天体2", "オーブ"),
        "th": ("ดาว 1", "มุมสัมพันธ์", "ดาว 2", "ออร์บ"),
        "es": ("Planeta 1", "Aspecto", "Planeta 2", "Orbe"),
        "ar": ("الكوكب 1", "الزاوية", "الكوكب 2", "الهامش"),
    }.get(language, ("Planet 1", "Aspect", "Planet 2", "Orb"))
    rows=[]
    for a in aspects:
        rows.append({labels[0]: translate_planet(a.planet1.value, language), labels[1]: translate_aspect(a.aspect_type.value, language), labels[2]: translate_planet(a.planet2.value, language), labels[3]: f"{a.orb:.2f}°"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_bazi_pillars(bazi_chart, language="zh-TW"):
    import pandas as pd
    headers = {
        "pillar": t("bazi_table.pillar", language=language, default="柱"),
        "stem": t("bazi_table.heavenly_stem", language=language, default="天干"),
        "branch": t("bazi_table.earthly_branch", language=language, default="地支"),
        "element": t("bazi_table.element", language=language, default="五行"),
    }
    pillars=[bazi_chart.year_pillar,bazi_chart.month_pillar,bazi_chart.day_pillar]
    if bazi_chart.hour_pillar: pillars.append(bazi_chart.hour_pillar)
    rows=[]
    for p in pillars:
        rows.append({headers["pillar"]: translate_pillar_label(p.label, language), headers["stem"]: translate_bazi_stem(p.heavenly_stem.value, language), headers["branch"]: translate_branch(p.earthly_branch.value, language), headers["element"]: translate_element(p.element.value, language)})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_five_element_chart(bazi_chart, language="zh-TW"):
    try:
        import pandas as pd
        ratio=bazi_chart.five_element_ratio; strength=bazi_chart.five_element_strength
        element_label=t("bazi_table.element", language=language, default="五行")
        ratio_label=t("bazi_table.ratio", language=language, default="比例(%)")
        strength_label=t("bazi_table.strength", language=language, default="強弱")
        rows=[{element_label:translate_element(k,language), ratio_label:v, strength_label:translate_strength(strength.get(k,""),language)} for k,v in ratio.items()]
        df=pd.DataFrame(rows)
        st.bar_chart(df.set_index(element_label)[ratio_label]); st.dataframe(df,use_container_width=True,hide_index=True)
    except Exception:
        st.write(bazi_chart.five_element_ratio)


def render_ziwei_palace_grid(ziwei_chart, language="zh-TW"):
    """Render the palace grid. Proper nouns are localized where safe."""
    palace_labels = {
        "命宮":{"en":"Life Palace","ja":"命宮","th":"วังชีวิต","es":"Palacio de Vida","ar":"قصر الحياة"},
        "兄弟宮":{"en":"Siblings Palace","ja":"兄弟宮","th":"วังพี่น้อง","es":"Palacio de Hermanos","ar":"قصر الإخوة"},
        "夫妻宮":{"en":"Relationship Palace","ja":"夫妻宮","th":"วังคู่ครอง","es":"Palacio de Pareja","ar":"قصر الشراكة"},
        "子女宮":{"en":"Children Palace","ja":"子女宮","th":"วังบุตร","es":"Palacio de Hijos","ar":"قصر الأبناء"},
        "財帛宮":{"en":"Wealth Palace","ja":"財帛宮","th":"วังทรัพย์","es":"Palacio de Riqueza","ar":"قصر المال"},
        "疾厄宮":{"en":"Health Palace","ja":"疾厄宮","th":"วังสุขภาพ","es":"Palacio de Salud","ar":"قصر الصحة"},
        "遷移宮":{"en":"Travel Palace","ja":"遷移宮","th":"วังการเดินทาง","es":"Palacio de Viajes","ar":"قصر السفر"},
        "僕役宮":{"en":"Friends Palace","ja":"交友宮","th":"วังมิตร","es":"Palacio de Amistades","ar":"قصر الأصدقاء"},
        "官祿宮":{"en":"Career Palace","ja":"官禄宮","th":"วังอาชีพ","es":"Palacio Profesional","ar":"قصر المهنة"},
        "田宅宮":{"en":"Property Palace","ja":"田宅宮","th":"วังทรัพย์สิน","es":"Palacio de Propiedades","ar":"قصر الممتلكات"},
        "福德宮":{"en":"Fortune Palace","ja":"福徳宮","th":"วังวาสนา","es":"Palacio de Bienestar","ar":"قصر الرفاه"},
        "父母宮":{"en":"Parents Palace","ja":"父母宮","th":"วังบิดามารดา","es":"Palacio de Padres","ar":"قصر الوالدين"},
    }
    def pal(name): return palace_labels.get(name,{}).get(language,name)
    palaces=[ziwei_chart.parents_palace,ziwei_chart.ming_palace,ziwei_chart.brother_palace,ziwei_chart.spouse_palace,ziwei_chart.career_palace,None,None,ziwei_chart.children_palace,ziwei_chart.property_palace,ziwei_chart.fortune_palace,ziwei_chart.friends_palace,ziwei_chart.wealth_palace]
    center = {"zh-TW":"身宮","en":"Body Palace","ja":"身宮","th":"วังกาย","es":"Palacio del Cuerpo","ar":"قصر الجسد"}.get(language,"Body Palace")
    for row_i in range(3):
        cols=st.columns(4)
        for col_i in range(4):
            p=palaces[row_i*4+col_i]
            with cols[col_i]:
                if p is None:
                    if row_i==1 and col_i==1: st.markdown(f"**{center}**\n\n{translate_branch(ziwei_chart.shen_palace.earthly_branch,language)}")
                else:
                    stars=", ".join(p.main_stars) if p.main_stars else "—"
                    st.markdown(f"**{pal(p.name)}** ({translate_branch(p.earthly_branch,language)})\n\n{stars}")


def render_ziwei_formal_table(ziwei_chart, language="zh-TW"):
    import pandas as pd
    labels={
        "zh-TW":("宮位","地支","主星","吉輔","煞曜","四化","解讀摘要"),
        "en":("Palace","Branch","Main Stars","Supportive Stars","Challenging Stars","Transformations","Summary"),
        "ja":("宮位","地支","主星","吉星","煞星","四化","要約"),
        "th":("วัง","กิ่ง","ดาวหลัก","ดาวสนับสนุน","ดาวท้าทาย","การแปรสภาพ","สรุป"),
        "es":("Palacio","Rama","Estrellas principales","Estrellas de apoyo","Estrellas desafiantes","Transformaciones","Resumen"),
        "ar":("القصر","الفرع","النجوم الرئيسية","نجوم الدعم","النجوم الصعبة","التحولات","الملخص"),
    }.get(language,("Palace","Branch","Main Stars","Supportive Stars","Challenging Stars","Transformations","Summary"))
    palaces=[ziwei_chart.ming_palace,ziwei_chart.brother_palace,ziwei_chart.spouse_palace,ziwei_chart.children_palace,ziwei_chart.wealth_palace,ziwei_chart.health_palace,ziwei_chart.travel_palace,ziwei_chart.friends_palace,ziwei_chart.career_palace,ziwei_chart.property_palace,ziwei_chart.fortune_palace,ziwei_chart.parents_palace]
    star_cat=getattr(ziwei_chart,"star_categories",{}); malefic={s for s,c in star_cat.items() if c=="malefic"}
    rows=[]
    for p in palaces:
        aux=[x for x in p.minor_stars if x not in malefic]; sha=[x for x in p.minor_stars if x in malefic]
        summary = "Technical chart placement; detailed narrative follows the selected report language." if language!="zh-TW" else "依主星、輔煞與四化綜合判讀。"
        rows.append({labels[0]:p.name if language=="zh-TW" else p.name, labels[1]:translate_branch(p.earthly_branch,language), labels[2]:", ".join(p.main_stars) or "—", labels[3]:", ".join(aux) or "—", labels[4]:", ".join(sha) or "—", labels[5]:" / ".join(p.transformations) or "—", labels[6]:summary})
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)


def render_ziwei_auxiliary_table(ziwei_chart, language="zh-TW"):
    import pandas as pd
    labels={"zh-TW":("星曜","類別","所在宮位","地支","解讀方向"),"en":("Star","Category","Palace","Branch","Interpretive focus"),"ja":("星曜","分類","宮位","地支","解釈の焦点"),"th":("ดาว","ประเภท","วัง","กิ่ง","แนวตีความ"),"es":("Estrella","Categoría","Palacio","Rama","Enfoque interpretativo"),"ar":("النجم","الفئة","القصر","الفرع","محور التفسير")}.get(language,("Star","Category","Palace","Branch","Interpretive focus"))
    aux_map=getattr(ziwei_chart,"auxiliary_star_map",{}); mal_map=getattr(ziwei_chart,"malefic_star_map",{})
    all_palaces=[ziwei_chart.ming_palace,ziwei_chart.brother_palace,ziwei_chart.spouse_palace,ziwei_chart.children_palace,ziwei_chart.wealth_palace,ziwei_chart.health_palace,ziwei_chart.travel_palace,ziwei_chart.friends_palace,ziwei_chart.career_palace,ziwei_chart.property_palace,ziwei_chart.fortune_palace,ziwei_chart.parents_palace]
    b2n={p.earthly_branch:p.name for p in all_palaces}; rows=[]
    for star,cat in {**{s:"supportive" for s in aux_map},**{s:"challenging" for s in mal_map}}.items():
        branch=aux_map.get(star) or mal_map.get(star,"—")
        cat_label={"zh-TW":{"supportive":"吉輔","challenging":"煞曜"},"en":{"supportive":"Supportive","challenging":"Challenging"},"ja":{"supportive":"吉星","challenging":"煞星"},"th":{"supportive":"สนับสนุน","challenging":"ท้าทาย"},"es":{"supportive":"Apoyo","challenging":"Desafiante"},"ar":{"supportive":"داعمة","challenging":"صعبة"}}.get(language,{}).get(cat,cat)
        rows.append({labels[0]:star,labels[1]:cat_label,labels[2]:b2n.get(branch,"—"),labels[3]:translate_branch(branch,language),labels[4]:"Chart-specific influence to be interpreted with its palace context." if language!="zh-TW" else "需結合所在宮位與主星判讀。"})
    if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)


def render_daxian_table(ziwei_chart, language="zh-TW"):
    import pandas as pd
    da_xian=getattr(ziwei_chart,"da_xian",[])
    if not da_xian:
        st.caption({"zh-TW":"大限資料尚未計算。","en":"Major-cycle data is unavailable.","ja":"大限データは未計算です。","th":"ยังไม่มีข้อมูลรอบใหญ่","es":"No hay datos de ciclos mayores.","ar":"بيانات الدورات الكبرى غير متاحة."}.get(language,"Major-cycle data is unavailable.")); return
    labels={"zh-TW":("年齡區間","宮位","地支","主星","輔星 / 煞星","解讀"),"en":("Age Range","Palace","Branch","Main Stars","Supportive / Challenging Stars","Interpretation"),"ja":("年齢範囲","宮位","地支","主星","吉星 / 煞星","解釈"),"th":("ช่วงอายุ","วัง","กิ่ง","ดาวหลัก","ดาวสนับสนุน / ท้าทาย","คำอธิบาย"),"es":("Rango de edad","Palacio","Rama","Estrellas principales","Estrellas de apoyo / desafío","Interpretación"),"ar":("الفئة العمرية","القصر","الفرع","النجوم الرئيسية","النجوم الداعمة / الصعبة","التفسير")}.get(language,("Age Range","Palace","Branch","Main Stars","Supportive / Challenging Stars","Interpretation"))
    age_fmt={"zh-TW":"{a}–{b} 歲","en":"{a}–{b}","ja":"{a}～{b}歳","th":"{a}–{b} ปี","es":"{a}–{b} años","ar":"{a}–{b} سنة"}.get(language,"{a}–{b}")
    rows=[]
    for d in da_xian:
        interp=d.interpretation if language=="zh-TW" else "A ten-year focus period; interpret the palace, branch, and stars together rather than as a fixed event prediction."
        rows.append({labels[0]:age_fmt.format(a=d.start_age,b=d.end_age),labels[1]:d.palace_name,labels[2]:translate_branch(d.branch,language),labels[3]:", ".join(d.main_stars) or "—",labels[4]:", ".join(d.auxiliary_stars) or "—",labels[5]:interp})
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)


def render_numerology_card(num_chart, language="zh-TW"):
    labels = {
        "zh-TW": ("生命靈數", "生日數", "天賦數", "個人年"),
        "en": ("Life Path", "Birthday Number", "Talent Number", "Personal Year"),
        "ja": ("ライフパス", "誕生日数", "才能数", "個人年"),
        "th": ("เลขเส้นทางชีวิต", "เลขวันเกิด", "เลขพรสวรรค์", "ปีส่วนบุคคล"),
        "es": ("Camino de Vida", "Número de nacimiento", "Número de talento", "Año personal"),
        "ar": ("مسار الحياة", "رقم الميلاد", "رقم الموهبة", "السنة الشخصية"),
    }.get(language, ("Life Path", "Birthday Number", "Talent Number", "Personal Year"))
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(labels[0], num_chart.life_path_number)
    with col2:
        st.metric(labels[1], num_chart.birthday_number)
    with col3:
        st.metric(labels[2], num_chart.talent_number)
    with col4:
        st.metric(labels[3], num_chart.personal_year)


def _localized_synthesis_bodies(report, language: str):
    """Create safe, factual multilingual summaries from canonical chart data.

    These summaries do not alter the calculation model and avoid leaking the
    Traditional-Chinese narrative engine into another UI language.
    """
    wc = getattr(report, "western_chart", None) if report is not None else None
    bc = getattr(report, "bazi_chart", None) if report is not None else None
    zc = getattr(report, "ziwei_chart", None) if report is not None else None
    nc = getattr(report, "numerology_chart", None) if report is not None else None
    hd = getattr(report, "human_design_chart", None) if report is not None else None

    sun = moon = asc = "—"
    if wc:
        for pp in getattr(wc, "planet_positions", []) or []:
            if pp.planet.value == "太陽":
                sun = translate_zodiac(normalize_zodiac_value(pp.sign.value), language)
            elif pp.planet.value == "月亮":
                moon = translate_zodiac(normalize_zodiac_value(pp.sign.value), language)
        if getattr(wc, "ascendant_accuracy", "") == "precise":
            asc = translate_zodiac(normalize_zodiac_value(wc.ascendant.value), language)
    day_master = translate_bazi_stem(getattr(getattr(bc, "day_master", None), "value", "—"), language) if bc else "—"
    fav = ", ".join(translate_element(getattr(x, "value", str(x)), language) for x in (getattr(bc, "favorable_elements", []) or [])) if bc else "—"
    life_path = getattr(nc, "life_path_number", "—") if nc else "—"
    hd_type = translate_hd_type(getattr(hd, "type_name", getattr(hd, "type_name_zh", "—")), language) if hd else "—"

    data = {"sun": sun, "moon": moon, "asc": asc, "day_master": day_master, "fav": fav or "—", "life_path": life_path, "hd_type": hd_type}
    templates = {
        "en": [
            "Your chart combines Sun {sun}, Moon {moon}, and Ascendant {asc}. The BaZi Day Master is {day_master}, the Life Path number is {life_path}, and the Human Design Type is {hd_type}. Use these as complementary perspectives rather than fixed judgments.",
            "The Moon placement ({moon}) describes emotional needs, while the Day Master ({day_master}) adds an elemental view of how energy is processed. Observe which patterns are consistent in daily life.",
            "Relationship themes are best understood by combining emotional needs, communication style, timing, and personal boundaries. The chart is a reflection tool, not a guarantee of outcomes.",
            "Career direction is supported by recurring strengths across the chart. Favorable BaZi elements: {fav}. Choose environments where these strengths can be practiced sustainably.",
            "Wealth patterns reflect decision style, risk tolerance, and resource habits. Treat chart indicators as prompts for reflection, not financial advice.",
            "Social patterns combine the visible Ascendant ({asc}) with deeper emotional and decision-making tendencies. Notice where you adapt too much or withdraw too quickly.",
            "Family themes often show where security, duty, and belonging intersect. Use the chart to identify patterns that can be discussed rather than assumed.",
            "Shadow themes are usually overused strengths or protective habits. Awareness creates more choice; it does not label any trait as permanently negative.",
            "Talents emerge where several systems point in the same direction. Life Path {life_path} and Human Design Type {hd_type} offer two practical lenses for observing these abilities.",
            "Apply one insight at a time, record what changes, and keep decisions grounded in real-world evidence and personal responsibility.",
        ],
        "ja": [
            "太陽は{sun}、月は{moon}、アセンダントは{asc}です。八字の日主は{day_master}、ライフパスは{life_path}、Human Design Type は{hd_type}です。固定的な運命判断ではなく、複数の視点として活用してください。",
            "月（{moon}）は感情的な安心感を、日主（{day_master}）はエネルギー処理の傾向を示します。日常で一貫して現れるパターンを観察しましょう。",
            "関係性は感情ニーズ、対話、タイミング、境界線を組み合わせて考えると理解しやすくなります。結果を保証するものではありません。",
            "仕事では複数の体系で繰り返し示される強みを重視します。八字の有利な五行は{fav}です。継続可能な環境を選びましょう。",
            "財運は意思決定、リスク許容度、資源管理の傾向を考えるための参考です。投資助言ではありません。",
            "対人面ではアセンダント（{asc}）と内面的な感情・判断傾向の両方を観察します。過度な適応や早すぎる撤退に気づくことが大切です。",
            "家庭テーマでは安心感、責任、所属感が交差します。推測ではなく対話のきっかけとして使ってください。",
            "影の課題は、強みの使い過ぎや防衛反応として現れることがあります。気づきは選択肢を増やします。",
            "才能は複数の体系が同じ方向を示す部分に表れやすいです。ライフパス{life_path}とType {hd_type}を実生活で検証してください。",
            "一度に一つの示唆を試し、変化を記録し、現実の情報と自己責任を基準に判断してください。",
        ],
        "th": [
            "ดวงนี้ประกอบด้วยดวงอาทิตย์ {sun} ดวงจันทร์ {moon} และลัคนา {asc} Day Master คือ {day_master} เลขเส้นทางชีวิต {life_path} และ Human Design Type คือ {hd_type} ควรใช้เป็นมุมมองประกอบ ไม่ใช่คำตัดสินตายตัว",
            "ดวงจันทร์ ({moon}) สะท้อนความต้องการทางอารมณ์ ส่วน Day Master ({day_master}) ช่วยอธิบายรูปแบบการใช้พลังงาน ควรสังเกตสิ่งที่เกิดซ้ำในชีวิตจริง",
            "ความสัมพันธ์ควรพิจารณาความต้องการทางอารมณ์ การสื่อสาร จังหวะเวลา และขอบเขตส่วนตัวร่วมกัน ผลลัพธ์ไม่ได้รับการรับประกัน",
            "ทิศทางงานควรดูจุดแข็งที่ปรากฏซ้ำ ธาตุที่ส่งเสริมใน BaZi คือ {fav} เลือกสภาพแวดล้อมที่ทำให้จุดแข็งเติบโตได้อย่างยั่งยืน",
            "รูปแบบการเงินสะท้อนวิธีตัดสินใจ ความเสี่ยง และนิสัยการใช้ทรัพยากร ไม่ใช่คำแนะนำการลงทุน",
            "ด้านสังคมให้ดูทั้งลัคนา ({asc}) และแนวโน้มภายใน สังเกตว่าคุณปรับตัวมากเกินไปหรือถอยเร็วเกินไปหรือไม่",
            "เรื่องครอบครัวเกี่ยวข้องกับความมั่นคง หน้าที่ และความรู้สึกเป็นส่วนหนึ่ง ใช้เป็นจุดเริ่มต้นของการพูดคุย",
            "เงาหรือความท้าทายมักเป็นจุดแข็งที่ใช้มากเกินไปหรือกลไกป้องกันตนเอง การตระหนักรู้ช่วยเพิ่มทางเลือก",
            "พรสวรรค์มักชัดเมื่อหลายระบบชี้ไปในทิศทางเดียวกัน ลองสังเกตเลขเส้นทางชีวิต {life_path} และ Type {hd_type} ในชีวิตจริง",
            "ทดลองใช้ข้อสังเกตทีละข้อ บันทึกผล และยึดข้อมูลจริงกับความรับผิดชอบส่วนบุคคลเป็นหลัก",
        ],
        "es": [
            "La carta combina Sol en {sun}, Luna en {moon} y Ascendente en {asc}. El Maestro del Día es {day_master}, el Camino de Vida es {life_path} y el Tipo de Human Design es {hd_type}. Úsalos como perspectivas complementarias, no como juicios fijos.",
            "La Luna ({moon}) describe necesidades emocionales y el Maestro del Día ({day_master}) aporta una visión elemental. Observa qué patrones se repiten en la vida diaria.",
            "Las relaciones se comprenden mejor al combinar necesidades emocionales, comunicación, tiempos y límites personales. No garantiza resultados.",
            "La dirección profesional se apoya en fortalezas recurrentes. Elementos favorables de BaZi: {fav}. Busca entornos sostenibles para desarrollarlas.",
            "Los patrones financieros reflejan decisiones, tolerancia al riesgo y hábitos de recursos. No constituyen asesoramiento financiero.",
            "La vida social combina el Ascendente ({asc}) con tendencias emocionales y de decisión. Observa la sobreadaptación o el retiro prematuro.",
            "Los temas familiares muestran cómo se cruzan seguridad, deber y pertenencia. Úsalos para conversar, no para asumir.",
            "Las sombras suelen ser fortalezas usadas en exceso o hábitos protectores. La conciencia amplía las opciones.",
            "Los talentos aparecen donde varios sistemas coinciden. El Camino de Vida {life_path} y el Tipo {hd_type} son lentes prácticos para observarlos.",
            "Aplica una idea cada vez, registra los cambios y mantén las decisiones ancladas en evidencia real y responsabilidad personal.",
        ],
        "ar": [
            "تجمع الخريطة بين الشمس في {sun} والقمر في {moon} والطالع {asc}. سيد اليوم هو {day_master} ورقم مسار الحياة {life_path} ونوع Human Design هو {hd_type}. استخدمها كوجهات نظر متكاملة لا كأحكام ثابتة.",
            "يعكس القمر ({moon}) الاحتياجات العاطفية، بينما يضيف سيد اليوم ({day_master}) منظورًا عن معالجة الطاقة. راقب الأنماط المتكررة في الحياة اليومية.",
            "تُفهم العلاقات بصورة أفضل عند جمع الاحتياجات العاطفية والتواصل والتوقيت والحدود الشخصية. لا تضمن الخريطة نتيجة محددة.",
            "يتضح المسار المهني من نقاط القوة المتكررة. العناصر الداعمة في BaZi هي {fav}. اختر بيئة تسمح بتنمية هذه القدرات بصورة مستدامة.",
            "تعكس أنماط المال أسلوب القرار وتحمل المخاطر وعادات إدارة الموارد. وهي ليست نصيحة مالية.",
            "تجمع الحياة الاجتماعية بين الطالع ({asc}) والميول الداخلية. لاحظ الإفراط في التكيف أو الانسحاب السريع.",
            "تتعلق موضوعات الأسرة بالأمان والمسؤولية والانتماء. استخدمها كبداية للحوار لا كافتراضات نهائية.",
            "غالبًا ما تكون موضوعات الظل نقاط قوة أُفرط في استخدامها أو عادات دفاعية. الوعي يوسّع مساحة الاختيار.",
            "تظهر المواهب حين تشير عدة أنظمة إلى الاتجاه نفسه. راقب مسار الحياة {life_path} ونوع {hd_type} في الواقع.",
            "طبّق ملاحظة واحدة في كل مرة، وسجّل النتائج، واجعل القرارات قائمة على الواقع والمسؤولية الشخصية.",
        ],
    }
    chosen = templates.get(language, templates["en"])
    return [text.format(**data) for text in chosen]


# Compatibility marker retained for regression coverage: report_preview.original_language
def render_synthesis_section(synthesis, language="zh-TW", report=None):
    """Render synthesis tabs in the requested language.

    Traditional Chinese keeps the original long-form engine output. Other
    languages receive factual structured summaries generated from canonical
    chart values, so the page remains useful without mixed-language leakage.
    """
    keys = [
        "report.section.core_personality", "report.section.emotion_action",
        "report.section.relationship", "report.section.career",
        "report.section.wealth", "report.section.social",
        "report.section.family", "report.section.shadow",
        "report.section.talent", "report.section.advice",
    ]
    labels = [t(k, language=language, default=k) for k in keys]
    tabs = st.tabs(labels)
    if language != "zh-TW":
        try:
            from reports.localized_renderer import localized_section_bodies
            bodies = localized_section_bodies(report, language)
        except Exception:
            bodies = _localized_synthesis_bodies(report, language)
        for tab, body in zip(tabs, bodies):
            with tab:
                st.markdown(body)
        return
    with tabs[0]:
        st.markdown(synthesis.core_personality)
    with tabs[1]:
        st.markdown("**情緒模式**\n\n" + synthesis.emotional_pattern)
        st.markdown("---")
        st.markdown("**行動模式**\n\n" + synthesis.action_pattern)
    with tabs[2]: st.markdown(synthesis.love_pattern)
    with tabs[3]:
        st.markdown(synthesis.career_pattern)
        if synthesis.suitable_careers:
            st.markdown("**建議職業方向**：" + "、".join(synthesis.suitable_careers))
    with tabs[4]: st.markdown(synthesis.wealth_pattern)
    with tabs[5]: st.markdown(synthesis.social_pattern)
    with tabs[6]: st.markdown(synthesis.family_security)
    with tabs[7]:
        st.markdown(synthesis.stress_shadow)
        st.markdown(synthesis.life_lessons)
        if synthesis.contradictions:
            st.warning("**內在矛盾點**")
            for c in synthesis.contradictions: st.write(f"• {c}")
            st.info("**整合建議**")
            for item in synthesis.integration_suggestions: st.write(f"• {item}")
    with tabs[8]:
        st.markdown(synthesis.innate_gifts)
        st.markdown("**容易反覆出現的問題**\n\n" + synthesis.recurring_challenges)
    with tabs[9]:
        st.markdown("**今年流年重點**\n\n" + synthesis.one_year_advice)
        st.markdown("---")
        st.markdown("**未來三年趨勢**\n\n" + synthesis.three_year_advice)


