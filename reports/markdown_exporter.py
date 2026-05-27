"""
Astro Destiny Analyzer — Markdown Exporter
Produces a complete Markdown report with cover, disclaimer, calc-mode
summary, TOC, and the full body from reports/templates.py.
"""
import re
from core.models import FullReport
from reports.templates import render_report
from reports.utils import build_report_meta, DISCLAIMER
from config import APP_VERSION


_COVER_TEMPLATE = """\
# {app_name}
## 命盤整合分析報告

| 項目 | 資料 |
|------|------|
| 姓名 | {name} |
| 出生日期 | {birth_date} |
| 出生時間 | {birth_time} |
| 出生地 | {location} |
| 產生時間 | {created_at} |
| 系統版本 | v{app_version} |

---

## ⚠️ 免責聲明

> {disclaimer}

---

## 基本資料

| 項目 | 內容 |
|------|------|
| 姓名 | {name} |
| 性別 | {gender} |
| 出生日期 | {birth_date} |
| 出生時間 | {birth_time} |
| 出生地 | {location} |
| 血型 | {blood_type} |
| 分析主題 | {themes} |
| 報告長度 | {report_length} |

---

## 計算模式摘要

| 系統 | 計算模式 | 備注 |
|------|----------|------|
| 西洋占星 | {western_mode} | {western_note} |
| 八字 | {bazi_mode} | {bazi_note} |
| 紫微 | {ziwei_mode} | {ziwei_note} |
| 紫微輔星 | — | {ziwei_aux_note} |
| 紫微大限 | {daxian_accuracy} | — |

---

## 一頁式總覽

| 指標 | 數值 | 指標 | 數值 |
|------|------|------|------|
| 太陽星座 | {sun_sign} | 月亮星座 | {moon_sign} |
| 上升星座 | {asc_sign} | 天頂 MC | {mc_sign} |
| 八字日主 | {day_master} | 喜用神 | {fav_elements} |
| 命宮主星 | {ming_stars} | 身宮 | {shen_name} |
| 五行局 | {bureau} | 生命靈數 | {life_path} |
| 血型 | {blood_type} | — | — |

---

## 目錄

1. 西洋占星分析
2. 八字命理分析
3. 紫微斗數分析
4. 血型分析
5. 生命靈數分析
6. 整合分析
7. 感情模式
8. 事業與職涯
9. 財富與資源
10. 人際關係
11. 壓力與陰影
12. 流年 / 三年趨勢
13. 行動建議

---

"""


class MarkdownExporter:
    def export(self, report: FullReport) -> str:
        meta = build_report_meta(report)
        cover = _COVER_TEMPLATE.format(**meta)
        body = render_report(report, version=APP_VERSION)
        # Clean up excessive blank lines (4+ → 3)
        body = re.sub(r'\n{4,}', '\n\n\n', body)
        return cover + body

    def save(self, report: FullReport, path: str) -> None:
        content = self.export(report)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
