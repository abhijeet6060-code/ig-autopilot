"""Renders clean, bold founder carousel slides (1080x1350, 4:5) with rich gradients."""
import os
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 90

PALETTES = [
    # (top_rgb, bottom_rgb, name)
    ((15, 23, 42), (30, 64, 175), "Royal Blue"),
    ((17, 24, 39), (109, 40, 217), "Deep Violet"),
    ((3, 7, 18), (13, 148, 136), "Midnight Teal"),
    ((24, 24, 27), (180, 65, 25), "Warm Copper"),
    ((10, 25, 47), (20, 85, 185), "Electric Navy"),
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


def _gradient(c1, c2):
    """Draws a smooth 4:5 vertical gradient."""
    col = Image.new("RGB", (1, H))
    for y in range(H):
        factor = y / H
        r = int(c1[0] + (c2[0] - c1[0]) * factor)
        g = int(c1[1] + (c2[1] - c1[1]) * factor)
        b = int(c1[2] + (c2[2] - c1[2]) * factor)
        col.putpixel((0, y), (r, g, b))
    return col.resize((W, H), Image.Resampling.BICUBIC)


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
    f_handle = _font(34)
    draw.text((MARGIN, 85), handle, font=f_handle, fill=(255, 255, 255, 220))

    if total > 1:
        f_counter = _font(34)
        label = f"{index}/{total}"
        cw = draw.textlength(label, font=f_counter)
        draw.text((W - MARGIN - cw, 85), label, font=f_counter, fill=(255, 255, 255, 220))


def _slide_cover(palette, hook, handle, index, total):
    img = _gradient(palette[0], palette[1])
    draw = ImageDraw.Draw(img)
    _draw_top_bar(draw, handle, index, total)

    # Big, bold, clean headline
    f_title = _font(82)
    lines = _wrap(draw, hook, f_title, W - 2 * MARGIN)

    # Position in center-upper area
    y = 380
    for line in lines:
        draw.text((MARGIN, y), line, font=f_title, fill=(255, 255, 255, 255))
        y += 105

    # Bottom swipe indicator
    f_swipe = _font(40)
    draw.text((MARGIN, H - 200), "Swipe  >", font=f_swipe, fill=(255, 255, 255, 240))

    return img


def _slide_content(palette, slide, handle, index, total):
    img = _gradient(palette[0], palette[1])
    draw = ImageDraw.Draw(img)
    _draw_top_bar(draw, handle, index, total)

    # Title
    title = slide.get("title", "")
    f_title = _font(68)
    y = 280
    for line in _wrap(draw, title, f_title, W - 2 * MARGIN):
        draw.text((MARGIN, y), line, font=f_title, fill=(255, 255, 255, 255))
        y += 88

    # Sleek accent bar
    draw.rectangle([(MARGIN, y + 25), (MARGIN + 120, y + 31)], fill=(255, 255, 255, 240))
    y += 80

    # Body text
    body = slide.get("body", "")
    f_body = _font(46)
    for line in _wrap(draw, body, f_body, W - 2 * MARGIN):
        draw.text((MARGIN, y), line, font=f_body, fill=(226, 232, 240, 255))
        y += 68

    # Optional takeaway at bottom
    takeaway = slide.get("takeaway", "")
    if takeaway:
        f_take = _font(36)
        ty = H - 240
        draw.rectangle([(MARGIN, ty), (MARGIN + 6, ty + 70)], fill=(251, 146, 60, 255))
        draw.text((MARGIN + 25, ty + 12), takeaway, font=f_take, fill=(255, 255, 255, 255))

    return img


def _slide_outro(palette, source_name, handle, index, total):
    img = _gradient(palette[0], palette[1])
    draw = ImageDraw.Draw(img)
    _draw_top_bar(draw, handle, index, total)

    y = 360
    f_big = _font(74)
    draw.text((MARGIN, y), "Follow", font=f_big, fill=(255, 255, 255, 255))
    y += 95
    draw.text((MARGIN, y), handle, font=f_big, fill=(255, 255, 255, 255))
    y += 120

    f_sub = _font(44)
    for line in _wrap(draw, "For daily sharp breakdowns on AI, startups, and operational leverage.", f_sub, W - 2 * MARGIN):
        draw.text((MARGIN, y), line, font=f_sub, fill=(215, 225, 240, 255))
        y += 64

    # Source credit
    draw.text((MARGIN, H - 180), f"Source: {source_name}", font=_font(34), fill=(180, 200, 225, 200))

    return img


def render(data, source_name, handle, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    palette = random.choice(PALETTES)

    hook = data.get("cover_hook", "")
    slides_content = data.get("slides", [])
    total_slides = 1 + len(slides_content) + 1  # Cover + content slides + Outro

    paths = []
    # 1. Cover Slide
    p1 = os.path.join(out_dir, "slide_1.jpg")
    _slide_cover(palette, hook, handle, 1, total_slides).save(p1, "JPEG", quality=95)
    paths.append(p1)

    # 2. Content Slides
    for i, slide in enumerate(slides_content, 2):
        pi = os.path.join(out_dir, f"slide_{i}.jpg")
        _slide_content(palette, slide, handle, i, total_slides).save(pi, "JPEG", quality=95)
        paths.append(pi)

    # 3. Outro Slide
    p_last = os.path.join(out_dir, f"slide_{total_slides}.jpg")
    _slide_outro(palette, source_name, handle, total_slides, total_slides).save(p_last, "JPEG", quality=95)
    paths.append(p_last)

    return paths
