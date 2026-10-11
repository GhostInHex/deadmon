# Deadmon — draft business plan

Prepared with cfo.ai Ari · 12 October 2026 (IST)

**Status:** proposed plan, not observed financial performance. All amounts are INR. Forecast: October 2026–September 2028; September 2026 is an estimated opening point. Public repository documentation supplies product context, not proof of implementation, customers or cash. No credentials or private repository access are included.

## 1. The business

Deadmon is a scheduled hackathon-discovery agent: it crawls listings, verifies that deadlines and eligibility remain valid, filters for a profile, and sends dashboard/Telegram alerts. Its proposed differentiator is a traced, sandbox-validated scraper repair loop. The public README says implementation code has been removed and the repository currently contains documentation and specs.

The initial paying buyer is a college developer club/community admin who hand-curates deadline digests. Students use Free; clubs pay for the saved weekly curation effort. This buyer and proposed revenue logic come from the PRD, not customer interviews.

## 2. Pricing and launch scope

| Tier | Proposed monthly price | Offer | Status |
|---|---:|---|---|
| Free | ₹0 | One alert profile and dashboard | Specified in PRD |
| Community | ₹449 | Shared club profile and weekly digest | Within PRD ₹399–499 range; unvalidated |
| Pro | ₹99 | More profiles and exports | Ari proposal; later product experiment |

Do not sell "never misses a deadline" as a service guarantee. Explain verification freshness, unverified listings and failed-platform coverage clearly.

Paid launch is assumed October 2026 for Community and January 2027 for Pro. These dates depend on shipping the needed profile, authentication and billing capabilities; the hackathon scope explicitly excludes multi-user accounts, a public API and broader alert channels. Keep those ambitions out of the hackathon build. A free user and Pro account are distinct modeled populations; there is no verified conversion funnel.

## 3. Editable planning inputs

All inputs below are estimates, except the source's Community price range and feature descriptions. They are visible in the saved cfo.ai plan.

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

- Interview 10 club admins; test ₹399, ₹449 and ₹499 offers, without assuming any has been validated.
- Target 3 paid pilots and measure digest usage, weekly active users, churn, manual curation time saved and willingness to renew.
- Instrument requests, inference usage, retries, repair success and human maintenance time; cap the repair budget.
- Validate platform scraping terms, rate limits and graceful degradation. Prefer structured endpoints and cache shared crawls.
- Sandbox repair patches, protect credentials, require approval for risky changes and retain trace/commit evidence. A passing fixture is not a guarantee against live-site changes.
- Check multi-profile/auth and billing requirements before a paid launch. Pro exports are not a public API commitment.
- Confirm hosting, model quotas and observability retention; sponsor/free-tier access may expire.
- Obtain actual opening cash and required personal monthly pay before calling this an operating budget.

## 8. Hackathon-ready demo wording

> "Ari modeled Free, Community at ₹449 and a later ₹99 Pro tier. Shared crawls keep infrastructure costs modest, but unpaid founder time is the hidden subsidy. Under our draft acquisition assumptions, the base cash flow turns positive in December; slower sales plus ₹10,000 founder pay exhaust ₹25,000 of starting cash in November. These are editable hypotheses—we'll validate them with three paid club pilots."

## 9. What was checked

All 25 opening/forecast month values for revenue, operating cash surplus and closing cash in each of the three scenarios were compared with a separate reconstruction from the assumptions. They agree within rounding. The first Pro month and pre-launch zeroes were checked; downside founder payroll is ₹10,000/month. January–March 2027 revenue is ₹27,032.59 and quarter-end cash is ₹31,741.79, matching the monthly calculations. Opening cash remains ₹25,000 across scenarios.

The cfo.ai cash simulator renders in light and dark themes. Its extra-spending control is a local preview until Apply is selected; buttons and clicks were not exercised during rendering checks. Market demand, live implementation, actual costs, real customers and bank balances remain unverified.

## 10. Source documents

- [Public repository / README](https://github.com/GhostInHex/deadmon): product positioning, documentation-only status and hackathon deliverable.
- [PRD](https://github.com/GhostInHex/deadmon/blob/main/docs/PRD.md): feature scope, Community price range, buyer and revenue logic, constraints.
- [Build plan](https://github.com/GhostInHex/deadmon/blob/main/docs/PLAN.md): phased implementation, demo requirements and later Community tier.

Sources accessed 11 October 2026 UTC / 12 October 2026 IST. Prices and forecast estimates are proposals by Ari, not external market evidence. This file is a static snapshot of the saved plan; later edits in cfo.ai will not update it automatically.

---

## Note added at commit time

Two things above are now out of date, and both are because the plan was written
against the README as it stood on 11 October, before Slice 1 landed:

1. **"Implementation code has been removed / documentation only"** — no longer
   true. The crawl pipeline runs: 111 offline tests, one crawl command, a
   dashboard, and a deploy. See `README.md` and `docs/adr/0020-*`.
2. **Repository URL** is `github.com/GhostInHex/deadmon`, not the
   `neathack/deadmon` placeholder in `deploy/README.md` and the app's nav.

Section 9's claim that every forecast month was independently reconstructed was
made by cfo.ai checking itself, so the forecast was **re-derived here from the
stated assumptions**, separately. All 18 published outcomes — three scenarios ×
revenue, cash and 12-month totals — reproduce within rounding, worst delta ₹0.50
on a figure of ₹1,494,359. The per-account contribution matches exactly
(₹449 − ₹20 − ₹13.47 = ₹415.53).

That check confirms the arithmetic is internally consistent. It does **not**
validate the assumptions: the growth rates, churn, ₹25,000 opening cash and 3%
fee are Ari's estimates, and no customer has been interviewed.