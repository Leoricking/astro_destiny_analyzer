"""
V1.8.1 Tests: Windows encoding and UTF-8 output
"""
import os
import pytest


# ── 1–2. Encoding helper ──────────────────────────────────────────────────────

def test_encoding_utils_import_no_crash():
    """encoding_utils import 不 crash"""
    from scripts.encoding_utils import ensure_utf8_console  # noqa: F401


def test_ensure_utf8_console_no_crash():
    """ensure_utf8_console() 可執行不 crash"""
    from scripts.encoding_utils import ensure_utf8_console
    ensure_utf8_console()  # should not raise


# ── 3–5. run.bat encoding settings ───────────────────────────────────────────

@pytest.fixture(scope="module")
def run_bat_content():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bat_path = os.path.join(root, "run.bat")
    with open(bat_path, encoding="utf-8", errors="replace") as f:
        return f.read()


def test_run_bat_has_pythonutf8(run_bat_content):
    assert "PYTHONUTF8=1" in run_bat_content, "run.bat 應包含 PYTHONUTF8=1"


def test_run_bat_has_pythonioencoding(run_bat_content):
    assert "PYTHONIOENCODING=utf-8" in run_bat_content, "run.bat 應包含 PYTHONIOENCODING=utf-8"


def test_run_bat_has_chcp(run_bat_content):
    assert "chcp 65001" in run_bat_content, "run.bat 應包含 chcp 65001"


# ── 6. setup.bat encoding settings ───────────────────────────────────────────

def test_setup_bat_has_utf8_settings():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bat_path = os.path.join(root, "setup.bat")
    with open(bat_path, encoding="utf-8", errors="replace") as f:
        content = f.read()
    assert "PYTHONUTF8=1" in content, "setup.bat 應包含 PYTHONUTF8=1"
    assert "PYTHONIOENCODING=utf-8" in content, "setup.bat 應包含 PYTHONIOENCODING=utf-8"
    assert "chcp 65001" in content, "setup.bat 應包含 chcp 65001"


# ── 7. Chinese label strings are valid Python strings (not bytes garble) ──────

def test_chinese_labels_are_valid_strings():
    """互補良好、結構良好、進階西洋合盤 等中文標籤在 Python 內是合法字串"""
    from compatibility.advanced_astrology import (
        CONFLICT_CAPTION, COMPOSITE_INTRO, ADVANCED_SCORE_DISCLAIMER, SYNASTRY_INTRO,
        aspect_type_zh, category_zh,
    )
    labels = [
        CONFLICT_CAPTION, COMPOSITE_INTRO, ADVANCED_SCORE_DISCLAIMER, SYNASTRY_INTRO,
        "互補良好", "結構良好", "進階西洋合盤",
        aspect_type_zh("trine"),
        category_zh("emotional"),
    ]
    for lbl in labels:
        assert isinstance(lbl, str), f"標籤應為 str：{repr(lbl)}"
        assert len(lbl) > 0, "標籤不應為空字串"
        # Check it contains at least one CJK character
        assert any("\u4e00" <= ch <= "\u9fff" for ch in lbl), \
            f"標籤應包含中文字符：{repr(lbl)}"
