---
status: resolved
raised: 2026-05-27
sources: [raw/sources/mindvault-v3.md]
resolved_by: docs/concepts/mesh-scaling-thresholds.md
created: 2026-05-27
updated: 2026-05-27
---

> **Resolved 2026-05-27** by [[mesh-scaling-thresholds]] — benchmarked with
> `tools/bench_mesh_scale.py`. Answer: the ceiling is *priming tokens*
> (~13.8/node), not grep latency (sub-200 ms at 10k nodes). Priming all hubs at
> a ~20k-token budget caps out near ~1,450 nodes; selective priming pushes that
> out 5–20× before embedding retrieval is warranted. This page is kept as the
> historical record of the question.

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
