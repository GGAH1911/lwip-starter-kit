---
sources: [raw/sources/omegawiki.md]
created: 2026-05-27
updated: 2026-05-27
---

# OmegaWiki (ΩmegaWiki)

A full academic-research lifecycle platform powered by Claude Code, by PKU DAIR
Lab (8-person team). The most *built-out* instantiation of [[llm-as-compiler]]
— and the most domain-locked.

## Shape

- 26 slash commands: /init, /ingest, /discover, /ideate, /exp-design, /exp-run,
  /paper-draft, /paper-compile, /survey, /rebuttal, /poster, /daily-arxiv, ...
- 9 fixed entity types: Paper, Concept, Topic, Person, Idea, Experiment,
  Method, Summary, Foundation.
- Graph split: `graph/edges.jsonl` (semantic) + `graph/citations.jsonl`
  (bibliographic). Obsidian wikilinks + custom web UI.

## Stack

Claude Code specific (`.claude/skills/`, CLAUDE.md as runtime schema; supports
Anthropic-compatible third-party APIs). Python tools, GitHub Actions cron, MCP
cross-model review. Bilingual EN / 中文.

## Where it sits

A **vertical platform**, not a protocol — the opposite end of the spectrum from
LWIP's minimal, domain-agnostic rule set. Several of its structural ideas were
borrowed into LWIP v1.6 (terminal foundations, first-class gaps,
anti-repetition memory, an edges.jsonl cache) without adopting the schema lock
or command surface. Its fine-grained typed edges (10+ workflow/semantic
relations) go further than LWIP's six types.
