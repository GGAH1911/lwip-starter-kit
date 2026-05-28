---
health: Optimal
pages: 7
orphans: 0
conflicts: 0
gaps_open: 0
suggested_action: "Ingest the next domain. (gap-grep-scale-ceiling resolved by mesh-scaling-thresholds.)"
last_updated: 2026-05-27
---

# 📚 Knowledge Index

> Health: Optimal | Pages: 7 | Orphans: 0 | Conflicts: 0 | Open gaps: 0
> Suggested action: Ingest the next domain. (`gap-grep-scale-ceiling` resolved.)

This is the master catalog of all knowledge in this wiki. The Agent updates this file on every Ingest, Merge, or Prune operation. The Human reads this file to understand the current state of the knowledge base at a glance.

---

## 🗂️ Categories

### Concepts
| Page | Summary | Sources |
| :--- | :--- | :--- |
| [llm-as-compiler](concepts/llm-as-compiler.md) | Compile-once-then-read mechanism behind the Karpathy premise | raw/sources/karpathy-llm-wiki.md |
| [static-priming-vs-dynamic-retrieval](concepts/static-priming-vs-dynamic-retrieval.md) | The axis separating LWIP from embedding-memory systems | raw/sources/mindvault-v3.md |
| [mesh-scaling-thresholds](concepts/mesh-scaling-thresholds.md) | Measured ceiling of the priming model (~13.8 tokens/node) | raw/sources/mesh-scale-benchmark.md |

### Entities
| Page | Summary | Sources |
| :--- | :--- | :--- |
| [mindvault-v3](entities/mindvault-v3.md) | Claude Code persistent-memory infra (dynamic retrieval) | raw/sources/mindvault-v3.md |
| [omegawiki](entities/omegawiki.md) | Academic-research vertical platform (Claude Code) | raw/sources/omegawiki.md |

### Foundations
| Page | Summary | Sources |
| :--- | :--- | :--- |
| [karpathy-llm-wiki](foundations/karpathy-llm-wiki.md) | The originating LLM-Wiki premise (terminal node) | raw/sources/karpathy-llm-wiki.md |

### Gaps
| Page | Status | Summary |
| :--- | :--- | :--- |
| [gap-grep-scale-ceiling](gaps/gap-grep-scale-ceiling.md) | resolved | Ceiling is priming tokens (~13.8/node), not grep — resolved by mesh-scaling-thresholds |

### Syntheses & Analyses
| Page | Summary | Sources |
| :--- | :--- | :--- |
| *(Promoted from Q&A — see lifecycle.md §Query & Promote)* | | |

---

## 🔗 Navigation
- **Hubs**: [docs/hubs/](hubs/) — [knowledge-systems](hubs/knowledge-systems.md)
- **Operation Log**: [log.md](log.md)
