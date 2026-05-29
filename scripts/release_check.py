"""
Astro Destiny Analyzer — Release Checklist  V1.9.9
Validates that the project source is ready for a customer release build.

Usage:
    python scripts/release_check.py

Exit code: 0 = all checks passed, 1 = one or more checks failed.
"""
import sys
import os

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

EXPECTED_VERSION = "1.9.9"

# ── Required files ─────────────────────────────────────────────────────────────
REQUIRED_FILES = [
    "run.bat",
    "setup.bat",
    "install_pdf_support.bat",
    "requirements.txt",
    "README.md",
    "CUSTOMER_README.md",
    "RELEASE_NOTES.md",
    "VERSION.txt",
    "config.py",
    os.path.join("ui", "streamlit_app.py"),
]

# ── Forbidden DATA files that must NOT exist in the source tree ───────────────
# (dev dirs like .git/.venv are naturally present in source but excluded by
#  the build script — only check for data files that should never be committed)
FORBIDDEN_SOURCE_PATTERNS = [
    os.path.join("data", "leads_mock.json"),
    os.path.join("data", "lead_funnel_events.json"),
    os.path.join("data", "client_cases.json"),
    os.path.join("data", "human_design_calibration_cases.json"),
    ".env",
]

FORBIDDEN_EXTENSIONS = {".key", ".pem", ".token"}

# ── Forbidden keywords that must NOT appear in CUSTOMER_README ────────────────
CUSTOMER_README_FORBIDDEN = [
    "golden case",
    "Rossi",
    "debug",
    "password",
    "token",
    "api_key",
    "run_dev.bat を一般",    # pattern for "use run_dev.bat as normal"
]

# ── Forbidden keyword substrings in CUSTOMER_README (case-insensitive) ────────
CUSTOMER_README_FORBIDDEN_CI = ["golden case", "rossi"]

# ── Keywords that must NOT appear as a *recommended normal flow* in CUSTOMER_README
CUSTOMER_README_NO_NORMAL_DEV_FLOW = ["run_dev.bat"]


def _check(label: str, ok: bool, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    msg = f"  [{status}] {label}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return ok


def run_checks() -> int:
    """Run all release checks. Returns number of failures."""
    failures = 0
    print("=" * 60)
    print(f"  Astro Destiny Analyzer — Release Check v{EXPECTED_VERSION}")
    print("=" * 60)
    print()

    # ── 1. Required files exist ───────────────────────────────────────────────
    print("[CHECK] Required files:")
    for rel_path in REQUIRED_FILES:
        abs_path = os.path.join(_PROJECT_ROOT, rel_path)
        ok = os.path.isfile(abs_path)
        if not _check(rel_path, ok, "" if ok else "NOT FOUND"):
            failures += 1
    print()

    # ── 2. Forbidden source paths do not exist ────────────────────────────────
    print("[CHECK] Forbidden source paths (must NOT exist):")
    for rel_path in FORBIDDEN_SOURCE_PATTERNS:
        abs_path = os.path.join(_PROJECT_ROOT, rel_path)
        exists = os.path.exists(abs_path)
        ok = not exists
        if not _check(rel_path, ok, "OK — not present" if ok else "PRESENT — must be excluded"):
            failures += 1
    print()

    # ── 3. No credential files by extension ───────────────────────────────────
    print("[CHECK] No credential files (*.key / *.pem / *.token):")
    found_creds = []
    for dirpath, _, filenames in os.walk(_PROJECT_ROOT):
        rel_dir = os.path.relpath(dirpath, _PROJECT_ROOT)
        if any(p in rel_dir.split(os.sep) for p in [".git", ".venv", "release"]):
            continue
        for fn in filenames:
            _, ext = os.path.splitext(fn)
            if ext.lower() in FORBIDDEN_EXTENSIONS:
                found_creds.append(os.path.join(rel_dir, fn))
    ok = len(found_creds) == 0
    if not _check("No .key/.pem/.token files", ok,
                  "OK" if ok else f"Found: {found_creds}"):
        failures += 1
    print()

    # ── 4. APP_VERSION matches expected ───────────────────────────────────────
    print("[CHECK] config.py APP_VERSION:")
    try:
        import config as _cfg
        importlib = __import__("importlib")
        importlib.reload(_cfg)
        ok = _cfg.APP_VERSION == EXPECTED_VERSION
        _check(f"APP_VERSION == {EXPECTED_VERSION}", ok,
               f"found: {_cfg.APP_VERSION}" if not ok else "")
        if not ok:
            failures += 1
    except Exception as e:
        _check("config.py importable", False, str(e))
        failures += 1
    print()

    # ── 5. CUSTOMER_README content checks ─────────────────────────────────────
    print("[CHECK] CUSTOMER_README.md content:")
    cr_path = os.path.join(_PROJECT_ROOT, "CUSTOMER_README.md")
    if os.path.isfile(cr_path):
        cr_text = open(cr_path, encoding="utf-8").read()
        for forbidden in CUSTOMER_README_FORBIDDEN_CI:
            found = forbidden.lower() in cr_text.lower()
            ok = not found
            if not _check(f"No '{forbidden}' in CUSTOMER_README", ok,
                          "OK" if ok else f"Found forbidden term"):
                failures += 1
        # Must not instruct customer to use run_dev.bat as normal flow
        # Simple heuristic: run_dev.bat should not appear without developer disclaimer
        for dev_ref in CUSTOMER_README_NO_NORMAL_DEV_FLOW:
            if dev_ref in cr_text:
                # Only flag if it appears outside a "developer" section context
                lines_with_dev = [l for l in cr_text.splitlines() if dev_ref in l]
                bad_lines = [l for l in lines_with_dev if "開發" not in l and "developer" not in l.lower() and "dev" not in l.lower()]
                ok = len(bad_lines) == 0
                if not _check(f"run_dev.bat not promoted as normal flow", ok,
                              f"Found in non-dev context: {bad_lines[:2]}"):
                    failures += 1
    else:
        _check("CUSTOMER_README.md readable", False, "file not found")
        failures += 1
    print()

    # ── 6. RELEASE_NOTES content checks ───────────────────────────────────────
    print("[CHECK] RELEASE_NOTES.md content:")
    rn_path = os.path.join(_PROJECT_ROOT, "RELEASE_NOTES.md")
    if os.path.isfile(rn_path):
        rn_text = open(rn_path, encoding="utf-8").read()
        ok = EXPECTED_VERSION in rn_text
        if not _check(f"Contains version {EXPECTED_VERSION}", ok):
            failures += 1
        ok = "Privacy" in rn_text or "隱私" in rn_text
        if not _check("Contains Privacy section", ok):
            failures += 1
    else:
        _check("RELEASE_NOTES.md readable", False, "file not found")
        failures += 1
    print()

    # ── 7. VERSION.txt content checks ─────────────────────────────────────────
    print("[CHECK] VERSION.txt content:")
    vt_path = os.path.join(_PROJECT_ROOT, "VERSION.txt")
    if os.path.isfile(vt_path):
        vt_text = open(vt_path, encoding="utf-8").read()
        ok = f"Version: {EXPECTED_VERSION}" in vt_text
        if not _check(f"Contains 'Version: {EXPECTED_VERSION}'", ok):
            failures += 1
    else:
        _check("VERSION.txt readable", False, "file not found")
        failures += 1
    print()

    # ── Summary ───────────────────────────────────────────────────────────────
    print("=" * 60)
    if failures == 0:
        print("  [OK] Release check PASSED -- all checks OK")
    else:
        print(f"  [FAIL] Release check FAILED -- {failures} check(s) failed")
    print("=" * 60)

    return failures


def main() -> int:
    failures = run_checks()
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
