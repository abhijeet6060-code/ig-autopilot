"""Renders multi-theme carousel slides (1080x1350, 4:5):
Alternates between:
1. 'dark': Deep rich gradients (Royal Blue, Violet, Teal, Copper)
2. 'light': Luxury minimalist editorial (Cream / Slate with deep charcoal typography)
3. 'glass': Dark frosted glassmorphism with glowing cyan accents
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 90

THEMES = [
    # 1. Dark Gradients
    {"type": "dark", "top": (15, 23, 42), "bot": (30, 64, 175), "text": (255, 255, 255), "sub": (226, 232, 240), "accent": (56, 189, 248), "name": "Royal Blue Dark"},
    {"type": "dark", "top": (17, 24, 39), "bot": (109, 40, 217), "text": (255, 255, 255), "sub": (226, 232, 240), "accent": (192, 132, 252), "name": "Deep Violet Dark"},
    {"type": "dark", "top": (3, 7, 18), "bot": (13, 148, 136), "text": (255, 255, 255), "sub": (226, 232, 240), "accent": (45, 212, 191), "name": "Midnight Teal Dark"},
    {"type": "dark", "top": (24, 24, 27), "bot": (180, 65, 25), "text": (255, 255, 255), "sub": (226, 232, 240), "accent": (251, 146, 60), "name": "Warm Copper Dark"},

    # 2. Light Minimalist Editorial
    {"type": "light", "top": (248, 250, 252), "bot": (241, 245, 249), "text": (15, 23, 42), "sub": (51, 65, 85), "accent": (37, 99, 235), "name": "Slate Minimal Light"},
    {"type": "light", "top": (255, 251, 245), "bot": (245, 238, 227), "text": (28, 25, 23), "sub": (68, 64, 60), "accent": (217, 70, 239), "name": "Cream Editorial Light"},
    {"type": "light", "top": (250, 250, 250), "bot": (235, 240, 248), "text": (10, 15, 30), "sub": (71, 85, 105), "accent": (14, 116, 144), "name": "Ice Clean Light"},

    # 3. Glassmorphic Combo
    {"type": "glass", "top": (8, 14, 28), "bot": (15, 32, 67), "text": (255, 255, 255), "sub": (203, 213, 225), "accent": (56, 189, 248), "name": "Cyber Glassmorphism"},
]

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
    return ImageFont.load_default()


def _render_bg(th):
    """Creates base background for the theme."""
    col = Image.new("RGB", (1, H))
    c1, c2 = th["top"], th["bot"]
    for y in range(H):
        factor = y / H
        r = int(c1[0] + (c2[0] - c1[0]) * factor)
        g = int(c1[1] + (c2[1] - c1[1]) * factor)
        b = int(c1[2] + (c2[2] - c1[2]) * factor)
        col.putpixel((0, y), (r, g, b))
    bg = col.resize((W, H), Image.Resampling.BICUBIC)

    # Optional subtle outer frame for light themes
    if th["type"] == "light":
        d = ImageDraw.Draw(bg)
        d.rectangle([(30, 30), (W - 30, H - 30)], outline=(226, 232, 240), width=2)

    return bg


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


def _draw_top_bar(draw, th, handle, index, total):
    f_bar = _font(34)
    # Color depends on theme
    bar_color = th["text"]
    alpha_fill = bar_color + (220,) if len(bar_color) == 4 else bar_color

    draw.text((MARGIN, 85), handle, font=f_bar, fill=alpha_fill)

    # Clean accent line after handle
    h_len = draw.textlength(handle, font=f_bar)
    line_col = th["accent"]
    draw.line([(MARGIN + h_len + 20, 101), (MARGIN + h_len + 100, 101)], fill=line_col, width=2)

    if total > 1:
        label = f"{index}/{total}"
        cw = draw.textlength(label, font=f_bar)
        draw.text((W - MARGIN - cw, 85), label, font=f_bar, fill=alpha_fill)


def _slide_cover(th, hook, handle, index, total):
    img = _render_bg(th)
    draw = ImageDraw.Draw(img)
    _draw_top_bar(draw, th, handle, index, total)

    # Headline Hook
    f_title = _font(82)
    lines = _wrap(draw, hook, f_title, W - 2 * MARGIN)

    y = 360
    for line in lines:
        draw.text((MARGIN, y), line, font=f_title, fill=th["text"])
        y += 105

    # Swipe CTA
    f_swipe = _font(38)
    if th["type"] == "glass":
        # Glowing pill
        bx, by = MARGIN, H - 210
        bw, bh = 210, 68
        draw.rounded_rectangle([(bx, by), (bx + bw, by + bh)], radius=34, fill=(15, 28, 55, 180), outline=th["accent"], width=2)
        draw.text((bx + 35, by + 14), "Swipe  >", font=f_swipe, fill=th["text"])
    else:
        # Minimalist text with accent dot
        draw.text((MARGIN, H - 200), "Swipe  >", font=f_swipe, fill=th["accent"])

    return img


def _slide_content(th, slide, handle, index, total):
    img = _render_bg(th)
    draw = ImageDraw.Draw(img)
    _draw_top_bar(draw, th, handle, index, total)

    # Category Tag Pill
    tag = slide.get("tag", "BREAKDOWN").upper()
    f_tag = _font(22)
    tag_w = draw.textlength(tag, font=f_tag) + 32
    if th["type"] == "light":
        draw.rounded_rectangle([(MARGIN, 210), (MARGIN + tag_w, 252)], radius=10, fill=(241, 245, 249), outline=th["accent"], width=1)
        draw.text((MARGIN + 16, 222), tag, font=f_tag, fill=th["accent"])
    else:
        draw.rounded_rectangle([(MARGIN, 210), (MARGIN + tag_w, 252)], radius=10, fill=(20, 35, 65), outline=th["accent"], width=1)
        draw.text((MARGIN + 16, 222), tag, font=f_tag, fill=th["accent"])

    # Headline
    title = slide.get("title", "")
    f_title = _font(66)
    y = 280
    for line in _wrap(draw, title, f_title, W - 2 * MARGIN):
        draw.text((MARGIN, y), line, font=f_title, fill=th["text"])
        y += 86

    # Card Container (Glassmorphic or Minimal Card)
    card_top = y + 35
    card_bot = H - 280
    f_body = _font(44)
    body = slide.get("body", "")

    if th["type"] == "glass":
        # Frosted glass card
        img_rgba = img.convert("RGBA")
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d_ov = ImageDraw.Draw(overlay)
        d_ov.rounded_rectangle([(MARGIN, card_top), (W - MARGIN, card_bot)], radius=22, fill=(15, 28, 55, 175), outline=(th["accent"][0], th["accent"][1], th["accent"][2], 120), width=2)
        img = Image.alpha_composite(img_rgba, overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
        by = card_top + 45
        for line in _wrap(draw, body, f_body, W - 2 * MARGIN - 80):
            draw.text((MARGIN + 40, by), line, font=f_body, fill=th["sub"])
            by += 64
    elif th["type"] == "light":
        # Clean white card on subtle background
        draw.rounded_rectangle([(MARGIN, card_top), (W - MARGIN, card_bot)], radius=18, fill=(255, 255, 255), outline=(226, 232, 240), width=2)
        by = card_top + 45
        for line in _wrap(draw, body, f_body, W - 2 * MARGIN - 80):
            draw.text((MARGIN + 40, by), line, font=f_body, fill=th["sub"])
            by += 64
    else:
        # Sleek accent underline + clean text
        draw.rectangle([(MARGIN, y + 25), (MARGIN + 110, y + 31)], fill=th["accent"])
        by = y + 70
        for line in _wrap(draw, body, f_body, W - 2 * MARGIN):
            draw.text((MARGIN, by), line, font=f_body, fill=th["sub"])
            by += 64

    # Bottom Takeaway
    takeaway = slide.get("takeaway", "")
    if takeaway:
        f_take = _font(34)
        ty = H - 230
        draw.rectangle([(MARGIN, ty), (MARGIN + 6, ty + 68)], fill=th["accent"])
        draw.text((MARGIN + 25, ty + 12), takeaway, font=f_take, fill=th["text"])

    return img


def _slide_outro(th, source_name, handle, index, total):
    img = _render_bg(th)
    draw = ImageDraw.Draw(img)
    _draw_top_bar(draw, th, handle, index, total)

    y = 360
    f_big = _font(74)
    draw.text((MARGIN, y), "Follow", font=f_big, fill=th["text"])
    y += 95
    draw.text((MARGIN, y), handle, font=f_big, fill=th["accent"])
    y += 120

    f_sub = _font(44)
    for line in _wrap(draw, "For daily sharp breakdowns on AI, startups, and operational leverage.", f_sub, W - 2 * MARGIN):
        draw.text((MARGIN, y), line, font=f_sub, fill=th["sub"])
        y += 64

    # Source credit
    draw.text((MARGIN, H - 180), f"Source: {source_name}", font=_font(34), fill=th["sub"])

    return img


def render(data, source_name, handle, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    # Dynamically select from Dark, Light, or Glassmorphic themes
    theme = random.choice(THEMES)
    print(f"[images] Rendering carousel with theme: {theme['name']} ({theme['type']})")

    hook = data.get("cover_hook", "")
    slides_content = data.get("slides", [])
    total_slides = 1 + len(slides_content) + 1  # Cover + content slides + Outro

    paths = []
    # 1. Cover Slide
    p1 = os.path.join(out_dir, "slide_1.jpg")
    _slide_cover(theme, hook, handle, 1, total_slides).save(p1, "JPEG", quality=95)
    paths.append(p1)

    # 2. Content Slides
    for i, slide in enumerate(slides_content, 2):
        pi = os.path.join(out_dir, f"slide_{i}.jpg")
        _slide_content(theme, slide, handle, i, total_slides).save(pi, "JPEG", quality=95)
        paths.append(pi)

    # 3. Outro Slide
    p_last = os.path.join(out_dir, f"slide_{total_slides}.jpg")
    _slide_outro(theme, source_name, handle, total_slides, total_slides).save(p_last, "JPEG", quality=95)
    paths.append(p_last)

    return paths
