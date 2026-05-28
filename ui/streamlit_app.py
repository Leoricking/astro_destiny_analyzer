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

from config import (
    APP_NAME, APP_SUBTITLE, APP_VERSION,
    TAIWAN_CITY_DISPLAY_NAMES, lookup_location,
    DEVELOPER_MODE, CUSTOMER_MODE, SHOW_DEMO_DATA, SHOW_INTERNAL_VERSION_INFO,
    BRAND_NAME, BRAND_TAGLINE, REPORT_WATERMARK,
)
from core.models import (
    BirthProfile, Gender, BloodType, AnalysisTheme,
    ReportLanguage, ReportLength,
)
from core.validators import validate_birth_date, validate_birth_time, validate_name, validate_city
from reports.generator import ReportGenerator
from reports.pdf_exporter import PdfExporter
from reports.docx_exporter import DocxExporter
from reports.utils import make_export_filename
from demo.sample_profiles import SAMPLE_PROFILES, SAMPLE_LABELS, SAMPLE_COUPLES
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

_PAGES_BASE = [
    "🏠 首頁", "🌐 免費內容入口", "🎁 免費報告", "📝 輸入資料", "🔮 計算命盤",
    "📄 報告預覽", "📚 歷史報告", "📤 匯出", "💕 合盤分析",
    "⚙️ 設定",
]
_PAGES_DEV = [
    "🏠 首頁", "🌐 免費內容入口", "🎁 免費報告", "📝 輸入資料", "🔮 計算命盤",
    "📄 報告預覽", "📚 歷史報告", "📤 匯出", "💕 合盤分析",
    "🧭 紫微校準", "🔷 人類圖校準", "⚙️ 設定",
]
_PAGES = _PAGES_DEV if DEVELOPER_MODE else _PAGES_BASE

_DEFAULT_THEME_VALUES = [t.value for t in AnalysisTheme]

# ── Birth year constants ───────────────────────────────────────────────────────
DEFAULT_BIRTH_YEAR: int = 1990
MIN_BIRTH_YEAR:     int = 1900
MAX_BIRTH_YEAR:     int = date.today().year

# ── Session state: global defaults (never overwrite existing values) ───────────
_GLOBAL_DEFAULTS: dict = {
    "profile": None,
    "report": None,
    "active_report_id": None,
    "nav_page": "🏠 首頁",
    "ziwei_rec_report": None,
}
for _k, _v in _GLOBAL_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Session state: input field defaults ───────────────────────────────────────
_INPUT_DEFAULTS: dict = {
    "input_name": "",
    "input_gender": "不填寫",
    "input_birth_year": DEFAULT_BIRTH_YEAR,
    "input_birth_year_user_touched": False,
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

def _mark_birth_year_touched() -> None:
    """on_change callback: user has explicitly interacted with the birth year field."""
    st.session_state["input_birth_year_user_touched"] = True


def _normalize_birth_year_state() -> None:
    """Ensure input_birth_year displays DEFAULT_BIRTH_YEAR (1990), not the
    Streamlit artefact of min_value (1900) that appears when the widget key
    is first created by the framework rather than by our initialization loop.
    """
    year    = st.session_state.get("input_birth_year")
    touched = st.session_state.get("input_birth_year_user_touched", False)
    has_profile = bool(st.session_state.get("profile") or st.session_state.get("current_profile"))
    has_report  = bool(st.session_state.get("report"))

    if year is None:
        st.session_state["input_birth_year"] = DEFAULT_BIRTH_YEAR
        st.session_state["input_birth_year_user_touched"] = False
        return

    try:
        year_int = int(year)
    except Exception:
        st.session_state["input_birth_year"] = DEFAULT_BIRTH_YEAR
        st.session_state["input_birth_year_user_touched"] = False
        return

    if year_int < MIN_BIRTH_YEAR or year_int > MAX_BIRTH_YEAR:
        st.session_state["input_birth_year"] = DEFAULT_BIRTH_YEAR
        st.session_state["input_birth_year_user_touched"] = False
        return

    # 舊 session 常見問題：1900 被 Streamlit 當成 min_value 預設。
    # 如果使用者尚未手動碰過，且沒有已建立 profile/report，就把 1900 拉回 1990。
    if year_int == MIN_BIRTH_YEAR and not touched and not has_profile and not has_report:
        st.session_state["input_birth_year"] = DEFAULT_BIRTH_YEAR
        st.session_state["input_birth_year_user_touched"] = False

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
    st.session_state["input_birth_year"] = DEFAULT_BIRTH_YEAR
    st.session_state["input_birth_year_user_touched"] = False
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


def _load_sample(index: int) -> None:
    """Load a demo sample profile into session state and navigate to Calculate."""
    profile = SAMPLE_PROFILES[index]
    _sync_input_state_from_profile(profile)
    st.session_state["profile"] = profile
    st.session_state["report"] = None
    st.session_state["_demo_loaded"] = True
    st.session_state["_pending_nav_page"] = "🔮 計算命盤"


# Apply pending navigation before the radio widget is instantiated.
# Streamlit does not allow modifying a widget-backed session_state key after
# the widget has been created in the same run.
if "_pending_nav_page" in st.session_state:
    _pending_page = st.session_state.pop("_pending_nav_page")
    if _pending_page in _PAGES:
        st.session_state["nav_page"] = _pending_page

# Guard: if a stale session has nav_page pointing to a dev-only page, reset to home.
if not DEVELOPER_MODE and st.session_state.get("nav_page") == "🧭 紫微校準":
    st.session_state["nav_page"] = "🏠 首頁"
if not DEVELOPER_MODE and st.session_state.get("nav_page") == "🔷 人類圖校準":
    st.session_state["nav_page"] = "🏠 首頁"


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
    if DEVELOPER_MODE:
        st.caption(f"v{APP_VERSION} · DEV MODE")
        st.caption(f"DEVELOPER_MODE=True")
    else:
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

    _home_c1, _home_c2, _home_c3 = st.columns(3)
    with _home_c1:
        if st.button("🚀 開始建立個人命盤", type="primary", use_container_width=True):
            _go_to_page("📝 輸入資料")
    with _home_c2:
        if st.button("💕 建立合盤報告", use_container_width=True):
            _go_to_page("💕 合盤分析")
    with _home_c3:
        if st.button("📚 查看歷史報告", use_container_width=True):
            _go_to_page("📚 歷史報告")

    if SHOW_DEMO_DATA:
        st.divider()
        st.subheader("⚡ 快速體驗")
        st.caption("不需要手動輸入，直接使用範例資料體驗完整分析流程。")
        demo_c1, demo_c2, demo_c3 = st.columns(3)
        with demo_c1:
            if st.button("🏙️ Demo 台北精準時間", use_container_width=True):
                _load_sample(0)
                st.rerun()
        with demo_c2:
            if st.button("💼 Demo 新竹科技職涯", use_container_width=True):
                _load_sample(1)
                st.rerun()
        with demo_c3:
            if st.button("❓ Demo 未知出生時間", use_container_width=True):
                _load_sample(2)
                st.rerun()

        if st.session_state.get("_demo_loaded"):
            st.info("✅ 已載入範例資料，可直接計算，也可返回輸入頁修改。")
            st.session_state["_demo_loaded"] = False


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 免費內容入口
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🌐 免費內容入口":
    from public_content.content_registry import (
        get_public_content_catalog, get_public_page, list_public_pages, list_featured_pages,
    )
    from public_content.templates import (
        render_public_page_markdown, render_public_page_excerpt,
        render_public_catalog_markdown, render_public_catalog_html,
    )
    from public_content.exporters import (
        export_public_page_html, export_public_page_markdown,
        export_public_catalog_markdown, export_public_catalog_html,
        safe_public_content_filename,
    )

    _catalog = get_public_content_catalog()

    # ── A. Header ─────────────────────────────────────────────────────────────
    st.title("🌐 免費內容入口")
    st.caption("從星座、人類圖、合盤、紫微、八字開始，快速了解自己，再建立完整整合報告。")

    # ── B. Featured cards ─────────────────────────────────────────────────────
    _featured = list_featured_pages()
    if _featured:
        st.subheader("精選內容")
        _fcols = st.columns(min(len(_featured), 3))
        for _i, _fp in enumerate(_featured):
            with _fcols[_i % 3]:
                st.markdown(f"**{_fp.title}**")
                if _fp.summary:
                    st.caption(_fp.summary[:120] + ("…" if len(_fp.summary) > 120 else ""))
                if _fp.tags:
                    st.caption("標籤：" + " · ".join(_fp.tags))
                if _fp.cta_button_label:
                    if st.button(_fp.cta_button_label, key=f"feat_cta_{_fp.slug}"):
                        st.session_state["nav_page"] = _fp.cta_target
                        st.rerun()
        st.divider()

    # ── C. Category filter ────────────────────────────────────────────────────
    _CAT_LABELS = {
        "全部": None,
        "星座": "zodiac",
        "人類圖": "human_design",
        "合盤": "compatibility",
        "紫微": "ziwei",
        "八字": "bazi",
        "靈數": "numerology",
        "指南": "guide",
    }
    _cat_choice = st.selectbox(
        "分類篩選",
        options=list(_CAT_LABELS.keys()),
        key="public_content_cat_filter",
    )
    _filtered_pages = list_public_pages(category=_CAT_LABELS[_cat_choice])

    # ── D. Page detail ────────────────────────────────────────────────────────
    _page_titles = [p.title for p in _filtered_pages]
    if _page_titles:
        _selected_title = st.selectbox(
            "選擇內容頁面",
            options=_page_titles,
            key="public_content_page_select",
        )
        _sel_page = next((p for p in _filtered_pages if p.title == _selected_title), None)
        if _sel_page:
            st.markdown(render_public_page_markdown(_sel_page))
            # CTA navigation
            _cta_col1, _cta_col2 = st.columns(2)
            if _sel_page.cta_button_label and _sel_page.cta_target:
                with _cta_col1:
                    if st.button(
                        f"→ {_sel_page.cta_button_label}",
                        key="public_content_cta_nav",
                        type="primary",
                    ):
                        st.session_state["nav_page"] = _sel_page.cta_target
                        st.rerun()
            # Free report secondary CTA
            if _sel_page.free_report_cta_slug:
                with _cta_col2:
                    if st.button(
                        "🎁 先領免費摘要",
                        key="public_content_free_report_cta",
                    ):
                        st.session_state["nav_page"] = "🎁 免費報告"
                        st.session_state["free_report_type_preset"] = _sel_page.free_report_cta_slug
                        st.rerun()

            # ── E. Export (developer mode only) ───────────────────────────────
            if DEVELOPER_MODE:
                from public_content.seo import validate_seo_data, build_meta_tags
                st.divider()
                st.subheader("開發者工具：SEO & 匯出")
                # SEO warnings
                _seo_warnings = validate_seo_data(_sel_page)
                if _seo_warnings:
                    st.warning("SEO warnings:\n" + "\n".join(f"- {w}" for w in _seo_warnings))
                else:
                    st.success("SEO 驗證通過")
                # Meta tags preview
                with st.expander("Meta Tags 預覽"):
                    st.code(build_meta_tags(_sel_page), language="html")
                # Download buttons
                _md_content = export_public_page_markdown(_sel_page)
                _html_content = export_public_page_html(_sel_page)
                _dl1, _dl2 = st.columns(2)
                with _dl1:
                    st.download_button(
                        "下載 Markdown",
                        data=_md_content.encode("utf-8"),
                        file_name=safe_public_content_filename(_sel_page.slug, "md"),
                        mime="text/markdown",
                    )
                with _dl2:
                    st.download_button(
                        "下載 HTML",
                        data=_html_content.encode("utf-8"),
                        file_name=safe_public_content_filename(_sel_page.slug, "html"),
                        mime="text/html",
                    )
                # Catalog export
                st.divider()
                st.caption("全目錄匯出")
                _cat_md = export_public_catalog_markdown(_catalog)
                _cat_html = export_public_catalog_html(_catalog)
                _cl1, _cl2 = st.columns(2)
                with _cl1:
                    st.download_button(
                        "下載全目錄 Markdown",
                        data=_cat_md.encode("utf-8"),
                        file_name="public_content_catalog.md",
                        mime="text/markdown",
                    )
                with _cl2:
                    st.download_button(
                        "下載全目錄 HTML",
                        data=_cat_html.encode("utf-8"),
                        file_name="public_content_catalog.html",
                        mime="text/html",
                    )
    else:
        st.info("此分類目前沒有內容頁面。")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 免費報告
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🎁 免費報告":
    from lead_magnet.models import LeadProfile, PartnerProfile, LeadCapture
    from lead_magnet.storage import validate_email, append_lead, load_leads, export_leads_csv, delete_all_leads
    from lead_magnet.engine import generate_free_report
    from lead_magnet.templates import render_lead_capture_copy, render_upgrade_cta
    from lead_magnet.exporters import export_free_report_markdown, export_free_report_html, safe_free_report_filename
    import config as _lcfg

    st.title("🎁 取得免費命盤摘要")
    st.caption("先用免費摘要了解方向，再決定是否建立完整整合報告。")

    # ── B. Report type selector ───────────────────────────────────────────────
    _REPORT_TYPE_LABELS = {
        "星座速覽": "zodiac_free_summary",
        "人類圖 Type 速覽": "human_design_free_summary",
        "合盤初評": "compatibility_free_summary",
        "整合命盤摘要": "integrated_free_summary",
    }
    _preset = st.session_state.pop("free_report_type_preset", None)
    _preset_label = None
    if _preset:
        for _lbl, _slug in _REPORT_TYPE_LABELS.items():
            if _slug == _preset:
                _preset_label = _lbl
                break
    _rt_label = st.selectbox(
        "選擇免費報告類型",
        options=list(_REPORT_TYPE_LABELS.keys()),
        index=list(_REPORT_TYPE_LABELS.keys()).index(_preset_label) if _preset_label else 0,
        key="free_report_type_select",
    )
    _rt = _REPORT_TYPE_LABELS[_rt_label]
    _copy = render_lead_capture_copy(_rt)
    st.subheader(_copy["title"])
    st.caption(_copy["description"])

    # ── C. Lead form ──────────────────────────────────────────────────────────
    with st.form("free_report_form"):
        _fm_name = st.text_input("姓名", key="fr_name")
        _fm_email = st.text_input("Email *", key="fr_email")
        _fm_date = st.text_input("出生日期（YYYY-MM-DD）", key="fr_birth_date")
        _fm_time = st.text_input("出生時間（HH:MM，選填）", key="fr_birth_time")
        _fm_loc = st.text_input("出生地點（選填）", key="fr_birth_loc")
        _show_partner = _rt == "compatibility_free_summary"
        if _show_partner:
            st.markdown("**對方資料**")
            _fm_partner_name = st.text_input("對方姓名", key="fr_partner_name")
            _fm_partner_date = st.text_input("對方出生日期（YYYY-MM-DD）", key="fr_partner_date")
            _fm_partner_time = st.text_input("對方出生時間（HH:MM，選填）", key="fr_partner_time")
        _fm_consent = st.checkbox(_copy["consent_text"], key="fr_consent")
        _fm_mkt = st.checkbox("我願意接收後續完整報告或諮詢服務資訊。（選填）", key="fr_marketing")
        _submitted = st.form_submit_button(_copy["button_label"], type="primary")

    if _submitted:
        _err = False
        if not validate_email(_fm_email):
            st.error("❌ 請輸入有效的 Email 地址。")
            _err = True
        if not _fm_consent:
            st.warning("⚠️ 請勾選同意聲明，才能產生並儲存免費摘要。")
            _err = True
        if not _err:
            _profile = LeadProfile(
                name=_fm_name,
                email=_fm_email,
                birth_date=_fm_date or None,
                birth_time=_fm_time or None,
                birth_location=_fm_loc,
            )
            _partner = None
            if _show_partner:
                _partner = PartnerProfile(
                    name=_fm_partner_name,
                    birth_date=_fm_partner_date or None,
                    birth_time=_fm_partner_time or None,
                )
            _lead = LeadCapture(
                profile=_profile,
                partner=_partner,
                report_type=_rt,
                source_page_slug="free_report_page",
                consent_given=True,
                marketing_consent=_fm_mkt,
            )
            try:
                _lead = append_lead(_lead, _lcfg.LEAD_STORAGE_PATH)
                st.success("✅ 資料已儲存（本機）。正在產生免費摘要……")
            except Exception as _e:
                st.warning(f"儲存提示：{_e}")
            # Generate and display report
            _result = generate_free_report(_lead)
            st.markdown("---")
            st.markdown(export_free_report_markdown(_result))
            # CTA
            _ucta = render_upgrade_cta(_rt)
            st.info(f"**{_ucta['title']}** — {_ucta['description']}")
            _uc1, _uc2, _uc3 = st.columns(3)
            with _uc1:
                if st.button(f"→ {_ucta['button_label']}", key="fr_upgrade_cta"):
                    st.session_state["nav_page"] = _ucta["target"]
                    st.rerun()
            with _uc2:
                st.download_button(
                    "下載免費摘要 Markdown",
                    data=export_free_report_markdown(_result).encode("utf-8"),
                    file_name=safe_free_report_filename(_fm_name, _rt, "md"),
                    mime="text/markdown",
                    key="fr_dl_md",
                )
            with _uc3:
                st.download_button(
                    "下載免費摘要 HTML",
                    data=export_free_report_html(_result).encode("utf-8"),
                    file_name=safe_free_report_filename(_fm_name, _rt, "html"),
                    mime="text/html",
                    key="fr_dl_html",
                )

    # ── E. Developer mode area ────────────────────────────────────────────────
    if DEVELOPER_MODE:
        st.divider()
        st.subheader("開發者工具：Leads 管理")
        try:
            _snap = load_leads(_lcfg.LEAD_STORAGE_PATH)
        except Exception as _le:
            st.error(f"Leads 載入失敗：{_le}")
            _snap = None
        if _snap is not None:
            st.metric("Lead 總數", len(_snap.leads))
            st.caption(f"儲存路徑：{_lcfg.LEAD_STORAGE_PATH}")
            if _snap.leads:
                import pandas as _pd
                _leads_df = _pd.DataFrame([
                    {
                        "lead_id": ld.lead_id,
                        "name": ld.profile.name,
                        "email": ld.profile.email,
                        "report_type": ld.report_type,
                        "created_at": ld.created_at,
                        "consent": ld.consent_given,
                    }
                    for ld in _snap.leads
                ])
                st.dataframe(_leads_df, use_container_width=True)
                _csv_str = export_leads_csv(_snap)
                st.download_button(
                    "下載 Leads CSV",
                    data=_csv_str.encode("utf-8"),
                    file_name="leads_export.csv",
                    mime="text/csv",
                )
            # Clear leads with confirmation
            if "fr_confirm_clear" not in st.session_state:
                st.session_state["fr_confirm_clear"] = False
            if st.button("🗑️ 清除所有 Leads", key="fr_clear_btn"):
                st.session_state["fr_confirm_clear"] = True
            if st.session_state.get("fr_confirm_clear"):
                st.warning("確認要清除所有 leads 資料？此操作不可復原。")
                _cc1, _cc2 = st.columns(2)
                with _cc1:
                    if st.button("確認清除", key="fr_confirm_yes"):
                        delete_all_leads(_lcfg.LEAD_STORAGE_PATH)
                        st.session_state["fr_confirm_clear"] = False
                        st.success("Leads 已清除。")
                        st.rerun()
                with _cc2:
                    if st.button("取消", key="fr_confirm_no"):
                        st.session_state["fr_confirm_clear"] = False
                        st.rerun()


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
        _normalize_birth_year_state()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input(
                "西元年 *",
                min_value=MIN_BIRTH_YEAR,
                max_value=MAX_BIRTH_YEAR,
                step=1,
                key="input_birth_year",
                on_change=_mark_birth_year_touched,
            )
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

        tab_w, tab_b, tab_z, tab_n, tab_hd = st.tabs(
            ["🌟 西洋占星", "☯️ 八字", "🏮 紫微", "🔢 靈數", "🔷 人類圖"]
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
                        accuracy = getattr(zc, "accuracy_note", "")
                        _reason = accuracy if accuracy else "原因不明（lunardate 缺失或農曆轉換失敗）"
                        st.error(f"⚠️ 紫微斗數使用 fallback，排盤資料僅供參考。原因：{_reason}")
                    accuracy = getattr(zc, "accuracy_note", "")
                    if accuracy and mode != "mock_fallback":
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

                # ── H1. 命主 / 身主 / 天馬 (V1.7.5) ─────────────────────────
                if getattr(zc, "ming_zhu", None) or getattr(zc, "shen_zhu", None) or getattr(zc, "tian_ma_branch", None):
                    with st.container(border=True):
                        st.markdown("#### 命主 / 身主 / 天馬")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("命主（先天人格輔助星）", getattr(zc, "ming_zhu", None) or "—")
                        with col2:
                            st.metric("身主（後天行動重心）", getattr(zc, "shen_zhu", None) or "—")
                        with col3:
                            _tm_b = getattr(zc, "tian_ma_branch", None)
                            _tm_p = getattr(zc, "tian_ma_palace", None)
                            tian_ma_disp = f"{_tm_b}（{_tm_p}）" if _tm_b else "—"
                            st.metric("天馬（移動/變動能量）", tian_ma_disp)

                # ── H2. 紫微盤面結構支援度 Phase 1 (V1.7.6) ─────────────────
                _zscore = getattr(zc, "ziwei_score", None)
                if _zscore is not None:
                    with st.container(border=True):
                        st.markdown("#### 紫微盤面結構支援度")
                        st.metric(
                            f"盤面支援度：{getattr(zc, 'ziwei_score_label', '') or ''}",
                            f"{_zscore} / 100",
                        )
                        st.caption("此分數不是外部網站好運指數，也不代表命運好壞；它只是本系統 Phase 1 的結構支援度模型。")
                        _zexpl = getattr(zc, "ziwei_score_explanation", "")
                        if _zexpl:
                            st.caption(_zexpl)
                        if _zscore >= 85:
                            st.info("高支援也代表高承載，不宜解讀成無壓力或必定成功。")

                # ── H3. 命宮主星廟旺陷 (V1.7.5) ──────────────────────────────
                _bmap = getattr(zc, "brightness_map", {}) or {}
                if _bmap and getattr(zc, "ming_branch", None):
                    ming_brightness = _bmap.get("命宮", {})
                    if ming_brightness:
                        with st.container(border=True):
                            st.markdown("#### 命宮主星廟旺陷")
                            br_text = "、".join(f"{s}（{b}）" for s, b in ming_brightness.items())
                            st.write(br_text)

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

        with tab_hd:
            hd = getattr(report, "human_design_chart", None)
            if hd is None:
                st.warning("人類圖資料尚未生成，請重新計算命盤。")
            else:
                # ── Summary cards ─────────────────────────────────────────────
                import pandas as pd
                st.caption(f"計算模式：{hd.calculation_mode}")
                if "partial" in hd.calculation_mode or "mock" in hd.calculation_mode:
                    st.warning("⚠️ 人類圖需要精確出生時間與 Swiss Ephemeris。目前結果僅供參考。")

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("類型 Type", hd.type_name_zh)
                with col2:
                    st.metric("策略", hd.strategy)
                with col3:
                    st.metric("人生角色", hd.profile)
                with col4:
                    st.metric("已定義中心", len(hd.defined_centers))
                with col5:
                    st.metric("通道數", len(hd.defined_channels))

                st.markdown(f"**內在權威**：{hd.authority}")
                st.markdown(f"**輪迴交叉**：{hd.incarnation_cross}")

                # ── Method summary (V1.9.3) ────────────────────────────────────
                _design_method_label = {
                    "solar_arc_88": "精準太陽弧 88°",
                    "minus_88_days": "近似 −88 天",
                    "minus_88_days_fallback": "近似 −88 天（回退）",
                }.get(getattr(hd, "design_date_method", ""), getattr(hd, "design_date_method", "─"))
                _wheel_offset = getattr(hd, "gate_wheel_offset_degrees", 0.0)
                _offset_label = f"{_wheel_offset:+.3f}°" if _wheel_offset != 0.0 else "無偏移（Phase 1 預設）"
                st.caption(
                    f"設計日期方法：{_design_method_label} ｜ "
                    f"Gate Wheel Offset：{_offset_label} ｜ "
                    f"設計日期：{hd.design_datetime or '─'}"
                )

                # ── Centers Visual Bundle ─────────────────────────────────────
                from human_design.visuals import build_hd_visuals
                _hd_bundle = build_hd_visuals(hd)
                st.subheader("九大中心")
                st.caption(_hd_bundle.summary)
                if _hd_bundle.centers:
                    center_rows = [
                        {
                            "中心": f"{v.center_zh}（{v.center}）",
                            "狀態": "✅ 已定義" if v.is_defined else "⬜ 開放",
                            "主題": v.theme,
                            "啟動閘門": ", ".join(str(g) for g in v.active_gates) if v.active_gates else "─",
                            "解讀": v.interpretation_short,
                        }
                        for v in _hd_bundle.centers
                    ]
                    st.dataframe(pd.DataFrame(center_rows), hide_index=True, use_container_width=True)

                # ── Channels ──────────────────────────────────────────────────
                if hd.defined_channels:
                    st.subheader("已定義通道")
                    ch_rows = [{"通道": ch.channel, "名稱": ch.name,
                                "連接中心": f"{ch.centers[0]} — {ch.centers[1]}",
                                "迴路": ch.circuit, "解讀": ch.interpretation}
                               for ch in hd.defined_channels]
                    st.dataframe(pd.DataFrame(ch_rows), hide_index=True, use_container_width=True)
                else:
                    st.info("目前無已定義通道（所有中心皆開放）。")

                # ── Activated Gates ───────────────────────────────────────────
                with st.expander(f"已啟動閘門（{len(hd.activated_gates)} 個）"):
                    if hd.activated_gates:
                        gate_rows = [{"Gate": g.gate, "名稱": g.name, "中心": g.center,
                                      "來源": " + ".join(g.side_sources)}
                                     for g in hd.activated_gates]
                        st.dataframe(pd.DataFrame(gate_rows), hide_index=True, use_container_width=True)

                # ── Planet tables ─────────────────────────────────────────────
                col_c, col_d = st.columns(2)
                with col_c:
                    st.subheader("Conscious 行星（意識面）")
                    if hd.conscious_activations:
                        rows = [{"行星": a.planet, "星座": a.sign,
                                 "黃經": f"{a.longitude:.2f}°",
                                 "Gate": a.gate, "Line": a.line}
                                for a in hd.conscious_activations]
                        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
                with col_d:
                    st.subheader("Design 行星（設計面）")
                    if hd.design_activations:
                        rows = [{"行星": a.planet, "星座": a.sign,
                                 "黃經": f"{a.longitude:.2f}°",
                                 "Gate": a.gate, "Line": a.line}
                                for a in hd.design_activations]
                        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

                # ── Decision guidance ─────────────────────────────────────────
                with st.expander("決策建議與能量摘要"):
                    st.markdown(hd.energy_summary)
                    if hd.conditioning_risks:
                        st.markdown("**制約風險（開放中心）：**")
                        for r in hd.conditioning_risks:
                            st.markdown(f"- {r}")

                # ── Validation ────────────────────────────────────────────────
                from human_design.validation import build_validation_status, render_validation_markdown
                _hd_vs = build_validation_status(hd)
                with st.expander("準確度與外部校準說明"):
                    st.markdown(render_validation_markdown(_hd_vs))

                # ── Developer debug ───────────────────────────────────────────
                if DEVELOPER_MODE:
                    with st.expander("🔧 開發者：HD Debug"):
                        st.write(f"設計日期：{hd.design_datetime}")
                        st.write(f"出生日期：{hd.birth_datetime}")
                        st.write(f"accuracy_note：{hd.accuracy_note}")
                        st.write(f"defined_centers: {hd.defined_centers}")
                        st.write(f"open_centers: {hd.open_centers}")
                        st.write(f"raw gate count: {len(hd.activated_gates)}")
                        st.write(f"validation_level: {_hd_vs.validation_level}")
                        st.write(f"ephemeris_status: {_hd_vs.ephemeris_status}")
                        st.markdown("**V1.9.3 校準欄位**")
                        st.write(f"design_date_method: {hd.design_date_method}")
                        st.write(f"design_date_fallback_used: {hd.design_date_fallback_used}")
                        if hd.design_solar_arc_target_longitude is not None:
                            st.write(f"solar_arc_target_lon: {hd.design_solar_arc_target_longitude:.4f}°")
                            st.write(f"solar_arc_actual_lon: {hd.design_solar_arc_actual_longitude:.4f}°")
                            st.write(f"solar_arc_error: {hd.design_solar_arc_error_degrees:.4f}°")
                        st.write(f"gate_wheel_offset: {hd.gate_wheel_offset_degrees:+.3f}°")
                        st.write(f"gate_wheel_version: {hd.gate_wheel_version}")
                        if hd.calibration_notes:
                            st.markdown("**calibration_notes:**")
                            for cn in hd.calibration_notes:
                                st.write(f"- {cn}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 報告預覽
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📄 報告預覽":
    st.title("📄 報告預覽")

    if st.session_state["report"] is None:
        st.warning("尚無報告，請先至「🔮 計算命盤」產生報告。")
        st.stop()

    report = st.session_state["report"]

    # ── Demo label ────────────────────────────────────────────────────────────
    if report.profile.name.startswith("Demo"):
        st.info("🔍 這是範例報告，可用於展示與功能驗證。")

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
    with st.expander("📋 推薦匯出格式說明", expanded=False):
        st.markdown("""
| 格式 | 推薦用途 |
|------|----------|
| 🌐 HTML | 最適合展示與列印，單一檔案，自含樣式 |
| 📘 Word | 最適合交付客戶，可人工調整排版 |
| 📝 Markdown | 最適合二次編輯，版本控制友善 |
| 📕 PDF | 需環境支援 WeasyPrint（pip install weasyprint） |
""")
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
            st.warning(
                "需安裝 python-docx：請執行 `setup.bat` 或 "
                "`.venv\\Scripts\\python -m pip install -r requirements.txt`"
            )

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
                "PDF 需要 WeasyPrint；Windows 可能需要 GTK/Pango。\n\n"
                "建議先用 **HTML** 或 **Word** 交付。\n\n"
                "若要啟用 PDF：執行 `install_pdf_support.bat` 或 `pip install weasyprint`"
            )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 合盤分析
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💕 合盤分析":
    st.title("💕 合盤分析")
    st.caption("情侶、伴侶、合作夥伴、親子、朋友、同事 — 多系統關係互動分析")
    st.info(
        "**合盤分數不是絕對適合度，而是互動模式地圖。**\n\n"
        "高衝突不一定不好，低衝突也不一定代表長期成長。"
        "分數描述的是互動模式的可觀察指標，關係品質由兩人共同創造。"
    )

    from compatibility.engine import CompatibilityEngine
    from compatibility.models import CompatibilityInput, RelationshipType
    from compatibility.exporters import make_compat_filename, export_compat_to_html, export_compat_to_docx
    from reports.docx_exporter import DocxExporter as _DocxExporter

    # ── Intro ─────────────────────────────────────────────────────────────────
    with st.expander("📖 合盤分析說明", expanded=False):
        st.markdown("""
合盤分析整合以下五套系統，從多個角度理解兩人之間的互動模式：

| 系統 | 分析內容 |
|------|---------|
| 🌟 西洋占星 | 太陽、月亮、水星、金星火星、上升配對 |
| ☯️ 八字 | 日主五行互動、喜用神互補、忌神放大 |
| 🏮 紫微 | 命宮主星、身宮、關係宮位互動 |
| 🔢 生命靈數 | 生命靈數配對、共鳴主題 |
| 🩸 血型 | 互動風格、衝突模式 |

> ⚠️ 本分析為關係理解與溝通參考，不代表「一定適合」或「一定不適合」。
""")

    # ── Relationship type ─────────────────────────────────────────────────────
    st.subheader("關係類型")
    _RT_OPTIONS = {
        "情侶 / 伴侶": "romantic",
        "婚姻": "marriage",
        "合作夥伴": "business",
        "親子": "parent_child",
        "朋友": "friendship",
        "同事": "colleague",
        "一般關係": "general",
    }
    rt_label_sel = st.selectbox(
        "選擇關係類型",
        list(_RT_OPTIONS.keys()),
        key="compat_rel_type",
    )
    selected_rt = RelationshipType(_RT_OPTIONS[rt_label_sel])

    # ── Person A ──────────────────────────────────────────────────────────────
    st.subheader("A 方資料")
    use_current = st.session_state.get("profile") is not None
    if use_current:
        if st.button("📋 使用目前命盤作為 A 方", key="compat_use_current_as_a"):
            st.session_state["compat_a_profile"] = st.session_state["profile"]
            st.success(f"已載入：{st.session_state['profile'].name}")

    with st.expander("手動輸入 A 方資料", expanded=(not use_current)):
        ca1, ca2 = st.columns(2)
        with ca1:
            st.text_input("A 姓名 *", key="compat_a_name", placeholder="例：小明")
        with ca2:
            st.selectbox("A 性別", ["不填寫", "男", "女", "其他"], key="compat_a_gender")
        ca3, ca4, ca5 = st.columns(3)
        with ca3:
            st.number_input("A 出生年 *", min_value=1900, max_value=date.today().year,
                            step=1, key="compat_a_year", value=1989)
        with ca4:
            st.number_input("A 月 *", min_value=1, max_value=12, step=1,
                            key="compat_a_month", value=9)
        with ca5:
            st.number_input("A 日 *", min_value=1, max_value=31, step=1,
                            key="compat_a_day", value=21)
        st.checkbox("A 方知道精確出生時間", key="compat_a_time_known")
        if st.session_state.get("compat_a_time_known"):
            cah, cam = st.columns(2)
            with cah:
                st.number_input("A 時（24H）", min_value=0, max_value=23,
                                step=1, key="compat_a_hour", value=11)
            with cam:
                st.number_input("A 分", min_value=0, max_value=59,
                                step=1, key="compat_a_minute", value=5)
        ca6, ca7 = st.columns(2)
        with ca6:
            st.text_input("A 出生城市 *", key="compat_a_city", placeholder="例：新竹")
        with ca7:
            st.text_input("A 出生國家", key="compat_a_country", value="台灣")
        st.selectbox("A 血型", ["Unknown", "A", "B", "O", "AB"],
                     key="compat_a_blood")

        if st.button("確認 A 方資料", key="compat_a_confirm"):
            try:
                _a_name = st.session_state.get("compat_a_name", "").strip()
                if not _a_name:
                    st.error("請填寫 A 方姓名")
                else:
                    _a_time = None
                    _a_time_known = bool(st.session_state.get("compat_a_time_known"))
                    if _a_time_known:
                        _a_time = time(
                            int(st.session_state.get("compat_a_hour", 12)),
                            int(st.session_state.get("compat_a_minute", 0)),
                        )
                    _a_gender_map = {"男": "male", "女": "female", "其他": "other", "不填寫": "unknown"}
                    _a_gender_val = _a_gender_map.get(st.session_state.get("compat_a_gender", "不填寫"), "unknown")
                    _a_city = st.session_state.get("compat_a_city", "台北").strip() or "台北"
                    _a_country = st.session_state.get("compat_a_country", "台灣").strip() or "台灣"
                    _loc_a = lookup_location(_a_city)
                    st.session_state["compat_a_profile"] = BirthProfile(
                        name=_a_name,
                        gender=Gender(_a_gender_val),
                        birth_date=date(
                            int(st.session_state.get("compat_a_year", 1989)),
                            int(st.session_state.get("compat_a_month", 1)),
                            int(st.session_state.get("compat_a_day", 1)),
                        ),
                        birth_time=_a_time,
                        birth_city=_a_city,
                        birth_country=_a_country,
                        blood_type=BloodType(st.session_state.get("compat_a_blood", "Unknown")),
                        themes=list(AnalysisTheme),
                        report_length=ReportLength.STANDARD,
                        birth_latitude=_loc_a["lat"] if _loc_a else None,
                        birth_longitude=_loc_a["lon"] if _loc_a else None,
                        birth_timezone_offset=8.0,
                        birth_time_is_known=_a_time_known,
                    )
                    st.success(f"A 方已確認：{_a_name}")
            except Exception as _e:
                st.error(f"A 方資料錯誤：{_e}")

    if st.session_state.get("compat_a_profile"):
        _pa = st.session_state["compat_a_profile"]
        st.info(f"✅ A 方：{_pa.name}（{_pa.birth_date}，{_pa.birth_city}）")

    # ── Person B ──────────────────────────────────────────────────────────────
    st.subheader("B 方資料")
    with st.expander("輸入 B 方資料", expanded=True):
        cb1, cb2 = st.columns(2)
        with cb1:
            st.text_input("B 姓名 *", key="compat_b_name", placeholder="例：小花")
        with cb2:
            st.selectbox("B 性別", ["不填寫", "男", "女", "其他"], key="compat_b_gender")
        cb3, cb4, cb5 = st.columns(3)
        with cb3:
            st.number_input("B 出生年 *", min_value=1900, max_value=date.today().year,
                            step=1, key="compat_b_year", value=1991)
        with cb4:
            st.number_input("B 月 *", min_value=1, max_value=12, step=1,
                            key="compat_b_month", value=3)
        with cb5:
            st.number_input("B 日 *", min_value=1, max_value=31, step=1,
                            key="compat_b_day", value=8)
        st.checkbox("B 方知道精確出生時間", key="compat_b_time_known")
        if st.session_state.get("compat_b_time_known"):
            cbh, cbm = st.columns(2)
            with cbh:
                st.number_input("B 時（24H）", min_value=0, max_value=23,
                                step=1, key="compat_b_hour", value=9)
            with cbm:
                st.number_input("B 分", min_value=0, max_value=59,
                                step=1, key="compat_b_minute", value=45)
        cb6, cb7 = st.columns(2)
        with cb6:
            st.text_input("B 出生城市 *", key="compat_b_city", placeholder="例：高雄")
        with cb7:
            st.text_input("B 出生國家", key="compat_b_country", value="台灣")
        st.selectbox("B 血型", ["Unknown", "A", "B", "O", "AB"],
                     key="compat_b_blood")

        if st.button("確認 B 方資料", key="compat_b_confirm"):
            try:
                _b_name = st.session_state.get("compat_b_name", "").strip()
                if not _b_name:
                    st.error("請填寫 B 方姓名")
                else:
                    _b_time = None
                    _b_time_known = bool(st.session_state.get("compat_b_time_known"))
                    if _b_time_known:
                        _b_time = time(
                            int(st.session_state.get("compat_b_hour", 12)),
                            int(st.session_state.get("compat_b_minute", 0)),
                        )
                    _b_gender_map = {"男": "male", "女": "female", "其他": "other", "不填寫": "unknown"}
                    _b_gender_val = _b_gender_map.get(st.session_state.get("compat_b_gender", "不填寫"), "unknown")
                    _b_city = st.session_state.get("compat_b_city", "台北").strip() or "台北"
                    _b_country = st.session_state.get("compat_b_country", "台灣").strip() or "台灣"
                    _loc_b = lookup_location(_b_city)
                    st.session_state["compat_b_profile"] = BirthProfile(
                        name=_b_name,
                        gender=Gender(_b_gender_val),
                        birth_date=date(
                            int(st.session_state.get("compat_b_year", 1991)),
                            int(st.session_state.get("compat_b_month", 1)),
                            int(st.session_state.get("compat_b_day", 1)),
                        ),
                        birth_time=_b_time,
                        birth_city=_b_city,
                        birth_country=_b_country,
                        blood_type=BloodType(st.session_state.get("compat_b_blood", "Unknown")),
                        themes=list(AnalysisTheme),
                        report_length=ReportLength.STANDARD,
                        birth_latitude=_loc_b["lat"] if _loc_b else None,
                        birth_longitude=_loc_b["lon"] if _loc_b else None,
                        birth_timezone_offset=8.0,
                        birth_time_is_known=_b_time_known,
                    )
                    st.success(f"B 方已確認：{_b_name}")
            except Exception as _e:
                st.error(f"B 方資料錯誤：{_e}")

    if st.session_state.get("compat_b_profile"):
        _pb = st.session_state["compat_b_profile"]
        st.info(f"✅ B 方：{_pb.name}（{_pb.birth_date}，{_pb.birth_city}）")

    # ── Demo couple buttons (developer/demo mode only) ────────────────────────
    if SHOW_DEMO_DATA:
        st.divider()
        st.subheader("⚡ 快速體驗")
        st.caption("直接載入範例資料，體驗合盤分析流程。")
        _DEMO_RT_MAP = {"romantic": "情侶 / 伴侶", "business": "合作夥伴", "parent_child": "親子"}
        _DEMO_ICONS = ["💑", "🤝", "👨‍👩‍👧"]
        _demo_cols = st.columns(len(SAMPLE_COUPLES))
        for _di, (_dcol, _couple) in enumerate(zip(_demo_cols, SAMPLE_COUPLES)):
            with _dcol:
                _btn_label = f"{_DEMO_ICONS[_di] if _di < len(_DEMO_ICONS) else '👥'} {_couple['label']}"
                if st.button(_btn_label, use_container_width=True, key=f"compat_demo_{_di}"):
                    st.session_state["compat_a_profile"] = _couple["person_a"]
                    st.session_state["compat_b_profile"] = _couple["person_b"]
                    _rt_ui = _DEMO_RT_MAP.get(_couple["relationship_type"], "一般關係")
                    st.session_state["compat_rel_type"] = _rt_ui
                    st.session_state["compatibility_report"] = None
                    st.session_state[f"show_demo_info_{_di}"] = True
                    st.rerun()
                if st.session_state.get(f"show_demo_info_{_di}"):
                    st.caption(_couple.get("description", ""))
                    _tps = _couple.get("talking_points", [])
                    if _tps:
                        st.markdown("**展示重點：**")
                        for _tp in _tps:
                            st.markdown(f"- {_tp}")

    # ── Generate ──────────────────────────────────────────────────────────────
    st.divider()
    _can_generate = (
        st.session_state.get("compat_a_profile") is not None
        and st.session_state.get("compat_b_profile") is not None
    )
    if not _can_generate:
        st.info("請確認 A 方與 B 方資料後，再產生合盤分析。")

    if st.button("💕 產生合盤分析", type="primary", use_container_width=True,
                 disabled=not _can_generate, key="compat_generate"):
        with st.spinner("正在計算合盤分析，請稍候…"):
            try:
                _ci = CompatibilityInput(
                    person_a=st.session_state["compat_a_profile"],
                    person_b=st.session_state["compat_b_profile"],
                    relationship_type=selected_rt,
                )
                _engine = CompatibilityEngine()
                _cr = _engine.generate(_ci)
                st.session_state["compatibility_report"] = _cr
                st.success("合盤分析完成！")
            except Exception as _err:
                st.error(f"合盤計算錯誤：{_err}")

    # ── Results ───────────────────────────────────────────────────────────────
    _cr = st.session_state.get("compatibility_report")
    if _cr is not None:
        sc = _cr.score_breakdown
        st.divider()
        st.subheader(f"🎯 合盤結果：{_cr.person_a_profile.name} × {_cr.person_b_profile.name}")

        # Score overview
        om1, om2 = st.columns([1, 3])
        with om1:
            st.metric("綜合評分", f"{sc.overall_score}/100")
            st.caption(sc.score_label())
            _dyn = sc.dynamic_label()
            if _dyn != sc.score_label():
                st.caption(f"🔍 {_dyn}")
        with om2:
            sm1, sm2, sm3, sm4 = st.columns(4)
            sm1.metric("情感共鳴", sc.emotional_score)
            sm2.metric("溝通契合", sc.communication_score)
            sm3.metric("吸引力", sc.attraction_score)
            sm4.metric("穩定性", sc.stability_score)
            sm5, sm6, sm7, _ = st.columns(4)
            sm5.metric("成長潛力", sc.growth_score)
            sm6.metric("衝突強度", sc.conflict_score)
            sm7.metric("協作效能", sc.collaboration_score)
        st.caption("⚠️ 衝突分數高代表張力強，不代表關係不好。")

        # Tabs (16 tabs, V1.8.2 adds visual chart tabs)
        (tab_overview, tab_emo_comm, tab_attract, tab_conflict,
         tab_adv_astro, tab_synastry, tab_composite,
         tab_visual_overview, tab_visual_aspects, tab_visual_composite,
         tab_astro, tab_bazi, tab_ziwei, tab_num_blood,
         tab_md, tab_export_tab) = st.tabs([
            "總覽", "情緒 / 溝通", "吸引力 / 合作", "衝突修復",
            "進階西洋合盤", "相位矩陣", "Composite 中點盤",
            "視覺總覽", "相位分類圖", "Composite 分布圖",
            "西洋占星", "八字", "紫微", "靈數 / 血型",
            "報告原文", "匯出",
        ])

        with tab_overview:
            st.markdown(f"**關係總論**\n\n{_cr.synthesis.relationship_summary}")
            st.subheader("關係優勢")
            for s in _cr.synthesis.strengths:
                st.markdown(f"- ✅ {s}")
            st.subheader("關係挑戰")
            for c in _cr.synthesis.challenges:
                st.markdown(f"- ⚡ {c}")
            st.subheader("溝通建議")
            for i, a in enumerate(_cr.synthesis.practical_advice, 1):
                st.markdown(f"{i}. {a}")

        with tab_emo_comm:
            _syn = _cr.synthesis
            st.subheader("情緒互動模式")
            st.markdown(_syn.emotional_pattern)
            st.divider()
            st.subheader("溝通模式")
            st.markdown(_syn.communication_pattern)

        with tab_attract:
            st.subheader("吸引力與合作動能")
            st.markdown(_cr.synthesis.attraction_pattern)

        with tab_conflict:
            st.subheader("衝突模式")
            st.markdown(_cr.synthesis.conflict_pattern)
            st.divider()
            st.subheader("衝突修復步驟")
            _repair_steps = [
                "**暫停** — 感到情緒升高時，約定「暫停 20 分鐘」的信號。",
                "**命名情緒** — 用「我現在感到…」說出自己的情緒狀態。",
                "**回到事實** — 只描述具體發生的事，不加推測或標籤。",
                "**說明需求** — 表達「我需要的是…」，而非期待對方猜測。",
                "**約定下一步** — 衝突結束前，各說一個可以做到的具體行動。",
                "**不翻舊帳** — 每次衝突只處理當下議題。",
                "**不用沉默懲罰** — 需要空間時說出來，而不是冷戰。",
            ]
            for i, s in enumerate(_repair_steps, 1):
                st.markdown(f"{i}. {s}")
            st.divider()
            st.subheader("30 天關係練習")
            for p in _cr.synthesis.thirty_day_practice:
                st.markdown(f"- {p}")

        # ── V1.8.0: Advanced Astrology tabs ──────────────────────────────────
        _adv = getattr(_cr, "advanced_astrology", None)

        with tab_adv_astro:
            st.caption("Synastry 觀察兩人星盤互動；Composite Chart 觀察關係本身形成的共同場域。兩者皆為關係理解工具，不代表絕對適合度。")
            if _adv is None:
                st.info("進階西洋合盤資料尚未計算或不可用。")
            else:
                from compatibility.advanced_astrology import (
                    CONFLICT_CAPTION as _CONFLICT_CAP,
                    ADVANCED_SCORE_DISCLAIMER as _ADV_DISC,
                )
                _adv_sc = _adv.advanced_scores
                _label_desc = {
                    "高度共鳴但仍需經營": "雙方在多個維度高度契合，互動通常自然流暢，但長期關係仍需持續投入與溝通設計。",
                    "互補良好": "差異帶來活力，兩人能在各自優勢中找到平衡，合作潛力強。",
                    "有潛力但需溝通設計": "有良好基礎，但部分面向需要刻意建立溝通節奏才能發揮最大潛力。",
                    "張力明顯，需成熟互動": "互動中存在明顯張力，需要較高的情緒成熟度與溝通技巧才能穩固關係。",
                    "高壓關係，需要清楚界線": "挑戰較多，建議先各自穩固個人狀態，並在關係中建立清楚的界線與修復流程。",
                }
                with st.container(border=True):
                    st.subheader("📊 分數總覽")
                    _col_total, _col_label = st.columns([1, 2])
                    with _col_total:
                        st.metric("進階合盤總分", f"{_adv_sc.overall_advanced_score} / 100")
                        st.markdown(f"**{_adv_sc.label}**")
                    with _col_label:
                        _desc = _label_desc.get(_adv_sc.label, "")
                        if _desc:
                            st.info(_desc)
                    _c1, _c2 = st.columns(2)
                    with _c1:
                        st.metric("情緒連結", _adv_sc.emotional_bond)
                        st.metric("溝通流暢度", _adv_sc.communication_flow)
                        st.metric("吸引力 / 化學反應", _adv_sc.attraction_chemistry)
                        st.metric("穩定潛力", _adv_sc.stability_potential)
                    with _c2:
                        st.metric("成長張力", _adv_sc.growth_intensity)
                        st.metric("衝突強度（張力計）", _adv_sc.conflict_intensity)
                        st.caption(_CONFLICT_CAP)
                        st.metric("長期潛力", _adv_sc.long_term_potential)
                    st.caption(_adv_sc.explanation)
                if _adv.strengths:
                    with st.container(border=True):
                        st.subheader("✅ 優勢")
                        for _s in _adv.strengths:
                            st.markdown(f"- {_s}")
                if _adv.challenges:
                    with st.container(border=True):
                        st.subheader("⚡ 挑戰")
                        for _ch in _adv.challenges:
                            st.markdown(f"- {_ch}")
                if _adv.repair_advice:
                    with st.container(border=True):
                        st.subheader("🔧 修復建議")
                        for _ra in _adv.repair_advice:
                            st.markdown(f"- {_ra}")
                st.caption(_adv.accuracy_note)
                st.caption(_ADV_DISC)

        with tab_synastry:
            if _adv is None:
                st.info("相位矩陣資料尚未計算或不可用。")
            else:
                from compatibility.advanced_astrology import (
                    aspect_type_zh as _atz, category_zh as _cz,
                    aspect_nature as _an, format_orb as _fo,
                )
                import pandas as _pd
                sm = _adv.synastry_matrix
                st.caption("相位強度代表兩人星盤互動的明顯程度，不代表好壞。張力相位通常代表需要溝通設計，和諧相位代表自然流動較多。")
                if sm.aspects:
                    # Top cards
                    _top_str = sm.strongest_aspects[0] if sm.strongest_aspects else None
                    _top_attr = next((a for a in sm.aspects if a.category == "attraction"), None)
                    _top_emo = next((a for a in sm.aspects if a.category == "emotional"), None)
                    _top_ten = sm.tension_aspects[0] if sm.tension_aspects else None
                    _tc1, _tc2, _tc3, _tc4 = st.columns(4)
                    _tc1.metric("最強相位",
                                f"{_top_str.person_a_planet}×{_top_str.person_b_planet}" if _top_str else "暫無",
                                f"{_atz(_top_str.aspect_type)} 強度{_top_str.strength}" if _top_str else None)
                    _tc2.metric("最強吸引力",
                                f"{_top_attr.person_a_planet}×{_top_attr.person_b_planet}" if _top_attr else "暫無",
                                _atz(_top_attr.aspect_type) if _top_attr else None)
                    _tc3.metric("最強情緒連結",
                                f"{_top_emo.person_a_planet}×{_top_emo.person_b_planet}" if _top_emo else "暫無",
                                _atz(_top_emo.aspect_type) if _top_emo else None)
                    _tc4.metric("最強張力",
                                f"{_top_ten.person_a_planet}×{_top_ten.person_b_planet}" if _top_ten else "暫無",
                                _atz(_top_ten.aspect_type) if _top_ten else None)
                    st.divider()
                    # Filters
                    _fcol1, _fcol2, _fcol3, _fcol4 = st.columns([3, 1, 1, 1])
                    _all_cats = sorted({_cz(a.category) for a in sm.aspects})
                    _sel_cats = _fcol1.multiselect("分類篩選", options=_all_cats, default=_all_cats, key="syn_cat_filter")
                    _only_str = _fcol2.checkbox("只看最強", key="syn_top_filter")
                    _only_ten = _fcol3.checkbox("只看張力", key="syn_tension_filter")
                    _only_har = _fcol4.checkbox("只看和諧", key="syn_harmony_filter")
                    # Sort: strongest first, then strength desc, orb asc
                    _strong_keys = {(a.person_a_planet, a.person_b_planet, a.aspect_type) for a in sm.strongest_aspects}
                    _sorted = sorted(
                        sm.aspects,
                        key=lambda a: (0 if (a.person_a_planet, a.person_b_planet, a.aspect_type) in _strong_keys else 1,
                                       -a.strength, a.orb)
                    )
                    # Apply filters
                    _filtered = _sorted
                    if _only_str:
                        _filtered = [a for a in _filtered
                                     if (a.person_a_planet, a.person_b_planet, a.aspect_type) in _strong_keys]
                    if _only_ten:
                        _filtered = [a for a in _filtered if a.is_challenging]
                    if _only_har:
                        _filtered = [a for a in _filtered if a.is_harmonious]
                    if _sel_cats != _all_cats:
                        _filtered = [a for a in _filtered if _cz(a.category) in _sel_cats]
                    _asp_data = [{
                        "A 行星": a.person_a_planet,
                        "B 行星": a.person_b_planet,
                        "相位": _atz(a.aspect_type),
                        "容許度 orb": _fo(a.orb),
                        "強度": a.strength,
                        "分類": _cz(a.category),
                        "性質": _an(a),
                        "解讀": a.interpretation,
                    } for a in _filtered]
                    st.dataframe(_pd.DataFrame(_asp_data), use_container_width=True, hide_index=True)
                    st.caption(sm.accuracy_note)
                else:
                    st.info("無可計算相位（行星經度資料不足）。")

        with tab_composite:
            if _adv is None:
                st.info("Composite Chart 資料尚未計算或不可用。")
            else:
                from compatibility.advanced_astrology import COMPOSITE_INTRO as _COMP_INTRO
                import pandas as _pd
                cc = _adv.composite_chart
                st.caption(_COMP_INTRO)
                if not cc.ascendant_sign:
                    st.info("Composite ASC / MC 需要雙方精準出生時間與出生地，本次未納入四軸解讀。")
                # Core planet cards
                _key_planet_roles = {
                    "太陽": "關係核心目的",
                    "月亮": "情緒氣候",
                    "金星": "親密與喜好",
                    "火星": "行動與衝突",
                    "土星": "承諾與壓力",
                }
                _cp_dict = {p.planet: p for p in cc.planets}
                with st.container(border=True):
                    st.subheader("核心行星")
                    for _planet_zh, _role in _key_planet_roles.items():
                        _cp = _cp_dict.get(_planet_zh)
                        if _cp:
                            _pcol1, _pcol2 = st.columns([1, 3])
                            with _pcol1:
                                st.metric(f"Composite {_planet_zh}", _cp.sign)
                                st.caption(_role)
                            with _pcol2:
                                if _cp.interpretation:
                                    st.markdown(_cp.interpretation)
                            st.divider()
                # Full planet table
                if cc.planets:
                    _planet_data = [{
                        "行星": p.planet,
                        "星座": p.sign,
                        "度數": f"{p.longitude:.1f}°",
                        "宮位": str(p.house) if p.house is not None else "─",
                        "解讀": p.interpretation or "─",
                    } for p in cc.planets]
                    with st.expander("完整行星表格"):
                        st.dataframe(_pd.DataFrame(_planet_data), use_container_width=True, hide_index=True)
                st.caption(cc.accuracy_note)

        # ── V1.8.2: Visual chart tabs ─────────────────────────────────────────
        _vis = getattr(_cr, "visuals", None)
        if _vis is None and _adv is not None:
            try:
                from compatibility.visuals import build_relationship_visuals as _bv
                _vis = _bv(_adv)
            except Exception:
                _vis = None

        with tab_visual_overview:
            st.caption("衝突張力是互動強度的指標，不是壞分數。視覺圖表呈現互動模式，不代表適合度的絕對評分。")
            if _vis is None:
                st.info("視覺圖表需要進階合盤資料，目前不可用。")
            else:
                import pandas as _pd
                _r = _vis.radar
                _radar_df = _pd.DataFrame({
                    "維度": _r.labels,
                    "分數": _r.values,
                })
                st.subheader(_r.title)
                st.bar_chart(_radar_df.set_index("維度"))
                st.caption(_r.description)
                st.divider()
                _vc1, _vc2, _vc3, _vc4 = st.columns(4)
                _vc1.metric("情緒連結", _r.values[0])
                _vc2.metric("溝通理解", _r.values[1])
                _vc3.metric("吸引力",   _r.values[2])
                _vc4.metric("穩定度",   _r.values[3])
                _vc5, _vc6, _vc7, _ = st.columns(4)
                _vc5.metric("成長張力", _r.values[4])
                _vc6.metric("衝突張力", _r.values[5])
                _vc7.metric("長期潛力", _r.values[6])
                st.divider()
                st.markdown(f"**摘要：** {_vis.summary}")

        with tab_visual_aspects:
            st.caption("和諧相位代表自然流動，張力相位代表需要修復流程。")
            if _vis is None:
                st.info("相位分類圖需要進階合盤資料，目前不可用。")
            else:
                import pandas as _pd
                _ac = _vis.aspect_categories
                _ab = _vis.aspect_balance
                _a1, _a2, _a3 = st.columns(3)
                _a1.metric("和諧相位", _ab.harmony_count, f"{_ab.harmony_percentage}%")
                _a2.metric("張力相位", _ab.tension_count, f"{_ab.tension_percentage}%")
                _a3.metric("混合/其他", _ab.neutral_count)
                st.divider()
                _cat_df = _pd.DataFrame({
                    "分類":     _ac.categories,
                    "相位數":   _ac.counts,
                    "平均強度": _ac.strengths,
                })
                st.subheader(_ac.title)
                st.bar_chart(_cat_df.set_index("分類")["相位數"])
                st.dataframe(_cat_df, use_container_width=True, hide_index=True)
                st.caption(_ac.description)

        with tab_visual_composite:
            st.caption("Composite 分布用來觀察關係本身的共同場域，不代表任何一方個人命盤。")
            if _vis is None:
                st.info("Composite 分布圖需要進階合盤資料，目前不可用。")
            else:
                import pandas as _pd
                _cd = _vis.composite_distribution
                _cv1, _cv2 = st.columns(2)
                with _cv1:
                    st.subheader("元素分布")
                    _elem_df = _pd.DataFrame({
                        "元素": [f"{k}象" for k in _cd.elements.keys()],
                        "行星數": list(_cd.elements.values()),
                    })
                    st.bar_chart(_elem_df.set_index("元素"))
                    st.dataframe(_elem_df, use_container_width=True, hide_index=True)
                with _cv2:
                    st.subheader("星座模式")
                    _mod_df = _pd.DataFrame({
                        "模式": list(_cd.modalities.keys()),
                        "行星數": list(_cd.modalities.values()),
                    })
                    st.bar_chart(_mod_df.set_index("模式"))
                    st.dataframe(_mod_df, use_container_width=True, hide_index=True)
                if _cd.planets:
                    _planet_sign_df = _pd.DataFrame({
                        "行星": _cd.planets,
                        "星座": _cd.signs,
                    })
                    with st.expander("Composite 行星星座表"):
                        st.dataframe(_planet_sign_df, use_container_width=True, hide_index=True)

        with tab_astro:
            ast = _cr.astrology
            st.markdown(f"- **太陽**：{ast.sun_pair}")
            st.markdown(f"- **月亮**：{ast.moon_pair}")
            st.markdown(f"- **水星**：{ast.mercury_pair}")
            st.markdown(f"- **金星火星**：{ast.venus_mars_pair}")
            st.markdown(f"- **上升**：{ast.ascendant_pair}")
            if ast.key_aspects:
                st.write("**主要相位：**")
                for a in ast.key_aspects:
                    st.write(f"- {a}")
            st.markdown(ast.interpretation)
            st.caption(f"準確度：{ast.accuracy_note}")

        with tab_bazi:
            bz = _cr.bazi
            st.markdown(f"- **A 日主**：{bz.person_a_day_master}")
            st.markdown(f"- **B 日主**：{bz.person_b_day_master}")
            st.markdown(f"- **日主關係**：{bz.day_master_relation}")
            st.markdown(bz.interpretation)
            st.caption(f"準確度：{bz.accuracy_note}")

        with tab_ziwei:
            zw = _cr.ziwei
            st.markdown(f"- **A 命宮**：{zw.person_a_ming_palace}")
            st.markdown(f"- **B 命宮**：{zw.person_b_ming_palace}")
            st.markdown(f"- **主星共鳴**：{zw.main_star_resonance}")
            st.markdown(zw.interpretation)
            st.caption(f"準確度：{zw.accuracy_note}")

        with tab_num_blood:
            num = _cr.numerology
            st.subheader("生命靈數")
            st.markdown(f"- **靈數配對**：{num.life_path_pair}")
            st.markdown(num.interpretation)
            st.divider()
            bld = _cr.blood_type
            st.subheader("血型")
            st.markdown(f"- **血型配對**：{bld.blood_pair}")
            st.markdown(f"- **互動風格**：{bld.interaction_style}")
            st.markdown(f"- **建議**：{bld.advice}")

        with tab_md:
            st.text_area("報告原文", value=_cr.markdown_body, height=500,
                         label_visibility="collapsed")

        with tab_export_tab:
            st.subheader("📤 匯出合盤報告")
            st.caption("選擇適合用途的匯出格式：")
            ex1, ex2, ex3 = st.columns(3)
            _rt_str = _cr.relationship_type.value
            with ex1:
                st.caption("📝 **Markdown** — 適合二次編輯與純文字使用")
                _md_bytes = _cr.markdown_body.encode("utf-8")
                st.download_button(
                    label="📝 下載 Markdown",
                    data=_md_bytes,
                    file_name=make_compat_filename(
                        _cr.person_a_profile.name,
                        _cr.person_b_profile.name,
                        "md",
                        _rt_str,
                    ),
                    mime="text/markdown",
                    use_container_width=True,
                )
            with ex2:
                st.caption("🌐 **HTML** — 適合展示與列印")
                try:
                    _html_str = export_compat_to_html(_cr)
                    st.download_button(
                        label="🌐 下載 HTML",
                        data=_html_str.encode("utf-8"),
                        file_name=make_compat_filename(
                            _cr.person_a_profile.name,
                            _cr.person_b_profile.name,
                            "html",
                            _rt_str,
                        ),
                        mime="text/html",
                        use_container_width=True,
                    )
                except Exception as _he:
                    st.button("🌐 HTML（錯誤）", disabled=True, use_container_width=True)
                    st.warning(str(_he))
            with ex3:
                st.caption("📘 **Word** — 適合交付與排版")
                if _DocxExporter().is_available():
                    try:
                        _docx_bytes = export_compat_to_docx(_cr)
                        st.download_button(
                            label="📘 下載 Word",
                            data=_docx_bytes,
                            file_name=make_compat_filename(
                                _cr.person_a_profile.name,
                                _cr.person_b_profile.name,
                                "docx",
                                _rt_str,
                            ),
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True,
                        )
                    except Exception as _de:
                        st.button("📘 Word（錯誤）", disabled=True, use_container_width=True)
                        st.warning(str(_de))
                else:
                    st.button("📘 Word（未安裝）", disabled=True, use_container_width=True)
                    st.info("pip install python-docx")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 紫微校準
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧭 紫微校準":
    if not DEVELOPER_MODE:
        st.warning("此頁面僅開發人員模式可用。")
        st.info(
            "若為開發者，請以開發者模式啟動：\n\n"
            "**Windows CMD：** `set ASTRO_DEVELOPER_MODE=1` 後執行 `run_dev.bat`\n\n"
            "**PowerShell：** `$env:ASTRO_DEVELOPER_MODE=\"1\"` 後執行 `run_dev.bat`"
        )
        st.stop()
    st.title("🧭 紫微外部排盤校準")
    st.caption(
        "此工具用於將本系統紫微盤與外部網站 / 人工排盤逐項比對，"
        "協助判斷是演算法差異、流派差異，或外部網站自家評分模型。"
    )
    st.info(
        "目前紫微排盤已通過 Rossi 外部盤校準，但不同網站可能因流派、閏月、子時換日、"
        "輔星表、廟旺陷表與分數模型而產生差異。"
        "本系統會標示 calculation_mode 與 accuracy_note，"
        "並建議使用外部校準工具確認重大差異。"
    )
    st.divider()

    # ── A. Check if local chart is available ──────────────────────────────────
    _rpt = st.session_state.get("report")
    _zc = _rpt.ziwei_chart if _rpt else None

    if _zc is None:
        st.warning("⚠️ 尚無本機紫微命盤，請先在「📝 輸入資料」填寫資料並計算命盤。")
        if st.button("前往輸入資料"):
            _go_to_page("📝 輸入資料")
        st.stop()

    with st.expander("📋 本機紫微盤摘要", expanded=False):
        _mode = getattr(_zc, "calculation_mode", "unknown")
        st.markdown(f"**排盤模式**：{_mode}")
        st.markdown(f"**五行局**：{getattr(_zc, 'five_element_bureau', '—')}")
        st.markdown(f"**命宮地支**：{getattr(_zc, 'ming_branch', '—')}")
        st.markdown(f"**身宮地支**：{getattr(_zc, 'shen_branch', '—')}")
        st.markdown(f"**準確度說明**：{getattr(_zc, 'accuracy_note', '—')}")

    st.divider()

    # ── B. External chart input ────────────────────────────────────────────────
    from ziwei_reconciliation.examples import EXAMPLE_ROSSI_EXTERNAL_CHART, BLANK_EXTERNAL_CHART_JSON
    from ziwei_reconciliation.models import ExternalZiWeiChart

    _input_mode = st.radio(
        "外部盤輸入方式",
        ["使用內建 Rossi 截圖範例", "手動 JSON 輸入"],
        horizontal=True,
    )

    _ext_chart: ExternalZiWeiChart | None = None
    _parse_error: str = ""

    if _input_mode == "使用內建 Rossi 截圖範例":
        _ext_chart = EXAMPLE_ROSSI_EXTERNAL_CHART
        with st.expander("查看範例資料", expanded=False):
            import json as _json
            st.json(_ext_chart.model_dump())

    else:
        _json_input = st.text_area(
            "外部盤 JSON",
            value=BLANK_EXTERNAL_CHART_JSON,
            height=300,
        )
        st.caption("請依格式填入外部網站或人工排盤資料，不確定的欄位請留 null 或空白。")
        if _json_input.strip():
            try:
                import json as _json
                _parsed = _json.loads(_json_input)
                _ext_chart = ExternalZiWeiChart(**_parsed)
            except Exception as _e:
                _parse_error = str(_e)

    if _parse_error:
        st.error(f"JSON 解析失敗：{_parse_error}")

    # ── C. Run reconciliation ──────────────────────────────────────────────────
    if st.button("🔍 開始紫微校準比對", disabled=(_ext_chart is None), type="primary"):
        from ziwei_reconciliation.engine import ZiWeiReconciliationEngine
        with st.spinner("比對中…"):
            _rec_report = ZiWeiReconciliationEngine().reconcile(_zc, _ext_chart)
        st.session_state["ziwei_rec_report"] = _rec_report

    _rec_report = st.session_state.get("ziwei_rec_report")

    if _rec_report is None:
        st.info("填寫外部盤資料後，按「開始紫微校準比對」。")
        st.stop()

    # ── D. Display results ─────────────────────────────────────────────────────
    from ziwei_reconciliation.models import STATUS_ZH, SEVERITY_ZH, OVERALL_STATUS_ZH

    overall_zh = OVERALL_STATUS_ZH.get(_rec_report.overall_status, _rec_report.overall_status)
    _col1, _col2, _col3, _col4, _col5 = st.columns(5)
    with _col1:
        st.metric("整體狀態", overall_zh)
    with _col2:
        st.metric("✅ 一致", _rec_report.match_count)
    with _col3:
        st.metric("❌ 不一致", _rec_report.mismatch_count)
    with _col4:
        st.metric("🏫 流派差異", _rec_report.school_difference_count)
    with _col5:
        st.metric("⚙️ 尚未實作", _rec_report.not_implemented_count)

    st.caption(_rec_report.summary)

    _rtabs = st.tabs(["總覽", "一致項", "差異項", "流派差異", "尚未實作", "Markdown 報告"])

    with _rtabs[0]:
        st.markdown("### 建議")
        for _r in _rec_report.recommendation.split(". "):
            _r = _r.strip()
            if _r:
                st.write(f"• {_r}")

    with _rtabs[1]:
        _match_items = [i for i in _rec_report.items if i.status == "match"]
        if _match_items:
            import pandas as _pd
            _df = _pd.DataFrame([{
                "類別": i.category, "項目": i.field_name,
                "本機": i.local_value, "外部": i.external_value,
            } for i in _match_items])
            st.dataframe(_df, use_container_width=True, hide_index=True)
        else:
            st.info("無一致項。")

    with _rtabs[2]:
        _mm_items = [i for i in _rec_report.items if i.status == "mismatch"]
        if _mm_items:
            import pandas as _pd
            _df = _pd.DataFrame([{
                "類別": i.category, "項目": i.field_name,
                "本機": i.local_value, "外部": i.external_value,
                "嚴重度": SEVERITY_ZH.get(i.severity, i.severity),
                "說明": i.explanation,
            } for i in _mm_items])
            st.dataframe(_df, use_container_width=True, hide_index=True)
        else:
            st.success("無不一致項。")

    with _rtabs[3]:
        _sd_items = [i for i in _rec_report.items if i.status == "likely_school_difference"]
        if _sd_items:
            import pandas as _pd
            _df = _pd.DataFrame([{
                "類別": i.category, "項目": i.field_name,
                "本機": i.local_value, "外部": i.external_value,
                "說明": i.explanation,
            } for i in _sd_items])
            st.dataframe(_df, use_container_width=True, hide_index=True)
        else:
            st.info("無流派差異項。")

    with _rtabs[4]:
        _ni_items = [i for i in _rec_report.items if i.status == "not_implemented"]
        if _ni_items:
            import pandas as _pd
            _df = _pd.DataFrame([{
                "類別": i.category, "項目": i.field_name,
                "外部值": i.external_value, "說明": i.explanation,
            } for i in _ni_items])
            st.dataframe(_df, use_container_width=True, hide_index=True)
            st.caption("以上項目（好運指數、廟旺陷等）屬外部網站自家功能，不代表本機排盤有誤。")
        else:
            st.info("無尚未實作項。")

    with _rtabs[5]:
        st.markdown(_rec_report.markdown_body)
        st.download_button(
            "📥 下載 Markdown 報告",
            data=_rec_report.markdown_body.encode("utf-8"),
            file_name=f"ziwei_reconciliation_{_rec_report.created_at[:10]}.md",
            mime="text/markdown",
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 人類圖校準
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔷 人類圖校準":
    if not DEVELOPER_MODE:
        st.warning("此頁面僅開發人員模式可用。")
        st.info(
            "若為開發者，請以開發者模式啟動：\n\n"
            "**Windows CMD：** `set ASTRO_DEVELOPER_MODE=1` 後執行 `run_dev.bat`\n\n"
            "**PowerShell：** `$env:ASTRO_DEVELOPER_MODE=\"1\"` 後執行 `run_dev.bat`"
        )
        st.stop()
    st.title("🔷 人類圖外部排盤校準")
    st.caption(
        "此工具用於開發者比對外部人類圖網站結果（Jovian Archive / Genetic Matrix / MyBodyGraph）。"
        "客戶版不顯示。不應直接提供給客戶。"
    )
    st.info(
        "本工具不代表已完成外部校準。"
        "需從外部人類圖系統取得結果並輸入後，才能進行比對。"
        "如發現差異，本工具輸出差異原因與修正建議，不自動修改計算核心。"
    )
    st.divider()

    # ── Local chart summary ───────────────────────────────────────────────────
    _hd_rpt = st.session_state.get("report")
    _hd_local = _hd_rpt.human_design_chart if _hd_rpt else None

    if _hd_local is None:
        st.warning("⚠️ 尚無本機人類圖，請先在「📝 輸入資料」填寫資料並計算命盤。")
        if st.button("前往輸入資料"):
            _go_to_page("📝 輸入資料")
        st.stop()

    with st.expander("📋 本機人類圖摘要", expanded=True):
        _hd_c1, _hd_c2, _hd_c3, _hd_c4 = st.columns(4)
        with _hd_c1:
            st.metric("類型", _hd_local.type_name_zh)
        with _hd_c2:
            st.metric("Authority", _hd_local.authority[:20] if _hd_local.authority else "─")
        with _hd_c3:
            st.metric("Profile", _hd_local.profile)
        with _hd_c4:
            st.metric("計算模式", _hd_local.calculation_mode[:15])
        st.markdown(f"**策略**：{_hd_local.strategy}")
        st.markdown(f"**輪迴交叉**：{_hd_local.incarnation_cross}")
        _cs = next((a for a in _hd_local.conscious_activations if "sun" in a.planet.lower()), None)
        _ce = next((a for a in _hd_local.conscious_activations if "earth" in a.planet.lower()), None)
        _ds = next((a for a in _hd_local.design_activations if "sun" in a.planet.lower()), None)
        _de = next((a for a in _hd_local.design_activations if "earth" in a.planet.lower()), None)
        import pandas as _pd
        _summary_rows = [
            {"Side": "Conscious", "Planet": "Sun", "Gate": _cs.gate if _cs else "─", "Line": _cs.line if _cs else "─"},
            {"Side": "Conscious", "Planet": "Earth", "Gate": _ce.gate if _ce else "─", "Line": _ce.line if _ce else "─"},
            {"Side": "Design", "Planet": "Sun", "Gate": _ds.gate if _ds else "─", "Line": _ds.line if _ds else "─"},
            {"Side": "Design", "Planet": "Earth", "Gate": _de.gate if _de else "─", "Line": _de.line if _de else "─"},
        ]
        st.dataframe(_pd.DataFrame(_summary_rows), hide_index=True, use_container_width=True)
        st.markdown(
            f"**已定義中心**：{', '.join(_hd_local.defined_centers) or '無'}  \n"
            f"**已定義通道**：{len(_hd_local.defined_channels)} 個  \n"
            f"**啟動閘門**：{len(_hd_local.activated_gates)} 個"
        )

    with st.expander("🔬 Gate Wheel Offset 診斷", expanded=False):
        from config import HUMAN_DESIGN_GATE_WHEEL_OFFSET_DEGREES, HUMAN_DESIGN_DESIGN_DATE_METHOD
        _cur_offset = getattr(_hd_local, "gate_wheel_offset_degrees", 0.0)
        _cur_method = getattr(_hd_local, "design_date_method", "unknown")
        _solar_arc_err = getattr(_hd_local, "design_solar_arc_error_degrees", None)
        st.markdown(f"**現行設定**：Design Date Method = `{HUMAN_DESIGN_DESIGN_DATE_METHOD}` ｜ Gate Wheel Offset = `{HUMAN_DESIGN_GATE_WHEEL_OFFSET_DEGREES:+.3f}°`")
        st.markdown(f"**本機圖使用**：Method = `{_cur_method}` ｜ Offset = `{_cur_offset:+.3f}°`")
        if _solar_arc_err is not None:
            if _solar_arc_err > 0.1:
                st.warning(f"⚠️ Solar arc 誤差 {_solar_arc_err:.4f}°（>0.1°）。可能影響設計面閘門。")
            else:
                st.success(f"✅ Solar arc 誤差 {_solar_arc_err:.4f}° — 精準。")
        else:
            st.info("Solar arc 誤差未記錄（mock fallback 或 minus-88-days 模式）。")
        if _hd_local.design_activations:
            _sun_act = next((a for a in _hd_local.design_activations if "sun" in a.planet.lower()), None)
            if _sun_act:
                from human_design.calibration import simulate_gate_offset_for_activations
                _sim_results = simulate_gate_offset_for_activations(
                    {"Design Sun": _sun_act.longitude}, [-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0],
                )
                import pandas as _cal_pd
                st.dataframe(_cal_pd.DataFrame(_sim_results), hide_index=True, use_container_width=True)
        if getattr(_hd_local, "calibration_notes", []):
            for _cn in _hd_local.calibration_notes:
                st.write(f"- {_cn}")

    st.divider()

    # ── Four main tabs ────────────────────────────────────────────────────────
    from human_design_reconciliation.models import (
        ExternalHumanDesignChart, STATUS_ZH, SEVERITY_ZH, OVERALL_STATUS_ZH,
    )
    from human_design_reconciliation.templates import render_reconciliation_markdown
    from human_design_reconciliation.examples import (
        BLANK_EXTERNAL_HD_JSON, EXAMPLE_ROSSI_EXTERNAL_HD_JSON,
        BLANK_CALIBRATION_CASE_TEMPLATE, BLANK_DATASET_TEMPLATE, EXAMPLE_MINIMAL_EXTERNAL_CASE,
    )
    from human_design_reconciliation.dataset import (
        parse_external_chart_json, parse_calibration_case_json, parse_calibration_dataset_json,
        save_dataset, load_dataset, append_case_to_dataset,
    )
    from human_design_reconciliation.exporters import (
        export_reconciliation_markdown, export_batch_summary_markdown,
        export_reconciliation_html, export_dataset_json, safe_calibration_filename,
    )
    from human_design_reconciliation.engine import HumanDesignReconciliationEngine, reconcile_dataset
    import config as _hd_cfg

    _hd_main_tabs = st.tabs(["單案例比對", "外部案例匯入", "多案例資料集", "校準報告匯出"])

    # ══ Tab 1: 單案例比對 ═════════════════════════════════════════════════════
    with _hd_main_tabs[0]:
        st.subheader("單案例外部排盤比對")

        _hd_tpl_col1, _hd_tpl_col2 = st.columns(2)
        with _hd_tpl_col1:
            if st.button("載入空白模板", key="hd_single_blank"):
                st.session_state["hd_rec_json_input"] = BLANK_EXTERNAL_HD_JSON
        with _hd_tpl_col2:
            if st.button("載入 Rossi template", key="hd_single_rossi"):
                st.session_state["hd_rec_json_input"] = EXAMPLE_ROSSI_EXTERNAL_HD_JSON

        _hd_json_input = st.text_area(
            "外部盤 JSON（貼入外部人類圖資料）",
            value=st.session_state.get("hd_rec_json_input", BLANK_EXTERNAL_HD_JSON),
            height=280,
            key="hd_rec_json_input",
        )
        st.caption("請依格式填入外部網站資料，不確定的欄位請留 null 或空白。")

        _hd_ext_chart = None
        _hd_parse_error = ""
        if _hd_json_input and _hd_json_input.strip():
            try:
                _hd_ext_chart = parse_external_chart_json(_hd_json_input)
            except ValueError as _e:
                _hd_parse_error = str(_e)

        if _hd_parse_error:
            st.error(f"JSON 解析失敗：{_hd_parse_error}")

        if st.button("🔍 開始人類圖校準比對", disabled=(_hd_ext_chart is None), type="primary"):
            with st.spinner("比對中…"):
                _hd_rec_report = HumanDesignReconciliationEngine().reconcile(_hd_local, _hd_ext_chart)
            st.session_state["hd_rec_report"] = _hd_rec_report

        _hd_rec_report = st.session_state.get("hd_rec_report")
        if _hd_rec_report is None:
            st.info("填寫外部盤資料後，按「開始人類圖校準比對」。")
        else:
            _hd_overall_zh = OVERALL_STATUS_ZH.get(_hd_rec_report.overall_status, _hd_rec_report.overall_status)
            _hrc1, _hrc2, _hrc3, _hrc4, _hrc5 = st.columns(5)
            with _hrc1:
                st.metric("整體狀態", _hd_overall_zh)
            with _hrc2:
                st.metric("✅ 一致", _hd_rec_report.match_count)
            with _hrc3:
                st.metric("❌ 不一致", _hd_rec_report.mismatch_count)
            with _hrc4:
                st.metric("🏫 方法差異", _hd_rec_report.method_difference_count)
            with _hrc5:
                st.metric("⬜ 缺少外部", _hd_rec_report.missing_count)
            st.caption(_hd_rec_report.summary)

            _single_rtabs = st.tabs(["總覽", "一致項", "差異項", "方法差異", "Markdown 報告"])
            with _single_rtabs[0]:
                for _a in _hd_rec_report.next_actions:
                    st.write(f"• {_a}")
            with _single_rtabs[1]:
                _match_items = [i for i in _hd_rec_report.items if i.status == "match"]
                if _match_items:
                    st.dataframe(_pd.DataFrame([{"類別": i.category, "欄位": i.field, "本機": i.local_value, "外部": i.external_value} for i in _match_items]), use_container_width=True, hide_index=True)
                else:
                    st.info("無一致項。")
            with _single_rtabs[2]:
                _mm_items = [i for i in _hd_rec_report.items if i.status == "mismatch"]
                if _mm_items:
                    st.dataframe(_pd.DataFrame([{"類別": i.category, "欄位": i.field, "本機": i.local_value, "外部": i.external_value, "嚴重度": SEVERITY_ZH.get(i.severity, i.severity), "說明": i.explanation} for i in _mm_items]), use_container_width=True, hide_index=True)
                else:
                    st.success("無不一致項。")
            with _single_rtabs[3]:
                _md_items = [i for i in _hd_rec_report.items if i.status == "likely_method_difference"]
                if _md_items:
                    st.dataframe(_pd.DataFrame([{"類別": i.category, "欄位": i.field, "本機": i.local_value, "外部": i.external_value, "說明": i.explanation} for i in _md_items]), use_container_width=True, hide_index=True)
                else:
                    st.info("無方法差異項。")
            with _single_rtabs[4]:
                _hd_md_report = render_reconciliation_markdown(_hd_rec_report)
                st.markdown(_hd_md_report)
                st.download_button(
                    "📥 下載 Markdown 校準報告",
                    data=_hd_md_report.encode("utf-8"),
                    file_name="human_design_reconciliation_report.md",
                    mime="text/markdown",
                )

    # ══ Tab 2: 外部案例匯入 ═══════════════════════════════════════════════════
    with _hd_main_tabs[1]:
        st.subheader("外部案例匯入")
        st.caption("將外部人類圖案例儲存至校準資料集，供批次比對使用。")

        _imp_col1, _imp_col2, _imp_col3 = st.columns(3)
        with _imp_col1:
            if st.button("載入空白案例模板", key="hd_imp_blank"):
                st.session_state["hd_case_json_input"] = BLANK_CALIBRATION_CASE_TEMPLATE
        with _imp_col2:
            if st.button("載入 Sample 案例", key="hd_imp_sample"):
                st.session_state["hd_case_json_input"] = EXAMPLE_MINIMAL_EXTERNAL_CASE
        with _imp_col3:
            _uploaded_file = st.file_uploader("上傳 .json 案例檔", type=["json"], key="hd_case_uploader")
            if _uploaded_file is not None:
                try:
                    _uploaded_text = _uploaded_file.read().decode("utf-8")
                    st.session_state["hd_case_json_input"] = _uploaded_text
                except Exception as _ue:
                    st.error(f"檔案讀取失敗：{_ue}")

        _hd_case_json = st.text_area(
            "案例 JSON（貼入或上傳 HumanDesignCalibrationCase JSON）",
            value=st.session_state.get("hd_case_json_input", BLANK_CALIBRATION_CASE_TEMPLATE),
            height=300,
            key="hd_case_json_input",
        )

        _parsed_case = None
        _case_parse_error = ""
        if st.button("🔍 解析案例 JSON", key="hd_parse_case"):
            try:
                _parsed_case = parse_calibration_case_json(_hd_case_json)
                st.session_state["hd_parsed_case"] = _parsed_case
                st.success(f"解析成功：{_parsed_case.label} （ID: {_parsed_case.case_id}）")
            except ValueError as _ce:
                _case_parse_error = str(_ce)
                st.session_state["hd_parsed_case"] = None

        if _case_parse_error:
            st.error(f"案例解析失敗：{_case_parse_error}")

        _parsed_case = st.session_state.get("hd_parsed_case")
        if _parsed_case is not None:
            with st.expander("📋 已解析案例預覽", expanded=True):
                st.write(f"**ID**：{_parsed_case.case_id}")
                st.write(f"**Label**：{_parsed_case.label}")
                st.write(f"**Birth Date**：{_parsed_case.birth_date}")
                st.write(f"**Location**：{_parsed_case.birth_location or '─'}")
                ext_preview = _parsed_case.external_chart
                st.write(f"**Type**：{ext_preview.type_name or '─'} ｜ **Authority**：{ext_preview.authority or '─'} ｜ **Profile**：{ext_preview.profile or '─'}")

            _ds_path = _hd_cfg.HUMAN_DESIGN_CALIBRATION_DATASET_PATH
            _cur_ds = load_dataset(_ds_path)
            st.caption(f"目前資料集：{len(_cur_ds.cases)} 個案例 ｜ 路徑：{_ds_path}")

            if st.button("➕ 加入資料集並儲存", type="primary", key="hd_append_case"):
                _cur_ds = append_case_to_dataset(_cur_ds, _parsed_case)
                try:
                    save_dataset(_cur_ds, _ds_path)
                    st.success(f"已儲存！資料集現有 {len(_cur_ds.cases)} 個案例。")
                    st.session_state["hd_dataset"] = _cur_ds
                except Exception as _save_e:
                    st.error(f"儲存失敗：{_save_e}")

    # ══ Tab 3: 多案例資料集 ═══════════════════════════════════════════════════
    with _hd_main_tabs[2]:
        st.subheader("多案例資料集")

        _ds_path = _hd_cfg.HUMAN_DESIGN_CALIBRATION_DATASET_PATH
        if st.button("🔄 載入資料集", key="hd_load_ds"):
            _loaded_ds = load_dataset(_ds_path)
            st.session_state["hd_dataset"] = _loaded_ds

        _hd_ds = st.session_state.get("hd_dataset")
        if _hd_ds is None:
            _hd_ds = load_dataset(_ds_path)
            st.session_state["hd_dataset"] = _hd_ds

        st.caption(f"資料集路徑：{_ds_path} ｜ 案例數：{len(_hd_ds.cases)}")

        if _hd_ds.cases:
            _ds_rows = [
                {
                    "ID": c.case_id,
                    "Label": c.label,
                    "Birth Date": c.birth_date,
                    "Location": c.birth_location,
                    "Type": c.external_chart.type_name or "─",
                    "Profile": c.external_chart.profile or "─",
                }
                for c in _hd_ds.cases
            ]
            st.dataframe(_pd.DataFrame(_ds_rows), hide_index=True, use_container_width=True)

            if st.button("▶️ 執行批次校準比對", type="primary", key="hd_batch_run"):
                with st.spinner(f"批次比對 {len(_hd_ds.cases)} 個案例…"):
                    _batch_summary = reconcile_dataset(_hd_local, _hd_ds)
                st.session_state["hd_batch_summary"] = _batch_summary
                st.success(f"完成！已處理 {_batch_summary.processed_cases}/{_batch_summary.total_cases} 案例。")

            _batch_summary = st.session_state.get("hd_batch_summary")
            if _batch_summary:
                st.markdown("### 批次比對摘要")
                _bs1, _bs2, _bs3, _bs4 = st.columns(4)
                with _bs1:
                    st.metric("✅ 大致一致", _batch_summary.mostly_match_count)
                with _bs2:
                    st.metric("⚠️ 輕微差異", _batch_summary.minor_difference_count)
                with _bs3:
                    st.metric("❌ 重大差異", _batch_summary.major_difference_count)
                with _bs4:
                    st.metric("⬜ 資料不足", _batch_summary.insufficient_data_count)
                st.caption(_batch_summary.summary)
                if _batch_summary.most_common_mismatch_categories:
                    st.write(f"最常見差異類別：{', '.join(_batch_summary.most_common_mismatch_categories)}")
        else:
            st.info("資料集為空。請先在「外部案例匯入」頁面新增案例。")

    # ══ Tab 4: 校準報告匯出 ═══════════════════════════════════════════════════
    with _hd_main_tabs[3]:
        st.subheader("校準報告匯出")

        _hd_ds_exp = st.session_state.get("hd_dataset") or load_dataset(_hd_cfg.HUMAN_DESIGN_CALIBRATION_DATASET_PATH)
        _hd_single_rpt = st.session_state.get("hd_rec_report")
        _hd_batch_exp = st.session_state.get("hd_batch_summary")

        st.markdown("**單案例報告**")
        if _hd_single_rpt:
            _exp_md = export_reconciliation_markdown(_hd_single_rpt)
            _exp_html = export_reconciliation_html(_exp_md)
            _exp_fn_md = safe_calibration_filename("single_report", "md")
            _exp_fn_html = safe_calibration_filename("single_report", "html")
            _dl1, _dl2 = st.columns(2)
            with _dl1:
                st.download_button(
                    "📥 下載 Markdown 報告",
                    data=_exp_md.encode("utf-8"),
                    file_name=_exp_fn_md,
                    mime="text/markdown",
                    key="dl_single_md",
                )
            with _dl2:
                st.download_button(
                    "📥 下載 HTML 報告",
                    data=_exp_html.encode("utf-8"),
                    file_name=_exp_fn_html,
                    mime="text/html",
                    key="dl_single_html",
                )
        else:
            st.info("尚無單案例報告，請先在「單案例比對」執行比對。")

        st.markdown("**批次摘要報告**")
        if _hd_batch_exp:
            _exp_batch_md = export_batch_summary_markdown(_hd_batch_exp)
            _exp_batch_html = export_reconciliation_html(_exp_batch_md)
            _exp_fn_batch_md = safe_calibration_filename("batch_summary", "md")
            _exp_fn_batch_html = safe_calibration_filename("batch_summary", "html")
            _bdl1, _bdl2 = st.columns(2)
            with _bdl1:
                st.download_button(
                    "📥 下載批次摘要 Markdown",
                    data=_exp_batch_md.encode("utf-8"),
                    file_name=_exp_fn_batch_md,
                    mime="text/markdown",
                    key="dl_batch_md",
                )
            with _bdl2:
                st.download_button(
                    "📥 下載批次摘要 HTML",
                    data=_exp_batch_html.encode("utf-8"),
                    file_name=_exp_fn_batch_html,
                    mime="text/html",
                    key="dl_batch_html",
                )
        else:
            st.info("尚無批次摘要，請先在「多案例資料集」執行批次比對。")

        st.markdown("**資料集 JSON**")
        if _hd_ds_exp and _hd_ds_exp.cases:
            _exp_ds_json = export_dataset_json(_hd_ds_exp)
            _exp_fn_ds = safe_calibration_filename("dataset", "json")
            st.download_button(
                "📥 下載資料集 JSON",
                data=_exp_ds_json.encode("utf-8"),
                file_name=_exp_fn_ds,
                mime="application/json",
                key="dl_dataset_json",
            )
        else:
            st.info("資料集為空，無可匯出的 JSON。")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 設定
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️ 設定":
    st.title("⚙️ 應用程式設定")

    # ── Delivery mode status ──────────────────────────────────────────────────
    st.subheader("交付模式狀態")
    if DEVELOPER_MODE:
        st.info("🛠️ **DEV MODE 啟用** — 紫微校準、Demo 資料、內部工具均可用。")
        dm1, dm2, dm3, dm4 = st.columns(4)
        with dm1:
            st.metric("DEV MODE", "啟用 ✅")
        with dm2:
            st.metric("紫微校準", "可用 ✅")
        with dm3:
            st.metric("Demo 資料", "可用 ✅")
        with dm4:
            st.metric("客戶模式", "關閉")
    else:
        st.success("📦 **客戶交付模式** — 已啟用，開發工具已隱藏。")
        dm1, dm2, dm3, dm4 = st.columns(4)
        with dm1:
            st.metric("客戶模式", "啟用 ✅")
        with dm2:
            st.metric("開發者工具", "隱藏")
        with dm3:
            st.metric("Demo 資料", "隱藏")
        with dm4:
            st.metric("紫微校準", "隱藏")

    # ── System info ───────────────────────────────────────────────────────────
    st.divider()
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
