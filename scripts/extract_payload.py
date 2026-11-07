#!/usr/bin/env python3
"""
Apple tvOS PBZX Streaming Extractor
Milestone 1 - Reverse Engineering and Architecture Reconstruction

Extracts files from Apple MobileAsset OTA payload chunks (PBZX / XZ format)
using the 30-byte record format (>HQQIHHHH) without loading multi-gigabyte
files into memory.
"""

import os
import sys
import struct
import lzma
import hashlib
import time
import argparse
from pathlib import Path

# Core UI & System Applications to extract
DEFAULT_TARGET_APPS = [
    "Applications/PineBoard.app",
    "Applications/HeadBoard.app",
    "Applications/PreBoard.app",
    "Applications/Setup.app",
    "Applications/TVSystemMenuService.app",
    "Applications/TVSystemBulletinService.app",
    "Applications/TVPeripheralAgent.app",
    "Applications/TVIdleScreen.app",
    "Applications/AppleTV.app",
    "Applications/AppStore.app",
    "Applications/TVMusic.app",
]

# Additional core bundle targets
DEFAULT_TARGET_BUNDLES = [
    "System/Library/CoreServices/CoreGlyphs.bundle",
]

# dyld shared cache target
DYLD_CACHE_PATH = "System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"


class StreamEOFError(EOFError, IOError):
    """Raised when a stream terminates prematurely."""
    pass


def stream_pbzx(file_path):
    """
    Generator that parses a PBZX archive and yields uncompressed byte chunks.
    PBZX header: 4-byte magic ('pbzx') + 8-byte uint64 chunk buffer size.
    Each chunk: 8-byte uncompressed length (dlen) + 8-byte compressed length (clen).
    If dlen == clen, payload is uncompressed.
    If payload starts with XZ magic (\xfd7zXZ\x00), decompressed using lzma.
    """
    with open(file_path, "rb") as fp:
        magic = fp.read(4)
        if magic != b"pbzx":
            raise ValueError(f"Invalid PBZX magic in {file_path}: {magic}")
        _ = struct.unpack(">Q", fp.read(8))[0]
        while True:
            chdr = fp.read(16)
            if len(chdr) < 16:
                break
            dlen, clen = struct.unpack(">QQ", chdr)
            cdata = fp.read(clen)
            if len(cdata) < clen:
                raise StreamEOFError(f"Unexpected EOF in {file_path}: expected {clen} bytes, got {len(cdata)}")
            if dlen == clen:
                yield cdata
            else:
                yield lzma.decompress(cdata)


class StreamBuffer:
    """
    Buffered reader over a PBZX chunk generator providing read() and skip().
    """
    def __init__(self, gen):
        self.gen = gen
        self.buf = bytearray()

    def read(self, n):
        while len(self.buf) < n:
            try:
                self.buf.extend(next(self.gen))
            except StopIteration:
                break
        res = bytes(self.buf[:n])
        del self.buf[:n]
        return res

    def skip(self, n, strict=True):
        """Efficiently discard n bytes from stream."""
        remaining = n
        if len(self.buf) >= remaining:
            del self.buf[:remaining]
            return
        remaining -= len(self.buf)
        self.buf.clear()
        while remaining > 0:
            try:
                chunk = next(self.gen)
            except StopIteration:
                break
            if len(chunk) <= remaining:
                remaining -= len(chunk)
            else:
                self.buf.extend(chunk[remaining:])
                remaining = 0
        if remaining > 0 and strict:
            raise StreamEOFError(f"Unexpected EOF while skipping {n} bytes (unskipped: {remaining})")


def create_filter(target_apps, target_bundles, include_dyld=True, skip_videos=True):
    """Returns a filter function determining whether to extract a given file path."""
    app_prefixes = tuple(app.rstrip("/") + "/" for app in target_apps)
    app_exact = tuple(app.rstrip("/") for app in target_apps)
    bundle_prefixes = tuple(b.rstrip("/") + "/" for b in target_bundles)
    bundle_exact = tuple(b.rstrip("/") for b in target_bundles)

    def should_extract(name):
        # Prevent disk exhaustion from raw video screen savers
        if skip_videos and (name.endswith(".mov") or name.endswith(".mp4")):
            return False

        if include_dyld and name == DYLD_CACHE_PATH:
            return True

        if name in app_exact or name.startswith(app_prefixes):
            return True

        if name in bundle_exact or name.startswith(bundle_prefixes):
            return True

        # Always catch any Assets.car belonging to any application or system bundle
        if name.endswith("Assets.car") and ("Applications/" in name or "CoreServices/" in name):
            return True

        return False

    return should_extract


def extract_payload_archive(payload_path, rootfs_out, dyld_out, should_extract, verbose=False):
    """
    Extracts matching files from a single PBZX payload archive.
    Returns (extracted_count, skipped_count, extracted_bytes).
    """
    sb = StreamBuffer(stream_pbzx(payload_path))
    extracted_count = 0
    skipped_count = 0
    extracted_bytes = 0

    while True:
        hdr = sb.read(30)
        if len(hdr) == 0:
            break
        if len(hdr) < 30:
            raise StreamEOFError(f"Truncated record header in {payload_path}: expected 30 bytes, got {len(hdr)}")
        rtype, fsize, mtime, flags, nlen, uid, gid, mode = struct.unpack(">HQQIHHHH", hdr)
        name_bytes = sb.read(nlen)
        if len(name_bytes) < nlen:
            raise StreamEOFError(f"Truncated file path in {payload_path}: expected {nlen} bytes, got {len(name_bytes)}")
        name = name_bytes.decode("utf-8", errors="replace")

        extract = should_extract(name)

        if name == DYLD_CACHE_PATH and extract:
            # Special destination for dyld shared cache
            target_path = os.path.join(dyld_out, "dyld_shared_cache_arm64")
            rootfs_symlink = os.path.join(rootfs_out, name)
            is_dyld = True
        else:
            target_path = os.path.join(rootfs_out, name)
            is_dyld = False

        if rtype == 0x1002:  # Directory
            if extract:
                os.makedirs(target_path, exist_ok=True)
                extracted_count += 1
            else:
                skipped_count += 1

        elif rtype == 0x1001:  # Regular file
            if extract:
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, "wb") as out_f:
                    remaining = fsize
                    while remaining > 0:
                        chunk_size = min(remaining, 65536)
                        block = sb.read(chunk_size)
                        if not block:
                            raise StreamEOFError(f"Truncated file stream while writing {name}")
                        out_f.write(block)
                        remaining -= len(block)
                try:
                    os.chmod(target_path, mode & 0o777)
                except OSError:
                    pass

                if is_dyld:
                    # Create symlink in rootfs pointing to extracted/dyld_cache
                    os.makedirs(os.path.dirname(rootfs_symlink), exist_ok=True)
                    rel_target = os.path.relpath(target_path, os.path.dirname(rootfs_symlink))
                    try:
                        if os.path.islink(rootfs_symlink) or os.path.exists(rootfs_symlink):
                            os.remove(rootfs_symlink)
                        os.symlink(rel_target, rootfs_symlink)
                    except OSError:
                        pass

                extracted_count += 1
                extracted_bytes += fsize
                if verbose or fsize > 1000000:
                    print(f"  [+] Extracted: {name} ({fsize:,} bytes)")
            else:
                sb.skip(fsize)
                skipped_count += 1

        elif rtype == 0x1003:  # Symbolic link
            target_bytes = sb.read(fsize)
            if len(target_bytes) < fsize:
                raise StreamEOFError(f"Truncated symlink target in {payload_path}")
            if extract:
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                link_target = target_bytes.decode("utf-8", errors="replace")
                try:
                    if os.path.islink(target_path) or os.path.exists(target_path):
                        os.remove(target_path)
                    os.symlink(link_target, target_path)
                    extracted_count += 1
                except OSError:
                    pass
            else:
                skipped_count += 1

        else:  # Fallback for unknown record types
            if fsize > 0:
                sb.skip(fsize)
            skipped_count += 1

    return extracted_count, skipped_count, extracted_bytes


def validate_extracted_files(rootfs_dir, dyld_dir):
    """
    Validates magic bytes of extracted files:
    - Mach-O 64-bit: 0xfeedfacf (little endian cffaedfe)
    - Asset catalogs: BOMStore
    - dyld cache: dyld_v1   arm64
    """
    results = {
        "macho_valid": 0,
        "macho_invalid": 0,
        "car_valid": 0,
        "car_invalid": 0,
        "dyld_valid": False,
        "files_checked": 0,
    }

    # Check dyld shared cache
    dyld_file = os.path.join(dyld_dir, "dyld_shared_cache_arm64")
    if os.path.isfile(dyld_file):
        with open(dyld_file, "rb") as f:
            magic = f.read(16)
            if magic.startswith(b"dyld_v1   arm64"):
                results["dyld_valid"] = True
                print(f"[VALID] dyld_shared_cache_arm64 magic verified: {magic[:15]}")
            else:
                print(f"[ERROR] dyld_shared_cache_arm64 invalid magic: {magic}")

    for root, dirs, files in os.walk(rootfs_dir):
        for f in files:
            p = os.path.join(root, f)
            if os.path.islink(p):
                continue
            results["files_checked"] += 1
            try:
                with open(p, "rb") as fp:
                    hdr = fp.read(16)
                    if len(hdr) >= 4:
                        u32 = struct.unpack("<I", hdr[:4])[0]
                        if u32 == 0xfeedfacf:
                            results["macho_valid"] += 1
                        elif hdr[:8] == b"BOMStore":
                            results["car_valid"] += 1
            except (OSError, IOError):
                pass

    print("\nValidation Summary:")
    print(f"  Files checked: {results['files_checked']}")
    print(f"  Valid Mach-O 64-bit binaries: {results['macho_valid']}")
    print(f"  Valid Asset Catalogs (BOMStore): {results['car_valid']}")
    print(f"  Valid dyld shared cache: {results['dyld_valid']}")
    return results


def main():
    parser = argparse.ArgumentParser(description="Apple tvOS PBZX Streaming Extractor")
    parser.add_argument(
        "--payload-dir",
        default="8988ef3518b1f20f95c66d03be3c15eb4e1be2a0/AssetData/payloadv2",
        help="Path to AssetData/payloadv2 directory",
    )
    parser.add_argument(
        "--rootfs-out",
        default="extracted/rootfs",
        help="Destination directory for rootfs contents",
    )
    parser.add_argument(
        "--dyld-out",
        default="extracted/dyld_cache",
        help="Destination directory for dyld shared cache",
    )
    parser.add_argument(
        "--payloads",
        nargs="*",
        default=[
            "payload.000",
            "payload.001",
            "payload.004",
            "payload.010",
            "payload.011",
            "payload.017",
            "payload.018",
            "payload.020",
            "payload.021",
            "payload.022",
            "payload.023",
            "payload.024",
        ],
        help="List of payload chunk filenames to process (or 'all')",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose file logging")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Skip extraction, run validation on existing files",
    )

    args = parser.parse_args()

    if args.validate_only:
        validate_extracted_files(args.rootfs_out, args.dyld_out)
        return

    os.makedirs(args.rootfs_out, exist_ok=True)
    os.makedirs(args.dyld_out, exist_ok=True)

    filter_fn = create_filter(
        DEFAULT_TARGET_APPS,
        DEFAULT_TARGET_BUNDLES,
        include_dyld=True,
        skip_videos=True,
    )

    payload_files = args.payloads
    if payload_files == ["all"]:
        payload_files = ["data_payload"] + [f"payload.{i:03d}" for i in range(25)]

    print("[*] Beginning PBZX streaming extraction...")
    print(f"    Payloads: {len(payload_files)} archives")
    print(f"    Rootfs output: {args.rootfs_out}")
    print(f"    dyld output: {args.dyld_out}")

    t0 = time.time()
    total_extracted_files = 0
    total_skipped_files = 0
    total_extracted_bytes = 0

    for pf in payload_files:
        payload_path = os.path.join(args.payload_dir, pf)
        if not os.path.isfile(payload_path):
            print(f"[!] Warning: Payload file not found: {payload_path}")
            continue

        print(f"\n[*] Processing {pf}...")
        t_chunk = time.time()
        ext_count, skip_count, ext_bytes = extract_payload_archive(
            payload_path,
            args.rootfs_out,
            args.dyld_out,
            filter_fn,
            verbose=args.verbose,
        )
        elapsed = time.time() - t_chunk
        total_extracted_files += ext_count
        total_skipped_files += skip_count
        total_extracted_bytes += ext_bytes
        print(
            f"    -> Extracted {ext_count:,} records ({ext_bytes:,} bytes), "
            f"skipped {skip_count:,} in {elapsed:.2f}s"
        )

    total_time = time.time() - t0
    print("\n[+] Extraction Complete!")
    print(f"    Total files/dirs extracted: {total_extracted_files:,}")
    print(f"    Total bytes extracted: {total_extracted_bytes:,} ({total_extracted_bytes / 1024**2:.1f} MB)")
    print(f"    Total time: {total_time:.2f}s")

    print("\n[*] Validating extracted components...")
    validate_extracted_files(args.rootfs_out, args.dyld_out)


if __name__ == "__main__":
    main()
