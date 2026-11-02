"""Publishes swipeable PDF carousels and video reels to LinkedIn via the REST API (/rest/posts)."""
import os
from PIL import Image
import requests
import config

VERSION = "202610"


def _headers():
    token = config.require("LINKEDIN_ACCESS_TOKEN")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": VERSION,
    }


def is_configured():
    return bool(config.get("LINKEDIN_ACCESS_TOKEN") and config.get("LINKEDIN_AUTHOR_URN"))


def _make_pdf(image_paths):
    """Compiles individual JPG slides into a single swipeable PDF carousel."""
    out_pdf = os.path.join(os.path.dirname(image_paths[0]), "carousel.pdf")
    imgs = [Image.open(p).convert("RGB") for p in image_paths]
    imgs[0].save(out_pdf, "PDF", resolution=100.0, save_all=True, append_images=imgs[1:])
    return out_pdf


def publish_carousel(image_paths, caption):
    """Uploads slides as a native swipeable LinkedIn Document Carousel."""
    author_urn = config.require("LINKEDIN_AUTHOR_URN")
    token = config.require("LINKEDIN_ACCESS_TOKEN")
    headers = _headers()

    pdf_path = _make_pdf(image_paths)

    # 1. Initialize Document Upload
    init_url = "https://api.linkedin.com/rest/documents?action=initializeUpload"
    init_payload = {"initializeUploadRequest": {"owner": author_urn}}
    r_init = requests.post(init_url, headers=headers, json=init_payload, timeout=60)
    if not r_init.ok:
        raise RuntimeError(f"LinkedIn document init failed {r_init.status_code}: {r_init.text[:300]}")

    init_data = r_init.json().get("value", {})
    upload_url = init_data["uploadUrl"]
    doc_urn = init_data["document"]

    # 2. Upload PDF Binary
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    r_upload = requests.put(upload_url, headers={"Authorization": f"Bearer {token}"}, data=pdf_bytes, timeout=120)
    if r_upload.status_code not in (200, 201):
        raise RuntimeError(f"LinkedIn document binary upload failed: {r_upload.status_code}")

    # 3. Create Post referencing Document
    posts_url = "https://api.linkedin.com/rest/posts"
    post_title = caption.split("\n")[0][:100]
    payload = {
        "author": author_urn,
        "commentary": caption[:3000],
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "content": {
            "media": {
                "title": post_title,
                "id": doc_urn,
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    r_post = requests.post(posts_url, headers=headers, json=payload, timeout=60)
    if r_post.status_code not in (200, 201):
        raise RuntimeError(f"LinkedIn post creation failed {r_post.status_code}: {r_post.text[:300]}")

    post_id = r_post.headers.get("x-restli-id", "published")
    return post_id


def publish_reel(video_path, caption):
    """Uploads and publishes a vertical 9:16 video to LinkedIn."""
    author_urn = config.require("LINKEDIN_AUTHOR_URN")
    token = config.require("LINKEDIN_ACCESS_TOKEN")
    headers = _headers()
    file_size = os.path.getsize(video_path)

    # 1. Initialize Video Upload
    init_url = "https://api.linkedin.com/rest/videos?action=initializeUpload"
    init_payload = {
        "initializeUploadRequest": {
            "owner": author_urn,
            "fileSizeBytes": file_size,
            "uploadCaptions": False,
            "uploadThumbnail": False,
        }
    }
    r_init = requests.post(init_url, headers=headers, json=init_payload, timeout=60)
    if not r_init.ok:
        raise RuntimeError(f"LinkedIn video init failed {r_init.status_code}: {r_init.text[:300]}")

    init_data = r_init.json().get("value", {})
    upload_url = init_data["uploadInstructions"][0]["uploadUrl"]
    video_urn = init_data["video"]

    # 2. Upload Video Binary
    with open(video_path, "rb") as f:
        vid_bytes = f.read()

    r_upload = requests.put(upload_url, headers={"Authorization": f"Bearer {token}"}, data=vid_bytes, timeout=180)
    if r_upload.status_code not in (200, 201):
        raise RuntimeError(f"LinkedIn video binary upload failed: {r_upload.status_code}")

    # 3. Create Video Post
    posts_url = "https://api.linkedin.com/rest/posts"
    post_title = caption.split("\n")[0][:100]
    payload = {
        "author": author_urn,
        "commentary": caption[:3000],
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "content": {
            "media": {
                "title": post_title,
                "id": video_urn,
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    r_post = requests.post(posts_url, headers=headers, json=payload, timeout=60)
    if r_post.status_code not in (200, 201):
        raise RuntimeError(f"LinkedIn video post creation failed {r_post.status_code}: {r_post.text[:300]}")

    return r_post.headers.get("x-restli-id", "published")

