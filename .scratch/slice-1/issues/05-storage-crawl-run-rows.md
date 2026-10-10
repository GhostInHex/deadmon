# 05: Storage: a crawl run writes hackathon and source rows, and can be read back

**What to build:** A crawl's output becomes state. Candidates carrying verdicts
are written as hackathons and sources, the run that produced them is recorded,
and a run that is killed mid-flight resumes without duplicating rows or
re-asserting a verdict it already holds.

**Blocked by:** 01 (the schema and the verdict model).

**Status:** open
**Triage:** blocked

- [ ] One crawl run row is recorded per crawler per execution, with start, finish, status, listings found, and its trace reference
- [ ] A live candidate creates one hackathon with one source beneath it, keyed so a second crawl of the same source updates rather than duplicates
- [ ] An unverified candidate keeps a record in exactly the same way — unverified is a stored verdict, not a skipped row
- [ ] A closed verdict is retained with its row intact
- [ ] Re-running the same crawl against the same fixture produces no duplicate rows and no second verdict for the same source
- [ ] A run interrupted mid-write leaves the database consistent and resumable
- [ ] The subscriber and profile tables exist and are empty at this stage, because the model is not a singleton even though the demo runs with exactly one
- [ ] No committed database file is the source of truth; the schema files are
- [ ] A test kills a run part-way through and asserts no duplicate rows and no duplicated alerts

## Comments
