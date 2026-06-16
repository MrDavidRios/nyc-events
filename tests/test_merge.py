import json
import os
from scraper.utils.merge import merge_sources, write_output_files


def test_merge_deduplicates_by_id(tmp_path):
    source_dir = tmp_path / "sources"
    source_dir.mkdir()

    events_a = [
        {"id": "a-2026-06-01-show", "source_id": "a", "title": "Show", "start_date": "2026-06-01"},
        {"id": "a-2026-06-02-gig", "source_id": "a", "title": "Gig", "start_date": "2026-06-02"},
    ]
    events_b = [
        {"id": "a-2026-06-01-show", "source_id": "a", "title": "Show (updated)", "start_date": "2026-06-01"},
        {"id": "b-2026-06-03-fest", "source_id": "b", "title": "Fest", "start_date": "2026-06-03"},
    ]

    (source_dir / "a.json").write_text(json.dumps(events_a))
    (source_dir / "b.json").write_text(json.dumps(events_b))

    merged = merge_sources(str(source_dir))
    ids = [e["id"] for e in merged]
    assert len(merged) == 3
    assert ids.count("a-2026-06-01-show") == 1


def test_write_output_files_splits_by_date(tmp_path):
    events = [
        {"id": "past", "start_date": "2020-01-01"},
        {"id": "future", "start_date": "2099-12-31"},
    ]
    write_output_files(events, str(tmp_path))

    all_events = json.loads((tmp_path / "events.json").read_text())
    upcoming = json.loads((tmp_path / "events-upcoming.json").read_text())
    past = json.loads((tmp_path / "events-past.json").read_text())

    assert len(all_events) == 2
    assert len(upcoming) == 1
    assert upcoming[0]["id"] == "future"
    assert len(past) == 1
    assert past[0]["id"] == "past"


def test_merge_empty_directory(tmp_path):
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    merged = merge_sources(str(source_dir))
    assert merged == []
