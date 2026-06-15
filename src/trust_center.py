from __future__ import annotations

import pandas as pd
import streamlit as st
from src.database import add_nda_signup, get_nda_signups


def render_trust_center() -> None:
    st.markdown("## Customer Trust & Security Portal")
    st.caption("Self-service compliance audit package repository for prospects and customers.")

    st.divider()

    cols = st.columns(4)
    with cols[0]:
        st.markdown(
            """
        <div class='metric-card' style='text-align: center;'>
            <div class='value' style='font-size:1.35rem;'>◇ SOC 2 Type II</div>
            <div class='label' style='font-size:0.75rem; margin-top:5px;'>Active Audit Period</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with cols[1]:
        st.markdown(
            """
        <div class='metric-card' style='text-align: center;'>
            <div class='value' style='font-size:1.35rem;'>◇ ISO/IEC 27001</div>
            <div class='label' style='font-size:0.75rem; margin-top:5px;'>Information Security</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with cols[2]:
        st.markdown(
            """
        <div class='metric-card' style='text-align: center;'>
            <div class='value' style='font-size:1.35rem;'>◇ GDPR Ready</div>
            <div class='label' style='font-size:0.75rem; margin-top:5px;'>Privacy Assured</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with cols[3]:
        st.markdown(
            """
        <div class='metric-card' style='text-align: center;'>
            <div class='value' style='font-size:1.35rem;'>◇ EU AI Act Compliant</div>
            <div class='label' style='font-size:0.75rem; margin-top:5px;'>Model Integrity</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.divider()

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("### Document Repository")
        st.markdown("Access to these documents is restricted. You must sign the Non-Disclosure Agreement (NDA) to generate download tokens.")

        docs = [
            ("ComplyFlow_SOC_2_Type_II_Report_2026.pdf", "Restricted · Requires NDA"),
            ("ComplyFlow_ISO_27001_Certificate_2026.pdf", "Restricted · Requires NDA"),
            ("ComplyFlow_Annual_Penetration_Test_Summary.pdf", "Restricted · Requires NDA"),
            ("ComplyFlow_Information_Security_Policies_Pack.pdf", "Restricted · Requires NDA"),
        ]

        for name, status in docs:
            st.markdown(
                f"""
                <div style='padding: 12px 16px; border: 1px solid #333; background: #111; border-radius: 12px; margin-bottom: 8px;'>
                    <b>📁 {name}</b><br/>
                    <span style='color: #888; font-size: 0.82rem;'>{status}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        if "nda_signed" not in st.session_state:
            st.session_state.nda_signed = False

        if not st.session_state.nda_signed:
            st.markdown("### Request Document Access (NDA Sign-off)")

            with st.form("nda_form"):
                name = st.text_input("Full Name")
                email = st.text_input("Business Email")
                company = st.text_input("Company Name")

                nda_text = """CONFIDENTIALITY & NON-DISCLOSURE AGREEMENT (NDA)
-----------------------------------------------
By checking the box below and clicking "Sign NDA & Request Access", you agree that all compliance, penetration testing, policies, and audit documents downloaded from this portal are proprietary and confidential to ComplyFlow AI. 

You agree to:
1. Hold all materials in strict confidence.
2. Use materials solely for the purpose of evaluating ComplyFlow AI security controls.
3. Not distribute, copy, or disclose the contents of these documents to any third parties without prior written consent.
4. Revoke access and destroy downloaded materials immediately upon request."""
                st.text_area("NDA Terms", nda_text, height=130, disabled=True)
                agree = st.checkbox("I agree to the confidentiality terms listed above.")
                submit = st.form_submit_button("Sign NDA & Request Access")

                if submit:
                    if not name or not email or not company:
                        st.error("Please fill out all fields.")
                    elif not agree:
                        st.error("You must agree to the NDA terms to request access.")
                    else:
                        nda_hash = add_nda_signup(name, email, company)
                        st.session_state.nda_signed = True
                        st.session_state.nda_hash = nda_hash
                        st.session_state.nda_name = name
                        st.session_state.nda_company = company
                        st.rerun()
        else:
            st.success("NDA Signed & Verified")
            st.markdown(f"**Signatory:** {st.session_state.nda_name}")
            st.markdown(f"**Company:** {st.session_state.nda_company}")
            st.markdown(f"**NDA Signature Hash:** `{st.session_state.nda_hash[:16]}...`")

            st.divider()
            st.markdown("### Download Tokens Active")
            st.info("The following reports are now available for download under the terms of the signed NDA:")

            dummy_soc2_data = "ComplyFlow AI - Sample SOC 2 Type II Compliance Report. This document contains detailed security audit logs, encryption guidelines, IAM structures, and continuous logging evidence compiled securely."
            st.download_button(
                "Download SOC 2 Report (PDF)",
                data=dummy_soc2_data,
                file_name="ComplyFlow_SOC_2_Type_II_Report_2026.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

            dummy_pented_data = "ComplyFlow AI - Penetration Test Report Summary 2026. Zero high or critical findings. All medium vulnerabilities patched within the 30-day remediation SLA."
            st.download_button(
                "Download Pen Test Summary (PDF)",
                data=dummy_pented_data,
                file_name="ComplyFlow_Penetration_Test_2026.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

            reset = st.button("Logout / Clear Access Link")
            if reset:
                st.session_state.nda_signed = False
                st.rerun()

    st.divider()
    st.markdown("### Signed NDA Registry (Audit Ledger)")
    signups = get_nda_signups()
    if signups:
        st.dataframe(pd.DataFrame(signups), use_container_width=True)
    else:
        st.caption("No NDAs signed yet in the ledger.")
