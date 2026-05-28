# Source clip — MindVault v3

Origin: https://github.com/etinpres/mindvault-v3 (README, v3.2.5)
Captured: 2026-05-27. Tier 1 immutable input. Paraphrased key facts.

## What it is

A persistent-memory system for Claude Code. Fills the per-session amnesia of
Claude Code with a 4-layer pipeline. Built by a single author (etinpres).
Explicitly cites Karpathy's LLM-as-Compiler pattern.

## Architecture (4 layers)

- L1 — SessionStart auto-injection: recent 5 sessions summarized by local Gemma,
  injected into new session. Cache hit ~50ms.
- L2 — `/recall` natural-language search: JSONL FTS5 + Gemma rerank for sessions;
  Arctic-ko embedding + FTS5 hybrid RRF for memory.
- L3 — Memory Compiler: SessionEnd → Gemma distills → `memory/_procedural/_staged/`
  → `/memory_review` approval → permanent memory.
- L4 — UserPromptSubmit hook: every message runs hybrid search, injects relevant
  memory via system-reminder. raw cosine gate (default 0.32) + query intent
  classifier block chatter (false positive 0%).

## Stack / constraints

- Local Gemma 4 E4B (~3GB) + Arctic-ko embedding (MLX 4bit, ~322MB).
- macOS Apple Silicon only (MLX + launchd). Intel/Linux/Windows unsupported.
- Zero API cost (local inference), no external data transfer.
- Storage: SQLite (FTS5 + vectors) at ~/.claude/mindvault-v3/index.db, plus
  ~/.claude/memory/*.md. Memory pool is user-global by default.

## Measured (v3.2.x)

- 392 passed + 13 subtests. false positive 0.0%.
- hit rate cumulative 83.0% (n=6,781). Latency p50=40ms, p95=400ms, p99=471ms.

## Self-correction

Echo-chamber guards: self-affirming memory detection, false-positive measurement
(negative cue tracking), type-gate stricter cosine for procedural memory.
