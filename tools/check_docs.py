#!/usr/bin/env python3
"""Pre-commit checks for deadmon docs.

Mechanical invariants that have already been violated by hand:
  - every docs/adr/*.md link in AGENTS.md resolves
  - GLOSSARY.md defines each term exactly once
  - the term count asserted in AGENTS.md matches the file
  - no line-number citations (doc.md:12) across files - they rot silently
"""
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
failures = []


def fail(msg: str) -> None:
    failures.append(msg)


agents = (root / "AGENTS.md").read_text(encoding="utf-8")
glossary = (root / "GLOSSARY.md").read_text(encoding="utf-8")

# 1. ADR links resolve
for target in set(re.findall(r"\((docs/adr/[^)]+\.md)\)", agents)):
    if not (root / target).is_file():
        fail(f"AGENTS.md links to {target}, which does not exist")

# 2. no duplicate glossary definitions
terms = re.findall(r"^\*\*([A-Za-z][A-Za-z ]*)\*\*:", glossary, re.M)
dupes = {t for t in terms if terms.count(t) > 1}
if dupes:
    fail(f"GLOSSARY.md defines more than once: {', '.join(sorted(dupes))}")

# 3. asserted term count matches reality
declared = re.search(r"GLOSSARY\.md` — (\d+) terms", agents)
if not declared:
    fail("AGENTS.md does not assert a GLOSSARY.md term count (expected 'GLOSSARY.md` — N terms')")
elif int(declared.group(1)) != len(terms):
    fail(f"AGENTS.md says {declared.group(1)} glossary terms; GLOSSARY.md defines {len(terms)}")

# 4. no cross-file line-number citations
for path in [root / "AGENTS.md", root / ".gitignore", *sorted((root / "docs" / "adr").glob("*.md"))]:
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for m in re.finditer(r"[\w./-]+\.(?:md|py|txt):\d+", line):
            rel = path.relative_to(root)
            fail(f"{rel}:{i} cites {m.group(0)} - line numbers rot; cite doc + section heading")

if failures:
    print("docs-check failed:\n  " + "\n  ".join(failures))
    sys.exit(1)
print(f"docs-check ok ({len(terms)} glossary terms, ADR links resolve)")