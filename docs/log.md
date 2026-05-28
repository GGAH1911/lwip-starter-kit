# 📝 Operation Log

> Append-only. Every Ingest, Merge, Prune, and Lint operation is recorded here.
> Format: `## [YYYY-MM-DD] operation | Subject`

This file is the chronological backbone of the wiki. Even when pages are deleted (Pruned), the fact that they existed and why they were removed is preserved here. The Agent appends entries; the Human reads them to understand the wiki's evolution.

---

<!-- Entries below this line. Do not edit above. -->

## [2026-05-27] ingest | LLM knowledge-systems comparison — 6 pages created, 0 updated. First real ingest. Tier 1: raw/sources/{karpathy-llm-wiki,mindvault-v3,omegawiki}.md. Tier 2: hub knowledge-systems + concepts/{llm-as-compiler, static-priming-vs-dynamic-retrieval} + entities/{mindvault-v3, omegawiki} + foundation karpathy-llm-wiki + gap gap-grep-scale-ceiling. Typed links: depends/core×3/supports×2 from hub. 22 edges cached. Source = the multi-session LWIP vs MindVault v3 vs OmegaWiki analysis.

## [2026-05-27] fix | edges.jsonl missed hub edges — extract_all_edges() reused EXCLUDE_TOP (which excludes hubs/ from is_node), so the auditor skipped hubs entirely and every edge came out 'navigational'. Surfaced by the first real ingest. Split out EXCLUDE_EDGES_TOP ({00_inbox, .lwip, handoffs, archive}) so hubs are scanned for edges while still being exempt as nodes. Meaningful hub edges now captured (6/22).
