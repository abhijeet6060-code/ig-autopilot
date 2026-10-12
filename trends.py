"""Collects trending AI / business stories from free public sources."""
import re
from dataclasses import dataclass

import feedparser
import requests
from concurrent.futures import ThreadPoolExecutor

HEADERS = {"User-Agent": "ig-autopilot/1.0"}

KEYWORDS = {
    "AI": ["ai", "gpt", "llm", "openai", "anthropic", "claude", "gemini", "model", "agent",
           "machine learning", "neural", "nvidia", "chip", "robot", "copilot", "chatbot"],
    "business": ["startup", "founder", "revenue", "funding", "raises", "ipo", "acquisition",
                 "market", "saas", "pricing", "layoff", "profit", "valuation", "growth",
                 "marketing", "sales", "customers"],
}

RSS_FEEDS = [
    ("Google News: AI", "https://news.google.com/rss/search?q=artificial+intelligence+when:1d&hl=en-US&gl=US&ceid=US:en", 1.0),
    ("Google News: Business", "https://news.google.com/rss/search?q=startup+OR+business+strategy+when:1d&hl=en-US&gl=US&ceid=US:en", 0.8),
    ("Reddit r/artificial", "https://www.reddit.com/r/artificial/top/.rss?t=day", 0.9),
    ("Reddit r/Entrepreneur", "https://www.reddit.com/r/Entrepreneur/top/.rss?t=day", 0.7),
    ("Reddit r/startups", "https://www.reddit.com/r/startups/top/.rss?t=day", 0.7),
]


@dataclass
class Trend:
    title: str
    url: str
    source: str
    score: float
    summary: str = ""


def _clean(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or "")).strip()


def _relevant(text, niches):
    t = text.lower()
    return any(re.search(rf"\b{re.escape(k)}\b", t) for n in niches for k in KEYWORDS.get(n, []))


def _fetch_hn_item(item_id):
    try:
        return requests.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json",
                            headers=HEADERS, timeout=8).json()
    except Exception:
        return None


def hacker_news(niches, limit=50):
    out = []
    try:
        ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json",
                           headers=HEADERS, timeout=10).json()[:limit]
        with ThreadPoolExecutor(max_workers=10) as ex:
            raw_items = list(ex.map(_fetch_hn_item, ids))
        items = [it for it in raw_items if it and it.get("title") and _relevant(it["title"], niches)]
        top = max([it.get("score", 1) + 0.5 * it.get("descendants", 0) for it in items] or [1])
        for it in items:
            raw = it.get("score", 1) + 0.5 * it.get("descendants", 0)
            url = it.get("url") or f"https://news.ycombinator.com/item?id={it['id']}"
            out.append(Trend(it["title"], url, "Hacker News", raw / top * 1.2))
    except Exception as e:
        print(f"[trends] Hacker News failed: {e}")
    return out


def rss(name, url, weight):
    out = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if not r.ok:
            return out
        feed = feedparser.parse(r.content)
        n = len(feed.entries) or 1
        for rank, e in enumerate(feed.entries[:25]):
            out.append(Trend(
                title=_clean(e.get("title", "")),
                url=e.get("link", ""),
                source=name,
                score=(1 - rank / n) * weight,
                summary=_clean(e.get("summary", ""))[:300],
            ))
    except Exception as e:
        print(f"[trends] {name} failed: {e}")
    return out


def collect(niches=("AI", "business")):
    trends = hacker_news(niches)
    for name, url, w in RSS_FEEDS:
        trends += rss(name, url, w)

    # Merge near-duplicates (same story from several sources gets a boost).
    merged = {}
    for t in trends:
        if not t.title or not t.url:
            continue
        key = re.sub(r"[^a-z0-9 ]", "", t.title.lower())[:50]
        if key in merged:
            merged[key].score += t.score * 0.5
        else:
            merged[key] = t
    return sorted(merged.values(), key=lambda t: t.score, reverse=True)
