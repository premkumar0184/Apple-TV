# Milestone 1 Independent Review Report: Reviewer 2

**Author**: Reviewer 2 (`reviewer_m1_2`)  
**Roles**: reviewer, critic  
**Working Directory**: `/home/prem/Projects/AppleTV/.agents/teamwork/reviewer_m1_2`  
**Workspace Root**: `/home/prem/Projects/AppleTV`  
**Parent Agent**: `995e6d20-c347-437b-93ba-1b98ec79241b`  
**Reviewed Artifact**: Milestone 1 Deliverables by `worker_m1`  
**Milestone**: M1 (Archive Forensics, Filesystem Extraction & Hierarchy Preservation)  
**Verdict**: **`APPROVE`**  
**Integrity Audit**: PASS (0 Integrity Violations Detected)  

---

## 1. Observation

### 1.1 Directory Structure & Interface Contracts
Direct directory inspection of `/home/prem/Projects/AppleTV` verified that the 6-tier architecture specified in `PROJECT.md` is strictly enforced:
- `raw/`: Populated with `checksums.sha256`, `manifests/` (7 files), and `firmware/` (12 files).
- `extracted/`: Populated with `rootfs/Applications/` (10 applications + 2 app extensions), `dyld_cache/` (unified 1.08 GB shared cache), `ramdisk/` (507 files), `kernel/` (`kernelcache.macho`), and `firmware/` (`DeviceTree.bin`, `applelogo.img3`, `recoverymode.img3`).
- `decoded/`: Prepared with subdirectories `assets/`, `strings/`, `plists/`, `nibs/`.
- `analysis/`: Prepared with subdirectories `objc/`, `swift/`, `symbols/`, `ipc/`.
- `graphify-out/`: Initialized for M4 knowledge graph artifacts.
- `reports/`: Populated with authoritative `EXTRACTION_LEDGER.md`.
- `scripts/`: Populated with `extract_payload.py` and `generate_ledger.py`.
- `.agents/teamwork/`: Strictly contains only agent coordination metadata and reports.

All interface contracts defined in `PROJECT.md` (§ Interface Contracts) for downstream milestones M2 (UI & Assets) and M3 (Binary Analysis) are fully present and verified:
- `PineBoard.app/` contains `PineBoard` binary (3,645,792 bytes), `Info.plist`, `Assets.car` (116,088 bytes), and 33 `.lproj` localization directories.
- `HeadBoard.app/` contains `HeadBoard` binary (1,319,504 bytes), `Info.plist`, `Assets.car` (666,808 bytes), and 33 `.lproj` localization directories.
- `CoreGlyphs.bundle/Assets.car` (91,411,496 bytes) is located at `extracted/rootfs/System/Library/CoreServices/CoreGlyphs.bundle/Assets.car`.
- `extracted/rootfs/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64` is a valid relative symlink resolving to `../../../../../dyld_cache/dyld_shared_cache_arm64`.

### 1.2 Cryptographic Verification (`raw/checksums.sha256`)
Execution of `sha256sum -c raw/checksums.sha256` in `/home/prem/Projects/AppleTV` produced verbatim:
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
Result: 20 of 20 cryptographic digests matched on disk (exit status 0).

### 1.3 Target Application Binaries Mach-O Verification
Direct byte-level Mach-O header parsing of `PineBoard` and `HeadBoard` binaries confirmed:
- `extracted/rootfs/Applications/PineBoard.app/PineBoard`:
  - Size: 3,645,792 bytes
  - SHA-256: `1a72bb5bd7b18385bc720b0f1ec47b4589ac889131e46a7c5de8b04b5d9d44bc`
  - Magic: `0xfeedfacf` (`MH_MAGIC_64`)
  - CPU Type: `0x100000c` (`CPU_TYPE_ARM64`)
  - File Type: `2` (`MH_EXECUTE`)
  - Number of Load Commands: `106`, Size of Commands: `11,792` bytes, Flags: `0x200085` (`NOUNDEFS|DYLDLINK|TWOLEVEL|PIE`)
  - `LC_BUILD_VERSION`: `platform=3` (`PLATFORM_TVOS`), `minos=0xd0400` (tvOS 13.4.0), `sdk=0xd0400` (tvOS 13.4.0)
- `extracted/rootfs/Applications/HeadBoard.app/HeadBoard`:
  - Size: 1,319,504 bytes
  - SHA-256: `15c11e632a40c402e142102b912bbc6c1a7e195cc227933b5b2be0d4c542437b`
  - Magic: `0xfeedfacf` (`MH_MAGIC_64`)
  - CPU Type: `0x100000c` (`CPU_TYPE_ARM64`)
  - File Type: `2` (`MH_EXECUTE`)
  - Number of Load Commands: `52`, Size of Commands: `6,104` bytes, Flags: `0x200085`
  - `LC_BUILD_VERSION`: `platform=3` (`PLATFORM_TVOS`), `minos=0xd0400`, `sdk=0xd0400`

### 1.4 Extracted Kernelcache & dyld Shared Cache
- `extracted/kernel/kernelcache.macho`:
  - Exact file size: `31,363,656` bytes
  - Magic: `0xfeedfacf` (`MH_MAGIC_64`), CPU Type: `0x100000c` (`CPU_TYPE_ARM64`), File Type: `2` (`MH_EXECUTE`), ncmds: `22`
  - Computed SHA-256: `df0d622ace9a648f3de12c1f2c003360f4048f1024a0a074cc28916e1ad5afe3`
- `extracted/dyld_cache/dyld_shared_cache_arm64`:
  - Exact file size: `1,086,013,440` bytes
  - Magic header prefix: `b'dyld_v1   arm64\x00'`
  - Computed SHA-256: `8b0cf8e0a862915d5c98a26ba07dd9b574e367aa332a20a1d94bf2dc51d30412`

### 1.5 Forensic Ledger Accuracy & Security Boundary Verification
- An independent Python audit script parsed all 83 table rows from `reports/EXTRACTION_LEDGER.md` (covering applications, plugins, asset catalogs, kernel, dyld shared cache, ramdisk utilities, and raw firmware components). Every entry was checked against the file system for exact file existence, byte size, and SHA-256 hash:
  - Total entries parsed: 83
  - Verified exact size & hash: **83**
  - Missing files: **0**
  - Mismatches: **0**
- Technical Boundary Verification:
  - ASN.1 DER sequence dissection of `raw/firmware/LLB.j105a.RELEASE.im4p` confirmed an ASN.1 outer sequence of 483,034 bytes containing 5 fields. Field 3 is an OCTET STRING of 482,880 bytes with high entropy (7.999591), and Field 4 is a 116-byte OCTET STRING containing two keybag sequences:
    - `KBAG[0]`: Production GID key (`type=1`), `IV=b6f06448ed73765fd1c3d93ce522e0c8`, `Key=2c69107d2acd280cff5080db0b851b8e2e956a57430aebfb325206bf5b99b833`
    - `KBAG[1]`: Development GID key (`type=2`), `IV=7d89d95bb4317d2874a2671d2d1d51a4`, `Key=4598185c2bc95c1431bd0cf7d0e976b6580ed90ec113701d4303e871bb4c696a`
  - In contrast, ASN.1 parsing of `raw/firmware/kernelcache.release.j105a` confirmed only 4 fields (tag `IM4P`, tag `krnl`, version string, and a 11,891,604-byte `bvx2` LZFSE stream). No Field 4 (KBAG) exists, confirming that kernelcache, ramdisk, and userspace are 100% unencrypted.

### 1.6 Host Safety (R7) & Adversarial Integrity Audit
- Host environment check: `uname -m` confirmed `x86_64`.
- Host emulator check: `which qemu-aarch64 qemu-arm-static` returned exit status 2 (neither installed nor present in PATH).
- Verification of extraction codebase: `scripts/extract_payload.py` was inspected line-by-line. It implements authentic streaming PBZX chunk parsing and XZ decompression via Python's standard `lzma` library, decoding the 30-byte record header `>HQQIHHHH`. No dummy stubs, hardcoded return values, or shortcuts were found.
- Execution history confirms strictly static inspection (zero ARM64 executions on host).

---

## 2. Logic Chain

1. **Premise**: Milestone 1 acceptance criteria require verifying archive identity and SHA-256 digests against manifests, preserving a 6-tier directory hierarchy, extracting core applications, kernelcache, and dyld shared cache, documenting security boundaries in an extraction ledger, and enforcing host execution safety (R1, R2, R7).
2. **From §1.1**: The directory tree matches the required 6-tier structure, and all specified interface files for M2 and M3 exist at expected paths.
3. **From §1.2**: All 20 items in `raw/checksums.sha256` pass automated SHA-256 verification against physical disk files without a single discrepancy.
4. **From §1.3**: Inspection of Mach-O headers in `PineBoard` and `HeadBoard` proves they are authentic 64-bit ARM64 Mach-O executables targeted specifically at tvOS (`PLATFORM_TVOS`, SDK 13.4.0).
5. **From §1.4**: `kernelcache.macho` and `dyld_shared_cache_arm64` exhibit correct magic bytes, valid sizes, and exact SHA-256 hashes matching the ledger.
6. **From §1.5**: All 83 rows in `reports/EXTRACTION_LEDGER.md` match physical disk size and SHA-256 hash with 0 errors. Low-level ASN.1 DER parsing proves that pre-kernel bootloaders (`LLB`, `iBoot`, `SEP`) contain AES-256 keybags encrypted under hardware silicon GID keys, whereas the kernelcache and userspace are completely unencrypted.
7. **From §1.6**: Zero target binaries were executed on the x86_64 Linux host, complying with Requirement R7. The implementation contains no dummy facade code or integrity violations.
8. **Conclusion**: Milestone 1 meets all requirements and acceptance criteria.

---

## 3. Caveats

1. **Selective Exclusion of Screen Saver Videos**: The aerial video assets (`Default@2x.mov` and `Default@2x_HDR.mov`, totaling 255 MB in `payload.002` and `payload.003`) were deliberately bypassed by `extract_payload.py` to prevent host disk exhaustion. The `TVIdleScreen` Mach-O binary, property lists, and localization strings were fully extracted. This is an intentional engineering optimization documented in both the worker handoff and project plan.
2. **Hardware GID Keybag Inaccessibility**: The AES keybags embedded in Field 4 of the bootloader IM4P containers (`LLB`, `iBoot`, `sep-firmware`) require the physical Apple A10X Fusion silicon GID key to decrypt. These keys are fused in hardware metal layers and are unextractable statically. This boundary is thoroughly explained in §2.1 of `reports/EXTRACTION_LEDGER.md` and poses zero obstacle to userspace UI and binary reverse engineering.
3. **Relative Symlink for dyld Shared Cache**: The dyld cache is physically stored in `extracted/dyld_cache/dyld_shared_cache_arm64` and symlinked from `extracted/rootfs/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64`. Downstream tools resolving relative symlinks will locate the cache transparently without duplicating 1.08 GB of disk space.

---

## 4. Conclusion

Milestone 1 is **VERIFIED AND APPROVED**.
- **Verdict**: **`APPROVE`**
- All deliverables for Requirements R1, R2, and R7 are present, cryptographically verified, and compliant with project architectural boundaries.
- No integrity violations, shortcuts, facade implementations, or host execution hazards were found.
- The workspace is ready for Milestone 2 (UI Architecture & Asset Reverse Engineering) and Milestone 3 (Binary Analysis & REA Reverse Engineering).

---

## 5. Verification Method

To independently re-verify Reviewer 2's findings, run the following commands from `/home/prem/Projects/AppleTV`:

### 1. Verify Raw Input Checksums
```bash
sha256sum -c raw/checksums.sha256
# Expected: All 20 files output OK
```

### 2. Verify Target Application Mach-O Headers
```bash
python3 -c "
import struct
for path in ['extracted/rootfs/Applications/PineBoard.app/PineBoard', 'extracted/rootfs/Applications/HeadBoard.app/HeadBoard']:
    with open(path, 'rb') as f:
        magic, cputype, cpusubtype, filetype, ncmds = struct.unpack('<IIIII', f.read(20))
        assert magic == 0xfeedfacf and cputype == 0x100000c and filetype == 2
    print(f'{path}: Valid Mach-O 64-bit ARM64 executable')
"
```

### 3. Verify Decompressed Kernelcache & dyld Shared Cache
```bash
python3 -c "
import os, struct
assert os.path.getsize('extracted/kernel/kernelcache.macho') == 31363656
with open('extracted/kernel/kernelcache.macho', 'rb') as f:
    assert struct.unpack('<I', f.read(4))[0] == 0xfeedfacf
print('kernelcache verified.')

assert os.path.getsize('extracted/dyld_cache/dyld_shared_cache_arm64') == 1086013440
with open('extracted/dyld_cache/dyld_shared_cache_arm64', 'rb') as f:
    assert f.read(16).startswith(b'dyld_v1   arm64')
print('dyld shared cache verified.')
"
```

### 4. Verify Forensic Ledger Accuracy (83 Entries)
```bash
python3 -c "
import os, hashlib
with open('reports/EXTRACTION_LEDGER.md') as f:
    lines = f.readlines()
for line in lines:
    if line.startswith('| `extracted/') or line.startswith('| `raw/'):
        parts = [p.strip().strip('\`') for p in line.split('|')[1:-1]]
        path, size, h = parts[0], int(parts[1].replace(',', '')), parts[-1]
        assert os.path.getsize(path) == size, f'Size mismatch on {path}'
        hasher = hashlib.sha256()
        with open(path, 'rb') as fp:
            while chunk := fp.read(1048576): hasher.update(chunk)
        assert hasher.hexdigest() == h, f'Hash mismatch on {path}'
print('All extraction ledger entries verified against disk.')
"
```

### 5. Invalidation Conditions
- Any checksum mismatch in `raw/checksums.sha256`.
- Missing target applications in `extracted/rootfs/Applications/`.
- Inability to read or parse Mach-O headers in `PineBoard` or `HeadBoard`.
- Discrepancies in `reports/EXTRACTION_LEDGER.md` table data vs disk contents.
