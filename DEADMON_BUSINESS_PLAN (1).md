# Deadmon — draft business plan

Prepared with cfo.ai Ari · 12 October 2026 (IST)

Updated 12 October 2026, 00:54 IST · repository reassessment at commit `8374bae`

**Status:** proposed plan, not observed financial performance. All amounts are INR. Forecast: October 2026–September 2028; September 2026 is an estimated opening point. The public repository now contains implementation code as well as documentation. Static review establishes a fixture-backed prototype, not a working live monitoring service, paying customers or a verified cash balance. Financial assumptions and forecast amounts are unchanged from the original plan. No credentials or private repository access are included.

## 1. The business

Deadmon’s intended product is a scheduled hackathon-discovery agent: discover listings, verify deadlines and eligibility, filter for a profile, and deliver dashboard/Telegram alerts. Its proposed differentiator is a traced, sandbox-validated scraper repair loop.

**What exists now:** the earlier documentation-only description is outdated. The reviewed repository contains a Python Unstop adapter, candidate and verdict contracts, verification rules, SQLite storage, crawl tracing, a Python dashboard and read-only JSON feed. It also contains Next.js landing, dashboard and pricing pages, deployment configuration, and the business plan. The intended architecture is Python/SQLite on EC2 plus Next.js on Vercel, with the Python HTML dashboard retained as a demo fallback.

**What this proves:** an implemented, fixture-backed prototype. The current runner reads recorded JSON payloads, processes them once and serves the dashboard; it does not establish fresh daily crawling. Its verification call uses a default that assumes sources respond rather than performing a live source-response check. A future deadline in a recorded fixture is therefore not proof that the primary page is still live. Scheduled refresh, subscriber-specific eligibility, Telegram delivery, end-to-end self-healing and paid onboarding remain unestablished by this review. The Unstop adapter is the only implemented platform adapter identified; Devfolio fixtures are not a working Devfolio adapter.

Code inspection is not a production deployment check. The missing frontend API module noted below also means the reviewed checkout needs repair and a clean build before frontend readiness can be claimed.

The initial paying buyer is a college developer club/community admin who hand-curates deadline digests. Students use Free; clubs pay for the saved weekly curation effort. This buyer and proposed revenue logic come from the PRD, not customer interviews.

## 2. Pricing and launch scope

| Tier | Proposed monthly price | Offer | Status |
|---|---:|---|---|
| Free | ₹0 | Intended one individual alert profile and dashboard | PRD offer; current implementation is a single-subscriber fixture demo |
| Community | ₹449 | Club-admin subscription: shared club profile and weekly digest | Within PRD ₹399–499 range; proposed, not operational or demand-validated |
| Pro | ₹99 | Individual subscription: additional personal profiles and exports, excluding the club package | Recommended entitlement distinction; later product experiment |

**Fix the packaging:** the reviewed pricing page says ₹99 Pro includes “Everything in Community,” while Community costs ₹449. At these proposed prices, distinguish an individual Pro subscription from the club-admin Community subscription. Pro should not promise the complete club package. This is a recommended correction to the offer, not an implemented product change or a change to the forecast prices.

Do not sell "never misses a deadline" as a service guarantee. Explain verification freshness, unverified listings and failed-platform coverage clearly. For the current demo, label fixture-derived verdicts as such rather than implying the primary source was just checked live.

The **unchanged financial model** assumes paid launch in October 2026 for Community and January 2027 for Pro. Those are scenario inputs, not release commitments or evidence that the product is ready to collect revenue. Actual paid launch should depend on capability gates: scheduled live collection, genuine source verification, reliable delivery, subscriber isolation, the promised digest/profile features, and billing. If these gates delay launch, revise the launch dates and recalculate revenue and cash; the published figures below would no longer describe that delayed case.

The PRD places multi-user accounts, a public API and broader alert channels outside the hackathon MVP. Keep scope controlled rather than claiming the full paid offering has shipped. A Free user and Pro account are distinct modeled populations; there is no verified conversion funnel.

## 3. Editable planning inputs

All inputs below are estimates, except the source’s Community price range and feature descriptions. They are visible in the saved cfo.ai plan.

| Input | Free | Community | Pro |
|---|---:|---:|---:|
| Accounts at September 2026 opening | 0 | 0 | 0 |
| New accounts in launch month | 100 | 3 | 10 |
| Monthly growth in additions | 3% | 5% | 5% |
| Monthly account churn | 8% | 3% | 6% |
| Monthly delivery reserve per account | ₹1 | ₹20 | ₹3 |

Fractional accounts are expected values, not literal users or signed customers. Growth is a hypothesis, not a commitment. Additions are independent of marketing spend; no acquisition-cost elasticity has been established.

- Opening cash: ₹25,000, estimated at September 2026.
- Monthly fixed costs: hosting ₹1,500; crawl/AI contingency ₹500; marketing ₹1,000; admin ₹500 — total ₹3,500.
- Payment fee assumption: 3% of paid receipts, not a verified provider quote.
- One-time launch setup spending: ₹3,000 in October 2026, expensed.
- Minimum operating cash buffer: ₹5,000.
- Founder: one placeholder solo builder, annual cash pay ₹0 in base/upside. Benefits rate 0%. No planned hires or paid contractors.
- Debt, sponsorship, prizes and fundraising: ₹0. No sponsor credits treated as guaranteed funding.

Founder living expenses are excluded until pay is entered. An unpaid-founder surplus is not fully loaded economic profit. Model free-tier limits and human maintenance effort before scaling; "free inference" does not mean a free business.

**Cost evidence correction:** the reviewed normal fixture-crawl path makes no model inference call. That supports a narrow statement about that code path, not a measured zero total crawl cost. The pricing page’s “measured” economics and “inference dominates cost” language are not established by the reviewed evidence: processor fees, delivery reserves and forecast results remain estimates. The EC2/Vercel split introduces two deployments and an API boundary even if temporary free-tier allowances cover the bills. Retain the hosting and crawl/AI reserves until actual production requests, quotas, repairs and human maintenance effort have been measured. No financial input is reduced to zero by this update.

## 4. How the forecast works

For each tier and month:

1. New accounts = launch additions × (1 + additions growth)^(months since launch), zero before launch.
2. Cancellations = opening accounts × monthly churn.
3. Ending accounts = opening accounts + new accounts − cancellations.
4. Recurring revenue = ending accounts × monthly price.
5. Delivery costs = ending accounts × per-account reserve.
6. Gross profit = recurring revenue − delivery costs − payment fees.
7. Operating cash surplus = gross profit − fixed costs − founder cash cost − setup spending.
8. Closing cash = prior closing cash + operating cash surplus + financing cash.

Collections and payments occur in the month recognized. Cancellations happen before billing and new accounts pay a full month. No annual prepaid subscriptions, receivables, inventory, capex, tax/GST, refunds or restricted cash is assumed. Setup is expensed. Founder salary is calendar-day prorated for start/end dates. Founder headcount counts anyone employed during the month.

These simplified cash assumptions are suitable for testing a launch; validate invoicing, processor charges, GST and tax treatment before using the draft as a formal budget. Revenue and spending add across months; cash and accounts use the closing month for quarterly/yearly summaries. Negative cash is not hidden.

## 5. Scenarios and outcomes

Base uses the inputs above. Upside changes paid launch additions to 5 Community and 15 Pro, paid-addition growth to 8%, and churn to 2% Community/4% Pro. Downside changes paid launch additions to 1 Community and 5 Pro, paid-addition growth to 0%, churn to 6% Community/10% Pro, and founder pay to ₹10,000/month. Free assumptions and opening cash stay unchanged across cases. These are alternative plans, not probabilities.

| Result | Base | Upside | Downside |
|---|---:|---:|---:|
| September 2027 recurring revenue | ₹27,360 | ₹55,084 | ₹6,954 |
| September 2027 closing cash | ₹120,839 | ₹250,995 | ₹-104,216 |
| First 12 months revenue | ₹158,722 | ₹298,876 | ₹45,617 |
| First 12 months operating cash surplus | ₹95,839 | ₹225,995 | ₹-129,216 |
| September 2028 recurring revenue | ₹68,816 | ₹185,578 | ₹10,197 |
| September 2028 closing cash | ₹602,474 | ₹1,494,359 | ₹-182,508 |

- Base: monthly cash flow first turns positive in December 2026. Lowest cash is ₹18,470; neither zero cash nor the ₹5,000 buffer is crossed through September 2028.
- Upside: monthly cash flow first turns positive in November 2026; no cash-out through September 2028.
- Downside: October 2026 closes at ₹8,816; both zero cash and the ₹5,000 buffer are crossed in November 2026. Cash flow remains negative throughout the forecast. Later negative balances measure funding needed, not a feasible operating plan.

Monthly cash-out is not an exact day and cannot detect an intramonth shortfall. The draft is conditional on the assumed opening cash and growth. Downside mixes slower sales with founder pay; it does not isolate one factor. Use the simulator to test additional recurring spending separately, then refine the saved assumptions.

## 6. Unit economics and recommendation

One Community account generates ₹449 less ₹20 delivery reserve and ₹13.47 fee = **₹415.53 monthly contribution**, before shared overhead, Free-user costs and founder pay. Roughly **9 clubs** cover the initial ₹3,500 fixed monthly costs alone. That is not company breakeven: the saved cash forecast includes delivery for Free/Pro, setup and founder compensation.

Under unchanged base growth, adding ₹10,000/month of spending from launch exhausts the estimated ₹25,000 cash in November 2026. Do not take the high year-two balances as traction evidence; they come from compounding unvalidated additions.

Recommendation: focus Community first. Get 3 paid club pilots before investing in Pro. Shared crawling is the cost advantage; verified deadlines and reduced admin effort are the benefit. Track cash compensation separately so you know whether this supports a business or only a side project.

## 7. Launch validation and risk controls

### Implementation priorities from the repository reassessment

1. **Restore the missing frontend API module and prove a clean build.** `apps/web/src/app/dashboard/page.tsx` imports `@/lib/api`, but no corresponding module was present in the reviewed checkout. Direct checks for `src/lib/api.ts`, `src/lib/api.tsx` and `src/lib/api/index.ts` returned not found. A screenshot does not establish that a clean checkout builds.
2. **Replace fixture-only input with live collection and scheduled refresh.** Retain fixtures as regression tests and a labeled demo fallback, not as current-market data. Handle platform limits, response failures, freshness and retries explicitly.
3. **Make the liveness check real.** Pass actual source-response evidence into verification; do not let a default “responds” value create a live-verification claim. Show when each source was fetched and what could not be verified.
4. **Demonstrate the differentiator and delivery.** Establish repair detection → patch proposal → sandbox validation → commit → backfill, and Telegram delivery, with trace/commit evidence and failure paths. Architecture decisions alone do not establish these workflows work.
5. **Separate demo deployment from production.** `deploy/deadmon.service` invokes the runner with `--reset`; remove that history reset from a durable production service. The feed/trace endpoints are unauthenticated: choose a deliberate access and network-exposure policy before deployment for real users. Do not assume “read-only” means all data is safe to expose.
6. **Correct customer-facing claims.** Separate individual Pro from Community entitlements; distinguish proposed unit economics from measured costs; describe only implemented platform coverage and alert/repair capabilities as available.
7. **Publish one reproducible test result.** The reviewed README reports 109 offline tests, while ADR-0020 reports 111. Neither count was independently executed in this review. Run the suite on a clean checkout and align the docs with the result.

### Commercial validation and financial controls

- Interview 10 club admins; test ₹399, ₹449 and ₹499 offers, without assuming any has been validated.
- Target 3 paid pilots and measure digest usage, weekly active users, churn, manual curation time saved and willingness to renew.
- Instrument requests, inference usage, retries, repair success and human maintenance time; cap the repair budget.
- Validate platform scraping terms, rate limits and graceful degradation. Prefer structured endpoints and cache shared crawls.
- Sandbox repair patches, protect credentials, require approval for risky changes and retain trace/commit evidence. A passing fixture is not a guarantee against live-site changes.
- Check multi-profile/auth and billing requirements before a paid launch. Pro exports are not a public API commitment.
- Confirm hosting, model quotas and observability retention; sponsor/free-tier access may expire.
- Obtain actual opening cash and required personal monthly pay before calling this an operating budget.

## 8. Hackathon-ready demo wording

> “Deadmon now has a fixture-backed Python discovery pipeline, storage, tracing and dashboard code, with a Next.js frontend in progress. Live refresh, Telegram delivery and the complete repair loop still need to be demonstrated. Ari modeled Community at ₹449 and a later ₹99 individual Pro tier. Under our draft acquisition assumptions, base cash flow turns positive in December; slower sales plus ₹10,000 founder pay exhaust ₹25,000 of starting cash in November. These are hypotheses, not traction—we’ll validate them with three paid club pilots.”

## 9. What was checked — and what remains unverified

**Original model checks:** all 25 opening/forecast month values for revenue, operating cash surplus and closing cash in each of the three scenarios were compared with a separate reconstruction from the assumptions. They agree within rounding. The first Pro month and pre-launch zeroes were checked; downside founder payroll is ₹10,000/month. January–March 2027 revenue is ₹27,032.59 and quarter-end cash is ₹31,741.79, matching the monthly calculations. Opening cash remains ₹25,000 across scenarios.

The cfo.ai cash simulator renders in light and dark themes. Its extra-spending control is a local preview until Apply is selected; buttons and clicks were not exercised during rendering checks. These were checks of the original saved model and simulator; this file update did not rerun them or change their financial inputs.

**Repository reassessment:** source-tree and static code inspection at commit `8374bae533758270becfa4926151f879c3f30ba3`, covering the Python runner, Unstop adapter, verification, storage, tracing, dashboard, Next.js pages, deployment configuration and business-plan documentation. Implementation code is present. No Python test suite, Next.js production build, live crawl, Telegram delivery, repair execution or public deployment was run during this review.

The repository’s business-plan note reports a separate reconstruction of the 18 published financial outcomes, reproducing them within rounding. That is a reported arithmetic check, not independent proof of customer demand. It was not rerun as part of this file update.

Market demand, actual operating costs, real customers, bank balances and production service reliability remain unverified. The financial forecast still relies on the original estimates.

## 10. Source documents

The repository reassessment is pinned to commit `8374bae533758270becfa4926151f879c3f30ba3`; later changes may resolve or alter these findings.

- [README](https://github.com/GhostInHex/deadmon/blob/8374bae533758270becfa4926151f879c3f30ba3/README.md): updated implementation status and reported test count.
- [PRD](https://github.com/GhostInHex/deadmon/blob/8374bae533758270becfa4926151f879c3f30ba3/docs/PRD.md): feature scope, Community price range, buyer and revenue logic.
- [Build plan](https://github.com/GhostInHex/deadmon/blob/8374bae533758270becfa4926151f879c3f30ba3/docs/PLAN.md): phased delivery, demo requirements and later Community tier.
- [Crawl runner](https://github.com/GhostInHex/deadmon/blob/8374bae533758270becfa4926151f879c3f30ba3/src/deadmon/crawl.py): fixture processing, feed serving and verification call.
- [Unstop adapter](https://github.com/GhostInHex/deadmon/blob/8374bae533758270becfa4926151f879c3f30ba3/src/deadmon/adapters/unstop.py): recorded-payload input, not live transport.
- [Verification](https://github.com/GhostInHex/deadmon/blob/8374bae533758270becfa4926151f879c3f30ba3/src/deadmon/verification.py): verdict logic and default source-response behavior.
- [Next.js dashboard](https://github.com/GhostInHex/deadmon/blob/8374bae533758270becfa4926151f879c3f30ba3/apps/web/src/app/dashboard/page.tsx): API-client import and intended feed integration.
- [Pricing page](https://github.com/GhostInHex/deadmon/blob/8374bae533758270becfa4926151f879c3f30ba3/apps/web/src/app/pricing/page.tsx): published draft tiers, entitlement conflict and cost claims.
- [Deployment service](https://github.com/GhostInHex/deadmon/blob/8374bae533758270becfa4926151f879c3f30ba3/deploy/deadmon.service): startup reset and serving configuration.
- [Dashboard architecture decision](https://github.com/GhostInHex/deadmon/blob/8374bae533758270becfa4926151f879c3f30ba3/docs/adr/0020-dashboard-moves-to-nextjs.md): EC2/Vercel split and reported test count.
- [Repository business plan](https://github.com/GhostInHex/deadmon/blob/8374bae533758270becfa4926151f879c3f30ba3/docs/business-plan.md): original plan plus implementation-status and arithmetic-check notes.

Repository evidence reviewed 11 October 2026 UTC / 12 October 2026 IST. Revision prepared 12 October 2026 at 00:54 IST. Prices and forecast estimates are proposals by Ari, not external market evidence. This file is a static snapshot of the saved plan; later edits in cfo.ai will not update it automatically. The original assumptions and scenario figures have deliberately been preserved.

## 11. Change summary

- Replaced the obsolete documentation-only description with the implemented prototype’s actual scope.
- Distinguished recorded-fixture verdicts from live verification, and planned alerts/repair from established capabilities.
- Added the missing frontend-module finding, live-refresh and verification requirements, demo-only reset warning and test-count discrepancy.
- Distinguished the recommended individual Pro package from the higher-priced club package, without changing prices.
- Removed the implication that free-tier hosting or no inference call proves measured zero operating cost.
- Made paid launch capability-gated while leaving the model’s October/January assumptions explicitly provisional.
- Kept all financial assumptions, formulas and forecast figures unchanged; no GitHub changes or model-input edits were made by this file update.

