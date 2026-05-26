"""
Astro Destiny Analyzer — Entry Point
Usage:
    python app.py              → launches Streamlit via subprocess
    streamlit run ui/streamlit_app.py   → direct launch
"""
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent

def main():
    # Initialise database
    sys.path.insert(0, str(BASE_DIR))
    from core.database import init_db
    init_db()
    print("[Astro Destiny Analyzer] Database initialised.")

    # Launch Streamlit
    streamlit_script = BASE_DIR / "ui" / "streamlit_app.py"
    print(f"[Astro Destiny Analyzer] Starting Streamlit: {streamlit_script}")
    result = subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(streamlit_script),
         "--server.headless", "false"],
        cwd=str(BASE_DIR),
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
