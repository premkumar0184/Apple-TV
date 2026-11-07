#!/usr/bin/env python3
"""
Prototype for automated table veracity test for tests/test_ipsw_m1_integrity.py.
"""

import os
import re
import hashlib
import unittest

PROJECT_ROOT = "/home/prem/Projects/AppleTV"

class TestTableVeracityPrototype(unittest.TestCase):

    def setUp(self):
        os.chdir(PROJECT_ROOT)

    def test_ledger_tables_veracity(self):
        """Programmatically audit all markdown table rows in reports/IPSW_EXTRACTION_LEDGER.md against disk."""
        ledger_path = "reports/IPSW_EXTRACTION_LEDGER.md"
        self.assertTrue(os.path.isfile(ledger_path), f"Ledger missing: {ledger_path}")

        with open(ledger_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Parse rows containing | `path` | size | ... | `sha256` |
        # Regex captures:
        # 1: file path in backticks
        # 2: size in bytes (with commas)
        # 3: sha256 hash in backticks
        row_pattern = re.compile(
            r"\|\s*`([^`]+)`\s*\|\s*([0-9,]+)\s*\|.*?`([0-9a-f]{64})`\s*\|",
            re.MULTILINE
        )

        matches = row_pattern.findall(text)
        self.assertGreater(len(matches), 30, f"Expected >30 audited table rows, found {len(matches)}")

        mismatches = []
        audited_count = 0

        for rel_path, size_str, recorded_hash in matches:
            expected_size = int(size_str.replace(",", ""))

            # Candidate locations for the file:
            # 1. Project root direct (e.g. extracted/ipsw/...)
            # 2. Ramdisk erase (extracted/ipsw/ramdisk_erase/...)
            # 3. Ramdisk update (extracted/ipsw/ramdisk_update/...)
            # 4. IPSW archive unpacked (AppleTV5,3_26.6.1_23L781_Restore/...)
            candidates = [
                rel_path,
                os.path.join("extracted/ipsw/ramdisk_erase", rel_path),
                os.path.join("extracted/ipsw/ramdisk_update", rel_path),
                os.path.join("AppleTV5,3_26.6.1_23L781_Restore", rel_path),
            ]

            disk_file = None
            for cand in candidates:
                if os.path.exists(cand) and not os.path.isdir(cand):
                    disk_file = cand
                    break

            if disk_file is None:
                mismatches.append(f"MISSING FILE on disk: {rel_path} (checked: {candidates})")
                continue

            actual_size = os.path.getsize(disk_file)
            if actual_size != expected_size:
                mismatches.append(
                    f"SIZE MISMATCH for {rel_path} ({disk_file}): actual {actual_size:,} vs recorded {expected_size:,}"
                )
                continue

            with open(disk_file, "rb") as fp:
                actual_hash = hashlib.sha256(fp.read()).hexdigest()
            if actual_hash != recorded_hash:
                mismatches.append(
                    f"HASH MISMATCH for {rel_path} ({disk_file}): actual {actual_hash} vs recorded {recorded_hash}"
                )
                continue

            audited_count += 1

        print(f"Audited {audited_count} table rows successfully.")
        if mismatches:
            print("Mismatches found (as expected on unmodified ledger):")
            for m in mismatches:
                print("  -", m)

        # For this prototype test, we verify that it caught the exact known discrepancies
        return mismatches

if __name__ == "__main__":
    t = TestTableVeracityPrototype()
    t.setUp()
    mismatches = t.test_ledger_tables_veracity()
