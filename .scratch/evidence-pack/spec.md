# Evidence pack — copy firstrun's packaging, beat him on deadlines

Source of truth: firstrun teardown P0 1-5 (2026-10-11),
`docs/PLAN.md` Slice 5 + Slice 6, `GLOSSARY.md` + ADRs.
Read `GLOSSARY.md` and `fixtures/README.md` before any ticket.

## Problem Statement

firstrun wins judges by packaging: a `/judges` page mapping 7 rows to
rubric %, an `evidence/` folder with traces + receipts + screenshots,
`agent.md` + `llms.txt` one-fetch docs, numbers everywhere ($0.0178/run,
384 passed), and a double-run proof (break -> heal -> 2nd clean container).

deadmon has the stronger claim — `Deadlines that stay true. Literally.` —
full crawl + deadline sweep, fail-closed verification, heal + backfill proof
— but it is scattered across `docs/`, `fixtures/`, and three Next.js routes.
A judge cannot verify it in 60 seconds today.

## Solution

Clone his evidence machine onto deadmon's vocabulary: a `/judges` route
with rubric weights + v1 vs v2 table + receipt count + copy-paste verify
commands; hero one-liner `Deadlines that stay true. Literally.`;
`agent.md` + `llms.txt` + `skills/deadmon/SKILL.md`; a versioned evidence
pack (break -> heal -> 2nd clean crawl + backfill, local JSON, no login
wall) with numbered hashed receipts; costs everywhere `$0.00/crawl
stdlib-only` vs his `$0.018`, tiers from `docs/business-plan.md` kept
honest as modelled not measured.

Differentiate on time + trust + self-heal. Attack his known-limits gaps:
blocked pages -> `unverified`, kill-mid-run resume.

## Status

Status: ready-for-agent
## User Stories

1. As a judge, I want a `/judges` page mapping each claim to a rubric % weight, so that I can score deadmon in 60 seconds.
2. As a judge, I want copy-paste verify commands on `/judges`, so that I can check every claim without reading code.
3. As a judge, I want a v1 vs v2 trace-pair table on `/judges`, so that I can see the before/after improvement with numbers.
4. As a judge, I want a receipt count + hash check command on `/judges`, so that I trust the evidence was not edited.
5. As a visitor, I want the hero to read `Deadlines that stay true. Literally.`, so that I remember deadmon as deadlines vs his docs.
6. As a visitor, I want a comparison table vs firstrun/Copilot on the landing, so that I see proves-deadline-every-day plus heals vs proves-doc-once.
7. As a visitor, I want a pricing banner `$0.00/crawl stdlib-only`, so that I see the cost edge vs his `$0.018`.
8. As an agent builder, I want `agent.md` as a one-line copy-prompt, so that I can drive deadmon from Claude/Cursor/Codex.
9. As an agent builder, I want `llms.txt` as a one-fetch doc, so that I do not crawl five pages.
10. As an agent builder, I want preflight + `--json` commands + error codes in `agent.md`, so that I know the fail-closed contract upfront.
11. As an operator, I want a `skills/deadmon/SKILL.md` copyable into `.claude/skills/`, so that the Scout loop is agent-invokable.
12. As an operator, I want every crawl run to emit a numbered receipt with a hash, so that evidence is countable proof.
13. As an operator, I want a receipt verify path, so that an edited receipt fails verification.
14. As an operator, I want a double-run proof (break -> heal -> 2nd clean crawl + backfill) as trace + local JSON, so that the demo needs no login wall.
15. As an operator, I want Unstop 25->0 overnight kept as the break demo and MLH off-season 0 kept as steady-not-break, so that baseline vs break stays honest per ADR-0011.
16. As a subscriber, I want blocked pages to stay `unverified` and visible in needs attention, so that a login wall never silently drops a deadline.
17. As a contributor, I want fixtures versioned beside the old never overwritten, so that a known-good baseline stays the validation target per ADR-0015.
18. As a contributor, I want `PRODUCT.md` + `hackathon.md` build log in repo, so that the build narrative is auditable like his.

## Implementation Decisions

- The Scout stays the one scheduled loop (daily full crawl + frequent deadline sweep); per-platform work stays the crawler; per-platform HTML knowledge stays the adapter behind the scraper interface.
- Verification stays per source with exactly one verdict: `live`, `unverified` (indeterminate), or `closed`. Blocked/login/rate-limit maps to `unverified`, never hidden, shown greyed in needs attention.
- The dashboard keeps two groups: feed (`live`) and needs attention (`unverified`). `/judges` is a third marketing-evidence route, not a third feed group.
- Cards stay one per hackathon; sources stay one listing per platform claim (ADR-0003, ADR-0010). Receipts count crawl runs, not cards.
- A break stays a regression against a per-crawler baseline (ADR-0011), not an absence. MLH off-season zero is steady; Unstop 25->0 overnight is the break demo.
- A heal stays a proposal against an allowlist (selectors/extraction rules only), validated in sandbox, committed, then backfill re-crawls the gap. At most one heal in flight per crawler.
- Evidence files live versioned under `fixtures/`, `.scratch/`, `docs/evidence/` per `.gitignore`; a legit page change adds a new fixture beside the old and links both.
- Web work stays in Next.js (Python serves JSON per ADR-0020); Python owns every fact, web only types and fetches. No fact typed into JSX.
- Copy uses glossary words: `crawler` not agent, `proposal` not fix, `card` not listing, `subscriber` profile, `deadline sweep` not re-crawl.
- Costs stay honest: `$0.00/crawl stdlib-only` is modelled (no model calls on current crawl path), tiers cite `docs/business-plan.md` as modelled draft never measured traction.
## Testing Decisions

- Good test = behavior through public interfaces (HTTP route, CLI output,
  file presence + hash), never internals; expected values from known-good
  fixtures or worked examples, never recomputed the way the code does.
- Web seam (highest): Next.js route rendering for `/judges`, `agent.md`,
  `llms.txt` — rubric % table present, verify commands copy-pasteable,
  hero one-liner exact, comparison + cost banner present.
- Evidence-pack seam: versioned files in `docs/evidence/` + `fixtures/` —
  new versions beside old never overwritten; receipts carry hash and
  verify; before/after traces both present. Rule: ADR-0015.
- CLI seam: `deadmon-crawl --json` receipt/cost output — machine-readable
  verdict counts + cost fields, stable across stdlib-only path.
- No live-network tests; the corpus is recorded fixtures.

## Out of Scope

- Sitemap discovery, server watch, countdown closes-in-2d-4h (P2 roadmap).
- Login-gated proof, overwriting fixtures, claiming `live` when
  fixture-backed, rewriting git history.
- Inbound Telegram commands, weekly digest, new platforms beyond the six
  recorded crawlers.
- `unstop-endpoint.md` structured endpoint doc (P1, only if P0 green).
- Kill-mid-run resume + timeouts unless P0 1-5 demoable first.

## Further Notes

- Steal his packaging: `PRODUCT.md` + `hackathon.md` + `AGENTS.md` log,
  `skills/*/SKILL.md`, `evidence/` moat, `doctor --json` preflight + env
  table, ask-once rule, honest `known-limits.md`, numbers everywhere,
  Entire checkpoints, upstream PRs, failure stories with numbers.
- Differentiate on time + trust + self-heal: he proves a doc once,
  deadmon proves a deadline every day, catches moves, heals breaks,
  pings before close.
- Demo safety: every beat recorded against fixtures; video pre-recorded
  never live; PNG fallback for login-gated traces.
- Commits: one per green unit, imperative <=72 chars, scope from glossary;
  `wip:` for in-flight; fixtures versioned never overwritten; history
  append-only.
