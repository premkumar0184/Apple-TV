#!/usr/bin/env python3
"""
test_binary_analysis.py
Verification suite for Milestone 3 (Binary Analysis & REA Reverse Engineering).
Validates structural integrity, Objective-C classes, Swift reflection,
framework dependency graph, and IPC contract definitions.
Strictly static analysis - zero execution of ARM64 binaries.
"""

import os
import unittest
import json

class TestMilestone3BinaryAnalysis(unittest.TestCase):
    
    def test_macho_structures_integrity(self):
        json_path = "analysis/symbols/macho_structures.json"
        self.assertTrue(os.path.exists(json_path), f"Missing {json_path}")
        with open(json_path) as f:
            data = json.load(f)
            
        expected_binaries = ["PineBoard", "HeadBoard", "PreBoard", "TVMusic", "TVSystemMenuService", "TVPeripheralAgent", "kernelcache", "dyld_shared_cache"]
        for b in expected_binaries:
            self.assertIn(b, data, f"Missing binary entry: {b}")
            self.assertIn("file_info", data[b])
            self.assertGreater(data[b]["file_info"]["size_bytes"], 1000)

        # Check PineBoard Mach-O details
        pb_macho = data["PineBoard"]["macho_info"]
        self.assertEqual(pb_macho["header"]["magic"], "MH_MAGIC_64")
        self.assertEqual(pb_macho["header"]["cputype"], "ARM64")
        self.assertEqual(pb_macho["header"]["filetype"], "EXECUTE")
        self.assertGreaterEqual(pb_macho["load_commands_count"], 100)

        # Check dyld shared cache mappings
        dyld = data["dyld_shared_cache"]["cache_info"]
        self.assertEqual(dyld["magic"], "dyld_v1   arm64")
        self.assertEqual(dyld["image_count"], 1086)
        self.assertEqual(dyld["mapping_count"], 3)

    def test_objc_metadata_integrity(self):
        json_path = "analysis/objc/objc_classes.json"
        self.assertTrue(os.path.exists(json_path), f"Missing {json_path}")
        with open(json_path) as f:
            data = json.load(f)
            
        self.assertIn("PineBoard", data)
        self.assertIn("HeadBoard", data)
        self.assertIn("TVMusic", data)
        
        # Check class counts
        self.assertGreaterEqual(data["PineBoard"]["class_count"], 250)
        self.assertGreaterEqual(data["HeadBoard"]["class_count"], 150)
        self.assertGreaterEqual(data["TVMusic"]["class_count"], 100)
        
        # Verify specific critical classes
        pb_class_names = [c["name"] for c in data["PineBoard"]["classes"]]
        self.assertIn("PBSystemOverlaySession", pb_class_names)
        self.assertIn("PBSystemService", pb_class_names)
        self.assertIn("PBScreenSaverManager", pb_class_names)
        self.assertIn("PBAppInfoController", pb_class_names)
        
        hb_class_names = [c["name"] for c in data["HeadBoard"]["classes"]]
        self.assertIn("HBTopShelfManager", hb_class_names)
        self.assertIn("HBIconCache", hb_class_names)
        
        # Verify class dumps exist on disk
        for app in ["PineBoard", "HeadBoard", "PreBoard", "TVMusic", "TVSystemMenuService", "TVPeripheralAgent"]:
            dump_file = f"analysis/objc/{app}_classes.txt"
            self.assertTrue(os.path.exists(dump_file), f"Missing {dump_file}")
            with open(dump_file) as df:
                content = df.read()
                self.assertIn("@interface", content)
                self.assertIn("@end", content)

    def test_swift_architecture_integrity(self):
        json_path = "analysis/swift/TVMusic_swift_types.json"
        self.assertTrue(os.path.exists(json_path), f"Missing {json_path}")
        with open(json_path) as f:
            data = json.load(f)
            
        self.assertIn("metadata_sections", data)
        self.assertIn("__swift5_reflstr", data["metadata_sections"])
        self.assertIn("__swift5_typeref", data["metadata_sections"])
        
        # Verify audio visualizer strings in reflection
        refl = data["reflection_identifiers"]
        self.assertIn("device", refl)
        self.assertIn("commandQueue", refl)
        self.assertIn("visualizerIntensity", refl)
        self.assertIn("spectrumAnalysis", refl)
        
        # Verify demangled symbols file
        sym_file = "analysis/swift/TVMusic_swift_symbols.txt"
        self.assertTrue(os.path.exists(sym_file))
        with open(sym_file) as f:
            content = f.read()
            self.assertIn("Mangled:", content)
            self.assertIn("Demangled:", content)

    def test_framework_dependency_mapping(self):
        json_path = "analysis/symbols/framework_dependencies.json"
        self.assertTrue(os.path.exists(json_path), f"Missing {json_path}")
        with open(json_path) as f:
            data = json.load(f)
            
        meta = data["metadata"]
        self.assertGreaterEqual(meta["total_unique_frameworks"], 50)
        self.assertGreater(meta["public_frameworks_count"], 15)
        self.assertGreater(meta["private_frameworks_count"], 30)
        
        # Check PineBoard links PineBoardServices and FrontBoard
        pb_deps = [d["framework_name"] for d in data["applications"]["PineBoard"]["dependencies"]]
        self.assertIn("PineBoardServices", pb_deps)
        self.assertIn("FrontBoard", pb_deps)
        self.assertIn("BackBoardServices", pb_deps)
        self.assertIn("UIKit", pb_deps)
        
        # Check exports and imports files
        self.assertTrue(os.path.exists("analysis/symbols/exported_symbols.json"))
        self.assertTrue(os.path.exists("analysis/symbols/imported_symbols.json"))
        self.assertTrue(os.path.exists("analysis/symbols/FRAMEWORK_DEPENDENCY_GRAPH.md"))

    def test_ipc_contracts_documentation(self):
        md_path = "analysis/ipc/IPC_CONTRACTS.md"
        self.assertTrue(os.path.exists(md_path), f"Missing {md_path}")
        with open(md_path) as f:
            content = f.read()
            
        self.assertIn("com.apple.PBSystemService.XPCListener", content)
        self.assertIn("PBSSystemServiceInterface", content)
        self.assertIn("com.apple.HeadBoard.topShelf", content)
        self.assertIn("TVTopShelfProvider", content)
        self.assertIn("TVPeripheralAgent", content)
        self.assertIn("TVSystemMenuService", content)
        self.assertIn("NSDistributedNotificationCenter", content)

    def test_binary_analysis_report(self):
        report_path = "analysis/BINARY_ANALYSIS_REPORT.md"
        self.assertTrue(os.path.exists(report_path), f"Missing {report_path}")
        with open(report_path) as f:
            content = f.read()
            
        self.assertIn("Executive Summary", content)
        self.assertIn("Mach-O Structure", content)
        self.assertIn("Objective-C Runtime Architecture", content)
        self.assertIn("Swift Runtime & Type Infrastructure", content)
        self.assertIn("System Framework Dependency Topology", content)
        self.assertIn("Inter-Process Communication", content)
        self.assertIn("dyld_shared_cache & kernelcache", content)
        self.assertIn("Execution Safety Attestation (R7)", content)

if __name__ == "__main__":
    unittest.main()
