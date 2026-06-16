from scraper.utils.normalize import normalize_date, normalize_time, clean_text


def test_normalize_date_iso():
    assert normalize_date("2026-06-20") == "2026-06-20"


def test_normalize_date_american():
    assert normalize_date("06/20/2026") == "2026-06-20"


def test_normalize_date_written():
    assert normalize_date("June 20, 2026") == "2026-06-20"


def test_normalize_date_none():
    assert normalize_date(None) is None
    assert normalize_date("") is None


def test_normalize_time_24h():
    assert normalize_time("19:30") == "19:30"


def test_normalize_time_12h():
    assert normalize_time("7:30 PM") == "19:30"


def test_normalize_time_noon():
    assert normalize_time("12:00 PM") == "12:00"


def test_normalize_time_none():
    assert normalize_time(None) is None
    assert normalize_time("") is None


def test_clean_text_whitespace():
    assert clean_text("  hello   world  ") == "hello world"


def test_clean_text_html_entities():
    assert clean_text("rock &amp; roll") == "rock & roll"


def test_clean_text_none():
    assert clean_text(None) is None
