from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scraper.models import Event
from scraper.scrapers.base import BaseScraper
from scraper.utils.normalize import normalize_date, normalize_time, clean_text


class HtmlScraper(BaseScraper):
    def __init__(self, source: dict):
        super().__init__(source)
        self.selectors = source.get("selectors", {})

    def _select_text(self, card, selector: str | None) -> str | None:
        if not selector:
            return None
        el = card.select_one(selector)
        if not el:
            return None
        if el.name == "meta" and el.get("content"):
            return clean_text(el["content"])
        return clean_text(el.get_text())

    def _select_attr(self, card, selector: str | None, attr: str) -> str | None:
        if not selector:
            return None
        el = card.select_one(selector)
        if not el:
            return None
        return el.get(attr)

    def parse_html(self, html: str) -> list[Event]:
        soup = BeautifulSoup(html, "lxml")
        event_selector = self.selectors.get("event_list", "")
        if not event_selector:
            return []

        cards = soup.select(event_selector)
        events = []
        for card in cards:
            title = self._select_text(card, self.selectors.get("title"))
            if not title:
                continue

            date_text = self._select_text(card, self.selectors.get("date"))
            start_date = normalize_date(date_text)
            if not start_date:
                continue

            time_text = self._select_text(card, self.selectors.get("time"))
            start_time = normalize_time(time_text)

            url_href = self._select_attr(card, self.selectors.get("url"), "href")
            event_url = urljoin(self.url, url_href) if url_href else self.url

            venue = self._select_text(card, self.selectors.get("venue"))
            description = self._select_text(card, self.selectors.get("description"))
            image_src = self._select_attr(card, self.selectors.get("image"), "src")
            image_url = urljoin(self.url, image_src) if image_src else None

            event = Event.from_dict({
                "source_id": self.source_id,
                "title": title,
                "description": description,
                "url": event_url,
                "image_url": image_url,
                "venue": venue,
                "category": self.category,
                "start_date": start_date,
                "start_time": start_time,
            })
            events.append(event)
        return events

    def scrape(self) -> list[Event]:
        html = self.fetch()
        return self.parse_html(html)
