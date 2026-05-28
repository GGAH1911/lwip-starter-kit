---
status: open
raised: 2026-05-27
sources: [raw/sources/mindvault-v3.md]
resolved_by: null
created: 2026-05-27
updated: 2026-05-27
---

# Gap: where does grep + wikilinks stop scaling?

## Why it matters

LWIP serves compiled knowledge by static priming + grep, not embedding
retrieval (see [[static-priming-vs-dynamic-retrieval]]). That choice is
correct at small scale and clearly wrong at very large scale — but the
crossover point is asserted, not measured. Knowing it would tell a user *when*
to consider a [[mindvault-v3]]-style retrieval layer instead of staying pure
LWIP.

## What we know so far

- At ~27 pages + ~100 log entries (the cta-law exemplar), grep is effectively
  instant and priming holds the relevant context.
- Asserted boundary: "breaks past ~thousands of nodes." This number is a
  guess, not an experiment.
- MindVault's rationale implies the boundary is wherever the relevant subset
  no longer fits the prompt prefix economically.

## What we'd need to close it

- A benchmark: synthetic meshes at 10² / 10³ / 10⁴ nodes, measuring (a) grep
  latency, (b) tokens needed to prime "enough" context, (c) retrieval quality
  vs. an embedding baseline.
- A definition of "enough context" — recall@k against a question set.

## Discussion

Open. First noted while contrasting LWIP's priming model with MindVault's
per-message retrieval. Resolution would likely become a `concepts/` node on
mesh-scaling thresholds, linked back here with `addresses_gap`.
