# 📝 Operation Log

> Append-only. Every Ingest, Merge, Prune, and Lint operation is recorded here.
> Format: `## [YYYY-MM-DD] operation | Subject`

This file is the chronological backbone of the wiki. Even when pages are deleted (Pruned), the fact that they existed and why they were removed is preserved here. The Agent appends entries; the Human reads them to understand the wiki's evolution.

---

<!-- Entries below this line. Do not edit above. -->

## [2026-05-27] ingest | LLM knowledge-systems comparison — 6 pages created, 0 updated. First real ingest. Tier 1: raw/sources/{karpathy-llm-wiki,mindvault-v3,omegawiki}.md. Tier 2: hub knowledge-systems + concepts/{llm-as-compiler, static-priming-vs-dynamic-retrieval} + entities/{mindvault-v3, omegawiki} + foundation karpathy-llm-wiki + gap gap-grep-scale-ceiling. Typed links: depends/core×3/supports×2 from hub. 22 edges cached. Source = the multi-session LWIP vs MindVault v3 vs OmegaWiki analysis.

## [2026-05-27] fix | edges.jsonl missed hub edges — extract_all_edges() reused EXCLUDE_TOP (which excludes hubs/ from is_node), so the auditor skipped hubs entirely and every edge came out 'navigational'. Surfaced by the first real ingest. Split out EXCLUDE_EDGES_TOP ({00_inbox, .lwip, handoffs, archive}) so hubs are scanned for edges while still being exempt as nodes. Meaningful hub edges now captured (6/22).

## [2026-05-27] test | Auditor test suite — tests/test_lwip_audit.py (stdlib unittest, 11 tests): is_node classification, isolation/weak-isolation, missing/broken lineage, congestion, flat-dir, inbox backlog, hub-edge extraction (regression guard), pipe-annotated edge type, node→node links NOT clearing isolation, addresses_gap edge capture. First run caught two real inconsistencies: (1) gaps/README overstated that addresses_gap auto-clears 0-Isolation via a non-hub resolver (corrected — isolation is always "from a hub"); (2) lwip-audit.py DEFAULTS.meaningful_link_types was out of sync with lwip.config.yaml (missing addresses_gap → auditor misbehaved without the config file present). Both fixed. README gains a Tests section.

## [2026-05-27] feature | dangling_edge alert (soft) — auditor now flags any wikilink whose target stem matches no .md file in the mesh. Soft (not in hard_alerts): forward-linking to a not-yet-written node is legitimate (Obsidian "unresolved links"). Only wikilinks checked; markdown links ](path) skipped (may point at dirs/anchors/external). Edges now carry a `kind` field (wikilink|mdlink). +4 tests (15 total). README gains an Alert types table; lifecycle.md Shutdown Gate lists it. Motivated by a real `edge-typing-granularity` wikilink typo (quoted, not linked, to avoid self-tripping the new check) made during the first ingest.

## [2026-05-27] fix | edge extraction ignores code spans — strip_code_spans() blanks fenced blocks (``` / ~~~) and inline code before link parsing in collect_hub_links, extract_all_edges, and the congestion count. Prose that documents wikilink syntax (log entries, READMEs, hub-table examples) no longer creates phantom edges or false dangling/congestion alerts. +3 tests (18 total). Found while writing the dangling_edge log entry, which self-tripped the new check.

## [2026-05-27] ci | GitHub Actions — .github/workflows/lwip.yml runs the stdlib test suite + a strict audit (python3 tools/lwip-audit.py --strict) on every push and PR to master. Protects the auditor from silent regression for all users. stdlib-only, no external deps. README gains a status badge + CI note.

## [2026-05-27] resolve | gap-grep-scale-ceiling — benchmarked with new tools/bench_mesh_scale.py (synthetic meshes 100/1k/10k nodes). Finding: ceiling is priming tokens (~13.8/node, linear), NOT grep latency (sub-200ms at 10k). All-hubs priming at a ~20k-token budget caps ~1,450 nodes; selective priming pushes that 5-20x before embedding retrieval is warranted. New concept mesh-scaling-thresholds (sources: raw/sources/mesh-scale-benchmark.md + the script), linked from hub (derives) and back to the gap via addresses_gap. Gap status open→resolved, resolved_by set, page kept as historical record. First end-to-end exercise of the gap lifecycle. 1 page created (7 total), gaps_open 1→0, 36 edges.

## [2026-05-27] publish | Share prep — added MIT LICENSE (Copyright ihwang). README gains a "worked example" callout distinguishing kit scaffolding (keep) from the demonstration mesh + handoffs (clear to start fresh), plus a License section. Repo already public; metadata typo fix (knowlege→knowledge) and v1.6 release tagged via gh.
