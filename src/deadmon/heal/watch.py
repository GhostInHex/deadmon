"""The heal watchdog: crawl-run rows in, breaks out.

Detection only. This module answers one question — has one crawler produced no
listings on two consecutive finished crawl runs? — and answers nothing else:
proposing a change, sandbox-validating it and committing it are later steps
(ADR-0014, ADR-0016, ADR-0017), and a break has to be right before anything
acts on it.

Two runs rather than one, because a single empty run is ordinary: a platform
can be between hackathon seasons. Consecutive rather than any two, because a
run that found listings in between means the crawler worked as recently as
yesterday.

An unfinished run — still `running`, or killed and closed out as `interrupted`
— is skipped, never counted. It carries no yield, so it is neither an empty
page nor a recovery: a run killed mid-write must not read as a broken
platform, and a hole in the history must not read as evidence either.

Rows in, breaks out. No Store, no clock, no I/O: the watchdog never learns
where its rows came from, which is what keeps it cheap to test and impossible
to tempt with a network call.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Protocol

RUNNING = "running"
INTERRUPTED = "interrupted"

# A run that never finished. `resume_interrupted` finds the ones still in
# flight; `mark_interrupted` closes the killed ones out with a status rather
# than leaving them ambiguous.
UNFINISHED_STATUSES = (RUNNING, INTERRUPTED)

ZERO_LISTINGS = 0


class RunRow(Protocol):
    """One crawl-run row, read by column name.

    What `Store.run_history` returns, and nothing more than that: `sqlite3.Row`
    and a plain dict both satisfy it, and the watchdog does not care which.
    """

    def __getitem__(self, column: str) -> Any: ...


@dataclass(frozen=True)
class Break:
    """Two consecutive zero-listing finished runs for one crawler."""

    crawler: str
    run_ids: tuple[int, int]
    trace_ref: str | None


def detect_breaks(rows: Iterable[RunRow]) -> list[Break]:
    """One Break per crawler with two consecutive finished runs that found nothing."""
    histories: dict[str, list[RunRow]] = {}
    for row in rows:
        histories.setdefault(row["crawler"], []).append(row)

    breaks: list[Break] = []
    for crawler in sorted(histories):
        runs = sorted(histories[crawler], key=lambda row: row["id"])
        pair = _two_consecutive_zero_listing_runs(runs)
        if pair is None:
            continue
        older, newer = pair
        breaks.append(
            Break(
                crawler=crawler,
                run_ids=(older["id"], newer["id"]),
                trace_ref=newer["trace_ref"],
            )
        )
    return breaks


def _two_consecutive_zero_listing_runs(runs: list[RunRow]) -> tuple[RunRow, RunRow] | None:
    """The newest adjacent pair of finished zero-listing runs nothing recovered from.

    Adjacent in that crawler's own history, not merely its two most recent
    runs: an unfinished run between two empty ones is a gap in what was
    observed, and a gap is not evidence. A later run that found listings ends
    the story whatever came before it — that crawler is working again — so the
    pair reported is the newest evidence, not the oldest.
    """
    for index in range(len(runs) - 2, -1, -1):
        older, newer = runs[index], runs[index + 1]
        if not (_zero_listing_finished(older) and _zero_listing_finished(newer)):
            continue
        if any(_found_listings(later) for later in runs[index + 2 :]):
            continue
        return older, newer
    return None


def _finished(row: RunRow) -> bool:
    """A run that closed out: it has a finish stamp and a final status."""
    return bool(row["finished_at"]) and row["status"] not in UNFINISHED_STATUSES


def _zero_listing_finished(row: RunRow) -> bool:
    """A finished run that yielded nothing — the suspicious shape."""
    return _finished(row) and row["listings_found"] == ZERO_LISTINGS


def _found_listings(row: RunRow) -> bool:
    """A finished run that yielded something: evidence the crawler still works."""
    return _finished(row) and row["listings_found"] != ZERO_LISTINGS
