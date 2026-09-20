"""Lightweight, dependency-free NER-style extractor for the hackathon demo.

This is intentionally transparent rather than a black-box transformer. It uses
high-confidence regex patterns for the personal fields demonstrated in the UI.
In a production system, this module could be replaced by spaCy, Presidio, or a
domain-specific NER model while keeping the same Memory Vault contract.
"""
from __future__ import annotations
import re
from typing import Any

FIELD_PATTERNS = [
    ("Identity", "name", "Name", r"\bmy name is\s+([A-Za-z][A-Za-z .'-]{1,40}?)(?=\s+and\b|[,.!?]|$)"),
    ("Personal Information", "age", "Age", r"\b(?:i am|i'm)\s+(\d{1,3})\s*(?:years old)?\b"),
    ("Education", "field_of_study", "Field of study", r"\b(?:i study|i'm studying|my field is)\s+([A-Za-z][A-Za-z &-]{2,50}?)(?=[,.!?]|$)"),
    ("Work", "workplace", "Workplace", r"\b(?:i work at|i work for|my workplace is)\s+([A-Za-z0-9 .&'-]{2,60}?)(?=[,.!?]|$)"),
    ("Location", "city", "City", r"\b(?:i live in|i'm from|my city is)\s+([A-Za-z .'-]{2,50}?)(?=[,.!?]|$)"),
    ("Preferences", "interest", "Interest", r"\b(?:i like|i love|my interest is)\s+([A-Za-z][A-Za-z &'-]{2,50}?)(?=[,.!?]|$)"),
]

MONEY_FIELDS = [
    ("salary", "Salary", r"\b(?:my\s+)?salary\s*(?:is|=|:)?\s*(₹|rs\.?|inr|\$)?\s*([\d,]+(?:\.\d+)?)"),
    ("budget", "Budget", r"\b(?:my\s+)?(?:monthly\s+)?budget\s*(?:is|=|:)?\s*(₹|rs\.?|inr|\$)?\s*([\d,]+(?:\.\d+)?)"),
]

def _memory_id(key: str, value: str) -> str:
    import hashlib
    return "MEM-" + hashlib.sha256(f"{key}:{value}".encode()).hexdigest()[:8].upper()

def _money_value(prefix: str | None, amount: str) -> str:
    prefix = (prefix or "").strip()
    if prefix.lower() in {"rs", "rs.", "inr"}:
        return f"₹{amount}"
    return f"{prefix}{amount}".strip()

def extract_memories(text: str, timestamp: str) -> list[dict[str, Any]]:
    """Extract atomic, user-visible memory objects from one message."""
    found: list[dict[str, Any]] = []

    for category, key, label, pattern in FIELD_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            found.append({
                "id": _memory_id(key, value),
                "category": category, "key": key, "label": label, "value": value,
                "source": "Conversation", "kind": "text", "status": "Learned",
                "learnedAt": timestamp,
            })

    for key, label, pattern in MONEY_FIELDS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = _money_value(match.group(1), match.group(2))
            found.append({
                "id": _memory_id(key, value),
                "category": "Finance", "key": key, "label": label, "value": value,
                "source": "Conversation", "kind": "text", "status": "Learned",
                "learnedAt": timestamp,
            })

    # Deduplicate within one message.
    unique: dict[str, dict[str, Any]] = {}
    for item in found:
        unique[item["id"]] = item
    return list(unique.values())
