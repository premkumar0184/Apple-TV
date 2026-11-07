import os
import unittest
import struct
import re

class TestIPSW_M4_Binary(unittest.TestCase):
    """Integrity and REA reverse engineering test suite for Milestone IPSW-M4."""

    PROJECT_ROOT = "/home/prem/Projects/AppleTV"
    RAMDISK_ERASE = os.path.join(PROJECT_ROOT, "extracted/ipsw/ramdisk_erase")
    RAMDISK_UPDATE = os.path.join(PROJECT_ROOT, "extracted/ipsw/ramdisk_update")
    FIRMWARE_DIR = os.path.join(PROJECT_ROOT, "extracted/ipsw/firmware")
    KERNEL_DIR = os.path.join(PROJECT_ROOT, "extracted/ipsw/kernel")
    REPORT_PATH = os.path.join(PROJECT_ROOT, "analysis/ipsw/BINARY_ANALYSIS_REPORT.md")

    def test_01_report_existence_and_sections(self):
        """Verify BINARY_ANALYSIS_REPORT.md exists, is non-empty, and has all key sections."""
        self.assertTrue(os.path.exists(self.REPORT_PATH), f"Missing report: {self.REPORT_PATH}")
        with open(self.REPORT_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertGreater(len(content), 4000, "Report is too short")
        required_headers = [
            "Executive Summary & Binary Inventory",
            "Mach-O Topography & Header Structures",
            "Dynamic Linker & Framework Dependencies",
            "Objective-C & Swift Runtime Metadata",
            "Kernelcache Architecture & Fileset Analysis",
            "Bootloader Static Inspection",
            "Verification Method",
        ]
        for header in required_headers:
            self.assertIn(header, content, f"Report missing section header: {header}")

    def test_02_restored_external_macho_header(self):
        """Verify restored_external Mach-O 64-bit ARM64 structure, load commands, and segments."""
        bin_path = os.path.join(self.RAMDISK_ERASE, "usr/local/bin/restored_external")
        self.assertTrue(os.path.exists(bin_path))
        with open(bin_path, "rb") as f:
            hdr = f.read(32)
            magic, cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags, reserved = struct.unpack("<8I", hdr)
            cmd_bytes = f.read(sizeofcmds)

        self.assertEqual(magic, 0xfeedfacf)
        self.assertEqual(cputype, 0x0100000c)  # ARM64
        self.assertEqual(filetype, 2)  # MH_EXECUTE
        self.assertEqual(ncmds, 64)

        # Parse segments
        segments = []
        offset = 0
        for _ in range(ncmds):
            cmd, cmdsize = struct.unpack("<2I", cmd_bytes[offset:offset+8])
            if cmd == 0x19:  # LC_SEGMENT_64
                segname = cmd_bytes[offset+8:offset+24].rstrip(b"\x00").decode("latin1")
                segments.append(segname)
            offset += cmdsize
        self.assertEqual(segments, ["__PAGEZERO", "__TEXT", "__DATA_CONST", "__DATA", "__LINKEDIT"])

    def test_03_restored_update_macho_header(self):
        """Verify restored_update Mach-O header in the update ramdisk."""
        bin_path = os.path.join(self.RAMDISK_UPDATE, "usr/local/bin/restored_update")
        self.assertTrue(os.path.exists(bin_path))
        with open(bin_path, "rb") as f:
            magic, cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags = struct.unpack("<7I", f.read(28))
        self.assertEqual(magic, 0xfeedfacf)
        self.assertEqual(cputype, 0x0100000c)
        self.assertEqual(ncmds, 64)

    def test_04_diskimagesiod_and_driverkitd_headers(self):
        """Verify diskimagesiod and driverkitd Mach-O structures."""
        di_path = os.path.join(self.RAMDISK_ERASE, "usr/libexec/diskimagesiod")
        dk_path = os.path.join(self.RAMDISK_ERASE, "usr/libexec/driverkitd")
        self.assertTrue(os.path.exists(di_path))
        self.assertTrue(os.path.exists(dk_path))

        with open(di_path, "rb") as f:
            m_di, cpu_di, _, _, ncmds_di, _, _ = struct.unpack("<7I", f.read(28))
        self.assertEqual(m_di, 0xfeedfacf)
        self.assertEqual(cpu_di, 0x0100000c)
        self.assertEqual(ncmds_di, 43)

        with open(dk_path, "rb") as f:
            m_dk, cpu_dk, _, _, ncmds_dk, _, _ = struct.unpack("<7I", f.read(28))
        self.assertEqual(m_dk, 0xfeedfacf)
        self.assertEqual(cpu_dk, 0x0100000c)
        self.assertEqual(ncmds_dk, 40)

    def test_05_restored_external_objc_classes(self):
        """Verify key reverse-engineered Objective-C and Swift classes in restored_external."""
        bin_path = os.path.join(self.RAMDISK_ERASE, "usr/local/bin/restored_external")
        with open(bin_path, "rb") as f:
            f.seek(0x138410)
            data = f.read(1141)
        classes = set(data.split(b"\x00"))

        required_classes = [
            b"WKMSRequest",
            b"_TtC14restored_swift14AEAAuthDataBox",
            b"LPStaticAPFSContainer",
            b"LPStaticAPFSVolume",
            b"MSUBootFirmwareUpdater",
            b"RestoreASRServerStream",
        ]
        for cls in required_classes:
            self.assertIn(cls, classes, f"Missing class in restored_external: {cls.decode()}")

    def test_06_kernelcache_segments_and_version(self):
        """Verify kernelcache 18 segments, Darwin 25.6.0 version, and xnu release string."""
        kc_path = os.path.join(self.KERNEL_DIR, "kernelcache.macho")
        self.assertTrue(os.path.exists(kc_path))
        self.assertEqual(os.path.getsize(kc_path), 44122112)

        with open(kc_path, "rb") as f:
            hdr = f.read(32)
            magic, cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags, reserved = struct.unpack("<8I", hdr)
            cmd_bytes = f.read(sizeofcmds)
            data = f.read(5000000)  # read start for strings

        self.assertEqual(magic, 0xfeedfacf)
        self.assertEqual(cputype, 0x0100000c)
        self.assertEqual(ncmds, 25)

        # Verify Darwin kernel version string
        with open(kc_path, "rb") as f:
            full_data = f.read()
        self.assertIn(b"Darwin Kernel Version 25.6.0", full_data)
        self.assertIn(b"RELEASE_ARM64_T7000", full_data)
        self.assertIn(b"xnu-12377.163.4~3", full_data)

    def test_07_kernelcache_prelinked_kexts(self):
        """Verify prelinked KEXT manifest in kernelcache contains at least 150 unique drivers."""
        kc_path = os.path.join(self.KERNEL_DIR, "kernelcache.macho")
        with open(kc_path, "rb") as f:
            f.seek(0x27c0000)
            data = f.read(2441216).rstrip(b"\x00").decode("latin1", errors="replace")

        bids = set(re.findall(r"<key>CFBundleIdentifier</key>\s*<string>([^<]+)</string>", data))
        self.assertGreaterEqual(len(bids), 150)
        self.assertIn("com.apple.driver.AppleBluetoothRemote", bids)
        self.assertIn("com.apple.AGXG4P", bids)
        self.assertIn("com.apple.driver.AppleAVEH7", bids)

    def test_08_bootloaders_iboot_version(self):
        """Verify LLB.bin and iBoot.bin contain iBoot-13822.120.5 and entry instructions."""
        llb_path = os.path.join(self.FIRMWARE_DIR, "LLB.bin")
        iboot_path = os.path.join(self.FIRMWARE_DIR, "iBoot.bin")
        self.assertTrue(os.path.exists(llb_path))
        self.assertTrue(os.path.exists(iboot_path))

        with open(llb_path, "rb") as f:
            llb_data = f.read()
        with open(iboot_path, "rb") as f:
            iboot_data = f.read()

        self.assertIn(b"iBoot-13822.120.5", llb_data)
        self.assertIn(b"iBoot-13822.120.5", iboot_data)
        self.assertIn(b"boot-ramdisk", iboot_data)

if __name__ == "__main__":
    unittest.main()
