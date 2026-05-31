"""
config.py — All settings in one place.
Change behaviour here without touching other files.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM Provider ──────────────────────────────────────────
# Set LLM_PROVIDER in your .env to switch between providers
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

# ── OpenAI settings ───────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL   = "gpt-3.5-turbo"

# ── Hugging Face settings (free alternative) ──────────────
HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL  = "mistralai/Mistral-7B-Instruct-v0.2"

# ── OpenRouter settings ───────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL   = "meta-llama/llama-3.3-70b-instruct:free"

# ── Google Gemini settings ────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL   = "gemini-pro"
# ── Groq settings (FREE) ─────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = "llama2-70b-4096"
# ── Generation settings ───────────────────────────────────
TEMPERATURE = 0.3    # low = consistent, safe for health info
MAX_TOKENS  = 350    # keep answers concise

# ── Conversation settings ─────────────────────────────────
MAX_HISTORY_TURNS = 10   # keep last N user+assistant pairs

# ── App settings ──────────────────────────────────────────
APP_TITLE       = "🩺 Health Assistant"
APP_DESCRIPTION = (
    "Ask general health questions in plain English. "
    "This assistant provides **general information only** — "
    "not a substitute for professional medical advice."
)
SHARE_PUBLICLY = True   # set False to run locally only (requires localhost access)