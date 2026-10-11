"""GenAI.works adapter: the code that knows one platform's payload.

The homepage carries its featured hackathon as a server-rendered card: the
title and event path on the card link, the event window on the meta line
("Oct 22, 2026 – Oct 27, 2026") and the registration close on the facts
rail ("Closes Oct 22, 23:59 UTC").

The close value carries no year of its own; the year comes from the same
card's event window — same event, same card, read together, not guessed.
Combined with the UTC marker that yields a tz-aware close, which is what
verification needs. The card states no mode (online, venue or hybrid), so
mode stays absent: a future close with no mode verifies `unverified`,
never `live`.
"""
from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
import re

from ..candidate import make_candidate
from ..scraper import Scraper

BASE = "https://hackathon.genai.works"

_CARD = re.compile(r'lpHackCardLink" href="([^"]+)">([^<]+)</a>')
_WINDOW = re.compile(
    r"lpHackFeatMetaItem\">([A-Za-z]{3} \d{1,2}, (\d{4})) [–-] ([A-Za-z]{3} \d{1,2}, \d{4})"
)
_CLOSE = re.compile(r"lpHackRailFactValue\">([A-Za-z]{3} \d{1,2}), (\d{1,2}):(\d{2}) (UTC)")


class GenaiWorksScraper(Scraper):
    """One crawl run's worth of GenAI.works' featured hackathon."""

    name = "genai-works"

    def fetch(self, source: Path | str) -> bytes:
        """Read the recorded payload. No transport in Slice 2."""
        path = Path(source)
        if path.suffix.lower() in {".html"} and path.exists():
            return path.read_bytes()
        raise FileNotFoundError(
            f"GenAI.works adapter replays a recorded HTML payload, got {source!r}"
        )

    def extract(self, payload: bytes) -> Iterable:
        page = payload.decode("utf-8")
        card = _CARD.search(page)
        window = _WINDOW.search(page)
        close = _CLOSE.search(page)
        if not card:
            return
        title = unescape(card.group(2)).strip()
        if not title:
            return
        yield make_candidate(
            title=title,
            source_url=_absolute(card.group(1)),
            registration_close=_close(window, close),
            mode=None,
            crawler=self.name,
        )

    # -- extraction rules -------------------------------------------------


def _absolute(href: str) -> str:
    href = href.strip()
    if href.startswith("http"):
        return href
    return BASE + (href if href.startswith("/") else "/" + href)


def _close(window, close) -> datetime | None:
    """The rail's close, year-qualified by the same card's event window.

    The zone is read, not assumed: anything that is not literally UTC stays
    absent, because a naive close verifies `unverified` by rule.
    """
    if not window or not close or close.group(4) != "UTC":
        return None
    try:
        naive = datetime.strptime(
            f"{close.group(1)}, {window.group(2)} {close.group(2)}:{close.group(3)}",
            "%b %d, %Y %H:%M",
        )
    except ValueError:
        return None
    return naive.replace(tzinfo=timezone.utc)
