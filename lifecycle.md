# ⌛ Operations & Lifecycle (LWIP Gates)

> **Protocol**: LLM-Wiki Implementation Protocol (LWIP v1.2)
> **Rule**: An Agent must strictly follow these sequences at the beginning and end of every interaction session. 

---

## 🚀 The Boot Gate (Session Start)

**"Understand before you act."**

When you begin a session with the Human Curator:
1. **Locate the Index**: Read `docs/index.md`. Check the **Health Dashboard** at the top for current wiki state (page count, orphans, conflicts, suggested actions).
2. **Check the Log**: Read the last 5 entries of `docs/log.md` to understand what happened in recent sessions.
3. **Scan the Hubs**: Browse `docs/hubs/` to understand the current topology (Which domains exist? Where are the gaps?).
4. **Check Operational Status**: If a `task.md` or roadmap file exists, read it to understand the current objectives.
5. **Report Ready**: Acknowledge the start of the session and state your awareness of the current topology and any pending suggested actions from the Health Dashboard.

---

## 🔄 The Ingest Loop (During Session)

**"Grow the mesh, but keep it traceable."**

When the Human provides new raw data:
1. **Resource Check**: Evaluate your available tokens/context. Choose between Deep Ingest or Light Sync.
2. **Semantic Delta**: Identify what this new data adds or contradicts in the existing mesh.
3. **Update Spoke Pages**: Write/modify detail pages with proper YAML frontmatter:
   ```yaml
   ---
   sources: [raw/new_source.md]
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   ---
   ```
4. **Update Hubs**: Add the new Spoke pages to the relevant Semantic Hub. Format as `| Link | Role | Description |`.
5. **Log It**: Append an entry to `docs/log.md`:
   `## [YYYY-MM-DD] ingest | Source Title — N pages created, M pages updated.`
6. **Update Health Dashboard**: Increment the page count and update status in `docs/index.md`.

---

## 🔍 The Query & Promote Loop (During Session)

**"Good answers should not vanish into chat history."**

When the Human asks a substantive question:
1. **Search**: Read the index and relevant hub pages to find source material.
2. **Synthesize**: Generate a thorough answer with citations to wiki pages.
3. **Evaluate Promotion**: If the answer contains a novel comparison, analysis, or synthesis that would be valuable as a permanent reference, **offer to promote it** into a wiki page.
4. **If Promoted**: Create the page with proper frontmatter, link it from the relevant Hub, update `docs/index.md` under "Syntheses & Analyses", and log the operation.

---

## ✂️ The Prune Protocol (As Needed)

**"Contract the graph with discipline, never blindly."**

When a page is stale, superseded, or abandoned:
1. **Impact Assessment**: Before deleting, count how many inbound links point to this page.
2. **Log the Removal**: Append an entry to `docs/log.md`:
   `## [YYYY-MM-DD] prune | 'Page Title' — 3 inbound links from 'Hub X' redirected to 'Archive Page'.`
3. **Archive, Don't Destroy**: Move the page to a `docs/archive/` folder rather than permanently deleting it.
4. **Update Links**: Redirect all inbound links to the archive page or a suitable replacement.
5. **Update Health Dashboard**: Decrement the page count in `docs/index.md`.

---

## 🛑 The Shutdown Gate (Session End)

**"Leave no trace of disorder."**

Before you finalize the work and allow the human to disconnect, you must execute the Zero-Entropy Audit.

**Step 1: JIT Audit Generation**
- Write a temporary script that scans the `docs/` folder to check for:
  - Flat directories (More than 12 files without a sub-folder).
  - Isolated nodes (Markdown files with no `[[inbound_links]]` from a Hub).
  - Congested Hubs (Hubs with >20 outbound links).
  - Missing frontmatter (Pages without a `sources:` YAML field).

**Step 2: Execution & Purge**
- Run the script and capture the output.
- Delete the temporary script immediately.

**Step 3: Self-Healing (Consolidation)**
- If the Audit returned Alerts (Entropy > 0): 
  - **Execute Restructuring**: Split congested hubs, link isolated nodes, group flat directories, add missing frontmatter.
  - Re-run the JIT Audit until Alerts = 0.

**Step 4: Final Briefing**
- Only when Entropy = 0, present the Final Summary to the Human. 
- State the number of nodes updated.
- Confirm that `100%-Lineage`, `0-Gap`, and `0-Isolation` maintain optimal status.
- Update the Health Dashboard in `docs/index.md`.
- Session closed.
