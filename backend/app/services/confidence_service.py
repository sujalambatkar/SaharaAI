from typing import List, Tuple
from app.config import settings

HANDOFF_MESSAGES = {
    "EN": (
        "I'm not confident I have the right answer for your query. "
        "Let me connect you to our support team who can help you better. "
        "You can reach us at support@saharaai.in or call 1800-XXX-XXXX (toll-free)."
    ),
    "HI": (
        "मुझे सही उत्तर की जानकारी नहीं है। "
        "मैं आपको हमारी सपोर्ट टीम से जोड़ता हूं जो आपकी बेहतर मदद कर सकती है। "
        "आप support@saharaai.in पर ईमेल करें या 1800-XXX-XXXX (टोल-फ्री) पर कॉल करें।"
    ),
    "HINGLISH": (
        "Mujhe confident answer nahi mila aapke query ke liye. "
        "Support team se connect karta hoon jo aapki better help kar sakti hai. "
        "support@saharaai.in pe email karo ya 1800-XXX-XXXX (toll-free) pe call karo."
    ),
}


def compute_confidence(scores: List[float]) -> float:
    """Confidence = average of top-k retrieval scores, normalized to [0, 1]."""
    if not scores:
        return 0.0
    # Qdrant cosine scores are already in [-1, 1]; shift to [0, 1]
    normalized = [(s + 1) / 2 for s in scores]
    return min(1.0, max(0.0, sum(normalized) / len(normalized)))


def evaluate_handoff(
    confidence: float,
    language: str,
) -> Tuple[bool, str | None]:
    """
    Returns (handoff_triggered, handoff_message_or_None).
    """
    if confidence < settings.confidence_threshold:
        message = HANDOFF_MESSAGES.get(language, HANDOFF_MESSAGES["EN"])
        return True, message
    return False, None
