"""High-converting Neo-Brutalist Creator Carousel Generator (1080x1350, 4:5).
Features:
- Two-tone ultra-bold display typography
- Clean 3-bullet checklist layout with custom vector checkmark badges
- Digital tablet & checklist mockup graphics
- Neo-brutalist interactive CTA button ("COMMENT [KEYWORD]") with hard drop shadows
- 6 vibrant creator color themes rotating across the 7 days of the week
"""
import datetime
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 75

THEMES = [
    # 0. Monday: Lavender Creator (Exact match to target screenshot)
    {
        "id": 0,
        "name": "Lavender Creator",
        "day": "Monday",
        "bg": (196, 181, 253),         # #C4B5FD Pastel Lavender
        "card_bg": (255, 255, 255),
        "text_primary": (15, 23, 42),  # #0F172A Deep Slate / Black
        "text_accent": (37, 99, 235),  # #2563EB Electric Royal Blue
        "btn_bg": (56, 189, 248),      # #38BDF8 Bright Cyan
        "btn_text": (15, 23, 42),      # Deep Black
        "badge_bg": (37, 99, 235),     # Checkmark circle color
        "badge_check": (255, 255, 255),# White checkmark
        "border": (15, 23, 42),        # Solid black outline
        "sub": (71, 85, 105),          # Subtitle color
        "pill_bg": (224, 231, 255),    # Soft indigo pill
        "is_dark": False,
    },
    # 1. Tuesday: Ice Blue Neo-Brutalist
    {
        "id": 1,
        "name": "Ice Blue Neo",
        "day": "Tuesday",
        "bg": (186, 230, 253),         # #BAE6FD Sky Ice Blue
        "card_bg": (255, 255, 255),
        "text_primary": (15, 23, 42),
        "text_accent": (2, 132, 199),  # #0284C7 Deep Cobalt Blue
        "btn_bg": (250, 204, 21),      # #FACC15 Electric Yellow
        "btn_text": (15, 23, 42),
        "badge_bg": (2, 132, 199),
        "badge_check": (255, 255, 255),
        "border": (15, 23, 42),
        "sub": (71, 85, 105),
        "pill_bg": (224, 242, 254),
        "is_dark": False,
    },
    # 2. Wednesday: Neo Mint & Emerald
    {
        "id": 2,
        "name": "Neo Mint",
        "day": "Wednesday",
        "bg": (167, 243, 208),         # #A7F3D0 Pastel Mint
        "card_bg": (255, 255, 255),
        "text_primary": (6, 78, 59),   # Deep Forest
        "text_accent": (5, 150, 105),  # #059669 Vibrant Emerald
        "btn_bg": (103, 232, 249),     # #67E8F9 Electric Cyan
        "btn_text": (6, 78, 59),
        "badge_bg": (5, 150, 105),
        "badge_check": (255, 255, 255),
        "border": (6, 78, 59),
        "sub": (55, 65, 81),
        "pill_bg": (209, 250, 229),
        "is_dark": False,
    },
    # 3. Thursday: Warm Butter / Pop Yellow
    {
        "id": 3,
        "name": "Butter Pop",
        "day": "Thursday",
        "bg": (254, 240, 138),         # #FEF08A Butter Yellow
        "card_bg": (255, 255, 255),
        "text_primary": (24, 24, 27),
        "text_accent": (37, 99, 235),  # Royal Blue contrast
        "btn_bg": (56, 189, 248),      # Cyan
        "btn_text": (24, 24, 27),
        "badge_bg": (37, 99, 235),
        "badge_check": (255, 255, 255),
        "border": (24, 24, 27),
        "sub": (82, 82, 91),
        "pill_bg": (254, 249, 195),
        "is_dark": False,
    },
    # 4. Friday: Sunset Peach & Coral
    {
        "id": 4,
        "name": "Sunset Peach",
        "day": "Friday",
        "bg": (254, 215, 170),         # #FED7AA Pastel Peach
        "card_bg": (255, 255, 255),
        "text_primary": (28, 25, 23),  # Deep Espresso Black
        "text_accent": (234, 88, 12),  # Sunset Orange
        "btn_bg": (129, 140, 248),     # Electric Periwinkle
        "btn_text": (255, 255, 255),
        "badge_bg": (234, 88, 12),
        "badge_check": (255, 255, 255),
        "border": (28, 25, 23),
        "sub": (68, 64, 60),
        "pill_bg": (255, 237, 213),
        "is_dark": False,
    },
    # 5. Weekend: Cyber Midnight (High-End Dark Mode)
    {
        "id": 5,
        "name": "Cyber Midnight",
        "day": "Weekend",
        "bg": (11, 15, 25),            # Deep Midnight Obsidian
        "card_bg": (24, 33, 53),
        "text_primary": (248, 250, 252),# Crisp Pure White
        "text_accent": (56, 189, 248), # Glowing Cyan
        "btn_bg": (250, 204, 21),      # High-voltage Yellow
        "btn_text": (15, 23, 42),
        "badge_bg": (56, 189, 248),
        "badge_check": (11, 15, 25),
        "border": (56, 189, 248),
        "sub": (203, 213, 225),
        "pill_bg": (30, 41, 59),
        "is_dark": True,
    },
]

FONT_PATHS = {
    "impact": [
        "fonts/Impact.ttf",
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/ariblk.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "inter": [
        "fonts/Inter.ttf",
        os.getenv("FONT_PATH"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ],
}


def _font(kind, size):
    for p in FONT_PATHS.get(kind, FONT_PATHS["inter"]):
        if p and os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def get_theme(theme_idx=None):
    if theme_idx is not None and 0 <= theme_idx < len(THEMES):
        return THEMES[theme_idx]
    weekday = datetime.datetime.now().weekday()  # 0=Monday .. 6=Sunday
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


def _draw_top_header(draw, th, handle, index, total):
    f_meta = _font("inter", 30)
    # Handle top left
    draw.text((MARGIN, 65), handle, font=f_meta, fill=th["text_primary"])

    # Slide count pill top right (e.g. • 1/5)
    pill_w, pill_h = 135, 46
    px, py = W - MARGIN - pill_w, 58
    draw.rounded_rectangle([(px, py), (px + pill_w, py + pill_h)], radius=23, fill=th["pill_bg"], outline=th["border"], width=2)
    # Recording/live indicator dot
    draw.ellipse([(px + 16, py + 16), (px + 28, py + 28)], fill=(249, 115, 22))
    draw.text((px + 38, py + 8), f"{index}/{total}", font=f_meta, fill=th["text_primary"])


def _draw_footer(draw, th, handle, right_label="SWIPE  ➔"):
    fy = H - 85
    f_meta = _font("inter", 30)
    draw.line([(MARGIN, fy), (W - MARGIN, fy)], fill=th["border"], width=2)
    draw.text((MARGIN, fy + 22), handle, font=f_meta, fill=th["text_primary"])
    rw = draw.textlength(right_label, font=f_meta)
    draw.text((W - MARGIN - rw, fy + 22), right_label, font=f_meta, fill=th["text_primary"])


def _draw_checklist_bullets(draw, th, bullets, start_y, max_w=460):
    f_bullet = _font("inter", 35)
    by = start_y
    for b in bullets[:3]:
        r = 23
        cx, cy = MARGIN + r, by + r
        # Circle badge
        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=th["badge_bg"])
        # White checkmark inside
        draw.line([(cx - 9, cy), (cx - 3, cy + 7)], fill=th["badge_check"], width=4)
        draw.line([(cx - 3, cy + 7), (cx + 9, cy - 7)], fill=th["badge_check"], width=4)

        # Multi-line bullet text if needed
        wrapped = _wrap(draw, b, f_bullet, max_w)
        ly = by + 2
        for line in wrapped[:2]:
            draw.text((MARGIN + 62, ly), line, font=f_bullet, fill=th["text_primary"])
            ly += 42
        by += max(74, len(wrapped) * 44 + 20)
    return by


def _draw_tablet_mockup(draw, th, tx, ty, tw=370, th_box=460, header_text="FREE TOOLS"):
    # Hard offset drop shadow (+8px, +8px)
    shadow_fill = (0, 0, 0, 160) if not th["is_dark"] else (0, 0, 0, 240)
    draw.rounded_rectangle([(tx + 8, ty + 8), (tx + tw + 8, ty + th_box + 8)], radius=20, fill=shadow_fill)
    # Tablet body
    draw.rounded_rectangle([(tx, ty), (tx + tw, ty + th_box)], radius=20, fill=th["card_bg"], outline=th["border"], width=4)

    # Tablet header
    f_tbl_head = _font("impact", 36)
    draw.text((tx + 24, ty + 24), header_text, font=f_tbl_head, fill=th["text_primary"])

    # Rows inside tablet
    ry = ty + 80
    for i in range(5):
        # App icon badge
        draw.rounded_rectangle([(tx + 24, ry), (tx + 64, ry + 40)], radius=8, fill=th["border"] if not th["is_dark"] else (30, 41, 59))
        # Content bar
        draw.rounded_rectangle([(tx + 78, ry + 12), (tx + tw - 75, ry + 28)], radius=6, fill=(226, 232, 240) if not th["is_dark"] else (51, 65, 85))
        # Blue checkmark box
        draw.rounded_rectangle([(tx + tw - 62, ry), (tx + tw - 24, ry + 40)], radius=8, fill=th["badge_bg"])
        draw.line([(tx + tw - 53, ry + 20), (tx + tw - 47, ry + 27)], fill=th["badge_check"], width=3)
        draw.line([(tx + tw - 47, ry + 27), (tx + tw - 35, ry + 13)], fill=th["badge_check"], width=3)
        ry += 64


def _draw_neo_button(draw, th, btn_x, btn_y, btn_w, btn_h, label_small, label_big):
    # Hard drop shadow (+8px, +8px)
    shadow_fill = (15, 23, 42) if not th["is_dark"] else (0, 0, 0)
    draw.rounded_rectangle([(btn_x + 8, btn_y + 8), (btn_x + btn_w + 8, btn_y + btn_h + 8)], radius=24, fill=shadow_fill)
    # Button body
    draw.rounded_rectangle([(btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h)], radius=24, fill=th["btn_bg"], outline=th["border"], width=4)

    # Text inside button
    f_small = _font("impact", 30)
    f_big = _font("impact", 68)
    draw.text((btn_x + 48, btn_y + 22), label_small, font=f_small, fill=th["btn_text"])
    draw.text((btn_x + 48, btn_y + 58), label_big, font=f_big, fill=th["btn_text"])

    # Speech bubble icon
    bx = btn_x + btn_w - 135
    by = btn_y + 40
    draw.rounded_rectangle([(bx, by), (bx + 80, by + 60)], radius=14, outline=th["btn_text"], width=4)
    draw.polygon([(bx + 20, by + 60), (bx + 10, by + 78), (bx + 35, by + 60)], fill=th["btn_bg"])
    draw.line([(bx + 20, by + 60), (bx + 10, by + 78)], fill=th["btn_text"], width=4)
    draw.line([(bx + 10, by + 78), (bx + 35, by + 60)], fill=th["btn_text"], width=4)
    for dx in [20, 40, 60]:
        draw.ellipse([(bx + dx - 4, by + 30 - 4), (bx + dx + 4, by + 30 + 4)], fill=th["btn_text"])


def _slide_cover(th, data, handle, index, total):
    img = Image.new("RGB", (W, H), th["bg"])
    draw = ImageDraw.Draw(img)
    _draw_top_header(draw, th, handle, index, total)

    f_head = _font("impact", 94)
    f_sub = _font("inter", 38)

    title_main = data.get("cover_title_main", "THE 7 FREE")
    title_accent = data.get("cover_title_accent", "AI TOOLS")
    subtitle = data.get("cover_subtitle", "All verified for 2026 founder workflows.")
    bullets = data.get("cover_bullets", ["Direct prompt links", "Zero setup steps", "Best founder use cases"])

    # 1. Two-tone Headline
    y = 150
    draw.text((MARGIN, y), title_main + " ", font=f_head, fill=th["text_primary"])
    t1_w = draw.textlength(title_main + " ", font=f_head)
    if MARGIN + t1_w + draw.textlength(title_accent, font=f_head) <= W - MARGIN:
        draw.text((MARGIN + t1_w, y), title_accent, font=f_head, fill=th["text_accent"])
        y += 115
    else:
        y += 105
        draw.text((MARGIN, y), title_accent, font=f_head, fill=th["text_accent"])
        y += 115

    # 2. Subtitle
    draw.text((MARGIN, y), subtitle, font=f_sub, fill=th["sub"])
    y += 85

    # 3. Left column bullets
    _draw_checklist_bullets(draw, th, bullets, y + 25, max_w=460)

    # 4. Right column tablet mockup
    tx, ty = W - MARGIN - 380, y - 5
    _draw_tablet_mockup(draw, th, tx, ty, tw=370, th_box=460, header_text="FREE TOOLS")

    # 5. Neo-brutalist Teaser Button
    btn_x = MARGIN
    btn_y = H - 380
    btn_w = W - 2 * MARGIN
    btn_h = 160
    cta_keyword = data.get("cta_keyword", "TOOLS")
    _draw_neo_button(draw, th, btn_x, btn_y, btn_w, btn_h, "SWIPE TO REVEAL", cta_keyword)

    # 6. Sub-CTA
    draw.text((MARGIN, btn_y + btn_h + 30), "SWIPE FOR THE COMPLETE STEP-BY-STEP BREAKDOWN.", font=_font("impact", 32), fill=th["text_primary"])

    # 7. Footer
    _draw_footer(draw, th, handle, "SWIPE  ➔")
    return img


def _slide_content(th, slide, handle, index, total):
    img = Image.new("RGB", (W, H), th["bg"])
    draw = ImageDraw.Draw(img)
    _draw_top_header(draw, th, handle, index, total)

    # Category Pill
    tag = slide.get("tag", "BREAKDOWN").upper()
    f_tag = _font("impact", 24)
    tag_w = draw.textlength(tag, font=f_tag) + 36
    draw.rounded_rectangle([(MARGIN, 140), (MARGIN + tag_w, 184)], radius=12, fill=th["pill_bg"], outline=th["border"], width=2)
    draw.text((MARGIN + 18, 148), tag, font=f_tag, fill=th["text_accent"])

    # Two-tone Title
    f_head = _font("impact", 84)
    title_main = slide.get("title_main", "WHAT")
    title_accent = slide.get("title_accent", "HAPPENED")
    y = 210
    draw.text((MARGIN, y), title_main + " ", font=f_head, fill=th["text_primary"])
    t1_w = draw.textlength(title_main + " ", font=f_head)
    if MARGIN + t1_w + draw.textlength(title_accent, font=f_head) <= W - MARGIN:
        draw.text((MARGIN + t1_w, y), title_accent, font=f_head, fill=th["text_accent"])
        y += 105
    else:
        y += 95
        draw.text((MARGIN, y), title_accent, font=f_head, fill=th["text_accent"])
        y += 105

    # Subtitle
    subtitle = slide.get("subtitle", "Key facts and strategic shifts for founders.")
    f_sub = _font("inter", 36)
    draw.text((MARGIN, y), subtitle, font=f_sub, fill=th["sub"])
    y += 75

    # Bullets on left
    bullets = slide.get("bullets", ["Direct verified facts", "Actionable takeaways", "Best founder use cases"])
    _draw_checklist_bullets(draw, th, bullets, y + 25, max_w=460)

    # Right column: Data / Insights Card Mockup
    tx, ty = W - MARGIN - 380, y - 5
    _draw_tablet_mockup(draw, th, tx, ty, tw=370, th_box=460, header_text="KEY SHIFTS")

    # Bottom Takeaway Box (Neo-brutalist card)
    takeaway = slide.get("takeaway", "Focus on defensible execution, not narrative momentum.")
    box_x = MARGIN
    box_y = H - 350
    box_w = W - 2 * MARGIN
    box_h = 160

    # Hard drop shadow
    draw.rounded_rectangle([(box_x + 8, box_y + 8), (box_x + box_w + 8, box_y + box_h + 8)], radius=20, fill=(0, 0, 0, 160) if not th["is_dark"] else (0, 0, 0))
    # Box body
    draw.rounded_rectangle([(box_x, box_y), (box_x + box_w, box_y + box_h)], radius=20, fill=th["card_bg"], outline=th["border"], width=3)

    # Label pill inside box
    draw.rounded_rectangle([(box_x + 25, box_y + 20), (box_x + 165, box_y + 54)], radius=8, fill=th["badge_bg"])
    draw.text((box_x + 36, box_y + 24), "FOUNDER RULE", font=_font("impact", 22), fill=th["badge_check"])

    f_take = _font("inter", 34)
    lines = _wrap(draw, takeaway, f_take, box_w - 50)
    ty = box_y + 68
    for line in lines[:2]:
        draw.text((box_x + 25, ty), line, font=f_take, fill=th["text_primary"])
        ty += 42

    # Footer
    _draw_footer(draw, th, handle, "SWIPE  ➔")
    return img


def _slide_outro(th, source_name, data, handle, index, total):
    img = Image.new("RGB", (W, H), th["bg"])
    draw = ImageDraw.Draw(img)
    _draw_top_header(draw, th, handle, index, total)

    f_head = _font("impact", 96)
    f_sub = _font("inter", 40)

    # 1. Two-tone Title (Exact target image style: "GET THE FREE TOOLKIT")
    cta_keyword = data.get("cta_keyword", "TOOLS").upper()
    title_main = "GET THE "
    title_accent = f"FREE {cta_keyword}"

    y = 150
    draw.text((MARGIN, y), title_main, font=f_head, fill=th["text_primary"])
    t1_w = draw.textlength(title_main, font=f_head)
    draw.text((MARGIN + t1_w, y), "FREE", font=f_head, fill=th["text_accent"])
    y += 105
    draw.text((MARGIN, y), f"{cta_keyword} GUIDE", font=f_head, fill=th["text_primary"])
    y += 120

    # 2. Subtitle
    draw.text((MARGIN, y), f"The complete breakdown + founder blueprint.", font=f_sub, fill=th["text_primary"])
    y += 85

    # 3. Bullets on left
    bullets = [
        "Direct verified prompts",
        "Zero-cost setup steps",
        "Real-world founder ROI"
    ]
    _draw_checklist_bullets(draw, th, bullets, y + 25, max_w=460)

    # 4. Right column tablet mockup
    tx, ty = W - MARGIN - 380, y - 5
    _draw_tablet_mockup(draw, th, tx, ty, tw=370, th_box=460, header_text="RESOURCES")

    # 5. Neo-brutalist CTA Button (COMMENT [KEYWORD])
    btn_x = MARGIN
    btn_y = H - 380
    btn_w = W - 2 * MARGIN
    btn_h = 160
    _draw_neo_button(draw, th, btn_x, btn_y, btn_w, btn_h, "COMMENT", cta_keyword)

    # 6. Sub-CTA text
    cta_sub = data.get("cta_subtext", "I'LL SEND YOU THE COMPLETE GUIDE.")
    draw.text((MARGIN, btn_y + btn_h + 30), cta_sub, font=_font("impact", 34), fill=th["text_primary"])

    # 7. Bottom footer
    _draw_footer(draw, th, handle, f"VIA {source_name.upper()[:12]}")
    return img


def render(data, source_name, handle, out_dir, theme_idx=None):
    os.makedirs(out_dir, exist_ok=True)
    # Select from the 6 daily creator themes
    theme = get_theme(theme_idx)
    print(f"[images] Rendering carousel with Theme #{theme['id']+1}: {theme['name']} ({theme['day']})")

    slides_content = data.get("slides", [])
    total_slides = 1 + len(slides_content) + 1  # Cover + content slides + Outro CTA

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

    print(f"[images] Rendered {len(paths)} slides in {out_dir}")
    return paths
