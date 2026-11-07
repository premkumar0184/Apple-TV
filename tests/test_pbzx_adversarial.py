#!/usr/bin/env python3
"""
Adversarial Stress Test Suite for PBZX Streaming Extractor and Buffer Logic
Milestone 1 - Challenger 1 (challenger_m1_1)
"""

import unittest
import struct
import lzma
import tempfile
import os
import shutil
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
from extract_payload import StreamBuffer, stream_pbzx, extract_payload_archive, create_filter


class TestStreamBufferAdversarial(unittest.TestCase):
    """Stress tests for StreamBuffer edge cases and boundary conditions."""

    def test_zero_length_read_and_skip(self):
        """Verify zero-length reads and skips don't mutate buffer or crash."""
        def dummy_gen():
            yield b"12345"
            yield b"67890"

        sb = StreamBuffer(dummy_gen())
        self.assertEqual(sb.read(0), b"")
        sb.skip(0)
        self.assertEqual(sb.read(5), b"12345")
        self.assertEqual(sb.read(0), b"")
        sb.skip(0)
        self.assertEqual(sb.read(5), b"67890")
        self.assertEqual(sb.read(0), b"")

    def test_boundary_crossing_read(self):
        """Verify reading across multiple small chunks reconstitutes original stream."""
        def chunk_gen():
            yield b"chunk_"
            yield b"one_"
            yield b"two_"
            yield b"three"

        sb = StreamBuffer(chunk_gen())
        # Request 15 bytes: crosses chunk_ (6), one_ (4), two_ (4), three (1)
        res = sb.read(15)
        self.assertEqual(res, b"chunk_one_two_t")
        res2 = sb.read(4)
        self.assertEqual(res2, b"hree")
        res3 = sb.read(10)
        self.assertEqual(res3, b"")

    def test_boundary_crossing_skip(self):
        """Verify skip across multiple chunks leaves exact remaining bytes in buffer."""
        def chunk_gen():
            yield b"AAAAA" # 5
            yield b"BBBBB" # 5
            yield b"CCCCC" # 5
            yield b"DDDDD" # 5

        sb = StreamBuffer(chunk_gen())
        # Skip 12 bytes: all A's (5), all B's (5), first 2 C's
        sb.skip(12)
        # Remaining should be 'CCC' and 'DDDDD' = 'CCCDDDDD'
        self.assertEqual(sb.read(8), b"CCCDDDDD")

    def test_truncated_read(self):
        """Verify read when stream terminates before n bytes are read returns available bytes."""
        def short_gen():
            yield b"short"

        sb = StreamBuffer(short_gen())
        res = sb.read(100)
        self.assertEqual(res, b"short")
        self.assertEqual(sb.read(10), b"")

    def test_skip_past_eof(self):
        """Verify skipping past EOF raises EOFError in strict mode."""
        def short_gen():
            yield b"123"

        sb = StreamBuffer(short_gen())
        # Should raise EOFError when skipping 100 bytes on a 3-byte stream in strict mode
        with self.assertRaises(EOFError):
            sb.skip(100)

        # In non-strict mode, skipping past EOF does not raise
        sb2 = StreamBuffer(short_gen())
        sb2.skip(100, strict=False)
        self.assertEqual(sb2.read(10), b"")


class TestPBZXExtractionAdversarial(unittest.TestCase):
    """Stress tests for PBZX format parsing and archive extraction."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.rootfs_dir = os.path.join(self.test_dir, "rootfs")
        self.dyld_dir = os.path.join(self.test_dir, "dyld")
        os.makedirs(self.rootfs_dir)
        os.makedirs(self.dyld_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _create_pbzx_archive(self, file_records, chunk_size=8388608):
        """Helper to create synthetic PBZX files with records."""
        stream_bytes = bytearray()
        for rtype, name, data, mode in file_records:
            name_bytes = name.encode("utf-8")
            nlen = len(name_bytes)
            fsize = len(data) if rtype == 0x1001 else 0
            # >HQQIHHHH
            hdr = struct.pack(">HQQIHHHH", rtype, fsize, 1600000000, 0, nlen, 0, 0, mode)
            stream_bytes.extend(hdr)
            stream_bytes.extend(name_bytes)
            if rtype == 0x1001:
                stream_bytes.extend(data)

        # Compress stream into PBZX chunks
        pbzx_data = bytearray()
        pbzx_data.extend(b"pbzx")
        pbzx_data.extend(struct.pack(">Q", chunk_size))

        offset = 0
        while offset < len(stream_bytes) or len(stream_bytes) == 0:
            raw_chunk = stream_bytes[offset:offset+chunk_size]
            dlen = len(raw_chunk)
            cdata = lzma.compress(bytes(raw_chunk))
            clen = len(cdata)
            pbzx_data.extend(struct.pack(">QQ", dlen, clen))
            pbzx_data.extend(cdata)
            offset += chunk_size
            if offset >= len(stream_bytes):
                break

        return bytes(pbzx_data)

    def test_zero_length_file_extraction(self):
        """Verify extractor correctly handles zero-length (0-byte) files."""
        records = [
            (0x1002, "Applications/Test.app", b"", 0o755),
            (0x1001, "Applications/Test.app/empty.txt", b"", 0o644),
            (0x1001, "Applications/Test.app/nonempty.txt", b"hello", 0o644),
        ]
        archive_path = os.path.join(self.test_dir, "test_zero.pbzx")
        with open(archive_path, "wb") as f:
            f.write(self._create_pbzx_archive(records))

        filt = create_filter(["Applications/Test.app"], [])
        ext_count, skip_count, ext_bytes = extract_payload_archive(
            archive_path, self.rootfs_dir, self.dyld_dir, filt
        )

        self.assertEqual(ext_count, 3)
        empty_file = os.path.join(self.rootfs_dir, "Applications/Test.app/empty.txt")
        self.assertTrue(os.path.isfile(empty_file))
        self.assertEqual(os.path.getsize(empty_file), 0)

        nonempty_file = os.path.join(self.rootfs_dir, "Applications/Test.app/nonempty.txt")
        self.assertTrue(os.path.isfile(nonempty_file))
        self.assertEqual(os.path.getsize(nonempty_file), 5)

    def test_invalid_pbzx_magic(self):
        """Verify invalid magic raises ValueError."""
        archive_path = os.path.join(self.test_dir, "corrupt_magic.pbzx")
        with open(archive_path, "wb") as f:
            f.write(b"bad!\x00\x00\x00\x00\x00\x80\x00\x00")

        with self.assertRaises(ValueError):
            list(stream_pbzx(archive_path))

    def test_truncated_pbzx_chunk_header(self):
        """Verify truncated chunk header terminates stream without crash."""
        archive_path = os.path.join(self.test_dir, "trunc_hdr.pbzx")
        with open(archive_path, "wb") as f:
            f.write(b"pbzx\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x05") # 12 bytes header (less than 16)

        chunks = list(stream_pbzx(archive_path))
        self.assertEqual(len(chunks), 0)

    def test_truncated_chunk_data(self):
        """Verify truncated chunk data raises IOError."""
        archive_path = os.path.join(self.test_dir, "trunc_data.pbzx")
        with open(archive_path, "wb") as f:
            # clen declares 100 bytes, but only 10 bytes provided
            f.write(b"pbzx\x00\x00\x00\x00\x00\x80\x00\x00" + struct.pack(">QQ", 100, 100) + b"1234567890")

        with self.assertRaises(IOError):
            list(stream_pbzx(archive_path))

    def test_uncompressed_chunk(self):
        """Verify dlen == clen processes uncompressed payload directly."""
        archive_path = os.path.join(self.test_dir, "uncompressed.pbzx")
        payload = b"DIRECT_UNCOMPRESSED_DATA"
        with open(archive_path, "wb") as f:
            f.write(b"pbzx\x00\x00\x00\x00\x00\x80\x00\x00" + struct.pack(">QQ", len(payload), len(payload)) + payload)

        chunks = list(stream_pbzx(archive_path))
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], payload)

    def test_truncated_file_stream_detection(self):
        """Verify extractor raises IOError when file payload is truncated mid-stream."""
        # Record says fsize is 1000, but stream ends immediately
        records = [
            (0x1001, "Applications/Test.app/truncated.bin", b"A" * 50, 0o644)
        ]
        # Modify the fsize inside the compressed stream by creating with fake fsize
        stream_bytes = bytearray()
        name = "Applications/Test.app/truncated.bin"
        name_bytes = name.encode("utf-8")
        hdr = struct.pack(">HQQIHHHH", 0x1001, 1000, 1600000000, 0, len(name_bytes), 0, 0, 0o644)
        stream_bytes.extend(hdr)
        stream_bytes.extend(name_bytes)
        stream_bytes.extend(b"A" * 50) # only 50 bytes instead of 1000

        cdata = lzma.compress(bytes(stream_bytes))
        archive_path = os.path.join(self.test_dir, "trunc_file.pbzx")
        with open(archive_path, "wb") as f:
            f.write(b"pbzx\x00\x00\x00\x00\x00\x80\x00\x00" + struct.pack(">QQ", len(stream_bytes), len(cdata)) + cdata)

        filt = create_filter(["Applications/Test.app"], [])
        with self.assertRaises(IOError) as ctx:
            extract_payload_archive(archive_path, self.rootfs_dir, self.dyld_dir, filt)
        self.assertIn("Truncated file stream", str(ctx.exception))

    def test_truncated_record_header(self):
        """Verify extractor raises EOFError when record header is truncated (< 30 bytes)."""
        stream_bytes = b"\x10\x01\x00\x00\x00\x05"  # 6 bytes instead of 30
        cdata = lzma.compress(stream_bytes)
        archive_path = os.path.join(self.test_dir, "trunc_hdr_rec.pbzx")
        with open(archive_path, "wb") as f:
            f.write(b"pbzx\x00\x00\x00\x00\x00\x80\x00\x00" + struct.pack(">QQ", len(stream_bytes), len(cdata)) + cdata)

        filt = create_filter(["Applications/Test.app"], [])
        with self.assertRaises(EOFError) as ctx:
            extract_payload_archive(archive_path, self.rootfs_dir, self.dyld_dir, filt)
        self.assertIn("Truncated record header", str(ctx.exception))

    def test_truncated_file_path(self):
        """Verify extractor raises EOFError when file path is truncated."""
        hdr = struct.pack(">HQQIHHHH", 0x1002, 0, 1600000000, 0, 50, 0, 0, 0o755)  # declares 50 bytes nlen
        stream_bytes = hdr + b"short_path"  # only 10 bytes path
        cdata = lzma.compress(stream_bytes)
        archive_path = os.path.join(self.test_dir, "trunc_path.pbzx")
        with open(archive_path, "wb") as f:
            f.write(b"pbzx\x00\x00\x00\x00\x00\x80\x00\x00" + struct.pack(">QQ", len(stream_bytes), len(cdata)) + cdata)

        filt = create_filter(["Applications/Test.app"], [])
        with self.assertRaises(EOFError) as ctx:
            extract_payload_archive(archive_path, self.rootfs_dir, self.dyld_dir, filt)
        self.assertIn("Truncated file path", str(ctx.exception))

    def test_truncated_skip_in_extraction(self):
        """Verify extractor raises EOFError when skipped file data is truncated."""
        # Unmatched file (will be skipped), declares 5000 bytes, but provides only 20
        name = "Unmatched/Skipped.bin"
        name_bytes = name.encode("utf-8")
        hdr = struct.pack(">HQQIHHHH", 0x1001, 5000, 1600000000, 0, len(name_bytes), 0, 0, 0o644)
        stream_bytes = hdr + name_bytes + (b"X" * 20)
        cdata = lzma.compress(stream_bytes)
        archive_path = os.path.join(self.test_dir, "trunc_skip.pbzx")
        with open(archive_path, "wb") as f:
            f.write(b"pbzx\x00\x00\x00\x00\x00\x80\x00\x00" + struct.pack(">QQ", len(stream_bytes), len(cdata)) + cdata)

        filt = create_filter(["Applications/Test.app"], [])
        with self.assertRaises(EOFError) as ctx:
            extract_payload_archive(archive_path, self.rootfs_dir, self.dyld_dir, filt)
        self.assertIn("Unexpected EOF while skipping", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
