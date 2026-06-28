# LWIP — Design Rationale (v1.6)

> **LLM-Wiki Implementation Protocol.** This document explains *why* LWIP is
> built the way it is. For the other three angles:
> - **How do I use it** → `README.md`
> - **What are the rules** → `agent.md`
> - **What do I do each session** → `lifecycle.md`
>
> This file is the only one that argues for the design choices rather than
> stating them. If you just want to run LWIP, you don't need to read this.

---

## 1. What LWIP is — and isn't

LWIP is a **protocol** for an LLM agent to build and maintain a Markdown
knowledge base whose structure stays coherent across sessions. It is a set of
rules plus a small deterministic checker. It is not:

- **Not a platform.** No slash commands, no fixed domain schema, no services.
  It does not know or care whether you are tracking tax law, research papers,
  or game design.
- **Not RAG.** It does not chunk-and-retrieve raw documents per query. The
  agent reads named files and greps; the human navigates hubs (and, if they
  like, an Obsidian graph view).
- **Not an embedding memory.** There are no vectors, no similarity search, no
  model dependency. The "graph" is discrete, typed wikilinks the agent and
  human draw by hand.

The thing LWIP produces is a directory of Markdown files with YAML
frontmatter and `[[wikilinks]]`. That artifact outlives any specific LLM,
tool, or vendor.

## 2. Design principles

These are the load-bearing decisions. Each one is a deliberate trade-off.

### 2.1 Markdown is the single source of truth
Every durable fact lives in a plain `.md` file. Derived artifacts (the
auditor's `state.json`, the `edges.jsonl` cache) are gitignored and
regenerated — they can always be thrown away and rebuilt from the markdown.
Reason: plain text is readable in ten years, diffable in git, editable by any
tool, and renders natively in Obsidian. Nothing is locked in a database whose
schema or model version can rot.

### 2.2 LLM-agnostic entry point
The agent boots by reading `agent.md`, not a tool-specific file like
`CLAUDE.md`. Reason: `CLAUDE.md`, `GEMINI.md`, `.cursorrules` etc. are each
one vendor's convention. Binding the protocol to one of them would couple the
kit to that vendor. A project that happens to use a specific tool may add a
thin adapter pointing to `agent.md` — but that is a downstream choice, not
part of the kit.

### 2.3 Measurement is deterministic; judgment is the LLM's
Counting links, finding orphans, validating frontmatter, computing churn —
these are mechanical. They live in `tools/lwip-audit.py`, a stdlib-only script
that runs the same way every time, for free, with no LLM call. Deciding what a
node *means*, how to split a hub, whether two pages should merge — that is
semantic work only the LLM can do. Earlier versions had the LLM write
throwaway audit scripts on every shutdown; v1.3 moved measurement into the
version-controlled auditor and kept only judgment as the LLM's job. Reason:
measurement should be repeatable and cost nothing; spending tokens to
re-derive an orphan count every session is waste.

### 2.4 Static priming, not per-message retrieval
At session start the agent reads the index, the recent log, the latest
handoff, and the relevant hubs — once. It does not re-inject memory on every
message. Reason: at the scale LWIP targets (tens to low-thousands of nodes),
the whole relevant context fits in the prompt prefix and stays prompt-cached
across turns, which is far cheaper than retrieving and injecting fresh context
each message. Dynamic per-message retrieval only earns its token cost when the
memory store grows past what priming can hold — see §6.

### 2.5 Grooming is trigger-gated
A full heal pass does not run every session. The auditor decides whether one
is warranted based on open alerts and git churn (changed lines, file velocity,
commits since last groom). Reason: in a fast dev loop most sessions change
little; forcing a full audit on a quiet session burns tokens for no structural
gain. The cheap deterministic scan still runs; only the expensive LLM
restructuring is gated.

### 2.6 Index topology follows the primary reader
The mesh has two kinds of reader, and they want different index shapes.

- **Humans and query-consumers** browse by *topic*. A person opens a hub, an
  Obsidian graph, or a backlink panel; a downstream app may read pages through
  a content-collection query. For them the natural index is the **semantic
  hub** (`docs/hubs/`): curated entry points grouped by subject, not by
  filesystem location. This is LWIP's default.
- **An LLM that reconstructs the whole graph at boot** reads by *traversal*. It
  starts at the index and follows pointers until the full map sits in the
  prompt prefix. For that reader the strongest shape is a **per-directory
  index**: one index file in every folder that registers exactly that folder's
  files, with each index linking its parent. The set of indexes then mirrors
  the filesystem one-to-one, so following the pointers from the root is
  *guaranteed* to reach every node — there is no file that some topic hub
  happened not to curate.

Both shapes satisfy 0-Gap ("every file is registered somewhere"); they differ
in *what* "somewhere" is, and therefore in what the registration guarantees.
Topic hubs guarantee *semantic* placement and read well for a browsing human;
per-directory indexes guarantee *spanning* coverage and read well for an LLM
doing a deterministic full sweep. The trade-off is real both ways: a
per-directory index is more index files to keep in step with the tree and does
not group by meaning, while topic hubs leave completeness dependent on the
agent remembering to curate every node into some hub.

The reference implementation of the per-directory shape is **TME (The Master
Engine)**, which places a `00_<DIR>.md` index in every folder and gates session
shutdown on completeness — non-zero drift blocks the session from ending, so
the spanning tree can never silently develop a hole. LWIP keeps the hub shape
as its default because it targets a *human-browsable* knowledge base (§6); a
project whose primary reader is an LLM doing full-graph priming should set
`index_topology: directory` (`lwip.config.yaml`) and treat each folder's index
as the registration target for 0-Gap.

## 3. The tier model

Assets are separated by who owns them and what rules apply.

| Tier | Location | Owner | Rules |
| :--- | :--- | :--- | :--- |
| **0 — Inbox** | `docs/00_inbox/` | human | size/age caps only |
| **1 — Immutable inputs** | `raw/` (or any path) | human | read-only for the agent |
| **2 — Mesh** | `docs/` (minus 0 and 2.5) | agent | full Zero-Entropy rules |
| **2.5 — Session continuity** | `docs/handoffs/` | agent | own schema; exempt from mesh rules |
| **3 — Governance** | `agent.md`, `lifecycle.md`, `lwip.config.yaml`, this file | both, by proposal | n/a |

Why each non-obvious tier exists:

- **Tier 0 (Inbox)** buys *frictionless capture*. A half-formed idea or pasted
  error log shouldn't have to satisfy linking and lineage rules just to be
  written down. The inbox is exempt — but bounded by size/age caps so it can't
  rot into a junk drawer. The agent drains it via the triage loop.
- **Tier 2.5 (Handoffs)** buys *working memory across sessions*. The operation
  log records *what* changed; a handoff records *why*, what's unresolved, and
  where to start next. Without it, each session re-derives context from
  artifacts alone. Handoffs reference mesh nodes but aren't mesh nodes, so they
  are exempt from the mesh rules.

Two Tier-2 *conventions* (not separate tiers, same rules) shape the mesh:

- **`docs/foundations/`** — terminal background nodes. They receive inbound
  links but mostly don't link out (settled definitions). The signal to the
  agent: "don't traverse deeper here."
- **`docs/gaps/`** — first-class open questions, each its own node with a
  `status` lifecycle. Distinct from a handoff's session-bound "Open questions":
  a gap persists across sessions until explicitly resolved or abandoned, giving
  the project a visible list of what it does *not* know.

## 4. The Zero-Entropy rules, and why each exists

These four metrics apply to the Tier 2 mesh. The auditor reports a violation
when any is broken. Thresholds live in `lwip.config.yaml`.

- **0-Gap** — every mesh file is registered in a hub. *Why:* a file no hub
  points to is invisible to navigation; it exists physically but not
  semantically.
- **0-Isolation** — every node has at least one *meaningful* inbound link
  (`core` / `derives` / `supports` / `depends` / `contradicts` /
  `addresses_gap`). *Why:* a node nothing meaningfully links to has no place in
  the argument structure. v1.4 made this type-aware specifically to close a
  Goodhart loophole — under the old rule, a single throwaway `see-also` could
  silence the orphan alert without actually anchoring the node. Navigational
  links still keep the graph browsable, but a node held only by them is
  reported as `weak-isolation`, not cleared.
- **0-Congestion** — no hub exceeds its outbound-link cap. *Why:* a hub with a
  hundred links is a junk drawer again. Past the cap, the agent performs
  Semantic Fission — splitting it into sub-hubs — so the topology stays
  navigable.
- **100%-Lineage** — every node carries a `sources:` frontmatter field, and
  every listed path resolves. *Why:* an untraceable claim is indistinguishable
  from a hallucination. Lineage lets any assertion be walked back to the raw
  input that justified it; merges must preserve conflicting claims with their
  origins rather than silently picking a winner.

The point of expressing these as *quantitative, machine-checked* rules is that
"is the knowledge base healthy?" becomes a number the auditor reports, not a
vibe the agent has to assess.

## 5. Anti-repetition: failed paths are signal

The Prune Protocol distinguishes two reasons for removing a page:

- **Stale** — out of date, superseded; nothing was wrong with it. Archive
  quietly.
- **Failed** — an approach or hypothesis that was tried and didn't work.

A failed attempt is not deleted into silence. It is archived *with* a
`contradicts` edge from the relevant hub carrying a one-line summary of why it
failed. *Why:* a dead end is information. Burying it loses the warning, and the
next session re-explores the same path. Keeping it as an explicit semantic edge
turns "we already tried this" into something the agent can find.

## 6. Scope — when LWIP fits, and when it doesn't

LWIP is a good fit when:

- The corpus is curated and human-meaningful (tens to low-thousands of nodes).
- You want to *browse* the knowledge (Obsidian graph, backlinks) — humans are a
  first-class audience, not just the LLM.
- The knowledge has long-term value beyond any one tool or session.
- You work across heterogeneous projects and want each kept cleanly separate.
- Multiple different LLMs may touch the same base.

LWIP is the wrong tool when:

- You want automatic capture of things you *didn't* write down — LWIP relies on
  the agent actively maintaining the mesh; it has no background extractor.
- The store grows past what static priming can hold (many thousands of
  entries), at which point embedding-based retrieval becomes necessary.
- You need conceptual-similarity search across synonyms — grep matches strings,
  not meanings. (In LWIP, a missed connection is a signal to *draw the edge*,
  not to add a vector index.)

Being explicit about the second list is the point: LWIP does a narrow thing
well rather than claiming to be a universal memory system.

## 7. Heritage

LWIP descends from Andrej Karpathy's "LLM-Wiki" idea: have the LLM compile
scattered sources into a persistent, structured wiki once, then query the
refined result — instead of re-feeding raw documents to the model on every
question. LWIP's additions are the quantitative rules, the deterministic
auditor, the tier model (inbox, handoffs, foundations, gaps), and the
trigger-gated grooming loop — the machinery that lets the idea survive a real
working cadence without either rotting or burning tokens.

## 8. Where everything lives

| Concern | File |
| :--- | :--- |
| Quickstart, setup, file inventory | `README.md` |
| Agent role + the four rules + link types | `agent.md` |
| Boot / Ingest / Triage / Prune / Shutdown procedures | `lifecycle.md` |
| Tunable thresholds | `lwip.config.yaml` |
| Deterministic measurement | `tools/lwip-audit.py` |
| Per-folder semantics | `docs/*/README.md` |
| Design reasoning (this document) | `LWIP_Specification.md` |
