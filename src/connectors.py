from __future__ import annotations

import json
from src.models import Document, utc_now_iso


def get_aws_config_evidence(simulate_fail: bool = False) -> Document:
    if simulate_fail:
        raise ConnectionError("Failed to connect to AWS Security Hub API. Verify credentials.")

    findings = {
        "connector": "AWS Security Hub Config Sync",
        "timestamp": utc_now_iso(),
        "account_id": "123456789012",
        "region": "us-east-1",
        "checks": [
            {
                "id": "AWS-S3-1",
                "name": "S3 buckets should block public access",
                "status": "PASS",
                "evidence": "All 14 active S3 buckets have Block Public Access enabled at the bucket level.",
                "severity": "CRITICAL",
            },
            {
                "id": "AWS-S3-2",
                "name": "S3 buckets should have server-side encryption enabled",
                "status": "PASS",
                "evidence": "All S3 buckets are configured with default SSE-KMS or SSE-S3 encryption.",
                "severity": "HIGH",
            },
            {
                "id": "AWS-IAM-1",
                "name": "MFA should be enabled for all IAM users with console passwords",
                "status": "PASS",
                "evidence": "All 8 active console users have hardware or virtual MFA devices registered.",
                "severity": "CRITICAL",
            },
            {
                "id": "AWS-IAM-2",
                "name": "IAM root user should have MFA enabled",
                "status": "PASS",
                "evidence": "The AWS account root user is protected by a hardware MFA token.",
                "severity": "CRITICAL",
            },
            {
                "id": "AWS-CLOUDTRAIL-1",
                "name": "CloudTrail should be enabled in all regions",
                "status": "PASS",
                "evidence": "Multi-region CloudTrail 'organization-audit-trail' is active and sending logs to an encrypted S3 bucket.",
                "severity": "HIGH",
            },
            {
                "id": "AWS-KMS-1",
                "name": "KMS customer-managed keys should have rotation enabled",
                "status": "PASS",
                "evidence": "Automatic yearly rotation is enabled for all 5 customer-managed KMS keys.",
                "severity": "MEDIUM",
            },
        ],
    }

    text = (
        "# AWS Configuration Audit Snapshot\n\n"
        f"Generated at: {findings['timestamp']}\n"
        f"AWS Account: {findings['account_id']} | Region: {findings['region']}\n"
        f"Collector: {findings['connector']}\n\n"
        "## Summary of Findings\n\n"
    )
    for check in findings["checks"]:
        text += (
            f"### {check['id']}: {check['name']}\n"
            f"- **Status**: {check['status']}\n"
            f"- **Severity**: {check['severity']}\n"
            f"- **Proof Details**: {check['evidence']}\n\n"
        )

    return Document(
        doc_id="aws-config-snapshot",
        title="AWS Configuration Audit Snapshot",
        source_type="Cloud Config Integration",
        text=text,
        metadata={"account_id": findings["account_id"], "region": findings["region"]},
    )


def get_gcp_config_evidence(simulate_fail: bool = False) -> Document:
    if simulate_fail:
        raise ConnectionError("Failed to connect to GCP Security Command Center API. Verify credentials.")

    findings = {
        "connector": "GCP Security Command Center Config Sync",
        "timestamp": utc_now_iso(),
        "project_id": "complyflow-prod-3829",
        "checks": [
            {
                "id": "GCP-GCS-1",
                "name": "GCS buckets should have uniform bucket-level access enabled",
                "status": "PASS",
                "evidence": "Uniform bucket-level access (UBLA) is enabled on all 9 Google Cloud Storage buckets.",
                "severity": "HIGH",
            },
            {
                "id": "GCP-GCS-2",
                "name": "GCS buckets should be encrypted with Customer-Managed Encryption Keys (CMEK)",
                "status": "PASS",
                "evidence": "All production GCS buckets use KMS-managed keys for envelope encryption.",
                "severity": "HIGH",
            },
            {
                "id": "GCP-IAM-1",
                "name": "MFA/2-Step Verification must be enforced for all users in the Google Workspace domain",
                "status": "PASS",
                "evidence": "Two-step verification enforcement policy is active domain-wide for complyflow.ai.",
                "severity": "CRITICAL",
            },
            {
                "id": "GCP-LOGGING-1",
                "name": "Audit logging should be enabled for all Cloud APIs",
                "status": "PASS",
                "evidence": "Data access audit logs (Admin Write, Data Read, Data Write) are active for all resource types.",
                "severity": "HIGH",
            },
            {
                "id": "GCP-KMS-1",
                "name": "Cloud KMS rotation periods should be 90 days or less",
                "status": "PASS",
                "evidence": "All keys in key ring 'prod-keyring-us' have a rotation schedule of 90 days configured.",
                "severity": "MEDIUM",
            },
        ],
    }

    text = (
        "# GCP Configuration Audit Snapshot\n\n"
        f"Generated at: {findings['timestamp']}\n"
        f"GCP Project: {findings['project_id']}\n"
        f"Collector: {findings['connector']}\n\n"
        "## Summary of Findings\n\n"
    )
    for check in findings["checks"]:
        text += (
            f"### {check['id']}: {check['name']}\n"
            f"- **Status**: {check['status']}\n"
            f"- **Severity**: {check['severity']}\n"
            f"- **Proof Details**: {check['evidence']}\n\n"
        )

    return Document(
        doc_id="gcp-config-snapshot",
        title="GCP Configuration Audit Snapshot",
        source_type="Cloud Config Integration",
        text=text,
        metadata={"project_id": findings["project_id"]},
    )
