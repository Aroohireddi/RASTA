import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from pydantic import BaseModel
from bootstrap import bootstrap_store
from store import disambiguate_token, disambiguate_batch, get_store_stats

app = FastAPI(title="RASTA RAG Pronunciation Store", version="1.0.0")

class TokenInput(BaseModel):
    token: str

class BatchInput(BaseModel):
    tokens: list[str]

@app.on_event("startup")
def startup():
    print("[rag-store] Bootstrapping pronunciation store...")
    count = bootstrap_store()
    print(f"[rag-store] Store ready with {count} entries.")

@app.get("/health")
def health():
    return {"status": "ok", "service": "rag-store", **get_store_stats()}

@app.post("/disambiguate")
def disambiguate(input: TokenInput):
    return disambiguate_token(input.token)

@app.post("/disambiguate/batch")
def disambiguate_batch_endpoint(input: BatchInput):
    results = disambiguate_batch(input.tokens)
    matched = sum(1 for r in results if r["matched"])
    return {
        "total": len(results),
        "matched": matched,
        "unmatched": len(results) - matched,
        "results": results
    }

@app.get("/stats")
def stats():
    return get_store_stats()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)