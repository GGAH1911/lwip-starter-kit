---
sources: [raw/sources/karpathy-llm-wiki.md]
created: 2026-05-27
updated: 2026-05-27
---

# Foundation: Karpathy's LLM-Wiki

The originating idea behind this whole design space. Treated as a **terminal
background node**: everything here links *in* to it; it does not argue or
synthesize further.

## The claim

Don't re-feed raw documents to an LLM on every query (the RAG pattern). Use the
LLM **once, like a compiler**, to distill scattered sources into a persistent,
structured wiki. Then query the refined wiki — not the raw corpus.

- LLM = librarian / compiler
- Wiki = the codebase of knowledge
- Obsidian = the IDE for the wiki

## Why it's a foundation, not a concept page

This is settled ground that the rest of the mesh builds on. It states the
premise; the actual mechanism (how to compile, how to keep the result healthy)
is developed in the `llm-as-compiler` concept and the systems that implement
it. No outbound links by design — traversal stops here.
