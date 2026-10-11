"""Slice 4 — the heal watchdog: two zero-listing runs in a row break a crawler.

Every row here is fabricated in the shape `Store.run_history` returns — id,
crawler, started_at, finished_at, status, listings_found, live_found,
closed_found, trace_ref — and nothing else is real: no database, no clock, no
network. conftest's autouse socket guard is still watching.
"""
from __future__ import annotations

import ast
from pathlib import Path

from deadmon.heal.watch import Break, detect_breaks

DEV = "devfolio"
OTHER = "unstop"
AT = "2026-10-12T06:00:00+00:00"
WATCH_SOURCE = Path("src/deadmon/heal/watch.py")

# What a rows-in / breaks-out module may import. Anything else brings a clock,
# a socket or a database into the thing that decides a crawler is broken.
PURE_IMPORTS = {"__future__", "collections", "dataclasses", "typing"}


def run_row(
    run_id,
    crawler,
    *,
    listings_found=0,
    status="success",
    finished_at=AT,
    trace_ref=None,
):
    """One fabricated run-history row. `finished_at=None` is a run still going."""
    return {
        "id": run_id,
        "crawler": crawler,
        "started_at": AT,
        "finished_at": finished_at,
        "status": status,
        "listings_found": listings_found,
        "live_found": listings_found,
        "closed_found": 0,
        "trace_ref": trace_ref,
    }


def history(*rows):
    """`run_history` hands rows back newest first; so does this."""
    return list(reversed(rows))


# -- the fire case ----------------------------------------------------------


def test_watchdog_fires_on_two_consecutive_zero_listing_runs():
    rows = history(
        run_row(7, DEV, trace_ref="local://run-7"),
        run_row(8, DEV, trace_ref="local://run-8"),
    )
    breaks = detect_breaks(rows)
    assert len(breaks) == 1
    (found,) = breaks
    assert isinstance(found, Break)
    assert found.crawler == DEV
    assert found.run_ids == (7, 8)
    assert found.trace_ref == "local://run-8"  # the latest run's trace


def test_a_third_zero_run_still_reports_one_break():
    rows = history(
        run_row(6, DEV, trace_ref="local://run-6"),
        run_row(7, DEV, trace_ref="local://run-7"),
        run_row(8, DEV, trace_ref="local://run-8"),
    )
    (found,) = detect_breaks(rows)
    assert found.run_ids == (7, 8)
    assert found.trace_ref == "local://run-8"


def test_one_crawlers_break_does_not_depend_on_another_being_healthy():
    rows = history(
        run_row(7, OTHER, listings_found=25),
        run_row(8, DEV, trace_ref="local://run-8"),
        run_row(9, DEV, trace_ref="local://run-9"),
        run_row(10, OTHER, listings_found=31),
    )
    (found,) = detect_breaks(rows)
    assert found.crawler == DEV
    assert found.run_ids == (8, 9)


def test_the_order_the_rows_arrive_in_does_not_change_the_answer():
    """`run_history` is newest first, but the watchdog reads run ids."""
    rows = history(
        run_row(7, DEV, trace_ref="local://run-7"),
        run_row(8, DEV, trace_ref="local://run-8"),
    )
    assert detect_breaks(rows) == detect_breaks(rows[::-1])


# -- the silence cases ------------------------------------------------------


def test_zero_then_a_healthy_run_is_silent():
    rows = history(
        run_row(7, DEV, trace_ref="local://run-7"),
        run_row(8, DEV, listings_found=4, trace_ref="local://run-8"),
    )
    assert detect_breaks(rows) == []


def test_a_healthy_run_then_a_zero_run_is_silent():
    rows = history(
        run_row(7, DEV, listings_found=25, trace_ref="local://run-7"),
        run_row(8, DEV, trace_ref="local://run-8"),
    )
    assert detect_breaks(rows) == []


def test_a_healthy_run_after_the_zeros_silences_the_break():
    """The crawler worked since: two empty runs followed by a yield is not a break."""
    rows = history(
        run_row(6, DEV, trace_ref="local://run-6"),
        run_row(7, DEV, trace_ref="local://run-7"),
        run_row(8, DEV, listings_found=12, trace_ref="local://run-8"),
    )
    assert detect_breaks(rows) == []


def test_a_lone_zero_listing_run_is_silent():
    assert detect_breaks(history(run_row(8, DEV, trace_ref="local://run-8"))) == []


def test_zeros_split_across_two_crawlers_are_silent():
    """One empty run each is not one crawler failing twice."""
    rows = history(run_row(7, DEV), run_row(8, OTHER))
    assert detect_breaks(rows) == []


def test_an_empty_history_is_silent():
    assert detect_breaks([]) == []


def test_unfinished_rows_are_ignored():
    """A run that never finished carries no yield, so it is not an empty page.

    `running` is a run still in flight; `interrupted` is a killed one, closed
    out with a status and `listings_found` left at its default. Neither is
    evidence about the platform, so neither can make a second zero.
    """
    rows = history(
        run_row(7, DEV, trace_ref="local://run-7"),
        run_row(8, DEV, status="running", finished_at=None),
        run_row(9, DEV, status="interrupted"),
    )
    assert detect_breaks(rows) == []


def test_an_older_unfinished_run_does_not_hide_a_break():
    """Skipping is not the same as stopping: the two finished zeros still stand."""
    rows = history(
        run_row(6, DEV, status="running", finished_at=None),
        run_row(7, DEV, trace_ref="local://run-7"),
        run_row(8, DEV, trace_ref="local://run-8"),
    )
    (found,) = detect_breaks(rows)
    assert found.run_ids == (7, 8)


def test_an_unfinished_run_between_two_zero_runs_is_a_gap_not_a_break():
    """A killed run between two empty runs leaves the yield unobserved.

    Two finished zero runs with nothing in between is the trigger; two zero
    runs with a hole between them is one empty run and one unknown.
    """
    rows = history(
        run_row(7, DEV, trace_ref="local://run-7"),
        run_row(8, DEV, status="interrupted"),
        run_row(9, DEV, trace_ref="local://run-9"),
    )
    assert detect_breaks(rows) == []


# -- the module's own contract ---------------------------------------------


def test_the_watchdog_reads_no_store_and_opens_no_io():
    """Rows in, breaks out: the judge of a break reads nothing else."""
    source = WATCH_SOURCE.read_text(encoding="utf-8")
    imports = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
    assert imports <= PURE_IMPORTS, imports
    assert "storage" not in imports
    assert "socket" not in imports
