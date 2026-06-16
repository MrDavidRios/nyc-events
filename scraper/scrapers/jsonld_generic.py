import json

from bs4 import BeautifulSoup

from scraper.models import Event
from scraper.scrapers.base import BaseScraper
from scraper.utils.normalize import normalize_date, normalize_time, clean_text


class JsonLdScraper(BaseScraper):
    def _extract_jsonld_blocks(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "lxml")
        blocks = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
            except (json.JSONDecodeError, TypeError):
                continue
            if isinstance(data, list):
                blocks.extend(data)
            else:
                blocks.append(data)
        return blocks

    def _parse_datetime(self, value: str | None) -> tuple[str | None, str | None]:
        if not value:
            return None, None
        if "T" in value:
            parts = value.split("T")
            return normalize_date(parts[0]), normalize_time(parts[1][:5])
        return normalize_date(value), None

    def _parse_event(self, data: dict) -> Event | None:
        event_type = data.get("@type", "")
        if isinstance(event_type, list):
            event_type = event_type[0] if event_type else ""
        if event_type not in (
            "Event",
            "MusicEvent",
            "TheaterEvent",
            "DanceEvent",
            "ExhibitionEvent",
            "ScreeningEvent",
        ):
            return None

        start_date, start_time = self._parse_datetime(data.get("startDate"))
        if not start_date:
            return None
        end_date, end_time = self._parse_datetime(data.get("endDate"))

        if end_date == start_date:
            end_date = None

        location = data.get("location", {})
        if isinstance(location, dict):
            venue = location.get("name")
            address_obj = location.get("address", "")
            if isinstance(address_obj, dict):
                address = address_obj.get("streetAddress") or address_obj.get("name")
            else:
                address = address_obj or None
        else:
            venue = str(location) if location else None
            address = None

        price_range = None
        is_free = None
        offers = data.get("offers")
        if isinstance(offers, dict):
            price = offers.get("price")
            if price is not None:
                price = str(price)
                if price == "0" or price.lower() == "free":
                    is_free = True
                    price_range = "Free"
                else:
                    is_free = False
                    currency = offers.get("priceCurrency", "USD")
                    symbol = "$" if currency == "USD" else currency + " "
                    price_range = f"{symbol}{price}"

        image = data.get("image")
        if isinstance(image, dict):
            image = image.get("url")
        elif isinstance(image, list):
            image = image[0] if image else None

        return Event.from_dict({
            "source_id": self.source_id,
            "title": clean_text(data.get("name", "")) or "Untitled",
            "description": clean_text(data.get("description")),
            "url": data.get("url") or self.url,
            "image_url": image,
            "venue": clean_text(venue),
            "address": clean_text(address),
            "category": self.category,
            "start_date": start_date,
            "end_date": end_date,
            "start_time": start_time,
            "end_time": end_time,
            "is_free": is_free,
            "price_range": price_range,
        })

    def parse_jsonld(self, html: str) -> list[Event]:
        blocks = self._extract_jsonld_blocks(html)
        events = []
        for block in blocks:
            event = self._parse_event(block)
            if event:
                events.append(event)
        return events

    def scrape(self) -> list[Event]:
        html = self.fetch()
        return self.parse_jsonld(html)
