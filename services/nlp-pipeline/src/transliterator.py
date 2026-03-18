import re

# Simple rule-based Telugu transliteration for English tokens
# Maps common English phoneme patterns to Telugu script approximations
PHONEME_MAP = {
    'a': 'అ', 'b': 'బ', 'c': 'క', 'd': 'డ', 'e': 'ఎ',
    'f': 'ఫ', 'g': 'గ', 'h': 'హ', 'i': 'ఇ', 'j': 'జ',
    'k': 'క', 'l': 'ల', 'm': 'మ', 'n': 'న', 'o': 'ఒ',
    'p': 'ప', 'q': 'క', 'r': 'ర', 's': 'స', 't': 'త',
    'u': 'ఉ', 'v': 'వ', 'w': 'వ', 'x': 'క్స', 'y': 'య',
    'z': 'జ'
}

def transliterate_english_to_telugu(word: str) -> str:
    """
    Rule-based transliteration of English word to Telugu script.
    Used as fallback when RAG store has no entry for a token.
    """
    word_lower = word.lower()
    result = []
    i = 0
    while i < len(word_lower):
        char = word_lower[i]
        if char in PHONEME_MAP:
            result.append(PHONEME_MAP[char])
        elif char.isalpha():
            result.append(char)
        else:
            result.append(char)
        i += 1
    return ''.join(result)


def transliterate_tagged_tokens(tagged_tokens: list[dict]) -> list[dict]:
    """
    For each token tagged EN or EN_OOV, apply transliteration.
    TE tokens pass through unchanged.
    """
    result = []
    for token_data in tagged_tokens:
        tag = token_data["tag"]
        token = token_data["token"]
        clean = token_data["clean"]

        if tag in ("EN", "EN_OOV") and clean:
            transliterated = transliterate_english_to_telugu(clean)
            result.append({
                **token_data,
                "transliterated": transliterated,
                "final_token": transliterated
            })
        else:
            result.append({
                **token_data,
                "transliterated": None,
                "final_token": token
            })

    return result


def reconstruct_sentence(transliterated_tokens: list[dict]) -> str:
    """Reconstruct full sentence from transliterated tokens."""
    return ' '.join(t["final_token"] for t in transliterated_tokens)