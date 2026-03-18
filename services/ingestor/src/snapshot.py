import json
import os
from datetime import datetime
from pathlib import Path

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

SEEN_IDS_FILE = RAW_DIR / "seen_ids.json"

def load_seen_ids() -> set:
    if SEEN_IDS_FILE.exists():
        with open(SEEN_IDS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_seen_ids(seen_ids: set):
    with open(SEEN_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen_ids), f)

def save_articles(articles: list[dict]) -> int:
    seen_ids = load_seen_ids()
    new_count = 0
    today = datetime.utcnow().strftime("%Y-%m-%d")
    output_file = RAW_DIR / f"articles_{today}.jsonl"

    with open(output_file, "a", encoding="utf-8") as f:
        for article in articles:
            if article["id"] not in seen_ids:
                f.write(json.dumps(article, ensure_ascii=False) + "\n")
                seen_ids.add(article["id"])
                new_count += 1

    save_seen_ids(seen_ids)
    print(f"[snapshot] {new_count} new articles saved to {output_file}")
    return new_count

def load_unprocessed_articles() -> list[dict]:
    articles = []
    for file in sorted(RAW_DIR.glob("articles_*.jsonl")):
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    article = json.loads(line.strip())
                    if not article.get("processed", False):
                        articles.append(article)
                except json.JSONDecodeError:
                    continue
    return articles