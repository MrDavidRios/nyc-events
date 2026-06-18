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
        self.use_browser = source.get("use_browser", False)

    def fetch(self, url: str | None = None) -> str:
        if self.use_browser:
            return self.fetch_with_browser(url)
        resp = httpx.get(url or self.url, headers=HEADERS, follow_redirects=True, timeout=30)
        resp.raise_for_status()
        return resp.text

    def fetch_bytes(self, url: str | None = None) -> bytes:
        resp = httpx.get(url or self.url, headers=HEADERS, follow_redirects=True, timeout=30)
        resp.raise_for_status()
        return resp.content

    def fetch_with_browser(self, url: str | None = None) -> str:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url or self.url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)
            html = page.content()
            browser.close()
            return html

    @abstractmethod
    def scrape(self) -> list[Event]:
        pass
