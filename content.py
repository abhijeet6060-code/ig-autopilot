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

Write an Instagram carousel in a bold, editorial "how-to" style for a founder / operator audience.
Tone: calm, confident, specific. Sentence case. Short sentences. Every headline ends with a period.
Structure: a cover promise, 3-4 numbered steps, two "rule" statements, then a comment CTA.

Return JSON with exactly this shape:
{{
  "skip": false,
  "chosen_index": <int index from the list>,
  "cover_headline": "<Title Case promise, 4-8 words, e.g. 'How Founders Use AI Agents to Ship Faster'>",
  "cover_kicker": "<one italic line, max 9 words, ends with a period, e.g. 'The 3 moves that actually save time.'>",
  "cover_hook": "<same as cover_headline>",
  "slides": [
    {{
      "kicker": "Step 1",
      "headline": "<the step as an instruction, 4-8 words, ends with a period>",
      "body": "<1-2 plain sentences explaining it, max 26 words>",
      "panel_label": "<2-3 word label for the list, e.g. 'Start with', 'What changes', 'Do this'>",
      "bullets": ["<max 5 words>", "<max 5 words>", "<max 5 words>"],
      "takeaway": "<one rule, max 10 words>"
    }}
  ],
  "statements": [
    "<rule 1, 10-16 words, pattern 'Your X controls Y, so Z.'>",
    "<rule 2, 10-16 words, same pattern, contrasting rule 1>"
  ],
  "cta_keyword": "<single all-caps keyword, e.g. 'AGENT', 'PROMPT', 'SYSTEM'>",
  "cta_subtext": "<one line promise, e.g. 'I'll send you my agent setup checklist.'>",
  "caption": "<hook line, 2-4 short paragraphs, question to drive comments, max 1500 chars>",
  "hashtags": ["<6 to 10 relevant hashtags without #>"]
}}

Rules:
- "slides" must have 3 to 4 items, kicker "Step 1", "Step 2", ... in order.
- Steps must be things the reader can do; ground them in the chosen story.
- Bullets are 2-5 words each, never full sentences.
- If none of the stories are good or safe to post about, return {{"skip": true}}."""


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
        data["chosen_index"] = 0
    if not data.get("cover_hook"):
        data["cover_hook"] = data.get("cover_headline", "")
    if not data.get("cover_headline"):
        data["cover_headline"] = data.get("cover_hook", "")
    for key in ("cover_hook", "caption", "hashtags"):
        if not data.get(key):
            raise ValueError(f"Missing {key}")

    # Normalize creator format fields
    hook = data["cover_hook"]
    if not data.get("cover_title_main") or not data.get("cover_title_accent"):
        words = hook.split()
        half = max(1, len(words) // 2)
        data["cover_title_main"] = " ".join(words[:half]).upper()
        data["cover_title_accent"] = " ".join(words[half:]).upper()

    if not data.get("cover_subtitle"):
        data["cover_subtitle"] = "The complete breakdown for founders."

    if not data.get("cover_bullets") or len(data["cover_bullets"]) < 3:
        data["cover_bullets"] = ["Direct verified facts", "Actionable takeaways", "Best founder use cases"]

    if not data.get("cta_keyword"):
        data["cta_keyword"] = "TOOLS"

    if not data.get("cta_subtext"):
        data["cta_subtext"] = "I'LL SEND YOU THE COMPLETE GUIDE."

    for n, s in enumerate(data["slides"], 1):
        s.setdefault("kicker", f"Step {n}")
        legacy = f"{s.get('title_main', '')} {s.get('title_accent', '')}".strip()
        title = s.get("headline") or s.get("title") or legacy.capitalize() or "Breakdown"
        if not s.get("headline"):
            s["headline"] = title
        if not s.get("title_main") or not s.get("title_accent"):
            words = title.split()
            half = max(1, len(words) // 2)
            s["title_main"] = " ".join(words[:half]).upper()
            s["title_accent"] = " ".join(words[half:]).upper()
        if not s.get("bullets"):
            body = s.get("body", "")
            raw = [p.strip() for p in re.split(r"[,.;]\s*", body) if p.strip()]
            s["bullets"] = raw[:3] if len(raw) >= 3 else (raw + ["Verified impact", "Strategic takeaway"])[:3]
        if not s.get("takeaway"):
            s["takeaway"] = "Focus on defensible execution, not hype."


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


REEL_PROMPT = """Trending stories right now:
{listing}

Write an engaging, viral, high-retention 25-30 second Instagram Reel script for a founder audience.
Rules:
- Hook in the first 3 seconds (provocative question or bold counter-intuitive statement).
- Short, spoken-style sentences (natural rhythm, punchy, zero fluff, no corporate buzzwords).
- End with a fast takeaway and a question to prompt comments.
- Output ONLY valid JSON, no markdown fences.

Return JSON with exactly this shape:
{{
  "chosen_index": <int index from the list>,
  "hook": "<dramatic hook line spoken in seconds 0-4>",
  "sentences": [
    "<sentence 1, what happened>",
    "<sentence 2, why most people get it wrong>",
    "<sentence 3, the real business implication>",
    "<sentence 4, the actionable takeaway for founders>"
  ],
  "caption": "<engaging Instagram Reel caption with question, max 800 chars>",
  "hashtags": ["<6 to 10 relevant hashtags without #>"]
}}"""


def generate_reel_script(trends):
    listing = "\n".join(
        f"[{i}] ({t.source}) {t.title}" + (f" - {t.summary[:200]}" if t.summary else "")
        for i, t in enumerate(trends)
    )
    system = SYSTEM.format(voice=config.BRAND_VOICE, handle=config.HANDLE)
    prompt = REEL_PROMPT.format(listing=listing)
    last_err = None
    for _ in range(3):
        try:
            data = _parse(_complete(system, prompt))
            idx = data.get("chosen_index", 0)
            if not isinstance(idx, int) or not (0 <= idx < len(trends)):
                data["chosen_index"] = 0
            if not data.get("hook") or not data.get("sentences"):
                raise ValueError("Missing hook or sentences")
            return data
        except Exception as e:
            last_err = e
            time.sleep(2)
    raise RuntimeError(f"Could not generate reel script after 3 tries: {last_err}")

