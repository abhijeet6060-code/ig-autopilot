"""IG Autopilot: trends -> Claude -> images -> Instagram."""
import argparse
import os
import time
import traceback

import schedule

import config
import content
import db
import images
import instagram
import reels
import trends as trends_mod
import uploader


def run_once(force_draft=False, post_type="carousel", force=False):
    if not force and db.published_last_24h() >= config.MAX_POSTS_PER_DAY:
        print(f"[main] Daily post cap ({config.MAX_POSTS_PER_DAY}) reached, skipping. (Use --force to override)")
        return

    niches = [n.strip() for n in config.get("NICHES", "AI,business").split(",")]
    found = [t for t in trends_mod.collect(niches) if not db.seen(t.url)][:8]
    if not found:
        # Fallback to any recent trends if all are seen
        found = trends_mod.collect(niches)[:8]
    if not found:
        print("[main] No fresh trends found.")
        return
    print(f"[main] {len(found)} candidate trends, top: {found[0].title}")

    if post_type == "reel":
        reel_data = content.generate_reel_script(found)
        chosen = found[reel_data.get("chosen_index", 0)]
        caption = content.full_caption(reel_data, chosen.source)
        stamp = time.strftime("%Y%m%d_%H%M%S")
        out_dir = os.path.join(config.OUTPUT_DIR, f"reel_{stamp}")
        video_path = reels.render_reel(reel_data, config.HANDLE, out_dir)
        with open(os.path.join(out_dir, "caption.txt"), "w", encoding="utf-8") as f:
            f.write(f"{caption}\n\nStory: {chosen.title}\n{chosen.url}\n")

        if force_draft or not config.AUTO_POST:
            db.record(chosen.url, chosen.title, caption, None, "draft")
            print(f"[main] Reel draft saved to {out_dir} (AUTO_POST is off).")
            return

        try:
            video_url = uploader.upload(video_path)
            media_id = instagram.publish_reel(video_url, caption)
        finally:
            uploader.cleanup()
        db.record(chosen.url, chosen.title, caption, media_id, "published")
        print(f"[main] Reel published! media id {media_id}: {chosen.title}")
        return

    data = content.generate(found)
    if data.get("skip"):
        print("[main] LLM found nothing worth posting. Skipping.")
        return

    chosen = found[data["chosen_index"]]
    caption = content.full_caption(data, chosen.source)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(config.OUTPUT_DIR, stamp)
    paths = images.render(data, chosen.source, config.HANDLE, out_dir)
    with open(os.path.join(out_dir, "caption.txt"), "w", encoding="utf-8") as f:
        f.write(f"{caption}\n\nStory: {chosen.title}\n{chosen.url}\n")

    if force_draft or not config.AUTO_POST:
        db.record(chosen.url, chosen.title, caption, None, "draft")
        print(f"[main] Draft saved to {out_dir} (AUTO_POST is off).")
        return

    try:
        urls = [uploader.upload(p) for p in paths]
        media_id = instagram.publish(urls, caption)
    finally:
        uploader.cleanup()
    db.record(chosen.url, chosen.title, caption, media_id, "published")
    print(f"[main] Published! media id {media_id}: {chosen.title}")


def safe_run(force_draft=False, post_type="carousel", force=False):
    try:
        run_once(force_draft, post_type=post_type, force=force)
    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="run a single cycle and exit")
    ap.add_argument("--dry-run", action="store_true", help="never post, only save a draft")
    ap.add_argument("--daemon", action="store_true", help="run on POST_TIMES forever")
    ap.add_argument("--reel", action="store_true", help="generate/publish a 9:16 vertical Reel instead of carousel")
    ap.add_argument("--force", action="store_true", help="force run even if daily post cap is reached")
    ap.add_argument("--type", choices=["carousel", "reel", "auto"], default=None,
                    help="override post type (default: carousel or config POST_TYPE)")
    args = ap.parse_args()

    chosen_type = "reel" if args.reel else (args.type or config.get("POST_TYPE", "carousel"))

    if args.daemon:
        times = config.POST_TIMES
        for idx, t in enumerate(times):
            # If auto, schedule Morning as Carousel and Evening as Reel!
            ptype = chosen_type
            if chosen_type == "auto":
                ptype = "carousel" if idx == 0 else "reel"
            schedule.every().day.at(t).do(safe_run, args.dry_run, ptype, args.force)
        print(f"[main] Scheduled daily at {', '.join(times)} (server local time). Type={chosen_type}, AUTO_POST={config.AUTO_POST}")
        while True:
            schedule.run_pending()
            time.sleep(30)
    else:
        run_once(args.dry_run, post_type=chosen_type, force=args.force)
