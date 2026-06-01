from __future__ import annotations

import io
import json
import zipfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pandas as pd

from src.models import AnalysisResult, QuestionnaireAnswer


def ensure_outputs(base_dir: Path) -> Path:
    out = base_dir / "outputs"
    out.mkdir(exist_ok=True)
    return out


def mappings_dataframe(result: AnalysisResult) -> pd.DataFrame:
    rows = []
    for m in result.control_mappings:
        rows.append(
            {
                "Framework": m.framework,
                "Control ID": m.control_id,
                "Control": m.name,
                "Status": m.status,
                "Confidence": m.confidence,
                "Risk": m.risk_level,
                "Explanation": m.explanation,
                "Evidence Count": len(m.evidence),
                "Missing Evidence": "; ".join(m.missing_evidence),
                "Improvement Actions": "; ".join(m.improvement_actions),
            }
        )
    return pd.DataFrame(rows)


def gaps_dataframe(result: AnalysisResult) -> pd.DataFrame:
    return pd.DataFrame([asdict(x) for x in result.gaps])


def risks_dataframe(result: AnalysisResult) -> pd.DataFrame:
    return pd.DataFrame([asdict(x) for x in result.risks])


def answers_dataframe(answers: list[QuestionnaireAnswer]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Question": a.question,
                "Answer": a.answer,
                "Confidence": a.confidence,
                "Review Required": a.review_required,
                "Evidence IDs": "; ".join(str(e.get("evidence_id")) for e in a.evidence),
                "Sources": "; ".join(str(e.get("source_title")) for e in a.evidence),
                "Assumptions": "; ".join(a.assumptions),
            }
            for a in answers
        ]
    )


def markdown_report(result: AnalysisResult, answers: list[QuestionnaireAnswer] | None = None) -> str:
    answers = answers or []
    lines = [
        f"# Compliance Readiness Report",
        "",
        f"**Audit ID:** {result.audit_id}",
        f"**Generated:** {result.generated_at}",
        f"**Frameworks:** {', '.join(result.frameworks)}",
        "",
        "## Executive Summary",
        result.executive_summary,
        "",
        "## Readiness Metrics",
        f"- Readiness score: {result.readiness_score}%",
        f"- Covered controls: {result.covered_count}",
        f"- Partial controls: {result.partial_count}",
        f"- Missing controls: {result.missing_count}",
        "",
        "## Control Mapping",
    ]
    for m in result.control_mappings:
        lines.extend(
            [
                f"### {m.control_id} — {m.name}",
                f"- Framework: {m.framework}",
                f"- Status: {m.status}",
                f"- Confidence: {m.confidence}",
                f"- Risk: {m.risk_level}",
                f"- Explanation: {m.explanation}",
                f"- Missing evidence: {'; '.join(m.missing_evidence) if m.missing_evidence else 'None noted'}",
                f"- Actions: {'; '.join(m.improvement_actions)}",
                "",
            ]
        )
        for ev in m.evidence[:3]:
            lines.append(f"> **{ev.get('source_title')}**: {ev.get('quote')}")
            lines.append("")

    lines.extend(["## Risk Register", ""])
    for r in result.risks:
        lines.append(f"- **{r.risk_id} / {r.severity} / {r.area}:** {r.issue} Action: {r.recommended_action}")
    lines.append("")

    if answers:
        lines.extend(["## Security Questionnaire Answers", ""])
        for a in answers:
            lines.extend([f"### {a.question}", a.answer, f"Confidence: {a.confidence}. Review required: {a.review_required}", ""])

    return "\n".join(lines)


def build_audit_zip(result: AnalysisResult, answers: list[QuestionnaireAnswer] | None = None) -> bytes:
    answers = answers or []
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("audit_result.json", json.dumps(result.to_dict(), indent=2, default=str))
        zf.writestr("readiness_report.md", markdown_report(result, answers))
        zf.writestr("control_mapping.csv", mappings_dataframe(result).to_csv(index=False))
        zf.writestr("gaps.csv", gaps_dataframe(result).to_csv(index=False))
        zf.writestr("risk_register.csv", risks_dataframe(result).to_csv(index=False))
        if answers:
            zf.writestr("questionnaire_answers.csv", answers_dataframe(answers).to_csv(index=False))
    mem.seek(0)
    return mem.read()


def save_audit_files(base_dir: Path, result: AnalysisResult, answers: list[QuestionnaireAnswer] | None = None) -> dict[str, Path]:
    out = ensure_outputs(base_dir)
    answers = answers or []
    paths: dict[str, Path] = {}
    paths["json"] = out / f"{result.audit_id}.json"
    paths["json"].write_text(json.dumps(result.to_dict(), indent=2, default=str), encoding="utf-8")
    paths["md"] = out / f"{result.audit_id}_report.md"
    paths["md"].write_text(markdown_report(result, answers), encoding="utf-8")
    paths["control_csv"] = out / f"{result.audit_id}_control_mapping.csv"
    mappings_dataframe(result).to_csv(paths["control_csv"], index=False)
    if answers:
        paths["answers_csv"] = out / f"{result.audit_id}_questionnaire_answers.csv"
        answers_dataframe(answers).to_csv(paths["answers_csv"], index=False)
    return paths
