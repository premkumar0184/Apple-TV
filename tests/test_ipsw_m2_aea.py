import os
import unittest
import struct
import hashlib
import base64
import lzfse
from cryptography.hazmat.primitives.serialization import load_pem_private_key, Encoding, PublicFormat
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class TestIPSW_M2_AEA(unittest.TestCase):
    """Integrity and cryptographic test suite for Milestone IPSW-M2."""

    PROJECT_ROOT = "/home/prem/Projects/AppleTV"
    IPSW_DIR = os.path.join(PROJECT_ROOT, "AppleTV5,3_26.6.1_23L781_Restore")
    RAW_DIR = os.path.join(PROJECT_ROOT, "raw/ipsw")
    REPORT_PATH = os.path.join(PROJECT_ROOT, "analysis/ipsw/AEA_CRYPTOGRAPHIC_REPORT.md")

    def test_01_report_existence_and_sections(self):
        """Verify AEA_CRYPTOGRAPHIC_REPORT.md exists, is non-empty, and has all key sections."""
        self.assertTrue(os.path.exists(self.REPORT_PATH), f"Missing report: {self.REPORT_PATH}")
        with open(self.REPORT_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertGreater(len(content), 4000, "Report is too short")
        required_headers = [
            "Executive Summary",
            "AEA Container Anatomy",
            "Cryptographic Key Recovery via RFC 9180 HPKE",
            "Root Header Decryption",
            "Canonical RootFS Mtree Manifest Forensics",
            "Cryptographic Boundaries & Comparative Analysis",
            "Verification Method",
        ]
        for header in required_headers:
            self.assertIn(header, content, f"Report missing section header: {header}")

    def test_02_aea_container_headers(self):
        """Verify AEA container headers: AEA1 magic, Profile 1, and auth data length."""
        rootfs_aea = os.path.join(self.IPSW_DIR, "094-98312-089.dmg.aea")
        recovery_aea = os.path.join(self.IPSW_DIR, "094-98220-089.dmg.aea")
        self.assertTrue(os.path.exists(rootfs_aea))
        self.assertTrue(os.path.exists(recovery_aea))

        # RootFS
        with open(rootfs_aea, "rb") as f:
            magic = f.read(4)
            profile = struct.unpack("<I", f.read(4))[0]
            auth_len = struct.unpack("<I", f.read(4))[0]
        self.assertEqual(magic, b"AEA1")
        self.assertEqual(profile, 1)
        self.assertEqual(auth_len, 2168)

        # Recovery
        with open(recovery_aea, "rb") as f:
            magic = f.read(4)
            profile = struct.unpack("<I", f.read(4))[0]
            auth_len = struct.unpack("<I", f.read(4))[0]
        self.assertEqual(magic, b"AEA1")
        self.assertEqual(profile, 1)
        self.assertEqual(auth_len, 2200)

    def test_03_fcs_key_id_verification(self):
        """Verify the Apple FCS P-256 public key hash matches the key identifier in the AEA metadata."""
        pem_data = b"""-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgaDR+I1N0urD/PH23
IMsnlc9ROZRz+H2kOk7Eubgr9M6hRANCAARJQuSRYsvcRwFFboVjOT5wUwTDr7RV
mXMFejowBG3kMGDe5+YHdstsm7vkEYUs24wl8pRmdLtPNHavjxS/YPok
-----END PRIVATE KEY-----"""
        sk = load_pem_private_key(pem_data, None)
        pk_bytes = sk.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
        key_id = base64.urlsafe_b64encode(hashlib.sha256(pk_bytes).digest()).decode("utf-8")
        self.assertEqual(key_id, "EqKp4rUE1uMIIEqnfHnqfscN_VFy_qgyE3Vus8_KQhE=")

    def test_04_aea_symmetric_key_unwrapping(self):
        """Verify mathematical unwrapping of the RootFS symmetric archive key."""
        key = bytes.fromhex("ca290007d5f02323902a6dd5b1d47f1fdca2217eeea1440e28bc06c92ec8d464")
        nonce = bytes.fromhex("60f73bd985fb09418e3a0f30")
        wrapped = base64.b64decode("T8z+k9S92HgNPwaMRKsALAgbRIfNl4O3+E+qawTkGvxVop8b9y7FhZjATeZgQlo0")

        aesgcm = AESGCM(key)
        plaintext_key = aesgcm.decrypt(nonce, wrapped, b"")
        self.assertEqual(
            plaintext_key.hex(),
            "ca0d1a3eb45cdb15b15babced612a5d37914299f5d5d141d488ddccb40cda496"
        )

    def test_05_mtree_pbze_stream_decompression(self):
        """Verify that the 21 pbze chunks in RootFS mtree decompress to 87,516,522 bytes."""
        mtree_path = os.path.join(self.RAW_DIR, "firmware/094-98312-089.dmg.aea.mtree")
        self.assertTrue(os.path.exists(mtree_path))

        with open(mtree_path, "rb") as f:
            idx = f.read(128).find(b"pbze")
            self.assertNotEqual(idx, -1)
            f.seek(idx + 4)
            max_chunk = struct.unpack(">Q", f.read(8))[0]
            self.assertEqual(max_chunk, 4194304)  # 4 MiB chunks

            chunk_count = 0
            total_uncomp = 0
            while True:
                hdr = f.read(16)
                if len(hdr) < 16:
                    break
                uncomp, comp = struct.unpack(">2Q", hdr)
                if uncomp == 0 or comp == 0:
                    break
                chunk_data = f.read(comp)
                dec = lzfse.decompress(chunk_data)
                self.assertEqual(len(dec), uncomp)
                total_uncomp += uncomp
                chunk_count += 1

        self.assertEqual(chunk_count, 21)
        self.assertEqual(total_uncomp, 87516522)

    def test_06_mtree_core_applications(self):
        """Verify the decoded mtree.txt contains core tvOS system applications."""
        mtree_path = os.path.join(self.RAW_DIR, "firmware/094-98312-089.dmg.aea.mtree")
        stream = bytearray()
        with open(mtree_path, "rb") as f:
            idx = f.read(128).find(b"pbze")
            f.seek(idx + 4)
            max_chunk = struct.unpack(">Q", f.read(8))[0]
            while True:
                hdr = f.read(16)
                if len(hdr) < 16:
                    break
                uncomp, comp = struct.unpack(">2Q", hdr)
                if uncomp == 0 or comp == 0:
                    break
                chunk_data = f.read(comp)
                stream.extend(lzfse.decompress(chunk_data))

        pos = stream.find(b"PATP\t\x00mtree.txt")
        self.assertNotEqual(pos, -1)
        dat_pos = stream.find(b"DAT", pos)
        self.assertNotEqual(dat_pos, -1)

        mtree_text = stream[dat_pos+8:].decode("utf-8", errors="replace")

        # Verify key system apps
        key_apps = [
            "PineBoard.app",
            "HeadBoard.app",
            "PreBoard.app",
            "PosterBoard.app",
            "TVSystemUIService.app",
            "TVMusic.app",
            "FaceTime.app",
            "Sing.app",
        ]
        for app in key_apps:
            self.assertIn(f"./Applications/{app}", mtree_text, f"Missing system application: {app}")

if __name__ == "__main__":
    unittest.main()
