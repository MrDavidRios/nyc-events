from scraper.scrapers.html_generic import HtmlScraper

SAMPLE_HTML = """
<html><body>
<div class="events-list">
    <div class="event-card">
        <h3 class="event-title"><a href="/event/1">Jazz Night</a></h3>
        <span class="event-date">June 20, 2026</span>
        <span class="event-time">7:30 PM</span>
        <span class="event-venue">Central Park</span>
    </div>
    <div class="event-card">
        <h3 class="event-title"><a href="/event/2">Rock Festival</a></h3>
        <span class="event-date">June 21, 2026</span>
        <span class="event-time">6:00 PM</span>
        <span class="event-venue">Prospect Park</span>
    </div>
</div>
</body></html>
"""


def test_html_scraper_parses_events():
    source = {
        "id": "summerstage",
        "url": "https://cityparksfoundation.org/summerstage/",
        "category": "outdoor",
        "selectors": {
            "event_list": ".event-card",
            "title": ".event-title a",
            "url": ".event-title a[href]",
            "date": ".event-date",
            "time": ".event-time",
            "venue": ".event-venue",
        },
    }
    scraper = HtmlScraper(source)
    events = scraper.parse_html(SAMPLE_HTML)

    assert len(events) == 2
    assert events[0].title == "Jazz Night"
    assert events[0].start_date == "2026-06-20"
    assert events[0].start_time == "19:30"
    assert events[0].venue == "Central Park"
    assert events[0].url == "https://cityparksfoundation.org/event/1"


def test_html_scraper_handles_empty():
    source = {
        "id": "test",
        "url": "https://example.com",
        "category": "outdoor",
        "selectors": {"event_list": ".event-card", "title": ".title", "date": ".date"},
    }
    scraper = HtmlScraper(source)
    events = scraper.parse_html("<html><body>No events</body></html>")
    assert events == []
