# Goal: heal watchdog (zero-listings detection)

Compiled with `to-goal` from the Slice 4 spec in conversation + repo evidence.
Read-only compile; nothing here is implemented. Paste the Goal block into a
fresh session to execute. Scope: detection only — proposal, sandbox, loop,
and schema-spike detection are explicitly out.

## Readiness checklist (compiler-side, not part of the paste block)

- [x] Source is agent-ready: Slice 4 contract + rails, `docs/PLAN.md:34`
  (zero-listings twice), ADR-0016, ADR-0017, `run_history()` row shape
  confirmed in code. Trigger reads `listings_found` (candidates are not
  stored; PLAN says zero-*listings*).
- [x] Unblocked: pure function + offline tests; no key, no network.
- [x] Exactly one bounded frontier: watchdog only.
- [x] Pre-implementation HEAD: `7a1bf59`.
- [x] Criteria classified: complete (rows expose `listings_found`/
  `trace_ref`), incomplete (no module/type/tests), unverified
  (schema-spike signal — deferred).
- [x] Validation: `.\.venv\Scripts\python.exe -m pytest -q` (122 baseline),
  `.\.venv\Scripts\python.exe tools/check_docs.py`.
- [x] Permissions preserved: no ticket files, `.env` keys never printed or
  committed, suite offline, one commit per unit.
- [x] Every criterion decidable from observable evidence.

## Goal

```markdown
## Goal

Watchdog that fires a Break on two consecutive zero-listing finished runs
for one crawler, and stays silent otherwise. No proposal, no sandbox, no
loop — detection only.

## Current state

- Branch: main
- HEAD (comparison baseline): 7a1bf59
- Dirty / untracked files to protect: M .env.example (uncommitted doc edit,
  no secrets — leave untouched)
- Evidenced complete:
  - `Store.run_history()` returns per-crawler rows with `listings_found`,
    `status`, `trace_ref` (`src/deadmon/storage.py:127`)
  - `finish_run()` defaults `listings_found` to `live_found + closed_found`
    (`src/deadmon/storage.py:86`)
  - Rails settled: ADR-0016 one heal in flight per crawler, ADR-0017 heal
    loop instrumented; verification stays fail-closed
- Known gaps:
  - No watchdog module, no Break type, no tests
  - Schema-spike trigger deferred: no schema-failure signal is stored
    anywhere yet; this goal covers zero-listings only
  - Downstream (proposal, sandbox, loop, wiring) explicitly out of scope
- Existing failures: none (122 passed)

## Execution order

1. Red: `test_watchdog_fires_on_two_consecutive_zero_listing_runs` — two
   finished rows, same crawler, `listings_found=0` → one Break carrying
   crawler + both run ids + latest trace_ref.
2. Red: silence cases — zero then healthy, healthy then zero, lone zero,
   zeros split across two crawlers, interrupted (unfinished) rows ignored.
3. Green: minimal pure module (suggested `src/deadmon/heal/watch.py`;
   takes rows, returns Breaks — no Store import, no I/O).
4. Full suite + docs-check green, then one commit per repo convention.

## Completion criteria

- [ ] Two consecutive zero-listing finished runs for one crawler yield
      exactly one Break with crawler, both run ids, latest trace_ref
- [ ] Zero-then-healthy, healthy-then-zero, lone zero, cross-crawler zeros,
      and unfinished rows all yield silence
- [ ] Watchdog is I/O-free (rows in, Breaks out; no Store/network imports)
- [ ] Ran the smallest applicable validation:
      `.\.venv\Scripts\python.exe -m pytest tests/test_heal_watch.py -q`
      during development, full `.\.venv\Scripts\python.exe -m pytest -q`
      (122 + new, zero failures) before committing
- [ ] Reviewed the final diff against the source criteria and recorded baseline
- [ ] Commit only after all selected criteria pass and the source context or user authorizes a commit
- [ ] Workspace is clean except for this goal's changes (`.env.example`
      modification and any unrelated files untouched)

## Constraints

- do not open a pull request, merge, close issues, or edit tracker state;
  push to origin/main after the green commit per AGENTS.md hourly-push rule
  (rewritten from the push prohibition — source: AGENTS.md commits section)
- do not modify unrelated dirty or untracked files (notably .env.example)
- do not implement proposal, sandbox, loop, or wiring early
- use the agreed validation seam (fake Store rows, never a live DB) and
  prefer behavior evidence over implementation details
- always run the smallest applicable validation during development
- require full validation only because the change touches shared run-history
  semantics the whole dashboard reads
- review the final diff against the source criteria and recorded baseline
  before committing; no review tool needed for a pure function this size
- commit only after all selected criteria pass and the source context or user authorizes a commit
- Validation breadth: full
  Reason: new module reads the run-history contract shared by crawl,
  dashboard, and future heal steps
- Never print, log, or commit secrets; `.env` is gitignored and stays that way

## Context

- Approved source: Slice 4 spec from this conversation (contract + rails +
  first-red acceptance) constrained by docs/PLAN.md:34 zero-listings twice
- Design docs: docs/adr/0016-one-heal-in-flight-per-crawler.md,
  docs/adr/0017-heal-loop-is-itself-instrumented.md, GLOSSARY.md (crawler,
  run, trace vocabulary)
- Agreed validation seam: fabricated `run_history()`-shaped rows
  (id/crawler/status/listings_found/trace_ref), offline suite
- Inspect first: `src/deadmon/storage.py` (run_history, finish_run),
  `tests/test_crawl.py` (workspace/store fixture pattern),
  `tests/conftest.py` (`_no_network` autouse guard)
```

## Session recommendation

- Session: fresh
- Capability: Standard
- Intensity: Low
- Reason: deterministic pure function over stored rows with cheap offline verification and clear repo patterns.
