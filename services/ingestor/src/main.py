import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
import threading
from fastapi import FastAPI
from feeds import fetch_all_feeds
from snapshot import save_articles, load_unprocessed_articles

app = FastAPI(title="RASTA Ingestor", version="1.0.0")

POLL_INTERVAL = 60  # seconds

def ingest_loop():
    print("[ingestor] Starting ingestion loop...")
    while True:
        try:
            articles = fetch_all_feeds()
            saved = save_articles(articles)
            print(f"[ingestor] Cycle complete. {saved} new articles saved.")
        except Exception as e:
            print(f"[ingestor] Error in ingestion loop: {e}")
        time.sleep(POLL_INTERVAL)

@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=ingest_loop, daemon=True)
    thread.start()
    print("[ingestor] Background ingestion thread started.")

@app.get("/health")
def health():
    return {"status": "ok", "service": "ingestor"}

@app.get("/articles")
def get_articles():
    articles = load_unprocessed_articles()
    return {"count": len(articles), "articles": articles[:20]}

@app.get("/articles/count")
def get_count():
    articles = load_unprocessed_articles()
    return {"unprocessed": len(articles)}

if __name__ == "__main__":
    import uvicorn
    # Run one immediate fetch before starting server
    print("[ingestor] Running initial fetch...")
    articles = fetch_all_feeds()
    saved = save_articles(articles)
    print(f"[ingestor] Initial fetch complete. {saved} articles saved.")
    uvicorn.run(app, host="0.0.0.0", port=8001)