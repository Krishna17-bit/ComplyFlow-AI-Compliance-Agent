from __future__ import annotations

import re
from typing import Any

# PII and Secret Regex Definitions
PATTERNS = {
    "API Key / Secret": r"(?:api_key|apikey|secret|password|private_key|token|auth_token|bearer)\s*[:=]\s*['\"][A-Za-z0-9_\-\.\+\=\/]{12,}['\"]",
    "Email Address": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "Phone Number": r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}",
    "Credit Card": r"\b(?:\d[ -]*?){13,16}\b",
    "Restricted Markings": r"\b(CONFIDENTIAL|INTERNAL ONLY|PROPRIETARY|RESTRICTED DO NOT DISTRIBUTE)\b",
    "IP Address": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
}


def scan_text(text: str) -> list[dict[str, Any]]:
    """Scan text and return a list of sensitive findings."""
    findings = []
    if not text:
        return findings

    for label, pattern in PATTERNS.items():
        for match in re.finditer(pattern, text, re.IGNORECASE):
            matched_str = match.group(0)
            
            # Additional heuristic: skip short phone numbers or common digits
            if label == "Phone Number" and len(re.sub(r"\D", "", matched_str)) < 7:
                continue

            findings.append({
                "category": label,
                "text": matched_str,
                "start": match.start(),
                "end": match.end(),
                "severity": "Critical" if label in ("API Key / Secret", "Credit Card") else "Medium"
            })
    return findings


def mask_text(text: str) -> str:
    """Mask PII and secrets in target text."""
    if not text:
        return text

    findings = scan_text(text)
    # Sort findings by start in reverse to replace from end (preserves indices)
    findings.sort(key=lambda x: x["start"], reverse=True)
    
    masked = text
    for f in findings:
        cat = f["category"].upper().replace(" ", "_")
        replacement = f"[{cat}_REDACTED]"
        masked = masked[:f["start"]] + replacement + masked[f["end"]:]
    return masked


def has_sensitive_data(text: str) -> bool:
    """Return true if any sensitive findings are discovered."""
    return len(scan_text(text)) > 0
