# 04: Emit numbered hashed receipts per crawl run plus verify path

**What to build:** every crawl run is countable proof: it emits a
numbered receipt carrying a hash, and an edited receipt fails
verification. A local JSON fallback keeps the demo free of any login
wall.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Each crawl run emits a numbered receipt with a hash
- [ ] Verify path fails an edited receipt
- [ ] Local JSON fallback resolves with no login
- [ ] Receipts count crawl runs not cards
