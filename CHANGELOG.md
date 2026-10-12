# Changelog

One entry per shipped unit, newest first. Every entry names its commit;
`git show <hash>` is the audit trail. Vocabulary follows `GLOSSARY.md`.

## 2026-10-12

- **Deploy: EC2 crawl service + Vercel app live** (`a262ad4`). The crawl
  runs on EC2 (systemd unit, SQLite, traces, `/api/feed`); the Next.js
  dashboard runs on Vercel with `apps/web` as the project root. Evidence
  screenshots in `docs/evidence/`.
- **Heal proof pack, ticket 05** (`ed0e8ef`). heal-001: staged Unstop
  25-to-0 snapshot beside the untouched known-good fixture, watchdog
  fires, allowlist-scoped proposal, sandbox validation 25-vs-25, second
  clean crawl 25 live, backfill 25 live, MLH zero stays steady state.
  Plus `PRODUCT.md`, `hackathon.md`, `docs/known-limits.md`.
- **Evidence pack frontier, tickets 01–04** (`1d6a12a`). `/judges` route
  with rubric weights and v1-vs-v2 trace pair; hero `Deadlines that stay
  true. Literally.` with comparison and `$0.00/crawl` banner;
  `agent.md`, `llms.txt`, `skills/deadmon/SKILL.md`; numbered hashed
  receipts per crawl run with `deadmon-receipt-check`.
- **Web polish** (`2da8668`–`099bbff`). Contrast and landmark fixes on
  badges, labels, needs attention, nav/footer.
- **Heal watchdog, detection only** (`12a5535`). Two consecutive
  zero-listing finished runs for one crawler yield one break; unfinished
  runs never count. Proposal, sandbox, and loop stay out.
- **Slice 2: five more crawlers** (`8db4476`–`7a1bf59`). HackerRank,
  hackathon.com, lablab, MLH, GenAI.works behind the scraper interface,
  one command runs all, adapter tests, recorded provenance and dead ends.
- **Dashboard moves to Next.js** (`885439e`, ADR-0020). Python serves
  JSON (`/api/feed`, `/runs.json`, `/trace/<ref>`); web types and
  fetches, never types a fact.

## 2026-10-11

- **Slice 1 pipeline** (`6b8e994`–`d8a5bd0`). Unstop crawler over the
  recorded corpus: 77 candidates in, 25 live, 49 closed, 3 unverified
  (one declared double); 22 feed cards, 3 needing attention. One verdict
  per source, fail closed; one trace per crawl run; feed plus needs
  attention on one page; one command, no network.
- **Contracts and corpus** (`9e5db19`, `6573c9f`). Candidate, verdict,
  schema, and scraper interface; closed and past fixtures recorded live;
  `unverified` proven unrecordable on Unstop and covered by a named
  double.
- **Foundation** (`0b32760`). PRD, build plan, `GLOSSARY.md`, 19 ADRs,
  Devfolio fixtures proving no usable data path there.

## Verify any entry

```console
py -m pytest -q
deadmon-crawl --reset --no-serve --as-of 2026-10-11T00:00:00+00:00
deadmon-receipt-check
```
