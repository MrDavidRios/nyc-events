from scraper.utils.favicon import resolve_favicon_url, _extract_favicon_from_html


def test_extract_link_rel_icon():
    html = '<html><head><link rel="icon" href="/favicon.png"></head></html>'
    assert _extract_favicon_from_html(html, "https://example.com") == "https://example.com/favicon.png"


def test_extract_apple_touch_icon():
    html = '<html><head><link rel="apple-touch-icon" href="/apple-icon.png"></head></html>'
    assert _extract_favicon_from_html(html, "https://example.com") == "https://example.com/apple-icon.png"


def test_extract_absolute_url():
    html = '<html><head><link rel="icon" href="https://cdn.example.com/icon.png"></head></html>'
    assert _extract_favicon_from_html(html, "https://example.com") == "https://cdn.example.com/icon.png"


def test_extract_no_favicon():
    html = "<html><head><title>No icon</title></head></html>"
    assert _extract_favicon_from_html(html, "https://example.com") is None


def test_extract_prefers_apple_touch_icon():
    html = """<html><head>
        <link rel="icon" href="/small.ico">
        <link rel="apple-touch-icon" href="/apple.png">
    </head></html>"""
    assert _extract_favicon_from_html(html, "https://example.com") == "https://example.com/apple.png"
