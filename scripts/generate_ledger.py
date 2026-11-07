#!/usr/bin/env python3
"""
Generates reports/EXTRACTION_LEDGER.md with full cryptographic hashes,
byte counts, file formats, and technical documentation of encryption boundaries.
"""

import os
import hashlib
import struct

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while chunk := f.read(1048576):
            h.update(chunk)
    return h.hexdigest()

def get_file_info(p):
    size = os.path.getsize(p)
    with open(p, 'rb') as fp:
        hdr = fp.read(32)
    fmt = 'Unknown'
    if len(hdr) >= 4:
        u32 = struct.unpack('<I', hdr[:4])[0]
        if u32 == 0xfeedfacf:
            fmt = 'Mach-O 64-bit ARM64'
        elif hdr[:8] == b'BOMStore':
            fmt = 'BOMStore Asset Catalog (.car)'
        elif hdr[:7] == b'iBootIm':
            fmt = 'iBoot Image (iBootIm)'
        elif hdr[:8] == b'bplist00':
            fmt = 'Binary Plist (bplist00)'
        elif hdr[:5] == b'<?xml':
            fmt = 'XML Property List'
        elif hdr[:15] == b'dyld_v1   arm64':
            fmt = 'dyld Shared Cache (ARM64)'
        elif hdr[:4] == b'\x12\x00\x00\x00':
            fmt = 'DeviceTree Binary'
        elif b'HX\x00\x05' in hdr:
            fmt = 'HFSX Filesystem Image'
    return size, fmt

print('Cataloging extracted files and computing hashes...')

# Target Apps
app_rows = []
car_rows = []
apps_dir = 'extracted/rootfs/Applications'
for app in sorted(os.listdir(apps_dir)):
    app_path = os.path.join(apps_dir, app)
    if not os.path.isdir(app_path): continue
    for root, dirs, files in os.walk(app_path):
        for f in files:
            full = os.path.join(root, f)
            if os.path.islink(full): continue
            size, fmt = get_file_info(full)
            if 'Mach-O' in fmt:
                h = sha256_file(full)
                rel = os.path.relpath(full, '.')
                app_rows.append((rel, size, fmt, h))
            elif 'BOMStore' in fmt:
                h = sha256_file(full)
                rel = os.path.relpath(full, '.')
                car_rows.append((rel, size, fmt, h))

# CoreGlyphs and other system cars
cg_path = 'extracted/rootfs/System/Library/CoreServices/CoreGlyphs.bundle/Assets.car'
if os.path.exists(cg_path):
    size, fmt = get_file_info(cg_path)
    car_rows.append((cg_path, size, fmt, sha256_file(cg_path)))

for extra_car in ['extracted/rootfs/System/Library/CoreServices/AssistiveTouch.app/Assets.car',
                  'extracted/rootfs/System/Library/CoreServices/MobileCoreTypes.bundle/Assets.car']:
    if os.path.exists(extra_car):
        size, fmt = get_file_info(extra_car)
        car_rows.append((extra_car, size, fmt, sha256_file(extra_car)))

# System Partitions
sys_rows = []
for p, desc in [
    ('extracted/dyld_cache/dyld_shared_cache_arm64', 'dyld Shared Cache (ARM64)'),
    ('extracted/kernel/kernelcache.macho', 'Decrypted/Decompressed Kernelcache (Mach-O 64-bit)'),
    ('extracted/firmware/DeviceTree.bin', 'Decapsulated Apple DeviceTree Binary'),
    ('extracted/firmware/applelogo.img3', 'Decapsulated Boot Logo Image (iBootIm)'),
    ('extracted/firmware/recoverymode.img3', 'Decapsulated Recovery Mode Image (iBootIm)')
]:
    if os.path.exists(p):
        sys_rows.append((p, os.path.getsize(p), desc, sha256_file(p)))

# Raw inputs
raw_rows = []
for p in [
    '8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip',
    'raw/manifests/BuildManifest.plist',
    'raw/manifests/Info.plist',
    'raw/manifests/AssetData_Info.plist',
    'raw/manifests/ZipMetadata.plist',
    'raw/manifests/payload.bom',
    'raw/manifests/pre.bom',
    'raw/manifests/post.bom',
    'raw/firmware/038-50764-064.dmg.image-img4',
    'raw/firmware/kernelcache.release.j105a',
    'raw/firmware/arm64SURamDisk.dmg',
    'raw/firmware/DeviceTree.j105aap.im4p',
    'raw/firmware/applelogo~appletv.im4p',
    'raw/firmware/recoverymode@1080~appletv5.im4p',
    'raw/firmware/iBoot.j105a.RELEASE.im4p',
    'raw/firmware/LLB.j105a.RELEASE.im4p',
    'raw/firmware/sep-firmware.j105a.RELEASE.im4p',
    'raw/firmware/aopfw-j105aaop.im4p',
    'raw/firmware/iBEC.j105a.RELEASE.im4p',
    'raw/firmware/iBSS.j105a.RELEASE.im4p'
]:
    if os.path.exists(p):
        raw_rows.append((p, os.path.getsize(p), sha256_file(p)))

# Ramdisk top binaries
rd_rows = []
rd_dir = 'extracted/ramdisk'
for sub in ['bin', 'sbin', 'usr/bin', 'usr/sbin', 'System/Library/Frameworks']:
    dir_path = os.path.join(rd_dir, sub)
    if not os.path.exists(dir_path): continue
    for item in sorted(os.listdir(dir_path)):
        full = os.path.join(dir_path, item)
        if os.path.islink(full): continue
        if os.path.isfile(full):
            size, fmt = get_file_info(full)
            if 'Mach-O' in fmt or size > 100000:
                h = sha256_file(full)
                rel = os.path.relpath(full, '.')
                rd_rows.append((rel, size, fmt, h))
        elif os.path.isdir(full) and full.endswith('.framework'):
            fw_bin = os.path.join(full, item[:-10])
            if os.path.exists(fw_bin) and not os.path.islink(fw_bin):
                size, fmt = get_file_info(fw_bin)
                h = sha256_file(fw_bin)
                rel = os.path.relpath(fw_bin, '.')
                rd_rows.append((rel, size, f'{fmt} ({item})', h))

md = []
md.append('# Apple tvOS Forensic Extraction Ledger')
md.append('')
md.append('**Milestone**: M1 (Archive Forensics, Filesystem Extraction & Hierarchy Preservation)  ')
md.append('**Date**: 2026-11-06T17:50:00Z  ')
md.append('**Target**: tvOS 13.4.8 (Build 17M61, AppleTV6,2 / j105aap / Apple TV 4K 1st Gen)  ')
md.append('**Execution Safety (R7)**: Strictly Static Analysis — 0 Target Host Executions  ')
md.append('')
md.append('---')
md.append('')
md.append('## 1. Executive Forensic Summary')
md.append('')
md.append('| Parameter | Forensic Value |')
md.append('| :--- | :--- |')
md.append('| **Archive File** | `8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip` |')
md.append('| **Archive Size** | `2,014,940,073` bytes (~1.876 GiB, 2.01 GB) |')
md.append('| **SHA-256** | `8725797b4ddfd93fc67023c93c1d9277f128e9731a9ac18618b9b2e812c027c1` |')
md.append('| **SHA-1** | `6802f6170a3c713d7111e98b0a81a5afb33ed9b8` |')
md.append('| **MD5** | `c29d3b384511eed5a4a0a309f907b4f9` |')
md.append('| **Package Format** | Apple MobileAsset SoftwareUpdate Package (Version 3.0) |')
md.append('| **Target OS Version** | `13.4.8` |')
md.append('| **Target Build** | `17M61` (Train: `YagerG`) |')
md.append('| **Target Device** | Apple TV 4K (1st Generation, Model A1842) |')
md.append('| **Device Identifier** | `AppleTV6,2` / `j105aap` |')
md.append('| **Target SoC** | Apple A10X Fusion (T8011, `ApChipID = 0x8011`, `ApBoardID = 0x02`) |')
md.append('| **Filesystem Encryption** | **0% Encrypted** (Userspace rootfs, applications, dyld cache, ramdisk, kernelcache are plaintext) |')
md.append('| **Hardware GID Encryption** | Early bootloaders only (`LLB`, `iBoot`, `SEP`, `iBEC`, `iBSS` contain silicon GID KBAGs) |')
md.append('| **Extraction Pipeline** | Pure Python streaming PBZX decompressor (`scripts/extract_payload.py`) |')
md.append('')
md.append('---')
md.append('')
md.append('## 2. Technical Analysis: Security & Encryption Boundaries')
md.append('')
md.append('### 2.1 The Two-Tier Firmware Boundary: Secure Boot vs. Userspace')
md.append('Apple MobileAsset SoftwareUpdate packages enforce a strict cryptographic partition between early pre-kernel boot stages and operating system userspace:')
md.append('')
md.append('1. **Hardware-Locked Pre-Kernel Stage (Encrypted via Silicon GID Keys)**:')
md.append('   - **Components**: `LLB.j105a.RELEASE.im4p`, `iBoot.j105a.RELEASE.im4p`, `sep-firmware.j105a.RELEASE.im4p`, `iBSS.j105a.RELEASE.im4p`, `iBEC.j105a.RELEASE.im4p`.')
md.append('   - **Container Structure**: Encapsulated in ASN.1 DER Image4 (`IM4P`) containers containing 5 sequence elements.')
md.append('   - **Keybag Sequence**: Element 4 is a `KBAG` (Keybag) sequence containing AES-256 initialization vectors and ciphertexts encrypted under the Apple A10X Fusion SoC Group Identification (GID) key.')
md.append('   - **Security Boundary**: The GID key is hard-fused into the silicon metal layers during chip fabrication and is accessible only to the AES crypto engine on physical hardware. It cannot be extracted or emulated in static software.')
md.append('   - **Reverse Engineering Impact**: **Zero impact** on tvOS application, UI framework, or system architecture reverse engineering. These bootloaders only manage DRAM initialization, low-level power rails, and initial signature validation before handing execution to the kernel.')
md.append('')
md.append('2. **Fully Accessible OS, Frameworks, and Application Stage (100% Plaintext)**:')
md.append('   - **Kernelcache** (`kernelcache.release.j105a`): The IM4P container tag `krnl` contains **no KBAG**. Element 3 contains a raw LZFSE-compressed byte stream (`bvx2` magic). Decompression produces a standard 64-bit ARM64 Mach-O kernel executable (`0xfeedfacf`) of 31,363,656 bytes with all Mach-O headers, segment commands, and kext symbols intact.')
md.append('   - **Restore Ramdisk** (`038-50764-064.dmg.image-img4` / `arm64SURamDisk.dmg`): The IM4P tag `rdsk` contains **no KBAG**. Stripping the 27-byte ASN.1 header reveals an unencrypted HFSX partition image (`HX\\x00\\x05`) with volume label `YagerG17M61.arm64SURamDisk`. Contains 507 files including core frameworks (`CoreFoundation`, `Foundation`, `CFNetwork`, `Security`) and utilities (`bin/`, `usr/bin/`).')
md.append('   - **Device Configuration & Boot Graphics**: `DeviceTree.j105aap.im4p` (`dtre`), `applelogo~appletv.im4p` (`logo`), and `recoverymode@1080~appletv5.im4p` (`recm`) contain **no KBAG** and decompress directly into native DeviceTree nodes and `iBootIm` pixel buffers.')
md.append('   - **Target OS Root Filesystem** (`038-50852-064.dmg` across `payloadv2/`): Chunked into 25 `pbzx` files (`payload.000` through `payload.024`). Zero encryption keys or DRM wrappers exist on these chunks. Every single file, directory, and framework is compressed with standard XZ / LZMA2 and extracts cleanly.')
md.append('')
md.append('### 2.2 PBZX Container and Record Header Architecture')
md.append("The root filesystem payload is distributed as a multi-chunk stream governed by Apple's `pbzx` format:")
md.append('- **File Header**: 4-byte magic string `pbzx` followed by an 8-byte big-endian unsigned integer declaring the buffer chunk size (`0x0000000000800000` = 8,388,608 bytes / 8 MB).')
md.append('- **Chunk Header**: 16 bytes per chunk: `dlen: uint64_be` (decompressed length) and `clen: uint64_be` (compressed length).')
md.append('  - If `dlen == clen`: Raw uncompressed block.')
md.append('  - If payload starts with `\\xfd7zXZ\\x00`: Standard XZ / LZMA2 container.')
md.append('- **Record Header (Decompressed Stream)**: Every file and directory is encoded as an exact 30-byte header unpacked via `struct.unpack(\">HQQIHHHH\", hdr)`:')
md.append('  - `rtype: uint16_be`: Record type (`0x1001` = Regular File, `0x1002` = Directory).')
md.append('  - `fsize: uint64_be`: File byte count (0 for directories).')
md.append('  - `mtime: uint64_be`: POSIX timestamp.')
md.append('  - `flags: uint32_be`: Apple filesystem metadata flags.')
md.append('  - `nlen: uint16_be`: Length of the UTF-8 relative path.')
md.append('  - `uid: uint16_be`: User ID.')
md.append('  - `gid: uint16_be`: Group ID.')
md.append('  - `mode: uint16_be`: POSIX octal file permissions.')
md.append('  - Followed by `nlen` path bytes, then `fsize` raw file data bytes.')
md.append('')
md.append('---')
md.append('')
md.append('## 3. Extracted Applications Inventory (`extracted/rootfs/Applications/`)')
md.append('')
md.append('| Application Path | Size (Bytes) | Format | SHA-256 Digest |')
md.append('| :--- | :--- | :--- | :--- |')
for r in sorted(app_rows):
    md.append(f'| `{r[0]}` | {r[1]:,} | {r[2]} | `{r[3]}` |')
md.append('')
md.append('---')
md.append('')
md.append('## 4. Compiled UI Asset Catalogs (`.car`)')
md.append('')
md.append('| Asset Catalog Path | Size (Bytes) | Format | SHA-256 Digest |')
md.append('| :--- | :--- | :--- | :--- |')
for r in sorted(car_rows):
    md.append(f'| `{r[0]}` | {r[1]:,} | {r[2]} | `{r[3]}` |')
md.append('')
md.append('---')
md.append('')
md.append('## 5. System Partitions, Kernel & Shared Libraries')
md.append('')
md.append('| Component Path | Size (Bytes) | Subsystem Description | SHA-256 Digest |')
md.append('| :--- | :--- | :--- | :--- |')
for r in sorted(sys_rows):
    md.append(f'| `{r[0]}` | {r[1]:,} | {r[2]} | `{r[3]}` |')
md.append('')
md.append('---')
md.append('')
md.append('## 6. Restore Ramdisk Partition Components (`extracted/ramdisk/`)')
md.append('')
md.append('| Component Path | Size (Bytes) | Subsystem Description | SHA-256 Digest |')
md.append('| :--- | :--- | :--- | :--- |')
for r in sorted(rd_rows):
    md.append(f'| `{r[0]}` | {r[1]:,} | {r[2]} | `{r[3]}` |')
md.append('')
md.append('---')
md.append('')
md.append('## 7. Raw Input Manifests & Firmware Checksums (`raw/`)')
md.append('')
md.append('| File Path | Size (Bytes) | SHA-256 Digest |')
md.append('| :--- | :--- | :--- |')
for r in sorted(raw_rows):
    md.append(f'| `{r[0]}` | {r[1]:,} | `{r[2]}` |')
md.append('')
md.append('---')
md.append('')
md.append('## 8. Forensic Verification Protocol')
md.append('')
md.append('To independently audit and verify this extraction ledger, execute the following commands from the project root:')
md.append('')
md.append('### 1. Verify Raw Input Checksums')
md.append('```bash')
md.append('sha256sum -c raw/checksums.sha256')
md.append('```')
md.append('')
md.append('### 2. Verify Extracted Kernelcache Mach-O')
md.append('```bash')
md.append('file extracted/kernel/kernelcache.macho')
md.append('# Expected: Mach-O 64-bit arm64 executable')
md.append('```')
md.append('')
md.append('### 3. Verify dyld Shared Cache Magic')
md.append('```bash')
md.append('head -c 16 extracted/dyld_cache/dyld_shared_cache_arm64')
md.append('# Expected: dyld_v1   arm64')
md.append('```')
md.append('')
md.append('### 4. Verify Asset Catalogs BOMStore Header')
md.append('```bash')
md.append('head -c 8 extracted/rootfs/System/Library/CoreServices/CoreGlyphs.bundle/Assets.car')
md.append('# Expected: BOMStore')
md.append('```')
md.append('')
md.append('### 5. Validate Application Binaries')
md.append('```bash')
md.append('file extracted/rootfs/Applications/PineBoard.app/PineBoard')
md.append('file extracted/rootfs/Applications/HeadBoard.app/HeadBoard')
md.append('file extracted/rootfs/Applications/Setup.app/Setup')
md.append('```')

os.makedirs('reports', exist_ok=True)
with open('reports/EXTRACTION_LEDGER.md', 'w') as out:
    out.write('\n'.join(md) + '\n')

print('Successfully generated reports/EXTRACTION_LEDGER.md')
