#!/usr/bin/env python3
"""
Fixture-based tests for tools/lwip-audit.py.

Stdlib `unittest` only — no pip installs, matching the kit's dependency-free
promise. Each test builds a throwaway repo tree in a temp dir and points the
auditor's module-level path globals at it, then calls the unit functions
directly (no subprocess, no git).

Run from the repo root:
    python3 -m unittest discover -s tests
    python3 tests/test_lwip_audit.py            # also works
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

# The auditor filename is hyphenated, so load it by path rather than `import`.
_AUDIT_PATH = Path(__file__).resolve().parent.parent / "tools" / "lwip-audit.py"
_spec = importlib.util.spec_from_file_location("lwip_audit", _AUDIT_PATH)
audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit)


def node(sources="[raw/exists.md]", body="body"):
    """A minimal Tier 2 node page with frontmatter."""
    return f"---\nsources: {sources}\ncreated: 2026-05-27\nupdated: 2026-05-27\n---\n\n# Title\n\n{body}\n"


class AuditorTest(unittest.TestCase):
    # ---- fixture plumbing ------------------------------------------------
    def setUp(self):
        self._saved = {k: getattr(audit, k) for k in
                       ("ROOT", "DOCS", "INBOX", "HUBS", "STATE_DIR", "CONFIG")}
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        for d in ("docs/hubs", "docs/concepts", "docs/00_inbox",
                  "docs/handoffs", "docs/foundations", "docs/gaps",
                  "docs/archive", "raw"):
            (self.root / d).mkdir(parents=True, exist_ok=True)
        # A real raw file so valid lineage resolves.
        (self.root / "raw" / "exists.md").write_text("x", encoding="utf-8")

        audit.ROOT = self.root
        audit.DOCS = self.root / "docs"
        audit.INBOX = self.root / "docs" / "00_inbox"
        audit.HUBS = self.root / "docs" / "hubs"
        audit.STATE_DIR = self.root / "docs" / ".lwip"
        audit.CONFIG = self.root / "lwip.config.yaml"

    def tearDown(self):
        for k, v in self._saved.items():
            setattr(audit, k, v)
        self._tmp.cleanup()

    def write(self, relpath, text):
        p = self.root / relpath
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def cfg(self, **overrides):
        c = dict(audit.DEFAULTS)
        c.update(overrides)
        return c

    # ---- is_node ---------------------------------------------------------
    def test_is_node_classification(self):
        cases = {
            "docs/concepts/foo.md": True,
            "docs/foundations/bar.md": True,   # foundations obey node rules
            "docs/gaps/gap-x.md": True,        # gaps obey node rules
            "docs/hubs/h.md": False,           # hubs are link sources, not spokes
            "docs/index.md": False,            # EXCLUDE_NAMES
            "docs/log.md": False,
            "docs/00_inbox/note.md": False,    # Tier 0
            "docs/handoffs/s.md": False,       # Tier 2.5
            "docs/archive/old.md": False,
            "docs/concepts/README.md": False,  # readme excluded by name
        }
        for rel, expected in cases.items():
            p = self.write(rel, node())
            self.assertEqual(audit.is_node(p), expected, rel)

    # ---- isolation / weak-isolation -------------------------------------
    def test_isolation_levels(self):
        # Hub links 'good' meaningfully, 'weak' only navigationally; 'orphan'
        # is not linked at all.
        self.write("docs/hubs/h.md",
                   "| [[good]] | core | ok |\n"
                   "| [[weak]] | see-also | nav only |\n")
        self.write("docs/concepts/good.md", node())
        self.write("docs/concepts/weak.md", node())
        self.write("docs/concepts/orphan.md", node())

        alerts, _ = audit.static_scan(self.cfg())
        iso = {Path(p).stem for p in alerts["isolation"]}
        weak = {Path(p).stem for p in alerts["weak_isolation"]}

        self.assertIn("orphan", iso)
        self.assertNotIn("good", iso)
        self.assertNotIn("weak", iso)        # it IS linked, just not meaningfully
        self.assertIn("weak", weak)
        self.assertNotIn("good", weak)

    # ---- lineage ---------------------------------------------------------
    def test_missing_and_broken_lineage(self):
        self.write("docs/hubs/h.md",
                   "| [[nolin]] | core | x |\n"
                   "| [[badlin]] | core | x |\n"
                   "| [[goodlin]] | core | x |\n")
        # No frontmatter at all -> missing_lineage.
        self.write("docs/concepts/nolin.md", "# no frontmatter\n")
        # sources points at a file that does not exist -> broken_lineage.
        self.write("docs/concepts/badlin.md", node(sources="[raw/nope.md]"))
        # Valid.
        self.write("docs/concepts/goodlin.md", node(sources="[raw/exists.md]"))

        alerts, _ = audit.static_scan(self.cfg())
        missing = {Path(p).stem for p in alerts["missing_lineage"]}
        broken = {p.split(" -> ")[0].split("/")[-1] for p in alerts["broken_lineage"]}

        self.assertIn("nolin.md", {Path(p).name for p in alerts["missing_lineage"]})
        self.assertIn("badlin.md", {p.split(" -> ")[0].split("/")[-1]
                                    for p in alerts["broken_lineage"]})
        self.assertNotIn("goodlin", missing)
        self.assertTrue(any("raw/nope.md" in b for b in alerts["broken_lineage"]))

    # ---- congestion ------------------------------------------------------
    def test_congestion(self):
        links = "".join(f"[[n{i}]] " for i in range(3))
        self.write("docs/hubs/big.md", links)
        alerts, _ = audit.static_scan(self.cfg(hub_max_outbound_links=2))
        self.assertTrue(any("big.md" in c for c in alerts["congestion"]))
        # Under the cap -> no alert.
        alerts2, _ = audit.static_scan(self.cfg(hub_max_outbound_links=5))
        self.assertEqual(alerts2["congestion"], [])

    # ---- flat directory --------------------------------------------------
    def test_flat_directory(self):
        for i in range(3):
            self.write(f"docs/concepts/f{i}.md", node())
        alerts, _ = audit.static_scan(self.cfg(dir_max_flat_files=2))
        self.assertTrue(any("concepts" in f for f in alerts["flat_dir"]))

    # ---- inbox backlog ---------------------------------------------------
    def test_inbox_backlog(self):
        for i in range(3):
            self.write(f"docs/00_inbox/i{i}.md", "raw note\n")
        alerts, _ = audit.static_scan(self.cfg(inbox_max_items=2))
        self.assertTrue(alerts["inbox_backlog"])

    # ---- edge extraction (the v1.6 hub-edge regression) ------------------
    def test_hub_edges_are_captured_with_types(self):
        """Regression guard: hubs MUST be scanned for edges even though they
        are excluded from is_node(). This is the bug the first real ingest
        surfaced — extract_all_edges() had reused EXCLUDE_TOP."""
        self.write("docs/hubs/h.md",
                   "| [[alpha]] | core | x |\n"
                   "| [[beta]] | depends | x |\n"
                   "| [[gamma]] | see-also | nav |\n")
        self.write("docs/concepts/alpha.md", node())
        self.write("docs/concepts/beta.md", node())
        self.write("docs/concepts/gamma.md", node())

        edges = audit.extract_all_edges(self.cfg())
        by_dst = {e["dst"]: e for e in edges if e["src"].endswith("hubs/h.md")}

        self.assertIn("alpha", by_dst, "hub edges must be captured")
        self.assertEqual(by_dst["alpha"]["type"], "core")
        self.assertEqual(by_dst["beta"]["type"], "depends")
        self.assertEqual(by_dst["gamma"]["type"], "navigational")

    def test_pipe_annotated_edge_type(self):
        self.write("docs/hubs/h.md", "prose with [[delta|supports]] inline.\n")
        self.write("docs/concepts/delta.md", node())
        edges = audit.extract_all_edges(self.cfg())
        delta = [e for e in edges if e["dst"] == "delta"]
        self.assertTrue(delta)
        self.assertEqual(delta[0]["type"], "supports")

    def test_excluded_subtrees_are_not_edge_sources(self):
        # Tier 0 / handoffs / archive / .lwip must not contribute edges.
        self.write("docs/00_inbox/note.md", "[[should_not_appear]]\n")
        self.write("docs/handoffs/s.md", "[[also_not]]\n")
        self.write("docs/archive/old.md", "[[archived_out]]\n")
        edges = audit.extract_all_edges(self.cfg())
        dsts = {e["dst"] for e in edges}
        self.assertNotIn("should_not_appear", dsts)
        self.assertNotIn("also_not", dsts)
        self.assertNotIn("archived_out", dsts)

    def test_gap_isolation_via_hub_and_addresses_gap_edge(self):
        # 0-Isolation is consistently "linked from a hub" — gaps included.
        # A gap clears isolation via its HUB link (typically `core` while open).
        # The addresses_gap edge from a resolving *node* is captured as a
        # meaningful edge in edges.jsonl, but does NOT itself clear isolation
        # (node->node links never do). This guards the doc/impl agreement that
        # the test suite caught diverging on its first run.
        self.write("docs/hubs/h.md",
                   "| [[gap-x]] | core | open question |\n"
                   "| [[resolver]] | core | x |\n")
        self.write("docs/gaps/gap-x.md", node())
        self.write("docs/concepts/resolver.md",
                   node(body="resolves [[gap-x|addresses_gap]] now."))

        alerts, _ = audit.static_scan(self.cfg())
        iso = {Path(p).stem for p in alerts["isolation"]}
        weak = {Path(p).stem for p in alerts["weak_isolation"]}
        self.assertNotIn("gap-x", iso)    # cleared by the hub `core` link
        self.assertNotIn("gap-x", weak)

        edges = audit.extract_all_edges(self.cfg())
        ag = [e for e in edges
              if e["dst"] == "gap-x" and e["type"] == "addresses_gap"]
        self.assertTrue(ag, "addresses_gap edge from resolver must be captured")

    def test_node_to_node_link_does_not_clear_isolation(self):
        # Only hub links count for 0-Isolation. A node anchored solely by
        # another node (no hub) is still isolated.
        self.write("docs/hubs/h.md", "| [[anchored]] | core | x |\n")
        self.write("docs/concepts/anchored.md",
                   node(body="points to [[lonely|supports]]."))
        self.write("docs/concepts/lonely.md", node())  # only a node links it
        alerts, _ = audit.static_scan(self.cfg())
        iso = {Path(p).stem for p in alerts["isolation"]}
        self.assertIn("lonely", iso)

    # ---- dangling edges (soft) ------------------------------------------
    def test_dangling_wikilink_detected(self):
        # A wikilink to a stem with no backing .md file is dangling.
        self.write("docs/hubs/h.md", "| [[real]] | core | x |\n")
        self.write("docs/concepts/real.md",
                   node(body="links to [[ghost]] which does not exist."))
        edges = audit.extract_all_edges(self.cfg())
        dangling = audit.find_dangling_edges(edges, audit.valid_node_stems())
        joined = " ".join(dangling)
        self.assertIn("ghost", joined)
        self.assertNotIn("[[real]]", joined)  # real resolves, not dangling

    def test_mdlink_is_not_dangling_checked(self):
        # Markdown links (relative paths, dirs, anchors) are NOT dangling-checked
        # — only wikilinks are. A nav link to a directory must not be flagged.
        self.write("docs/hubs/h.md", "| [[real]] | core | x |\n")
        self.write("docs/concepts/real.md",
                   node(body="see [the hubs](../hubs/) and [log](../log.md)."))
        edges = audit.extract_all_edges(self.cfg())
        dangling = audit.find_dangling_edges(edges, audit.valid_node_stems())
        self.assertEqual(dangling, [])

    def test_dangling_is_soft_not_hard(self):
        # A dangling wikilink must NOT raise hard_alerts (forward-linking to a
        # not-yet-written node is a legitimate authoring pattern).
        self.write("docs/hubs/h.md", "| [[real]] | core | x |\n")
        self.write("docs/concepts/real.md", node(body="forward [[planned]]."))
        alerts, hard = audit.static_scan(self.cfg())
        edges = audit.extract_all_edges(self.cfg())
        dangling = audit.find_dangling_edges(edges, audit.valid_node_stems())
        self.assertEqual(hard, 0)           # nothing hard wrong
        self.assertTrue(dangling)           # but the dangling link is reported

    def test_edges_record_kind(self):
        self.write("docs/hubs/h.md",
                   "| [[wikitarget]] | core | x | and [md](../log.md)\n")
        self.write("docs/concepts/wikitarget.md", node())
        edges = audit.extract_all_edges(self.cfg())
        kinds = {e["dst"]: e["kind"] for e in edges if e["src"].endswith("hubs/h.md")}
        self.assertEqual(kinds.get("wikitarget"), "wikilink")
        self.assertEqual(kinds.get("log"), "mdlink")

    # ---- code-span stripping --------------------------------------------
    def test_fenced_code_block_links_ignored(self):
        # A wikilink inside a fenced code block is documentation, not a real
        # edge — must not be extracted (and so must not be flagged dangling).
        self.write("docs/concepts/doc.md", node(body=(
            "Real link [[realnode]].\n\n"
            "```\n"
            "Example: [[fenced_ghost]] | core | x |\n"
            "```\n"
        )))
        self.write("docs/concepts/realnode.md", node())
        self.write("docs/hubs/h.md", "| [[doc]] | core | x |\n| [[realnode]] | core | x |\n")
        edges = audit.extract_all_edges(self.cfg())
        dsts = {e["dst"] for e in edges if e["src"].endswith("concepts/doc.md")}
        self.assertIn("realnode", dsts)
        self.assertNotIn("fenced_ghost", dsts)
        dangling = audit.find_dangling_edges(edges, audit.valid_node_stems())
        self.assertFalse(any("fenced_ghost" in d for d in dangling))

    def test_inline_code_links_ignored(self):
        self.write("docs/concepts/doc.md", node(body=(
            "Use the `[[inline_ghost]]` syntax, but really link [[realnode]]."
        )))
        self.write("docs/concepts/realnode.md", node())
        self.write("docs/hubs/h.md", "| [[doc]] | core | x |\n| [[realnode]] | core | x |\n")
        edges = audit.extract_all_edges(self.cfg())
        dsts = {e["dst"] for e in edges if e["src"].endswith("concepts/doc.md")}
        self.assertIn("realnode", dsts)
        self.assertNotIn("inline_ghost", dsts)

    def test_congestion_ignores_code_block_links(self):
        # Links shown as an example inside a fence must not inflate the
        # hub's outbound-link count.
        body = "```\n" + "".join(f"[[ex{i}]] " for i in range(10)) + "\n```\n"
        body += "[[only_real]]\n"
        self.write("docs/hubs/big.md", body)
        alerts, _ = audit.static_scan(self.cfg(hub_max_outbound_links=2))
        self.assertEqual(alerts["congestion"], [])  # only 1 real link


if __name__ == "__main__":
    unittest.main(verbosity=2)
