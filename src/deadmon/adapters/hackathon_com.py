"""hackathon.com adapter: the code that knows one platform's payload.

The homepage carries the upcoming grid server-rendered: one `div.hero` card
per event with the title and event URL on `a.hero__title`, the mode on the
location link (Online / Virtual / Hybrid), and start/end day-month pairs
with no year and no timezone.

Day-month without a year is not a fact about when registration closes, so
registration close (and registration open) stay absent: verification fails
closed on every record. Mode is the one thing the page states outright, so
it is mapped; anything unrecognised stays absent rather than defaulted.
"""
from __future__ import annotations

from collections.abc import Iterable
from html import unescape
from pathlib import Path
import re

from ..candidate import make_candidate
from ..scraper import Scraper

BASE = "https://hackathon.com"

_TITLE = re.compile(r'hero__title[^>]*href="([^"]+)"[^>]*>([^<]+)</a>')
_LOCATION = re.compile(r"hero__key-info__location.*?<\s*a [^>]*>([^<>]+)</a>", re.S)


class HackathonComScraper(Scraper):
    """One crawl run's worth of hackathon.com's upcoming grid."""

    name = "hackathon-com"

    def fetch(self, source: Path | str) -> bytes:
        """Read the recorded payload. No transport in Slice 2."""
        path = Path(source)
        if path.suffix.lower() in {".html"} and path.exists():
            return path.read_bytes()
        raise FileNotFoundError(
            f"hackathon.com adapter replays a recorded HTML payload, got {source!r}"
        )

    def extract(self, payload: bytes) -> Iterable:
        page = payload.decode("utf-8")
        # The first card carries the `active` class and quoted attributes;
        # the rest are bare `<div class=hero>`. Both shapes are one event.
        cards = re.split(r'<div class=(?:"hero active"|hero)>', page)
        for card in cards[1:]:
            record = self._extract_card(card)
            if record is not None:
                yield record

    # -- extraction rules -------------------------------------------------

    def _extract_card(self, card: str):
        title = _TITLE.search(card)
        if not title:
            return None
        location = _LOCATION.search(card)
        return make_candidate(
            title=unescape(title.group(2)).strip(),
            source_url=_absolute(title.group(1)),
            registration_close=None,
            mode=_mode(location.group(1)) if location else None,
            crawler=self.name,
        )


def _absolute(href: str) -> str:
    href = href.strip()
    if href.startswith("http"):
        return href
    return BASE + (href if href.startswith("/") else "/" + href)


def _mode(location: str) -> str | None:
    """Online and Virtual are both remote-first; Hybrid mixes remote and venue."""
    text = location.strip().lower()
    if "hybrid" in text:
        return "hybrid"
    if "online" in text or "virtual" in text:
        return "online"
    return None
