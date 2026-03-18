import re

def segment_sentences(text: str) -> list[str]:
    """
    Segment Telugu-English mixed text into sentences.
    Uses punctuation-based rules since indic-nlp-library
    handles Telugu sentence boundaries.
    """
    if not text:
        return []

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Split on Telugu and English sentence boundaries
    # Telugu full stop: ।  English: . ! ?
    pattern = r'(?<=[.!?।])\s+'
    sentences = re.split(pattern, text)

    # Clean and filter
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    return sentences


def is_telugu(text: str) -> bool:
    """Check if text contains Telugu characters."""
    telugu_range = range(0x0C00, 0x0C7F)
    return any(ord(c) in telugu_range for c in text)


def detect_language_ratio(text: str) -> dict:
    """Return ratio of Telugu vs English characters."""
    telugu_chars = sum(1 for c in text if 0x0C00 <= ord(c) <= 0x0C7F)
    english_chars = sum(1 for c in text if c.isascii() and c.isalpha())
    total = telugu_chars + english_chars
    if total == 0:
        return {"telugu": 0.0, "english": 0.0}
    return {
        "telugu": round(telugu_chars / total, 2),
        "english": round(english_chars / total, 2)
    }