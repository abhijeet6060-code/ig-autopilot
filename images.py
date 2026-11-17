"""Vibrant 3D Gradient Tech & Creator Carousel Generator (1080x1080, 1:1).

Exact 1-to-1 match to user reference creative:
- Soft off-white canvas with dual ambient purple/lavender radial glow
- Floating 3D isometric AI glass tile with neon backlighting
- Iconic purple-to-indigo gradient pill headline with curved brush swoosh underline
- 6-card feature grid with custom gradient vector icons (Document, Bar Chart, Palette, Code, Checklist, Graduation Cap)
- Bottom "Follow @abhijeetkumar.founder" CTA system with spark lines and profile badge
"""
import datetime
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1080

FONT_PATHS = {
    "bold": ["fonts/Inter.ttf", "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"],
    "regular": ["fonts/Inter.ttf", "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"],
    "mono": ["C:/Windows/Fonts/consola.ttf", "fonts/Inter.ttf"],
}

FONT_CACHE = {}


def _get_font(kind, size):
    key = (kind, size)
    if key in FONT_CACHE:
        return FONT_CACHE[key]
    for p in FONT_PATHS.get(kind, FONT_PATHS["regular"]):
        if p and os.path.exists(p):
            try:
                f = ImageFont.truetype(p, size)
                FONT_CACHE[key] = f
                return f
            except Exception:
                pass
    return ImageFont.load_default()


THEMES = [
    # 0. Primary Reference: Electric Violet & Royal Indigo
    {
        "id": 0,
        "name": "Electric Violet",
        "day": "Everyday",
        "glow_tr": (168, 85, 247),       # Purple glow top right
        "glow_bl": (192, 132, 252),      # Lavender glow bottom left
        "grad_start": (124, 58, 237),    # #7C3AED Vibrant Purple
        "grad_end": (99, 102, 241),      # #6366F1 Royal Indigo
        "accent": (124, 58, 237),
        "card_shadow": (99, 102, 241, 28),
        "text_primary": (15, 23, 42),
        "text_secondary": (71, 85, 105),
    },
]


def get_theme(theme_idx=None):
    return THEMES[0]


def _create_linear_gradient(w, h, color1, color2, direction="horizontal"):
    """Creates a smooth RGBA linear gradient surface."""
    grad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(grad)
    steps = w if direction == "horizontal" else h
    for i in range(steps):
        ratio = i / float(steps)
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        a = int(color1[3] * (1 - ratio) + color2[3] * ratio) if len(color1) > 3 else 255
        if direction == "horizontal":
            draw.line([(i, 0), (i, h)], fill=(r, g, b, a))
        else:
            draw.line([(0, i), (w, i)], fill=(r, g, b, a))
    return grad


def _draw_gradient_pill(base, x, y, w, h, radius, color1, color2, direction="horizontal"):
    """Draws a rounded rectangle filled with a linear gradient."""
    grad = _create_linear_gradient(w, h, color1, color2, direction)
    mask = Image.new("L", (w, h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), (w, h)], radius=radius, fill=255)
    base.paste(grad, (x, y), mask)


def _create_ambient_background(th):
    """Renders the ambient gradient background from the reference image."""
    base = Image.new("RGBA", (W, H), (248, 250, 253, 255))
    
    # Top-right intense purple radial glow
    glow_tr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gtr_draw = ImageDraw.Draw(glow_tr)
    gtr_color = th["glow_tr"]
    for r in range(500, 20, -30):
        alpha = int(140 * (1.0 - (r / 500.0)**1.2))
        gtr_draw.ellipse([(960 - r, 80 - r), (960 + r, 80 + r)], fill=gtr_color + (alpha,))
    glow_tr = glow_tr.filter(ImageFilter.GaussianBlur(55))
    base = Image.alpha_composite(base, glow_tr)

    # Bottom-left lavender ambient glow
    glow_bl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gbl_draw = ImageDraw.Draw(glow_bl)
    gbl_color = th["glow_bl"]
    for r in range(420, 20, -30):
        alpha = int(120 * (1.0 - (r / 420.0)**1.2))
        gbl_draw.ellipse([(70 - r, 1000 - r), (70 + r, 1000 + r)], fill=gbl_color + (alpha,))
    glow_bl = glow_bl.filter(ImageFilter.GaussianBlur(50))
    base = Image.alpha_composite(base, glow_bl)
    
    return base


def _draw_card(base, th, x, y, w, h, radius=24):
    """Draws a clean white card with subtle drop shadow and hairline border."""
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.rounded_rectangle([(x, y + 6), (x + w, y + h + 6)], radius=radius, fill=th["card_shadow"])
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    base = Image.alpha_composite(base, shadow)

    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(card)
    c_draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=radius, fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=1)
    base = Image.alpha_composite(base, card)
    return base


def _draw_vector_icon(draw, icon_type, cx, cy):
    """Draws high-fidelity vector gradient icons matching the reference image."""
    if icon_type == "content":
        draw.rounded_rectangle([(cx - 24, cy - 20), (cx + 8, cy + 20)], radius=4, fill=(168, 85, 247))
        draw.line([(cx - 16, cy - 8), (cx + 0, cy - 8)], fill=(255, 255, 255), width=3)
        draw.line([(cx - 16, cy), (cx + 0, cy)], fill=(255, 255, 255), width=3)
        draw.line([(cx - 16, cy + 8), (cx - 4, cy + 8)], fill=(255, 255, 255), width=3)
        draw.line([(cx + 4, cy + 18), (cx + 22, cy - 8)], fill=(99, 102, 241), width=6)
        draw.ellipse([(cx + 19, cy - 12), (cx + 25, cy - 6)], fill=(59, 130, 246))

    elif icon_type == "plan":
        draw.rounded_rectangle([(cx - 22, cy + 4), (cx - 10, cy + 20)], radius=3, fill=(147, 51, 234))
        draw.rounded_rectangle([(cx - 6, cy - 6), (cx + 6, cy + 20)], radius=3, fill=(99, 102, 241))
        draw.rounded_rectangle([(cx + 10, cy - 16), (cx + 22, cy + 20)], radius=3, fill=(59, 130, 246))
        draw.line([(cx - 22, cy - 2), (cx + 18, cy - 24)], fill=(37, 99, 235), width=4)
        draw.polygon([(cx + 22, cy - 26), (cx + 10, cy - 28), (cx + 18, cy - 14)], fill=(37, 99, 235))

    elif icon_type == "design":
        draw.rounded_rectangle([(cx - 24, cy - 18), (cx + 24, cy + 18)], radius=6, fill=(147, 51, 234))
        draw.polygon([(cx - 20, cy + 14), (cx - 8, cy - 2), (cx + 4, cy + 14)], fill=(255, 255, 255))
        draw.polygon([(cx - 2, cy + 14), (cx + 10, cy + 2), (cx + 20, cy + 14)], fill=(255, 255, 255))
        draw.ellipse([(cx + 8, cy - 12), (cx + 16, cy - 4)], fill=(255, 255, 255))

    elif icon_type == "code":
        f_mono = _get_font("bold", 34)
        tag_str = "</>"
        tw = draw.textlength(tag_str, font=f_mono)
        draw.text((cx - tw / 2, cy - 22), tag_str, font=f_mono, fill=(124, 58, 237))

    elif icon_type == "automate":
        draw.rounded_rectangle([(cx - 20, cy - 20), (cx + 20, cy + 20)], radius=8, fill=(139, 92, 246))
        draw.line([(cx - 10, cy), (cx - 2, cy + 8)], fill=(255, 255, 255), width=4)
        draw.line([(cx - 2, cy + 8), (cx + 11, cy - 7)], fill=(255, 255, 255), width=4)

    elif icon_type == "learn":
        draw.polygon([(cx, cy - 16), (cx + 24, cy - 4), (cx, cy + 8), (cx - 24, cy - 4)], fill=(99, 102, 241))
        draw.arc([(cx - 16, cy - 2), (cx + 16, cy + 16)], 0, 180, fill=(79, 70, 229), width=5)
        draw.line([(cx + 20, cy - 2), (cx + 24, cy + 14)], fill=(147, 51, 234), width=3)
        draw.ellipse([(cx + 22, cy + 14), (cx + 26, cy + 20)], fill=(147, 51, 234))


def _draw_top_pill(draw, index, total):
    f_pill = _get_font("bold", 22)
    pill_text = f"{index}/{total}"
    draw.rounded_rectangle([(65, 45), (150, 88)], radius=21, fill=(255, 255, 255), outline=(226, 232, 240), width=1)
    draw.text((90, 52), pill_text, font=f_pill, fill=(15, 23, 42))


def _draw_3d_badge(base):
    badge_path = "assets/3d_ai_badge.png"
    if os.path.exists(badge_path):
        badge_img = Image.open(badge_path).convert("RGBA")
        base.paste(badge_img, (710, 45), badge_img)


def _draw_follow_bar(base, th, handle):
    draw = ImageDraw.Draw(base)
    
    # 1. Floating "Follow" Gradient Pill
    follow_w = 185
    follow_h = 54
    follow_x = (W - follow_w) // 2
    follow_y = 830
    _draw_gradient_pill(base, follow_x, follow_y, follow_w, follow_h, radius=27,
                        color1=th["grad_start"], color2=th["grad_end"], direction="horizontal")

    draw = ImageDraw.Draw(base)
    f_fol = _get_font("bold", 28)
    fw = draw.textlength("Follow", font=f_fol)
    draw.text((follow_x + (follow_w - fw) / 2, follow_y + 10), "Follow", font=f_fol, fill=(255, 255, 255))

    # 3 Radiating Spark Rays
    sp_x = follow_x + follow_w + 10
    sp_y = follow_y + 12
    draw.line([(sp_x, sp_y + 10), (sp_x + 14, sp_y)], fill=th["accent"], width=3)
    draw.line([(sp_x - 2, sp_y + 18), (sp_x + 16, sp_y + 16)], fill=th["accent"], width=3)
    draw.line([(sp_x - 8, sp_y + 24), (sp_x + 8, sp_y + 28)], fill=th["accent"], width=3)

    # 2. Main White Outline Pill with User Handle
    pill2_w = 680
    pill2_h = 82
    pill2_x = (W - pill2_w) // 2
    pill2_y = 900
    draw.rounded_rectangle([(pill2_x, pill2_y), (pill2_x + pill2_w, pill2_y + pill2_h)], radius=41,
                           fill=(255, 255, 255), outline=th["accent"], width=2)

    # Purple circle icon inside pill
    u_cx, u_cy = pill2_x + 60, pill2_y + 41
    draw.ellipse([(u_cx - 24, u_cy - 24), (u_cx + 24, u_cy + 24)], fill=th["accent"])
    draw.ellipse([(u_cx - 6, u_cy - 12), (u_cx + 6, u_cy)], fill=(255, 255, 255))
    draw.arc([(u_cx - 13, u_cy - 4), (u_cx + 13, u_cy + 17)], 0, 180, fill=(255, 255, 255), width=4)
    draw.line([(u_cx + 11, u_cy - 2), (u_cx + 17, u_cy - 2)], fill=(255, 255, 255), width=2)
    draw.line([(u_cx + 14, u_cy - 5), (u_cx + 14, u_cy + 1)], fill=(255, 255, 255), width=2)

    # Username text
    f_user = _get_font("bold", 36)
    draw.text((pill2_x + 112, pill2_y + 18), handle, font=f_user, fill=th["text_primary"])

    # 3. Flanking divider lines & subtitle
    f_subcta = _get_font("regular", 22)
    cta_sub_text = "for practical AI tools, use cases and founder insights."
    draw.line([(140, 1012), (240, 1012)], fill=th["accent"], width=2)
    draw.line([(840, 1012), (940, 1012)], fill=th["accent"], width=2)

    lw = draw.textlength(cta_sub_text, font=f_subcta)
    draw.text(((W - lw) / 2, 1000), cta_sub_text, font=f_subcta, fill=(51, 65, 85))


def _slide_cover(th, data, handle, index, total):
    base = _create_ambient_background(th)
    draw = ImageDraw.Draw(base)
    _draw_top_pill(draw, index, total)
    _draw_3d_badge(base)

    draw = ImageDraw.Draw(base)
    f_head = _get_font("bold", 64)

    title_main = data.get("cover_title_main", "Use AI in")
    title_accent = data.get("cover_title_accent", "Daily Work")
    subtitle = data.get("cover_subtitle", "Practical ways to save time, be more productive, and grow faster.")

    # Line 1: Main Hook (e.g. "Use AI in")
    draw.text((65, 100), title_main, font=f_head, fill=th["text_primary"])

    # Line 2: "Your [Daily Work]" with gradient pill & brush swoosh
    draw.text((65, 178), "Your ", font=f_head, fill=th["text_primary"])
    your_w = draw.textlength("Your ", font=f_head)

    accent_text = title_accent.strip()
    pill_text_w = draw.textlength(accent_text, font=f_head)
    pill_w = max(260, int(pill_text_w + 48))
    pill_h = 78
    pill_x = 65 + int(your_w)
    pill_y = 175

    _draw_gradient_pill(base, pill_x, pill_y, pill_w, pill_h, radius=22,
                        color1=th["grad_start"], color2=th["grad_end"], direction="horizontal")

    draw = ImageDraw.Draw(base)
    draw.text((pill_x + 24, pill_y + 4), accent_text, font=f_head, fill=(255, 255, 255))

    # Curved brush swoosh underline under pill
    swoosh_y = pill_y + pill_h + 8
    draw.arc([(pill_x + 10, swoosh_y - 10), (pill_x + pill_w - 20, swoosh_y + 12)], 10, 170, fill=th["accent"], width=4)

    # Subtitle
    f_sub = _get_font("regular", 26)
    lines = subtitle.split("\n") if "\n" in subtitle else [subtitle[:42], subtitle[42:].strip()]
    sy = 285
    for l in lines:
        if l:
            draw.text((65, sy), l, font=f_sub, fill=(51, 65, 85))
            sy += 36

    # 6 Feature Cards (Matching user's reference)
    cards_data = [
        {"icon": "content", "title": "Create Content", "desc": "Blogs, captions, scripts\nin minutes"},
        {"icon": "plan", "title": "Analyze & Plan", "desc": "Get insights, ideas\nand strategy"},
        {"icon": "design", "title": "Design & Edit", "desc": "Images, posters,\nthumbnails with AI"},
        {"icon": "code", "title": "Build Faster", "desc": "Write, debug and\nship code quickly"},
        {"icon": "automate", "title": "Automate Tasks", "desc": "Save hours on\nrepetitive work"},
        {"icon": "learn", "title": "Learn Anything", "desc": "From new skills to\nbusiness & tech"},
    ]

    card_w = 295
    card_h = 180
    xs = [65, 392, 720]
    ys = [410, 615]

    for idx, c in enumerate(cards_data):
        row = idx // 3
        col = idx % 3
        cx = xs[col]
        cy = ys[row]

        base = _draw_card(base, th, cx, cy, card_w, card_h, radius=22)
        draw = ImageDraw.Draw(base)

        icon_cx = cx + card_w // 2
        icon_cy = cy + 44
        _draw_vector_icon(draw, c["icon"], icon_cx, icon_cy)

        f_ctitle = _get_font("bold", 26)
        tw = draw.textlength(c["title"], font=f_ctitle)
        draw.text((cx + (card_w - tw) / 2, cy + 78), c["title"], font=f_ctitle, fill=th["text_primary"])

        f_cdesc = _get_font("regular", 19)
        dlines = c["desc"].split("\n")
        ly = cy + 116
        for line in dlines:
            lw = draw.textlength(line, font=f_cdesc)
            draw.text((cx + (card_w - lw) / 2, ly), line, font=f_cdesc, fill=th["text_secondary"])
            ly += 24

    _draw_follow_bar(base, th, handle)
    return base.convert("RGB")


def _slide_content(th, slide, handle, index, total):
    base = _create_ambient_background(th)
    draw = ImageDraw.Draw(base)
    _draw_top_pill(draw, index, total)
    _draw_3d_badge(base)

    draw = ImageDraw.Draw(base)
    f_head = _get_font("bold", 62)

    title_main = slide.get("title_main", "Master The")
    title_accent = slide.get("title_accent", "Core Workflow")
    subtitle = slide.get("subtitle", "Strategic requirements and execution steps.")

    draw.text((65, 100), title_main, font=f_head, fill=th["text_primary"])

    accent_text = title_accent.strip()
    pill_text_w = draw.textlength(accent_text, font=f_head)
    pill_w = max(260, int(pill_text_w + 48))
    pill_h = 78
    pill_x = 65
    pill_y = 175

    _draw_gradient_pill(base, pill_x, pill_y, pill_w, pill_h, radius=22,
                        color1=th["grad_start"], color2=th["grad_end"], direction="horizontal")

    draw = ImageDraw.Draw(base)
    draw.text((pill_x + 24, pill_y + 4), accent_text, font=f_head, fill=(255, 255, 255))
    swoosh_y = pill_y + pill_h + 8
    draw.arc([(pill_x + 10, swoosh_y - 10), (pill_x + pill_w - 20, swoosh_y + 12)], 10, 170, fill=th["accent"], width=4)

    f_sub = _get_font("regular", 26)
    draw.text((65, 285), subtitle, font=f_sub, fill=(51, 65, 85))

    # 3 Large Feature Breakdown Cards
    bullets = slide.get("bullets", ["Direct verified facts", "Actionable takeaways", "Best founder use cases"])
    icons = ["content", "automate", "plan"]
    card_w = 950
    card_h = 105
    sy = 390

    for i, b in enumerate(bullets[:3]):
        cy = sy + i * 125
        base = _draw_card(base, th, 65, cy, card_w, card_h, radius=20)
        draw = ImageDraw.Draw(base)

        _draw_vector_icon(draw, icons[i % len(icons)], 115, cy + 52)
        f_b = _get_font("bold", 30)
        draw.text((165, cy + 24), b, font=f_b, fill=th["text_primary"])
        f_desc = _get_font("regular", 21)
        draw.text((165, cy + 62), f"Critical tactical element #{i+1} for high-retention execution.", font=f_desc, fill=th["text_secondary"])

    # Bottom Founder Rule Box
    takeaway = slide.get("takeaway", "Focus on defensible execution, not narrative momentum.")
    take_y = sy + 3 * 125 + 10
    base = _draw_card(base, th, 65, take_y, card_w, 85, radius=18)
    draw = ImageDraw.Draw(base)
    
    # Left accent indicator
    draw.rounded_rectangle([(80, take_y + 18), (86, take_y + 68)], radius=3, fill=th["accent"])
    draw.text((105, take_y + 16), "FOUNDER RULE //", font=_get_font("bold", 20), fill=th["accent"])
    draw.text((105, take_y + 44), takeaway, font=_get_font("bold", 24), fill=th["text_primary"])

    _draw_follow_bar(base, th, handle)
    return base.convert("RGB")


def _slide_outro(th, source_name, data, handle, index, total):
    base = _create_ambient_background(th)
    draw = ImageDraw.Draw(base)
    _draw_top_pill(draw, index, total)
    _draw_3d_badge(base)

    draw = ImageDraw.Draw(base)
    f_head = _get_font("bold", 62)

    cta_keyword = data.get("cta_keyword", "TOOLS").upper()
    title_main = "Get The Full"
    title_accent = f"{cta_keyword} Toolkit"

    draw.text((65, 100), title_main, font=f_head, fill=th["text_primary"])

    accent_text = title_accent.strip()
    pill_text_w = draw.textlength(accent_text, font=f_head)
    pill_w = max(280, int(pill_text_w + 48))
    pill_h = 78
    pill_x = 65
    pill_y = 175

    _draw_gradient_pill(base, pill_x, pill_y, pill_w, pill_h, radius=22,
                        color1=th["grad_start"], color2=th["grad_end"], direction="horizontal")

    draw = ImageDraw.Draw(base)
    draw.text((pill_x + 24, pill_y + 4), accent_text, font=f_head, fill=(255, 255, 255))
    swoosh_y = pill_y + pill_h + 8
    draw.arc([(pill_x + 10, swoosh_y - 10), (pill_x + pill_w - 20, swoosh_y + 12)], 10, 170, fill=th["accent"], width=4)

    f_sub = _get_font("regular", 26)
    draw.text((65, 285), "Save this post and comment below for the complete raw resources.", font=f_sub, fill=(51, 65, 85))

    # 3 Large Resource Delivery Cards
    assets = [
        ("content", "Prompt Templates", "Direct copy-paste prompts tested for 2026"),
        ("automate", "Automated Workflows", "Zero-setup scripts & verified founder tool links"),
        ("plan", "Execution Blueprint", "Full tactical breakdown and strategic checklist"),
    ]
    card_w = 950
    card_h = 105
    sy = 390

    for i, (ic, atitle, adesc) in enumerate(assets):
        cy = sy + i * 125
        base = _draw_card(base, th, 65, cy, card_w, card_h, radius=20)
        draw = ImageDraw.Draw(base)

        _draw_vector_icon(draw, ic, 115, cy + 52)
        f_b = _get_font("bold", 30)
        draw.text((165, cy + 24), atitle, font=f_b, fill=th["text_primary"])
        f_desc = _get_font("regular", 21)
        draw.text((165, cy + 62), adesc, font=f_desc, fill=th["text_secondary"])

    # Action Comment Box
    take_y = sy + 3 * 125 + 10
    base = _draw_card(base, th, 65, take_y, card_w, 85, radius=18)
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([(80, take_y + 18), (86, take_y + 68)], radius=3, fill=th["accent"])
    draw.text((105, take_y + 16), "INSTANT ACCESS //", font=_get_font("bold", 20), fill=th["accent"])
    draw.text((105, take_y + 44), f'Comment "{cta_keyword}" on this post to receive the full guide.', font=_get_font("bold", 24), fill=th["text_primary"])

    _draw_follow_bar(base, th, handle)
    return base.convert("RGB")


def render(data, source_name, handle, out_dir, theme_idx=None):
    os.makedirs(out_dir, exist_ok=True)
    theme = get_theme(theme_idx)
    print(f"[images] Rendering 3D Gradient Creator Carousel matching user reference style")

    slides_content = data.get("slides", [])
    total_slides = 1 + len(slides_content) + 1

    paths = []
    # 1. Cover Slide (Exact 6-card feature grid matching reference)
    p1 = os.path.join(out_dir, "slide_1.jpg")
    _slide_cover(theme, data, handle, 1, total_slides).save(p1, "JPEG", quality=95)
    paths.append(p1)

    # 2. Content Slides
    for i, slide in enumerate(slides_content, 2):
        pi = os.path.join(out_dir, f"slide_{i}.jpg")
        _slide_content(theme, slide, handle, i, total_slides).save(pi, "JPEG", quality=95)
        paths.append(pi)

    # 3. Outro CTA Slide
    p_last = os.path.join(out_dir, f"slide_{total_slides}.jpg")
    _slide_outro(theme, source_name, data, handle, total_slides, total_slides).save(p_last, "JPEG", quality=95)
    paths.append(p_last)

    print(f"[images] Rendered {len(paths)} slides in {out_dir}")
    return paths
