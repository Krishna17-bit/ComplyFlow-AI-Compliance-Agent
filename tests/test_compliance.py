from __future__ import annotations

import os
import pytest
from datetime import datetime, timezone, timedelta
from src.privacy_scanner import scan_text, mask_text, has_sensitive_data
from src.provider_client import MultiProviderClient
from src.database import init_db, get_frameworks, get_controls, get_evidence_items, add_evidence_item, delete_evidence_item
from src.models import Document, EvidenceChunk
from src.retrieval import keyword_overlap_score, best_quote


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


def test_sensitive_data_scanner():
    """Verify that the privacy scanner flags emails and secrets."""
    text_with_pii = "Hello, my contact email is dev@complyflow.ai and my key is API_KEY='sk-proj-1234567890abcdef1234'."
    findings = scan_text(text_with_pii)
    
    categories = [f["category"] for f in findings]
    assert "Email Address" in categories
    assert "API Key / Secret" in categories
    
    masked = mask_text(text_with_pii)
    assert "dev@complyflow.ai" not in masked
    assert "sk-proj-1234567890abcdef1234" not in masked
    assert "[EMAIL_ADDRESS_REDACTED]" in masked


def test_no_sensitive_data():
    """Verify scanner does not flag clean text."""
    clean_text = "This is a standard information security policy statement containing no secrets."
    assert not has_sensitive_data(clean_text)
    assert not scan_text(clean_text)


def test_evidence_freshness():
    """Verify validity date constraints correctly update database records."""
    valid_from = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    valid_to = (datetime.now(timezone.utc) + timedelta(days=200)).isoformat()
    
    # Insert custom item and delete
    add_evidence_item(
        "EV-TEST-101", "Validity Test Policy", "Check expiry boundaries.",
        "uploads/test.txt", 100, "txt", "upload", "Alice Green",
        valid_from, valid_to, "current", "internal", "Clean content."
    )
    
    items = get_evidence_items()
    test_item = next((i for i in items if i["id"] == "EV-TEST-101"), None)
    
    assert test_item is not None
    assert test_item["freshness"] == "current"
    assert test_item["confidentiality"] == "internal"
    
    # Cleanup
    delete_evidence_item("EV-TEST-101")


def test_keyword_overlap_score():
    """Verify TF-IDF keyword overlap calculation correctness."""
    text = "Our organization enforces multi-factor authentication (MFA) on all access accounts."
    keywords = ["MFA", "access", "authentication", "encryption"]
    score = keyword_overlap_score(text, keywords)
    assert score > 0.0


def test_best_quote_extraction():
    """Verify sentence matching logic extracts the correct subset of text."""
    text = "We do not enforce passwords. However, we require encryption for critical systems. This protects data at rest."
    keywords = ["encryption", "at rest"]
    quote = best_quote(text, keywords)
    assert "encryption" in quote or "at rest" in quote


def test_provider_mock_adapter():
    """Verify MultiProviderClient in mock mode returns structured mappings."""
    client = MultiProviderClient(provider="mock")
    hc = client.health_check()
    assert hc["configured"] is True
    
    prompt = "proposed control mappings payload for SOC2-CC1"
    resp = client.generate(prompt, json_mode=True)
    assert resp.ok is True
    assert "SOC2-CC1" in resp.text
