from langdetect import detect, detect_langs, LangDetectException
from typing import Literal

LanguageLabel = Literal["EN", "HI", "HINGLISH"]


def detect_language(text: str) -> LanguageLabel:
    """
    Classify query as EN, HI, or HINGLISH.
    HINGLISH is returned when langdetect confidence is low or detects multiple languages.
    """
    try:
        langs = detect_langs(text)
        if not langs:
            return "EN"

        top = langs[0]
        lang_code = top.lang
        confidence = top.prob

        # Pure English with high confidence
        if lang_code == "en" and confidence >= 0.9:
            return "EN"

        # Pure Hindi with high confidence
        if lang_code == "hi" and confidence >= 0.9:
            return "HI"

        # Hinglish: mixed signals, low confidence, or roman-script Hindi
        # Also catches "ur" (Urdu) which often means Devanagari text
        if lang_code in ("en", "hi", "ur", "mr"):
            if confidence < 0.9:
                return "HINGLISH"

        # Multiple detected languages at similar probabilities → Hinglish
        if len(langs) >= 2 and langs[1].prob > 0.15:
            return "HINGLISH"

        # Default mappings
        if lang_code == "en":
            return "EN"
        if lang_code in ("hi", "ur", "mr"):
            return "HI"

        return "HINGLISH"

    except LangDetectException:
        return "EN"
