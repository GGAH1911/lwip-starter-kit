# 📥 Tier 0 — The Inbox (Sandbox)

> **Drop anything here. No rules. No frontmatter. No links required.**

This folder is the **buffer layer** between your raw thinking and the
structured mesh. It exists so that a half-formed idea, a pasted terminal
error, or a quick voice-to-text note never has to interrupt your flow to
satisfy the Zero-Entropy rules.

## What goes here

- Raw error logs pasted mid-debug
- Half-baked ideas, TODOs, questions
- Clipped quotes, links, screenshots — anything, any format

## The two rules that *do* apply (hygiene)

The Inbox is exempt from `0-Gap`, `0-Isolation`, and `100%-Lineage` — **but it
is not a junk drawer.** It is bounded so it can never rot into one:

1. **Size cap** — if the Inbox holds more than `inbox_max_items` files
   (default **15**, see `lwip.config.yaml`), the auditor raises a
   `inbox-backlog` alert.
2. **Age cap** — any item older than `inbox_max_age_days` (default **7**)
   raises the same alert.

When either trips, the agent's **Inbox Triage Loop** (see `lifecycle.md`)
parses each item, promotes the worthwhile ones into proper Tier 2 spoke
pages with full lineage, and removes the rest. The Inbox should regularly
return to (or near) empty.

## How to triage

Tell your agent:

> "Triage the inbox."

It will, for each item: decide *keep / merge / discard*, and for anything
kept, create a structured node, link it from the right hub, record its
`sources:`, then clear the item from the Inbox.
