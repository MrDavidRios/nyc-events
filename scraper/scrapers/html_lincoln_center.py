import re
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scraper.models import Event
from scraper.scrapers.base import BaseScraper
from scraper.utils.normalize import normalize_time, clean_text

BASE_URL = "https://www.lincolncenter.org"
MONTHS_AHEAD = 3


class LincolnCenterScraper(BaseScraper):
    def scrape(self) -> list[Event]:
        from playwright.sync_api import sync_playwright

        all_events: list[Event] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)

            for month_idx in range(MONTHS_AHEAD):
                html = page.content()
                all_events.extend(self._parse_month(html))

                clicked = page.evaluate("""
                    (() => {
                        const btn = document.querySelector('a[class*="calendar-next-month-text"]');
                        if (btn) { btn.click(); return true; }
                        return false;
                    })()
                """)
                if clicked:
                    page.wait_for_timeout(3000)

            browser.close()

        seen_ids: set[str] = set()
        deduped: list[Event] = []
        for event in all_events:
            if event.id not in seen_ids:
                seen_ids.add(event.id)
                deduped.append(event)
        return deduped

    def _parse_month(self, html: str) -> list[Event]:
        soup = BeautifulSoup(html, "lxml")
        rows = soup.select("div.calendar-row")
        if len(rows) < 2:
            return []

        now = datetime.now()
        current_year = now.year
        current_month: int | None = None
        events: list[Event] = []

        for row in rows[1:]:
            days = row.select("div.calendar-day")
            for day in days:
                date_el = day.select_one("h1.calendar-day-date")
                if not date_el:
                    continue

                date_text = date_el.get_text(strip=True)
                current_month, day_num = self._parse_day_label(
                    date_text, current_month
                )
                if current_month is None or day_num is None:
                    continue

                year = current_year
                if current_month < now.month:
                    year += 1

                date_str = f"{year}-{current_month:02d}-{day_num:02d}"

                for show in day.select("div.cal-day-show-border-cont"):
                    event = self._parse_show(show, date_str)
                    if event:
                        events.append(event)

        return events

    def _parse_day_label(
        self, text: str, current_month: int | None
    ) -> tuple[int | None, int | None]:
        match = re.match(r"([A-Za-z]+)\s*(\d+)", text)
        if match:
            month_str, day_str = match.group(1), match.group(2)
            try:
                month_num = datetime.strptime(month_str, "%b").month
            except ValueError:
                try:
                    month_num = datetime.strptime(month_str, "%B").month
                except ValueError:
                    return current_month, None
            return month_num, int(day_str)

        if text.isdigit():
            return current_month, int(text)

        return current_month, None

    def _parse_show(self, show, date_str: str) -> Event | None:
        name_el = show.select_one(".show-name")
        if not name_el:
            return None
        title = clean_text(name_el.get_text())
        if not title:
            return None

        time_el = show.select_one(".show-time")
        time_text = clean_text(time_el.get_text()) if time_el else None
        start_time = normalize_time(time_text) if time_text else None

        org_el = show.select_one(".show-org")
        venue = clean_text(org_el.get_text()) if org_el else None

        link = show.select_one("a")
        href = link.get("href", "") if link else ""
        if href and not href.startswith("http"):
            href = urljoin(BASE_URL, href)
        event_url = href or self.url

        return Event.from_dict({
            "source_id": self.source_id,
            "title": title,
            "url": event_url,
            "venue": venue,
            "category": self.category,
            "start_date": date_str,
            "start_time": start_time,
        })
