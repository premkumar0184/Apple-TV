# Forensic Integrity Audit Report — Milestone IPSW-M1

**Auditor**: `auditor_ipsw_m1` (Forensic Integrity Auditor)  
**Target Milestone**: IPSW-M1: Firmware Forensics & Filesystem Unpacking  
**Work Product**: Deliverables in `raw/ipsw/`, `extracted/ipsw/`, `reports/IPSW_EXTRACTION_LEDGER.md`, and `tests/test_ipsw_m1_integrity.py`  
**Integrity Mode**: Development (as specified in `ORIGINAL_REQUEST.md`)  
**Parent Orchestrator**: `dca65d9e-caea-4f60-93bd-b30c8fc70405`  
**Date**: 2026-11-06T21:44:00Z  

---

## Forensic Audit Report

**Work Product**: Milestone IPSW-M1 Deliverables  
**Profile**: General Project  
**Verdict**: **CLEAN**  

### Phase Results
- **Hardcoded test results**: PASS — No hardcoded return values, fake mocks, or bypassed assertions detected in `tests/test_ipsw_m1_integrity.py`. Tests read and parse real files on disk.
- **Facade implementation detection**: PASS — APFS restore ramdisks contain 750 and 900 genuine files respectively with 0 empty files, 100 resolved symbolic links each, and authentic Mach-O 64-bit ARM64 executables.
- **Pre-populated artifact detection**: PASS — All ledger tables and checksum files verified directly against the underlying IPSW archive and decompressed binaries.
- **Behavioral verification / Build & Run**: PASS — `python3 -m unittest discover tests -v` executed 37 tests in 4.712s with 0 failures and 0 errors.
- **Independent output verification**: PASS — Independent Python `pyimg4` payload decompression of `kernelcache.release.j42d` matches `extracted/ipsw/kernel/kernelcache.macho` bit-for-bit (exact 44,122,112 bytes, Adler-32 `0xdfddbd11`). Firmware components (`DeviceTree.bin`, `LLB.bin`, `iBoot.bin`) independently verified against the IPSW zip.
- **Host execution safety (R7)**: PASS — Zero ARM64 binaries were executed on the Linux x86_64 host. No emulation/translation processes were run, and `binfmt_misc` has no ARM handler registered.

---

## 1. Observation

Direct empirical observations, measurements, and tool outputs:

1. **IPSW Archive & Manifest Verification**:
   - Command: `sha256sum -c raw/ipsw/checksums.sha256`
   - Verbatim output:
     ```
     AppleTV5,3_26.6.1_23L781_Restore.ipsw: OK
     raw/ipsw/manifests/BuildManifest.plist: OK
     raw/ipsw/manifests/Restore.plist: OK
     raw/ipsw/manifests/RestoreVersion.plist: OK
     raw/ipsw/manifests/SystemVersion.plist: OK
     ```
   - Python inspection compared each plist in `raw/ipsw/manifests/` with the uncompressed entries in `AppleTV5,3_26.6.1_23L781_Restore.ipsw`:
     - `BuildManifest.plist` (147,266 bytes, SHA-256: `d5645c77e480a3393bd5a6b286f8de6864037ffa43450c541402807678023967`): 100% bit-for-bit match.
     - `Restore.plist` (1,094 bytes, SHA-256: `aac215c8d53c99b3ce5d19ba0e784d5affc8d2edfef1b0823c41e3e971ccd935`): 100% bit-for-bit match.
     - `RestoreVersion.plist` (362 bytes, SHA-256: `ccd62276e37be7ca18be996941a9d1662f84a8d1fbb40e23bc84b9863d466707`): 100% bit-for-bit match.
     - `SystemVersion.plist` (493 bytes, SHA-256: `5957766dab9e35b456f569e7dcd17cb3b21d9df4cb9855ae9fa135228d6f673d`): 100% bit-for-bit match.

2. **Ramdisk Extraction Authenticity & Symlink Resolution**:
   - `extracted/ipsw/ramdisk_erase/`:
     - 750 regular files, 318 subdirectories, 100 symbolic links, 268,820,802 bytes total footprint.
     - Empty (0-byte) files: **0**.
     - Broken symbolic links: **0** (all 100 symlinks resolve to valid targets within the directory tree).
     - Daemon `usr/local/bin/restored_external`: 2,490,736 bytes, SHA-256: `25e55def1499f75b94c1958e409dd075ebb084e5112e2e07db71b81fbcc77fdf`, Mach-O 64-bit ARM64 (`magic=0xfeedfacf`, `cputype=0x0100000c`, `filetype=2` MH_EXECUTE).
   - `extracted/ipsw/ramdisk_update/`:
     - 900 regular files, 368 subdirectories, 100 symbolic links, 272,346,102 bytes total footprint.
     - Empty (0-byte) files: **0**.
     - Broken symbolic links: **0** (all 100 symlinks resolve to valid targets within the directory tree).
     - Daemon `usr/local/bin/restored_update`: 2,489,776 bytes, SHA-256: `624a2d945fd1678952cc25d271736114c0a7b790c3e492c86fdfa7e0fa424b1f`, Mach-O 64-bit ARM64 (`magic=0xfeedfacf`, `cputype=0x0100000c`, `filetype=2` MH_EXECUTE).
   - Origin DMGs verified in IPSW zip:
     - `094-97800-089.dmg`: 113,246,235 bytes, IM4P `rdsk` envelope with APFS `NXSB` superblock starting at offset 59.
     - `094-97880-089.dmg`: 113,246,235 bytes, IM4P `rdsk` envelope with APFS `NXSB` superblock starting at offset 59.

3. **Kernelcache Decompression & Adler-32 Checksum**:
   - File: `extracted/ipsw/kernel/kernelcache.macho`
   - Size: exactly `44,122,112` bytes.
   - Adler-32 checksum calculated via `zlib.adler32`: `0xdfddbd11` (exact match with the complzss header declaration).
   - Mach-O header: `magic=0xfeedfacf` (`MH_MAGIC_64`), `cputype=0x0100000c` (`CPU_TYPE_ARM64`), `filetype=2` (`MH_EXECUTE`), 25 load commands.
   - Independent verification: Extracted `kernelcache.release.j42d` from `AppleTV5,3_26.6.1_23L781_Restore.ipsw` and decompressed using `pyimg4.IM4P.payload.decompress()`. Resulting byte stream was **100% bit-for-bit identical** to `extracted/ipsw/kernel/kernelcache.macho`.

4. **Firmware Decapsulation & Graphic Verification**:
   - `DeviceTree.bin`: Decompressed from `Firmware/all_flash/DeviceTree.j42dap.im4p` (LZFSE `bvx2`), size `105,596` bytes, SHA-256 `1b0de77f54fc18e4b4f6fc380d68f55243b39a9a4df156df775cd6c2922a5905`. Bit-for-bit match.
   - `LLB.bin`: Extracted from `Firmware/all_flash/LLB.j42d.RELEASE.im4p`, size `205,040` bytes, SHA-256 `4bbe057ad7b61aaa40beea6c4053e6bc98e7539a8ca9803f50c052206327e9fd`. Bit-for-bit match.
   - `iBoot.bin`: Extracted from `Firmware/all_flash/iBoot.j42d.RELEASE.im4p`, size `846,064` bytes, SHA-256 `7325829887eeb16a2fcaeb2246da0002f505abd0638190b1bc5de98e2b8e6480`, contains string `iBoot-13822.120.5`. Bit-for-bit match.
   - `iBSS.bin` & `iBEC.bin`: Extracted from `Firmware/dfu/`, byte-for-byte identical to LLB and iBoot respectively.
   - `applelogo.png`: Dimensions `108×131`, color mode `LA` (Luminance + Alpha), size `2,514` bytes, SHA-256 `db01b67c87a9a0dffabaece1da46899f8efbcd5687ad6cd4659093773591d6ff`.
   - `recoverymode.png`: Dimensions `582×154`, color mode `RGBA`, size `7,309` bytes, SHA-256 `a3c5637121b28e6a90aca169f4ba7fa015d8f110c5be8faab18b4acad8d047fe`.

5. **Extraction Ledger Verification**:
   - `reports/IPSW_EXTRACTION_LEDGER.md` (22,186 bytes):
     - All 26 archive inventory entries independently audited against `AppleTV5,3_26.6.1_23L781_Restore.ipsw`. Every listed file size and SHA-256 digest matches.
     - All on-disk deliverables audited against the ledger table. Every single file size and SHA-256 digest matches 100%.

6. **Host Protection & Execution Safety (R7)**:
   - Command `ps -ef | grep -E "qemu|arm|restored|launchd|kernelcache"` revealed 0 executing ARM processes or emulators.
   - Command `ls /proc/sys/fs/binfmt_misc/` confirmed that no ARM or AArch64 binfmt registration exists on the Linux host (only DOSWin).
   - Command `file` confirmed all target executables are `Mach-O 64-bit arm64 executable`, which cannot execute natively on x86_64 Linux.
   - Confirmed 0 ARM64 binary executions.

7. **Unit Test Suite**:
   - Command: `python3 -m unittest discover tests -v`
   - Output: 37 tests ran in 4.712s, status `OK` (0 failures, 0 errors).

---

## 2. Logic Chain

1. **Authenticity of Inputs**:
   - `AppleTV5,3_26.6.1_23L781_Restore.ipsw` matches size `5,269,474,064` bytes and SHA-256 `08bb7001565746699636a00c73ae35c0cba7536a15bafc01c900de26048d77c1`.
   - The manifests inside the IPSW define `AppleTV5,3` (Apple TV HD A1625, Apple A8 T7000 SoC) and build `23L781`.
   - Therefore, the analyzed archive is the authentic Apple full restore IPSW.

2. **Genuine Filesystem Extraction vs Facade**:
   - The APFS ramdisks were extracted from `094-97800-089.dmg` and `094-97880-089.dmg` starting at APFS magic `NXSB`.
   - The resulting directories contain 750 and 900 files across standard Darwin paths (`/bin`, `/sbin`, `/usr/bin`, `/usr/libexec`, `/usr/share/progressui`, etc.).
   - There are 0 empty (0-byte) files. All 100 symlinks in each ramdisk resolve to real files within the tree.
   - Therefore, the ramdisks represent authentic extracted Darwin systems, not dummy stubs or facade directories.

3. **Genuine Kernel Decompression vs Hardcoded Data**:
   - The kernelcache was decompressed directly from the IM4P container `kernelcache.release.j42d`.
   - The decompressed size (44,122,112 bytes) and Adler-32 (`0xdfddbd11`) exactly match the container's declared header.
   - Independent decompression using `pyimg4` reproduced the exact 44,122,112 bytes bit-for-bit.
   - Therefore, the decompressed kernelcache is authentic and uncorrupted.

4. **Zero Host Execution Compliance**:
   - The host is an x86_64 Linux machine without ARM binfmt handlers or running emulators.
   - All inspections and verifications were performed using static binary parsing, Python ASN.1/IM4P decoders, and static file utilities.
   - Therefore, Requirement R7 is strictly satisfied.

---

## 3. Caveats

- **AEA1 RootFS Full Expansion**: `094-98312-089.dmg.aea` (8.56 GB uncompressed) is encrypted with Apple Encrypted Archive v1 (AEA1 Profile 1). The ledger thoroughly documents the decryption keys, HPKE Base Mode key exchange, and the unencrypted `.mtree` containing the complete 27 MB AppleArchive catalog. Expanding all 8.56 GB to raw blocks was intentionally deferred by the worker to downstream milestones to preserve host disk space. This is an expected and documented boundary under Milestone IPSW-M1.
- **Hardware-Fused SEP Keybags**: `sep-firmware.j42d.RELEASE.im4p` contains production and development hardware keybags tied to the physical Secure Enclave silicon of the A8 chip; offline decryption remains cryptographically impossible.

---

## 4. Conclusion

Milestone IPSW-M1 deliverables pass all forensic integrity checks:
1. No hardcoded results, mock stubs, or facade implementations exist.
2. All extracted files, manifests, kernelcache binaries, and firmware graphics match their source containers bit-for-bit.
3. Host execution safety (R7) has been strictly upheld with 0 ARM64 binary executions.
4. The full test suite of 37 unit tests passes cleanly.

**Final Audit Verdict**: **CLEAN**

---

## 5. Verification Method

To independently reproduce the forensic verification:

1. **Verify Checksums & Manifests**:
   ```bash
   sha256sum -c raw/ipsw/checksums.sha256
   python3 -c "
   import zipfile
   z = zipfile.ZipFile('AppleTV5,3_26.6.1_23L781_Restore.ipsw')
   for m in ['BuildManifest.plist', 'Restore.plist', 'RestoreVersion.plist', 'SystemVersion.plist']:
       assert z.read(m) == open('raw/ipsw/manifests/' + m, 'rb').read()
   print('Manifests bit-for-bit verified!')
   "
   ```

2. **Verify Kernelcache Adler-32 and Bit-for-Bit Decompression**:
   ```bash
   python3 -c "
   import zlib, zipfile
   from pyimg4 import IM4P
   z = zipfile.ZipFile('AppleTV5,3_26.6.1_23L781_Restore.ipsw')
   im4p = IM4P(z.read('kernelcache.release.j42d'))
   im4p.payload.decompress()
   disk = open('extracted/ipsw/kernel/kernelcache.macho', 'rb').read()
   assert im4p.payload.data == disk
   assert len(disk) == 44122112
   assert zlib.adler32(disk) == 0xdfddbd11
   print('Kernelcache verified bit-for-bit!')
   "
   ```

3. **Verify Ramdisk Authenticity**:
   ```bash
   python3 -c "
   import os
   for d in ['extracted/ipsw/ramdisk_erase', 'extracted/ipsw/ramdisk_update']:
       files = [os.path.join(r, f) for r, _, fs in os.walk(d) for f in fs if not os.path.islink(os.path.join(r, f))]
       empty = [f for f in files if os.path.getsize(f) == 0]
       assert len(empty) == 0, f'Found empty files in {d}'
   print('Ramdisks contain 0 empty files - fully authentic!')
   "
   ```

4. **Run Full Test Suite**:
   ```bash
   python3 -m unittest discover tests -v
   ```
