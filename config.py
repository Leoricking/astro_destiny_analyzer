"""
Astro Destiny Analyzer — Global Configuration
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "astro_destiny.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)

APP_NAME = "Astro Destiny Analyzer"
APP_VERSION = "1.0.0"
APP_SUBTITLE = "命盤整合分析系統"

DISCLAIMER_ZH = """
本系統定位為「自我探索與娛樂型命盤分析工具」。
所有分析結果僅供參考，不構成科學定論、醫療診斷、投資建議或絕對命運預測。
請以開放、探索的心態閱讀本報告，最終決策仍以您自身判斷為準。
"""

# Report settings
REPORT_SHORT_WORD_TARGET = 800
REPORT_STANDARD_WORD_TARGET = 3000
REPORT_FULL_WORD_TARGET = 10000

# Supported languages
SUPPORTED_LANGUAGES = ["繁體中文", "簡體中文", "English"]

# Swiss Ephemeris data path (optional; leave empty to use mock engine)
SWISSEPH_DATA_PATH = os.environ.get("SWISSEPH_DATA_PATH", "")
