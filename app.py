from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from src.agents import ComplianceAgent
from src.document_loader import load_local_folder, load_uploaded_file, parse_questionnaire_file
from src.frameworks import FRAMEWORKS
from src.gemini_client import GeminiClient
from src.models import QuestionnaireAnswer
from src.reporting import (
    answers_dataframe,
    build_audit_zip,
    gaps_dataframe,
    mappings_dataframe,
    markdown_report,
    risks_dataframe,
    save_audit_files,
)
from src.ui_styles import APP_CSS

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = BASE_DIR / "sample_data"

st.set_page_config(
    page_title="ComplyFlow AI",
    page_icon="◇",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(APP_CSS, unsafe_allow_html=True)


def status_class(status: str) -> str:
    return "good" if status == "Covered" else "warn" if status == "Partial" else "bad"


def metric_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='label'>{label}</div>
            <div class='value'>{value}</div>
            <div class='small-muted'>{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def readiness_gauge(score: float) -> None:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "%"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"thickness": 0.28},
                "steps": [
                    {"range": [0, 45], "color": "#202020"},
                    {"range": [45, 75], "color": "#303030"},
                    {"range": [75, 100], "color": "#444444"},
                ],
            },
        )
    )
    fig.update_layout(height=235, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="#111111", font_color="#ffffff")
    st.plotly_chart(fig, use_container_width=True)


def collect_documents(uploaded_files, use_sample: bool):
    docs = []
    errors = []
    if use_sample:
        docs.extend(load_local_folder(SAMPLE_DIR))
    for up in uploaded_files or []:
        try:
            docs.append(load_uploaded_file(up))
        except Exception as exc:
            errors.append(f"{up.name}: {exc}")
    return docs, errors


def render_mapping_card(mapping) -> None:
    st.markdown(
        f"""
        <div class='panel'>
            <span class='status-pill {status_class(mapping.status)}'>{mapping.status}</span>
            <span class='status-pill'>{mapping.framework}</span>
            <h4 style='margin: 10px 0 4px 0;'>{mapping.control_id} — {mapping.name}</h4>
            <p>{mapping.explanation}</p>
            <div class='small-muted'>Confidence: {mapping.confidence} · Risk: {mapping.risk_level}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if mapping.evidence:
        for ev in mapping.evidence:
            st.markdown(
                f"""
                <div class='evidence-card'>
                    <b>{ev.get('source_title')}</b> <span class='small-muted'>· {ev.get('evidence_id')} · score {ev.get('score')}</span>
                    <p>{ev.get('quote')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    if mapping.missing_evidence:
        st.markdown("**Missing evidence to collect**")
        for item in mapping.missing_evidence:
            st.markdown(f"- {item}")
    if mapping.improvement_actions:
        st.markdown("**Recommended actions**")
        for item in mapping.improvement_actions:
            st.markdown(f"- {item}")


def render_answer(answer: QuestionnaireAnswer) -> None:
    st.markdown(
        f"""
        <div class='panel'>
            <h4 style='margin-top:0;'>{answer.question}</h4>
            <p>{answer.answer}</p>
            <span class='status-pill'>Confidence {answer.confidence}</span>
            <span class='status-pill'>{'Review required' if answer.review_required else 'Ready after final check'}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if answer.evidence:
        for ev in answer.evidence:
            st.markdown(
                f"""
                <div class='evidence-card'>
                    <b>{ev.get('source_title')}</b> <span class='small-muted'>· {ev.get('evidence_id')}</span>
                    <p>{ev.get('quote')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    if answer.assumptions:
        st.caption("Assumptions / notes: " + " | ".join(answer.assumptions))


if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "agent_docs" not in st.session_state:
    st.session_state.agent_docs = []
if "questionnaire_answers" not in st.session_state:
    st.session_state.questionnaire_answers = []

client = GeminiClient()

with st.sidebar:
    st.markdown("### ComplyFlow AI")
    st.markdown("Evidence-grounded compliance and security review workspace.")
    st.divider()

    st.markdown("**AI engine**")
    if client.configured:
        st.success("Connected")
    else:
        st.warning("Local fallback active")
        st.caption("Add your key to `.env` to enable AI-assisted analysis.")

    st.divider()
    st.markdown("**What it can process**")
    st.markdown("- Policies and SOPs\n- PDF/DOCX/TXT evidence\n- CSV/XLSX exports\n- Security questionnaires\n- Vendor and AI governance docs")
    st.divider()
    st.markdown("**Outputs**")
    st.markdown("- Control mapping\n- Missing evidence\n- Risk register\n- Questionnaire answers\n- Audit package export")

st.markdown(
    """
    <div class='hero'>
        <h1>ComplyFlow AI</h1>
        <p>Compliance evidence and security questionnaire agent for control mapping, audit-ready citations, missing evidence detection, policy gap review, risk tracking, and grounded response drafting.</p>
        <span class='status-pill'>Evidence-grounded</span>
        <span class='status-pill'>Human review gates</span>
        <span class='status-pill'>Audit package export</span>
        <span class='status-pill'>Questionnaire automation</span>
    </div>
    """,
    unsafe_allow_html=True,
)

setup_cols = st.columns([1.2, 1, 1])
with setup_cols[0]:
    st.markdown("### 1. Select frameworks")
    selected_frameworks = st.multiselect(
        "Frameworks",
        list(FRAMEWORKS.keys()),
        default=["SOC 2 Readiness", "ISO 27001 Readiness", "AI Governance Readiness"],
        label_visibility="collapsed",
    )
with setup_cols[1]:
    st.markdown("### 2. Analysis depth")
    depth = st.radio("Depth", ["Fast", "Balanced", "Deep"], index=1, horizontal=True, label_visibility="collapsed")
    use_sample = st.checkbox("Include sample evidence", value=True)
with setup_cols[2]:
    st.markdown("### 3. Run")
    st.caption("Upload files below, then run the assessment.")

uploaded_files = st.file_uploader(
    "Upload evidence files",
    accept_multiple_files=True,
    type=["pdf", "docx", "txt", "md", "csv", "xlsx", "xls", "json"],
)

run_col, save_col = st.columns([1, 1])
with run_col:
    run = st.button("Run compliance analysis", use_container_width=True, type="primary")
with save_col:
    clear = st.button("Clear session", use_container_width=True)

if clear:
    st.session_state.analysis_result = None
    st.session_state.agent_docs = []
    st.session_state.questionnaire_answers = []
    st.rerun()

if run:
    docs, load_errors = collect_documents(uploaded_files, use_sample)
    if load_errors:
        for err in load_errors:
            st.error(err)
    if not selected_frameworks:
        st.error("Select at least one framework.")
    elif not docs:
        st.error("Upload at least one document or keep sample evidence enabled.")
    else:
        with st.spinner("Analyzing evidence, mapping controls, and building risk register..."):
            agent = ComplianceAgent(docs, use_ai=True)
            result = agent.analyze(selected_frameworks, depth=depth)
            st.session_state.analysis_result = result
            st.session_state.agent_docs = docs
            st.session_state.questionnaire_answers = []
            save_audit_files(BASE_DIR, result)
        st.success("Analysis complete.")

result = st.session_state.analysis_result
answers = st.session_state.questionnaire_answers

if result:
    st.divider()
    cols = st.columns([1, 1, 1, 1])
    with cols[0]:
        metric_card("Readiness", f"{result.readiness_score}%", "Evidence-backed readiness score")
    with cols[1]:
        metric_card("Covered", str(result.covered_count), "Controls with usable evidence")
    with cols[2]:
        metric_card("Partial", str(result.partial_count), "Evidence needs strengthening")
    with cols[3]:
        metric_card("Missing", str(result.missing_count), "No reliable evidence found")

    tabs = st.tabs(["Dashboard", "Control Mapping", "Questionnaire", "Policy Gaps", "Risk Register", "Evidence Library", "Audit Package"])

    with tabs[0]:
        left, right = st.columns([1.3, 1])
        with left:
            st.markdown("### Executive summary")
            st.markdown(f"<div class='panel'><p>{result.executive_summary}</p></div>", unsafe_allow_html=True)
            st.markdown("### Documents reviewed")
            doc_df = pd.DataFrame(result.documents)
            st.dataframe(doc_df, use_container_width=True)
        with right:
            st.markdown("### Readiness gauge")
            readiness_gauge(result.readiness_score)
            status_df = pd.DataFrame(
                {
                    "Status": ["Covered", "Partial", "Missing"],
                    "Count": [result.covered_count, result.partial_count, result.missing_count],
                }
            )
            st.bar_chart(status_df.set_index("Status"))

    with tabs[1]:
        st.markdown("### Control mapping")
        df = mappings_dataframe(result)
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "Download control mapping CSV",
            data=df.to_csv(index=False),
            file_name=f"{result.audit_id}_control_mapping.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.markdown("### Evidence-backed control details")
        fw_filter = st.selectbox("Filter by framework", ["All"] + result.frameworks)
        status_filter = st.selectbox("Filter by status", ["All", "Covered", "Partial", "Missing"])
        for mapping in result.control_mappings:
            if fw_filter != "All" and mapping.framework != fw_filter:
                continue
            if status_filter != "All" and mapping.status != status_filter:
                continue
            with st.expander(f"{mapping.control_id} · {mapping.name} · {mapping.status}"):
                render_mapping_card(mapping)

    with tabs[2]:
        st.markdown("### Security questionnaire assistant")
        st.caption("Paste questions manually or upload a CSV/XLSX/TXT questionnaire. Answers are grounded only in the evidence library.")
        default_questions = """Do you enforce multi-factor authentication for administrative access?
How often are user access rights reviewed?
Do you encrypt customer data in transit and at rest?
Describe your incident response process.
Do you maintain an inventory and risk review process for AI systems?
How are vendors and subprocessors reviewed?"""
        q_text = st.text_area("Questions", value=default_questions, height=170)
        q_upload = st.file_uploader("Optional questionnaire file", type=["csv", "xlsx", "xls", "txt", "md"], key="questionnaire_upload")
        answer_btn = st.button("Generate grounded answers", use_container_width=True)
        if answer_btn:
            questions = [q.strip() for q in q_text.splitlines() if q.strip()]
            if q_upload is not None:
                try:
                    questions.extend(parse_questionnaire_file(q_upload))
                except Exception as exc:
                    st.error(f"Could not parse questionnaire file: {exc}")
            questions = list(dict.fromkeys(questions))
            with st.spinner("Retrieving evidence and drafting answers..."):
                agent = ComplianceAgent(st.session_state.agent_docs, use_ai=True)
                st.session_state.questionnaire_answers = agent.answer_questions(questions)
                answers = st.session_state.questionnaire_answers
                save_audit_files(BASE_DIR, result, answers)
            st.success("Answers generated.")

        if answers:
            ans_df = answers_dataframe(answers)
            st.dataframe(ans_df, use_container_width=True)
            st.download_button(
                "Download questionnaire answers CSV",
                data=ans_df.to_csv(index=False),
                file_name=f"{result.audit_id}_questionnaire_answers.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.markdown("### Answer details")
            for ans in answers:
                with st.expander(ans.question):
                    render_answer(ans)

    with tabs[3]:
        st.markdown("### Missing evidence and policy gaps")
        gaps_df = gaps_dataframe(result)
        if gaps_df.empty:
            st.success("No major policy gaps detected from selected frameworks.")
        else:
            st.dataframe(gaps_df, use_container_width=True)
            st.download_button(
                "Download gaps CSV",
                data=gaps_df.to_csv(index=False),
                file_name=f"{result.audit_id}_gaps.csv",
                mime="text/csv",
                use_container_width=True,
            )
            for gap in result.gaps:
                st.markdown(
                    f"""
                    <div class='panel'>
                        <span class='status-pill'>{gap.severity}</span>
                        <h4 style='margin: 10px 0 4px 0;'>{gap.area}</h4>
                        <p><b>Finding:</b> {gap.finding}</p>
                        <p><b>Recommendation:</b> {gap.recommendation}</p>
                        <div class='small-muted'>Linked controls: {', '.join(gap.linked_controls)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tabs[4]:
        st.markdown("### Risk register")
        risks_df = risks_dataframe(result)
        if risks_df.empty:
            st.success("No high-priority risks generated from current evidence.")
        else:
            st.dataframe(risks_df, use_container_width=True)
            st.download_button(
                "Download risk register CSV",
                data=risks_df.to_csv(index=False),
                file_name=f"{result.audit_id}_risk_register.csv",
                mime="text/csv",
                use_container_width=True,
            )
            for risk in result.risks:
                st.markdown(
                    f"""
                    <div class='risk-card'>
                        <span class='status-pill'>{risk.risk_id}</span>
                        <span class='status-pill'>{risk.severity}</span>
                        <h4 style='margin: 10px 0 4px 0;'>{risk.area}</h4>
                        <p><b>Issue:</b> {risk.issue}</p>
                        <p><b>Business impact:</b> {risk.business_impact}</p>
                        <p><b>Action:</b> {risk.recommended_action}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tabs[5]:
        st.markdown("### Evidence library")
        st.caption("These are the documents the agent used for retrieval and citations.")
        for doc in st.session_state.agent_docs:
            with st.expander(f"{doc.title} · {doc.source_type} · {len(doc.text):,} characters"):
                st.write(doc.text[:6000])

    with tabs[6]:
        st.markdown("### Audit package")
        st.caption("Export a complete package containing JSON, report markdown, control mapping CSV, gaps, risks, and questionnaire answers if generated.")
        audit_json = json.dumps(result.to_dict(), indent=2, default=str)
        st.code(audit_json[:15000], language="json")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button(
                "Download audit JSON",
                data=audit_json,
                file_name=f"{result.audit_id}.json",
                mime="application/json",
                use_container_width=True,
            )
        with c2:
            st.download_button(
                "Download markdown report",
                data=markdown_report(result, answers),
                file_name=f"{result.audit_id}_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with c3:
            st.download_button(
                "Download full audit ZIP",
                data=build_audit_zip(result, answers),
                file_name=f"{result.audit_id}_audit_package.zip",
                mime="application/zip",
                use_container_width=True,
            )
else:
    st.divider()
    st.markdown("### How to test")
    st.markdown(
        """
        1. Keep **Include sample evidence** enabled.
        2. Select **SOC 2 Readiness**, **ISO 27001 Readiness**, and **AI Governance Readiness**.
        3. Click **Run compliance analysis**.
        4. Open **Control Mapping** to verify source quotes and missing evidence.
        5. Open **Questionnaire** and click **Generate grounded answers**.
        6. Open **Audit Package** and download the ZIP.
        """
    )
    st.info("For real use, upload your policies, security questionnaire, vendor evidence, access reviews, incident records, cloud configuration exports, and AI governance docs.")

st.divider()
st.caption("Human review is required before submitting audit responses, legal claims, customer security answers, or compliance representations.")
