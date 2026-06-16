import httpx
from bs4 import BeautifulSoup

from scraper.models import Event
from scraper.scrapers.base import BaseScraper
from scraper.utils.normalize import clean_text


class GuggenheimScraper(BaseScraper):
    def scrape(self) -> list[Event]:
        resp = httpx.get(self.url, follow_redirects=True, timeout=30, params={"per_page": 100})
        resp.raise_for_status()
        data = resp.json()

        events = []
        for item in data:
            raw_title = item.get("title", {}).get("rendered", "")
            title = clean_text(BeautifulSoup(raw_title, "lxml").get_text()) if raw_title else None
            if not title:
                continue

            link = item.get("link", self.url)
            slug = item.get("slug", "")

            start_date = None
            end_date = None
            meta = item.get("meta", {})
            if isinstance(meta, dict):
                start_date = meta.get("exhibition_start_date")
                end_date = meta.get("exhibition_end_date")

            if not start_date:
                date_str = item.get("date", "")
                if date_str:
                    start_date = date_str[:10]

            if not start_date:
                continue

            raw_desc = item.get("excerpt", {}).get("rendered", "")
            description = clean_text(BeautifulSoup(raw_desc, "lxml").get_text()) if raw_desc else None

            image_url = None
            featured = item.get("featured_media_url") or item.get("_embedded", {}).get("wp:featuredmedia", [{}])
            if isinstance(featured, list) and featured:
                image_url = featured[0].get("source_url")
            elif isinstance(featured, str):
                image_url = featured

            event = Event.from_dict({
                "source_id": self.source_id,
                "title": title,
                "description": description,
                "url": link,
                "image_url": image_url,
                "venue": "Solomon R. Guggenheim Museum",
                "address": "1071 Fifth Avenue, New York, NY 10128",
                "category": self.category,
                "start_date": start_date,
                "end_date": end_date if end_date != start_date else None,
                "is_free": False,
            })
            events.append(event)

        return events
