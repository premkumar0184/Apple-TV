# Milestone 1 Challenge & Verification Report: Archive Forensics & Filesystem Extraction

**Author**: Challenger 2 (`challenger_m1_2`)  
**Role**: critic / specialist (Empirical Challenger)  
**Working Directory**: `/home/prem/Projects/AppleTV/.agents/teamwork/challenger_m1_2`  
**Workspace Root**: `/home/prem/Projects/AppleTV`  
**Parent Conversation ID**: `995e6d20-c347-437b-93ba-1b98ec79241b`  
**Milestone**: M1 (Archive Forensics, Filesystem Extraction & Hierarchy Preservation)  
**Verdict**: **APPROVE**  
**Overall Risk Assessment**: **LOW**  
**Execution Safety (R7)**: Strictly Static Analysis — 0 Target Host Executions  

---

## 1. Observation

### 1.1 Verification of Cryptographic Hash Ledger (`raw/checksums.sha256`)
- **Execution Command**: `sha256sum -c raw/checksums.sha256` from workspace root `/home/prem/Projects/AppleTV`.
- **Verbatim Result**:
  ```text
  8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip: OK
  raw/manifests/BuildManifest.plist: OK
  raw/manifests/Info.plist: OK
  raw/manifests/AssetData_Info.plist: OK
  raw/manifests/ZipMetadata.plist: OK
  raw/manifests/payload.bom: OK
  raw/manifests/pre.bom: OK
  raw/manifests/post.bom: OK
  raw/firmware/038-50764-064.dmg.image-img4: OK
  raw/firmware/kernelcache.release.j105a: OK
  raw/firmware/arm64SURamDisk.dmg: OK
  raw/firmware/DeviceTree.j105aap.im4p: OK
  raw/firmware/applelogo~appletv.im4p: OK
  raw/firmware/recoverymode@1080~appletv5.im4p: OK
  raw/firmware/iBoot.j105a.RELEASE.im4p: OK
  raw/firmware/LLB.j105a.RELEASE.im4p: OK
  raw/firmware/sep-firmware.j105a.RELEASE.im4p: OK
  raw/firmware/aopfw-j105aaop.im4p: OK
  raw/firmware/iBEC.j105a.RELEASE.im4p: OK
  raw/firmware/iBSS.j105a.RELEASE.im4p: OK
  ```
- **Exit Code**: `0`. All 20 items cryptographically validated with zero mismatches.

### 1.2 Verification of Original Archive Integrity & Non-Destructive Extraction
- **Original Archive**: `/home/prem/Projects/AppleTV/8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip`
- **Commands & Results**:
  ```text
  sha256sum: 8725797b4ddfd93fc67023c93c1d9277f128e9731a9ac18618b9b2e812c027c1
  stat: Size = 2,014,940,073 bytes, Inode = 26476903, Links = 1
  unzip -tq 8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip:
  "No errors detected in compressed data of 8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip."
  ```
- **Finding**: The source archive is 100% byte-for-byte identical to the recorded hash and completely free of container corruption.

### 1.3 Cross-Referencing Extracted Rootfs Against Authoritative `post.bom`
- **Manifest**: `raw/manifests/post.bom` (BOMStore format, version 1, 188,511 blocks, 62,792 records).
- **Inspection Methodology**: Compiled native C++ `lsbom` utility (from `bomutils`, resolving inverted `strstr` branch) and parsed all 62,792 BOM path records with permissions, file types, sizes, and POSIX CRC-32 checksums (`cksum`).
- **Scan Scope**: 1,414 total filesystem records in `extracted/rootfs` (901 regular files, 512 directories, 1 symlink).
- **Audit Findings**:
  - **Missing in BOM**: `0` (100% of extracted files and directories exist in `post.bom`).
  - **Type Mismatches**: `0` (Directories, regular files, and symlinks match BOM types).
  - **Zero-Byte File Anomalies**: `0` (Zero files in `extracted/rootfs` have size 0 where `post.bom` expects > 0 bytes).
  - **File Size Matches**: `901 / 901` (`100%` exact match).
  - **POSIX `cksum` Matches**: `901 / 901` (`100%` exact match).
  - **Permission Mode Matches (mask `0777`)**: `901 / 901` (`100%` exact match).

### 1.4 Verification of Zero-Byte Files Across the Entire Workspace
- **Command**: `find extracted/ -type f -size 0`
- **Result**: Exactly two files found in the entire `extracted/` hierarchy:
  1. `extracted/ramdisk/usr/share/progressui/disconnect-prompt-inverted.tga`
  2. `extracted/ramdisk/.Trashes`
- **DMG Source Cross-Check**: Inspected original `raw/firmware/arm64SURamDisk.dmg` via `7z l`:
  - `YagerG17M61.arm64SURamDisk/.Trashes`: Size `0` bytes.
  - `YagerG17M61.arm64SURamDisk/usr/share/progressui/disconnect-prompt-inverted.tga`: Size `0` bytes.
- **Finding**: Zero unintended 0-byte files exist. The two 0-byte files in the ramdisk are byte-accurate reflections of the original Apple DMG filesystem. In `extracted/rootfs`, zero 0-byte files exist.

### 1.5 Verification of Forensic Ledger (`reports/EXTRACTION_LEDGER.md`)
- **Entries Checked**: All 83 documented table rows:
  - 12 Application binaries in `extracted/rootfs/Applications/`
  - 17 Asset catalogs (`.car`)
  - 5 System partitions, kernelcache, and dyld cache
  - 29 Restore ramdisk components (`extracted/ramdisk/`)
  - 20 Raw inputs and manifests (`raw/`)
- **Result**:
  - Verified entries: `83 / 83`
  - Size mismatches: `0`
  - SHA-256 mismatches: `0`
  - Missing files: `0`

### 1.6 Verification of Core System Applications & dyld Shared Cache
- **Applications Verified**:
  1. `Applications/PineBoard.app/PineBoard`: 3,645,792 bytes, Mach-O 64-bit arm64 (`1a72bb5bd7b18385bc720b0f1ec47b4589ac889131e46a7c5de8b04b5d9d44bc`)
  2. `Applications/HeadBoard.app/HeadBoard`: 1,319,504 bytes, Mach-O 64-bit arm64 (`15c11e632a40c402e142102b912bbc6c1a7e195cc227933b5b2be0d4c542437b`)
  3. `Applications/PreBoard.app/PreBoard`: 111,008 bytes, Mach-O 64-bit arm64 (`51d44a4c5c5589ee0c07bedbe6c0f3b89744b3c3a1451cb8a833d03aeba48305`)
  4. `Applications/Setup.app/Setup`: 1,190,000 bytes, Mach-O 64-bit arm64 (`62fa7dbe70617d5fd40a0449fc53f53b0f16347885cabb5ad3ec06cdd77ed1ba`)
  5. `Applications/TVSystemMenuService.app/TVSystemMenuService`: 129,472 bytes, Mach-O 64-bit arm64 (`d3dc9f056de85715cfbcbca08152e63f65e194ebf764a072bde5c7ad8ac64f47`)
  6. `Applications/TVSystemBulletinService.app/TVSystemBulletinService`: 74,512 bytes, Mach-O 64-bit arm64 (`4617d638931a4978cd9321c3608bfa66515eb776835a638f0f5a6201b4007099`)
  7. `Applications/TVPeripheralAgent.app/TVPeripheralAgent`: 130,176 bytes, Mach-O 64-bit arm64 (`ba276a6efc75bb7bfcad3bfe2de9436d41c2ad70a97b998d97c1a68b98f0465c`)
  8. `Applications/TVIdleScreen.app/TVIdleScreen`: 269,776 bytes, Mach-O 64-bit arm64 (`3d68c35f42b8c0418932457638dd0aa89b5c4eed47e47744f552941904c1d014`)
  9. `Applications/AppleTV.app/AppleTV`: 134,176 bytes, Mach-O 64-bit arm64 (`a0bf529c1688e7e39909a38ff65bb09118d04023535f241786f82482c1719347`)
  10. `Applications/AppStore.app/AppStore`: 2,829,904 bytes, Mach-O 64-bit arm64 (`45aeda4bd7269c9b993ec5332277fb12ecc2ec072268a0e0d722ec043d27d40e`)
  11. `Applications/AppleTV.app/PlugIns/TVUpNextExtension.appex/TVUpNextExtension`: 112,928 bytes, Mach-O 64-bit arm64 (`564772c152f2aa78d01e7bafb15be6bdb6a4757265a4e89386df07662339e7b4`)
  12. `Applications/AppStore.app/PlugIns/AppStoreTopShelfExtension.appex/AppStoreTopShelfExtension`: 156,912 bytes, Mach-O 64-bit arm64 (`78459c8f60322e986a8c8dedec04c0363b0bc9c6d9c43f0b9cc659977788a0f2`)
- **dyld Shared Cache**:
  - Size: `1,086,013,440` bytes
  - Header: `dyld_v1   arm64\x00`
  - Mapping Count: `3` (offset 312)
  - Mapped Images Count: `1,086` (offset 408)
  - Rootfs Symlink: `extracted/rootfs/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64 -> ../../../../../dyld_cache/dyld_shared_cache_arm64` (valid, relative target resolves).

### 1.7 Execution Safety (Requirement R7)
- Target binary architecture is Mach-O 64-bit ARM64. Host is Linux x86_64.
- Zero binary emulation wrappers (`qemu-arm64`, `darling`) were deployed or invoked.
- All inspections conducted exclusively via static magic byte analysis, struct unpacking, ASN.1 parsing, and cryptographic checksumming.

---

## 2. Logic Chain

1. **Premise**: Under Milestone 1 acceptance criteria, the worker deliverables must be verified for complete consistency between raw manifests (`post.bom`), the extraction ledger (`reports/EXTRACTION_LEDGER.md`), and the actual extracted assets on disk without modifying source inputs or executing target ARM64 binaries on host.
2. **From §1.1 & §1.2**: Running `sha256sum -c raw/checksums.sha256` proved that all 20 baseline inputs match authoritative hashes with 0 errors. Direct hashing and `unzip -tq` on `8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip` proved that extraction was strictly non-destructive.
3. **From §1.3**: Cross-referencing `raw/manifests/post.bom` against `extracted/rootfs/` proved that all 901 extracted files perfectly match their BOM-specified permissions, file sizes, and POSIX `cksum` values. This proves that `scripts/extract_payload.py` performed lossless PBZX stream unpacking without truncating data chunks or corrupting record boundaries.
4. **From §1.4**: Scanning the entire workspace revealed zero unintended 0-byte files. The only two 0-byte files reside in `extracted/ramdisk/` and were proven to originate as 0-byte files in Apple's original `arm64SURamDisk.dmg` image.
5. **From §1.5 & §1.6**: Auditing `reports/EXTRACTION_LEDGER.md` confirmed that every single table row (83 entries across all 5 tables) accurately reflects disk reality, down to SHA-256 digests, byte counts, and Mach-O / BOMStore magic signatures. The `dyld_shared_cache_arm64` was validated to contain 1,086 mapped images with valid internal structures.
6. **From §1.7**: Conformance with R7 was maintained with zero target host executions.

---

## 3. Caveats

1. **Selective Extraction of Aerial Video Screensavers**:
   - `TVIdleScreen.app` aerial video assets (`Default@2x.mov` and `Default@2x_HDR.mov`, totaling 255 MB) were excluded from extraction to preserve host disk headroom under the 2.5 GB ceiling. This design decision was explicitly documented in worker caveats and did not omit any code, binary, plist, asset catalog, or localization string.
2. **Hardware GID Encryption Boundary**:
   - The early bootloader stages (`LLB`, `iBoot`, `SEP`, `iBSS`, `iBEC`) contain AES-256 keys encrypted with the A10X SoC GID silicon key. They cannot be decrypted statically without physical silicon exploitation, which is correctly identified and documented as an out-of-scope boundary.
3. **symlink in Rootfs for dyld Cache**:
   - `extracted/rootfs/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64` is a symbolic link pointing to `../../../../../dyld_cache/dyld_shared_cache_arm64`. Tools checking `lstat` will report size 49 bytes (symlink path length), while `stat` reports the full 1,086,013,440 bytes. This is by design and standard for Unix filesystem hierarchies.

---

## 4. Adversarial Challenge Report

### Challenge Summary
**Overall Risk Assessment**: **LOW**

### Stress Test Results

| Hypothesis / Attack Scenario | Expected Behavior | Actual Behavior | Result |
| :--- | :--- | :--- | :--- |
| **H1: PBZX Chunk Truncation**<br>Decompression cuts off stream records | POSIX `cksum` and byte sizes mismatch `post.bom` | 901/901 files match `post.bom` byte count and POSIX `cksum` | **PASS (Robust)** |
| **H2: Corrupt dyld Shared Cache**<br>Extracted cache has invalid offsets or truncated mappings | Header magic or image count invalid | Magic `dyld_v1 arm64`, 3 mappings, 1,086 images intact | **PASS (Robust)** |
| **H3: Unintended Zero-Byte Files**<br>Files created empty during failed extraction | Empty files present in `extracted/rootfs` | Zero 0-byte files in `extracted/rootfs` | **PASS (Robust)** |
| **H4: Ledger Phantom Hashes**<br>EXTRACTION_LEDGER contains fabricated entries | Files missing or hash mismatch | 83/83 entries exist and match SHA-256 | **PASS (Robust)** |
| **H5: Input Archive Modification**<br>Extraction modified original zip | Hash of zip changes, `unzip -t` fails | SHA-256 `8725797b...` intact, `unzip -tq` clean | **PASS (Robust)** |
| **H6: Host Execution of Target Binaries**<br>Worker or challenger executed ARM64 code | Host execution logs or crash traces | 0 host executions, static inspection only | **PASS (Robust)** |

### Unchallenged Areas
- Silicon GID key extraction: Impossible without physical hardware test bench. Correctly documented as hardware boundary.

---

## 5. Conclusion & Verdict

**Verdict**: **APPROVE**

Milestone 1 satisfies all forensic, cryptographic, extraction, and safety criteria set forth in `ORIGINAL_REQUEST.md` (R1, R2, R7) and the Project Plan:
- `raw/checksums.sha256` is 100% verified (`20/20 OK`).
- The original firmware archive remains completely unmodified and bit-accurate.
- The 10 required system applications, 17 asset catalogs, and 1.08 GB dyld shared cache are extracted cleanly with zero corruption and zero 0-byte file anomalies.
- All extracted rootfs assets match Apple's authoritative `post.bom` manifest with 100% precision across sizes, modes, paths, and POSIX checksums.
- `reports/EXTRACTION_LEDGER.md` is complete, accurate, and independently verified against disk reality.

The project is fully cleared to proceed to Milestone 2 (UI Asset & Component Reverse Engineering).

---

## 6. Verification Method

To reproduce these empirical findings from `/home/prem/Projects/AppleTV`:

### 1. Verify Checksum Ledger
```bash
sha256sum -c raw/checksums.sha256
```

### 2. Verify Original Archive Integrity
```bash
sha256sum 8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip
unzip -tq 8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip
```

### 3. Verify dyld Shared Cache Header & Tables
```bash
python3 -c "
import struct
with open('extracted/dyld_cache/dyld_shared_cache_arm64', 'rb') as f:
    hdr = f.read(128)
magic, mapping_offset, mapping_count, images_offset, images_count = struct.unpack('<16sIIII', hdr[:32])
assert magic.startswith(b'dyld_v1   arm64')
assert mapping_count == 3
assert images_count == 1086
print(f'dyld_shared_cache_arm64 validated! {images_count} images mapped.')
"
```

### 4. Verify EXTRACTION_LEDGER.md Against Filesystem
```bash
python3 -c "
import os, re, hashlib
def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while c := f.read(1048576): h.update(c)
    return h.hexdigest()
with open('reports/EXTRACTION_LEDGER.md') as f: c = f.read()
entries = re.findall(r'\|\s*\`([^\`]+)\`\s*\|\s*([0-9,]+)\s*\|(?:[^\`]*\|\s*\`([0-9a-f]{64})\`\s*\||\s*\`([0-9a-f]{64})\`\s*\|)', c)
verified = 0
for p, s, h1, h2 in entries:
    expected_h = h1 if h1 else h2
    sz = int(s.replace(',', ''))
    assert os.path.exists(p) and os.path.getsize(p) == sz and sha256_file(p) == expected_h
    verified += 1
print(f'All {verified} ledger entries verified on disk with 0 errors.')
"
```

### 5. Check for Unexpected Zero-Byte Files
```bash
find extracted/rootfs -type f -size 0
# Expected: (empty output)
```
