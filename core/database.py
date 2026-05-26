"""
Astro Destiny Analyzer — SQLite Persistence Layer
Safe initialisation: never drops existing data.
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from config import DB_PATH


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create tables if they do not already exist (safe, idempotent)."""
    conn = _get_conn()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT UNIQUE NOT NULL,
                created_at  TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS birth_profiles (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER REFERENCES users(id),
                name            TEXT NOT NULL,
                gender          TEXT,
                birth_date      TEXT NOT NULL,
                birth_time      TEXT,
                birth_city      TEXT NOT NULL,
                birth_country   TEXT NOT NULL,
                residence_city  TEXT,
                residence_country TEXT,
                blood_type      TEXT DEFAULT 'Unknown',
                themes          TEXT DEFAULT '[]',
                report_language TEXT DEFAULT '繁體中文',
                report_length   TEXT DEFAULT '標準版',
                created_at      TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS chart_results (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id      INTEGER NOT NULL REFERENCES birth_profiles(id),
                western_chart   TEXT,
                bazi_chart      TEXT,
                ziwei_chart     TEXT,
                blood_analysis  TEXT,
                numerology      TEXT,
                synthesis       TEXT,
                created_at      TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS reports (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id      INTEGER NOT NULL REFERENCES birth_profiles(id),
                chart_id        INTEGER REFERENCES chart_results(id),
                title           TEXT NOT NULL,
                language        TEXT NOT NULL,
                length          TEXT NOT NULL,
                markdown_body   TEXT,
                html_body       TEXT,
                created_at      TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS report_templates (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT UNIQUE NOT NULL,
                language    TEXT NOT NULL,
                length      TEXT NOT NULL,
                template    TEXT NOT NULL,
                created_at  TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS app_settings (
                key         TEXT PRIMARY KEY,
                value       TEXT NOT NULL,
                updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
    conn.close()


# ── Birth Profile CRUD ────────────────────────────────────────────────────────

def save_birth_profile(profile_dict: Dict[str, Any], user_id: Optional[int] = None) -> int:
    conn = _get_conn()
    with conn:
        cur = conn.execute(
            """INSERT INTO birth_profiles
               (user_id, name, gender, birth_date, birth_time, birth_city,
                birth_country, residence_city, residence_country, blood_type,
                themes, report_language, report_length)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                user_id,
                profile_dict.get("name"),
                profile_dict.get("gender"),
                str(profile_dict.get("birth_date")),
                str(profile_dict.get("birth_time")) if profile_dict.get("birth_time") else None,
                profile_dict.get("birth_city"),
                profile_dict.get("birth_country"),
                profile_dict.get("residence_city"),
                profile_dict.get("residence_country"),
                profile_dict.get("blood_type", "Unknown"),
                json.dumps(profile_dict.get("themes", []), ensure_ascii=False),
                profile_dict.get("report_language", "繁體中文"),
                profile_dict.get("report_length", "標準版"),
            ),
        )
        return cur.lastrowid


def get_birth_profile(profile_id: int) -> Optional[Dict]:
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM birth_profiles WHERE id=?", (profile_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def list_birth_profiles(limit: int = 50) -> List[Dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM birth_profiles ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Chart Results CRUD ────────────────────────────────────────────────────────

def save_chart_result(profile_id: int, charts: Dict[str, Any]) -> int:
    conn = _get_conn()

    def _dump(obj):
        return json.dumps(obj, ensure_ascii=False, default=str) if obj else None

    with conn:
        cur = conn.execute(
            """INSERT INTO chart_results
               (profile_id, western_chart, bazi_chart, ziwei_chart,
                blood_analysis, numerology, synthesis)
               VALUES (?,?,?,?,?,?,?)""",
            (
                profile_id,
                _dump(charts.get("western_chart")),
                _dump(charts.get("bazi_chart")),
                _dump(charts.get("ziwei_chart")),
                _dump(charts.get("blood_type_analysis")),
                _dump(charts.get("numerology_chart")),
                _dump(charts.get("synthesis")),
            ),
        )
        return cur.lastrowid


def get_chart_result(chart_id: int) -> Optional[Dict]:
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM chart_results WHERE id=?", (chart_id,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    for key in ("western_chart", "bazi_chart", "ziwei_chart",
                "blood_analysis", "numerology", "synthesis"):
        if d[key]:
            d[key] = json.loads(d[key])
    return d


# ── Report CRUD ───────────────────────────────────────────────────────────────

def save_report(profile_id: int, chart_id: Optional[int],
                title: str, language: str, length: str,
                markdown_body: str, html_body: str) -> int:
    conn = _get_conn()
    with conn:
        cur = conn.execute(
            """INSERT INTO reports
               (profile_id, chart_id, title, language, length,
                markdown_body, html_body)
               VALUES (?,?,?,?,?,?,?)""",
            (profile_id, chart_id, title, language, length,
             markdown_body, html_body),
        )
        return cur.lastrowid


def get_report(report_id: int) -> Optional[Dict]:
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM reports WHERE id=?", (report_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def list_reports(limit: int = 50) -> List[Dict]:
    conn = _get_conn()
    rows = conn.execute(
        """SELECT r.id, r.title, r.language, r.length, r.created_at,
                  bp.name, bp.birth_date
           FROM reports r
           JOIN birth_profiles bp ON bp.id = r.profile_id
           ORDER BY r.created_at DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_report(report_id: int) -> None:
    conn = _get_conn()
    with conn:
        conn.execute("DELETE FROM reports WHERE id=?", (report_id,))
    conn.close()


# ── App Settings ──────────────────────────────────────────────────────────────

def get_setting(key: str, default: str = "") -> str:
    conn = _get_conn()
    row = conn.execute(
        "SELECT value FROM app_settings WHERE key=?", (key,)
    ).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    conn = _get_conn()
    with conn:
        conn.execute(
            """INSERT INTO app_settings (key, value, updated_at)
               VALUES (?,?,datetime('now'))
               ON CONFLICT(key) DO UPDATE SET value=excluded.value,
                                              updated_at=excluded.updated_at""",
            (key, value),
        )
    conn.close()
