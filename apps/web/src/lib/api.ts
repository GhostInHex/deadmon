/**
 * The seam between the Python crawl service and this app (ADR-0020).
 *
 * The pipeline stays in Python and owns every fact here; this module only
 * types and fetches it. Types mirror `deadmon.dashboard.view_as_json` field for
 * field — if one side renames a field, TypeScript errors at the call site
 * instead of the page silently rendering an empty feed.
 */

export type Verdict = 'live' | 'unverified' | 'closed';

export interface CardSource {
  crawler: string;
  source_url: string;
  verdict: Verdict;
  stated_close: string | null;
  stated_close_display: string;
  verified_at: string;
  verified_at_display: string;
}

export interface Card {
  title: string;
  earliest_credible_close: string | null;
  earliest_credible_close_display: string;
  sources: CardSource[];
}

export interface Run {
  id: number;
  crawler: string;
  started_at: string;
  finished_at: string;
  status: string;
  live_found: number;
  closed_found: number;
  duration: string;
  trace_ref: string | null;
}

export interface Feed {
  feed: Card[];
  needs_attention: Card[];
  needs_attention_by_crawler: Record<string, number>;
  runs: Run[];
}

/** Public so a deploy can point at the instance without a rebuild. */
const BASE =
  process.env.NEXT_PUBLIC_DEADMON_API ??
  'http://127.0.0.1:8080';

/**
 * Fetch the feed, or return null when the crawl service is unreachable.
 *
 * Null rather than throw: the page is still worth rendering without it, and a
 * dead backend should read as "no data yet", not as a 500 on the marketing
 * site. Every caller handles the null branch explicitly.
 */
export async function getFeed(): Promise<Feed | null> {
  try {
    const res = await fetch(`${BASE}/api/feed`, {
      cache: 'no-store',
      signal: AbortSignal.timeout(4000),
    });
    if (!res.ok) return null;
    return (await res.json()) as Feed;
  } catch {
    return null;
  }
}

/** True when the feed is live. Unverified is never counted as a listing. */
export function feedCounts(feed: Feed | null): {
  live: number;
  unverified: number;
  runs: number;
} {
  if (!feed) return { live: 0, unverified: 0, runs: 0 };
  return {
    live: feed.feed.length,
    unverified: feed.needs_attention.length,
    runs: feed.runs.length,
  };
}