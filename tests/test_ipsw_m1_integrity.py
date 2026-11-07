#!/usr/bin/env python3
"""
IPSW Milestone M1 Integrity & Verification Test Suite
Validates:
1. raw/ipsw/ checksums and manifest preservation.
2. extracted/ipsw/ramdisk_erase and extracted/ipsw/ramdisk_update APFS restore environments.
3. extracted/ipsw/kernel/kernelcache.macho Mach-O ARM64 decompression, Adler-32, and size.
4. extracted/ipsw/firmware/ DeviceTree, bootloaders (LLB, iBoot), and restore graphics (PNG).
5. reports/IPSW_EXTRACTION_LEDGER.md completeness.
"""

import hashlib
import os
import plistlib
import re
import struct
import unittest
import zlib
from PIL import Image


class TestIPSWExtractionM1(unittest.TestCase):

    PROJECT_ROOT = "/home/prem/Projects/AppleTV"

    def setUp(self):
        os.chdir(self.PROJECT_ROOT)

    def test_01_directories_exist(self):
        """Verify all required M1 directories exist."""
        required_dirs = [
            "raw/ipsw",
            "raw/ipsw/manifests",
            "extracted/ipsw",
            "extracted/ipsw/ramdisk_erase",
            "extracted/ipsw/ramdisk_update",
            "extracted/ipsw/kernel",
            "extracted/ipsw/firmware",
            "reports",
        ]
        for d in required_dirs:
            self.assertTrue(os.path.isdir(d), f"Required directory missing: {d}")

    def test_02_ipsw_checksum_and_size(self):
        """Verify checksums.sha256 records correct hash and size for the IPSW."""
        checksum_file = "raw/ipsw/checksums.sha256"
        self.assertTrue(os.path.isfile(checksum_file), "Checksum file missing")
        with open(checksum_file, "r") as f:
            content = f.read()

        expected_hash = "08bb7001565746699636a00c73ae35c0cba7536a15bafc01c900de26048d77c1"
        self.assertIn(expected_hash, content, "IPSW SHA-256 missing from checksums.sha256")
        self.assertIn("5269474064", content, "IPSW file size missing from checksums.sha256")

        # Verify actual file size
        actual_size = os.path.getsize("AppleTV5,3_26.6.1_23L781_Restore.ipsw")
        self.assertEqual(actual_size, 5269474064, f"IPSW file size mismatch: {actual_size}")

    def test_03_manifest_preservation(self):
        """Verify manifest plists were extracted and match target properties."""
        manifest_dir = "raw/ipsw/manifests"
        manifest_files = [
            "BuildManifest.plist",
            "Restore.plist",
            "SystemVersion.plist",
            "RestoreVersion.plist",
        ]
        for mf in manifest_files:
            p = os.path.join(manifest_dir, mf)
            self.assertTrue(os.path.isfile(p), f"Manifest file missing: {p}")
            self.assertGreater(os.path.getsize(p), 0, f"Manifest file empty: {p}")

        # Validate SystemVersion.plist
        with open("raw/ipsw/manifests/SystemVersion.plist", "rb") as f:
            sys_ver = plistlib.load(f)
        self.assertEqual(sys_ver.get("ProductBuildVersion"), "23L781")
        self.assertEqual(sys_ver.get("ProductVersion"), "26.6.1")
        self.assertEqual(sys_ver.get("ProductName"), "Apple TVOS")

        # Validate RestoreVersion.plist
        with open("raw/ipsw/manifests/RestoreVersion.plist", "rb") as f:
            res_ver = plistlib.load(f)
        self.assertEqual(res_ver.get("RestoreVersion"), "23.12.781.0.0")

        # Validate Restore.plist
        with open("raw/ipsw/manifests/Restore.plist", "rb") as f:
            restore = plistlib.load(f)
        self.assertEqual(restore.get("ProductBuildVersion"), "23L781")
        self.assertEqual(restore.get("SupportedProductTypes"), ["AppleTV5,3"])
        dev_map = restore.get("DeviceMap", [{}])[0]
        self.assertEqual(dev_map.get("BoardConfig"), "j42dap")
        self.assertEqual(dev_map.get("BDID"), 52)
        self.assertEqual(dev_map.get("CPID"), 28672)

    def test_04_ramdisk_extraction(self):
        """Verify erase and update restore ramdisks extracted cleanly."""
        erase_daemon = "extracted/ipsw/ramdisk_erase/usr/local/bin/restored_external"
        update_daemon = "extracted/ipsw/ramdisk_update/usr/local/bin/restored_update"

        self.assertTrue(os.path.isfile(erase_daemon), f"restored_external missing: {erase_daemon}")
        self.assertTrue(os.path.isfile(update_daemon), f"restored_update missing: {update_daemon}")

        # Verify Mach-O 64-bit ARM64 headers without execution
        for daemon_path in (erase_daemon, update_daemon):
            with open(daemon_path, "rb") as f:
                header = f.read(32)
            magic, cputype, cpusubtype = struct.unpack("<III", header[:12])
            self.assertEqual(magic, 0xfeedfacf, f"{daemon_path} is not Mach-O 64-bit")
            self.assertEqual(cputype, 0x0100000c, f"{daemon_path} is not ARM64")

        # Verify system directories exist in ramdisk
        for sub in ("bin", "sbin", "usr", "System", "private"):
            self.assertTrue(os.path.isdir(f"extracted/ipsw/ramdisk_erase/{sub}"))
            self.assertTrue(os.path.isdir(f"extracted/ipsw/ramdisk_update/{sub}"))

    def test_05_kernelcache_decompression(self):
        """Verify kernelcache decompression matches exact byte size, Adler32, and Mach-O header."""
        kc_path = "extracted/ipsw/kernel/kernelcache.macho"
        self.assertTrue(os.path.isfile(kc_path), f"Kernelcache missing: {kc_path}")

        with open(kc_path, "rb") as f:
            data = f.read()

        # Size check
        self.assertEqual(len(data), 44122112, f"Kernelcache size mismatch: {len(data)} != 44122112")

        # Adler-32 check
        calc_adler = zlib.adler32(data)
        self.assertEqual(calc_adler, 0xdfddbd11, f"Adler-32 mismatch: {hex(calc_adler)} != 0xdfddbd11")

        # Mach-O header check
        magic, cputype, cpusubtype, filetype = struct.unpack("<IIII", data[:16])
        self.assertEqual(magic, 0xfeedfacf, f"Mach-O magic mismatch: {hex(magic)}")
        self.assertEqual(cputype, 0x0100000c, f"CPUType is not ARM64: {hex(cputype)}")
        self.assertEqual(filetype, 2, f"Mach-O filetype is not MH_EXECUTE: {filetype}")

    def test_06_firmware_devicetree_and_bootloaders(self):
        """Verify DeviceTree and bootloader binary sizes and payloads."""
        dt_path = "extracted/ipsw/firmware/DeviceTree.bin"
        llb_path = "extracted/ipsw/firmware/LLB.bin"
        iboot_path = "extracted/ipsw/firmware/iBoot.bin"

        self.assertTrue(os.path.isfile(dt_path), "DeviceTree.bin missing")
        self.assertTrue(os.path.isfile(llb_path), "LLB.bin missing")
        self.assertTrue(os.path.isfile(iboot_path), "iBoot.bin missing")

        self.assertEqual(os.path.getsize(dt_path), 105596, "DeviceTree.bin size mismatch")
        self.assertEqual(os.path.getsize(llb_path), 205040, "LLB.bin size mismatch")
        self.assertEqual(os.path.getsize(iboot_path), 846064, "iBoot.bin size mismatch")

        # Check iBoot version string inside iBoot.bin
        with open(iboot_path, "rb") as f:
            iboot_data = f.read()
        self.assertIn(b"iBoot-13822.120.5", iboot_data, "iBoot version string missing")

    def test_07_firmware_images(self):
        """Verify restored PNG images are valid and have correct dimensions."""
        logo_path = "extracted/ipsw/firmware/applelogo.png"
        recm_path = "extracted/ipsw/firmware/recoverymode.png"

        self.assertTrue(os.path.isfile(logo_path), "applelogo.png missing")
        self.assertTrue(os.path.isfile(recm_path), "recoverymode.png missing")

        with Image.open(logo_path) as img:
            self.assertEqual(img.size, (108, 131), f"applelogo.png size mismatch: {img.size}")
            self.assertEqual(img.mode, "LA", f"applelogo.png mode mismatch: {img.mode}")

        with Image.open(recm_path) as img:
            self.assertEqual(img.size, (582, 154), f"recoverymode.png size mismatch: {img.size}")
            self.assertEqual(img.mode, "RGBA", f"recoverymode.png mode mismatch: {img.mode}")

    def test_08_extraction_ledger(self):
        """Verify reports/IPSW_EXTRACTION_LEDGER.md exists, is non-empty, and covers all components."""
        ledger_path = "reports/IPSW_EXTRACTION_LEDGER.md"
        self.assertTrue(os.path.isfile(ledger_path), "IPSW_EXTRACTION_LEDGER.md missing")
        self.assertGreater(os.path.getsize(ledger_path), 5000, "Ledger report too short")

        with open(ledger_path, "r") as f:
            ledger_text = f.read()

        self.assertIn("08bb7001565746699636a00c73ae35c0cba7536a15bafc01c900de26048d77c1", ledger_text)
        self.assertIn("5,269,474,064", ledger_text)
        self.assertIn("23L781", ledger_text)
        self.assertIn("AppleTV5,3", ledger_text)
        self.assertIn("restored_external", ledger_text)
        self.assertIn("restored_update", ledger_text)
        self.assertIn("kernelcache.macho", ledger_text)
        self.assertIn("DeviceTree.bin", ledger_text)
        self.assertIn("LLB.bin", ledger_text)
        self.assertIn("iBoot.bin", ledger_text)
        self.assertIn("applelogo.png", ledger_text)
        self.assertIn("recoverymode.png", ledger_text)
        self.assertIn("sep-firmware.j42d.RELEASE.im4p", ledger_text)
        self.assertIn("094-98312-089.dmg.aea", ledger_text)

    def test_09_extraction_ledger_veracity(self):
        """Programmatically audit all markdown table rows in reports/IPSW_EXTRACTION_LEDGER.md against disk."""
        ledger_path = "reports/IPSW_EXTRACTION_LEDGER.md"
        self.assertTrue(os.path.isfile(ledger_path), f"Ledger missing: {ledger_path}")

        with open(ledger_path, "r", encoding="utf-8") as f:
            text = f.read()

        row_pattern = re.compile(
            r"\|\s*`([^`]+)`\s*\|\s*([0-9,]+)\s*\|.*?`([0-9a-f]{64})`\s*\|",
            re.MULTILINE,
        )

        matches = row_pattern.findall(text)
        self.assertGreater(len(matches), 50, f"Expected >50 audited table rows, found {len(matches)}")

        mismatches = []
        for rel_path, size_str, recorded_hash in matches:
            expected_size = int(size_str.replace(",", ""))

            candidates = [
                os.path.join(self.PROJECT_ROOT, rel_path),
                os.path.join(self.PROJECT_ROOT, "extracted/ipsw/ramdisk_erase", rel_path),
                os.path.join(self.PROJECT_ROOT, "extracted/ipsw/ramdisk_update", rel_path),
                os.path.join(self.PROJECT_ROOT, "AppleTV5,3_26.6.1_23L781_Restore", rel_path),
            ]

            disk_file = None
            for cand in candidates:
                if os.path.exists(cand) and not os.path.isdir(cand):
                    disk_file = cand
                    break

            if disk_file is None:
                mismatches.append(f"MISSING FILE on disk: {rel_path}")
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

        self.assertEqual(mismatches, [], f"Ledger veracity audit failed with discrepancies: {mismatches}")


if __name__ == "__main__":
    unittest.main()
