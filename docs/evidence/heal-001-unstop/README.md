# heal-001 — Unstop break, heal, second clean crawl, backfill

Recorded 2026-10-12. Offline throughout: every run replays a recorded
fixture, never the network.

## The story

1. **Baseline.** The Unstop crawler yields 25 live listings from the
   known-good fixture (`fixtures/unstop/hackathons-open.json`). The MLH
   crawler has no baseline history — off-season quiet is steady state.
   See `baseline.json`.
2. **Break.** The platform serves a changed layout overnight (HTTP 200,
   records moved, zero candidates). The crawler yields 0 on two
   consecutive finished crawl runs. The watchdog fires one break carrying
   the crawler, both run ids, and the latest trace ref. See
   `break-runs.json`.
3. **Proposal.** The change reads records under the new key as well as
   the old one — selectors and extraction rules only, per the allowlist
   (ADR-0018). Verification, dedupe, and alerts are untouched. The break
   is staged, so the proposal stays a demo double and the real adapter is
   unchanged. See `proposal.json`.
4. **Sandbox validation.** The proposal reproduces the known-good shape:
   25 candidates, required fields populated, registration closes
   parseable, 25 live. See `sandbox-validation.json`.
5. **Second clean crawl.** The healed crawler yields 25 live from the
   changed layout. See `second-clean-crawl.json` and `traces/`.
6. **Backfill.** The gap window is re-crawled: 25 live, nothing silently
   missed. See `backfill.json` and `traces/`.
7. **MLH steady state.** One off-season zero run with no baseline history
   yields watchdog silence — not a break, per the baseline rule
   (ADR-0011). See `mlh-steady-state.json`.

## Verify (copy, paste, believe)

```console
py -m pytest -q tests/test_heal_proof.py
py -m deadmon.receipts docs/evidence/heal-001-unstop/receipts/receipt-000*.json
py -m pytest -q
```

The full roll-up is `heal-event.json`: evidence, baseline, break,
proposal, sandbox validation result, commit ref, backfill count — one
heal event, never several.

## Honesty notes

- The changed-layout snapshot is **constructed, not recorded**: Unstop did
  not change its layout overnight. It says so in its own contents, in its
  filename, and in `fixtures/README.md`. The known-good fixture is
  untouched and still yields 25.
- Receipts count crawl runs, not cards: 5 runs, 5 receipts, 5 traces.
- `deadmon-receipt-check` is the same program as `py -m deadmon.receipts`.
