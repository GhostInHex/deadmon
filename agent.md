# agent.md — drive deadmon with one fetch

Copy-prompt: `Read agent.md in the deadmon repo, run the preflight, then crawl: deadmon-crawl --reset --no-serve --port 8080 --as-of 2026-10-11T00:00:00+00:00.`

deadmon watches hackathon platforms so a student developer never misses a registration close. The Scout is the one scheduled loop (daily full crawl plus a frequent deadline sweep); per-platform work belongs to a crawler; per-platform HTML knowledge belongs to the adapter behind the scraper interface. Start here: `GLOSSARY.md` wins over every older doc, and `fixtures/README.md` names the recorded corpus before any adapter work.

## Preflight

```bash
py --version            # 3.11+
pip install -e ".[test]"
py -m pytest -q         # 114 passed with tracing extra, else 112 passed 2 skipped; offline, no network
dir fixtures            # recorded corpus present; never overwrite a fixture (ADR-0015)
```

Optional: set `NEATLOGS_API_KEY` to trace a crawl run to neatlogs; without it every trace falls back to a local JSON sink and the dashboard links still resolve.

## Crawl commands

```bash
deadmon-crawl --reset --no-serve --port 8080 --as-of 2026-10-11T00:00:00+00:00
deadmon-crawl --port 8080            # crawl the corpus, then serve the dashboard on 127.0.0.1:8080
py -m deadmon.crawl --help           # every flag: --fixtures --db --traces --host --port --as-of --reset --no-serve
```

Use port 8080, not 8765: 8765 falls inside a Windows reserved range and the server dies with `WinError 10013`. Pin `--as-of` to replay the recorded state deterministically. Runs are append-only; `--reset` is the explicit opt-out for a clean demo.

## Machine-readable (--json) commands

Stdout prints one machine-parseable line per crawl run (`<crawler> run #<id> candidates=.. live=.. closed=.. unverified=.. trace=..`) plus a totals line; no network is used. The same view model is JSON over HTTP:

```bash
curl http://127.0.0.1:8080/api/feed   # feed + needs_attention + needs_attention_by_crawler + runs
curl http://127.0.0.1:8080/runs.json  # crawl-run history with trace_ref per run
curl http://127.0.0.1:8080/trace/<trace_ref>  # one crawl run's trace document
```

Python owns every fact; the Next.js app only types and fetches (`apps/web/src/lib/api.ts` mirrors `deadmon.dashboard.view_as_json` field for field). Every crawl run emits a numbered hashed receipt to `.runs/receipts/` (local JSON, no login wall); `deadmon-receipt-check` verifies them — an edited receipt fails.

## Error codes

| Code | Where | Meaning |
|---|---|---|
| `0` | process exit | crawl done (and dashboard served until Ctrl-C, if serving) |
| `2` | process exit | CLI usage error from argparse (unknown flag, bad value) |
| `1` | process exit | runtime failure: missing fixture dir, locked DB, unhandled traceback |
| `200` | HTTP | `/`, `/api/feed`, `/runs.json`, `/trace/<ref>` served |
| `404` | HTTP | unknown route; also a trace page with no stored document says so in the body |

Data contract: verification yields exactly one verdict per source — `live`, `unverified`, or `closed`. An `unverified` record is never counted as a live card (ADR-0007).

## Fail-closed contract

When verification cannot establish a registration close, the verdict is `unverified` — deadmon never infers, defaults, or carries forward a close it did not read. Blocked pages, login walls, and rate limits map to `unverified`, never hidden: the card stays visible, greyed, in needs attention, and is re-verified on the next crawl. A quiet crawler is steady state, not a break; a break is a regression against that crawler's baseline (ADR-0011). A heal is a proposal against the adapter allowlist, proven in sandbox validation against the known-good fixture, committed, then followed by a backfill over the gap.
