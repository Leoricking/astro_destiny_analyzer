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
from copy import deepcopy

# ── Bootstrap ─────────────────────────────────────────────────────────────────
from core.database import init_db
init_db()

from config import (
    APP_NAME, APP_SUBTITLE, APP_VERSION,
    TAIWAN_CITY_DISPLAY_NAMES, lookup_location,
    DEVELOPER_MODE, CUSTOMER_MODE, CONSULTANT_MODE, SHOW_DEMO_DATA, SHOW_INTERNAL_VERSION_INFO,
    BRAND_NAME, BRAND_TAGLINE, REPORT_WATERMARK,
    CLIENT_CASE_STORAGE_PATH, BUILD_PROFILE,
    APP_LANGUAGE, DEFAULT_LANGUAGE,  # V2.0.4 i18n
)
from i18n.translator import t, get_language_options  # V2.0.4 i18n
from i18n.display_names import (
    translate_zodiac, normalize_zodiac_value,
    translate_analysis_theme, normalize_analysis_theme,
    translate_report_length, normalize_report_length,
    translate_bazi_stem, translate_element, translate_hd_type,
    translate_hd_strategy, translate_hd_authority, translate_branch, translate_center,
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
try:
    from demo.sample_profiles import SAMPLE_PROFILES, SAMPLE_LABELS, SAMPLE_COUPLES
except ModuleNotFoundError:
    SAMPLE_PROFILES = {}
    SAMPLE_LABELS = {}
    SAMPLE_COUPLES = {}
except ImportError:
    SAMPLE_PROFILES = {}
    SAMPLE_LABELS = {}
    SAMPLE_COUPLES = {}
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

# ── Canonical Page IDs (V2.0.4) ──────────────────────────────────────────────
PAGE_HOME = "home"
PAGE_PUBLIC_CONTENT = "public_content"
PAGE_FREE_REPORT = "free_report"
PAGE_INPUT = "input"
PAGE_CALCULATE = "calculate"
PAGE_REPORT_PREVIEW = "report_preview"
PAGE_HISTORY = "history"
PAGE_EXPORT = "export"
PAGE_COMPATIBILITY = "compatibility"
PAGE_SETTINGS = "settings"
PAGE_LEAD_FUNNEL = "lead_funnel"
PAGE_CLIENT_CASES = "client_cases"
PAGE_ZIWEI_RECONCILIATION = "ziwei_reconciliation"
PAGE_HD_RECONCILIATION = "human_design_reconciliation"

_PAGES_BASE = [
    PAGE_HOME, PAGE_PUBLIC_CONTENT, PAGE_FREE_REPORT, PAGE_INPUT, PAGE_CALCULATE,
    PAGE_REPORT_PREVIEW, PAGE_HISTORY, PAGE_EXPORT, PAGE_COMPATIBILITY,
    PAGE_SETTINGS,
]
_PAGES_DEV = [
    PAGE_HOME, PAGE_PUBLIC_CONTENT, PAGE_FREE_REPORT, PAGE_INPUT, PAGE_CALCULATE,
    PAGE_REPORT_PREVIEW, PAGE_HISTORY, PAGE_EXPORT, PAGE_COMPATIBILITY,
    PAGE_LEAD_FUNNEL, PAGE_CLIENT_CASES,
    PAGE_ZIWEI_RECONCILIATION, PAGE_HD_RECONCILIATION, PAGE_SETTINGS,
]

# ── V2.0.0 Mode-specific page lists ──────────────────────────────────────────
CONSULTANT_PAGES: list = [
    PAGE_HOME, PAGE_PUBLIC_CONTENT, PAGE_FREE_REPORT, PAGE_INPUT, PAGE_CALCULATE,
    PAGE_REPORT_PREVIEW, PAGE_HISTORY, PAGE_EXPORT, PAGE_COMPATIBILITY,
    PAGE_LEAD_FUNNEL, PAGE_CLIENT_CASES,
    PAGE_SETTINGS,
]
CUSTOMER_PAGES: list = _PAGES_BASE
DEVELOPER_PAGES: list = _PAGES_DEV


def get_active_pages() -> list:
    """Return the page list for the current mode (V2.0.0 three-way split)."""
    if DEVELOPER_MODE:
        return DEVELOPER_PAGES
    elif CONSULTANT_MODE:
        return CONSULTANT_PAGES
    else:
        return CUSTOMER_PAGES


def is_page_allowed(page: str) -> bool:
    """Return True if page is visible in the current mode."""
    return page in get_active_pages()


def page_label(page_id: str, language: str | None = None) -> str:
    """Return the translated display label for a canonical page ID."""
    lang = language or st.session_state.get("app_language", DEFAULT_LANGUAGE)
    return t(f"nav.{page_id}", language=lang, default=page_id)


_PAGES = get_active_pages()  # CONSULTANT_MODE → CONSULTANT_PAGES; DEVELOPER_MODE → DEVELOPER_PAGES

_DEFAULT_THEME_VALUES = [
    "overall_personality", "relationships", "career", "wealth",
    "social", "family", "current_year", "next_three_years",
]

# ── Birth year constants ───────────────────────────────────────────────────────
DEFAULT_BIRTH_YEAR: int = 1990
MIN_BIRTH_YEAR:     int = 1900
MAX_BIRTH_YEAR:     int = date.today().year

# ── Country default ────────────────────────────────────────────────────────────
DEFAULT_COUNTRY: str = "台灣"

# ── Session state: global defaults (never overwrite existing values) ───────────
_GLOBAL_DEFAULTS: dict = {
    "profile": None,
    "report": None,
    "active_report_id": None,
    "nav_page": PAGE_HOME,
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
    "input_birth_country": DEFAULT_COUNTRY,
    "input_res_city": "",
    "input_res_country": "",
    "input_blood_type": "Unknown",
    "input_themes": [
        "overall_personality", "relationships", "career", "wealth",
        "social", "family", "current_year", "next_three_years",
    ],
    "input_report_lang": "auto",
    "input_report_len": "standard",
    "input_manual_lat": 0.0,
    "input_manual_lon": 0.0,
    "input_manual_tz": 8.0,
    "input_use_manual_latlon": False,
    "input_country_code": "TW",
    "input_city_query": "",
    "input_city_candidates": [],
    "input_selected_candidate_idx": 0,
    "input_location_confirmed": False,
    "input_manual_tz_name": "",
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



def _localized_age(value, language: str) -> str:
    formats = {
        "zh-TW": "{n}歲", "en": "{n}", "ja": "{n}歳",
        "th": "{n} ปี", "es": "{n} años", "ar": "{n} سنة",
    }
    return formats.get(language, "{n}").format(n=value)


def _report_length_label(value, language: str | None = None) -> str:
    """Return a localized report-length label for enum or string values."""
    lang = language or st.session_state.get("app_language", DEFAULT_LANGUAGE)
    raw = getattr(value, "value", value)
    key_map = {
        "short": "report_length.short",
        "簡短版": "report_length.short",
        "standard": "report_length.standard",
        "標準版": "report_length.standard",
        "full": "report_length.full",
        "完整版": "report_length.full",
        "complete": "report_length.complete",
        "10k": "report_length.ten_thousand",
        "complete_10k": "report_length.ten_thousand",
        "Complete 10K": "report_length.ten_thousand",
        "萬字完整版": "report_length.ten_thousand",
    }
    key = key_map.get(str(raw), "report_length.unknown")
    translated = t(key, language=lang, default=str(raw))
    return translated if translated != key else str(raw)

# ── Navigation helper ─────────────────────────────────────────────────────────

def _go_to_page(page_id: str) -> None:
    """Programmatically navigate without stale sidebar state snapping back.

    The browser can restore the previous value of a radio widget after any
    input field triggers a rerun.  Merely deleting one fixed widget key is not
    sufficient.  Store the canonical destination and rotate the navigation
    widget generation so the next run creates a fresh radio widget whose
    initial value is the requested page.
    """
    if page_id in get_active_pages():
        st.session_state["_pending_nav_page"] = page_id
        st.session_state["_nav_radio_generation"] = (
            int(st.session_state.get("_nav_radio_generation", 0)) + 1
        )
        # Backward compatibility with sessions created by older builds.
        st.session_state.pop("_nav_radio", None)
    st.rerun()


def _clear_input_state() -> None:
    """Reset all input fields to defaults and clear profile / report."""
    for k, v in _INPUT_DEFAULTS.items():
        st.session_state[k] = list(v) if isinstance(v, list) else v
    st.session_state["input_birth_year"] = DEFAULT_BIRTH_YEAR
    st.session_state["input_birth_year_user_touched"] = False
    st.session_state["profile"] = None
    st.session_state["report"] = None
    st.session_state.pop("_last_input_snapshot", None)


def _capture_input_snapshot() -> dict:
    """Capture the exact widget state used to create the current profile.

    Restoring from the raw widget snapshot is more reliable than rebuilding
    every field from the persisted profile because Smart Location, localized
    selectboxes, and multiselect widgets keep additional canonical state.
    """
    snapshot = {}
    for key, value in st.session_state.items():
        if key.startswith("input_") or key in {
            "birth_time_is_known", "_country_migrated",
        }:
            try:
                snapshot[key] = deepcopy(value)
            except Exception:
                snapshot[key] = value
    return snapshot


def _restore_input_snapshot(snapshot: dict) -> None:
    """Restore input values before any input-page widgets are instantiated."""
    if not snapshot:
        return
    # Remove display-only widget mirrors so their labels are rebuilt in the
    # current UI language while canonical values remain unchanged.
    for key in ("_country_sel", "_cand_sel", "_gender_display", "loc_search_btn"):
        st.session_state.pop(key, None)
    for key, value in snapshot.items():
        try:
            st.session_state[key] = deepcopy(value)
        except Exception:
            st.session_state[key] = value
    st.session_state["input_birth_year_user_touched"] = True


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

    birth_country_text = getattr(profile, "birth_country", None) or "台灣"
    st.session_state["input_birth_country"] = birth_country_text

    # Restore the smart-location widgets from the saved profile.  The UI stores
    # canonical country codes and candidate dictionaries, while older profiles
    # only contain display text.  Resolve the code without mutating the profile.
    try:
        from location.countries import COUNTRIES
        normalized_country = str(birth_country_text).strip().casefold()
        country_code = "TW"
        for code, names in COUNTRIES.items():
            if code == "OTHER":
                continue
            aliases = {str(code).casefold()} | {str(v).strip().casefold() for v in names.values()}
            if normalized_country in aliases:
                country_code = code
                break
    except Exception:
        country_code = "TW"

    birth_lat = getattr(profile, "birth_latitude", None)
    birth_lon = getattr(profile, "birth_longitude", None)
    birth_tz_name = getattr(profile, "birth_timezone", None) or ""
    st.session_state["input_country_code"] = country_code
    st.session_state["input_city_query"] = city
    st.session_state["input_manual_tz_name"] = birth_tz_name
    if birth_lat is not None and birth_lon is not None:
        restored_candidate = {
            "country_code": country_code,
            "country_name": birth_country_text,
            "country_display_name": birth_country_text,
            "region": "",
            "city": city,
            "city_display_name": city or birth_country_text,
            "latitude": float(birth_lat),
            "longitude": float(birth_lon),
            "timezone": birth_tz_name or "UTC",
            "source": "profile",
            "confidence": 1.0,
            "formatted_address": ", ".join(v for v in (city, birth_country_text) if v),
            "is_confirmed": True,
        }
        st.session_state["input_city_candidates"] = [restored_candidate]
        st.session_state["input_selected_candidate_idx"] = 0
        st.session_state["input_location_confirmed"] = True
    else:
        st.session_state["input_city_candidates"] = []
        st.session_state["input_selected_candidate_idx"] = 0
        st.session_state["input_location_confirmed"] = False

    st.session_state["input_res_city"] = getattr(profile, "residence_city", None) or ""
    st.session_state["input_res_country"] = getattr(profile, "residence_country", None) or ""
    st.session_state["input_blood_type"] = profile.blood_type.value if profile.blood_type else "Unknown"
    profile_themes = [normalize_analysis_theme(t.value) for t in getattr(profile, "themes", [])]
    st.session_state["input_themes"] = profile_themes or [
        "overall_personality", "relationships", "career", "wealth",
        "social", "family", "current_year", "next_three_years",
    ]
    _profile_lang_map = {
        "繁體中文": "zh-TW", "簡體中文": "zh-TW", "English": "en",
        "ไทย": "th", "日本語": "ja", "Español": "es", "العربية": "ar",
    }
    st.session_state["input_report_lang"] = _profile_lang_map.get(profile.report_language.value, "auto")
    st.session_state["input_report_len"] = normalize_report_length(profile.report_length.value)

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
    st.session_state["_pending_nav_page"] = PAGE_CALCULATE


# Apply a pending profile edit snapshot before any input widgets are created.
# This is deliberately performed on the next rerun: mutating widget-backed
# keys after their widgets were instantiated can make Streamlit ignore the
# restored values or raise a session-state exception.
if st.session_state.pop("_pending_profile_edit", False):
    _edit_snapshot = st.session_state.pop("_pending_input_snapshot", None)
    if _edit_snapshot:
        _restore_input_snapshot(_edit_snapshot)
    else:
        _edit_profile = st.session_state.get("profile")
        if _edit_profile is not None:
            for _widget_key in (
                "_country_sel", "_cand_sel", "_gender_display",
                "loc_search_btn",
            ):
                st.session_state.pop(_widget_key, None)
            _sync_input_state_from_profile(_edit_profile)

# Apply pending navigation before the radio widget is instantiated.
# Streamlit does not allow modifying a widget-backed session_state key after
# the widget has been created in the same run.
if "_pending_nav_page" in st.session_state:
    _pending_page = st.session_state.pop("_pending_nav_page")
    if _pending_page in get_active_pages():
        st.session_state["nav_page"] = _pending_page
        # Remove the legacy fixed key. The active radio below uses a
        # generation-specific key and therefore cannot restore the old page.
        st.session_state.pop("_nav_radio", None)

# Guard: stale session pointing to a page not in the active list → reset to home.
# Also keeps V1.x backward compat guards for developer-only calibration pages.
_active_pages = get_active_pages()
if st.session_state.get("nav_page") not in _active_pages:
    st.session_state["nav_page"] = PAGE_HOME
# Legacy explicit guards (retained for test compatibility and clarity):
if not DEVELOPER_MODE and st.session_state.get("nav_page") == PAGE_ZIWEI_RECONCILIATION:
    st.session_state["nav_page"] = PAGE_HOME
if not DEVELOPER_MODE and st.session_state.get("nav_page") == PAGE_HD_RECONCILIATION:
    st.session_state["nav_page"] = PAGE_HOME


# ── V2.0.4: Initialize language session state ─────────────────────────────
if "app_language" not in st.session_state:
    st.session_state["app_language"] = APP_LANGUAGE
if "report_language" not in st.session_state:
    st.session_state["report_language"] = "auto"


def _tr(key: str, **kwargs) -> str:
    """Translate key using current app language."""
    return t(key, language=st.session_state.get("app_language", DEFAULT_LANGUAGE), **kwargs)

_tr_lang = st.session_state.get("app_language", DEFAULT_LANGUAGE)

_REPORT_LANGUAGE_CODES = ["auto", "zh-TW", "en", "th", "ja", "es", "ar"]
_REPORT_LANGUAGE_SELF_NAMES = {
    "zh-TW": "繁體中文", "en": "English", "th": "ไทย",
    "ja": "日本語", "es": "Español", "ar": "العربية",
}

def _resolve_report_language() -> str:
    code = st.session_state.get("report_language", "auto")
    if code == "auto":
        return st.session_state.get("app_language", DEFAULT_LANGUAGE)
    return code if code in _REPORT_LANGUAGE_CODES else DEFAULT_LANGUAGE


def _localized_ziwei_summary(zc, language: str) -> None:
    """Render a safe localized Zi Wei overview without leaking Chinese prose."""
    copy = {
        "en": {"title": "Zi Wei Overview", "mode": "Calculation mode", "formal": "Formal Phase 1 chart", "note": "This overview presents the calculated Life Palace, Body Palace, lunar date, birth-hour branch, and Five-Element bureau. These values are preserved from the original chart calculation.", "lunar": "Lunar date", "hour": "Birth-hour branch", "ming": "Life Palace branch", "shen": "Body Palace branch", "bureau": "Five-element bureau"},
        "ja": {"title": "紫微斗数の概要", "mode": "計算モード", "formal": "正式配置 Phase 1", "note": "命宮・身宮・旧暦日・出生時支・五行局など、計算済みの主要情報を表示します。元の計算値は変更しません。", "lunar": "旧暦日", "hour": "出生時支", "ming": "命宮地支", "shen": "身宮地支", "bureau": "五行局"},
        "th": {"title": "ภาพรวม Zi Wei", "mode": "โหมดการคำนวณ", "formal": "ผังอย่างเป็นทางการ Phase 1", "note": "ภาพรวมนี้แสดง Life Palace, Body Palace, วันที่จันทรคติ กิ่งยามเกิด และโครงสร้างธาตุทั้งห้าจากผลคำนวณเดิม โดยไม่เปลี่ยนค่าของผัง", "lunar": "วันที่จันทรคติ", "hour": "กิ่งยามเกิด", "ming": "กิ่ง Life Palace", "shen": "กิ่ง Body Palace", "bureau": "โครงสร้างธาตุทั้งห้า"},
        "es": {"title": "Resumen de Zi Wei", "mode": "Modo de cálculo", "formal": "Carta formal Phase 1", "note": "Este resumen muestra el Palacio de Vida, el Palacio del Cuerpo, la fecha lunar, la rama de la hora natal y la estructura de Cinco Elementos calculados, sin alterar la carta original.", "lunar": "Fecha lunar", "hour": "Rama de la hora natal", "ming": "Rama del Palacio de Vida", "shen": "Rama del Palacio del Cuerpo", "bureau": "Estructura de Cinco Elementos"},
        "ar": {"title": "ملخص Zi Wei", "mode": "وضع الحساب", "formal": "خريطة رسمية Phase 1", "note": "يعرض هذا الملخص قصر الحياة وقصر الجسد والتاريخ القمري وفرع ساعة الميلاد وبنية العناصر الخمسة المحسوبة، من دون تغيير الخريطة الأصلية.", "lunar": "التاريخ القمري", "hour": "فرع ساعة الميلاد", "ming": "فرع قصر الحياة", "shen": "فرع قصر الجسد", "bureau": "بنية العناصر الخمسة"},
    }.get(language)
    if not copy:
        return
    st.subheader(copy["title"])
    st.info(copy["note"])
    mode = getattr(zc, "calculation_mode", "unknown")
    st.caption(f"{copy['mode']}: {copy['formal'] if mode == 'formal_layout_phase1' else mode}")
    cols = st.columns(5)
    lunar = "—"
    if getattr(zc, "lunar_year", None):
        lunar = f"{zc.lunar_year}/{zc.lunar_month}/{zc.lunar_day}"
    values = [
        (copy["lunar"], lunar),
        (copy["hour"], getattr(zc, "birth_hour_branch", None) or "—"),
        (copy["ming"], getattr(zc, "ming_branch", None) or "—"),
        (copy["shen"], getattr(zc, "shen_branch", None) or "—"),
        (copy["bureau"], getattr(zc, "five_element_bureau", None) or "—"),
    ]
    for col, (label, value) in zip(cols, values):
        with col:
            st.metric(label, value)


def _localized_hd_summary(hd, language: str) -> None:
    copy = {
        "en": ("Human Design Overview", "This overview shows the calculated Type, Strategy, Authority, Profile, defined Centers, and channel count. Use it for self-observation rather than fixed prediction."),
        "ja": ("ヒューマンデザイン概要", "計算されたタイプ、ストラテジー、オーソリティ、プロファイル、定義センター、チャネル数を表示します。固定的な予言ではなく自己観察の参考として活用してください。"),
        "th": ("ภาพรวม Human Design", "ภาพรวมนี้แสดง Type, Strategy, Authority, Profile, ศูนย์ที่นิยาม และจำนวน Channel จากผลคำนวณ ใช้เพื่อการสังเกตตนเอง ไม่ใช่คำทำนายตายตัว"),
        "es": ("Resumen de Human Design", "Este resumen muestra el Tipo, la Estrategia, la Autoridad, el Perfil, los Centros definidos y el número de Canales calculados. Úsalo para la autoobservación, no como predicción fija."),
        "ar": ("ملخص Human Design", "يعرض هذا الملخص النوع والاستراتيجية والسلطة الداخلية والملف والمراكز المحددة وعدد القنوات المحسوبة. استخدمه للملاحظة الذاتية لا كتنبؤ ثابت."),
    }.get(language)
    if not copy:
        return
    st.subheader(copy[0])
    st.info(copy[1])
    type_value = getattr(hd, "type_name", None) or getattr(hd, "type_name_zh", "—")
    strategy_value = getattr(hd, "strategy", "—")
    authority_value = getattr(hd, "authority", "—")
    cols = st.columns(6)
    values = [
        (_tr("human_design.type"), translate_hd_type(type_value, language)),
        (_tr("human_design.strategy"), translate_hd_strategy(strategy_value, language)),
        (_tr("human_design.authority"), translate_hd_authority(authority_value, language)),
        (_tr("human_design.profile"), getattr(hd, "profile", "—")),
        (_tr("human_design.centers"), len(getattr(hd, "defined_centers", []) or [])),
        (_tr("human_design.channels"), len(getattr(hd, "defined_channels", []) or [])),
    ]
    for col, (label, value) in zip(cols, values):
        with col:
            st.metric(label, value)

    _center_names = [translate_center(c, language) for c in (getattr(hd, "defined_centers", []) or [])]
    if _center_names:
        center_label = {"en":"Defined Centers","ja":"定義センター","th":"ศูนย์ที่นิยาม","es":"Centros definidos","ar":"المراكز المحددة"}.get(language, "Defined Centers")
        st.markdown(f"**{center_label}:** " + ", ".join(_center_names))


# V2.0.5: Apply RTL direction if needed
from i18n.rtl import apply_streamlit_direction as _apply_direction
_apply_direction(st.session_state.get("app_language", DEFAULT_LANGUAGE))


# ── Sidebar Navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.title(f"✨ {APP_NAME}")
    st.caption(_tr("app.subtitle"))
    st.divider()
    # Language selector
    _lang_options = get_language_options()
    _lang_codes = [c for c, _ in _lang_options]
    _lang_labels = [lbl for _, lbl in _lang_options]
    _cur_lang = st.session_state.get("app_language", DEFAULT_LANGUAGE)
    _cur_lang_idx = _lang_codes.index(_cur_lang) if _cur_lang in _lang_codes else 0
    _selected_lang_label = st.selectbox(
        _tr("language.label"),
        _lang_labels,
        index=_cur_lang_idx,
        key="_lang_sel_widget",
    )
    _selected_lang_code = _lang_codes[_lang_labels.index(_selected_lang_label)]
    if _selected_lang_code != st.session_state.get("app_language"):
        st.session_state["app_language"] = _selected_lang_code
        st.rerun()
    st.divider()
    # Navigation — canonical page IDs are the real widget values. Translation
    # is display-only. A generation-specific key prevents a stale browser
    # value (for example ``public_content``) from overriding a CTA jump to the
    # input page on the next text-field rerun.
    _cur_pages = get_active_pages()
    _cur_page_id = st.session_state.get("nav_page", PAGE_HOME)
    if _cur_page_id not in _cur_pages:
        _cur_page_id = _cur_pages[0]
    _cur_page_idx = _cur_pages.index(_cur_page_id)
    _nav_generation = int(st.session_state.get("_nav_radio_generation", 0))
    _nav_widget_key = f"_nav_radio_{_nav_generation}"
    page = st.radio(
        "nav",
        _cur_pages,
        index=_cur_page_idx,
        key=_nav_widget_key,
        format_func=page_label,
        label_visibility="collapsed",
    )
    st.session_state["nav_page"] = page

    # Entering the input page from any other page restores the most recent
    # partial snapshot. This keeps direct sidebar navigation and CTA navigation
    # behavior identical without clearing user input.
    _previous_page = st.session_state.get("_last_rendered_page")
    if page == PAGE_INPUT and _previous_page not in (None, PAGE_INPUT):
        _saved_snapshot = st.session_state.get("_last_input_snapshot")
        if _saved_snapshot:
            _restore_input_snapshot(_saved_snapshot)
        elif st.session_state.get("profile") is not None:
            _sync_input_state_from_profile(st.session_state.get("profile"))
    st.session_state["_last_rendered_page"] = page
    st.divider()
    if DEVELOPER_MODE:
        st.caption(f"v{APP_VERSION} · DEV MODE")
        st.caption(f"DEVELOPER_MODE=True")
    elif CONSULTANT_MODE:
        st.caption(f"v{APP_VERSION} · CONSULTANT MODE")
    else:
        st.caption(f"v{APP_VERSION}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 首頁
# ══════════════════════════════════════════════════════════════════════════════
if page == PAGE_HOME:
    st.title(f"✨ {_tr('app.title')}")
    st.subheader(_tr("app.subtitle"))
    st.markdown(
        _tr("home.welcome") + "\n\n"
        f"| {_tr('home.modules_table_header_module')} | {_tr('home.modules_table_header_desc')} |\n"
        "|------|------|\n"
        f"| {_tr('home.module_western')} | {_tr('home.module_western_desc')} |\n"
        f"| {_tr('home.module_bazi')} | {_tr('home.module_bazi_desc')} |\n"
        f"| {_tr('home.module_ziwei')} | {_tr('home.module_ziwei_desc')} |\n"
        f"| {_tr('home.module_blood')} | {_tr('home.module_blood_desc')} |\n"
        f"| {_tr('home.module_numerology')} | {_tr('home.module_numerology_desc')} |\n\n"
        f"{_tr('home.how_to_start')}\n"
        f"{_tr('home.step1')}\n"
        f"{_tr('home.step2')}\n"
        f"{_tr('home.step3')}\n"
        f"{_tr('home.step4')}\n\n"
        f"---\n> {_tr('home.disclaimer')}"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(_tr("home.metric_systems"), "5")
    with col2:
        st.metric(_tr("home.metric_sections"), "32")
    with col3:
        st.metric(_tr("home.metric_formats"), "Markdown / HTML / Word")

    _home_c1, _home_c2, _home_c3 = st.columns(3)
    with _home_c1:
        if st.button(_tr("home.btn_start_chart"), type="primary", use_container_width=True):
            _go_to_page(PAGE_INPUT)
    with _home_c2:
        if st.button(_tr("home.btn_compatibility"), use_container_width=True):
            _go_to_page(PAGE_COMPATIBILITY)
    with _home_c3:
        if st.button(_tr("home.btn_history"), use_container_width=True):
            _go_to_page(PAGE_HISTORY)

    # ── V2.0.2 三步驟 Onboarding ──────────────────────────────────────────────
    st.divider()
    st.subheader(_tr("home.quick_start.title"))
    _ob_c1, _ob_c2, _ob_c3 = st.columns(3)
    with _ob_c1:
        with st.container(border=True):
            st.markdown(f"**{_tr('home.quick_start.step1.title')}**")
            st.caption(_tr("home.quick_start.step1.description"))
    with _ob_c2:
        with st.container(border=True):
            st.markdown(f"**{_tr('home.quick_start.step2.title')}**")
            st.caption(_tr("home.quick_start.step2.description"))
    with _ob_c3:
        with st.container(border=True):
            st.markdown(f"**{_tr('home.quick_start.step3.title')}**")
            st.caption(_tr("home.quick_start.step3.description"))

    _cta_c1, _cta_c2, _cta_c3, _cta_c4 = st.columns(4)
    with _cta_c1:
        if st.button(_tr("home.btn_input"), use_container_width=True, key="home_cta_input"):
            _go_to_page(PAGE_INPUT)
    with _cta_c2:
        if st.button(_tr("home.btn_compat"), use_container_width=True, key="home_cta_compat"):
            _go_to_page(PAGE_COMPATIBILITY)
    with _cta_c3:
        if st.button(_tr("home.btn_content"), use_container_width=True, key="home_cta_content"):
            _go_to_page(PAGE_PUBLIC_CONTENT)
    with _cta_c4:
        if st.button(_tr("home.btn_free"), use_container_width=True, key="home_cta_free"):
            _go_to_page(PAGE_FREE_REPORT)

    if SHOW_DEMO_DATA and not SAMPLE_PROFILES and DEVELOPER_MODE:
        st.info("Demo profiles are not included in this release package.")
    if SHOW_DEMO_DATA and SAMPLE_PROFILES:
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
elif page == PAGE_PUBLIC_CONTENT:
    from public_content.content_registry import (
        get_public_content_catalog, get_public_page, list_public_pages, list_featured_pages,
    )
    from public_content.templates import (
        render_public_page_markdown, render_public_page_excerpt,
        render_public_catalog_markdown, render_public_catalog_html,
    )
    from public_content.localization import localize_public_page
    from public_content.exporters import (
        export_public_page_html, export_public_page_markdown,
        export_public_catalog_markdown, export_public_catalog_html,
        safe_public_content_filename,
    )

    _catalog = get_public_content_catalog()

    # ── A. Header ─────────────────────────────────────────────────────────────
    st.title(_tr("free_content.title"))
    st.caption(_tr("free_content.subtitle"))

    # ── B. Featured cards ─────────────────────────────────────────────────────
    _featured = list_featured_pages()
    if _featured:
        st.subheader(_tr("free_content.featured"))
        _fcols = st.columns(min(len(_featured), 3))
        for _i, _fp_source in enumerate(_featured):
            _fp, _fp_fallback = localize_public_page(_fp_source, _tr_lang)
            with _fcols[_i % 3]:
                st.markdown(f"**{_fp.title}**")
                if _fp.summary:
                    st.caption(_fp.summary[:160] + ("…" if len(_fp.summary) > 160 else ""))
                if _fp_fallback and _tr_lang != "zh-TW":
                    st.caption(_tr("report.partial_translation_notice"))
                if _fp.tags:
                    st.caption(_tr("public_content.tags_label") + " · ".join(_fp.tags))
                if _fp.cta_button_label:
                    if st.button(_fp.cta_button_label, key=f"feat_cta_{_fp.slug}"):
                        _go_to_page(_fp.cta_target)
        st.divider()

    # ── C. Category filter ────────────────────────────────────────────────────
    _CAT_CANONICAL = [None, "zodiac", "human_design", "compatibility", "ziwei", "bazi", "numerology", "guide"]
    _CAT_KEY_MAP = {
        None: "public_content.cat_all",
        "zodiac": "public_content.cat_zodiac",
        "human_design": "public_content.cat_human_design",
        "compatibility": "public_content.cat_compatibility",
        "ziwei": "public_content.cat_ziwei",
        "bazi": "public_content.cat_bazi",
        "numerology": "public_content.cat_numerology",
        "guide": "public_content.cat_guide",
    }
    _cat_labels_display = [_tr(_CAT_KEY_MAP[c]) for c in _CAT_CANONICAL]
    _cat_sel_label = st.selectbox(
        _tr("public_content.cat_filter"),
        options=_cat_labels_display,
        key="public_content_cat_filter",
    )
    _cat_sel_canonical = _CAT_CANONICAL[_cat_labels_display.index(_cat_sel_label)]
    _filtered_pages = list_public_pages(category=_cat_sel_canonical)

    # ── D. Page detail ────────────────────────────────────────────────────────
    _localized_pages = [localize_public_page(p, _tr_lang)[0] for p in _filtered_pages]
    _page_slugs = [p.slug for p in _localized_pages]
    if _page_slugs:
        _selected_slug = st.selectbox(
            _tr("public_content.select_page"),
            options=_page_slugs,
            format_func=lambda slug: next((p.title for p in _localized_pages if p.slug == slug), slug),
            key="public_content_page_select",
        )
        _sel_source = next((p for p in _filtered_pages if p.slug == _selected_slug), None)
        _sel_page, _sel_fallback = localize_public_page(_sel_source, _tr_lang) if _sel_source else (None, False)
        if _sel_page:
            if _sel_fallback and _tr_lang != "zh-TW":
                st.info(_tr("report.partial_translation_notice"))
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
                        _go_to_page(_sel_page.cta_target)
            # Free report secondary CTA
            if _sel_page.free_report_cta_slug:
                with _cta_col2:
                    if st.button(
                        _tr("public_content.free_report_cta"),
                        key="public_content_free_report_cta",
                    ):
                        st.session_state["free_report_type_preset"] = _sel_page.free_report_cta_slug
                        _go_to_page(PAGE_FREE_REPORT)

            # ── E. Export (developer mode only) ───────────────────────────────
            if DEVELOPER_MODE:
                from public_content.seo import validate_seo_data, build_meta_tags
                st.divider()
                st.subheader(_tr("public_content.dev_tools"))
                # SEO warnings
                _seo_warnings = validate_seo_data(_sel_page)
                if _seo_warnings:
                    st.warning("SEO warnings:\n" + "\n".join(f"- {w}" for w in _seo_warnings))
                else:
                    st.success(_tr("public_content.seo_pass"))
                # Meta tags preview
                with st.expander("Meta Tags"):
                    st.code(build_meta_tags(_sel_page), language="html")
                # Download buttons
                _md_content = export_public_page_markdown(_sel_page)
                _html_content = export_public_page_html(_sel_page)
                _dl1, _dl2 = st.columns(2)
                with _dl1:
                    st.download_button(
                        _tr("public_content.dl_markdown"),
                        data=_md_content.encode("utf-8"),
                        file_name=safe_public_content_filename(_sel_page.slug, "md"),
                        mime="text/markdown",
                    )
                with _dl2:
                    st.download_button(
                        _tr("public_content.dl_html"),
                        data=_html_content.encode("utf-8"),
                        file_name=safe_public_content_filename(_sel_page.slug, "html"),
                        mime="text/html",
                    )
                # Catalog export
                st.divider()
                st.caption(_tr("public_content.catalog_caption"))
                _cat_md = export_public_catalog_markdown(_catalog)
                _cat_html = export_public_catalog_html(_catalog)
                _cl1, _cl2 = st.columns(2)
                with _cl1:
                    st.download_button(
                        _tr("public_content.dl_catalog_md"),
                        data=_cat_md.encode("utf-8"),
                        file_name="public_content_catalog.md",
                        mime="text/markdown",
                    )
                with _cl2:
                    st.download_button(
                        _tr("public_content.dl_catalog_html"),
                        data=_cat_html.encode("utf-8"),
                        file_name="public_content_catalog.html",
                        mime="text/html",
                    )
    else:
        st.info(_tr("free_content.no_content"))


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 免費報告
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGE_FREE_REPORT:
    from lead_magnet.models import LeadProfile, PartnerProfile, LeadCapture
    from lead_magnet.storage import validate_email, append_lead, load_leads, export_leads_csv, delete_all_leads
    from lead_magnet.engine import generate_free_report
    from lead_magnet.templates import render_lead_capture_copy, render_upgrade_cta
    from lead_magnet.exporters import export_free_report_markdown, export_free_report_html, safe_free_report_filename
    import config as _lcfg

    st.title(_tr("free_report.title"))
    st.caption(_tr("free_report.subtitle"))
    st.info(_tr("free_report.info"))

    # ── B. Report type selector ───────────────────────────────────────────────
    _REPORT_TYPE_CANONICAL = ["zodiac_free_summary", "human_design_free_summary", "compatibility_free_summary", "integrated_free_summary"]
    _REPORT_TYPE_TR_KEYS = {
        "zodiac_free_summary": "free_report.type_zodiac",
        "human_design_free_summary": "free_report.type_human_design",
        "compatibility_free_summary": "free_report.type_compatibility",
        "integrated_free_summary": "free_report.type_integrated",
    }
    _preset = st.session_state.pop("free_report_type_preset", None)
    _preset_idx = _REPORT_TYPE_CANONICAL.index(_preset) if _preset in _REPORT_TYPE_CANONICAL else 0
    _rt_display_options = [_tr(_REPORT_TYPE_TR_KEYS[c]) for c in _REPORT_TYPE_CANONICAL]
    _rt_sel_display = st.selectbox(
        _tr("free_report.select_type"),
        options=_rt_display_options,
        index=_preset_idx,
        key="free_report_type_select",
    )
    _rt = _REPORT_TYPE_CANONICAL[_rt_display_options.index(_rt_sel_display)]
    _copy = render_lead_capture_copy(_rt, language=_tr_lang)
    st.subheader(_copy["title"])
    st.caption(_copy["description"])

    # ── C. Lead form ──────────────────────────────────────────────────────────
    with st.form("free_report_form"):
        _fm_name = st.text_input(_tr("free_report.name_label"), key="fr_name")
        _fm_email = st.text_input(_tr("free_report.email_label"), key="fr_email")
        _fm_date = st.text_input(_tr("free_report.birth_date_label"), key="fr_birth_date")
        _fm_time = st.text_input(_tr("free_report.birth_time_label"), key="fr_birth_time")
        _fm_loc = st.text_input(_tr("free_report.birth_loc_label"), key="fr_birth_loc")
        _show_partner = _rt == "compatibility_free_summary"
        if _show_partner:
            st.markdown(f"**{_tr('free_report.partner_section')}**")
            _fm_partner_name = st.text_input(_tr("free_report.partner_name_label"), key="fr_partner_name")
            _fm_partner_date = st.text_input(_tr("free_report.partner_date_label"), key="fr_partner_date")
            _fm_partner_time = st.text_input(_tr("free_report.partner_time_label"), key="fr_partner_time")
        _fm_consent = st.checkbox(_copy["consent_text"], key="fr_consent")
        _fm_mkt = st.checkbox(_tr("free_report.marketing_consent"), key="fr_marketing")
        _submitted = st.form_submit_button(_copy["button_label"], type="primary")

    if _submitted:
        _err = False
        if not validate_email(_fm_email):
            st.error(_tr("free_report.email_error"))
            _err = True
        if not _fm_consent:
            st.warning(_tr("free_report.consent_warning"))
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
                st.success(_tr("free_report.saved_ok"))
            except Exception as _e:
                st.warning(f"Storage note: {_e}")
            # Generate and display report
            _result = generate_free_report(_lead)
            st.markdown("---")
            st.markdown(export_free_report_markdown(_result))
            # CTA
            _ucta = render_upgrade_cta(_rt, language=_tr_lang)
            st.info(f"**{_ucta['title']}** — {_ucta['description']}")
            _uc1, _uc2, _uc3 = st.columns(3)
            with _uc1:
                if st.button(f"→ {_ucta['button_label']}", key="fr_upgrade_cta"):
                    st.session_state["nav_page"] = _ucta["target"]
                    st.rerun()
            with _uc2:
                st.download_button(
                    _tr("free_report.dl_md"),
                    data=export_free_report_markdown(_result).encode("utf-8"),
                    file_name=safe_free_report_filename(_fm_name, _rt, "md"),
                    mime="text/markdown",
                    key="fr_dl_md",
                )
            with _uc3:
                st.download_button(
                    _tr("free_report.dl_html"),
                    data=export_free_report_html(_result).encode("utf-8"),
                    file_name=safe_free_report_filename(_fm_name, _rt, "html"),
                    mime="text/html",
                    key="fr_dl_html",
                )

    # ── E. Developer mode area ────────────────────────────────────────────────
    if DEVELOPER_MODE:
        st.divider()
        st.subheader("Developer Tools: Leads Management")
        try:
            _snap = load_leads(_lcfg.LEAD_STORAGE_PATH)
        except Exception as _le:
            st.error(f"Leads 載入失敗：{_le}")
            _snap = None
        if _snap is not None:
            st.metric("Total Leads", len(_snap.leads))
            st.caption(f"Storage path: {_lcfg.LEAD_STORAGE_PATH}")
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
                    "Download Leads CSV",
                    data=_csv_str.encode("utf-8"),
                    file_name="leads_export.csv",
                    mime="text/csv",
                )
            # Clear leads with confirmation
            if "fr_confirm_clear" not in st.session_state:
                st.session_state["fr_confirm_clear"] = False
            if st.button("🗑️ Clear All Leads", key="fr_clear_btn"):
                st.session_state["fr_confirm_clear"] = True
            if st.session_state.get("fr_confirm_clear"):
                st.warning("Confirm clearing all leads data? This cannot be undone.")
                _cc1, _cc2 = st.columns(2)
                with _cc1:
                    if st.button("Confirm Clear", key="fr_confirm_yes"):
                        delete_all_leads(_lcfg.LEAD_STORAGE_PATH)
                        st.session_state["fr_confirm_clear"] = False
                        st.success("Leads cleared.")
                        st.rerun()
                with _cc2:
                    if st.button(_tr("common.cancel"), key="fr_confirm_no"):
                        st.session_state["fr_confirm_clear"] = False
                        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 輸入資料
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGE_INPUT:
    st.title(_tr("input.title"))

    # ── Reactive input container ──────────────────────────────────────────────
    # Do not use st.form here: birth_time_is_known must rerender immediately so
    # the time fields appear/disappear without an extra submit click.
    with st.container(border=True):
        st.subheader(_tr("input.basic_info"))
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(_tr("input.name"), placeholder=_tr("input.name_placeholder"), key="input_name")
        with col2:
            _gender_options = ["不填寫", "男", "女", "其他"]
            _gender_labels = [_tr("input.gender_unspecified"), _tr("input.gender_male"), _tr("input.gender_female"), _tr("input.gender_other")]
            _cur_gender = st.session_state.get("input_gender", "不填寫")
            _cur_gender_idx = _gender_options.index(_cur_gender) if _cur_gender in _gender_options else 0
            _sel_gender_label = st.selectbox(_tr("input.gender"), _gender_labels, index=_cur_gender_idx, key="_gender_display")
            st.session_state["input_gender"] = _gender_options[_gender_labels.index(_sel_gender_label)]

        st.subheader(_tr("input.birth_date"))
        _normalize_birth_year_state()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input(
                _tr("input.birth_year"),
                min_value=MIN_BIRTH_YEAR,
                max_value=MAX_BIRTH_YEAR,
                step=1,
                key="input_birth_year",
                on_change=_mark_birth_year_touched,
            )
        with col2:
            st.number_input(_tr("input.birth_month"), min_value=1, max_value=12, step=1,
                            key="input_birth_month")
        with col3:
            st.number_input(_tr("input.birth_day"), min_value=1, max_value=31, step=1,
                            key="input_birth_day")

        st.subheader(_tr("input.birth_time_section"))
        st.checkbox(
            _tr("input.birth_time_known"),
            key="birth_time_is_known",
        )
        if st.session_state["birth_time_is_known"]:
            col_h, col_m = st.columns(2)
            with col_h:
                st.number_input(_tr("input.birth_hour"), min_value=0, max_value=23, step=1,
                                key="input_birth_hour")
            with col_m:
                st.number_input(_tr("input.birth_minute"), min_value=0, max_value=59, step=1,
                                key="input_birth_minute")
            st.caption(_tr("input.birth_time_zi_note"))
        else:
            st.caption(_tr("input.birth_time_unknown_note"))

        st.subheader(_tr("input.birth_place"))
        # ── Smart location: Country selectbox ──────────────────────────────
        from location.countries import get_country_options
        _tr_lang = st.session_state.get("app_language", DEFAULT_LANGUAGE)

        _country_options = get_country_options(_tr_lang)
        _country_codes = [c for c, _ in _country_options]
        _country_labels = [lbl for _, lbl in _country_options]
        # Backward compat: if old session has input_birth_country (text), migrate
        _old_text_country = st.session_state.get("input_birth_country", "")
        if _old_text_country and not st.session_state.get("_country_migrated"):
            _cc_guess = "TW" if "台灣" in _old_text_country or "taiwan" in _old_text_country.lower() else "TW"
            st.session_state["input_country_code"] = _cc_guess
            st.session_state["_country_migrated"] = True
        _cur_cc = st.session_state.get("input_country_code", "TW")
        _cur_cc_idx = _country_codes.index(_cur_cc) if _cur_cc in _country_codes else 0
        _sel_country_label = st.selectbox(_tr("location.country_label"), _country_labels, index=_cur_cc_idx, key="_country_sel")
        _new_cc = _country_codes[_country_labels.index(_sel_country_label)]
        if _new_cc != st.session_state.get("input_country_code"):
            st.session_state["input_country_code"] = _new_cc
            st.session_state["input_city_candidates"] = []
            st.session_state["input_selected_candidate_idx"] = 0
            st.session_state["input_location_confirmed"] = False
        _selected_country_code = st.session_state["input_country_code"]

        # City search — align the input and action button on the same baseline.
        _city_q_col, _city_btn_col = st.columns([8, 1.25], vertical_alignment="bottom")
        with _city_q_col:
            st.text_input(
                _tr("location.city_search_label"),
                placeholder=_tr("location.city_search_placeholder"),
                key="input_city_query",
            )
        with _city_btn_col:
            if st.button(
                _tr("location.search_btn"),
                key="loc_search_btn",
                use_container_width=True,
            ):
                from location.resolver import search_cities
                from config import ENABLE_ONLINE_GEOCODING
                _cq = st.session_state.get("input_city_query", "")
                _cands = search_cities(_selected_country_code, _cq, _tr_lang, ENABLE_ONLINE_GEOCODING)
                st.session_state["input_city_candidates"] = [vars(c) for c in _cands]
                st.session_state["input_selected_candidate_idx"] = 0
                st.session_state["input_location_confirmed"] = False

        # Candidate selectbox
        _candidates_raw = st.session_state.get("input_city_candidates", [])
        if _candidates_raw:
            _cand_labels = [
                c.get("city_display_name", c.get("city", "?"))
                + f" ({c.get('latitude', 0):.2f}, {c.get('longitude', 0):.2f})"
                for c in _candidates_raw
            ]
            _sel_idx = st.session_state.get("input_selected_candidate_idx", 0)
            _sel_cand_label = st.selectbox(
                _tr("location.candidates_label"), _cand_labels,
                index=min(_sel_idx, len(_cand_labels) - 1), key="_cand_sel"
            )
            _sel_cand_idx = _cand_labels.index(_sel_cand_label)
            st.session_state["input_selected_candidate_idx"] = _sel_cand_idx
            _sel_cand = _candidates_raw[_sel_cand_idx]

            # Location summary card
            with st.container(border=True):
                st.markdown(f"**{_tr('location.summary_card')}**")
                _sc1, _sc2, _sc3 = st.columns(3)
                with _sc1:
                    st.metric(_tr("location.latitude"), f"{_sel_cand.get('latitude', 0):.4f}")
                with _sc2:
                    st.metric(_tr("location.longitude"), f"{_sel_cand.get('longitude', 0):.4f}")
                with _sc3:
                    st.metric(_tr("location.timezone"), _sel_cand.get("timezone", "─"))

                # UTC offset preview using current birth date/time
                from location.timezone import resolve_utc_offset
                from datetime import datetime as _dt
                _preview_dt = _dt(
                    int(st.session_state.get("input_birth_year", 1990)),
                    int(st.session_state.get("input_birth_month", 1)),
                    int(st.session_state.get("input_birth_day", 1)),
                    int(st.session_state.get("input_birth_hour", 12)) if st.session_state.get("birth_time_is_known") else 12,
                    int(st.session_state.get("input_birth_minute", 0)) if st.session_state.get("birth_time_is_known") else 0,
                )
                _tz_result = resolve_utc_offset(_preview_dt, _sel_cand.get("timezone", "UTC"))
                st.metric(_tr("location.utc_offset"), f"UTC{_tz_result['utc_offset']:+.1f}")
                if _tz_result["warnings"]:
                    st.warning(_tr("location.dst_warning"))

                # Accuracy level
                from location.display import get_accuracy_level, get_accuracy_label
                _acc_level = get_accuracy_level(
                    _sel_cand.get("confidence", 0.9),
                    bool(_sel_cand.get("city")),
                    bool(_sel_cand.get("latitude")),
                    st.session_state.get("input_location_confirmed", False),
                )
                _acc_label = get_accuracy_label(_acc_level, _tr_lang)
                if _acc_level == "high":
                    st.success(_acc_label)
                elif _acc_level == "medium":
                    st.info(_acc_label)
                else:
                    st.warning(_acc_label)

            # Confirm checkbox
            st.checkbox(_tr("location.confirm_label"), key="input_location_confirmed",
                        help=_tr("location.confirm_help"))

        elif st.session_state.get("input_city_query"):
            st.info(_tr("location.no_candidates"))

        # Keep legacy city for backward compat with submit handler
        _sel_cand_for_submit = None
        if _candidates_raw:
            _sidx = st.session_state.get("input_selected_candidate_idx", 0)
            if _sidx < len(_candidates_raw):
                _sel_cand_for_submit = _candidates_raw[_sidx]

        with st.expander(_tr("location.advanced_label")):
            adv1, adv2 = st.columns(2)
            with adv1:
                st.number_input(_tr("location.manual_lat"), min_value=-90.0, max_value=90.0,
                                step=0.0001, format="%.4f", key="input_manual_lat")
            with adv2:
                st.number_input(_tr("location.manual_lon"), min_value=-180.0, max_value=180.0,
                                step=0.0001, format="%.4f", key="input_manual_lon")
            st.number_input("UTC Offset (hours)", min_value=-12.0, max_value=14.0,
                            step=0.5, key="input_manual_tz")
            st.text_input(_tr("location.manual_tz"), placeholder=_tr("location.manual_tz_placeholder"),
                          key="input_manual_tz_name")
            st.checkbox(_tr("input.use_manual_latlon"),
                        key="input_use_manual_latlon")

        st.subheader(_tr("input.residence"))
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(_tr("input.res_city"), placeholder=_tr("input.res_city_placeholder"), key="input_res_city")
        with col2:
            st.text_input(_tr("input.res_country"), placeholder=_tr("input.res_country_placeholder"), key="input_res_country")

        st.subheader(_tr("input.blood_type"))
        st.selectbox(_tr("input.blood_type"), ["Unknown", "A", "B", "O", "AB"], key="input_blood_type")

        st.subheader(_tr("input.themes"))
        _theme_ids = [
            "overall_personality", "relationships", "career", "wealth",
            "social", "family", "current_year", "next_three_years",
        ]
        _legacy_themes = st.session_state.get("input_themes", [])
        _normalized_themes = [normalize_analysis_theme(v) for v in _legacy_themes]
        st.session_state["input_themes"] = [v for v in _normalized_themes if v in _theme_ids] or list(_theme_ids)
        st.multiselect(
            _tr("input.themes_select"),
            options=_theme_ids,
            format_func=lambda value: translate_analysis_theme(value, _tr_lang),
            key="input_themes",
        )

        st.subheader(_tr("input.report_settings"))
        col1, col2 = st.columns(2)
        _report_language_codes = ["auto", "zh-TW", "en", "th", "ja", "es", "ar"]
        _report_language_self_names = {
            "zh-TW": "繁體中文", "en": "English", "th": "ไทย",
            "ja": "日本語", "es": "Español", "ar": "العربية",
        }
        _legacy_report_lang = st.session_state.get("input_report_lang", "auto")
        _legacy_report_lang_map = {
            "繁體中文": "zh-TW", "簡體中文": "zh-TW", "English": "en",
            "ไทย": "th", "日本語": "ja", "Español": "es", "العربية": "ar",
            "Follow UI Language": "auto", "跟隨介面語言": "auto",
        }
        st.session_state["input_report_lang"] = _legacy_report_lang_map.get(_legacy_report_lang, _legacy_report_lang)
        if st.session_state["input_report_lang"] not in _report_language_codes:
            st.session_state["input_report_lang"] = "auto"

        _report_length_ids = ["short", "standard", "full", "complete_10k"]
        st.session_state["input_report_len"] = normalize_report_length(
            st.session_state.get("input_report_len", "standard")
        )
        if st.session_state["input_report_len"] not in _report_length_ids:
            st.session_state["input_report_len"] = "standard"

        with col1:
            st.selectbox(
                _tr("input.report_lang"),
                options=_report_language_codes,
                format_func=lambda code: (
                    _tr("report.language_auto") if code == "auto"
                    else _report_language_self_names[code]
                ),
                key="input_report_lang",
            )
        with col2:
            st.selectbox(
                _tr("input.report_len"),
                options=_report_length_ids,
                format_func=lambda value: translate_report_length(value, _tr_lang),
                key="input_report_len",
            )

        submitted = st.button(_tr("input.submit"), type="primary",
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
        # New location module: get from candidate or manual
        _submit_candidates = ss.get("input_city_candidates", [])
        _submit_cand_idx = ss.get("input_selected_candidate_idx", 0)
        _submit_cand = _submit_candidates[_submit_cand_idx] if _submit_candidates and _submit_cand_idx < len(_submit_candidates) else None
        birth_city   = (_submit_cand.get("city", "") if _submit_cand else str(ss.get("input_city_query", "")).strip())
        birth_country = (_submit_cand.get("country_display_name", "") if _submit_cand
                        else ss.get("input_country_code", "TW"))
        res_city     = str(ss.get("input_res_city", "")).strip()
        res_country  = str(ss.get("input_res_country", "")).strip()
        blood_type   = ss.get("input_blood_type", "Unknown")
        themes       = ss.get("input_themes", [])
        report_lang  = ss.get("input_report_lang", "auto")
        report_len   = ss.get("input_report_len", "standard")
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
            errors.append(_tr("input.error_country_required"))

        if errors:
            for e in errors:
                st.error(e)
        else:
            gender_map = {"男": Gender.MALE, "女": Gender.FEMALE,
                          "其他": Gender.OTHER, "不填寫": None}
            blood_map  = {bt.value: bt for bt in BloodType}
            theme_map = {
                "overall_personality": AnalysisTheme.PERSONALITY,
                "relationships": AnalysisTheme.LOVE,
                "career": AnalysisTheme.CAREER,
                "wealth": AnalysisTheme.WEALTH,
                "social": AnalysisTheme.SOCIAL,
                "family": AnalysisTheme.FAMILY,
                "current_year": AnalysisTheme.CURRENT_YEAR,
                "next_three_years": AnalysisTheme.THREE_YEARS,
            }
            _resolved_report_lang = _tr_lang if report_lang == "auto" else report_lang
            lang_map = {
                "zh-TW": ReportLanguage.TRADITIONAL_CHINESE,
                "en": ReportLanguage.ENGLISH,
                "th": ReportLanguage.ENGLISH,
                "ja": ReportLanguage.ENGLISH,
                "es": ReportLanguage.ENGLISH,
                "ar": ReportLanguage.ENGLISH,
            }
            len_map = {
                "short": ReportLength.SHORT,
                "standard": ReportLength.STANDARD,
                "full": ReportLength.FULL,
                "complete_10k": ReportLength.FULL,
            }

            # Resolve lat/lon: manual override > location candidate > legacy city lookup
            resolved_lat = resolved_lon = resolved_tz_offset = None
            resolved_tz = None
            _submit_candidates = ss.get("input_city_candidates", [])
            _submit_cand_idx = ss.get("input_selected_candidate_idx", 0)
            _submit_cand = _submit_candidates[_submit_cand_idx] if _submit_candidates and _submit_cand_idx < len(_submit_candidates) else None
            if use_manual and (manual_lat != 0.0 or manual_lon != 0.0):
                resolved_lat = manual_lat
                resolved_lon = manual_lon
                _manual_tz_name = ss.get("input_manual_tz_name", "")
                if _manual_tz_name:
                    from location.timezone import resolve_utc_offset as _ruo
                    from datetime import datetime as _dtz
                    _preview_dtz = _dtz(birth_year, birth_month, birth_day,
                                       birth_hour if time_known else 12,
                                       birth_minute if time_known else 0)
                    _tz_r = _ruo(_preview_dtz, _manual_tz_name)
                    resolved_tz = _manual_tz_name
                    resolved_tz_offset = _tz_r["utc_offset"]
                else:
                    resolved_tz_offset = manual_tz
            elif _submit_cand:
                resolved_lat = _submit_cand.get("latitude")
                resolved_lon = _submit_cand.get("longitude")
                resolved_tz = _submit_cand.get("timezone") or "UTC"
                from location.timezone import resolve_utc_offset as _ruo
                from datetime import datetime as _dtz
                _preview_dtz = _dtz(birth_year, birth_month, birth_day,
                                   birth_hour if time_known else 12,
                                   birth_minute if time_known else 0)
                _tz_r = _ruo(_preview_dtz, resolved_tz)
                resolved_tz_offset = _tz_r["utc_offset"]
            else:
                # Legacy fallback: lookup by city text
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
                report_language=lang_map.get(_resolved_report_lang, ReportLanguage.TRADITIONAL_CHINESE),
                report_length=len_map.get(report_len, ReportLength.STANDARD),
                birth_latitude=resolved_lat,
                birth_longitude=resolved_lon,
                birth_timezone=resolved_tz,
                birth_timezone_offset=resolved_tz_offset,
                birth_time_is_known=time_known,
            )
            st.session_state["profile"] = profile
            st.session_state["report"] = None   # invalidate old report
            # Preserve the exact form state for 「Return to Edit Data」.
            st.session_state["_last_input_snapshot"] = _capture_input_snapshot()

            # Feedback messages
            if resolved_lat is not None:
                st.info(_tr("input.coord_found", lat=resolved_lat, lon=resolved_lon))
            else:
                st.warning(_tr("input.coord_not_found"))
            if not time_known:
                st.warning(_tr("input.time_not_filled"))
            if time_known and resolved_lat is not None:
                st.success(_tr("input.time_and_coord_complete"))
            st.success(_tr("input.saved", name=name))

    # Preserve the current form continuously, not only after submission.
    # This lets users visit another page and return without losing partially
    # entered values, while keeping canonical widget values intact.
    st.session_state["_last_input_snapshot"] = _capture_input_snapshot()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 計算命盤
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGE_CALCULATE:
    st.title(_tr("calculate.title"))

    profile = st.session_state.get("profile")

    if profile is None:
        st.warning(_tr("calculate.no_profile"))
        if st.button(_tr("calculate.btn_go_input"), type="primary"):
            _go_to_page(PAGE_INPUT)
        st.stop()

    # Profile summary
    time_label = profile.birth_time.strftime("%H:%M") if profile.birth_time else _tr("calculate.time_unknown")
    loc_label  = profile.birth_city or _tr("calculate.place_unknown")
    st.info(_tr("calculate.current_data", name=profile.name, date=profile.birth_date, time=time_label, place=loc_label))

    # Navigation buttons (always visible when profile exists)
    col_edit, col_clear = st.columns(2)
    with col_edit:
        if st.button(_tr("calculate.btn_edit"), use_container_width=True):
            # Restore the saved profile on the next rerun, before the input
            # widgets are instantiated.  This preserves all previous values
            # instead of returning to a blank/default form.
            _edit_state = st.session_state.get("_last_input_snapshot") or _capture_input_snapshot()
            if _edit_state:
                st.session_state["_pending_input_snapshot"] = deepcopy(_edit_state)
            else:
                st.session_state.pop("_pending_input_snapshot", None)
            st.session_state["_pending_profile_edit"] = True
            # Preserve the explicit canonical destination for compatibility
            # with existing sessions and regression checks.
            st.session_state["_pending_nav_page"] = PAGE_INPUT
            _go_to_page(PAGE_INPUT)
    with col_clear:
        if st.button(_tr("calculate.btn_clear"), use_container_width=True, type="secondary"):
            _clear_input_state()
            _go_to_page(PAGE_INPUT)

    st.divider()

    report = st.session_state.get("report")
    if report is not None:
        st.success(_tr("calculate.done", report_id=report.report_id))
        col_recalc, col_preview = st.columns(2)
        with col_recalc:
            do_calculate = st.button(_tr("calculate.btn_recalc"), type="primary",
                                     use_container_width=True)
        with col_preview:
            if st.button(_tr("calculate.btn_preview"), use_container_width=True):
                _go_to_page(PAGE_REPORT_PREVIEW)
    else:
        do_calculate = st.button(_tr("calculate.btn_start"), type="primary",
                                 use_container_width=True)

    if do_calculate:
        with st.spinner(_tr("calculate.spinner")):
            try:
                gen = ReportGenerator()
                new_report = gen.generate(profile, persist=True)
                st.session_state["report"] = new_report
            except Exception as e:
                st.error(_tr("calculate.error", error=str(e)))
                st.exception(e)
        st.rerun()

    # Show tabs when report is available
    if st.session_state.get("report") is not None:
        report = st.session_state["report"]
        st.divider()
        st.subheader(_tr("calculate.overview"))

        tab_w, tab_b, tab_z, tab_n, tab_hd = st.tabs(
            [_tr("calculate.tab_western"), _tr("calculate.tab_bazi"), _tr("calculate.tab_ziwei"), _tr("calculate.tab_numerology"), _tr("calculate.tab_hd")]
        )

        with tab_w:
            wc = report.western_chart
            if wc:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    sun_pos = next(
                        (p for p in wc.planet_positions if p.planet.value == "太陽"), None)
                    st.metric(_tr("calculate.western_sun"), translate_zodiac(normalize_zodiac_value(sun_pos.sign.value), _tr_lang) if sun_pos else "─")
                with col2:
                    moon_pos = next(
                        (p for p in wc.planet_positions if p.planet.value == "月亮"), None)
                    st.metric(_tr("calculate.western_moon"), translate_zodiac(normalize_zodiac_value(moon_pos.sign.value), _tr_lang) if moon_pos else "─")
                with col3:
                    if wc.ascendant_accuracy == "precise":
                        st.metric(_tr("calculate.western_asc"), translate_zodiac(normalize_zodiac_value(wc.ascendant.value), _tr_lang))
                    else:
                        st.metric(_tr("calculate.western_asc"), _tr("calculate.western_need_data"))
                with col4:
                    if wc.mc_accuracy == "precise":
                        st.metric(_tr("calculate.western_mc"), translate_zodiac(normalize_zodiac_value(wc.mc.value), _tr_lang))
                    else:
                        st.metric(_tr("calculate.western_mc"), _tr("calculate.western_need_data"))

                mode = wc.calculation_mode
                if mode == "swiss_ephemeris":
                    st.success(_tr("calculate.western_mode_precise"))
                elif mode == "partial_real":
                    st.info(_tr("calculate.western_mode_partial"))
                else:
                    st.warning(_tr("calculate.western_mode_mock"))

                if wc.accuracy_note:
                    if _tr_lang == "zh-TW":
                        st.caption(wc.accuracy_note)
                    else:
                        st.caption(_tr("report.partial_translation_notice"))
                if wc.ascendant_accuracy != "precise":
                    st.caption(_tr("calculate.western_asc_hint"))

                with st.expander(_tr("calculate.western_planets_expander")):
                    render_planet_table(wc.planet_positions, language=_tr_lang)
                with st.expander(_tr("calculate.western_houses_expander")):
                    render_house_table(wc.houses, language=_tr_lang)
                with st.expander(_tr("calculate.western_aspects_expander")):
                    render_aspect_table(wc.aspects, language=_tr_lang)

        with tab_b:
            bc = report.bazi_chart
            if bc:
                if bc.accuracy_note:
                    st.caption(f"ℹ️ {bc.accuracy_note}" if _tr_lang == "zh-TW" else _tr("report.partial_translation_notice"))
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        _tr("calculate.bazi_day_master"),
                        f"{translate_bazi_stem(bc.day_master.value, _tr_lang)} ({translate_element(bc.day_master_element.value, _tr_lang)})"
                        if _tr_lang != "zh-TW" else f"{bc.day_master.value}（{bc.day_master_element.value}）",
                    )
                with col2:
                    _sep = "、" if _tr_lang == "zh-TW" else ", "
                    fav = _sep.join(translate_element(e.value, _tr_lang) for e in bc.favorable_elements)
                    st.metric(_tr("calculate.bazi_favorable"), fav)
                render_bazi_pillars(bc, language=_tr_lang)
                with st.expander(_tr("calculate.bazi_elements_expander")):
                    render_five_element_chart(bc, language=_tr_lang)
                with st.expander(_tr("calculate.bazi_daxian_expander")):
                    import pandas as pd
                    dy_rows = [
                        {_tr("calculate.bazi_start_age"): _localized_age(dy.start_age, _tr_lang), _tr("calculate.bazi_end_age"): _localized_age(dy.end_age, _tr_lang),
                         _tr("calculate.bazi_stem_branch"): f"{translate_bazi_stem(dy.stem.value, _tr_lang)} / {translate_branch(dy.branch.value, _tr_lang)}"}
                        for dy in bc.da_yun
                    ]
                    st.dataframe(pd.DataFrame(dy_rows), hide_index=True)

        with tab_z:
            zc = report.ziwei_chart
            if zc:
                if _tr_lang != "zh-TW":
                    _localized_ziwei_summary(zc, _tr_lang)
                else:
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
                    render_ziwei_formal_table(zc, language=_tr_lang)

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
                        render_ziwei_auxiliary_table(zc, language=_tr_lang)

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
                        render_daxian_table(zc, language=_tr_lang)

        with tab_n:
            nc = report.numerology_chart
            if nc:
                render_numerology_card(nc, language=_tr_lang)
                if _tr_lang == "zh-TW":
                    st.markdown(f"**{nc.life_path_description}**")
                else:
                    _num_copy = {
                        "en": f"Life Path {nc.life_path_number} highlights recurring motivations, learning patterns, and ways of contributing. Use it as a reflection prompt rather than a fixed prediction.",
                        "ja": f"ライフパス {nc.life_path_number} は、繰り返しやすい動機、学習パターン、社会への関わり方を考える手掛かりです。固定的な予言ではなく自己理解の参考として活用してください。",
                        "th": f"เลขเส้นทางชีวิต {nc.life_path_number} ช่วยสะท้อนแรงจูงใจ รูปแบบการเรียนรู้ และวิธีมีส่วนร่วมกับผู้อื่น ควรใช้เพื่อการสังเกตตนเอง ไม่ใช่คำทำนายตายตัว",
                        "es": f"El Camino de Vida {nc.life_path_number} ayuda a observar motivaciones, patrones de aprendizaje y formas de contribuir. Úsalo como reflexión, no como predicción fija.",
                        "ar": f"يساعد مسار الحياة {nc.life_path_number} على ملاحظة الدوافع وأنماط التعلم وطرق المساهمة. استخدمه للتأمل لا كتنبؤ ثابت.",
                    }
                    st.markdown(_num_copy.get(_tr_lang, _num_copy["en"]))

        with tab_hd:
            hd = getattr(report, "human_design_chart", None)
            if hd is None:
                st.warning(_tr("report.not_ready"))
            elif _tr_lang != "zh-TW":
                _localized_hd_summary(hd, _tr_lang)
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
elif page == PAGE_REPORT_PREVIEW:
    st.title(_tr("report_preview.title"))

    if st.session_state["report"] is None:
        st.info(_tr("report_preview.empty"))
        st.stop()

    # Report language selector stores canonical language codes, never display labels.
    _report_lang_codes = ["auto", "zh-TW", "en", "th", "ja", "es", "ar"]
    _report_lang_self_names = {
        "zh-TW": "繁體中文", "en": "English", "th": "ไทย",
        "ja": "日本語", "es": "Español", "ar": "العربية",
    }
    _cur_rl = st.session_state.get("report_language", "auto")
    if _cur_rl not in _report_lang_codes:
        _cur_rl = "auto"
        st.session_state["report_language"] = "auto"
    st.selectbox(
        _tr("report.language_selector"),
        options=_report_lang_codes,
        index=_report_lang_codes.index(_cur_rl),
        format_func=lambda code: (
            _tr("report.language_auto") if code == "auto"
            else _report_lang_self_names[code]
        ),
        key="report_language",
    )

    report = st.session_state["report"]

    # ── Demo label ────────────────────────────────────────────────────────────
    if report.profile.name.startswith("Demo"):
        st.info(_tr("report_preview.demo_notice"))

    # ── Report summary card ───────────────────────────────────────────────────
    with st.container(border=True):
        rc1, rc2, rc3, rc4 = st.columns(4)
        with rc1:
            st.metric(_tr("report_preview.col_name"), report.profile.name)
        with rc2:
            st.metric(_tr("report_preview.col_length"), _report_length_label(report.profile.report_length, _tr_lang))
        with rc3:
            st.metric(_tr("settings.version"), f"v{APP_VERSION}")
        with rc4:
            st.metric(_tr("report_preview.col_created"), report.created_at[:16] if report.created_at else "─")

    # ── Calculation mode expander ─────────────────────────────────────────────
    with st.expander(_tr("report_preview.calc_summary")):
        wc = report.western_chart
        bc = report.bazi_chart
        zc = report.ziwei_chart
        mode_data = [
            (_tr("calculate.tab_western"), getattr(wc, "calculation_mode", "─") if wc else "─",
             getattr(wc, "accuracy_note", "") if wc else ""),
            (_tr("calculate.tab_bazi"), getattr(bc, "calculation_mode", "─") if bc else "─",
             getattr(bc, "accuracy_note", "") if bc else ""),
            (_tr("calculate.tab_ziwei"), getattr(zc, "calculation_mode", "─") if zc else "─",
             getattr(zc, "accuracy_note", "") if zc else ""),
        ]
        import pandas as pd
        st.dataframe(
            pd.DataFrame(mode_data, columns=[_tr("report_preview.system"), _tr("report_preview.calc_mode"), _tr("report_preview.notes")]),
            hide_index=True, use_container_width=True,
        )
        aux_note = getattr(zc, "auxiliary_accuracy_note", "") if zc else ""
        if aux_note:
            auxiliary_label = _tr("report_preview.auxiliary")
            if _tr_lang == "zh-TW":
                st.caption(f"{auxiliary_label}: {aux_note}")
            else:
                st.caption(_tr("report.partial_translation_notice"))

    view_mode = st.radio(_tr("report_preview.view_mode"), [_tr("report_preview.view_interactive"), _tr("report_preview.view_markdown")], horizontal=True)

    _resolved_report_language = (
        _tr_lang if st.session_state.get("report_language", "auto") == "auto"
        else st.session_state.get("report_language", _tr_lang)
    )

    if view_mode == _tr("report_preview.view_interactive"):
        if report.synthesis:
            # Backward-compatible call shape: render_synthesis_section(report.synthesis, language=_resolved_report_language)
            render_synthesis_section(report.synthesis, language=_resolved_report_language, report=report)
        else:
            st.warning(_tr("report_preview.synthesis_not_ready"))
    else:
        from reports.markdown_exporter import MarkdownExporter
        md_text = MarkdownExporter().export(report, language=_resolved_report_language)
        st.markdown(md_text, unsafe_allow_html=False)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 歷史報告
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGE_HISTORY:
    st.title(_tr("history.title"))

    reports = list_reports(limit=50)
    if not reports:
        st.info(_tr("history.no_reports"))
        st.stop()

    import pandas as pd
    df = pd.DataFrame(reports)
    df_display = df[
        ["id", "name", "birth_date", "title", "language", "length", "created_at"]
    ].copy()
    df_display.columns = ["ID", _tr("report_preview.col_name"), _tr("history.col_birth_date"), _tr("history.col_title"), _tr("history.col_lang"), _tr("history.col_length"), _tr("report_preview.col_created")]
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        load_id = st.number_input(_tr("history.load_id"), min_value=1, step=1)
        if st.button(_tr("history.load")):
            row = get_report(int(load_id))
            if row:
                st.session_state["active_report_id"] = int(load_id)
                st.session_state["_loaded_report_markdown"] = row["markdown_body"]
                st.success(_tr("history.loaded", id=load_id))
            else:
                st.error(_tr("history.not_found"))
    with col2:
        del_id = st.number_input(_tr("history.delete_id"), min_value=1, step=1, key="del_id")
        if st.button(_tr("history.delete"), type="secondary"):
            delete_report(int(del_id))
            st.success(_tr("history.deleted"))
            st.rerun()

    if st.session_state.get("_loaded_report_markdown"):
        st.divider()
        st.markdown(f"### {_tr('history.loaded_content')}")
        st.markdown(st.session_state["_loaded_report_markdown"])


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 匯出
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGE_EXPORT:
    st.title(_tr("export.title"))

    if st.session_state["report"] is None:
        st.info(_tr("export.no_report"))
        st.stop()

    report = st.session_state["report"]

    _cur_export_lang = st.session_state.get("report_language", "auto")
    if _cur_export_lang not in _REPORT_LANGUAGE_CODES:
        _cur_export_lang = "auto"
        st.session_state["report_language"] = "auto"
    st.selectbox(
        _tr("report.language_selector"),
        options=_REPORT_LANGUAGE_CODES,
        index=_REPORT_LANGUAGE_CODES.index(_cur_export_lang),
        format_func=lambda code: (
            _tr("report.language_auto") if code == "auto"
            else _REPORT_LANGUAGE_SELF_NAMES[code]
        ),
        key="report_language",
    )
    _export_language = _resolve_report_language()

    # ── Report summary card ───────────────────────────────────────────────────
    with st.container(border=True):
        ec1, ec2, ec3, ec4 = st.columns(4)
        with ec1:
            st.metric(_tr("report_preview.col_name"), report.profile.name)
        with ec2:
            st.metric(_tr("report_preview.col_created"), report.created_at[:16] if report.created_at else "─")
        with ec3:
            st.metric(_tr("report_preview.col_length"), _report_length_label(report.profile.report_length, _tr_lang))
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
    with st.expander(f"📋 {_tr('export.format_section')}", expanded=True):
        st.markdown(f"""
| {_tr('export.format_col')} | {_tr('export.usage_col')} |
|------|----------|
| 🌐 HTML | {_tr('export.html_desc')} |
| 📘 Word | {_tr('export.word_desc')} |
| 📝 Markdown | {_tr('export.md_desc')} |
| 📕 PDF | {_tr('export.pdf_desc')} |
""")
    st.divider()

    from reports.markdown_exporter import MarkdownExporter
    from reports.html_exporter import HtmlExporter

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("**Markdown**")
        st.caption(_tr("export.md_desc"))
        md_content = MarkdownExporter().export(report, language=_export_language)
        st.download_button(
            label=_tr("report.download_md"),
            data=md_content.encode("utf-8"),
            file_name=make_export_filename(report.profile.name, "md"),
            mime="text/markdown",
            use_container_width=True,
        )

    with col2:
        st.markdown("**HTML**")
        st.caption(_tr("export.html_desc"))
        html_content = HtmlExporter().export(report, language=_export_language)
        st.download_button(
            label=_tr("report.download_html"),
            data=html_content.encode("utf-8"),
            file_name=make_export_filename(report.profile.name, "html"),
            mime="text/html",
            use_container_width=True,
        )

    with col3:
        st.markdown("**Word**")
        st.caption(_tr("export.word_desc"))
        docx_exp = DocxExporter()
        if docx_exp.is_available():
            try:
                docx_bytes = docx_exp.export(report, language=_export_language)
                st.download_button(
                    label=_tr("report.download_word"),
                    data=docx_bytes,
                    file_name=make_export_filename(report.profile.name, "docx"),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            except Exception as e:
                st.button(_tr("export.word_failed"), disabled=True,
                          use_container_width=True)
                st.caption(str(e))
        else:
            st.button(_tr("export.word_not_installed"), disabled=True,
                      use_container_width=True)
            st.warning(
                "需安裝 python-docx：請執行 `setup.bat` 或 "
                "`.venv\\Scripts\\python -m pip install -r requirements.txt`"
            )

    with col4:
        st.markdown("**PDF**")
        st.caption(_tr("export.pdf_desc"))
        pdf_exp = PdfExporter()
        if pdf_exp.is_available():
            try:
                pdf_bytes = pdf_exp.export(report, language=_export_language)
                st.download_button(
                    label=_tr("report.download_pdf"),
                    data=pdf_bytes,
                    file_name=make_export_filename(report.profile.name, "pdf"),
                    mime="application/pdf",
                    use_container_width=True,
                )
            except RuntimeError as e:
                st.button(_tr("export.pdf_env_error"), disabled=True,
                          use_container_width=True)
                st.warning(str(e))
        else:
            st.button(_tr("export.pdf_not_installed"), disabled=True,
                      use_container_width=True)
            st.info(
                "PDF export requires WeasyPrint or ReportLab. "
                "Run setup.bat to install the complete export environment."
            )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 合盤分析
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGE_COMPATIBILITY:
    st.title(_tr("compatibility.title"))
    st.caption(_tr("compatibility.caption"))
    st.info(_tr("compatibility.disclaimer"))

    from compatibility.engine import CompatibilityEngine
    from compatibility.models import CompatibilityInput, RelationshipType
    from compatibility.exporters import make_compat_filename, export_compat_to_markdown, export_compat_to_html, export_compat_to_docx, export_compat_to_pdf
    from reports.docx_exporter import DocxExporter as _DocxExporter

    # ── Intro ─────────────────────────────────────────────────────────────────
    with st.expander(_tr("compat.intro_expander"), expanded=False):
        st.markdown(_tr("compatibility.disclaimer"))

    # ── Relationship type ─────────────────────────────────────────────────────
    st.subheader(_tr("compat.relationship_type"))
    _RT_CANONICAL = ["romantic", "marriage", "business", "parent_child", "friendship", "colleague", "general"]
    _RT_TR_KEYS = {
        "romantic": "compat.type_romantic",
        "marriage": "compat.type_spouse",
        "business": "compat.type_business",
        "parent_child": "compat.type_parent_child",
        "friendship": "compat.type_friendship",
        "colleague": "compat.type_colleague",
        "general": "compat.type_general",
    }
    _rt_display_labels = [_tr(_RT_TR_KEYS[c]) for c in _RT_CANONICAL]
    rt_label_sel = st.selectbox(
        _tr("compat.select_rel_type"),
        _rt_display_labels,
        key="compat_rel_type_display",
    )
    _rt_canonical_val = _RT_CANONICAL[_rt_display_labels.index(rt_label_sel)]
    # Map canonical to RelationshipType enum values
    _RT_ENUM_MAP = {
        "romantic": "romantic", "marriage": "marriage", "business": "business",
        "parent_child": "parent_child", "friendship": "friendship",
        "colleague": "colleague", "general": "general",
    }
    try:
        selected_rt = RelationshipType(_RT_ENUM_MAP.get(_rt_canonical_val, "general"))
    except Exception:
        selected_rt = RelationshipType("general")

    # ── Person A ──────────────────────────────────────────────────────────────
    st.subheader(_tr("compat.person_a_section"))
    _compat_tr_lang = st.session_state.get("app_language", DEFAULT_LANGUAGE)

    _compat_gender_canonical = ["不填寫", "男", "女", "其他"]
    _compat_gender_labels_a = [_tr("input.gender_unspecified"), _tr("input.gender_male"), _tr("input.gender_female"), _tr("input.gender_other")]
    use_current = st.session_state.get("profile") is not None
    if use_current:
        if st.button(_tr("compat.use_current_as_a"), key="compat_use_current_as_a"):
            st.session_state["compat_a_profile"] = st.session_state["profile"]
            st.success(f"Loaded: {st.session_state['profile'].name}")

    with st.expander(_tr("compat.manual_input_a"), expanded=(not use_current)):
        ca1, ca2 = st.columns(2)
        with ca1:
            st.text_input(_tr("compat.name_a"), key="compat_a_name", placeholder="e.g. Alice")
        with ca2:
            _cur_ag = st.session_state.get("compat_a_gender", "不填寫")
            _cur_ag_idx = _compat_gender_canonical.index(_cur_ag) if _cur_ag in _compat_gender_canonical else 0
            _sel_ag = st.selectbox(_tr("compat.gender_a"), _compat_gender_labels_a, index=_cur_ag_idx, key="_compat_a_gender_display")
            st.session_state["compat_a_gender"] = _compat_gender_canonical[_compat_gender_labels_a.index(_sel_ag)]
        ca3, ca4, ca5 = st.columns(3)
        with ca3:
            st.number_input(_tr("compat.birth_year_a"), min_value=1900, max_value=date.today().year,
                            step=1, key="compat_a_year", value=1989)
        with ca4:
            st.number_input(_tr("compat.birth_month_a"), min_value=1, max_value=12, step=1,
                            key="compat_a_month", value=9)
        with ca5:
            st.number_input(_tr("compat.birth_day_a"), min_value=1, max_value=31, step=1,
                            key="compat_a_day", value=21)
        st.checkbox(_tr("compat.time_known_a"), key="compat_a_time_known")
        if st.session_state.get("compat_a_time_known"):
            cah, cam = st.columns(2)
            with cah:
                st.number_input(_tr("compat.birth_hour_a"), min_value=0, max_value=23,
                                step=1, key="compat_a_hour", value=11)
            with cam:
                st.number_input(_tr("compat.birth_minute_a"), min_value=0, max_value=59,
                                step=1, key="compat_a_minute", value=5)
        ca6, ca7 = st.columns(2)
        with ca6:
            st.text_input(_tr("compat.birth_city_a"), key="compat_a_city", placeholder="e.g. Taipei")
        with ca7:
            st.text_input(_tr("compat.birth_country_a"), key="compat_a_country", value=DEFAULT_COUNTRY)
        st.selectbox(_tr("compat.blood_type_a"), ["Unknown", "A", "B", "O", "AB"],
                     key="compat_a_blood")

        if st.button(_tr("compat.confirm_a"), key="compat_a_confirm"):
            try:
                _a_name = st.session_state.get("compat_a_name", "").strip()
                if not _a_name:
                    st.error(_tr("compat.name_required_a"))
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
                    _a_city = st.session_state.get("compat_a_city", "Taipei").strip() or "Taipei"
                    _a_country = st.session_state.get("compat_a_country", DEFAULT_COUNTRY).strip() or DEFAULT_COUNTRY
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
                    st.success(_tr("compat.confirmed_a", name=_a_name))
            except Exception as _e:
                st.error(_tr("compat.error_a", error=str(_e)))

    if st.session_state.get("compat_a_profile"):
        _pa = st.session_state["compat_a_profile"]
        st.info(_tr("compat.loaded_a", name=_pa.name, date=str(_pa.birth_date), city=getattr(_pa, "birth_city", "")))

    # ── Person B ──────────────────────────────────────────────────────────────
    st.subheader(_tr("compat.person_b_section"))
    _compat_gender_labels_b = [_tr("input.gender_unspecified"), _tr("input.gender_male"), _tr("input.gender_female"), _tr("input.gender_other")]
    with st.expander(_tr("compat.manual_input_b"), expanded=True):
        cb1, cb2 = st.columns(2)
        with cb1:
            st.text_input(_tr("compat.name_b"), key="compat_b_name", placeholder="e.g. Bob")
        with cb2:
            _cur_bg = st.session_state.get("compat_b_gender", "不填寫")
            _cur_bg_idx = _compat_gender_canonical.index(_cur_bg) if _cur_bg in _compat_gender_canonical else 0
            _sel_bg = st.selectbox(_tr("compat.gender_b"), _compat_gender_labels_b, index=_cur_bg_idx, key="_compat_b_gender_display")
            st.session_state["compat_b_gender"] = _compat_gender_canonical[_compat_gender_labels_b.index(_sel_bg)]
        cb3, cb4, cb5 = st.columns(3)
        with cb3:
            st.number_input(_tr("compat.birth_year_b"), min_value=1900, max_value=date.today().year,
                            step=1, key="compat_b_year", value=1991)
        with cb4:
            st.number_input(_tr("compat.birth_month_b"), min_value=1, max_value=12, step=1,
                            key="compat_b_month", value=3)
        with cb5:
            st.number_input(_tr("compat.birth_day_b"), min_value=1, max_value=31, step=1,
                            key="compat_b_day", value=8)
        st.checkbox(_tr("compat.time_known_b"), key="compat_b_time_known")
        if st.session_state.get("compat_b_time_known"):
            cbh, cbm = st.columns(2)
            with cbh:
                st.number_input(_tr("compat.birth_hour_b"), min_value=0, max_value=23,
                                step=1, key="compat_b_hour", value=9)
            with cbm:
                st.number_input(_tr("compat.birth_minute_b"), min_value=0, max_value=59,
                                step=1, key="compat_b_minute", value=45)
        cb6, cb7 = st.columns(2)
        with cb6:
            st.text_input(_tr("compat.birth_city_b"), key="compat_b_city", placeholder="e.g. Kaohsiung")
        with cb7:
            st.text_input(_tr("compat.birth_country_b"), key="compat_b_country", value=DEFAULT_COUNTRY)
        st.selectbox(_tr("compat.blood_type_b"), ["Unknown", "A", "B", "O", "AB"],
                     key="compat_b_blood")

        if st.button(_tr("compat.confirm_b"), key="compat_b_confirm"):
            try:
                _b_name = st.session_state.get("compat_b_name", "").strip()
                if not _b_name:
                    st.error(_tr("compat.name_required_b"))
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
                    _b_city = st.session_state.get("compat_b_city", "Taipei").strip() or "Taipei"
                    _b_country = st.session_state.get("compat_b_country", DEFAULT_COUNTRY).strip() or DEFAULT_COUNTRY
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
                    st.success(_tr("compat.confirmed_b", name=_b_name))
            except Exception as _e:
                st.error(_tr("compat.error_b", error=str(_e)))

    if st.session_state.get("compat_b_profile"):
        _pb = st.session_state["compat_b_profile"]
        st.info(_tr("compat.loaded_b", name=_pb.name, date=str(_pb.birth_date), city=getattr(_pb, "birth_city", "")))

    # ── Demo couple buttons (developer/demo mode only) ────────────────────────
    if SHOW_DEMO_DATA and not SAMPLE_COUPLES and DEVELOPER_MODE:
        st.info("Demo profiles are not included in this release package.")
    if SHOW_DEMO_DATA and SAMPLE_COUPLES:
        st.divider()
        st.subheader(_tr("compat.demo_section"))
        st.caption(_tr("compat.demo_caption"))
        _DEMO_RT_MAP = {"romantic": _tr("compat.type_romantic"), "business": _tr("compat.type_business"), "parent_child": _tr("compat.type_parent_child")}
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
        st.info(_tr("compatibility.not_ready"))

    if st.button(_tr("compatibility.generate"), type="primary", use_container_width=True,
                 disabled=not _can_generate, key="compat_generate"):
        with st.spinner(_tr("compatibility.spinner")):
            try:
                _ci = CompatibilityInput(
                    person_a=st.session_state["compat_a_profile"],
                    person_b=st.session_state["compat_b_profile"],
                    relationship_type=selected_rt,
                )
                _engine = CompatibilityEngine()
                _cr = _engine.generate(_ci)
                st.session_state["compatibility_report"] = _cr
                st.success(_tr("compatibility.done"))
            except Exception as _err:
                st.error(f"Compatibility error: {_err}")

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

            _syn_precise = _cr.synthesis
            if getattr(_syn_precise, "precision_summary", ""):
                st.divider()
                st.subheader("🔎 精準分析摘要")
                st.markdown(_syn_precise.precision_summary)
            if getattr(_syn_precise, "score_drivers", None):
                with st.expander("分數形成依據", expanded=True):
                    for _driver in _syn_precise.score_drivers:
                        st.markdown(f"- {_driver}")
            if getattr(_syn_precise, "dimension_evidence", None):
                _dim_titles = {
                    "emotional": "情緒與安全感",
                    "communication": "溝通與理解",
                    "attraction": "吸引力與親密節奏",
                    "stability": "穩定性與承諾",
                    "conflict": "衝突與修復",
                    "growth": "成長與合作",
                }
                with st.expander("各維度具體證據", expanded=False):
                    for _dim, _items in _syn_precise.dimension_evidence.items():
                        st.markdown(f"**{_dim_titles.get(_dim, _dim)}**")
                        for _item in _items:
                            st.markdown(f"- {_item}")
            if getattr(_syn_precise, "priority_actions", None):
                st.subheader("🎯 優先改善順序")
                for _idx, _action in enumerate(_syn_precise.priority_actions, 1):
                    st.markdown(f"{_idx}. {_action}")
            if getattr(_syn_precise, "uncertainty_notes", None):
                with st.expander("資料限制與可信度", expanded=False):
                    for _note in _syn_precise.uncertainty_notes:
                        st.markdown(f"- {_note}")

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
            _compat_export_labels = {
                "zh-TW": ("📤 匯出合盤報告", "選擇適合用途的匯出格式：", "下載"),
                "en": ("📤 Export Compatibility Report", "Choose an export format:", "Download"),
                "ja": ("📤 相性レポートを出力", "用途に合う形式を選択してください：", "ダウンロード"),
                "th": ("📤 ส่งออกรายงานความเข้ากันได้", "เลือกรูปแบบการส่งออก:", "ดาวน์โหลด"),
                "es": ("📤 Exportar informe de compatibilidad", "Elige un formato:", "Descargar"),
                "ar": ("📤 تصدير تقرير التوافق", "اختر صيغة التصدير:", "تنزيل"),
            }
            _compat_export_title, _compat_export_caption, _compat_download = _compat_export_labels.get(
                _compat_tr_lang, _compat_export_labels["en"]
            )
            st.subheader(_compat_export_title)
            st.caption(_compat_export_caption)
            _compat_report_lang = st.selectbox(
                _tr("report.language_selector"),
                options=_REPORT_LANGUAGE_CODES,
                format_func=lambda code: (
                    _tr("report.language_auto") if code == "auto"
                    else _REPORT_LANGUAGE_SELF_NAMES[code]
                ),
                key="compat_report_language",
            )
            _compat_export_language = (
                _compat_tr_lang if _compat_report_lang == "auto"
                else _compat_report_lang
            )
            ex1, ex2, ex3, ex4 = st.columns(4)
            # Compatibility export labels include: 下載 PDF / Download PDF / ダウンロード PDF
            _rt_str = _cr.relationship_type.value
            with ex1:
                _md_text = export_compat_to_markdown(_cr, language=_compat_export_language)
                st.download_button(
                    label=f"📝 {_compat_download} Markdown",
                    data=_md_text.encode("utf-8"),
                    file_name=make_compat_filename(
                        _cr.person_a_profile.name, _cr.person_b_profile.name, "md", _rt_str
                    ),
                    mime="text/markdown",
                    use_container_width=True,
                )
            with ex2:
                try:
                    _html_str = export_compat_to_html(_cr, language=_compat_export_language)
                    st.download_button(
                        label=f"🌐 {_compat_download} HTML",
                        data=_html_str.encode("utf-8"),
                        file_name=make_compat_filename(
                            _cr.person_a_profile.name, _cr.person_b_profile.name, "html", _rt_str
                        ),
                        mime="text/html",
                        use_container_width=True,
                    )
                except Exception as _he:
                    st.button("🌐 HTML", disabled=True, use_container_width=True)
                    st.warning(str(_he))
            with ex3:
                try:
                    _docx_bytes = export_compat_to_docx(_cr, language=_compat_export_language)
                    st.download_button(
                        label=f"📘 {_compat_download} Word",
                        data=_docx_bytes,
                        file_name=make_compat_filename(
                            _cr.person_a_profile.name, _cr.person_b_profile.name, "docx", _rt_str
                        ),
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
                except Exception as _de:
                    st.button("📘 Word", disabled=True, use_container_width=True)
                    st.warning(str(_de))
            with ex4:
                try:
                    _pdf_bytes = export_compat_to_pdf(_cr, language=_compat_export_language)
                    st.download_button(
                        label=f"📕 {_compat_download} PDF",
                        data=_pdf_bytes,
                        file_name=make_compat_filename(
                            _cr.person_a_profile.name, _cr.person_b_profile.name, "pdf", _rt_str
                        ),
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as _pe:
                    st.button("📕 PDF", disabled=True, use_container_width=True)
                    st.warning(str(_pe))


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 紫微校準
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGE_ZIWEI_RECONCILIATION:
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
            _go_to_page(PAGE_INPUT)
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
elif page == PAGE_HD_RECONCILIATION:
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
            _go_to_page(PAGE_INPUT)
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
elif page == PAGE_SETTINGS:
    st.title(_tr("settings.title"))

    # ── Delivery mode status ──────────────────────────────────────────────────
    st.subheader(_tr("settings.mode_status"))
    if DEVELOPER_MODE:
        st.info(f"🛠️ **{_tr('settings.mode_developer')}** — {_tr('settings.dev_mode_info')}")
        dm1, dm2, dm3, dm4 = st.columns(4)
        with dm1:
            st.metric("DEV MODE", f"{_tr('settings.enabled')} ✅")
        with dm2:
            st.metric(_tr("settings.ziwei_cal"), f"{_tr('settings.enabled')} ✅")
        with dm3:
            st.metric(_tr("settings.demo_data"), f"{_tr('settings.enabled')} ✅")
        with dm4:
            st.metric(_tr("settings.mode_customer"), _tr("settings.off"))
    else:
        st.success(f"📦 **{_tr('settings.mode_customer')}** — {_tr('settings.customer_mode_info')}")
        dm1, dm2, dm3, dm4 = st.columns(4)
        with dm1:
            st.metric(_tr("settings.mode_customer"), f"{_tr('settings.enabled')} ✅")
        with dm2:
            st.metric(_tr("settings.dev_tools"), _tr("settings.hidden"))
        with dm3:
            st.metric(_tr("settings.demo_data"), _tr("settings.hidden"))
        with dm4:
            st.metric(_tr("settings.ziwei_cal"), _tr("settings.hidden"))

    # ── System info ───────────────────────────────────────────────────────────
    st.divider()
    st.subheader(_tr("settings.system_info"))
    from config import DB_PATH, SWISSEPH_DATA_PATH
    si1, si2 = st.columns(2)
    with si1:
        st.metric(_tr("settings.version"), f"v{APP_VERSION}")
        st.write(f"**{_tr('settings.db_path')}**：`{DB_PATH}`")
    with si2:
        sweph_status = "Set ✅" if SWISSEPH_DATA_PATH else "Not set (Moshier built-in) ⚠️"
        st.write(f"**Swiss Ephemeris**：{sweph_status}")

    # ── Supported features ────────────────────────────────────────────────────
    st.divider()
    st.subheader(_tr("settings.features"))
    st.markdown(f"""
| {_tr('settings.feature')} | {_tr('settings.status')} |
|------|------|
| Western Astrology (Swiss Ephemeris) | ✅ {_tr('settings.supported')} |
| BaZi | ✅ {_tr('settings.supported')} |
| Zi Wei Dou Shu Phase 1 | ✅ {_tr('settings.supported')} |
| Zi Wei auxiliary stars (V1.5.5) | ✅ {_tr('settings.supported')} |
| Zi Wei Da Xian Phase 1 (V1.5.5) | ✅ {_tr('settings.supported')} |
| Blood Type Analysis | ✅ {_tr('settings.supported')} |
| Numerology | ✅ {_tr('settings.supported')} |
""")

    # ── Export format availability ────────────────────────────────────────────
    st.divider()
    st.subheader(_tr("settings.export_formats"))
    _docx_ok = DocxExporter().is_available()
    _pdf_ok  = PdfExporter().is_available()
    ef1, ef2, ef3, ef4 = st.columns(4)
    with ef1:
        st.success("📝 Markdown ✅")
        st.caption(_tr("export.md_desc"))
    with ef2:
        st.success("🌐 HTML ✅")
        st.caption(_tr("export.html_desc"))
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
    st.subheader(_tr("settings.ephemeris"))
    st.caption(_tr("settings.ephemeris_desc"))
    sweph_path = st.text_input(
        _tr("settings.ephemeris_path"),
        value=get_setting("swisseph_path", ""),
        placeholder="例：/usr/share/swisseph",
    )
    if st.button(_tr("common.save")):
        set_setting("swisseph_path", sweph_path)
        st.success(_tr("settings.saved"))

    # ── Data management ───────────────────────────────────────────────────────
    st.divider()
    st.subheader(_tr("settings.data_management"))
    dm1, dm2 = st.columns(2)
    with dm1:
        full_reports = list_reports(limit=9999)
        st.metric(_tr("settings.saved_reports"), len(full_reports))
    with dm2:
        full_profiles = list_birth_profiles(limit=9999)
        st.metric(_tr("settings.saved_profiles"), len(full_profiles))


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Lead Funnel (Consultant / Developer mode only)
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGE_LEAD_FUNNEL:
    if not CONSULTANT_MODE:
        st.error("🔒 此頁面僅供顧問 / 開發者模式使用。")
        st.stop()

    from lead_magnet.storage import load_leads

    st.title("📊 Lead Funnel 分析")
    st.caption("Lead 來源與轉換漏斗概覽 — V2.0.0")

    _lf_snapshot = load_leads()
    _lf_leads = _lf_snapshot.leads if _lf_snapshot else []

    # ── Summary metrics ───────────────────────────────────────────────────────
    _total = len(_lf_leads)
    _consented = sum(1 for l in _lf_leads if getattr(l, "consent", False))
    _marketing = sum(1 for l in _lf_leads if getattr(l, "marketing_consent", False))
    _by_type: dict = {}
    for _l in _lf_leads:
        _rt = getattr(_l, "report_type", "unknown")
        _by_type[_rt] = _by_type.get(_rt, 0) + 1

    _c1, _c2, _c3 = st.columns(3)
    _c1.metric("總 Lead 數", _total)
    _c2.metric("同意條款", _consented)
    _c3.metric("行銷同意", _marketing)

    st.divider()
    st.subheader("依報告類型分佈")
    if _by_type:
        for _rtype, _cnt in sorted(_by_type.items(), key=lambda x: -x[1]):
            st.write(f"- **{_rtype}**: {_cnt} 筆")
    else:
        st.info("尚無 Lead 資料。請先透過「免費報告」頁面取得 Lead。")

    st.divider()
    st.subheader("轉換漏斗")
    if _total > 0:
        _conv_pct = round(_consented / _total * 100, 1) if _total else 0
        _mkt_pct = round(_marketing / _total * 100, 1) if _total else 0
        st.write(f"- 訪客 → 提交表單（Lead 取得率）：{_total} 筆")
        st.write(f"- 同意條款率：{_conv_pct}%")
        st.write(f"- 行銷同意率：{_mkt_pct}%")
    else:
        st.info("尚無資料可計算漏斗。")

    if DEVELOPER_MODE:
        st.divider()
        st.subheader("開發者：原始 Lead 列表")
        if _lf_leads:
            import pandas as pd
            _rows = [
                {
                    "email": getattr(l, "email", ""),
                    "name": getattr(l, "name", ""),
                    "report_type": getattr(l, "report_type", ""),
                    "consent": getattr(l, "consent", False),
                    "marketing_consent": getattr(l, "marketing_consent", False),
                    "created_at": getattr(l, "created_at", ""),
                }
                for l in _lf_leads
            ]
            st.dataframe(pd.DataFrame(_rows), use_container_width=True)
        else:
            st.info("無 Lead 資料。")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: 客戶個案 (Developer / Consultant mode only)
# ══════════════════════════════════════════════════════════════════════════════
elif page == PAGE_CLIENT_CASES:
    if not CONSULTANT_MODE:
        st.error("🔒 此頁面僅供顧問 / 開發者模式使用。")
        st.stop()

    from consultant_workflow.models import (
        ClientCase, ClientProfile, CaseNote, CaseTask, ReportDelivery,
        CASE_STATUS_VALUES, REPORT_STATUS_VALUES,
    )
    from consultant_workflow.storage import (
        load_cases, append_case, update_case, get_case,
        add_note, add_task, update_task_status, add_delivery,
        export_cases_csv as _export_csv, delete_all_cases,
    )
    from consultant_workflow.engine import (
        create_case_from_lead, suggest_next_action,
        summarize_case, compute_case_metrics, filter_cases,
    )
    from consultant_workflow.exporters import (
        export_case_markdown, export_case_html,
        export_cases_csv as _exp_cases_csv,
        export_case_metrics_markdown, safe_case_filename,
    )

    st.title("🗂️ 客戶個案管理")
    st.caption("顧問工作流 / 客戶個案追蹤 — V1.9.8")

    _cw_tabs = st.tabs(["個案總覽", "從 Lead 建立個案", "個案詳情", "待辦與交付", "匯出"])

    # ── Tab 0: 個案總覽 ────────────────────────────────────────────────────────
    with _cw_tabs[0]:
        st.subheader("個案總覽")
        try:
            _snap = load_cases(CLIENT_CASE_STORAGE_PATH)
        except ValueError as _e:
            st.error(f"載入個案資料失敗：{_e}")
            st.stop()

        _metrics = compute_case_metrics(_snap)
        _m1, _m2, _m3, _m4, _m5, _m6 = st.columns(6)
        _m1.metric("總個案", _metrics["total"])
        _m2.metric("已交付", _metrics["delivered_count"])
        _m3.metric("Follow-up", _metrics["follow_up_count"])
        open_c = sum(1 for c in _snap.cases if c.case_status not in ("closed", "delivered"))
        _m4.metric("進行中", open_c)
        _m5.metric("待辦任務", _metrics["open_tasks"])
        _m6.metric("逾期任務", _metrics["overdue_tasks"])

        st.divider()
        if _snap.cases:
            import pandas as pd
            _df_status = pd.DataFrame(
                [{"狀態": k, "數量": v} for k, v in _metrics["by_case_status"].items()]
            )
            _df_rep = pd.DataFrame(
                [{"報告狀態": k, "數量": v} for k, v in _metrics["by_report_status"].items()]
            )
            _col_a, _col_b = st.columns(2)
            with _col_a:
                st.caption("個案狀態分布")
                st.dataframe(_df_status, use_container_width=True)
            with _col_b:
                st.caption("報告狀態分布")
                st.dataframe(_df_rep, use_container_width=True)

            st.divider()
            _filter_status = st.selectbox(
                "篩選狀態", ["（全部）"] + list(CASE_STATUS_VALUES),
                key="cw_filter_status",
            )
            _filter_kw = st.text_input("關鍵字搜尋（姓名 / Email）", key="cw_filter_kw")
            _filtered = filter_cases(
                _snap,
                status=None if _filter_status == "（全部）" else _filter_status,
                keyword=_filter_kw.strip() or None,
            )
            _df_cases = pd.DataFrame([
                {
                    "case_id": c.case_id,
                    "客戶姓名": c.client.name,
                    "Email": c.client.email,
                    "個案狀態": c.case_status,
                    "報告狀態": c.report_status,
                    "下一步": c.next_action[:40] if c.next_action else "",
                    "建立時間": c.created_at[:10] if c.created_at else "",
                }
                for c in _filtered
            ])
            st.dataframe(_df_cases, use_container_width=True)
        else:
            st.info("尚無個案資料。請先從 Lead 建立個案，或手動新增。")

    # ── Tab 1: 從 Lead 建立個案 ───────────────────────────────────────────────
    with _cw_tabs[1]:
        st.subheader("從 Lead 建立個案")
        try:
            from lead_magnet.storage import load_leads
            import config as _lcfg2
            _leads_snap = load_leads(_lcfg2.LEAD_STORAGE_PATH)
        except Exception as _e:
            st.warning(f"無法載入 Leads：{_e}")
            _leads_snap = None

        if _leads_snap and _leads_snap.leads:
            import pandas as pd
            _leads_df = pd.DataFrame([
                {
                    "lead_id": l.lead_id,
                    "姓名": l.profile.name,
                    "Email": l.profile.email,
                    "報告類型": l.report_type,
                    "建立時間": l.created_at[:10] if l.created_at else "",
                }
                for l in _leads_snap.leads
            ])
            st.dataframe(_leads_df, use_container_width=True)

            _lead_options = {f"{l.profile.name} ({l.lead_id[:12]}…)": l for l in _leads_snap.leads}
            _sel_lead_label = st.selectbox("選擇 Lead", list(_lead_options.keys()), key="cw_sel_lead")
            _sel_lead = _lead_options.get(_sel_lead_label)

            if st.button("建立個案", key="cw_create_case_btn"):
                if _sel_lead:
                    _cw_snap2 = load_cases(CLIENT_CASE_STORAGE_PATH)
                    _existing_ids = {c.source_lead_id for c in _cw_snap2.cases}
                    if _sel_lead.lead_id and _sel_lead.lead_id in _existing_ids:
                        st.warning(f"此 Lead（{_sel_lead.lead_id[:16]}…）已建立個案，請勿重複建立。")
                    else:
                        _new_case = create_case_from_lead(_sel_lead)
                        _new_case = append_case(_new_case, CLIENT_CASE_STORAGE_PATH)
                        st.success(f"✅ 個案已建立！case_id: `{_new_case.case_id}`")
        else:
            st.info("尚無 Lead 資料，或 leads_mock.json 不存在。請先透過免費報告頁取得 Lead。")

        st.divider()
        st.subheader("手動建立個案")
        with st.form("cw_manual_case_form"):
            _mc_name = st.text_input("客戶姓名 *", key="cw_mc_name")
            _mc_email = st.text_input("Email", key="cw_mc_email")
            _mc_phone = st.text_input("電話", key="cw_mc_phone")
            _mc_birth_date = st.text_input("出生日期（YYYY-MM-DD）", key="cw_mc_birth_date")
            _mc_birth_country = st.text_input("出生國家", value="台灣", key="cw_mc_birth_country")
            _mc_birth_city = st.text_input("出生城市", key="cw_mc_birth_city")
            _mc_source = st.text_input("來源備註", key="cw_mc_source")
            _mc_submit = st.form_submit_button("建立個案")
        if _mc_submit:
            if not _mc_name.strip():
                st.error("請填寫客戶姓名。")
            else:
                _mc_profile = ClientProfile(
                    name=_mc_name.strip(),
                    email=_mc_email.strip(),
                    phone=_mc_phone.strip(),
                    birth_date=_mc_birth_date.strip(),
                    birth_country=_mc_birth_country.strip() or "台灣",
                    birth_city=_mc_birth_city.strip(),
                    source=_mc_source.strip(),
                )
                _mc_case = ClientCase(client=_mc_profile)
                _mc_case = append_case(_mc_case, CLIENT_CASE_STORAGE_PATH)
                st.success(f"✅ 手動個案已建立！case_id: `{_mc_case.case_id}`")

    # ── Tab 2: 個案詳情 ────────────────────────────────────────────────────────
    with _cw_tabs[2]:
        st.subheader("個案詳情")
        _cw_snap3 = load_cases(CLIENT_CASE_STORAGE_PATH)
        if not _cw_snap3.cases:
            st.info("尚無個案資料。")
        else:
            _case_options3 = {
                f"{c.client.name} ({c.case_id[:14]}…)": c.case_id
                for c in _cw_snap3.cases
            }
            _sel_case_label3 = st.selectbox("選擇個案", list(_case_options3.keys()), key="cw_sel_case3")
            _sel_case_id3 = _case_options3.get(_sel_case_label3)
            _sel_case3 = get_case(_sel_case_id3, CLIENT_CASE_STORAGE_PATH) if _sel_case_id3 else None

            if _sel_case3:
                st.markdown(f"**case_id**: `{_sel_case3.case_id}`")
                st.markdown(f"**客戶**: {_sel_case3.client.name} / {_sel_case3.client.email}")

                with st.form("cw_update_case_form"):
                    _upd_case_status = st.selectbox(
                        "個案狀態", list(CASE_STATUS_VALUES),
                        index=list(CASE_STATUS_VALUES).index(_sel_case3.case_status)
                        if _sel_case3.case_status in CASE_STATUS_VALUES else 0,
                        key="cw_upd_case_status",
                    )
                    _upd_report_status = st.selectbox(
                        "報告狀態", list(REPORT_STATUS_VALUES),
                        index=list(REPORT_STATUS_VALUES).index(_sel_case3.report_status)
                        if _sel_case3.report_status in REPORT_STATUS_VALUES else 0,
                        key="cw_upd_report_status",
                    )
                    _upd_report_types = st.multiselect(
                        "申請報告類型",
                        ["natal", "compatibility", "human_design", "integrated", "free_summary"],
                        default=_sel_case3.requested_report_types,
                        key="cw_upd_report_types",
                    )
                    _upd_next_action = st.text_input(
                        "下一步行動", value=_sel_case3.next_action, key="cw_upd_next_action"
                    )
                    _upd_next_due = st.text_input(
                        "預計完成日（YYYY-MM-DD）", value=_sel_case3.next_action_due,
                        key="cw_upd_next_due",
                    )
                    _upd_note_content = st.text_area("新增備註", key="cw_upd_note")
                    _upd_note_type = st.selectbox(
                        "備註類型",
                        ["general", "consultation", "follow_up", "report_revision", "payment_note"],
                        key="cw_upd_note_type",
                    )
                    _upd_save = st.form_submit_button("儲存更新")

                if _upd_save:
                    _sel_case3.case_status = _upd_case_status
                    _sel_case3.report_status = _upd_report_status
                    _sel_case3.requested_report_types = _upd_report_types
                    _sel_case3.next_action = _upd_next_action
                    _sel_case3.next_action_due = _upd_next_due
                    update_case(_sel_case_id3, _sel_case3, CLIENT_CASE_STORAGE_PATH)
                    if _upd_note_content.strip():
                        add_note(
                            _sel_case_id3,
                            CaseNote(note_type=_upd_note_type, content=_upd_note_content.strip()),
                            CLIENT_CASE_STORAGE_PATH,
                        )
                    st.success("✅ 個案已更新。")

                st.divider()
                st.caption("現有備註")
                _reloaded3 = get_case(_sel_case_id3, CLIENT_CASE_STORAGE_PATH)
                if _reloaded3 and _reloaded3.notes:
                    for _n in _reloaded3.notes:
                        st.markdown(f"- **[{_n.note_type}]** {_n.created_at[:10] if _n.created_at else ''} — {_n.content}")
                else:
                    st.caption("（無備註）")

    # ── Tab 3: 待辦與交付 ─────────────────────────────────────────────────────
    with _cw_tabs[3]:
        st.subheader("待辦與交付")
        _cw_snap4 = load_cases(CLIENT_CASE_STORAGE_PATH)
        if not _cw_snap4.cases:
            st.info("尚無個案資料。")
        else:
            _case_options4 = {
                f"{c.client.name} ({c.case_id[:14]}…)": c.case_id
                for c in _cw_snap4.cases
            }
            _sel_label4 = st.selectbox("選擇個案", list(_case_options4.keys()), key="cw_sel_case4")
            _sel_id4 = _case_options4.get(_sel_label4)

            if _sel_id4:
                _c4 = get_case(_sel_id4, CLIENT_CASE_STORAGE_PATH)

                if _c4:
                    st.subheader("待辦任務")
                    if _c4.tasks:
                        import pandas as pd
                        _tasks_df = pd.DataFrame([
                            {"task_id": t.task_id, "標題": t.title, "狀態": t.status,
                             "優先級": t.priority, "到期日": t.due_date}
                            for t in _c4.tasks
                        ])
                        st.dataframe(_tasks_df, use_container_width=True)

                        with st.form("cw_update_task_form"):
                            _task_options = {t.title: t.task_id for t in _c4.tasks}
                            _sel_task_title = st.selectbox("選擇任務", list(_task_options.keys()),
                                                           key="cw_sel_task")
                            _sel_task_id = _task_options.get(_sel_task_title, "")
                            _new_task_status = st.selectbox(
                                "更新狀態", ["todo", "doing", "done", "canceled"],
                                key="cw_task_new_status",
                            )
                            _task_upd_btn = st.form_submit_button("更新任務狀態")
                        if _task_upd_btn and _sel_task_id:
                            update_task_status(_sel_id4, _sel_task_id, _new_task_status,
                                               CLIENT_CASE_STORAGE_PATH)
                            st.success("✅ 任務狀態已更新。")
                    else:
                        st.caption("（無待辦任務）")

                    st.divider()
                    st.subheader("新增任務")
                    with st.form("cw_add_task_form"):
                        _task_title = st.text_input("任務標題 *", key="cw_new_task_title")
                        _task_desc = st.text_area("說明", key="cw_new_task_desc")
                        _task_due = st.text_input("到期日（YYYY-MM-DD）", key="cw_new_task_due")
                        _task_priority = st.selectbox("優先級", ["low", "medium", "high"],
                                                      index=1, key="cw_new_task_priority")
                        _task_submit = st.form_submit_button("新增任務")
                    if _task_submit:
                        if not _task_title.strip():
                            st.error("請填寫任務標題。")
                        else:
                            add_task(
                                _sel_id4,
                                CaseTask(
                                    title=_task_title.strip(),
                                    description=_task_desc.strip(),
                                    due_date=_task_due.strip(),
                                    priority=_task_priority,
                                ),
                                CLIENT_CASE_STORAGE_PATH,
                            )
                            st.success("✅ 任務已新增。")

                    st.divider()
                    st.subheader("交付記錄")
                    if _c4.deliveries:
                        import pandas as pd
                        _del_df = pd.DataFrame([
                            {"delivery_id": d.delivery_id, "報告類型": d.report_type,
                             "格式": d.format, "交付時間": d.delivered_at, "備註": d.delivery_note}
                            for d in _c4.deliveries
                        ])
                        st.dataframe(_del_df, use_container_width=True)
                    else:
                        st.caption("（無交付記錄）")

                    st.subheader("新增交付記錄")
                    with st.form("cw_add_delivery_form"):
                        _del_rt = st.selectbox(
                            "報告類型",
                            ["natal", "compatibility", "human_design", "integrated", "free_summary"],
                            key="cw_del_report_type",
                        )
                        _del_fmt = st.selectbox(
                            "格式",
                            ["markdown", "html", "docx", "pdf", "consultation"],
                            key="cw_del_format",
                        )
                        _del_fp = st.text_input("檔案路徑（選填）", key="cw_del_file_path")
                        _del_note = st.text_input("交付備註", key="cw_del_note")
                        _del_submit = st.form_submit_button("記錄交付")
                    if _del_submit:
                        add_delivery(
                            _sel_id4,
                            ReportDelivery(
                                report_type=_del_rt,
                                format=_del_fmt,
                                file_path=_del_fp.strip(),
                                delivery_note=_del_note.strip(),
                            ),
                            CLIENT_CASE_STORAGE_PATH,
                        )
                        st.success("✅ 交付記錄已新增。")

    # ── Tab 4: 匯出 ────────────────────────────────────────────────────────────
    with _cw_tabs[4]:
        st.subheader("匯出")
        _cw_snap5 = load_cases(CLIENT_CASE_STORAGE_PATH)

        if _cw_snap5.cases:
            _metrics5 = compute_case_metrics(_cw_snap5)

            st.markdown("**下載全部個案 CSV**")
            _csv_data = _exp_cases_csv(_cw_snap5)
            st.download_button(
                "⬇️ 下載 cases.csv",
                data=_csv_data.encode("utf-8-sig"),
                file_name=safe_case_filename("all", "csv"),
                mime="text/csv",
                key="cw_dl_csv",
            )

            st.divider()
            _case_options5 = {
                f"{c.client.name} ({c.case_id[:14]}…)": c.case_id
                for c in _cw_snap5.cases
            }
            _sel_label5 = st.selectbox("選擇個案下載", list(_case_options5.keys()), key="cw_sel5")
            _sel_id5 = _case_options5.get(_sel_label5)
            if _sel_id5:
                _c5 = get_case(_sel_id5, CLIENT_CASE_STORAGE_PATH)
                if _c5:
                    _md_data = export_case_markdown(_c5)
                    _html_data = export_case_html(_c5)
                    _safe_label = _c5.client.name or "case"
                    _dl1, _dl2 = st.columns(2)
                    with _dl1:
                        st.download_button(
                            "⬇️ 下載 Markdown",
                            data=_md_data.encode("utf-8"),
                            file_name=safe_case_filename(_safe_label, "md"),
                            mime="text/markdown",
                            key="cw_dl_md",
                        )
                    with _dl2:
                        st.download_button(
                            "⬇️ 下載 HTML",
                            data=_html_data.encode("utf-8"),
                            file_name=safe_case_filename(_safe_label, "html"),
                            mime="text/html",
                            key="cw_dl_html",
                        )

            st.divider()
            _metrics_md = export_case_metrics_markdown(_metrics5)
            st.download_button(
                "⬇️ 下載 Metrics Markdown",
                data=_metrics_md.encode("utf-8"),
                file_name=safe_case_filename("metrics", "md"),
                mime="text/markdown",
                key="cw_dl_metrics",
            )
        else:
            st.info("尚無個案資料可匯出。")

        if DEVELOPER_MODE:
            st.divider()
            st.subheader("⚠️ 危險操作（開發者限定）")
            _confirm_clear = st.checkbox("確認清空所有個案資料", key="cw_confirm_clear")
            if st.button("清空所有個案", key="cw_clear_all_btn", type="secondary"):
                if _confirm_clear:
                    delete_all_cases(CLIENT_CASE_STORAGE_PATH)
                    st.success("✅ 所有個案資料已清空。")
                else:
                    st.warning("請先勾選確認才能清空。")
