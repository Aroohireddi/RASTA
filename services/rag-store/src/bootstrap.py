import json
import os
import chromadb
from pathlib import Path

LEXICON_PATH = Path("data/pronunciation_lexicon/seed_entries.json")
CHROMA_PATH = Path("data/pronunciation_index")

def get_client():
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_PATH))

def get_or_create_collection(client):
    return client.get_or_create_collection(
        name="pronunciation_store"
    )

def bootstrap_store():
    if not LEXICON_PATH.exists():
        print(f"[bootstrap] Lexicon file not found at {LEXICON_PATH}")
        return 0

    with open(LEXICON_PATH, "r", encoding="utf-8") as f:
        entries = json.load(f)

    client = get_client()
    collection = get_or_create_collection(client)

    existing = collection.count()
    if existing >= len(entries):
        print(f"[bootstrap] Store already has {existing} entries. Skipping.")
        return existing

    documents = []
    metadatas = []
    ids = []

    for i, entry in enumerate(entries):
        surface = entry["surface"]
        phoneme = entry["phoneme"]
        domain = entry.get("domain", "general")
        documents.append(surface)
        metadatas.append({
            "surface": surface,
            "phoneme": phoneme,
            "domain": domain,
            "verified": str(entry.get("verified", False))
        })
        ids.append(f"entry_{i}_{surface}")

    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"[bootstrap] Bootstrapped {len(entries)} entries into ChromaDB.")
    return len(entries)

if __name__ == "__main__":
    bootstrap_store()