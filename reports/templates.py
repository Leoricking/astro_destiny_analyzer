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

{% if report.human_design_chart %}
{% set hd = report.human_design_chart %}
{{ section("人類圖速覽", "**類型**：" ~ hd.type_name ~ "（" ~ hd.type_name_zh ~ "）\n\n**策略**：" ~ hd.strategy ~ "\n\n**角色**：" ~ hd.profile) }}
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

{% if report.human_design_chart %}
{% set hd = report.human_design_chart %}
{{ section("人類圖 Human Design 摘要", "") }}
| 項目 | 內容 |
|------|------|
| 類型 Type | {{ hd.type_name }}（{{ hd.type_name_zh }}） |
| 策略 Strategy | {{ hd.strategy }} |
| 內在權威 Authority | {{ hd.authority[:60] }}… |
| 人生角色 Profile | {{ hd.profile }} |
| 計算模式 | {{ hd.calculation_mode }} |

> 人類圖需要精確出生時間，僅供自我探索參考，不代表絕對命運。
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

### 一、排盤狀態說明

{% set zmode = report.ziwei_chart.calculation_mode %}
{% if zmode == "formal_layout_phase1" %}
本版紫微斗數為 **V1.5 第一階段正式排盤**（formal_layout_phase1）。

已正式完成：
- 農曆日期轉換
- 命宮 / 身宮精確定位
- 五行局計算
- 十四主星安置
- 生年四化安置

尚未完成（後續版本）：
- 輔星與煞星
- 大限 / 流年 / 流月
- 宮干四化
- 廟旺陷流派細節

> **重要說明**：V1.5 的紫微分析適合作為人格主軸與宮位架構的參考，不適合做完整流年斷事。
{% elif zmode == "partial_lunar_only" %}
本次排盤為 **部分農曆模式**（partial_lunar_only）：農曆轉換成功，但出生時辰未知，命宮 / 身宮 / 主星位置不可視為精準結果。補填出生時辰後可升級為正式排盤。
{% else %}
本次排盤為 **Fallback 模式**（mock_fallback）：農曆轉換套件不可用，資料為架構性 mock，不代表真實排盤結果。
{% endif %}

{% if report.ziwei_chart.accuracy_note %}
> {{ report.ziwei_chart.accuracy_note }}
{% endif %}

---

### 二、命宮解讀

宮位：**{{ report.ziwei_chart.ming_palace.earthly_branch }}宮**
主星：{{ report.ziwei_chart.ming_palace.main_stars | join('、') if report.ziwei_chart.ming_palace.main_stars else "無主星（空宮）" }}
四化：{{ report.ziwei_chart.ming_palace.transformations | join('、') if report.ziwei_chart.ming_palace.transformations else "無" }}

命宮是紫微命盤的核心，代表你的根本個性、外在氣質與人生主軸。命宮主星決定了你最本能的行為策略與人生著力點。

{{ report.ziwei_chart.ming_palace.interpretation }}

---

### 三、身宮解讀

{% if report.ziwei_chart.shen_branch %}
身宮地支：**{{ report.ziwei_chart.shen_branch }}**
身宮所在宮位：{{ report.ziwei_chart.shen_palace.name if report.ziwei_chart.shen_palace else "─" }}
主星：{{ report.ziwei_chart.shen_palace.main_stars | join('、') if report.ziwei_chart.shen_palace and report.ziwei_chart.shen_palace.main_stars else "無主星" }}

身宮代表後天行動重心，會隨年齡增長越來越明顯。身宮所在宮位揭示你人生後半段用力最多的領域——這是你中年之後逐漸找到節奏、越來越游刃有餘的生命舞台。
{% else %}
出生時辰未知，身宮無法精確計算。
{% endif %}

---

### 四、官祿宮解讀（事業格局）

宮位：**{{ report.ziwei_chart.career_palace.earthly_branch }}宮**
主星：{{ report.ziwei_chart.career_palace.main_stars | join('、') if report.ziwei_chart.career_palace.main_stars else "無主星（空宮）" }}
四化：{{ report.ziwei_chart.career_palace.transformations | join('、') if report.ziwei_chart.career_palace.transformations else "無" }}

官祿宮是事業格局的核心，揭示你的職涯走向、工作模式與成就方式。空宮不代表事業無成，而是格局更靈活，往往借鑑對宮（夫妻宮）特質來展現。

{{ report.ziwei_chart.career_palace.interpretation }}

---

### 五、財帛宮解讀（財富模式）

宮位：**{{ report.ziwei_chart.wealth_palace.earthly_branch }}宮**
主星：{{ report.ziwei_chart.wealth_palace.main_stars | join('、') if report.ziwei_chart.wealth_palace.main_stars else "無主星（空宮）" }}
四化：{{ report.ziwei_chart.wealth_palace.transformations | join('、') if report.ziwei_chart.wealth_palace.transformations else "無" }}

財帛宮揭示你的財富獲取方式、金錢觀與理財模式。與八字財星及五行財富能量互為參照，可以幫助你更立體地理解自己的財富場域。

{{ report.ziwei_chart.wealth_palace.interpretation }}

---

### 六、夫妻宮解讀（感情模式）

宮位：**{{ report.ziwei_chart.spouse_palace.earthly_branch }}宮**
主星：{{ report.ziwei_chart.spouse_palace.main_stars | join('、') if report.ziwei_chart.spouse_palace.main_stars else "無主星（空宮）" }}
四化：{{ report.ziwei_chart.spouse_palace.transformations | join('、') if report.ziwei_chart.spouse_palace.transformations else "無" }}

夫妻宮揭示你在長期親密關係中的模式與課題。搭配西洋占星金星 / 月亮 / 第七宮，可以更完整地看見你對伴侶的期待與自身的關係模式。

{{ report.ziwei_chart.spouse_palace.interpretation }}

---

### 七、福德宮解讀（精神世界）

宮位：**{{ report.ziwei_chart.fortune_palace.earthly_branch }}宮**
主星：{{ report.ziwei_chart.fortune_palace.main_stars | join('、') if report.ziwei_chart.fortune_palace.main_stars else "無主星（空宮）" }}
四化：{{ report.ziwei_chart.fortune_palace.transformations | join('、') if report.ziwei_chart.fortune_palace.transformations else "無" }}

福德宮顯示你的內在精神世界、享樂模式與壓力修復方式。福德宮強的人，即使外在環境困難，也能在內心找到平靜的出口。

{{ report.ziwei_chart.fortune_palace.interpretation }}

---

### 八、生年四化解讀

四化是流動的命運之鑰，反映出生年天干帶給人格的能量烙印。

{% set four_trans = report.ziwei_chart.four_transformations %}
{% set lu_star = namespace(value="") %}
{% set quan_star = namespace(value="") %}
{% set ke_star = namespace(value="") %}
{% set ji_star = namespace(value="") %}
{% for star, tx in four_trans.items() %}
  {% if tx == "化祿" %}{% set lu_star.value = star %}{% endif %}
  {% if tx == "化權" %}{% set quan_star.value = star %}{% endif %}
  {% if tx == "化科" %}{% set ke_star.value = star %}{% endif %}
  {% if tx == "化忌" %}{% set ji_star.value = star %}{% endif %}
{% endfor %}

**化祿**（{{ lu_star.value if lu_star.value else "─" }}）：化祿代表資源流入、機會匯聚的方向。化祿落在哪個星曜，就是那顆星在你的命盤中發揮最豐盛能量之處，往往也是你最容易得到滋養的領域。

**化權**（{{ quan_star.value if quan_star.value else "─" }}）：化權代表主導力、掌控感與決策能量的強化。有化權的星曜在你的命盤中帶有強烈的自主意志，適合你在對應領域中主動掌舵。

**化科**（{{ ke_star.value if ke_star.value else "─" }}）：化科代表名聲、學習力與形象的光環。化科所在的星曜具有文星能量，適合與學術、知識傳遞、形象建立相關的展現。

**化忌**（{{ ji_star.value if ji_star.value else "─" }}）：化忌帶來壓力、執念與反覆的功課，但這並不是詛咒，而是深化的邀請。化忌所在的領域是你此生需要面對、轉化與精熟的重要課題——有功課才有深度。

| 星曜 | 四化 |
|------|------|
{% for star, transform in four_trans.items() %}
| {{ star }} | {{ transform }} |
{% endfor %}

---

### 九、十二宮完整分析

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

主星：{{ palace.main_stars | join('、') if palace.main_stars else "無主星（空宮）" }}
輔星：{{ palace.minor_stars | join('、') if palace.minor_stars else "無（輔星後續版本安置）" }}
四化：{{ palace.transformations | join('、') if palace.transformations else "無" }}

{{ palace.interpretation }}

{% endfor %}

---

### 十、輔星與煞星分析（V1.5.5）

輔星與煞星是紫微命盤的加權因子，不是主角，但它們讓主星的能量更立體。

**吉輔星的作用**：讓宮位主星更容易發揮，增加貴人、資源與機會的流入。
**煞曜的作用**：不等於壞，而是壓力、突破、代價與強度——它們帶來挑戰，也帶來磨礪後的韌性。

#### 吉輔星解讀

{% if report.ziwei_chart.auxiliary_star_map %}
{% set aux = report.ziwei_chart.auxiliary_star_map %}
**左輔**（{{ aux.get("左輔", "─") }}宮）：貴人輔佐之星，代表你生命中能給予實質支援的人際力量。左輔入宮，往往帶來協作型貴人與後天助力。

**右弼**（{{ aux.get("右弼", "─") }}宮）：幕後輔佐之星，默默在側的支持力量。右弼代表不顯山露水卻在關鍵時刻出現的援助。

**文昌**（{{ aux.get("文昌", "─") }}宮）：主學習、考試、文書、正式表達與專業能力。文昌入宮讓該宮位的主星更具學術或文化底蘊。

**文曲**（{{ aux.get("文曲", "─") }}宮）：主才藝、口才、情感表達與藝術審美。文曲入宮讓該宮位增添浪漫與才氣。

**天魁**（{{ aux.get("天魁", "─") }}宮）：天乙貴人，代表在重要時刻出現的關鍵推手與提攜者。

**天鉞**（{{ aux.get("天鉞", "─") }}宮）：玉堂貴人，代表溫柔、優雅的貴人緣分與機會。

**祿存**（{{ aux.get("祿存", "─") }}宮）：資源守成之星，象徵財庫穩固與守得住的能量。祿存所在宮位往往能守住應有的資源。
{% else %}
輔星資料尚未計算。
{% endif %}

#### 煞曜解讀

{% if report.ziwei_chart.malefic_star_map %}
{% set sha = report.ziwei_chart.malefic_star_map %}
**擎羊**（{{ sha.get("擎羊", "─") }}宮）：刀鋒之星，象徵衝突、果斷與破局力量。擎羊入宮讓該宮位充滿張力，但也帶來決斷能力——學會駕馭這股力量，才能化刀為劍。

**陀羅**（{{ sha.get("陀羅", "─") }}宮）：糾纏拉扯之星，象徵慢性執著與反覆拖延。陀羅所在宮位容易陷入「放不下」的迴圈，但持續深耕也能成為最終的精熟者。

**火星**（{{ sha.get("火星", "─") }}宮）：爆發行動之星，象徵急躁、衝動但也是高爆發力的能量。火星入宮時如能控制節奏，可成為快速行動的優勢。

**鈴星**（{{ sha.get("鈴星", "─") }}宮）：內在焦躁之星，象徵突發狀況與警覺過度。鈴星提醒你要培養處理突發事件的能力，也要注意過度緊張帶來的消耗。

**地空**（{{ sha.get("地空", "─") }}宮）：空性之星，象徵理想與現實的落差感。地空入宮常帶來「期待落空」的課題，但也是探索靈性與超然視角的機會。

**地劫**（{{ sha.get("地劫", "─") }}宮）：破耗之星，象徵資源的斷裂與重建需求。地劫入宮時需謹慎管理該宮位的資源，也需要做好「破而後立」的心理準備。

> **重要提示**：煞曜不是詛咒，而是命盤中需要更有意識去面對的高壓區域。每一顆煞曜都有其對應的「化解策略」——了解它，比逃避它更有力量。
{% else %}
煞星資料尚未計算（需出生時辰進行完整安星）。
{% endif %}

---

### 十一、大限 10 年運限分析（V1.5.5 Phase 1）

{% if report.ziwei_chart.da_xian %}
大限是紫微斗數中最重要的後天運限系統，每十年為一個生命章節的主旋律。

**大限方向**：{{ report.ziwei_chart.da_xian_direction | replace("forward", "順行（陽男 / 陰女）") | replace("backward", "逆行（陰男 / 陽女）") | replace("unknown", "未知（性別未填，以保守順行計算）") }}

**大限起始歲數**：{{ report.ziwei_chart.da_xian_start_age }}歲（依五行局數：{{ report.ziwei_chart.five_element_bureau }}）

> **V1.5.5 大限版本說明**：目前大限為 Phase 1 骨架，已建立十二個大限的宮位對應與基礎解讀。尚未加入大限四化、宮干飛化與流年細部系統。適合作為十年生命焦點的大框架參考，不適合直接斷具體年份事件。

{% for d in report.ziwei_chart.da_xian %}
#### {{ d.start_age }}–{{ d.end_age }} 歲：{{ d.palace_name }}（{{ d.branch }}）

主星：{{ d.main_stars | join('、') if d.main_stars else "無主星" }}
輔星 / 煞星：{{ d.auxiliary_stars | join('、') if d.auxiliary_stars else "無" }}

{{ d.interpretation }}

{% endfor %}
{% else %}
大限資料尚未計算。
{% endif %}

---

### 十二、版本限制聲明

V1.7.7 已完成核心輔星、六煞、大限 Phase 1、命主、身主、天馬、廟旺陷 Phase 1、盤面結構支援度 Phase 1（校準版）。以下功能尚未完成，解讀時請注意：

> **準確度護欄**：目前紫微排盤已通過 Rossi 外部盤校準，但不同網站可能因流派、閏月、子時換日、輔星表、廟旺陷表與分數模型而產生差異。本系統會標示 calculation_mode 與 accuracy_note，並建議使用外部校準工具確認重大差異。

- **大限四化 / 宮干四化**：尚未實作，目前大限僅有宮位骨架與基礎解讀。
- **流年 / 流月 / 流日**：尚未實作，不適合做完整年份斷事。
- **輔星安星流派差異**：V1.7.6 採用 Phase 1 常見表法，流派細節後續版本可配置。
- **閏月精準處理**：採保守處理，後續版本加入閏月流派設定。
- **盤面結構支援度**：Phase 1 校準指標，不等同外部網站好運指數，不代表命運好壞。

---

{% if report.ziwei_chart.ming_zhu or report.ziwei_chart.shen_zhu or report.ziwei_chart.tian_ma_branch %}
### 十三、命主 / 身主 / 天馬（V1.7.5）

{% if report.ziwei_chart.ming_zhu %}
- **命主（先天人格輔助星）**：{{ report.ziwei_chart.ming_zhu }}
{% endif %}
{% if report.ziwei_chart.shen_zhu %}
- **身主（後天行動重心輔助星）**：{{ report.ziwei_chart.shen_zhu }}
{% endif %}
{% if report.ziwei_chart.tian_ma_branch %}
- **天馬（移動與外部機會能量）**：{{ report.ziwei_chart.tian_ma_branch }}{% if report.ziwei_chart.tian_ma_palace %}（落{{ report.ziwei_chart.tian_ma_palace }}）{% endif %}
{% endif %}

---
{% endif %}

{% if report.ziwei_chart.ziwei_score is not none %}
### 十四、紫微盤面結構支援度（V1.7.6）

**盤面結構支援度**：{{ report.ziwei_chart.ziwei_score }} / 100（{{ report.ziwei_chart.ziwei_score_label or "" }}）

{% if report.ziwei_chart.ziwei_score_components %}
**分數組成摘要**：基準 {{ report.ziwei_chart.ziwei_score_components.get('base', 50) }}，命宮 {{ '{:+d}'.format(report.ziwei_chart.ziwei_score_components.get('ming_palace', 0)) }}，官祿財帛福德 {{ '{:+d}'.format(report.ziwei_chart.ziwei_score_components.get('career_wealth_fortune', 0)) }}，四化 {{ '{:+d}'.format(report.ziwei_chart.ziwei_score_components.get('transformations', 0)) }}，輔星 {{ '{:+d}'.format(report.ziwei_chart.ziwei_score_components.get('auxiliary_support', 0)) }}，六煞 {{ '{:+d}'.format(report.ziwei_chart.ziwei_score_components.get('malefic_tension', 0)) }}。
{% endif %}

> **聲明**：此分數不等同外部網站好運指數，也不代表命運好壞、絕對成敗或人生保證。它是本系統 Phase 1 的結構支援度模型，供自我探索參考。

{% if report.ziwei_chart.ziwei_score_explanation %}
> {{ report.ziwei_chart.ziwei_score_explanation }}
{% endif %}

{% if report.ziwei_chart.ziwei_score >= 85 %}
> **高分提醒**：高分代表盤面資源集中，不代表人生沒有壓力；反而通常意味著需要承載更高期待與更強責任。
{% endif %}

---
{% endif %}

{% set _ming_brightness = report.ziwei_chart.brightness_map.get("命宮", {}) if report.ziwei_chart.brightness_map else {} %}
{% if _ming_brightness %}
### 十五、命宮主星廟旺陷（V1.7.5 Phase 1）

{% for star, bv in _ming_brightness.items() %}
- {{ star }}：{{ bv }}
{% endfor %}

---
{% endif %}

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

{{ hd_narrative }}

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

    hd_narrative = ""
    if getattr(report, "human_design_chart", None) is not None:
        try:
            from human_design.templates import render_hd_full_narrative
            hd_narrative = render_hd_full_narrative(report.human_design_chart)
        except Exception:
            hd_narrative = ""

    template_str = get_template(report.profile.report_length.value)
    env = Environment(loader=BaseLoader())
    tmpl = env.from_string(template_str)
    return tmpl.render(
        report=report,
        version=version,
        disclaimer=disclaimer,
        hd_narrative=hd_narrative,
    )
