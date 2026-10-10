## Before you build

- **Slice 1's data path is undecided.** Devfolio serves no listing data in HTML — the grid is
  client-rendered and `api.devfolio.co` returns 422 for every parameter shape tried. Recorded
  fixtures prove it. Read [`fixtures/README.md`](fixtures/README.md) before writing an adapter;
  it names the three options (render the page, find the XHR, or ship Slice 1 on another platform).
- **The PRD predates the glossary and contradicts it.** Where they disagree, `GLOSSARY.md` wins.
  Four facts an agent gets wrong without them, because each has a natural wrong answer:
  - One hackathon, **many sources** — a deduped event and each platform's claim about it are
    different things ([ADR-0003](docs/adr/0003-hackathon-has-many-sources.md))
  - Verification is **per source**, and yields exactly one verdict: `live`, `unverified`
    (indeterminate — we could not find out), or `closed`
  - The dashboard has **two groups**: the feed (`live`) and needs attention (`unverified`)
  - Profile belongs to a **subscriber**; tables are plural from the first commit
    ([ADR-0006](docs/adr/0006-profile-is-per-subscriber.md))

Read the ADR before changing any of these. They were settled against real alternatives; the
rejected options are recorded in the same files. 19 decisions, one file each.

## Vocabulary

`GLOSSARY.md` — 45 terms with an `_Avoid_` list each. Two rules that carry most of the weight:

- **Use the glossary's word.** `crawler`, not "agent"; `proposal`, not "fix"; `card`, not "listing".
- **When the glossary names a decision, follow it.** A decision reached by interview or code is
  settled; changing one means writing a new ADR that supersedes it, not quietly editing code.

## Commits

The repo's history is a scoring artifact: the evidence checklist asks for a **public repo with
commits dated Oct 10–12** ([`docs/PLAN.md`](docs/PLAN.md) → evidence checklist).

- **One commit per green unit.** One adapter, one slice step, one ADR, one bug. A subject line
  that cannot summarise it means it was more than one unit.
- **Subject:** imperative, ≤72 chars, `<scope>: <what>`, scope from glossary vocabulary —
  *"add Unstop crawler"*. Body points at the slice, ADR, or `.scratch/` ticket; Slice 4's
  self-heal commits name the break they repair.
- **Push hourly**, and at the end of every slice.
- **Commit the last known-good state before a risky change** — a selector rename, a scraper
  interface refactor, or starting Slice 4's deliberate break.
- **In-flight work gets a `wip:` prefix**, and a pushed branch ends on a settled commit.
- **Fixtures are versioned.** Add a new version beside the old one; a known-good fixture is the
  validation target, so overwriting it lets the agent edit its own test
  ([ADR-0015](docs/adr/0015-validation-against-known-good-fixture.md)).
- **Pushed history is final.** Append-only — Entire records its session graph on top of git, and
  rewriting the graph breaks the evidence ([`docs/SPONSORS.md`](docs/SPONSORS.md) → Entire).
- `.gitignore` keeps the DB, secrets, caches and run output out of the tree while preserving the
  evidence set (`fixtures/`, `.scratch/`, `docs/evidence/`). Read it before adding a path.
- Every commit gets an Entire checkpoint via its hooks; `entire enable` runs once, before the
  first commit.

## Issue tracker

Issues live as markdown under `.scratch/<feature>/` — see [`docs/agents/issue-tracker.md`](docs/agents/issue-tracker.md).