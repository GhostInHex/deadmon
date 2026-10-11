/**
 * V7 Go — landing page
 * Tokens: ./tokens.css   Styles: ./components.css
 *
 * Composes Nav + Hero. The stat strip is part of Hero.
 */

import { Nav, Hero } from './components';

export default function LandingPage() {
  return (
    <main className="page">
      <Nav />
      <Hero />
    </main>
  );
}