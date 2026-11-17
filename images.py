"""Minimalist Editorial / Notion Post UI Design (1080x1350, 4:5).

Features:
- Elegant warm paper & editorial palettes (Cream, Sand, Sage, Navy, Blush, and Dark Notion)
- Top segmented progress tracker (active slide indicator)
- Refined editorial serif headlines (Georgia Bold) and crisp body typography (Inter)
- Notion-style callout boxes with colored left accent bars
- Delicate rounded vector checklist markers for bullet points
- Bottom Founder Takeaway cards on every content slide
- Minimalist, high-converting interactive comment CTA box
"""
import datetime
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 85

THEMES = [
    # 0. Monday: Classic Notion Cream & Slate
    {
        "id": 0,
        "name": "Classic Cream & Slate",
        "day": "Monday",
        "bg": (250, 248, 245),          # #FAF8F5 Warm Cream Paper
        "card_bg": (255, 255, 255),     # #FFFFFF Pure Paper
        "callout_bg": (243, 239, 233),  # #F3EFE9 Subtle Tint
        "border": (226, 221, 212),      # #E2DDD4 Hairline stroke
        "border_light": (238, 235, 229),# #EEEBE5 Very subtle
        "text_primary": (24, 24, 27),   # #18181B Deep Charcoal Ink
        "text_secondary": (113, 113, 122),# #71717A Muted Slate
        "accent": (37, 99, 235),        # #2563EB Editorial Royal Blue
        "tag_bg": (236, 232, 225),      # #ECE8E1
        "tag_text": (39, 39, 42),
        "check_box": (255, 255, 255),
        "check_mark": (37, 99, 235),
        "btn_bg": (24, 24, 27),         # Minimalist Black Button
        "btn_text": (255, 255, 255),
        "is_dark": False,
    },
    # 1. Tuesday: Warm Sand & Espresso
    {
        "id": 1,
        "name": "Warm Sand & Espresso",
        "day": "Tuesday",
        "bg": (246, 243, 237),          # #F6F3ED
        "card_bg": (255, 255, 255),
        "callout_bg": (237, 232, 222),
        "border": (222, 216, 206),
        "border_light": (235, 230, 221),
        "text_primary": (39, 34, 31),   # #27221F
        "text_secondary": (120, 113, 108),
        "accent": (194, 65, 12),        # #C2410C Warm Terracotta
        "tag_bg": (234, 228, 217),
        "tag_text": (41, 37, 34),
        "check_box": (255, 255, 255),
        "check_mark": (194, 65, 12),
        "btn_bg": (39, 34, 31),
        "btn_text": (255, 255, 255),
        "is_dark": False,
    },
    # 2. Wednesday: Sage Botanical & Forest
    {
        "id": 2,
        "name": "Sage Botanical",
        "day": "Wednesday",
        "bg": (242, 245, 243),          # #F2F5F3
        "card_bg": (255, 255, 255),
        "callout_bg": (230, 236, 232),
        "border": (216, 226, 220),
        "border_light": (231, 238, 234),
        "text_primary": (20, 40, 29),   # #14281D
        "text_secondary": (82, 106, 94),
        "accent": (5, 150, 105),        # #059669 Muted Emerald
        "tag_bg": (222, 231, 225),
        "tag_text": (22, 43, 31),
        "check_box": (255, 255, 255),
        "check_mark": (5, 150, 105),
        "btn_bg": (20, 40, 29),
        "btn_text": (255, 255, 255),
        "is_dark": False,
    },
    # 3. Thursday: Warm Butter & Navy
    {
        "id": 3,
        "name": "Warm Butter & Navy",
        "day": "Thursday",
        "bg": (250, 247, 238),          # #FAF7EE
        "card_bg": (255, 255, 255),
        "callout_bg": (243, 238, 222),
        "border": (232, 224, 204),
        "border_light": (242, 236, 220),
        "text_primary": (15, 23, 42),   # #0F172A
        "text_secondary": (100, 116, 139),
        "accent": (217, 119, 6),        # #D97706 Warm Amber
        "tag_bg": (236, 229, 211),
        "tag_text": (24, 24, 27),
        "check_box": (255, 255, 255),
        "check_mark": (217, 119, 6),
        "btn_bg": (15, 23, 42),
        "btn_text": (255, 255, 255),
        "is_dark": False,
    },
    # 4. Friday: Soft Blush & Burgundy
    {
        "id": 4,
        "name": "Soft Blush & Burgundy",
        "day": "Friday",
        "bg": (250, 245, 243),          # #FAF5F3
        "card_bg": (255, 255, 255),
        "callout_bg": (242, 232, 230),
        "border": (231, 219, 216),
        "border_light": (241, 232, 230),
        "text_primary": (59, 29, 40),   # #3B1D28
        "text_secondary": (124, 93, 105),
        "accent": (190, 18, 60),        # #BE123C Editorial Rose
        "tag_bg": (235, 220, 217),
        "tag_text": (59, 29, 40),
        "check_box": (255, 255, 255),
        "check_mark": (190, 18, 60),
        "btn_bg": (59, 29, 40),
        "btn_text": (255, 255, 255),
        "is_dark": False,
    },
    # 5. Weekend: Notion Dark Mode Charcoal
    {
        "id": 5,
        "name": "Notion Dark Mode",
        "day": "Weekend",
        "bg": (24, 24, 27),             # #18181B Dark Paper
        "card_bg": (35, 35, 38),        # #232326
        "callout_bg": (39, 39, 42),     # #27272A
        "border": (55, 55, 60),         # #37373C
        "border_light": (45, 45, 48),
        "text_primary": (244, 244, 245),# #F4F4F5 Crisp Pure White
        "text_secondary": (161, 161, 170),# #A1A1AA Muted Gray
        "accent": (56, 189, 248),       # #38BDF8 Soft Sky Blue
        "tag_bg": (42, 42, 46),
        "tag_text": (228, 228, 231),
        "check_box": (35, 35, 38),
        "check_mark": (56, 189, 248),
        "btn_bg": (244, 244, 245),
        "btn_text": (24, 24, 27),
        "is_dark": True,
    },
]

FONT_CACHE = {}


def _get_font(family, size):
    key = (family, size)
    if key in FONT_CACHE:
        return FONT_CACHE[key]
    paths = {
        "serif_bold": ["fonts/georgiab.ttf", "C:/Windows/Fonts/georgiab.ttf"],
        "serif_reg": ["fonts/georgia.ttf", "C:/Windows/Fonts/georgia.ttf"],
        "sans": ["fonts/Inter.ttf", "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"],
        "sans_bold": ["fonts/Inter.ttf", "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"],
    }
    for p in paths.get(family, paths["sans"]):
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
    # 1. Segmented Progress Bar at the top
    bar_y = 52
    seg_spacing = 8
    total_w = W - 2 * MARGIN
    seg_w = (total_w - (total - 1) * seg_spacing) / total
    for i in range(total):
        sx = MARGIN + i * (seg_w + seg_spacing)
        fill_color = th["accent"] if i == (index - 1) else (th["text_primary"] if i < (index - 1) else th["border"])
        draw.rounded_rectangle([(sx, bar_y), (sx + seg_w, bar_y + 4)], radius=2, fill=fill_color)

    # 2. Header Metadata Line
    f_handle = _get_font("sans", 25)
    f_meta = _get_font("sans", 24)
    hy = 80
    draw.text((MARGIN, hy), handle, font=f_handle, fill=th["text_primary"])

    meta_str = f"ISSUE // {index:02d} OF {total:02d}"
    mw = draw.textlength(meta_str, font=f_meta)
    draw.text((W - MARGIN - mw, hy), meta_str, font=f_meta, fill=th["text_secondary"])

    # Hairline divider
    draw.line([(MARGIN, hy + 42), (W - MARGIN, hy + 42)], fill=th["border"], width=1)


def _draw_footer(draw, th, handle, right_action="SWIPE ➔"):
    fy = H - 95
    f_foot = _get_font("sans", 24)
    draw.line([(MARGIN, fy), (W - MARGIN, fy)], fill=th["border"], width=1)
    draw.text((MARGIN, fy + 24), handle, font=f_foot, fill=th["text_secondary"])
    rw = draw.textlength(right_action, font=f_foot)
    draw.text((W - MARGIN - rw, fy + 24), right_action, font=f_foot, fill=th["accent"])


def _draw_tag(draw, th, text, x, y):
    """Draws a clean, refined Notion category badge."""
    f_tag = _get_font("sans", 22)
    tag_clean = text.upper()
    tw = draw.textlength(tag_clean, font=f_tag)
    px, py = 16, 7
    draw.rounded_rectangle([(x, y), (x + tw + px * 2, y + 26 + py * 2)], radius=8, fill=th["tag_bg"], outline=th["border"], width=1)
    draw.text((x + px, y + py), tag_clean, font=f_tag, fill=th["tag_text"])
    return y + 26 + py * 2


def _draw_checklist(draw, th, items, x, y, max_w):
    """Draws Notion-style checklist rows with delicate vector checkboxes."""
    f_item = _get_font("sans", 32)
    cur_y = y
    box_size = 28
    for item in items[:3]:
        # Notion Checkbox
        draw.rounded_rectangle([(x, cur_y + 4), (x + box_size, cur_y + 4 + box_size)], radius=6, fill=th["check_box"], outline=th["border"], width=2)
        # Vector checkmark inside
        cx, cy = x + 6, cur_y + 16
        draw.line([(cx, cy + 2), (cx + 5, cy + 7)], fill=th["check_mark"], width=3)
        draw.line([(cx + 5, cy + 7), (cx + 14, cy - 4)], fill=th["check_mark"], width=3)

        # Item text
        text_x = x + box_size + 24
        wrapped = _wrap(draw, item, f_item, max_w - (box_size + 24))
        for line in wrapped:
            draw.text((text_x, cur_y), line, font=f_item, fill=th["text_primary"])
            cur_y += 42
        cur_y += 24
    return cur_y


def _draw_callout_box(draw, th, x, y, w, title_tag, body_text):
    """Renders a sleek Notion callout box with a vertical colored accent bar."""
    f_title = _get_font("sans", 22)
    f_body = _get_font("sans", 32)
    lines = _wrap(draw, body_text, f_body, w - 80)
    box_h = 44 + len(lines) * 44 + 36

    draw.rounded_rectangle([(x, y), (x + w, y + box_h)], radius=14, fill=th["callout_bg"], outline=th["border"], width=1)
    draw.rounded_rectangle([(x + 14, y + 20), (x + 19, y + box_h - 20)], radius=3, fill=th["accent"])
    draw.text((x + 40, y + 22), title_tag.upper(), font=f_title, fill=th["accent"])

    ly = y + 60
    for line in lines:
        draw.text((x + 40, ly), line, font=f_body, fill=th["text_primary"])
        ly += 44

    return y + box_h


def _slide_cover(th, data, handle, index, total):
    img = Image.new("RGB", (W, H), th["bg"])
    draw = ImageDraw.Draw(img)
    _draw_top_nav(draw, th, handle, index, total)

    y = 175
    y = _draw_tag(draw, th, "FOUNDER PLAYBOOK // 2026", MARGIN, y) + 36

    # Headline (Serif Bold)
    f_head = _get_font("serif_bold", 78)
    title_main = data.get("cover_title_main", "THE 7 FREE")
    title_accent = data.get("cover_title_accent", "AI TOOLS")

    full_headline = f"{title_main} {title_accent}".strip()
    headline_lines = _wrap(draw, full_headline, f_head, W - 2 * MARGIN)
    for line in headline_lines:
        draw.text((MARGIN, y), line, font=f_head, fill=th["text_primary"])
        y += 94

    # Subtitle
    y += 12
    subtitle = data.get("cover_subtitle", "Verified tactical workflows for founders and operators.")
    f_sub = _get_font("sans", 34)
    for line in _wrap(draw, subtitle, f_sub, W - 2 * MARGIN):
        draw.text((MARGIN, y), line, font=f_sub, fill=th["text_secondary"])
        y += 48

    y += 45
    # Notion Agenda / Checklist Card
    bullets = data.get("cover_bullets", ["Direct prompt links included", "Zero setup steps required", "High-leverage founder use cases"])
    card_w = W - 2 * MARGIN
    card_h = 320
    draw.rounded_rectangle([(MARGIN, y), (MARGIN + card_w, y + card_h)], radius=16, fill=th["card_bg"], outline=th["border"], width=1)
    draw.rounded_rectangle([(MARGIN + 16, y + 24), (MARGIN + 21, y + card_h - 24)], radius=3, fill=th["accent"])
    draw.text((MARGIN + 45, y + 24), "WHAT IS INSIDE THIS GUIDE", font=_get_font("sans", 22), fill=th["accent"])
    _draw_checklist(draw, th, bullets, MARGIN + 45, y + 68, card_w - 70)

    # Minimalist Bottom Pill Button
    btn_y = H - 235
    btn_w = W - 2 * MARGIN
    btn_h = 90
    draw.rounded_rectangle([(MARGIN, btn_y), (MARGIN + btn_w, btn_y + btn_h)], radius=14, fill=th["btn_bg"])
    
    f_btn = _get_font("sans", 28)
    btn_label = "READ PLAYBOOK  ➔"
    bl_w = draw.textlength(btn_label, font=f_btn)
    draw.text((MARGIN + (btn_w - bl_w) / 2, btn_y + 30), btn_label, font=f_btn, fill=th["btn_text"])

    _draw_footer(draw, th, handle, "SWIPE ➔")
    return img


def _slide_content(th, slide, handle, index, total):
    img = Image.new("RGB", (W, H), th["bg"])
    draw = ImageDraw.Draw(img)
    _draw_top_nav(draw, th, handle, index, total)

    y = 175
    tag = slide.get("tag", "STRATEGIC BREAKDOWN")
    y = _draw_tag(draw, th, tag, MARGIN, y) + 36

    # Slide Title (Serif Bold)
    f_head = _get_font("serif_bold", 74)
    title_main = slide.get("title_main", "WHAT")
    title_accent = slide.get("title_accent", "HAPPENED")
    title_full = f"{title_main} {title_accent}".strip()
    for line in _wrap(draw, title_full, f_head, W - 2 * MARGIN):
        draw.text((MARGIN, y), line, font=f_head, fill=th["text_primary"])
        y += 90

    # Subtitle
    y += 12
    subtitle = slide.get("subtitle", "Strategic context and key tactical developments.")
    f_sub = _get_font("sans", 34)
    for line in _wrap(draw, subtitle, f_sub, W - 2 * MARGIN):
        draw.text((MARGIN, y), line, font=f_sub, fill=th["text_secondary"])
        y += 48

    y += 40
    # 3 Notion Bullets inside Card
    bullets = slide.get("bullets", ["Direct verified facts", "Actionable takeaways", "Best founder use cases"])
    card_w = W - 2 * MARGIN
    bullets_card_h = 280
    draw.rounded_rectangle([(MARGIN, y), (MARGIN + card_w, y + bullets_card_h)], radius=16, fill=th["card_bg"], outline=th["border"], width=1)
    _draw_checklist(draw, th, bullets, MARGIN + 36, y + 36, card_w - 60)
    y += bullets_card_h + 35

    # Bottom Takeaway Callout Box
    takeaway = slide.get("takeaway", "Focus on defensible execution, not narrative momentum.")
    _draw_callout_box(draw, th, MARGIN, y, card_w, "CORE TAKEAWAY", takeaway)

    _draw_footer(draw, th, handle, "SWIPE ➔")
    return img


def _slide_outro(th, source_name, data, handle, index, total):
    img = Image.new("RGB", (W, H), th["bg"])
    draw = ImageDraw.Draw(img)
    _draw_top_nav(draw, th, handle, index, total)

    y = 175
    y = _draw_tag(draw, th, "SUMMARY & NEXT STEPS", MARGIN, y) + 36

    f_head = _get_font("serif_bold", 74)
    cta_keyword = data.get("cta_keyword", "TOOLS").upper()
    title = f"Get The Free {cta_keyword} Guide."
    for line in _wrap(draw, title, f_head, W - 2 * MARGIN):
        draw.text((MARGIN, y), line, font=f_head, fill=th["text_primary"])
        y += 90

    y += 12
    subtitle = "Save this playbook for reference or request the raw toolkit below."
    f_sub = _get_font("sans", 34)
    for line in _wrap(draw, subtitle, f_sub, W - 2 * MARGIN):
        draw.text((MARGIN, y), line, font=f_sub, fill=th["text_secondary"])
        y += 48

    y += 40
    card_w = W - 2 * MARGIN
    bullets = [
        "Complete step-by-step workflow prompts",
        "Direct verified zero-setup tool links",
        "Ready-to-use founder execution templates"
    ]
    card_h = 280
    draw.rounded_rectangle([(MARGIN, y), (MARGIN + card_w, y + card_h)], radius=16, fill=th["card_bg"], outline=th["border"], width=1)
    _draw_checklist(draw, th, bullets, MARGIN + 36, y + 36, card_w - 60)
    y += card_h + 35

    # Minimalist Interactive Comment Box
    comment_box_h = 160
    draw.rounded_rectangle([(MARGIN, y), (MARGIN + card_w, y + comment_box_h)], radius=16, fill=th["callout_bg"], outline=th["border"], width=1)
    draw.rounded_rectangle([(MARGIN + 16, y + 24), (MARGIN + 21, y + comment_box_h - 24)], radius=3, fill=th["accent"])
    draw.text((MARGIN + 45, y + 28), "HOW TO GET THE COMPLETE KIT", font=_get_font("sans", 22), fill=th["accent"])
    
    cta_line = f'Comment "{cta_keyword}" on this post.'
    draw.text((MARGIN + 45, y + 62), cta_line, font=_get_font("sans_bold", 38), fill=th["text_primary"])
    
    cta_sub = data.get("cta_subtext", "I will send you the complete guide and links.")
    draw.text((MARGIN + 45, y + 112), cta_sub, font=_get_font("sans", 28), fill=th["text_secondary"])

    _draw_footer(draw, th, handle, f"VIA {source_name.upper()[:12]}")
    return img


def render(data, source_name, handle, out_dir, theme_idx=None):
    os.makedirs(out_dir, exist_ok=True)
    theme = get_theme(theme_idx)
    print(f"[images] Rendering Notion Editorial carousel with Theme #{theme['id']+1}: {theme['name']} ({theme['day']})")

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

    print(f"[images] Rendered {len(paths)} editorial slides in {out_dir}")
    return paths
