# A proposal is a patch against an allowlist, never executed code

The Scout reads untrusted HTML off the public internet and writes to its own codebase. A proposal is generated from a page's content (ADR-0014), which means scraped page text can influence the code that runs. ADR-0016 restricts a proposal to its own adapter's files, but that still permits deleting the verification stage, corrupting extraction logic, or writing arbitrary code. An agent that executes model output influenced by adversarial page content is the one thing in this project that could genuinely harm something.

Settled: a proposal is a **diff against an allowlist of adapter files**, applied as a patch. It may change selectors and extraction rules only. Anything requiring new logic is rejected and **escalated**.

## Considered Options

- **Trust scope confinement to ADR-0016's per-adapter boundary.** Rejected: confinement limits *where*, not *what*. Code confined to one adapter's directory can still corrupt everything that adapter feeds.
- **Execute the proposal in a container for real, then commit.** Rejected: sandboxing limits blast radius to the sandbox, but the *committed* code is what runs unscoped for the following weeks. It also costs real money and time for a property an allowlist gives for free.
- **Require human approval for every proposal.** Rejected: defeats the demo's central claim — the agent heals itself while you watch. The distinguishing property is that healing is *bounded*, not that it is *supervised*.

## Consequences

- The allowlist is expressed as "selector and extraction-rule declarations," not "any text in these files." Arbitrary code in an adapter is unreachable by a proposal.
- A proposal needing new logic escalates with its diff attached — the operator can widen the allowlist deliberately, which is an auditable act rather than a silent escalation of agent capability.
- This is the property that makes "the agent edits its own code" defensible on stage: the agent can only ever repair *how it reads a page*, never *what it does with what it reads*.
- Slice 4's test must include a deliberately injection-shaped fixture — page text instructing the model to edit unrelated code — asserting the proposal is rejected at the allowlist, not at review.