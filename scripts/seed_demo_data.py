"""
Astro Destiny Analyzer — Demo Seed Data Generator  V2.0.0

Generates demo leads and client cases for developer/consultant testing.
Uses generic placeholder names only — no real personal data.

Usage:
    python scripts/seed_demo_data.py

Output:
    data/demo_seed/demo_leads.json
    data/demo_seed/demo_client_cases.json

IMPORTANT:
- This script does NOT run automatically.
- Demo seed files are excluded from customer release ZIPs.
- Do NOT use real personal names in this script.
"""
import sys
import os
import json
from datetime import datetime, date

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

DEMO_SEED_DIR = os.path.join(_PROJECT_ROOT, "data", "demo_seed")

# ── Generic demo names (NO real names, NO Rossi) ──────────────────────────────
DEMO_SAMPLE_NAMES = [
    "Demo Client A",
    "Demo Client B",
    "Sample Relationship Case",
]

DEMO_LEADS = [
    {
        "name": "Demo Client A",
        "email": "demo_a@example.com",
        "report_type": "natal_free_summary",
        "birth_date": "1990-01-15",
        "birth_location": "台北",
        "birth_country": "台灣",
        "consent": True,
        "marketing_consent": False,
        "created_at": "2026-01-01T10:00:00",
    },
    {
        "name": "Demo Client B",
        "email": "demo_b@example.com",
        "report_type": "compatibility_free_summary",
        "birth_date": "1985-06-20",
        "birth_location": "台中",
        "birth_country": "台灣",
        "consent": True,
        "marketing_consent": True,
        "created_at": "2026-01-02T11:00:00",
    },
    {
        "name": "Sample Relationship Case",
        "email": "demo_rel@example.com",
        "report_type": "compatibility_free_summary",
        "birth_date": "1992-11-30",
        "birth_location": "高雄",
        "birth_country": "台灣",
        "consent": True,
        "marketing_consent": False,
        "created_at": "2026-01-03T09:30:00",
    },
]

DEMO_CLIENT_CASES = [
    {
        "case_id": "case_demo_001",
        "profile": {
            "name": "Demo Client A",
            "birth_date": "1990-01-15",
            "birth_location": "台北",
            "birth_country": "台灣",
        },
        "case_status": "data_collected",
        "report_status": "draft",
        "report_types": ["natal", "integrated"],
        "notes": [],
        "tasks": [],
        "deliveries": [],
        "created_at": "2026-01-01T10:00:00",
        "updated_at": "2026-01-05T14:00:00",
    },
    {
        "case_id": "case_demo_002",
        "profile": {
            "name": "Demo Client B",
            "birth_date": "1985-06-20",
            "birth_location": "台中",
            "birth_country": "台灣",
        },
        "case_status": "report_generated",
        "report_status": "reviewed",
        "report_types": ["compatibility"],
        "notes": [],
        "tasks": [],
        "deliveries": [],
        "created_at": "2026-01-02T11:00:00",
        "updated_at": "2026-01-06T10:00:00",
    },
]


def _write_json(path: str, data: object) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK]   Written: {path}")


def main() -> int:
    print("=" * 60)
    print("  Astro Destiny Analyzer — Demo Seed Data Generator")
    print("=" * 60)
    print()
    print(f"[INFO] Output dir: {DEMO_SEED_DIR}")
    print("[INFO] All names are generic placeholders (no real personal data).")
    print()

    # Verify no Rossi references
    all_names = [l["name"] for l in DEMO_LEADS] + [c["profile"]["name"] for c in DEMO_CLIENT_CASES]
    for name in all_names:
        if "rossi" in name.lower():
            print(f"[ERROR] Forbidden name detected: {name}")
            return 1

    _write_json(os.path.join(DEMO_SEED_DIR, "demo_leads.json"), DEMO_LEADS)
    _write_json(os.path.join(DEMO_SEED_DIR, "demo_client_cases.json"), DEMO_CLIENT_CASES)

    print()
    print(f"[OK]   Generated {len(DEMO_LEADS)} demo leads.")
    print(f"[OK]   Generated {len(DEMO_CLIENT_CASES)} demo client cases.")
    print()
    print("[NOTE] These files are excluded from customer release ZIPs.")
    print("       Do not mix with real leads/client data in data/.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
