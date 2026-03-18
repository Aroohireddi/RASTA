import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from pydantic import BaseModel
from segmenter import segment_sentences, detect_language_ratio
from summariser import summarise
from codemixer import codemix
from transliterator import transliterate_tagged_tokens, reconstruct_sentence

app = FastAPI(title="RASTA NLP Pipeline", version="1.0.0")

class TextInput(BaseModel):
    text: str
    source: str = "unknown"

class ArticleInput(BaseModel):
    title: str
    summary: str
    url: str = ""
    source: str = "unknown"

@app.get("/health")
def health():
    return {"status": "ok", "service": "nlp-pipeline"}

@app.post("/process/sentence")
def process_sentence(input: TextInput):
    """Full pipeline for a single sentence."""
    # Step 1: Code-mix
    codemixed = codemix(input.text)

    # Step 2: Transliterate EN/EN_OOV tokens
    transliterated = transliterate_tagged_tokens(codemixed["tagged_tokens"])

    # Step 3: Reconstruct final sentence
    final_sentence = reconstruct_sentence(transliterated)

    return {
        "original": input.text,
        "codemixed": codemixed["codemixed"],
        "final_sentence": final_sentence,
        "tagged_tokens": transliterated,
        "oov_tokens": codemixed["oov_tokens"],
        "protected_count": codemixed["protected_count"]
    }

@app.post("/process/article")
def process_article(input: ArticleInput):
    """Full pipeline for an article — summarise then process each sentence."""
    full_text = f"{input.title}. {input.summary}"

    # Step 1: Summarise
    sentences = summarise(full_text)

    # Step 2: Process each sentence
    processed_sentences = []
    for sentence in sentences:
        codemixed = codemix(sentence)
        transliterated = transliterate_tagged_tokens(codemixed["tagged_tokens"])
        final = reconstruct_sentence(transliterated)
        processed_sentences.append({
            "original": sentence,
            "final": final,
            "oov_tokens": codemixed["oov_tokens"]
        })

    lang_ratio = detect_language_ratio(full_text)

    return {
        "source": input.source,
        "url": input.url,
        "sentence_count": len(processed_sentences),
        "language_ratio": lang_ratio,
        "sentences": processed_sentences
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)