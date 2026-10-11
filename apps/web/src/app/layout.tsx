import type { Metadata } from 'next';
import './tokens.css';
import './app.css';

export const metadata: Metadata = {
  title: 'deadmon — an agent that never misses a deadline',
  description:
    'deadmon crawls hackathon platforms, verifies every listing is still live, and tells you before registration closes.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        {/* Instrument Serif, Inter and DM Mono — the design system's three families. */}
        <link
          href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}