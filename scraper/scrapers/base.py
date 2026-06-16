from abc import ABC, abstractmethod

import httpx

from scraper.models import Event


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}


class BaseScraper(ABC):
    def __init__(self, source: dict):
        self.source = source
        self.source_id = source["id"]
        self.url = source["url"]
        self.category = source.get("category")

    def fetch(self, url: str | None = None) -> str:
        resp = httpx.get(url or self.url, headers=HEADERS, follow_redirects=True, timeout=30)
        resp.raise_for_status()
        return resp.text

    def fetch_bytes(self, url: str | None = None) -> bytes:
        resp = httpx.get(url or self.url, headers=HEADERS, follow_redirects=True, timeout=30)
        resp.raise_for_status()
        return resp.content

    @abstractmethod
    def scrape(self) -> list[Event]:
        pass
