import re
from deep_translator import GoogleTranslator

def extract_protected_tokens(text: str) -> tuple[str, dict]:
    """
    Step 1: Find capitalized English words (named entities, technical terms).
    Reverse them as protection before translation.
    Returns modified text and mapping of reversed->original.
    """
    mapping = {}
    words = text.split()
    protected_words = []

    for word in words:
        clean = re.sub(r'[^\w]', '', word)
        # Protect if: starts with capital, is ASCII, length > 1
        if clean and clean[0].isupper() and clean.isascii() and len(clean) > 1:
            reversed_word = clean[::-1]
            mapping[reversed_word] = clean
            protected_words.append(word.replace(clean, reversed_word))
        else:
            protected_words.append(word)

    return ' '.join(protected_words), mapping


def restore_protected_tokens(text: str, mapping: dict) -> str:
    """
    Step 4: Restore reversed tokens back to original English.
    """
    words = text.split()
    restored = []
    for word in words:
        clean = re.sub(r'[^\w]', '', word)
        if clean in mapping:
            restored.append(word.replace(clean, mapping[clean]))
        else:
            restored.append(word)
    return ' '.join(restored)


def translate_to_telugu(text: str) -> str:
    """
    Step 2: Translate English text to Telugu using GoogleTranslator.
    Protected tokens (reversed) pass through untouched.
    """
    try:
        translator = GoogleTranslator(source='en', target='te')
        translated = translator.translate(text)
        return translated if translated else text
    except Exception as e:
        print(f"[codemixer] Translation error: {e}")
        return text


def tag_tokens(text: str, mapping: dict) -> list[dict]:
    """
    Tag each token as Telugu [TE] or English [EN] or English OOV [EN_OOV].
    English tokens that were protected are tagged EN_OOV.
    """
    tagged = []
    words = text.split()
    oov_set = set(mapping.values())

    for word in words:
        clean = re.sub(r'[^\w]', '', word)
        if clean in oov_set:
            tagged.append({"token": word, "tag": "EN_OOV", "clean": clean})
        elif clean.isascii() and clean.isalpha():
            tagged.append({"token": word, "tag": "EN", "clean": clean})
        else:
            tagged.append({"token": word, "tag": "TE", "clean": clean})

    return tagged


def codemix(text: str) -> dict:
    """
    Full reverse-protect-translate-restore-tag pipeline.
    Returns original text, mixed text, and tagged tokens.
    """
    # Step 1: Protect capitalized English tokens
    protected_text, mapping = extract_protected_tokens(text)

    # Step 2: Translate to Telugu
    translated = translate_to_telugu(protected_text)

    # Step 3: Restore protected English tokens
    restored = restore_protected_tokens(translated, mapping)

    # Step 4: Tag tokens
    tagged_tokens = tag_tokens(restored, mapping)

    return {
        "original": text,
        "codemixed": restored,
        "tagged_tokens": tagged_tokens,
        "protected_count": len(mapping),
        "oov_tokens": list(mapping.values())
    }