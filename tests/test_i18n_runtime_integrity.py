"""Runtime language integrity tests."""
import pytest
from i18n.audit import detect_scripts, validate_render_language, strip_allowlist
from i18n.translator import get_translation, SUPPORTED_LANGUAGES


ALL_NAV_KEYS = [
    "nav.home", "nav.public_content", "nav.free_report", "nav.input",
    "nav.calculate", "nav.report_preview", "nav.history", "nav.export",
    "nav.compatibility", "nav.settings",
]

ALL_BUTTON_KEYS = [
    "input.submit", "input.clear", "calculate.btn_start", "calculate.btn_recalc",
    "home.btn_start_chart", "compatibility.generate",
]


@pytest.mark.parametrize("key", ALL_NAV_KEYS)
def test_en_nav_no_cjk(key):
    val = get_translation("en", key)
    clean = strip_allowlist(val)
    scripts = detect_scripts(clean)
    assert "cjk" not in scripts, f"English nav {key!r} contains CJK: {val!r}"

@pytest.mark.parametrize("key", ALL_NAV_KEYS)
def test_th_nav_no_cjk(key):
    val = get_translation("th", key)
    clean = strip_allowlist(val)
    scripts = detect_scripts(clean)
    assert "cjk" not in scripts, f"Thai nav {key!r} contains CJK: {val!r}"

@pytest.mark.parametrize("key", ALL_NAV_KEYS)
def test_es_nav_no_cjk(key):
    val = get_translation("es", key)
    clean = strip_allowlist(val)
    scripts = detect_scripts(clean)
    assert "cjk" not in scripts, f"Spanish nav {key!r} contains CJK: {val!r}"

@pytest.mark.parametrize("key", ALL_NAV_KEYS)
def test_ar_nav_no_cjk(key):
    val = get_translation("ar", key)
    clean = strip_allowlist(val)
    scripts = detect_scripts(clean)
    assert "cjk" not in scripts, f"Arabic nav {key!r} contains CJK: {val!r}"

@pytest.mark.parametrize("key", ALL_BUTTON_KEYS)
def test_en_buttons_no_cjk(key):
    val = get_translation("en", key)
    clean = strip_allowlist(val)
    assert "cjk" not in detect_scripts(clean), f"English button {key!r} has CJK: {val!r}"

@pytest.mark.parametrize("key", ALL_BUTTON_KEYS)
def test_th_buttons_no_cjk(key):
    val = get_translation("th", key)
    clean = strip_allowlist(val)
    assert "cjk" not in detect_scripts(clean), f"Thai button {key!r} has CJK: {val!r}"

def test_technical_allowlist_not_flagged():
    val = "Swiss Ephemeris with Human Design"
    is_valid, issues = validate_render_language(val, "en")
    assert is_valid, f"Allowlist terms should not be flagged: {issues}"

def test_zh_tw_cjk_is_valid():
    val = "命盤整合分析"
    is_valid, _ = validate_render_language(val, "zh-TW")
    assert is_valid  # CJK is fine for zh-TW

def test_render_registry_pages_have_keys():
    from i18n.render_registry import get_all_registered_pages, get_page_keys
    pages = get_all_registered_pages()
    assert len(pages) > 0
    for page in pages:
        keys = get_page_keys(page)
        assert len(keys) > 0

def test_render_registry_coverage_zh_tw():
    from i18n.render_registry import verify_page_coverage
    for page in ["home", "input", "calculate"]:
        coverage, missing = verify_page_coverage(page, "zh-TW")
        assert coverage == 1.0, f"Page {page!r} missing zh-TW keys: {missing}"

def test_render_registry_coverage_en():
    from i18n.render_registry import verify_page_coverage
    for page in ["home", "input", "calculate"]:
        coverage, missing = verify_page_coverage(page, "en")
        assert coverage == 1.0, f"Page {page!r} missing en keys: {missing}"

def test_six_languages_all_have_nav_keys():
    for lang in SUPPORTED_LANGUAGES:
        for key in ALL_NAV_KEYS:
            val = get_translation(lang, key)
            assert val != key, f"Language {lang!r} missing key {key!r}"
