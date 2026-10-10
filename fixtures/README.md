# Fixture provenance

Fixtures are the recorded pages an adapter is tested against — the corpus that makes
tests deterministic and network-free ([ADR-0015](../../../docs/adr/0015-validation-against-known-good-fixture.md)).
Recorded live, never hand-edited, never overwritten: a heal that legitimately changes
a page adds a new version beside the old one.

## `unstop/` — Slice 1's first crawler

| File | Source | Recorded | Purpose |
|---|---|---|---|
| `hackathons-open.json` | `GET unstop.com/api/public/opportunity/search-result?opportunity=hackathons&oppstatus=open&per_page=25` | 2026-10-11 | 25 live hackathons, 295 KB |

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