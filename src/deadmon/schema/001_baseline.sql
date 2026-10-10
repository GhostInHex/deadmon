-- 001: Slice 1 baseline schema. Plural tables from the first commit.
-- DDL lives here; a committed database file is never the source of truth.
-- Card = a view over sources (one row per hackathon, many sources beneath).

CREATE TABLE IF NOT EXISTS hackathons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hackathon_id INTEGER NOT NULL REFERENCES hackathons(id),
    crawler TEXT NOT NULL,
    source_url TEXT NOT NULL,
    title TEXT NOT NULL,
    registration_close TEXT,
    mode TEXT,
    prize_summary TEXT,
    team_size_rule TEXT,
    eligibility_rules TEXT,
    registration_open TEXT,
    verdict TEXT NOT NULL,
    verified_at TEXT NOT NULL,
    UNIQUE (crawler, source_url)
);

CREATE TABLE IF NOT EXISTS crawl_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crawler TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    listings_found INTEGER NOT NULL DEFAULT 0,
    live_found INTEGER NOT NULL DEFAULT 0,
    closed_found INTEGER NOT NULL DEFAULT 0,
    trace_ref TEXT
);

CREATE TABLE IF NOT EXISTS subscribers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscriber_id INTEGER NOT NULL REFERENCES subscribers(id),
    mode TEXT,
    created_at TEXT NOT NULL
);
