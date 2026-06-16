from scraper.models import Event


def test_event_from_dict():
    data = {
        "source_id": "lincoln-center",
        "title": "A Midsummer Night's Dream",
        "url": "https://www.lincolncenter.org/event/123",
        "start_date": "2026-06-20",
    }
    event = Event.from_dict(data)
    assert event.source_id == "lincoln-center"
    assert event.title == "A Midsummer Night's Dream"
    assert event.start_date == "2026-06-20"
    assert event.id == "lincoln-center-2026-06-20-a-midsummer-nights-dream"


def test_event_to_dict_roundtrip():
    data = {
        "source_id": "met-museum",
        "title": "Ancient Egypt Reimagined",
        "url": "https://www.metmuseum.org/exhibitions/123",
        "start_date": "2026-07-01",
        "end_date": "2026-10-15",
        "category": "museum",
        "is_free": False,
        "price_range": "$25-$30",
    }
    event = Event.from_dict(data)
    result = event.to_dict()
    assert result["id"] == "met-museum-2026-07-01-ancient-egypt-reimagined"
    assert result["source_id"] == "met-museum"
    assert result["title"] == "Ancient Egypt Reimagined"
    assert result["start_date"] == "2026-07-01"
    assert result["end_date"] == "2026-10-15"
    assert result["is_free"] is False
    assert result["price_range"] == "$25-$30"
    assert "last_updated" in result


def test_event_id_is_deterministic():
    data = {
        "source_id": "moma",
        "title": "Starry Night & Friends!",
        "url": "https://www.moma.org/event/1",
        "start_date": "2026-08-01",
    }
    e1 = Event.from_dict(data)
    e2 = Event.from_dict(data)
    assert e1.id == e2.id
    assert e1.id == "moma-2026-08-01-starry-night-friends"


def test_event_defaults():
    data = {
        "source_id": "whitney",
        "title": "Some Show",
        "url": "https://whitney.org/1",
        "start_date": "2026-06-01",
    }
    event = Event.from_dict(data)
    d = event.to_dict()
    assert d["description"] is None
    assert d["image_url"] is None
    assert d["venue"] is None
    assert d["address"] is None
    assert d["category"] is None
    assert d["tags"] == []
    assert d["end_date"] is None
    assert d["start_time"] is None
    assert d["end_time"] is None
    assert d["is_free"] is None
    assert d["price_range"] is None
