from scraper.scrapers.ical_generic import ICalScraper

SAMPLE_ICAL = """\
BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:20260620T193000
DTEND:20260620T213000
SUMMARY:A Midsummer Night's Dream
DESCRIPTION:Ballet performance
LOCATION:David H. Koch Theater
URL:https://www.lincolncenter.org/event/123
END:VEVENT
BEGIN:VEVENT
DTSTART:20260621T200000
SUMMARY:Piano Concerto
LOCATION:Alice Tully Hall
URL:https://www.lincolncenter.org/event/456
END:VEVENT
END:VCALENDAR
"""


def test_ical_scraper_parses_events():
    source = {
        "id": "lincoln-center",
        "name": "Lincoln Center",
        "url": "https://www.lincolncenter.org/calendar.ics",
        "category": "performing-arts",
    }
    scraper = ICalScraper(source)
    events = scraper.parse_ical(SAMPLE_ICAL)

    assert len(events) == 2

    e1 = events[0]
    assert e1.title == "A Midsummer Night's Dream"
    assert e1.start_date == "2026-06-20"
    assert e1.start_time == "19:30"
    assert e1.end_time == "21:30"
    assert e1.venue == "David H. Koch Theater"
    assert e1.source_id == "lincoln-center"
    assert e1.category == "performing-arts"

    e2 = events[1]
    assert e2.title == "Piano Concerto"
    assert e2.start_date == "2026-06-21"
    assert e2.start_time == "20:00"
    assert e2.end_time is None


def test_ical_scraper_handles_all_day():
    ical = """\
BEGIN:VCALENDAR
BEGIN:VEVENT
DTSTART;VALUE=DATE:20260701
DTEND;VALUE=DATE:20261015
SUMMARY:Summer Exhibition
URL:https://example.com/exhibit
END:VEVENT
END:VCALENDAR
"""
    source = {"id": "test", "url": "https://example.com", "category": "museum"}
    scraper = ICalScraper(source)
    events = scraper.parse_ical(ical)
    assert len(events) == 1
    assert events[0].start_date == "2026-07-01"
    assert events[0].end_date == "2026-10-15"
    assert events[0].start_time is None
