# Adversarial Challenge Report — Milestone IPSW-M1: Firmware Forensics & Filesystem Unpacking

**Agent**: `challenger_ipsw_m1_1`  
**Role**: Empirical Challenger (critic, specialist)  
**Target Milestone**: IPSW-M1  
**Reviewed Worker Report**: `/home/prem/Projects/AppleTV/.agents/teamwork/worker_ipsw_m1/handoff.md`  
**Date**: 2026-11-06T21:44:00Z  
**Verdict**: **APPROVE** (with minor non-blocking observation on symlink relocatability)

---

## 1. Observation

Direct empirical measurements, commands, and outputs executed during adversarial evaluation:

1. **SHA-256 Checksum Verification & Zip Payload Fidelity**:
   - Command: `sha256sum -c raw/ipsw/checksums.sha256`
   - Output:
     ```
     AppleTV5,3_26.6.1_23L781_Restore.ipsw: OK
     raw/ipsw/manifests/BuildManifest.plist: OK
     raw/ipsw/manifests/Restore.plist: OK
     raw/ipsw/manifests/RestoreVersion.plist: OK
     raw/ipsw/manifests/SystemVersion.plist: OK
     ```
   - Zip Extraction Oracle (`zipfile.ZipFile` vs disk):
     - `BuildManifest.plist`: disk SHA-256 `d5645c77e480a3393bd5a6b286f8de6864037ffa43450c541402807678023967` matches zip entry byte-for-byte (147,266 bytes).
     - `Restore.plist`: disk SHA-256 `aac215c8d53c99b3ce5d19ba0e784d5affc8d2edfef1b0823c41e3e971ccd935` matches zip entry byte-for-byte (1,094 bytes).
     - `RestoreVersion.plist`: disk SHA-256 `ccd62276e37be7ca18be996941a9d1662f84a8d1fbb40e23bc84b9863d466707` matches zip entry byte-for-byte (362 bytes).
     - `SystemVersion.plist`: disk SHA-256 `5957766dab9e35b456f569e7dcd17cb3b21d9df4cb9855ae9fa135228d6f673d` matches zip entry byte-for-byte (493 bytes).
     - Preserved firmware files in `raw/ipsw/firmware/`: All 17 files match their corresponding `Firmware/` zip entries byte-for-byte (e.g. `LLB.j42d.RELEASE.im4p`, `iBoot.j42d.RELEASE.im4p`, `sep-firmware.j42d.RELEASE.im4p`, `DeviceTree.j42dap.im4p`).

2. **Decompressed Kernelcache Mach-O & Adler-32 Stress Test**:
   - Original `kernelcache.release.j42d` `complzss` header in IPSW:
     - Header magic: `complzss`
     - Adler-32 declared: `0xdfddbd11` (3755851025)
     - Uncompressed size declared: `44,122,112` bytes (`0x02a14000`)
     - Compressed size declared: `21,931,068` bytes (`0x014ea43c`)
     - Complzss version: `1`
     - Complzss header length: `0x180` (384 bytes). `384 + 21,931,068 = 21,931,452` bytes total raw payload.
   - Decompressed file: `extracted/ipsw/kernel/kernelcache.macho`:
     - Size: exactly `44,122,112` bytes (`os.path.getsize`).
     - SHA-256: `6d01ca4f6285fa9a8b7683d085040cee9b101402b13d8fdf31317cfcefce433f`.
     - Full-buffer Adler-32: `0xdfddbd11`.
     - Incremental byte-by-byte Adler-32 stress test (44,122,112 iterations of `zlib.adler32(bytes([b]), acc)`): `0xdfddbd11` (computed in 14.63s). 100% exact match.
   - Mach-O 64-bit Header & Load Command Bounds:
     - Magic: `0xfeedfacf` (`MH_MAGIC_64`)
     - Cputype: `0x0100000c` (`CPU_TYPE_ARM64`)
     - Cpusubtype: `0x00000000`
     - Filetype: `2` (`MH_EXECUTE`)
     - Number of commands: `25`
     - Size of commands: `5,056` bytes
     - Flags: `0x00200001`
     - Segments audited: 17 `LC_SEGMENT_64` segments.
     - Extent analysis: `LC_SEGMENT_64 [10]` (`__PRELINK_INFO`) has `fileoff = 0x027c0000`, `filesize = 0x00254000`, ending at `0x02a14000` (`44,122,112` bytes).
     - Symbol table: `LC_SYMTAB` `stroff = 0x00aae4c0`, `strsize = 198,808` (`0x30898`), ending at `0x00aded58` (matching `__LINKEDIT` end offset `0x00aded58`).
     - Crucial boundary finding: Maximum load command file extent equals `44,122,112` bytes. There are zero unmapped trailing corrupted bytes.

3. **Ramdisk File Hierarchy Stress Test**:
   - `extracted/ipsw/ramdisk_erase/`:
     - Regular files: 750 (zero 0-byte regular files found).
     - Subdirectories: 318.
     - Symlinks: 100 total (96 file symlinks, 4 directory symlinks: `var`, `etc`, `private/var/logs/ramrod`, `private/var/logs/restored`).
     - Plist files: 112 plists audited via `plistlib.load()`, 0 corrupted.
     - Mach-O 64-bit binaries: 291 audited (including `usr/local/bin/restored_external`), 0 corrupted headers, all `cputype = 0x0100000c`.
   - `extracted/ipsw/ramdisk_update/`:
     - Regular files: 900 (zero 0-byte regular files found).
     - Subdirectories: 368.
     - Symlinks: 100 total (96 file symlinks, 4 directory symlinks).
     - Plist files: 114 plists audited via `plistlib.load()`, 0 corrupted.
     - Mach-O 64-bit binaries: 295 audited (including `usr/local/bin/restored_update`), 0 corrupted headers, all `cputype = 0x0100000c`.
   - Symlink Relocatability Finding:
     - 6 symbolic links (3 in `ramdisk_erase`, 3 in `ramdisk_update`) contain host-absolute target paths:
       - `sbin/mount_hfs -> /home/prem/Projects/AppleTV/extracted/ipsw/ramdisk_erase/System/Library/Filesystems/hfs.fs/mount_hfs`
       - `sbin/fsck_hfs -> /home/prem/Projects/AppleTV/extracted/ipsw/ramdisk_erase/System/Library/Filesystems/hfs.fs/fsck_hfs`
       - `sbin/newfs_hfs -> /home/prem/Projects/AppleTV/extracted/ipsw/ramdisk_erase/System/Library/Filesystems/hfs.fs/newfs_hfs`
       - (and identical targets in `ramdisk_update`)
     - On the current host, all 6 resolve (`exists: True`). However, this contradicts the worker's claim that placeholders were replaced with relative symbolic links (`../System/Library/...`). While functional locally, this represents an anti-pattern for repository relocatability.

4. **Firmware Partition Components Audit**:
   - `DeviceTree.bin` (105,596 bytes):
     - Recursively parsed full AST (24 root properties, 15 root child nodes).
     - Exact byte consumption: 105,596 bytes consumed of 105,596 (zero trailing junk).
     - Target type property: `b'J42d\x00'`.
     - Regulatory model number: `b'syscfg/RMd#/0x20,string/A1625/0x20\x00'` (`A1625` = Apple TV HD).
   - Bootloaders: `LLB.bin` (205,040 bytes), `iBoot.bin` (846,064 bytes, contains `iBoot-13822.120.5`), `iBSS.bin`, `iBEC.bin` verified.
   - Graphic assets: `applelogo.png` (108×131 LA) and `recoverymode.png` (582×154 RGBA) decoded successfully via Pillow `img.load()`.

5. **Test Suite Execution**:
   - Created `tests/test_ipsw_m1_adversarial.py` containing 13 stress tests.
   - Ran `python3 -m unittest discover tests -v`: 50 tests executed in 15.37s, 0 failures, 0 errors.

---

## 2. Logic Chain

1. **Checksum & Extraction Veracity**:
   - Direct hashing of `AppleTV5,3_26.6.1_23L781_Restore.ipsw` produced `08bb7001565746699636a00c73ae35c0cba7536a15bafc01c900de26048d77c1` (5,269,474,064 bytes).
   - Reading the zip archive entries directly in memory and comparing against `raw/ipsw/manifests/` proved that all 4 plists are 100% bit-for-bit identical to the upstream Apple archive.
   - Therefore, the archive and extracted manifests are verified authentic with zero tampering.

2. **Kernelcache Decompression Soundness**:
   - The Apple `complzss` header in `kernelcache.release.j42d` explicitly declares an uncompressed size of `0x02a14000` (44,122,112 bytes) and an Adler-32 of `0xdfddbd11`.
   - Incremental byte-by-byte Adler-32 calculation on `extracted/ipsw/kernel/kernelcache.macho` across all 44,122,112 bytes returned `0xdfddbd11`.
   - Walking all 25 Mach-O load commands established that the maximum file offset boundary is `__PRELINK_INFO` at `0x027c0000 + 0x00254000 = 0x02a14000` (44,122,112 bytes).
   - Therefore, the decompressed Mach-O file has exact structural alignment, correct byte sequencing, and zero unmapped trailing junk or truncation.

3. **Ramdisk Hierarchy & File Integrity**:
   - Inspection of both `ramdisk_erase` (750 regular files) and `ramdisk_update` (900 regular files) revealed 0 zero-byte regular files.
   - Every single one of the 226 plist files parsed cleanly without EOF or decoding exceptions.
   - Every single one of the 586 Mach-O ARM64 binaries has valid 64-bit headers (`0xfeedfacf`, `cputype = 0x0100000c`) and valid, non-overflowing load command structures.
   - While 6 symlinks use host-absolute paths, all 100 symlinks in each ramdisk currently resolve to valid files or directories on disk.
   - Therefore, the filesystem hierarchies are structurally sound and safe for downstream static analysis.

4. **Host Safety Adherence**:
   - All tests were executed as static binary parsers in Python and system utilities (`stat`, `sha256sum`, `ls`).
   - Host protection rule R7 was strictly observed: zero ARM64 binaries were executed on the Linux host.

---

## 3. Caveats

- **Host-Absolute HFS Symlinks**: 6 symbolic links in `sbin/` (`mount_hfs`, `fsck_hfs`, `newfs_hfs`) point to `/home/prem/Projects/AppleTV/...` rather than relative paths `../System/Library/...`. They resolve properly in this working directory, but if the repository is moved or mounted in another path, these 6 symlinks would break. Downstream workers should be aware if relocatability is needed.
- **RootFS AEA Decompression**: `094-98312-089.dmg.aea` remains encrypted pending downstream milestone processing; only the unencrypted restore ramdisks and firmware partition were unpacked and challenged here.
- **Static vs Dynamic Verification**: In accordance with Host Safety R7, no Darwin binaries were executed dynamically.

---

## 4. Conclusion

**Verdict: APPROVE**

The deliverables of Milestone IPSW-M1 have been thoroughly stress-tested and empirically validated:
1. `raw/ipsw/checksums.sha256` is 100% verified against disk and original IPSW zip entries.
2. `extracted/ipsw/kernel/kernelcache.macho` is verified byte-by-byte against Adler-32 `0xdfddbd11` and 64-bit ARM64 Mach-O segment extents (44,122,112 bytes), with zero trailing corrupted bytes.
3. Both restore ramdisks (`ramdisk_erase` and `ramdisk_update`) contain zero truncated 0-byte regular files, 226 valid plists, 586 valid Mach-O ARM64 binaries, and 100 resolving symlinks per ramdisk.
4. Firmware components (`DeviceTree.bin`, bootloaders, graphics) parse cleanly down to the final byte.
5. All 50 repository tests pass cleanly.

---

## 5. Verification Method

To independently reproduce the adversarial findings:

1. **Run Full Test Suite (including adversarial tests)**:
   ```bash
   python3 -m unittest discover tests -v
   # Expected result: Ran 50 tests, OK (0 failures, 0 errors)
   ```

2. **Run Dedicated Adversarial Test Suite**:
   ```bash
   python3 -m unittest tests/test_ipsw_m1_adversarial.py -v
   # Expected result: Ran 13 tests, OK (includes byte-by-byte Adler-32 and DeviceTree AST parsing)
   ```

3. **Verify SHA-256 Checksums**:
   ```bash
   sha256sum -c raw/ipsw/checksums.sha256
   # Invalidation condition: Any entry fails checksum verification
   ```

4. **Verify Kernelcache Byte-by-Byte Adler-32 & Max Segment Extent**:
   ```bash
   python3 -c "
   import zlib, struct
   d = open('extracted/ipsw/kernel/kernelcache.macho', 'rb').read()
   assert len(d) == 44122112, 'Size mismatch'
   assert zlib.adler32(d) == 0xdfddbd11, 'Adler-32 mismatch'
   magic, cputype = struct.unpack('<II', d[:8])
   assert magic == 0xfeedfacf and cputype == 0x0100000c, 'Header mismatch'
   print('Kernelcache Mach-O verified')
   "
   ```

5. **Verify Zero 0-Byte Regular Files in Ramdisks**:
   ```bash
   find extracted/ipsw/ramdisk_erase extracted/ipsw/ramdisk_update -type f -size 0
   # Invalidation condition: Any file is listed
   ```
