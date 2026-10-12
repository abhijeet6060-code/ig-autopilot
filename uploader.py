"""Hosts images at a public URL (Instagram must be able to fetch them).
Default: your own public GitHub repo (free). Optional: Cloudinary."""
import base64
import hashlib
import os
import time
import uuid

import requests

import config

_uploaded = []  # (repo_path, sha) for cleanup


def _gh_headers():
    token = config.get("GH_TOKEN") or config.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("Set GH_TOKEN (or run inside GitHub Actions) for the github uploader")
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}


def _github(path):
    repo = config.require("GITHUB_REPOSITORY")
    branch = config.get("REPO_BRANCH", "main")
    remote = f"tmp-media/{uuid.uuid4().hex[:8]}_{os.path.basename(path)}"
    with open(path, "rb") as f:
        body = {"message": "temp media", "branch": branch,
                "content": base64.b64encode(f.read()).decode()}
    r = requests.put(f"https://api.github.com/repos/{repo}/contents/{remote}",
                     headers=_gh_headers(), json=body, timeout=60)
    if not r.ok:
        raise RuntimeError(f"GitHub upload failed: {r.status_code} {r.text[:300]}")
    _uploaded.append((remote, r.json()["content"]["sha"]))

    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{remote}"
    for _ in range(15):  # wait until the raw URL is live
        if requests.head(url, timeout=15).status_code == 200:
            return url
        time.sleep(2)
    raise RuntimeError(f"Uploaded image never became reachable (is the repo public?): {url}")


def _cloudinary(path):
    cloud = config.require("CLOUDINARY_CLOUD_NAME")
    key = config.require("CLOUDINARY_API_KEY")
    secret = config.require("CLOUDINARY_API_SECRET")
    ts, folder = str(int(time.time())), "ig-autopilot"
    sig = hashlib.sha1(f"folder={folder}&timestamp={ts}{secret}".encode()).hexdigest()
    with open(path, "rb") as f:
        r = requests.post(f"https://api.cloudinary.com/v1_1/{cloud}/image/upload",
                          data={"api_key": key, "timestamp": ts, "folder": folder, "signature": sig},
                          files={"file": f}, timeout=60)
    if not r.ok:
        raise RuntimeError(f"Cloudinary upload failed: {r.text}")
    return r.json()["secure_url"]


def upload(path):
    return _cloudinary(path) if config.get("UPLOADER", "github") == "cloudinary" else _github(path)


def cleanup():
    """Delete temp images from the repo after publishing so it stays small."""
    repo = config.get("GITHUB_REPOSITORY")
    branch = config.get("REPO_BRANCH", "main")
    while _uploaded:
        remote, sha = _uploaded.pop()
        try:
            requests.delete(f"https://api.github.com/repos/{repo}/contents/{remote}",
                            headers=_gh_headers(),
                            json={"message": "remove temp media", "sha": sha, "branch": branch},
                            timeout=30)
        except Exception as e:
            print(f"[uploader] cleanup failed for {remote}: {e}")
