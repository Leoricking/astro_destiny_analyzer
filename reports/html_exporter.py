"""
Astro Destiny Analyzer — HTML Exporter
Converts Markdown to a self-contained HTML document.
"""
import markdown as md_lib
from core.models import FullReport
from reports.templates import render_report
from config import APP_VERSION, APP_NAME

_HTML_WRAP = """\
<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    body {{
      font-family: "Noto Serif TC", "Georgia", serif;
      max-width: 860px;
      margin: 40px auto;
      padding: 0 24px;
      color: #222;
      line-height: 1.8;
      background: #faf9f7;
    }}
    h1 {{ color: #3d2b1f; border-bottom: 2px solid #c9a96e; padding-bottom: 8px; }}
    h2 {{ color: #5a3e28; border-left: 4px solid #c9a96e; padding-left: 12px; margin-top: 2em; }}
    h3 {{ color: #7a5c40; margin-top: 1.5em; }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
    th, td {{ border: 1px solid #d4c5b0; padding: 8px 12px; text-align: left; }}
    th {{ background: #f0e8d8; }}
    blockquote {{ border-left: 4px solid #c9a96e; margin: 16px 0;
                  padding: 8px 16px; background: #f5f0e8; color: #555; }}
    code {{ background: #eee; padding: 2px 6px; border-radius: 3px; }}
    hr {{ border: none; border-top: 1px solid #d4c5b0; margin: 2em 0; }}
    .footer {{ margin-top: 3em; font-size: 0.85em; color: #888; text-align: center; }}
  </style>
</head>
<body>
{body}
<div class="footer">{app_name} v{version}</div>
</body>
</html>
"""


class HtmlExporter:
    def export(self, report: FullReport) -> str:
        markdown_text = render_report(report, version=APP_VERSION)
        html_body = md_lib.markdown(
            markdown_text,
            extensions=["tables", "fenced_code", "nl2br"],
        )
        title = f"{report.profile.name} 命盤分析報告"
        return _HTML_WRAP.format(
            title=title,
            body=html_body,
            app_name=APP_NAME,
            version=APP_VERSION,
        )

    def save(self, report: FullReport, path: str) -> None:
        content = self.export(report)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
