from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

TRACKING_PARAMS_PREFIX = ("utm_", "fbclid", "gclid", "mc_", "igshid")
DISALLOWED_PATH_SEGMENTS = {
    "",
    "/",
    "/blog",
    "/news",
    "/research",
    "/press",
    "/updates",
    "/discover/blog",
}


def canonicalize_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url.strip())
    if not parsed.scheme or not parsed.netloc:
        return ""

    clean_query = [
        (k, v)
        for k, v in parse_qsl(parsed.query, keep_blank_values=True)
        if not any(k.lower().startswith(prefix) for prefix in TRACKING_PARAMS_PREFIX)
    ]
    normalized_path = parsed.path or "/"
    rebuilt = parsed._replace(query=urlencode(clean_query), fragment="", path=normalized_path)
    return urlunparse(rebuilt)


def is_article_like_url(url: str) -> bool:
    if not url:
        return False
    parsed = urlparse(url)
    path = (parsed.path or "/").rstrip("/")
    if not path:
        path = "/"
    return path.lower() not in DISALLOWED_PATH_SEGMENTS
