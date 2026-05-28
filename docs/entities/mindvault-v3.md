---
sources: [raw/sources/mindvault-v3.md]
created: 2026-05-27
updated: 2026-05-27
---

# MindVault v3

A persistent-memory system for Claude Code (single author, etinpres). An
automatic implementation of [[llm-as-compiler]]: a local model distills each
session into memory without the user writing anything down.

## Shape

4-layer pipeline:
1. SessionStart — recent sessions summarized + injected.
2. `/recall` — hybrid FTS5 + Arctic-ko embedding + Gemma rerank.
3. Memory Compiler — SessionEnd → Gemma distills → staged → `/memory_review`.
4. UserPromptSubmit hook — per-message hybrid search + injection.

## Stack

Local Gemma 4 E4B (~3GB) + Arctic-ko embedding (MLX 4bit). macOS Apple Silicon
only. Storage in SQLite (FTS5 + vectors); memory pool user-global by default.

## Where it sits

It is the **dynamic-retrieval** pole of
[[static-priming-vs-dynamic-retrieval]]. Its automatic capture is the thing
LWIP deliberately does *not* do — which is a strength for un-disciplined,
high-volume, single-domain use, and a liability (cross-project noise, token
cost, platform lock-in) otherwise.

## Measured

392 tests pass; false-positive 0%; hit rate 83.0% (n=6,781); latency p50 40ms.
Echo-chamber guards: self-affirming memory detection, false-positive tracking.
