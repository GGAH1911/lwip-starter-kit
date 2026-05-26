# ⌛ Operations & Lifecycle (LWIP Gates)

> **Protocol**: LLM-Wiki Implementation Protocol (**LWIP v1.5**)
> **Rule**: Follow these sequences at the start and end of every session.

> **v1.5 change**: Every Shutdown writes a session handoff to
> `docs/handoffs/<timestamp>.md` — even quiet sessions get a minimal entry. The
> Boot Gate reads the latest handoff so the next session inherits rationale,
> open questions, and a starting point — not just artifacts.

> **v1.4 change**: 0-Isolation is now type-aware. The heal cycle distinguishes
> `isolation` (no link at all) from `weak-isolation` (linked only by
> navigational pointers); both must be cleared with a *meaningful* typed link.

> **v1.3 changes**: the Boot Gate now reads a deterministic state file and an
> Inbox; a new **Inbox Triage Loop** drains Tier 0; and the Shutdown Gate is
> **trigger-gated** — it no longer forces a full audit on every session.

---

## 🚀 The Boot Gate (Session Start)

**"Understand before you act."**

1. **Read deterministic state**: Open `docs/.lwip/state.json` (written by
   `tools/lwip-audit.py` / the git hook). Note `hard_alerts`,
   `grooming_recommended`, and `grooming_reasons`. If the file is missing,
   run `python3 tools/lwip-audit.py --quiet` once to generate it.
2. **Locate the Index**: Read `docs/index.md` and its Health Dashboard.
3. **Check the Log**: Read the last 5 entries of `docs/log.md`.
4. **Read the latest handoff**: Open the most recent file in `docs/handoffs/`
   (highest filename wins, since handoffs are timestamped). Pay attention to
   its **Open questions** and **Next session — start here** sections — these
   are your inherited context. If `docs/handoffs/` is empty (first session),
   skip this step.
5. **Scan the Hubs**: Browse `docs/hubs/` to understand current topology.
6. **Check the Inbox**: Glance at `docs/00_inbox/` — how many items wait, how
   old is the oldest.
7. **Report Ready**: Acknowledge the session in one line: current topology,
   inbox depth, count of inherited open questions from the last handoff, and
   whether grooming is recommended (and why). If grooming is **not**
   recommended, proceed straight to the Human's request — do not restructure
   for its own sake.

---

## 📥 The Inbox Triage Loop (Tier 0 → Tier 2)

**"Capture freely, but never let the buffer rot."**

Run this on request ("triage the inbox"), or automatically whenever the state
file shows an `inbox-backlog` alert.

1. **List**: Enumerate items in `docs/00_inbox/` (ignore `README.md`).
2. **Classify each**: decide **keep / merge / discard**.
   - *Discard*: noise, duplicates, transient logs already resolved.
   - *Merge*: belongs inside an existing node — append and re-cite.
   - *Keep*: create a new Tier 2 spoke page.
3. **Promote kept items**: write the node with proper frontmatter
   (`sources:` pointing at the original capture or its Tier 1 origin), link it
   from the relevant Hub, and add it to `docs/index.md`.
4. **Clear**: remove the triaged item from the Inbox.
5. **Log it**:
   `## [YYYY-MM-DD] triage | Inbox drained — K kept, M merged, D discarded.`

---

## 🔄 The Ingest Loop (During Session)

**"Grow the mesh, but keep it traceable."**

1. **Resource Check**: Evaluate available tokens/context — Deep Ingest vs Light
   Sync.
2. **Semantic Delta**: Identify what the new data adds or contradicts.
3. **Update Spoke Pages**: Write/modify detail pages with YAML frontmatter
   (`sources:`, `created:`, `updated:`).
4. **Update Hubs**: Add new Spokes to the relevant Hub as
   `| Link | Role | Description |`.
5. **Log It**:
   `## [YYYY-MM-DD] ingest | Source Title — N pages created, M updated.`
6. **Update Health Dashboard** in `docs/index.md`.

---

## 🔍 The Query & Promote Loop (During Session)

**"Good answers should not vanish into chat history."**

1. **Search**: Read the index and relevant hub pages.
2. **Synthesize**: Answer thoroughly, with citations to wiki pages.
3. **Evaluate Promotion**: If the answer is a novel comparison, analysis, or
   synthesis worth keeping, **offer to promote it** into a wiki page.
4. **If Promoted**: Create the page with frontmatter, link it from the Hub,
   update `docs/index.md` under "Syntheses & Analyses", and log it.

---

## ✂️ The Prune Protocol (Trigger-Aware)

**"Contract the graph with discipline, never blindly."**

Prune when a page is stale/superseded **and** the deterministic signal supports
it (e.g. the auditor flags it, or its file velocity spiked then went cold).

1. **Impact Assessment**: Count inbound links to the page.
2. **Log the Removal**:
   `## [YYYY-MM-DD] prune | 'Page Title' — 3 inbound links redirected to 'X'.`
3. **Archive, don't destroy**: Move it to `docs/archive/`. (Git history is your
   real undo; the archive folder is for human-browsable recovery.)
4. **Update Links**: Redirect all inbound links.
5. **Update Health Dashboard** in `docs/index.md`.

---

## 🛑 The Shutdown Gate (Session End) — Trigger-Gated

**"Leave no trace of disorder — but don't burn tokens chasing zero on a quiet
session."**

**Step 0: Refresh + decide.**
Run `python3 tools/lwip-audit.py`. Read `grooming_recommended` from the
resulting `docs/.lwip/state.json`.

**If `grooming_recommended` is `false`:**
- The mesh is lean and churn is below trigger. Update the Health Dashboard,
  confirm `0` hard alerts, then jump to **Step H** (write handoff). No
  restructuring needed.

**If `grooming_recommended` is `true`, run the heal cycle:**

1. **Read the alerts** straight from `state.json` (deterministic — no need to
   re-scan by hand): isolation, **weak-isolation**, missing/broken lineage,
   congestion, flat directories, inbox backlog.
2. **Self-Heal (Consolidation)**: split congested hubs; for `isolation` and
   `weak-isolation` nodes add a **meaningful typed link** from the right hub
   (`core`/`derives`/`supports`/`depends`; never paper over an orphan with a
   bare `see-also`); add missing frontmatter; fix broken source paths; group
   flat directories; and drain the inbox if it tripped.
3. **Re-run** `python3 tools/lwip-audit.py --quiet` until `hard_alerts` = 0.
4. **Mark the groom point** so churn triggers reset:
   `git rev-parse HEAD > docs/.lwip/last_groom`
5. Update the Health Dashboard in `docs/index.md`; then fall through to
   **Step H**.

**Step H: Write the session handoff (always — both branches).**

- Create `docs/handoffs/<YYYY-MM-DD-HHMM>.md` using the schema in
  `docs/handoffs/README.md`.
- Required frontmatter: `session`, `turns`, `mesh_changes` (created/modified/
  pruned arrays), `sources_ingested`, `hard_alerts_at_close`, `grooming_ran`.
- Required sections: **Human asked**, **What was done**, **Decisions &
  rationale**, **Open questions / deferred**, **Next session — start here**.
- A quiet session (no mesh changes) still writes a handoff: minimal
  frontmatter plus a one-line body ("Q&A only, no mesh changes") is enough.
- Do **not** skip this step to save tokens. The cost is a single write; the
  value is that next session boots with rationale and a starting point, not
  just artifacts.

**Step F: Final Briefing.**

- State: nodes updated, handoff written, `hard_alerts = 0`. Session closed.

---

## 🔧 Setup (one-time)

```
# install the deterministic trigger hook
cp hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
#   (or, to version the hooks: git config core.hooksPath hooks)

# keep machine state out of git
echo "docs/.lwip/" >> .gitignore
```
