# Session Handoffs (Tier 2.5)

Per-session narrative records. Each agent session writes exactly one file
named `YYYY-MM-DD-HHMM.md` capturing what the human asked, what was done, the
**rationale** behind decisions, open questions, and a starting point for the
next session.

## Why this folder exists

Without handoffs, the agent's working memory evaporates at session end. The
operation log (`docs/log.md`) records *what* changed (ingest / prune / triage,
one line each), but not *why* or *what was in progress*. The next session
boots from artifacts and re-discovers context from scratch.

`docs/.lwip/state.json` is machine churn (gitignored, overwritten each run).
Handoffs are the human-readable, versioned counterpart.

## Schema

```yaml
---
session: 2026-05-26T23:35
turns: 12
mesh_changes:
  created: [docs/concepts/foo.md]
  modified: [docs/hubs/bar.md]
  pruned: []
sources_ingested: [raw/paper_x.pdf]
hard_alerts_at_close: 0
grooming_ran: false
---

## Human asked
<1-3 lines>

## What was done
<bullets, with [[wikilinks]] to touched nodes where relevant>

## Decisions & rationale
<the *why*, not the *what*. Why a node was split, why a prune was deferred, etc.>

## Open questions / deferred
<things to address next session>

## Next session — start here
<concrete first actions>
```

## Rules

- One file per session, named `YYYY-MM-DD-HHMM.md` (24-hour local time).
- Exempt from 0-Isolation, 0-Gap, and 100%-Lineage (see `agent.md` Chapter 5,
  Tier 2.5). Handoffs reference mesh nodes but are not themselves mesh nodes.
- Versioned in git (unlike `docs/.lwip/state.json` which is gitignored).
- The Boot Gate reads the highest-named file in this folder. Filenames sort
  chronologically as long as the format is honoured.
- Even a quiet session writes a handoff: frontmatter plus a one-line body
  ("Q&A only, no mesh changes") is sufficient. Do **not** skip to save tokens —
  the next session relies on this being there.

## How the next Boot Gate uses it

The agent opens the latest file and prioritises the **Open questions** and
**Next session — start here** sections during its orientation. Inherited
context appears in the Report Ready line ("3 open questions inherited from
2026-05-26-2330").
