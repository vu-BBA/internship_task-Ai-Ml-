"""
app.py — Gradio chatbot UI.

Run with:
    python app.py

Opens at http://localhost:7860
"""

import gradio as gr
from prompt import SYSTEM_PROMPT
from safety import check_input, add_disclaimer
from llm import get_response, provider_name
from config import APP_TITLE, APP_DESCRIPTION, SHARE_PUBLICLY


# ── Core chat function ─────────────────────────────────────────────────────────

def chat(user_message: str, history: list) -> str:
    """
    Main chat handler called by Gradio on every user message.

    Args:
        user_message: What the user typed.
        history:      Gradio's history — list of [user_msg, bot_msg] pairs.

    Returns:
        The assistant's reply as a string.
    """
    # ── Layer 1 & 2: Safety input check ───────────────────
    check = check_input(user_message)
    if not check["allowed"]:
        # Return canned response; Gradio will NOT add it to history
        # since we return before building the messages list
        return check["message"]

    # ── Build full message history for the LLM ─────────────
    # Start with system prompt, then replay the conversation so far
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for user_msg, bot_msg in history:
        messages.append({"role": "user",      "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})

    messages.append({"role": "user", "content": user_message})

    # ── Layer 3: LLM call (safety rules are in the system prompt) ──
    reply = get_response(messages)

    # ── Layer 4: Append disclaimer to every response ────────
    return add_disclaimer(reply)


# ── Build the Gradio UI ────────────────────────────────────────────────────────

def build_ui() -> gr.Blocks:
    with gr.Blocks(title=APP_TITLE) as demo:

        # Header
        gr.Markdown(f"# {APP_TITLE}")
        gr.Markdown(APP_DESCRIPTION)

        # Chat interface
        gr.ChatInterface(
            fn=chat,
            examples=[
                "What causes a sore throat?",
                "What are the symptoms of flu vs a common cold?",
                "How does the immune system fight infections?",
                "Is paracetamol safe for children?",
                "What is hypertension and what causes it?",
                "How much sleep does an adult need?",
            ],
            cache_examples=False,
        )

        # Footer
        gr.Markdown(
            f"<div class='disclaimer'>"
            f"Model: {provider_name()} &nbsp;|&nbsp; "
            f"For emergencies call 115 (Pakistan) / 999 / 911"
            f"</div>"
        )

    return demo


def get_launch_kwargs():
    """Build launch parameters with proper error handling."""
    kwargs = {
        "share": SHARE_PUBLICLY,
        "show_error": True,
        "theme": gr.themes.Soft(),
        "css": """
            .disclaimer {
                font-size: 12px;
                color: #888;
                text-align: center;
                margin-top: 8px;
            }
        """,
    }
    return kwargs


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{'='*50}")
    print(f"  {APP_TITLE}")
    print(f"  Provider: {provider_name()}")
    print(f"{'='*50}\n")

    ui = build_ui()
    ui.launch(**get_launch_kwargs())