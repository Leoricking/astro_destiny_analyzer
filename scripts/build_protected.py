"""
Astro Destiny Analyzer — Protected Trial Build Script  V2.0.3
Builds a PyInstaller one-folder protected trial package.
Source .py files are compiled into bytecode inside _internal/;
customers see only the .exe and bundled runtime — not the raw source.

Usage:
    python scripts/build_protected.py

Output:
    dist/AstroDestinyAnalyzer/   — PyInstaller one-folder build
    release/astro_destiny_analyzer_v2.0.3_protected_trial.zip

Exit code: 0 = success, 1 = failure.
"""
import sys
import os
import subprocess
import shutil
import zipfile
import pathlib

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = pathlib.Path(_SCRIPT_DIR).parent

APP_VERSION = "2.0.5"
DIST_NAME = "AstroDestinyAnalyzer"
DIST_DIR = _ROOT / "dist" / DIST_NAME
RELEASE_DIR = _ROOT / "release"
ZIP_NAME = f"astro_destiny_analyzer_v{APP_VERSION}_protected_trial.zip"
ZIP_PATH = RELEASE_DIR / ZIP_NAME
ZIP_ROOT_DIR = f"astro_destiny_analyzer_v{APP_VERSION}_protected_trial"

# ── Docs to include alongside the executable ───────────────────────────────────
_INCLUDE_DOCS = [
    "CUSTOMER_README.md",
    "CUSTOMER_ONBOARDING.md",
    "TRIAL_README.txt",
    "試用說明.txt",
    "VERSION.txt",
    "RELEASE_NOTES.md",
    "start_protected.bat",
]

# ── Forbidden patterns — must NOT appear in the protected ZIP ──────────────────
# (These are checked by protected_smoke_test.py against the final ZIP)
_FORBIDDEN_ZIP_PATTERNS = [
    ".git",
    ".venv",
    "tests/",
    "demo/",
    "data/leads_mock.json",
    "data/client_cases.json",
    "data/lead_funnel_events.json",
    "data/human_design_calibration_cases.json",
    ".env",
    "run_dev.bat",
    "run_consultant.bat",
    "rossi",
]

# ── PyInstaller hidden imports needed for Streamlit ───────────────────────────
_HIDDEN_IMPORTS = [
    "streamlit",
    "streamlit.web",
    "streamlit.web.cli",
    "streamlit.runtime",
    "altair",
    "pydeck",
    "config",
    "runpy",
]

# ── Third-party packages: collect all files + copy dist-info metadata ─────────
# Required so streamlit's importlib.metadata lookups succeed at runtime.
_COLLECT_ALL_THIRD_PARTY = [
    "streamlit",
    "altair",
    "pydeck",
    "watchdog",
    "blinker",
    "click",
    "cachetools",
]

_COPY_METADATA = [
    "streamlit",
    "altair",
    "pydeck",
    "watchdog",
    "blinker",
    "click",
    "cachetools",
]

# ── Project packages to collect as compiled bytecode (no .py source exposed) ──
_COLLECT_SUBMODULES = [
    "ui",
    "core",
    "engines",
    "reports",
    "compatibility",
    "human_design",
    "human_design_reconciliation",
    "public_content",
    "lead_magnet",
    "consultant_workflow",
    "ziwei_reconciliation",
    "i18n",
    "i18n.locales.es",
    "i18n.locales.ar",
    "i18n.rtl",
    "ui.i18n_helpers",
]


def _check_pyinstaller() -> bool:
    try:
        import PyInstaller  # noqa: F401
        return True
    except ImportError:
        return False


def _run_pyinstaller() -> bool:
    """Run PyInstaller to create a one-folder build."""
    launcher = str(_ROOT / "app_launcher.py")
    stub = str(_ROOT / "protected_streamlit_entry.py")

    hidden = []
    for hi in _HIDDEN_IMPORTS:
        hidden += ["--hidden-import", hi]

    # Collect all third-party runtime files + metadata (streamlit, altair, etc.)
    collect_all = []
    for pkg in _COLLECT_ALL_THIRD_PARTY:
        collect_all += ["--collect-all", pkg]

    copy_meta = []
    for pkg in _COPY_METADATA:
        copy_meta += ["--copy-metadata", pkg]

    # Collect all project submodules as compiled bytecode — no .py source exposed
    collect_sub = []
    for pkg in _COLLECT_SUBMODULES:
        collect_sub += ["--collect-submodules", pkg]

    # Include only the minimal stub as a data file (no business logic)
    sep = ";" if sys.platform == "win32" else ":"
    add_data = [
        "--add-data", f"{stub}{sep}.",
    ]

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",
        "--name", DIST_NAME,
        "--distpath", str(_ROOT / "dist"),
        "--workpath", str(_ROOT / "build"),
        "--specpath", str(_ROOT / "build"),
        "--noconfirm",
        "--clean",
        *hidden,
        *collect_all,
        *copy_meta,
        *collect_sub,
        *add_data,
        launcher,
    ]
    print(f"[INFO] Running: {' '.join(cmd[:6])} ...")
    result = subprocess.run(cmd, cwd=str(_ROOT))
    return result.returncode == 0


def _create_zip() -> pathlib.Path:
    """Package the PyInstaller dist folder + docs into the release ZIP."""
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    files_added = 0
    with zipfile.ZipFile(str(ZIP_PATH), "w", zipfile.ZIP_DEFLATED) as zf:
        # Add everything from the PyInstaller dist folder under the root wrapper
        if DIST_DIR.exists():
            for f in DIST_DIR.rglob("*"):
                if not f.is_file():
                    continue
                rel = f.relative_to(DIST_DIR.parent).as_posix()
                arc_name = ZIP_ROOT_DIR + "/" + rel
                zf.write(str(f), arc_name)
                files_added += 1

        # Add docs inside the root wrapper folder
        for doc in _INCLUDE_DOCS:
            src = _ROOT / doc
            if src.exists():
                arc_name = ZIP_ROOT_DIR + "/" + doc
                zf.write(str(src), arc_name)
                files_added += 1

        # Empty data directories inside root wrapper
        zf.writestr(ZIP_ROOT_DIR + "/data/.gitkeep", "")
        zf.writestr(ZIP_ROOT_DIR + "/data/exports/.gitkeep", "")

    return files_added


def main() -> int:
    print("=" * 60)
    print(f"  Astro Destiny Analyzer — Protected Build v{APP_VERSION}")
    print("=" * 60)
    print()

    # ── 1. Check PyInstaller ──────────────────────────────────────────────────
    if not _check_pyinstaller():
        print("[ERROR] PyInstaller not found in this environment.")
        print("  Install: pip install pyinstaller")
        print("  Or:      pip install -r requirements-build.txt")
        return 1

    # ── 2. Run PyInstaller ────────────────────────────────────────────────────
    print("[INFO] Running PyInstaller (one-folder mode)...")
    if not _run_pyinstaller():
        print("[ERROR] PyInstaller build failed. Check output above.")
        return 1
    print(f"[OK]   PyInstaller build complete: {DIST_DIR}")
    print()

    # ── 3. Create release ZIP ─────────────────────────────────────────────────
    print("[INFO] Creating protected release ZIP...")
    files_added = _create_zip()
    print(f"[OK]   ZIP created: {ZIP_PATH}  ({files_added} files)")
    print()

    print("=" * 60)
    print(f"  Profile : protected_trial")
    print(f"  ZIP     : {ZIP_PATH}")
    print(f"  Note    : Source .py files compiled to bytecode in _internal/")
    print(f"            Customers see only the .exe — not raw source.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
