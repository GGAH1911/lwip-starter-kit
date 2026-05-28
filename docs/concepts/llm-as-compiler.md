---
sources: [raw/sources/karpathy-llm-wiki.md]
created: 2026-05-27
updated: 2026-05-27
---

# LLM-as-Compiler

The mechanism that turns the [[karpathy-llm-wiki]] premise into something
operable: treat the LLM as a *compile step* that runs once per source, not a
runtime interpreter that re-reads everything per query.

## RAG vs LLM-as-Compiler

| | RAG | LLM-as-Compiler |
| :--- | :--- | :--- |
| When the LLM works | every query | once, at ingest |
| What it stores | raw chunks | distilled, structured nodes |
| Cost profile | recurring (same cost each query) | paid once, then cheap reads |
| Noise | re-encountered every query | filtered out at compile time |

## How the three systems instantiate it

- **LWIP** (this kit) compiles by hand — the LLM writes structured markdown
  nodes under a rule set; the human curates. See [[static-priming-vs-dynamic-retrieval]]
  for how the compiled result is then served back.
- **MindVault v3** ([[mindvault-v3]]) compiles automatically — a local model
  distills each session at SessionEnd into staged memory.
- **OmegaWiki** ([[omegawiki]]) compiles via 26 explicit commands for one
  vertical (academic research).

All three pay the compile cost once and read the refined result thereafter —
the defining move of this pattern.
