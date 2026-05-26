"""
Astro Destiny Analyzer — Report Templates
Jinja2 templates for Short, Standard, and Full (萬字) reports.
"""
from jinja2 import Environment, BaseLoader

# ── Shared macros ─────────────────────────────────────────────────────────────

_MACROS = """
{%- macro section(title, body) %}
## {{ title }}

{{ body }}
{% endmacro -%}

{%- macro subsection(title, body) %}
### {{ title }}

{{ body }}
{% endmacro -%}
"""

# ── Short report (~800 words) ─────────────────────────────────────────────────

TEMPLATE_SHORT = _MACROS + """
# {{ report.profile.name }} 命盤摘要報告

> **免責聲明**：{{ disclaimer }}

---

## 基本資料

| 項目 | 內容 |
|------|------|
| 姓名 | {{ report.profile.name }} |
| 出生日期 | {{ report.profile.birth_date }} |
| 出生地 | {{ report.profile.birth_city }}，{{ report.profile.birth_country }} |
| 血型 | {{ report.profile.blood_type.value }} |

---

{% if report.synthesis %}
{{ section("核心人格速覽", report.synthesis.core_personality) }}
{{ section("感情模式", report.synthesis.love_pattern) }}
{{ section("事業方向", report.synthesis.career_pattern) }}
{{ section("今年重點建議", report.synthesis.one_year_advice) }}
{% endif %}

{% if report.bazi_chart %}
{{ section("八字日主", report.bazi_chart.day_master.value ~ "（" ~ report.bazi_chart.day_master_element.value ~ "）") }}
{% endif %}

{% if report.western_chart %}
{{ section("太陽星座", (report.western_chart.planet_positions | selectattr("planet.value", "equalto", "太陽") | list | first).sign.value ~ "（上升：" ~ report.western_chart.ascendant.value ~ "）") }}
{% endif %}

{% if report.numerology_chart %}
{{ section("生命靈數", report.numerology_chart.life_path_number | string ~ " — " ~ report.numerology_chart.life_path_description[:80] ~ "…") }}
{% endif %}

---
*本報告由 Astro Destiny Analyzer 自動生成，僅供娛樂與自我探索。*
"""

# ── Standard report (~3000 words) ────────────────────────────────────────────

TEMPLATE_STANDARD = _MACROS + """
# {{ report.profile.name }} 命盤整合分析報告

> **免責聲明**：{{ disclaimer }}

---

## 一、基本資料

| 項目 | 內容 |
|------|------|
| 姓名 | {{ report.profile.name }} |
| 性別 | {{ report.profile.gender.value if report.profile.gender else "未填寫" }} |
| 出生日期 | {{ report.profile.birth_date }} |
| 出生時間 | {{ report.profile.birth_time if report.profile.birth_time else "未知" }} |
| 出生地 | {{ report.profile.birth_city }}，{{ report.profile.birth_country }} |
| 血型 | {{ report.profile.blood_type.value }} |
| 分析主題 | {{ report.profile.themes | map(attribute='value') | join('、') if report.profile.themes else "全方位" }} |

---

{% if report.synthesis %}
{{ section("二、核心人格總論", report.synthesis.core_personality) }}
{{ section("三、情緒與行動模式", report.synthesis.emotional_pattern ~ "\n\n" ~ report.synthesis.action_pattern) }}
{{ section("四、感情與親密關係", report.synthesis.love_pattern) }}
{{ section("五、事業與職涯方向", report.synthesis.career_pattern) }}
{% if report.synthesis.suitable_careers %}
**建議職業方向：** {{ report.synthesis.suitable_careers | join('、') }}
{% endif %}
{{ section("六、財富與資源管理", report.synthesis.wealth_pattern) }}
{{ section("七、人際關係模式", report.synthesis.social_pattern) }}
{{ section("八、家庭與安全感", report.synthesis.family_security) }}
{{ section("九、壓力、陰影與人生課題", report.synthesis.stress_shadow ~ "\n\n" ~ report.synthesis.life_lessons) }}
{{ section("十、天賦與優勢", report.synthesis.innate_gifts) }}
{% if report.synthesis.contradictions %}
{{ section("十一、內在矛盾點與整合建議", "") }}
{% for c in report.synthesis.contradictions %}
- {{ c }}
{% endfor %}
{% for s in report.synthesis.integration_suggestions %}
- **整合**：{{ s }}
{% endfor %}
{% endif %}
{{ section("十二、今年流年重點", report.synthesis.one_year_advice) }}
{{ section("十三、未來三年趨勢", report.synthesis.three_year_advice) }}
{% endif %}

{% if report.bazi_chart %}
---
{{ section("附錄 A：八字四柱", "") }}
| 柱 | 天干 | 地支 | 五行 |
|----|------|------|------|
| 年柱 | {{ report.bazi_chart.year_pillar.heavenly_stem.value }} | {{ report.bazi_chart.year_pillar.earthly_branch.value }} | {{ report.bazi_chart.year_pillar.element.value }} |
| 月柱 | {{ report.bazi_chart.month_pillar.heavenly_stem.value }} | {{ report.bazi_chart.month_pillar.earthly_branch.value }} | {{ report.bazi_chart.month_pillar.element.value }} |
| 日柱 | {{ report.bazi_chart.day_pillar.heavenly_stem.value }} | {{ report.bazi_chart.day_pillar.earthly_branch.value }} | {{ report.bazi_chart.day_pillar.element.value }} |
| 時柱 | {{ report.bazi_chart.hour_pillar.heavenly_stem.value if report.bazi_chart.hour_pillar else "─" }} | {{ report.bazi_chart.hour_pillar.earthly_branch.value if report.bazi_chart.hour_pillar else "─" }} | {{ report.bazi_chart.hour_pillar.element.value if report.bazi_chart.hour_pillar else "─" }} |

**日主**：{{ report.bazi_chart.day_master.value }}（{{ report.bazi_chart.day_master_element.value }}）

**五行比例**：
{% for elem, pct in report.bazi_chart.five_element_ratio.items() %}
- {{ elem }}：{{ pct }}%（{{ report.bazi_chart.five_element_strength[elem] }}）
{% endfor %}
{% endif %}

---
*本報告由 Astro Destiny Analyzer v{{ version }} 自動生成，僅供娛樂與自我探索。*
"""

# ── Full (萬字完整版) report ───────────────────────────────────────────────────

TEMPLATE_FULL = _MACROS + """
# {{ report.profile.name }} 萬字命盤整合完整分析報告

---

## 封面

**姓名**：{{ report.profile.name }}
**出生日期**：{{ report.profile.birth_date }}
**出生地**：{{ report.profile.birth_city }}，{{ report.profile.birth_country }}
**報告生成時間**：{{ report.created_at }}
**版本**：Astro Destiny Analyzer v{{ version }}

---

## 免責聲明

{{ disclaimer }}

本報告整合西洋占星、八字、紫微斗數、血型分析與生命靈數五套系統，
目的是為您提供一個多角度的自我探索地圖。每個系統都有其文化背景與內在邏輯；
不同系統的結論有時會相互印證，有時也會出現差異——這種差異本身就是值得深思的線索。
請以開放、探索的心態閱讀，最終的詮釋與選擇始終屬於您自己。

---

## 一頁式總覽

{% if report.western_chart and report.bazi_chart and report.numerology_chart %}
| 系統 | 核心標籤 |
|------|---------|
| 西洋占星 | 太陽 {{ (report.western_chart.planet_positions | selectattr("planet.value", "equalto", "太陽") | list | first).sign.value }}／上升 {{ report.western_chart.ascendant.value }}／月亮 {{ (report.western_chart.planet_positions | selectattr("planet.value", "equalto", "月亮") | list | first).sign.value }} |
| 八字 | 日主 {{ report.bazi_chart.day_master.value }}（{{ report.bazi_chart.day_master_element.value }}）喜{{ report.bazi_chart.favorable_elements | map(attribute='value') | join('、') }} |
| 紫微斗數 | 命宮 {{ report.ziwei_chart.ming_palace.earthly_branch if report.ziwei_chart else "─" }}宮，主星 {{ report.ziwei_chart.ming_palace.main_stars | join('、') if report.ziwei_chart and report.ziwei_chart.ming_palace.main_stars else "─" }} |
| 生命靈數 | {{ report.numerology_chart.life_path_number }} 號 |
| 血型 | {{ report.profile.blood_type.value }} 型 |
{% endif %}

---

{% if report.synthesis %}
## 核心人格總論

{{ report.synthesis.core_personality }}

---

## 情緒模式

{{ report.synthesis.emotional_pattern }}

---

## 行動模式

{{ report.synthesis.action_pattern }}

---
{% endif %}

{% if report.western_chart %}
## 西洋占星分析

### 太陽／月亮／上升三核心

{% set sun_pos = report.western_chart.planet_positions | selectattr("planet.value", "equalto", "太陽") | list | first %}
{% set moon_pos = report.western_chart.planet_positions | selectattr("planet.value", "equalto", "月亮") | list | first %}

**太陽星座**：{{ sun_pos.sign.value }}（第 {{ sun_pos.house }} 宮，{{ sun_pos.sign_degree | round(1) }}°）

太陽代表你的核心自我、生命力的流向，以及你在一生中渴望展現的本質。太陽所在星座決定了你最本能的行事風格與人生主旋律。

**月亮星座**：{{ moon_pos.sign.value }}（第 {{ moon_pos.house }} 宮）

月亮揭示你的情緒底層、潛意識需求，以及你在私下最真實的樣貌。月亮所在星座是你的情感語言，也是你在親密關係中最渴望被理解的部分。

**上升星座**：{{ report.western_chart.ascendant.value }}

上升代表你的「外殼」與第一印象，是你在世界舞台上呈現的面貌。它決定了你的身體外形傾向、初次見面時給他人的感受，以及你應對外部世界的本能方式。

---

### 個人行星分析：水星、金星、火星

{% for planet_name in ["水星", "金星", "火星"] %}
{% set pos = report.western_chart.planet_positions | selectattr("planet.value", "equalto", planet_name) | list | first %}
{% if pos %}
**{{ planet_name }}**：{{ pos.sign.value }}，第 {{ pos.house }} 宮{{ "（逆行）" if pos.retrograde else "" }}

{% if planet_name == "水星" %}水星代表你的思維模式、溝通方式與學習風格。水星所在星座影響你傾向於如何處理資訊、表達想法，以及你的神經系統偏好如何運作。{% endif %}
{% if planet_name == "金星" %}金星代表你的愛情語言、美感標準，以及你在關係中吸引他人的方式。金星揭示了你對美、享樂與人際親密的渴望模式。{% endif %}
{% if planet_name == "火星" %}火星代表你的行動驅力、欲望能量與面對挑戰的方式。火星揭示了你如何追求目標、表達憤怒，以及你在競爭與衝突中的本能反應。{% endif %}
{% endif %}
{% endfor %}

---

### 社會行星分析：木星、土星

{% for planet_name in ["木星", "土星"] %}
{% set pos = report.western_chart.planet_positions | selectattr("planet.value", "equalto", planet_name) | list | first %}
{% if pos %}
**{{ planet_name }}**：{{ pos.sign.value }}，第 {{ pos.house }} 宮{{ "（逆行）" if pos.retrograde else "" }}

{% if planet_name == "木星" %}木星代表你的擴展方向、幸運領域與信仰系統。木星所在之處，是你在一生中容易獲得眷顧、資源豐沛的主題領域。{% endif %}
{% if planet_name == "土星" %}土星代表你人生中最需要磨練的功課、自律與責任。土星不是懲罰，而是在這個領域要求你付出扎實努力，以換取長遠的精熟與成就。{% endif %}
{% endif %}
{% endfor %}

---

### 世代行星分析：天王、海王、冥王

{% for planet_name in ["天王星", "海王星", "冥王星"] %}
{% set pos = report.western_chart.planet_positions | selectattr("planet.value", "equalto", planet_name) | list | first %}
{% if pos %}
**{{ planet_name }}**：{{ pos.sign.value }}，第 {{ pos.house }} 宮{{ "（逆行）" if pos.retrograde else "" }}

{% if planet_name == "天王星" %}天王星代表你所屬世代追求的突破與革新方向，同時在個人命盤中揭示你渴望自由、打破常規的領域。{% endif %}
{% if planet_name == "海王星" %}海王星代表你所屬世代的集體夢境與靈性傾向，在個人命盤中揭示你容易理想化、超脫或迷幻的人生領域。{% endif %}
{% if planet_name == "冥王星" %}冥王星代表你所屬世代的深層轉化力量，在個人命盤中揭示你需要面對死亡與重生、摧毀與重建的人生課題。{% endif %}
{% endif %}
{% endfor %}

---

### 宮位分析

{% for house in report.western_chart.houses %}
**第 {{ house.house_number }} 宮**（{{ house.sign.value }}，{{ house.cusp_degree | round(1) }}°）
{% if house.planets %}入宮行星：{{ house.planets | map(attribute='value') | join('、') }}{% endif %}

{% endfor %}

---

### 主要相位分析

{% for aspect in report.western_chart.aspects[:15] %}
- **{{ aspect.planet1.value }} {{ aspect.aspect_type.value }} {{ aspect.planet2.value }}**（容許度 {{ aspect.orb | round(2) }}°）
{% endfor %}

---
{% endif %}

{% if report.bazi_chart %}
## 八字四柱分析

### 四柱命盤

| 柱 | 天干 | 地支 | 天干五行 |
|----|------|------|----------|
| 年柱 | {{ report.bazi_chart.year_pillar.heavenly_stem.value }} | {{ report.bazi_chart.year_pillar.earthly_branch.value }} | {{ report.bazi_chart.year_pillar.element.value }} |
| 月柱 | {{ report.bazi_chart.month_pillar.heavenly_stem.value }} | {{ report.bazi_chart.month_pillar.earthly_branch.value }} | {{ report.bazi_chart.month_pillar.element.value }} |
| 日柱 | {{ report.bazi_chart.day_pillar.heavenly_stem.value }} | {{ report.bazi_chart.day_pillar.earthly_branch.value }} | {{ report.bazi_chart.day_pillar.element.value }} |
| 時柱 | {{ report.bazi_chart.hour_pillar.heavenly_stem.value if report.bazi_chart.hour_pillar else "─" }} | {{ report.bazi_chart.hour_pillar.earthly_branch.value if report.bazi_chart.hour_pillar else "─" }} | {{ report.bazi_chart.hour_pillar.element.value if report.bazi_chart.hour_pillar else "─" }} |

---

### 五行強弱分析

| 五行 | 比例 | 強弱 |
|------|------|------|
{% for elem, pct in report.bazi_chart.five_element_ratio.items() %}
| {{ elem }} | {{ pct }}% | {{ report.bazi_chart.five_element_strength[elem] }} |
{% endfor %}

五行是宇宙能量的五種基本形態，在八字命盤中的比例反映了你先天的能量底色。
強旺的五行代表你的天賦力量，同時也可能成為過度的來源；
弱缺的五行則是你需要透過後天環境與習慣加以補強的方向。

---

### 十神分析

日主 **{{ report.bazi_chart.day_master.value }}**（{{ report.bazi_chart.day_master_element.value }}）

| 天干 | 十神關係 |
|------|----------|
{% for stem_val, tg_val in report.bazi_chart.ten_gods_map.items() %}
| {{ stem_val }} | {{ tg_val }} |
{% endfor %}

---

### 喜用神與忌神

**喜用神**（扶助日主、帶來順境）：{{ report.bazi_chart.favorable_elements | map(attribute='value') | join('、') }}

**忌神**（耗洩日主、帶來阻力）：{{ report.bazi_chart.unfavorable_elements | map(attribute='value') | join('、') }}

喜用神是你的「能量充電板」——當你的生活環境、工作性質、人際關係的五行屬性符合喜用神時，你會感到如魚得水、事半功倍。
忌神則相反，在忌神旺盛的流年需要特別謹慎，避免重大決策或高風險行動。

---

### 大運（十年運程）

| 大運 | 起始年齡 | 天干地支 |
|------|----------|----------|
{% for dy in report.bazi_chart.da_yun %}
| {{ loop.index }} | {{ dy.start_age }}–{{ dy.end_age }} 歲 | {{ dy.stem.value }}{{ dy.branch.value }} |
{% endfor %}

---

### 流年（近十年）

| 年份 | 天干地支 |
|------|----------|
{% for ly in report.bazi_chart.liu_nian %}
| {{ ly.year }} | {{ ly.stem.value }}{{ ly.branch.value }} |
{% endfor %}

---
{% endif %}

{% if report.ziwei_chart %}
## 紫微斗數命盤分析

### 命宮分析

宮位：{{ report.ziwei_chart.ming_palace.earthly_branch }}宮
主星：{{ report.ziwei_chart.ming_palace.main_stars | join('、') if report.ziwei_chart.ming_palace.main_stars else "無主星" }}
輔星：{{ report.ziwei_chart.ming_palace.minor_stars | join('、') if report.ziwei_chart.ming_palace.minor_stars else "無" }}
四化：{{ report.ziwei_chart.ming_palace.transformations | join('、') if report.ziwei_chart.ming_palace.transformations else "無" }}

{{ report.ziwei_chart.ming_palace.interpretation }}

---

### 十二宮完整分析

{% for palace in [
    report.ziwei_chart.ming_palace,
    report.ziwei_chart.brother_palace,
    report.ziwei_chart.spouse_palace,
    report.ziwei_chart.children_palace,
    report.ziwei_chart.wealth_palace,
    report.ziwei_chart.health_palace,
    report.ziwei_chart.travel_palace,
    report.ziwei_chart.friends_palace,
    report.ziwei_chart.career_palace,
    report.ziwei_chart.property_palace,
    report.ziwei_chart.fortune_palace,
    report.ziwei_chart.parents_palace,
] %}
#### {{ palace.name }}（{{ palace.earthly_branch }}宮）

主星：{{ palace.main_stars | join('、') if palace.main_stars else "無主星" }}
輔星：{{ palace.minor_stars | join('、') if palace.minor_stars else "無" }}
四化：{{ palace.transformations | join('、') if palace.transformations else "無" }}

{{ palace.interpretation }}

{% endfor %}

---

### 四化分析

| 星曜 | 四化 |
|------|------|
{% for star, transform in report.ziwei_chart.four_transformations.items() %}
| {{ star }} | {{ transform }} |
{% endfor %}

四化是流動的命運之鑰：化祿帶來豐盛、化權帶來掌控力、化科帶來名聲智慧、化忌帶來考驗。
當四化落入不同宮位，決定了人生哪些領域在特定時期成為主要舞台。

---
{% endif %}

{% if report.blood_type_analysis %}
## 血型輔助分析

*血型分析作為命盤主結論的補充，不取代占星與八字的核心詮釋。*

**血型**：{{ report.profile.blood_type.value }}

**人際風格**：{{ report.blood_type_analysis.interpersonal_style }}

**感情反應**：{{ report.blood_type_analysis.love_response }}

**壓力反應**：{{ report.blood_type_analysis.stress_response }}

**職場合作**：{{ report.blood_type_analysis.workplace_cooperation }}

**金錢態度**：{{ report.blood_type_analysis.money_attitude }}

---
{% endif %}

{% if report.numerology_chart %}
## 生命靈數分析

### 生命靈數 {{ report.numerology_chart.life_path_number }}

{{ report.numerology_chart.life_path_description }}

---

### 生日數 {{ report.numerology_chart.birthday_number }}

{{ report.numerology_chart.birthday_description }}

---

### 天賦數 {{ report.numerology_chart.talent_number }}

{{ report.numerology_chart.talent_description }}

---

### 個人年數 {{ report.numerology_chart.personal_year }}

{{ report.numerology_chart.personal_year_description }}

---
{% endif %}

{% if report.synthesis %}
## 感情與親密關係

{{ report.synthesis.love_pattern }}

---

## 事業與職涯方向

{{ report.synthesis.career_pattern }}

{% if report.synthesis.suitable_careers %}
**建議職業方向**：
{% for career in report.synthesis.suitable_careers %}
- {{ career }}
{% endfor %}
{% endif %}

---

## 財富與資源管理

{{ report.synthesis.wealth_pattern }}

---

## 人際關係與貴人小人

{{ report.synthesis.social_pattern }}

---

## 家庭、安全感與內在需求

{{ report.synthesis.family_security }}

---

## 壓力、陰影與人生課題

{{ report.synthesis.stress_shadow }}

{{ report.synthesis.life_lessons }}

---

## 天賦與優勢

{{ report.synthesis.innate_gifts }}

---

## 容易反覆出現的問題

{{ report.synthesis.recurring_challenges }}

---

## 今年流年重點

{{ report.synthesis.one_year_advice }}

---

## 未來三年趨勢

{{ report.synthesis.three_year_advice }}

---

## 具體行動建議

基於以上各系統的整合分析，以下是針對你目前人生階段的具體可執行建議：

{% if report.bazi_chart %}
1. **能量校準**：你的喜用神為 {{ report.bazi_chart.favorable_elements | map(attribute='value') | join('、') }}，在日常生活中有意識地引入這些元素——包括居家環境的顏色、食物選擇（如木對應綠色蔬菜、水對應黑色食物）、以及工作性質的選擇。
{% endif %}

{% if report.synthesis.suitable_careers %}
2. **職業方向**：建議探索 {{ report.synthesis.suitable_careers[:3] | join('、') }} 等方向，這些領域與你的天生能量最為契合。
{% endif %}

{% if report.synthesis.suitable_love_styles %}
3. **感情策略**：在伴侶選擇上，注意尋找{{ report.synthesis.suitable_love_styles | join('、') }}的特質。
{% endif %}

4. **個人成長**：{{ report.synthesis.life_lessons[:200] if report.synthesis.life_lessons else "持續深化自我認知，是這份報告最重要的實踐方向。" }}

{% if report.synthesis.contradictions %}
5. **整合矛盾**：你的命盤中存在以下需要整合的內在矛盾，面對而非迴避它們，是真正成長的路徑。
{% for s in report.synthesis.integration_suggestions %}
   - {{ s }}
{% endfor %}
{% endif %}

---

## 總結

{{ report.profile.name }}，你的命盤是一張獨一無二的人生地圖。
這份報告試圖從五個不同的視角為你勾勒出這張地圖的輪廓。
沒有任何一個系統能夠完整地定義你，真正的你永遠比任何命盤更豐富、更複雜。

命盤告訴你的，是你帶著什麼樣的天賦和課題來到這個世界；
而你如何運用這些天賦、如何面對這些課題，始終是你自己的選擇與創造。

願這份報告成為你自我探索旅途中的一盞燈，而非一個框架。

{% endif %}

---
*本報告由 Astro Destiny Analyzer v{{ version }} 自動生成。*
*{{ report.created_at }}*
"""


def get_template(length: str) -> str:
    """Return the Jinja2 template string for the given report length."""
    if length == "簡短版":
        return TEMPLATE_SHORT
    elif length == "萬字完整版":
        return TEMPLATE_FULL
    else:
        return TEMPLATE_STANDARD


def render_report(report, version: str = "1.0.0", disclaimer: str = "") -> str:
    """Render a FullReport object to a Markdown string."""
    from config import DISCLAIMER_ZH
    if not disclaimer:
        disclaimer = DISCLAIMER_ZH.strip()

    template_str = get_template(report.profile.report_length.value)
    env = Environment(loader=BaseLoader())
    tmpl = env.from_string(template_str)
    return tmpl.render(report=report, version=version, disclaimer=disclaimer)
