# Source clip — OmegaWiki (ΩmegaWiki)

Origin: https://github.com/skyllwt/OmegaWiki (README)
Captured: 2026-05-27. Tier 1 immutable input. Paraphrased key facts.

## What it is

"Karpathy's LLM-Wiki vision, fully realized" — a full academic-research
lifecycle platform powered by Claude Code. Built by PKU DAIR Lab (8-person
team). Vertically specialized for research: paper ingestion → knowledge graph →
gap detection → idea generation → experiment design → paper writing → rebuttal.

## Surface

- 26 slash commands across Phase 0 (setup) → Phase 3 (writing & submission):
  /init, /ingest, /discover, /ideate, /exp-design, /exp-run, /paper-draft,
  /paper-compile, /survey, /rebuttal, /poster, /daily-arxiv, etc.
- 9 fixed entity types: Paper, Concept, Topic, Person, Idea, Experiment, Method,
  Summary, Foundation.
- Knowledge graph in graph/edges.jsonl (semantic) + graph/citations.jsonl
  (bibliographic), separated.
- Obsidian [[wikilink]] format; also a custom web UI graph view at
  localhost:8765.

## Stack

- Claude Code specific (.claude/skills/, CLAUDE.md as runtime schema). Supports
  Anthropic-compatible third-party APIs (DeepSeek, Kimi, MiMo, etc.).
- Python tools (research_wiki.py, lint.py, fetch_*.py, remote.py), GitHub
  Actions for daily-arxiv cron, MCP server for cross-model review.
- Bilingual EN / 中文.

## Notable ideas

- foundations/ = terminal background nodes (receive inward links, write none).
- Knowledge gaps tracked explicitly inside Topic nodes (known + methodological).
- Failed experiments kept as first-class anti-repetition memory.
- Fine-grained typed edges: same_problem_as, similar_method_to, builds_on,
  challenges (paper-paper); introduces/uses/extends/critiques_concept
  (paper-concept); supports, contradicts, tested_by, invalidates, addresses_gap,
  inspired_by, derived_from (workflow).
