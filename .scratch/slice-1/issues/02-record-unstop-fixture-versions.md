# 02: Record the Unstop fixture versions that exercise the other two verdicts

**What to build:** Verification has to prove `unverified` and `closed` from
recorded pages, not from invented ones. Record what the platform actually
serves in those states and add each as a new fixture version beside the healthy
one, with provenance recorded so a future reader knows where it came from and
when.

**Blocked by:** None (can start immediately). Runs alongside 01 — it is recording
work with no code dependency.

**Status:** open
**Triage:** ready-for-agent

- [ ] New fixtures are recorded live from the public Unstop endpoint, never hand-edited, and never derived by editing the healthy fixture
- [ ] The healthy fixture is untouched — it stays the known-good baseline that a proposal must later reproduce
- [ ] Each new fixture is a new version added beside the old one; nothing is overwritten
- [ ] `fixtures/README.md` gains a provenance row per new file: source URL, record date, and the verdict state it exercises
- [ ] Where a state cannot be recorded live — a timeout or a hard block is not something a server will hand you as a file — that fact is written into `fixtures/README.md` and the state is covered by a declared test double instead
- [ ] A test double is named as a double wherever it appears, so no test result is mistaken for recorded evidence

## Comments
