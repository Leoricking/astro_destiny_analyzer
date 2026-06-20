"""
Astro Destiny Analyzer — HTML Exporter
Produces a self-contained HTML document with embedded CSS, cover page,
disclaimer, calculation-mode summary, one-page overview, TOC, and body.
No external CDN or CSS dependencies. Supports Traditional Chinese.
"""
from core.models import FullReport
from reports.templates import render_report
from reports.utils import build_report_meta
import config as _cfg

try:
    import markdown as _md_lib
    _MD_AVAILABLE = True
except ImportError:
    _MD_AVAILABLE = False

# ── CSS ────────────────────────────────────────────────────────────────────────
# All curly braces in this CSS string are literal CSS braces,
# NOT Python format specs. This string is substituted as a value,
# not expanded with .format().
_CSS = (
    "body {"
    '  font-family: "Microsoft JhengHei", "Noto Sans TC", Arial, sans-serif;'
    "  max-width: 960px;"
    "  margin: 40px auto;"
    "  padding: 0 32px;"
    "  color: #222;"
    "  line-height: 1.75;"
    "  background: #faf9f7;"
    "}\n"
    "h1 { color: #3d2b1f; border-bottom: 2px solid #c9a96e;"
    "     padding-bottom: 8px; font-size: 1.8em; margin-top: 1.5em; }\n"
    "h2 { color: #5a3e28; border-left: 4px solid #c9a96e;"
    "     padding-left: 12px; margin-top: 2em; font-size: 1.35em; }\n"
    "h3 { color: #7a5c40; margin-top: 1.5em; font-size: 1.15em; }\n"
    "h4 { color: #8a6a50; margin-top: 1em; }\n"
    "p  { margin: 0.6em 0; }\n"
    "table { border-collapse: collapse; width: 100%; margin: 16px 0; }\n"
    "th, td { border: 1px solid #d4c5b0; padding: 10px 14px; text-align: left; }\n"
    "th { background: #f0e8d8; font-weight: bold; }\n"
    "tr:nth-child(even) { background: #faf5ee; }\n"
    "blockquote { border-left: 4px solid #c9a96e; margin: 16px 0;"
    "             padding: 10px 18px; background: #f5f0e8; color: #555; }\n"
    "code { background: #eee; padding: 2px 6px; border-radius: 3px;"
    "       font-family: monospace; }\n"
    "pre code { display: block; padding: 12px; overflow-x: auto; }\n"
    "hr { border: none; border-top: 1px solid #d4c5b0; margin: 2.5em 0; }\n"
    "ul, ol { padding-left: 2em; }\n"
    "li { margin: 0.3em 0; }\n"
    "\n"
    "/* Cover */\n"
    ".cover {"
    "  text-align: center; padding: 60px 40px 40px;"
    "  background: linear-gradient(135deg, #f5f0e8 0%, #ede3d0 100%);"
    "  border-radius: 8px; margin-bottom: 2em;"
    "}\n"
    ".cover h1 { border: none; font-size: 2.4em; color: #3d2b1f;"
    "            padding-bottom: 0; }\n"
    ".cover .subtitle { font-size: 1.3em; color: #5a3e28; margin: 0.5em 0 1.5em; }\n"
    ".cover .meta-tbl { width: auto; margin: 0 auto; border-collapse: collapse; }\n"
    ".cover .meta-tbl td { border: none; padding: 4px 16px; text-align: left; }\n"
    "\n"
    "/* Disclaimer */\n"
    ".disclaimer {"
    "  background: #fff8e8; border: 1px solid #f0d080;"
    "  border-left: 5px solid #e8a000; padding: 14px 18px;"
    "  margin: 2em 0; border-radius: 4px;"
    "  font-size: 0.95em; color: #6b5000;"
    "}\n"
    "\n"
    "/* Calc mode card */\n"
    ".calc-mode {"
    "  background: #f0f8ff; border: 1px solid #b8d8f0;"
    "  padding: 16px 20px; margin: 2em 0; border-radius: 6px; font-size: 0.92em;"
    "}\n"
    ".calc-mode h3 { color: #2060a0; margin-top: 0; border: none; padding: 0; }\n"
    ".calc-mode table { font-size: 0.93em; }\n"
    "\n"
    "/* Overview card */\n"
    ".overview {"
    "  background: #f5f0e8; border: 1px solid #d4c5b0;"
    "  padding: 16px 20px; margin: 2em 0; border-radius: 6px;"
    "}\n"
    ".overview h3 { color: #5a3e28; margin-top: 0; border: none; padding: 0; }\n"
    "\n"
    "/* TOC */\n"
    ".toc { background: #fafafa; border: 1px solid #ddd;"
    "       padding: 16px 24px; margin: 2em 0; border-radius: 6px; }\n"
    ".toc h3 { color: #444; margin-top: 0; border: none; padding: 0; }\n"
    ".toc ol { margin: 0.5em 0 0 0; }\n"
    "\n"
    "/* Footer */\n"
    ".footer { margin-top: 3em; font-size: 0.85em; color: #888;"
    "          text-align: center; padding: 20px 0; border-top: 1px solid #d4c5b0; }\n"
    "\n"
    "@media print {\n"
    "  body { max-width: 100%; margin: 0; padding: 0 20px; background: #fff; }\n"
    "  .cover { page-break-after: always; }\n"
    "  h2 { page-break-after: avoid; }\n"
    "  h3 { page-break-after: avoid; }\n"
    "  table { page-break-inside: avoid; }\n"
    "  blockquote { page-break-inside: avoid; }\n"
    "  .footer { page-break-before: avoid; }\n"
    "}\n"
)


def _h(s: str) -> str:
    """Minimal HTML-escape for user data embedded in HTML attributes/text."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _build_pre_body(meta: dict) -> str:
    m = {k: _h(str(v)) for k, v in meta.items()}
    cover = (
        '<div class="cover">'
        f'<h1>{_h(_cfg.BRAND_NAME)}</h1>'
        f'<div class="subtitle">{_h(_cfg.BRAND_TAGLINE)}</div>'
        '<table class="meta-tbl">'
        f'<tr><td><strong>姓名</strong></td><td>{m["name"]}</td></tr>'
        f'<tr><td><strong>出生日期</strong></td><td>{m["birth_date"]}</td></tr>'
        f'<tr><td><strong>出生時間</strong></td><td>{m["birth_time"]}</td></tr>'
        f'<tr><td><strong>出生地</strong></td><td>{m["location"]}</td></tr>'
        f'<tr><td><strong>產生時間</strong></td><td>{m["created_at"]}</td></tr>'
        f'<tr><td><strong>系統版本</strong></td><td>v{m["app_version"]}</td></tr>'
        '</table>'
        '</div>'
    )
    disclaimer = (
        '<div class="disclaimer">'
        f'<strong>⚠️ 免責聲明</strong><br>{m["disclaimer"]}'
        '</div>'
    )
    calc_mode = (
        '<div class="calc-mode">'
        '<h3>計算模式摘要</h3>'
        '<table>'
        '<tr><th>系統</th><th>計算模式</th><th>備注</th></tr>'
        f'<tr><td>西洋占星</td><td>{m["western_mode"]}</td><td>{m["western_note"]}</td></tr>'
        f'<tr><td>八字</td><td>{m["bazi_mode"]}</td><td>{m["bazi_note"]}</td></tr>'
        f'<tr><td>紫微</td><td>{m["ziwei_mode"]}</td><td>{m["ziwei_note"]}</td></tr>'
        f'<tr><td>紫微輔星</td><td>—</td><td>{m["ziwei_aux_note"]}</td></tr>'
        f'<tr><td>紫微大限</td><td>{m["daxian_accuracy"]}</td><td>—</td></tr>'
        '</table>'
        '</div>'
    )
    overview = (
        '<div class="overview">'
        '<h3>一頁式總覽</h3>'
        '<table>'
        '<tr><th>指標</th><th>數值</th><th>指標</th><th>數值</th></tr>'
        f'<tr><td>太陽星座</td><td>{m["sun_sign"]}</td><td>月亮星座</td><td>{m["moon_sign"]}</td></tr>'
        f'<tr><td>上升星座</td><td>{m["asc_sign"]}</td><td>天頂 MC</td><td>{m["mc_sign"]}</td></tr>'
        f'<tr><td>八字日主</td><td>{m["day_master"]}</td><td>喜用神</td><td>{m["fav_elements"]}</td></tr>'
        f'<tr><td>命宮主星</td><td>{m["ming_stars"]}</td><td>身宮</td><td>{m["shen_name"]}</td></tr>'
        f'<tr><td>五行局</td><td>{m["bureau"]}</td><td>生命靈數</td><td>{m["life_path"]}</td></tr>'
        f'<tr><td>血型</td><td>{m["blood_type"]}</td><td>—</td><td>—</td></tr>'
        '</table>'
        '</div>'
    )
    toc = (
        '<div class="toc">'
        '<h3>目錄</h3>'
        '<ol>'
        '<li>西洋占星分析</li>'
        '<li>八字命理分析</li>'
        '<li>紫微斗數分析</li>'
        '<li>血型分析</li>'
        '<li>生命靈數分析</li>'
        '<li>整合分析</li>'
        '<li>感情模式</li>'
        '<li>事業與職涯</li>'
        '<li>財富與資源</li>'
        '<li>人際關係</li>'
        '<li>壓力與陰影</li>'
        '<li>流年 / 三年趨勢</li>'
        '<li>行動建議</li>'
        '</ol>'
        '</div>'
    )
    return cover + disclaimer + calc_mode + overview + toc


class HtmlExporter:
    def export(self, report: FullReport, language: str = "zh-TW") -> str:
        from reports.localized_renderer import normalize_report_language, report_html_meta, report_text, render_localized_markdown
        language = normalize_report_language(language)
        meta = build_report_meta(report)
        markdown_text = (
            render_report(report, version=_cfg.APP_VERSION)
            if language == "zh-TW"
            else render_localized_markdown(report, language=language, version=_cfg.APP_VERSION)
        )

        if _MD_AVAILABLE:
            try:
                html_body = _md_lib.markdown(
                    markdown_text,
                    extensions=["tables", "fenced_code", "nl2br"],
                )
            except Exception:
                html_body = f"<pre>{_h(markdown_text)}</pre>"
        else:
            html_body = f"<pre>{_h(markdown_text)}</pre>"

        pre_body = _build_pre_body(meta)
        localized = report_text(language)
        title = _h(f"{meta['name']} — {localized['title']}")
        footer_txt = _h(f"{_cfg.REPORT_WATERMARK} · v{_cfg.APP_VERSION} ｜ {meta['created_at']}")

        return (
            '<!DOCTYPE html>\n'
            f'<html lang="{report_html_meta(language)["html_lang"]}" dir="{report_html_meta(language)["dir"]}">\n'
            '<head>\n'
            '  <meta charset="UTF-8" />\n'
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
            f'  <title>{title}</title>\n'
            '  <style>\n'
            + _CSS +
            '  </style>\n'
            '</head>\n'
            '<body>\n'
            + pre_body + '\n'
            + html_body + '\n'
            f'<div class="footer">{footer_txt}</div>\n'
            '</body>\n'
            '</html>\n'
        )

    def save(self, report: FullReport, path: str, language: str = "zh-TW") -> None:
        content = self.export(report, language=language)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
