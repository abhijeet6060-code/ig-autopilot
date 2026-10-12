"""Tiny JSON state file (committed back to the repo by the workflow)."""
import json
import os
import time

PATH = "state.json"


def _load():
    if not os.path.exists(PATH):
        return {"posts": []}
    with open(PATH, encoding="utf-8") as f:
        return json.load(f)


def _save(state):
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def seen(url):
    return any(p["source_url"] == url for p in _load()["posts"])


def record(url, title, caption, media_id, status):
    state = _load()
    state["posts"] = [p for p in state["posts"] if p["source_url"] != url]
    state["posts"].append({
        "source_url": url, "title": title, "caption": caption,
        "media_id": media_id, "status": status, "created_at": time.time(),
    })
    state["posts"] = state["posts"][-300:]  # keep the file small
    _save(state)


def published_last_24h():
    cutoff = time.time() - 86400
    return sum(1 for p in _load()["posts"]
               if p["status"] == "published" and p["created_at"] > cutoff)
