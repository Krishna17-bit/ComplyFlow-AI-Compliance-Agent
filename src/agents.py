from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

from src.frameworks import get_controls
from src.gemini_client import GeminiClient, extract_json
from src.models import (
    AnalysisResult,
    Control,
    ControlMapping,
    Document,
    EvidenceChunk,
    PolicyGap,
    QuestionnaireAnswer,
    RiskItem,
    utc_now_iso,
)
from src.retrieval import EvidenceRetriever, best_quote, chunk_documents, keyword_overlap_score


STATUS_WEIGHT = {"Covered": 1.0, "Partial": 0.55, "Missing": 0.0}


class ComplianceAgent:
    def __init__(self, documents: list[Document], *, use_ai: bool = True) -> None:
        self.documents = documents
        self.chunks = chunk_documents(documents)
        self.llm = GeminiClient()
        self.use_ai = use_ai and self.llm.configured
        self.retriever = EvidenceRetriever(self.chunks, gemini_client=(self.llm if self.use_ai else None))


    def analyze(self, framework_names: list[str], depth: str = "Balanced") -> AnalysisResult:
        controls = get_controls(framework_names)
        local_maps = [self._local_map_control(control) for control in controls]
        mappings = local_maps

        if self.use_ai:
            batch_size = 4 if depth == "Deep" else 6
            enhanced: list[ControlMapping] = []
            for start in range(0, len(local_maps), batch_size):
                batch = local_maps[start : start + batch_size]
                enhanced.extend(self._ai_review_control_batch(batch))
            if len(enhanced) == len(local_maps):
                mappings = enhanced

        gaps = self._generate_gaps(mappings)
        risks = self._generate_risks(mappings)
        score = self._readiness_score(mappings)
        covered = sum(1 for m in mappings if m.status == "Covered")
        partial = sum(1 for m in mappings if m.status == "Partial")
        missing = sum(1 for m in mappings if m.status == "Missing")
        summary = self._executive_summary(mappings, gaps, risks, score)

        return AnalysisResult(
            audit_id=f"CF-{uuid.uuid4().hex[:10].upper()}",
            generated_at=utc_now_iso(),
            documents=[{"title": d.title, "type": d.source_type, "characters": len(d.text), **d.metadata} for d in self.documents],
            frameworks=framework_names,
            control_mappings=mappings,
            gaps=gaps,
            risks=risks,
            readiness_score=score,
            covered_count=covered,
            partial_count=partial,
            missing_count=missing,
            executive_summary=summary,
        )

    def _local_map_control(self, control: Control) -> ControlMapping:
        query = f"{control.framework} {control.name}. {control.objective}. " + " ".join(control.keywords)
        retrieved = self.retriever.search(query, top_k=5)
        evidence: list[dict[str, Any]] = []
        combined_strength = 0.0
        for chunk in retrieved:
            overlap = keyword_overlap_score(chunk.text, control.keywords)
            strength = min(1.0, (chunk.score * 1.8) + overlap)
            if strength <= 0.03 and len(evidence) >= 2:
                continue
            combined_strength += strength
            evidence.append(
                {
                    "evidence_id": chunk.chunk_id,
                    "source_title": chunk.title,
                    "page": chunk.page,
                    "score": round(strength, 3),
                    "quote": best_quote(chunk.text, control.keywords),
                }
            )

        confidence = max(0.0, min(1.0, combined_strength / 2.2))
        if confidence >= 0.55 and len(evidence) >= 2:
            status = "Covered"
        elif confidence >= 0.22 and evidence:
            status = "Partial"
        else:
            status = "Missing"

        missing = []
        actions = []
        if status != "Covered":
            missing = [
                f"Approved evidence for {control.name}",
                "Owner, review date, scope, and operational proof",
            ]
            actions = [
                f"Collect or write evidence showing how {control.name.lower()} is performed.",
                "Add source owner, approval date, and review cadence.",
            ]
        else:
            actions = ["Keep evidence current and attach latest operational proof during audit review."]

        risk_level = "Low" if status == "Covered" else "Medium" if status == "Partial" else "High"
        explanation = (
            f"Evidence appears sufficient for {control.name}." if status == "Covered"
            else f"Some relevant evidence was found for {control.name}, but it does not fully prove operating effectiveness." if status == "Partial"
            else f"No reliable evidence was found for {control.name}."
        )

        return ControlMapping(
            control_id=control.control_id,
            framework=control.framework,
            name=control.name,
            status=status,
            confidence=round(confidence, 2),
            risk_level=risk_level,
            explanation=explanation,
            evidence=evidence[:4],
            missing_evidence=missing,
            improvement_actions=actions,
        )

    def _ai_review_control_batch(self, mappings: list[ControlMapping]) -> list[ControlMapping]:
        payload = []
        for m in mappings:
            payload.append(
                {
                    "control_id": m.control_id,
                    "framework": m.framework,
                    "name": m.name,
                    "current_status": m.status,
                    "current_confidence": m.confidence,
                    "evidence": m.evidence,
                }
            )
        prompt = f"""
You are a strict compliance evidence analyst. Review the proposed control mappings using only the provided evidence quotes.
Do not invent evidence. If evidence is weak, mark Partial or Missing.

CRITICAL EVALUATION RULES FOR AI GOVERNANCE (ISO 42001) & EU AI ACT:
1. For AI System Inventory (AIGOV-INVENTORY) or High-Risk Classification (EUAIACT-HIGH-RISK): The evidence MUST explicitly state the registry/inventory details, owners, and deployment contexts of specific models. General generic assertions without reference to a model list or specific tools are "Partial" or "Missing".
2. For Data Governance & Lineage (AIGOV-DATA or EUAIACT-DATA-GOV): The evidence MUST document training/validation dataset provenance, license checks, or systematic bias checking processes. Standard security policies (e.g. databases are encrypted) do NOT suffice for model data governance; if model-specific data governance is absent, mark "Partial".
3. For Prohibited Practices (EUAIACT-PROHIBITED): Ensure there is an explicit screening policy or ethics check blocking prohibited practices (e.g. social scoring, subliminal influence).

Return strict JSON array. Each item must contain:
control_id, status (Covered|Partial|Missing), confidence (0-1), risk_level (Low|Medium|High|Critical), explanation, missing_evidence array, improvement_actions array.

Mappings:
{json.dumps(payload, indent=2)}
"""
        resp = self.llm.generate(prompt, temperature=0.05, json_mode=True)
        parsed = extract_json(resp.text, []) if resp.ok else []
        if not isinstance(parsed, list):
            return mappings
        by_id = {str(x.get("control_id")): x for x in parsed if isinstance(x, dict)}
        out: list[ControlMapping] = []
        for m in mappings:
            ai = by_id.get(m.control_id)
            if not ai:
                out.append(m)
                continue
            status = ai.get("status", m.status)
            if status not in {"Covered", "Partial", "Missing"}:
                status = m.status
            risk = ai.get("risk_level", m.risk_level)
            if risk not in {"Low", "Medium", "High", "Critical"}:
                risk = m.risk_level
            try:
                conf = float(ai.get("confidence", m.confidence))
            except Exception:
                conf = m.confidence
            out.append(
                ControlMapping(
                    control_id=m.control_id,
                    framework=m.framework,
                    name=m.name,
                    status=status,
                    confidence=round(max(0.0, min(1.0, conf)), 2),
                    risk_level=risk,
                    explanation=str(ai.get("explanation", m.explanation)),
                    evidence=m.evidence,
                    missing_evidence=[str(x) for x in ai.get("missing_evidence", m.missing_evidence)][:5],
                    improvement_actions=[str(x) for x in ai.get("improvement_actions", m.improvement_actions)][:5],
                )
            )
        return out

    def answer_questions(self, questions: list[str]) -> list[QuestionnaireAnswer]:
        questions = [q.strip() for q in questions if q.strip()]
        if not questions:
            return []

        local_answers = [self._local_answer_question(q) for q in questions]
        if not self.use_ai:
            return local_answers

        enhanced: list[QuestionnaireAnswer] = []
        for start in range(0, len(local_answers), 6):
            batch = local_answers[start : start + 6]
            enhanced.extend(self._ai_answer_batch(batch))
        return enhanced if len(enhanced) == len(local_answers) else local_answers

    def _local_answer_question(self, question: str) -> QuestionnaireAnswer:
        chunks = self.retriever.search(question, top_k=6)
        evidence = [
            {
                "evidence_id": c.chunk_id,
                "source_title": c.title,
                "page": c.page,
                "score": round(c.score, 3),
                "quote": best_quote(c.text, question.split()[:10]),
            }
            for c in chunks
            if c.score > 0 or len(chunks) <= 2
        ][:4]
        confidence = round(min(1.0, sum(float(e.get("score", 0)) for e in evidence) * 1.6), 2)
        if confidence >= 0.35 and evidence:
            answer = "Based on the available evidence, this requirement is partially supported. Review the cited evidence before submitting the answer."
            review = True
        else:
            answer = "Not enough approved evidence was found to answer this confidently. Mark this for human review and collect supporting documentation."
            review = True
        return QuestionnaireAnswer(question, answer, confidence, review, evidence, ["Generated from uploaded evidence only."])

    def _ai_answer_batch(self, answers: list[QuestionnaireAnswer]) -> list[QuestionnaireAnswer]:
        payload = [
            {
                "question": a.question,
                "draft_answer": a.answer,
                "evidence": a.evidence,
            }
            for a in answers
        ]
        prompt = f"""
You are a security questionnaire response specialist.
Use only the evidence quotes provided for each question. Do not invent certifications, tools, dates, or commitments.
If evidence is insufficient, say what is missing and mark review_required true.
Return strict JSON array. Each item must include:
question, answer, confidence (0-1), review_required (boolean), assumptions array, evidence_ids array.
Answers should be clear, business-ready, and safe to send after human review.

Questions and evidence:
{json.dumps(payload, indent=2)}
"""
        resp = self.llm.generate(prompt, temperature=0.1, json_mode=True)
        parsed = extract_json(resp.text, []) if resp.ok else []
        if not isinstance(parsed, list):
            return answers
        by_q = {str(x.get("question", "")).strip(): x for x in parsed if isinstance(x, dict)}
        out: list[QuestionnaireAnswer] = []
        for local in answers:
            ai = by_q.get(local.question)
            if not ai:
                out.append(local)
                continue
            try:
                conf = float(ai.get("confidence", local.confidence))
            except Exception:
                conf = local.confidence
            chosen_ids = set(str(x) for x in ai.get("evidence_ids", []))
            evidence = [ev for ev in local.evidence if not chosen_ids or ev.get("evidence_id") in chosen_ids]
            out.append(
                QuestionnaireAnswer(
                    question=local.question,
                    answer=str(ai.get("answer", local.answer)).strip(),
                    confidence=round(max(0.0, min(1.0, conf)), 2),
                    review_required=bool(ai.get("review_required", True)),
                    evidence=evidence or local.evidence,
                    assumptions=[str(x) for x in ai.get("assumptions", local.assumptions)][:5],
                )
            )
        return out

    def _generate_gaps(self, mappings: list[ControlMapping]) -> list[PolicyGap]:
        gaps: list[PolicyGap] = []
        for m in mappings:
            if m.status == "Covered":
                continue
            gaps.append(
                PolicyGap(
                    area=f"{m.framework}: {m.name}",
                    severity="High" if m.status == "Missing" else "Medium",
                    finding=m.explanation,
                    recommendation="; ".join(m.improvement_actions[:2]),
                    linked_controls=[m.control_id],
                )
            )
        return gaps[:18]

    def _generate_risks(self, mappings: list[ControlMapping]) -> list[RiskItem]:
        risks: list[RiskItem] = []
        count = 1
        for m in mappings:
            if m.risk_level in {"High", "Critical"} or m.status == "Missing":
                risks.append(
                    RiskItem(
                        risk_id=f"R-{count:03d}",
                        severity=m.risk_level if m.risk_level in {"High", "Critical"} else "High",
                        area=m.name,
                        issue=f"Insufficient evidence for {m.control_id}.",
                        business_impact="May delay customer security review, audit readiness, certification preparation, or vendor onboarding.",
                        recommended_action="Collect owner-approved policy and operating evidence, then rerun the assessment.",
                        linked_controls=[m.control_id],
                    )
                )
                count += 1
        return risks[:15]

    def _readiness_score(self, mappings: list[ControlMapping]) -> float:
        if not mappings:
            return 0.0
        total = sum(STATUS_WEIGHT.get(m.status, 0.0) * (0.5 + 0.5 * m.confidence) for m in mappings)
        return round((total / len(mappings)) * 100, 1)

    def _executive_summary(self, mappings: list[ControlMapping], gaps: list[PolicyGap], risks: list[RiskItem], score: float) -> str:
        summary = (
            f"Readiness score is {score}%. The assessment found "
            f"{sum(1 for m in mappings if m.status == 'Covered')} covered controls, "
            f"{sum(1 for m in mappings if m.status == 'Partial')} partial controls, and "
            f"{sum(1 for m in mappings if m.status == 'Missing')} missing controls. "
            f"Top priority is to close {len([g for g in gaps if g.severity == 'High'])} high-severity evidence gaps."
        )
        if not self.use_ai:
            return summary
        compact = {
            "score": score,
            "covered": sum(1 for m in mappings if m.status == "Covered"),
            "partial": sum(1 for m in mappings if m.status == "Partial"),
            "missing": sum(1 for m in mappings if m.status == "Missing"),
            "top_gaps": [g.__dict__ for g in gaps[:8]],
            "top_risks": [r.__dict__ for r in risks[:8]],
        }
        prompt = f"""
Write a concise executive compliance readiness summary for leadership. Use only these facts.
Do not mention any model or provider. Do not give legal advice. Include priorities and next actions.

Facts:
{json.dumps(compact, indent=2)}
"""
        resp = self.llm.generate(prompt, temperature=0.2)
        return resp.text.strip() if resp.ok and resp.text.strip() else summary
