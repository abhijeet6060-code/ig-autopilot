"""Renders viral 3D visual carousel slides (1080x1350, 4:5) with Pillow and AI backgrounds."""
import io
import os
import re
import urllib.parse
import requests
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 75

FONT_PATHS = [
    "fonts/Inter.ttf",
    os.getenv("FONT_PATH"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def _font(size):
    for p in FONT_PATHS:
        if p and os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default(size)


def _fetch_ai_background(prompt):
    """Generates a 3D cinematic background visual via Pollinations Flux (free)."""
    if not prompt:
        prompt = "digital art of tech founder looking at holographic glowing AI brain in dark futuristic space"
    try:
        clean_p = prompt + ", dark futuristic space, neon cyan and orange lighting, 8k render, octane render, 4:5 portrait"
        encoded = urllib.parse.quote(clean_p)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1350&nologo=true&model=flux"
        r = requests.get(url, timeout=30)
        if r.ok and len(r.content) > 10000:
            img = Image.open(io.BytesIO(r.content)).convert("RGBA")
            return img.resize((W, H), Image.Resampling.LANCZOS)
    except Exception as e:
        print(f"[images] AI bg fetch fallback: {e}")

    # Fallback to dark cybernetic glowing gradient
    img = Image.new("RGBA", (W, H), (10, 15, 30, 255))
    d = ImageDraw.Draw(img)
    for y in range(H):
        factor = y / H
        r = int(8 + 14 * factor)
        g = int(14 + 22 * factor)
        b = int(28 + 65 * factor)
        d.line([(0, y), (W, y)], fill=(r, g, b, 255))
    return img


def _draw_icon(draw, icon_type, x, y, size=32, color=(56, 189, 248, 255)):
    """Draws crisp geometric tech icons."""
    if icon_type == "code":
        draw.line([(x + 8, y + 6), (x + 2, y + 16), (x + 8, y + 26)], fill=color, width=3)
        draw.line([(x + 24, y + 6), (x + 30, y + 16), (x + 24, y + 26)], fill=color, width=3)
        draw.line([(x + 19, y + 4), (x + 13, y + 28)], fill=color, width=2)
    elif icon_type == "doc":
        draw.rounded_rectangle([(x + 4, y + 2), (x + 26, y + 30)], radius=3, outline=color, width=2)
        draw.line([(x + 9, y + 10), (x + 21, y + 10)], fill=color, width=2)
        draw.line([(x + 9, y + 16), (x + 21, y + 16)], fill=color, width=2)
        draw.line([(x + 9, y + 22), (x + 17, y + 22)], fill=color, width=2)
    elif icon_type == "chart":
        draw.rectangle([(x + 4, y + 18), (x + 8, y + 28)], fill=color)
        draw.rectangle([(x + 12, y + 12), (x + 16, y + 28)], fill=color)
        draw.rectangle([(x + 20, y + 6), (x + 24, y + 28)], fill=color)
        draw.line([(x + 2, y + 29), (x + 28, y + 29)], fill=color, width=2)
    elif icon_type == "lightbulb":
        draw.ellipse([(x + 6, y + 4), (x + 24, y + 20)], outline=color, width=2)
        draw.line([(x + 11, y + 24), (x + 19, y + 24)], fill=color, width=2)
        draw.line([(x + 12, y + 27), (x + 18, y + 27)], fill=color, width=2)
    elif icon_type == "chat":
        draw.rounded_rectangle([(x + 3, y + 5), (x + 27, y + 23)], radius=5, outline=color, width=2)
        draw.ellipse([(x + 8, y + 13), (x + 10, y + 15)], fill=color)
        draw.ellipse([(x + 14, y + 13), (x + 16, y + 15)], fill=color)
        draw.ellipse([(x + 20, y + 13), (x + 22, y + 15)], fill=color)
    else:  # globe / network
        draw.ellipse([(x + 4, y + 4), (x + 26, y + 26)], outline=color, width=2)
        draw.line([(x + 4, y + 15), (x + 26, y + 15)], fill=color, width=2)
        draw.line([(x + 15, y + 4), (x + 15, y + 26)], fill=color, width=2)


def _wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        test = f"{cur} {word}".strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _draw_top_bar(draw, handle, index, total):
    f_handle = _font(32)
    draw.text((MARGIN, 65), handle, font=f_handle, fill=(255, 255, 255, 220))
    h_len = draw.textlength(handle, font=f_handle)
    draw.line([(MARGIN + h_len + 20, 81), (MARGIN + h_len + 120, 81)], fill=(255, 255, 255, 100), width=2)

    f_counter = _font(34)
    label = f"{index}/{total}"
    cw = draw.textlength(label, font=f_counter)
    draw.text((W - MARGIN - cw, 65), label, font=f_counter, fill=(255, 255, 255, 200))


def _slide_cover(bg, data, handle, index, total):
    # Dark vignette overlay
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_ov = ImageDraw.Draw(overlay)
    for y in range(H):
        if y < 460:
            alpha = int(190 * (1 - y / 460) + 70)
        elif y > 680:
            alpha = int(130 + 115 * ((y - 680) / (H - 680)))
        else:
            alpha = 75
        d_ov.line([(0, y), (W, y)], fill=(8, 12, 24, min(240, alpha)))

    base = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(base)
    _draw_top_bar(draw, handle, index, total)

    # --- Headline Hook ---
    hook = data.get("cover_hook", "")
    cyan_term = data.get("cover_highlight_cyan", "")
    orange_term = data.get("cover_highlight_orange", "")
    f_title = _font(68)

    # Wrap title into lines
    lines = _wrap(draw, hook, f_title, W - 2 * MARGIN)
    y_text = 155
    for line in lines[:5]:
        x_text = MARGIN
        words = line.split()
        for w_word in words:
            clean_w = re.sub(r"[^a-zA-Z0-9]", "", w_word).lower()
            color = (255, 255, 255, 255)
            if cyan_term and clean_w in cyan_term.lower():
                color = (56, 189, 248, 255)
            elif orange_term and clean_w in orange_term.lower():
                color = (251, 146, 60, 255)
            draw.text((x_text, y_text), w_word, font=f_title, fill=color)
            x_text += draw.textlength(w_word + " ", font=f_title)
        y_text += 80

    # --- Glassmorphic Cards (up to 8) ---
    cards = data.get("cards", [])
    if not cards:
        cards = [
            {"icon": "doc", "line1": "Reads &", "line2": "understands docs"},
            {"icon": "lightbulb", "line1": "Solves complex", "line2": "problems"},
            {"icon": "code", "line1": "Writes", "line2": "code"},
            {"icon": "chart", "line1": "Creates visuals", "line2": "& designs"},
            {"icon": "chat", "line1": "Holds natural", "line2": "dialogue"},
            {"icon": "globe", "line1": "Researches", "line2": "the web live"},
            {"icon": "calendar", "line1": "Automates multi-", "line2": "step tasks"},
            {"icon": "chart", "line1": "Finds data", "line2": "& insights"},
        ]

    grid_y = max(y_text + 25, 660)
    card_w = 215
    card_h = 160
    gap_x = 24
    gap_y = 20

    card_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_card = ImageDraw.Draw(card_layer)
    f_card = _font(21)

    for i, c in enumerate(cards[:8]):
        row = i // 4
        col = i % 4
        cx = MARGIN + col * (card_w + gap_x)
        cy = grid_y + row * (card_h + gap_y)

        d_card.rounded_rectangle(
            [(cx, cy), (cx + card_w, cy + card_h)],
            radius=18,
            fill=(14, 28, 56, 175),
            outline=(56, 189, 248, 120),
            width=2,
        )
        _draw_icon(d_card, c.get("icon", "globe"), cx + int(card_w / 2) - 16, cy + 22, size=32)
        l1, l2 = c.get("line1", ""), c.get("line2", "")
        w1 = d_card.textlength(l1, font=f_card)
        w2 = d_card.textlength(l2, font=f_card)
        d_card.text((cx + int((card_w - w1) / 2), cy + 82), l1, font=f_card, fill=(240, 246, 255, 255))
        d_card.text((cx + int((card_w - w2) / 2), cy + 110), l2, font=f_card, fill=(186, 210, 240, 230))

    base = Image.alpha_composite(base, card_layer)
    draw = ImageDraw.Draw(base)

    # --- Doodle Note with arrow ---
    doodle = data.get("doodle_note", "Most people still think it's just 'ChatGPT'")
    f_doodle = _font(25)
    doodle_x = W - MARGIN - 320
    doodle_y = grid_y + 355
    draw.text((doodle_x, doodle_y), doodle, font=f_doodle, fill=(225, 235, 255, 220))
    draw.line([(doodle_x + 10, doodle_y + 36), (doodle_x + 180, doodle_y + 36)], fill=(251, 146, 60, 220), width=3)
    draw.arc([(doodle_x - 45, doodle_y + 5), (doodle_x, doodle_y + 50)], start=160, end=270, fill=(255, 255, 255, 180), width=2)
    draw.line([(doodle_x - 40, doodle_y + 10), (doodle_x - 50, doodle_y + 18)], fill=(255, 255, 255, 180), width=2)

    # --- Bottom Left Callout ---
    foot_bold = data.get("footer_takeaway", "AI is not just a chatbot.")
    foot_sub = data.get("footer_subtext", "It's a general-purpose technology changing everything.")
    call_y = H - 180
    draw.rectangle([(MARGIN, call_y + 4), (MARGIN + 6, call_y + 70)], fill=(56, 189, 248, 255))
    draw.text((MARGIN + 24, call_y), foot_bold, font=_font(34), fill=(255, 255, 255, 255))
    draw.text((MARGIN + 24, call_y + 42), foot_sub, font=_font(28), fill=(180, 205, 235, 240))

    # --- Swipe Pill Button ---
    btn_w, btn_h = 190, 68
    bx, by = W - MARGIN - btn_w, H - 170
    draw.rounded_rectangle([(bx, by), (bx + btn_w, by + btn_h)], radius=34, fill=(15, 28, 50, 190), outline=(56, 189, 248, 180), width=2)
    f_btn = _font(30)
    btn_text = "Swipe  >"
    bw = draw.textlength(btn_text, font=f_btn)
    draw.text((bx + int((btn_w - bw) / 2), by + 16), btn_text, font=f_btn, fill=(255, 255, 255, 255))

    return base.convert("RGB")


def _slide_content(bg, slide, handle, index, total):
    # Dark blurred background overlay for high text contrast
    overlay = Image.new("RGBA", (W, H), (8, 14, 28, 225))
    base = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(base)
    _draw_top_bar(draw, handle, index, total)

    # --- Tag Pill ---
    tag = slide.get("tag", "BREAKDOWN").upper()
    f_tag = _font(24)
    tag_w = draw.textlength(tag, font=f_tag) + 36
    draw.rounded_rectangle([(MARGIN, 180), (MARGIN + tag_w, 226)], radius=12, fill=(30, 64, 175, 180), outline=(56, 189, 248, 200), width=1)
    draw.text((MARGIN + 18, 192), tag, font=f_tag, fill=(224, 242, 254, 255))

    # --- Headline ---
    title = slide.get("title", "")
    f_head = _font(64)
    y = 260
    for line in _wrap(draw, title, f_head, W - 2 * MARGIN):
        draw.text((MARGIN, y), line, font=f_head, fill=(255, 255, 255, 255))
        y += 76

    # --- Glassmorphic Content Card ---
    card_top = y + 40
    card_bot = H - 280
    card_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_card = ImageDraw.Draw(card_layer)
    d_card.rounded_rectangle([(MARGIN, card_top), (W - MARGIN, card_bot)], radius=24, fill=(15, 28, 52, 180), outline=(56, 189, 248, 100), width=2)
    base = Image.alpha_composite(base, card_layer)
    draw = ImageDraw.Draw(base)

    # Body / Points
    f_body = _font(40)
    body = slide.get("body", "")
    by = card_top + 45
    for line in _wrap(draw, body, f_body, W - 2 * MARGIN - 80):
        draw.text((MARGIN + 40, by), line, font=f_body, fill=(226, 232, 240, 255))
        by += 56

    # --- Bottom Key Takeaway Callout ---
    takeaway = slide.get("takeaway", "")
    if takeaway:
        f_take = _font(32)
        ty = H - 210
        draw.rounded_rectangle([(MARGIN, ty), (W - MARGIN, ty + 100)], radius=18, fill=(10, 24, 46, 210), outline=(251, 146, 60, 160), width=2)
        draw.text((MARGIN + 30, ty + 16), "KEY TAKEAWAY", font=_font(22), fill=(251, 146, 60, 255))
        draw.text((MARGIN + 30, ty + 46), takeaway, font=f_take, fill=(255, 255, 255, 255))

    return base.convert("RGB")


def _slide_outro(bg, source_name, handle, index, total):
    overlay = Image.new("RGBA", (W, H), (8, 14, 28, 230))
    base = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(base)
    _draw_top_bar(draw, handle, index, total)

    y = 300
    f_big = _font(72)
    draw.text((MARGIN, y), "Follow", font=f_big, fill=(255, 255, 255, 255))
    y += 85
    draw.text((MARGIN, y), handle, font=f_big, fill=(56, 189, 248, 255))
    y += 120

    f_sub = _font(42)
    for line in _wrap(draw, "For daily sharp breakdowns on AI, startups, and operational leverage.", f_sub, W - 2 * MARGIN):
        draw.text((MARGIN, y), line, font=f_sub, fill=(203, 213, 225, 255))
        y += 58

    # Question Box
    qy = H - 420
    draw.rounded_rectangle([(MARGIN, qy), (W - MARGIN, qy + 170)], radius=20, fill=(15, 28, 52, 190), outline=(56, 189, 248, 120), width=2)
    draw.text((MARGIN + 40, qy + 35), "What is your take on this?", font=_font(38), fill=(255, 255, 255, 255))
    draw.text((MARGIN + 40, qy + 90), "Share your thoughts in the comments below 👇", font=_font(30), fill=(148, 163, 184, 255))

    # Source Credit
    draw.text((MARGIN, H - 120), f"Source: {source_name}", font=_font(28), fill=(148, 163, 184, 200))

    return base.convert("RGB")


def render(data, source_name, handle, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    prompt = data.get("image_prompt", "")
    bg = _fetch_ai_background(prompt)

    slides_content = data.get("slides", [])
    total_slides = 1 + len(slides_content) + 1  # Cover + content slides + Outro

    paths = []
    # 1. Cover Slide
    cover_img = _slide_cover(bg, data, handle, 1, total_slides)
    p1 = os.path.join(out_dir, "slide_1.jpg")
    cover_img.save(p1, "JPEG", quality=95)
    paths.append(p1)

    # 2. Content Slides
    for i, slide in enumerate(slides_content, 2):
        s_img = _slide_content(bg, slide, handle, i, total_slides)
        pi = os.path.join(out_dir, f"slide_{i}.jpg")
        s_img.save(pi, "JPEG", quality=95)
        paths.append(pi)

    # 3. Outro Slide
    outro_img = _slide_outro(bg, source_name, handle, total_slides, total_slides)
    p_last = os.path.join(out_dir, f"slide_{total_slides}.jpg")
    outro_img.save(p_last, "JPEG", quality=95)
    paths.append(p_last)

    return paths
