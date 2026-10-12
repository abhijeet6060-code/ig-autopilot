"""Renders carousel slides (1080x1350, 4:5) with Pillow."""
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 90
PALETTES = [
    ((15, 23, 42), (30, 64, 175)),
    ((17, 24, 39), (109, 40, 217)),
    ((3, 7, 18), (13, 148, 136)),
    ((24, 24, 27), (190, 70, 30)),
]
FONT_PATHS = [
    os.getenv("FONT_PATH"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def _font(size):
    for p in FONT_PATHS:
        if p and os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)


def _gradient(c1, c2):
    col = Image.new("RGB", (1, H))
    for y in range(H):
        col.putpixel((0, y), tuple(int(c1[i] + (c2[i] - c1[i]) * y / H) for i in range(3)))
    return col.resize((W, H))


def _wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        test = f"{cur} {word}".strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _block(draw, text, font, y, fill, spacing=1.25):
    for line in _wrap(draw, text, font, W - 2 * MARGIN):
        draw.text((MARGIN, y), line, font=font, fill=fill)
        y += int(font.size * spacing)
    return y


def _slide(palette, title, body, footer, index, total, big=False):
    img = _gradient(*palette)
    d = ImageDraw.Draw(img)
    d.text((MARGIN, 80), footer, font=_font(34), fill=(255, 255, 255, 180))
    if total > 1:
        label = f"{index}/{total}"
        d.text((W - MARGIN - d.textlength(label, font=_font(34)), 80), label,
               font=_font(34), fill=(255, 255, 255))
    if big:
        y = _block(d, title, _font(88), 380, (255, 255, 255), 1.2)
        d.text((MARGIN, H - 200), "Swipe  >", font=_font(40), fill=(255, 255, 255))
    else:
        y = _block(d, title, _font(70), 300, (255, 255, 255), 1.2)
        d.rectangle([MARGIN, y + 20, MARGIN + 120, y + 26], fill=(255, 255, 255))
        _block(d, body, _font(46), y + 70, (225, 232, 245), 1.4)
    return img


def render(data, source_name, handle, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    palette = random.choice(PALETTES)
    slides = [(data["cover_hook"], "", True)]
    slides += [(s["title"], s["body"], False) for s in data["slides"]]
    slides.append((f"Follow {handle} for daily AI & business breakdowns", f"Source: {source_name}", False))

    paths = []
    for i, (title, body, big) in enumerate(slides, 1):
        img = _slide(palette, title, body, handle, i, len(slides), big)
        path = os.path.join(out_dir, f"slide_{i}.jpg")
        img.save(path, "JPEG", quality=92)
        paths.append(path)
    return paths
