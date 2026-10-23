"""Generates high-retention 9:16 vertical Instagram Reels (1080x1920) with AI voiceover and kinetic captions."""
import asyncio
import os
import re
import subprocess
from PIL import Image, ImageDraw, ImageFont
import edge_tts
import imageio_ffmpeg

W, H = 1080, 1920
FPS = 25
MARGIN = 90
VOICE = "en-US-ChristopherNeural"  # Authoritative, natural tech founder voice

FONT_PATHS = [
    "fonts/Inter.ttf",
    os.getenv("FONT_PATH"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
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


def _get_audio_duration(audio_path):
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-i", audio_path, "-f", "null", "-"]
    p = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", p.stderr)
    if m:
        h, mn, s = map(float, m.groups())
        return h * 3600 + mn * 60 + s
    return 15.0


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


async def _generate_voiceover(text, out_mp3):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(out_mp3)


_BG_CACHE = None

def _get_base_bg():
    global _BG_CACHE
    if _BG_CACHE is None:
        img = Image.new("RGB", (1, H))
        c1, c2 = (8, 14, 30), (20, 50, 120)
        for y in range(H):
            factor = y / H
            r = int(c1[0] + (c2[0] - c1[0]) * factor)
            g = int(c1[1] + (c2[1] - c1[1]) * factor)
            b = int(c1[2] + (c2[2] - c1[2]) * factor)
            img.putpixel((0, y), (r, g, b))
        _BG_CACHE = img.resize((W, H), Image.Resampling.BICUBIC)
    return _BG_CACHE.copy()


def _draw_frame(t, total_dur, blocks, handle):
    """Draws a single 1080x1920 frame at timestamp t."""
    frame = _get_base_bg()
    draw = ImageDraw.Draw(frame)

    # Top Branding Header
    f_brand = _font(38)
    draw.text((MARGIN, 130), handle, font=f_brand, fill=(255, 255, 255, 240))
    # Glowing green live dot
    draw.ellipse([(MARGIN + draw.textlength(handle, font=f_brand) + 20, 144),
                  (MARGIN + draw.textlength(handle, font=f_brand) + 36, 160)],
                 fill=(34, 197, 94))

    # Tag Pill
    f_tag = _font(24)
    tag_text = "AI STRATEGY BREAKDOWN"
    tw = draw.textlength(tag_text, font=f_tag) + 36
    draw.rounded_rectangle([(MARGIN, 210), (MARGIN + tw, 256)], radius=12, fill=(30, 58, 138, 200), outline=(56, 189, 248, 220), width=2)
    draw.text((MARGIN + 18, 224), tag_text, font=f_tag, fill=(56, 189, 248, 255))

    # Active subtitle block
    active_block = blocks[-1]
    for b in blocks:
        if b["start"] <= t <= b["end"]:
            active_block = b
            break

    # Check if we are in outro (last 3 seconds)
    if t >= total_dur - 3.2:
        # Outro Callout
        f_outro_big = _font(74)
        draw.text((MARGIN, 820), "Follow", font=f_outro_big, fill=(255, 255, 255))
        draw.text((MARGIN, 915), handle, font=f_outro_big, fill=(56, 189, 248))
        draw.text((MARGIN, 1020), "For daily sharp AI & business breakdowns", font=_font(42), fill=(203, 213, 225))
    else:
        # Kinetic Subtitles in center
        text = active_block["text"]
        f_caption = _font(64)
        lines = _wrap(draw, text, f_caption, W - 2 * MARGIN)

        # Center vertically
        total_text_h = len(lines) * 85
        start_y = int((H - total_text_h) / 2) - 40

        # Translucent glass card behind caption for instant readability
        pad_x, pad_y = 40, 36
        draw.rounded_rectangle(
            [(MARGIN - pad_x, start_y - pad_y), (W - MARGIN + pad_x, start_y + total_text_h + pad_y)],
            radius=24,
            fill=(10, 18, 38),
            outline=(56, 189, 248),
            width=2
        )

        curr_y = start_y
        for idx, line in enumerate(lines):
            # Highlight first/last word in vibrant yellow
            words = line.split()
            x = MARGIN
            for w_idx, word in enumerate(words):
                w_color = (255, 255, 255)
                if (idx == 0 and w_idx == 0) or (idx == len(lines)-1 and w_idx == len(words)-1):
                    w_color = (250, 204, 21)  # Hormozi bold yellow
                draw.text((x, curr_y), word, font=f_caption, fill=w_color)
                x += draw.textlength(word + " ", font=f_caption)
            curr_y += 85

    # Bottom Progress Bar
    progress_w = int((W - 2 * MARGIN) * (t / total_dur))
    bar_y = H - 120
    draw.rounded_rectangle([(MARGIN, bar_y), (W - MARGIN, bar_y + 8)], radius=4, fill=(40, 55, 85))
    if progress_w > 0:
        draw.rounded_rectangle([(MARGIN, bar_y), (MARGIN + progress_w, bar_y + 8)], radius=4, fill=(56, 189, 248))

    return frame


def render_reel(script_data, handle, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    out_mp4 = os.path.join(out_dir, "reel.mp4")
    out_mp3 = os.path.join(out_dir, "voice.mp3")

    # 1. Compile full narration text
    hook = script_data.get("hook", "")
    sentences = script_data.get("sentences", [])
    all_sentences = [hook] + sentences
    full_speech = " ".join(all_sentences)

    print("[reels] Generating neural voiceover with edge-tts...")
    asyncio.run(_generate_voiceover(full_speech, out_mp3))

    total_dur = _get_audio_duration(out_mp3)
    # Add 2.5s for clean outro
    total_dur += 2.5
    print(f"[reels] Audio duration: {total_dur:.1f}s")

    # Estimate timing blocks per sentence
    per_sent_dur = (total_dur - 2.5) / len(all_sentences)
    blocks = []
    curr_t = 0.0
    for s in all_sentences:
        blocks.append({
            "text": s,
            "start": curr_t,
            "end": curr_t + per_sent_dur,
        })
        curr_t += per_sent_dur

    # 2. Render video using ffmpeg pipe
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ff, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",  # stdin pipe
        "-i", out_mp3,
        "-filter_complex", "[1:a]apad=pad_dur=3.0[a]",
        "-map", "0:v",
        "-map", "[a]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-t", f"{total_dur:.2f}",
        out_mp4
    ]

    print("[reels] Encoding 1080x1920 video with FFmpeg...")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    total_frames = int(total_dur * FPS)
    try:
        for frame_idx in range(total_frames):
            t = frame_idx / FPS
            frame = _draw_frame(t, total_dur, blocks, handle)
            proc.stdin.write(frame.tobytes())
    except (BrokenPipeError, OSError):
        pass
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass

    _, stderr_bytes = proc.communicate()
    if proc.returncode != 0:
        err_msg = stderr_bytes.decode(errors="replace") if stderr_bytes else "Unknown error"
        raise RuntimeError(f"FFmpeg encoding failed (exit {proc.returncode}): {err_msg[-500:]}")

    print(f"[reels] Reel created successfully at: {out_mp4} ({os.path.getsize(out_mp4) / 1024:.0f} KB)")
    return out_mp4
