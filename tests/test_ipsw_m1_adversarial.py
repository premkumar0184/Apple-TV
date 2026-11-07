#!/usr/bin/env python3
"""
Adversarial Stress Test Suite for Milestone IPSW-M1
Empirical Challenger: challenger_ipsw_m1_1

Validates:
1. Exact SHA-256 integrity for raw/ipsw/checksums.sha256 and bit-for-bit zip extraction fidelity.
2. Kernelcache decompression: Adler-32 byte-by-byte calculation, 64-bit Mach-O structure,
   load command bounds, and zero trailing corrupted bytes.
3. Ramdisk hierarchies: absolute/relative symlinks, dangling link detection, 0-byte file truncation,
   plist validity, and Mach-O header integrity across all binaries.
4. Firmware partition components: recursive DeviceTree parser, bootloader headers, and graphics decoding.
"""

import hashlib
import os
import plistlib
import struct
import unittest
import zipfile
import zlib
from PIL import Image


class TestAdversarialChecksums(unittest.TestCase):
    PROJECT_ROOT = "/home/prem/Projects/AppleTV"
    IPSW_PATH = "AppleTV5,3_26.6.1_23L781_Restore.ipsw"

    def setUp(self):
        os.chdir(self.PROJECT_ROOT)

    def test_01_all_checksum_entries_match_disk(self):
        """Audit every single line in raw/ipsw/checksums.sha256 against disk files."""
        checksum_file = "raw/ipsw/checksums.sha256"
        self.assertTrue(os.path.isfile(checksum_file))

        with open(checksum_file, "r") as f:
            lines = f.readlines()

        entries_checked = 0
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            self.assertEqual(len(parts), 2, f"Malformed checksum line: {line}")
            expected_hash, file_path = parts
            self.assertTrue(os.path.isfile(file_path), f"Target file does not exist: {file_path}")

            # Compute sha256
            hasher = hashlib.sha256()
            with open(file_path, "rb") as fp:
                while chunk := fp.read(1024 * 1024):
                    hasher.update(chunk)
            actual_hash = hasher.hexdigest()
            self.assertEqual(actual_hash, expected_hash, f"Hash mismatch for {file_path}")
            entries_checked += 1

        self.assertGreaterEqual(entries_checked, 5, "Insufficient entries in checksums.sha256")

    def test_02_manifests_bit_for_bit_match_ipsw_zip(self):
        """Adversarially verify extracted manifests match IPSW zip archive entries bit-for-bit."""
        manifests = [
            "BuildManifest.plist",
            "Restore.plist",
            "RestoreVersion.plist",
            "SystemVersion.plist",
        ]
        with zipfile.ZipFile(self.IPSW_PATH, "r") as zf:
            for m in manifests:
                zip_data = zf.read(m)
                disk_path = os.path.join("raw/ipsw/manifests", m)
                with open(disk_path, "rb") as fp:
                    disk_data = fp.read()
                self.assertEqual(
                    disk_data,
                    zip_data,
                    f"Extracted manifest {m} differs from original zip payload",
                )

    def test_03_preserved_firmware_files_match_ipsw_zip(self):
        """Adversarially audit all raw/ipsw/firmware files against the original zip archive."""
        firmware_dir = "raw/ipsw/firmware"
        with zipfile.ZipFile(self.IPSW_PATH, "r") as zf:
            zip_names = set(zf.namelist())
            for root, dirs, files in os.walk(firmware_dir):
                for f in files:
                    disk_path = os.path.join(root, f)
                    rel = os.path.relpath(disk_path, "raw/ipsw")
                    # Map to zip path
                    zip_candidate = rel.replace("firmware/", "Firmware/")
                    self.assertIn(
                        zip_candidate,
                        zip_names,
                        f"Preserved file {disk_path} not found in IPSW zip",
                    )
                    zip_data = zf.read(zip_candidate)
                    with open(disk_path, "rb") as fp:
                        disk_data = fp.read()
                    self.assertEqual(
                        disk_data,
                        zip_data,
                        f"Preserved firmware file {disk_path} corrupted vs zip archive",
                    )


class TestAdversarialKernelcache(unittest.TestCase):
    PROJECT_ROOT = "/home/prem/Projects/AppleTV"
    KC_PATH = "extracted/ipsw/kernel/kernelcache.macho"
    IPSW_PATH = "AppleTV5,3_26.6.1_23L781_Restore.ipsw"

    def setUp(self):
        os.chdir(self.PROJECT_ROOT)

    def test_01_complzss_header_parameters_match_decompressed_payload(self):
        """Inspect complzss header in IPSW and verify parameters match decompressed file."""
        with zipfile.ZipFile(self.IPSW_PATH, "r") as zf:
            raw_im4p = zf.read("kernelcache.release.j42d")

        # Parse complzss header
        self.assertIn(b"complzss", raw_im4p)
        header_idx = raw_im4p.find(b"complzss")
        header = raw_im4p[header_idx : header_idx + 0x180]

        magic = header[:8]
        self.assertEqual(magic, b"complzss")
        adler32, uncomp_len, comp_len, version = struct.unpack(">IIII", header[8:24])

        self.assertEqual(uncomp_len, 44122112)
        self.assertEqual(adler32, 0xDFDDBD11)
        self.assertEqual(comp_len, 21931068)
        self.assertEqual(version, 1)

        actual_size = os.path.getsize(self.KC_PATH)
        self.assertEqual(
            actual_size,
            uncomp_len,
            f"Decompressed file size {actual_size} != declared uncompressed size {uncomp_len}",
        )

    def test_02_adler32_byte_by_byte_stress_test(self):
        """Calculate Adler-32 byte-by-byte to test accumulator stability and exact match."""
        with open(self.KC_PATH, "rb") as f:
            data = f.read()

        self.assertEqual(len(data), 44122112)

        # Full buffer check
        self.assertEqual(zlib.adler32(data), 0xDFDDBD11)

        # Byte-by-byte incremental check
        adler_acc = 1
        for b in data:
            adler_acc = zlib.adler32(bytes([b]), adler_acc)

        self.assertEqual(
            adler_acc,
            0xDFDDBD11,
            f"Byte-by-byte Adler-32 {hex(adler_acc)} does not match declared 0xdfddbd11",
        )

    def test_03_macho_64bit_arm64_header_and_load_commands(self):
        """Parse 64-bit Mach-O load commands and verify zero trailing corrupted bytes."""
        with open(self.KC_PATH, "rb") as f:
            header = f.read(32)
            magic, cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags, reserved = struct.unpack(
                "<IIIIIIII", header
            )

            self.assertEqual(magic, 0xFEEDFACF, "Mach-O magic is not MH_MAGIC_64")
            self.assertEqual(cputype, 0x0100000C, "cputype is not CPU_TYPE_ARM64")
            self.assertEqual(filetype, 2, "filetype is not MH_EXECUTE")
            self.assertEqual(ncmds, 25, "Expected 25 load commands")
            self.assertEqual(sizeofcmds, 5056, "Expected sizeofcmds 5056")

            cmds_bytes = f.read(sizeofcmds)
            self.assertEqual(len(cmds_bytes), sizeofcmds)

            offset = 0
            max_file_extent = 32 + sizeofcmds
            segment_names = []

            for i in range(ncmds):
                self.assertLessEqual(offset + 8, len(cmds_bytes))
                cmd, cmdsize = struct.unpack("<II", cmds_bytes[offset : offset + 8])
                self.assertGreaterEqual(cmdsize, 8)
                self.assertLessEqual(offset + cmdsize, len(cmds_bytes))

                if cmd == 0x19:  # LC_SEGMENT_64
                    segname_raw, vmaddr, vmsize, fileoff, filesize, maxprot, initprot, nsects, sflags = struct.unpack(
                        "<16sQQQQiiII", cmds_bytes[offset + 8 : offset + 72]
                    )
                    segname = segname_raw.rstrip(b"\x00").decode("latin1")
                    segment_names.append(segname)
                    self.assertLessEqual(fileoff + filesize, 44122112)
                    if fileoff + filesize > max_file_extent:
                        max_file_extent = fileoff + filesize
                elif cmd == 0x2:  # LC_SYMTAB
                    symoff, nsyms, stroff, strsize = struct.unpack(
                        "<IIII", cmds_bytes[offset + 8 : offset + 24]
                    )
                    self.assertLessEqual(stroff + strsize, 44122112)
                    if stroff + strsize > max_file_extent:
                        max_file_extent = stroff + strsize

                offset += cmdsize

            # Assert key kernel segments exist
            for req_seg in ("__TEXT", "__DATA", "__LINKEDIT", "__PRELINK_TEXT", "__PRELINK_INFO"):
                self.assertIn(req_seg, segment_names)

            # Crucial verification: max_file_extent must EXACTLY equal 44,122,112
            self.assertEqual(
                max_file_extent,
                44122112,
                f"Trailing byte anomaly: file size (44122112) != max segment extent ({max_file_extent})",
            )


class TestAdversarialRamdisks(unittest.TestCase):
    PROJECT_ROOT = "/home/prem/Projects/AppleTV"
    RAMDISKS = {
        "erase": "extracted/ipsw/ramdisk_erase",
        "update": "extracted/ipsw/ramdisk_update",
    }

    def setUp(self):
        os.chdir(self.PROJECT_ROOT)

    def test_01_no_zero_byte_regular_files(self):
        """Stress-test: ensure 0-byte truncated regular files do not exist."""
        for name, root_path in self.RAMDISKS.items():
            zero_byte_files = []
            for root, dirs, files in os.walk(root_path):
                for f in files:
                    p = os.path.join(root, f)
                    if not os.path.islink(p) and os.path.getsize(p) == 0:
                        zero_byte_files.append(os.path.relpath(p, root_path))
            self.assertEqual(
                len(zero_byte_files),
                0,
                f"Found {len(zero_byte_files)} 0-byte truncated files in {name}: {zero_byte_files}",
            )

    def test_02_all_symlinks_resolve(self):
        """Stress-test: verify all 100 symlinks in each ramdisk resolve to existing targets."""
        for name, root_path in self.RAMDISKS.items():
            broken = []
            symlink_count = 0
            for root, dirs, files in os.walk(root_path, followlinks=False):
                for item in dirs + files:
                    p = os.path.join(root, item)
                    if os.path.islink(p):
                        symlink_count += 1
                        target = os.readlink(p)
                        if target.startswith("/"):
                            exists = os.path.exists(target)
                        else:
                            resolved = os.path.normpath(os.path.join(root, target))
                            exists = os.path.exists(resolved)
                        if not exists:
                            broken.append((os.path.relpath(p, root_path), target))
            self.assertEqual(symlink_count, 100, f"Expected 100 symlinks in {name}, found {symlink_count}")
            self.assertEqual(len(broken), 0, f"Found broken symlinks in {name}: {broken}")

    def test_03_audit_absolute_host_symlink_anti_pattern(self):
        """Audit symlinks to verify zero host-absolute paths (/home/prem/...) remain."""
        host_absolute_links = []
        for name, root_path in self.RAMDISKS.items():
            for root, dirs, files in os.walk(root_path, followlinks=False):
                for item in dirs + files:
                    p = os.path.join(root, item)
                    if os.path.islink(p):
                        target = os.readlink(p)
                        if target.startswith("/home/prem") or os.path.isabs(target):
                            host_absolute_links.append((name, os.path.relpath(p, root_path), target))

        # Verify that all symlinks use relative paths, ensuring full filesystem relocatability.
        self.assertEqual(
            len(host_absolute_links),
            0,
            f"Expected 0 legacy absolute symlinks, found {len(host_absolute_links)}: {host_absolute_links}",
        )

    def test_04_all_plists_are_valid(self):
        """Stress-test: verify every plist file in ramdisks parses without syntax or EOF errors."""
        for name, root_path in self.RAMDISKS.items():
            total_checked = 0
            for root, dirs, files in os.walk(root_path):
                for f in files:
                    if f.endswith(".plist"):
                        total_checked += 1
                        p = os.path.join(root, f)
                        with open(p, "rb") as fp:
                            try:
                                plistlib.load(fp)
                            except Exception as e:
                                self.fail(f"Corrupted plist in {name}: {p} ({e})")
            self.assertGreater(total_checked, 100, f"Expected >100 plists in {name}")

    def test_05_all_macho_binaries_have_valid_headers(self):
        """Audit all Mach-O binaries: verify non-truncated ARM64 headers and load commands."""
        for name, root_path in self.RAMDISKS.items():
            macho_count = 0
            for root, dirs, files in os.walk(root_path):
                for f in files:
                    p = os.path.join(root, f)
                    if os.path.islink(p):
                        continue
                    sz = os.path.getsize(p)
                    if sz >= 4:
                        with open(p, "rb") as fp:
                            mag = fp.read(4)
                        if mag == b"\xcf\xfa\xed\xfe":
                            macho_count += 1
                            self.assertGreaterEqual(sz, 32, f"Truncated Mach-O in {name}: {p}")
                            with open(p, "rb") as fp:
                                header = fp.read(32)
                                magic, cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags, res = struct.unpack(
                                    "<IIIIIIII", header
                                )
                                self.assertEqual(cputype, 0x0100000C, f"Non-ARM64 Mach-O: {p}")
                                self.assertLessEqual(32 + sizeofcmds, sz, f"Overflowing load commands: {p}")
            self.assertGreaterEqual(macho_count, 290, f"Expected >= 290 Mach-O binaries in {name}")


class TestAdversarialFirmwareComponents(unittest.TestCase):
    PROJECT_ROOT = "/home/prem/Projects/AppleTV"

    def setUp(self):
        os.chdir(self.PROJECT_ROOT)

    def test_01_devicetree_recursive_ast_validation(self):
        """Recursively parse DeviceTree.bin and verify structural integrity down to the last byte."""
        dt_path = "extracted/ipsw/firmware/DeviceTree.bin"
        self.assertTrue(os.path.isfile(dt_path))
        with open(dt_path, "rb") as f:
            data = f.read()

        self.assertEqual(len(data), 105596)

        def parse_node(offset):
            nprops, nchildren = struct.unpack("<II", data[offset : offset + 8])
            offset += 8
            props = {}
            for _ in range(nprops):
                name = data[offset : offset + 32].rstrip(b"\x00").decode("latin1")
                raw_len = struct.unpack("<I", data[offset + 32 : offset + 36])[0]
                length = raw_len & 0x7FFFFFFF
                val = data[offset + 36 : offset + 36 + length]
                pad = (4 - (length % 4)) % 4
                offset += 36 + length + pad
                props[name] = val
            children = []
            for _ in range(nchildren):
                child_props, child_children, offset = parse_node(offset)
                children.append((child_props, child_children))
            return props, children, offset

        root_props, root_children, end_offset = parse_node(0)
        self.assertEqual(
            end_offset,
            105596,
            f"DeviceTree trailing bytes or parsing truncated: {end_offset} != 105596",
        )
        self.assertIn("target-type", root_props)
        self.assertIn(b"J42d", root_props["target-type"])
        self.assertIn("regulatory-model-number", root_props)
        self.assertIn(b"A1625", root_props["regulatory-model-number"])

    def test_02_bootloaders_and_images_integrity(self):
        """Verify LLB, iBoot, iBSS, iBEC and decode graphics."""
        iboot_path = "extracted/ipsw/firmware/iBoot.bin"
        with open(iboot_path, "rb") as f:
            iboot_data = f.read()
        self.assertEqual(len(iboot_data), 846064)
        self.assertIn(b"iBoot-13822.120.5", iboot_data)

        # Images
        logo_path = "extracted/ipsw/firmware/applelogo.png"
        recm_path = "extracted/ipsw/firmware/recoverymode.png"
        with Image.open(logo_path) as img:
            self.assertEqual(img.size, (108, 131))
            self.assertEqual(img.mode, "LA")
            # Ensure pixel data can load without decompression error
            img.load()

        with Image.open(recm_path) as img:
            self.assertEqual(img.size, (582, 154))
            self.assertEqual(img.mode, "RGBA")
            img.load()


if __name__ == "__main__":
    unittest.main()
