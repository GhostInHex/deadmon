"""HackerRank adapter: the code that knows one platform's payload.

The contests index is server-rendered: promoted carousel cards, one active
card, upcoming cards and archived cards are all in the initial HTML. A card
carries its event URL (`data-attr1` on promoted/upcoming cards) or a contest
slug (`data-attr1` on active/archived cards), resolved against the contests
index. The carousel repeats every promoted card twice, so records dedupe on
(title, source URL).

Dates on the page are day-month with no year and no timezone
("Registrations open till 30th October"), so registration close stays
absent: verification fails closed on it. The archived "Event ended on ..."
dates carry a year but still no timezone, so they stay absent too — a naive
datetime is not a fact about when registration closed. The page states no
per-contest mode, so mode stays absent as well. Every HackerRank record
therefore verifies `unverified`: watched and linked, never a feed card.
"""
from __future__ import annotations

from collections.abc import Iterable
from html import unescape
from pathlib import Path
import re

from ..candidate import make_candidate
from ..scraper import Scraper

BASE = "https://www.hackerrank.com"
CONTEST_URL = BASE + "/contests/{}"

# Only the card `<div>` carries the title that follows it; the Register
# `<button>` repeats the same URL *after* its card's title, so matching it
# would pair the URL with the next card's title.
_PROMOTED_URL = re.compile(r'data-attr1="([^"]+)"')
_PROMOTED_TITLE = re.compile(r'promoted-contest-v2__name" title="([^"]+)"')
_UPCOMING = re.compile(r'ContestUpcomingCard" data-attr1="([^"]+)"[^>]*>\s*([^<>]+)')
_CONTEST_SLUG = re.compile(r'data-attr1="([A-Za-z0-9-]+)"')
_CONTEST_TITLE = re.compile(r'contest-item__heading[^>]*>([^<]+)</h4>')
_NEXT_CARD = re.compile(r'<div[^>]*data-analytics="Contest\w+"[^>]*>')


def _cards(page: str, analytics: str, url_pat, title_pat):
    """(url, title) pairs, one per card div.

    The split keeps each card's opening div beside its body, and the body is
    cut at the next card — so a title can never leak in from a neighbour,
    which is what a fixed-width forward window gets wrong on repeated slugs.
    """
    parts = re.split('(<div[^>]*data-analytics="%s"[^>]*>)' % analytics, page)
    for index in range(1, len(parts), 2):
        opening = parts[index]
        body = parts[index + 1] if index + 1 < len(parts) else ""
        body = _NEXT_CARD.split(body, maxsplit=1)[0]
        url = url_pat.search(opening)
        title = title_pat.search(body)
        if url and title:
            yield url.group(1), title.group(1)


class HackerRankScraper(Scraper):
    """One crawl run's worth of HackerRank's contests index."""

    name = "hackerrank"

    def fetch(self, source: Path | str) -> bytes:
        """Read the recorded payload. No transport in Slice 2."""
        path = Path(source)
        if path.suffix.lower() in {".html"} and path.exists():
            return path.read_bytes()
        raise FileNotFoundError(
            f"HackerRank adapter replays a recorded HTML payload, got {source!r}"
        )

    def extract(self, payload: bytes) -> Iterable:
        page = payload.decode("utf-8")
        seen = set()
        for title, url in self._records(page):
            title = unescape(title).strip()
            if not title or (title, url) in seen:
                continue
            seen.add((title, url))
            yield make_candidate(
                title=title,
                source_url=url,
                registration_close=None,
                mode=None,
                crawler=self.name,
            )

    # -- extraction rules -------------------------------------------------

    def _records(self, page: str):
        """(title, url) pairs in page order: promoted, upcoming, contest cards."""
        for url, title in _cards(page, "ContestPromoted", _PROMOTED_URL, _PROMOTED_TITLE):
            yield title, url
        for match in _UPCOMING.finditer(page):
            yield match.group(2), match.group(1)
        for slug, title in _cards(page, "ContestCardSignupLink", _CONTEST_SLUG, _CONTEST_TITLE):
            yield title, CONTEST_URL.format(slug)
