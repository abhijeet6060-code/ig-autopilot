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
import trends as trends_mod
import uploader


def run_once(force_draft=False):
    if db.published_last_24h() >= config.MAX_POSTS_PER_DAY:
        print("[main] Daily post cap reached, skipping.")
        return

    niches = [n.strip() for n in config.get("NICHES", "AI,business").split(",")]
    found = [t for t in trends_mod.collect(niches) if not db.seen(t.url)][:8]
    if not found:
        print("[main] No fresh trends found.")
        return
    print(f"[main] {len(found)} candidate trends, top: {found[0].title}")

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


def safe_run(force_draft=False):
    try:
        run_once(force_draft)
    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="run a single cycle and exit")
    ap.add_argument("--dry-run", action="store_true", help="never post, only save a draft")
    ap.add_argument("--daemon", action="store_true", help="run on POST_TIMES forever")
    args = ap.parse_args()

    if args.daemon:
        for t in config.POST_TIMES:
            schedule.every().day.at(t).do(safe_run, args.dry_run)
        print(f"[main] Scheduled daily at {', '.join(config.POST_TIMES)} (server local time). AUTO_POST={config.AUTO_POST}")
        while True:
            schedule.run_pending()
            time.sleep(30)
    else:
        run_once(args.dry_run)
