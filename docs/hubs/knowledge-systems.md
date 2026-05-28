---
sources: [raw/sources/karpathy-llm-wiki.md, raw/sources/mindvault-v3.md, raw/sources/omegawiki.md]
created: 2026-05-27
updated: 2026-05-27
---

# Hub: LLM Knowledge Systems

The design space of LLM-driven persistent knowledge — the originating idea, the
core mechanism, the axis that separates implementations, the systems that
embody them, and the open questions.

## Foundations

| Node | Role | Description |
| :--- | :--- | :--- |
| [[karpathy-llm-wiki]] | depends | the originating premise the whole space rests on |

## Concepts

| Node | Role | Description |
| :--- | :--- | :--- |
| [[llm-as-compiler]] | core | compile-once-then-read mechanism behind the premise |
| [[static-priming-vs-dynamic-retrieval]] | core | the axis separating LWIP from embedding-memory systems |

## Entities

| Node | Role | Description |
| :--- | :--- | :--- |
| [[mindvault-v3]] | supports | dynamic-retrieval implementation (Claude Code memory infra) |
| [[omegawiki]] | supports | vertical-platform implementation (academic research) |

## Open Gaps

| Node | Role | Description |
| :--- | :--- | :--- |
| [[gap-grep-scale-ceiling]] | core | unmeasured crossover where grep+priming stops scaling |

## Navigation

- Operation log: [log.md](../log.md)
- Index: [index.md](../index.md)
