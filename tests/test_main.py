import json
import os
from unittest.mock import patch, MagicMock
from scraper.main import load_sources, get_scraper, run_all


def test_load_sources():
    sources = load_sources()
    assert isinstance(sources, list)
    assert len(sources) > 0
    assert all("id" in s for s in sources)
    assert all("scraper" in s for s in sources)


def test_get_scraper_ical():
    source = {"id": "test", "url": "http://example.com", "scraper": "ical_generic", "category": "museum"}
    scraper = get_scraper(source)
    from scraper.scrapers.ical_generic import ICalScraper
    assert isinstance(scraper, ICalScraper)


def test_get_scraper_jsonld():
    source = {"id": "test", "url": "http://example.com", "scraper": "jsonld_generic", "category": "museum"}
    scraper = get_scraper(source)
    from scraper.scrapers.jsonld_generic import JsonLdScraper
    assert isinstance(scraper, JsonLdScraper)


def test_get_scraper_html():
    source = {"id": "test", "url": "http://example.com", "scraper": "html_generic", "category": "museum", "selectors": {}}
    scraper = get_scraper(source)
    from scraper.scrapers.html_generic import HtmlScraper
    assert isinstance(scraper, HtmlScraper)


def test_run_all_writes_output(tmp_path):
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "sources").mkdir()

    fake_sources = [
        {"id": "test-source", "url": "http://example.com", "scraper": "jsonld_generic", "category": "museum", "favicon_url": None}
    ]
    fake_event = MagicMock()
    fake_event.to_dict.return_value = {
        "id": "test-source-2026-07-01-show",
        "source_id": "test-source",
        "title": "Show",
        "start_date": "2026-07-01",
    }

    with patch("scraper.main.load_sources", return_value=fake_sources), \
         patch("scraper.main.get_scraper") as mock_get, \
         patch("scraper.main.resolve_favicon_url", return_value="https://example.com/favicon.ico"), \
         patch("scraper.main.DATA_DIR", str(data_dir)), \
         patch("scraper.main.SOURCES_JSON", str(tmp_path / "sources.json")):
        mock_scraper = MagicMock()
        mock_scraper.scrape.return_value = [fake_event]
        mock_get.return_value = mock_scraper

        (tmp_path / "sources.json").write_text(json.dumps({"sources": fake_sources}))
        run_all()

    assert (data_dir / "events.json").exists()
    assert (data_dir / "events-upcoming.json").exists()
    assert (data_dir / "events-past.json").exists()
