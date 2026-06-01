from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass
class Document:
    doc_id: str
    title: str
    source_type: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceChunk:
    chunk_id: str
    doc_id: str
    title: str
    text: str
    page: int | None = None
    score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Control:
    control_id: str
    framework: str
    name: str
    objective: str
    keywords: list[str]


@dataclass
class ControlMapping:
    control_id: str
    framework: str
    name: str
    status: str
    confidence: float
    risk_level: str
    explanation: str
    evidence: list[dict[str, Any]]
    missing_evidence: list[str]
    improvement_actions: list[str]


@dataclass
class QuestionnaireAnswer:
    question: str
    answer: str
    confidence: float
    review_required: bool
    evidence: list[dict[str, Any]]
    assumptions: list[str]


@dataclass
class PolicyGap:
    area: str
    severity: str
    finding: str
    recommendation: str
    linked_controls: list[str]


@dataclass
class RiskItem:
    risk_id: str
    severity: str
    area: str
    issue: str
    business_impact: str
    recommended_action: str
    linked_controls: list[str]


@dataclass
class AnalysisResult:
    audit_id: str
    generated_at: str
    documents: list[dict[str, Any]]
    frameworks: list[str]
    control_mappings: list[ControlMapping]
    gaps: list[PolicyGap]
    risks: list[RiskItem]
    readiness_score: float
    covered_count: int
    partial_count: int
    missing_count: int
    executive_summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "generated_at": self.generated_at,
            "documents": self.documents,
            "frameworks": self.frameworks,
            "control_mappings": [asdict(x) for x in self.control_mappings],
            "gaps": [asdict(x) for x in self.gaps],
            "risks": [asdict(x) for x in self.risks],
            "readiness_score": self.readiness_score,
            "covered_count": self.covered_count,
            "partial_count": self.partial_count,
            "missing_count": self.missing_count,
            "executive_summary": self.executive_summary,
        }


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
