"""
Astro Destiny Analyzer — Release Checklist  V2.0.3
Validates that the project source is ready for a customer release build.

Usage:
    python scripts/release_check.py [--profile customer|consultant|developer]

Exit code: 0 = all checks passed, 1 = one or more checks failed.
"""
import sys
import os
import argparse

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

EXPECTED_VERSION = "2.0.3"

# ── Required files (all profiles) ─────────────────────────────────────────────
REQUIRED_FILES = [
    "run.bat",
    "setup.bat",
    "install_pdf_support.bat",
    "requirements.txt",
    "README.md",
    "CUSTOMER_README.md",
    "CUSTOMER_ONBOARDING.md",
    "RELEASE_NOTES.md",
    "RELEASE_QA_CHECKLIST.md",
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

# ── Profile-specific checks ───────────────────────────────────────────────────
CUSTOMER_PROFILE_FORBIDDEN_FILES = ["run_dev.bat", "tests"]
CUSTOMER_PROFILE_FORBIDDEN_CONTENT = ["run_dev.bat"]


def _check(label: str, ok: bool, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    msg = f"  [{status}] {label}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return ok


def run_checks(profile: str = "customer") -> int:
    """Run all release checks. Returns number of failures."""
    failures = 0
    print("=" * 60)
    print(f"  Astro Destiny Analyzer — Release Check v{EXPECTED_VERSION}")
    print(f"  Profile: {profile}")
    print("=" * 60)
    print()

    # ── 1. Required files exist ───────────────────────────────────────────────
    print("[CHECK] Required files:")
    required = list(REQUIRED_FILES)
    if profile in ("consultant", "developer"):
        required.append("run_consultant.bat")
    for rel_path in required:
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
        if any(p in rel_dir.split(os.sep) for p in [".git", ".venv", "release", "dist", "build"]):
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

    # ── 5b. CUSTOMER_ONBOARDING.md content checks ─────────────────────────────
    print("[CHECK] CUSTOMER_ONBOARDING.md content:")
    co_path = os.path.join(_PROJECT_ROOT, "CUSTOMER_ONBOARDING.md")
    if os.path.isfile(co_path):
        co_text = open(co_path, encoding="utf-8").read()
        for forbidden in ["run_dev.bat", "Rossi", "golden case", "debug", "calibration"]:
            found = forbidden.lower() in co_text.lower()
            ok = not found
            if not _check(f"No '{forbidden}' in CUSTOMER_ONBOARDING", ok,
                          "OK" if ok else "Found forbidden term"):
                failures += 1
        ok = "setup.bat" in co_text
        if not _check("Contains setup.bat", ok):
            failures += 1
        ok = "run.bat" in co_text
        if not _check("Contains run.bat", ok):
            failures += 1
    else:
        _check("CUSTOMER_ONBOARDING.md readable", False, "file not found")
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
        ok = "Privacy" in rn_text or "\u96b1\u79c1" in rn_text
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

    # ── 7b. Optional demo import check ────────────────────────────────────────
    print("[CHECK] streamlit_app.py optional demo import:")
    app_path = os.path.join(_PROJECT_ROOT, "ui", "streamlit_app.py")
    if os.path.isfile(app_path):
        app_text = open(app_path, encoding="utf-8").read()
        ok = ("except ModuleNotFoundError" in app_text or "except ImportError" in app_text)
        if not _check("demo import has exception fallback", ok,
                      "OK" if ok else "Missing except handler — will crash in customer/consultant release"):
            failures += 1
        ok = "SAMPLE_PROFILES = {}" in app_text
        if not _check("SAMPLE_PROFILES = {} fallback present", ok):
            failures += 1
        ok = "SAMPLE_COUPLES = {}" in app_text
        if not _check("SAMPLE_COUPLES = {} fallback present", ok):
            failures += 1
    else:
        _check("ui/streamlit_app.py readable", False, "file not found")
        failures += 1
    print()

    # ── 8. Profile-specific checks ────────────────────────────────────────────
    print(f"[CHECK] Profile-specific checks ({profile}):")
    if profile == "customer":
        # run.bat must have customer flags
        run_bat = os.path.join(_PROJECT_ROOT, "run.bat")
        if os.path.isfile(run_bat):
            rb_text = open(run_bat, encoding="utf-8").read()
            ok = "ASTRO_CUSTOMER_MODE=1" in rb_text
            if not _check("run.bat has ASTRO_CUSTOMER_MODE=1", ok):
                failures += 1
            ok = "ASTRO_BUILD_PROFILE=customer" in rb_text
            if not _check("run.bat has ASTRO_BUILD_PROFILE=customer", ok):
                failures += 1
            ok = "ASTRO_DEVELOPER_MODE=1" not in rb_text
            if not _check("run.bat does not set DEVELOPER_MODE=1", ok):
                failures += 1
        else:
            _check("run.bat readable", False, "file not found")
            failures += 1
    elif profile == "consultant":
        # run_consultant.bat must have consultant flags
        rc_bat = os.path.join(_PROJECT_ROOT, "run_consultant.bat")
        if os.path.isfile(rc_bat):
            rc_text = open(rc_bat, encoding="utf-8").read()
            ok = "ASTRO_CONSULTANT_MODE=1" in rc_text
            if not _check("run_consultant.bat has ASTRO_CONSULTANT_MODE=1", ok):
                failures += 1
            ok = "ASTRO_BUILD_PROFILE=consultant" in rc_text
            if not _check("run_consultant.bat has ASTRO_BUILD_PROFILE=consultant", ok):
                failures += 1
        else:
            _check("run_consultant.bat readable", False, "file not found")
            failures += 1
    elif profile == "developer":
        # run_dev.bat must have developer flags
        rd_bat = os.path.join(_PROJECT_ROOT, "run_dev.bat")
        if os.path.isfile(rd_bat):
            rd_text = open(rd_bat, encoding="utf-8").read()
            ok = "ASTRO_DEVELOPER_MODE=1" in rd_text
            if not _check("run_dev.bat has ASTRO_DEVELOPER_MODE=1", ok):
                failures += 1
            ok = "ASTRO_BUILD_PROFILE=developer" in rd_text
            if not _check("run_dev.bat has ASTRO_BUILD_PROFILE=developer", ok):
                failures += 1
        else:
            _check("run_dev.bat readable", False, "file not found")
            failures += 1
    elif profile == "protected_trial":
        # Protected trial: verify all required scripts and docs exist
        for required_file in [
            os.path.join("scripts", "build_protected.py"),
            os.path.join("scripts", "protected_smoke_test.py"),
            "app_launcher.py",
            "start_protected.bat",
        ]:
            abs_p = os.path.join(_PROJECT_ROOT, required_file)
            ok = os.path.isfile(abs_p)
            if not _check(required_file, ok, "" if ok else "NOT FOUND"):
                failures += 1
        # Verify build_protected.py excludes source .py, tests, demo, private data
        bp_path = os.path.join(_PROJECT_ROOT, "scripts", "build_protected.py")
        if os.path.isfile(bp_path):
            bp_text = open(bp_path, encoding="utf-8").read()
            for must_have in [".py", "tests", "demo", "run_dev.bat", "run_consultant.bat",
                               "leads_mock", "rossi"]:
                ok = must_have.lower() in bp_text.lower()
                if not _check(f"build_protected.py references '{must_have}'", ok):
                    failures += 1
        # Verify start_protected.bat does not call run_dev or run_consultant
        sp_path = os.path.join(_PROJECT_ROOT, "start_protected.bat")
        if os.path.isfile(sp_path):
            sp_text = open(sp_path, encoding="utf-8").read()
            for forbidden in ["run_dev.bat", "run_consultant.bat"]:
                ok = forbidden not in sp_text
                if not _check(f"start_protected.bat does not call {forbidden}", ok):
                    failures += 1
    print()

    # ── Summary ───────────────────────────────────────────────────────────────
    print("=" * 60)
    if failures == 0:
        print(f"  [OK] Release check PASSED -- all checks OK (profile: {profile})")
    else:
        print(f"  [FAIL] Release check FAILED -- {failures} check(s) failed (profile: {profile})")
    print("=" * 60)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Astro Destiny Analyzer Release Checker")
    parser.add_argument(
        "--profile",
        choices=["customer", "consultant", "developer", "protected_trial"],
        default="customer",
        help="Release profile: customer (default) | consultant | developer | protected_trial",
    )
    args = parser.parse_args()
    failures = run_checks(profile=args.profile)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
