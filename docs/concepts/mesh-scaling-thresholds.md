---
sources: [raw/sources/mesh-scale-benchmark.md, tools/bench_mesh_scale.py]
created: 2026-05-27
updated: 2026-05-27
---

# Mesh-Scaling Thresholds

Where the grep + static-priming model of [[static-priming-vs-dynamic-retrieval]]
stops scaling — measured, not asserted. This [[gap-grep-scale-ceiling|addresses_gap]]
with a reproducible benchmark (`tools/bench_mesh_scale.py`).

## Finding: the ceiling is priming tokens, not grep speed

| nodes | hubs | grep | prime tokens |
| ---: | ---: | ---: | ---: |
| 100 | 7 | ~5 ms | 1,357 |
| 1,000 | 67 | 18 ms | 13,732 |
| 10,000 | 667 | 160 ms | 139,873 |

Two clean linear trends:

- **grep latency** stays sub-200 ms even at 10k nodes (~16 µs/node). Lookup is
  *not* the bottleneck at any realistic LWIP scale.
- **prime tokens** grow at **~13.8 tokens/node** (index + all hubs). This is
  the real ceiling: priming the whole hub layer eventually blows the prompt
  budget.

## The crossover (prime-everything model)

| priming budget | node ceiling |
| ---: | ---: |
| 10k tokens | ~725 |
| 20k tokens | ~1,450 |
| 50k tokens | ~3,600 |

So LWIP's earlier hand-wave — "breaks past ~thousands of nodes" — is confirmed
and quantified: if you prime *all* hubs and cap priming at a sane ~20k tokens,
the ceiling is ~1,450 nodes.

## What this means for the LWIP-vs-retrieval choice

The crossover is **not** a hard wall, and embeddings are **not** the first
mitigation. Before reaching for [[mindvault-v3]]-style retrieval:

1. **Selective priming** — read only the hubs relevant to the current task,
   not all of them. The `edges.jsonl` cache + the hub topology make this cheap,
   and it pushes the ceiling out by whatever fraction of hubs a typical task
   touches (often 5–20×).
2. **Hub-of-hubs** — Semantic Fission already splits congested hubs; a second
   tier of index hubs keeps the boot-time read bounded.

Embedding retrieval only clearly wins once even the *relevant-subset* hubs
exceed the priming budget — i.e. tens of thousands of nodes, or a corpus with
no usable locality. For the curated, domain-separated meshes LWIP targets, that
is rarely reached.

## Reproducing

`python3 tools/bench_mesh_scale.py [node_counts...]`. Constants
(`NODES_PER_HUB`, `CHARS_PER_TOKEN`, `NODE_BODY_CHARS`) are at the top of the
script; the *shape* (linear prime cost, cheap grep) is the durable result, not
the exact numbers, which are hardware- and corpus-dependent.
