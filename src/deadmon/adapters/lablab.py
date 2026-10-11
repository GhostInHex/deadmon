"""lablab.ai adapter: the code that knows one platform's payload.

The events page is a Next.js page with two independent structures that
agree: a JSON-LD `ItemList` carries every event's title and canonical URL,
and one card per event carries its status badge (LIVE / Finished /
Register), its mode badge (Online / Hybrid / On-site) and its build-window
dates ("SEP 1 - DEC 15", no year, no timezone).

Titles and URLs come from the JSON-LD — the platform's own structured
data, parsed as JSON rather than scraped from markup. Status and mode come
from each card, segmented on the card link, which appears exactly once per
event. Build-window dates are event bounds, not registration closes, and
carry neither year nor timezone, so registration close stays absent:
verification fails closed on every record.

Mode mapping is the one judgment call: Online and Hybrid are the
platform's own words; On-site means venue-only, which is `offline` in
deadmon's taxonomy.
"""
from __future__ import annotations

from collections.abc import Iterable
from html import unescape
from pathlib import Path
import json
import re

from ..candidate import make_candidate
from ..scraper import Scraper

_CARD_LINK = re.compile(r'href="(/ai-hackathons/[^"]*)"')
_LD_JSON = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
_BADGE = re.compile(r"(LIVE|Finished|Register|Online|Hybrid|On-site)</span>")

_MODES = {"Online": "online", "Hybrid": "hybrid", "On-site": "offline"}


class LablabScraper(Scraper):
    """One crawl run's worth of lablab.ai's AI-hackathons grid."""

    name = "lablab"

    def fetch(self, source: Path | str) -> bytes:
        """Read the recorded payload. No transport in Slice 2."""
        path = Path(source)
        if path.suffix.lower() in {".html"} and path.exists():
            return path.read_bytes()
        raise FileNotFoundError(
            f"lablab adapter replays a recorded HTML payload, got {source!r}"
        )

    def extract(self, payload: bytes) -> Iterable:
        page = payload.decode("utf-8")
        events = _item_list(page)
        cards = _cards(page)
        seen = set()
        for title, url in events:
            title = unescape(title).strip()
            # The JSON-LD repeats the list; the first occurrence wins.
            if not title or url in seen:
                continue
            seen.add(url)
            yield make_candidate(
                title=title,
                source_url=url,
                registration_close=None,
                mode=_mode(cards.get(url, "")),
                crawler=self.name,
            )

    # -- extraction rules -------------------------------------------------


def _item_list(page: str) -> list[tuple[str, str]]:
    """(title, url) pairs from the page's own JSON-LD ItemList, in order."""
    for block in _LD_JSON.findall(page):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        graph = data if isinstance(data, list) else data.get("@graph", [])
        for node in graph:
            if node.get("@type") == "ItemList":
                return [
                    (item["name"], item["url"])
                    for item in node.get("itemListElement", [])
                    if item.get("name") and item.get("url")
                ]
    return []


def _cards(page: str) -> dict[str, str]:
    """Map card URL to the card's raw markup, segmented on the card link."""
    links = [(m.group(1), m.start()) for m in _CARD_LINK.finditer(page)]
    cards = {}
    for index, (href, start) in enumerate(links):
        end = links[index + 1][1] if index + 1 < len(links) else len(page)
        # The JSON-LD block repeats every URL once; only chunks containing a
        # status badge are real cards.
        chunk = page[start:end]
        if "Finished</span>" in chunk or "LIVE</span>" in chunk or "Register</span>" in chunk:
            cards["https://lablab.ai" + href] = chunk
    return cards


def _mode(chunk: str) -> str | None:
    """The mode badge, if the card states one."""
    for badge in _BADGE.findall(chunk):
        if badge in _MODES:
            return _MODES[badge]
    return None
