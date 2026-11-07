import os
import unittest
import json

class TestIPSW_M5_ReportAndGraph(unittest.TestCase):
    """Integrity and synthesis test suite for Milestone IPSW-M5."""

    PROJECT_ROOT = "/home/prem/Projects/AppleTV"
    REPORT_PATH = os.path.join(PROJECT_ROOT, "reports/IPSW_TECHNICAL_REPORT.md")
    GRAPH_JSON = os.path.join(PROJECT_ROOT, "graphify-out/graph.json")
    GRAPH_HTML = os.path.join(PROJECT_ROOT, "graphify-out/graph.html")
    INDEX_HTML = os.path.join(PROJECT_ROOT, "graphify-out/index.html")
    PROJECT_MD = os.path.join(PROJECT_ROOT, "PROJECT.md")

    def test_01_master_report_existence_and_sections(self):
        """Verify IPSW_TECHNICAL_REPORT.md exists, is non-empty, and has all required sections."""
        self.assertTrue(os.path.exists(self.REPORT_PATH), f"Missing report: {self.REPORT_PATH}")
        with open(self.REPORT_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertGreater(len(content), 6000, "Master report is too short")

        required_sections = [
            "Executive Summary & Project Profile",
            "Firmware Partition Map & Forensic Topology",
            "Cryptographic Evaluation: AEA1 & RFC 9180 HPKE",
            "RootFS Manifest Forensics",
            "UI Architecture & Comparative Evolution",
            "Static Binary Analysis & REA Reverse Engineering",
            "Security Boundaries & Hardware Exploits",
            "Knowledge Graph Expansion",
            "Verification & Quality Gate Audit Trail",
        ]
        for section in required_sections:
            self.assertIn(section, content, f"Master report missing section: {section}")

    def test_02_master_report_veracity(self):
        """Verify authentic hashes, keys, and kernel versions in IPSW_TECHNICAL_REPORT.md."""
        with open(self.REPORT_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("08bb7001565746699636a00c73ae35c0cba7536a15bafc01c900de26048d77c1", content)
        self.assertIn("ca0d1a3eb45cdb15b15babced612a5d37914299f5d5d141d488ddccb40cda496", content)
        self.assertIn("efd41ef06e0adc9426ae40d7c6635dbca5c88f68029411bf465a34c7c9baf7d9", content)
        self.assertIn("xnu-12377.163.4~3", content)
        self.assertIn("iBoot-13822.120.5", content)

    def test_03_graph_json_metrics(self):
        """Verify graph.json node count, edge count, and community count."""
        self.assertTrue(os.path.exists(self.GRAPH_JSON))
        with open(self.GRAPH_JSON, "r", encoding="utf-8") as f:
            graph = json.load(f)

        node_count = len(graph.get("nodes", []))
        edge_count = len(graph.get("links", []))
        community_count = len(graph.get("communities", {}))

        self.assertGreaterEqual(node_count, 770, f"Expected >= 770 nodes, found {node_count}")
        self.assertGreaterEqual(edge_count, 1540, f"Expected >= 1540 edges, found {edge_count}")
        self.assertGreaterEqual(community_count, 9, f"Expected >= 9 communities, found {community_count}")

    def test_04_graph_community_8_presence(self):
        """Verify Community 8 (IPSW & AEA Cryptography) is present and populated."""
        with open(self.GRAPH_JSON, "r", encoding="utf-8") as f:
            graph = json.load(f)
        communities = graph.get("communities", {})
        self.assertIn("8", communities)
        c8 = communities["8"]
        self.assertIn("IPSW", c8.get("name", ""))
        self.assertGreaterEqual(c8.get("node_count", 0), 15)

    def test_05_graph_key_nodes_present(self):
        """Verify core IPSW entities exist in graph.json nodes."""
        with open(self.GRAPH_JSON, "r", encoding="utf-8") as f:
            graph = json.load(f)
        node_ids = {n["id"] for n in graph.get("nodes", [])}

        required_nodes = [
            "ipsw_restore_archive",
            "part_ipsw_rootfs_aea",
            "part_ipsw_recovery_aea",
            "part_ipsw_erase_ramdisk",
            "crypto_hpke_rfc9180",
            "crypto_wkms_escrow",
            "key_rootfs_aes256",
            "manifest_rootfs_mtree",
            "daemon_restored_external",
            "daemon_diskimagesiod",
            "kernel_xnu_25_6_0",
            "hw_appletv_5_3",
            "vuln_checkm8_a8",
        ]
        for nid in required_nodes:
            self.assertIn(nid, node_ids, f"Missing graph node: {nid}")

    def test_06_graph_html_visualizers(self):
        """Verify graph.html and index.html exist, are non-empty, and contain updated metrics."""
        self.assertTrue(os.path.exists(self.GRAPH_HTML))
        self.assertTrue(os.path.exists(self.INDEX_HTML))
        with open(self.GRAPH_HTML, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn("775 Nodes", html)
        self.assertIn("1545 Edges", html)
        self.assertIn("9 Subsystems", html)

    def test_07_project_md_milestones(self):
        """Verify PROJECT.md documents all completed IPSW milestones."""
        self.assertTrue(os.path.exists(self.PROJECT_MD))
        with open(self.PROJECT_MD, "r", encoding="utf-8") as f:
            content = f.read()
        required_milestones = [
            "IPSW-M1",
            "IPSW-M2",
            "IPSW-M3",
            "IPSW-M4",
            "IPSW-M5",
        ]
        for m in required_milestones:
            self.assertIn(m, content, f"PROJECT.md missing milestone: {m}")
        self.assertIn("IPSW_TECHNICAL_REPORT.md", content)

if __name__ == "__main__":
    unittest.main()
