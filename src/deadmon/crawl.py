"""The crawl run: one command, the whole pipeline, no network.

    py -m deadmon.crawl

Replays every recorded Unstop fixture through fetch → extract → verify → store
→ trace, then serves one server-rendered page on 127.0.0.1 where live listings
appear as cards in the feed and everything else appears in needs attention.

The Scout is the loop; this module is the loop's per-platform runner. Nothing
here knows which platform it is talking to beyond the adapter it is handed, and
nothing fetches from the network: the fixture set is the input, which is what
makes the demo reproducible and the suite offline.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import urllib.parse

from .adapters import CRAWLERS
from .adapters.unstop import UnstopScraper
from .dashboard import (
    build_view,
    cards_from_rows,
    render_page,
    render_trace,
    view_as_json,
)
from .storage import Store
from .tracing import TraceClient, shutdown, trace_client
from .verification import verify_crawl

DEFAULT_FIXTURE_DIR = Path("fixtures") / "unstop"
DEFAULT_DB = Path(".runs") / "deadmon.db"
DEFAULT_SINK_DIR = Path(".runs") / "traces"
PIPELINE_STAGES = ("fetch", "extract", "verify", "store")


@dataclass(frozen=True)
class CrawlOutcome:
    crawler: str
    run_id: int
    reference: str
    candidates: int
    live_found: int
    closed_found: int
    unverified_found: int
    error: str | None = None

    @property
    def listings_found(self) -> int:
        """An unverified record is not a live listing (ADR-0007)."""
        return self.live_found + self.closed_found


def crawl_one_fixture(
    scraper,
    fixture: Path,
    *,
    store: Store,
    now: datetime | None = None,
    sink_dir: Path = DEFAULT_SINK_DIR,
) -> CrawlOutcome:
    """Run one crawler against one recorded fixture, end to end, offline."""
    checked_at = now if now is not None else datetime.now(timezone.utc)
    client: TraceClient = trace_client(scraper.name, sink_dir=sink_dir).start()
    run_id = store.start_run(scraper.name)
    error: str | None = client.trace.error

    with client.span("fetch", stage="fetch", platform=scraper.name):
        payload = fixture.read_bytes()

    with client.span("extract", stage="extract", platform=scraper.name) as span:
        candidates = list(scraper.extract(payload))
        span.attributes["candidates"] = len(candidates)

    with client.span("verify", stage="verify", platform=scraper.name) as span:
        results = verify_crawl(candidates, now=checked_at)
        span.attributes["live"] = sum(1 for r in results if r.verdict == "live")
        span.attributes["unverified"] = sum(1 for r in results if r.verdict == "unverified")
        span.attributes["closed"] = sum(1 for r in results if r.verdict == "closed")

    with client.span("store", stage="store", platform=scraper.name):
        pair = list(zip(candidates, (result.listing for result in results), strict=True))
        store.record_run_listings(run_id, pair)

    live_found = sum(1 for r in results if r.verdict == "live")
    closed_found = sum(1 for r in results if r.verdict == "closed")
    unverified_found = sum(1 for r in results if r.verdict == "unverified")

    reference = client.close_and_link()
    store.finish_run(
        run_id,
        status="success",
        live_found=live_found,
        closed_found=closed_found,
        trace_ref=reference,
    )
    return CrawlOutcome(
        crawler=scraper.name,
        run_id=run_id,
        reference=reference,
        candidates=len(candidates),
        live_found=live_found,
        closed_found=closed_found,
        unverified_found=unverified_found,
        error=error,
    )


def fixtures_in(directory: Path) -> list[Path]:
    """Every recorded fixture in the corpus, in a stable order."""
    return sorted(
        p
        for p in Path(directory).iterdir()
        if p.is_file() and p.suffix.lower() in {".json", ".html"}
    )


def crawl_corpus(
    *,
    fixture_dir: Path = DEFAULT_FIXTURE_DIR,
    db_path: Path = DEFAULT_DB,
    sink_dir: Path = DEFAULT_SINK_DIR,
    now: datetime | None = None,
    scraper=None,
) -> list[CrawlOutcome]:
    """Run the crawler over the recorded corpus. One run per fixture."""
    adapter = scraper if scraper is not None else UnstopScraper()
    outcomes: list[CrawlOutcome] = []
    store = Store(db_path).open()
    try:
        for fixture in fixtures_in(fixture_dir):
            outcomes.append(
                crawl_one_fixture(adapter, fixture, store=store, now=now, sink_dir=sink_dir)
            )
    finally:
        store.close()
    return outcomes


def crawl_all(
    *,
    db_path: Path = DEFAULT_DB,
    sink_dir: Path = DEFAULT_SINK_DIR,
    now: datetime | None = None,
    fixture_dirs: dict[str, Path] | None = None,
) -> list[CrawlOutcome]:
    """Run every registered crawler over its recorded corpus.

    One run per fixture per crawler; the store is shared so the dashboard
    sees every platform. `fixture_dirs` overrides a crawler's corpus
    directory by name — that is how `--fixtures` keeps pointing at Unstop.
    Platform names live in `adapters.CRAWLERS`, never here.
    """
    overrides = fixture_dirs or {}
    outcomes: list[CrawlOutcome] = []
    store = Store(db_path).open()
    try:
        for name, scraper_cls, corpus_dir in CRAWLERS:
            directory = overrides.get(name, corpus_dir)
            for fixture in fixtures_in(directory):
                outcomes.append(
                    crawl_one_fixture(
                        scraper_cls(), fixture, store=store, now=now, sink_dir=sink_dir
                    )
                )
    finally:
        store.close()
    return outcomes


# -- the server-rendered page ---------------------------------------------


class Dashboard:
    """The single page, assembled from the database on every request."""

    def __init__(self, db_path: Path, sink_dir: Path = DEFAULT_SINK_DIR):
        self.db_path = Path(db_path)
        self.sink_dir = Path(sink_dir)

    def dispatch(self, path: str) -> tuple[int, str]:
        """Route one path. No framework, no SPA, no network."""
        route = urllib.parse.urlparse(path)
        with Store(self.db_path).open() as store:
            view = build_view(
                cards_from_rows(store.source_rows()), store.run_history()
            )
        if route.path in ("/", "/index.html"):
            return 200, render_page(view)
        # The seam Next.js renders from (ADR-0020). Read-only, same view model.
        if route.path == "/api/feed":
            return 200, json.dumps(view_as_json(view), default=str)
        if route.path.startswith("/trace/"):
            reference = urllib.parse.unquote(route.path[len("/trace/"):])
            return 200, render_trace(reference, sink_dir=self.sink_dir)
        if route.path == "/runs.json":
            return 200, json.dumps([dict(run) for run in view.runs], default=str)
        return 404, "<!doctype html><h1>Not found</h1>"


def make_handler(dashboard: Dashboard):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - http.server's contract
            status, body = dashboard.dispatch(self.path)
            payload = body.encode("utf-8")
            self.send_response(status)
            if self.path.split("?")[0] in ("/api/feed", "/runs.json"):
                self.send_header("Content-Type", "application/json; charset=utf-8")
                # The Next.js app is deployed to a different origin (ADR-0020).
                # Read-only GETs, no credentials, so a wildcard origin is safe
                # here; this endpoint never mutates anything.
                self.send_header("Access-Control-Allow-Origin", "*")
            else:
                self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *_args) -> None:
            """Keep the demo output readable."""

    return Handler


def serve(dashboard: Dashboard, *, host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), make_handler(dashboard))
    return server


# -- the one command ------------------------------------------------------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="deadmon.crawl",
        description="Crawl every registered platform against the recorded fixtures "
                    "and serve the dashboard.",
    )
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURE_DIR,
                        help="Unstop fixture directory to replay; the other crawlers "
                             "use their recorded corpora")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="SQLite database path")
    parser.add_argument("--traces", type=Path, default=DEFAULT_SINK_DIR,
                        help="directory holding trace documents")
    parser.add_argument("--port", type=int, default=8765, help="dashboard port")
    parser.add_argument("--host", default="127.0.0.1", help="dashboard bind address")
    parser.add_argument("--as-of", default=None,
                        help="verification clock, e.g. 2026-10-11T00:00:00+00:00. "
                             "Pin it to replay the recorded state deterministically.")
    parser.add_argument("--reset", action="store_true",
                        help="remove the database and stored traces first, so the demo "
                             "starts from a clean slate. Runs are otherwise append-only.")
    parser.add_argument("--no-serve", action="store_true", help="crawl and print, do not serve")
    args = parser.parse_args(argv)

    now = None
    if args.as_of:
        now = datetime.fromisoformat(args.as_of)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

    # This is the process entry point, so the SDK is drained here and nowhere
    # else: once for a `--no-serve` crawl that exits immediately, and once more
    # on Ctrl-C when the dashboard was serving. Per-run spans are batched and
    # exported by the SDK's own background thread, not by this call.
    try:
        return _run(args, now)
    finally:
        shutdown()


def _run(args, now) -> int:
    if args.reset:
        # Runs are append-only by design; this is the explicit opt-out, used by
        # the demo so a fresh run is the whole story.
        for path in (args.db, *args.traces.glob("*.json")):
            if path.exists():
                path.unlink()

    outcomes = crawl_all(
        db_path=args.db,
        sink_dir=args.traces,
        now=now,
        fixture_dirs={"unstop": args.fixtures},
    )
    for outcome in outcomes:
        print(
            f"{outcome.crawler:8s} run #{outcome.run_id}  "
            f"candidates={outcome.candidates:3d}  live={outcome.live_found:3d}  "
            f"closed={outcome.closed_found:3d}  unverified={outcome.unverified_found:3d}  "
            f"trace={outcome.reference}"
        )

    total_live = sum(o.live_found for o in outcomes)
    total_closed = sum(o.closed_found for o in outcomes)
    total_unverified = sum(o.unverified_found for o in outcomes)
    print(
        f"\n{len(outcomes)} crawl run(s): live found={total_live} + closed found={total_closed}, "
        f"{total_unverified} unverified. No network was used."
    )

    if args.no_serve:
        return 0

    dashboard = Dashboard(args.db, args.traces)
    server = serve(dashboard, host=args.host, port=args.port)
    print(f"dashboard: http://{args.host}:{args.port}/  (Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
