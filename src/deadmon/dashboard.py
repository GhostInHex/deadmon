"""Dashboard: one server-rendered page, two groups.

A page is assembled from rows by `build_view()` / `cards_from_rows()` and
emitted as HTML by `render_page()` — both pure functions, so the page renders
from seeded rows with no fetch over the network and no single-page-application
framework.

The two groups are ADR-0007: the **feed** holds every card with a live source,
**needs attention** holds the rest, and a closed listing appears in neither.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import html
from pathlib import Path

from .storage import Store
from .tracing import TraceClient
from .verdict import CLOSED, LIVE, UNVERIFIED

DEFAULT_SINK_DIR = Path(".runs/traces")

# Stored dates are UTC (ADR-0013). Slice 1 has no subscriber timezone yet, so
# every date is rendered with an explicit zone label rather than bare.
DISPLAY_ZONE = timezone.utc
DISPLAY_LABEL = "UTC"


@dataclass(frozen=True)
class CardSource:
    crawler: str
    source_url: str
    stated_close: str | None
    verdict: str
    verified_at: str


@dataclass(frozen=True)
class Card:
    title: str
    earliest_credible_close: str | None
    sources: tuple[CardSource, ...]

    @property
    def live(self) -> bool:
        return any(source.verdict == LIVE for source in self.sources)


@dataclass(frozen=True)
class View:
    feed: tuple[Card, ...]
    needs_attention: tuple[Card, ...]
    runs: tuple[dict, ...]

    @property
    def feed_count(self) -> int:
        return len(self.feed)


def build_view(cards, runs) -> View:
    """Split the cards into the feed and needs attention.

    Closed listings appear in neither group, and an unverified record is never
    counted in a feed count (ADR-0007).
    """
    feed: list[Card] = []
    attention: list[Card] = []
    for card in cards:
        verdicts = {source.verdict for source in card.sources}
        if LIVE in verdicts:
            feed.append(card)
        elif UNVERIFIED in verdicts:
            attention.append(card)
        # else: closed only — no group; the row survives in storage
    feed.sort(key=lambda card: (card.earliest_credible_close is None, card.earliest_credible_close or ""))
    attention.sort(key=lambda card: card.title)
    return View(feed=tuple(feed), needs_attention=tuple(attention), runs=tuple(runs))


def cards_from_rows(rows) -> list[Card]:
    """Turn stored source rows into cards (ADR-0010: one card per hackathon).

    A hackathon with one source still collapses to a single row, but the card
    is a view over sources rather than a listing row.
    """
    grouped: dict[int, list[CardSource]] = {}
    titles: dict[int, str] = {}
    for row in rows:
        grouped.setdefault(row["hackathon_id"], []).append(
            CardSource(
                crawler=row["crawler"],
                source_url=row["source_url"],
                stated_close=row["registration_close"],
                verdict=row["verdict"],
                verified_at=row["verified_at"],
            )
        )
        titles[row["hackathon_id"]] = row["hackathon_title"]
    return [
        Card(
            title=titles[hackathon_id],
            earliest_credible_close=earliest_credible_close(grouped[hackathon_id]),
            sources=tuple(grouped[hackathon_id]),
        )
        for hackathon_id in sorted(grouped)
    ]


def earliest_credible_close(sources) -> str | None:
    """The earliest date read from a source that verified and parsed (ADR-0009).

    Only a source that verified contributes: a closed source's date is evidence
    it was credible once but is not a live claim now, and an unverified source
    never had a parseable date at all. No contributing source means no credible
    date — never a fallback.
    """
    parsed = []
    for source in sources:
        if source.verdict != LIVE or not source.stated_close:
            continue
        try:
            parsed.append((datetime.fromisoformat(source.stated_close), source.stated_close))
        except (TypeError, ValueError):
            continue
    return min(parsed, key=lambda pair: pair[0])[1] if parsed else None


def needs_attention_by_crawler(view: View) -> dict[str, int]:
    """The operator's blocked-platform signal: a count per crawler."""
    counts: dict[str, int] = {}
    for card in view.needs_attention:
        for source in card.sources:
            if source.verdict == UNVERIFIED:
                counts[source.crawler] = counts.get(source.crawler, 0) + 1
    return counts


def render_page(view: View, *, title: str = "deadmon") -> str:
    """One server-rendered page. Two groups; badges read the verdict word."""
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            f"<title>{html.escape(title)}</title>",
            "<style>",
            _CSS,
            "</style>",
            "</head>",
            "<body>",
            "<h1>deadmon</h1>",
            _summary(view),
            _feed(view),
            _needs_attention(view),
            _run_history(view),
            "</body>",
            "</html>",
        ]
    )


def render_trace(reference: str, trace=None, *, sink_dir: Path | None = None) -> str:
    """The detail page one dashboard link opens."""
    directory = Path(sink_dir) if sink_dir else DEFAULT_SINK_DIR
    stored = trace if trace is not None else TraceClient.load(reference, sink_dir=directory)
    body = [f"<h1>Trace <code>{html.escape(reference)}</code></h1>", '<p><a href="/">&larr; dashboard</a></p>']
    if stored is None:
        body.append("<p>No trace document is stored for this run.</p>")
    else:
        body.extend(
            [
                "<p>crawler <strong>%s</strong></p>" % html.escape(stored.crawler),
                "<p>backend <strong>%s</strong></p>" % html.escape(stored.backend),
                "<p>tokens <strong>%d</strong> &middot; cost <strong>$%.6f</strong></p>"
                % (stored.token_usage, stored.cost_usd),
                "<table><thead><tr><th>span</th><th>duration (ms)</th></tr></thead><tbody>",
            ]
        )
        body.extend(
            "<tr><td>%s</td><td>%s</td></tr>" % (html.escape(span.name), span.duration_ms)
            for span in stored.spans
        )
        body.append("</tbody></table>")
        if stored.error:
            body.append("<p class='badge unverified'>%s</p>" % html.escape(stored.error))
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            "<title>trace</title>",
            "<style>",
            _CSS,
            "</style>",
            "</head>",
            "<body>",
            *body,
            "</body>",
            "</html>",
        ]
    )


def format_instant(value) -> str:
    """Every date carries a visible zone label (ADR-0013)."""
    if not value:
        return "—"
    try:
        moment = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return html.escape(str(value))
    if moment.tzinfo is None:
        return html.escape(f"{moment.strftime('%Y-%m-%d %H:%M')} (zone unknown)")
    return moment.astimezone(DISPLAY_ZONE).strftime("%Y-%m-%d %H:%M") + " " + DISPLAY_LABEL


def _summary(view: View) -> str:
    needs = needs_attention_by_crawler(view)
    badges = " ".join(
        "<span class='badge unverified'>%s: %d</span>" % (html.escape(crawler), count)
        for crawler, count in sorted(needs.items())
    )
    return (
        "<p class='summary'>%d card(s) in the feed &middot; %d card(s) needing attention%s</p>"
        % (view.feed_count, len(view.needs_attention), (" &middot; " + badges) if badges else "")
    )


def _feed(view: View) -> str:
    cards = [
        "<article class='card'>"
        "<h2>%s</h2>"
        "<p class='close'>registration close <time>%s</time></p>%s</article>"
        % (
            html.escape(card.title),
            html.escape(format_instant(card.earliest_credible_close)),
            _sources(card),
        )
        for card in view.feed
    ]
    if not cards:
        cards.append("<p class='empty'>Nothing in the feed.</p>")
    return "<section><h2>Feed</h2>%s</section>" % "".join(cards)


def _needs_attention(view: View) -> str:
    cards = [
        "<article class='card greyed'>"
        "<h2>%s</h2>"
        "<p class='close'>no credible registration close &middot; unverified</p>%s</article>"
        % (html.escape(card.title), _sources(card))
        for card in view.needs_attention
    ]
    if not cards:
        cards.append("<p class='empty'>Nothing needs attention.</p>")
    return "<section><h2>Needs attention</h2>%s</section>" % "".join(cards)


def _sources(card: Card) -> str:
    cells = [
        "<li class='source'>"
        "<a href='%s' rel='nofollow'>%s</a>"
        "<span class='badge %s'>%s</span>"
        "<span class='stated'>stated close %s</span>"
        "<span class='verified'>verified %s</span>"
        "</li>"
        % (
            html.escape(source.source_url),
            html.escape(source.source_url),
            html.escape(source.verdict),
            html.escape(source.verdict),
            html.escape(format_instant(source.stated_close)),
            html.escape(format_instant(source.verified_at)),
        )
        for source in card.sources
    ]
    return "<ul class='sources'>%s</ul>" % "".join(cells)


def _record_field(record, name: str, default=None):
    """Read a field from a run row, whether it is a Row or a plain dict."""
    if isinstance(record, dict):
        return record.get(name, default)
    try:
        return record[name]
    except (IndexError, KeyError):
        return default


def _run_history(view: View) -> str:
    if not view.runs:
        return "<section><h2>Run history</h2><p class='empty'>No runs recorded.</p></section>"
    rows = []
    for run in view.runs:
        link = _record_field(run, "trace_ref")
        cell = (
            "<a href='/trace/%s'>%s</a>" % (html.escape(link), html.escape(link))
            if link
            else "<span class='empty'>none</span>"
        )
        rows.append(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (
                html.escape(str(_record_field(run, "crawler", ""))),
                html.escape(str(_record_field(run, "status", ""))),
                _record_field(run, "live_found", 0),
                _record_field(run, "closed_found", 0),
                html.escape(
                    _duration(_record_field(run, "started_at"), _record_field(run, "finished_at"))
                ),
                cell,
            )
        )
    return (
        "<section><h2>Run history</h2>"
        "<table><thead><tr><th>crawler</th><th>status</th><th>live</th>"
        "<th>closed</th><th>duration</th><th>trace</th></tr></thead><tbody>%s</tbody></table></section>"
        % "".join(rows)
    )


def _duration(started_at, finished_at) -> str:
    if not started_at or not finished_at:
        return "—"
    try:
        start = datetime.fromisoformat(started_at)
        finish = datetime.fromisoformat(finished_at)
    except ValueError:
        return "—"
    return f"{max((finish - start).total_seconds(), 0.0):.2f}s"


_CSS = """
body { font: 16px/1.5 system-ui, sans-serif; margin: 2rem auto; max-width: 56rem; color: #111 }
h1 { font-size: 1.6rem } h2 { font-size: 1.1rem }
section { margin: 1.5rem 0 }
.card { border: 1px solid #d7d7dc; border-radius: .5rem; margin: .5rem 0; padding: .75rem .9rem }
.card.greyed { background: #f4f4f6; border-color: #dcdce1 }
.close { margin: .2rem 0 .5rem } .stated, .verified { color: #5b5b66; font-size: .85rem }
.sources { list-style: none; margin: 0; padding: 0 }
.source { display: flex; flex-wrap: wrap; gap: .5rem; align-items: baseline; margin: .25rem 0 }
.source a { word-break: break-all }
.badge { border-radius: 999px; font-size: .78rem; font-weight: 600; padding: .1rem .55rem }
.badge.live { background: #dcf5e3; color: #14612f }
.badge.unverified { background: #eceaf3; color: #4b4364 }
.badge.closed { background: #e8e8ea; color: #55555e }
.empty { color: #72726f } code { word-break: break-all }
table { border-collapse: collapse } td, th { padding: .3rem .8rem .3rem 0; text-align: left }
"""
