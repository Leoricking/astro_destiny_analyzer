"""
Astro Destiny Analyzer — Protected Trial Smoke Test  V2.0.3
Static ZIP smoke test for the protected trial build.
Verifies required files are present and no forbidden entries exist.

Usage:
    python scripts/protected_smoke_test.py --zip release/astro_destiny_analyzer_v2.0.3_protected_trial.zip

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

# ── Required files in the protected ZIP ───────────────────────────────────────
REQUIRED_FILES_PROTECTED = [
    "CUSTOMER_README.md",
    "TRIAL_README.txt",
    "VERSION.txt",
    "RELEASE_NOTES.md",
]

# At least one of these must be present (exe OR launcher bat)
REQUIRED_EXECUTABLE_ANY = [
    "AstroDestinyAnalyzer.exe",
    "start_protected.bat",
]

# ── Forbidden entries (all must be absent) ────────────────────────────────────
FORBIDDEN_ENTRIES_PROTECTED = [
    ".git",
    ".venv",
    "run_dev.bat",
    "run_consultant.bat",
    "tests/",
    "tests\\",
    "demo/",
    "demo\\",
    "data/leads_mock.json",
    "data/client_cases.json",
    "data/lead_funnel_events.json",
    "data/human_design_calibration_cases.json",
    ".env",
    "rossi",
]


def _is_internal_path(normalized: str) -> bool:
    """Return True if the path is inside a PyInstaller _internal/ bundle."""
    # Matches: _internal/... or AnyFolder/_internal/...
    parts = normalized.split("/")
    return "_internal" in parts


def _is_forbidden_entry(arc_name: str) -> bool:
    """Return True if a ZIP entry matches any forbidden pattern."""
    normalized = arc_name.replace("\\", "/").lower()
    parts = normalized.split("/")
    for forbidden in FORBIDDEN_ENTRIES_PROTECTED:
        fl = forbidden.lower().replace("\\", "/")
        if fl.startswith(".") and not fl.endswith("/"):
            # Dot-prefixed components (e.g. ".git", ".venv") — match as exact part
            if fl in parts:
                return True
        elif fl.endswith("/"):
            # Directory patterns (e.g. "tests/", "demo/") — only flag outside _internal/
            if _is_internal_path(normalized):
                continue
            if fl in normalized:
                return True
        else:
            # Substring patterns — skip if inside _internal/
            if _is_internal_path(normalized):
                # Still check truly sensitive items even inside _internal/
                if fl in ("rossi",):
                    if fl in normalized:
                        return True
                continue
            if fl in normalized:
                return True
    return False


def _is_py_source_outside_internal(arc_name: str) -> bool:
    """Return True if the entry is a .py file outside the _internal/ bundle."""
    normalized = arc_name.replace("\\", "/").lower()
    if not normalized.endswith(".py"):
        return False
    # Allow .py inside PyInstaller's _internal/ folder (compiled bundle)
    if "/_internal/" in normalized or normalized.startswith("_internal/"):
        return False
    # Allow .py inside the named dist folder's _internal/
    parts = normalized.split("/")
    if len(parts) >= 2 and parts[1] == "_internal":
        return False
    return True


def _result(label: str, ok: bool, detail: str = "") -> bool:
    status = "PASS" if ok else "FAIL"
    msg = f"  [{status}] {label}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return ok


def run_smoke_test(zip_path: str) -> int:
    """Run protected smoke test. Returns number of failures (0 = PASS)."""
    failures = 0

    print("=" * 60)
    print(f"  Astro Destiny Analyzer — Protected Smoke Test v{EXPECTED_VERSION}")
    print(f"  ZIP    : {zip_path}")
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

    # ── 2. ZIP readable / integrity ───────────────────────────────────────────
    print("[CHECK] ZIP integrity:")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            bad = zf.testzip()
            ok = bad is None
            if not _result("ZIP integrity (testzip)", ok,
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

    normalized_names = [n.replace("\\", "/") for n in names]

    def _zip_contains(rel_path: str) -> bool:
        rp = rel_path.replace("\\", "/").lower()
        for n in normalized_names:
            nl = n.lower()
            if nl == rp or nl.endswith("/" + rp):
                return True
        return False

    # ── 3. Required executable present ───────────────────────────────────────
    print("[CHECK] Executable or launcher:")
    has_executable = any(_zip_contains(e) for e in REQUIRED_EXECUTABLE_ANY)
    if not _result(
        "AstroDestinyAnalyzer.exe or start_protected.bat present",
        has_executable,
        "" if has_executable else "MISSING — neither .exe nor start_protected.bat found",
    ):
        failures += 1
    print()

    # ── 4. Required docs present ──────────────────────────────────────────────
    print("[CHECK] Required documentation files:")
    for req in REQUIRED_FILES_PROTECTED:
        ok = _zip_contains(req)
        if not _result(req, ok, "" if ok else "MISSING"):
            failures += 1
    print()

    # ── 5. No .py source files outside _internal/ ─────────────────────────────
    print("[CHECK] No .py source files exposed at top level:")
    exposed_py = [n for n in names if _is_py_source_outside_internal(n)]
    ok = len(exposed_py) == 0
    if not _result(
        "No .py source files outside _internal/",
        ok,
        "OK" if ok else f"Found: {exposed_py[:5]}",
    ):
        failures += 1
    print()

    # ── 6. Forbidden entries absent ───────────────────────────────────────────
    print("[CHECK] Forbidden entries absent:")
    found_forbidden = [n for n in names if _is_forbidden_entry(n)]
    if found_forbidden:
        for entry in found_forbidden[:10]:
            _result(f"Absent: {entry}", False, "FOUND — must not be included")
            failures += 1
    else:
        _result("No forbidden entries found", True)
    print()

    # ── 7. tests/ absent (excluding _internal/ which may have library tests) ──
    print("[CHECK] No tests/ directory outside _internal/:")
    has_tests = any(
        "tests/" in n.replace("\\", "/").lower()
        and not _is_internal_path(n.replace("\\", "/").lower())
        for n in names
    )
    if not _result("tests/ absent outside _internal/", not has_tests,
                   "OK" if not has_tests else "FOUND — must not be included"):
        failures += 1
    print()

    # ── 8. demo/ absent ──────────────────────────────────────────────────────
    print("[CHECK] No demo/ directory:")
    has_demo = any(
        "demo/" in n.replace("\\", "/").lower()
        and not _is_internal_path(n.replace("\\", "/").lower())
        for n in names
    )
    if not _result("demo/ absent", not has_demo,
                   "OK" if not has_demo else "FOUND — must not be included"):
        failures += 1
    print()

    # ── 9. VERSION.txt content ────────────────────────────────────────────────
    print("[CHECK] VERSION.txt content:")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            ver_entries = [n for n in names if n.lower().endswith("version.txt")]
            if ver_entries:
                content = zf.read(ver_entries[0]).decode("utf-8", errors="replace")
                ok = EXPECTED_VERSION in content
                if not _result(f"VERSION.txt contains {EXPECTED_VERSION}", ok,
                               "" if ok else f"content: {content[:80]}"):
                    failures += 1
            else:
                _result("VERSION.txt found", False, "NOT FOUND")
                failures += 1
    except Exception as exc:
        _result("VERSION.txt readable", False, str(exc))
        failures += 1
    print()

    # ── Summary ───────────────────────────────────────────────────────────────
    print("=" * 60)
    if failures == 0:
        print(f"  [PASS] Protected smoke test PASSED — all checks OK")
    else:
        print(f"  [FAIL] Protected smoke test FAILED — {failures} check(s) failed")
    print("=" * 60)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Astro Destiny Analyzer Protected Trial Smoke Test"
    )
    parser.add_argument("--zip", required=True, dest="zip_path",
                        help="Path to the protected trial ZIP file")
    args = parser.parse_args()
    return 0 if run_smoke_test(zip_path=args.zip_path) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
