"""
Astro Destiny Analyzer — Compatibility Report Templates
V1.7.0
"""
from __future__ import annotations
from typing import TYPE_CHECKING

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
    lines += [
        "## 關係總分與分項分數",
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
        f"| 衝突強度 | {sc.conflict_score} | 高不代表壞，代表張力強度 |",
        f"| 協作效能 | {sc.collaboration_score} | 事業、合作、分工模式 |",
        "",
        "> 衝突強度高 + 成長潛力高 = 「高張力高成長」型關係，需要更多溝通設計。",
        "",
    ]

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

    # ── Patterns ──────────────────────────────────────────────────────────────
    lines += [
        "## 情感模式",
        "",
        syn.emotional_pattern,
        "",
        "## 溝通模式",
        "",
        syn.communication_pattern,
        "",
        "## 衝突模式",
        "",
        syn.conflict_pattern,
        "",
    ]

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
