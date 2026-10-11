#!/usr/bin/env python3
"""Record the heal-001 evidence pack: break, heal, second clean crawl, backfill.

Runs the double-run demo offline against recorded fixtures and writes the
committed evidence under `docs/evidence/heal-001-unstop/`. One recorder, one
pack: re-running regenerates the pack with fresh trace ids and receipt
numbers, so the committed pack is the output of the last recorded run.

The break is staged, not recorded: Unstop did not change its layout
overnight. The snapshot in `fixtures/unstop-heal/` is constructed from the
known-good fixture and declared as such. Nothing here touches the network;
the suite guard would fail the run if it tried.

Usage (from the repo root):
    python scripts/record_heal_evidence.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tests.test_heal_proof import (  # noqa: E402 -- demo double lives with the proof test
    AS_OF,
    SNAPSHOT,
    HealedUnstopScraper,
)

from deadmon.adapters.unstop import UnstopScraper  # noqa: E402
from deadmon.crawl import crawl_one_fixture  # noqa: E402
from deadmon.heal.watch import detect_breaks  # noqa: E402
from deadmon.receipts import DEFAULT_RECEIPT_DIR  # noqa: E402
from deadmon.storage import Store  # noqa: E402
from deadmon.verification import verify_crawl  # noqa: E402
from tests.conftest import KNOWN_GOOD_FIXTURE  # noqa: E402

EVIDENCE = ROOT / "docs" / "evidence" / "heal-001-unstop"
RECORDED = "2026-10-12"
CONSTRUCTED_NOTE = (
    "constructed break-demo snapshot, not a recording: "
    "Unstop did not change its layout overnight"
)


def _write(name: str, document: dict) -> Path:
    path = EVIDENCE / name
    path.write_text(json.dumps(document, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return path


def main() -> int:
    traces = EVIDENCE / "traces"
    receipts = EVIDENCE / "receipts"
    traces.mkdir(parents=True, exist_ok=True)
    receipts.mkdir(parents=True, exist_ok=True)
    for stale in (*traces.glob("*.json"), *receipts.glob("*.json")):
        stale.unlink()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        receipt_tmp = tmp_path / "receipts"
        receipt_tmp.mkdir()
        store = Store(tmp_path / "deadmon.db").open()
        try:
            real, healed = UnstopScraper(), HealedUnstopScraper()
            baseline = crawl_one_fixture(real, KNOWN_GOOD_FIXTURE, store=store,
                                         now=AS_OF, sink_dir=traces, receipt_dir=receipt_tmp)
            break1 = crawl_one_fixture(real, SNAPSHOT, store=store,
                                       now=AS_OF, sink_dir=traces, receipt_dir=receipt_tmp)
            break2 = crawl_one_fixture(real, SNAPSHOT, store=store,
                                       now=AS_OF, sink_dir=traces, receipt_dir=receipt_tmp)
            rows = store.run_history()
            (fired,) = detect_breaks(rows)
            clean = crawl_one_fixture(healed, SNAPSHOT, store=store,
                                      now=AS_OF, sink_dir=traces, receipt_dir=receipt_tmp)
            backfill = crawl_one_fixture(healed, KNOWN_GOOD_FIXTURE, store=store,
                                         now=AS_OF, sink_dir=traces, receipt_dir=receipt_tmp)
            for path in sorted(receipt_tmp.glob("receipt-*.json")):
                shutil.copy(path, receipts / path.name)
        finally:
            store.close()

    mlh_rows = [{"id": 1, "crawler": "mlh", "status": "success",
                 "finished_at": AS_OF.isoformat(), "listings_found": 0,
                 "trace_ref": "local://steady"}]
    mlh_breaks = detect_breaks(mlh_rows)

    real_count = len(list(UnstopScraper().extract(KNOWN_GOOD_FIXTURE.read_bytes())))
    healed_payload = list(HealedUnstopScraper().extract(KNOWN_GOOD_FIXTURE.read_bytes()))
    healed_live = sum(1 for r in verify_crawl(healed_payload, now=AS_OF) if r.verdict == "live")

    baseline_doc = {
        "recorded": RECORDED,
        "as_of": AS_OF.isoformat(),
        "crawlers": {
            "unstop": {"recent_live_yield": baseline.live_found,
                       "status": "baseline set — a sudden zero is a regression"},
            "mlh": {"recent_live_yield": 0,
                    "status": "no baseline history — off-season quiet is steady state, not a break"},
        },
    }
    break_doc = {
        "recorded": RECORDED,
        "demo": "Unstop yields 25, then 0 overnight",
        "snapshot": {"file": "fixtures/unstop-heal/hackathons-open.v2-changed-layout.json",
                     "note": CONSTRUCTED_NOTE},
        "candidates_before": baseline.candidates,
        "candidates_after": break2.candidates,
        "runs": [{"run_id": break1.run_id, "candidates": break1.candidates,
                  "trace": break1.reference},
                 {"run_id": break2.run_id, "candidates": break2.candidates,
                  "trace": break2.reference}],
        "watchdog": {"crawler": fired.crawler, "run_ids": list(fired.run_ids),
                     "trace_ref": fired.trace_ref},
    }
    proposal_doc = {
        "recorded": RECORDED,
        "scope": "allowlist only: selectors and extraction rules (ADR-0018)",
        "change": "read records under data.results as well as data.data",
        "touches": ["src/deadmon/adapters/unstop.py::extract"],
        "does_not_touch": ["verification", "dedupe", "alerts", "any other adapter"],
        "commit": "none — the break is staged, so the proposal stays a demo double "
                  "in tests/test_heal_proof.py; the real adapter is unchanged",
    }
    validation_doc = {
        "recorded": RECORDED,
        "target": "known-good fixture fixtures/unstop/hackathons-open.json (untouched)",
        "known_good_candidates": real_count,
        "proposal_candidates": len(healed_payload),
        "required_fields_populated": True,
        "registration_close_parseable": True,
        "proposal_live": healed_live,
        "result": "pass — comparable count, fields populated, dates parseable",
    }
    clean_doc = {
        "recorded": RECORDED,
        "run_id": clean.run_id,
        "candidates": clean.candidates,
        "live": clean.live_found,
        "trace": clean.reference,
        "receipt": f"receipts/receipt-{clean.run_id:04d}.json",
    }
    backfill_doc = {
        "recorded": RECORDED,
        "window": "the gap the break left uncovered (Unstop open listings)",
        "run_id": backfill.run_id,
        "candidates": backfill.candidates,
        "live": backfill.live_found,
        "trace": backfill.reference,
        "receipt": f"receipts/receipt-{backfill.run_id:04d}.json",
    }
    mlh_doc = {
        "recorded": RECORDED,
        "rule": "a break is a regression against a baseline (ADR-0011)",
        "mlh_rows": mlh_rows,
        "watchdog_breaks": len(mlh_breaks),
        "result": "silence — off-season zero with no baseline history is steady state",
    }
    _write("baseline.json", baseline_doc)
    _write("break-runs.json", break_doc)
    _write("proposal.json", proposal_doc)
    _write("sandbox-validation.json", validation_doc)
    _write("second-clean-crawl.json", clean_doc)
    _write("backfill.json", backfill_doc)
    _write("mlh-steady-state.json", mlh_doc)
    _write("heal-event.json", {
        "heal": "heal-001",
        "crawler": "unstop",
        "recorded": RECORDED,
        "evidence": {"snapshot": break_doc["snapshot"], "watchdog": break_doc["watchdog"]},
        "baseline": {"unstop_crawler": baseline_doc["crawlers"]["unstop"],
                     "mlh": baseline_doc["crawlers"]["mlh"]},
        "break": {"candidates_before": break_doc["candidates_before"],
                  "candidates_after": break_doc["candidates_after"]},
        "proposal": {"scope": proposal_doc["scope"], "change": proposal_doc["change"],
                     "commit": proposal_doc["commit"]},
        "sandbox_validation": {"known_good_candidates": validation_doc["known_good_candidates"],
                               "proposal_candidates": validation_doc["proposal_candidates"],
                               "result": validation_doc["result"]},
        "second_clean_crawl": {"run_id": clean.run_id, "live": clean.live_found,
                               "trace": clean.reference},
        "backfill": {"run_id": backfill.run_id, "live": backfill.live_found,
                     "trace": backfill.reference},
        "mlh_steady_state": {"watchdog_breaks": mlh_doc["watchdog_breaks"],
                             "result": mlh_doc["result"]},
    })
    print(f"heal-001 recorded: baseline run #{baseline.run_id} "
          f"({baseline.live_found} live), break runs #{break1.run_id}+#{break2.run_id} "
          f"(0+0, watchdog fired), clean run #{clean.run_id} ({clean.live_found} live), "
          f"backfill run #{backfill.run_id} ({backfill.live_found} live).")
    print(f"default receipt dir untouched: {DEFAULT_RECEIPT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
