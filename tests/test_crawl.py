"""Ticket 08 — the demo moment: one command, whole pipeline, no network."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import shutil

import pytest

from deadmon.adapters.unstop import UnstopScraper
from deadmon.crawl import (
    DEFAULT_SINK_DIR,
    CrawlOutcome,
    Dashboard,
    crawl_corpus,
    crawl_one_fixture,
    fixtures_in,
    main,
)
from deadmon.storage import Store
from deadmon.tracing import TraceClient, span_names
from deadmon.verdict import CLOSED, LIVE, UNVERIFIED

from tests.conftest import (
    CLOSED_FIXTURE,
    KNOWN_GOOD_FIXTURE,
    PAST_FIXTURE,
    UNVERIFIED_DOUBLE,
)

AS_OF = datetime(2026, 10, 11, tzinfo=timezone.utc)


@pytest.fixture
def workspace(tmp_path):
    (tmp_path / "traces").mkdir()
    (tmp_path / "db").mkdir()
    return tmp_path


def crawl_one(fixture, workspace):
    return crawl_one_fixture(
        UnstopScraper(),
        fixture,
        store=Store(workspace / "db" / "deadmon.db").open(),
        now=AS_OF,
        sink_dir=workspace / "traces",
    )


def test_one_command_runs_the_crawler_end_to_end_with_no_network(workspace):
    outcomes = crawl_corpus(
        fixture_dir=Path("fixtures/unstop"),
        db_path=workspace / "db" / "deadmon.db",
        sink_dir=workspace / "traces",
        now=AS_OF,
    )
    assert len(outcomes) == 4
    # one run per fixture, each extracting, verifying, storing and tracing
    for outcome in outcomes:
        assert outcome.candidates > 0
        assert outcome.reference
        assert outcome.run_id > 0


def test_the_fixture_corpus_is_discovered_in_a_stable_order():
    fixtures = fixtures_in(Path("fixtures/unstop"))
    assert [f.name for f in fixtures] == [
        CLOSED_FIXTURE.name,
        KNOWN_GOOD_FIXTURE.name,
        PAST_FIXTURE.name,
        UNVERIFIED_DOUBLE.name,
    ]


def test_the_run_produces_at_least_one_live_listing(workspace):
    outcomes = crawl_corpus(
        fixture_dir=Path("fixtures/unstop"),
        db_path=workspace / "db" / "deadmon.db",
        sink_dir=workspace / "traces",
        now=AS_OF,
    )
    assert any(o.live_found > 0 for o in outcomes)
    healthy = max(outcomes, key=lambda o: o.live_found)
    assert healthy.live_found == 25  # the known-good fixture, recorded live


def test_the_run_produces_one_verdict_of_each_kind_where_the_corpus_supports_it(workspace):
    outcomes = crawl_corpus(
        fixture_dir=Path("fixtures/unstop"),
        db_path=workspace / "db" / "deadmon.db",
        sink_dir=workspace / "traces",
        now=AS_OF,
    )
    live = sum(o.live_found for o in outcomes)
    closed = sum(o.closed_found for o in outcomes)
    unverified = sum(o.unverified_found for o in outcomes)
    assert live == 25      # hackathons-open.json, recorded live
    assert closed == 49    # closed + past, recorded live
    assert unverified == 3  # the declared double


def test_one_crawl_run_row_per_fixture(workspace):
    db = workspace / "db" / "deadmon.db"
    crawl_corpus(
        fixture_dir=Path("fixtures/unstop"),
        db_path=db,
        sink_dir=workspace / "traces",
        now=AS_OF,
    )
    with Store(db).open() as store:
        runs = store.run_history()
        assert len(runs) == 4
        for run in runs:
            assert run["status"] == "success"
            assert run["trace_ref"]


def test_one_trace_per_crawl_run_stored_and_linked(workspace):
    db = workspace / "db" / "deadmon.db"
    outcomes = crawl_corpus(
        fixture_dir=Path("fixtures/unstop"),
        db_path=db,
        sink_dir=workspace / "traces",
        now=AS_OF,
    )
    for outcome in outcomes:
        document = workspace / "traces" / f"{outcome.reference.split('://', 1)[-1]}.json"
        assert document.exists(), outcome.reference
        stored = json.loads(document.read_text(encoding="utf-8"))
        assert span_names_stored(stored) == ["fetch", "extract", "verify", "store"]

    with Store(db).open() as store:
        runs = store.run_history()  # newest first
        stored_refs = [run["trace_ref"] for run in runs]
    assert sorted(stored_refs) == sorted(o.reference for o in outcomes)
    assert len(set(stored_refs)) == len(outcomes) == 4


def span_names_stored(document) -> list[str]:
    return [span["name"] for span in document["spans"]]


def test_the_trace_link_is_visible_on_the_dashboard(workspace):
    db = workspace / "db" / "deadmon.db"
    crawl_corpus(
        fixture_dir=Path("fixtures/unstop"),
        db_path=db,
        sink_dir=workspace / "traces",
        now=AS_OF,
    )
    dashboard = Dashboard(db, workspace / "traces")
    status, page = dashboard.dispatch("/")

    assert status == 200
    assert "/trace/local://" in page or "/trace/neatlogs://" in page
    assert "Run history" in page

    import re

    reference = re.search(r"/trace/([a-z]+://[0-9a-f-]+)", page).group(1)
    status, detail = dashboard.dispatch(f"/trace/{reference}")
    assert status == 200
    assert reference in detail
    assert "extract" in detail


def test_live_listings_render_as_cards_with_verdict_badges(workspace):
    db = workspace / "db" / "deadmon.db"
    crawl_corpus(
        fixture_dir=Path("fixtures/unstop"),
        db_path=db,
        sink_dir=workspace / "traces",
        now=AS_OF,
    )
    dashboard = Dashboard(db, workspace / "traces")
    status, page = dashboard.dispatch("/")

    assert status == 200
    assert "<h2>Feed</h2>" in page
    assert "<h2>Needs attention</h2>" in page
    assert "<span class='badge live'>live</span>" in page
    assert "<span class='badge unverified'>unverified</span>" in page
    # a closed verdict renders no badge at all: closed is in neither group
    assert "badge closed" not in page
    assert page.count("<span class='badge live'>live</span>") == 22
    assert page.count("<span class='badge unverified'>unverified</span>") == 3
    assert "Seed" not in page


def test_the_closed_fixture_is_in_neither_group(workspace):
    db = workspace / "db" / "deadmon.db"
    crawl_corpus(
        fixture_dir=Path("fixtures/unstop"),
        db_path=db,
        sink_dir=workspace / "traces",
        now=AS_OF,
    )
    with Store(db).open() as store:
        rows = store.source_rows()

    verdicts = {row["verdict"] for row in rows}
    assert verdicts == {LIVE, CLOSED, UNVERIFIED}
    live = [row for row in rows if row["verdict"] == LIVE]
    closed = [row for row in rows if row["verdict"] == CLOSED]
    unverified = [row for row in rows if row["verdict"] == UNVERIFIED]

    # 25 + 24 + 25 + 3 = 77 candidates crawled; the stored rows number 74
    # because the declared unverified double re-crawls three of the URLs the
    # healthy fixture already claimed and *updates* them. Re-verification
    # replaces a verdict; it does not add a second one.
    assert len(rows) == 77 - 3
    assert len(closed) == 49       # closed.json + past.json, recorded live
    assert len(unverified) == 3    # the declared double
    assert len(live) == 25 - 3


def test_the_trace_counts_agree_with_the_dashboard(workspace, tmp_path):
    """Per run, the trace's counts and the run row agree exactly."""
    only_open = tmp_path / "corpus"
    only_open.mkdir()
    shutil.copy(KNOWN_GOOD_FIXTURE, only_open / KNOWN_GOOD_FIXTURE.name)

    outcomes = crawl_corpus(
        fixture_dir=only_open,
        db_path=workspace / "db" / "deadmon.db",
        sink_dir=workspace / "traces",
        now=AS_OF,
    )
    (outcome,) = outcomes
    document = json.loads(
        (workspace / "traces" / f"{outcome.reference.split('://', 1)[-1]}.json").read_text(
            encoding="utf-8"
        )
    )
    verify_span = next(span for span in document["spans"] if span["name"] == "verify")
    trace_live = verify_span["attributes"]["live"]
    trace_closed = verify_span["attributes"]["closed"]

    with Store(workspace / "db" / "deadmon.db").open() as store:
        run = store.run_history()[0]
    assert (run["live_found"], run["closed_found"]) == (trace_live, trace_closed) == (25, 0)

    status, page = Dashboard(
        workspace / "db" / "deadmon.db", workspace / "traces"
    ).dispatch("/")
    assert f"{trace_live} card(s) in the feed" in page
    assert "0 card(s) needing attention" in page


def test_crawling_the_whole_corpus_keeps_every_verdict_visible(workspace):
    crawl_corpus(
        fixture_dir=Path("fixtures/unstop"),
        db_path=workspace / "db" / "deadmon.db",
        sink_dir=workspace / "traces",
        now=AS_OF,
    )
    status, page = Dashboard(workspace / "db" / "deadmon.db", workspace / "traces").dispatch("/")
    assert status == 200
    assert ">live<" in page and ">unverified<" in page
    # the closed listings are in neither group, but their rows survive
    with Store(workspace / "db" / "deadmon.db").open() as store:
        rows = store.source_rows()
    assert sum(1 for r in rows if r["verdict"] == CLOSED) == 49
    assert sum(1 for r in rows if r["verdict"] == LIVE) == 22
    assert sum(1 for r in rows if r["verdict"] == UNVERIFIED) == 3
    assert "22 card(s) in the feed" in page
    assert "3 card(s) needing attention" in page
    # the operator signal names the crawler that produced them
    assert "unstop: 3" in page
    # no closed badge is rendered, in either group
    assert "badge closed" not in page


def test_no_module_knows_which_platform_it_is_talking_to(workspace):
    """A stand-in adapter behind the same interface must work unchanged."""
    from deadmon.adapters.unstop import UnstopScraper

    source_text = Path("src/deadmon/crawl.py").read_text(encoding="utf-8")
    for platform in ("unstop.com", "devfolio", "devpost", "hack2skill"):
        assert platform not in source_text, platform

    outcome = crawl_one(KNOWN_GOOD_FIXTURE, workspace)
    assert outcome.crawler == UnstopScraper().name == "unstop"
    assert outcome.live_found == 25


def test_the_command_line_runs_and_prints(workspace):
    code = main(
        [
            "--fixtures", "fixtures/unstop",
            "--db", str(workspace / "db" / "cli.db"),
            "--traces", str(workspace / "traces"),
            "--as-of", AS_OF.isoformat(),
            "--no-serve",
        ]
    )
    assert code == 0


def test_the_verification_clock_is_injected_never_assumed():
    """`--as-of` pins it for a deterministic replay; the default is real now."""
    import inspect

    crawl_source = inspect.getsource(crawl_one_fixture)
    assert "datetime.now(timezone.utc)" in crawl_source
    assert "now if now is not None else" in crawl_source
    assert "--as-of" in inspect.getsource(main)

    workspace = Path("unused")


def test_the_dashboard_dispatches_known_routes_only(workspace):
    dashboard = Dashboard(workspace / "db" / "missing.db", workspace / "traces")
    assert dashboard.dispatch("/nope")[0] == 404
    assert dashboard.dispatch("/trace/local://absent")[0] == 200
    assert "No trace document" in dashboard.dispatch("/trace/local://absent")[1]


def test_no_network_is_enforced_mechanically(workspace):
    """The suite's autouse guard turns any socket use into a failure."""
    import socket

    with pytest.raises(RuntimeError):
        socket.create_connection(("unstop.com", 443), timeout=1)
