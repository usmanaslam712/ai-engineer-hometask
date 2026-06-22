"""
Route a question into exactly one lane: ANSWER | REFUSE | ESCALATE | OUT_OF_SCOPE.
Rules are deterministic keyword checks — no LLM involved.
Order of checks matters: REFUSE > OUT_OF_SCOPE > ESCALATE > ANSWER.

Lane distinctions:
  ANSWER      — covered by knowledge.md or safe customer data
  REFUSE      — customer requests a restricted field (cnic/pan/iban)
  ESCALATE    — problem exists or no approved policy → human agent needed
  OUT_OF_SCOPE — service PayWallet simply doesn't offer (not a support issue)
"""


_OFF_TOPIC_KEYWORDS = [
    "weather", "temperature", "forecast", "rain", "sunny",
    "news", "politics", "political", "situation in", "election", "government",
    "sports", "cricket", "football",
    "recipe", "cook", "food", "restaurant", "khaaney", "khaana",
    "movie", "film", "song", "music", "joke",
    "tell me a", "write me a", "what is the capital", "who is the president",
    "stock price", "share price",
]


def _has(text: str, *keywords: str) -> bool:
    return any(k in text for k in keywords)


def _is_spam(text: str) -> bool:
    """True if the input looks like gibberish or spam rather than a real question."""
    stripped = text.strip()
    if len(stripped) < 3:
        return True
    # Majority of characters are the same (e.g. "aaaaaaa", "!!!!!!")
    if len(stripped) > 3 and max(stripped.count(c) for c in set(stripped)) / len(stripped) > 0.7:
        return True
    # No letters at all
    if not any(c.isalpha() for c in stripped):
        return True
    return False


def route(question: str, customer: dict) -> tuple[str, str]:
    """Return (lane, topic)."""
    q = question.lower()

    # ── SPAM GUARDRAIL ───────────────────────────────────────────────────────
    if _is_spam(q):
        return "OUT_OF_SCOPE", "spam"

    # ── OFF-TOPIC GUARDRAIL ──────────────────────────────────────────────────
    if _has(q, *_OFF_TOPIC_KEYWORDS):
        return "OUT_OF_SCOPE", "off_topic"

    # ── REFUSE ──────────────────────────────────────────────────────────────
    # Customer asks for a restricted field. Hard block regardless of anything else.
    if _has(q, "cnic", "national id", "full card", "card number", "pan", "iban"):
        return "REFUSE", "restricted_fields"

    # ── OUT_OF_SCOPE ─────────────────────────────────────────────────────────
    # Services PayWallet doesn't offer — a clear "no", not a support escalation.
    if _has(q, "crypto", "bitcoin", "ethereum", "btc", "eth", "trading"):
        return "OUT_OF_SCOPE", "crypto"

    # ── ESCALATE ────────────────────────────────────────────────────────────
    if _has(q, "twice", "double", "charged twice", "duplicate", "two times"):
        return "ESCALATE", "duplicate_charge"

    if _has(q, "saving", "interest rate", "profit rate", "return on"):
        return "ESCALATE", "savings_rate"

    # ── ANSWER ──────────────────────────────────────────────────────────────
    # Freeze card — covers English and Urdu ("kaise karun" = "how do I do")
    if _has(q, "freeze", "unfreeze", "band kar", "kaise karun"):
        return "ANSWER", "freeze_card"

    # Balance — safe field
    if _has(q, "balance", "kitna", "how much", "funds"):
        return "ANSWER", "balance"

    # Tap to pay — knowledge.md topic
    if _has(q, "tap to pay", "tap pay", "contactless", "nfc"):
        return "ANSWER", "tap_to_pay"

    # OTP — knowledge.md topic
    if _has(q, "otp", "one time password", "sms code", "verification code"):
        return "ANSWER", "otp"

    # Account deletion — knowledge.md topic
    if _has(q, "delete account", "close account", "remove account"):
        return "ANSWER", "account_deletion"

    # Card declined / payment failing — knowledge.md topic
    if _has(q, "declined", "payment fail", "not going through", "rejected"):
        return "ANSWER", "card_declined"

    # Account restricted / can't access — no approved policy to resolve it;
    # human agent has access to KYC data and can act.
    if _has(q, "why can't", "cannot", "can't do", "why nothing", "nothing works",
             "why is my account", "account blocked", "kyun nahi", "kuch nahi"):
        return "ESCALATE", "account_restricted"

    # ── OUT OF SCOPE ─────────────────────────────────────────────────────────
    return "OUT_OF_SCOPE", "no_match"
