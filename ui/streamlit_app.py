"""
Astro Destiny Analyzer — Streamlit Multi-Page Application
Entry: streamlit run ui/streamlit_app.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from datetime import date, time

# ── Bootstrap ─────────────────────────────────────────────────────────────────
from core.database import init_db
init_db()

from config import APP_NAME, APP_SUBTITLE, APP_VERSION
from core.models import (
    BirthProfile, Gender, BloodType, AnalysisTheme,
    ReportLanguage, ReportLength,
)
from core.validators import validate_birth_date, validate_birth_time, validate_name, validate_city
from reports.generator import ReportGenerator
from reports.pdf_exporter import PdfExporter
from reports.docx_exporter import DocxExporter
from core.database import list_reports, get_report, delete_report, list_birth_profiles, get_setting, set_setting
from ui.components import (
    render_planet_table, render_house_table, render_aspect_table,
    render_bazi_pillars, render_five_element_chart,
    render_ziwei_palace_grid, render_numerology_card, render_synthesis_section,
)

st.set_page_config(
    page_title=APP_NAME,
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar Navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.title(f"✨ {APP_NAME}")
    st.caption(APP_SUBTITLE)
    st.divider()
    page = st.radio(
        "導航",
        ["🏠 首頁", "📝 輸入資料", "🔮 計算命盤", "📄 報告預覽", "📚 歷史報告", "📤 匯出", "⚙️ 設定"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption(f"v{APP_VERSION}")

# ── Session State Defaults ────────────────────────────────────────────────────
defaults = {
    "profile": None,
    "report": None,
    "active_report_id": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 首頁
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 首頁":
    st.title(f"✨ {APP_NAME}")
    st.subheader(APP_SUBTITLE)
    st.markdown("""
    歡迎使用命盤整合分析系統。本系統整合以下五套命理體系，為您生成一份深度個人化的人生分析報告。

    | 模組 | 說明 |
    |------|------|
    | 🌟 西洋占星 | 行星、宮位、相位、上升、天頂等完整星盤 |
    | ☯️ 八字命理 | 四柱、五行、十神、大運、流年 |
    | 🏮 紫微斗數 | 十二宮、十四主星、四化 |
    | 🩸 血型分析 | 個性、感情、職場、財富輔助分析 |
    | 🔢 生命靈數 | 生命靈數、天賦數、個人年運 |

    ### 如何開始？
    1. 點選左側「**📝 輸入資料**」填寫您的出生資訊
    2. 前往「**🔮 計算命盤**」執行分析
    3. 在「**📄 報告預覽**」閱讀完整報告
    4. 透過「**📤 匯出**」下載 Markdown / HTML / Word 檔案

    ---
    > ⚠️ 本系統定位為自我探索與娛樂工具，不構成科學定論、醫療診斷或投資建議。
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("支援命理系統", "5")
    with col2:
        st.metric("報告章節", "32")
    with col3:
        st.metric("報告格式", "Markdown / HTML / Word")

    if st.button("🚀 立即開始分析", type="primary", use_container_width=True):
        st.session_state["_nav"] = "📝 輸入資料"
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 輸入資料
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📝 輸入資料":
    st.title("📝 輸入出生資料")

    with st.form("birth_form"):
        st.subheader("基本資料")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("姓名 / 暱稱 *", placeholder="例：小明")
        with col2:
            gender = st.selectbox(
                "性別（可選填）",
                ["不填寫", "男", "女", "其他"],
            )

        st.subheader("出生日期與時間")
        col1, col2, col3 = st.columns(3)
        with col1:
            birth_year = st.number_input("西元年 *", min_value=1800,
                                         max_value=date.today().year, value=1990)
        with col2:
            birth_month = st.number_input("月 *", min_value=1, max_value=12, value=1)
        with col3:
            birth_day = st.number_input("日 *", min_value=1, max_value=31, value=1)

        time_known = st.checkbox("已知出生時間")
        birth_hour = birth_minute = 0
        if time_known:
            col1, col2 = st.columns(2)
            with col1:
                birth_hour = st.number_input("時（24H）", 0, 23, 12)
            with col2:
                birth_minute = st.number_input("分", 0, 59, 0)

        st.subheader("出生地")
        col1, col2 = st.columns(2)
        with col1:
            birth_city = st.text_input("城市 *", placeholder="例：台北市")
        with col2:
            birth_country = st.text_input("國家 *", placeholder="例：台灣")

        st.subheader("居住地（可選填）")
        col1, col2 = st.columns(2)
        with col1:
            res_city = st.text_input("目前居住城市", placeholder="例：高雄市")
        with col2:
            res_country = st.text_input("目前居住國家", placeholder="例：台灣")

        st.subheader("血型")
        blood_type = st.selectbox("血型", ["Unknown", "A", "B", "O", "AB"])

        st.subheader("分析主題（可複選）")
        theme_options = [t.value for t in AnalysisTheme]
        selected_themes = st.multiselect(
            "請選擇您想深入分析的主題",
            theme_options,
            default=theme_options,
        )

        st.subheader("報告設定")
        col1, col2 = st.columns(2)
        with col1:
            report_lang = st.selectbox("報告語言", ["繁體中文", "簡體中文", "English"])
        with col2:
            report_len = st.selectbox("報告長度", ["簡短版", "標準版", "萬字完整版"])

        submitted = st.form_submit_button("✅ 確認資料", type="primary", use_container_width=True)

    if submitted:
        errors = []
        ok, msg = validate_name(name)
        if not ok:
            errors.append(msg)
        ok, msg = validate_birth_date(int(birth_year), int(birth_month), int(birth_day))
        if not ok:
            errors.append(msg)
        if time_known:
            ok, msg = validate_birth_time(int(birth_hour), int(birth_minute))
            if not ok:
                errors.append(msg)
        ok, msg = validate_city(birth_city)
        if not ok:
            errors.append(msg)
        if not birth_country.strip():
            errors.append("出生國家不得為空。")

        if errors:
            for e in errors:
                st.error(e)
        else:
            gender_map = {"男": Gender.MALE, "女": Gender.FEMALE,
                          "其他": Gender.OTHER, "不填寫": None}
            blood_map = {bt.value: bt for bt in BloodType}
            theme_map = {t.value: t for t in AnalysisTheme}
            lang_map  = {l.value: l for l in ReportLanguage}
            len_map   = {l.value: l for l in ReportLength}

            profile = BirthProfile(
                name=name.strip(),
                gender=gender_map.get(gender),
                birth_date=date(int(birth_year), int(birth_month), int(birth_day)),
                birth_time=time(int(birth_hour), int(birth_minute)) if time_known else None,
                birth_city=birth_city.strip(),
                birth_country=birth_country.strip(),
                residence_city=res_city.strip() or None,
                residence_country=res_country.strip() or None,
                blood_type=blood_map.get(blood_type, BloodType.UNKNOWN),
                themes=[theme_map[t] for t in selected_themes if t in theme_map],
                report_language=lang_map.get(report_lang, ReportLanguage.TRADITIONAL_CHINESE),
                report_length=len_map.get(report_len, ReportLength.STANDARD),
            )
            st.session_state["profile"] = profile
            st.session_state["report"] = None
            st.success(f"✅ 資料已儲存！{name} 的出生資料登錄完成。請前往「🔮 計算命盤」。")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 計算命盤
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔮 計算命盤":
    st.title("🔮 計算命盤")

    if st.session_state["profile"] is None:
        st.warning("請先至「📝 輸入資料」填寫出生資訊。")
        st.stop()

    profile = st.session_state["profile"]
    st.info(f"正在分析：**{profile.name}**（{profile.birth_date}）")

    if st.session_state["report"] is not None:
        st.success("命盤已計算完成。若要重新計算，請點擊下方按鈕。")

    if st.button("🔮 開始計算命盤", type="primary", use_container_width=True):
        with st.spinner("正在運算五套命盤系統，請稍候…"):
            try:
                gen = ReportGenerator()
                report = gen.generate(profile, persist=True)
                st.session_state["report"] = report
                st.success(f"✅ 命盤計算完成！報告 ID：{report.report_id}")
            except Exception as e:
                st.error(f"計算失敗：{e}")
                st.exception(e)
        st.rerun()

    if st.session_state["report"] is not None:
        report = st.session_state["report"]
        st.divider()
        st.subheader("命盤速覽")

        tab_w, tab_b, tab_z, tab_n = st.tabs(["🌟 西洋占星", "☯️ 八字", "🏮 紫微", "🔢 靈數"])

        with tab_w:
            wc = report.western_chart
            if wc:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    sun_pos = next((p for p in wc.planet_positions if p.planet.value == "太陽"), None)
                    st.metric("太陽星座", sun_pos.sign.value if sun_pos else "─")
                with col2:
                    moon_pos = next((p for p in wc.planet_positions if p.planet.value == "月亮"), None)
                    st.metric("月亮星座", moon_pos.sign.value if moon_pos else "─")
                with col3:
                    st.metric("上升星座", wc.ascendant.value)
                with col4:
                    st.metric("天頂 MC", wc.mc.value)
                if wc.is_mock:
                    st.caption("⚠️ 西洋占星目前使用近似計算（太陽使用真實演算法；其餘行星為Mock）。配置 Swiss Ephemeris 可獲得完整精確星曆。")
                with st.expander("行星位置詳表"):
                    render_planet_table(wc.planet_positions)
                with st.expander("宮位分析"):
                    render_house_table(wc.houses)
                with st.expander("主要相位"):
                    render_aspect_table(wc.aspects)

        with tab_b:
            bc = report.bazi_chart
            if bc:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("日主", f"{bc.day_master.value}（{bc.day_master_element.value}）")
                with col2:
                    fav = "、".join(e.value for e in bc.favorable_elements)
                    st.metric("喜用神", fav)
                render_bazi_pillars(bc)
                with st.expander("五行比例"):
                    render_five_element_chart(bc)
                with st.expander("大運"):
                    import pandas as pd
                    dy_rows = [{"起始": f"{dy.start_age}歲", "結束": f"{dy.end_age}歲",
                                "天干地支": dy.stem.value + dy.branch.value}
                               for dy in bc.da_yun]
                    st.dataframe(pd.DataFrame(dy_rows), hide_index=True)

        with tab_z:
            zc = report.ziwei_chart
            if zc:
                if zc.is_mock:
                    st.caption("⚠️ 紫微斗數目前為 Mock 布局。完整排盤演算法開發中。")
                render_ziwei_palace_grid(zc)

        with tab_n:
            nc = report.numerology_chart
            if nc:
                render_numerology_card(nc)
                st.markdown(f"**{nc.life_path_description}**")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 報告預覽
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📄 報告預覽":
    st.title("📄 報告預覽")

    if st.session_state["report"] is None:
        st.warning("尚無報告，請先至「🔮 計算命盤」產生報告。")
        st.stop()

    report = st.session_state["report"]
    st.subheader(f"{report.profile.name} 的命盤整合分析報告")
    st.caption(f"生成時間：{report.created_at} ｜ 報告長度：{report.profile.report_length.value}")

    view_mode = st.radio("顯示模式", ["整合分析（互動式）", "Markdown 原文"], horizontal=True)

    if view_mode == "整合分析（互動式）":
        if report.synthesis:
            render_synthesis_section(report.synthesis)
        else:
            st.warning("整合分析尚未產生。")
    else:
        from reports.markdown_exporter import MarkdownExporter
        md_text = MarkdownExporter().export(report)
        st.markdown(md_text, unsafe_allow_html=False)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 歷史報告
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📚 歷史報告":
    st.title("📚 歷史報告")

    reports = list_reports(limit=50)
    if not reports:
        st.info("尚無歷史報告。請先分析一個命盤。")
        st.stop()

    import pandas as pd
    df = pd.DataFrame(reports)
    df_display = df[["id", "name", "birth_date", "title", "language", "length", "created_at"]].copy()
    df_display.columns = ["ID", "姓名", "出生日期", "報告標題", "語言", "長度", "生成時間"]

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        load_id = st.number_input("載入報告 ID", min_value=1, step=1)
        if st.button("載入此報告"):
            row = get_report(int(load_id))
            if row:
                st.session_state["active_report_id"] = int(load_id)
                st.session_state["_loaded_report_markdown"] = row["markdown_body"]
                st.success(f"已載入報告 ID {load_id}")
            else:
                st.error("找不到此報告 ID。")
    with col2:
        del_id = st.number_input("刪除報告 ID", min_value=1, step=1, key="del_id")
        if st.button("刪除此報告", type="secondary"):
            delete_report(int(del_id))
            st.success(f"報告 ID {del_id} 已刪除。")
            st.rerun()

    if st.session_state.get("_loaded_report_markdown"):
        st.divider()
        st.markdown("### 已載入的報告內容")
        st.markdown(st.session_state["_loaded_report_markdown"])


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 匯出
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📤 匯出":
    st.title("📤 匯出報告")

    if st.session_state["report"] is None:
        st.warning("尚無報告，請先計算命盤。")
        st.stop()

    report = st.session_state["report"]
    st.info(f"目前報告：**{report.profile.name}**（{report.created_at}）")

    from reports.markdown_exporter import MarkdownExporter
    from reports.html_exporter import HtmlExporter

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        md_content = MarkdownExporter().export(report)
        st.download_button(
            label="📝 下載 Markdown",
            data=md_content.encode("utf-8"),
            file_name=f"{report.profile.name}_命盤報告.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col2:
        html_content = HtmlExporter().export(report)
        st.download_button(
            label="🌐 下載 HTML",
            data=html_content.encode("utf-8"),
            file_name=f"{report.profile.name}_命盤報告.html",
            mime="text/html",
            use_container_width=True,
        )

    with col3:
        pdf_exp = PdfExporter()
        if pdf_exp.is_available():
            try:
                pdf_bytes = pdf_exp.export(report)
                st.download_button(
                    label="📕 下載 PDF",
                    data=pdf_bytes,
                    file_name=f"{report.profile.name}_命盤報告.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except NotImplementedError as e:
                st.button("📕 PDF（尚未設定）", disabled=True, use_container_width=True)
                st.caption(str(e))
        else:
            st.button("📕 PDF（需安裝 WeasyPrint）", disabled=True, use_container_width=True)
            st.caption("pip install weasyprint")

    with col4:
        docx_exp = DocxExporter()
        if docx_exp.is_available():
            try:
                docx_bytes = docx_exp.export(report)
                st.download_button(
                    label="📘 下載 Word",
                    data=docx_bytes,
                    file_name=f"{report.profile.name}_命盤報告.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            except Exception as e:
                st.button("📘 Word 匯出失敗", disabled=True, use_container_width=True)
                st.caption(str(e))
        else:
            st.button("📘 Word（需安裝 python-docx）", disabled=True, use_container_width=True)
            st.caption("pip install python-docx")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 設定
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️ 設定":
    st.title("⚙️ 應用程式設定")

    st.subheader("系統資訊")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**版本**：{APP_VERSION}")
        from config import DB_PATH
        st.write(f"**資料庫**：`{DB_PATH}`")
    with col2:
        from config import SWISSEPH_DATA_PATH
        st.write(f"**Swiss Ephemeris**：{'已設定 ✅' if SWISSEPH_DATA_PATH else '未設定（使用 Mock）⚠️'}")

    st.divider()
    st.subheader("Swiss Ephemeris 設定（可選）")
    st.caption("設定後可使用精確星曆計算西洋星盤，需先安裝 pyswisseph 並下載星曆資料。")
    sweph_path = st.text_input(
        "Swiss Ephemeris 資料路徑",
        value=get_setting("swisseph_path", ""),
        placeholder="例：/usr/share/swisseph",
    )
    if st.button("儲存設定"):
        set_setting("swisseph_path", sweph_path)
        st.success("設定已儲存。請重新啟動應用程式以生效。")

    st.divider()
    st.subheader("資料管理")
    reports = list_reports(limit=1)
    profiles = list_birth_profiles(limit=1)
    col1, col2 = st.columns(2)
    with col1:
        full_reports = list_reports(limit=9999)
        st.metric("已儲存報告數", len(full_reports))
    with col2:
        full_profiles = list_birth_profiles(limit=9999)
        st.metric("已儲存命盤數", len(full_profiles))
