"""The heal package: detection now, repair later.

`watch` decides whether a crawler broke; the steps that act on that decision —
proposal, sandbox validation, commit, backfill — arrive behind the same
boundary. A break has to be right before anything acts on it, which is why the
watchdog is a pure function of stored rows (ADR-0014, ADR-0016, ADR-0017).
"""
