import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bootstrap import get_client, get_or_create_collection, bootstrap_store

SIMILARITY_THRESHOLD = 0.75

def disambiguate_token(token: str) -> dict:
    client = get_client()
    collection = get_or_create_collection(client)

    if collection.count() == 0:
        bootstrap_store()

    try:
        results = collection.query(
            query_texts=[token],
            n_results=1,
            include=["metadatas", "distances", "documents"]
        )

        if not results["ids"][0]:
            return {"token": token, "phoneme": None, "matched": False, "confidence": 0.0}

        distance = results["distances"][0][0]
        confidence = round(1 - distance, 4)
        metadata = results["metadatas"][0][0]
        matched_surface = results["documents"][0][0]

        if confidence >= SIMILARITY_THRESHOLD:
            return {
                "token": token,
                "phoneme": metadata["phoneme"],
                "matched_surface": matched_surface,
                "domain": metadata["domain"],
                "matched": True,
                "confidence": confidence
            }
        else:
            return {
                "token": token,
                "phoneme": None,
                "matched": False,
                "confidence": confidence
            }

    except Exception as e:
        print(f"[store] Error querying store: {e}")
        return {"token": token, "phoneme": None, "matched": False, "confidence": 0.0}


def disambiguate_batch(tokens: list[str]) -> list[dict]:
    return [disambiguate_token(token) for token in tokens]


def get_store_stats() -> dict:
    try:
        client = get_client()
        collection = get_or_create_collection(client)
        return {
            "total_entries": collection.count(),
            "threshold": SIMILARITY_THRESHOLD
        }
    except Exception as e:
        return {"total_entries": 0, "threshold": SIMILARITY_THRESHOLD, "error": str(e)}