import re
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text


@dataclass
class Event:
    source_id: str
    title: str
    url: str
    start_date: str
    id: str = ""
    description: str | None = None
    image_url: str | None = None
    venue: str | None = None
    address: str | None = None
    category: str | None = None
    tags: list[str] = field(default_factory=list)
    end_date: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    is_free: bool | None = None
    price_range: str | None = None
    last_updated: str = ""

    def __post_init__(self):
        if not self.id:
            slug = _slugify(self.title)
            self.id = f"{self.source_id}-{self.start_date}-{slug}"
        if not self.last_updated:
            self.last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "image_url": self.image_url,
            "venue": self.venue,
            "address": self.address,
            "category": self.category,
            "tags": self.tags,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "is_free": self.is_free,
            "price_range": self.price_range,
            "last_updated": self.last_updated,
        }
