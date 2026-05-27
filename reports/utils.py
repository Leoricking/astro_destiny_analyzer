"""
Astro Destiny Analyzer — Report Utilities
Safe filename, export filename helpers, and shared report metadata builder.
"""
import re
from datetime import datetime
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from core.models import FullReport

DISCLAIMER = (
    "本報告為自我探索、人格理解與娛樂參考工具，"
    "不構成科學定論、醫療診斷、法律意見、投資建議或絕對命運預測。"
    "請以開放態度閱讀，並以自身判斷做最終決策。"
)


def sanitize_filename(name: str) -> str:
    """
    Remove Windows-illegal characters (\\/:*?"<>|) and newlines.
    Preserve Chinese characters. Truncate to 80 chars.
    Falls back to 'astro_report' for empty input.
    """
    if not name or not name.strip():
        return "astro_report"
    cleaned = re.sub(r'[\\/:*?"<>|\r\n\t]', '', name)
    cleaned = cleaned.strip()
    if not cleaned:
        return "astro_report"
    return cleaned[:80]


def make_export_filename(name: str, ext: str) -> str:
    """Build: {safe_name}_命盤整合分析報告_{YYYYMMDD_HHMM}.{ext}"""
    safe = sanitize_filename(name)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    return f"{safe}_命盤整合分析報告_{ts}.{ext}"


def build_report_meta(report: "FullReport") -> Dict[str, Any]:
    """
    Extract all cover / summary metadata from a FullReport into a flat dict.
    Used by Markdown, HTML, and DOCX exporters for consistent cover pages.
    """
    from config import APP_VERSION, APP_NAME

    profile = report.profile

    birth_time_str = (
        profile.birth_time.strftime("%H:%M") if profile.birth_time else "未知"
    )
    birth_city_str = profile.birth_city or "未提供"
    birth_country_str = profile.birth_country or ""
    if birth_country_str and birth_country_str != birth_city_str:
        location_str = f"{birth_city_str}，{birth_country_str}"
    else:
        location_str = birth_city_str

    gender_map = {"male": "男", "female": "女", "other": "其他", "unknown": "未填寫"}
    gender_val = profile.gender.value if profile.gender else "unknown"
    gender_str = gender_map.get(gender_val, "未填寫")
    blood_str = profile.blood_type.value if profile.blood_type else "未填寫"
    themes_str = "、".join(t.value for t in (profile.themes or []))
    length_str = profile.report_length.value if profile.report_length else ""

    # Calculation modes
    wc = report.western_chart
    bc = report.bazi_chart
    zc = report.ziwei_chart

    western_mode = getattr(wc, "calculation_mode", "─") if wc else "─"
    western_note = getattr(wc, "accuracy_note", "") if wc else ""
    bazi_mode    = getattr(bc, "calculation_mode", "─") if bc else "─"
    bazi_note    = getattr(bc, "accuracy_note", "") if bc else ""
    ziwei_mode   = getattr(zc, "calculation_mode", "─") if zc else "─"
    ziwei_note   = getattr(zc, "accuracy_note", "") if zc else ""
    ziwei_aux_note  = getattr(zc, "auxiliary_accuracy_note", "") if zc else ""
    daxian_accuracy = getattr(zc, "da_xian_accuracy", "") if zc else ""

    # One-page overview — Western
    sun_sign = moon_sign = asc_sign = mc_sign = "─"
    if wc and wc.planet_positions:
        for pp in wc.planet_positions:
            if getattr(getattr(pp, "planet", None), "value", "") == "太陽":
                sun_sign = getattr(getattr(pp, "sign", None), "value", "─") or "─"
            elif getattr(getattr(pp, "planet", None), "value", "") == "月亮":
                moon_sign = getattr(getattr(pp, "sign", None), "value", "─") or "─"
    if wc and getattr(wc, "ascendant_accuracy", "") == "precise" and wc.ascendant:
        asc_sign = wc.ascendant.value
    if wc and getattr(wc, "mc_accuracy", "") == "precise" and wc.mc:
        mc_sign = wc.mc.value

    # One-page overview — BaZi
    day_master = fav_elements = "─"
    if bc and bc.day_master:
        dm_elem = getattr(bc, "day_master_element", None)
        day_master = (
            f"{bc.day_master.value}（{dm_elem.value}）" if dm_elem else bc.day_master.value
        )
    if bc and bc.favorable_elements:
        fav_elements = "、".join(e.value for e in bc.favorable_elements)

    # One-page overview — Zi Wei
    ming_stars = shen_name = bureau = "─"
    if zc:
        if zc.ming_palace:
            stars = zc.ming_palace.main_stars
            ming_stars = "、".join(stars) if stars else "空宮"
        shen_p = getattr(zc, "shen_palace", None)
        if shen_p:
            shen_name = shen_p.name
        elif getattr(zc, "shen_branch", None):
            shen_name = zc.shen_branch
        bureau = getattr(zc, "five_element_bureau", None) or "─"

    # Numerology
    life_path = "─"
    nc = report.numerology_chart
    if nc and getattr(nc, "life_path_number", None) is not None:
        life_path = str(nc.life_path_number)

    return {
        "name": profile.name,
        "birth_date": str(profile.birth_date),
        "birth_time": birth_time_str,
        "location": location_str,
        "gender": gender_str,
        "blood_type": blood_str,
        "themes": themes_str,
        "report_length": length_str,
        "created_at": report.created_at or "",
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "disclaimer": DISCLAIMER,
        "western_mode": western_mode,
        "western_note": western_note,
        "bazi_mode": bazi_mode,
        "bazi_note": bazi_note,
        "ziwei_mode": ziwei_mode,
        "ziwei_note": ziwei_note,
        "ziwei_aux_note": ziwei_aux_note,
        "daxian_accuracy": daxian_accuracy,
        "sun_sign": sun_sign,
        "moon_sign": moon_sign,
        "asc_sign": asc_sign,
        "mc_sign": mc_sign,
        "day_master": day_master,
        "fav_elements": fav_elements,
        "ming_stars": ming_stars,
        "shen_name": shen_name,
        "bureau": bureau,
        "life_path": life_path,
    }
