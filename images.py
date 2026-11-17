"""World-Class Social Media Creative Engine (1080x1350, 4:5).

Features:
- Atmospheric radial lighting & spotlight glowing background
- Micro-dot grid tech texture inspired by Linear, Raycast, and Vercel
- macOS glass window mockups with traffic light dots & dual-border highlights
- Realistic diffused gaussian drop shadows
- High-contrast visual metric badges & step counters
- 3D interactive CTA buttons with glossy top sheen
- 6 weekly rotating high-converting themes
"""
import datetime
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
MARGIN = 75

THEMES = [
    # 0. Monday: Electric Indigo / Modern Linear Dark
    {
        "id": 0,
        "name": "Electric Indigo",
        "day": "Monday",
        "bg_base": (11, 15, 25),          # #0B0F19 Deep Obsidian
        "bg_glow": (59, 130, 246, 50),     # Glowing Electric Blue Aura
        "dot_color": (30, 41, 59, 160),   # Subtle tech grid dots
        "card_bg": (20, 27, 45, 235),     # Glassmorphic Slate Card
        "card_border": (59, 130, 246, 90), # Glowing subtle border
        "card_border_inner": (255, 255, 255, 30),
        "text_primary": (255, 255, 255),  # Pure Crisp White
        "text_secondary": (148, 163, 184),# Slate Muted
        "accent": (56, 189, 248),         # #38BDF8 Cyan Glow
        "accent_secondary": (129, 140, 248),
        "tag_bg": (30, 41, 59),
        "tag_border": (56, 189, 248, 140),
        "btn_bg": (56, 189, 248),         # Glowing Cyan Button
        "btn_text": (11, 15, 25),         # Deep Black Text
        "is_dark": True,
    },
    # 1. Tuesday: Clean Luxury Editorial Light
    {
        "id": 1,
        "name": "Luxury Editorial Light",
        "day": "Tuesday",
        "bg_base": (250, 250, 252),        # #FAFAFC Off-white
        "bg_glow": (224, 231, 255, 120),   # Soft Indigo ambient aura
        "dot_color": (226, 232, 240, 200),# Soft dot grid
        "card_bg": (255, 255, 255, 245),  # Pure white card
        "card_border": (226, 232, 240, 255),
        "card_border_inner": (255, 255, 255, 255),
        "text_primary": (15, 23, 42),     # Deep Obsidian Ink
        "text_secondary": (100, 116, 139),# Muted Slate
        "accent": (37, 99, 235),          # Royal Blue Accent
        "accent_secondary": (79, 70, 229),
        "tag_bg": (238, 242, 255),
        "tag_border": (199, 210, 254, 255),
        "btn_bg": (15, 23, 42),           # Obsidian Black Button
        "btn_text": (255, 255, 255),
        "is_dark": False,
    },
    # 2. Wednesday: Cyber Emerald & Mint
    {
        "id": 2,
        "name": "Cyber Emerald",
        "day": "Wednesday",
        "bg_base": (8, 22, 18),           # Deep Pine Obsidian
        "bg_glow": (16, 185, 129, 45),    # Glowing Emerald Aura
        "dot_color": (20, 50, 40, 160),
        "card_bg": (14, 35, 28, 235),
        "card_border": (16, 185, 129, 90),
        "card_border_inner": (255, 255, 255, 25),
        "text_primary": (255, 255, 255),
        "text_secondary": (167, 243, 208),
        "accent": (52, 211, 153),         # Glowing Mint
        "accent_secondary": (110, 231, 183),
        "tag_bg": (20, 50, 40),
        "tag_border": (52, 211, 153, 140),
        "btn_bg": (52, 211, 153),
        "btn_text": (6, 78, 59),
        "is_dark": True,
    },
    # 3. Thursday: Warm Butter Champagne
    {
        "id": 3,
        "name": "Warm Butter Champagne",
        "day": "Thursday",
        "bg_base": (254, 252, 243),        # Warm Ivory
        "bg_glow": (254, 243, 199, 140),   # Golden warm ambient
        "dot_color": (243, 233, 207, 220),
        "card_bg": (255, 255, 255, 245),
        "card_border": (245, 235, 215, 255),
        "card_border_inner": (255, 255, 255, 255),
        "text_primary": (24, 24, 27),
        "text_secondary": (113, 113, 122),
        "accent": (217, 119, 6),          # Warm Amber
        "accent_secondary": (180, 83, 9),
        "tag_bg": (254, 243, 199),
        "tag_border": (253, 230, 138, 255),
        "btn_bg": (24, 24, 27),
        "btn_text": (255, 255, 255),
        "is_dark": False,
    },
    # 4. Friday: Sunset Neon & Purple
    {
        "id": 4,
        "name": "Neon Sunset",
        "day": "Friday",
        "bg_base": (22, 13, 31),          # Deep Velvet Purple
        "bg_glow": (236, 72, 153, 50),    # Magenta Glow
        "dot_color": (45, 25, 60, 160),
        "card_bg": (35, 20, 50, 235),
        "card_border": (236, 72, 153, 90),
        "card_border_inner": (255, 255, 255, 25),
        "text_primary": (255, 255, 255),
        "text_secondary": (244, 114, 182),
        "accent": (244, 63, 94),          # Neon Rose
        "accent_secondary": (168, 85, 247),
        "tag_bg": (50, 25, 70),
        "tag_border": (244, 63, 94, 140),
        "btn_bg": (244, 63, 94),
        "btn_text": (255, 255, 255),
        "is_dark": True,
    },
    # 5. Weekend: Stealth Monolith
    {
        "id": 5,
        "name": "Stealth Monolith",
        "day": "Weekend",
        "bg_base": (15, 15, 17),          # Pitch Charcoal
        "bg_glow": (245, 158, 11, 40),    # Warm Amber Candle Glow
        "dot_color": (32, 32, 36, 160),
        "card_bg": (25, 25, 28, 240),
        "card_border": (45, 45, 52, 255),
        "card_border_inner": (255, 255, 255, 20),
        "text_primary": (255, 255, 255),
        "text_secondary": (161, 161, 170),
        "accent": (245, 158, 11),         # Cyber Gold
        "accent_secondary": (217, 119, 6),
        "tag_bg": (35, 35, 40),
        "tag_border": (245, 158, 11, 140),
        "btn_bg": (245, 158, 11),
        "btn_text": (15, 15, 17),
        "is_dark": True,
    },
]

FONT_CACHE = {}


def _get_font(family, size):
    key = (family, size)
    if key in FONT_CACHE:
        return FONT_CACHE[key]
    paths = {
        "title": ["fonts/Inter.ttf", "C:/Windows/Fonts/segoeuib.ttf", "fonts/Impact.ttf"],
        "body": ["fonts/Inter.ttf", "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"],
        "serif": ["fonts/georgiab.ttf", "C:/Windows/Fonts/georgiab.ttf"],
    }
    for p in paths.get(family, paths["body"]):
        if p and os.path.exists(p):
            try:
                font = ImageFont.truetype(p, size)
                FONT_CACHE[key] = font
                return font
            except Exception:
                pass
    return ImageFont.load_default()


def get_theme(theme_idx=None):
    if theme_idx is not None and 0 <= theme_idx < len(THEMES):
        return THEMES[theme_idx]
    weekday = datetime.datetime.now().weekday()
    return THEMES[weekday % 6]


def _create_ambient_background(th):
    """Generates a rich canvas with radial glow spotlight and subtle dot grid."""
    base = Image.new("RGBA", (W, H), th["bg_base"] + (255,))
    
    # Radial Glow Layer
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    spot_cx, spot_cy = W // 2, 420
    max_radius = 480
    glow_color = th["bg_glow"]
    
    for r in range(max_radius, 40, -40):
        alpha = int(glow_color[3] * (1.0 - (r / max_radius)**1.5))
        c = (glow_color[0], glow_color[1], glow_color[2], max(alpha, 0))
        glow_draw.ellipse([(spot_cx - r, spot_cy - r), (spot_cx + r, spot_cy + r)], fill=c)
        
    glow = glow.filter(ImageFilter.GaussianBlur(50))
    base = Image.alpha_composite(base, glow)
    
    # Dot Grid Texture
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grid_draw = ImageDraw.Draw(grid)
    step = 36
    dot_color = th["dot_color"]
    for x in range(step // 2, W, step):
        for y in range(step // 2, H, step):
            grid_draw.ellipse([(x - 1, y - 1), (x + 1, y + 1)], fill=dot_color)
            
    base = Image.alpha_composite(base, grid)
    return base


def _draw_shadowed_card(base, th, x, y, w, h, radius=24, is_window=False):
    """Draws a premium glassmorphic card with a realistic diffused drop shadow."""
    # 1. Soft Diffused Shadow
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    shadow_fill = (0, 0, 0, 75 if th["is_dark"] else 35)
    s_draw.rounded_rectangle([(x, y + 14), (x + w, y + h + 14)], radius=radius, fill=shadow_fill)
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    base = Image.alpha_composite(base, shadow)
    
    # 2. Card Body
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(card)
    c_draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=radius, fill=th["card_bg"], outline=th["card_border"], width=2)
    c_draw.rounded_rectangle([(x + 2, y + 2), (x + w - 2, y + h - 2)], radius=radius - 2, outline=th["card_border_inner"], width=1)
    
    if is_window:
        header_h = 56
        c_draw.line([(x, y + header_h), (x + w, y + header_h)], fill=th["card_border"], width=1)
        dot_r = 6
        dx = x + 24
        dy = y + header_h // 2
        colors = [(255, 95, 86), (255, 189, 46), (39, 201, 63)]
        for i, dot_c in enumerate(colors):
            c_draw.ellipse([(dx + i * 22 - dot_r, dy - dot_r), (dx + i * 22 + dot_r, dy + dot_r)], fill=dot_c)
            
        f_pill = _get_font("body", 18)
        win_title = "SYSTEM INSIGHT // VERIFIED"
        c_draw.text((x + 105, dy - 10), win_title, font=f_pill, fill=th["text_secondary"])

    base = Image.alpha_composite(base, card)
    return base


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


def _draw_top_nav(draw, th, handle, index, total):
    bar_y = 52
    seg_spacing = 8
    total_w = W - 2 * MARGIN
    seg_w = (total_w - (total - 1) * seg_spacing) / total
    for i in range(total):
        sx = MARGIN + i * (seg_w + seg_spacing)
        fill_c = th["accent"] if i == (index - 1) else (th["text_primary"] if i < (index - 1) else th["dot_color"])
        draw.rounded_rectangle([(sx, bar_y), (sx + seg_w, bar_y + 5)], radius=2, fill=fill_c)

    f_brand = _get_font("title", 24)
    hy = 82
    draw.ellipse([(MARGIN, hy - 4), (MARGIN + 32, hy + 28)], fill=th["accent"])
    draw.text((MARGIN + 7, hy), "A", font=_get_font("title", 20), fill=(255, 255, 255) if not th["is_dark"] else (11, 15, 25))
    draw.text((MARGIN + 44, hy), handle, font=f_brand, fill=th["text_primary"])

    f_pill = _get_font("body", 22)
    pill_text = f"{index:02d} / {total:02d}"
    pw = draw.textlength(pill_text, font=f_pill) + 30
    px = W - MARGIN - pw
    draw.rounded_rectangle([(px, hy - 6), (px + pw, hy + 30)], radius=18, fill=th["tag_bg"], outline=th["tag_border"], width=1)
    draw.text((px + 15, hy), pill_text, font=f_pill, fill=th["accent"])


def _draw_footer(draw, th, handle, right_action="SWIPE NEXT  ➔"):
    fy = H - 90
    draw.line([(MARGIN, fy), (W - MARGIN, fy)], fill=th["card_border"], width=1)
    
    f_meta = _get_font("body", 24)
    draw.text((MARGIN, fy + 24), "FOUNDER PLAYBOOK", font=f_meta, fill=th["text_secondary"])
    rw = draw.textlength(right_action, font=f_meta)
    draw.text((W - MARGIN - rw, fy + 24), right_action, font=f_meta, fill=th["accent"])


def _slide_cover(th, data, handle, index, total):
    base = _create_ambient_background(th)
    
    card_w = W - 2 * MARGIN
    card_y = 440
    card_h = 490
    base = _draw_shadowed_card(base, th, MARGIN, card_y, card_w, card_h, radius=24, is_window=True)
    
    draw = ImageDraw.Draw(base)
    _draw_top_nav(draw, th, handle, index, total)
    
    ey = 165
    f_eye = _get_font("title", 22)
    kicker = "STRATEGIC BREAKDOWN // 2026 EDITION"
    kw = draw.textlength(kicker, font=f_eye) + 32
    draw.rounded_rectangle([(MARGIN, ey), (MARGIN + kw, ey + 38)], radius=19, fill=th["tag_bg"], outline=th["tag_border"], width=1)
    draw.text((MARGIN + 16, ey + 8), kicker, font=f_eye, fill=th["accent"])
    
    hy = ey + 60
    f_head = _get_font("title", 76)
    title_main = data.get("cover_title_main", "THE 7 FREE")
    title_accent = data.get("cover_title_accent", "AI TOOLS")
    
    draw.text((MARGIN, hy), title_main, font=f_head, fill=th["text_primary"])
    t1_w = draw.textlength(title_main, font=f_head)
    
    if MARGIN + t1_w + draw.textlength(" " + title_accent, font=f_head) <= W - MARGIN:
        draw.text((MARGIN + t1_w + 14, hy), title_accent, font=f_head, fill=th["accent"])
        hy += 88
    else:
        hy += 88
        draw.text((MARGIN, hy), title_accent, font=f_head, fill=th["accent"])
        hy += 88
        
    subtitle = data.get("cover_subtitle", "Verified tactical workflows to scale revenue & operations.")
    f_sub = _get_font("body", 34)
    for line in _wrap(draw, subtitle, f_sub, W - 2 * MARGIN):
        draw.text((MARGIN, hy), line, font=f_sub, fill=th["text_secondary"])
        hy += 44
        
    wy = card_y + 85
    bullets = data.get("cover_bullets", ["Direct verified prompt templates", "Zero setup steps or paid seats", "High-leverage founder use cases"])
    f_b = _get_font("title", 32)
    f_sub_b = _get_font("body", 26)
    
    for i, b in enumerate(bullets[:3]):
        by = wy + i * 115
        ir = 22
        icx, icy = MARGIN + 45, by + 24
        draw.ellipse([(icx - ir, icy - ir), (icx + ir, icy + ir)], fill=th["tag_bg"], outline=th["tag_border"], width=2)
        draw.line([(icx - 8, icy), (icx - 2, icy + 6)], fill=th["accent"], width=3)
        draw.line([(icx - 2, icy + 6), (icx + 9, icy - 6)], fill=th["accent"], width=3)
        
        draw.text((MARGIN + 85, by + 2), b, font=f_b, fill=th["text_primary"])
        draw.text((MARGIN + 85, by + 40), f"Key asset #{i+1} tested and verified for 2026 execution.", font=f_sub_b, fill=th["text_secondary"])
        if i < 2:
            draw.line([(MARGIN + 35, by + 95), (W - MARGIN - 35, by + 95)], fill=th["card_border"], width=1)
            
    btn_y = H - 280
    btn_w = W - 2 * MARGIN
    btn_h = 135
    
    b_shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bs_draw = ImageDraw.Draw(b_shadow)
    bs_draw.rounded_rectangle([(MARGIN, btn_y + 8), (MARGIN + btn_w, btn_y + btn_h + 8)], radius=22, fill=(0, 0, 0, 60))
    b_shadow = b_shadow.filter(ImageFilter.GaussianBlur(14))
    base = Image.alpha_composite(base, b_shadow)
    
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([(MARGIN, btn_y), (MARGIN + btn_w, btn_y + btn_h)], radius=22, fill=th["btn_bg"])
    draw.line([(MARGIN + 24, btn_y + 2), (MARGIN + btn_w - 24, btn_y + 2)], fill=(255, 255, 255, 120), width=2)
    
    f_btn_sub = _get_font("title", 22)
    f_btn_main = _get_font("title", 48)
    draw.text((MARGIN + 45, btn_y + 24), "STEP-BY-STEP PLAYBOOK", font=f_btn_sub, fill=th["btn_text"])
    draw.text((MARGIN + 45, btn_y + 54), "SWIPE TO REVEAL  ➔", font=f_btn_main, fill=th["btn_text"])
    
    ar_cx, ar_cy = W - MARGIN - 75, btn_y + btn_h // 2
    draw.ellipse([(ar_cx - 30, ar_cy - 30), (ar_cx + 30, ar_cy + 30)], fill=th["card_border_inner"])
    draw.text((ar_cx - 14, ar_cy - 16), "➔", font=_get_font("title", 32), fill=th["btn_text"])
    
    _draw_footer(draw, th, handle, "SWIPE TO START  ➔")
    return base.convert("RGB")


def _slide_content(th, slide, handle, index, total):
    base = _create_ambient_background(th)
    
    card_w = W - 2 * MARGIN
    card_y = 390
    card_h = 440
    base = _draw_shadowed_card(base, th, MARGIN, card_y, card_w, card_h, radius=24, is_window=True)
    
    take_y = card_y + card_h + 30
    take_h = 240
    base = _draw_shadowed_card(base, th, MARGIN, take_y, card_w, take_h, radius=24, is_window=False)
    
    draw = ImageDraw.Draw(base)
    _draw_top_nav(draw, th, handle, index, total)
    
    tag = slide.get("tag", "STRATEGIC BREAKDOWN")
    f_eye = _get_font("title", 22)
    kw = draw.textlength(tag.upper(), font=f_eye) + 32
    draw.rounded_rectangle([(MARGIN, 165), (MARGIN + kw, 203)], radius=19, fill=th["tag_bg"], outline=th["tag_border"], width=1)
    draw.text((MARGIN + 16, 173), tag.upper(), font=f_eye, fill=th["accent"])
    
    f_head = _get_font("title", 72)
    title_main = slide.get("title_main", "WHAT")
    title_accent = slide.get("title_accent", "HAPPENED")
    title_full = f"{title_main} {title_accent}".strip()
    draw.text((MARGIN, 225), title_full, font=f_head, fill=th["text_primary"])
    
    subtitle = slide.get("subtitle", "Key tactical shifts and strategic requirements.")
    f_sub = _get_font("body", 34)
    draw.text((MARGIN, 315), subtitle, font=f_sub, fill=th["text_secondary"])
    
    bullets = slide.get("bullets", ["Direct verified facts", "Actionable takeaways", "Best founder use cases"])
    wy = card_y + 80
    f_b = _get_font("title", 32)
    f_sub_b = _get_font("body", 26)
    
    for i, b in enumerate(bullets[:3]):
        by = wy + i * 110
        num_str = f"0{i+1}"
        draw.rounded_rectangle([(MARGIN + 35, by + 6), (MARGIN + 85, by + 46)], radius=10, fill=th["tag_bg"], outline=th["tag_border"], width=1)
        draw.text((MARGIN + 46, by + 13), num_str, font=_get_font("title", 20), fill=th["accent"])
        
        draw.text((MARGIN + 105, by + 4), b, font=f_b, fill=th["text_primary"])
        draw.text((MARGIN + 105, by + 42), "Critical decision factor for strategic execution.", font=f_sub_b, fill=th["text_secondary"])
        if i < 2:
            draw.line([(MARGIN + 35, by + 90), (W - MARGIN - 35, by + 90)], fill=th["card_border"], width=1)
            
    draw.rounded_rectangle([(MARGIN + 35, take_y + 30), (MARGIN + 195, take_y + 66)], radius=10, fill=th["tag_bg"], outline=th["tag_border"], width=1)
    draw.text((MARGIN + 48, take_y + 37), "FOUNDER RULE", font=_get_font("title", 20), fill=th["accent"])
    
    takeaway = slide.get("takeaway", "Focus on defensible execution, not narrative momentum.")
    f_take = _get_font("title", 38)
    ty = take_y + 85
    for line in _wrap(draw, takeaway, f_take, card_w - 70):
        draw.text((MARGIN + 35, ty), line, font=f_take, fill=th["text_primary"])
        ty += 48
        
    _draw_footer(draw, th, handle, "SWIPE NEXT  ➔")
    return base.convert("RGB")


def _slide_outro(th, source_name, data, handle, index, total):
    base = _create_ambient_background(th)
    
    card_w = W - 2 * MARGIN
    card_y = 390
    card_h = 420
    base = _draw_shadowed_card(base, th, MARGIN, card_y, card_w, card_h, radius=24, is_window=True)
    
    cta_y = card_y + card_h + 30
    cta_h = 280
    base = _draw_shadowed_card(base, th, MARGIN, cta_y, card_w, cta_h, radius=24, is_window=False)
    
    draw = ImageDraw.Draw(base)
    _draw_top_nav(draw, th, handle, index, total)
    
    f_eye = _get_font("title", 22)
    kicker = "FREE FOUNDER BLUEPRINT"
    kw = draw.textlength(kicker, font=f_eye) + 32
    draw.rounded_rectangle([(MARGIN, 165), (MARGIN + kw, 203)], radius=19, fill=th["tag_bg"], outline=th["tag_border"], width=1)
    draw.text((MARGIN + 16, 173), kicker, font=f_eye, fill=th["accent"])
    
    f_head = _get_font("title", 72)
    cta_keyword = data.get("cta_keyword", "TOOLS").upper()
    title = f"Get The Complete {cta_keyword} Kit."
    for line in _wrap(draw, title, f_head, W - 2 * MARGIN):
        draw.text((MARGIN, 225), line, font=f_head, fill=th["text_primary"])
        
    subtitle = "Save this carousel or comment below for immediate resource delivery."
    f_sub = _get_font("body", 34)
    draw.text((MARGIN, 315), subtitle, font=f_sub, fill=th["text_secondary"])
    
    wy = card_y + 85
    assets = [
        "100% verified zero-setup tool links",
        "Direct copy-paste prompt templates",
        "Founder ROI & execution breakdown"
    ]
    f_b = _get_font("title", 32)
    for i, a in enumerate(assets):
        by = wy + i * 105
        icx, icy = MARGIN + 55, by + 22
        draw.ellipse([(icx - 18, icy - 18), (icx + 18, icy + 18)], fill=th["tag_bg"], outline=th["tag_border"], width=2)
        draw.line([(icx - 6, icy), (icx - 2, icy + 5)], fill=th["accent"], width=3)
        draw.line([(icx - 2, icy + 5), (icx + 7, icy - 5)], fill=th["accent"], width=3)
        
        draw.text((MARGIN + 95, by + 2), a, font=f_b, fill=th["text_primary"])
        draw.text((MARGIN + 95, by + 40), "Included in the raw resource bundle.", font=_get_font("body", 24), fill=th["text_secondary"])
        if i < 2:
            draw.line([(MARGIN + 35, by + 85), (W - MARGIN - 35, by + 85)], fill=th["card_border"], width=1)
            
    draw.rounded_rectangle([(MARGIN + 35, cta_y + 30), (MARGIN + 225, cta_y + 66)], radius=10, fill=th["tag_bg"], outline=th["tag_border"], width=1)
    draw.text((MARGIN + 48, cta_y + 37), "INSTANT ACCESS", font=_get_font("title", 20), fill=th["accent"])
    
    draw.text((MARGIN + 35, cta_y + 85), f'COMMENT "{cta_keyword}" BELOW', font=_get_font("title", 52), fill=th["accent"])
    
    cta_sub = data.get("cta_subtext", "I'll send you the direct resource link & blueprint.")
    draw.text((MARGIN + 35, cta_y + 155), cta_sub, font=_get_font("body", 32), fill=th["text_primary"])
    draw.text((MARGIN + 35, cta_y + 205), "Save & bookmark this post to revisit during execution.", font=_get_font("body", 26), fill=th["text_secondary"])
    
    _draw_footer(draw, th, handle, f"VIA {source_name.upper()[:12]}")
    return base.convert("RGB")


def render(data, source_name, handle, out_dir, theme_idx=None):
    os.makedirs(out_dir, exist_ok=True)
    theme = get_theme(theme_idx)
    print(f"[images] Rendering World-Class Creative with Theme #{theme['id']+1}: {theme['name']} ({theme['day']})")

    slides_content = data.get("slides", [])
    total_slides = 1 + len(slides_content) + 1

    paths = []
    # 1. Cover Slide
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

    print(f"[images] Rendered {len(paths)} world-class slides in {out_dir}")
    return paths
