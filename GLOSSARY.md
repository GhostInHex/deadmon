# deadmon

deadmon watches hackathon platforms so a student developer never misses a registration deadline. It crawls listings, proves each one is still live, filters them against one person's profile, and alerts before the deadline closes. When a platform breaks the scraper, the agent repairs itself.

## Agents and platforms

**Scout**:
The scheduled agent loop that runs every platform through fetch → extract → verify → dedupe → filter → alert. There is one Scout; it is not per-platform. It runs on two tiers: a daily full crawl and a frequent deadline sweep.
_Avoid_: crawler, bot, worker, daemon

**Deadline sweep**:
A cheap re-verification pass over only those listings currently inside a lead-time window. It runs every few hours so the 24-hour lead time can actually fire; without it the tightest alert is silently unreachable.
_Avoid_: heartbeat, poll, re-crawl, full crawl

**Full crawl**:
The daily pass over every tracked platform, discovering and extracting candidates. The only tier that adds new work to a platform.
_Avoid_: deadline sweep, sync, harvest

**Crawler**:
The per-platform unit of work inside the Scout — one crawl run against one platform. Named `<Platform> crawler` (e.g. Devfolio crawler). This is the thing that breaks, and the thing that heals.
_Avoid_: Scout, agent, session

**Adapter**:
The code that knows one platform's HTML, behind the scraper interface. Implements fetch and extract; knows nothing about verification, dedupe, or alerts.
_Avoid_: scraper, parser, spider

**Crawl run**:
One execution of one crawler at one point in time, with its outcome. The unit that is traced, counted, and evidenced.
_Avoid_: job, task, sweep, tick

## Listing lifecycle

**Candidate**:
What extraction produces before anything is proven about it. A claim, not a fact — it may never become a listing.
_Avoid_: unverified listing, raw listing, draft, result

**Listing**:
One platform's claim about one hackathon — a **source** — that carries a verdict. A listing is not the event itself; it is a platform's claim about an event. See **Source** for the same thing viewed from the dedupe side.
_Avoid_: candidate (pre-verdict), event, hackathon, entry

**Live listing**:
A listing whose verdict is **live**. The only kind of record the feed presents as fact.
_Avoid_: verified (ambiguous — says nothing about what was checked), confirmed

**Needs attention**:
The greyed group holding every listing currently marked **unverified**. Visible but never in the feed; also the operator's signal that an adapter is failing.
_Avoid_: failed, problem, warning list

**Verification**:
The stage that re-checks one candidate against its source page: the page responds, the registration-close date parses to a real future date in a known timezone, and the page states a mode. Produces exactly one verdict.
_Avoid_: check, validation, health check

**Verdict**:
The single outcome of verification. Exactly three values:

- **live** — page up, deadline parses to a future date, mode present. Enters the feed.
- **unverified** — page unreachable, blocked, rate-limited, or the date is unusable (`"TBA"`, unparseable). **Indeterminate, not bad.** Never asserted as fact, never deleted; shown greyed in **needs attention**.
- **closed** — confirmed over: registration passed, or the event was cancelled. Terminal; keeps its row, leaves the feed.

_Avoid_: status, result, state, health

**Fail closed**:
When verification cannot establish a deadline, the verdict is **unverified**. deadmon never infers, defaults, or carries forward a deadline it did not read.
_Avoid_: best effort, fall back, infer

## Dedupe and identity

**Hackathon**:
One real-world event, independent of how many platforms advertise it. What the user actually cares about and what deduplication exists to produce. It renders as one **card**.
_Avoid_: listing, event, opportunity, entry

**Card**:
The dashboard's unit of display — one hackathon, its earliest credible registration close, and every source underneath with its own verdict. Dismissing a suspected-same link splits one card into two.
_Avoid_: listing row, tile, result, item

**Registration close**:
The deadline after which a hackathon can no longer be entered. One per hackathon: the earliest credible date across its sources. Never varies by subscriber.
_Avoid_: deadline (ambiguous — start and end dates both exist), due date, cutoff

**Credible date**:
A registration close read from a source that verified and parsed. An unparseable date is not credible and contributes nothing — it is never a fallback.
_Avoid_: fallback date, estimated date, default deadline

**Source**:
One platform's claim about one hackathon — a listing. A hackathon has N sources and its dates and prize text are read from them.
_Avoid_: listing (use Source), reference, link, mirror

**Fingerprint**:
The normalised title plus date-window proximity used to decide whether two sources describe the same hackathon. A comparison, not a proof — which is why an uncertain match only ever proposes.
_Avoid_: hash (the key), id, key, slug

**Suspected same**:
An uncertain dedupe match between two sources. Shown as one card with a note; never an automatic merge, and dismissable in one click. It never merges deadlines — each source alerts on its own date until a person confirms the link.
_Avoid_: fuzzy match, tentative link, possible duplicate

## Fit

**Profile**:
One subscriber's stated constraints — country, student status, interests, team preference — that listings are filtered against. Belongs to a **subscriber**, never to the Scout; many profiles, one Scout.
_Avoid_: user, account, preferences, persona

**Subscriber**:
A person who receives alerts and has a profile. The demo runs with exactly one; the model is not a singleton.
_Avoid_: user, account, member, customer

**Reason tag**:
A short marker on a listing explaining why it is worth attention (`online`, `₹1L+`, `AI-relevant`). A set of tags, never a numeric score — the inputs are too coarse to support a number.
_Avoid_: score, rating, rank, priority, weight

**Match**:
A listing that fits the profile: eligible, in-scope, live. A fit judgement is never a truth judgement and never changes a verdict.
_Avoid_: eligible, relevant, included, approved

**Exclusion**:
A live listing removed from the feed by profile fit, with the reason retained. Surfaced in the excluded view, never silently dropped.
_Avoid_: filter result, rejection, removal, drop

**Exclusion reason**:
The specific cause a live listing did not match the profile (e.g. offline-only, students ineligible, below prize threshold). Always recorded with the exclusion.
_Avoid_: rejection reason, disqualifier, filter tag

## Self-heal

**Heal event**:
The audit record of one self-repair. Carries evidence → proposal → sandbox validation result → commit ref → backfill count. One per incident, never several.
_Avoid_: heal, fix (use Proposal), incident, patch, repair

**Proposal**:
A proposed change to an adapter, produced from the failing run's evidence and the existing adapter code. A step inside a heal event, not an artifact in its own right.
_Avoid_: fix, patch, diff, suggestion, commit

**Sandbox validation**:
Proving a proposal reproduces the **known-good fixture** — comparable candidate count, required fields populated, dates parseable. Non-empty output is the floor, not the bar; a selector matching page furniture also returns results.
_Avoid_: test, dry run, check

**Fixture**:
A recorded page for one platform, replayed offline as adapter input. The corpus covers a healthy page, a changed-layout page, and a dead page per platform, and is the primary test asset.
_Avoid_: snapshot (the failing one), mock, sample, stub

**Known-good fixture**:
The most recent fixture that extracted correctly. The thing a proposal must reproduce and the thing a diff is taken against.
_Avoid_: golden file (ambiguous), reference fixture, baseline page

**Snapshot**:
The page as actually served at the moment a break was detected. Compared against the known-good fixture to produce the diff a proposal reasons from.
_Avoid_: fixture, screenshot, evidence (too vague)

**Diff**:
The scoped change between snapshot and known-good fixture, restricted to the regions the adapter reads. A proposal's primary evidence — never the whole page.
_Avoid_: patch, change, delta of code

**Fixture version**:
Fixtures are added, never overwritten. A heal that legitimately changes a page adds a new fixture beside the old and links both; retirement is explicit and stays in history.
_Avoid_: update fixture, refresh fixture, replace fixture

**Heal in flight**:
A proposal generated, validating, or awaiting commit for one crawler. At most one per crawler; a second break while one is running escalates instead of healing.
_Avoid_: pending heal, active job, open proposal

**Escalation**:
What happens when sandbox validation fails twice, or a second break arrives while a heal is in flight — the operator is given the evidence and the proposal rather than a third guess. A proposal touching any file outside its own adapter's allowlist is rejected pre-flight, never healed.
_Avoid_: give up, failure, abort, human review

**Operator fault**:
A failure in the heal loop itself — the proposal step erroring on an expired key, an unavailable model, exhausted budget. Looks identical to an unresolved crawler break and needs the opposite fix, so it is tracked and alarmed separately.
_Avoid_: scout failure, crawler break, system error

**Allowlist**:
The declaration-only surface — selectors and extraction rules — a proposal may change. A proposal can never introduce new logic, so page content read from the internet can never become executable code.
_Avoid_: sandbox (limits blast radius, not capability), permission, scope

**Break**:
A *regression* in a crawler's yield against its **baseline** — a crawler that recently produced listings suddenly producing none. A crawler with no history, or one quiet for a long time, is not broken.
_Avoid_: failure, error, incident, outage, empty run

**Baseline**:
A per-crawler rolling record of recent yield, used to judge whether a low-yield run is normal or a regression. A quiet platform is a legitimate steady state, not a break.
_Avoid_: average, threshold, expected count

**Backfill**:
Re-crawling the window a break left uncovered, so deadlines inside the gap are not silently missed. The final step of a heal event, and the reason a heal matters.
_Avoid_: replay, re-run, catch-up, refill

## Notification

**Lead time**:
The fixed set of intervals before registration close at which an alert is sent: 7 days, 3 days, 24 hours. Computed in UTC from the registration-close instant, never the start date, and never varying by subscriber.
_Avoid_: reminder window, warning, nudge

**Alert**:
One message dispatched to one channel about one hackathon at one lead time, sent the moment it is due — never queued for a later batch. Each lead time fires at most once per subscriber per hackathon per window.
_Avoid_: notification, message, ping, digest

**Superseded**:
An alert for a hackathon whose credible date moved **earlier** after an earlier alert was already sent. Sent precisely because it revises the last one. Distinct from a suppressed duplicate, which is silent.
_Avoid_: duplicate, correction, update, resend

**Closed**:
A terminal verdict meaning registration passed or the event was cancelled. The card leaves the feed, every unsent alert is cancelled, the mute expires, and reason tags stop being computed. Rows, tags, and sent-alert history survive — closure removes a hackathon from view, not from the record.
_Avoid_: expired (a cause, not the verdict), archived, removed, past

**Mute**:
A subscriber's decision to stop alerts for one hackathon until a stated time. Keyed to the **hackathon**, never to a source URL, because sources change URLs between crawls. `mute until` defaults to the registration-close date so it expires on its own; a shorter value is a snooze.
_Avoid_: dismiss (that's a dedupe action), suppress, block, ignore