"""
Astro Destiny Analyzer — Compatibility Report Templates
V1.7.1
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from compatibility.models import CompatibilityReport

_DISCLAIMER_COMPAT = (
    "本報告為關係理解、溝通探索與人格對照之參考工具。"
    "分析內容不代表兩人「一定適合」或「一定不適合」，"
    "不構成科學定論、醫療診斷、法律意見、投資建議或任何形式的絕對命運預測。"
    "請以開放態度閱讀，關係的品質由兩人共同創造。"
)

_SCORE_GRADE_DESC = {
    (85, 100): "高共鳴 — 基礎元素高度契合，互動通常自然流暢。",
    (70,  84): "互補佳 — 差異帶來活力，能在各自優勢中找到平衡。",
    (55,  69): "需要溝通設計 — 有差異但可管理，刻意建立溝通節奏後關係穩固。",
    (40,  54): "磨合壓力高 — 需要更多耐心與理解，雙方都需具備較高的情緒成熟度。",
    ( 0,  39): "需要高度成熟與界線 — 挑戰較多，建議先各自穩固個人狀態再深化關係。",
}


def _score_grade_desc(overall: int) -> str:
    for (lo, hi), desc in _SCORE_GRADE_DESC.items():
        if lo <= overall <= hi:
            return desc
    return ""


_RELATIONSHIP_TYPE_ADVICE: Dict[str, Dict] = {
    "romantic": {
        "focus_title": "情感安全感與親密節奏",
        "priority_questions": [
            "我們如何處理彼此的情緒不安全感？",
            "我們如何談承諾與個人自由的平衡？",
            "我們發生衝突後，如何修復關係？",
            "我們如何長期維持吸引力與新鮮感？",
        ],
        "key_advice": "建立固定的「關係時光」，讓情感連結不只在問題出現時才被討論。",
        "avoid_patterns": ["情緒勒索與沉默懲罰", "翻舊帳或放大過去錯誤", "假設對方知道你的需求"],
        "best_practices": ["每週確認彼此的情緒狀態", "建立衝突後的修復流程", "主動表達欣賞與感謝"],
    },
    "marriage": {
        "focus_title": "長期承諾與共同生活設計",
        "priority_questions": [
            "我們如何處理彼此的情緒不安全感？",
            "財務、家務、育兒的決策如何分工？",
            "我們發生衝突後，如何修復關係？",
            "如何在長期關係中維持個人成長與共同願景？",
        ],
        "key_advice": "婚姻需要定期「關係健檢」，主動討論彼此的期待與現況，而非等問題爆發才溝通。",
        "avoid_patterns": ["假設分工「理所當然」", "情感帳戶長期透支", "停止表達感謝與欣賞"],
        "best_practices": ["每年進行一次關係回顧", "建立家務與財務的明確共識", "保持個人興趣與社交空間"],
    },
    "business": {
        "focus_title": "決策分工與利益共識",
        "priority_questions": [
            "誰負責最終決策？各自的決策範圍是什麼？",
            "誰負責執行？誰負責策略？分工是否清楚？",
            "利益與風險如何分配？是否有書面共識？",
            "發生重大分歧時，有什麼解決機制？",
        ],
        "key_advice": "合作前先把「不說出口的假設」說出來，包括利潤分配、退出條件、決策優先順序。",
        "avoid_patterns": ["友情凌駕於契約之上", "角色模糊導致責任推諉", "迴避財務與退出條款的討論"],
        "best_practices": ["定期舉行合夥人會議", "書面記錄重要決策", "建立分歧時的仲裁機制"],
    },
    "parent_child": {
        "focus_title": "支持與界線的平衡",
        "priority_questions": [
            "期待是否符合對方的年齡與當前能力？",
            "支持與控制的界線在哪裡？",
            "孩子的節奏是否被看見與尊重？",
            "父母的焦慮是否被投射到孩子身上？",
        ],
        "key_advice": "最好的支持是讓對方感到「被看見」，而不只是「被教導」。先聆聽，再給建議。",
        "avoid_patterns": ["將自己未完成的期望轉移給孩子", "以愛為名控制對方的選擇", "比較兄弟姊妹或他人"],
        "best_practices": ["定期問「你現在需要什麼？」", "分辨「我擔心的」和「他實際面對的」", "慶祝小進步而非只關注缺失"],
    },
    "friendship": {
        "focus_title": "陪伴品質與情感支持",
        "priority_questions": [
            "彼此需要多少陪伴頻率才感到被重視？",
            "自由度與承諾之間如何平衡？",
            "情緒支持是否相對對等？",
        ],
        "key_advice": "友誼也需要維護，主動聯繫不代表打擾，而是讓對方知道你在乎。",
        "avoid_patterns": ["單方面付出卻不表達需求", "只在需要時才出現", "比較與競爭"],
        "best_practices": ["定期約定共同時光", "在對方低潮時主動出現", "允許彼此有其他朋友圈"],
    },
    "colleague": {
        "focus_title": "工作協作與角色定位",
        "priority_questions": [
            "工作節奏與優先順序是否一致？",
            "溝通方式是否清楚？是否有誤解積累？",
            "各自的職責邊界是否清楚？",
            "壓力情境下誰會接住誰？",
        ],
        "key_advice": "職場關係的核心是清楚的期待管理，主動確認「你理解的任務和我說的一樣嗎？」",
        "avoid_patterns": ["假設對方知道你的進度", "私下抱怨而非直接反映", "模糊責任邊界"],
        "best_practices": ["定期同步工作進度", "建立清楚的溝通頻道", "在壓力前預防性討論分工"],
    },
    "general": {
        "focus_title": "互動模式理解",
        "priority_questions": [
            "彼此最重視的互動品質是什麼？",
            "溝通風格是否相容？",
            "如何在差異中找到共同語言？",
        ],
        "key_advice": "了解彼此的互動風格是建立良好關係的第一步，好奇心比評判更有效。",
        "avoid_patterns": ["用自己的標準衡量對方", "迴避直接溝通"],
        "best_practices": ["保持開放與好奇", "表達需求而非期待對方猜測"],
    },
}


def _build_relationship_type_advice(rt_value: str) -> Dict:
    """Return relationship-type-specific advice dict."""
    return _RELATIONSHIP_TYPE_ADVICE.get(rt_value, _RELATIONSHIP_TYPE_ADVICE["general"])


_CONFLICT_REPAIR_STEPS: List[str] = [
    "**暫停** — 感到情緒升高時，約定「暫停 20 分鐘」的信號，讓雙方冷靜後再繼續。",
    "**命名情緒** — 用「我現在感到…」說出自己的情緒狀態，而非評論對方的行為。",
    "**回到事實** — 只描述具體發生的事，不加入推測或標籤（「你總是…」「你從來…」）。",
    "**說明需求** — 表達「我需要的是…」，而非要求對方猜測你的期望。",
    "**約定下一步** — 衝突結束前，雙方各說一個可以做到的具體行動，不留模糊承諾。",
    "**不翻舊帳** — 每次衝突只處理當下的議題，過去已解決的事不再重提。",
    "**不用沉默懲罰** — 冷戰不是休息，是傷害；若需要空間，說「我需要一點時間，但我不是在放棄這段關係」。",
]


def build_compatibility_markdown(report: "CompatibilityReport") -> str:
    """
    Build a full Markdown document for a CompatibilityReport.
    Returns a plain Markdown string (no HTML).
    """
    from config import APP_NAME, APP_VERSION
    from compatibility.models import relationship_label

    pa = report.person_a_profile
    pb = report.person_b_profile
    rt_label = relationship_label(report.relationship_type)
    rt_advice = _build_relationship_type_advice(report.relationship_type.value)
    sc = report.score_breakdown
    ast = report.astrology
    bz  = report.bazi
    zw  = report.ziwei
    num = report.numerology
    bld = report.blood_type
    syn = report.synthesis

    lines = []

    # ── Cover ─────────────────────────────────────────────────────────────────
    lines += [
        f"# {APP_NAME}",
        "## 關係合盤分析報告",
        "",
        f"**{pa.name} × {pb.name}**",
        "",
        f"| 項目 | 資料 |",
        f"|------|------|",
        f"| 關係類型 | {rt_label} |",
        f"| A 方 | {pa.name} |",
        f"| A 出生日期 | {pa.birth_date} |",
        f"| A 出生時間 | {pa.birth_time.strftime('%H:%M') if pa.birth_time else '未知'} |",
        f"| A 出生地 | {pa.birth_city} |",
        f"| B 方 | {pb.name} |",
        f"| B 出生日期 | {pb.birth_date} |",
        f"| B 出生時間 | {pb.birth_time.strftime('%H:%M') if pb.birth_time else '未知'} |",
        f"| B 出生地 | {pb.birth_city} |",
        f"| 產生時間 | {report.created_at} |",
        f"| 版本 | v{APP_VERSION} |",
        "",
    ]

    # ── Disclaimer ────────────────────────────────────────────────────────────
    lines += [
        "## ⚠️ 免責聲明",
        "",
        f"> {_DISCLAIMER_COMPAT}",
        "",
    ]

    # ── Calculation mode ──────────────────────────────────────────────────────
    cs_a = report.person_a_chart_summary
    cs_b = report.person_b_chart_summary
    lines += [
        "## 計算模式與資料完整度",
        "",
        "| 系統 | A 方模式 | B 方模式 |",
        "|------|----------|----------|",
        f"| 西洋占星 | {cs_a.get('western_mode', '─')} | {cs_b.get('western_mode', '─')} |",
        f"| 八字 | {cs_a.get('bazi_mode', '─')} | {cs_b.get('bazi_mode', '─')} |",
        f"| 紫微 | {cs_a.get('ziwei_mode', '─')} | {cs_b.get('ziwei_mode', '─')} |",
        f"| 出生時間已知 | {'是' if cs_a.get('birth_time_known') else '否'} | {'是' if cs_b.get('birth_time_known') else '否'} |",
        "",
        "> 缺出生時間會影響月亮、上升、宮位、紫微命宮等關係判讀，請謹慎解讀相關段落。",
        "",
    ]

    # ── Scores ────────────────────────────────────────────────────────────────
    grade = _score_grade_desc(sc.overall_score)
    dyn_label = sc.dynamic_label()
    lines += [
        "## 關係總分與分項分數",
        "",
        "> **分數解讀說明**：分數不是絕對適合度，而是互動模式的可觀察指標。"
        "高分代表自然共鳴較多；中等分代表需要溝通設計；"
        "衝突分數高不等於不好，而是代表關係張力與成長課題較強。",
        "",
        f"**綜合評分：{sc.overall_score}/100 — {sc.score_label()}**",
        "",
        f"> {grade}",
        "",
        "| 維度 | 分數 | 說明 |",
        "|------|------|------|",
        f"| 情感共鳴 | {sc.emotional_score} | 月亮、水象、情緒安全感 |",
        f"| 溝通契合 | {sc.communication_score} | 水星、生命靈數、表達節奏 |",
        f"| 吸引力 | {sc.attraction_score} | 金星火星、感情表達 |",
        f"| 穩定性 | {sc.stability_score} | 土象、八字相生、共同基礎 |",
        f"| 成長潛力 | {sc.growth_score} | 差異互補、共同進步 |",
        f"| 衝突強度 | {sc.conflict_score} | 衝突分數高代表張力強，不代表關係不好 |",
        f"| 協作效能 | {sc.collaboration_score} | 事業、合作、分工模式 |",
        "",
    ]

    # High-tension high-growth / low-conflict low-growth notes
    if sc.conflict_score >= 65 and sc.growth_score >= 65:
        lines += [
            f"> **高張力高成長型關係**（衝突強度 {sc.conflict_score}，成長潛力 {sc.growth_score}）",
            "> 這不是低品質關係，而是高張力、高成長型關係。"
            "關鍵不在於避免衝突，而在於能否建立清楚的修復流程。",
            "",
        ]
    elif sc.conflict_score < 45 and sc.growth_score < 50:
        lines += [
            f"> **舒適型關係提醒**（衝突強度 {sc.conflict_score}，成長潛力 {sc.growth_score}）",
            "> 關係可能相處舒適，但需要避免一起停滯。"
            "適合加入共同目標或新的學習計畫，持續帶入成長動能。",
            "",
        ]
    else:
        lines += [
            "> 衝突強度高 + 成長潛力高 = 「高張力高成長」型關係，需要更多溝通設計。",
            "",
        ]

    # ── Relationship Type Positioning ─────────────────────────────────────────
    lines += [
        f"## 關係定位總論（{rt_label}）",
        "",
        f"**關係焦點**：{rt_advice['focus_title']}",
        "",
        "**本關係類型的核心提問：**",
        "",
    ]
    for q in rt_advice["priority_questions"]:
        lines.append(f"- {q}")
    lines += [
        "",
        f"**關鍵建議**：{rt_advice['key_advice']}",
        "",
        "**建議避免的模式：**",
        "",
    ]
    for p in rt_advice["avoid_patterns"]:
        lines.append(f"- ⚠️ {p}")
    lines += [
        "",
        "**有效的互動實踐：**",
        "",
    ]
    for bp in rt_advice["best_practices"]:
        lines.append(f"- ✅ {bp}")
    lines += [""]

    # ── Summary ───────────────────────────────────────────────────────────────
    lines += [
        "## 關係總論",
        "",
        syn.relationship_summary,
        "",
    ]

    # ── Astrology ─────────────────────────────────────────────────────────────
    lines += [
        "## 西洋占星互動",
        "",
        f"- **太陽配對**：{ast.sun_pair}",
        f"- **月亮配對**：{ast.moon_pair}",
        f"- **水星配對**：{ast.mercury_pair}",
        f"- **金星火星**：{ast.venus_mars_pair}",
        f"- **上升配對**：{ast.ascendant_pair}",
        "",
    ]
    if ast.key_aspects:
        lines.append("**主要星象相位：**")
        lines += [f"- {a}" for a in ast.key_aspects]
        lines.append("")
    if ast.harmony_factors:
        lines.append("**和諧因素：**")
        lines += [f"- ✅ {h}" for h in ast.harmony_factors]
        lines.append("")
    if ast.tension_factors:
        lines.append("**張力因素：**")
        lines += [f"- ⚡ {t}" for t in ast.tension_factors]
        lines.append("")
    lines += [
        ast.interpretation,
        "",
        f"*準確度說明：{ast.accuracy_note}*",
        "",
    ]

    # ── BaZi ──────────────────────────────────────────────────────────────────
    lines += [
        "## 八字五行互補",
        "",
        f"- **A 日主**：{bz.person_a_day_master}",
        f"- **B 日主**：{bz.person_b_day_master}",
        f"- **日主關係**：{bz.day_master_relation}",
        f"- **五行概況**：{bz.five_element_balance}",
        "",
    ]
    if bz.supportive_elements:
        lines.append("**互補之處：**")
        lines += [f"- ✅ {s}" for s in bz.supportive_elements]
        lines.append("")
    if bz.conflicting_elements:
        lines.append("**需注意之處：**")
        lines += [f"- ⚡ {c}" for c in bz.conflicting_elements]
        lines.append("")
    lines += [
        bz.interpretation,
        "",
        f"*準確度說明：{bz.accuracy_note}*",
        "",
    ]

    # ── ZiWei ─────────────────────────────────────────────────────────────────
    lines += [
        "## 紫微宮位互動",
        "",
        f"- **A 命宮主星**：{zw.person_a_ming_palace}",
        f"- **B 命宮主星**：{zw.person_b_ming_palace}",
        f"- **A 身宮**：{zw.person_a_shen_palace}",
        f"- **B 身宮**：{zw.person_b_shen_palace}",
        "",
    ]
    if zw.key_palace_interactions:
        lines.append("**宮位互動重點：**")
        lines += [f"- {k}" for k in zw.key_palace_interactions]
        lines.append("")
    lines += [
        f"**主星共鳴**：{zw.main_star_resonance}",
        "",
        f"**大限背景**：{zw.da_xian_context}",
        "",
        zw.interpretation,
        "",
        f"*準確度說明：{zw.accuracy_note}*",
        "",
    ]

    # ── Numerology ────────────────────────────────────────────────────────────
    lines += [
        "## 生命靈數互動",
        "",
        f"- **生命靈數配對**：{num.life_path_pair}",
        f"- **共鳴主題**：{num.shared_theme}",
        f"- **挑戰主題**：{num.challenge_theme}",
        "",
        num.interpretation,
        "",
    ]

    # ── Blood Type ────────────────────────────────────────────────────────────
    lines += [
        "## 血型互動",
        "",
        f"- **血型配對**：{bld.blood_pair}",
        f"- **互動風格**：{bld.interaction_style}",
        f"- **衝突模式**：{bld.conflict_style}",
        f"- **建議**：{bld.advice}",
        "",
    ]

    # ── Strengths & Challenges ────────────────────────────────────────────────
    lines += ["## 關係優勢", ""]
    lines += [f"- ✅ {s}" for s in syn.strengths]
    lines += ["", "## 關係挑戰", ""]
    lines += [f"- ⚡ {c}" for c in syn.challenges]
    lines += [""]

    # ── Emotional Interaction ─────────────────────────────────────────────────
    moon_pair_short = ast.moon_pair.split("（")[0].strip() if ast.moon_pair else "─"
    lines += [
        "## 情緒互動模式",
        "",
        syn.emotional_pattern,
        "",
        f"**月亮配對（{moon_pair_short}）說明**：",
        "月亮星座代表一個人的情緒語言與安全感需求。",
        "月亮配對顯示兩人如何給予與接收情緒支持，以及情緒衝突可能的來源。",
        "",
        "| 提問 | 思考方向 |",
        "|------|----------|",
        "| 誰在關係中更需要被安撫？ | 月亮在水象或土象的人通常更需要情緒確認 |",
        "| 誰傾向理性化情緒？ | 月亮在風象或火象的人可能先找解決方案 |",
        "| 誰容易沉默？ | 土象月亮可能需要時間才開口 |",
        "| 誰容易直接表達？ | 火象或風象月亮通常更快表達感受 |",
        "",
        "**修復情緒斷線的方式**：先確認「你現在需要被聽見還是需要建議？」",
        "再進入溝通，可以大幅減少「說了但沒被接住」的失落感。",
        "",
    ]

    # ── Communication Pattern ─────────────────────────────────────────────────
    merc_pair_short = ast.mercury_pair.split("（")[0].strip() if ast.mercury_pair else "─"
    lines += [
        "## 溝通模式",
        "",
        syn.communication_pattern,
        "",
        f"**水星配對（{merc_pair_short}）說明**：",
        "水星代表思考與表達方式，影響溝通速度、直接度與偏好的對話節奏。",
        "",
        "| 溝通面向 | 觀察指標 |",
        "|----------|----------|",
        "| 溝通速度 | 火象 / 風象水星通常速度快；土象 / 水象較慢且深思 |",
        "| 直接或委婉 | 火象傾向直接；水象傾向委婉與情感優先 |",
        "| 討論問題時 | 風象容易跳到解決方案；水象先需要被理解 |",
        "| 溝通節奏 | 是否需要先確認情緒再談道理？ |",
        "",
    ]

    # ── Attraction / Collaboration ────────────────────────────────────────────
    vm_pair_short = ast.venus_mars_pair.split("（")[0].strip() if ast.venus_mars_pair else "─"
    rt_val = report.relationship_type.value
    lines += [
        "## 吸引力與合作動能",
        "",
        syn.attraction_pattern,
        "",
        f"**金星火星配對（{vm_pair_short}）說明**：",
    ]
    if rt_val in ("romantic", "marriage"):
        lines += [
            "金星代表吸引力與愛的語言，火星代表主動性與行動節奏。",
            "兩人的金星火星互動反映吸引力的自然流動與熱度維持方式。",
        ]
    elif rt_val == "business":
        lines += [
            "在合作關係中，金星代表協調風格，火星代表推進力與執行節奏。",
            "兩人的金火配對反映合作時的互補分工與推動力。",
        ]
    elif rt_val == "parent_child":
        lines += [
            "金星代表欣賞與肯定的表達方式，火星代表動機引導的風格。",
            "了解彼此的動機語言，有助於建立更有效的支持方式。",
        ]
    else:
        lines += [
            "金星火星配對反映兩人在互動中的主動性與回應節奏。",
        ]
    lines += [""]

    # ── Conflict Pattern ──────────────────────────────────────────────────────
    lines += [
        "## 衝突模式",
        "",
        syn.conflict_pattern,
        "",
    ]

    # ── Conflict Repair ───────────────────────────────────────────────────────
    lines += [
        "## 衝突修復七步驟",
        "",
        "衝突本身不是問題，無法修復才是問題。以下步驟適用於大多數關係衝突：",
        "",
    ]
    for i, step in enumerate(_CONFLICT_REPAIR_STEPS, 1):
        lines.append(f"{i}. {step}")
    lines += [""]

    # ── Advice ────────────────────────────────────────────────────────────────
    lines += ["## 溝通建議", ""]
    lines += [f"{i+1}. {a}" for i, a in enumerate(syn.practical_advice)]
    lines += [""]

    # ── 30-day practice ───────────────────────────────────────────────────────
    lines += ["## 30 天關係練習", ""]
    lines += [f"- {p}" for p in syn.thirty_day_practice]
    lines += [""]

    # ── Long-term ─────────────────────────────────────────────────────────────
    lines += [
        "## 長期關係建議",
        "",
        syn.long_term_potential,
        "",
    ]

    # ── V1.8.0 Advanced Astrology ─────────────────────────────────────────────
    adv = getattr(report, "advanced_astrology", None)
    if adv is not None:
        from compatibility.advanced_astrology import (
            aspect_type_zh as _atz, category_zh as _cz, format_orb as _fo,
            SYNASTRY_INTRO, COMPOSITE_INTRO, ADVANCED_SCORE_DISCLAIMER, CONFLICT_CAPTION,
        )
        sm = adv.synastry_matrix
        cc = adv.composite_chart
        adv_sc = adv.advanced_scores

        # ── Synastry Matrix ────────────────────────────────────────────────────
        lines += [
            "## 進階西洋合盤：Synastry 相位矩陣",
            "",
            SYNASTRY_INTRO,
            "",
            adv.summary,
            "",
        ]
        if sm.strongest_aspects:
            lines += [
                "### 最強相位 Top 8",
                "",
                "| A 行星 | B 行星 | 相位 | orb | 強度 | 分類 | 解讀 |",
                "|--------|--------|------|-----|------|------|------|",
            ]
            for a in sm.strongest_aspects:
                interp_short = a.interpretation[:40] + "…" if len(a.interpretation) > 40 else a.interpretation
                lines.append(
                    f"| {a.person_a_planet} | {a.person_b_planet} | {_atz(a.aspect_type)} "
                    f"| {_fo(a.orb)} | {a.strength} | {_cz(a.category)} | {interp_short} |"
                )
            lines.append("")
        if sm.harmony_aspects:
            lines += ["### 情緒連結相位", ""]
            for a in sm.emotional_aspects[:4]:
                lines.append(f"- {a.interpretation}")
            lines.append("")
        if sm.communication_aspects:
            lines += ["### 溝通相位", ""]
            for a in sm.communication_aspects[:4]:
                lines.append(f"- {a.interpretation}")
            lines.append("")
        if sm.attraction_aspects:
            lines += ["### 吸引力 / 化學反應相位", ""]
            for a in sm.attraction_aspects[:4]:
                lines.append(f"- {a.interpretation}")
            lines.append("")
        if sm.tension_aspects:
            lines += ["### 張力相位", ""]
            for a in sm.tension_aspects[:6]:
                lines.append(
                    f"- ⚡ {a.person_a_planet}（A）× {a.person_b_planet}（B）"
                    f"{_atz(a.aspect_type)}｜{_fo(a.orb)}"
                )
            lines.append("")
        if sm.stability_aspects:
            lines += ["### 穩定與責任相位", ""]
            for a in sm.stability_aspects[:4]:
                lines.append(f"- {a.interpretation}")
            lines.append("")
        if adv.repair_advice:
            lines += ["### 修復建議", ""]
            for tip in adv.repair_advice:
                lines.append(f"- {tip}")
            lines.append("")
        lines += [f"*{sm.accuracy_note}*", ""]

        # ── Composite Chart ───────────────────────────────────────────────────
        lines += [
            "## Composite Chart 中點盤",
            "",
            COMPOSITE_INTRO,
            "",
            f"*計算模式：{cc.calculation_mode}*",
            "",
        ]
        key_planets = ["太陽", "月亮", "金星", "火星", "土星"]
        _key_planet_roles = {
            "太陽": "關係核心目的",
            "月亮": "情緒氣候",
            "金星": "親密與喜好",
            "火星": "行動與衝突",
            "土星": "承諾與壓力",
        }
        for cp in cc.planets:
            if cp.planet in key_planets and cp.interpretation:
                role = _key_planet_roles.get(cp.planet, "")
                lines += [
                    f"### Composite {cp.planet}（{cp.sign}）{'— ' + role if role else ''}",
                    "",
                    cp.interpretation,
                    "",
                ]
        lines += [
            "### 關係核心主題", "", cc.relationship_theme, "",
            "### 情緒氣候", "", cc.emotional_climate, "",
            "### 吸引力風格", "", cc.attraction_style, "",
            "### 衝突模式", "", cc.conflict_style, "",
        ]
        if cc.ascendant_sign:
            lines += [f"**Composite ASC**：{cc.ascendant_sign}", ""]
        else:
            lines += [
                "> Composite ASC / MC 需要雙方精準出生時間與出生地，本次未納入四軸解讀。",
                "",
            ]
        lines += [f"*{cc.accuracy_note}*", ""]

        # ── Advanced Scores ───────────────────────────────────────────────────
        lines += [
            "## 進階合盤分數",
            "",
            f"**進階合盤總分：{adv_sc.overall_advanced_score} / 100 — {adv_sc.label}**",
            "",
            f"> {ADVANCED_SCORE_DISCLAIMER}",
            "",
            f"| 項目 | 分數 | 說明 |",
            f"|------|------|------|",
            f"| 情緒連結 | {adv_sc.emotional_bond} | 情感共鳴與情緒安全感 |",
            f"| 溝通流暢度 | {adv_sc.communication_flow} | 思維契合與表達節奏 |",
            f"| 吸引力 / 化學反應 | {adv_sc.attraction_chemistry} | 自然吸引力與磁場 |",
            f"| 穩定潛力 | {adv_sc.stability_potential} | 長期穩定的結構基礎 |",
            f"| 成長張力 | {adv_sc.growth_intensity} | 激勵彼此突破成長 |",
            f"| 衝突強度（張力計） | {adv_sc.conflict_intensity} | {CONFLICT_CAPTION} |",
            f"| 長期潛力 | {adv_sc.long_term_potential} | 長期關係的綜合評估 |",
            "",
            f"> {adv_sc.explanation}",
            "",
            f"*{adv.accuracy_note}*",
            "",
        ]

    # ── Red Flag & Safety Boundary ────────────────────────────────────────────
    lines += [
        "## 關係紅旗與安全界線",
        "",
        "命盤分析描述的是互動**傾向**與**模式**，不代表命運，也不代表任何人「命中注定」要受苦。",
        "",
        "> 若現實關係中存在**羞辱、操控、暴力、財務控制或長期情緒勒索**，",
        "> 請優先尋求現實支持與專業協助，建立安全界線優先於任何命盤分析。",
        "> 命盤分析不能取代安全判斷，也不能合理化傷害行為。",
        "",
    ]

    # ── Closing ───────────────────────────────────────────────────────────────
    lines += [
        "## 結語",
        "",
        f"本報告完成時間：{report.created_at}",
        "",
        f"> {syn.warning_note}",
        "",
        f"---",
        f"> *{APP_NAME} v{APP_VERSION} — 東西方命盤整合分析系統*",
    ]

    return "\n".join(lines)
