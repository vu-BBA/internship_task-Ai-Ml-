"""
llm.py — Unified LLM interface.

Supports OpenAI (GPT-3.5) and Hugging Face (Mistral-7B, free).
Switch providers by setting LLM_PROVIDER in your .env file.

Both providers expose the same function signature:
    get_response(messages: list[dict]) -> str

So the rest of the app never needs to know which provider is active.
"""

import os
import sys
import time
import requests
from config import (
    LLM_PROVIDER,
    OPENAI_API_KEY, OPENAI_MODEL,
    HF_TOKEN, HF_MODEL,
    OPENROUTER_API_KEY, OPENROUTER_MODEL,
    GEMINI_API_KEY, GEMINI_MODEL,
    GROQ_API_KEY, GROQ_MODEL,
    TEMPERATURE, MAX_TOKENS,
)


# ── Validation ─────────────────────────────────────────────────────────────────

def _validate_config():
    """Check required keys are present at startup — fail early with a clear error."""
    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            sys.exit(
                "❌ OPENAI_API_KEY not found.\n"
                "Add it to your .env file:\n"
                "  OPENAI_API_KEY=sk-your-key-here"
            )
    elif LLM_PROVIDER == "openrouter":
        if not OPENROUTER_API_KEY:
            sys.exit(
                "❌ OPENROUTER_API_KEY not found.\n"
                "Add it to your .env file:\n"
                "  OPENROUTER_API_KEY=your-key-here"
            )
    elif LLM_PROVIDER == "huggingface":
        if not HF_TOKEN:
            sys.exit(
                "❌ HF_TOKEN not found.\n"
                "Add it to your .env file:\n"
                "  HF_TOKEN=hf_your-token-here"
            )
    elif LLM_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            sys.exit(
                "❌ GEMINI_API_KEY not found.\n"
                "Add it to your .env file:\n"
                "  GEMINI_API_KEY=your-key-here"
            )
    elif LLM_PROVIDER == "groq":
        if not GROQ_API_KEY:
            sys.exit(
                "❌ GROQ_API_KEY not found.\n"
                "Add it to your .env file:\n"
                "  GROQ_API_KEY=your-key-here"
            )
    else:
        sys.exit(
            f"❌ Unknown LLM_PROVIDER: '{LLM_PROVIDER}'.\n"
            "Set LLM_PROVIDER to 'openai', 'openrouter', 'huggingface', 'gemini', or 'groq' in .env"
        )

_validate_config()


# ── History trimming ───────────────────────────────────────────────────────────

def trim_history(messages: list, max_turns: int = 10) -> list:
    """
    Keep the system prompt + last `max_turns` conversation turns.
    Prevents hitting the model's context window limit.

    Each "turn" = 1 user message + 1 assistant message = 2 items.
    """
    system_msgs = [m for m in messages if m["role"] == "system"]
    convo_msgs  = [m for m in messages if m["role"] != "system"]

    max_msgs = max_turns * 2
    if len(convo_msgs) > max_msgs:
        convo_msgs = convo_msgs[-max_msgs:]

    return system_msgs + convo_msgs


# ── OpenAI provider ────────────────────────────────────────────────────────────

def _call_openai(messages: list) -> str:
    """Call OpenAI Chat Completions API."""
    from openai import OpenAI, OpenAIError

    client = OpenAI(api_key=OPENAI_API_KEY)

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        return response.choices[0].message.content

    except OpenAIError as e:
        print(f"OpenAI error: {e}")
        return "Sorry, I had trouble reaching the AI service. Please try again."


# ── OpenRouter provider ───────────────────────────────────────────────────────

def _call_openrouter(messages: list) -> str:
    """Call OpenRouter API (uses same library — just different base_url)."""
    from openai import OpenAI

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
    )
    try:
        resp = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        return resp.choices[0].message.content
    except Exception as e:
        print(f"[OpenRouter error] {e}")
        return "Sorry, could not reach the AI service. Please try again."


# ── Google Gemini provider ────────────────────────────────────────────────────

def _call_gemini(messages: list) -> str:
    """Call Google Gemini API."""
    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)

    try:
        gemini_messages = []
        for msg in messages:
            if msg["role"] == "system":
                continue
            role = "user" if msg["role"] == "user" else "model"
            gemini_messages.append({"role": role, "parts": [msg["content"]]})

        resp = model.generate_content(
            gemini_messages,
            generation_config=genai.types.GenerationConfig(
                temperature=TEMPERATURE,
                max_output_tokens=MAX_TOKENS,
            ),
        )
        return resp.text
    except Exception as e:
        print(f"[Gemini error] {e}")
        return "Sorry, could not reach the AI service. Please try again."


# ── Groq provider (FREE) ───────────────────────────────────────────────────────

def _call_groq(messages: list) -> str:
    """Call Groq API (free LLaMA 2 70B model)."""
    from groq import Groq

    client = Groq(api_key=GROQ_API_KEY)

    try:
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        return resp.choices[0].message.content
    except Exception as e:
        print(f"[Groq error] {e}")
        return "Sorry, could not reach the AI service. Please try again."


# ── Hugging Face provider ──────────────────────────────────────────────────────

HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}/v1/chat/completions"
HF_HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}


def _call_huggingface(messages: list, retries: int = 3) -> str:
    """
    Call Hugging Face Inference API (free tier).

    Handles two common free-tier issues automatically:
      - 503: model is loading (cold start) — waits, then retries
      - 429: rate limited — waits 10s, then retries
    """
    payload = {
        "model": HF_MODEL,
        "messages": messages,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "stream": False,
    }

    for attempt in range(retries):
        try:
            resp = requests.post(
                HF_API_URL,
                headers=HF_HEADERS,
                json=payload,
                timeout=60,
            )

            # Model is sleeping (cold start) — wait and retry
            if resp.status_code == 503:
                data = resp.json()
                wait = min(data.get("estimated_time", 20), 40)
                print(f"⏳ Model loading, waiting {wait:.0f}s... (attempt {attempt + 1}/{retries})")
                time.sleep(wait)
                continue

            # Rate limited — wait and retry
            if resp.status_code == 429:
                print(f"⏳ Rate limited, waiting 10s... (attempt {attempt + 1}/{retries})")
                time.sleep(10)
                continue

            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

        except requests.Timeout:
            print(f"⚠️  Request timed out (attempt {attempt + 1}/{retries})")
        except requests.RequestException as e:
            print(f"⚠️  Request error: {e}")

    return (
        "Sorry, the free AI service is temporarily unavailable. "
        "Try again in a moment, or switch to OpenAI by setting "
        "LLM_PROVIDER=openai in your .env file."
    )


# ── Unified public function ────────────────────────────────────────────────────

def get_response(messages: list) -> str:
    """
    Send messages to the active LLM provider and return the reply.

    Args:
        messages: Full conversation history in OpenAI format:
                  [{"role": "system"|"user"|"assistant", "content": "..."}]

    Returns:
        The assistant's reply as a plain string.
    """
    trimmed = trim_history(messages)

    if LLM_PROVIDER == "openrouter":
        return _call_openrouter(trimmed)
    elif LLM_PROVIDER == "openai":
        return _call_openai(trimmed)
    elif LLM_PROVIDER == "gemini":
        return _call_gemini(trimmed)
    elif LLM_PROVIDER == "groq":
        return _call_groq(trimmed)
    else:
        return _call_huggingface(trimmed)


def provider_name() -> str:
    """Human-readable name of the active provider (for UI display)."""
    if LLM_PROVIDER == "openai":
        return f"OpenAI {OPENAI_MODEL}"
    elif LLM_PROVIDER == "openrouter":
        return f"OpenRouter {OPENROUTER_MODEL}"
    elif LLM_PROVIDER == "gemini":
        return f"Google {GEMINI_MODEL}"
    elif LLM_PROVIDER == "groq":
        return f"Groq {GROQ_MODEL} (FREE)"
    return f"HuggingFace {HF_MODEL.split('/')[-1]}"