"""
Astro Destiny Analyzer — Streamlit Multi-Page Application
V1.3.8: Birth country default & safe navigation fix.
  - input page uses a reactive container instead of st.form so birth time stays in the correct section
  - one-time migration prevents stale sessions from showing birth year 1800 as the default
  - All input widgets keyed to st.session_state → state persists across page switches
  - 計算命盤 page: 返回修改資料 / 清空並重新輸入 / 重新計算 buttons
  - Programmatic navigation via nav_page session key
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

from config import APP_NAME, APP_SUBTITLE, APP_VERSION, TAIWAN_CITY_DISPLAY_NAMES, lookup_location
from core.models import (
    BirthProfile, Gender, BloodType, AnalysisTheme,
    ReportLanguage, ReportLength,
)
from core.validators import validate_birth_date, validate_birth_time, validate_name, validate_city
from reports.generator import ReportGenerator
from reports.pdf_exporter import PdfExporter
from reports.docx_exporter import DocxExporter
from reports.utils import make_export_filename
from core.database import (
    list_reports, get_report, delete_report,
    list_birth_profiles, get_setting, set_setting,
)
from ui.components import (
    render_planet_table, render_house_table, render_aspect_table,
    render_bazi_pillars, render_five_element_chart,
    render_ziwei_palace_grid, render_ziwei_formal_table,
    render_ziwei_auxiliary_table, render_daxian_table,
    render_numerology_card, render_synthesis_section,
)

st.set_page_config(
    page_title=APP_NAME,
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

_PAGES = [
    "🏠 首頁", "📝 輸入資料", "🔮 計算命盤",
    "📄 報告預覽", "📚 歷史報告", "📤 匯出", "⚙️ 設定",
]

_DEFAULT_THEME_VALUES = [t.value for t in AnalysisTheme]

# ── Session state: global defaults (never overwrite existing values) ───────────
_GLOBAL_DEFAULTS: dict = {
    "profile": None,
    "report": None,
    "active_report_id": None,
    "nav_page": "🏠 首頁",
}
for _k, _v in _GLOBAL_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Session state: input field defaults ───────────────────────────────────────
_INPUT_DEFAULTS: dict = {
    "input_name": "",
    "input_gender": "不填寫",
    "input_birth_year": 1990,
    "input_birth_month": 1,
    "input_birth_day": 1,
    "birth_time_is_known": False,
    "input_birth_hour": 12,
    "input_birth_minute": 0,
    "input_tw_city_sel": "其他 / 手動輸入",
    "input_birth_city": "",
    "input_birth_country": "台灣",
    "input_res_city": "",
    "input_res_country": "",
    "input_blood_type": "Unknown",
    "input_themes": list(_DEFAULT_THEME_VALUES),
    "input_report_lang": "繁體中文",
    "input_report_len": "標準版",
    "input_manual_lat": 0.0,
    "input_manual_lon": 0.0,
    "input_manual_tz": 8.0,
    "input_use_manual_latlon": False,
}
for _k, _v in _INPUT_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = list(_v) if isinstance(_v, list) else _v

# ── One-time migration for old Streamlit sessions ─────────────────────────────
# Earlier UI versions could leave input_birth_year at the old number_input minimum
# value (1800). Do not overwrite normal user edits; only migrate once when no
# profile/report has been created yet and a stale pre-1900 value is detected.
if (
    st.session_state.get("input_birth_year", 1990) <= 1900
    and not st.session_state.get("profile")
    and not st.session_state.get("report")
    and not st.session_state.get("_birth_year_default_migrated")
):
    st.session_state["input_birth_year"] = _INPUT_DEFAULTS["input_birth_year"]
st.session_state["_birth_year_default_migrated"] = True

# Migrate old blank country state to Taiwan for Taiwan-first workflow.
# This only applies before a profile/report is created, so it will not overwrite
# a saved chart or a deliberate later edit.
if (
    not st.session_state.get("input_birth_country")
    and not st.session_state.get("profile")
    and not st.session_state.get("report")
):
    st.session_state["input_birth_country"] = _INPUT_DEFAULTS["input_birth_country"]

# Ensure analysis themes default to select-all for first use / old blank sessions.
# This only applies before a profile/report exists, so it will not overwrite
# deliberate edits after a chart has been created.
if (
    not st.session_state.get("input_themes")
    and not st.session_state.get("profile")
    and not st.session_state.get("report")
):
    st.session_state["input_themes"] = list(_DEFAULT_THEME_VALUES)

# Migrate stale edge values left by older number_input sessions.
# Only apply before a profile/report exists and when manual override is disabled.
if (
    not st.session_state.get("profile")
    and not st.session_state.get("report")
    and not st.session_state.get("input_use_manual_latlon")
):
    if st.session_state.get("input_manual_lat") in (-90.0, None):
        st.session_state["input_manual_lat"] = _INPUT_DEFAULTS["input_manual_lat"]
    if st.session_state.get("input_manual_lon") in (-180.0, None):
        st.session_state["input_manual_lon"] = _INPUT_DEFAULTS["input_manual_lon"]
    if st.session_state.get("input_manual_tz") in (-12.0, None):
        st.session_state["input_manual_tz"] = _INPUT_DEFAULTS["input_manual_tz"]


# ── Navigation helper ─────────────────────────────────────────────────────────

def _go_to_page(page_name: str) -> None:
    """Programmatically navigate to a page and rerun safely.

    The sidebar radio owns ``st.session_state["nav_page"]``. Streamlit raises
    an exception if that widget-backed key is modified after the widget has
    already been instantiated in the same run. Store the requested page in a
    pending key and apply it before creating the sidebar radio on the next run.
    """
    if page_name in _PAGES:
        st.session_state["_pending_nav_page"] = page_name
    st.rerun()


def _clear_input_state() -> None:
    """Reset all input fields to defaults and clear profile / report."""
    for k, v in _INPUT_DEFAULTS.items():
        st.session_state[k] = list(v) if isinstance(v, list) else v
    st.session_state["profile"] = None
    st.session_state["report"] = None


def _sync_input_state_from_profile(profile: BirthProfile) -> None:
    """Load a saved BirthProfile back into input widgets for editing.

    This keeps 「返回修改資料」 from showing blank/default fields after a
    chart has already been calculated. It intentionally does not clear the
    report; the report is invalidated only after the user confirms updated
    data.
    """
    if profile is None:
        return

    gender_value = profile.gender.value if profile.gender else "unknown"
    gender_to_label = {
        "male": "男",
        "female": "女",
        "other": "其他",
        "unknown": "不填寫",
    }

    city = getattr(profile, "birth_city", "") or ""
    if city in TAIWAN_CITY_DISPLAY_NAMES:
        st.session_state["input_tw_city_sel"] = city
        st.session_state["input_birth_city"] = ""
        use_manual = False
    else:
        st.session_state["input_tw_city_sel"] = "其他 / 手動輸入"
        st.session_state["input_birth_city"] = city
        use_manual = bool(
            getattr(profile, "birth_latitude", None) is not None
            and getattr(profile, "birth_longitude", None) is not None
        )

    st.session_state["input_name"] = profile.name or ""
    st.session_state["input_gender"] = gender_to_label.get(gender_value, "不填寫")
    st.session_state["input_birth_year"] = profile.birth_date.year
    st.session_state["input_birth_month"] = profile.birth_date.month
    st.session_state["input_birth_day"] = profile.birth_date.day
    st.session_state["birth_time_is_known"] = bool(
        getattr(profile, "birth_time_is_known", bool(profile.birth_time))
        and profile.birth_time is not None
    )
    if profile.birth_time is not None:
        st.session_state["input_birth_hour"] = profile.birth_time.hour
        st.session_state["input_birth_minute"] = profile.birth_time.minute
    else:
        st.session_state["input_birth_hour"] = _INPUT_DEFAULTS["input_birth_hour"]
        st.session_state["input_birth_minute"] = _INPUT_DEFAULTS["input_birth_minute"]

    st.session_state["input_birth_country"] = getattr(profile, "birth_country", None) or "台灣"
    st.session_state["input_res_city"] = getattr(profile, "residence_city", None) or ""
    st.session_state["input_res_country"] = getattr(profile, "residence_country", None) or ""
    st.session_state["input_blood_type"] = profile.blood_type.value if profile.blood_type else "Unknown"
    profile_themes = [t.value for t in getattr(profile, "themes", [])]
    st.session_state["input_themes"] = profile_themes or list(_DEFAULT_THEME_VALUES)
    st.session_state["input_report_lang"] = profile.report_language.value
    st.session_state["input_report_len"] = profile.report_length.value

    st.session_state["input_manual_lat"] = float(
        getattr(profile, "birth_latitude", None)
        if getattr(profile, "birth_latitude", None) is not None
        else _INPUT_DEFAULTS["input_manual_lat"]
    )
    st.session_state["input_manual_lon"] = float(
        getattr(profile, "birth_longitude", None)
        if getattr(profile, "birth_longitude", None) is not None
        else _INPUT_DEFAULTS["input_manual_lon"]
    )
    st.session_state["input_manual_tz"] = float(
        getattr(profile, "birth_timezone_offset", None)
        if getattr(profile, "birth_timezone_offset", None) is not None
        else _INPUT_DEFAULTS["input_manual_tz"]
    )
    st.session_state["input_use_manual_latlon"] = use_manual


# Apply pending navigation before the radio widget is instantiated.
# Streamlit does not allow modifying a widget-backed session_state key after
# the widget has been created in the same run.
if "_pending_nav_page" in st.session_state:
    _pending_page = st.session_state.pop("_pending_nav_page")
    if _pending_page in _PAGES:
        st.session_state["nav_page"] = _pending_page


# ── Sidebar Navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.title(f"✨ {APP_NAME}")
    st.caption(APP_SUBTITLE)
    st.divider()
    page = st.radio(
        "導航",
        _PAGES,
        key="nav_page",
        label_visibility="collapsed",
    )
    st.divider()
    st.caption(f"v{APP_VERSION}")


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
        _go_to_page("📝 輸入資料")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 輸入資料
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📝 輸入資料":
    st.title("📝 輸入出生資料")

    # ── Reactive input container ──────────────────────────────────────────────
    # Do not use st.form here: birth_time_is_known must rerender immediately so
    # the time fields appear/disappear without an extra submit click.
    with st.container(border=True):
        st.subheader("基本資料")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("姓名 / 暱稱 *", placeholder="例：小明", key="input_name")
        with col2:
            st.selectbox("性別（可選填）", ["不填寫", "男", "女", "其他"],
                         key="input_gender")

        st.subheader("出生日期")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input("西元年 *", min_value=1900, max_value=date.today().year,
                            step=1, key="input_birth_year")
        with col2:
            st.number_input("月 *", min_value=1, max_value=12, step=1,
                            key="input_birth_month")
        with col3:
            st.number_input("日 *", min_value=1, max_value=31, step=1,
                            key="input_birth_day")

        st.subheader("出生時間")
        st.checkbox(
            "我知道精確出生時間",
            key="birth_time_is_known",
        )
        if st.session_state["birth_time_is_known"]:
            col_h, col_m = st.columns(2)
            with col_h:
                st.number_input("時（24H）", min_value=0, max_value=23, step=1,
                                key="input_birth_hour")
            with col_m:
                st.number_input("分", min_value=0, max_value=59, step=1,
                                key="input_birth_minute")
            st.caption(
                "ℹ️ 23:00～23:59 子時換日規則可依派別不同；本版預設晚子時不換日（late_zi_same_day）。"
            )
        else:
            st.caption(
                "⚠️ 出生時間未填：行星以中午 12:00 估算（可能有誤差）；"
                "上升星座與天頂無法精確計算。"
            )

        st.subheader("出生地")
        col1, col2 = st.columns(2)
        with col1:
            tw_city_options = ["其他 / 手動輸入"] + TAIWAN_CITY_DISPLAY_NAMES
            tw_city_sel = st.selectbox("台灣城市（快速選擇）", tw_city_options,
                                       key="input_tw_city_sel")
        with col2:
            st.text_input(
                "國家 *",
                placeholder="例：台灣",
                key="input_birth_country",
                help="預設為台灣；若為海外出生地，可自行修改國家並使用進階經緯度。",
            )

        if tw_city_sel == "其他 / 手動輸入":
            st.text_input("城市（手動輸入）*", placeholder="例：東京、首爾、Paris",
                          key="input_birth_city")
        else:
            st.caption(f"已選擇：{tw_city_sel}（將自動帶入經緯度）")

        with st.expander("進階：手動輸入經緯度（可選）"):
            st.caption(
                "若城市從上方下拉選單可自動取得，可不填。"
                "若出生地非台灣，請補充以精確計算上升與天頂。"
            )
            adv1, adv2 = st.columns(2)
            with adv1:
                st.number_input("出生地緯度（南為負）", min_value=-90.0, max_value=90.0,
                                step=0.0001, format="%.4f", key="input_manual_lat")
            with adv2:
                st.number_input("出生地經度（西為負）", min_value=-180.0, max_value=180.0,
                                step=0.0001, format="%.4f", key="input_manual_lon")
            st.number_input("時區偏移（UTC+？，台灣=8）", min_value=-12.0, max_value=14.0,
                            step=0.5, key="input_manual_tz")
            st.checkbox("使用以上手動經緯度覆蓋自動查詢",
                        key="input_use_manual_latlon")

        st.subheader("居住地（可選填）")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("目前居住城市", placeholder="例：高雄市", key="input_res_city")
        with col2:
            st.text_input("目前居住國家", placeholder="例：台灣", key="input_res_country")

        st.subheader("血型")
        st.selectbox("血型", ["Unknown", "A", "B", "O", "AB"], key="input_blood_type")

        st.subheader("分析主題（可複選）")
        theme_options = list(_DEFAULT_THEME_VALUES)
        if not st.session_state.get("input_themes"):
            st.session_state["input_themes"] = list(_DEFAULT_THEME_VALUES)
        st.multiselect("請選擇您想深入分析的主題", theme_options,
                       key="input_themes")

        st.subheader("報告設定")
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("報告語言", ["繁體中文", "簡體中文", "English"],
                         key="input_report_lang")
        with col2:
            st.selectbox("報告長度", ["簡短版", "標準版", "萬字完整版"],
                         key="input_report_len")

        submitted = st.button("✅ 確認資料", type="primary",
                              use_container_width=True)

    # ── Submit handler ────────────────────────────────────────────────────────
    if submitted:
        ss = st.session_state

        # Read all values from session_state (keyed widgets update ss on submit)
        name         = str(ss.get("input_name", "")).strip()
        birth_year   = int(ss.get("input_birth_year", 1990))
        birth_month  = int(ss.get("input_birth_month", 1))
        birth_day    = int(ss.get("input_birth_day", 1))
        time_known   = bool(ss.get("birth_time_is_known", False))
        birth_hour   = int(ss.get("input_birth_hour", 12))
        birth_minute = int(ss.get("input_birth_minute", 0))
        tw_city_sel  = ss.get("input_tw_city_sel", "其他 / 手動輸入")
        birth_city   = (tw_city_sel if tw_city_sel != "其他 / 手動輸入"
                        else str(ss.get("input_birth_city", "")).strip())
        birth_country = str(ss.get("input_birth_country", "")).strip()
        res_city     = str(ss.get("input_res_city", "")).strip()
        res_country  = str(ss.get("input_res_country", "")).strip()
        blood_type   = ss.get("input_blood_type", "Unknown")
        themes       = ss.get("input_themes", [])
        report_lang  = ss.get("input_report_lang", "繁體中文")
        report_len   = ss.get("input_report_len", "標準版")
        manual_lat   = float(ss.get("input_manual_lat", 0.0))
        manual_lon   = float(ss.get("input_manual_lon", 0.0))
        manual_tz    = float(ss.get("input_manual_tz", 8.0))
        use_manual   = bool(ss.get("input_use_manual_latlon", False))

        # Validate
        errors = []
        ok, msg = validate_name(name)
        if not ok:
            errors.append(msg)
        ok, msg = validate_birth_date(birth_year, birth_month, birth_day)
        if not ok:
            errors.append(msg)
        if time_known:
            ok, msg = validate_birth_time(birth_hour, birth_minute)
            if not ok:
                errors.append(msg)
        ok, msg = validate_city(birth_city)
        if not ok:
            errors.append(msg)
        if not birth_country:
            errors.append("出生國家不得為空。")

        if errors:
            for e in errors:
                st.error(e)
        else:
            gender_map = {"男": Gender.MALE, "女": Gender.FEMALE,
                          "其他": Gender.OTHER, "不填寫": None}
            blood_map  = {bt.value: bt for bt in BloodType}
            theme_map  = {t.value: t for t in AnalysisTheme}
            lang_map   = {l.value: l for l in ReportLanguage}
            len_map    = {l.value: l for l in ReportLength}

            # Resolve lat/lon: manual override > city lookup
            resolved_lat = resolved_lon = resolved_tz_offset = None
            resolved_tz = None
            if use_manual and (manual_lat != 0.0 or manual_lon != 0.0):
                resolved_lat = manual_lat
                resolved_lon = manual_lon
                resolved_tz_offset = manual_tz
            else:
                loc = lookup_location(birth_city)
                if loc:
                    resolved_lat = loc["lat"]
                    resolved_lon = loc["lon"]
                    resolved_tz  = loc["tz"]
                    resolved_tz_offset = float(loc["utc_offset"])

            profile = BirthProfile(
                name=name,
                gender=gender_map.get(ss.get("input_gender", "不填寫")),
                birth_date=date(birth_year, birth_month, birth_day),
                birth_time=time(birth_hour, birth_minute) if time_known else None,
                birth_city=birth_city,
                birth_country=birth_country,
                residence_city=res_city or None,
                residence_country=res_country or None,
                blood_type=blood_map.get(blood_type, BloodType.UNKNOWN),
                themes=[theme_map[t] for t in themes if t in theme_map],
                report_language=lang_map.get(report_lang, ReportLanguage.TRADITIONAL_CHINESE),
                report_length=len_map.get(report_len, ReportLength.STANDARD),
                birth_latitude=resolved_lat,
                birth_longitude=resolved_lon,
                birth_timezone=resolved_tz,
                birth_timezone_offset=resolved_tz_offset,
                birth_time_is_known=time_known,
            )
            st.session_state["profile"] = profile
            st.session_state["report"] = None   # invalidate old report

            # Feedback messages
            if resolved_lat is not None:
                st.info(f"📍 已取得出生地座標：緯度 {resolved_lat:.4f}，經度 {resolved_lon:.4f}")
            else:
                st.warning("⚠️ 未取得出生地經緯度，上升與天頂將無法精確計算。")
            if not time_known:
                st.warning("⚠️ 未填寫出生時間，上升與天頂將無法精確計算。")
            if time_known and resolved_lat is not None:
                st.success("✅ 出生時間與地點完整，可精準計算上升星座（ASC）與天頂（MC）。")
            st.success(
                f"✅ 資料已儲存！{name} 的出生資料登錄完成。請前往「🔮 計算命盤」。"
            )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 計算命盤
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔮 計算命盤":
    st.title("🔮 計算命盤")

    profile = st.session_state.get("profile")

    if profile is None:
        st.warning("尚未輸入出生資料，請先前往輸入資料頁面。")
        if st.button("📝 前往輸入資料", type="primary"):
            _go_to_page("📝 輸入資料")
        st.stop()

    # Profile summary
    time_label = profile.birth_time.strftime("%H:%M") if profile.birth_time else "未知"
    loc_label  = profile.birth_city or "未提供"
    st.info(
        f"**目前資料：{profile.name}**　｜　"
        f"出生日期：{profile.birth_date}　｜　"
        f"出生時間：{time_label}　｜　"
        f"出生地：{loc_label}"
    )

    # Navigation buttons (always visible when profile exists)
    col_edit, col_clear = st.columns(2)
    with col_edit:
        if st.button("📝 返回修改資料", use_container_width=True):
            _sync_input_state_from_profile(profile)
            _go_to_page("📝 輸入資料")
    with col_clear:
        if st.button("🗑️ 清空並重新輸入", use_container_width=True, type="secondary"):
            _clear_input_state()
            _go_to_page("📝 輸入資料")

    st.divider()

    report = st.session_state.get("report")
    if report is not None:
        st.success(f"✅ 命盤已計算完成！報告 ID：{report.report_id}")
        col_recalc, col_preview = st.columns(2)
        with col_recalc:
            do_calculate = st.button("🔄 重新計算", type="primary",
                                     use_container_width=True)
        with col_preview:
            if st.button("📄 前往報告預覽", use_container_width=True):
                _go_to_page("📄 報告預覽")
    else:
        do_calculate = st.button("🔮 開始計算命盤", type="primary",
                                 use_container_width=True)

    if do_calculate:
        with st.spinner("正在運算五套命盤系統，請稍候…"):
            try:
                gen = ReportGenerator()
                new_report = gen.generate(profile, persist=True)
                st.session_state["report"] = new_report
            except Exception as e:
                st.error(f"計算失敗：{e}")
                st.exception(e)
        st.rerun()

    # Show tabs when report is available
    if st.session_state.get("report") is not None:
        report = st.session_state["report"]
        st.divider()
        st.subheader("命盤速覽")

        tab_w, tab_b, tab_z, tab_n = st.tabs(
            ["🌟 西洋占星", "☯️ 八字", "🏮 紫微", "🔢 靈數"]
        )

        with tab_w:
            wc = report.western_chart
            if wc:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    sun_pos = next(
                        (p for p in wc.planet_positions if p.planet.value == "太陽"), None)
                    st.metric("太陽星座", sun_pos.sign.value if sun_pos else "─")
                with col2:
                    moon_pos = next(
                        (p for p in wc.planet_positions if p.planet.value == "月亮"), None)
                    st.metric("月亮星座", moon_pos.sign.value if moon_pos else "─")
                with col3:
                    if wc.ascendant_accuracy == "precise":
                        st.metric("上升星座", wc.ascendant.value)
                    else:
                        st.metric("上升星座", "─ 需補充資料")
                with col4:
                    if wc.mc_accuracy == "precise":
                        st.metric("天頂 MC", wc.mc.value)
                    else:
                        st.metric("天頂 MC", "─ 需補充資料")

                mode = wc.calculation_mode
                if mode == "swiss_ephemeris":
                    st.success("🔭 Swiss Ephemeris 精確計算（行星 + 上升 + 天頂）")
                elif mode == "partial_real":
                    st.info(
                        "🔭 Swiss Ephemeris 行星計算；上升與天頂需要出生時間與經緯度。"
                    )
                else:
                    st.warning("⚠️ Mock 計算層（pyswisseph 不可用）。")

                if wc.accuracy_note:
                    st.caption(wc.accuracy_note)
                if wc.ascendant_accuracy != "precise":
                    st.caption(
                        "ℹ️ 上升與天頂：請在「輸入資料」頁補填精確出生時間與出生地經緯度。"
                    )

                with st.expander("行星位置詳表"):
                    render_planet_table(wc.planet_positions)
                with st.expander("宮位分析"):
                    render_house_table(wc.houses)
                with st.expander("主要相位"):
                    render_aspect_table(wc.aspects)

        with tab_b:
            bc = report.bazi_chart
            if bc:
                if bc.accuracy_note:
                    st.caption(f"ℹ️ {bc.accuracy_note}")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("日主",
                              f"{bc.day_master.value}（{bc.day_master_element.value}）")
                with col2:
                    fav = "、".join(e.value for e in bc.favorable_elements)
                    st.metric("喜用神", fav)
                render_bazi_pillars(bc)
                with st.expander("五行比例"):
                    render_five_element_chart(bc)
                with st.expander("大運"):
                    import pandas as pd
                    dy_rows = [
                        {"起始": f"{dy.start_age}歲", "結束": f"{dy.end_age}歲",
                         "天干地支": dy.stem.value + dy.branch.value}
                        for dy in bc.da_yun
                    ]
                    st.dataframe(pd.DataFrame(dy_rows), hide_index=True)

        with tab_z:
            zc = report.ziwei_chart
            if zc:
                from engines.ziwei import _interpret_main_star, _interpret_palace, _MAIN_STARS_14

                mode = getattr(zc, "calculation_mode", "mock_fallback")

                # ── A. 排盤狀態卡片 ─────────────────────────────────────────
                with st.container(border=True):
                    mode_labels = {
                        "formal_layout_phase1": "正式排盤 Phase 1",
                        "partial_lunar_only": "只有農曆資料，缺出生時辰",
                        "mock_fallback": "Fallback（農曆轉換不可用）",
                    }
                    st.markdown(f"**排盤模式**：{mode_labels.get(mode, mode)}")
                    if mode == "formal_layout_phase1":
                        st.success(
                            "紫微斗數 V1.5.5 正式排盤：命宮、身宮、十四主星、四化、"
                            "核心輔星、六煞與大限 Phase 1 已完成。"
                            " 尚未加入大限四化、流年、流月。"
                        )
                    elif mode == "partial_lunar_only":
                        st.warning(
                            "⚠️ 缺少出生時辰，命宮 / 身宮 / 主星不可視為精準。"
                            " 部分輔星（文昌文曲、火鈴空劫）需出生時辰方可安置。"
                        )
                    else:
                        st.error(
                            "農曆轉換或紫微正式排盤不可用，目前使用 fallback。"
                        )
                    accuracy = getattr(zc, "accuracy_note", "")
                    if accuracy:
                        st.caption(f"ℹ️ {accuracy}")

                # ── B. 基本盤資訊卡片 ────────────────────────────────────────
                with st.container(border=True):
                    st.markdown("**基本盤資訊**")
                    info_cols = st.columns(6)
                    with info_cols[0]:
                        if zc.lunar_year:
                            leap_mark = "（閏）" if zc.lunar_is_leap_month else ""
                            st.metric(
                                "農曆生日",
                                f"{zc.lunar_year}/{zc.lunar_month}{leap_mark}/{zc.lunar_day}"
                            )
                    with info_cols[1]:
                        if zc.birth_hour_branch:
                            st.metric("出生時辰", zc.birth_hour_branch)
                        else:
                            st.metric("出生時辰", "未知")
                    with info_cols[2]:
                        if zc.ming_branch:
                            st.metric("命宮地支", zc.ming_branch)
                    with info_cols[3]:
                        if zc.shen_branch:
                            st.metric("身宮地支", zc.shen_branch)
                    with info_cols[4]:
                        if zc.five_element_bureau:
                            st.metric("五行局", zc.five_element_bureau)
                    with info_cols[5]:
                        year_stem = None
                        if zc.lunar_year:
                            _stems_list = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
                            year_stem = _stems_list[(zc.lunar_year - 4) % 10]
                        if year_stem:
                            st.metric("生年天干", year_stem)

                # ── C. 命宮 / 身宮重點解讀 ─────────────────────────────────
                if zc.ming_palace:
                    with st.container(border=True):
                        st.markdown("**命宮 / 身宮解讀**")
                        cc1, cc2 = st.columns(2)
                        with cc1:
                            st.markdown(
                                f"**命宮（{zc.ming_palace.earthly_branch}）**\n\n"
                                "命宮代表人格主軸、外在行為與人生基調。"
                            )
                            ming_stars = zc.ming_palace.main_stars
                            if ming_stars:
                                st.markdown(f"主星：{'、'.join(ming_stars)}")
                                for s in ming_stars:
                                    interp = _interpret_main_star(s)
                                    if interp:
                                        st.caption(interp)
                            else:
                                st.caption("命宮無主星（空宮）。")
                        with cc2:
                            shen_branch = getattr(zc, "shen_branch", None)
                            shen_label = shen_branch if shen_branch else "未知"
                            st.markdown(
                                f"**身宮（{shen_label}）**\n\n"
                                "身宮代表後天行動重心、中年後越來越明顯的生命著力點。"
                            )
                            if zc.shen_palace and zc.shen_palace.main_stars:
                                st.markdown(f"主星：{'、'.join(zc.shen_palace.main_stars)}")

                # ── D. 十二宮表格 ────────────────────────────────────────────
                st.markdown("##### 十二宮總表")
                render_ziwei_formal_table(zc)

                # ── E. 十四主星總覽 ─────────────────────────────────────────
                with st.expander("十四主星分布"):
                    four_trans = zc.four_transformations or {}
                    star_rows = []
                    all_palaces = [
                        zc.ming_palace, zc.brother_palace, zc.spouse_palace,
                        zc.children_palace, zc.wealth_palace, zc.health_palace,
                        zc.travel_palace, zc.friends_palace, zc.career_palace,
                        zc.property_palace, zc.fortune_palace, zc.parents_palace,
                    ]
                    branch_to_palace: dict = {}
                    for p in all_palaces:
                        branch_to_palace[p.earthly_branch] = p.name
                    for star in _MAIN_STARS_14:
                        palace_name = "—"
                        for p in all_palaces:
                            if star in p.main_stars:
                                palace_name = f"{p.name}（{p.earthly_branch}）"
                                break
                        sihua = four_trans.get(star, "")
                        star_rows.append({
                            "星曜": star,
                            "所在宮位": palace_name,
                            "四化": sihua if sihua else "—",
                        })
                    import pandas as pd
                    st.dataframe(pd.DataFrame(star_rows), use_container_width=True, hide_index=True)

                # ── F. 四化總覽 ──────────────────────────────────────────────
                with st.expander("生年四化"):
                    four_trans = zc.four_transformations or {}
                    from engines.ziwei import _MAIN_STARS_14 as _MS14
                    sihua_order = ["化祿", "化權", "化科", "化忌"]
                    sihua_desc = {
                        "化祿": "偏機會 / 資源",
                        "化權": "偏主導 / 權力",
                        "化科": "偏名聲 / 學習",
                        "化忌": "偏壓力 / 課題（轉化視角：深化的功課）",
                    }
                    for tx_type in sihua_order:
                        star = next((s for s, t in four_trans.items() if t == tx_type), None)
                        if star:
                            is_main = star in _MS14
                            palace_info = ""
                            if is_main:
                                for p in all_palaces:
                                    if star in p.main_stars:
                                        palace_info = f"，落於{p.name}（{p.earthly_branch}）"
                                        break
                            else:
                                palace_info = "（輔星四化，V1.5 保留資訊）"
                            st.markdown(
                                f"**{tx_type}**：{star}{palace_info} — {sihua_desc.get(tx_type, '')}"
                            )
                        else:
                            st.markdown(f"**{tx_type}**：—")

                # ── G. 輔星 / 煞星總覽 ───────────────────────────────────────
                with st.expander("輔星 / 煞星總覽（V1.5.5）"):
                    aux_note = getattr(zc, "auxiliary_accuracy_note", "")
                    if aux_note:
                        st.caption(f"ℹ️ {aux_note}")
                    render_ziwei_auxiliary_table(zc)

                # ── H. 大限 ──────────────────────────────────────────────────
                with st.expander("大限 10 年運限（V1.5.5 Phase 1）"):
                    dx_dir = getattr(zc, "da_xian_direction", "")
                    dx_age = getattr(zc, "da_xian_start_age", None)
                    dir_labels = {"forward": "順行（陽男 / 陰女）",
                                  "backward": "逆行（陰男 / 陽女）",
                                  "unknown": "方向未知（性別未填）"}
                    if dx_dir:
                        st.caption(f"大限方向：{dir_labels.get(dx_dir, dx_dir)}")
                    if dx_age:
                        st.caption(f"第一大限起始歲數：{dx_age} 歲（依五行局數）")
                    st.caption(
                        "ℹ️ V1.5.5 大限為 Phase 1 骨架，尚未加入大限四化與流年飛化。"
                        " 適合看十年生命焦點，不適合直接斷具體年份事件。"
                    )
                    render_daxian_table(zc)

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

    # ── Report summary card ───────────────────────────────────────────────────
    with st.container(border=True):
        rc1, rc2, rc3, rc4 = st.columns(4)
        with rc1:
            st.metric("姓名", report.profile.name)
        with rc2:
            st.metric("報告長度", report.profile.report_length.value)
        with rc3:
            st.metric("版本", f"v{APP_VERSION}")
        with rc4:
            st.metric("生成時間", report.created_at[:16] if report.created_at else "─")

    # ── Calculation mode expander ─────────────────────────────────────────────
    with st.expander("計算模式摘要"):
        wc = report.western_chart
        bc = report.bazi_chart
        zc = report.ziwei_chart
        mode_data = [
            ("西洋占星", getattr(wc, "calculation_mode", "─") if wc else "─",
             getattr(wc, "accuracy_note", "") if wc else ""),
            ("八字",    getattr(bc, "calculation_mode", "─") if bc else "─",
             getattr(bc, "accuracy_note", "") if bc else ""),
            ("紫微",    getattr(zc, "calculation_mode", "─") if zc else "─",
             getattr(zc, "accuracy_note", "") if zc else ""),
        ]
        import pandas as pd
        st.dataframe(
            pd.DataFrame(mode_data, columns=["系統", "計算模式", "備注"]),
            hide_index=True, use_container_width=True,
        )
        aux_note = getattr(zc, "auxiliary_accuracy_note", "") if zc else ""
        if aux_note:
            st.caption(f"輔星：{aux_note}")

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
    df_display = df[
        ["id", "name", "birth_date", "title", "language", "length", "created_at"]
    ].copy()
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

    # ── Report summary card ───────────────────────────────────────────────────
    with st.container(border=True):
        ec1, ec2, ec3, ec4 = st.columns(4)
        with ec1:
            st.metric("姓名", report.profile.name)
        with ec2:
            st.metric("生成時間", report.created_at[:16] if report.created_at else "─")
        with ec3:
            st.metric("報告長度", report.profile.report_length.value)
        with ec4:
            wc = report.western_chart
            bc = report.bazi_chart
            zc = report.ziwei_chart
            modes_summary = (
                f"西洋: {getattr(wc, 'calculation_mode', '─') if wc else '─'} ｜ "
                f"八字: {getattr(bc, 'calculation_mode', '─') if bc else '─'} ｜ "
                f"紫微: {getattr(zc, 'calculation_mode', '─') if zc else '─'}"
            )
            st.caption(modes_summary)

    st.divider()

    from reports.markdown_exporter import MarkdownExporter
    from reports.html_exporter import HtmlExporter

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("**Markdown**")
        st.caption("適合二次編輯")
        md_content = MarkdownExporter().export(report)
        st.download_button(
            label="📝 下載 Markdown",
            data=md_content.encode("utf-8"),
            file_name=make_export_filename(report.profile.name, "md"),
            mime="text/markdown",
            use_container_width=True,
        )

    with col2:
        st.markdown("**HTML**")
        st.caption("適合瀏覽與列印")
        html_content = HtmlExporter().export(report)
        st.download_button(
            label="🌐 下載 HTML",
            data=html_content.encode("utf-8"),
            file_name=make_export_filename(report.profile.name, "html"),
            mime="text/html",
            use_container_width=True,
        )

    with col3:
        st.markdown("**Word**")
        st.caption("適合交付客戶與人工排版")
        docx_exp = DocxExporter()
        if docx_exp.is_available():
            try:
                docx_bytes = docx_exp.export(report)
                st.download_button(
                    label="📘 下載 Word",
                    data=docx_bytes,
                    file_name=make_export_filename(report.profile.name, "docx"),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            except Exception as e:
                st.button("📘 Word 匯出失敗", disabled=True,
                          use_container_width=True)
                st.caption(str(e))
        else:
            st.button("📘 Word（未安裝）", disabled=True,
                      use_container_width=True)
            st.info("需安裝 python-docx：`pip install python-docx`")

    with col4:
        st.markdown("**PDF**")
        st.caption("若環境支援 WeasyPrint 則可用")
        pdf_exp = PdfExporter()
        if pdf_exp.is_available():
            try:
                pdf_bytes = pdf_exp.export(report)
                st.download_button(
                    label="📕 下載 PDF",
                    data=pdf_bytes,
                    file_name=make_export_filename(report.profile.name, "pdf"),
                    mime="application/pdf",
                    use_container_width=True,
                )
            except RuntimeError as e:
                st.button("📕 PDF（環境問題）", disabled=True,
                          use_container_width=True)
                st.warning(str(e))
        else:
            st.button("📕 PDF（未安裝）", disabled=True,
                      use_container_width=True)
            st.info(
                "需安裝 WeasyPrint：`pip install weasyprint`\n\n"
                "Windows 可能需要額外系統依賴（GTK / Pango）。\n"
                "建議優先使用 HTML 或 Word 格式交付。"
            )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 設定
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️ 設定":
    st.title("⚙️ 應用程式設定")

    # ── System info ───────────────────────────────────────────────────────────
    st.subheader("系統資訊")
    from config import DB_PATH, SWISSEPH_DATA_PATH
    si1, si2 = st.columns(2)
    with si1:
        st.metric("版本", f"v{APP_VERSION}")
        st.write(f"**資料庫路徑**：`{DB_PATH}`")
    with si2:
        sweph_status = "已設定 ✅" if SWISSEPH_DATA_PATH else "未設定（Moshier 內建）⚠️"
        st.write(f"**Swiss Ephemeris**：{sweph_status}")

    # ── Supported features ────────────────────────────────────────────────────
    st.divider()
    st.subheader("支援功能")
    st.markdown("""
| 功能 | 狀態 |
|------|------|
| 西洋占星（Swiss Ephemeris） | ✅ 支援 |
| 八字（節氣精確計算） | ✅ 支援 |
| 紫微斗數（正式排盤 Phase 1） | ✅ 支援 |
| 紫微輔星 / 煞星（V1.5.5） | ✅ 支援 |
| 紫微大限 Phase 1（V1.5.5） | ✅ 支援 |
| 血型分析 | ✅ 支援 |
| 生命靈數 | ✅ 支援 |
""")

    # ── Export format availability ────────────────────────────────────────────
    st.divider()
    st.subheader("可用匯出格式")
    _docx_ok = DocxExporter().is_available()
    _pdf_ok  = PdfExporter().is_available()
    ef1, ef2, ef3, ef4 = st.columns(4)
    with ef1:
        st.success("📝 Markdown ✅")
        st.caption("適合二次編輯")
    with ef2:
        st.success("🌐 HTML ✅")
        st.caption("適合瀏覽與列印")
    with ef3:
        if _docx_ok:
            st.success("📘 Word ✅")
        else:
            st.warning("📘 Word ⚠️")
            st.caption("pip install python-docx")
    with ef4:
        if _pdf_ok:
            st.success("📕 PDF ✅")
        else:
            st.warning("📕 PDF ⚠️")
            st.caption("pip install weasyprint")

    # ── Swiss Ephemeris path ──────────────────────────────────────────────────
    st.divider()
    st.subheader("Swiss Ephemeris 設定（可選）")
    st.caption(
        "設定後可指定星曆資料目錄（.se1 檔案）。"
        "未設定時使用 Moshier 內建星曆（精度足夠一般用途）。"
    )
    sweph_path = st.text_input(
        "Swiss Ephemeris 資料路徑",
        value=get_setting("swisseph_path", ""),
        placeholder="例：/usr/share/swisseph",
    )
    if st.button("儲存設定"):
        set_setting("swisseph_path", sweph_path)
        st.success("設定已儲存。請重新啟動應用程式以生效。")

    # ── Data management ───────────────────────────────────────────────────────
    st.divider()
    st.subheader("資料管理")
    dm1, dm2 = st.columns(2)
    with dm1:
        full_reports = list_reports(limit=9999)
        st.metric("已儲存報告數", len(full_reports))
    with dm2:
        full_profiles = list_birth_profiles(limit=9999)
        st.metric("已儲存命盤數", len(full_profiles))
