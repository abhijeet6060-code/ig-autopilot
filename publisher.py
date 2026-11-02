"""Unified Multi-Platform Distribution Hub.
Dispatches content across:
- Instagram (Carousels & Reels)
- Facebook (Multi-photo posts & Reels)
- YouTube (YouTube Shorts)
- LinkedIn (PDF Carousels & Videos)
"""
import config
import facebook
import instagram


def publish_carousel(image_urls, caption):
    """Cross-posts a carousel/multi-photo post to all active platforms."""
    results = {}

    # 1. Instagram
    try:
        ig_id = instagram.publish(image_urls, caption)
        print(f"[publisher] ✅ Instagram Carousel published! ID: {ig_id}")
        results["instagram"] = ig_id
    except Exception as e:
        print(f"[publisher] ❌ Instagram publish failed: {e}")
        results["instagram_error"] = str(e)

    # 2. Facebook
    if facebook.is_configured():
        try:
            fb_id = facebook.publish_carousel(image_urls, caption)
            print(f"[publisher] ✅ Facebook Carousel published! ID: {fb_id}")
            results["facebook"] = fb_id
        except Exception as e:
            print(f"[publisher] ❌ Facebook publish failed: {e}")
            results["facebook_error"] = str(e)
    else:
        print("[publisher] ℹ️ Facebook skipped (set FB_PAGE_ACCESS_TOKEN to enable).")

    return results


def publish_reel(video_url, caption):
    """Cross-posts a video reel to all active platforms."""
    results = {}

    # 1. Instagram
    try:
        ig_id = instagram.publish_reel(video_url, caption)
        print(f"[publisher] ✅ Instagram Reel published! ID: {ig_id}")
        results["instagram"] = ig_id
    except Exception as e:
        print(f"[publisher] ❌ Instagram Reel failed: {e}")
        results["instagram_error"] = str(e)

    # 2. Facebook
    if facebook.is_configured():
        try:
            fb_id = facebook.publish_reel(video_url, caption)
            print(f"[publisher] ✅ Facebook Reel published! ID: {fb_id}")
            results["facebook"] = fb_id
        except Exception as e:
            print(f"[publisher] ❌ Facebook Reel failed: {e}")
            results["facebook_error"] = str(e)
    else:
        print("[publisher] ℹ️ Facebook skipped (set FB_PAGE_ACCESS_TOKEN to enable).")

    return results

