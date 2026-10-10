# Fixture provenance

Fixtures are the recorded pages an adapter is tested against — the corpus that makes
tests deterministic and network-free ([ADR-0015](../../../docs/adr/0015-validation-against-known-good-fixture.md)).
Recorded live, never hand-edited, never overwritten: a heal that legitimately changes
a page adds a new version beside the old one.

## `devfolio/`

| File | URL | Recorded | Purpose |
|---|---|---|---|
| `hackathons-index.html` | `https://devfolio.co/hackathons?page=1` | 2026-10-10 | the adapter's primary input |
| `hackathons-open.html` | `https://devfolio.co/hackathons/open` | 2026-10-10 | applications-open filter |

Both captured with `user-agent: deadmon/0.1 (+hackathon research; contact via repo)`.

## Read this before writing the Devfolio adapter

**These pages contain zero hackathon data. The listing markup is client-side rendered.**

Verified on the recording:

- The `<body>` holds only shimmer placeholders (`jDIqJr` / `eyFpZQ` styled divs), no
  hackathon titles, no registration dates, no prize fields.
- `__NEXT_DATA__` is `{"pageProps":{"filterType":"application_open"},"__N_SSG":true}` —
  the listing array is **not** in the initial payload.
- `https://devfolio.co/hackathons?page=1` returns 186 KB and contains exactly **one**
  hackathon-shaped URL pattern (`/hackathons/<ulid>`), which is a single featured
  entry, not the result grid.
- `_next/data/.../hackathons.json` returns 200 with an **empty** `queries: []`
  dehydrated state.
- `api.devfolio.co/api/hackathons*` returns **422 Unprocessable Entity** for every
  parameter shape tried (`filter`, `filterType`, `type`, `filter[type]`, `limit`/`offset`,
  bare path). `api.devfolio.co/api/hackathons/search` returns 404.

**Consequence:** an HTML-selector adapter over these fixtures extracts nothing. That is
correct behaviour, not a broken test — and it is precisely the shape of the failure the
heal loop is built to detect ([ADR-0011](../../../docs/adr/0011-break-is-a-regression-not-an-absence.md)):
a page that returns HTTP 200 and yields zero candidates.

**Decide before Slice 1 coding.** The options, in the order worth trying:

1. **Render the page.** A headless browser fetches, waits for hydration, and captures the
   *rendered* DOM. The fixture becomes the post-hydration HTML, and the adapter is an
   ordinary selector scraper again. Cost: browser dependency, but everything downstream
   (fixtures, diffs, sandbox validation) keeps working unchanged.
2. **Find the real XHR.** The client calls some endpoint after hydration. Capture it once
   via the browser's network panel, then the adapter reads JSON — which is the "prefer
   structured endpoints over HTML" posture [PRD §Scraping posture](../../../docs/PRD.md).
   Best outcome if the endpoint is public and stable, and *also* the most fragile thing
   to heal.
3. **Swap the first platform.** Unstop and Devpost were both expected to be scrapable.
   Slice 1 could ship on whichever turns out to server-render, keeping Devfolio for
   Slice 2 once its data path is known.

`.gitignore` keeps `fixtures/` and deliberately excludes `.playwright/` / `ms-playwright/`
(browser binaries stay out of the tree).

Whatever is chosen, **record a fixture before writing the adapter**, and record it as the
known-good version. Do not edit these files to add data — they are the record of what
the platform actually served.