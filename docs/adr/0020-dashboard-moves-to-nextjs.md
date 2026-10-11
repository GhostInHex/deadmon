# The dashboard moves to Next.js; Python keeps the crawl and serves JSON

Supersedes the constraint in `docs/PRD.md`:86 — *"Dashboard is one server-rendered page
(no SPA framework) ... Speed of build beats UI ambition."* That line predates the
glossary and the build, and the decision it recorded is being reversed on evidence.

## What changed

Slice 1 shipped with the Python process doing three jobs at once: crawling,
verifying, storing, *and* emitting HTML. The last of those was always the
weakest. The rendered page was semantic markup with no type scale, no tokens and
no visual hierarchy — readable, but not something to put in front of judges.

The product is the pipeline. The page is only a view of it. Keeping HTML
generation inside the crawl process made the presentation layer the thing with
the most leverage and the least testing.

## Settled

The **crawl pipeline stays in Python, unchanged.** It keeps the adapter
interface, the verification verdict, the SQLite store and the tracing client —
and all 111 offline tests. The pipeline is the scored artefact; it does not move.

Python gains a **read-only JSON endpoint** over the same view model
`dashboard.py` already builds. Next.js/TypeScript renders the dashboard, the
landing page and the pricing page from that JSON, and is deployed to Vercel. The
crawl stays on the EC2 instance under `deploy/deadmon.service`.

So: **two runtimes, two hosts, one seam.** The seam is the JSON contract.

## Considered Options

- **Next.js reads the SQLite file directly.** Rejected: couples the frontend to a
  mutable local file. Across two hosts that means a shared volume or committing
  the database — and `.gitignore` already forbids a committed DB as source of
  truth (ticket 05). The JSON endpoint is one extra route; the volume is an
  operational tax paid forever.
- **Next.js replaces the Python server entirely.** Rejected: this discards the
  pipeline, which is the deliverable. A Next.js re-implementation of the crawler
  would trade 111 offline tests and a working self-heal seam for a UI framework.
- **Keep the server-rendered page and just style it.** Rejected on the evidence:
  it was tried, and the honest result is that inline CSS in a string literal
  cannot express a token system, a type scale, or shared components across a
  landing page and a dashboard. `web/` proved the design system works and that
  hand-written HTML is the wrong substrate for it.
- **Keep HTML as a fallback and add Next.js alongside.** Kept, deliberately: the
  Python route still renders, so the pipeline is demonstrable with no Node
  toolchain and no network. It is the safety net for the demo, not the product
  surface.

## Consequences

- Two deploys instead of one: Vercel for the UI, the t3.micro for the crawl. The
  EC2 instance needs no Node runtime.
- The Python HTML route stays in the tree and stays tested. Removing it would
  delete the offline demo path on submission day to tidy a directory.
- The JSON contract is now a real interface and needs its own tests. A frontend
  that silently renders an empty feed because a field was renamed is exactly
  the failure the self-heal loop exists to prevent, so it gets caught here
  instead.
- `docs/PRD.md`:86 is corrected to point here rather than left to contradict.
- The design system in `docs/design-system-reference/` is now actually in use,
  so the `.gitignore` rule that parked it as "not part of deadmon" no longer
  holds and is removed.