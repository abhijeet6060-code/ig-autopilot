"""Publishes multi-photo carousels and reels to Facebook via Meta Graph API."""
import json
import requests
import config


def _base():
    return f"https://graph.facebook.com/{config.get('GRAPH_VERSION', 'v21.0')}"


def is_configured():
    return bool(config.get("FB_PAGE_ID") and config.get("FB_PAGE_ACCESS_TOKEN"))


def publish_carousel(image_urls, caption):
    """Publishes a multi-photo post to Facebook Page feed."""
    token = config.require("FB_PAGE_ACCESS_TOKEN")
    page_id = config.require("FB_PAGE_ID")

    # 1. Upload each photo as unpublished/temporary media
    attached_media = []
    for url in image_urls:
        r = requests.post(
            f"{_base()}/{page_id}/photos",
            data={
                "url": url,
                "published": "false",
                "access_token": token,
            },
            timeout=60,
        )
        if not r.ok:
            raise RuntimeError(f"Facebook photo upload failed {r.status_code}: {r.text[:300]}")
        photo_id = r.json().get("id")
        attached_media.append({"media_fbid": photo_id})

    # 2. Publish multi-photo feed post
    r_post = requests.post(
        f"{_base()}/{page_id}/feed",
        data={
            "message": caption,
            "attached_media": json.dumps(attached_media),
            "access_token": token,
        },
        timeout=60,
    )
    if not r_post.ok:
        raise RuntimeError(f"Facebook feed publish failed {r_post.status_code}: {r_post.text[:300]}")
    return r_post.json().get("id")


def publish_reel(video_url, caption):
    """Publishes a video/reel to Facebook Page."""
    token = config.require("FB_PAGE_ACCESS_TOKEN")
    page_id = config.require("FB_PAGE_ID")

    r = requests.post(
        f"{_base()}/{page_id}/videos",
        data={
            "file_url": video_url,
            "description": caption,
            "access_token": token,
        },
        timeout=120,
    )
    if not r.ok:
        raise RuntimeError(f"Facebook video publish failed {r.status_code}: {r.text[:300]}")
    return r.json().get("id")

