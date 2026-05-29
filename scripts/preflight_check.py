"""
Astro Destiny Analyzer — Preflight Health Check  V2.0.0
Verifies that the environment is ready to run the application.

Usage:
    python scripts/preflight_check.py

Exit code: 0 = all required checks passed (optional warnings may exist)
           1 = one or more required checks failed
"""
import sys
import os
import importlib

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

EXPECTED_VERSION = "2.0.0"
MIN_PYTHON = (3, 10)

REQUIRED_PACKAGES = [
    "streamlit",
    "pydantic",
    "markdown",
    "docx",          # python-docx
    "jinja2",
    "swisseph",
    "lunardate",
]

OPTIONAL_PACKAGES = [
    "weasyprint",
]

REQUIRED_FILES = [
    "run.bat",
    "setup.bat",
    "CUSTOMER_README.md",
    "VERSION.txt",
    "config.py",
]

# Note: page name strings here must be cp950-safe for Windows terminal output.
# Match on the Chinese / ASCII portion (emoji prefix stripped).
CUSTOMER_FORBIDDEN_PAGES = [
    "紫微校準",
    "人類圖校準",
    "Lead Funnel",
    "客戶個案",
]

DATA_DIRS_WRITABLE = [
    "data",
    os.path.join("data", "exports"),
]

SENSITIVE_DATA_FILES = [
    os.path.join("data", "leads_mock.json"),
    os.path.join("data", "lead_funnel_events.json"),
    os.path.join("data", "client_cases.json"),
    os.path.join("data", "human_design_calibration_cases.json"),
    ".env",
]


def _check(label: str, ok: bool, detail: str = "", warn: bool = False) -> bool:
    if ok:
        status = "PASS"
    elif warn:
        status = "WARN"
    else:
        status = "FAIL"
    msg = f"  [{status}] {label}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return ok


def check_python_version() -> bool:
    """Check Python version meets minimum requirement."""
    v = sys.version_info
    ok = (v.major, v.minor) >= MIN_PYTHON
    detail = f"Python {v.major}.{v.minor}.{v.micro}" + ("" if ok else f" — need >= {MIN_PYTHON[0]}.{MIN_PYTHON[1]}")
    return _check(f"Python >= {MIN_PYTHON[0]}.{MIN_PYTHON[1]}", ok, detail)


def check_required_packages() -> int:
    """Check required packages are importable. Returns failure count."""
    failures = 0
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
            _check(f"Package: {pkg}", True, "OK")
        except ImportError as e:
            _check(f"Package: {pkg}", False, f"NOT FOUND — {e}")
            failures += 1
    return failures


def check_optional_packages() -> None:
    """Check optional packages — warn if missing, do not fail."""
    for pkg in OPTIONAL_PACKAGES:
        try:
            importlib.import_module(pkg)
            _check(f"Optional: {pkg}", True, "OK")
        except ImportError:
            _check(f"Optional: {pkg}", True, "not installed — PDF export unavailable", warn=True)


def check_data_dirs_writable() -> int:
    """Check data directories are writable. Returns failure count."""
    failures = 0
    for rel_dir in DATA_DIRS_WRITABLE:
        abs_dir = os.path.join(_PROJECT_ROOT, rel_dir)
        try:
            os.makedirs(abs_dir, exist_ok=True)
            test_file = os.path.join(abs_dir, ".preflight_write_test")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            _check(f"Writable: {rel_dir}/", True, "OK")
        except Exception as e:
            _check(f"Writable: {rel_dir}/", False, str(e))
            failures += 1
    return failures


def check_required_files() -> int:
    """Check required deployment files exist. Returns failure count."""
    failures = 0
    for rel_path in REQUIRED_FILES:
        abs_path = os.path.join(_PROJECT_ROOT, rel_path)
        ok = os.path.isfile(abs_path)
        if not _check(f"File: {rel_path}", ok, "" if ok else "NOT FOUND"):
            failures += 1
    return failures


def check_app_version() -> bool:
    """Check APP_VERSION matches expected. Returns True on pass."""
    try:
        import config as _cfg
        importlib.reload(_cfg)
        ok = _cfg.APP_VERSION == EXPECTED_VERSION
        detail = "" if ok else f"found: {_cfg.APP_VERSION}"
        return _check(f"APP_VERSION == {EXPECTED_VERSION}", ok, detail)
    except Exception as e:
        _check("config.py APP_VERSION", False, str(e))
        return False


def check_customer_forbidden_pages() -> int:
    """Check that CUSTOMER_PAGES does not include forbidden pages. Returns failure count."""
    failures = 0
    try:
        src_path = os.path.join(_PROJECT_ROOT, "ui", "streamlit_app.py")
        src = open(src_path, encoding="utf-8").read()
        # Find CUSTOMER_PAGES or _PAGES_BASE block
        marker = "CUSTOMER_PAGES = "
        if marker not in src:
            marker = "_PAGES_BASE = ["
        idx = src.find(marker)
        end = src.find("]", idx)
        block = src[idx:end] if idx != -1 else ""
        for forbidden in CUSTOMER_FORBIDDEN_PAGES:
            if forbidden in block:
                _check(f"CUSTOMER_PAGES excludes '{forbidden}'", False, "FOUND in customer page list")
                failures += 1
            else:
                _check(f"CUSTOMER_PAGES excludes '{forbidden}'", True, "OK")
    except Exception as e:
        _check("CUSTOMER_PAGES check", False, str(e))
        failures += 1
    return failures


def check_sensitive_data_files() -> None:
    """Warn (do not fail) if sensitive data files exist in the tree."""
    for rel_path in SENSITIVE_DATA_FILES:
        abs_path = os.path.join(_PROJECT_ROOT, rel_path)
        if os.path.exists(abs_path):
            _check(f"Sensitive file: {rel_path}", True,
                   "EXISTS — will be excluded from release ZIPs", warn=True)
        else:
            _check(f"Sensitive file: {rel_path}", True, "not present")


def main() -> int:
    """Run all preflight checks. Returns 0 on success."""
    print("=" * 60)
    print(f"  Astro Destiny Analyzer — Preflight Check v{EXPECTED_VERSION}")
    print("=" * 60)
    print()

    required_failures = 0
    warnings = 0

    print("[CHECK] Python version:")
    if not check_python_version():
        required_failures += 1
    print()

    print("[CHECK] Required packages:")
    required_failures += check_required_packages()
    print()

    print("[CHECK] Optional packages:")
    check_optional_packages()
    print()

    print("[CHECK] Data directories writable:")
    required_failures += check_data_dirs_writable()
    print()

    print("[CHECK] Required files:")
    required_failures += check_required_files()
    print()

    print("[CHECK] APP_VERSION:")
    if not check_app_version():
        required_failures += 1
    print()

    print("[CHECK] Customer mode forbidden pages:")
    required_failures += check_customer_forbidden_pages()
    print()

    print("[CHECK] Sensitive data files (warning only):")
    check_sensitive_data_files()
    print()

    print("=" * 60)
    if required_failures == 0:
        print("  [OK] Preflight PASSED — environment is ready")
    else:
        print(f"  [FAIL] Preflight FAILED — {required_failures} required check(s) failed")
    print("=" * 60)

    return 0 if required_failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
