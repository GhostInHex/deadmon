import Link from 'next/link';
import { Nav, Footer } from '@/components/Nav';

export const metadata = {
  title: 'deadmon — for judges',
  description: 'Score deadmon in 60 seconds.',
};

// Figures: rubric weights docs/SPONSORS.md. Corpus: fixtures/unstop with
// --as-of 2026-10-11, asserted in tests/test_crawl.py: 25 live, 49 closed,
// 3 unverified, 4 crawl runs, 22 feed cards + 3 needing attention.
const ROWS = [
  { c: 'One verdict per source: live, unverified, closed. Fails closed.', k: 'The agent', w: '30%', v: 'py -m pytest -q tests/test_verification.py' },
  { c: 'Feed holds live cards; needs attention holds unverified greyed.', k: 'The agent', w: '30%', v: 'py -m pytest -q tests/test_dashboard.py' },
  { c: 'One trace per crawl run, linked from run history, no login wall.', k: 'Use of the tools', w: '25%', v: 'py -m pytest -q tests/test_tracing.py' },
  { c: 'v1 naive shows 77 live (52 wrong); v2 feeds 22, keeps 3 visible.', k: 'Use of the tools', w: '25%', v: 'py -m pytest -q tests/test_crawl.py' },
  { c: 'Deterministic replay from recorded fixtures, no live network.', k: 'Demo video', w: '20%', v: 'deadmon-crawl --reset --no-serve' },
  { c: 'Public repo, commits Oct 10-12, fixtures versioned never overwritten.', k: 'Building in public', w: '15%', v: 'https://github.com/GhostInHex/deadmon' },
  { c: 'Blocked pages stay unverified; a login wall never drops a deadline.', k: 'Usefulness', w: '10%', v: 'deadmon-crawl --port 8080' },
];


const PAIR = [
  { m: 'Candidates in (same corpus)', a: '77', b: '77' },
  { m: 'Shown as live', a: '77, all extracted', b: '25 live sources, 22 cards' },
  { m: 'False positives', a: '49', b: '0' },
  { m: 'Unverified kept visible', a: '0', b: '3 cards needing attention' },
  { m: 'Closed rows retained', a: 'none', b: '49 rows, out of feed' },
  { m: 'Cost per crawl', a: '$0.00 stdlib-only', b: '$0.00 stdlib-only' },
  { m: 'Traces', a: 'none', b: '4 documents, fetch to store' },
];

const COMMANDS = [
  'py -m pytest -q',
  'deadmon-crawl --reset --no-serve --as-of 2026-10-11T00:00:00+00:00',
  'deadmon-crawl --port 8080',
  'deadmon-receipt-check',
];
export default function JudgesPage() {
  return (
    <>
      <Nav />

      {/* main holds the content only: nav and footer are repeated chrome and
          must not sit inside the landmark. */}
      <main id="main">
      <div className="hero">
        <span className="badge"><span className="badge__dot" />For judges</span>
        <h1 className="display">
          <span className="display__line">Score deadmon</span>
          <span className="display__line display__accent">in 60 seconds.</span>
        </h1>
        <div className="hero__lead">
          <p className="lead">Each claim maps to a rubric weight with a copy-paste verify command.</p>
        </div>
      </div>
      <section className="band" aria-label="Rubric map">
        <div className="band__inner">
          <p className="mono-label">Rubric map</p>
          <h2 className="band__title">Every claim, its weight, its proof.</h2>
          <table className="table">
            <thead><tr><th>claim</th><th>criterion</th><th>weight</th><th>verify</th></tr></thead>
            <tbody>
              {ROWS.map((r) => (
                <tr key={r.c.slice(0, 24)}><td>{r.c}</td><td>{r.k}</td><td>{r.w}</td><td><code>{r.v}</code></td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section className="band band--warm" aria-label="Trace pair">
        <div className="band__inner">
          <p className="mono-label">Trace pair</p>
          <h2 className="band__title">v1 naive vs v2 verified.</h2>
          <table className="table">
            <thead><tr><th>metric</th><th>v1 naive</th><th>v2 measured</th></tr></thead>
            <tbody>
              {PAIR.map((r) => (
                <tr key={r.m}><td>{r.m}</td><td>{r.a}</td><td>{r.b}</td></tr>
              ))}
            </tbody>
          </table>
          <div className="note"><p><strong>Traces</strong> link from <Link href="/dashboard">run history</Link> — serve with <code>deadmon-crawl --port 8080</code>.</p></div>
        </div>
      </section>
      <section className="band" aria-label="Receipts">
        <div className="band__inner">
          <p className="mono-label">Receipts</p>
          <h2 className="band__title">4 runs, 4 documents, 1 hash check.</h2>
          <table className="table">
            <thead><tr><th>crawl run</th><th>verdicts</th><th>trace</th></tr></thead>
            <tbody>
              <tr><td>Unstop crawler, open</td><td>25 live</td><td>1 per run</td></tr>
              <tr><td>Unstop crawler, closed</td><td>24 closed</td><td>1 per run</td></tr>
              <tr><td>Unstop crawler, past</td><td>25 closed</td><td>1 per run</td></tr>
              <tr><td>Unstop crawler, double</td><td>3 unverified</td><td>1 per run</td></tr>
            </tbody>
          </table>
          <div className="note"><p><strong>Hash check:</strong> run <code>deadmon-receipt-check</code> — an edited receipt fails.</p></div>
        </div>
      </section>
      <section className="band band--warm" aria-label="Verify">
        <div className="band__inner">
          <p className="mono-label">Verify</p>
          <h2 className="band__title">Copy, paste, believe.</h2>
          <div className="note">
            {COMMANDS.map((cmd) => (<p key={cmd}><code>{cmd}</code></p>))}
            <p><strong>Heal in flight:</strong> a crawler break becomes a proposal, validated in sandbox, then backfill. MLH zero stays steady state.</p>
          </div>
        </div>
      </section>
      </main>

      <Footer />
    </>
  );
}