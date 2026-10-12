"""Publishes single images or carousels via the Instagram Graph API."""
import time

import requests

import config


def _base():
    host = config.get("GRAPH_HOST", "graph.instagram.com")
    return f"https://{host}/{config.GRAPH_VERSION}"


def _call(method, path, **params):
    params["access_token"] = config.require("IG_ACCESS_TOKEN")
    r = requests.request(method, f"{_base()}/{path}",
                         **({"data": params} if method == "POST" else {"params": params}),
                         timeout=60)
    if not r.ok:
        raise RuntimeError(f"Instagram API error {r.status_code}: {r.text}")
    return r.json()


def _wait_ready(container_id, timeout=90):
    end = time.time() + timeout
    while time.time() < end:
        status = _call("GET", container_id, fields="status_code").get("status_code")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Media container {container_id} status: {status}")
        time.sleep(3)
    raise TimeoutError("Instagram media container did not finish in time")


def publish(image_urls, caption):
    ig = config.require("IG_USER_ID")
    if len(image_urls) == 1:
        container = _call("POST", f"{ig}/media", image_url=image_urls[0], caption=caption)["id"]
    else:
        children = []
        for url in image_urls:
            cid = _call("POST", f"{ig}/media", image_url=url, is_carousel_item="true")["id"]
            _wait_ready(cid)
            children.append(cid)
        container = _call("POST", f"{ig}/media", media_type="CAROUSEL",
                          children=",".join(children), caption=caption)["id"]
    _wait_ready(container)
    return _call("POST", f"{ig}/media_publish", creation_id=container)["id"]
