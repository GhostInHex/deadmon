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


def view_as_json(view: View) -> dict:
    """The same view model, as the JSON Next.js renders (ADR-0020).

    This is the seam between the two runtimes. It is deliberately a plain dict
    of primitives rather than anything richer: the frontend owns rendering, so
    the only contract that matters is that a field here always reaches a
    component, and that a renamed field fails a test here rather than silently
    rendering an empty feed.

    Dates stay as the stored ISO strings. `format_instant` owns display, and
    ADR-0013 requires the zone to be visible, so the label travels with the
    value instead of letting the browser guess a locale.
    """
    return {
        "feed": [_card_as_json(card) for card in view.feed],
        "needs_attention": [_card_as_json(card) for card in view.needs_attention],
        "needs_attention_by_crawler": needs_attention_by_crawler(view),
        "runs": [
            {
                "id": _record_field(run, "id"),
                "crawler": str(_record_field(run, "crawler", "")),
                "started_at": str(_record_field(run, "started_at", "")),
                "finished_at": str(_record_field(run, "finished_at", "")),
                "status": str(_record_field(run, "status", "")),
                "live_found": _record_field(run, "live_found", 0),
                "closed_found": _record_field(run, "closed_found", 0),
                "duration": _duration(
                    _record_field(run, "started_at"), _record_field(run, "finished_at")
                ),
                "trace_ref": _record_field(run, "trace_ref"),
            }
            for run in view.runs
        ],
    }


def _card_as_json(card: Card) -> dict:
    close = card.earliest_credible_close
    return {
        "title": card.title,
        "earliest_credible_close": close,
        "earliest_credible_close_display": format_instant(close),
        "sources": [
            {
                "crawler": source.crawler,
                "source_url": source.source_url,
                "verdict": source.verdict,
                "stated_close": source.stated_close,
                "stated_close_display": format_instant(source.stated_close),
                "verified_at": source.verified_at,
                "verified_at_display": format_instant(source.verified_at),
            }
            for source in card.sources
        ],
    }


def render_page(view: View, *, title: str = "deadmon") -> str:
    """One server-rendered page. Two groups; badges read the verdict word.

    Kept as the offline fallback after ADR-0020 moved the real UI to Next.js:
    the pipeline must stay demonstrable with no Node toolchain and no network.
    """
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{html.escape(title)}</title>",
            _FONTS,
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
    body = [
            f"<h1>Trace <code>{html.escape(reference)}</code></h1>",
            '<p class="trace-back"><a href="/">&larr; dashboard</a></p>',
        ]
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
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>trace</title>",
            _FONTS,
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


_FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1'
    "&family=Inter:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap\" rel=\"stylesheet\">"
)

_CSS = """
/* V7 Go tokens (docs/design-system-reference/tokens.css), inlined so the
   dashboard stays one self-contained server-rendered page with no asset
   fetch. Kept verbatim: design.md rule 1 - no raw hex below this block. */
:root {
  --color-ink: #292929;
  --color-ink-deep: #171717;
  --color-paper: #ffffff;
  --color-paper-warm: #f7f6f5;
  --color-rule: #e4e2e0;
  --color-rule-strong: #d1cfce;
  --color-signal: #ff683d;
  --color-signal-deep: #ec580a;
  --color-signal-ink: #b8420a;
  --color-signal-wash: #fff1eb;
  --color-mono: #737373;
  --color-ink-muted: #6b6b6b;
  --color-ink-inverse: #ffffff;
  --webfont-display: 'Instrument Serif', Georgia, serif;
  --webfont-body: 'Inter', system-ui, sans-serif;
  --webfont-mono: 'DM Mono', ui-monospace, monospace;
  --text-2xs: 0.6875rem;
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-md: 1rem;
  --text-lg: 1.25rem;
  --text-xl: 1.75rem;
  --text-2xl: 2.5rem;
  --tracking-mono: 0.08em;
  --tracking-display: -0.02em;
  --spacing-2: 0.5rem;
  --spacing-3: 0.75rem;
  --spacing-4: 1rem;
  --spacing-5: 1.5rem;
  --spacing-6: 2rem;
  --spacing-7: 3rem;
  --spacing-8: 4rem;
  --radius-sm: 4px;
  --radius-pill: 999px;
  --container-content: 75rem;
  --opacity-faint: 0.4;
}

*, *::before, *::after { box-sizing: border-box; }

body {
  margin: 0 auto;
  max-width: var(--container-content);
  padding: var(--spacing-6) var(--spacing-5) var(--spacing-9);
  font-family: var(--webfont-body);
  font-size: var(--text-md);
  line-height: 1.625;
  color: var(--color-ink);
  background: var(--color-paper);
  -webkit-font-smoothing: antialiased;
}

h1 {
  font-family: var(--webfont-display);
  font-size: var(--text-2xl);
  line-height: 1.286;
  letter-spacing: var(--tracking-display);
  color: var(--color-ink-deep);
  margin: 0;
}

.summary {
  font-family: var(--webfont-mono);
  font-size: var(--text-xs);
  letter-spacing: var(--tracking-mono);
  text-transform: uppercase;
  color: var(--color-mono);
  padding-bottom: var(--spacing-5);
  border-bottom: 1px solid var(--color-rule);
}

/* Hairlines over boxed cards (design.md rule 3). */
section { margin-top: var(--spacing-8); }

h2 {
  font-family: var(--webfont-mono);
  font-size: var(--text-xs);
  font-weight: 500;
  letter-spacing: var(--tracking-mono);
  text-transform: uppercase;
  color: var(--color-mono);
  padding-bottom: var(--spacing-3);
  border-bottom: 1px solid var(--color-rule);
  margin: 0 0 var(--spacing-3);
}

.card {
  padding: var(--spacing-4) 0;
  border-bottom: 1px solid var(--color-rule);
}

.card h2 {
  font-family: var(--webfont-body);
  font-size: var(--text-lg);
  font-weight: 500;
  letter-spacing: normal;
  text-transform: none;
  color: var(--color-ink-deep);
  border: 0;
  padding: 0;
  margin: 0 0 var(--spacing-1);
}

/* Unverified stays visible, not hidden (ADR-0007) - muted, never removed. */
.card.greyed { opacity: var(--opacity-faint); }
.card.greyed:hover { opacity: 1; }

.close {
  margin: 0 0 var(--spacing-3);
  font-size: var(--text-sm);
  color: var(--color-ink-muted);
}

.sources { list-style: none; margin: 0; padding: 0; }

.source {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2) var(--spacing-4);
  align-items: baseline;
  margin: var(--spacing-2) 0;
}

.source a {
  font-size: var(--text-xs);
  color: var(--color-ink-muted);
  word-break: break-all;
}
.source a:hover { color: var(--color-signal); }

.stated, .verified {
  font-family: var(--webfont-mono);
  font-size: var(--text-xs);
  color: var(--color-mono);
}

/* Mono uppercase pill, signal-wash ground, signal-deep text (design.md). */
.badge {
  font-family: var(--webfont-mono);
  font-size: var(--text-2xs);
  letter-spacing: var(--tracking-mono);
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: var(--radius-pill);
  background: var(--color-signal-wash);
  /* signal-ink, not signal-deep: the deep step is the hover value and
     measures 3.19:1 on this ground. ink clears AA at 4.98:1. */
  color: var(--color-signal-ink);
}

/* The other two verdicts stay neutral - signal is scarce (design.md rule 2).
   Both on ink-muted rather than mono: mono clears AA on white (4.74:1) but
   measures 4.39:1 on the paper-warm ground these badges sit on. */
.badge.unverified, .badge.closed {
  background: var(--color-paper-warm);
  color: var(--color-ink-muted);
}

.empty { color: var(--color-mono); font-size: var(--text-sm); }
code { font-family: var(--webfont-mono); word-break: break-all; }

table { border-collapse: collapse; width: 100%; }

th {
  font-family: var(--webfont-mono);
  font-size: var(--text-2xs);
  font-weight: 500;
  letter-spacing: var(--tracking-mono);
  text-transform: uppercase;
  text-align: left;
  color: var(--color-mono);
  padding: var(--spacing-2) var(--spacing-4) var(--spacing-2) 0;
  border-bottom: 1px solid var(--color-rule);
}

td {
  font-size: var(--text-sm);
  padding: var(--spacing-3) var(--spacing-4) var(--spacing-3) 0;
  border-bottom: 1px solid var(--color-rule);
  color: var(--color-ink-muted);
}

td a { color: var(--color-ink-muted); word-break: break-all; }
td a:hover { color: var(--color-signal); }

.trace-back {
  font-family: var(--webfont-mono);
  font-size: var(--text-xs);
  letter-spacing: var(--tracking-mono);
  text-transform: uppercase;
  padding-bottom: var(--spacing-5);
}
"""
