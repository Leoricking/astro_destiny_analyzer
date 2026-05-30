"""
Astro Destiny Analyzer — Protected Trial Launcher
Sets customer/trial-mode environment variables and launches the Streamlit app.
Entry point for PyInstaller one-folder build.
"""
import os
import sys
import socket
import threading
import webbrowser

# ── Environment: Protected trial / customer mode ───────────────────────────────
os.environ.setdefault("ASTRO_CUSTOMER_MODE", "1")
os.environ.setdefault("ASTRO_CONSULTANT_MODE", "0")
os.environ.setdefault("ASTRO_DEVELOPER_MODE", "0")
os.environ.setdefault("ASTRO_TRIAL_MODE", "1")
os.environ.setdefault("ASTRO_PORTABLE_MODE", "1")
os.environ.setdefault("ASTRO_BUILD_PROFILE", "protected_trial")

# ── Force Streamlit port to 8501 — ignore any PORT=3000 from the environment ──
os.environ.pop("PORT", None)
os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
os.environ["STREAMLIT_SERVER_PORT"] = "8501"
os.environ["STREAMLIT_SERVER_ADDRESS"] = "127.0.0.1"
os.environ["STREAMLIT_BROWSER_SERVER_PORT"] = "8501"
os.environ["STREAMLIT_BROWSER_SERVER_ADDRESS"] = "127.0.0.1"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"

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

# ── Disable development mode via Streamlit config API (before stcli import) ───
try:
    from streamlit import config as _st_config
    _st_config.set_option("global.developmentMode", False)
except Exception:
    pass  # best-effort; env var above is the primary guard

# ── Browser auto-open helpers ─────────────────────────────────────────────────
def _wait_for_server(host: str, port: int, timeout_seconds: int = 30) -> bool:
    """Poll host:port every 0.5 s until it accepts connections or timeout."""
    import time
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False


def _open_browser_when_ready() -> None:
    """Wait for server to be ready, then open the browser."""
    if _wait_for_server("127.0.0.1", 8501):
        webbrowser.open("http://127.0.0.1:8501")


# ── Launch Streamlit ───────────────────────────────────────────────────────────
print("Local URL: http://127.0.0.1:8501")
print("If the browser does not open automatically, open the URL above.")
try:
    from streamlit.web import cli as stcli
    threading.Thread(target=_open_browser_when_ready, daemon=True).start()
    sys.argv = [
        "streamlit", "run", _app_script,
        "--global.developmentMode=false",
        "--server.port=8501",
        "--server.address=127.0.0.1",
        "--browser.serverPort=8501",
        "--browser.serverAddress=127.0.0.1",
        "--browser.gatherUsageStats=false",
        "--server.headless=true",
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
