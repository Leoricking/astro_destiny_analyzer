"""
Zi Wei Reconciliation Engine — V1.7.3.
Compares a local ZiWeiChart against a manually-entered ExternalZiWeiChart.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional

from core.models import ZiWeiChart
from ziwei_reconciliation.models import (
    ExternalZiWeiChart,
    ReconciliationItem,
    ZiWeiReconciliationReport,
)
from ziwei_reconciliation.templates import render_reconciliation_markdown


# ── Helpers ────────────────────────────────────────────────────────────────────

def _norm_bureau(name: Optional[str]) -> str:
    """Normalise five-element bureau name for comparison.

    外部網站常寫完整名稱如「爐中火六局」，本機只寫「火六局」。
    """
    if not name:
        return ""
    # Strip classical poetic prefix (木=木, 火=火, 金=金, 水=水, 土=土)
    # 爐中火 → 火, 海中金 → 金, etc.
    for elem in ("水", "木", "金", "土", "火"):
        if elem in name:
            # Extract element + number suffix
            m = re.search(rf"{elem}[二三四五六]局", name)
            if m:
                return m.group()
    return name.strip()


def _stars_match(local: List[str], external: List[str]) -> bool:
    """Stars match if they contain the same elements regardless of order."""
    return set(local) == set(external)


def _item(category: str, field_name: str, local_val: str, ext_val: str,
          status: str, severity: str, explanation: str = "") -> ReconciliationItem:
    return ReconciliationItem(
        category=category,
        field_name=field_name,
        local_value=local_val,
        external_value=ext_val,
        status=status,
        severity=severity,
        explanation=explanation,
    )


# ── Engine ─────────────────────────────────────────────────────────────────────

class ZiWeiReconciliationEngine:
    """Compare local ZiWeiChart against ExternalZiWeiChart."""

    def reconcile(
        self,
        local_chart: ZiWeiChart,
        external_chart: ExternalZiWeiChart,
    ) -> ZiWeiReconciliationReport:
        items: List[ReconciliationItem] = []

        # A. Basic information
        items.extend(self._compare_basic(local_chart, external_chart))

        # B. Palace branch comparison (twelve palaces)
        items.extend(self._compare_palace_branches(local_chart, external_chart))

        # C. Main star comparison
        items.extend(self._compare_main_stars(local_chart, external_chart))

        # D. Four transformations (四化)
        items.extend(self._compare_sihua(local_chart, external_chart))

        # E. Auxiliary / malefic stars
        items.extend(self._compare_aux_malefic(local_chart, external_chart))

        # F. Da Xian (大限)
        items.extend(self._compare_da_xian(local_chart, external_chart))

        # G. Tian Ma (V1.7.5)
        items.extend(self._compare_tian_ma(local_chart, external_chart))

        # H. Luck score / brightness
        items.extend(self._compare_not_implemented(local_chart, external_chart))

        # Tally
        match_count = sum(1 for i in items if i.status == "match")
        mismatch_count = sum(1 for i in items if i.status == "mismatch")
        not_implemented_count = sum(1 for i in items if i.status == "not_implemented")
        school_diff_count = sum(1 for i in items if i.status == "likely_school_difference")

        # H. Overall status
        high_mismatches = sum(
            1 for i in items if i.status == "mismatch" and i.severity == "high"
        )
        total_decided = match_count + mismatch_count + school_diff_count
        if total_decided < 3:
            overall = "insufficient_data"
        elif high_mismatches >= 3:
            overall = "major_difference"
        elif mismatch_count > match_count:
            overall = "partial_match"
        else:
            overall = "mostly_match"

        summary = self._build_summary(
            overall, match_count, mismatch_count, not_implemented_count,
            school_diff_count, items,
        )
        recommendation = self._build_recommendation(overall, items)

        report = ZiWeiReconciliationReport(
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            source_name=external_chart.source_name,
            overall_status=overall,
            match_count=match_count,
            mismatch_count=mismatch_count,
            not_implemented_count=not_implemented_count,
            school_difference_count=school_diff_count,
            items=items,
            summary=summary,
            recommendation=recommendation,
        )
        report.markdown_body = render_reconciliation_markdown(report)
        return report

    # ── A. Basic info ──────────────────────────────────────────────────────────

    def _compare_basic(
        self, local: ZiWeiChart, ext: ExternalZiWeiChart
    ) -> List[ReconciliationItem]:
        items: List[ReconciliationItem] = []

        # Five-element bureau
        local_bureau = _norm_bureau(local.five_element_bureau)
        ext_bureau = _norm_bureau(ext.five_element_bureau)
        if ext_bureau:
            if local_bureau and local_bureau == ext_bureau:
                items.append(_item(
                    "basic", "五行局", local_bureau, ext_bureau, "match", "info",
                ))
            elif local_bureau:
                items.append(_item(
                    "basic", "五行局", local_bureau, ext_bureau, "mismatch", "high",
                    "五行局決定大限起始歲數，差異影響重大。",
                ))
            else:
                items.append(_item(
                    "basic", "五行局", "（本機未計算）", ext_bureau, "missing_local", "medium",
                ))

        # 命宮地支
        local_ming = local.ming_branch or ""
        ext_ming = ext.ming_palace_branch or ""
        if ext_ming:
            if local_ming == ext_ming:
                items.append(_item("basic", "命宮地支", local_ming, ext_ming, "match", "info"))
            elif local_ming:
                items.append(_item(
                    "basic", "命宮地支", local_ming, ext_ming, "mismatch", "high",
                    "命宮地支錯誤會導致整個十二宮位偏移，需優先確認農曆日期與時辰。",
                ))
            else:
                items.append(_item("basic", "命宮地支", "（本機未記錄）", ext_ming, "missing_local", "medium"))

        # 身宮地支
        local_shen = local.shen_branch or ""
        ext_shen = ext.shen_palace_branch or ""
        if ext_shen:
            if local_shen == ext_shen:
                items.append(_item("basic", "身宮地支", local_shen, ext_shen, "match", "info"))
            elif local_shen:
                items.append(_item(
                    "basic", "身宮地支", local_shen, ext_shen, "mismatch", "medium",
                    "身宮差異可能因身宮演算法流派不同。",
                ))
            else:
                items.append(_item("basic", "身宮地支", "（本機未記錄）", ext_shen, "missing_local", "low"))

        # 命主
        if ext.ming_zhu:
            local_mz = getattr(local, "ming_zhu", None) or ""
            if local_mz and local_mz == ext.ming_zhu:
                items.append(_item("basic", "命主", local_mz, ext.ming_zhu, "match", "info"))
            elif local_mz:
                items.append(_item(
                    "basic", "命主", local_mz, ext.ming_zhu, "mismatch", "medium",
                    "命主差異可能源自流派表法不同。",
                ))
            else:
                items.append(_item(
                    "basic", "命主", "（尚未實作）", ext.ming_zhu, "not_implemented", "info",
                    "本機未計算命主。",
                ))
        # 身主
        if ext.shen_zhu:
            local_sz = getattr(local, "shen_zhu", None) or ""
            if local_sz and local_sz == ext.shen_zhu:
                items.append(_item("basic", "身主", local_sz, ext.shen_zhu, "match", "info"))
            elif local_sz:
                items.append(_item(
                    "basic", "身主", local_sz, ext.shen_zhu, "mismatch", "medium",
                    "身主差異可能源自流派表法不同。",
                ))
            else:
                items.append(_item(
                    "basic", "身主", "（尚未實作）", ext.shen_zhu, "not_implemented", "info",
                    "本機未計算身主。",
                ))

        # 農曆日期（若本機有記錄）
        if local.lunar_year and local.lunar_month and local.lunar_day and ext.birth_lunar_date:
            local_lunar = f"{local.lunar_year}-{local.lunar_month:02d}-{local.lunar_day:02d}"
            # Extract numeric part from external string e.g. "1989-08-22 午時"
            m = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", ext.birth_lunar_date)
            if m:
                ext_lunar = m.group(1)
                # Normalise
                parts = ext_lunar.split("-")
                ext_lunar_norm = f"{parts[0]}-{int(parts[1]):02d}-{int(parts[2]):02d}"
                if local_lunar == ext_lunar_norm:
                    items.append(_item("basic", "農曆日期", local_lunar, ext_lunar_norm, "match", "info"))
                else:
                    items.append(_item(
                        "basic", "農曆日期", local_lunar, ext_lunar_norm, "mismatch", "high",
                        "農曆轉換差異會影響所有星曜定位，需確認農曆換算來源。",
                    ))

        return items

    # ── B. Palace branch comparison ────────────────────────────────────────────

    def _compare_palace_branches(
        self, local: ZiWeiChart, ext: ExternalZiWeiChart
    ) -> List[ReconciliationItem]:
        if not ext.palaces:
            return []

        local_palace_map: dict[str, str] = {}
        for attr in (
            "ming_palace", "shen_palace", "brother_palace", "spouse_palace",
            "children_palace", "wealth_palace", "health_palace", "travel_palace",
            "friends_palace", "career_palace", "property_palace", "fortune_palace",
            "parents_palace",
        ):
            p = getattr(local, attr, None)
            if p:
                local_palace_map[p.name] = p.earthly_branch

        items: List[ReconciliationItem] = []
        for ep in ext.palaces:
            local_branch = local_palace_map.get(ep.palace_name, "")
            if not ep.branch:
                continue
            if local_branch == ep.branch:
                items.append(_item(
                    "palace_branch", f"{ep.palace_name}地支",
                    local_branch, ep.branch, "match", "info",
                ))
            elif local_branch:
                items.append(_item(
                    "palace_branch", f"{ep.palace_name}地支",
                    local_branch, ep.branch, "mismatch", "high",
                    f"{ep.palace_name}地支不同，需確認命宮起算點與安宮方向。",
                ))
            else:
                items.append(_item(
                    "palace_branch", f"{ep.palace_name}地支",
                    "（本機未找到此宮）", ep.branch, "missing_local", "medium",
                ))
        return items

    # ── C. Main star comparison ────────────────────────────────────────────────

    def _compare_main_stars(
        self, local: ZiWeiChart, ext: ExternalZiWeiChart
    ) -> List[ReconciliationItem]:
        if not ext.palaces:
            return []

        local_palace_star_map: dict[str, list[str]] = {}
        for attr in (
            "ming_palace", "shen_palace", "brother_palace", "spouse_palace",
            "children_palace", "wealth_palace", "health_palace", "travel_palace",
            "friends_palace", "career_palace", "property_palace", "fortune_palace",
            "parents_palace",
        ):
            p = getattr(local, attr, None)
            if p:
                local_palace_star_map[p.name] = list(p.main_stars)

        items: List[ReconciliationItem] = []
        for ep in ext.palaces:
            if not ep.main_stars:
                continue
            local_stars = local_palace_star_map.get(ep.palace_name, [])
            local_str = "、".join(sorted(local_stars)) if local_stars else "無主星"
            ext_str = "、".join(sorted(ep.main_stars))

            if _stars_match(local_stars, ep.main_stars):
                items.append(_item(
                    "main_stars", f"{ep.palace_name}主星",
                    local_str, ext_str, "match", "info",
                    "星曜一致（順序不影響比對）。" if local_stars != ep.main_stars else "",
                ))
            elif not local_stars:
                items.append(_item(
                    "main_stars", f"{ep.palace_name}主星",
                    "無主星", ext_str, "missing_local", "medium",
                    "本機此宮無主星，外部有主星，需確認安星表。",
                ))
            else:
                # Check if superset/subset — might be school difference
                local_set = set(local_stars)
                ext_set = set(ep.main_stars)
                overlap = local_set & ext_set
                if overlap and len(overlap) / max(len(local_set), len(ext_set)) >= 0.5:
                    items.append(_item(
                        "main_stars", f"{ep.palace_name}主星",
                        local_str, ext_str, "likely_school_difference", "medium",
                        "部分主星相同，差異可能源自不同安星表或流派版本。",
                    ))
                else:
                    items.append(_item(
                        "main_stars", f"{ep.palace_name}主星",
                        local_str, ext_str, "mismatch", "high",
                        "主星完全不同，需確認農曆日期、時辰與安星流派。",
                    ))
        return items

    # ── D. Four transformations (四化) ────────────────────────────────────────

    def _compare_sihua(
        self, local: ZiWeiChart, ext: ExternalZiWeiChart
    ) -> List[ReconciliationItem]:
        if not ext.sihua:
            return []

        # local four_transformations: {star: 化祿/化權/化科/化忌}
        local_sihua = local.four_transformations  # {star -> label}

        # Build {label -> star} for easy lookup
        local_by_label: dict[str, str] = {}
        for star, label in local_sihua.items():
            local_by_label[label] = star

        ext_by_label: dict[str, str] = {}
        for star, label in ext.sihua.items():
            ext_by_label[label] = star

        items: List[ReconciliationItem] = []
        for label in ("化祿", "化權", "化科", "化忌"):
            local_star = local_by_label.get(label, "")
            ext_star = ext_by_label.get(label, "")
            if not ext_star:
                continue
            if local_star == ext_star:
                items.append(_item(
                    "transformations", label, local_star, ext_star, "match", "info",
                ))
            elif local_star:
                items.append(_item(
                    "transformations", label, local_star, ext_star, "mismatch", "medium",
                    "四化差異可能源自年干輸入不同或不同流派生年四化表。",
                ))
            else:
                items.append(_item(
                    "transformations", label, "（本機未計算）", ext_star, "missing_local", "low",
                ))
        return items

    # ── E. Auxiliary / malefic stars ───────────────────────────────────────────

    def _compare_aux_malefic(
        self, local: ZiWeiChart, ext: ExternalZiWeiChart
    ) -> List[ReconciliationItem]:
        if not ext.palaces:
            return []

        # Build local auxiliary_star_map: {star → branch}
        local_aux = local.auxiliary_star_map  # {star → branch}
        local_malefic = local.malefic_star_map

        # Key malefic stars to check individually
        key_malefics = ["擎羊", "陀羅", "火星", "鈴星", "地空", "地劫"]

        items: List[ReconciliationItem] = []
        for ep in ext.palaces:
            all_ext_aux = ep.auxiliary_stars + ep.malefic_stars
            for star in all_ext_aux:
                local_branch = local_aux.get(star) or local_malefic.get(star)
                if local_branch is None:
                    # Check if this is a Phase 1 implemented star or not
                    if star in key_malefics:
                        if local_malefic.get(star):
                            local_b = local_malefic[star]
                            if local_b == ep.branch:
                                items.append(_item(
                                    "malefic", f"{star}位置",
                                    local_b, ep.branch, "match", "info",
                                ))
                            else:
                                items.append(_item(
                                    "malefic", f"{star}位置",
                                    local_b, ep.branch, "likely_school_difference", "low",
                                    "六煞星位置差異通常是流派表法或安星細節差異。",
                                ))
                        else:
                            items.append(_item(
                                "malefic", f"{star}位置",
                                "（出生時辰需知）", ep.branch, "not_implemented", "info",
                                "此星需出生時辰，若時辰未知則無法安置。",
                            ))
                    else:
                        items.append(_item(
                            "auxiliary", f"{star}位置",
                            "（尚未實作）", ep.branch, "not_implemented", "info",
                            "V1.5.5 Phase 1 尚未實作此輔星。",
                        ))
        return items

    # ── F. Da Xian comparison ──────────────────────────────────────────────────

    def _compare_da_xian(
        self, local: ZiWeiChart, ext: ExternalZiWeiChart
    ) -> List[ReconciliationItem]:
        if not ext.palaces:
            return []

        items: List[ReconciliationItem] = []
        local_da_xian = local.da_xian

        # Check start age from local
        if local_da_xian and local.da_xian_start_age is not None:
            local_start = local.da_xian_start_age
            # Look for da_xian_range in external palaces
            for ep in ext.palaces:
                if ep.da_xian_range:
                    m = re.search(r"(\d+)[~～\-–—至到](\d+)", ep.da_xian_range)
                    if m:
                        ext_start = int(m.group(1))
                        if local_start == ext_start:
                            items.append(_item(
                                "da_xian", "大限起始歲數",
                                str(local_start), str(ext_start), "match", "info",
                            ))
                        else:
                            items.append(_item(
                                "da_xian", "大限起始歲數",
                                str(local_start), str(ext_start), "mismatch", "high",
                                "大限起始歲數差異通常源自五行局錯誤或陰陽男女順逆判斷不同。",
                            ))
                        break

        # If external has xiao_xian_ages, mark as not_implemented
        for ep in ext.palaces:
            if ep.xiao_xian_ages:
                items.append(_item(
                    "da_xian", f"{ep.palace_name}小限",
                    "（尚未實作）", str(ep.xiao_xian_ages), "not_implemented", "info",
                    "本機 V1.5.5 Phase 1 尚未實作完整小限。",
                ))
                break  # one note is sufficient

        return items

    # ── G. Tian Ma comparison ──────────────────────────────────────────────────

    def _compare_tian_ma(
        self, local: ZiWeiChart, ext: ExternalZiWeiChart
    ) -> List[ReconciliationItem]:
        """Compare 天馬 branch between local and external chart."""
        items: List[ReconciliationItem] = []
        # Find 天馬 in external auxiliary stars
        ext_tian_ma_branch: Optional[str] = None
        for ep in (ext.palaces or []):
            if "天馬" in ep.auxiliary_stars:
                ext_tian_ma_branch = ep.branch
                break
        if ext_tian_ma_branch is None:
            return items

        local_tm = getattr(local, "tian_ma_branch", None) or ""
        if local_tm == ext_tian_ma_branch:
            items.append(_item(
                "auxiliary", "天馬位置",
                local_tm, ext_tian_ma_branch, "match", "info",
            ))
        elif local_tm:
            items.append(_item(
                "auxiliary", "天馬位置",
                local_tm, ext_tian_ma_branch, "mismatch", "medium",
                "天馬位置差異，請確認年支三合局表法。",
            ))
        else:
            items.append(_item(
                "auxiliary", "天馬位置",
                "（未計算）", ext_tian_ma_branch, "not_implemented", "info",
                "本機未計算天馬。",
            ))
        return items

    # ── H. Not-implemented features ────────────────────────────────────────────

    def _compare_not_implemented(
        self, local: ZiWeiChart, ext: ExternalZiWeiChart
    ) -> List[ReconciliationItem]:
        items: List[ReconciliationItem] = []

        # Score / 好運指數
        if ext.luck_score is not None:
            local_score = getattr(local, "ziwei_score", None)
            if local_score is not None:
                items.append(_item(
                    "score", "好運指數 vs 盤面強度",
                    f"本機 Phase 1 盤面強度：{local_score}",
                    f"外部好運指數：{ext.luck_score}",
                    "likely_school_difference", "info",
                    "本機分數為 Astro Destiny Analyzer Phase 1 盤面強度指標，不等同外部網站好運指數，兩者演算法不同，差異屬模型差異非排盤錯誤。",
                ))
            else:
                items.append(_item(
                    "score", "好運指數",
                    "（尚未實作）", str(ext.luck_score), "not_implemented", "info",
                    "外部網站好運指數屬自家權重模型，本系統目前未實作，不能視為排盤錯誤。",
                ))

        # Brightness (廟旺陷) — compare per palace
        local_bmap: dict = getattr(local, "brightness_map", {}) or {}
        for ep in (ext.palaces or []):
            if not ep.brightness:
                continue
            local_palace_brightness = local_bmap.get(ep.palace_name, {})
            if not local_palace_brightness:
                items.append(_item(
                    "brightness", f"{ep.palace_name}廟旺陷",
                    "（尚未實作）", str(ep.brightness), "not_implemented", "info",
                    "廟旺陷演算法尚未實作。",
                ))
            else:
                # Compare each star's brightness
                matches = all(
                    local_palace_brightness.get(star, "平") == bv
                    for star, bv in ep.brightness.items()
                    if star in local_palace_brightness
                )
                if matches and ep.brightness.keys() <= local_palace_brightness.keys():
                    items.append(_item(
                        "brightness", f"{ep.palace_name}廟旺陷",
                        str(local_palace_brightness), str(ep.brightness),
                        "match", "info", "廟旺陷一致。",
                    ))
                else:
                    items.append(_item(
                        "brightness", f"{ep.palace_name}廟旺陷",
                        str(local_palace_brightness), str(ep.brightness),
                        "likely_school_difference", "low",
                        "廟旺陷部分差異，各流派表法不同屬正常。",
                    ))
            break  # one palace brightness summary is sufficient

        return items

    # ── Summary / recommendation ───────────────────────────────────────────────

    def _build_summary(
        self, overall: str, match_count: int, mismatch_count: int,
        not_implemented_count: int, school_diff_count: int,
        items: List[ReconciliationItem],
    ) -> str:
        consistent_fields = [i.field_name for i in items if i.status == "match" and i.category == "basic"]
        mismatch_fields = [i.field_name for i in items if i.status == "mismatch"]

        lines = []
        if match_count > 0:
            lines.append(f"核心一致項目 {match_count} 個" + (
                f"（{', '.join(consistent_fields[:3])}{'...' if len(consistent_fields) > 3 else ''}）"
                if consistent_fields else ""
            ))
        if mismatch_count > 0:
            lines.append(f"不一致項目 {mismatch_count} 個" + (
                f"（{', '.join(mismatch_fields[:3])}{'...' if len(mismatch_fields) > 3 else ''}）"
                if mismatch_fields else ""
            ))
        if school_diff_count > 0:
            lines.append(f"可能流派差異 {school_diff_count} 項，不代表排盤錯誤。")
        if not_implemented_count > 0:
            lines.append(f"尚未實作功能 {not_implemented_count} 項（如廟旺陷、命主身主、好運指數）。")

        overall_zh = {"mostly_match": "大致一致", "partial_match": "部分一致",
                      "major_difference": "有主要差異", "insufficient_data": "資料不足"}
        prefix = f"整體比對結果：{overall_zh.get(overall, overall)}。"
        return prefix + " ".join(lines)

    def _build_recommendation(
        self, overall: str, items: List[ReconciliationItem]
    ) -> str:
        recs = []
        high_mismatches = [i for i in items if i.status == "mismatch" and i.severity == "high"]
        if any(i.field_name in ("命宮地支", "五行局", "農曆日期") for i in high_mismatches):
            recs.append("命宮地支、五行局或農曆日期有差異，請優先確認農曆換算來源、出生時辰是否正確輸入。")
        if any(i.category == "main_stars" and i.status == "mismatch" for i in items):
            recs.append("主星有差異，需檢查農曆日期、時辰與安星表流派是否相同。")
        if any(i.category in ("auxiliary", "malefic") and i.status in ("mismatch", "likely_school_difference") for i in items):
            recs.append("輔星/煞星差異通常屬流派表法不同，可先標記為流派差異，不必過度糾結。")
        if any(i.status == "not_implemented" for i in items):
            recs.append("好運指數、廟旺陷、命主身主等屬網站自家功能，不是標準紫微必備欄位，不應作為排盤正確性唯一依據。")
        if overall in ("mostly_match", "partial_match"):
            recs.append("若命宮、五行局、大限起始一致，可視基礎排盤大致符合，細節差異多屬流派問題。")
        if not recs:
            recs.append("本次比對資料充足，請詳閱上方各分類結果。")
        return " ".join(recs)
