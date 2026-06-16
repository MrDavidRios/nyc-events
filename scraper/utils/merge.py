import json
import os
from datetime import date


def merge_sources(source_dir: str) -> list[dict]:
    seen: dict[str, dict] = {}
    for filename in sorted(os.listdir(source_dir)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(source_dir, filename)
        with open(filepath) as f:
            events = json.load(f)
        for event in events:
            seen[event["id"]] = event
    return sorted(seen.values(), key=lambda e: e.get("start_date", ""))


def write_output_files(events: list[dict], output_dir: str) -> None:
    today = date.today().isoformat()

    upcoming = [e for e in events if e.get("start_date", "") >= today]
    past = [e for e in events if e.get("start_date", "") < today]

    os.makedirs(output_dir, exist_ok=True)
    for filename, data in [
        ("events.json", events),
        ("events-upcoming.json", upcoming),
        ("events-past.json", past),
    ]:
        with open(os.path.join(output_dir, filename), "w") as f:
            json.dump(data, f, indent=2)
