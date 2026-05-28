# Source clip — Karpathy "LLM-Wiki" idea

Origin: Andrej Karpathy, LLM-Wiki gist
(https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

Captured: 2026-05-27. This is a paraphrased clip of the originating idea, kept
as Tier 1 immutable input. Do not edit — it is the ground truth for the
foundation node derived from it.

## The idea (paraphrase)

Instead of re-feeding all raw documents to an LLM on every query (RAG), use the
LLM once — like a compiler — to distill scattered sources into a persistent,
structured wiki. After that, you query the refined wiki, not the raw corpus.
Knowledge is compiled once and maintained, rather than rediscovered on every
question.

Key metaphors:
- LLM as the librarian / compiler
- The wiki as the codebase of knowledge
- Obsidian as the IDE for the wiki

## Consequence

Knowledge compounds: each new source enriches the whole graph rather than
sitting as an isolated chunk. The cost is paid once at compile time, not on
every retrieval.
