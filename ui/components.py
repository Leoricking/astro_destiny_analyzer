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
