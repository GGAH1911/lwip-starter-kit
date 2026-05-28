---
sources: [raw/sources/mindvault-v3.md, raw/sources/karpathy-llm-wiki.md]
created: 2026-05-27
updated: 2026-05-27
---

# Static Priming vs Dynamic Retrieval

The axis that most sharply separates LWIP from [[mindvault-v3]] once both have
compiled knowledge (see [[llm-as-compiler]]). It's about *how the compiled
result is served back* into a session.

## The two modes

- **Static priming** (LWIP): at session start the agent reads the index, recent
  log, latest handoff, and relevant hubs — once. Context sits in the prompt
  prefix and stays prompt-cached across turns. No per-message injection.
- **Dynamic retrieval** (MindVault v3): every user message triggers a hybrid
  search and injects relevant memory via a hook.

## Trade-off

| | Static priming | Dynamic retrieval |
| :--- | :--- | :--- |
| Token cost | ~once per session, cache-friendly | per-message, cache-breaking |
| Est. cost (50-turn session) | ~$0.03 | ~$0.10–0.16 |
| Scales to | tens–low thousands of nodes | tens of thousands |
| Synonym matching | no (grep is literal) | yes (embeddings) |

## The crossover

Static priming wins while the relevant context fits the prefix. Dynamic
retrieval only earns its per-message cost once the store grows past what
priming can hold — the open question of *where exactly* that boundary sits is
tracked in [[gap-grep-scale-ceiling]].
