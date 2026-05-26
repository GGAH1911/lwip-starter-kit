#!/usr/bin/env python3
"""
LWIP v1.5 - Deterministic Knowledge-Mesh Auditor
=================================================

Purpose
-------
A single, version-controlled, DETERMINISTIC scanner that measures the
Zero-Entropy state of the mesh WITHOUT calling an LLM. This replaces the old
"write a throwaway script, run it, delete it" JIT loop for *measurement*.

The LLM is still responsible for *semantic judgement* (what to merge, how to
split a hub, what a node means). But counting links, finding orphans, checking
frontmatter and computing churn is now mechanical, repeatable and free.

What it does
------------
1. Static Zero-Entropy scan of docs/:
   - 0-Isolation     : spoke pages with no inbound [[link]] from any hub
   - missing-lineage : node pages with no usable `sources:` frontmatter
   - broken-lineage  : `sources:` entries pointing to files that do not exist
   - 0-Congestion    : hubs with too many outbound links (-> Semantic Fission)
   - flat-directory  : folders with too many flat .md files and no sub-folders
   - inbox-backlog   : Tier 0 sandbox over its size / age limits
2. Deterministic GROOMING TRIGGER (proposal 3): using git, decide whether a
   (costly) LLM grooming pass is actually warranted, based on churn - so the
   agent is NOT woken on every commit.
3. Writes machine-readable state to docs/.lwip/state.json for the agent's
   Boot Gate to read.

Design constraints
------------------
- Python 3 standard library only. No pip installs. No network.
- Never blocks by default (fast-dev friendly). Use --strict to fail on hard
  violations (suitable for CI).

Usage
-----
    python3 tools/lwip-audit.py            # scan + churn, write state, exit 0
    python3 tools/lwip-audit.py --quiet    # only write state, minimal output
    python3 tools/lwip-audit.py --strict   # exit 1 if hard alerts exist (CI)
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (this file lives in <repo>/tools/)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
INBOX = DOCS / "00_inbox"
HUBS = DOCS / "hubs"
STATE_DIR = DOCS / ".lwip"
CONFIG = ROOT / "lwip.config.yaml"

# Folders that are NOT spoke nodes (they are sources of links, buffers, or meta)
EXCLUDE_TOP = {"00_inbox", "archive", ".lwip", "hubs", "handoffs"}
EXCLUDE_NAMES = {"index.md", "log.md", "readme.md"}

DEFAULTS = {
    "hub_max_outbound_links": 20,
    "dir_max_flat_files": 12,
    "inbox_max_items": 15,
    "inbox_max_age_days": 7,
    "trigger_diff_lines": 200,
    "trigger_file_velocity": 5,
    "trigger_commits_since_groom": 10,
    # v1.4: link types that count as a *semantic* inbound link for 0-Isolation.
    # Anything else (see-also, related, nav, ...) is "navigational" and does
    # NOT, on its own, satisfy 0-Isolation - this closes the Goodhart loophole
    # where a single throwaway link silences the orphan alert.
    "meaningful_link_types": ["core", "derives", "supports", "depends",
                              "contradicts"],
}


# ---------------------------------------------------------------------------
# Config (flat `key: value` so we need no YAML dependency)
# ---------------------------------------------------------------------------
def load_config():
    cfg = dict(DEFAULTS)
    if CONFIG.exists():
        for raw in CONFIG.read_text(encoding="utf-8").splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            key, val = (p.strip() for p in line.split(":", 1))
            if key not in cfg:
                continue
            if isinstance(cfg[key], list):
                # comma- or space-separated list of bare tokens
                val = val.strip("[]")
                items = [t.strip().strip("'\"").lower()
                         for t in re.split(r"[,\s]+", val) if t.strip()]
                if items:
                    cfg[key] = items
            else:
                try:
                    cfg[key] = int(val)
                except ValueError:
                    pass
    return cfg


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def is_node(path):
    """A spoke page that must obey 0-Isolation and lineage rules."""
    if path.suffix != ".md":
        return False
    rel = path.relative_to(DOCS)
    if rel.parts and rel.parts[0] in EXCLUDE_TOP:
        return False
    if path.name.lower() in EXCLUDE_NAMES:
        return False
    return True


def read_frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[3:end]


def extract_sources(text):
    """Return list of source paths declared in frontmatter (may be empty)."""
    fm = read_frontmatter(text)
    if fm is None:
        return []
    items = []
    m = re.search(r"(?mi)^\s*sources\s*:\s*(.*)$", fm)
    if m:
        rest = m.group(1).strip()
        if rest.startswith("["):
            inner = rest.strip("[]")
            items += [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
    # multi-line dash list under `sources:`
    capture = False
    for ln in fm.splitlines():
        s = ln.strip()
        if re.match(r"(?i)^sources\s*:", s):
            capture = True
            continue
        if capture:
            if s.startswith("-"):
                items.append(s[1:].strip().strip("'\""))
            elif s and ":" in s:
                capture = False
    return [i for i in items if i]


def collect_hub_links(meaningful_types):
    """
    Scan every hub and classify inbound links per target stem.

    Type detection (deterministic, per line):
      - explicit type in the wikilink pipe:  [[target|core]]
      - or a meaningful-type token elsewhere on the same line (e.g. the
        `Role` cell of a `| [[target]] | core | ... |` hub table row)
    A target's status is the strongest seen across all hubs:
      "meaningful" > "navigational".

    Returns (any_links, meaningful_links) as two sets of lowercase stems.
    """
    any_links, meaningful = set(), set()
    if not HUBS.exists():
        return any_links, meaningful

    mset = {t.lower() for t in meaningful_types}
    type_token = re.compile(r"\b(" + "|".join(re.escape(t) for t in mset) + r")\b",
                            re.IGNORECASE) if mset else None

    for hub in HUBS.rglob("*.md"):
        for line in read_text(hub).splitlines():
            wikilinks = re.findall(r"\[\[([^\]#]+?)\]\]", line)
            mdlinks = re.findall(r"\]\(([^)#]+?)\)", line)
            if not wikilinks and not mdlinks:
                continue
            # is there a meaningful-type token anywhere on this line?
            line_meaningful = bool(type_token and type_token.search(line))
            for raw in wikilinks:
                if "|" in raw:
                    target, _, label = raw.partition("|")
                    pipe_meaningful = label.strip().lower() in mset
                else:
                    target, pipe_meaningful = raw, False
                stem = Path(target.strip()).stem.lower()
                any_links.add(stem)
                if pipe_meaningful or line_meaningful:
                    meaningful.add(stem)
            for raw in mdlinks:
                stem = Path(raw.strip()).stem.lower()
                any_links.add(stem)
                if line_meaningful:
                    meaningful.add(stem)
    return any_links, meaningful


def count_outbound_links(text):
    return len(re.findall(r"\[\[", text)) + len(re.findall(r"\]\(", text))


def git(*args):
    try:
        out = subprocess.run(
            ["git", *args], cwd=str(ROOT),
            capture_output=True, text=True, timeout=15,
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except Exception:
        return ""


def git_available():
    return bool(git("rev-parse", "--is-inside-work-tree"))


# ---------------------------------------------------------------------------
# Static Zero-Entropy scan
# ---------------------------------------------------------------------------
def static_scan(cfg):
    alerts = {
        "isolation": [],        # no inbound link at all
        "weak_isolation": [],   # linked, but only by navigational (untyped) links
        "missing_lineage": [],
        "broken_lineage": [],
        "congestion": [],
        "flat_dir": [],
        "inbox_backlog": [],
    }
    if not DOCS.exists():
        return alerts, 0

    any_links, meaningful_links = collect_hub_links(cfg["meaningful_link_types"])

    # nodes: isolation + lineage
    for path in DOCS.rglob("*.md"):
        if not is_node(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        stem = path.stem.lower()
        if stem not in any_links:
            alerts["isolation"].append(rel)
        elif stem not in meaningful_links:
            alerts["weak_isolation"].append(rel)
        srcs = extract_sources(read_text(path))
        if not srcs:
            alerts["missing_lineage"].append(rel)
        else:
            for s in srcs:
                if not (ROOT / s).exists():
                    alerts["broken_lineage"].append(f"{rel} -> {s}")

    # hubs: congestion
    if HUBS.exists():
        for hub in HUBS.rglob("*.md"):
            n = count_outbound_links(read_text(hub))
            if n > cfg["hub_max_outbound_links"]:
                alerts["congestion"].append(
                    f"{hub.relative_to(ROOT).as_posix()} ({n} links)"
                )

    # flat directories
    for d in [DOCS, *[p for p in DOCS.rglob("*") if p.is_dir()]]:
        rel = d.relative_to(DOCS)
        if rel.parts and rel.parts[0] in EXCLUDE_TOP:
            continue
        children = list(d.iterdir())
        mds = [c for c in children if c.is_file() and c.suffix == ".md"]
        subdirs = [c for c in children if c.is_dir()]
        if len(mds) > cfg["dir_max_flat_files"] and not subdirs:
            alerts["flat_dir"].append(
                f"{d.relative_to(ROOT).as_posix()} ({len(mds)} files)"
            )

    # inbox backlog (Tier 0 hygiene)
    if INBOX.exists():
        now = time.time()
        items = [
            f for f in INBOX.iterdir()
            if f.is_file() and f.name.lower() != "readme.md"
        ]
        if len(items) > cfg["inbox_max_items"]:
            alerts["inbox_backlog"].append(
                f"{len(items)} items (max {cfg['inbox_max_items']})"
            )
        max_age = cfg["inbox_max_age_days"] * 86400
        stale = [f.name for f in items if (now - f.stat().st_mtime) > max_age]
        if stale:
            alerts["inbox_backlog"].append(
                f"{len(stale)} item(s) older than {cfg['inbox_max_age_days']}d"
            )

    hard = sum(len(alerts[k]) for k in
               ("isolation", "weak_isolation", "missing_lineage",
                "broken_lineage", "congestion"))
    return alerts, hard


# ---------------------------------------------------------------------------
# Deterministic grooming trigger (proposal 3)
# ---------------------------------------------------------------------------
def churn_report(cfg):
    info = {"git": False, "diff_lines": 0, "max_file_velocity": 0,
            "commits_since_groom": 0, "last_groom": None}
    if not git_available():
        return info
    info["git"] = True

    last = ""
    marker = STATE_DIR / "last_groom"
    if marker.exists():
        last = read_text(marker).strip()
    if last and not git("rev-parse", "--verify", last):
        last = ""
    info["last_groom"] = last or None

    rng = f"{last}..HEAD" if last else "HEAD"

    # changed lines since last groom (committed) + staged
    lines = 0
    for src in (git("diff", "--numstat", rng) if last else "",
                git("diff", "--cached", "--numstat")):
        for row in src.splitlines():
            cols = row.split("\t")
            if len(cols) >= 2:
                a = cols[0] if cols[0].isdigit() else "0"
                d = cols[1] if cols[1].isdigit() else "0"
                lines += int(a) + int(d)
    info["diff_lines"] = lines

    if last:
        cnt = git("rev-list", "--count", f"{last}..HEAD")
        info["commits_since_groom"] = int(cnt) if cnt.isdigit() else 0
        log = git("log", f"{last}..HEAD", "--name-only", "--pretty=format:")
        freq = {}
        for f in log.splitlines():
            f = f.strip()
            if f:
                freq[f] = freq.get(f, 0) + 1
        info["max_file_velocity"] = max(freq.values()) if freq else 0

    return info


def decide_grooming(hard_alerts, churn, cfg):
    reasons = []
    if hard_alerts > 0:
        reasons.append(f"{hard_alerts} hard entropy alert(s) open")
    if churn["diff_lines"] >= cfg["trigger_diff_lines"]:
        reasons.append(
            f"churn {churn['diff_lines']} lines >= {cfg['trigger_diff_lines']}"
        )
    if churn["max_file_velocity"] >= cfg["trigger_file_velocity"]:
        reasons.append(
            f"file velocity {churn['max_file_velocity']} "
            f">= {cfg['trigger_file_velocity']}"
        )
    if churn["commits_since_groom"] >= cfg["trigger_commits_since_groom"]:
        reasons.append(
            f"{churn['commits_since_groom']} commits since last groom "
            f">= {cfg['trigger_commits_since_groom']}"
        )
    return reasons


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(argv):
    quiet = "--quiet" in argv
    strict = "--strict" in argv
    cfg = load_config()

    alerts, hard = static_scan(cfg)
    churn = churn_report(cfg)
    reasons = decide_grooming(hard, churn, cfg)
    recommended = bool(reasons)

    state = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "lwip_version": "1.5",
        "hard_alerts": hard,
        "alerts": alerts,
        "churn": churn,
        "grooming_recommended": recommended,
        "grooming_reasons": reasons,
    }
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "state.json").write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    if not quiet:
        print("LWIP v1.5 deterministic audit")
        print(f"  hard alerts          : {hard}")
        for k, v in alerts.items():
            if v:
                print(f"  - {k:16s}: {len(v)}")
                for item in v[:5]:
                    print(f"      . {item}")
                if len(v) > 5:
                    print(f"      . (+{len(v) - 5} more)")
        if churn["git"]:
            print(f"  churn since groom    : {churn['diff_lines']} lines, "
                  f"{churn['commits_since_groom']} commits, "
                  f"max file velocity {churn['max_file_velocity']}")
        else:
            print("  churn                : (git not available)")
        if recommended:
            print("  >> GROOMING RECOMMENDED:")
            for r in reasons:
                print(f"     - {r}")
        else:
            print("  >> mesh is lean; no grooming pass needed")

    if strict and hard > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
