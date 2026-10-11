import { Nav, Footer } from '@/components/Nav';

export const metadata = {
  title: 'deadmon — pricing',
  description:
    'deadmon pricing: verification you can audit, at near-zero marginal cost.',
};

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
            deadmon&rsquo;s cost is dominated by inference, not hosting. Crawling,
            storage and the dashboard run inside one free-tier instance; the
            agent&rsquo;s fix proposals are the only line item that scales with
            usage.
          </p>
        </div>
      </div>

      {/* TIER PRICES ARE NOT SET. Every figure below is a placeholder. */}
      <section className="tiers" aria-label="Plans">
        <article className="tier">
          <p className="mono-label">Solo</p>
          <p className="tier__price">
            <span className="tier__unset">&mdash;</span>
            <span className="tier__unit">/mo</span>
          </p>
          <p className="tier__blurb">
            One profile, every platform, alerts on the deadlines you pick.
          </p>
          <ul className="tier__list">
            <li>All platform crawls, daily</li>
            <li>Verification with a visible verdict per source</li>
            <li>Telegram alerts at 7d / 3d / 24h</li>
            <li>Run history with one trace per crawl</li>
          </ul>
          <span className="badge badge--neutral">price pending</span>
        </article>

        <article className="tier tier--feature">
          <p className="mono-label">Club</p>
          <p className="tier__price">
            <span className="tier__unset">&mdash;</span>
            <span className="tier__unit">/mo</span>
          </p>
          <p className="tier__blurb">
            A shared feed for a dev club or cohort, with per-member eligibility
            filtering.
          </p>
          <ul className="tier__list">
            <li>Everything in Solo</li>
            <li>Shared profile per subscriber (ADR-0006)</li>
            <li>Weekly digest instead of per-user spam</li>
            <li>Heal log: every adapter repair, with its diff</li>
          </ul>
          <span className="badge badge--neutral">price pending</span>
        </article>

        <article className="tier">
          <p className="mono-label">Self-hosted</p>
          <p className="tier__price">
            <span className="tier__amount tier__amount--signal">$0</span>
            <span className="tier__unit">to start</span>
          </p>
          <p className="tier__blurb">
            Run it on one instance you control. The pipeline is stdlib-only by
            design.
          </p>
          <ul className="tier__list">
            <li>Full source, MIT</li>
            <li>Your own AWS allowance or any t3.micro</li>
            <li>Traces to your own neatlogs project</li>
            <li>No inference cost unless you enable self-heal</li>
          </ul>
          <a className="btn btn--outline" href="/dashboard">
            Read the deploy notes
          </a>
        </article>
      </section>

      <section className="band">
        <div className="band__inner">
          <p className="mono-label">Unit economics</p>
          <h2 className="band__title">What a run actually costs.</h2>
          <p className="lead">
            These are measured from this repository, not estimated. Hosted cost
            is zero on free tier; inference is the only variable line, and it is
            only incurred when the agent proposes a fix.
          </p>

          <div className="costlist">
            <div className="cost">
              <p className="stat__figure">$0.00</p>
              <p className="stat__label">Crawl + verify + store + render</p>
              <p className="cost__note">
                One t3.micro inside the free tier. No database, queue or cache
                service.
              </p>
            </div>
            <div className="cost">
              <p className="stat__figure">$0.00</p>
              <p className="stat__label">Trace per crawl run</p>
              <p className="cost__note">
                Traced to neatlogs on the free project tier; local JSON sink
                otherwise.
              </p>
            </div>
            <div className="cost">
              <p className="stat__figure stat__figure--signal">$0.00</p>
              <p className="stat__label">Steady-state inference</p>
              <p className="cost__note">
                No model is called during a normal crawl. Token and cost are
                recorded as 0 by fact, not omitted.
              </p>
            </div>
            <div className="cost">
              <p className="stat__figure">$20</p>
              <p className="stat__label">Shared LLM budget, 30 days</p>
              <p className="cost__note">
                Team-wide hackathon allowance, the ceiling for self-heal
                proposals during the event.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="band band--warm">
        <div className="band__inner">
          <p className="mono-label">Provenance</p>
          <h2 className="band__title">Read this before you judge the numbers.</h2>
          <div className="note">
            <p>
              <strong>The cost figures above are measured from this repo.</strong>{' '}
              They come from running the pipeline and reading the run history,
              and they are the numbers I can defend.
            </p>
            <p>
              <strong>The tier prices are not set.</strong> They are shown as
              &ldquo;&mdash;&rdquo; because choosing them is a business decision, not
              a rendering one. Nothing on this page has been produced by cfo.ai
              &mdash; Ari was not available to generate it, and inventing pricing
              or revenue would misrepresent the work.
            </p>
            <p>
              <strong>Runway is therefore not stated.</strong> Runway needs a
              price, a conversion assumption and a cost-per-user figure, none of
              which exist yet. See <code>docs/business-plan.md</code> once those
              are supplied.
            </p>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  );
}