"""
safety.py — 4-layer safety filter system.

Layer 1: Input keyword blocklist  → catches obvious harmful requests
Layer 2: Emergency detection      → redirects to emergency services
Layer 3: System prompt rules      → handled in prompt.py / LLM itself
Layer 4: Output disclaimer        → appended to every response
"""

# ── Layer 1: Blocked query patterns ───────────────────────────────────────────
# Queries matching any of these are rejected before the LLM is called.
# Add more patterns as you discover edge cases during testing.

BLOCKED_PATTERNS = [
    # Diagnosis requests
    "diagnose me",
    "do i have",
    "i think i have",
    "is it cancer",
    "am i sick",

    # Dosage / prescribing
    "what dose",
    "what dosage",
    "how many mg",
    "how much should i take",
    "how many should i take",
    "what medication should",
    "prescribe me",
    "prescription for",

    # Stopping prescribed treatment
    "should i stop my medication",
    "can i stop taking",
    "stop taking my",

    # Self-harm
    "suicide",
    "kill myself",
    "end my life",
    "self harm",
    "self-harm",
    "hurt myself",

    # Overdose
    "how to overdose",
    "lethal dose",
    "fatal dose",
]

# ── Layer 2: Emergency detection patterns ──────────────────────────────────────
# These are NOT blocked — they return an urgent redirect to emergency services.
# Never block someone in a real emergency.

EMERGENCY_PATTERNS = [
    "chest pain",
    "chest tightness",
    "can't breathe",
    "cannot breathe",
    "difficulty breathing",
    "not breathing",
    "heart attack",
    "having a stroke",
    "stroke symptoms",
    "unconscious",
    "passed out",
    "severe bleeding",
    "won't stop bleeding",
    "allergic reaction",
    "anaphylaxis",
    "seizure",
    "overdosed",
    "took too many",
    "poisoning",
]

# ── Canned responses ───────────────────────────────────────────────────────────

EMERGENCY_RESPONSE = (
    "🚨 **This sounds like a medical emergency.**\n\n"
    "Please **call emergency services immediately**:\n"
    "- 🇵🇰 Pakistan: **115** (Rescue / Edhi)\n"
    "- 🌍 International: **999** or **911**\n\n"
    "Go to your nearest emergency room or call for an ambulance. "
    "Do not wait — please get help right now."
)

BLOCKED_RESPONSE = (
    "I'm sorry, I'm not able to help with that specific request. "
    "For personal medical advice, diagnosis, or prescriptions, "
    "please consult a qualified healthcare professional such as "
    "a doctor or pharmacist — they're the right people for this."
)

# ── Layer 4: Disclaimer ────────────────────────────────────────────────────────

DISCLAIMER = (
    "\n\n---\n"
    "⚠️ *This is general health information only and does not "
    "constitute medical advice. Please consult a qualified "
    "healthcare professional for advice specific to your situation.*"
)


# ── Public functions ───────────────────────────────────────────────────────────

def check_input(query: str) -> dict:
    """
    Run layers 1 and 2 on the user's input.

    Returns a dict:
        {
          "allowed":  bool,
          "reason":   "ok" | "blocked" | "emergency",
          "message":  str | None   (canned response if not allowed)
        }
    """
    q = query.lower().strip()

    # Layer 2: Emergency check — higher priority than block list
    if any(pattern in q for pattern in EMERGENCY_PATTERNS):
        return {
            "allowed": False,
            "reason":  "emergency",
            "message": EMERGENCY_RESPONSE,
        }

    # Layer 1: Blocked keyword check
    if any(pattern in q for pattern in BLOCKED_PATTERNS):
        return {
            "allowed": False,
            "reason":  "blocked",
            "message": BLOCKED_RESPONSE,
        }

    return {"allowed": True, "reason": "ok", "message": None}


def add_disclaimer(response: str) -> str:
    """
    Layer 4: Append the standard disclaimer to every LLM response.
    This runs unconditionally — every answer gets the disclaimer.
    """
    return response + DISCLAIMER