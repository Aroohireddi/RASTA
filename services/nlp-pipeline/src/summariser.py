import re
import math
from segmenter import segment_sentences

def extract_noun_phrases_simple(sentence: str) -> list[str]:
    """
    Simple noun phrase extraction using capitalization heuristic.
    Capitalized words in non-sentence-initial positions are likely NPs.
    """
    words = sentence.split()
    noun_phrases = []
    for i, word in enumerate(words):
        clean = re.sub(r'[^\w]', '', word)
        if i > 0 and clean and clean[0].isupper():
            noun_phrases.append(clean)
    return noun_phrases


def score_sentence(sentence: str) -> float:
    """
    Novel heuristic from original thesis:
    score = (capitalized_words + noun_phrases) / word_count
    Filters 50th-75th percentile to avoid intros and citation-heavy sentences.
    """
    words = sentence.split()
    if len(words) == 0:
        return 0.0

    capitalized = sum(1 for w in words if w and w[0].isupper())
    noun_phrases = extract_noun_phrases_simple(sentence)

    score = (capitalized + len(noun_phrases)) / len(words)
    return round(score, 4)


def summarise(text: str, max_sentences: int = 5) -> list[str]:
    """
    Extract salient sentences using NP heuristic.
    Returns sentences in 50th-75th percentile of score distribution.
    """
    sentences = segment_sentences(text)

    if not sentences:
        return []

    if len(sentences) <= 3:
        return sentences

    # Score all sentences
    scored = [(s, score_sentence(s)) for s in sentences]

    scores = [s for _, s in scored]
    scores_sorted = sorted(scores)
    n = len(scores_sorted)

    p50 = scores_sorted[int(n * 0.50)]
    p75 = scores_sorted[min(int(n * 0.75), n - 1)]

    # Select sentences in 50th-75th percentile
    selected = [
        s for s, score in scored
        if p50 <= score <= p75
    ]

    # Fallback: if percentile filter returns nothing, take top scored
    if not selected:
        selected = [s for s, _ in sorted(scored, key=lambda x: x[1], reverse=True)[:max_sentences]]

    return selected[:max_sentences]