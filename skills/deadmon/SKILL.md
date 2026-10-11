---
name: deadmon
description: Run the deadmon Scout loop — full crawl plus deadline sweep — and heal a broken crawler through proposal, sandbox validation, commit, and backfill.
---

# deadmon skill

Copy this file into `.claude/skills/deadmon/SKILL.md` (or `.codex/skills/`); it then invokes the Scout loop. Vocabulary follows `GLOSSARY.md`: crawler, proposal, card, subscriber, deadline sweep.

## The Scout loop

The Scout is the one scheduled loop: fetch → extract → verify → dedupe → filter → alert. It runs on two tiers:

1. **Full crawl** (daily) — every crawler replays its recorded corpus and discovers new candidates. The only tier that adds new work.
2. **Deadline sweep** (every few hours) — cheap re-verification over only the cards inside a lead-time window (7 days, 3 days, 24 hours, computed in UTC from the registration close), so the 24-hour lead time can actually fire.

```bash
pip install -e ".[test]"
py -m pytest -q                          # green before any loop work; offline
deadmon-crawl --reset --no-serve --port 8080 --as-of 2026-10-11T00:00:00+00:00
curl http://127.0.0.1:8080/api/feed     # feed vs needs_attention
curl http://127.0.0.1:8080/runs.json    # per-crawler history with trace_ref
```

Port 8080, never 8765 (Windows reserved range). Pin `--as-of` for deterministic replays. Fixtures are added beside the old, never overwritten — a known-good fixture is the validation target (ADR-0015).

## Heal one crawler: break → proposal → sandbox → commit → backfill

1. **Break.** A regression in one crawler's yield against its baseline (ADR-0011). A quiet crawler with no history is steady state, not a break. Confirm via `needs_attention_by_crawler` in `/api/feed` and the crawl run's trace at `/trace/<ref>`.
2. **Proposal.** A change to that crawler's adapter only, against the allowlist (selectors and extraction rules — never new logic, never a file outside the adapter). Reason from the diff between the snapshot and the known-good fixture. At most one heal in flight per crawler; a second break while one runs escalates to the operator with the evidence and the proposal.
3. **Sandbox validation.** Prove the proposal reproduces the known-good fixture: comparable candidate count, required fields populated, dates parseable. Non-empty output is the floor, not the bar. Twice failed → escalation, never a third guess.
4. **Commit.** One commit per green unit, imperative subject ≤72 chars with a glossary scope (`add Unstop crawler`, `heal Unstop crawler` naming the break). Commit the last known-good state before a risky change; pushed history is append-only.
5. **Backfill.** Crawl again over the window the break left uncovered so no registration close inside the gap is silently missed. Verify the gap closed via `/runs.json`, then close the heal event with evidence → proposal → sandbox result → commit ref → backfill count.

Fail closed throughout: any source whose registration close cannot be established stays `unverified` in needs attention — visible, greyed, re-verified next crawl — never asserted as `live`, never deleted.
