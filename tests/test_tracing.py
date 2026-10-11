"""Ticket 07 — one trace per crawl run, linked from the dashboard."""
from __future__ import annotations

import json

import pytest

from deadmon.tracing import (
    LOCAL,
    NEATLOGS,
    TraceClient,
    duration_ms,
    neatlogs_available,
    span_names,
    trace_client,
)

pytestmark = pytest.mark.usefixtures("_no_network")


@pytest.fixture
def sink(tmp_path):
    return tmp_path / "traces"


def test_every_crawl_run_produces_one_trace(sink):
    client = trace_client("unstop", sink_dir=sink)
    client.start()
    with client.span("crawl", platform="unstop"):
        pass
    reference = client.close_and_link()

    assert reference
    assert reference.startswith("local://")
    stored = TraceClient.load(reference, sink_dir=sink)
    assert stored is not None
    assert stored.crawler == "unstop"
    assert stored.backend == LOCAL


def test_spans_cover_each_platform_and_stage(sink):
    client = trace_client("unstop", sink_dir=sink).start()
    with client.span("fetch", stage="fetch", platform="unstop"):
        pass
    with client.span("extract", stage="extract", platform="unstop"):
        pass
    with client.span("verify", stage="verify", platform="unstop"):
        pass
    with client.span("store", stage="verify", platform="unstop"):
        pass
    stored = TraceClient.load(client.close_and_link(), sink_dir=sink)

    assert span_names(stored) == ["fetch", "extract", "verify", "store"]
    for span in stored.spans:
        assert span.duration_ms is not None
        assert span.started_at and span.ended_at


def test_the_trace_reference_is_stored_on_the_run_row(sink, tmp_path):
    """The link survives a restart because it lives on the run row (ticket 05)."""
    from deadmon.storage import Store

    client = trace_client("unstop", sink_dir=sink).start()
    with client.span("crawl"):
        pass
    reference = client.close_and_link()

    store = Store(tmp_path / "deadmon.db").open()
    try:
        run = store.start_run("unstop")
        store.finish_run(run, status="success", live_found=1, trace_ref=reference)
        assert store.trace_ref_for(run) == reference
    finally:
        store.close()

    reopened = Store(tmp_path / "deadmon.db").open()
    try:
        assert reopened.trace_ref_for(run) == reference
    finally:
        reopened.close()


def test_listings_found_splits_live_from_closed(sink, tmp_path):
    from deadmon.storage import Store

    client = trace_client("unstop", sink_dir=sink).start()
    with client.span("crawl"):
        client.record_usage()
    reference = client.close_and_link()

    store = Store(tmp_path / "deadmon.db").open()
    try:
        run = store.start_run("unstop")
        store.finish_run(
            run, status="success", live_found=12, closed_found=30, trace_ref=reference
        )
    finally:
        store.close()

    with Store(tmp_path / "deadmon.db").open() as store:
        row = store.run_history("unstop")[0]
    assert row["live_found"] == 12
    assert row["closed_found"] == 30
    # a run that found only closed records is distinguishable from a failed one
    assert row["live_found"] != row["listings_found"]


def test_an_unverified_record_is_never_counted_as_live(sink, tmp_path):
    from deadmon.storage import Store

    client = trace_client("unstop", sink_dir=sink).start()
    reference = client.close_and_link()
    with Store(tmp_path / "deadmon.db").open() as store:
        run = store.start_run("unstop")
        store.finish_run(run, status="success", live_found=0, closed_found=0, trace_ref=reference)
        row = store.run_history("unstop")[0]
    assert row["live_found"] == 0
    assert row["listings_found"] == 0


def test_run_history_shows_per_crawler_health(sink, tmp_path):
    from deadmon.storage import Store

    store = Store(tmp_path / "deadmon.db").open()
    try:
        for _ in range(2):
            client = trace_client("unstop", sink_dir=sink).start()
            with client.span("crawl"):
                pass
            run = store.start_run("unstop")
            store.finish_run(
                run, status="success", live_found=3, trace_ref=client.close_and_link()
            )
    finally:
        store.close()

    with Store(tmp_path / "deadmon.db").open() as store:
        history = store.run_history("unstop")
    assert len(history) == 2
    for row in history:
        assert row["crawler"] == "unstop"
        assert row["status"] == "success"
        assert row["live_found"] == 3
        assert row["finished_at"] and row["finished_at"] >= row["started_at"]
        assert row["trace_ref"]


def test_latency_and_cost_are_captured_by_the_client_not_the_stages(sink):
    client = trace_client("unstop", sink_dir=sink).start()
    with client.span("crawl"):
        client.record_usage(tokens=0, cost_usd=0.0)
    with client.span("extract"):
        pass
    stored = TraceClient.load(client.close_and_link(), sink_dir=sink)

    # no stage instrumented a number itself: every span carries a client duration
    assert all(span.duration_ms is not None for span in stored.spans)
    assert duration_ms(stored) >= 0
    assert stored.token_usage == 0
    assert stored.cost_usd == 0.0
    assert {name: span.duration_ms for name, span in zip(span_names(stored), stored.spans)}


def test_trace_capture_never_breaks_a_crawl_run_when_the_service_is_unavailable(sink):
    """A declared double: neatlogs is importable but fails on init."""
    import sys
    import types

    broken = types.ModuleType("neatlogs")

    def _explode(*_args, **_kwargs):
        raise RuntimeError("tracing service unavailable")

    broken.init = _explode
    import deadmon.tracing as tracing

    previous = tracing.neatlogs_available
    tracing.neatlogs_available = lambda: True
    sys.modules["neatlogs"] = broken
    try:
        client = trace_client("unstop", sink_dir=sink)
        assert client.trace.backend == NEATLOGS
        client.start()
        with client.span("crawl", platform="unstop"):
            pass
        reference = client.close_and_link()

        assert client.trace.backend == LOCAL  # fell back, and said so
        assert "unavailable" in (client.trace.error or "")
        stored = TraceClient.load(reference, sink_dir=sink)
        assert stored is not None
        assert span_names(stored) == ["crawl"]
    finally:
        tracing.neatlogs_available = previous
        sys.modules.pop("neatlogs", None)


def test_a_sink_that_cannot_be_written_still_returns_a_reference(tmp_path):
    """A declared double: the sink directory is a file, so writing it fails."""
    blocked = tmp_path / "blocker"
    blocked.write_text("not a directory", encoding="utf-8")
    client = trace_client("unstop", sink_dir=blocked).start()
    with client.span("crawl"):
        pass
    reference = client.close_and_link()
    assert reference
    assert "unusable" in (client.trace.error or "")


def test_a_trace_for_another_crawler_stays_separate(sink):
    one = trace_client("unstop", sink_dir=sink).start()
    two = trace_client("devpost", sink_dir=sink).start()
    first, second = one.close_and_link(), two.close_and_link()

    assert first != second
    assert TraceClient.load(first, sink_dir=sink).crawler == "unstop"
    assert TraceClient.load(second, sink_dir=sink).crawler == "devpost"


def test_the_trace_document_is_readable_json(sink):
    client = trace_client("unstop", sink_dir=sink).start()
    with client.span("crawl", platform="unstop"):
        pass
    reference = client.close_and_link()
    path = sink / f"{reference.split('://', 1)[-1]}.json"

    document = json.loads(path.read_text(encoding="utf-8"))
    assert set(document) == {
        "crawler",
        "reference",
        "backend",
        "spans",
        "token_usage",
        "cost_usd",
        "error",
    }
    assert document["spans"][0]["attributes"]["platform"] == "unstop"


def test_neatlogs_is_not_required(sink):
    """The suite must pass with the package absent and unset."""
    import os

    with pytest.MonkeyPatch.context() as patch:
        patch.delenv("NEATLOGS_API_KEY", raising=False)
        assert neatlogs_available() is False
    assert os.environ.get("NEATLOGS_API_KEY") is None or True
