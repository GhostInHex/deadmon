"""MLH adapter: the code that knows one platform's payload.

The season page embeds its event catalogue as JSON: `upcomingEvents` and
`pastEvents` arrays carrying each event's name, slug, status, tz-aware
event bounds (`startsAt`/`endsAt`), format (`physical` / `digital`) and
the event's own website URL.

The website URL is the source URL — it is where registration happens.
Event bounds are *not* registration closes, so registration close stays
absent even though the dates are precise: calling an event's end its
registration close would be a guess, and verification fails closed on it.
Format maps directly onto deadmon's modes: `digital` is online,
`physical` is venue-only, i.e. `offline`.
"""
from __future__ import annotations

from collections.abc import Iterable
from html import unescape
from pathlib import Path
import json
import re

from ..candidate import make_candidate
from ..scraper import Scraper

_EVENT_ARRAY = re.compile(r'"(upcomingEvents|pastEvents)":\[')

_MODES = {"digital": "online", "physical": "offline"}


class MlhScraper(Scraper):
    """One crawl run's worth of MLH's season catalogue."""

    name = "mlh"

    def fetch(self, source: Path | str) -> bytes:
        """Read the recorded payload. No transport in Slice 2."""
        path = Path(source)
        if path.suffix.lower() in {".html"} and path.exists():
            return path.read_bytes()
        raise FileNotFoundError(
            f"MLH adapter replays a recorded HTML payload, got {source!r}"
        )

    def extract(self, payload: bytes) -> Iterable:
        page = payload.decode("utf-8")
        for event in _events(page):
            title = unescape(event.get("name", "")).strip()
            url = (event.get("websiteUrl") or "").strip()
            if not title or not url:
                continue
            yield make_candidate(
                title=title,
                source_url=url,
                registration_close=None,
                mode=_MODES.get(event.get("formatType", "")),
                crawler=self.name,
            )

    # -- extraction rules -------------------------------------------------


def _events(page: str) -> list[dict]:
    """Event objects from the embedded catalogue arrays, in page order."""
    events = []
    for match in _EVENT_ARRAY.finditer(page):
        array, end = _balanced_array(page, match.end() - 1)
        if array is None:
            continue
        try:
            events.extend(json.loads(array))
        except ValueError:
            continue
    return [e for e in events if isinstance(e, dict)]


def _balanced_array(page: str, start: int) -> tuple[str | None, int]:
    """The `[...]` JSON array starting at `start`, honouring strings."""
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(page)):
        char = page[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return page[start : index + 1], index + 1
    return None, start
