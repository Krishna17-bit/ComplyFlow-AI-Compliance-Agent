from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent / "complyflow.db"


def init_db() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nda_signups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            nda_hash TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auditor_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            control_id TEXT NOT NULL,
            status TEXT NOT NULL,
            comment TEXT NOT NULL,
            auditor_name TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_locks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audit_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            mappings_hash TEXT NOT NULL,
            signature TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questionnaire_overrides (
            question TEXT PRIMARY KEY,
            answer TEXT NOT NULL,
            confidence REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_nda_signup(name: str, email: str, company: str) -> str:
    timestamp = datetime.now(timezone.utc).isoformat()
    nda_text = f"NDA agreement between ComplyFlow AI and {name} ({email}) at {company} signed on {timestamp}"
    nda_hash = hashlib.sha256(nda_text.encode("utf-8")).hexdigest()

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO nda_signups (name, email, company, timestamp, nda_hash) VALUES (?, ?, ?, ?, ?)",
        (name, email, company, timestamp, nda_hash),
    )
    conn.commit()
    conn.close()
    return nda_hash


def get_nda_signups() -> list[dict[str, Any]]:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, company, timestamp, nda_hash FROM nda_signups ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"name": r[0], "email": r[1], "company": r[2], "timestamp": r[3], "nda_hash": r[4]} for r in rows]


def add_auditor_comment(control_id: str, status: str, comment: str, auditor_name: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM auditor_comments WHERE control_id = ?", (control_id,))
    cursor.execute(
        "INSERT INTO auditor_comments (control_id, status, comment, auditor_name, timestamp) VALUES (?, ?, ?, ?, ?)",
        (control_id, status, comment, auditor_name, timestamp),
    )
    conn.commit()
    conn.close()


def get_auditor_comments() -> dict[str, dict[str, Any]]:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT control_id, status, comment, auditor_name, timestamp FROM auditor_comments")
    rows = cursor.fetchall()
    conn.close()
    return {r[0]: {"status": r[1], "comment": r[2], "auditor_name": r[3], "timestamp": r[4]} for r in rows}


def add_audit_lock(audit_id: str, mappings_hash: str, signature: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO audit_locks (audit_id, timestamp, mappings_hash, signature) VALUES (?, ?, ?, ?)",
        (audit_id, timestamp, mappings_hash, signature),
    )
    conn.commit()
    conn.close()


def get_audit_locks() -> list[dict[str, Any]]:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT audit_id, timestamp, mappings_hash, signature FROM audit_locks ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"audit_id": r[0], "timestamp": r[1], "mappings_hash": r[2], "signature": r[3]} for r in rows]


def add_questionnaire_override(question: str, answer: str, confidence: float) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO questionnaire_overrides (question, answer, confidence, timestamp) VALUES (?, ?, ?, ?)",
        (question, answer, confidence, timestamp),
    )
    conn.commit()
    conn.close()


def get_questionnaire_overrides() -> dict[str, dict[str, Any]]:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer, confidence, timestamp FROM questionnaire_overrides")
    rows = cursor.fetchall()
    conn.close()
    return {r[0]: {"answer": r[1], "confidence": r[2], "timestamp": r[3]} for r in rows}
