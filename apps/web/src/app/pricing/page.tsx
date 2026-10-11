import { Nav, Footer } from '@/components/Nav';

export const metadata = {
  title: 'deadmon — pricing',
  description:
    'deadmon pricing: Free, Community at ₹449 and Pro at ₹99. Modelled with cfo.ai Ari; assumptions are editable hypotheses, not traction.',
};

// Figures below come from docs/business-plan.md (cfo.ai Ari, 12 Oct 2026).
// They are a modelled draft, not observed performance.
const TIERS = [
  {
    name: 'Free',
    amount: '₹0',
    unit: 'forever',
    blurb: 'One alert profile and the full dashboard. No card, no trial clock.',
    items: [
      'All platform crawls, daily',
      'Verification with a visible verdict per source',
      'Run history with one trace per crawl',
    ],
    cta: { label: 'Start free', href: '/dashboard' },
  },
  {
    name: 'Community',
    amount: '₹449',
    unit: '/mo',
    blurb: 'A shared profile for a dev club or cohort, billed to the club admin.',
    items: [
      'Everything in Free',
      'Shared profile per subscriber (ADR-0006)',
      'Weekly digest instead of per-user alerts',
      'Heal log: every adapter repair, with its diff',
    ],
    cta: { label: 'Join the pilot', href: '/dashboard' },
    featured: true,
  },
  {
    name: 'Pro',
    amount: '₹99',
    unit: '/mo',
    blurb: 'For an individual, not a club. Additional personal profiles and exports.',
    items: [
      'One alert profile and the full dashboard',
      'Additional personal profiles',
      'Digest and feed exports',
      'Not the club package — that is Community',
    ],
    cta: { label: 'Read the plan', href: '/#evidence' },
  },
];

const ECONOMICS = [
  {
    figure: '₹415.53',
    label: 'Contribution per club',
    note: '₹449 price less ₹20 delivery reserve and a 3% payment fee, before shared overhead and founder pay.',
  },
  {
    figure: '~9',
    label: 'Clubs to cover fixed costs',
    note: 'Nine Community accounts cover the ₹3,500 monthly fixed costs alone. That is not company breakeven.',
  },
  {
    figure: '₹0.00',
    signal: true,
    label: 'Modelled cost of a crawl',
    note: 'The current crawl path calls no model, so a normal run adds no inference cost. Hosting and maintenance reserves are still carried in the plan — this is not a measured zero.',
  },
  {
    figure: '₹-182k',
    label: 'Downside cash, Sep 2028',
    note: 'Slower sales plus ₹10,000/month founder pay exhausts ₹25,000 of starting cash in November 2026.',
  },
];

export default function PricingPage() {
  return (
    <main className="page">
      <Nav />

      <div className="hero">
        <span className="badge">
          <span className="badge__dot" />
          Pricing
        </span>
        <h1 className="display">
          <span className="display__line">Verification you</span>
          <span className="display__line display__accent">can audit.</span>
        </h1>
        <div className="hero__lead">
          <p className="lead">
            The forecast assumes hosting and inference costs stay modest while
            crawling is shared across every account. Both are estimates. No
            production crawl has been measured, and the plan below keeps its
            hosting and crawl/AI reserves rather than assuming they are zero.
          </p>
        </div>
      </div>

      <section className="tiers" aria-label="Plans">
        {TIERS.map((tier) => (
          <article
            className={tier.featured ? 'tier tier--feature' : 'tier'}
            key={tier.name}
          >
            <p className="mono-label">{tier.name}</p>
            <p className="tier__price">
              <span className="tier__amount">{tier.amount}</span>
              <span className="tier__unit">{tier.unit}</span>
            </p>
            <p className="tier__blurb">{tier.blurb}</p>
            <ul className="tier__list">
              {tier.items.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
            <a
              className={
                tier.featured ? 'btn btn--primary tier__cta' : 'btn btn--outline tier__cta'
              }
              href={tier.cta.href}
            >
              {tier.cta.label}
            </a>
          </article>
        ))}
      </section>

      <section className="band">
        <div className="band__inner">
          <p className="mono-label">Unit economics</p>
          <h2 className="band__title">What a run actually costs.</h2>
          <p className="lead">
            Modelled by cfo.ai Ari from stated assumptions. They are projections,
            not measured costs: the current code path calls no model, but no
            production crawl, repair or maintenance effort has been measured yet.
          </p>

          <div className="costlist">
            {ECONOMICS.map((item) => (
              <div className="cost" key={item.label}>
                <p
                  className={
                    item.signal ? 'stat__figure stat__figure--signal' : 'stat__figure'
                  }
                >
                  {item.figure}
                </p>
                <p className="stat__label">{item.label}</p>
                <p className="cost__note">{item.note}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="band band--warm">
        <div className="band__inner">
          <p className="mono-label">Provenance</p>
          <h2 className="band__title">Read this before you judge the numbers.</h2>
          <div className="note">
            <p>
              <strong>This is a modelled plan, not a result.</strong> The tiers
              and forecasts were produced by <strong>cfo.ai Ari</strong> on 12
              October 2026 and are saved verbatim in{' '}
              <code>docs/business-plan.md</code>. No customer has been
              interviewed and no money has changed hands.
            </p>
            <p>
              <strong>The arithmetic was re-derived independently.</strong> All 18
              published outcomes &mdash; three scenarios &times; revenue, cash and
              12-month totals &mdash; reproduce from the stated assumptions
              within rounding, worst delta ₹0.50 on ₹1,494,359. That check
              proves the model is internally consistent. It does not make the
              assumptions true.
            </p>
            <p>
              <strong>The assumptions are the weak part.</strong> Growth rates,
              churn, ₹25,000 opening cash and the 3% payment fee are estimates.
              Ari&rsquo;s own recommendation is three paid club pilots before
              investing in Pro, and honest caution about one: <em>unpaid founder
              time is the hidden subsidy, and &ldquo;free inference&rdquo; does not
              mean a free business.</em>
            </p>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  );
}