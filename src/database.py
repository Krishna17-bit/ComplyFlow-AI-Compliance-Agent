from __future__ import annotations

import hashlib
import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent / "complyflow.db"


def init_db() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Original tables to preserve compatibility
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

    # New tables for AI Compliance OS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workspaces (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS frameworks (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            enabled INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS controls (
            id TEXT PRIMARY KEY,
            framework_id TEXT NOT NULL,
            domain TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            requirements TEXT,
            status TEXT NOT NULL,
            owner TEXT,
            last_reviewed_at TEXT,
            notes TEXT,
            FOREIGN KEY(framework_id) REFERENCES frameworks(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence_items (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            file_path TEXT,
            file_size INTEGER,
            file_type TEXT,
            source TEXT,
            owner TEXT,
            valid_from TEXT,
            valid_to TEXT,
            freshness TEXT,
            confidentiality TEXT,
            upload_date TEXT,
            review_status TEXT,
            content TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence_control_mappings (
            id TEXT PRIMARY KEY,
            control_id TEXT NOT NULL,
            evidence_id TEXT NOT NULL,
            status TEXT,
            confidence REAL,
            explanation TEXT,
            match_score REAL,
            is_approved INTEGER DEFAULT 0,
            FOREIGN KEY(control_id) REFERENCES controls(id),
            FOREIGN KEY(evidence_id) REFERENCES evidence_items(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gaps (
            id TEXT PRIMARY KEY,
            framework_id TEXT NOT NULL,
            control_id TEXT,
            severity TEXT NOT NULL,
            explanation TEXT NOT NULL,
            remediation TEXT,
            owner TEXT,
            status TEXT NOT NULL,
            FOREIGN KEY(framework_id) REFERENCES frameworks(id),
            FOREIGN KEY(control_id) REFERENCES controls(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remediation_tasks (
            id TEXT PRIMARY KEY,
            framework_id TEXT NOT NULL,
            control_id TEXT,
            gap_id TEXT,
            title TEXT NOT NULL,
            description TEXT,
            owner TEXT,
            due_date TEXT,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            FOREIGN KEY(framework_id) REFERENCES frameworks(id),
            FOREIGN KEY(control_id) REFERENCES controls(id),
            FOREIGN KEY(gap_id) REFERENCES gaps(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questionnaires (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            upload_date TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questionnaire_questions (
            id TEXT PRIMARY KEY,
            questionnaire_id TEXT NOT NULL,
            question TEXT NOT NULL,
            category TEXT,
            suggested_answer TEXT,
            source_evidence TEXT,
            confidence REAL,
            risk_level TEXT,
            review_status TEXT NOT NULL,
            final_answer TEXT,
            FOREIGN KEY(questionnaire_id) REFERENCES questionnaires(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS approved_answers (
            id TEXT PRIMARY KEY,
            question TEXT UNIQUE NOT NULL,
            answer TEXT NOT NULL,
            category TEXT,
            approved_by TEXT,
            usage_count INTEGER DEFAULT 0,
            is_public INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            owner TEXT,
            scope TEXT,
            commitments TEXT,
            status TEXT,
            upload_date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS policy_findings (
            id TEXT PRIMARY KEY,
            policy_id TEXT NOT NULL,
            severity TEXT NOT NULL,
            finding TEXT NOT NULL,
            recommendation TEXT,
            FOREIGN KEY(policy_id) REFERENCES policies(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trust_center_items (
            id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_packages (
            id TEXT PRIMARY KEY,
            framework_id TEXT NOT NULL,
            audit_period TEXT NOT NULL,
            export_format TEXT,
            download_url TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(framework_id) REFERENCES frameworks(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_systems (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            model TEXT,
            data_processed TEXT,
            risk_level TEXT,
            logging_enabled INTEGER DEFAULT 0,
            oversight TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS run_logs (
            id TEXT PRIMARY KEY,
            operation TEXT NOT NULL,
            input_summary TEXT,
            output_summary TEXT,
            provider TEXT,
            latency_ms INTEGER,
            status TEXT,
            timestamp TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            details TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eval_runs (
            id TEXT PRIMARY KEY,
            eval_type TEXT NOT NULL,
            dataset_name TEXT NOT NULL,
            accuracy REAL,
            summary TEXT,
            timestamp TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS provider_settings (
            key TEXT PRIMARY KEY,
            value TEXT
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


# --- CRUD Helpers for new entities ---

def execute_write(query: str, params: tuple = ()) -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()


def execute_read(query: str, params: tuple = ()) -> list[tuple]:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_audit_log(event_type: str, details: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    log_id = f"LOG-{hashlib.md5(f'{event_type}-{details}-{timestamp}'.encode()).hexdigest()[:8].upper()}"
    execute_write(
        "INSERT INTO audit_logs (id, event_type, details, timestamp) VALUES (?, ?, ?, ?)",
        (log_id, event_type, details, timestamp),
    )


def add_run_log(operation: str, input_summary: str, output_summary: str, provider: str, latency_ms: int, status: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    run_id = f"RUN-{hashlib.md5(f'{operation}-{timestamp}'.encode()).hexdigest()[:8].upper()}"
    execute_write(
        "INSERT INTO run_logs (id, operation, input_summary, output_summary, provider, latency_ms, status, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (run_id, operation, input_summary, output_summary, provider, latency_ms, status, timestamp),
    )


def reset_db() -> None:
    """Clear compliance operating system tables for re-seeding."""
    tables = [
        "frameworks", "controls", "evidence_items", "evidence_control_mappings",
        "gaps", "remediation_tasks", "questionnaires", "questionnaire_questions",
        "approved_answers", "policies", "policy_findings", "trust_center_items",
        "audit_packages", "ai_systems", "run_logs", "audit_logs", "eval_runs"
    ]
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    conn.close()
    init_db()


def get_frameworks() -> list[dict[str, Any]]:
    rows = execute_read("SELECT id, name, description, enabled FROM frameworks")
    return [{"id": r[0], "name": r[1], "description": r[2], "enabled": bool(r[3])} for r in rows]


def update_framework_enabled(fw_id: str, enabled: int) -> None:
    execute_write("UPDATE frameworks SET enabled = ? WHERE id = ?", (enabled, fw_id))
    add_audit_log("FRAMEWORK_STATUS", f"Updated enabled status for {fw_id} to {enabled}")


def get_controls(framework_id: str | None = None) -> list[dict[str, Any]]:
    if framework_id:
        rows = execute_read("SELECT id, framework_id, domain, title, description, requirements, status, owner, last_reviewed_at, notes FROM controls WHERE framework_id = ?", (framework_id,))
    else:
        rows = execute_read("SELECT id, framework_id, domain, title, description, requirements, status, owner, last_reviewed_at, notes FROM controls")
    return [
        {
            "id": r[0], "framework_id": r[1], "domain": r[2], "title": r[3], "description": r[4],
            "requirements": r[5], "status": r[6], "owner": r[7], "last_reviewed_at": r[8], "notes": r[9]
        }
        for r in rows
    ]


def update_control_status(control_id: str, status: str, owner: str = "", notes: str = "") -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    execute_write(
        "UPDATE controls SET status = ?, owner = ?, last_reviewed_at = ?, notes = ? WHERE id = ?",
        (status, owner, timestamp, notes, control_id)
    )
    add_audit_log("CONTROL_STATUS", f"Control {control_id} updated to {status} by {owner}")


def get_evidence_items() -> list[dict[str, Any]]:
    rows = execute_read("SELECT id, title, description, file_path, file_size, file_type, source, owner, valid_from, valid_to, freshness, confidentiality, upload_date, review_status, content FROM evidence_items")
    return [
        {
            "id": r[0], "title": r[1], "description": r[2], "file_path": r[3], "file_size": r[4],
            "file_type": r[5], "source": r[6], "owner": r[7], "valid_from": r[8], "valid_to": r[9],
            "freshness": r[10], "confidentiality": r[11], "upload_date": r[12], "review_status": r[13], "content": r[14]
        }
        for r in rows
    ]


def add_evidence_item(
    item_id: str, title: str, description: str, file_path: str, file_size: int,
    file_type: str, source: str, owner: str, valid_from: str, valid_to: str,
    freshness: str, confidentiality: str, content: str = ""
) -> None:
    upload_date = datetime.now(timezone.utc).isoformat()
    execute_write(
        """
        INSERT OR REPLACE INTO evidence_items 
        (id, title, description, file_path, file_size, file_type, source, owner, valid_from, valid_to, freshness, confidentiality, upload_date, review_status, content)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'needs_review', ?)
        """,
        (item_id, title, description, file_path, file_size, file_type, source, owner, valid_from, valid_to, freshness, confidentiality, upload_date, content)
    )
    add_audit_log("EVIDENCE_UPLOAD", f"Evidence {title} ({item_id}) uploaded by {owner}")


def delete_evidence_item(item_id: str) -> None:
    execute_write("DELETE FROM evidence_items WHERE id = ?", (item_id,))
    execute_write("DELETE FROM evidence_control_mappings WHERE evidence_id = ?", (item_id,))
    add_audit_log("EVIDENCE_DELETE", f"Evidence item {item_id} deleted")


def get_evidence_control_mappings() -> list[dict[str, Any]]:
    rows = execute_read("SELECT id, control_id, evidence_id, status, confidence, explanation, match_score, is_approved FROM evidence_control_mappings")
    return [
        {
            "id": r[0], "control_id": r[1], "evidence_id": r[2], "status": r[3],
            "confidence": r[4], "explanation": r[5], "match_score": r[6], "is_approved": bool(r[7])
        }
        for r in rows
    ]


def add_evidence_control_mapping(
    map_id: str, control_id: str, evidence_id: str, status: str, confidence: float,
    explanation: str, match_score: float, is_approved: int = 0
) -> None:
    execute_write(
        """
        INSERT OR REPLACE INTO evidence_control_mappings 
        (id, control_id, evidence_id, status, confidence, explanation, match_score, is_approved)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (map_id, control_id, evidence_id, status, confidence, explanation, match_score, is_approved)
    )
    add_audit_log("MAPPING_CREATE", f"Mapped {evidence_id} to control {control_id} with status {status}")


def update_evidence_control_mapping(map_id: str, status: str, is_approved: int) -> None:
    execute_write("UPDATE evidence_control_mappings SET status = ?, is_approved = ? WHERE id = ?", (status, is_approved, map_id))
    add_audit_log("MAPPING_APPROVE", f"Mapping {map_id} approved state set to {is_approved} (status: {status})")


def get_gaps(framework_id: str | None = None) -> list[dict[str, Any]]:
    if framework_id:
        rows = execute_read("SELECT id, framework_id, control_id, severity, explanation, remediation, owner, status FROM gaps WHERE framework_id = ?", (framework_id,))
    else:
        rows = execute_read("SELECT id, framework_id, control_id, severity, explanation, remediation, owner, status FROM gaps")
    return [
        {
            "id": r[0], "framework_id": r[1], "control_id": r[2], "severity": r[3],
            "explanation": r[4], "remediation": r[5], "owner": r[6], "status": r[7]
        }
        for r in rows
    ]


def add_gap(gap_id: str, framework_id: str, control_id: str, severity: str, explanation: str, remediation: str, owner: str) -> None:
    execute_write(
        "INSERT OR REPLACE INTO gaps (id, framework_id, control_id, severity, explanation, remediation, owner, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'Open')",
        (gap_id, framework_id, control_id, severity, explanation, remediation, owner)
    )


def update_gap_status(gap_id: str, status: str) -> None:
    execute_write("UPDATE gaps SET status = ? WHERE id = ?", (status, gap_id))


def get_remediation_tasks() -> list[dict[str, Any]]:
    rows = execute_read("SELECT id, framework_id, control_id, gap_id, title, description, owner, due_date, status, priority FROM remediation_tasks")
    return [
        {
            "id": r[0], "framework_id": r[1], "control_id": r[2], "gap_id": r[3], "title": r[4],
            "description": r[5], "owner": r[6], "due_date": r[7], "status": r[8], "priority": r[9]
        }
        for r in rows
    ]


def add_remediation_task(
    task_id: str, framework_id: str, control_id: str, gap_id: str, title: str,
    description: str, owner: str, due_date: str, status: str, priority: str
) -> None:
    execute_write(
        """
        INSERT OR REPLACE INTO remediation_tasks 
        (id, framework_id, control_id, gap_id, title, description, owner, due_date, status, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (task_id, framework_id, control_id, gap_id, title, description, owner, due_date, status, priority)
    )
    add_audit_log("TASK_CREATE", f"Created remediation task {task_id}: {title}")


def update_remediation_task(task_id: str, status: str) -> None:
    execute_write("UPDATE remediation_tasks SET status = ? WHERE id = ?", (status, task_id))
    add_audit_log("TASK_UPDATE", f"Task {task_id} status updated to {status}")


def get_questionnaires() -> list[dict[str, Any]]:
    rows = execute_read("SELECT id, name, type, upload_date, status FROM questionnaires")
    return [{"id": r[0], "name": r[1], "type": r[2], "upload_date": r[3], "status": r[4]} for r in rows]


def get_questionnaire_questions(q_id: str) -> list[dict[str, Any]]:
    rows = execute_read("SELECT id, questionnaire_id, question, category, suggested_answer, source_evidence, confidence, risk_level, review_status, final_answer FROM questionnaire_questions WHERE questionnaire_id = ?", (q_id,))
    return [
        {
            "id": r[0], "questionnaire_id": r[1], "question": r[2], "category": r[3],
            "suggested_answer": r[4], "source_evidence": r[5], "confidence": r[6],
            "risk_level": r[7], "review_status": r[8], "final_answer": r[9]
        }
        for r in rows
    ]


def update_questionnaire_question(q_id: str, suggested_answer: str, confidence: float, review_status: str, final_answer: str = "") -> None:
    execute_write(
        "UPDATE questionnaire_questions SET suggested_answer = ?, confidence = ?, review_status = ?, final_answer = ? WHERE id = ?",
        (suggested_answer, confidence, review_status, final_answer, q_id)
    )


def get_approved_answers() -> list[dict[str, Any]]:
    rows = execute_read("SELECT id, question, answer, category, approved_by, usage_count, is_public FROM approved_answers")
    return [
        {
            "id": r[0], "question": r[1], "answer": r[2], "category": r[3],
            "approved_by": r[4], "usage_count": r[5], "is_public": bool(r[6])
        }
        for r in rows
    ]


def add_approved_answer(answer_id: str, question: str, answer: str, category: str, approved_by: str, is_public: int = 1) -> None:
    execute_write(
        "INSERT OR REPLACE INTO approved_answers (id, question, answer, category, approved_by, is_public) VALUES (?, ?, ?, ?, ?, ?)",
        (answer_id, question, answer, category, approved_by, is_public)
    )
    add_audit_log("ANSWER_APPROVE", f"Added approved response template for: {question[:40]}...")


def get_policies() -> list[dict[str, Any]]:
    rows = execute_read("SELECT id, name, owner, scope, commitments, status, upload_date FROM policies")
    return [
        {
            "id": r[0], "name": r[1], "owner": r[2], "scope": r[3],
            "commitments": r[4], "status": r[5], "upload_date": r[6]
        }
        for r in rows
    ]


def get_policy_findings(policy_id: str | None = None) -> list[dict[str, Any]]:
    if policy_id:
        rows = execute_read("SELECT id, policy_id, severity, finding, recommendation FROM policy_findings WHERE policy_id = ?", (policy_id,))
    else:
        rows = execute_read("SELECT id, policy_id, severity, finding, recommendation FROM policy_findings")
    return [{"id": r[0], "policy_id": r[1], "severity": r[2], "finding": r[3], "recommendation": r[4]} for r in rows]


def get_trust_center_items() -> list[dict[str, Any]]:
    rows = execute_read("SELECT id, category, title, description, status, updated_at FROM trust_center_items")
    return [
        {
            "id": r[0], "category": r[1], "title": r[2], "description": r[3],
            "status": r[4], "updated_at": r[5]
        }
        for r in rows
    ]


def add_trust_center_item(item_id: str, category: str, title: str, description: str, status: str) -> None:
    updated_at = datetime.now(timezone.utc).isoformat()
    execute_write(
        "INSERT OR REPLACE INTO trust_center_items (id, category, title, description, status, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (item_id, category, title, description, status, updated_at)
    )


def update_trust_center_item(item_id: str, status: str) -> None:
    updated_at = datetime.now(timezone.utc).isoformat()
    execute_write("UPDATE trust_center_items SET status = ?, updated_at = ? WHERE id = ?", (status, updated_at, item_id))
    add_audit_log("TRUST_CENTER_UPDATE", f"Trust center item {item_id} status updated to {status}")


def get_audit_packages() -> list[dict[str, Any]]:
    rows = execute_read("SELECT id, framework_id, audit_period, export_format, download_url, created_at FROM audit_packages")
    return [
        {
            "id": r[0], "framework_id": r[1], "audit_period": r[2],
            "export_format": r[3], "download_url": r[4], "created_at": r[5]
        }
        for r in rows
    ]


def add_audit_package(pkg_id: str, framework_id: str, audit_period: str, export_format: str, download_url: str) -> None:
    created_at = datetime.now(timezone.utc).isoformat()
    execute_write(
        "INSERT OR REPLACE INTO audit_packages (id, framework_id, audit_period, export_format, download_url, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (pkg_id, framework_id, audit_period, export_format, download_url, created_at)
    )
    add_audit_log("AUDIT_PACKAGE_GENERATE", f"Generated audit package for {framework_id} ({audit_period})")


def get_ai_systems() -> list[dict[str, Any]]:
    rows = execute_read("SELECT id, name, model, data_processed, risk_level, logging_enabled, oversight FROM ai_systems")
    return [
        {
            "id": r[0], "name": r[1], "model": r[2], "data_processed": r[3],
            "risk_level": r[4], "logging_enabled": bool(r[5]), "oversight": r[6]
        }
        for r in rows
    ]


def add_ai_system(sys_id: str, name: str, model: str, data_processed: str, risk_level: str, logging_enabled: int, oversight: str) -> None:
    execute_write(
        "INSERT OR REPLACE INTO ai_systems (id, name, model, data_processed, risk_level, logging_enabled, oversight) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (sys_id, name, model, data_processed, risk_level, logging_enabled, oversight)
    )
    add_audit_log("AI_SYSTEM_ADD", f"Registered AI system: {name} (Risk: {risk_level})")


def update_ai_system(sys_id: str, risk_level: str, logging_enabled: int, oversight: str) -> None:
    execute_write(
        "UPDATE ai_systems SET risk_level = ?, logging_enabled = ?, oversight = ? WHERE id = ?",
        (risk_level, logging_enabled, oversight, sys_id)
    )


def get_run_logs() -> list[dict[str, Any]]:
    rows = execute_read("SELECT id, operation, input_summary, output_summary, provider, latency_ms, status, timestamp FROM run_logs ORDER BY timestamp DESC LIMIT 100")
    return [
        {
            "id": r[0], "operation": r[1], "input_summary": r[2], "output_summary": r[3],
            "provider": r[4], "latency_ms": r[5], "status": r[6], "timestamp": r[7]
        }
        for r in rows
    ]


def get_audit_logs() -> list[dict[str, Any]]:
    rows = execute_read("SELECT id, event_type, details, timestamp FROM audit_logs ORDER BY timestamp DESC LIMIT 200")
    return [{"id": r[0], "event_type": r[1], "details": r[2], "timestamp": r[3]} for r in rows]


def get_eval_runs() -> list[dict[str, Any]]:
    rows = execute_read("SELECT id, eval_type, dataset_name, accuracy, summary, timestamp FROM eval_runs ORDER BY timestamp DESC")
    return [
        {
            "id": r[0], "eval_type": r[1], "dataset_name": r[2],
            "accuracy": r[3], "summary": r[4], "timestamp": r[5]
        }
        for r in rows
    ]


def add_eval_run(run_id: str, eval_type: str, dataset_name: str, accuracy: float, summary: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    execute_write(
        "INSERT INTO eval_runs (id, eval_type, dataset_name, accuracy, summary, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (run_id, eval_type, dataset_name, accuracy, summary, timestamp)
    )

