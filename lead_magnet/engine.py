"""
V1.9.6 Lead Magnet — Free Report Engine.
Generates short, non-absolute free report summaries.
No forbidden phrases: 一定成功 / 一定分手 / 保證 / 必然 / 絕對命運.
"""
from __future__ import annotations
from datetime import datetime, timezone
from lead_magnet.models import (
    LeadCapture, FreeReportResult, FreeReportSection,
)

_DISCLAIMER = (
    "本報告為免費初步摘要，僅供探索參考，不構成命運斷語或生活決策依據。"
    "完整整合命盤報告包含更詳細的多系統解讀。"
)

# ── Sun sign lookup ───────────────────────────────────────────────────────────

_SUN_SIGN_RANGES = [
    (1,  20, "水瓶座"), (2,  19, "雙魚座"), (3,  21, "牡羊座"),
    (4,  20, "金牛座"), (5,  21, "雙子座"), (6,  21, "巨蟹座"),
    (7,  23, "獅子座"), (8,  23, "處女座"), (9,  23, "天秤座"),
    (10, 23, "天蠍座"), (11, 22, "射手座"), (12, 22, "摩羯座"),
]

_SUN_SIGN_DESC = {
    "牡羊座": "行動力強、勇於開創，適合新計畫的發起者。",
    "金牛座": "穩定務實、重視感官體驗，對物質與美感有高度需求。",
    "雙子座": "好奇心旺盛、善於溝通，能在多元領域快速吸收資訊。",
    "巨蟹座": "情感細膩、重視家庭與安全感，對親近的人照顧周到。",
    "獅子座": "自信表達、具創意熱情，擅長吸引注意力與帶動氣氛。",
    "處女座": "分析細心、注重細節，擅長整合資訊並找出改善方案。",
    "天秤座": "重視平衡與和諧，善於協調關係，對美感與公平有敏銳感知。",
    "天蠍座": "洞察力深刻、情感強烈，對人事有深度的觀察與理解。",
    "射手座": "樂觀開放、追求意義，喜歡探索不同文化與思想。",
    "摩羯座": "目標導向、有耐心，擅長長期規劃與建立穩定結構。",
    "水瓶座": "獨立思考、重視自由，對社會議題與未來發展有獨到見解。",
    "雙魚座": "感受力豐富、富有同理心，對藝術與靈性探索有天然親近感。",
}


def _get_sun_sign(birth_date_str: str) -> str:
    """Return Chinese sun sign name from YYYY-MM-DD string."""
    try:
        dt = datetime.strptime(birth_date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return ""
    m, d = dt.month, dt.day
    for cutoff_m, cutoff_d, sign in _SUN_SIGN_RANGES:
        if m < cutoff_m or (m == cutoff_m and d < cutoff_d):
            return sign
    return "摩羯座"


# ── Report generators ─────────────────────────────────────────────────────────

def _gen_zodiac(lead: LeadCapture) -> FreeReportResult:
    profile = lead.profile
    sign = _get_sun_sign(profile.birth_date or "") if profile.birth_date else ""
    if sign:
        title = f"免費星座速覽：{sign}"
        summary = f"以下是根據你的出生日期所推算的太陽星座（{sign}）初步速覽。"
        desc = _SUN_SIGN_DESC.get(sign, "星座描述一種能量傾向，不是固定的命運結果。")
        sections = [
            FreeReportSection(
                heading="你的星座速覽",
                body=f"你的太陽星座為 **{sign}**。{desc}",
                bullets=[
                    "太陽星座反映核心自我傾向",
                    "實際表現受月亮、上升、其他行星配置影響",
                    "同一星座的人在不同命盤下差異可以很大",
                ],
            ),
            FreeReportSection(
                heading="關係與溝通提示",
                body=(
                    "太陽星座提供初步的互動傾向參考。"
                    "若要了解你在關係中的情感模式，需要結合月亮星座與金星位置。"
                    "溝通風格與水星星座密切相關。"
                ),
            ),
            FreeReportSection(
                heading="為什麼完整命盤不只看太陽星座",
                body=(
                    "完整的西洋占星命盤包含太陽、月亮、上升、水星、金星、火星等十顆以上行星，"
                    "以及十二個宮位的配置。每個元素都描述人生不同層面的傾向。"
                    "太陽星座只是入口，不是全部。"
                ),
            ),
        ]
    else:
        title = "免費星座速覽（初步版本）"
        summary = "出生日期資料不完整，以下提供星座系統的基本說明。"
        sections = [
            FreeReportSection(
                heading="星座速覽需要出生日期",
                body="請提供完整的出生日期（年-月-日），以產生個人化的太陽星座速覽。",
            ),
            FreeReportSection(
                heading="太陽星座的意義",
                body="太陽星座是最廣為人知的占星入口，反映核心自我傾向。完整命盤包含更多層次的資訊。",
            ),
        ]
    return FreeReportResult(
        lead_id=lead.lead_id,
        report_type="zodiac_free_summary",
        title=title,
        summary=summary,
        sections=sections,
        cta_title="想了解完整命盤？",
        cta_description="建立包含太陽、月亮、上升、行星、宮位的完整西洋占星命盤報告。",
        cta_button_label="建立完整命盤報告",
        cta_target="📝 輸入資料",
        disclaimer=_DISCLAIMER,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


def _gen_human_design(lead: LeadCapture) -> FreeReportResult:
    profile = lead.profile
    has_date = bool(profile.birth_date)
    has_time = bool(profile.birth_time)
    hd_type = None
    hd_authority = None
    hd_profile = None

    if has_date and has_time:
        try:
            from datetime import date, time as dtime
            from human_design.engine import HumanDesignEngine
            from core.models import (
                BirthProfile, AnalysisTheme, ReportLanguage, ReportLength,
            )
            bd = datetime.strptime(profile.birth_date, "%Y-%m-%d").date()
            bt_parts = profile.birth_time.split(":")
            bt = dtime(int(bt_parts[0]), int(bt_parts[1]))
            bp = BirthProfile(
                name=profile.name or "User",
                birth_date=bd,
                birth_time=bt,
                birth_city=profile.birth_location or "台北",
                birth_country="台灣",
                themes=list(AnalysisTheme),
                report_language=ReportLanguage.TRADITIONAL_CHINESE,
                report_length=ReportLength.BRIEF,
                birth_latitude=profile.latitude or 25.0,
                birth_longitude=profile.longitude or 121.5,
                birth_timezone_offset=8.0,
                birth_time_is_known=True,
            )
            chart = HumanDesignEngine().calculate(bp)
            hd_type = getattr(chart, "hd_type", None)
            hd_authority = getattr(chart, "authority", None)
            hd_profile = getattr(chart, "profile", None)
        except Exception:
            pass

    if hd_type:
        title = f"免費人類圖 Type 速覽：{hd_type}"
        summary = f"根據你的出生資料，你的人類圖類型為 **{hd_type}**。以下為初步說明。"
        sections = [
            FreeReportSection(
                heading=f"你的人類圖類型：{hd_type}",
                body=(
                    f"人類圖類型（{hd_type}）描述你的能量運作方式與互動策略。"
                    "類型是整張人類圖的基礎，但完整解讀需要結合 Authority、Profile 與閘門通道。"
                ),
                bullets=[
                    f"類型：{hd_type}",
                    f"Authority（決策中心）：{hd_authority}" if hd_authority else "Authority：需完整報告解讀",
                    f"Profile（角色）：{hd_profile}" if hd_profile else "Profile：需完整報告解讀",
                ],
            ),
            FreeReportSection(
                heading="Strategy 的意義",
                body=(
                    "人類圖的 Strategy 是針對你的類型，在互動中最適合的啟動方式。"
                    "這不是「什麼都不做」，而是找到最省力的互動節奏。"
                ),
            ),
            FreeReportSection(
                heading="完整人類圖包含什麼",
                body=(
                    "完整人類圖報告包含 9 個能量中心的定義狀態、64 閘門與 36 通道的活化情況，"
                    "以及 Authority 與 Profile 的詳細解讀。這些共同構成你的完整能量藍圖。"
                ),
            ),
        ]
    elif has_date:
        title = "免費人類圖 Type 速覽（初步版本）"
        summary = "需要精確出生時間才能計算人類圖 Type。以下提供人類圖基本說明。"
        sections = [
            FreeReportSection(
                heading="人類圖需要精確出生時間",
                body=(
                    "人類圖的計算需要精確的出生時間（時、分），以及出生地點。"
                    "出生時間影響 Conscious 行星位置與設計日（Design date）計算。"
                    "如果你有精確的出生時間，請在「📝 輸入資料」填寫以取得完整結果。"
                ),
            ),
            FreeReportSection(
                heading="五種人類圖類型",
                body="人類圖分為顯示者、生產者、顯示生產者、投射者、反映者五種類型，各有不同的能量運作方式與策略。",
                bullets=[
                    "顯示者（約 8%）：啟動型能量",
                    "生產者（約 37%）：持續薦骨能量",
                    "顯示生產者（約 33%）：快速多元能量",
                    "投射者（約 20%）：引導型能量",
                    "反映者（約 1%）：月亮鏡像能量",
                ],
            ),
        ]
    else:
        title = "免費人類圖速覽（初步版本）"
        summary = "出生資料不足，以下提供人類圖系統基本說明。"
        sections = [
            FreeReportSection(
                heading="人類圖是什麼",
                body="人類圖整合占星、易經、卡巴拉與脈輪，描述個人的能量運作模式與決策節奏。需要精確出生日期、時間與地點。",
            ),
        ]
    return FreeReportResult(
        lead_id=lead.lead_id,
        report_type="human_design_free_summary",
        title=title,
        summary=summary,
        sections=sections,
        cta_title="想了解完整人類圖？",
        cta_description="建立完整人類圖報告，包含 Type、Strategy、Authority、Profile 與各中心詳細解讀。",
        cta_button_label="建立完整人類圖報告",
        cta_target="📝 輸入資料",
        disclaimer=_DISCLAIMER,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


def _gen_compatibility(lead: LeadCapture) -> FreeReportResult:
    has_partner = lead.partner is not None and bool(lead.partner.birth_date)
    profile = lead.profile
    partner = lead.partner

    if has_partner:
        p_name = partner.name or "對方"
        my_sign = _get_sun_sign(profile.birth_date or "") if profile.birth_date else ""
        partner_sign = _get_sun_sign(partner.birth_date or "") if partner.birth_date else ""
        title = "免費合盤初評"
        summary = "以下是基於雙方出生日期的初步關係探索，供你參考方向。"
        sign_desc = ""
        if my_sign and partner_sign:
            sign_desc = f"你的太陽星座為 {my_sign}，{p_name} 的太陽星座為 {partner_sign}。"
        sections = [
            FreeReportSection(
                heading="關係探索初步摘要",
                body=(
                    f"{sign_desc}"
                    "太陽星座配對提供初步的能量傾向參考，"
                    "但真正的關係互動模式需要透過 Synastry（星座對照）與 Composite（合盤）分析。"
                ),
                bullets=[
                    "Synastry 分析兩人行星的相位互動",
                    "Composite 揭示這段關係的共同能量場域",
                    "衝突相位不代表不適合，和諧相位也不代表無摩擦",
                    "關係的質量取決於雙方的行動與選擇",
                ],
            ),
            FreeReportSection(
                heading="感情互動的關鍵相位",
                body=(
                    "完整合盤分析看月亮（情感共鳴）、金星與火星（吸引力模式）、"
                    "水星（溝通方式）與土星（長期穩定性）的相位互動。"
                    "這些提供比太陽星座配對更準確的關係洞察。"
                ),
            ),
            FreeReportSection(
                heading="合盤分析的範圍",
                body=(
                    "本系統的完整合盤報告包含感情、溝通、吸引力、穩定性等多個維度的相位分析，"
                    "以及 Composite 合盤的整體關係能量解讀。"
                ),
            ),
        ]
    else:
        title = "免費合盤初評（初步版本）"
        summary = "請提供對方的出生資料，以產生合盤初步探索摘要。"
        sections = [
            FreeReportSection(
                heading="合盤需要雙方資料",
                body="合盤分析需要兩人的出生日期（最好有時間）。請在表單中填寫對方的出生資料。",
            ),
            FreeReportSection(
                heading="合盤能了解什麼",
                body="合盤分析透過 Synastry 與 Composite，幫助了解兩人的互動模式、溝通節奏與關係場域。",
            ),
        ]
    return FreeReportResult(
        lead_id=lead.lead_id,
        report_type="compatibility_free_summary",
        title=title,
        summary=summary,
        sections=sections,
        cta_title="想了解完整合盤？",
        cta_description="建立完整合盤報告，包含 Synastry 相位分析、Composite 合盤與多維度相容性評分。",
        cta_button_label="建立完整合盤報告",
        cta_target="💕 合盤分析",
        disclaimer=_DISCLAIMER,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


def _gen_integrated(lead: LeadCapture) -> FreeReportResult:
    return FreeReportResult(
        lead_id=lead.lead_id,
        report_type="integrated_free_summary",
        title="免費整合命盤摘要",
        summary=(
            "整合命盤將西洋占星、八字、紫微斗數與人類圖四套系統整合解讀，"
            "提供心理特質、五行結構、人生階段與能量模式的多維度視角。"
        ),
        sections=[
            FreeReportSection(
                heading="西洋占星：心理與互動",
                body=(
                    "西洋占星以行星在黃道上的位置計算，描述個人的心理特質、情感模式與人際互動傾向。"
                    "太陽、月亮、上升三個核心點各自描述不同層面的自我。行星相位揭示內在張力與資源。"
                ),
            ),
            FreeReportSection(
                heading="八字：節氣與五行",
                body=(
                    "八字透過出生年、月（節氣切分）、日、時四柱，分析五行能量結構與日主特質。"
                    "五行的比例與平衡反映個人的能量節奏與格局。"
                ),
            ),
            FreeReportSection(
                heading="紫微斗數：人生結構",
                body=(
                    "紫微斗數透過農曆出生時間計算十二宮位與主星配置，描述人生的基本結構與各階段（大限）節奏。"
                    "命宮主星反映核心特質，大限描述每 10 年的人生主題。"
                ),
            ),
            FreeReportSection(
                heading="人類圖：決策與能量",
                body=(
                    "人類圖透過出生時的行星位置計算 9 個能量中心，描述能量運作方式、決策節奏（Authority）"
                    "與互動策略（Strategy）。特別適合了解自己的能量邊界。"
                ),
            ),
            FreeReportSection(
                heading="為什麼要整合四套系統",
                body=(
                    "每套系統都有其擅長的維度。當多個系統指向相似的傾向時，這些特質往往更為突出。"
                    "整合命盤提供多維度的探索工具，而不是給出唯一答案。"
                ),
            ),
        ],
        cta_title="準備好建立完整整合命盤了嗎？",
        cta_description="輸入出生資料，建立包含西洋占星、八字、紫微、人類圖的完整整合命盤報告。",
        cta_button_label="建立完整整合命盤報告",
        cta_target="📝 輸入資料",
        disclaimer=_DISCLAIMER,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


def generate_free_report(lead: LeadCapture) -> FreeReportResult:
    """Dispatch to the appropriate free report generator by report_type."""
    rt = lead.report_type
    if rt == "zodiac_free_summary":
        return _gen_zodiac(lead)
    elif rt == "human_design_free_summary":
        return _gen_human_design(lead)
    elif rt == "compatibility_free_summary":
        return _gen_compatibility(lead)
    else:
        return _gen_integrated(lead)
