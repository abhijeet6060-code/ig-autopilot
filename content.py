"""Picks the best story and writes the carousel + caption.
Default provider is Google Gemini's free tier; Claude is optional."""
import json
import re

import requests

import config

SYSTEM = """You are the social media editor for the Instagram account {handle}, covering AI and business.
Voice: {voice}

Rules:
- Pick the single story from the list that is most interesting and useful for the audience.
- Only state facts the headline/summary supports. Never invent numbers, quotes or names.
  If detail is thin, write about the implication or a framework instead, and say so honestly.
- Plain language, short sentences, no hype words, no emoji spam (max 2 in the caption).
- Output ONLY valid JSON, no markdown fences."""

PROMPT = """Trending stories right now:
{listing}

Return JSON with exactly this shape:
{{
  "skip": false,
  "chosen_index": <int index from the list>,
  "cover_hook": "<max 12 words, scroll-stopping, honest>",
  "slides": [
    {{"title": "<max 7 words>", "body": "<max 28 words>"}}
  ],
  "caption": "<hook line, 2-4 short paragraphs, question to drive comments, max 1500 chars>",
  "hashtags": ["<6 to 10 relevant hashtags without #>"]
}}

"slides" must have 3 to 5 items covering: what happened, why it matters, what to do about it.
If none of the stories are good or safe to post about, return {{"skip": true}}."""


def _gemini(system, prompt):
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_MODEL}:generateContent",
        headers={"x-goog-api-key": config.require("GEMINI_API_KEY"), "Content-Type": "application/json"},
        json={
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7},
        },
        timeout=90,
    )
    if not r.ok:
        raise RuntimeError(f"Gemini error {r.status_code}: {r.text[:300]}")
    parts = r.json()["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts)


def _anthropic(system, prompt):
    import anthropic  # optional, paid
    msg = anthropic.Anthropic().messages.create(
        model=config.CLAUDE_MODEL, max_tokens=2000, system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in msg.content if b.type == "text")


def _complete(system, prompt):
    return _anthropic(system, prompt) if config.LLM_PROVIDER == "anthropic" else _gemini(system, prompt)


def _parse(text):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(text)


def _validate(data, n):
    if data.get("skip"):
        return
    if not (3 <= len(data.get("slides", [])) <= 5):
        raise ValueError("Expected 3-5 slides")
    idx = data.get("chosen_index")
    if not isinstance(idx, int) or not (0 <= idx < n):
        raise ValueError("Invalid chosen_index")
    for key in ("cover_hook", "caption", "hashtags"):
        if not data.get(key):
            raise ValueError(f"Missing {key}")


def generate(trends):
    listing = "\n".join(
        f"[{i}] ({t.source}) {t.title}" + (f" - {t.summary[:200]}" if t.summary else "")
        for i, t in enumerate(trends)
    )
    system = SYSTEM.format(voice=config.BRAND_VOICE, handle=config.HANDLE)
    prompt = PROMPT.format(listing=listing)
    last_err = None
    for _ in range(3):  # free models occasionally return bad JSON; retry
        try:
            data = _parse(_complete(system, prompt))
            _validate(data, len(trends))
            return data
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            last_err = e
    raise RuntimeError(f"Could not get valid content after 3 tries: {last_err}")


def full_caption(data, source_name):
    tags = " ".join("#" + h.lstrip("#").replace(" ", "") for h in data["hashtags"][:10])
    cap = f"{data['caption'].strip()}\n\nSource: {source_name}\n\n{tags}"
    return cap[:2200]
