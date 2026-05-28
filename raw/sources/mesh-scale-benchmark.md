# Source clip — mesh-scaling benchmark run

Origin: `tools/bench_mesh_scale.py`, run 2026-05-27 on the author's machine.
Tier 1 immutable measurement record. Synthetic meshes, 15 nodes/hub,
~300 chars/node, 4 chars/token, grep = best of 3 runs.

## Raw output

```
     nodes   hubs   grep ms   prime tokens
  -------- ------ --------- --------------
       100      7      4.9          1,357
      1000     67     18.0         13,732
     10000    667    159.7        139,873
```

## Derived

- prime tokens / nodes: 13.57 (n=100), 13.73 (n=1000), 13.99 (n=10000)
  → ~13.8 prime-tokens per node, strongly linear (index + all hubs).
- grep latency stays sub-200 ms even at 10k nodes (≈16 µs/node, linear).

## Priming-budget → node ceiling (at 13.8 tokens/node, priming all hubs)

| priming budget | node ceiling |
| ---: | ---: |
| 10k tokens | ~725 |
| 20k tokens | ~1,450 |
| 50k tokens | ~3,600 |

Notes / caveats:
- Numbers are hardware- and corpus-dependent; re-run `bench_mesh_scale.py`
  on the target machine. The *shape* (linear prime cost, cheap grep) is the
  durable result, not the exact constants.
- Synthetic nodes are uniform; a real mesh has uneven hub sizes and richer
  pages, so prime tokens per node will vary.
