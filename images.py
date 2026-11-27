"""Bold Swiss-editorial carousel generator (1080x1350, 4:5).

Design system (one place, every slide reads from it):
- Colours: Yellow #FED700, Ink #0B0909, Graphite #393939, Amber #EBB02A, Paper #EDEDED
- Type: Inter variable (Black / ExtraBold / Bold / Medium / Regular), tight negative
  tracking on display sizes, faux-oblique italics for kickers and statements.
- Layouts:
    cover      yellow, giant ink headline that fills the frame, italic kicker
    step       ink, italic "Step N", yellow headline, white body, paper panel
               that bleeds off the right edge with a numbered list
    statement  yellow, two big italic statements (the "rule" slide)
    outro      ink, comment-keyword CTA in yellow + follow line
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 96

YELLOW = (254, 215, 0)
INK = (11, 9, 9)
GRAPHITE = (57, 57, 57)
AMBER = (235, 176, 42)
PAPER = (237, 237, 237)
WHITE = (255, 255, 255)
MUTED_ON_INK = (190, 190, 186)

FONT_FILE = "fonts/Inter.ttf"
FALLBACKS = {
    900: ["C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    400: ["C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
}
_FONT_CACHE = {}
ITALIC_SHEAR = 0.21  # ~12 degrees, like Helvetica Oblique


def font(weight, size):
    """Inter variable font at a given weight (100-900) and pixel size."""
    key = (weight, size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    f = None
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, FONT_FILE)
    if os.path.exists(path):
        try:
            f = ImageFont.truetype(path, size)
            f.set_variation_by_axes([32 if size >= 40 else 14, weight])  # opsz, wght
        except Exception:
            f = None
    if f is None:
        for p in FALLBACKS[900 if weight >= 600 else 400]:
            if os.path.exists(p):
                f = ImageFont.truetype(p, size)
                break
    f = f or ImageFont.load_default()
    _FONT_CACHE[key] = f
    return f


# ---------------------------------------------------------------- text engine

def _tracking(size, display=True):
    """Negative letter-spacing in px; display sizes get tighter."""
    if not display:
        return 0
    return -round(size * (0.038 if size >= 90 else 0.022 if size >= 48 else 0.01))


def _gaps(text, n):
    """Letter gaps before index n that get tracking; word spaces keep full width."""
    return sum(1 for j in range(min(n, len(text) - 1)) if text[j] != " " and text[j + 1] != " ")


def text_width(text, f, tracking=0):
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    return d.textlength(text, font=f) + tracking * _gaps(text, len(text) - 1)


def _draw_tracked(draw, x, y, text, f, fill, tracking):
    if tracking == 0:
        draw.text((x, y), text, font=f, fill=fill)
        return
    # Position each glyph by the kerned length of its prefix, plus tracking.
    for i, ch in enumerate(text):
        if ch == " ":
            continue
        px = x + draw.textlength(text[:i], font=f) + tracking * _gaps(text, i)
        draw.text((px, y), ch, font=f, fill=fill)


def draw_line(base, x, y, text, f, fill, tracking=0, italic=False):
    """Draw one line of text, optionally faux-italic, onto an RGB(A) image."""
    if not italic:
        _draw_tracked(ImageDraw.Draw(base), x, y, text, f, fill, tracking)
        return
    asc, desc = f.getmetrics()
    lh = asc + desc
    tw = int(text_width(text, f, tracking)) + 8
    pad = int(ITALIC_SHEAR * lh) + 4
    layer = Image.new("RGBA", (tw + pad, lh), (0, 0, 0, 0))
    _draw_tracked(ImageDraw.Draw(layer), 0, 0, text, f, fill + (255,), tracking)
    # Shift each row right in proportion to its height above the baseline.
    layer = layer.transform(layer.size, Image.AFFINE,
                            (1, ITALIC_SHEAR, -ITALIC_SHEAR * asc, 0, 1, 0),
                            resample=Image.BICUBIC)
    base.alpha_composite(layer, (int(x), int(y))) if base.mode == "RGBA" else base.paste(layer, (int(x), int(y)), layer)


def wrap(text, f, max_w, tracking=0):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and text_width(trial, f, tracking) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def fit(text, weight, max_w, max_h, sizes, leading=0.98, max_lines=6):
    """Largest size from `sizes` whose wrapped block fits the box."""
    for s in sizes:
        f = font(weight, s)
        tr = _tracking(s)
        lines = wrap(text, f, max_w, tr)
        too_wide = any(text_width(l, f, tr) > max_w for l in lines)
        if not too_wide and len(lines) <= max_lines and len(lines) * s * leading <= max_h:
            return f, s, tr, lines
    s = sizes[-1]
    f = font(weight, s)
    return f, s, _tracking(s), wrap(text, f, max_w, _tracking(s))


def draw_block(base, x, y, lines, f, size, fill, tracking=0, leading=1.0, italic=False):
    """Draws wrapped lines; returns the y below the block."""
    asc, _ = f.getmetrics()
    top_trim = asc - size * 0.74  # pull cap-height to y so blocks align optically
    for line in lines:
        draw_line(base, x, y - top_trim, line, f, fill, tracking, italic)
        y += size * leading
    return y


# ---------------------------------------------------------------- chrome

def _chrome(base, handle, index, total, on_dark):
    """Small top/bottom furniture shared by every slide."""
    fg = MUTED_ON_INK if on_dark else INK
    f = font(600, 26)
    d = ImageDraw.Draw(base)
    # top-left brand square + handle
    d.rectangle([MARGIN, 64, MARGIN + 22, 86], fill=YELLOW if on_dark else INK)
    d.text((MARGIN + 38, 60), handle, font=f, fill=fg)
    # top-right counter
    counter = f"{index:02d} / {total:02d}"
    d.text((W - MARGIN - d.textlength(counter, font=f), 60), counter, font=f, fill=fg)
    # bottom-right swipe cue (not on last slide)
    if index < total:
        cue = "Swipe"
        fc = font(600, 26)
        cw = d.textlength(cue, font=fc)
        ax = W - MARGIN
        d.text((ax - cw - 52, H - 92), cue, font=fc, fill=fg)
        d.line([(ax - 40, H - 76), (ax, H - 76)], fill=fg, width=3)
        d.polygon([(ax, H - 76), (ax - 12, H - 84), (ax - 12, H - 68)], fill=fg)


# ---------------------------------------------------------------- slides

def _cover(data, handle, index, total):
    base = Image.new("RGB", (W, H), YELLOW)
    headline = data.get("cover_headline") or data.get("cover_hook", "")
    kicker = data.get("cover_kicker") or data.get("cover_subtitle", "")

    box_w = W - 2 * MARGIN
    f, s, tr, lines = fit(headline, 900, box_w, 820, list(range(200, 79, -6)), leading=0.98)
    block_h = len(lines) * s * 0.98
    y = 190 + max(0, (820 - block_h) * 0.55)
    y = draw_block(base, MARGIN - s * 0.03, y, lines, f, s, INK, tr, leading=0.98)

    if kicker:
        fk = font(800, 46)
        kl = wrap(kicker, fk, box_w - 40, -1)
        draw_block(base, MARGIN, y + 46, kl, fk, 46, INK, -1, leading=1.2, italic=True)

    _chrome(base, handle, index, total, on_dark=False)
    return base


def _step(slide, step_no, handle, index, total):
    base = Image.new("RGB", (W, H), INK)
    box_w = W - 2 * MARGIN

    label = slide.get("kicker") or f"Step {step_no}"
    fl = font(500, 48)
    y = draw_block(base, MARGIN, 170, [label], fl, 48, WHITE, -1, italic=True)

    headline = slide.get("headline") or f"{slide.get('title_main', '')} {slide.get('title_accent', '')}".strip()
    f, s, tr, lines = fit(headline, 800, box_w, 250, list(range(84, 51, -4)), leading=1.08, max_lines=3)
    y = draw_block(base, MARGIN, y + 40, lines, f, s, YELLOW, tr, leading=1.08)

    body = slide.get("body") or slide.get("subtitle", "")
    if body:
        fb = font(400, 38)
        bl = wrap(body, fb, box_w - 30, -1)[:4]
        y = draw_block(base, MARGIN, y + 34, bl, fb, 38, (232, 232, 228), -1, leading=1.32)

    # Paper panel that bleeds off the right edge (like a design-system sheet).
    bullets = [b for b in slide.get("bullets", []) if b][:3]
    if bullets:
        top = max(int(y + 60), 700)
        bottom = H - 150
        d = ImageDraw.Draw(base)
        d.rectangle([MARGIN, top, W, bottom], fill=PAPER)
        pl = slide.get("panel_label") or slide.get("tag", "").title() or "Key points"
        d.text((MARGIN + 40, top + 34), pl, font=font(500, 28), fill=GRAPHITE)
        row_h = (bottom - top - 100) / len(bullets)
        for i, b in enumerate(bullets):
            ry = top + 96 + i * row_h
            if i:
                d.line([(MARGIN + 40, ry - 6), (W, ry - 6)], fill=(205, 205, 203), width=2)
            num = f"{i + 1:02d}"
            fn = font(900, 64)
            draw_line(base, MARGIN + 40, ry + 6, num, fn, INK, -3)
            d.rectangle([MARGIN + 40, ry + 82, MARGIN + 74, ry + 88], fill=AMBER if i % 2 else YELLOW)
            fbt = font(700, 40)
            bl = wrap(b, fbt, W - MARGIN - 220 - 40, -1)[:2]
            draw_block(base, MARGIN + 180, ry + 26, bl, fbt, 40, INK, -1, leading=1.18)

    _chrome(base, handle, index, total, on_dark=True)
    return base


def _statement(statements, handle, index, total):
    base = Image.new("RGB", (W, H), YELLOW)
    box_w = W - 2 * MARGIN - 40
    statements = [s for s in statements if s][:2]
    # Pick one size that fits both statements together.
    chosen = None
    for s in range(78, 43, -4):
        f = font(800, s)
        tr = _tracking(s)
        blocks = [wrap(t, f, box_w, tr) for t in statements]
        total_h = sum(len(b) for b in blocks) * s * 1.12 + (len(blocks) - 1) * s * 1.3
        if total_h <= 860:
            chosen = (f, s, tr, blocks, total_h)
            break
    if chosen is None:
        s = 44
        f = font(800, s)
        tr = _tracking(s)
        blocks = [wrap(t, f, box_w, tr) for t in statements]
        chosen = (f, s, tr, blocks, 860)
    f, s, tr, blocks, total_h = chosen
    y = (H - total_h) / 2
    for b in blocks:
        y = draw_block(base, MARGIN + 10, y, b, f, s, INK, tr, leading=1.12, italic=True)
        y += s * 1.3
    _chrome(base, handle, index, total, on_dark=False)
    return base


def _outro(data, handle, index, total):
    base = Image.new("RGB", (W, H), INK)
    box_w = W - 2 * MARGIN
    kw = (data.get("cta_keyword") or "GUIDE").upper().strip()

    y = draw_block(base, MARGIN, 220, ["Want the full playbook?"], font(500, 48), 48, WHITE, -1, italic=True)

    f, s, tr, lines = fit(f"Comment “{kw}”", 900, box_w, 380, list(range(170, 71, -6)), leading=1.0, max_lines=2)
    y = draw_block(base, MARGIN - s * 0.03, y + 50, lines, f, s, YELLOW, tr, leading=1.0)

    sub = data.get("cta_subtext") or "I'll send you the complete guide."
    sub = sub[0].upper() + sub[1:].lower() if sub.isupper() else sub
    fb = font(400, 40)
    y = draw_block(base, MARGIN, y + 40, wrap(sub, fb, box_w, -1)[:3], fb, 40, (232, 232, 228), -1, leading=1.3)

    # Follow card
    d = ImageDraw.Draw(base)
    top = H - 380
    d.rectangle([MARGIN, top, W - MARGIN, top + 2], fill=GRAPHITE)
    draw_block(base, MARGIN, top + 60, ["Follow for daily AI"], font(800, 52), 52, WHITE, -2)
    draw_block(base, MARGIN, top + 130, ["playbooks for founders."], font(800, 52), 52, WHITE, -2)
    pill_y = top + 210
    fh = font(700, 34)
    pw = d.textlength(handle, font=fh) + 64
    d.rounded_rectangle([MARGIN, pill_y, MARGIN + pw, pill_y + 72], radius=36, fill=YELLOW)
    d.text((MARGIN + 32, pill_y + 15), handle, font=fh, fill=INK)

    _chrome(base, handle, index, total, on_dark=True)
    return base


# ---------------------------------------------------------------- entry point

def _statements_for(data):
    st = [s for s in data.get("statements", []) if isinstance(s, str) and s.strip()]
    if len(st) >= 2:
        return st[:2]
    takeaways = [s.get("takeaway", "") for s in data.get("slides", []) if s.get("takeaway")]
    return (st + takeaways)[:2]


def render(data, source_name, handle, out_dir, theme_idx=None):
    """Renders the carousel; returns slide paths. `theme_idx` kept for CLI compatibility."""
    os.makedirs(out_dir, exist_ok=True)
    steps = data.get("slides", [])
    statements = _statements_for(data)
    plan = [("cover", None)] + [("step", s) for s in steps]
    if len(statements) == 2:
        plan.append(("statement", statements))
    plan.append(("outro", None))
    total = len(plan)
    print(f"[images] Rendering Swiss-editorial carousel ({total} slides, 1080x1350)")

    paths = []
    step_no = 0
    for i, (kind, payload) in enumerate(plan, 1):
        if kind == "cover":
            img = _cover(data, handle, i, total)
        elif kind == "step":
            step_no += 1
            img = _step(payload, step_no, handle, i, total)
        elif kind == "statement":
            img = _statement(payload, handle, i, total)
        else:
            img = _outro(data, handle, i, total)
        p = os.path.join(out_dir, f"slide_{i}.jpg")
        img.convert("RGB").save(p, "JPEG", quality=95, subsampling=0)
        paths.append(p)

    print(f"[images] Rendered {len(paths)} slides in {out_dir}")
    return paths
