# Orchestration prompt — deadmon Slice 1 (autonomous run)

You are running the whole of Slice 1. The user is away until the work is done.
Work until every ticket is resolved or explicitly blocked-with-reason, then
deliver the report in §11. Do not stop to ask questions; §2 is the only place
you are allowed to stop.

## 1. Objective

Complete all eight tickets in `.scratch/slice-1/issues/`.

**Done means:** one command runs the Unstop crawler against the recorded fixture
with **no network access**, verifies what it extracted, stores it, traces the
crawl run, and renders live listings as cards carrying verdict badges on one
server-rendered page — and every ticket file reads `Status: resolved` with the
evidence written into its Comments.

The demoable target, verbatim: **"I crawl Unstop and see live listings with
badges."**

No ticket may be skipped, deferred to a later slice, cut for time, or marked
resolved without evidence. A ticket that genuinely cannot be finished gets
`Status: blocked` with the reason in Comments; the slice still ships and the
report says so plainly.

## 2. Your authority while the user is away

Decide everything yourself. When two options are otherwise equal, take the one
cheaper to reverse, and write the choice into the ticket's Comments.

Stop — and only then — if one of these is true:

- completing the work would require destroying or hand-editing a recorded fixture;
- it would require spending money or creating a third-party account;
- you have found that the architecture itself is wrong, not a detail within it;
- the Python environment is unusable.

Everything else: decide, record, continue. A recorded guess the user can correct
beats a stalled run every time.

## 3. Repository state at handoff

- HEAD: `055751d`; commits `6573c9f`, `dbd7b33`, `3190ec5`, `6b8e994`, all dated
  2026-10-11 — inside the Oct 10–12 evidence window.
- **No git remote is configured**, so `AGENTS.md`'s "push hourly" cannot be
  satisfied. Commit hourly instead and say so in the report. Do not add a remote.
- Ticket 02 is resolved; its fixtures are committed. Do not re-record.
- `untitled.md` is a stray empty untracked file. Leave it alone.
- No package manifest exists yet — you are creating the Python build. `pytest`
  is the runner; `python tools/check_docs.py` is the docs gate that must pass
  after any commit touching docs.

## 4. Read before touching anything, in order

`AGENTS.md` → `GLOSSARY.md` → `.scratch/slice-1/spec.md` →
`.scratch/slice-1/issues/*.md` → `fixtures/README.md` → `docs/PLAN.md`
(Slice 1) and `docs/PRD.md` → ADRs 0001, 0002, 0006, 0007, 0010, 0013, 0015.

## 5. Hard constraints

1. **Vocabulary is settled.** Scout = the loop. Crawler = the per-platform unit.
   Adapter = the code behind the scraper interface. Candidate = extraction
   output. Listing = a candidate carrying a verdict, i.e. one platform's
   *source* for a hackathon. Card = the display unit. Verdicts are exactly
   `live` / `unverified` / `closed`. **The badge reads the verdict word — never
   "verified."**
2. **Where the PRD and glossary disagree, the glossary wins.** The four
   conflicts are in the slice spec.
3. **Fixtures are frozen.** Never modify, overwrite, reformat, or hand-edit
   `hackathons-open.json` — it is the known-good baseline the project's own tests
   are graded against (ADR-0015). New versions are added beside it, never in
   place. Never write a file that pretends to be a recording but isn't.
4. **No network in any test.** Transport failures are *declared test doubles*,
   named as doubles everywhere they appear.
5. **Fail closed.** Never infer, default, or carry forward a deadline the
   pipeline did not read.
6. **One commit per green unit.** Imperative subject ≤72 chars,
   `<scope>: <what>`, body names the ticket number and any ADR.
7. **Entire checkpoints are currently broken** — the `entire` CLI is not on PATH
   so the post-commit hook skips. Don't block on it, don't install it uninvited,
   don't fabricate evidence for it.
8. **A committed `.db` is never the source of truth.** DDL lives in versioned
   schema files.
9. **No single-page-app framework.** One server-rendered page.
10. **Timebox ~6h.** Overrunning means cut scope by the plan's cut list — never
    by skipping the verification stage.

## 6. Recorded facts that will corrupt results if ignored

1. **`oppstatus=closed` does not mean the record says closed.** All 24 records
   still carry `status: "LIVE"` and `regn_open: 1`. Switching on either
   classifies the whole page live and is wrong 24 times. **Only
   `regnRequirements.end_regn_dt` distinguishes a closed registration.**
2. `oppstatus=past`, `all`, `draft` return the *same* page. A fixture's meaning
   comes from its content, not its parameter.
3. Some past records have `end_regn_dt` *after* `end_date`. Both parse, both
   past, verdict still `closed`.
4. `hackathons-closed.json` holds **24** records despite `per_page=25`. Don't
   assert 25.
5. Listing order is not date-sorted; paging is not a time filter.
6. All dates carry `+05:30` — normalise to UTC at extraction (ADR-0013).
7. Registration close is `regnRequirements.end_regn_dt`, **never** top-level
   `end_date`.
8. Source URL is `seo_url` (absolute), not `public_url` (relative).
9. `prizes` can be `[]`. Empty is legitimate, not missing.
10. **`unverified` is not recordable.** Cover it with a declared double
    (`fixtures/unstop/hackathons-unverified.json`, `"TBA"` dates), labelled as a
    double. Ticket 04 creates it.

## 7. Task graph and execution plan

```
02 ── resolved at handoff ──────────────────────┐
01 ── gate ──→ 03, 04, 05, 06, 07 ──→ 08       │
                  (parallel wave)              │
```

Wave 0 is done. **Wave 1:** ticket 01 alone — it establishes the module layout
every later ticket's ownership is expressed in. **Wave 2:** 03–07 together,
independent by design. **Wave 3:** ticket 08, the demo moment.

Execution strategy in descending preference: (1) run 03–07 as parallel workers
with self-contained specs; (2) if you can't isolate them safely, run them
**sequentially — correctness first**, sequential still completes the slice;
(3) if dispatching subagents, give each its ticket's full text plus §5 and §6,
and require back the diff summary, the test command and output, and the commit
subject it would use.

**Ownership boundaries — the rule that makes the wave safe.** Each worker edits
only its own module, its own tests, and its own ticket file. Module names come
from whatever layout 01 establishes — express ownership in those terms, never
guess a path. Nobody touches `AGENTS.md`, `GLOSSARY.md`, `fixtures/`, `tools/`,
or another ticket's file. If two tickets need the same edit, the lower number
owns it and the other waits.

## 8. Dispatch spec shape

Copy verbatim from the ticket file: **What to build**, **Blocked by**, and every
acceptance criterion — plus the applicable constraints from §5 and traps from
§6. Do not paraphrase the criteria; the worker has to verify itself with no
access to this conversation.

## 9. Landing rules

1. Claim: `Status: claimed`.
2. Build test-first, one red-green slice at a time. Smallest applicable
   validation: `pytest`, plus the docs gate when docs are touched.
3. Self-review the diff against every criterion before committing.
4. Commit one green unit, naming the ticket number.
5. Resolve: `Status: resolved`, append to `## Comments` what was built, the
   validation command and output summary, the commit SHAs, and every judgment
   call.

A ticket is resolved only when each criterion is satisfiable from the evidence
you wrote down. "Looks right" is not evidence.

## 10. If something blocks

`Status: blocked` with a written reason, then continue with the others. Never
mark resolved to keep the plan tidy. Never delete a ticket, fixture, or test to
make something pass. If the architecture is wrong, stop that ticket, record the
finding, continue with everything that doesn't depend on it, and make it the
first item of the report.

## 11. Completion criteria and report

- [ ] Every ticket reads `Status: resolved` (or `blocked` with a written reason)
- [ ] `pytest` green with no network anywhere in the suite
- [ ] `python tools/check_docs.py` passes
- [ ] One command crawls Unstop against the fixture, no network, ≥1 live listing
      rendered as a card in the feed
- [ ] The run writes a crawl-run row, a trace, and a trace link on the dashboard
- [ ] The trace's live-found and closed-found counts agree with the dashboard
- [ ] Tree clean apart from `untitled.md`; every commit dated Oct 10–12 and naming
      its ticket

Report in order: ticket-by-ticket outcome with SHAs and one line of evidence; any
blocked ticket and why; every judgment call made while away, with reasoning; the
demo command and how to run it; what a reviewer should check first; the state of
Entire (expected: still broken).
