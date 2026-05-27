"""
Astro Destiny Analyzer — Reusable Streamlit UI Components
"""
import streamlit as st
from core.models import ZodiacSign, FiveElement


def render_planet_table(planet_positions):
    import pandas as pd
    rows = []
    for pp in planet_positions:
        rows.append({
            "行星": pp.planet.value,
            "星座": pp.sign.value,
            "宮位": pp.house,
            "黃道度數": f"{pp.sign_degree:.1f}°",
            "逆行": "◌" if pp.retrograde else "",
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_house_table(houses):
    import pandas as pd
    rows = []
    for h in houses:
        rows.append({
            "宮位": f"第 {h.house_number} 宮",
            "星座": h.sign.value,
            "入宮行星": "、".join(p.value for p in h.planets) if h.planets else "—",
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_aspect_table(aspects):
    import pandas as pd
    rows = []
    for a in aspects:
        rows.append({
            "行星1": a.planet1.value,
            "相位": a.aspect_type.value,
            "行星2": a.planet2.value,
            "容許度": f"{a.orb:.2f}°",
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_bazi_pillars(bazi_chart):
    import pandas as pd
    pillars = [bazi_chart.year_pillar, bazi_chart.month_pillar, bazi_chart.day_pillar]
    if bazi_chart.hour_pillar:
        pillars.append(bazi_chart.hour_pillar)
    rows = [{"柱": p.label, "天干": p.heavenly_stem.value,
             "地支": p.earthly_branch.value, "五行": p.element.value}
            for p in pillars]
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_five_element_chart(bazi_chart):
    try:
        import pandas as pd
        ratio = bazi_chart.five_element_ratio
        strength = bazi_chart.five_element_strength
        rows = [{"五行": k, "比例(%)": v, "強弱": strength.get(k, "")}
                for k, v in ratio.items()]
        df = pd.DataFrame(rows)
        st.bar_chart(df.set_index("五行")["比例(%)"])
        st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception:
        st.write(bazi_chart.five_element_ratio)


def render_ziwei_palace_grid(ziwei_chart):
    """Render 12-palace grid in a 4×3 layout."""
    palaces = [
        ziwei_chart.parents_palace,  ziwei_chart.ming_palace,     ziwei_chart.brother_palace, ziwei_chart.spouse_palace,
        ziwei_chart.career_palace,   None,                         None,                       ziwei_chart.children_palace,
        ziwei_chart.property_palace, ziwei_chart.fortune_palace,   ziwei_chart.friends_palace, ziwei_chart.wealth_palace,
    ]
    center_text = f"身宮: {ziwei_chart.shen_palace.earthly_branch}"

    cols_per_row = 4
    for row_i in range(3):
        cols = st.columns(cols_per_row)
        for col_i in range(cols_per_row):
            idx = row_i * cols_per_row + col_i
            p = palaces[idx]
            with cols[col_i]:
                if p is None:
                    if row_i == 1 and col_i == 1:
                        st.markdown(f"**命盤中宮**\n\n{center_text}")
                    else:
                        st.empty()
                else:
                    stars = "、".join(p.main_stars) if p.main_stars else "無主星"
                    transforms = " ".join(p.transformations) if p.transformations else ""
                    st.markdown(
                        f"**{p.name}**（{p.earthly_branch}）\n\n"
                        f"{stars}\n\n"
                        f"{'🔶 ' + transforms if transforms else ''}"
                    )


def render_ziwei_formal_table(ziwei_chart):
    """Render 12-palace data as a readable table with 宮位/地支/主星/輔煞/四化/解讀摘要 columns."""
    import pandas as pd
    from engines.ziwei import _interpret_palace

    palaces = [
        ziwei_chart.ming_palace, ziwei_chart.brother_palace,
        ziwei_chart.spouse_palace, ziwei_chart.children_palace,
        ziwei_chart.wealth_palace, ziwei_chart.health_palace,
        ziwei_chart.travel_palace, ziwei_chart.friends_palace,
        ziwei_chart.career_palace, ziwei_chart.property_palace,
        ziwei_chart.fortune_palace, ziwei_chart.parents_palace,
    ]

    sihua_display = {
        "化祿": "化祿（機會）", "化權": "化權（主導）",
        "化科": "化科（名聲）", "化忌": "化忌（課題）",
    }
    four_trans = ziwei_chart.four_transformations or {}
    star_cat = getattr(ziwei_chart, "star_categories", {})
    malefic_set = {s for s, c in star_cat.items() if c == "malefic"}

    rows = []
    for p in palaces:
        stars = "、".join(p.main_stars) if p.main_stars else "—"
        tx_strs = []
        for s in p.main_stars:
            if s in four_trans:
                tx = four_trans[s]
                tx_strs.append(sihua_display.get(tx, tx))
        tx_display = " ".join(tx_strs) if tx_strs else "—"
        # Split minor_stars into auspicious and malefic
        aux_stars = [s for s in p.minor_stars if s not in malefic_set]
        sha_stars = [s for s in p.minor_stars if s in malefic_set]
        aux_display = "、".join(aux_stars) if aux_stars else "—"
        sha_display = "、".join(sha_stars) if sha_stars else "—"
        interp = _interpret_palace(p.name, p.main_stars, four_trans)
        interp_short = interp.split("\n")[0]
        if len(interp_short) > 60:
            interp_short = interp_short[:60] + "…"
        rows.append({
            "宮位": p.name,
            "地支": p.earthly_branch,
            "主星": stars,
            "吉輔": aux_display,
            "煞曜": sha_display,
            "四化": tx_display,
            "解讀摘要": interp_short,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_ziwei_auxiliary_table(ziwei_chart):
    """Render auxiliary + malefic star overview table."""
    import pandas as pd

    star_cat = getattr(ziwei_chart, "star_categories", {})
    aux_map = getattr(ziwei_chart, "auxiliary_star_map", {})
    malefic_map = getattr(ziwei_chart, "malefic_star_map", {})
    all_palaces = [
        ziwei_chart.ming_palace, ziwei_chart.brother_palace,
        ziwei_chart.spouse_palace, ziwei_chart.children_palace,
        ziwei_chart.wealth_palace, ziwei_chart.health_palace,
        ziwei_chart.travel_palace, ziwei_chart.friends_palace,
        ziwei_chart.career_palace, ziwei_chart.property_palace,
        ziwei_chart.fortune_palace, ziwei_chart.parents_palace,
    ]
    branch_to_name = {p.earthly_branch: p.name for p in all_palaces}

    _star_hints = {
        "左輔": "貴人輔佐，協作人際支援",
        "右弼": "貴人輔佐，幕後支援力量",
        "文昌": "學習、文書、考試、專業表達",
        "文曲": "藝術、口才、才藝、情感表達",
        "天魁": "天乙貴人，關鍵提攜機會",
        "天鉞": "玉堂貴人，溫柔助力與緣分",
        "祿存": "資源守成，財庫穩固之象",
        "擎羊": "衝突刀鋒，果斷破局之力",
        "陀羅": "拖延拉扯，慢性執著之象",
        "火星": "爆發行動，急躁突發之火",
        "鈴星": "內在焦躁，警覺突發之象",
        "地空": "空性落差，理想與現實的距離",
        "地劫": "資源破耗，斷裂與重建之象",
    }

    rows = []
    all_stars = {**{s: "auspicious" for s in aux_map}, **{s: "malefic" for s in malefic_map}}
    for star, cat in all_stars.items():
        branch = aux_map.get(star) or malefic_map.get(star, "—")
        palace = branch_to_name.get(branch, "—")
        cat_label = "吉輔" if cat == "auspicious" else "煞曜"
        hint = _star_hints.get(star, "")
        rows.append({
            "星曜": star,
            "類別": cat_label,
            "所在宮位": palace,
            "地支": branch,
            "解讀方向": hint,
        })

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.caption("輔煞星資料尚未計算（需出生時辰或正式排盤）。")


def render_daxian_table(ziwei_chart):
    """Render Da Xian 10-year period table."""
    import pandas as pd

    da_xian = getattr(ziwei_chart, "da_xian", [])
    if not da_xian:
        st.caption("大限資料尚未計算。")
        return

    rows = []
    for d in da_xian:
        main = "、".join(d.main_stars) if d.main_stars else "—"
        aux = "、".join(d.auxiliary_stars) if d.auxiliary_stars else "—"
        rows.append({
            "年齡區間": f"{d.start_age}–{d.end_age} 歲",
            "宮位": d.palace_name,
            "地支": d.branch,
            "主星": main,
            "輔星 / 煞星": aux,
            "解讀": d.interpretation,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_numerology_card(num_chart):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("生命靈數", num_chart.life_path_number)
    with col2:
        st.metric("生日數", num_chart.birthday_number)
    with col3:
        st.metric("天賦數", num_chart.talent_number)
    with col4:
        st.metric("個人年", num_chart.personal_year)


def render_synthesis_section(synthesis):
    tabs = st.tabs([
        "核心人格", "情緒與行動", "感情", "事業", "財富",
        "人際", "家庭", "陰影課題", "天賦", "建議"
    ])
    with tabs[0]:
        st.markdown(synthesis.core_personality)
    with tabs[1]:
        st.markdown("**情緒模式**\n\n" + synthesis.emotional_pattern)
        st.markdown("---")
        st.markdown("**行動模式**\n\n" + synthesis.action_pattern)
    with tabs[2]:
        st.markdown(synthesis.love_pattern)
    with tabs[3]:
        st.markdown(synthesis.career_pattern)
        if synthesis.suitable_careers:
            st.markdown("**建議職業方向**：" + "、".join(synthesis.suitable_careers))
    with tabs[4]:
        st.markdown(synthesis.wealth_pattern)
    with tabs[5]:
        st.markdown(synthesis.social_pattern)
    with tabs[6]:
        st.markdown(synthesis.family_security)
    with tabs[7]:
        st.markdown(synthesis.stress_shadow)
        st.markdown(synthesis.life_lessons)
        if synthesis.contradictions:
            st.warning("**內在矛盾點**")
            for c in synthesis.contradictions:
                st.write(f"• {c}")
            st.info("**整合建議**")
            for s in synthesis.integration_suggestions:
                st.write(f"• {s}")
    with tabs[8]:
        st.markdown(synthesis.innate_gifts)
        st.markdown("**容易反覆出現的問題**\n\n" + synthesis.recurring_challenges)
    with tabs[9]:
        st.markdown("**今年流年重點**\n\n" + synthesis.one_year_advice)
        st.markdown("---")
        st.markdown("**未來三年趨勢**\n\n" + synthesis.three_year_advice)
