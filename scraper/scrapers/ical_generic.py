from datetime import date, datetime

from icalendar import Calendar

from scraper.models import Event
from scraper.scrapers.base import BaseScraper
from scraper.utils.normalize import clean_text


class ICalScraper(BaseScraper):
    def parse_ical(self, ical_text: str) -> list[Event]:
        cal = Calendar.from_ical(ical_text)
        events = []
        for component in cal.walk("VEVENT"):
            dt_start = component.get("DTSTART")
            if not dt_start:
                continue
            dt_val = dt_start.dt

            if isinstance(dt_val, datetime):
                start_date = dt_val.strftime("%Y-%m-%d")
                start_time = dt_val.strftime("%H:%M")
            elif isinstance(dt_val, date):
                start_date = dt_val.strftime("%Y-%m-%d")
                start_time = None
            else:
                continue

            end_date = None
            end_time = None
            dt_end = component.get("DTEND")
            if dt_end:
                end_val = dt_end.dt
                if isinstance(end_val, datetime):
                    end_date = end_val.strftime("%Y-%m-%d")
                    end_time = end_val.strftime("%H:%M")
                elif isinstance(end_val, date):
                    end_date = end_val.strftime("%Y-%m-%d")

            if end_date == start_date:
                end_date = None

            event = Event.from_dict({
                "source_id": self.source_id,
                "title": clean_text(str(component.get("SUMMARY", ""))) or "Untitled",
                "description": clean_text(str(component.get("DESCRIPTION", ""))) or None,
                "url": str(component.get("URL", "")) or self.url,
                "venue": clean_text(str(component.get("LOCATION", ""))) or None,
                "category": self.category,
                "start_date": start_date,
                "end_date": end_date,
                "start_time": start_time,
                "end_time": end_time,
            })
            events.append(event)
        return events

    def scrape(self) -> list[Event]:
        ical_text = self.fetch()
        return self.parse_ical(ical_text)
