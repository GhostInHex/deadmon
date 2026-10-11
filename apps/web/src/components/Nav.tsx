import Link from 'next/link';

const LINKS = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/#how', label: 'How it works' },
  { href: '/pricing', label: 'Pricing' },
  { href: '/#evidence', label: 'Evidence' },
];

export function Nav() {
  return (
    <>
      {/* First focusable element on every page: the nav is repeated chrome on
          all three routes, so a keyboard user gets past it in one stop. */}
      <a className="skip" href="#main">
        Skip to content
      </a>
      <nav className="nav" aria-label="Main">
        <Link className="nav__brand" href="/">
          <span className="nav__mark" aria-hidden="true">
            <span className="nav__mark-inner" />
          </span>
          <span className="nav__wordmark">deadmon</span>
        </Link>

        <div className="nav__links">
          {LINKS.map((link) => (
            <Link className="nav__link" key={link.href} href={link.href}>
              {link.label}
            </Link>
          ))}
        </div>

        <div className="nav__actions">
          <a
            className="nav__link"
            href="https://github.com/GhostInHex/deadmon"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
          <Link className="btn btn--primary btn--lg" href="/dashboard">
            See it live
          </Link>
        </div>
      </nav>
    </>
  );
}

export function Footer() {
  return (
    <footer className="foot">
      <p className="foot__inner">
        deadmon &mdash; built for #neatHack. Crawl, verify, store, trace.
      </p>
    </footer>
  );
}