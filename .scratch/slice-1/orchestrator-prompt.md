# Orchestration prompt — deadmon Slice 1 (autonomous run)

> Handoff contract for a coordinator session. The user is away until the work is
> done. Work until every ticket is resolved or explicitly blocked-with-reason,
> then deliver the report in §11. Do not stop to ask questions; §2 is the only
> place you are allowed to stop.

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

- HEAD: `dbd7b33` — "slice-1: publish the eight tracer-bullet tickets"
- Commits on `main`: `dbd7b33`, `3190ec5`, `6b8e994`, all dated 2026-10-11, inside
  the Oct 10–12 evidence window.
- **No git remote is configured**, so `AGENTS.md`'s "push hourly" cannot be
  satisfied. Commit hourly instead, and say so in the final report. Do not add a
  remote.
- **Uncommitted at handoff:** ticket 02's two new fixtures and the
  `fixtures/README.md` provenance rows. Commit these as your first task.
- `untitled.md` is a stray empty untracked file. Leave it alone — do not delete
  it, do not ignore it, do not commit it.
- There is no package manifest yet. You are creating the Python build: `pytest`
  is the test runner, and `python tools/check_docs.py` is the docs gate that must
  pass after any commit that touches docs.

## 4. Read these before touching anything, in this order

1. `AGENTS.md` — commit discipline, evidence rules, vocabulary rules
2. `GLOSSARY.md` — the vocabulary and each term's `_Avoid_` list
3. `.scratch/slice-1/spec.md` — this slice's settled decisions
4. `.scratch/slice-1/issues/*.md` — the tickets, in number order
5. `fixtures/README.md` — provenance and the never-overwrite rule
6. `docs/PLAN.md` (Slice 1) and `docs/PRD.md` — the source these came from
7. The ADRs the tickets name: 0001, 0002, 0006, 0007, 0010, 0013, 0015

## 5. Hard constraints

Violating any of these corrupts the evidence, not just the code.

1. **Vocabulary is settled.** Scout = the scheduled loop. Crawler = the
   per-platform unit of work. Adapter = the code behind the scraper interface.
   Candidate = what extraction produces. Listing = a candidate carrying a
   verdict, which is a platform's *source* for a hackathon. Hackathon = the
   event. Card = the dashboard's display unit. Verdicts are exactly `live`,
   `unverified`, `closed`. **The badge reads the verdict word — never
   "verified."**
2. **Where the PRD and the glossary disagree, the glossary wins.** The four
   conflicts are written out in `.scratch/slice-1/spec.md`.
3. **Fixtures are frozen.** Never modify, overwrite, reformat, or hand-edit
   `fixtures/unstop/hackathons-open.json` — it is the known-good baseline the
   project's own tests are graded against (ADR-0015). New fixture versions are
   added beside it, never in place. Never write a file that pretends to be a
   recording but isn't.
4. **No network in any test.** Tests replay fixtures. A transport failure is a
   *declared test double*, named as a double in its contents and everywhere it
   appears in tests.
5. **Fail closed.** Never infer, default, or carry forward a deadline the
   pipeline did not read.
6. **One commit per green unit.** Subject imperative, ≤72 chars,
   `<scope>: <what>`; the body names the ticket number and any ADR. There is no
   remote, so commit rather than push.
7. **Entire checkpoints are currently broken** — the `entire` CLI is not on
   PATH, so the post-commit hook skips on every commit. Do not block on it, do
   not install it uninvited, and do not fabricate checkpoint evidence. Mention
   it in a commit body only where it matters.
8. **A committed database file is never the source of truth.** DDL lives in
   versioned schema files.
9. **No single-page-app framework** on the dashboard. One server-rendered page.
10. **Timebox is ~6h.** If a ticket overruns, cut scope by `docs/PLAN.md`'s cut
    list — never by skipping the verification stage, the self-heal demo, the
    trace pair, the business plan, or the video.

## 6. Recorded facts that will corrupt results if ignored

Ticket 02 recorded two fixture versions on 2026-10-11. These were verified
against the saved bytes and are not guesses:

1. **`oppstatus=closed` does not mean the record says closed.** All 24 records in
   `hackathons-closed.json` still carry `status: "LIVE"` and `regn_open: 1`. An
   adapter or a verification stage that switches on `status` or `regn_open`
   classifies the whole page live and is wrong 24 times. **Only
   `regnRequirements.end_regn_dt` distinguishes a closed registration.**
2. `oppstatus=past`, `all`, and `draft` return the *same* page; they differ only
   in the echoed pagination string. A fixture's meaning comes from its content,
   not from the parameter that fetched it.
3. In the past fixture, some records have `end_regn_dt` *after* `end_date`. Both
   parse, both are past, and the verdict is still `closed`.
4. `hackathons-closed.json` holds **24** records despite `per_page=25` — that is
   what the endpoint served. Do not write a test asserting 25.
5. Listing order is not date-sorted; paging is not a time filter.
6. All dates carry `+05:30` — normalise to UTC at extraction (ADR-0013).
7. **Registration close is `regnRequirements.end_regn_dt`, never the top-level
   `end_date`**, which is a different field that happens to coincide on some
   records.
8. The source URL is `seo_url` (absolute), not `public_url` (relative).
9. `prizes` can be `[]`. Empty is a legitimate value, not a missing field.
10. **`unverified` is not recordable** from this platform: no status filter
    produces an absent or unparseable date. Cover it with a declared test double
    (`fixtures/unstop/hackathons-unverified.json`, `"TBA"` dates), labelled as a
    double in its contents and wherever it appears in tests. Never present it as
    recorded evidence.

## 7. Task graph and execution plan

```
02 ── resolved at handoff ──────────────────────┐
01 ── gate ──→ 03, 04, 05, 06, 07 ──→ 08       │
                  (parallel wave)              │
```

- **Wave 0:** commit ticket 02's fixtures, mark 02 resolved. One task, do it first.
- **Wave 1:** ticket 01 alone. It establishes the module layout, and every later
  ticket's ownership is expressed in terms of that layout.
- **Wave 2:** tickets 03, 04, 05, 06, 07 together. They are independent by
  design — that is the entire reason the contracts in 01 exist.
- **Wave 3:** ticket 08, wiring them into the demo moment.

Execution strategy, in descending order of preference:

1. Run 03–07 as parallel workers, each with a self-contained spec (§8), each
   confined to its own module and its own tests.
2. If you cannot isolate them safely, run them **sequentially** — correctness
   first. Sequential still completes the slice; parallel only makes it faster.
3. If you dispatch subagents, give each the full text of its ticket plus §5 and
   §6 of this prompt, and require each to return: the diff summary, the test
   command and its output, and the commit subject it would use.

**Ownership boundaries — the rule that makes the wave safe.** Each worker edits
only its own module, its own tests, and its own ticket file. Module names come
from whatever layout ticket 01 establishes; express ownership in those terms and
never guess a path. No worker touches `AGENTS.md`, `GLOSSARY.md`, `fixtures/`,
`tools/`, or another ticket's file. If two tickets appear to need the same edit,
the earlier-numbered one owns it and the other waits.

## 8. Dispatch spec shape

Every work item you hand out must contain, copied verbatim from the ticket file:
**What to build**, **Blocked by**, and every acceptance criterion — plus the
constraints from §5 and the traps from §6 that apply to it. Do not paraphrase the
acceptance criteria; the worker has to be able to verify itself against them with
no access to this conversation.

## 9. Landing rules

For each ticket, in this order:

1. **Claim** — set `Status: claimed` in the ticket file.
2. **Build test-first** — one red-green slice at a time. The smallest applicable
   validation is `pytest`, plus `python tools/check_docs.py` whenever docs are
   touched.
3. **Self-review the diff** against every acceptance criterion before committing.
4. **Commit one green unit**, naming the ticket number in the body.
5. **Resolve** — set `Status: resolved` and append to `## Comments`: what was
   built, the validation command and its output summary, the commit SHAs, and
   every judgment call you made.

A ticket is resolved only when each acceptance criterion is satisfiable from the
evidence you wrote down. "Looks right" is not evidence.

## 10. If something blocks

- A ticket blocked by a real impossibility: set `Status: blocked`, write why in
  Comments, and continue with the others. The slice can still be demoable with one
  verdict's fixture missing — say so in the report rather than hiding it.
- **Never** mark a ticket resolved to keep the plan tidy.
- **Never** delete a ticket, a fixture, or a test to make something pass.
- If you find the architecture is wrong, stop that ticket, record the finding,
  continue with everything that does not depend on it, and make it the first item
  of the report.

## 11. Completion criteria and the report

**All of these must be true when you finish:**

- [ ] Every ticket file reads `Status: resolved` (or `blocked` with a written
      reason — count those in the report)
- [ ] `pytest` is green, with no network access anywhere in the suite
- [ ] `python tools/check_docs.py` passes
- [ ] One command crawls Unstop against the recorded fixture, no network, and
      produces at least one live listing rendered as a card in the feed
- [ ] The run writes a crawl-run row, a trace, and a trace link visible on the
      dashboard
- [ ] The trace's live-found and closed-found counts agree with the dashboard
- [ ] Working tree clean apart from `untitled.md`; every commit dated Oct 10–12
- [ ] Every commit message names its ticket

**Report, in this order:**

1. Ticket-by-ticket outcome: status, commit SHA, one line of evidence.
2. Any `blocked` ticket and the reason.
3. Every judgment call you made while the user was away, with the reasoning.
4. The demo command and how to run it.
5. What a reviewer should check first.
6. The state of Entire (expected: still broken, CLI not on PATH).
