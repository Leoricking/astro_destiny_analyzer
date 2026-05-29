"""
Astro Destiny Analyzer — Release Package Builder  V2.0.0
Copies the project into a clean release folder, excluding dev artifacts,
personal data, lead/client data, and credentials.

Usage:
    python scripts/build_release.py [--profile customer|consultant|developer]

Output:
    release/astro_destiny_analyzer_v{APP_VERSION}_{profile}/
    release/astro_destiny_analyzer_v{APP_VERSION}_{profile}.zip

Exit code: 0 = success, 1 = failure.
"""
import sys
import os
import shutil
import zipfile
import argparse
from datetime import date, datetime

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ── Exclusion rules (all profiles) ────────────────────────────────────────────

_EXCLUDE_DIRS_ALL = {
    ".git", ".venv", "venv", "env",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".idea", ".vscode", ".claude",
    "release", "dist", "build",
    "demo_outputs",
}

_EXCLUDE_EXTENSIONS = {
    ".db", ".sqlite", ".sqlite3",
    ".pyc", ".pyo", ".pyd",
    ".log", ".zip", ".rar",
    ".egg-info",
    ".key", ".pem", ".token",
}

_EXCLUDE_FILES = {
    ".DS_Store", "Thumbs.db", ".env",
}

# Data files with personal / lead / calibration content — never shipped
_EXCLUDE_DATA_PATTERNS = {
    "leads_mock.json",
    "lead_funnel_events.json",
    "client_cases.json",
    "human_design_calibration_cases.json",
}

# Filenames containing these substrings are blocked (case-insensitive) — all profiles
_BLOCK_FILENAME_SUBSTRINGS_ALL = {"rossi", "password", "secret", "api_key"}
# Extra blocks for customer profile
_BLOCK_FILENAME_SUBSTRINGS_CUSTOMER = {"token"}

# Empty data subdirectories to create in the release (with .gitkeep)
_EMPTY_DATA_DIRS = [
    "data",
    os.path.join("data", "exports"),
    os.path.join("data", "lead_exports"),
    os.path.join("data", "lead_funnel_exports"),
    os.path.join("data", "client_case_exports"),
]

# ── Backward-compat aliases (used by existing tests) ─────────────────────────
_EXCLUDE_DIRS = _EXCLUDE_DIRS_ALL
_BLOCK_FILENAME_SUBSTRINGS = _BLOCK_FILENAME_SUBSTRINGS_ALL

# ── Zip safety check ──────────────────────────────────────────────────────────

_FORBIDDEN_ZIP_ENTRIES_ALL = [
    ".git", ".venv", "__pycache__",
    "leads_mock", "lead_funnel_events",
    "client_cases", "human_design_calibration_cases",
    "rossi", ".env",
]
_FORBIDDEN_ZIP_ENTRIES_CUSTOMER_EXTRA = [
    "run_dev.bat", "run_consultant.bat",
]


def _zip_entry_safe(entry_name: str, profile: str = "customer") -> bool:
    normalized = entry_name.replace("\\", "/").lower()
    parts = normalized.split("/")
    forbidden_list = list(_FORBIDDEN_ZIP_ENTRIES_ALL)
    if profile == "customer":
        forbidden_list += _FORBIDDEN_ZIP_ENTRIES_CUSTOMER_EXTRA
    for forbidden in forbidden_list:
        fl = forbidden.lower()
        # For path-component checks (e.g. ".git"), match as a full path component
        # to avoid false positives like ".gitignore" containing ".git"
        if fl.startswith(".") and not fl.endswith(".json") and not fl.endswith(".bat"):
            # Match as exact path component
            if fl in parts:
                return False
        else:
            # Substring match for data filenames, keywords, and bat files
            if fl in normalized:
                return False
    return True


def _should_exclude(rel_path: str, profile: str = "customer") -> bool:
    """Return True if the given relative path should be excluded from release."""
    parts = rel_path.replace("\\", "/").split("/")

    exclude_dirs = set(_EXCLUDE_DIRS_ALL)
    if profile == "customer":
        exclude_dirs.add("tests")
        exclude_dirs.add("demo")
    elif profile == "consultant":
        exclude_dirs.add("tests")
        exclude_dirs.add("demo")

    for part in parts:
        if part in exclude_dirs:
            return True
        if part.endswith(".egg-info"):
            return True

    _, ext = os.path.splitext(rel_path)
    if ext.lower() in _EXCLUDE_EXTENSIONS:
        return True

    filename = os.path.basename(rel_path)
    if filename in _EXCLUDE_FILES:
        return True

    if filename in _EXCLUDE_DATA_PATTERNS:
        return True

    filename_lower = filename.lower()
    block_subs = set(_BLOCK_FILENAME_SUBSTRINGS_ALL)
    if profile == "customer":
        block_subs |= _BLOCK_FILENAME_SUBSTRINGS_CUSTOMER
        # Customer profile: exclude dev/consultant launchers
        if filename_lower in ("run_dev.bat", "run_consultant.bat"):
            return True

    for sub in block_subs:
        if sub in filename_lower:
            return True

    return False


def get_release_profile_config(profile: str) -> dict:
    """Return exclusion and inclusion rules for the given build profile."""
    base = {
        "profile": profile,
        "exclude_dirs": set(_EXCLUDE_DIRS_ALL),
        "exclude_data_patterns": set(_EXCLUDE_DATA_PATTERNS),
        "block_substrings": set(_BLOCK_FILENAME_SUBSTRINGS_ALL),
        "forbidden_zip_entries": list(_FORBIDDEN_ZIP_ENTRIES_ALL),
        "exclude_bat": [],
        "include_tests": False,
    }
    if profile == "customer":
        base["exclude_dirs"].add("tests")
        base["exclude_dirs"].add("demo")
        base["exclude_bat"] = ["run_dev.bat", "run_consultant.bat"]
        base["block_substrings"].add("token")
        base["forbidden_zip_entries"] += _FORBIDDEN_ZIP_ENTRIES_CUSTOMER_EXTRA
    elif profile == "consultant":
        base["exclude_dirs"].add("tests")
        base["exclude_dirs"].add("demo")
        base["exclude_bat"] = ["run_dev.bat"]
    elif profile == "developer":
        base["include_tests"] = True
    return base


def _copy_project(src_root: str, dst_root: str, profile: str = "customer") -> tuple:
    """
    Copy project files from src_root to dst_root, applying profile exclusions.
    Returns (copied_count, skipped_count, warnings).
    """
    copied = 0
    skipped = 0
    warnings = []

    profile_cfg = get_release_profile_config(profile)
    exclude_dirs = profile_cfg["exclude_dirs"]

    for dirpath, dirnames, filenames in os.walk(src_root):
        dirnames[:] = [
            d for d in dirnames
            if d not in exclude_dirs and not d.endswith(".egg-info")
        ]

        rel_dir = os.path.relpath(dirpath, src_root)

        for filename in filenames:
            rel_file = (
                os.path.join(rel_dir, filename)
                if rel_dir != "."
                else filename
            )
            if _should_exclude(rel_file, profile=profile):
                skipped += 1
                continue

            src_file = os.path.join(dirpath, filename)
            dst_file = os.path.join(dst_root, rel_file)
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.copy2(src_file, dst_file)
            copied += 1

    return copied, skipped, warnings


def _create_empty_data_dirs(dst_root: str) -> None:
    """Create empty data subdirectories with .gitkeep placeholders."""
    for rel_dir in _EMPTY_DATA_DIRS:
        abs_dir = os.path.join(dst_root, rel_dir)
        os.makedirs(abs_dir, exist_ok=True)
        gitkeep = os.path.join(abs_dir, ".gitkeep")
        if not os.path.exists(gitkeep):
            open(gitkeep, "w").close()
    print(f"[OK]   Created {len(_EMPTY_DATA_DIRS)} empty data dirs with .gitkeep")


def _create_zip(src_dir: str, zip_path: str, profile: str = "customer") -> tuple:
    """
    Create a zip archive of src_dir at zip_path.
    Returns (success: bool, unsafe_entries: list[str]).
    """
    unsafe_entries = []
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for dirpath, dirnames, filenames in os.walk(src_dir):
                dirnames[:] = [d for d in dirnames if d not in _EXCLUDE_DIRS_ALL]
                for filename in filenames:
                    abs_file = os.path.join(dirpath, filename)
                    arc_name = os.path.relpath(abs_file, os.path.dirname(src_dir))
                    if not _zip_entry_safe(arc_name, profile=profile):
                        unsafe_entries.append(arc_name)
                        print(f"[WARN] Blocked unsafe entry from zip: {arc_name}")
                        continue
                    zf.write(abs_file, arc_name)
        print(f"[OK]   ZIP created: {zip_path}")
        return True, unsafe_entries
    except Exception as exc:
        print(f"[WARN] ZIP creation failed: {exc}")
        return False, unsafe_entries


def main() -> int:
    """Build the release package. Returns 0 on success."""
    parser = argparse.ArgumentParser(description="Astro Destiny Analyzer Release Builder")
    parser.add_argument(
        "--profile",
        choices=["customer", "consultant", "developer"],
        default="customer",
        help="Build profile: customer (default) | consultant | developer",
    )
    args = parser.parse_args()
    profile = args.profile

    from config import APP_VERSION

    release_root = os.path.join(_PROJECT_ROOT, "release")
    pkg_name = f"astro_destiny_analyzer_v{APP_VERSION}_{profile}"
    pkg_dir = os.path.join(release_root, pkg_name)

    print("=" * 60)
    print(f"  Astro Destiny Analyzer — Release Builder v{APP_VERSION}")
    print(f"  Profile: {profile}")
    print("=" * 60)
    print()

    if os.path.exists(pkg_dir):
        print(f"[INFO] Removing existing release folder: {pkg_dir}")
        shutil.rmtree(pkg_dir)

    os.makedirs(pkg_dir, exist_ok=True)
    print(f"[INFO] Release target: {pkg_dir}")
    print()

    print("[INFO] Copying project files...")
    copied, skipped, warnings = _copy_project(_PROJECT_ROOT, pkg_dir, profile=profile)
    print(f"[OK]   Copied {copied} files, skipped {skipped} files")

    if warnings:
        for w in warnings:
            print(f"[WARN] {w}")

    print("[INFO] Creating empty data directories...")
    _create_empty_data_dirs(pkg_dir)

    zip_path = os.path.join(release_root, f"{pkg_name}.zip")
    _zip_ok, unsafe = _create_zip(pkg_dir, zip_path, profile=profile)

    if unsafe:
        print(f"[WARN] {len(unsafe)} unsafe entries were blocked from the zip.")

    print()
    print("=" * 60)
    print(f"  Profile : {profile}")
    print(f"  Copied  : {copied} files")
    print(f"  Skipped : {skipped} files")
    print(f"  ZIP     : {zip_path}")
    if not _zip_ok:
        print("  [WARN] ZIP was not created successfully.")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
