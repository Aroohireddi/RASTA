import feedparser
import requests
import hashlib
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup

FEEDS = {
    "sakshi": "https://www.sakshi.com/rss.xml",
    "telangana_today": "https://telanganatoday.com/feed",
    "oneindia_telugu": "https://telugu.oneindia.com/rss/telugu-news.xml",
    "ndtv_telugu": "https://feeds.feedburner.com/ndtvtelugu",
    "the_hans_india": "https://www.thehansindia.com/feeds/telugu-news",
    "eenadu": "https://www.eenadu.net/telugu-news/rss",
    "abn": "https://www.abnandhra.com/feed/",
    "tv9_telugu": "https://tv9telugu.com/feed",
    "ntv": "https://ntvtelugu.com/feed",
    "10tv": "https://10tv.in/feed",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "te-IN,te;q=0.9,en-US;q=0.8,en;q=0.7",
}

def get_url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()

def clean_html(raw: str) -> str:
    if not raw:
        return ""
    soup = BeautifulSoup(raw, "lxml")
    return soup.get_text(separator=" ").strip()

def fetch_feed(source: str, url: str) -> list[dict]:
    articles = []
    try:
        # Try with requests first for better header control
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
        else:
            # Fallback to feedparser direct
            feed = feedparser.parse(url)

        if not feed.entries:
            print(f"[feeds] {source}: no entries found (status may be {response.status_code if 'response' in dir() else 'unknown'})")
            return []

        for entry in feed.entries[:10]:
            title = clean_html(entry.get("title", ""))
            summary = clean_html(entry.get("summary", entry.get("description", "")))
            link = entry.get("link", "")
            published = entry.get("published", datetime.utcnow().isoformat())

            if not title or not link:
                continue

            # Skip if title is too short or just whitespace
            if len(title.strip()) < 5:
                continue

            articles.append({
                "id": get_url_hash(link),
                "source": source,
                "title": title,
                "summary": summary,
                "url": link,
                "published": published,
                "fetched_at": datetime.utcnow().isoformat(),
                "processed": False
            })

    except requests.exceptions.Timeout:
        print(f"[feeds] {source}: timeout after 15s")
    except requests.exceptions.ConnectionError:
        print(f"[feeds] {source}: connection error — feed may be down")
    except Exception as e:
        print(f"[feeds] {source}: error — {e}")

    return articles

def fetch_all_feeds() -> list[dict]:
    all_articles = []
    for source, url in FEEDS.items():
        articles = fetch_feed(source, url)
        if articles:
            print(f"[feeds] {source}: {len(articles)} articles fetched")
        all_articles.extend(articles)
    total = len(all_articles)
    print(f"[feeds] Total: {total} articles fetched across all sources")
    return all_articles