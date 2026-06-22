"""
LLM interface.  A real model can drop in by implementing LLMBackend.
The default is StubLLM: a fully deterministic stand-in that never invents policy.
"""
from __future__ import annotations
from typing import Protocol


class LLMBackend(Protocol):
    def complete(self, lane: str, topic: str, customer: dict, question: str) -> str:
        ...


class StubLLM:
    """Deterministic responses grounded only in knowledge.md and safe customer data."""

    def complete(self, lane: str, topic: str, customer: dict, question: str) -> str:
        name = customer.get("firstName", "there")

        if lane == "REFUSE":
            return (
                f"Hi {name}, for your security we can't share sensitive details "
                f"like card numbers or national ID through this channel. "
                f"If there's something specific you need help with, I'm here!"
            )

        if lane == "OUT_OF_SCOPE":
            if topic == "spam":
                return (
                    f"Hi {name}, I didn't quite catch that. "
                    f"If you have a question about your PayWallet account, I'm here to help."
                )
            if topic == "off_topic":
                return (
                    f"Hi {name}, I can only help with PayWallet account questions. "
                    f"Is there something about your account I can assist with?"
                )
            if topic == "crypto":
                return (
                    f"Hi {name}, PayWallet doesn't offer crypto trading or investment services. "
                    f"Is there anything else I can help you with?"
                )
            return (
                f"Hi {name}, that's not something PayWallet offers. "
                f"Is there anything else I can help you with?"
            )

        if lane == "ESCALATE":
            if topic == "duplicate_charge":
                return (
                    f"Hi {name}, I can see there may be a duplicate charge on your account. "
                    f"I'm flagging this for our team right now — a human agent will follow up "
                    f"with you shortly to look into it."
                )
            if topic == "savings_rate":
                return (
                    f"Hi {name}, I don't have rate information available here. "
                    f"Let me connect you with our team who can give you the accurate details."
                )
            if topic == "account_restricted":
                kyc = customer.get("kyc")
                if kyc == "pending":
                    return (
                        f"Hi {name} — I can see your account isn't fully active yet. "
                        f"Verification is still pending. I can't make that change from here, "
                        f"so I'm connecting you with an agent who can look into it and get you sorted."
                    )
                return (
                    f"Hi {name}, your account has some restrictions that I'm not able to resolve here. "
                    f"I'm connecting you with a human agent who can review your account and help "
                    f"get everything sorted."
                )
            return (
                f"Hi {name}, I want to make sure you get the right help — "
                f"I'm connecting you with a human agent now."
            )

        if lane == "ANSWER":
            if topic == "freeze_card":
                return (
                    f"Hi {name}! You can freeze or unfreeze your card right in the app: "
                    f"go to Current Balance → your card → Freeze card. "
                    f"A frozen card blocks all new transactions until you unfreeze it."
                )
            if topic == "balance":
                balance = customer.get("balance", "unavailable")
                return f"Hi {name}, your current balance is {balance}."

            if topic == "tap_to_pay":
                return (
                    f"Hi {name}, tap to pay works only with a physical card at a payment terminal "
                    f"— it's not available on virtual cards."
                )
            if topic == "otp":
                return (
                    f"Hi {name}, OTPs are sent by SMS to your registered mobile number only "
                    f"— never via WhatsApp or email. If you're abroad, make sure international "
                    f"roaming is enabled on that SIM."
                )
            if topic == "account_deletion":
                return (
                    f"Hi {name}, we'd be sorry to see you go! Just so you know: once your account "
                    f"is deleted, you won't be able to sign up again with the same national ID. "
                    f"Please transfer out any remaining balance first. "
                    f"Deletion takes 7–10 working days."
                )
            if topic == "card_declined":
                return (
                    f"Hi {name}, a declined payment is usually a temporary issue on the merchant's "
                    f"side. Please try again after a few hours (ideally 24h). If it keeps failing, "
                    f"let me know the merchant name, amount, and date so we can look into it."
                )
            return f"Hi {name}, let me help you with that."

        # Fallback — should not be reached with known lanes
        return f"Hi {name}, I'm not able to help with that right now."
