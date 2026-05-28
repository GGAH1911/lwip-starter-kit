# LWIP Starter Kit

[![LWIP](https://github.com/GGAH1911/lwip-starter-kit/actions/workflows/lwip.yml/badge.svg)](https://github.com/GGAH1911/lwip-starter-kit/actions/workflows/lwip.yml)

**LLM-Wiki Implementation Protocol, v1.6**

A minimal scaffold that lets an LLM agent maintain a project's Markdown knowledge base under a fixed set of structural rules. The agent owns `docs/`; the human drops sources and asks questions; a small Python auditor measures the result so the agent only does heavy work when it's actually needed.

This kit is the protocol files and tooling — not the knowledge base itself. The wiki grows from what you put in.

> **This repo ships with a worked example.** `docs/` is not empty — it contains
> a small demonstration mesh (a comparison of LWIP, MindVault v3, and
> OmegaWiki) so you can see what a populated LWIP knowledge base looks like.
> **To start your own**, copy the *kit* files into your project (or clear the
> example):
>
> - **Kit (keep):** `agent.md`, `lifecycle.md`, `lwip.config.yaml`,
>   `LWIP_Specification.md`, `tools/`, `hooks/`, `.github/`, `tests/`, and the
>   `docs/` skeleton — `docs/index.md`, `docs/log.md`, and every
>   `docs/*/README.md`.
> - **Example (clear to start fresh):** `docs/concepts/`, `docs/entities/`,
>   `docs/foundations/*.md`, `docs/gaps/*.md`, `docs/hubs/*.md`,
>   `docs/handoffs/*.md`, and `raw/sources/`. Reset `docs/index.md` /
>   `docs/log.md` to their template state, then run `python3 tools/lwip-audit.py`.

---

## What's in the kit

```
.
├── agent.md                # Agent role, rules, link types
├── lifecycle.md            # Boot / Ingest / Triage / Shutdown procedures
├── lwip.config.yaml        # Tunable thresholds (link caps, churn triggers, inbox limits)
├── LWIP_Specification.md   # Design rationale — the "why" behind the protocol
├── README.md               # This file
├── tools/
│   └── lwip-audit.py       # Deterministic auditor (stdlib only, no LLM call)
├── hooks/
│   └── pre-commit          # Refreshes audit state on every commit
└── docs/
    ├── index.md            # Page catalog + Health Dashboard
    ├── log.md              # Append-only operation log
    ├── 00_inbox/           # Tier 0: rule-free sandbox for raw capture
    │   └── README.md
    ├── handoffs/           # Tier 2.5: per-session narrative records
    │   └── README.md
    ├── foundations/        # Tier 2 convention: terminal background nodes
    │   └── README.md
    ├── gaps/               # Tier 2 convention: first-class open questions
    │   └── README.md
    ├── hubs/               # Semantic hubs (link tables)
    └── .lwip/              # Auditor state + edges.jsonl cache (gitignored)
```

---

## Setup

The kit ships with the hooks path already wired (`git config core.hooksPath hooks`) and `docs/.lwip/` already in `.gitignore`. If you copy this kit into a different repo, run:

```sh
git config core.hooksPath hooks
echo "docs/.lwip/" >> .gitignore
python3 tools/lwip-audit.py        # seeds docs/.lwip/state.json
```

No dependencies. `lwip-audit.py` uses only the Python 3 standard library.

To make the pre-commit hook block commits on hard alerts (e.g. in CI or a strict personal setup):

```sh
export LWIP_STRICT=1
```

### Tests

The auditor is the load-bearing component, so it has a stdlib-only test suite
(no pip install):

```sh
python3 -m unittest discover -s tests
```

`tests/test_lwip_audit.py` covers node classification, isolation /
weak-isolation, lineage, congestion, flat-dir, inbox backlog, dangling-edge
detection, code-span stripping, and edge extraction — including the hub-edge
case (hubs must be scanned for edges even though they are exempt as nodes).
Run it after any change to `tools/lwip-audit.py`.

GitHub Actions (`.github/workflows/lwip.yml`) runs the suite plus a strict
audit (`--strict`) on every push and PR to `master`, so the auditor can't
silently regress.

### Alert types

| Alert | Hard? | Meaning |
| :--- | :--- | :--- |
| `isolation` | yes | node with no inbound link from any hub |
| `weak_isolation` | yes | node linked from a hub only by navigational links |
| `missing_lineage` | yes | node with no `sources:` frontmatter |
| `broken_lineage` | yes | a `sources:` path doesn't resolve |
| `congestion` | yes | hub over its outbound-link cap |
| `flat_dir` | no | folder over its flat-file cap with no sub-folders |
| `inbox_backlog` | no | Tier 0 inbox over its size/age cap |
| `dangling_edge` | no | a `[[wikilink]]` whose target node doesn't exist |

Hard alerts block under `LWIP_STRICT=1`; soft alerts are reported only.
`dangling_edge` is soft because forward-linking to a not-yet-written node is a
legitimate authoring pattern — but it's worth reviewing, since most are typos.

Default behaviour is non-blocking: the hook refreshes `state.json` and prints whether grooming is recommended, but never fails a commit.

---

## How it runs

### Boot (session start)

The agent reads `docs/.lwip/state.json`, the index, the log tail, **the latest file in `docs/handoffs/`**, the hubs, and the inbox. The handoff carries inherited open questions and the previous session's "start here" pointer. If `grooming_recommended` is `false`, the agent goes straight to whatever the human asked. It does **not** restructure on every session.

### Ingest

New raw input → spoke page in `docs/` with YAML frontmatter (`sources:`, `created:`, `updated:`), entry added to the matching hub table, line appended to `docs/log.md`, index incremented.

### Inbox triage (Tier 0 → Tier 2)

Anything dropped into `docs/00_inbox/` is exempt from the structural rules. When the inbox exceeds `inbox_max_items` files or any item is older than `inbox_max_age_days`, the auditor raises `inbox-backlog` and the agent runs the triage loop: keep / merge / discard, then promote the kept items into proper Tier 2 nodes.

### Shutdown (trigger-gated, with mandatory handoff)

The agent runs `lwip-audit.py` and reads `grooming_recommended`. If false, it skips restructuring. If true (hard alerts open, or one of the churn triggers fired), it runs the heal cycle until `hard_alerts = 0`, then writes the current HEAD to `docs/.lwip/last_groom` to reset the churn counter.

**Both branches end with a session handoff** written to `docs/handoffs/<timestamp>.md` — rationale, decisions, open questions, and a "start here" pointer for the next session. Even a quiet session writes one (a minimal one-liner is fine). The trigger-gating only skips heavy *grooming*, never the handoff.

---

## The four structural rules (Tier 2 only)

The auditor reports a violation when any of these is broken:

| Rule | Check |
| :--- | :--- |
| **0-Gap** | every `.md` under `docs/` (excluding Tier 0, archive, hubs, meta) is linked from a hub |
| **0-Isolation** | every node has at least one inbound link of a *meaningful* type from a hub |
| **0-Congestion** | no hub exceeds `hub_max_outbound_links` (default 20) |
| **100%-Lineage** | every node has `sources:` in its frontmatter, and every listed path resolves |

**Meaningful link types** (v1.6): `core`, `derives`, `supports`, `depends`, `contradicts`, `addresses_gap`. Navigational types (`see-also`, `related`, `nav`, `index`) keep the graph browsable but do not, on their own, clear an `isolation` alert — a node linked only by navigational pointers is reported as `weak-isolation`. `addresses_gap` is the edge from any node back to a `docs/gaps/` entry it resolves.

Tier 0 (the inbox) is exempt from all four. It has its own bounded hygiene rule via `inbox_max_items` and `inbox_max_age_days`.

---

## Grooming triggers

A heavy LLM grooming pass is recommended when any of these fire (configurable in `lwip.config.yaml`):

- `hard_alerts > 0` — at least one structural rule is broken
- `diff_lines >= trigger_diff_lines` since last groom (default 200)
- `max_file_velocity >= trigger_file_velocity` — a single file edited that many times (default 5)
- `commits_since_groom >= trigger_commits_since_groom` (default 10)

`last_groom` is just a git ref stored at `docs/.lwip/last_groom`. It's updated when the agent finishes a heal cycle.

---

## Configuration

All thresholds live in `lwip.config.yaml` as flat `key: value` pairs (parsed without a YAML library). The defaults are reasonable for a small wiki; tune them as the project grows. See `agent.md` Chapter 7 and `lifecycle.md` for the schema co-evolution protocol.

---

## Tier model

| Tier | Location | Who writes | Rules apply |
| :--- | :--- | :--- | :--- |
| 0 — Inbox | `docs/00_inbox/` | human (free-form) | size/age caps only |
| 1 — Immutable inputs | `raw/`, or any path the human chooses | human | read-only for agent |
| 2 — Mesh | `docs/` (excluding Tier 0 and Tier 2.5) | agent | full Zero-Entropy rules |
| 2.5 — Session continuity | `docs/handoffs/` | agent (one file per session) | own schema; exempt from ZE rules |
| 3 — Governance | `agent.md`, `lifecycle.md`, `lwip.config.yaml` | both, by proposal | n/a |

---

## Lineage

Karpathy's "LLM-Wiki" essay proposed the core metaphor (LLM as librarian, wiki as codebase). LWIP adds the quantitative rules, the Tier 0 inbox, the deterministic auditor, and the trigger-gated grooming loop so the protocol survives a fast development cycle without burning tokens on every session.

---

## Version history

- **v1.6** — OmegaWiki-inspired refinements: (a) `docs/foundations/` for terminal background nodes, (b) `docs/gaps/` for first-class open questions with their own lifecycle, (c) Prune Protocol distinguishes *stale* (silent archive) from *failed* (archive + `contradicts` edge from hub), (d) auditor writes a derived `docs/.lwip/edges.jsonl` cache on each run so external tools can consume the graph without re-parsing markdown, (e) `addresses_gap` added to meaningful link types.
- **v1.5** — Tier 2.5 session handoffs. Every shutdown writes a narrative record to `docs/handoffs/<timestamp>.md`; the Boot Gate reads the latest so working memory survives across sessions.
- **v1.4** — typed inbound links; `weak-isolation` alert closes the Goodhart loophole where a single throwaway link silenced the orphan check.
- **v1.3** — Tier 0 inbox; deterministic auditor (`tools/lwip-audit.py`); trigger-gated shutdown; externalised thresholds in `lwip.config.yaml`; pre-commit hook.
- **v1.2** — initial four-rule protocol; JIT-scripted audits at every shutdown.

---

## License

MIT — see [LICENSE](LICENSE).
