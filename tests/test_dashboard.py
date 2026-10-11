"""Ticket 06 — dashboard rendering: the feed and needs attention."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from deadmon.dashboard import (
    Card,
    CardSource,
    build_view,
    cards_from_rows,
    earliest_credible_close,
    format_instant,
    needs_attention_by_crawler,
    render_page,
    render_trace,
)
from deadmon.storage import Store
from deadmon.verdict import CLOSED, LIVE, UNVERIFIED

NOW = datetime(2026, 10, 11, tzinfo=timezone.utc)


def source(verdict, *, url="https://unstop.com/a", close=None, crawler="unstop", verified=None):
    return CardSource(
        crawler=crawler,
        source_url=url,
        stated_close=close.isoformat() if close else None,
        verdict=verdict,
        verified_at=(verified or NOW).isoformat(),
    )


def card(title, verdicts):
    return Card(
        title=title,
        earliest_credible_close=earliest_credible_close(verdicts),
        sources=tuple(verdicts),
    )


# -- the two groups -------------------------------------------------------


def test_live_listings_appear_in_the_feed():
    view = build_view([card("Live one", [source(LIVE)])], [])
    assert [c.title for c in view.feed] == ["Live one"]
    assert view.needs_attention == ()


def test_unverified_listings_appear_greyed_in_needs_attention():
    view = build_view([card("Grey one", [source(UNVERIFIED)])], [])
    assert view.feed == ()
    assert [c.title for c in view.needs_attention] == ["Grey one"]
    assert "greyed" in render_page(view)


def test_closed_listings_appear_in_neither_group():
    view = build_view([card("Gone", [source(CLOSED)])], [])
    assert view.feed == ()
    assert view.needs_attention == ()
    assert "Nothing in the feed" in render_page(view)
    assert "Nothing needs attention" in render_page(view)


def test_a_card_with_one_live_and_one_closed_source_is_a_feed_card():
    view = build_view(
        [card("Mixed", [source(LIVE, url="https://unstop.com/a"), source(CLOSED, url="https://unstop.com/b")])],
        [],
    )
    assert [c.title for c in view.feed] == ["Mixed"]


def test_unverified_records_are_excluded_from_every_feed_count():
    view = build_view(
        [
            card("Live one", [source(LIVE, url="https://unstop.com/1")]),
            card("Live two", [source(LIVE, url="https://unstop.com/2")]),
            card("Grey one", [source(UNVERIFIED, url="https://unstop.com/3")]),
            card("Grey two", [source(UNVERIFIED, url="https://unstop.com/4")]),
        ],
        [],
    )
    page = render_page(view)
    assert view.feed_count == 2
    assert "2 card(s) in the feed" in page
    assert "2 card(s) needing attention" in page


def test_needs_attention_shows_a_per_crawler_count():
    view = build_view(
        [
            card("A", [source(UNVERIFIED, url="https://unstop.com/1")]),
            card("B", [source(UNVERIFIED, url="https://unstop.com/2")]),
            card("C", [source(UNVERIFIED, url="https://devpost.com/1", crawler="devpost")]),
        ],
        [],
    )
    counts = needs_attention_by_crawler(view)
    assert counts == {"unstop": 2, "devpost": 1}
    page = render_page(view)
    assert "unstop: 2" in page
    assert "devpost: 1" in page


# -- the card -------------------------------------------------------------


def test_a_card_shows_the_earliest_credible_close_across_sources():
    sooner = source(LIVE, url="https://unstop.com/a", close=NOW + timedelta(days=2))
    later = source(LIVE, url="https://unstop.com/b", close=NOW + timedelta(days=20))
    built = card("Both live", [later, sooner])

    assert built.earliest_credible_close == sooner.stated_close
    page = render_page(build_view([built], []))
    assert "2026-10-13" in page  # the earlier date, not the later one
    assert "2026-10-31" in page  # the second source's own stated date is visible


def test_a_closed_source_never_contributes_the_earliest_date():
    past = source(CLOSED, url="https://unstop.com/past", close=NOW - timedelta(days=5))
    live = source(LIVE, url="https://unstop.com/live", close=NOW + timedelta(days=5))
    built = card("One past one live", [past, live])

    assert built.earliest_credible_close == live.stated_close


def test_an_unverified_source_never_contributes_the_earliest_date():
    grey = source(UNVERIFIED, url="https://unstop.com/grey")
    live = source(LIVE, url="https://unstop.com/live", close=NOW + timedelta(days=5))
    built = card("One grey one live", [grey, live])

    assert built.earliest_credible_close == live.stated_close


def test_a_card_with_no_live_source_has_no_credible_date():
    built = card("All grey", [source(UNVERIFIED, url="https://unstop.com/a")])
    assert built.earliest_credible_close is None
    assert "no credible registration close" in render_page(build_view([built], []))


def test_each_source_lists_its_own_url_and_verdict():
    view = build_view([card("Two", [source(LIVE, url="https://unstop.com/a"), source(LIVE, url="https://unstop.com/b")])], [])
    page = render_page(view)
    assert "https://unstop.com/a" in page
    assert "https://unstop.com/b" in page
    assert page.count(">live<") == 2  # the badge reads the verdict word


def test_with_one_source_the_card_collapses_to_a_single_row():
    view = build_view([card("Solo", [source(LIVE, url="https://unstop.com/a")])], [])
    page = render_page(view)
    assert page.count("class='source'") == 1
    assert "https://unstop.com/a" in page
    # the card is still a view over sources, not a listing row
    assert isinstance(view.feed[0].sources, tuple) and len(view.feed[0].sources) == 1


def test_the_badge_never_reads_verified():
    """The badge reads the verdict word; "verified" is not one."""
    grey = render_page(build_view([card("Grey", [source(UNVERIFIED)])], []))
    assert ">unverified<" in grey
    assert ">verified<" not in grey

    live = render_page(build_view([card("Live", [source(LIVE)])], []))
    assert ">live<" in live
    assert ">verified<" not in live
    assert ">closed<" not in live

    closed = render_page(build_view([card("Closed", [source(CLOSED)])], []))
    assert ">closed<" not in closed  # closed appears in neither group


# -- rendering from stored rows -------------------------------------------


def test_the_page_renders_from_seeded_rows_with_no_network(tmp_path):
    store = Store(tmp_path / "seed.db").open()
    try:
        run = store.start_run("unstop")
        from deadmon.candidate import make_candidate
        from deadmon.verdict import Listing

        def pair(verdict, url, title, close):
            candidate = make_candidate(
                title=title,
                source_url=url,
                registration_close=close,
                mode="online",
                crawler="unstop",
            )
            listing = Listing(
                candidate_title=title,
                source_url=url,
                verdict=verdict,
                verified_at=NOW,
                crawler="unstop",
            )
            return candidate, listing

        store.record_run_listings(
            run,
            [
                pair(LIVE, "https://unstop.com/1", "Seed live", NOW + timedelta(days=3)),
                pair(UNVERIFIED, "https://unstop.com/2", "Seed grey", None),
                pair(CLOSED, "https://unstop.com/3", "Seed closed", NOW - timedelta(days=3)),
            ],
        )
        store.finish_run(run, status="success", live_found=1, trace_ref="local://seed")
    finally:
        store.close()

    reopened = Store(tmp_path / "seed.db").open()
    try:
        page = render_page(
            build_view(
                cards_from_rows(reopened.source_rows()),
                reopened.run_history("unstop"),
            )
        )
    finally:
        reopened.close()

    assert "Seed live" in page
    assert "Seed grey" in page
    assert "Seed closed" not in page  # closed appears in neither group
    assert ">live<" in page
    assert ">unverified<" in page


def test_no_single_page_application_framework_is_introduced():
    import deadmon.dashboard as dashboard

    source_text = Path(dashboard.__file__).read_text(encoding="utf-8")
    assert "react" not in source_text.lower()
    assert "vue" not in source_text.lower()
    assert "<!doctype html>" in source_text


def test_run_history_links_to_the_trace(tmp_path):
    from deadmon.tracing import TraceClient

    sink = tmp_path / "traces"
    client = TraceClient("unstop", sink_dir=sink).start()
    with client.span("crawl", platform="unstop"):
        pass
    reference = client.close_and_link()

    page = render_page(build_view([], [{"crawler": "unstop", "status": "success", "live_found": 3,
                                        "closed_found": 0, "started_at": NOW.isoformat(),
                                        "finished_at": (NOW + timedelta(seconds=2)).isoformat(),
                                        "trace_ref": reference}]))
    assert f"/trace/{reference}" in page
    assert "2.00s" in page

    detail = render_trace(reference, sink_dir=sink)
    assert reference in detail
    assert "crawl" in detail


def test_a_missing_trace_document_says_so(tmp_path):
    assert "No trace document" in render_trace("local://absent", sink_dir=tmp_path / "traces")


def test_every_rendered_date_carries_a_zone_label():
    assert format_instant(NOW.isoformat()).endswith("UTC")
    assert format_instant(NOW.isoformat()) == "2026-10-11 00:00 UTC"
    assert format_instant("2026-10-11T00:00:00Z") == "2026-10-11 00:00 UTC"
    assert format_instant("2026-10-11T00:00:00+05:30") == "2026-10-10 18:30 UTC"
    assert "zone unknown" in format_instant("2026-10-11 00:00:00")
    assert format_instant(None) == "—"


def test_titles_are_escaped():
    view = build_view([card("<script>alert(1)</script>", [source(LIVE)])], [])
    page = render_page(view)
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page
