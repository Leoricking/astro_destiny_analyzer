"""
Astro Destiny Analyzer — Release Smoke Test  V2.0.2
Static ZIP smoke test: verifies a release ZIP contains required files
and does NOT contain forbidden entries.

Usage:
    python scripts/release_smoke_test.py --zip path/to/release.zip --profile customer

Exit code: 0 = PASS, 1 = FAIL.
"""
import sys
import os
import zipfile
import argparse

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

EXPECTED_VERSION = "2.0.3"

# ── Required files (customer profile) ─────────────────────────────────────────
REQUIRED_FILES_CUSTOMER = [
    "run.bat",
    "setup.bat",
    "install_pdf_support.bat",
    "CUSTOMER_README.md",
    "CUSTOMER_ONBOARDING.md",
    "VERSION.txt",
    "RELEASE_NOTES.md",
    "requirements.txt",
    "config.py",
    "ui/streamlit_app.py",
]

# ── Required files (consultant profile) ───────────────────────────────────────
REQUIRED_FILES_CONSULTANT = [
    "run.bat",
    "run_consultant.bat",
    "setup.bat",
    "install_pdf_support.bat",
    "CUSTOMER_README.md",
    "CUSTOMER_ONBOARDING.md",
    "VERSION.txt",
    "RELEASE_NOTES.md",
    "requirements.txt",
    "config.py",
    "ui/streamlit_app.py",
]

# ── Forbidden ZIP entries (all profiles) ──────────────────────────────────────
FORBIDDEN_ENTRIES_ALL = [
    ".git",
    ".venv",
    "data/leads_mock.json",
    "data/lead_funnel_events.json",
    "data/client_cases.json",
    "data/human_design_calibration_cases.json",
    ".env",
    "rossi",
]

# ── Additional forbidden entries for customer profile ─────────────────────────
FORBIDDEN_ENTRIES_CUSTOMER_EXTRA = [
    "run_dev.bat",
    "tests/",
    "tests\\",
]

# ── Forbidden keywords in CUSTOMER_README ─────────────────────────────────────
CUSTOMER_README_FORBIDDEN_CI = ["golden case", "rossi", "debug", "calibration"]


def _get_required_files(profile: str) -> list:
    if profile == "consultant":
        return REQUIRED_FILES_CONSULTANT
    return REQUIRED_FILES_CUSTOMER


def _get_forbidden_entries(profile: str) -> list:
    entries = list(FORBIDDEN_ENTRIES_ALL)
    if profile == "customer":
        entries += FORBIDDEN_ENTRIES_CUSTOMER_EXTRA
    return entries


def _is_forbidden_entry(arc_name: str, profile: str) -> bool:
    """Return True if a ZIP entry name matches any forbidden pattern."""
    normalized = arc_name.replace("\\", "/").lower()
    parts = normalized.split("/")
    for forbidden in _get_forbidden_entries(profile):
        fl = forbidden.lower().replace("\\", "/")
        # Dot-prefixed path components (e.g. ".git") match as exact components
        if fl.startswith(".") and not fl.endswith("/"):
            if fl in parts:
                return True
        else:
            if fl in normalized:
                return True
    return False


def _result(label: str, ok: bool, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    msg = f"  [{status}] {label}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return ok


def run_smoke_test(zip_path: str, profile: str = "customer") -> int:
    """
    Run smoke test against the given ZIP file.
    Returns number of failures (0 = PASS).
    """
    failures = 0

    print("=" * 60)
    print(f"  Astro Destiny Analyzer — Release Smoke Test v{EXPECTED_VERSION}")
    print(f"  ZIP    : {zip_path}")
    print(f"  Profile: {profile}")
    print("=" * 60)
    print()

    # ── 1. ZIP exists ─────────────────────────────────────────────────────────
    print("[CHECK] ZIP file:")
    ok = os.path.isfile(zip_path)
    if not _result("ZIP file exists", ok, "" if ok else "NOT FOUND"):
        failures += 1
        print()
        print("=" * 60)
        print("  [FAIL] Smoke test FAILED — ZIP not found")
        print("=" * 60)
        return failures

    ok = os.path.getsize(zip_path) > 0
    if not _result("ZIP file is non-empty", ok):
        failures += 1
    print()

    # ── 2. ZIP is readable ────────────────────────────────────────────────────
    print("[CHECK] ZIP integrity:")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            bad = zf.testzip()
            ok = bad is None
            if not _result("ZIP integrity check (testzip)", ok,
                           "OK" if ok else f"Bad file: {bad}"):
                failures += 1
    except Exception as exc:
        _result("ZIP readable", False, str(exc))
        failures += 1
        print()
        print("=" * 60)
        print("  [FAIL] Smoke test FAILED — ZIP unreadable")
        print("=" * 60)
        return failures
    print()

    # ── 3. Required files present ─────────────────────────────────────────────
    print("[CHECK] Required files in ZIP:")
    required = _get_required_files(profile)
    # Normalize zip names to forward-slash, strip leading folder component
    # ZIP entries may have a top-level folder prefix (e.g. astro_destiny_analyzer_v2.0.2_customer/)
    normalized_names = [n.replace("\\", "/") for n in names]

    def _zip_contains(rel_path: str) -> bool:
        rp = rel_path.replace("\\", "/").lower()
        for n in normalized_names:
            nl = n.lower()
            # Exact match or suffix match (handles top-level folder prefix)
            if nl == rp or nl.endswith("/" + rp):
                return True
        return False

    for req in required:
        ok = _zip_contains(req)
        if not _result(req, ok, "" if ok else "MISSING"):
            failures += 1
    print()

    # ── 4. Forbidden entries absent ───────────────────────────────────────────
    print("[CHECK] Forbidden entries absent from ZIP:")
    found_forbidden = []
    for arc_name in names:
        if _is_forbidden_entry(arc_name, profile):
            found_forbidden.append(arc_name)

    if found_forbidden:
        for entry in found_forbidden[:10]:
            _result(f"Absent: {entry}", False, "FOUND — must not be included")
            failures += 1
    else:
        _result("No forbidden entries found", True)
    print()

    # ── 5. VERSION.txt content ────────────────────────────────────────────────
    print("[CHECK] VERSION.txt content:")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            version_entries = [n for n in names if n.lower().endswith("version.txt")]
            if version_entries:
                content = zf.read(version_entries[0]).decode("utf-8", errors="replace")
                ok = EXPECTED_VERSION in content
                if not _result(f"VERSION.txt contains {EXPECTED_VERSION}", ok,
                               "" if ok else f"content: {content[:80]}"):
                    failures += 1
            else:
                _result("VERSION.txt found in ZIP", False, "NOT FOUND")
                failures += 1
    except Exception as exc:
        _result("VERSION.txt readable", False, str(exc))
        failures += 1
    print()

    # ── 6. CUSTOMER_README forbidden words ────────────────────────────────────
    print("[CHECK] CUSTOMER_README.md content:")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            cr_entries = [n for n in names if n.lower().endswith("customer_readme.md")]
            if cr_entries:
                cr_text = zf.read(cr_entries[0]).decode("utf-8", errors="replace")
                for forbidden in CUSTOMER_README_FORBIDDEN_CI:
                    found = forbidden.lower() in cr_text.lower()
                    ok = not found
                    if not _result(f"No '{forbidden}' in CUSTOMER_README", ok,
                                   "OK" if ok else "Found forbidden term"):
                        failures += 1
            else:
                _result("CUSTOMER_README.md found in ZIP", False, "NOT FOUND")
                failures += 1
    except Exception as exc:
        _result("CUSTOMER_README.md readable", False, str(exc))
        failures += 1
    print()

    # ── 7. Optional demo import fallback in streamlit_app.py ──────────────────
    print("[CHECK] Optional demo import fallback (streamlit_app.py):")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            app_entries = [n for n in names if n.lower().endswith("ui/streamlit_app.py")
                           or n.lower().endswith("ui\\streamlit_app.py")]
            if app_entries:
                app_text = zf.read(app_entries[0]).decode("utf-8", errors="replace")
                ok = "except ModuleNotFoundError" in app_text or "except ImportError" in app_text
                if not _result("Has demo import exception handler", ok,
                               "OK" if ok else "Missing except handler for demo import"):
                    failures += 1
                ok = "SAMPLE_PROFILES = {}" in app_text
                if not _result("Has SAMPLE_PROFILES = {} fallback", ok):
                    failures += 1
                ok = "SAMPLE_LABELS = {}" in app_text
                if not _result("Has SAMPLE_LABELS = {} fallback", ok):
                    failures += 1
                ok = "SAMPLE_COUPLES = {}" in app_text
                if not _result("Has SAMPLE_COUPLES = {} fallback", ok):
                    failures += 1
                # Ensure demo sections are guarded (not raw unconditional access)
                ok = "SAMPLE_PROFILES:" in app_text or "SAMPLE_COUPLES:" in app_text
                if not _result("Demo sections guarded by SAMPLE_PROFILES/SAMPLE_COUPLES", ok):
                    failures += 1
            else:
                _result("ui/streamlit_app.py found in ZIP", False, "NOT FOUND")
                failures += 1
    except Exception as exc:
        _result("streamlit_app.py readable", False, str(exc))
        failures += 1
    print()

    # ── Summary ───────────────────────────────────────────────────────────────
    print("=" * 60)
    if failures == 0:
        print(f"  [PASS] Smoke test PASSED — all checks OK (profile: {profile})")
    else:
        print(f"  [FAIL] Smoke test FAILED — {failures} check(s) failed (profile: {profile})")
    print("=" * 60)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Astro Destiny Analyzer Release Smoke Test"
    )
    parser.add_argument(
        "--zip",
        required=True,
        help="Path to the release ZIP file to test",
        dest="zip_path",
    )
    parser.add_argument(
        "--profile",
        choices=["customer", "consultant", "developer"],
        default="customer",
        help="Release profile: customer (default) | consultant | developer",
    )
    args = parser.parse_args()
    failures = run_smoke_test(zip_path=args.zip_path, profile=args.profile)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
