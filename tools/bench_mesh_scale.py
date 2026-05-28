#!/usr/bin/env python3
"""
LWIP mesh-scaling benchmark
===========================

Answers docs/gaps/gap-grep-scale-ceiling.md: where does the grep + static-
priming model stop scaling, and where would embedding retrieval start to earn
its per-message cost?

It generates synthetic meshes at increasing node counts and measures the two
quantities that actually drive the LWIP serving model:

  1. grep latency  — wall time to `grep -rl <term>` across the whole mesh.
     This is the "lookup" cost. LWIP claims it is effectively instant at small
     scale.
  2. prime tokens  — the rough token cost to *prime* a session: the agent reads
     index.md + every hub on boot (not every node). Estimated as
     chars / 4. This is the cost that grows with the mesh and eventually
     blows the prompt budget — the real ceiling.

Design constraints: Python 3 stdlib only, no network. Self-cleaning (writes
into a temp dir that is removed on exit).

Usage:
    python3 tools/bench_mesh_scale.py                # default 100/1k/10k
    python3 tools/bench_mesh_scale.py 100 1000 5000  # custom node counts
"""
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

NODES_PER_HUB = 15          # respect the default 20-link congestion cap
CHARS_PER_TOKEN = 4         # crude but standard token estimate
NODE_BODY_CHARS = 300       # representative spoke-page size


def build_mesh(root: Path, n_nodes: int):
    """Create a synthetic mesh: n_nodes spoke pages grouped under hubs, plus an
    index.md. Returns (n_hubs, index_path)."""
    docs = root / "docs"
    hubs = docs / "hubs"
    concepts = docs / "concepts"
    for d in (hubs, concepts):
        d.mkdir(parents=True, exist_ok=True)

    n_hubs = max(1, (n_nodes + NODES_PER_HUB - 1) // NODES_PER_HUB)
    filler = "lorem ipsum dolor sit amet " * (NODE_BODY_CHARS // 27 + 1)

    node_i = 0
    index_lines = ["# Index\n"]
    for h in range(n_hubs):
        rows = []
        for _ in range(min(NODES_PER_HUB, n_nodes - node_i)):
            stem = f"node{node_i:06d}"
            (concepts / f"{stem}.md").write_text(
                f"---\nsources: [raw/x.md]\n---\n\n# {stem}\n\n{filler[:NODE_BODY_CHARS]}\n",
                encoding="utf-8",
            )
            rows.append(f"| [[{stem}]] | core | synthetic node {node_i} |")
            node_i += 1
        (hubs / f"hub{h:05d}.md").write_text(
            f"---\nsources: [raw/x.md]\n---\n\n# Hub {h}\n\n"
            "| Node | Role | Description |\n| :--- | :--- | :--- |\n"
            + "\n".join(rows) + "\n",
            encoding="utf-8",
        )
        index_lines.append(f"- [[hub{h:05d}]] — {len(rows)} nodes\n")
    index_path = docs / "index.md"
    index_path.write_text("".join(index_lines), encoding="utf-8")
    return n_hubs, index_path


def prime_tokens(root: Path) -> int:
    """Chars of index.md + every hub, divided by CHARS_PER_TOKEN."""
    docs = root / "docs"
    chars = (docs / "index.md").stat().st_size
    for hub in (docs / "hubs").glob("*.md"):
        chars += hub.stat().st_size
    return chars // CHARS_PER_TOKEN


def grep_latency_ms(root: Path, term: str) -> float:
    docs = str(root / "docs")
    t0 = time.perf_counter()
    subprocess.run(["grep", "-rl", term, docs],
                   capture_output=True, text=True)
    return (time.perf_counter() - t0) * 1000.0


def main(argv):
    counts = [int(a) for a in argv] if argv else [100, 1000, 10000]
    print("LWIP mesh-scaling benchmark")
    print(f"  nodes/hub={NODES_PER_HUB}, ~{NODE_BODY_CHARS} chars/node, "
          f"{CHARS_PER_TOKEN} chars/token\n")
    print(f"  {'nodes':>8} {'hubs':>6} {'grep ms':>9} {'prime tokens':>14}")
    print(f"  {'-'*8} {'-'*6} {'-'*9} {'-'*14}")
    for n in counts:
        tmp = Path(tempfile.mkdtemp(prefix="lwip-bench-"))
        try:
            n_hubs, _ = build_mesh(tmp, n)
            # take the best of 3 grep runs to reduce noise
            ms = min(grep_latency_ms(tmp, "node000042") for _ in range(3))
            toks = prime_tokens(tmp)
            print(f"  {n:>8} {n_hubs:>6} {ms:>8.1f} {toks:>14,}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1:])
