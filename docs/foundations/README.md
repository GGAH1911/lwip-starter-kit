# Foundations (Tier 2 — Terminal Background)

Settled background knowledge. Nodes here **receive** inbound semantic links
from the rest of the mesh but typically **do not link out** to other nodes.
They are conceptual endpoints — once the agent reaches a foundation page, no
further traversal is needed.

## When to use this folder

- A concept that the project assumes as a given (e.g. a math identity, a
  framework's vocabulary, a domain primitive) and isn't going to evolve.
- Pages that exist purely to be referenced — they don't argue, derive, or
  synthesize. They define.

## When NOT to use this folder

- If the page is itself a synthesis or builds on something, it belongs in
  `docs/concepts/` (or wherever the project organises actual mesh nodes), not
  here.
- If the page raises questions, it belongs in `docs/gaps/`.

## Rules

- Same Zero-Entropy rules as the rest of the mesh: must be linked from a hub
  (0-Gap), must have a *meaningful* inbound link (0-Isolation), must carry
  `sources:` frontmatter (100%-Lineage).
- No 0-Congestion rule applies (foundations aren't hubs).
- Convention: foundation pages link out as little as possible. If you find
  yourself adding many outbound links from a foundation page, it probably
  isn't a foundation — promote it to a regular Tier 2 node.

## Why this exists

Borrowed from OmegaWiki's `foundations/`. Marking some nodes as "terminal"
gives the agent a useful signal: *"don't traverse deeper here, this is
settled."* It prevents endless graph walks during synthesis and keeps the
mesh's deep core stable as the leading edge churns.

This folder is exempt from no rules — it's a convention, not a tier
exemption. Audit treats it the same as any other Tier 2 subfolder.
