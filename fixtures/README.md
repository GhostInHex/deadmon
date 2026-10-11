# Fixture provenance

Fixtures are the recorded pages an adapter is tested against — the corpus that makes
tests deterministic and network-free ([ADR-0015](../../../docs/adr/0015-validation-against-known-good-fixture.md)).
Recorded live, never hand-edited, never overwritten: a heal that legitimately changes
a page adds a new version beside the old one.

## `unstop/` — Slice 1's first crawler

| File | Source | Recorded | Purpose |
|---|---|---|---|
| `hackathons-open.json` | `GET unstop.com/api/public/opportunity/search-result?opportunity=hackathons&oppstatus=open&per_page=25` | 2026-10-11 | 25 live hackathons, 295 KB |

### The other two verdicts, recorded live

Verification has to prove `closed` and `unverified` from recorded pages, not invented
ones (ticket [02](../../.scratch/slice-1/issues/02-record-unstop-fixture-versions.md)).
Two versions were recorded beside the healthy one on 2026-10-11. Neither was edited,
re-keyed or pretty-printed, and `hackathons-open.json` is untouched — the known-good
baseline a proposal must still reproduce.

| File | Source | Recorded | Purpose |
|---|---|---|---|
| `hackathons-closed.json` | `GET unstop.com/api/public/opportunity/search-result?opportunity=hackathons&oppstatus=closed&per_page=25` | 2026-10-11 | 24 hackathons, 267 KB — `closed` via **registration already passed** |
| `hackathons-past.json` | `GET unstop.com/api/public/opportunity/search-result?opportunity=hackathons&oppstatus=past&per_page=25` | 2026-10-11 | 25 hackathons, 207 KB — `closed` via **the event being over** |

**What is now provable from recorded fixtures.** `closed` is covered, both ways
verification defines it. `hackathons-closed.json` closes every candidate because
registration already passed — `end_regn_dt` runs 2026-09-17 → 2026-10-10, every one in
the past, while `end_date` runs 2026-10-11 → 2026-11-14. `hackathons-past.json` closes
every candidate because the event is over — `end_date` runs 2021-11-12 → 2025-03-27,
every one past. With the healthy fixture, `live` and `closed` are both exercisable from
recorded pages. **`unverified` is not, and cannot be.** See below.

Five requests were made in total, ~2 seconds apart, with a normal browser user-agent;
only the two responses in the table were kept. What a reader would otherwise get wrong
about them:

- **`oppstatus=closed` does not return `status: "CLOSED"`.** All 24 records still say
  `status: "LIVE"` and `regn_open: 1`. The only thing separating them from the healthy
  page is that `end_regn_dt` has already passed. An adapter that switches on `status` or
  `regn_open` calls all 24 `live` and is wrong 24 times over.
- **`oppstatus=past` is not a distinct filter.** Any value the route does not recognise
  falls back to the unfiltered list: `past`, `all` and `draft` each returned the same
  first page (269 pages, 6720 total) and differed only in the `oppstatus` string echoed
  inside the pagination URLs. What makes the file a `closed` fixture is its content, not
  the parameter — although in it 8 of 25 records *do* carry `regn_open: 0`.
- **That fallback list is not date-sorted.** Page 1 interleaves 2021 with 2026, so a
  page is not a date range and paging is not a time filter.
- **`hackathons-closed.json` holds 24 records** although `per_page=25` asked for 25.
  That is what the endpoint served, not a truncated download.
- **The three pages share zero titles** between `open` and the other two, so the
  fallback is not a superset of the open page.
- Some records in `hackathons-past.json` have `end_regn_dt` **after** `end_date`. Both
  parse, both are past, the verdict is still `closed`.

**`unverified` could not be recorded live, and no parameter asks for it.** The verdict
means the date is unusable — absent, `"TBA"`, or unparseable — and Unstop does not serve
that shape for `opportunity=hackathons`. Across 100 records sampled from every status the
route accepts (`open`, `closed`, and two pages of the unfiltered fallback), every record
carried an ISO-8601 `end_date` and a `regnRequirements.end_regn_dt` with a `+05:30`
offset: zero absent, zero unparseable, and the route never returned a placeholder or an
error body where a record should be. This is a limitation of the platform, not of the
recording pass — do not hand-edit a fixture to fake it, and do not treat the healthy
fixture as an approximate one. **Cover `unverified` with a declared test double
instead** — `fixtures/unstop/hackathons-unverified.json`, built from the recorded payload
with `end_date` and `end_regn_dt` set to `"TBA"`. Name it as a double wherever it
appears — filename, provenance row, test name — so no test result is ever mistaken for
recorded evidence. When it lands, its provenance row must say `test double, not a
recording` in the Source column, because every row above it holds a live URL.

### The `unverified` double (ticket 04)

| File | Source | Recorded | Purpose |
|---|---|---|---|
| `hackathons-unverified.json` | **test double, not a recording** — built 2026-10-11 from `hackathons-open.json` (unmodified): 3 real records with `end_date`, `regnRequirements.end_regn_dt` and `start_regn_dt` set to `"TBA"`; a `_double` banner inside the file names its provenance | 2026-10-11 | 3 candidates whose registration close is unusable — the `unverified` verdict |

Every other row in this README holds a live URL. This one does not, and must never be
read as recorded evidence: **`unverified` is not recordable from this platform** (above),
so the third verdict is exercised by this declared double and nothing else. The double
carries `"kind": "test double, not a recording"` in its own contents so the file labels
itself wherever it is opened.

**Use Unstop first.** It is a public JSON endpoint — no browser, no hydration wait, no
selector fragility. Devfolio is not (see below), and shipping Slice 1 on the platform
that works beats shipping it on the one that fights you.

Every field verification needs is already in the payload:

| Glossary term | JSON path |
|---|---|
| **Hackathon** | `data.data[]` — each result is a real event |
| **Source** | one Unstop result; a hackathon may have others (Devfolio, Devpost) |
| **Registration close** | `regnRequirements.end_regn_dt` (ISO 8601 with offset) |
| **Mode** | `region` — `online` \| `offline` \| `hybrid` |
| Team size | `regnRequirements.min_team_size` / `max_team_size` |
| Eligibility | `filters[]` — typed eligibility rules (`type: "eligible"`) |
| **Verdict** input | `status` (`LIVE`), `end_date`, `visibility` |
| Title / URL | `title`, `public_url`, `seo_url` |

Dates carry `+05:30`, so normalise to UTC at extraction ([ADR-0013](../../../docs/adr/0013-timezones.md)) —
this is exactly the case that rule exists for.

## `devfolio/` — no usable data path

| File | URL | Recorded | Purpose |
|---|---|---|---|
| `hackathons-index.html` | `https://devfolio.co/hackathons?page=1` | 2026-10-10 | probe |
| `hackathons-open.html` | `https://devfolio.co/hackathons/open` | 2026-10-10 | probe |

**These pages contain zero hackathon data. The listing grid is client-side rendered.**

Verified on the recording:

- The `<body>` holds only shimmer placeholders (`jDIqJr` / `eyFpZQ` styled divs) — no
  titles, no registration dates, no prize fields.
- `__NEXT_DATA__` is `{"pageProps":{"filterType":"application_open"}}`; the listing
  array is **not** in the initial payload.
- `/hackathons?page=1` returns 186 KB and contains exactly **one** hackathon-shaped URL
  (`/hackathons/<ulid>`) — a single featured entry, not the result grid.
- `_next/data/.../hackathons.json` returns 200 with an **empty** `queries: []`.
- `api.devfolio.co/api/hackathons*` returns **422** for every parameter shape tried
  (`filter`, `filterType`, `type`, `filter[type]`, `limit`/`offset`, bare). `…/search` is 404.

An HTML-selector adapter over these extracts nothing — which is correct behaviour, not a
broken test, and is the exact failure shape the heal loop exists to detect
([ADR-0011](../../../docs/adr/0011-break-is-a-regression-not-an-absence.md)): HTTP 200,
zero candidates.

**Options, when Devfolio is next in scope:**

1. **Render the page.** Headless browser, wait for hydration, capture the rendered DOM.
   Everything downstream (fixtures, diffs, sandbox validation) keeps working.
2. **Find the post-hydration XHR.** Best outcome if the endpoint is public and stable —
   and the most fragile thing to heal.
3. **Leave Devfolio out of the demo.** Unstop alone demonstrates the pipeline; the
   dedupe claim then needs a second source, so pair it with Devpost when reachable.

Devpost returned **403** to a scripted request on 2026-10-11 — it may need a real browser
or may rate-limit automation. Treat it as unknown until measured, not as available.

`.gitignore` keeps `fixtures/` and excludes `.playwright/` / `ms-playwright/` (browser
binaries stay out of the tree).

**Record a fixture before writing any adapter**, and record it as the known-good version.
Do not edit these files to add data — they are the record of what the platform served.

## Slice 2 corpora — five more crawlers (recorded 2026-10-12)

One page per platform, recorded live with a browser user-agent, ~2 seconds
apart, never edited. None of these pages serves a tz-aware registration
close, so every record verifies `unverified` except GenAI.works' featured
card — that is the platforms' limitation, stated per row, not an adapter
gap. Mode is mapped only where the page states it outright.

| File | Source | Recorded | Purpose |
|---|---|---|---|
| `hackerrank/contests.html` | `GET www.hackerrank.com/contests` | 2026-10-12 | 11 contests (2 promoted, 1 active, 8 archived); reg strings carry no year or zone, mode unstated |
| `hackathon-com/index.html` | `GET hackathon.com` (upcoming grid on the homepage) | 2026-10-12 | 4 events with Online mode; start/end day-month, no year or zone |
| `lablab/event.html` | `GET lablab.ai/event` | 2026-10-12 | 24 events from the page's JSON-LD catalogue; card badges give Online ×8 / Hybrid ×3 / On-site ×1; build windows, no year or zone |
| `mlh/events-2026.html` | `GET mlh.io/seasons/2026/events` | 2026-10-12 | 24 past-season events from the embedded catalogue; physical ×21 / digital ×3; event bounds are not registration closes |
| `genai-works/index.html` | `GET hackathon.genai.works` | 2026-10-12 | 1 featured event; rail close year-qualified by the same card's window (`Oct 22, 23:59 UTC`); mode unstated |

Mode mappings, documented where they are judgment calls: hackathon.com
Online/Virtual → `online`, Hybrid → `hybrid`; lablab On-site → `offline`
(venue-only); MLH physical → `offline`, digital → `online`. HackerRank and
GenAI.works state no per-event mode, so mode stays absent.

## Measured dead ends — no adapter without a data path (2026-10-12)

Each URL below was fetched with a browser user-agent and returned the
stated shape. These are measured verdicts, not assumptions; re-probe
before writing an adapter, and record the fixture first if one appears.

| Platform | Probe | Result |
|---|---|---|
| Devpost `devpost.com/hackathons` | GET | **403** to a scripted request (matches the 2026-10-11 probe) — needs a real browser or rate-limit clearance |
| Hack2skill `hack2skill.com/hackathons` | GET | shell only ("Hack2skill", no listings) — client-rendered grid |
| HackerEarth `hackerearth.com/challenges/` | GET | shell only (a bare count, no event titles or dates) — client-rendered grid |
| DoraHacks `dorahacks.io`, `dorahacks.io/hackathons` | GET | homepage is a marketing shell with no listings; `/hackathons` is **404** — listing URL not discoverable statically |
| Devfolio | recorded 2026-10-10 | no usable data path (see `devfolio/` above) |