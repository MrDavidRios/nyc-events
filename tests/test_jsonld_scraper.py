from scraper.scrapers.jsonld_generic import JsonLdScraper

SAMPLE_HTML = """
<html>
<head>
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "Event",
    "name": "Picasso Exhibition",
    "startDate": "2026-07-01T10:00:00",
    "endDate": "2026-10-15T18:00:00",
    "url": "https://www.metmuseum.org/exhibitions/picasso",
    "location": {
        "@type": "Place",
        "name": "The Metropolitan Museum of Art",
        "address": "1000 Fifth Avenue, New York, NY 10028"
    },
    "image": "https://www.metmuseum.org/picasso.jpg",
    "description": "A retrospective of Picasso's work.",
    "offers": {
        "@type": "Offer",
        "price": "25",
        "priceCurrency": "USD"
    }
}
</script>
</head>
<body></body>
</html>
"""

SAMPLE_HTML_LIST = """
<html><head>
<script type="application/ld+json">
[
    {"@type": "Event", "name": "Show A", "startDate": "2026-07-01", "url": "https://example.com/a"},
    {"@type": "Event", "name": "Show B", "startDate": "2026-07-02", "url": "https://example.com/b"}
]
</script>
</head><body></body></html>
"""


def test_jsonld_parses_single_event():
    source = {
        "id": "met-museum",
        "url": "https://www.metmuseum.org/exhibitions",
        "category": "museum",
    }
    scraper = JsonLdScraper(source)
    events = scraper.parse_jsonld(SAMPLE_HTML)

    assert len(events) == 1
    e = events[0]
    assert e.title == "Picasso Exhibition"
    assert e.start_date == "2026-07-01"
    assert e.start_time == "10:00"
    assert e.end_date == "2026-10-15"
    assert e.venue == "The Metropolitan Museum of Art"
    assert e.address == "1000 Fifth Avenue, New York, NY 10028"
    assert e.image_url == "https://www.metmuseum.org/picasso.jpg"
    assert e.description == "A retrospective of Picasso's work."
    assert e.source_id == "met-museum"


def test_jsonld_parses_list():
    source = {"id": "test", "url": "https://example.com", "category": "museum"}
    scraper = JsonLdScraper(source)
    events = scraper.parse_jsonld(SAMPLE_HTML_LIST)
    assert len(events) == 2
    assert events[0].title == "Show A"
    assert events[1].title == "Show B"


def test_jsonld_no_events():
    html = "<html><head></head><body>No events here</body></html>"
    source = {"id": "test", "url": "https://example.com", "category": "museum"}
    scraper = JsonLdScraper(source)
    events = scraper.parse_jsonld(html)
    assert events == []


def test_jsonld_extracts_price():
    source = {
        "id": "met-museum",
        "url": "https://www.metmuseum.org/exhibitions",
        "category": "museum",
    }
    scraper = JsonLdScraper(source)
    events = scraper.parse_jsonld(SAMPLE_HTML)
    assert events[0].price_range == "$25"
    assert events[0].is_free is False
