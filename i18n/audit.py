"""Language audit utilities."""
import re

SCRIPT_RANGES = {
    "cjk": (0x4E00, 0x9FFF),
    "hiragana": (0x3040, 0x309F),
    "katakana": (0x30A0, 0x30FF),
    "thai": (0x0E00, 0x0E7F),
    "arabic": (0x0600, 0x06FF),
}

TECHNICAL_ALLOWLIST = {
    "Human Design", "Type", "Strategy", "Authority", "Profile",
    "Swiss Ephemeris", "Synastry", "Composite", "Markdown", "HTML",
    "Word", "PDF", "Email", "URL", "UTC", "IANA", "BaZi", "Zi Wei",
    "Astro Destiny Analyzer", "pyswisseph", "wkhtmltopdf",
}


def detect_scripts(text: str) -> set:
    scripts = set()
    for char in text:
        cp = ord(char)
        if SCRIPT_RANGES["cjk"][0] <= cp <= SCRIPT_RANGES["cjk"][1]:
            scripts.add("cjk")
        elif SCRIPT_RANGES["hiragana"][0] <= cp <= SCRIPT_RANGES["hiragana"][1]:
            scripts.add("hiragana")
        elif SCRIPT_RANGES["katakana"][0] <= cp <= SCRIPT_RANGES["katakana"][1]:
            scripts.add("katakana")
        elif SCRIPT_RANGES["thai"][0] <= cp <= SCRIPT_RANGES["thai"][1]:
            scripts.add("thai")
        elif SCRIPT_RANGES["arabic"][0] <= cp <= SCRIPT_RANGES["arabic"][1]:
            scripts.add("arabic")
        elif char.isalpha() and cp < 0x0250:
            scripts.add("latin")
        elif char.isdigit():
            scripts.add("digits")
    return scripts


def strip_allowlist(text: str) -> str:
    """Remove allowed technical terms before script detection."""
    result = text
    for term in sorted(TECHNICAL_ALLOWLIST, key=len, reverse=True):
        result = result.replace(term, " ")
    return result


def validate_render_language(text: str, language: str, allow_mixed_terms: bool = True) -> tuple:
    """
    Validate that rendered text is appropriate for the given language.
    Returns (is_valid, list_of_issues).
    For UI chrome validation — does NOT apply to long-form article body.
    """
    if allow_mixed_terms:
        clean = strip_allowlist(text)
    else:
        clean = text

    scripts = detect_scripts(clean)
    issues = []

    if language == "en":
        if "cjk" in scripts:
            issues.append(f"English UI should not contain CJK characters: {text[:80]!r}")
        if "thai" in scripts:
            issues.append(f"English UI should not contain Thai characters: {text[:80]!r}")
        if "arabic" in scripts:
            issues.append(f"English UI should not contain Arabic characters: {text[:80]!r}")
    elif language == "th":
        if "cjk" in scripts:
            issues.append(f"Thai UI should not contain CJK characters: {text[:80]!r}")
    elif language == "ja":
        if "cjk" in scripts and not ("hiragana" in scripts or "katakana" in scripts):
            # Pure CJK without any Japanese script is suspicious (might be Traditional Chinese)
            pass  # Japanese uses CJK too, can't easily distinguish
    elif language == "es":
        if "cjk" in scripts:
            issues.append(f"Spanish UI should not contain CJK characters: {text[:80]!r}")
        if "thai" in scripts:
            issues.append(f"Spanish UI should not contain Thai characters: {text[:80]!r}")
        if "arabic" in scripts:
            issues.append(f"Spanish UI should not contain Arabic characters: {text[:80]!r}")
    elif language == "ar":
        if "cjk" in scripts:
            issues.append(f"Arabic UI should not contain CJK characters: {text[:80]!r}")
        if "thai" in scripts:
            issues.append(f"Arabic UI should not contain Thai characters: {text[:80]!r}")

    return len(issues) == 0, issues
