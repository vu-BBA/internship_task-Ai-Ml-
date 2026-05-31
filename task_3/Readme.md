# 🩺 Health Query Chatbot

A prompt-engineered health information chatbot with safety filters, built with Python + Gradio.

**This README is for the files in** [task_3](task_3/Readme.md#L1).

## Project Layout

```
task_3/
├── .env                  ← your API keys (never commit this)
├── requirements.txt
├── config.py             ← all settings in one place
├── prompt.py             ← system prompt definition
├── safety.py             ← 4-layer safety filter system
├── llm.py                ← unified LLM interface (multiple providers)
├── app.py                ← Gradio UI (run this)
└── tests/
    └── test_safety.py    ← automated safety tests
```

**Supported LLM providers** (set `LLM_PROVIDER` in `.env`):

- `openai`     — OpenAI GPT models (paid)
- `openrouter` — OpenRouter shared Llama models (free but rate-limited)
- `huggingface`— Hugging Face Inference API (free tiers)
- `gemini`     — Google Gemini (requires `google-generativeai` package)
- `groq`       — Groq LLaMA models (free; recommended if you want a no-cost option)

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy the env template and edit keys (do NOT commit `.env`):

```bash
copy .env.example .env   # Windows
# Edit .env to add the keys you need
```

3. Important `.env` variables (examples):

```
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...
HF_TOKEN=hf_...
GEMINI_API_KEY=YOUR_GEMINI_KEY
GROQ_API_KEY=your-groq-key
LLM_PROVIDER=groq
```

4. Run the app:

```bash
python app.py
```

When Gradio launches it may show a local and a public URL (the public share link is created when `SHARE_PUBLICLY=True` in [config.py](config.py#L1)).

## Notes & Troubleshooting

- If a provider fails with network/DNS errors, check your internet connection and any proxy/firewall settings.
- `openrouter`'s free models are often rate-limited upstream; retry or use your own provider key.
- `huggingface` may return 503 while a model cold-starts — the code retries automatically.
- If you see `ModuleNotFoundError` for `google.generativeai`, install it with:

```bash
pip install google-generativeai
```

- To use Groq, install its client (or install all requirements):

```bash
pip install groq
# or
pip install -r requirements.txt
```

## Tests

Run safety tests:

```bash
python -m pytest tests/ -v
```