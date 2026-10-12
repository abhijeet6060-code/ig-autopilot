"""Picks the best story and writes the carousel + caption.
Default provider is Google Gemini's free tier; Claude is optional."""
import json
import re
import time

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
  "image_prompt": "<cinematic 3D render description for background visual, e.g. futuristic digital art of founder looking at glowing holographic AI brain in dark space with neon cyan particles, 8k octane render>",
  "cover_hook": "<max 12 words, scroll-stopping headline, honest>",
  "cover_highlight_cyan": "<1-3 words from cover_hook to highlight in glowing cyan>",
  "cover_highlight_orange": "<1-3 words from cover_hook to highlight in glowing orange>",
  "cards": [
    {{"icon": "doc", "line1": "Reads &", "line2": "understands docs"}},
    {{"icon": "lightbulb", "line1": "Solves complex", "line2": "problems"}},
    {{"icon": "code", "line1": "Writes", "line2": "code"}},
    {{"icon": "doc", "line1": "Creates visuals", "line2": "& designs"}},
    {{"icon": "chat", "line1": "Holds natural", "line2": "dialogue"}},
    {{"icon": "globe", "line1": "Searches &", "line2": "researches live"}},
    {{"icon": "calendar", "line1": "Automates multi-", "line2": "step tasks"}},
    {{"icon": "chart", "line1": "Finds data", "line2": "& insights"}}
  ],
  "doodle_note": "<short provocative 1-line thought, max 7 words>",
  "footer_takeaway": "<bold 1-line truth, max 7 words>",
  "footer_subtext": "<1-line explanation, max 10 words>",
  "slides": [
    {{"tag": "WHAT HAPPENED", "title": "<max 7 words>", "body": "<max 35 words>", "takeaway": "<1-line key point, max 12 words>"}},
    {{"tag": "WHY IT MATTERS", "title": "<max 7 words>", "body": "<max 35 words>", "takeaway": "<1-line key point, max 12 words>"}},
    {{"tag": "ACTION PLAYBOOK", "title": "<max 7 words>", "body": "<max 35 words>", "takeaway": "<1-line key point, max 12 words>"}}
  ],
  "caption": "<hook line, 2-4 short paragraphs, question to drive comments, max 1500 chars>",
  "hashtags": ["<6 to 10 relevant hashtags without #>"]
}}

"cards" must have 6 to 8 items summarizing the key dimensions or capabilities.
"slides" must have 3 to 5 items covering: what happened, why it matters, what to do about it.
If none of the stories are good or safe to post about, return {{"skip": true}}."""


def _gemini(system, prompt):
    api_key = config.require("GEMINI_API_KEY")
    models_to_try = [config.GEMINI_MODEL, "gemini-flash-latest", "gemini-2.5-flash", "gemini-2.5-pro"]
    seen = set()
    models = [m for m in models_to_try if m and not (m in seen or seen.add(m))]

    last_error = None
    for model in models:
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                json={
                    "systemInstruction": {"parts": [{"text": system}]},
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7},
                },
                timeout=90,
            )
            if r.status_code == 200:
                parts = r.json()["candidates"][0]["content"]["parts"]
                return "".join(p.get("text", "") for p in parts)
            print(f"[content] Gemini {model} returned {r.status_code}, trying fallback model...")
            last_error = f"Gemini error {r.status_code}: {r.text[:300]}"
            time.sleep(2)
        except Exception as e:
            last_error = str(e)
            time.sleep(1)

    raise RuntimeError(f"All Gemini models failed: {last_error}")


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
        except Exception as e:
            last_err = e
            time.sleep(2)
    raise RuntimeError(f"Could not get valid content after 3 tries: {last_err}")


def full_caption(data, source_name):
    tags = " ".join("#" + h.lstrip("#").replace(" ", "") for h in data["hashtags"][:10])
    cap = f"{data['caption'].strip()}\n\nSource: {source_name}\n\n{tags}"
    return cap[:2200]
