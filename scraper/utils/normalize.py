import re
from datetime import datetime
from html import unescape


def normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def normalize_time(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    for fmt in ("%H:%M", "%I:%M %p", "%I:%M%p", "%I %p"):
        try:
            return datetime.strptime(value, fmt).strftime("%H:%M")
        except ValueError:
            continue
    return None


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = unescape(value)
    value = re.sub(r"\s+", " ", value).strip()
    return value
