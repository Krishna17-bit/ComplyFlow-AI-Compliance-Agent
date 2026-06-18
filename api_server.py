from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

import src.database as db
from src.provider_client import MultiProviderClient
from src.privacy_scanner import scan_text

app = FastAPI(title="ComplyFlow AI REST API", version="1.0.0")

# Schemas
class FrameworkCreate(BaseModel):
    id: str
    name: str
    description: str
    enabled: int = 1

class ControlUpdate(BaseModel):
    status: str
    owner: str = ""
    notes: str = ""

class MappingAction(BaseModel):
    map_id: str
    status: str
    is_approved: int

class TaskCreate(BaseModel):
    framework_id: str
    control_id: str
    gap_id: str
    title: str
    description: str
    owner: str
    due_date: str
    priority: str

class AISystemCreate(BaseModel):
    name: str
    model: str
    data_processed: str
    risk_level: str
    logging_enabled: int
    oversight: str

# Endpoints
@app.get("/health")
def get_health() -> dict[str, Any]:
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat(), "mock_mode": os.getenv("MOCK_MODE", "true")}

@app.get("/api/frameworks")
def get_frameworks() -> list[dict[str, Any]]:
    return db.get_frameworks()

@app.post("/api/frameworks")
def create_framework(fw: FrameworkCreate) -> dict[str, Any]:
    db.execute_write(
        "INSERT OR REPLACE INTO frameworks (id, name, description, enabled) VALUES (?, ?, ?, ?)",
        (fw.id, fw.name, fw.description, fw.enabled)
    )
    db.add_audit_log("FRAMEWORK_CREATE", f"API registered framework: {fw.name}")
    return {"status": "success", "framework_id": fw.id}

@app.get("/api/controls")
def get_controls(framework_id: Optional[str] = None) -> list[dict[str, Any]]:
    return db.get_controls(framework_id)

@app.patch("/api/controls/{id}")
def update_control(id: str, payload: ControlUpdate) -> dict[str, Any]:
    db.update_control_status(id, payload.status, payload.owner, payload.notes)
    return {"status": "success", "control_id": id}

@app.get("/api/evidence")
def get_evidence() -> list[dict[str, Any]]:
    return db.get_evidence_items()

@app.post("/api/evidence")
async def upload_evidence(
    title: str = Form(...),
    description: str = Form(""),
    owner: str = Form("Alice Green"),
    confidentiality: str = Form("internal"),
    file: UploadFile = File(...)
) -> dict[str, Any]:
    content = await file.read()
    text_content = content.decode("utf-8", errors="ignore")
    
    # Scan for sensitive parameters
    findings = scan_text(text_content)
    review_status = "needs_review" if findings else "approved"
    
    item_id = f"EV-{uuid.uuid4().hex[:8].upper()}"
    file_path = f"uploads/{file.filename}"
    
    db.add_evidence_item(
        item_id, title, description, file_path, len(content),
        os.path.splitext(file.filename)[1], "upload", owner,
        datetime.now(timezone.utc).isoformat(),
        (datetime.now(timezone.utc) + timedelta(days=365)).isoformat() if 'timedelta' in globals() else (datetime.now(timezone.utc)).isoformat(),
        "current", confidentiality, text_content
    )
    
    if findings:
        db.add_audit_log("PII_ALERT", f"PII scanner detected credentials or sensitive entries in {title}")
        
    return {
        "status": "success",
        "evidence_id": item_id,
        "review_required": len(findings) > 0,
        "pii_findings_count": len(findings)
    }

@app.delete("/api/evidence/{id}")
def delete_evidence(id: str) -> dict[str, Any]:
    db.delete_evidence_item(id)
    return {"status": "success", "evidence_id": id}

@app.post("/api/mapping/approve")
def approve_mapping(action: MappingAction) -> dict[str, Any]:
    db.update_evidence_control_mapping(action.map_id, action.status, action.is_approved)
    return {"status": "success", "map_id": action.map_id}

@app.get("/api/gaps")
def get_gaps() -> list[dict[str, Any]]:
    return db.get_gaps()

@app.get("/api/tasks")
def get_tasks() -> list[dict[str, Any]]:
    return db.get_remediation_tasks()

@app.post("/api/tasks")
def create_task(task: TaskCreate) -> dict[str, Any]:
    task_id = f"TSK-{uuid.uuid4().hex[:8].upper()}"
    db.add_remediation_task(
        task_id, task.framework_id, task.control_id, task.gap_id,
        task.title, task.description, task.owner, task.due_date, "Open", task.priority
    )
    return {"status": "success", "task_id": task_id}

@app.get("/api/answers/library")
def get_answers_library() -> list[dict[str, Any]]:
    return db.get_approved_answers()

@app.get("/api/policies")
def get_policies() -> list[dict[str, Any]]:
    return db.get_policies()

@app.get("/api/trust-center")
def get_trust_center() -> list[dict[str, Any]]:
    return db.get_trust_center_items()

@app.get("/api/ai-governance/systems")
def get_ai_systems() -> list[dict[str, Any]]:
    return db.get_ai_systems()

@app.post("/api/ai-governance/systems")
def create_ai_system(sys: AISystemCreate) -> dict[str, Any]:
    sys_id = f"AI-SYS-{uuid.uuid4().hex[:8].upper()}"
    db.add_ai_system(sys_id, sys.name, sys.model, sys.data_processed, sys.risk_level, sys.logging_enabled, sys.oversight)
    return {"status": "success", "ai_system_id": sys_id}

@app.get("/api/runs")
def get_run_logs() -> list[dict[str, Any]]:
    return db.get_run_logs()

@app.get("/api/audit-logs")
def get_audit_logs() -> list[dict[str, Any]]:
    return db.get_audit_logs()

@app.get("/api/evals")
def get_evals() -> list[dict[str, Any]]:
    return db.get_eval_runs()

@app.post("/api/settings/providers/test")
def test_provider() -> dict[str, Any]:
    client = MultiProviderClient()
    hc = client.health_check()
    return {"provider": client.provider, "mock_mode": client.mock_mode, "configured": hc["configured"], "error": hc["error"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server.py:app", host="0.0.0.0", port=8000, reload=True)
