from __future__ import annotations

import hashlib
import json
import pandas as pd
import streamlit as st
from src.database import add_audit_lock, add_auditor_comment, get_audit_locks, get_auditor_comments


def render_auditor_portal(analysis_result) -> None:
    st.markdown("## Collaborative Auditor Portal")
    st.caption("Read-only verification workspace for external third-party reviewers and certification auditors.")

    if not analysis_result:
        st.warning("No analysis result found. Please run the compliance analysis first in the Dashboard tab.")
        return

    st.divider()

    st.markdown("### Cryptographic Audit Freeze")
    st.caption("Locks the current mapping state under an immutable SHA-256 hash signature for audit review verification.")

    lock_cols = st.columns([1.5, 1])
    with lock_cols[0]:
        auditor_name = st.text_input("Lead Auditor Name", value="ISO/SOC Auditor Team")
        lock_btn = st.button("Generate Cryptographic Audit Lock Receipt", use_container_width=True, type="primary")
        if lock_btn:
            if not auditor_name:
                st.error("Please enter the auditor name to sign the lock.")
            else:
                mappings_data = analysis_result.to_dict()
                mappings_data.pop("generated_at", None)
                serialized = json.dumps(mappings_data, sort_keys=True, default=str)
                mappings_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
                signature = f"Signed by {auditor_name} on ComplyFlow Audit Ledger"

                add_audit_lock(analysis_result.audit_id, mappings_hash, signature)
                st.success("Audit Lock successfully written to complyflow.db ledger!")
                st.toast("Audit Lock Receipt Generated.")

    with lock_cols[1]:
        st.markdown(f"**Active Audit ID:** `{analysis_result.audit_id}`")
        st.markdown(f"**Frameworks under Review:** {', '.join(analysis_result.frameworks)}")

    locks = get_audit_locks()
    if locks:
        with st.expander("Show Immutable Audit Lock History Ledger"):
            st.dataframe(pd.DataFrame(locks), use_container_width=True)

    st.divider()

    st.markdown("### Control Verification & Review Logs")
    st.caption("Auditors can review mapped evidence quotes and leave comments or verification status stamps.")

    comments = get_auditor_comments()

    for mapping in analysis_result.control_mappings:
        saved_review = comments.get(mapping.control_id, {})
        saved_status = saved_review.get("status", "Pending Review")
        saved_comment = saved_review.get("comment", "")
        saved_auditor = saved_review.get("auditor_name", "")
        saved_time = saved_review.get("timestamp", "")

        status_color = "#333"
        if saved_status == "Approved":
            status_color = "#1E4620"
        elif saved_status == "Clarification Needed":
            status_color = "#4D3B1D"
        elif saved_status == "Failed":
            status_color = "#5A1E1E"

        with st.expander(f"🔍 {mapping.control_id} · {mapping.name} [System: {mapping.status} | Auditor: {saved_status}]"):
            col1, col2 = st.columns([1.5, 1])
            with col1:
                st.markdown(f"**Description:** {mapping.explanation}")
                if mapping.evidence:
                    st.markdown("**Evidence Quotes:**")
                    for ev in mapping.evidence:
                        st.markdown(
                            f"""
                            <div style='background: #0f0f0f; border-left: 2px solid #555; padding: 6px 12px; margin-bottom: 6px; font-size:0.88rem;'>
                                <b>{ev.get('source_title')}</b> (Chunk: {ev.get('evidence_id')})<br/>
                                <i>"{ev.get('quote')}"</i>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.caption("No evidence mapping quotes available.")

            with col2:
                st.markdown(
                    f"""
                    <div style='background: {status_color}; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px;'>
                        <b>Auditor Status:</b> {saved_status}<br/>
                        <span style='font-size:0.8rem;'>{saved_comment if saved_comment else 'No auditor remarks.'}</span><br/>
                        <span style='font-size:0.75rem; color:#ccc;'>{f'By {saved_auditor} on {saved_time[:10]}' if saved_auditor else ''}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.form(key=f"verify_form_{mapping.control_id}"):
                    review_status = st.selectbox(
                        "Verification Decision",
                        ["Approved", "Clarification Needed", "Failed"],
                        index=(
                            ["Approved", "Clarification Needed", "Failed"].index(saved_status)
                            if saved_status in ["Approved", "Clarification Needed", "Failed"]
                            else 0
                        ),
                    )
                    review_comment = st.text_input("Auditor Review Comments", value=saved_comment)
                    submit_review = st.form_submit_button("Submit Verification Decision")

                    if submit_review:
                        add_auditor_comment(mapping.control_id, review_status, review_comment, auditor_name)
                        st.success(f"Review saved for {mapping.control_id}.")
                        st.rerun()
