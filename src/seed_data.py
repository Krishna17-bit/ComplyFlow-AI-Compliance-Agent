from __future__ import annotations

import sqlite3
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from src.database import DB_PATH, init_db, reset_db


def seed_database() -> None:
    # Reinitialize database
    reset_db()

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    now = datetime.now(timezone.utc).isoformat()
    past_10_days = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    future_30_days = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

    # 1. Frameworks
    frameworks = [
        ("SOC2", "SOC 2 Readiness", "System and Organization Controls criteria for security, availability, and confidentiality.", 1),
        ("ISO27001", "ISO 27001 Readiness", "Information Security Management System (ISMS) international standard controls.", 1),
        ("GDPR", "GDPR Readiness", "General Data Protection Regulation requirements for data controller and processor privacy.", 1),
        ("AIGOV", "AI Governance Readiness", "Framework mapping model inventory, risk criteria, data validation, and oversight.", 1),
        ("EUAIACT", "EU AI Act Readiness", "Compliance controls matching transparency, prohibited practices, and high-risk logs.", 1)
    ]
    cursor.executemany("INSERT OR REPLACE INTO frameworks (id, name, description, enabled) VALUES (?, ?, ?, ?)", frameworks)

    # 2. Controls (30 controls total)
    controls = [
        # SOC 2 (10)
        ("SOC2-CC1", "SOC2", "Governance", "Governance and ethical values", "Documents security responsibilities and ethics.", "Establish a code of conduct and security charter.", "Covered", "Jane Doe", now, "Meets criteria."),
        ("SOC2-CC2", "SOC2", "Governance", "Communication and information", "Communicates policy updates and security awareness rules.", "Provide awareness briefings to staff.", "Covered", "Jane Doe", now, "Meets criteria."),
        ("SOC2-CC3", "SOC2", "Risk", "Risk assessment", "Identifies security and operational risks.", "Conduct a risk review annually.", "Covered", "Bob Smith", now, "Assessed and tracked."),
        ("SOC2-CC4", "SOC2", "Monitoring", "Monitoring activities", "Performs control reviews and alert escalations.", "Review log outputs and alerts daily.", "Partial", "Bob Smith", now, "Logs generated, review periodic."),
        ("SOC2-CC5", "SOC2", "Control", "Control activities", "Defines operational control procedures.", "Standard procedures exist for code changes.", "Covered", "Bob Smith", now, "Written in handbook."),
        ("SOC2-CC6", "SOC2", "Access", "Logical access controls", "Enforces identity management and least-privilege review.", "Enable MFA and SSO access.", "Covered", "Jane Doe", now, "Verified via IAM controls."),
        ("SOC2-CC7", "SOC2", "Incident", "System operations and incident response", "Detects security concerns and processes incidents.", "Document root causes of breaches.", "Covered", "Jane Doe", now, "Playbook active."),
        ("SOC2-CC8", "SOC2", "Change", "Change management", "Approves code changes and tests configuration baselines.", "Require PR approval before merge.", "Covered", "Bob Smith", now, "PR policies active."),
        ("SOC2-CC9", "SOC2", "Vendor", "Vendor and third-party risk", "Conducts supplier checks and vendor evaluations.", "Check vendor SOC 2 reports annually.", "Partial", "Jane Doe", now, "Vendor reviews underway."),
        ("SOC2-A1", "SOC2", "Recovery", "Availability and continuity", "Backs up metadata and tests recovery procedures.", "Verify backup integrity monthly.", "Missing", "Bob Smith", now, "Backup scheduling needed."),

        # ISO 27001 (10)
        ("ISO-A5.1", "ISO27001", "ISMS Policies", "Information security policies", "Maintains information security policies.", "Publish approved security guidelines.", "Covered", "Alice Green", now, "Policies published."),
        ("ISO-A5.15", "ISO27001", "Access", "Access control", "Limits user privileges based on roles.", "Audit administrative permissions quarterly.", "Covered", "Alice Green", now, "Quarterly reviews active."),
        ("ISO-A5.19", "ISO27001", "Suppliers", "Supplier relationships", "Documents supplier security criteria.", "Insert DPAs in vendor vendor agreements.", "Partial", "Alice Green", now, "Contracts being updated."),
        ("ISO-A5.23", "ISO27001", "Cloud", "Cloud service security", "Hardens cloud containers and infrastructure parameters.", "Run automated cloud config scans.", "Covered", "Dan White", now, "Connected to Security Hub."),
        ("ISO-A6.3", "ISO27001", "HR", "Security awareness and training", "Enrolls employees in phishing simulator tests.", "Conduct security onboarding.", "Covered", "Alice Green", now, "Onboarding active."),
        ("ISO-A8.8", "ISO27001", "Vulnerabilities", "Management of technical vulnerabilities", "Patches CVE vulnerabilities inside SLA target bounds.", "Run vulnerability scans weekly.", "Covered", "Dan White", now, "Weekly scanning enabled."),
        ("ISO-A8.9", "ISO27001", "Configuration", "Configuration management", "Locks config drifts and tracks cloud baselines.", "Review base template edits.", "Covered", "Dan White", now, "GitOps workflow active."),
        ("ISO-A8.15", "ISO27001", "Logging", "Logging", "Collects central logs and saves to protected repositories.", "Retain log datasets for 90 days.", "Missing", "Dan White", now, "SIEM setup pending."),
        ("ISO-A8.24", "ISO27001", "Cryptography", "Use of cryptography", "Encrypts databases at rest and in transit.", "Enforce TLS 1.3 parameters.", "Covered", "Dan White", now, "All databases encrypted."),
        ("ISO-A8.32", "ISO27001", "Change", "Change management", "Approves code migrations and infrastructure edits.", "Review testing outcomes before deployment.", "Covered", "Dan White", now, "CICD gates active."),

        # GDPR (5)
        ("GDPR-ROPA", "GDPR", "Privacy", "Records of processing", "Maintains data inventories and record registries.", "Maintain a master ROPA ledger.", "Partial", "Sara Red", now, "ROPA compilation active."),
        ("GDPR-LAWFUL", "GDPR", "Privacy", "Lawful basis and transparency", "Establishes a public privacy statement.", "Publish a cookie opt-out dashboard.", "Covered", "Sara Red", now, "Privacy policy online."),
        ("GDPR-DSAR", "GDPR", "Privacy", "Data subject rights", "Resolves user requests for deletion or export.", "Acknowledge DSARs within 30 days.", "Covered", "Sara Red", now, "DSAR queue active."),
        ("GDPR-DPIA", "GDPR", "Privacy", "DPIA and high-risk processing", "Documents assessments before launching high-risk workflows.", "Conduct DPIA on profiling tools.", "Missing", "Sara Red", now, "DPIA needed for analytics."),
        ("GDPR-BREACH", "GDPR", "Privacy", "Breach notification", "Reports incidents within 72 hours of discovery.", "Create breach escalation playbooks.", "Covered", "Sara Red", now, "Breach guidelines ready."),

        # AI Governance & EU AI Act (5)
        ("AIGOV-INVENTORY", "AIGOV", "AI", "AI system inventory", "Catalogs deployed models and systems.", "Maintain registry of AI models.", "Covered", "Bob Smith", now, "AI Registry live."),
        ("AIGOV-RISK", "AIGOV", "AI", "AI risk classification", "Assesses AI models for risk levels.", "Map models into low, medium, or high risk.", "Partial", "Bob Smith", now, "Classification started."),
        ("AIGOV-DATA", "AIGOV", "AI", "Training and input data governance", "Checks data licenses and validation metrics.", "Track data lineages for models.", "Missing", "Bob Smith", now, "Lineage tracking needed."),
        ("EUAIACT-PROHIBITED", "EUAIACT", "EU AI Act", "Prohibited AI systems screening", "Validates that no prohibited models are deployed.", "Verify no social scoring systems exist.", "Covered", "Alice Green", now, "Verified screening policy."),
        ("EUAIACT-HUMAN", "EUAIACT", "EU AI Act", "Human oversight controls", "Ensures human reviewers can intercept outputs.", "Deploy warning checks on model tools.", "Partial", "Alice Green", now, "Human-in-the-loop active.")
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO controls (id, framework_id, domain, title, description, requirements, status, owner, last_reviewed_at, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, controls)

    # 3. Evidence Items (20 items)
    evidence = [
        ("EV-01", "Information Security Policy Document", "Global security policies covering organizational rules.", "policies/security_policy.md", 3235, "md", "upload", "Alice Green", past_10_days, future_30_days, "current", "internal", now, "approved", "Contains organization roles, password guidelines, and control guidelines."),
        ("EV-02", "Access Control Policy", "IAM onboarding and offboarding guidelines.", "policies/access_policy.md", 2150, "md", "upload", "Alice Green", past_10_days, future_30_days, "current", "internal", now, "approved", "Users are provisioned via least-privilege IAM rules."),
        ("EV-03", "Incident Response Playbook", "Steps for identifying and escalating incidents.", "policies/incident_response_plan.md", 2062, "md", "upload", "Jane Doe", past_10_days, future_30_days, "current", "internal", now, "approved", "Standard escalation timeline requiring breach notification within 72 hours."),
        ("EV-04", "AI Governance and Risk Policy", "Guidelines for model audits and inventory.", "policies/ai_governance_policy.md", 2083, "md", "upload", "Bob Smith", past_10_days, future_30_days, "current", "internal", now, "approved", "AI models are registered and reviewed for bias risks before production deployment."),
        ("EV-05", "IAM User Access Review Log", "Quarterly administrator review CSV.", "evidence/cloud_access_review.csv", 541, "csv", "upload", "Jane Doe", past_10_days, now, "current", "confidential", now, "approved", "Audit log showing MFA active for all administrators."),
        ("EV-06", "Vendor Risk Assessments Register", "Evaluations list for active subprocessors.", "evidence/vendor_register.csv", 372, "csv", "upload", "Jane Doe", past_10_days, now, "current", "internal", now, "approved", "Maintains risk reviews for critical software SaaS tools."),
        ("EV-07", "AWS Security Hub Encryption Settings", "Telemetry sync config details.", "evidence/aws_telemetry.json", 1200, "json", "aws", "Dan White", past_10_days, now, "current", "confidential", now, "approved", "AWS Config shows S3 default encryption enabled and public access blocked."),
        ("EV-08", "Weekly Vulnerability Scan Summary", "Weekly scanner execution result.", "evidence/vulnerability_scan.txt", 890, "txt", "upload", "Dan White", past_10_days, now, "current", "confidential", now, "approved", "All high vulnerabilities patched within remediation SLAs."),
        ("EV-09", "Staff Security Training Logs", "Staff onboarding completions tracker.", "evidence/training_logs.xlsx", 1850, "xlsx", "upload", "Alice Green", past_10_days, future_30_days, "current", "internal", now, "approved", "All active staff completed phishing awareness tests."),
        ("EV-10", "Production Change Ticket Log", "Change tickets and approval history.", "evidence/change_tickets.csv", 1120, "csv", "upload", "Dan White", past_10_days, now, "current", "internal", now, "approved", "PR merges require two administrative code approvals."),
        ("EV-11", "Data Subject Request Log", "Active log of DSAR request responses.", "evidence/dsar_log.csv", 750, "csv", "upload", "Sara Red", past_10_days, now, "current", "confidential", now, "approved", "All user deletion requests completed within GDPR deadlines."),
        ("EV-12", "Disaster Recovery Testing Log", "DR execution drill report.", "evidence/dr_test_report.txt", 1400, "txt", "upload", "Bob Smith", past_10_days, now, "stale", "confidential", now, "approved", "DR failover tested. Backup validation needed."),
        ("EV-13", "SIEM Syslog Configuration File", "Sample server logs file.", "evidence/syslog_config.conf", 430, "conf", "upload", "Dan White", past_10_days, now, "expired", "internal", now, "needs_review", "Needs SIEM target URL configuration."),
        ("EV-14", "DPA Template Agreement", "Data Processing Addendum template.", "evidence/dpa_template.docx", 2500, "docx", "upload", "Sara Red", past_10_days, future_30_days, "current", "public", now, "approved", "Standard DPA including EU Standard Contractual Clauses."),
        ("EV-15", "Cookie Policy Notice screenshot", "Public cookie screen asset.", "evidence/cookie_consent_screenshot.png", 52000, "png", "upload", "Sara Red", past_10_days, future_30_days, "current", "public", now, "approved", "Displays cookie preferences selector widget."),
        ("EV-16", "External Penetration Test Report", "Annual security pentest outcomes.", "evidence/pentest_report.pdf", 4500, "pdf", "upload", "Alice Green", past_10_days, future_30_days, "current", "restricted", now, "approved", "Zero critical findings. All media findings cleared."),
        ("EV-17", "GCP Command Center Security Report", "Telemetry sync config details.", "evidence/gcp_telemetry.json", 950, "json", "gcp", "Dan White", past_10_days, now, "current", "confidential", now, "approved", "MFA enabled for GCP accounts. Uniform bucket settings verified."),
        ("EV-18", "Code Review and QA Policy Guidelines", "Developer workflow parameters policy.", "policies/qa_policy.md", 1100, "md", "upload", "Dan White", past_10_days, future_30_days, "current", "internal", now, "approved", "All releases require automated test verification."),
        ("EV-19", "Ethics and Integrity policy handbook", "Acceptable conduct parameters policy.", "policies/ethics_policy.md", 1300, "md", "upload", "Alice Green", past_10_days, future_30_days, "current", "public", now, "approved", "Defines code of conduct guidelines and whistleblower rules."),
        ("EV-20", "AI Model Inventory Registry CSV", "Registry database file.", "evidence/ai_model_inventory.csv", 620, "csv", "upload", "Bob Smith", past_10_days, future_30_days, "current", "internal", now, "approved", "List of production systems, versions, and validation records.")
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO evidence_items (id, title, description, file_path, file_size, file_type, source, owner, valid_from, valid_to, freshness, confidentiality, upload_date, review_status, content)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, evidence)

    # 4. Evidence-Control Mappings (10 mappings)
    mappings = [
        ("MAP-01", "SOC2-CC1", "EV-01", "Covered", 0.90, "Security responsibility rules mapped clearly in section 1 of the InfoSec Policy.", 0.88, 1),
        ("MAP-02", "SOC2-CC2", "EV-09", "Covered", 0.85, "Staff awareness tracking proved by security onboarding completion logs.", 0.82, 1),
        ("MAP-03", "SOC2-CC3", "EV-04", "Covered", 0.92, "Model risk review guidelines mapped clearly in the AI Governance policy.", 0.90, 1),
        ("MAP-04", "SOC2-CC6", "EV-05", "Covered", 0.88, "User access validations verified in administrator access logs.", 0.84, 1),
        ("MAP-05", "SOC2-CC8", "EV-10", "Covered", 0.95, "PR approvals checked and validated inside production change logs.", 0.92, 1),
        ("MAP-06", "ISO-A5.1", "EV-01", "Covered", 0.90, "Global information security guidelines approved and published.", 0.88, 1),
        ("MAP-07", "ISO-A5.23", "EV-07", "Covered", 0.88, "Cloud configurations synced securely from AWS Security Hub config.", 0.86, 1),
        ("MAP-08", "ISO-A8.8", "EV-08", "Covered", 0.90, "Weekly vulnerability scans verify SLA patching commitments.", 0.85, 1),
        ("MAP-09", "GDPR-LAWFUL", "EV-15", "Covered", 0.85, "Privacy guidelines validated via website cookie settings.", 0.80, 1),
        ("MAP-10", "AIGOV-INVENTORY", "EV-20", "Covered", 0.95, "AI model details catalogs conform with master system register.", 0.92, 1)
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO evidence_control_mappings (id, control_id, evidence_id, status, confidence, explanation, match_score, is_approved)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, mappings)

    # 5. Gaps (10 gaps)
    gaps = [
        ("GAP-01", "SOC2", "SOC2-A1", "High", "No backup validation proof exists. Availability commitments require offsite logs.", "Verify backup logs and add to evidence repository.", "Bob Smith", "Open"),
        ("GAP-02", "ISO27001", "ISO-A8.15", "High", "Server event log retention parameters missing. No central SIEM exists.", "Connect logs to a centralized server and save log exports.", "Dan White", "Open"),
        ("GAP-03", "GDPR", "GDPR-DPIA", "Medium", "High-risk analytics processing lacks a Privacy Impact Assessment (DPIA).", "Execute and log a DPIA assessment for analytical profiling models.", "Sara Red", "Open"),
        ("GAP-04", "AIGOV", "AIGOV-DATA", "High", "Model training dataset provenance records and bias validation reports are missing.", "Compile dataset design papers and license reviews.", "Bob Smith", "Open"),
        ("GAP-05", "SOC2", "SOC2-CC9", "Medium", "No annual review documentation exists for critical software subprocessors.", "Request and review SOC 2 reports from top vendor systems.", "Jane Doe", "In Progress"),
        ("GAP-06", "ISO27001", "ISO-A5.19", "Medium", "Supplier security commitments lack standard Data Processing agreements.", "Insert DPA clauses in vendor agreements.", "Alice Green", "Open"),
        ("GAP-07", "SOC2", "SOC2-CC4", "Medium", "Operational review cycles of cloud alerts lack centralized tracking.", "Establish a log review checklist for weekly reviews.", "Bob Smith", "In Progress"),
        ("GAP-08", "AIGOV", "AIGOV-RISK", "Low", "AI risk classifications are incomplete for newer text helper models.", "Review model inventory parameters and flag risk tiers.", "Bob Smith", "Open"),
        ("GAP-09", "GDPR", "GDPR-ROPA", "Medium", "ROPA data details require validation checks from customer support tools.", "Update support tools record descriptors in ROPA ledger.", "Sara Red", "In Progress"),
        ("GAP-10", "EUAIACT", "EUAIACT-HUMAN", "Medium", "High-risk deployment warning markers lack confirmation.", "Configure manual overrides inside prompt routing tools.", "Alice Green", "Open")
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO gaps (id, framework_id, control_id, severity, explanation, remediation, owner, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, gaps)

    # 6. Remediation Tasks (8 tasks)
    tasks = [
        ("TSK-01", "SOC2", "SOC2-A1", "GAP-01", "Automate S3 Backup Integrity Script", "Create a daily script that verifies backup size and triggers alerts if empty.", "Bob Smith", future_30_days, "Open", "High"),
        ("TSK-02", "ISO27001", "ISO-A8.15", "GAP-02", "Deploy SIEM Syslog Daemon", "Establish SIEM logging connections to production servers.", "Dan White", future_30_days, "Open", "High"),
        ("TSK-03", "GDPR", "GDPR-DPIA", "GAP-03", "Draft DPIA for Analytics Model", "Write the DPIA checklist and submit to DPO review.", "Sara Red", future_30_days, "Open", "Medium"),
        ("TSK-04", "AIGOV", "AIGOV-DATA", "GAP-04", "Publish Model Dataset Provenance Papers", "Verify dataset licenses and store in compliance pack.", "Bob Smith", future_30_days, "Open", "High"),
        ("TSK-05", "SOC2", "SOC2-CC9", "GAP-05", "Collect Vendor SOC 2 Reports", "Email core suppliers for latest security certifications.", "Jane Doe", future_30_days, "In Progress", "Medium"),
        ("TSK-06", "ISO27001", "ISO-A5.19", "GAP-06", "Execute DPA Addendums", "Insert standard privacy commitments in vendor contracts.", "Alice Green", future_30_days, "Open", "Medium"),
        ("TSK-07", "SOC2", "SOC2-CC4", "GAP-07", "Draft Alert Review Checklist", "Establish playbook templates for operational monitoring.", "Bob Smith", future_30_days, "In Progress", "Low"),
        ("TSK-08", "EUAIACT", "EUAIACT-HUMAN", "GAP-10", "Deploy Human Intercept Controls", "Add validation gates before final model pipeline actions.", "Alice Green", future_30_days, "Open", "Medium")
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO remediation_tasks (id, framework_id, control_id, gap_id, title, description, owner, due_date, status, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tasks)

    # 7. Questionnaire & Questions (1 Questionnaire, 20 Questions)
    cursor.execute("""
        INSERT OR REPLACE INTO questionnaires (id, name, type, upload_date, status)
        VALUES ('QNR-01', 'Enterprise Vendor Security Questionnaire', 'Security Questionnaire', ?, 'Completed')
    """, (now,))

    questions = []
    # Generate 20 questions
    categories = ["Access Control", "Encryption", "Incident Response", "Vulnerability Management", "AI Usage", "HR Security"]
    for i in range(1, 21):
        cat = categories[(i - 1) % len(categories)]
        q_text = f"Question {i}: Do you follow industry standards for {cat.lower()} and compliance rules?"
        if i == 1:
            q_text = "Do you enforce multi-factor authentication (MFA) for administrative portal accesses?"
        elif i == 2:
            q_text = "How often do you perform access reviews and user privilege validations?"
        elif i == 3:
            q_text = "Are databases and customer records encrypted at rest and in transit?"
        elif i == 4:
            q_text = "Describe your incident response workflow and breach notification timeline."
        elif i == 5:
            q_text = "How do you screen deployed artificial intelligence (AI) models for security risks?"
        elif i == 6:
            q_text = "Are employees enrolled in security awareness training?"

        ans_text = f"Yes, we enforce safeguards for {cat.lower()}. Detailed evidence exists in our policies."
        confidence = 0.90 if i <= 6 else 0.50
        review_status = "Approved" if i <= 6 else "Needs Review"
        risk_level = "Low" if confidence > 0.8 else "Medium"

        questions.append((
            f"Q-{i:02d}", "QNR-01", q_text, cat, ans_text,
            "EV-01, EV-05" if i == 1 else "EV-02" if i == 2 else "EV-07" if i == 3 else "EV-03" if i == 4 else "EV-04" if i == 5 else "EV-09" if i == 6 else "",
            confidence, risk_level, review_status, ans_text if review_status == "Approved" else ""
        ))
    cursor.executemany("""
        INSERT OR REPLACE INTO questionnaire_questions (id, questionnaire_id, question, category, suggested_answer, source_evidence, confidence, risk_level, review_status, final_answer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, questions)

    # 8. Approved Answers Library (15 items)
    approved_answers = []
    for i in range(1, 16):
        approved_answers.append((
            f"ANS-{i:02d}",
            f"Grounded question variant {i} regarding core GRC controls?",
            f"Approved security answer template {i}. Our practices are aligned with standard SOC 2 criteria.",
            "General Security", "Alice Green", i * 3, 1
        ))
    cursor.executemany("""
        INSERT OR REPLACE INTO approved_answers (id, question, answer, category, approved_by, usage_count, is_public)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, approved_answers)

    # 9. Policies & findings (5 policies, 5 findings)
    policies = [
        ("POL-01", "Information Security Policy", "Alice Green", "All employees and IT assets.", "Centralized passwords, MFA rules, security auditing.", "Active", now),
        ("POL-02", "Access Control Policy", "Alice Green", "Users, administrators, database roles.", "Least-privilege reviews, identity management.", "Active", now),
        ("POL-03", "Incident Response Plan", "Jane Doe", "Security Operations Team, external counsel.", "72-hour breach notification, root cause analysis.", "Active", now),
        ("POL-04", "AI Governance Framework", "Bob Smith", "Model deployment pipeline, software engineers.", "Bias screening, model inventory registry.", "Active", now),
        ("POL-05", "Supplier Relationships Policy", "Alice Green", "Vendors, SaaS subprocessors, agencies.", "Annual SOC 2 checks, DPA contract inclusions.", "Draft", now)
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO policies (id, name, owner, scope, commitments, status, upload_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, policies)

    findings = [
        ("FND-01", "POL-01", "Medium", "Asset Inventory references out-of-date systems.", "Update asset register list in policy annex."),
        ("FND-02", "POL-02", "Medium", "Quarterly IAM audit schedules are loosely defined.", "Specify quarterly review cycle dates."),
        ("FND-03", "POL-03", "Low", "Escalation list lacks updated contact numbers.", "Insert latest security operations hotlines."),
        ("FND-04", "POL-04", "High", "Dataset bias evaluation protocols are omitted.", "Specify statistical bias checking criteria."),
        ("FND-05", "POL-05", "High", "Subprocessor evaluation standards lack strict criteria.", "Establish SOC 2 audit certification targets.")
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO policy_findings (id, policy_id, severity, finding, recommendation)
        VALUES (?, ?, ?, ?, ?)
    """, findings)

    # 10. Trust Center Items (5 items)
    trust_items = [
        ("TRST-01", "Certifications", "SOC 2 Type II Compliance", "Active SOC 2 Type II audit report for our hosted infrastructure services.", "Approved", now),
        ("TRST-02", "Certifications", "ISO/IEC 27001 ISMS Certification", "ISO 27001 certificate showing established secure practices.", "Approved", now),
        ("TRST-03", "Vulnerability", "Annual Penetration Testing Report", "Summary of annual third-party application penetration tests.", "Approved", now),
        ("TRST-04", "Privacy", "GDPR Compliance and DPA Package", "Data Processing Addendum including standard contractual clauses.", "Approved", now),
        ("TRST-05", "AI Safety", "Responsible AI Governance Disclosure", "Transparency statement mapping AI security and model safeguards.", "Approved", now)
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO trust_center_items (id, category, title, description, status, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, trust_items)

    # 11. Audit Packages (2 packages)
    packages = [
        ("PKG-01", "SOC2", "Q1-Q4 2026", "ZIP", "/exports/SOC2_Audit_Package_2026.zip", now),
        ("PKG-02", "ISO27001", "ISMS 2026 Cycle", "ZIP", "/exports/ISO27001_Audit_Package_2026.zip", now)
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO audit_packages (id, framework_id, audit_period, export_format, download_url, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, packages)

    # 12. AI Governance (3 systems)
    ai_systems = [
        ("AI-SYS-01", "Customer Support Chatbot", "Gemini 1.5 Flash", "Customer support transcripts", "Medium", 1, "Review logs weekly. Human-in-the-loop audit trigger enabled."),
        ("AI-SYS-02", "Security Log Classification Classifier", "Custom BERT", "Server metadata logs", "Low", 1, "Automated metrics verification."),
        ("AI-SYS-03", "HR CV Screener Analyzer", "GPT-4o Mini", "Job application resumes", "High", 1, "Human-in-the-loop review mandatory for pipeline outcomes.")
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO ai_systems (id, name, model, data_processed, risk_level, logging_enabled, oversight)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ai_systems)

    # 13. Privacy Scan Results (5 simulated)
    # Stored directly as logs or handled during scan actions

    # 14. Eval Runs (3 runs)
    evals = [
        ("EVL-01", "Evidence-to-Control Mapping", "SOC 2 Sample Dataset", 0.92, "Checked 30 controls against uploaded evidence chunks.", now),
        ("EVL-02", "Questionnaire Answer Accuracy", "Enterprise Vendor Questionnaire v2", 0.88, "Compared 20 drafted answers against approved answer database.", now),
        ("EVL-03", "Sensitive Data Scanner Validation", "Synthetic PII Dataset", 0.95, "Validated regex accuracy on bank records and emails.", now)
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO eval_runs (id, eval_type, dataset_name, accuracy, summary, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, evals)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    seed_database()
    print("Database seeded successfully with 25+ records across all entities!")
