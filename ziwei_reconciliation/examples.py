"""
Example external chart data for Zi Wei Reconciliation (V1.7.3.1).
Based on user-provided screenshots of external Zi Wei website (V2.0 chart).
Data manually transcribed from two clear screenshots — all 12 palaces filled.
"""
from __future__ import annotations

from ziwei_reconciliation.models import ExternalZiWeiChart, ExternalZiWeiPalace

# ── Rossi external chart — corrected from screenshots (V1.7.3.1) ──────────────
#
# Source:  External Zi Wei website V2.0 screenshot (1989-09-21 11h, 陰男)
# Central info confirmed:
#   陽曆  1989-09-21 11時  陰男
#   農曆  1989-08-22 午時
#   干支  己巳年癸酉月甲申日庚午時
#   五行局 爐中火六局
#   四化  貪狼化權 天梁化科 武曲化祿 文曲化忌
#   命主  文曲  身主  天機
#
# Palace layout (地支 confirmed from screenshot):
#   辰(父母) 巳(福德) 午(田宅) 未(事業)
#   卯(命宮)  [  CENTER  ]       申(交友)
#   寅(兄弟)  [  CENTER  ]       酉(遷移)
#   丑(夫妻) 子(子女) 亥(財帛) 戌(疾厄)
#
# Notes:
#   - 武曲: 廟旺陷表標示「利」（介於廟和旺之間的亮度）
#   - 右弼: 在命宮；左輔: 在財帛宮；天鉞: 在交友宮
#   - 文曲化忌 落在疾厄宮（甲戌宮）
#   - 貪狼化權 落在財帛宮（乙亥宮）
#   - 武曲化祿 落在命宮（丁卯宮）
#   - 天梁化科 落在兄弟宮（丙寅宮）
# ─────────────────────────────────────────────────────────────────────────────

EXAMPLE_ROSSI_EXTERNAL_CHART = ExternalZiWeiChart(
    source_name="external_screenshot_manual",
    birth_solar_date="1989-09-21",
    birth_lunar_date="1989-08-22 午時",
    birth_time_label="午時（11:00–12:59）",
    gender_label="陰男",
    five_element_bureau="爐中火六局",
    ming_palace_branch="卯",
    shen_palace_branch="卯",   # 命宮-身宮 同宮
    ming_zhu="文曲",
    shen_zhu="天機",
    luck_score=80,
    sihua={
        "武曲": "化祿",
        "貪狼": "化權",
        "天梁": "化科",
        "文曲": "化忌",
    },
    palaces=[
        # ── 命宮-身宮  丁卯  大限 6-15 ────────────────────────────────────
        ExternalZiWeiPalace(
            palace_name="命宮",
            branch="卯",
            main_stars=["武曲", "七殺"],
            auxiliary_stars=["右弼"],
            malefic_stars=[],
            transformations={"武曲": "化祿"},
            da_xian_range="6-15",
            brightness={"武曲": "利", "七殺": "旺"},
            raw_text="丁卯命宮-身宮。武曲利（化祿），七殺旺，右弼。養，小耗。",
        ),
        # ── 父母宮  戊辰  大限 116-125 ────────────────────────────────────
        ExternalZiWeiPalace(
            palace_name="父母宮",
            branch="辰",
            main_stars=["太陽"],
            auxiliary_stars=["文昌"],
            malefic_stars=["鈴星"],
            da_xian_range="116-125",
            brightness={"太陽": "旺"},
            raw_text="戊辰父母宮。太陽旺，文昌，鈴星，天喜，寡宿，天刑，胎，青龍。",
        ),
        # ── 福德宮  己巳  大限 106-115 ────────────────────────────────────
        ExternalZiWeiPalace(
            palace_name="福德宮",
            branch="巳",
            main_stars=[],          # 無主星
            auxiliary_stars=[],
            malefic_stars=["地空", "地劫", "陀羅"],
            da_xian_range="106-115",
            raw_text="己巳福德宮。地空，地劫，陀羅，鳳閣，絕，力士。無主星。",
        ),
        # ── 田宅宮  庚午  大限 96-105 ─────────────────────────────────────
        ExternalZiWeiPalace(
            palace_name="田宅宮",
            branch="午",
            main_stars=["天機"],
            auxiliary_stars=["祿存"],
            da_xian_range="96-105",
            brightness={"天機": "廟"},
            raw_text="庚午田宅宮。天機廟，祿存，天空，咸池，八座，天貴，墓，博士。",
        ),
        # ── 事業宮(官祿宮)  辛未  大限 86-95 ─────────────────────────────
        ExternalZiWeiPalace(
            palace_name="官祿宮",
            branch="未",
            main_stars=["紫微", "破軍"],
            auxiliary_stars=[],
            malefic_stars=["擎羊"],
            da_xian_range="86-95",
            brightness={"紫微": "廟", "破軍": "旺"},
            raw_text="辛未事業宮(官祿宮)。紫微廟，破軍旺，擎羊，蔭廉，天月，死，官府。",
        ),
        # ── 交友宮(僕役宮)  壬申  大限 76-85 ─────────────────────────────
        ExternalZiWeiPalace(
            palace_name="交友宮",
            branch="申",
            main_stars=[],          # 無主星
            auxiliary_stars=["天鉞"],
            da_xian_range="76-85",
            raw_text="壬申交友宮。天鉞，空亡，孤辰，天才，天壽，天姚，封誥，三台，天殤，病，伏兵。無主星。",
        ),
        # ── 遷移宮  癸酉  大限 66-75 ──────────────────────────────────────
        ExternalZiWeiPalace(
            palace_name="遷移宮",
            branch="酉",
            main_stars=["天府"],
            auxiliary_stars=[],
            malefic_stars=["火星"],
            da_xian_range="66-75",
            brightness={"天府": "旺"},
            raw_text="癸酉遷移宮。天府旺，火星，天官，截路，龍池，破碎，衰，大耗。",
        ),
        # ── 疾厄宮  甲戌  大限 56-65 ──────────────────────────────────────
        ExternalZiWeiPalace(
            palace_name="疾厄宮",
            branch="戌",
            main_stars=["太陰"],
            auxiliary_stars=["文曲"],
            transformations={"文曲": "化忌"},
            da_xian_range="56-65",
            brightness={"太陰": "旺", "文曲": "忌（陷）"},
            raw_text="甲戌疾厄宮。太陰旺，文曲忌（陷），紅鸞，旬空，天使，帝旺，病符。",
        ),
        # ── 財帛宮  乙亥  大限 46-55 ──────────────────────────────────────
        ExternalZiWeiPalace(
            palace_name="財帛宮",
            branch="亥",
            main_stars=["廉貞", "貪狼"],
            auxiliary_stars=["左輔", "天馬"],
            transformations={"貪狼": "化權"},
            da_xian_range="46-55",
            brightness={"廉貞": "陷", "貪狼": "陷"},
            raw_text="乙亥財帛宮。廉貞陷，貪狼陷（化權），左輔，天馬，天虛，月馬，天巫，旬空，臨官，喜神。",
        ),
        # ── 子女宮  丙子  大限 36-45 ──────────────────────────────────────
        ExternalZiWeiPalace(
            palace_name="子女宮",
            branch="子",
            main_stars=["巨門"],
            auxiliary_stars=["天魁"],
            da_xian_range="36-45",
            brightness={"巨門": "旺"},
            raw_text="丙子子女宮。巨門旺，天魁，陰煞，台輔，恩光，冠帶，飛廉。",
        ),
        # ── 夫妻宮  丁丑  大限 26-35 ──────────────────────────────────────
        ExternalZiWeiPalace(
            palace_name="夫妻宮",
            branch="丑",
            main_stars=["天相"],
            auxiliary_stars=[],
            da_xian_range="26-35",
            brightness={"天相": "廟"},
            raw_text="丁丑夫妻宮。天相廟，華蓋，天哭，沐浴，奏書。",
        ),
        # ── 兄弟宮  丙寅  大限 16-25 ──────────────────────────────────────
        ExternalZiWeiPalace(
            palace_name="兄弟宮",
            branch="寅",
            main_stars=["天同", "天梁"],
            auxiliary_stars=[],
            transformations={"天梁": "化科"},
            da_xian_range="16-25",
            brightness={"天同": "利", "天梁": "廟"},
            raw_text="丙寅兄弟宮。天同利，天梁廟（化科），天福，解神，長生，將軍。",
        ),
    ],
    raw_note=(
        "V1.7.3.1 修正版：根據使用者上傳的兩張外部網站紫微斗數命盤 V2.0 截圖人工整理。"
        " 十二宮地支已修正：辰(父母)、巳(福德)、午(田宅)、未(事業)、申(交友)、酉(遷移)、"
        " 戌(疾厄)、亥(財帛)、子(子女)、丑(夫妻)、寅(兄弟)、卯(命宮)。"
        " 好運指數80分為外部網站自家評分，非標準紫微指標。"
        " 廟旺陷資料依截圖標示填入，僅供參考。"
    ),
)


# ── Minimal blank template for manual entry ───────────────────────────────────

BLANK_EXTERNAL_CHART_JSON = """{
  "source_name": "manual_external",
  "birth_solar_date": "YYYY-MM-DD",
  "birth_lunar_date": "YYYY-MM-DD 時辰",
  "birth_time_label": "午時",
  "gender_label": "陰男",
  "five_element_bureau": "火六局",
  "ming_palace_branch": "卯",
  "shen_palace_branch": "卯",
  "ming_zhu": null,
  "shen_zhu": null,
  "sihua": {
    "武曲": "化祿",
    "貪狼": "化權",
    "天梁": "化科",
    "文曲": "化忌"
  },
  "luck_score": null,
  "palaces": [
    {
      "palace_name": "命宮",
      "branch": "卯",
      "main_stars": ["武曲", "七殺"],
      "auxiliary_stars": [],
      "malefic_stars": [],
      "transformations": {},
      "da_xian_range": null,
      "brightness": {},
      "raw_text": ""
    }
  ],
  "raw_note": ""
}"""
