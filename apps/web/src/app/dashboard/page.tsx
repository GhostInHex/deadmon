import { Nav, Footer } from '@/components/Nav';
import { getFeed, type Card, type Run, type Verdict } from '@/lib/api';

export const dynamic = 'force-dynamic';

function VerdictBadge({ verdict }: { verdict: Verdict }) {
  return (
    <span className={verdict === 'live' ? 'badge' : 'badge badge--neutral'}>
      {verdict}
    </span>
  );
}

function CardRow({ card, greyed }: { card: Card; greyed?: boolean }) {
  return (
    <article className={greyed ? 'card card--greyed' : 'card'}>
      <h3 className="card__title">{card.title}</h3>
      <p className="card__close">
        {greyed
          ? 'no credible registration close · unverified'
          : `registration close ${card.earliest_credible_close_display}`}
      </p>
      <ul className="sources">
        {card.sources.map((source) => (
          <li className="source" key={`${source.crawler}-${source.source_url}`}>
            <a href={source.source_url} rel="nofollow noopener noreferrer">
              {source.source_url}
            </a>
            <VerdictBadge verdict={source.verdict} />
            <span className="source__meta">
              stated close {source.stated_close_display}
            </span>
            <span className="source__meta">
              verified {source.verified_at_display}
            </span>
          </li>
        ))}
      </ul>
    </article>
  );
}

function RunTable({ runs }: { runs: Run[] }) {
  return (
    <table className="table">
      <thead>
        <tr>
          <th>crawler</th>
          <th>status</th>
          <th>live</th>
          <th>closed</th>
          <th>duration</th>
          <th>trace</th>
        </tr>
      </thead>
      <tbody>
        {runs.map((run) => (
          <tr key={run.id}>
            <td>{run.crawler}</td>
            <td>{run.status}</td>
            <td>{run.live_found}</td>
            <td>{run.closed_found}</td>
            <td>{run.duration}</td>
            <td>
              {run.trace_ref ? (
                <a href={`${process.env.NEXT_PUBLIC_DEADMON_API ?? 'http://127.0.0.1:8080'}/trace/${encodeURIComponent(run.trace_ref)}`}>
                  {run.trace_ref}
                </a>
              ) : (
                <span className="empty">none</span>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default async function DashboardPage() {
  const feed = await getFeed();

  return (
    <main className="page">
      <Nav />

      <div className="dash">
        <header className="dash__head">
          <h1 className="display" style={{ fontSize: 'var(--text-2xl)', lineHeight: 'var(--leading-heading)' }}>
            deadmon
          </h1>
          {feed ? (
            <div className="dash__summary">
              <span className="badge">
                {feed.feed.length} card{feed.feed.length === 1 ? '' : 's'} in the feed
              </span>
              <span className="badge badge--neutral">
                {feed.needs_attention.length} needing attention
              </span>
              <span className="badge badge--neutral">
                {Object.keys(feed.needs_attention_by_crawler).join(', ') || 'no crawler'}
              </span>
            </div>
          ) : (
            <p className="empty">
              The crawl service is not reachable. Start it with{' '}
              <code>deadmon-crawl</code> and reload.
            </p>
          )}
        </header>

        <section>
          <h2 className="section__title">
            Feed <span>{feed ? feed.feed.length : 0}</span>
          </h2>
          {feed && feed.feed.length > 0 ? (
            feed.feed.map((card) => <CardRow card={card} key={card.title} />)
          ) : (
            <p className="empty">Nothing in the feed.</p>
          )}
        </section>

        <section>
          <h2 className="section__title">
            Needs attention <span>{feed ? feed.needs_attention.length : 0}</span>
          </h2>
          {feed && feed.needs_attention.length > 0 ? (
            feed.needs_attention.map((card) => (
              <CardRow card={card} greyed key={card.title} />
            ))
          ) : (
            <p className="empty">Nothing needs attention.</p>
          )}
        </section>

        <section>
          <h2 className="section__title">
            Run history <span>{feed ? feed.runs.length : 0}</span>
          </h2>
          {feed && feed.runs.length > 0 ? (
            <RunTable runs={feed.runs} />
          ) : (
            <p className="empty">No runs recorded.</p>
          )}
        </section>
      </div>

      <Footer />
    </main>
  );
}