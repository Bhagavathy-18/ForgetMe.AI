"""Groq-powered chat service with privacy-aware context construction.

The browser never receives the API key. run_project.bat asks for the key in the
terminal and starts FastAPI with it as a process environment variable.

The important privacy behavior is here: only ACTIVE memories are injected into
the system prompt. Forgotten values are redacted from the conversation messages
before they are sent to Groq, reducing the chance of accidental re-disclosure.
"""
from __future__ import annotations
import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """
You are ForgetMe.AI, a privacy-first personal AI companion and general wellbeing assistant.

STYLE:
- Warm, calm, concise, non-judgmental, and practical.
- You are an AI, not a human, therapist, doctor, or emergency service.
- For ordinary stress, anxiety, study, work, or life questions, provide supportive
  general guidance and encourage appropriate professional support when useful.
- If a user appears to be in immediate danger or describes imminent self-harm,
  encourage contacting local emergency services or a trusted person and seeking
  urgent professional help. Do not present yourself as a crisis service.

PRIVACY / MEMORY RULES:
1. The ACTIVE MEMORY section is the only persistent personal-memory source you may use.
2. Never infer, reconstruct, or reveal the value of a FORGOTTEN memory.
3. If asked about forgotten information, say naturally that you do not have it anymore.
4. Do not say you remember the old value and then "forgot" it.
5. Treat conversation history as context, not as a memory database.
6. Do not expose internal implementation details unless the user asks about the demo.

ACTIVE MEMORY:
{active_memory}

FORGOTTEN MEMORY CATEGORIES:
{forgotten_categories}
""".strip()

def api_key() -> str:
    return os.getenv("GROQ_API_KEY", "").strip()

def groq_configured() -> bool:
    return bool(api_key())

def _memory_lines(memories: list[dict[str, Any]], forgotten: bool = False) -> str:
    status = "Forgotten" if forgotten else "Learned"
    lines = []
    for m in memories:
        if m.get("status") == status:
            if forgotten:
                lines.append(f"- {m.get('label', 'Unknown')}")
            else:
                lines.append(
                    f"- {m.get('label', 'Information')}: {m.get('value', '')} "
                    f"(category: {m.get('category', 'Personal')})"
                )
    return "\n".join(lines) if lines else "- None"

def build_system_prompt(memories: list[dict[str, Any]]) -> str:
    return SYSTEM_PROMPT.format(
        active_memory=_memory_lines(memories),
        forgotten_categories=_memory_lines(memories, True),
    )

def _redact_forgotten(messages: list[dict[str, str]], memories: list[dict[str, Any]]) -> list[dict[str, str]]:
    forgotten_values = [
        str(m.get("value", "")).strip()
        for m in memories
        if m.get("status") == "Forgotten" and str(m.get("value", "")).strip()
    ]
    cleaned = []
    for message in messages[-20:]:
        content = str(message.get("content", ""))
        for value in forgotten_values:
            content = re.sub(re.escape(value), "[forgotten information]", content, flags=re.IGNORECASE)
        cleaned.append({"role": message.get("role", "user"), "content": content})
    return cleaned

def call_groq(messages: list[dict[str, str]], memories: list[dict[str, Any]], temperature: float = 0.55) -> dict[str, Any]:
    key = api_key()
    if not key:
        return {"ok": False, "configured": False, "error": "GROQ_API_KEY is not configured."}

    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": build_system_prompt(memories)},
            *_redact_forgotten(messages, memories),
        ],
        "temperature": temperature,
        "stream": False,
    }

    request = urllib.request.Request(
        GROQ_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            body = json.loads(response.read().decode("utf-8"))
        return {
            "ok": True,
            "configured": True,
            "model": body.get("model", DEFAULT_MODEL),
            "content": body["choices"][0]["message"]["content"],
        }
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "configured": True, "error": f"Groq API error {exc.code}: {detail[:500]}"}
    except Exception as exc:
        return {"ok": False, "configured": True, "error": f"Groq connection error: {exc}"}

def local_fallback(message: str, memories: list[dict[str, Any]]) -> str:
    """Deterministic fallback so the demo remains runnable without a key."""
    q = message.lower()
    active = [m for m in memories if m.get("status") == "Learned"]

    def find(key):
        return next((m for m in active if m.get("key") == key), None)

    if "salary" in q:
        m = find("salary")
        return f"You told me your salary is {m['value']}." if m else "You haven't shared your salary information with me."
    if "age" in q:
        m = find("age")
        return f"You told me you are {m['value']} years old." if m else "You haven't shared your age information with me."
    if "name" in q:
        m = find("name")
        return f"You told me your name is {m['value']}." if m else "You haven't shared your name information with me."
    if "where do i work" in q or "workplace" in q:
        m = find("workplace")
        return f"You told me you work at {m['value']}." if m else "You haven't shared your workplace information with me."
    if "where do i live" in q or "city" in q:
        m = find("city")
        return f"You told me you live in {m['value']}." if m else "You haven't shared your location information with me."
    if any(word in q for word in ["stress", "stressed", "exam", "worried", "anxious"]):
        return "That sounds like a lot to carry. We can break it into smaller steps. What feels most urgent right now?"
    return "I'm here with you. Tell me what you're working through, and I'll help you take the next practical step."

def chat(message: str, messages: list[dict[str, str]], memories: list[dict[str, Any]]) -> dict[str, Any]:
    result = call_groq(messages, memories)
    if result["ok"]:
        return result
    return {
        "ok": True, "configured": result.get("configured", False), "fallback": True,
        "model": "local-demo-fallback", "content": local_fallback(message, memories),
        "api_error": result.get("error"),
    }
