import json
import logging
import os
import sys

from scraper.scrapers.base import BaseScraper
from scraper.scrapers.ical_generic import ICalScraper
from scraper.scrapers.jsonld_generic import JsonLdScraper
from scraper.scrapers.html_generic import HtmlScraper
from scraper.scrapers.api_guggenheim import GuggenheimScraper
from scraper.utils.favicon import resolve_favicon_url
from scraper.utils.merge import merge_sources, write_output_files

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

SCRAPER_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCES_JSON = os.path.join(SCRAPER_DIR, "sources.json")
DATA_DIR = os.path.join(os.path.dirname(SCRAPER_DIR), "data")

SCRAPER_MAP: dict[str, type[BaseScraper]] = {
    "ical_generic": ICalScraper,
    "jsonld_generic": JsonLdScraper,
    "html_generic": HtmlScraper,
    "html_nyc_parks": HtmlScraper,
    "api_guggenheim": GuggenheimScraper,
}


def load_sources() -> list[dict]:
    with open(SOURCES_JSON) as f:
        return json.load(f)["sources"]


def get_scraper(source: dict) -> BaseScraper:
    scraper_name = source["scraper"]
    scraper_cls = SCRAPER_MAP.get(scraper_name)
    if not scraper_cls:
        raise ValueError(f"Unknown scraper: {scraper_name}")
    return scraper_cls(source)


def run_all() -> None:
    sources = load_sources()
    sources_dir = os.path.join(DATA_DIR, "sources")
    os.makedirs(sources_dir, exist_ok=True)

    updated_favicons: dict[str, str | None] = {}
    succeeded = 0
    failed = 0

    for source in sources:
        if not source.get("enabled", True):
            log.info(f"Skipping {source.get('name', source['id'])} (disabled)")
            continue

        source_id = source["id"]
        log.info(f"Scraping {source.get('name', source_id)} ({source_id})...")
        try:
            scraper = get_scraper(source)
            events = scraper.scrape()
            event_dicts = [e.to_dict() for e in events]

            output_path = os.path.join(sources_dir, f"{source_id}.json")
            with open(output_path, "w") as f:
                json.dump(event_dicts, f, indent=2)

            log.info(f"  -> {len(events)} events")
            succeeded += 1
        except Exception as e:
            log.error(f"  -> FAILED: {e}")
            failed += 1

        try:
            favicon = resolve_favicon_url(source["url"])
            updated_favicons[source_id] = favicon
        except Exception:
            updated_favicons[source_id] = source.get("favicon_url")

    # Update favicon URLs in sources.json
    with open(SOURCES_JSON) as f:
        sources_data = json.load(f)
    for s in sources_data["sources"]:
        if s["id"] in updated_favicons:
            s["favicon_url"] = updated_favicons[s["id"]]
    with open(SOURCES_JSON, "w") as f:
        json.dump(sources_data, f, indent=2)

    # Merge and write output files
    all_events = merge_sources(sources_dir)
    write_output_files(all_events, DATA_DIR)

    log.info(f"Done: {succeeded} succeeded, {failed} failed, {len(all_events)} total events")


if __name__ == "__main__":
    run_all()
