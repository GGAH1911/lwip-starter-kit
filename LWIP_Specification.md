# LWIP: LLM-Wiki Implementation Protocol (v1.2)

> **"Turning scattered information into a compounding, traceable codebase of knowledge while maintaining zero upkeep cost."**
> LWIP is an industrial-grade engineering protocol evolved from Andrej Karpathy's original "LLM-Wiki" concept through the integration of Zero-Entropy metrics and Automated Governance.

---

## 🏛️ 1. Core Architecture (The Three-Tier Model)

LWIP categorizes project assets into three distinct, immutable layers to ensure structural clarity for any LLM Agent.

### Tier 1: The Immutable Source (Raw Data)
- **Manifest**: Static files, research papers, logs, and raw inputs.
- **Rule**: The Agent reads but **never** modifies this layer. It is the Ground Truth.

### Tier 2: The Evolving Mesh (The Wiki)
- **Manifest**: Automatically generated Markdown files structured in a **Hub-and-Spoke** topology. This includes not only prose pages but also comparison tables, charts, slide decks, or any format best suited to the content.
- **Rule**: This is the "Codebase" of knowledge. The Agent owns this layer and maintains its structural integrity.

### Tier 3: The Governance Engine (The Schema)
- **Manifest**: `agent.md` (Constitutional rules) and `lifecycle.md` (Operational gates).
- **Rule**: This provides the "Programming Interface" for the Agent to manage Tier 2. The Human and Agent co-evolve Tier 3 over time as the project matures.

---

## 🧬 2. Performance Metrics (Zero-Entropy Standards)

The protocol mandates a **Structural Zero-Entropy** state, where structural and semantic disorder is eliminated using quantitative alerts.

- **0-Gap Integrity**: 100% synchronization between physical files and the knowledge index.
- **0-Isolation**: Every node must have at least one semantic inbound link from a Hub.
- **0-Congestion**: Hubs containing excessive links must undergo **Semantic Fission** (splitting into sub-hubs) to maintain discoverability.
- **100%-Lineage (Traceability)**: When pages are merged or pruned, no factual claim may lose its origin. Every wiki page must carry a YAML frontmatter `sources:` field listing the raw inputs that informed it.

---

## ⚙️ 3. Operational Cycle (The Agentic Loop)

Any LLM Agent implementing LWIP must follow these standard operational phases:

### A. Context-Aware Ingest (Growth)
The Agent reads a source and integrates it. Before executing heavy cross-reference updates, the Agent evaluates **Resource Guardrails** (API token limits, context window size, or hardware constraints). If constrained, it performs a lightweight metadata-only sync. Every Ingest is logged in `docs/log.md` and the Health Dashboard in `docs/index.md` is updated.

### B. Query & Promote (Exploration → Accumulation)
When the Human asks a question, the Agent synthesizes an answer from the wiki. If the answer is substantive — a comparison, an analysis, a novel connection — the Agent should offer to **promote it into a permanent wiki page**. Valuable explorations must not vanish into chat history; they compound in the mesh.

### C. Consolidate & Merge (Organization)
The Agent transforms raw lists of links into **Role-Based Tables** and merges overlapping pages. During merges, the Agent preserves source lineage for every claim and logs the operation in `docs/log.md`.

### D. Prune (Controlled Contraction)
The Agent removes stale, superseded, or abandoned pages — but never blindly. Before deletion, the Agent must: (1) generate a one-line impact note in `docs/log.md` stating what was removed, how many inbound links pointed to it, and what was done about them; (2) archive the original content rather than destroy it; (3) update all affected inbound links.

### E. Audit (Sanitization)
Before session closure (The Shutdown Gate), the Agent runs a Zero-Entropy scan using JIT Tooling to resolve all structural and traceability alerts. No session ends with a broken graph or untraceable claim.

---

## 📂 4. The Standard Package Manifest (JIT Philosophy)

To implement LWIP in a new project, initialize the following structure in the root:

```text
.
├── .gitignore           # Prevents OS/JIT clutter
├── agent.md             # Constitutional rules
├── lifecycle.md         # Operational gates
├── LWIP_Specification.md# This manual
└── docs/
    ├── index.md         # Health Dashboard
    ├── log.md           # Operation Log
    └── hubs/            # Semantic Hubs
```

The following artifacts must be initialized:

1. **`/agent.md`**: This project's "Constitution" defining the Agent's roles, limits, and knowledge philosophy.
2. **`/lifecycle.md`**: Step-by-step "Boot" and "Shutdown" sequences for the session.
3. **`/docs/index.md`**: The master catalog of all wiki pages with a **Health Dashboard** at the top.
4. **`/docs/log.md`**: The chronological, append-only record of all wiki operations.
5. **`/docs/hubs/`**: The dedicated directory for structural navigation assets.

> [!TIP]
> **Just-In-Time (JIT) Tooling over Fixed Scripts**
> LWIP does *not* mandate hardcoded scripts. The Agent generates throwaway "vibe-coded" scripts during Audit or Consolidate phases, executes them to verify metrics, and instantly discards them. Keep the environment pristine.

---

## 🌟 5. Why LWIP?

- **Agent Portability**: Whether it's Claude, Codex, or a custom GPT, they "boot" into the project by reading `agent.md`.
- **Compounding Intelligence**: Information doesn't decay; it builds up with auditable traceability (YAML frontmatter lineage).
- **Exploratory Accumulation**: Valuable Q&A sessions are promoted into permanent wiki pages, not lost in chat history.
- **Architectural & Logical Clarity**: A clean root directory, organic JIT tooling, and a 0-Alert graph provide a seamless developer experience.

---
> [!IMPORTANT]
> **LWIP** is not just a tool; it is a **Contract** between the Human Curator and the AI Librarian. By signing this contract, you ensure your project remains an ever-sharp asset, never a computational junk drawer.
