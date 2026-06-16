from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup


def _extract_favicon_from_html(html: str, base_url: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    apple = soup.find("link", rel=lambda r: r and "apple-touch-icon" in r)
    if apple and apple.get("href"):
        return urljoin(base_url, apple["href"])
    icon = soup.find("link", rel=lambda r: r and "icon" in r)
    if icon and icon.get("href"):
        return urljoin(base_url, icon["href"])
    return None


def resolve_favicon_url(source_url: str) -> str | None:
    try:
        resp = httpx.get(source_url, follow_redirects=True, timeout=10)
        resp.raise_for_status()
        result = _extract_favicon_from_html(resp.text, str(resp.url))
        if result:
            return result
    except httpx.HTTPError:
        pass
    base = f"{httpx.URL(source_url).scheme}://{httpx.URL(source_url).host}"
    fallback = f"{base}/favicon.ico"
    try:
        resp = httpx.head(fallback, follow_redirects=True, timeout=5)
        if resp.status_code == 200:
            return fallback
    except httpx.HTTPError:
        pass
    return None
