/**
 * V7 Go — design system components
 * Tokens: ./tokens.css   Styles: ./components.css
 *
 * Rules enforced here:
 *   - No raw hex. Everything resolves through a token.
 *   - Two-tone headlines are split into sibling elements. A nested <span> for
 *     color is what Paper flattens; never reintroduce it.
 *   - Exactly one --color-signal element per viewport.
 */

import type { ReactNode } from 'react';

/* ---- Type primitives ----------------------------------------------------- */

export function Eyebrow({
  children,
  tone = 'default',
}: {
  children: ReactNode;
  tone?: 'default' | 'signal';
}) {
  return (
    <p className={`eyebrow${tone === 'signal' ? ' eyebrow--signal' : ''}`}>{children}</p>
  );
}

/**
 * Two-tone display headline.
 *
 * `base` and `accent` are rendered as siblings so the accent styling survives.
 * Pass plain strings — do not pass JSX.
 */
export function Display({
  base,
  accent,
  size = 'lg',
  level = 1,
}: {
  base: string;
  accent?: string;
  size?: 'lg' | 'sm';
  level?: 1 | 2 | 3;
}) {
  const Tag = `h${level}` as 'h1' | 'h2' | 'h3';
  return (
    <Tag className={`display${size === 'sm' ? ' display--sm' : ''}`}>
      <span className="display__line">{base}</span>
      {accent ? <span className="display__line display__accent">{accent}</span> : null}
    </Tag>
  );
}

export function Lead({ children }: { children: ReactNode }) {
  return <p className="lead">{children}</p>;
}

/* ---- Buttons -------------------------------------------------------------- */

type ButtonVariant = 'primary' | 'accent' | 'outline';

interface ButtonProps {
  children: ReactNode;
  variant?: ButtonVariant;
  size?: 'md' | 'lg';
  /** Renders a play glyph before the label. Decorative only. */
  withGlyph?: boolean;
  href?: string;
  onClick?: () => void;
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  withGlyph = false,
  href,
  onClick,
}: ButtonProps) {
  const cls = `btn btn--${variant}${size === 'lg' ? ' btn--lg' : ''}`;
  const content = (
    <>
      {withGlyph ? <span className="btn__glyph" aria-hidden="true" /> : null}
      {children}
    </>
  );

  if (href) {
    return (
      <a className={cls} href={href}>
        {content}
      </a>
    );
  }
  return (
    <button className={cls} type="button" onClick={onClick}>
      {content}
    </button>
  );
}

/* ---- Badge ---------------------------------------------------------------- */

export function Badge({ children }: { children: ReactNode }) {
  return (
    <span className="badge">
      <span className="badge__dot" aria-hidden="true" />
      {children}
    </span>
  );
}

/* ---- Stats ---------------------------------------------------------------- */

export interface Stat {
  figure: string;
  label: string;
  /** Reserve for at most one figure per strip. */
  signal?: boolean;
}

export function StatStrip({ stats }: { stats: Stat[] }) {
  return (
    <div className="stat-strip">
      {stats.map((stat, i) => (
        <div key={stat.label} style={{ display: 'contents' }}>
          {i > 0 ? <div className="stat__divider" aria-hidden="true" /> : null}
          <div className="stat">
            <p className={`stat__figure${stat.signal ? ' stat__figure--signal' : ''}`}>
              {stat.figure}
            </p>
            <span className="stat__label">{stat.label}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ---- Nav ------------------------------------------------------------------ */

const NAV_LINKS = [
  'Context Graph',
  'Workflow Agents',
  'Doc Generation',
  'Integrations',
  'Security',
] as const;

export function Nav() {
  return (
    <nav className="nav" aria-label="Main">
      <a className="nav__brand" href="/">
        <span className="nav__mark" aria-hidden="true">
          <span className="nav__mark-inner" />
        </span>
        <span className="nav__wordmark">V7</span>
      </a>

      <div className="nav__links">
        {NAV_LINKS.map((label) => (
          <a className="nav__link" key={label} href="#">
            {label}
          </a>
        ))}
      </div>

      <div className="nav__actions">
        <a className="nav__link" href="#">
          Log in
        </a>
        <Button href="/demo" size="lg">
          Book a demo
        </Button>
      </div>
    </nav>
  );
}

/* ---- Hero ----------------------------------------------------------------- */

export function Hero() {
  return (
    <>
      <div className="hero">
        <Badge>Operational AI for private markets</Badge>

        <Display base="Complex workflows." accent="Zero room for error." />

        <div className="hero__lead">
          <Lead>
            Turn hundreds of pages of instructions into AI workflows for due diligence,
            underwriting, and claims. Run complex operations at scale.
          </Lead>
        </div>

        <div className="hero__actions">
          <Button href="/demo" size="lg">
            Book a demo
          </Button>
          <Button variant="outline" size="lg" withGlyph>
            Watch video
          </Button>
        </div>
      </div>

      <StatStrip
        stats={[
          { figure: '21x', label: 'Faster processing' },
          { figure: '54%', label: 'Fewer errors' },
          { figure: '5x', label: 'More opportunities', signal: true },
          { figure: '300+', label: 'Integrations & MCPs' },
        ]}
      />
    </>
  );
}

/* ---- Design-system documentation ------------------------------------------ */

const PALETTE = [
  { name: 'Ink', hex: '#292929', cls: 'swatch--dark', style: { background: 'var(--color-ink)' } },
  {
    name: 'Ink Deep',
    hex: '#171717',
    cls: 'swatch--dark',
    style: { background: 'var(--color-ink-deep)' },
  },
  {
    name: 'Paper',
    hex: '#FFFFFF',
    cls: 'swatch--bordered',
    style: { background: 'var(--color-paper)' },
  },
  {
    name: 'Paper Warm',
    hex: '#F7F6F5',
    cls: 'swatch--bordered',
    style: { background: 'var(--color-paper-warm)' },
  },
  {
    name: 'Signal',
    hex: '#FF683D',
    cls: 'swatch--signal',
    style: { background: 'var(--color-signal)' },
  },
] as const;

/** Ramp is monotonic by construction: bar height = the token value it labels. */
const RAMP = [
  { label: '4', px: 4, cls: '' },
  { label: '8', px: 8, cls: '' },
  { label: '12', px: 12, cls: '' },
  { label: '16', px: 16, cls: '' },
  { label: '24', px: 24, cls: '' },
  { label: '32', px: 32, cls: '' },
  { label: '48', px: 48, cls: '' },
  { label: '64', px: 64, cls: '' },
  { label: '96', px: 96, cls: '' },
  { label: 'pill', px: 48, cls: 'ramp__bar--pill' },
] as const;

export function DesignSystemPage() {
  return (
    <div className="ds">
      <header
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 10,
          paddingBottom: 28,
          borderBottom: '1px solid var(--color-rule)',
        }}
      >
        <Eyebrow tone="signal">Design System v1.0</Eyebrow>
        <Display base="V7 Go —" accent="industrial precision" size="sm" />
        <p className="body" style={{ color: 'var(--color-ink-muted)' }}>
          Every value below is a live design token. Reference them as CSS variables — no raw
          hex in components.
        </p>
      </header>

      <section className="ds__section">
        <Eyebrow>01 — Palette</Eyebrow>
        <div className="ds__swatches">
          {PALETTE.map((s) => (
            <div className={`swatch ${s.cls}`} style={s.style} key={s.name}>
              <span className="swatch__name">{s.name}</span>
              <span className="swatch__hex">{s.hex}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="ds__section">
        <Eyebrow>02 — Typography</Eyebrow>
        <div className="ds__row">
          <Display base="Display" size="sm" />
          <span className="spec">Instrument Serif · 40 / 44 · -0.02em</span>
        </div>
        <div className="ds__row">
          <span
            style={{
              fontFamily: 'var(--webfont-display)',
              fontSize: '28px',
              fontStyle: 'italic',
              color: 'var(--color-signal)',
            }}
          >
            Display italic — emphasis
          </span>
          <span className="spec">28 / 34 · italic accent</span>
        </div>
        <div className="ds__row">
          <span style={{ fontSize: 'var(--text-md)', color: 'var(--color-ink)' }}>
            Body — Inter regular for lead paragraphs.
          </span>
          <span className="spec">16 / 26</span>
        </div>
        <div className="ds__row">
          <Eyebrow>Mono label — DM Mono uppercase</Eyebrow>
          <span className="spec">11 / 14 · 0.08em</span>
        </div>
      </section>

      <section className="ds__section">
        <Eyebrow>03 — Components</Eyebrow>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          <Button>Book a demo</Button>
          <Button variant="accent">Get in touch</Button>
          <Button variant="outline">Watch video</Button>
          <Badge>New</Badge>
        </div>
      </section>

      <section className="ds__section">
        <Eyebrow>04 — Spacing &amp; radius</Eyebrow>
        <div className="ramp">
          {RAMP.map((r) => (
            <div className="ramp__item" key={r.label}>
              <div className={`ramp__bar ${r.cls}`} style={{ height: r.px }} />
              <span className="ramp__label">{r.label}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}