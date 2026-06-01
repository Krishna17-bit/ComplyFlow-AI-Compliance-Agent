from __future__ import annotations

from src.models import Control


FRAMEWORKS: dict[str, list[Control]] = {
    "SOC 2 Readiness": [
        Control("SOC2-CC1", "SOC 2 Readiness", "Governance and ethical values", "The organization documents security responsibilities, leadership oversight, acceptable conduct, and accountability.", ["governance", "roles", "responsibilities", "security policy", "leadership", "ethics", "accountability"]),
        Control("SOC2-CC2", "SOC 2 Readiness", "Communication and information", "Security expectations, reporting channels, and policy updates are communicated to personnel.", ["communication", "training", "awareness", "policy acknowledgement", "reporting", "employees"]),
        Control("SOC2-CC3", "SOC 2 Readiness", "Risk assessment", "Security, privacy, vendor, and operational risks are identified, assessed, and reviewed.", ["risk assessment", "risk register", "vendor risk", "threat", "likelihood", "impact", "review"]),
        Control("SOC2-CC4", "SOC 2 Readiness", "Monitoring activities", "Controls and system operations are monitored, reviewed, and escalated when issues are detected.", ["monitoring", "review", "metrics", "logging", "alerts", "audit", "control testing"]),
        Control("SOC2-CC5", "SOC 2 Readiness", "Control activities", "Policies and procedures define control activities for operations, access, change, and incident response.", ["procedures", "control", "approval", "policy", "workflow", "segregation", "review"]),
        Control("SOC2-CC6", "SOC 2 Readiness", "Logical access controls", "User access is authorized, reviewed, modified, and removed based on role and business need.", ["access", "mfa", "password", "least privilege", "user review", "joiner", "mover", "leaver", "SSO"]),
        Control("SOC2-CC7", "SOC 2 Readiness", "System operations and incident response", "System events, vulnerabilities, incidents, and availability concerns are detected and handled.", ["incident", "vulnerability", "patch", "alert", "backup", "availability", "response", "root cause"]),
        Control("SOC2-CC8", "SOC 2 Readiness", "Change management", "Application, infrastructure, and configuration changes are reviewed, tested, and approved.", ["change", "pull request", "approval", "testing", "deployment", "rollback", "version control"]),
        Control("SOC2-CC9", "SOC 2 Readiness", "Vendor and third-party risk", "Vendors and subprocessors are evaluated, approved, and periodically reviewed.", ["vendor", "third party", "subprocessor", "supplier", "DPA", "security review", "contract"]),
        Control("SOC2-A1", "SOC 2 Readiness", "Availability and continuity", "Availability commitments are supported by backups, recovery objectives, monitoring, and continuity plans.", ["availability", "backup", "disaster recovery", "RTO", "RPO", "uptime", "continuity"]),
    ],
    "ISO 27001 Readiness": [
        Control("ISO-A5.1", "ISO 27001 Readiness", "Information security policies", "Information security policies are approved, published, reviewed, and aligned with business needs.", ["information security policy", "policy", "reviewed", "approved", "published", "scope"]),
        Control("ISO-A5.15", "ISO 27001 Readiness", "Access control", "Access to information and systems is governed through identity, authorization, and review processes.", ["access control", "identity", "authorization", "MFA", "least privilege", "access review"]),
        Control("ISO-A5.19", "ISO 27001 Readiness", "Supplier relationships", "Supplier security requirements and risk reviews are defined before and during supplier use.", ["supplier", "vendor", "third-party", "contract", "security requirements", "review"]),
        Control("ISO-A5.23", "ISO 27001 Readiness", "Cloud service security", "Cloud service use is governed through approval, configuration, monitoring, and security responsibilities.", ["cloud", "AWS", "Azure", "GCP", "configuration", "shared responsibility", "CSPM"]),
        Control("ISO-A6.3", "ISO 27001 Readiness", "Security awareness and training", "Personnel receive security training and understand reporting obligations.", ["security awareness", "training", "phishing", "onboarding", "employees", "report incident"]),
        Control("ISO-A8.8", "ISO 27001 Readiness", "Management of technical vulnerabilities", "Technical vulnerabilities are identified, prioritized, remediated, and tracked.", ["vulnerability", "patch", "CVE", "scan", "remediation", "SLA"]),
        Control("ISO-A8.9", "ISO 27001 Readiness", "Configuration management", "Configurations are baselined, reviewed, and controlled across infrastructure and applications.", ["configuration", "baseline", "hardening", "infrastructure", "review", "drift"]),
        Control("ISO-A8.15", "ISO 27001 Readiness", "Logging", "Logs are generated, protected, retained, and reviewed for relevant systems.", ["logging", "logs", "retention", "SIEM", "audit trail", "monitoring"]),
        Control("ISO-A8.24", "ISO 27001 Readiness", "Use of cryptography", "Cryptographic controls protect data in transit and at rest.", ["encryption", "TLS", "cryptography", "key management", "at rest", "in transit"]),
        Control("ISO-A8.32", "ISO 27001 Readiness", "Change management", "Changes are reviewed, tested, approved, documented, and reversible when required.", ["change management", "approval", "testing", "deployment", "rollback", "version"]),
    ],
    "GDPR Readiness": [
        Control("GDPR-ROPA", "GDPR Readiness", "Records of processing", "Processing activities, purposes, categories of data, recipients, and retention are documented.", ["processing activity", "personal data", "purpose", "retention", "recipient", "ROPA", "controller", "processor"]),
        Control("GDPR-LAWFUL", "GDPR Readiness", "Lawful basis and transparency", "Processing has documented lawful basis and individuals receive clear privacy information.", ["lawful basis", "consent", "contract", "legitimate interest", "privacy notice", "transparency"]),
        Control("GDPR-DSAR", "GDPR Readiness", "Data subject rights", "Processes exist for access, deletion, correction, portability, objection, and restriction requests.", ["data subject request", "DSAR", "delete", "erasure", "access request", "rectification", "portability"]),
        Control("GDPR-DPIA", "GDPR Readiness", "DPIA and high-risk processing", "High-risk processing is assessed through privacy impact review before launch.", ["DPIA", "privacy impact", "high risk", "assessment", "privacy by design"]),
        Control("GDPR-BREACH", "GDPR Readiness", "Breach notification", "Personal data breaches are detected, assessed, documented, and escalated for notification decisions.", ["breach", "notification", "72 hours", "incident", "personal data", "authority", "data subjects"]),
        Control("GDPR-SUBPROCESS", "GDPR Readiness", "Processors and subprocessors", "Processors and subprocessors are governed by contracts, DPAs, and review processes.", ["processor", "subprocessor", "DPA", "vendor", "contract", "international transfer"]),
        Control("GDPR-RETENTION", "GDPR Readiness", "Retention and deletion", "Personal data retention periods and deletion procedures are defined and applied.", ["retention", "deletion", "data lifecycle", "archive", "purge", "minimization"]),
    ],
    "AI Governance Readiness": [
        Control("AIGOV-INVENTORY", "AI Governance Readiness", "AI system inventory", "AI systems, owners, purpose, users, model dependencies, and deployment context are recorded.", ["AI inventory", "model inventory", "owner", "use case", "AI system", "dependency", "deployment"]),
        Control("AIGOV-RISK", "AI Governance Readiness", "AI risk classification", "AI use cases are classified by risk level and impact before deployment.", ["risk classification", "high risk", "impact", "AI risk", "assessment", "harm", "safety"]),
        Control("AIGOV-DATA", "AI Governance Readiness", "Training and input data governance", "Data provenance, consent, quality, bias, retention, and access are governed.", ["data provenance", "training data", "data quality", "bias", "retention", "dataset", "consent"]),
        Control("AIGOV-EVAL", "AI Governance Readiness", "Model evaluation and validation", "Models are evaluated for accuracy, robustness, bias, security, and intended use.", ["evaluation", "validation", "accuracy", "robustness", "bias", "red team", "test set"]),
        Control("AIGOV-HUMAN", "AI Governance Readiness", "Human oversight", "Human review, escalation, and override are defined for AI-assisted decisions.", ["human oversight", "review", "approval", "override", "escalation", "human in the loop"]),
        Control("AIGOV-TRANSPARENCY", "AI Governance Readiness", "Transparency and user notice", "Users and customers receive appropriate AI use notices and explanation of limitations.", ["transparency", "notice", "AI disclosure", "explainability", "limitations", "customer notice"]),
        Control("AIGOV-MONITORING", "AI Governance Readiness", "Post-deployment monitoring", "AI performance, drift, incidents, misuse, and feedback are monitored after deployment.", ["monitoring", "drift", "incident", "misuse", "feedback", "performance", "post-deployment"]),
        Control("AIGOV-SECURITY", "AI Governance Readiness", "AI security controls", "Prompt injection, data leakage, access, logging, and model abuse risks are controlled.", ["prompt injection", "data leakage", "access control", "AI security", "abuse", "logging", "guardrail"]),
    ],
}


def get_controls(framework_names: list[str]) -> list[Control]:
    controls: list[Control] = []
    for name in framework_names:
        controls.extend(FRAMEWORKS.get(name, []))
    return controls
