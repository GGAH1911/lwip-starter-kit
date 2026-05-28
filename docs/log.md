# 📝 Operation Log

> Append-only. Every Ingest, Merge, Prune, and Lint operation is recorded here.
> Format: `## [YYYY-MM-DD] operation | Subject`

This file is the chronological backbone of the wiki. Even when pages are deleted (Pruned), the fact that they existed and why they were removed is preserved here. The Agent appends entries; the Human reads them to understand the wiki's evolution.

---

<!-- Entries below this line. Do not edit above. -->

## [2026-05-27] ingest | LLM knowledge-systems comparison — 6 pages created, 0 updated. First real ingest. Tier 1: raw/sources/{karpathy-llm-wiki,mindvault-v3,omegawiki}.md. Tier 2: hub knowledge-systems + concepts/{llm-as-compiler, static-priming-vs-dynamic-retrieval} + entities/{mindvault-v3, omegawiki} + foundation karpathy-llm-wiki + gap gap-grep-scale-ceiling. Typed links: depends/core×3/supports×2 from hub. 22 edges cached. Source = the multi-session LWIP vs MindVault v3 vs OmegaWiki analysis.

## [2026-05-27] fix | edges.jsonl missed hub edges — extract_all_edges() reused EXCLUDE_TOP (which excludes hubs/ from is_node), so the auditor skipped hubs entirely and every edge came out 'navigational'. Surfaced by the first real ingest. Split out EXCLUDE_EDGES_TOP ({00_inbox, .lwip, handoffs, archive}) so hubs are scanned for edges while still being exempt as nodes. Meaningful hub edges now captured (6/22).

## [2026-05-27] test | Auditor test suite — tests/test_lwip_audit.py (stdlib unittest, 11 tests): is_node classification, isolation/weak-isolation, missing/broken lineage, congestion, flat-dir, inbox backlog, hub-edge extraction (regression guard), pipe-annotated edge type, node→node links NOT clearing isolation, addresses_gap edge capture. First run caught two real inconsistencies: (1) gaps/README overstated that addresses_gap auto-clears 0-Isolation via a non-hub resolver (corrected — isolation is always "from a hub"); (2) lwip-audit.py DEFAULTS.meaningful_link_types was out of sync with lwip.config.yaml (missing addresses_gap → auditor misbehaved without the config file present). Both fixed. README gains a Tests section.
