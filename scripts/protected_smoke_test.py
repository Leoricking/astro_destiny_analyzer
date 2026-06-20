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

EXPECTED_VERSION = "2.0.6"
ZIP_ROOT_DIR = f"astro_destiny_analyzer_v{EXPECTED_VERSION}_protected_trial"

# ── Project source packages — must NOT appear as .py inside _internal/ ────────
_PROJECT_PACKAGE_ROOTS = [
    "ui/",
    "core/",
    "engines/",
    "reports/",
    "compatibility/",
    "human_design/",
    "human_design_reconciliation/",
    "public_content/",
    "lead_magnet/",
    "consultant_workflow/",
    "ziwei_reconciliation/",
]

# ── Known minimal stubs allowed as .py inside _internal/ (no business logic) ──
_ALLOWED_STUBS_IN_INTERNAL = [
    "protected_streamlit_entry.py",
]

# ── Required files in the protected ZIP ───────────────────────────────────────
REQUIRED_FILES_PROTECTED = [
    "CUSTOMER_README.md",
    "TRIAL_README.txt",
    "VERSION.txt",
    "RELEASE_NOTES.md",
]

# Specific exe path within the ZIP (subdirectory from PyInstaller one-folder build)
REQUIRED_EXE_PATH = "AstroDestinyAnalyzer/AstroDestinyAnalyzer.exe"

# At least one of these must be present (exe OR launcher bat)
REQUIRED_EXECUTABLE_ANY = [
    "AstroDestinyAnalyzer.exe",
    "start_protected.bat",
]

# ── Streamlit runtime — must be present for the app to start ─────────────────
REQUIRED_STREAMLIT_DIR = "_internal/streamlit/"
REQUIRED_STREAMLIT_DISTINFO_PREFIX = "_internal/streamlit-"

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


def _is_project_source_inside_internal(arc_name: str) -> bool:
    """Return True if the entry is a project source .py inside _internal/.

    Rejects readable project source files (ui/, core/, engines/, etc.) that
    must not appear in the protected ZIP even inside _internal/.
    Allows known minimal stubs and third-party library files.
    """
    normalized = arc_name.replace("\\", "/").lower()
    if not normalized.endswith(".py"):
        return False

    # Only inspect files inside _internal/
    idx = normalized.find("/_internal/")
    if idx >= 0:
        after_internal = normalized[idx + len("/_internal/"):]
    elif normalized.startswith("_internal/"):
        after_internal = normalized[len("_internal/"):]
    else:
        return False  # outside _internal/ — handled by _is_py_source_outside_internal

    # Allow known minimal stubs (no business logic)
    for stub in _ALLOWED_STUBS_IN_INTERNAL:
        if after_internal == stub.lower():
            return False

    # Reject if the path starts with a project package root
    for pkg_root in _PROJECT_PACKAGE_ROOTS:
        if after_internal.startswith(pkg_root.lower()):
            return True

    # Third-party library files (numpy, pyarrow, streamlit, etc.) — allowed
    return False


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

    # ── 5. EXE at correct subdirectory path ───────────────────────────────────
    print("[CHECK] EXE at correct subdirectory path:")
    has_subdir_exe = any(
        n.replace("\\", "/").lower().endswith(REQUIRED_EXE_PATH.lower())
        for n in names
    )
    if not _result(
        f"{REQUIRED_EXE_PATH} present",
        has_subdir_exe,
        "OK" if has_subdir_exe else "MISSING — EXE not found at expected subdirectory path",
    ):
        failures += 1
    print()

    # ── 5b. start_protected.bat points to subdirectory EXE ────────────────────
    print("[CHECK] start_protected.bat EXE path and Windows batch syntax:")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            bat_entries = [n for n in names if n.lower().endswith("start_protected.bat")
                           and "_internal" not in n.lower()]
            if bat_entries:
                bat_content = zf.read(bat_entries[0]).decode("utf-8", errors="replace")
                subdir_ref = "AstroDestinyAnalyzer\\AstroDestinyAnalyzer.exe" in bat_content \
                             or "AstroDestinyAnalyzer/AstroDestinyAnalyzer.exe" in bat_content
                if not _result(
                    "start_protected.bat references AstroDestinyAnalyzer\\AstroDestinyAnalyzer.exe",
                    subdir_ref,
                    "OK" if subdir_ref else "FAIL — bat points to wrong EXE path",
                ):
                    failures += 1
                has_devmode = "STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false" in bat_content
                if not _result(
                    "start_protected.bat disables developmentMode",
                    has_devmode,
                    "OK" if has_devmode else "MISSING — STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false not set",
                ):
                    failures += 1
                has_8501 = "127.0.0.1:8501" in bat_content or "8501" in bat_content
                if not _result(
                    "start_protected.bat contains port 8501",
                    has_8501,
                    "OK" if has_8501 else "MISSING — bat does not set port 8501",
                ):
                    failures += 1
                no_3000 = "3000" not in bat_content
                if not _result(
                    "start_protected.bat does not reference port 3000",
                    no_3000,
                    "OK" if no_3000 else "FAIL — bat still references port 3000",
                ):
                    failures += 1
                # ── Windows batch syntax validation ──────────────────────────
                has_script_dir = 'set "SCRIPT_DIR=%~dp0"' in bat_content
                if not _result(
                    'start_protected.bat has set "SCRIPT_DIR=%~dp0"',
                    has_script_dir,
                    "OK" if has_script_dir else "MISSING or malformed — %~dp0 not found",
                ):
                    failures += 1
                no_bare_dp0 = "~dp0" not in bat_content.replace("%~dp0", "")
                if not _result(
                    "start_protected.bat has no bare ~dp0 without %",
                    no_bare_dp0,
                    "OK" if no_bare_dp0 else "FAIL — bare ~dp0 found (missing % prefix)",
                ):
                    failures += 1
                no_dollar_env = "$env" not in bat_content.lower()
                if not _result(
                    "start_protected.bat has no $env (PowerShell syntax)",
                    no_dollar_env,
                    "OK" if no_dollar_env else "FAIL — $env found in bat file",
                ):
                    failures += 1
                no_env_colon = "env:" not in bat_content.lower()
                if not _result(
                    "start_protected.bat has no env: (Linux syntax)",
                    no_env_colon,
                    "OK" if no_env_colon else "FAIL — env: found in bat file",
                ):
                    failures += 1
            else:
                _result("start_protected.bat found in ZIP", False, "NOT FOUND")
                failures += 1
    except Exception as exc:
        _result("start_protected.bat readable", False, str(exc))
        failures += 1
    print()

    # ── 5c. Streamlit runtime present ─────────────────────────────────────────
    print("[CHECK] Streamlit runtime in _internal/:")
    has_streamlit_dir = any(
        REQUIRED_STREAMLIT_DIR in n.replace("\\", "/").lower()
        for n in names
    )
    if not _result(
        f"{REQUIRED_STREAMLIT_DIR} present",
        has_streamlit_dir,
        "OK" if has_streamlit_dir else "MISSING — streamlit not bundled",
    ):
        failures += 1

    has_streamlit_dist = any(
        REQUIRED_STREAMLIT_DISTINFO_PREFIX in n.replace("\\", "/").lower()
        for n in names
    )
    if not _result(
        "streamlit dist-info present",
        has_streamlit_dist,
        "OK" if has_streamlit_dist else "MISSING — streamlit metadata not bundled",
    ):
        failures += 1
    print()

    # ── 7. No .py source files outside _internal/ ─────────────────────────────
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

    # ── 8. No project source .py inside _internal/ ───────────────────────────
    print("[CHECK] No project source .py inside _internal/:")
    leaked_internal = [n for n in names if _is_project_source_inside_internal(n)]
    if leaked_internal:
        for entry in leaked_internal[:10]:
            _result(f"Leaked: {entry}", False, "project source must be bytecode-only")
            failures += 1
    else:
        _result("No project source .py inside _internal/", True, "OK")
    print()

    # ── 9. Forbidden entries absent ───────────────────────────────────────────
    print("[CHECK] Forbidden entries absent:")
    found_forbidden = [n for n in names if _is_forbidden_entry(n)]
    if found_forbidden:
        for entry in found_forbidden[:10]:
            _result(f"Absent: {entry}", False, "FOUND — must not be included")
            failures += 1
    else:
        _result("No forbidden entries found", True)
    print()

    # ── 10. tests/ absent (excluding _internal/ which may have library tests) ──
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

    # ── 11. demo/ absent ──────────────────────────────────────────────────────
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

    # ── 12. VERSION.txt content ───────────────────────────────────────────────
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
