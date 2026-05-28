"""
Astro Destiny Analyzer — Encoding Utilities
V1.8.1: Windows UTF-8 console helper.
"""
import sys


def ensure_utf8_console() -> None:
    """
    On Windows, try to reconfigure stdout/stderr to UTF-8.
    If reconfiguration fails (e.g. older Python or redirected stream), does nothing.
    Never raises.
    """
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
