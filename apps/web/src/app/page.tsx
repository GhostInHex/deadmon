import Link from 'next/link';
import { Nav, Footer } from '@/components/Nav';
import { getFeed, feedCounts } from '@/lib/api';

export const dynamic = 'force-dynamic';

export default async function Home() {
  // The figures are read from the crawl service, not typed in. If the service
  // is down they fall back to an em-dash rather than showing a stale number.
  const feed = await getFeed();
  const counts = feedCounts(feed);
  const live = feed ? String(counts.live) : '—';
  const unverified = feed ? String(counts.unverified) : '—';
  const runs = feed ? String(counts.runs) : '—';

  return (
    <>
      <Nav />

      {/* main holds the content only: nav and footer are repeated chrome and
          must not sit inside the landmark. */}
      <main id="main">
        <div className="hero">
          <span className="badge">
            <span className="badge__dot" />
            Deadline verification for hackathons
          </span>

        {/* Two-tone headline as sibling lines, never a nested colored span. */}
        <h1 className="display">
          <span className="display__line">Deadlines that stay true.</span>
          <span className="display__line display__accent">Literally.</span>
        </h1>

        <div className="hero__lead">
          <p className="lead">
            deadmon crawls hackathon platforms, checks that every listing is
            genuinely still open, and surfaces what is real &mdash; what is
            uncertain, and what quietly closed while you were looking elsewhere.
          </p>
        </div>

        <div className="hero__actions">
          <Link className="btn btn--primary btn--lg" href="/dashboard">
            Open the dashboard
          </Link>
          <Link className="btn btn--outline btn--lg" href="/#how">
            How it works
          </Link>
        </div>
      </div>

      <section className="stat-strip" aria-label="Current crawl">
        <div className="stat">
          <p className="stat__figure">{live}</p>
          <p className="stat__label">Live listings</p>
        </div>
        <div className="stat__divider" aria-hidden="true" />
        <div className="stat">
          <p className="stat__figure">{unverified}</p>
          <p className="stat__label">Needing attention</p>
        </div>
        <div className="stat__divider" aria-hidden="true" />
        <div className="stat">
          <p className="stat__figure">{runs}</p>
          <p className="stat__label">Traced runs</p>
        </div>
      </section>

      <section className="band" id="compare">
        <div className="band__inner">
          <p className="mono-label">Deadlines, not docs</p>
          <h2 className="band__title">Proves a deadline every day.</h2>
          <p className="lead">
            firstrun proves a doc once. deadmon proves every deadline every day:
            a daily full crawl plus a deadline sweep, and when a crawler breaks
            it heals with a sandbox-validated proposal then backfills the gap.
          </p>

          <table className="table" aria-label="deadmon vs firstrun vs Copilot">
            <thead>
              <tr>
                <th scope="col">Claim</th>
                <th scope="col">deadmon</th>
                <th scope="col">firstrun</th>
                <th scope="col">Copilot</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>What it proves</td>
                <td>Proves a deadline every day — full crawl plus deadline sweep</td>
                <td>Proves a doc once</td>
                <td>Answers once, proves nothing</td>
              </tr>
              <tr>
                <td>When a platform breaks</td>
                <td>Crawler heals: proposal, sandbox check, backfill</td>
                <td>Manual repair</td>
                <td>Manual repair</td>
              </tr>
              <tr>
                <td>Blocked pages</td>
                <td>Verdict unverified, kept visible in needs attention</td>
                <td>Known limit, silently dropped</td>
                <td>Silent guess or drop</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="band band--warm" id="cost">
        <div className="band__inner">
          <p className="mono-label">Cost</p>
          <h2 className="band__title">$0.00 per crawl, stdlib-only.</h2>
          <p className="lead">
            The current crawl path calls no model. firstrun reports $0.018 per
            run; deadmon adds no inference cost per crawl run.
          </p>

          <div className="costlist">
            <div className="cost">
              <p className="stat__figure stat__figure--signal">$0.00</p>
              <p className="stat__label">Modelled cost of a crawl</p>
              <p className="cost__note">
                Modelled, not measured: stdlib-only path calls no model, so a
                normal run adds no inference cost. Hosting and maintenance
                reserves are still carried in the plan. Tiers are a modelled
                draft from <code>docs/business-plan.md</code>, not traction.
              </p>
            </div>
            <div className="cost">
              <p className="stat__figure">$0.018</p>
              <p className="stat__label">firstrun reported cost per run</p>
              <p className="cost__note">
                His packaged figure, shown for scale. See{' '}
                <Link href="/pricing">pricing</Link> for the full modelled
                tiers.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="band" id="how">
        <div className="band__inner">
          <p className="mono-label">How it works</p>
          <h2 className="band__title">Three verdicts, never a guess.</h2>
          <p className="lead">
            Aggregators list dead deadlines as if they were live. deadmon refuses
            to guess. Every listing earns exactly one verdict, and anything it
            cannot prove stays visible rather than being quietly dropped.
          </p>

          <dl className="verdicts">
            <div className="verdict">
              <dt className="verdict__term">
                <span className="verdict__dot verdict__dot--live" />
                live
              </dt>
              <dd className="verdict__def">
                Source responded, the registration close parses to a real future
                date in a known timezone, and a mode was stated.
              </dd>
            </div>
            <div className="verdict">
              <dt className="verdict__term">
                <span className="verdict__dot verdict__dot--unverified" />
                unverified
              </dt>
              <dd className="verdict__def">
                We could not find out. Blocked, unreachable, or an unreadable
                date. Re-checked next crawl, never cached as fact.
              </dd>
            </div>
            <div className="verdict">
              <dt className="verdict__term">
                <span className="verdict__dot verdict__dot--closed" />
                closed
              </dt>
              <dd className="verdict__def">
                Registration has passed or the event was cancelled. Terminal,
                keeps its row, and leaves the feed.
              </dd>
            </div>
          </dl>
        </div>
      </section>

      <section className="band band--warm" id="evidence">
        <div className="band__inner">
          <p className="mono-label">Evidence</p>
          <h2 className="band__title">Every run is a trace.</h2>
          <p className="lead">
            Each crawl run produces one trace with per-stage spans, linked from
            the run history. When a platform changes its layout, the crawler
            diagnoses the break from the failing run and repairs its own
            adapter.
          </p>
          <div className="hero__actions band__actions">
            <Link className="btn btn--primary" href="/dashboard">
              Open run history
            </Link>
            <Link className="btn btn--outline" href="/pricing">
              See pricing
            </Link>
          </div>
        </div>
      </section>
      </main>

      <Footer />
    </>
  );
}