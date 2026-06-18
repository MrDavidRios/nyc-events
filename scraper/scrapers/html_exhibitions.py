import re
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from scraper.models import Event
from scraper.scrapers.base import BaseScraper
from scraper.utils.normalize import clean_text


def _parse_exhibition_dates(
    text: str,
) -> tuple[str | None, str | None]:
    """Parse exhibition date strings like 'May 16–December 6, 2026' or 'Through April 11, 2027'."""
    text = text.replace("–", "-").replace("—", "-").strip()

    through = re.match(r"[Tt]hrough\s+(.+)", text)
    if through:
        end = _parse_single_date(through.group(1))
        return None, end

    parts = re.split(r"\s*-\s*", text, maxsplit=1)
    if len(parts) == 2:
        end_date = _parse_single_date(parts[1])
        year_match = re.search(r"\d{4}", parts[1])
        year = year_match.group() if year_match else str(datetime.now().year)
        start_text = parts[0].strip()
        if not re.search(r"\d{4}", start_text):
            start_text += f", {year}"
        start_date = _parse_single_date(start_text)
        return start_date, end_date

    return _parse_single_date(text), None


def _parse_single_date(text: str) -> str | None:
    text = text.strip().rstrip(".")
    for fmt in ("%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


class MetMuseumScraper(BaseScraper):
    def scrape(self) -> list[Event]:
        html = self.fetch()
        soup = BeautifulSoup(html, "lxml")
        events: list[Event] = []

        for card in soup.select("article[class*='exhibitionCard']"):
            title_el = card.select_one("[class*='title']")
            if not title_el:
                continue
            title = clean_text(title_el.get_text())
            if not title:
                continue

            meta_el = card.select_one("[class*='meta']")
            meta_text = clean_text(meta_el.get_text()) if meta_el else None
            start_date, end_date = _parse_exhibition_dates(meta_text) if meta_text else (None, None)

            if not start_date:
                start_date = datetime.now().strftime("%Y-%m-%d")

            link = card.select_one("a")
            href = link.get("href", "") if link else ""
            event_url = urljoin("https://www.metmuseum.org", href) if href else self.url

            img = card.select_one("img")
            image_url = img.get("src") if img else None

            events.append(Event.from_dict({
                "source_id": self.source_id,
                "title": title,
                "url": event_url,
                "image_url": image_url,
                "category": self.category,
                "start_date": start_date,
                "end_date": end_date,
                "venue": "The Metropolitan Museum of Art",
            }))

        return events


class BrooklynMuseumScraper(BaseScraper):
    def scrape(self) -> list[Event]:
        html = self.fetch()
        soup = BeautifulSoup(html, "lxml")
        events: list[Event] = []

        for link in soup.select("a[href*='/exhibitions/']"):
            href = link.get("href", "")
            if href in ("/exhibitions", "/exhibitions/upcoming"):
                continue

            title_el = link.select_one("h3 span")
            if not title_el:
                continue
            title = clean_text(title_el.get_text())
            if not title:
                continue

            date_el = link.select_one("span.flex.flex-row span")
            date_text = clean_text(date_el.get_text()) if date_el else None
            start_date, end_date = _parse_exhibition_dates(date_text) if date_text else (None, None)

            if not start_date:
                start_date = datetime.now().strftime("%Y-%m-%d")

            event_url = urljoin("https://www.brooklynmuseum.org", href)

            events.append(Event.from_dict({
                "source_id": self.source_id,
                "title": title,
                "url": event_url,
                "category": self.category,
                "start_date": start_date,
                "end_date": end_date,
                "venue": "Brooklyn Museum",
            }))

        seen: set[str] = set()
        deduped: list[Event] = []
        for e in events:
            if e.id not in seen:
                seen.add(e.id)
                deduped.append(e)
        return deduped
