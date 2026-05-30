"""
Astro Destiny Analyzer — Protected Trial Launcher
Sets customer/trial-mode environment variables and launches the Streamlit app.
Entry point for PyInstaller one-folder build.
"""
import os
import sys

# ── Environment: Protected trial / customer mode ───────────────────────────────
os.environ.setdefault("ASTRO_CUSTOMER_MODE", "1")
os.environ.setdefault("ASTRO_CONSULTANT_MODE", "0")
os.environ.setdefault("ASTRO_DEVELOPER_MODE", "0")
os.environ.setdefault("ASTRO_TRIAL_MODE", "1")
os.environ.setdefault("ASTRO_PORTABLE_MODE", "1")
os.environ.setdefault("ASTRO_BUILD_PROFILE", "protected_trial")

# ── Resolve app path ───────────────────────────────────────────────────────────
if getattr(sys, "frozen", False):
    # Running inside a PyInstaller bundle — data files are in sys._MEIPASS
    _base = sys._MEIPASS
else:
    # Normal Python execution (development / testing)
    _base = os.path.dirname(os.path.abspath(__file__))

_app_script = os.path.join(_base, "protected_streamlit_entry.py")

if not os.path.isfile(_app_script):
    print(f"[ERROR] App script not found: {_app_script}")
    print("Please ensure the package is intact. Contact support if this persists.")
    try:
        input("Press Enter to exit...")
    except EOFError:
        pass
    sys.exit(1)

# ── Launch Streamlit ───────────────────────────────────────────────────────────
try:
    from streamlit.web import cli as stcli
    sys.argv = [
        "streamlit", "run", _app_script,
        "--server.headless", "false",
        "--browser.gatherUsageStats", "false",
    ]
    sys.exit(stcli.main())
except ImportError as exc:
    print(f"[ERROR] Streamlit is not available: {exc}")
    print("The package may be corrupted. Please re-extract the ZIP.")
    try:
        input("Press Enter to exit...")
    except EOFError:
        pass
    sys.exit(1)
except Exception as exc:
    print(f"[ERROR] Failed to launch app: {exc}")
    try:
        input("Press Enter to exit...")
    except EOFError:
        pass
    sys.exit(1)
