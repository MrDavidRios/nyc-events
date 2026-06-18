from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scraper.models import Event
from scraper.scrapers.base import BaseScraper
from scraper.utils.normalize import normalize_date, normalize_time, clean_text

BASE_URL = "https://www.carnegiehall.org"
MAX_SHOW_MORE_CLICKS = 20


class CarnegieHallScraper(BaseScraper):
    def scrape(self) -> list[Event]:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)

            for _ in range(MAX_SHOW_MORE_CLICKS):
                clicked = page.evaluate("""
                    (() => {
                        const btn = document.querySelector(".ch-events-list__more button, .ch-events-list__more a");
                        if (btn) { btn.click(); return true; }
                        return false;
                    })()
                """)
                if not clicked:
                    break
                page.wait_for_timeout(2000)

            html = page.content()
            browser.close()

        return self._parse(html)

    def _parse(self, html: str) -> list[Event]:
        soup = BeautifulSoup(html, "lxml")
        events: list[Event] = []

        for item in soup.select(".ch-events-list-item"):
            date_el = item.select_one(".date")
            if not date_el:
                continue
            date_text = date_el.get_text(" ", strip=True)
            start_date = normalize_date(date_text)
            if not start_date:
                continue

            for ev in item.select(".ch-event-body"):
                title_el = ev.select_one(".ch-event-content__title")
                if not title_el:
                    continue
                title = clean_text(title_el.get_text())
                if not title:
                    continue

                time_el = ev.select_one(".time")
                time_text = clean_text(time_el.get_text()) if time_el else None
                start_time = normalize_time(time_text) if time_text else None

                location_el = ev.select_one(".location")
                venue = clean_text(location_el.get_text()) if location_el else None

                link = ev.select_one("a.event-item")
                href = link.get("href", "") if link else ""
                event_url = urljoin(BASE_URL, href) if href else self.url

                events.append(Event.from_dict({
                    "source_id": self.source_id,
                    "title": title,
                    "url": event_url,
                    "venue": venue,
                    "category": self.category,
                    "start_date": start_date,
                    "start_time": start_time,
                }))

        return events
