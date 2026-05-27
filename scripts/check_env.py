"""
Astro Destiny Analyzer — Environment Checker
Verifies Python version, required packages, optional packages, and
that necessary directories exist and are writable.

Exit code:
  0 — all required checks passed (weasyprint absence is a warning only)
  1 — one or more required checks failed
"""
import sys
import os


def _check_import(import_name: str) -> bool:
    """Try to import a module by name. Returns True if successful."""
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def _ensure_dir(path: str) -> bool:
    """Create directory if it does not exist. Returns True if OK."""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        return False


def main() -> int:
    """Run all environment checks. Returns 0 on success, 1 on failure."""
    errors = 0

    # ── Python version ────────────────────────────────────────────────────────
    major, minor, patch = sys.version_info[:3]
    version_str = f"Python {major}.{minor}.{patch}"
    if major < 3 or (major == 3 and minor < 10):
        print(f"[FAIL] {version_str} — 需要 Python 3.10+")
        errors += 1
    else:
        print(f"[OK]   {version_str}")

    # ── Required packages ─────────────────────────────────────────────────────
    required_packages = [
        ("streamlit",   "streamlit"),
        ("pydantic",    "pydantic"),
        ("jinja2",      "jinja2"),
        ("markdown",    "markdown"),
        ("python-docx", "docx"),
        ("lunardate",   "lunardate"),
        ("swisseph",    "swisseph"),
    ]

    for display_name, import_name in required_packages:
        if _check_import(import_name):
            print(f"[OK]   {display_name}")
        else:
            print(f"[FAIL] {display_name} not installed — run: pip install -r requirements.txt")
            errors += 1

    # ── Optional packages ─────────────────────────────────────────────────────
    if _check_import("weasyprint"):
        print("[OK]   weasyprint (PDF export enabled)")
    else:
        print("[WARN] weasyprint not installed; PDF export disabled")
        print("       To enable PDF export: pip install weasyprint")

    # ── Directories ───────────────────────────────────────────────────────────
    # Resolve project root as the parent of this script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    for label, rel_path in [("data directory", "data"), ("exports directory", "exports")]:
        full_path = os.path.join(project_root, rel_path)
        if _ensure_dir(full_path):
            print(f"[OK]   {label}: {full_path}")
        else:
            print(f"[FAIL] Cannot create {label}: {full_path}")
            errors += 1

    # ── DB directory writable ─────────────────────────────────────────────────
    db_dir = os.path.join(project_root, "data")
    db_path = os.path.join(db_dir, "astro_destiny.db")
    if os.path.isdir(db_dir) and os.access(db_dir, os.W_OK):
        print(f"[OK]   DB path writable: {db_path}")
    else:
        print(f"[FAIL] DB directory not writable: {db_dir}")
        errors += 1

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    if errors == 0:
        print("Environment check passed.")
    else:
        print(f"Environment check FAILED: {errors} issue(s) found.")

    return 1 if errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
