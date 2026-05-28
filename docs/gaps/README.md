# Gaps (Tier 2 — First-Class Unknowns)

Long-standing open questions the project has not yet resolved. Each gap is a
proper Tier 2 node with its own page and lineage. Gaps persist across
sessions until explicitly **resolved** (linked to the node that answers them)
or **abandoned** (no longer worth pursuing).

## Distinction from session "Open questions"

| Aspect | Handoff `Open questions` | `docs/gaps/` |
| :--- | :--- | :--- |
| Scope | One session's deferred items | Project-wide, multi-session |
| Lifetime | Until next session resolves it (or it's elevated to a gap) | Until status flips to `resolved` or `abandoned` |
| Rule compliance | Exempt (Tier 2.5) | **Full Tier 2 rules** (linked from hub, has `sources:`) |
| Granularity | Bullets in a handoff file | Each is its own node |

If a handoff's open question shows up across multiple sessions, **promote
it to a gap** — give it a page here. It now has a name and a lineage.

## File naming

`gap-<short-slug>.md` (e.g. `gap-foo-vs-bar-perf.md`, `gap-citation-rerank-failure.md`).

## Schema

```yaml
---
status: open            # open | resolved | abandoned
raised: 2026-05-27       # when the question was first noticed
sources: [raw/x.md, docs/concepts/y.md]   # where the question came from
resolved_by: null        # filled in when resolved: path to the resolving node
created: 2026-05-27
updated: 2026-05-27
---

# Gap: <one-line question>

## Why it matters
<1-3 sentences. What downstream decisions depend on resolving this?>

## What we know so far
<bullets — partial evidence, attempted approaches, what's been ruled out>

## What we'd need to close it
<bullets — concrete data, sources, or experiments that would resolve it>

## Discussion
<free-form notes accumulated across sessions>
```

## Lifecycle

1. **Open**: raised when a session-level handoff's "Open question" recurs or
   when the agent notices a question that can't be answered from the current
   mesh.
2. **Resolved**: a later node answers it. Link the resolving node back with
   `addresses_gap`. Update frontmatter (`status: resolved`, `resolved_by: <path>`).
   The gap page stays — its history is part of the lineage of the resolution.
3. **Abandoned**: the question is no longer worth pursuing (out of scope,
   superseded by a different question, etc.). Frontmatter `status: abandoned`
   with a note explaining why. Like resolved, the file stays.

## Rules

- Full Tier 2 obedience: linked from a hub (e.g. a `docs/hubs/gaps.md` or a
  domain-specific hub), `sources:` populated, no flat-dir violation.
- **0-Isolation works exactly as it does for every node: the meaningful inbound
  link must come from a hub.** While a gap is open, link it from a hub with
  `core` (it's a core open question of its topic). A node→node link does *not*
  clear 0-Isolation — the auditor only counts inbound links from hubs.
- The `addresses_gap` link type is the edge the *resolving node* carries back
  to the gap. It's a **meaningful** type (see `lwip.config.yaml`) and is
  recorded as a first-class semantic edge in `edges.jsonl`, but it does **not**
  substitute for the gap's hub link — the gap stays hub-linked throughout its
  lifecycle. (In practice the gap was already hub-linked while open, so nothing
  extra is needed when it's resolved.)
- Don't auto-prune a resolved gap. The historical record of "we used to not
  know this" is the point.

## Why this exists

Borrowed from OmegaWiki, which tracks "known gaps" and "methodological gaps"
inside Topic nodes. Promoted here to its own folder so the project has a
visible **list of what it doesn't know** — a quantity that should be
explicitly tracked rather than diffused across session handoffs.
