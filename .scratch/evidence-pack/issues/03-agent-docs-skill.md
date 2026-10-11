# 03: Ship agent-md plus llms-txt plus deadmon skill

**What to build:** an agent builder drives deadmon from Claude, Cursor
or Codex with one fetch: agent.md is a one-line copy-prompt, llms.txt
is a one-fetch doc, skills/deadmon/SKILL.md copies into .claude/skills.
Preflight plus --json commands plus error codes state the fail-closed
contract upfront.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] agent.md one-line copy-prompt present
- [ ] llms.txt one-fetch doc present
- [ ] skills/deadmon/SKILL.md copyable into .claude/skills
- [ ] Preflight, --json commands, error codes documented
- [ ] Fail-closed contract stated: unverified when deadline unproven
