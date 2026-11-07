#!/usr/bin/env python3
"""
Artifact Integrity and Forensic Verification Test Suite
Milestone 1 - Challenger 1 (challenger_m1_1)

Validates:
- Mach-O 64-bit ARM64 structure and segment completeness (no truncated binaries)
- BOMStore asset catalog integrity (.car files)
- dyld_shared_cache_arm64 mapping and slide info
- Forensic ledger veracity (EXTRACTION_LEDGER.md) against filesystem reality
"""

import unittest
import os
import struct
import hashlib
import re


class TestArtifactIntegrity(unittest.TestCase):

    def _parse_macho(self, path):
        self.assertTrue(os.path.isfile(path), f"Mach-O file does not exist: {path}")
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            data = f.read()

        self.assertGreaterEqual(len(data), 32, f"Mach-O file {path} is smaller than 32-byte header")
        magic = struct.unpack("<I", data[:4])[0]
        self.assertEqual(magic, 0xfeedfacf, f"File {path} is not Mach-O 64-bit ARM64 (magic: {hex(magic)})")

        cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags, reserved = struct.unpack("<IIIIIII", data[4:32])
        # CPU_TYPE_ARM64 = 0x0100000c (16777228)
        self.assertEqual(cputype, 0x0100000c, f"Binary {path} cputype is not ARM64 ({cputype})")

        offset = 32
        max_extent = 32 + sizeofcmds

        for i in range(ncmds):
            self.assertLessEqual(offset + 8, len(data), f"Truncated load command header at offset {offset}")
            cmd, cmdsize = struct.unpack("<II", data[offset:offset+8])
            cmd_data = data[offset:offset+cmdsize]
            if cmd == 0x19: # LC_SEGMENT_64
                segname = cmd_data[8:24].rstrip(b"\x00").decode("ascii", errors="replace")
                vmaddr, vmsize, fileoff, filesize = struct.unpack("<QQQQ", cmd_data[24:56])
                max_extent = max(max_extent, fileoff + filesize)
            elif cmd in (0x1d, 0x1e, 0x26, 0x29, 0x2b, 0x2e):
                dataoff, datasize = struct.unpack("<II", cmd_data[8:16])
                max_extent = max(max_extent, dataoff + datasize)
            offset += cmdsize

        self.assertEqual(size, max_extent, f"Mach-O {path} size ({size}) does not match expected extent ({max_extent})")
        return {"size": size, "ncmds": ncmds, "max_extent": max_extent}

    def test_pineboard_binary(self):
        res = self._parse_macho("extracted/rootfs/Applications/PineBoard.app/PineBoard")
        self.assertEqual(res["size"], 3645792)

    def test_headboard_binary(self):
        res = self._parse_macho("extracted/rootfs/Applications/HeadBoard.app/HeadBoard")
        self.assertEqual(res["size"], 1319504)

    def test_preboard_binary(self):
        res = self._parse_macho("extracted/rootfs/Applications/PreBoard.app/PreBoard")
        self.assertEqual(res["size"], 111008)

    def test_appstore_binary(self):
        res = self._parse_macho("extracted/rootfs/Applications/AppStore.app/AppStore")
        self.assertEqual(res["size"], 2829904)

    def test_tvmusic_binary(self):
        """Verify TVMusic binary presence and validity."""
        path = "extracted/rootfs/Applications/TVMusic.app/TVMusic"
        # TVMusic is an expected target per challenge instructions
        self.assertTrue(os.path.isfile(path), f"TVMusic binary is MISSING: {path}")
        res = self._parse_macho(path)
        self.assertEqual(res["size"], 1524400)

    def test_tvmusic_topshelf_binary(self):
        """Verify TVMusicTopShelfExtension binary presence and validity."""
        path = "extracted/rootfs/Applications/TVMusic.app/PlugIns/TVMusicTopShelfExtension.appex/TVMusicTopShelfExtension"
        self.assertTrue(os.path.isfile(path), f"TVMusicTopShelfExtension binary is MISSING: {path}")
        res = self._parse_macho(path)
        self.assertEqual(res["size"], 139328)

    def test_asset_catalogs_bomstore(self):
        """Verify all extracted .car files are valid BOMStore databases."""
        car_files = [
            "extracted/rootfs/Applications/AppStore.app/Assets.car",
            "extracted/rootfs/Applications/AppleTV.app/Assets.car",
            "extracted/rootfs/Applications/HeadBoard.app/Assets.car",
            "extracted/rootfs/Applications/PineBoard.app/Assets.car",
            "extracted/rootfs/Applications/PreBoard.app/Assets.car",
            "extracted/rootfs/Applications/Setup.app/Assets.car",
            "extracted/rootfs/Applications/TVMusic.app/Assets.car",
            "extracted/rootfs/Applications/TVPhotos.app/Assets.car",
            "extracted/rootfs/Applications/TVSearch.app/Assets.car",
            "extracted/rootfs/System/Library/CoreServices/CoreGlyphs.bundle/Assets.car",
        ]
        for car in car_files:
            self.assertTrue(os.path.isfile(car), f"Asset catalog missing: {car}")
            with open(car, "rb") as f:
                magic = f.read(8)
                self.assertEqual(magic, b"BOMStore", f"{car} invalid magic: {magic}")
                version, num_blocks, index_offset, index_length = struct.unpack(">IIII", f.read(16))
                size = os.path.getsize(car)
                self.assertLessEqual(index_offset + index_length, size, f"{car} index out of bounds")
                f.seek(0)
                content = f.read()
                self.assertIn(b"CARHEADER", content, f"{car} missing CARHEADER tree")
                self.assertIn(b"RENDITIONS", content, f"{car} missing RENDITIONS tree")

    def test_dyld_shared_cache(self):
        """Verify dyld_shared_cache_arm64 mapping and slide info structures."""
        path = "extracted/dyld_cache/dyld_shared_cache_arm64"
        self.assertTrue(os.path.isfile(path), f"dyld shared cache missing: {path}")
        size = os.path.getsize(path)
        self.assertEqual(size, 1086013440)

        with open(path, "rb") as f:
            hdr = f.read(256)
            magic = hdr[:16]
            self.assertTrue(magic.startswith(b"dyld_v1   arm64"), f"Invalid dyld magic: {magic}")

            mapping_offset, mapping_count = struct.unpack("<II", hdr[16:24])
            images_offset, images_count = struct.unpack("<II", hdr[24:32])
            slide_info_offset, slide_info_size = struct.unpack("<QQ", hdr[56:72])

            self.assertEqual(mapping_count, 3)
            self.assertGreater(images_count, 1000)

            # Check mappings
            f.seek(mapping_offset)
            for i in range(mapping_count):
                addr, msize, file_off, max_p, init_p = struct.unpack("<QQQII", f.read(32))
                self.assertLessEqual(file_off + msize, size, f"Mapping {i} out of bounds")

            # Check slide info v2
            self.assertGreater(slide_info_offset, 0)
            self.assertGreater(slide_info_size, 0)
            f.seek(slide_info_offset)
            slide_version = struct.unpack("<I", f.read(4))[0]
            self.assertEqual(slide_version, 2, f"Expected slide info version 2, got {slide_version}")

    def test_extraction_ledger_veracity(self):
        """Audit EXTRACTION_LEDGER.md table entries against physical files on disk."""
        ledger_path = "reports/EXTRACTION_LEDGER.md"
        self.assertTrue(os.path.isfile(ledger_path), f"Ledger missing: {ledger_path}")

        with open(ledger_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Parse markdown tables containing `path`, `size`, `hash`
        # Rows look like: | `path` | size | format | `sha256` |
        # or | `path` | size | `sha256` |
        table_rows = re.findall(r"\|\s*`([^`]+)`\s*\|\s*([0-9,]+)\s*\|(?:[^|]+\|)?\s*`([0-9a-f]{64})`\s*\|", text)
        self.assertGreater(len(table_rows), 20, "Ledger contains too few audited entries")

        mismatches = []
        for file_path, size_str, recorded_hash in table_rows:
            size_expected = int(size_str.replace(",", ""))
            if not os.path.exists(file_path):
                mismatches.append(f"MISSING FILE: {file_path}")
                continue

            actual_size = os.path.getsize(file_path)
            if actual_size != size_expected:
                mismatches.append(f"SIZE MISMATCH for {file_path}: actual {actual_size} vs recorded {size_expected}")
                continue

            with open(file_path, "rb") as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()
            if actual_hash != recorded_hash:
                mismatches.append(f"HASH MISMATCH for {file_path}: actual {actual_hash} vs recorded {recorded_hash}")

        self.assertEqual(mismatches, [], f"Ledger audit discovered mismatches: {mismatches}")


if __name__ == "__main__":
    unittest.main()
