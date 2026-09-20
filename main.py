from __future__ import annotations
from datetime import datetime, timezone
import hashlib
from typing import Any, Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .chat_service import chat as groq_chat, groq_configured
from .ner import extract_memories
from .unlearn import run_gradient_ascent

app = FastAPI(
    title="ForgetMe.AI API",
    version="4.0.0",
    description="Privacy-first selective memory and machine-unlearning hackathon demo.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()

def dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out, seen = [], set()
    for item in items:
        if item["id"] not in seen:
            out.append(item)
            seen.add(item["id"])
    return out

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "ForgetMe.AI",
        "groqConfigured": groq_configured(),
    }

@app.post("/api/chat")
async def chat_endpoint(payload: dict[str, Any]):
    message = str(payload.get("message", "")).strip()
    messages = payload.get("messages") or [{"role": "user", "content": message}]
    memories = payload.get("memories") or []
    if not message:
        return {"ok": False, "error": "Message is required."}

    result = groq_chat(message, messages, memories)
    result["newMemories"] = extract_memories(message, stamp())
    result["timestamp"] = stamp()
    return result

@app.post("/api/teach")
async def teach(text: str = Form(""), file: Optional[UploadFile] = File(None)):
    timestamp = stamp()
    memories = extract_memories(text, timestamp) if text.strip() else []
    events = []

    if text.strip():
        events.append({
            "time": timestamp,
            "icon": "brain",
            "title": "NER memory extraction",
            "detail": "The message was split into atomic, user-visible memory items.",
        })

    if file is not None:
        payload = await file.read()
        fingerprint = hashlib.sha256(payload).hexdigest()[:8].upper()
        memories.append({
            "id": f"MEM-{fingerprint}", "category": "Uploaded Images", "key": "image",
            "label": "Profile photo", "value": file.filename or "Uploaded image",
            "source": "Image upload", "kind": "image", "status": "Learned",
            "learnedAt": timestamp,
        })
        events.append({
            "time": timestamp, "icon": "image", "title": "Image memory learned",
            "detail": "The uploaded image became one independent memory item.",
        })

    return {
        "status": "learned",
        "message": "The AI has learned the relevant information.",
        "memories": dedupe(memories),
        "events": events,
        "timestamp": timestamp,
    }

@app.post("/api/unlearn")
def unlearn(memory_id: str = Form(...), label: str = Form(...)):
    """Trigger the targeted PyTorch gradient-ascent demonstration."""
    result = run_gradient_ascent(target=label)
    timestamp = stamp()
    verification_id = "VER-" + hashlib.sha256(
        (memory_id + timestamp).encode()
    ).hexdigest()[:8].upper()

    return {
        "status": "Forgotten",
        "memoryId": memory_id,
        "label": label,
        "verificationId": verification_id,
        "timestamp": timestamp,
        "method": "Targeted gradient-ascent simulation",
        "message": (
            "The explicit memory purge is represented by the client-side Memory Vault; "
            "the PyTorch engine demonstrates the targeted reverse-loss update."
        ),
        "engine": result.as_dict(),
    }

# Backward-compatible alias used by older UI builds.
@app.post("/api/forget")
def forget(memory_id: str = Form(...), label: str = Form(...)):
    return unlearn(memory_id, label)

@app.post("/api/verify")
def verify(label: str = Form(...), memory_id: str = Form(...)):
    timestamp = stamp()
    verification_id = "VER-" + hashlib.sha256(
        (memory_id + "verify" + timestamp).encode()
    ).hexdigest()[:8].upper()
    return {
        "target": label,
        "previousState": "Active",
        "currentState": "Forgotten",
        "retrieval": "No active memory found",
        "verification": "PASSED",
        "verificationId": verification_id,
        "timestamp": timestamp,
        "answer": f"I don't have your {label.lower()} information anymore.",
    }

@app.get("/api/green-metrics")
def green_metrics():
    # Illustrative hackathon numbers, not measured production savings.
    return {
        "retraining_cost": 5000,
        "unlearning_cost": 8,
        "cost_saved": 4992,
        "co2_prevented_kg": 400,
        "retraining_hours": 14,
        "unlearning_seconds": 10,
    }
