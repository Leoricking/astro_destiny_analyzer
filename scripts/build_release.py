"""
Astro Destiny Analyzer — Release Package Builder
Copies the project into a clean release folder, excluding dev artifacts.

Usage:
    python scripts/build_release.py

Output:
    release/astro_destiny_analyzer_v{APP_VERSION}/
    release/astro_destiny_analyzer_v{APP_VERSION}.zip  (optional)

Exit code: 0 = success, 1 = failure.
"""
import sys
import os
import shutil
import zipfile
from datetime import datetime

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# Directories and patterns to exclude from the release package
_EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "env",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".idea", ".vscode", ".claude",
    "release", "dist", "build", "exports",
    "demo_outputs",
}

_EXCLUDE_EXTENSIONS = {
    ".db", ".sqlite", ".sqlite3",
    ".pyc", ".pyo", ".pyd",
    ".log", ".zip", ".rar",
    ".egg-info",
}

_EXCLUDE_FILES = {
    ".DS_Store", "Thumbs.db",
}


def _should_exclude(rel_path: str) -> bool:
    """Return True if the given relative path should be excluded."""
    parts = rel_path.replace("\\", "/").split("/")
    # Exclude any path component that matches excluded dirs
    for part in parts:
        if part in _EXCLUDE_DIRS:
            return True
    # Exclude by extension
    _, ext = os.path.splitext(rel_path)
    if ext.lower() in _EXCLUDE_EXTENSIONS:
        return True
    # Exclude specific filenames
    filename = os.path.basename(rel_path)
    if filename in _EXCLUDE_FILES:
        return True
    return False


def _copy_project(src_root: str, dst_root: str) -> tuple:
    """
    Copy project files from src_root to dst_root, applying exclusions.
    Returns (copied_count, skipped_count).
    """
    copied = 0
    skipped = 0
    for dirpath, dirnames, filenames in os.walk(src_root):
        # Prune excluded directories in-place so os.walk skips them
        dirnames[:] = [
            d for d in dirnames
            if d not in _EXCLUDE_DIRS and not d.endswith(".egg-info")
        ]

        rel_dir = os.path.relpath(dirpath, src_root)

        for filename in filenames:
            rel_file = (
                os.path.join(rel_dir, filename)
                if rel_dir != "."
                else filename
            )
            if _should_exclude(rel_file):
                skipped += 1
                continue

            src_file = os.path.join(dirpath, filename)
            dst_file = os.path.join(dst_root, rel_file)
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.copy2(src_file, dst_file)
            copied += 1

    return copied, skipped


def _write_release_info(dst_root: str, version: str) -> None:
    """Write RELEASE_INFO.txt into the release folder."""
    info_path = os.path.join(dst_root, "RELEASE_INFO.txt")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    content = f"""\
Astro Destiny Analyzer — Release Info
======================================
Version      : {version}
Generated at : {now}
Python       : {py_ver}

Core Features
-------------
- Western Astrology (Swiss Ephemeris / Moshier fallback)
- BaZi (Four Pillars, solar-term precision)
- Zi Wei Dou Shu (formal layout Phase 1, auxiliary stars, Da Xian Phase 1)
- Blood Type Analysis
- Numerology
- Synthesis Engine (cross-system integration)
- Long-form report templates (Short / Standard / Full)
- HTML / Word / Markdown export; PDF optional (WeasyPrint)
- SQLite local storage
- Streamlit 7-page UI
- Demo sample profiles
- Windows one-click launcher

How to Launch
-------------
First time : Double-click setup.bat
Daily use  : Double-click run.bat

Manual     : .venv\\Scripts\\python -m streamlit run ui\\streamlit_app.py
"""
    with open(info_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK]   RELEASE_INFO.txt: {info_path}")


def _create_zip(src_dir: str, zip_path: str) -> bool:
    """Create a zip archive of src_dir at zip_path. Returns True on success."""
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for dirpath, dirnames, filenames in os.walk(src_dir):
                dirnames[:] = [d for d in dirnames if d not in _EXCLUDE_DIRS]
                for filename in filenames:
                    abs_file = os.path.join(dirpath, filename)
                    arc_name = os.path.relpath(abs_file, os.path.dirname(src_dir))
                    zf.write(abs_file, arc_name)
        print(f"[OK]   ZIP created: {zip_path}")
        return True
    except Exception as exc:
        print(f"[WARN] ZIP creation failed: {exc}")
        return False


def main() -> int:
    """Build the release package. Returns 0 on success."""
    from config import APP_VERSION

    release_root = os.path.join(_PROJECT_ROOT, "release")
    pkg_name = f"astro_destiny_analyzer_v{APP_VERSION}"
    pkg_dir = os.path.join(release_root, pkg_name)

    print("=" * 60)
    print(f"  Astro Destiny Analyzer — Release Builder v{APP_VERSION}")
    print("=" * 60)
    print()

    # Handle existing release sub-folder
    if os.path.exists(pkg_dir):
        print(f"[INFO] Removing existing release folder: {pkg_dir}")
        shutil.rmtree(pkg_dir)

    os.makedirs(pkg_dir, exist_ok=True)
    print(f"[INFO] Release target: {pkg_dir}")
    print()

    # Copy project files
    print("[INFO] Copying project files...")
    copied, skipped = _copy_project(_PROJECT_ROOT, pkg_dir)
    print(f"[OK]   Copied {copied} files, skipped {skipped} files")

    # Copy demo_outputs if present
    demo_out_src = os.path.join(_PROJECT_ROOT, "demo_outputs")
    if os.path.isdir(demo_out_src):
        demo_out_dst = os.path.join(pkg_dir, "demo_outputs")
        shutil.copytree(demo_out_src, demo_out_dst, dirs_exist_ok=True)
        print(f"[OK]   Copied demo_outputs/ into release")
    else:
        print("[INFO] demo_outputs/ not found — skipping (run generate_demo_assets.py first)")

    # Write release info
    _write_release_info(pkg_dir, APP_VERSION)

    # Optional zip
    zip_path = os.path.join(release_root, f"{pkg_name}.zip")
    _create_zip(pkg_dir, zip_path)

    print()
    print("=" * 60)
    print(f"  Release package ready: {pkg_dir}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
