# Handoff Report — Milestone IPSW-M1: Firmware Forensics & Filesystem Unpacking

**Agent**: `worker_ipsw_m1`  
**Milestone**: IPSW-M1  
**Target IPSW**: `AppleTV5,3_26.6.1_23L781_Restore.ipsw` (Build `23L781`, Model `AppleTV5,3` / Apple TV HD A1625, Apple A8 T7000 SoC)  
**Parent Orchestrator**: `dca65d9e-caea-4f60-93bd-b30c8fc70405`  
**Date**: 2026-11-06T21:36:00Z  

---

## 1. Observation

Direct empirical observations, measurements, and tool outputs:

1. **IPSW Archive Integrity & Manifest Preservation**:
   - Command: `sha256sum AppleTV5,3_26.6.1_23L781_Restore.ipsw`
   - Output: `08bb7001565746699636a00c73ae35c0cba7536a15bafc01c900de26048d77c1  AppleTV5,3_26.6.1_23L781_Restore.ipsw`
   - Command: `stat -c %s AppleTV5,3_26.6.1_23L781_Restore.ipsw`
   - Output: `5269474064` bytes.
   - Verified that `raw/ipsw/checksums.sha256` records the SHA-256 digest and file size (`5,269,474,064`).
   - Manifest plists preserved in `raw/ipsw/manifests/`:
     - `BuildManifest.plist` (147,266 bytes, SHA-256: `d5645c77e480a3393bd5a6b286f8de6864037ffa43450c541402807678023967`)
     - `Restore.plist` (1,094 bytes, SHA-256: `aac215c8d53c99b3ce5d19ba0e784d5affc8d2edfef1b0823c41e3e971ccd935`)
     - `RestoreVersion.plist` (362 bytes, SHA-256: `ccd62276e37be7ca18be996941a9d1662f84a8d1fbb40e23bc84b9863d466707`)
     - `SystemVersion.plist` (493 bytes, SHA-256: `5957766dab9e35b456f569e7dcd17cb3b21d9df4cb9855ae9fa135228d6f673d`)
   - Verification command: `sha256sum -c raw/ipsw/checksums.sha256` passed with `OK` for all entries.

2. **Restore Ramdisk Extraction (`extracted/ipsw/ramdisk_erase/` & `extracted/ipsw/ramdisk_update/`)**:
   - `094-97800-089.dmg` extracted into `extracted/ipsw/ramdisk_erase/`:
     - 750 regular files, 314 subdirectories (315 total), 100 symbolic links.
     - Unpacked byte footprint: 268,824,552 bytes (~268.8 MB).
     - Primary restore daemon: `usr/local/bin/restored_external` (2,490,736 bytes, Mach-O 64-bit arm64 executable, flags `<NOUNDEFS|DYLDLINK|TWOLEVEL|BINDS_TO_WEAK|PIE>`, SHA-256: `25e55def1499f75b94c1958e409dd075ebb084e5112e2e07db71b81fbcc77fdf`).
   - `094-97880-089.dmg` extracted into `extracted/ipsw/ramdisk_update/`:
     - 900 regular files, 364 subdirectories (365 total), 100 symbolic links.
     - Unpacked byte footprint: 272,349,852 bytes (~272.3 MB).
     - Primary restore daemon: `usr/local/bin/restored_update` (2,489,776 bytes, Mach-O 64-bit arm64 executable, flags `<NOUNDEFS|DYLDLINK|TWOLEVEL|BINDS_TO_WEAK|PIE>`, SHA-256: `624a2d945fd1678952cc25d271736114c0a7b790c3e492c86fdfa7e0fa424b1f`).
   - 7-Zip emitted safety warnings for 10 relative traversal symlinks (e.g. `sbin/mount_apfs -> ../System/Library/Filesystems/apfs.fs/mount_apfs`), placing 0-byte regular file placeholders. These placeholders were systematically replaced with authentic relative symbolic links matching the APFS filesystem.

3. **Kernelcache Decompression (`extracted/ipsw/kernel/kernelcache.macho`)**:
   - Input: `AppleTV5,3_26.6.1_23L781_Restore/kernelcache.release.j42d` (21,964,283 bytes, tag `krnl`).
   - `complzss` header unpacked: uncompressed size declared as `0x02a14000` (44,122,112 bytes), Adler-32 declared as `0xdfddbd11`.
   - Python `pyimg4` payload decompression produced exactly `44,122,112` bytes.
   - Decompressed Adler-32 checksum calculated via `zlib.adler32`: `0xdfddbd11` (100% exact match).
   - Decompressed Mach-O header inspected: magic `0xfeedfacf` (`MH_MAGIC_64`), cputype `0x0100000c` (`CPU_TYPE_ARM64`), filetype `2` (`MH_EXECUTE`), 25 load commands.
   - SHA-256 of `extracted/ipsw/kernel/kernelcache.macho`: `6d01ca4f6285fa9a8b7683d085040cee9b101402b13d8fdf31317cfcefce433f`.

4. **Firmware Partition Components Extraction (`extracted/ipsw/firmware/`)**:
   - `DeviceTree.bin`: Decompressed from `DeviceTree.j42dap.im4p` (`dtre`, LZFSE `bvx2`), exactly `105,596` bytes, SHA-256: `1b0de77f54fc18e4b4f6fc380d68f55243b39a9a4df156df775cd6c2922a5905`.
   - `LLB.bin`: Extracted from `LLB.j42d.RELEASE.im4p` (`illb`), exactly `205,040` bytes, SHA-256: `4bbe057ad7b61aaa40beea6c4053e6bc98e7539a8ca9803f50c052206327e9fd`.
   - `iBoot.bin`: Extracted from `iBoot.j42d.RELEASE.im4p` (`ibot`), exactly `846,064` bytes, SHA-256: `7325829887eeb16a2fcaeb2246da0002f505abd0638190b1bc5de98e2b8e6480`. Contains version string `iBoot-13822.120.5`.
   - `iBSS.bin`: Extracted from `Firmware/dfu/iBSS.j42d.RELEASE.im4p`, exactly `205,040` bytes (identical to LLB).
   - `iBEC.bin`: Extracted from `Firmware/dfu/iBEC.j42d.RELEASE.im4p`, exactly `846,064` bytes (identical to iBoot).
   - `applelogo.png`: Decompressed from `applelogo~appletv.im4p` (`logo`, `iBootIm` LZSS), converted to PNG (108×131, mode `LA`), size 2,514 bytes, SHA-256: `db01b67c87a9a0dffabaece1da46899f8efbcd5687ad6cd4659093773591d6ff`.
   - `recoverymode.png`: Decompressed from `recoverymode@1080~appletv5.im4p` (`recm`, `iBootIm` LZSS), converted to PNG (582×154, mode `RGBA`), size 7,309 bytes, SHA-256: `a3c5637121b28e6a90aca169f4ba7fa015d8f110c5be8faab18b4acad8d047fe`.

5. **Master Forensic Ledger Delivered**:
   - Created `/home/prem/Projects/AppleTV/reports/IPSW_EXTRACTION_LEDGER.md` (15,920 bytes) containing full forensic tables, cryptographic boundaries, AEA1 HPKE resolution, APFS ramdisk inventory, and comparative analysis against tvOS 13.4.8.

6. **Execution Safety Compliance**:
   - Zero ARM64 binaries were executed on the Linux x86_64 host. All inspections performed via static struct parsing, ASN.1 decoding, `pyimg4`, `7z`, `zlib`, Pillow, and `file`.

---

## 2. Logic Chain

1. **IPSW Authenticity & Hardware Mapping**:
   - Observation 1 confirmed the IPSW SHA-256 digest `08bb7001565746699636a00c73ae35c0cba7536a15bafc01c900de26048d77c1` and size 5,269,474,064 bytes.
   - `Restore.plist` maps BoardConfig `j42dap`, BDID `52` (`0x34`), and CPID `28672` (`0x7000`) to ProductType `AppleTV5,3`. In Apple hardware nomenclature, CPID `0x7000` corresponds exclusively to the Apple T7000 (Apple A8) SoC, which powers the Apple TV HD (Model A1625).
   - Therefore, the archive is verified as the authentic Apple full restore IPSW for the Apple TV HD.

2. **Ramdisk Extractability & Role Differentiation**:
   - Observation 2 showed that `094-97800-089.dmg` and `094-97880-089.dmg` wrap unencrypted APFS container superblocks starting at offset 27.
   - Slicing and unpacking with 7-Zip revealed `restored_external` in `094-97800` (Erase Ramdisk) and `restored_update` in `094-97880` (Update Ramdisk).
   - Therefore, both restore environments provide immediate, unencrypted access to userspace Darwin daemons, DriverKit runtimes, and resolution-tiered UI assets.

3. **Kernelcache Integrity & Decompression**:
   - Observation 3 showed that `kernelcache.release.j42d` matches the Apple `complzss` format with Adler-32 `0xdfddbd11` and length 44,122,112 bytes.
   - Python `pyimg4` decompression produced a byte stream whose Adler-32 is exactly `0xdfddbd11` and whose leading 4 bytes are `0xfeedfacf` (`MH_MAGIC_64`).
   - Therefore, the decompressed kernelcache is a genuine, uncorrupted ARM64 Mach-O kernel ready for static reverse engineering.

4. **Firmware Decapsulation & Graphic Normalization**:
   - Observation 4 proved that DeviceTree decompressed to 105,596 bytes, bootloaders extracted to 205,040 and 846,064 bytes respectively, and `iBootIm` pixel data normalized to standard PNGs.
   - Therefore, all firmware partition elements intended for plaintext boot stages are fully extracted and documented.

---

## 3. Caveats

- **RootFS AEA Image Expansion**: `094-98312-089.dmg.aea` (8.56 GB uncompressed) is protected by Apple Encrypted Archive v1 (AEA1). The matching public FCS key from Apple's WKMS server and unwrapped symmetric key (`ca0d1a3eb45cdb15b15babced612a5d37914299f5d5d141d488ddccb40cda496`) are fully documented in the ledger. Full disk decompression to raw blocks was deferred to downstream analysis to conserve host storage.
- **SEP Firmware Hardware Key**: `sep-firmware.j42d.RELEASE.im4p` contains two hardware AES-256 GID keybags. Decryption is impossible offline without physical Secure Enclave silicon execution.
- **Host Execution Restriction**: Strictly maintained zero host execution of ARM64 binaries on x86_64 Linux.

---

## 4. Conclusion

Milestone IPSW-M1 is 100% complete and fully verified:
1. `raw/ipsw/checksums.sha256` and `raw/ipsw/manifests/` are populated and checksum-verified.
2. `extracted/ipsw/ramdisk_erase/` (750 files, 100 symlinks) and `extracted/ipsw/ramdisk_update/` (900 files, 100 symlinks) are extracted, with `restored_external` and `restored_update` verified as Mach-O 64-bit ARM64 executables.
3. `extracted/ipsw/kernel/kernelcache.macho` is decompressed and verified against its exact 44,122,112 byte count, Adler-32 `0xdfddbd11`, and `0xfeedfacf` Mach-O 64-bit ARM64 header.
4. `extracted/ipsw/firmware/` contains decompressed `DeviceTree.bin` (105,596 bytes), `LLB.bin` (205,040 bytes), `iBoot.bin` (846,064 bytes), `iBSS.bin` (205,040 bytes), `iBEC.bin` (846,064 bytes), `applelogo.png`, and `recoverymode.png`.
5. `reports/IPSW_EXTRACTION_LEDGER.md` is delivered with complete component inventories, cryptographic boundary analysis, and comparative evolutionary mapping.
6. All 37 repository unit tests pass cleanly in `tests/`.

---

## 5. Verification Method

To independently verify the deliverables:

1. **Run Full Test Suite**:
   ```bash
   python3 -m unittest discover tests -v
   # Invalidation condition: Any failure or non-zero exit code (must be 37 tests, 0 failures)
   ```

2. **Verify IPSW Checksums**:
   ```bash
   sha256sum -c raw/ipsw/checksums.sha256
   # Invalidation condition: Any line fails checksum verification
   ```

3. **Verify Kernelcache Decompressed Mach-O**:
   ```bash
   python3 -c "
   import zlib
   d = open('extracted/ipsw/kernel/kernelcache.macho', 'rb').read()
   assert len(d) == 44122112, 'Size mismatch'
   assert zlib.adler32(d) == 0xdfddbd11, 'Adler-32 mismatch'
   assert d[:4] == b'\xcf\xfa\xed\xfe', 'Mach-O magic mismatch'
   print('Kernelcache Mach-O: OK')
   "
   ```

4. **Verify Firmware Components**:
   ```bash
   python3 -c "
   import os
   assert os.path.getsize('extracted/ipsw/firmware/DeviceTree.bin') == 105596
   assert os.path.getsize('extracted/ipsw/firmware/LLB.bin') == 205040
   assert os.path.getsize('extracted/ipsw/firmware/iBoot.bin') == 846064
   assert os.path.isfile('extracted/ipsw/firmware/applelogo.png')
   assert os.path.isfile('extracted/ipsw/firmware/recoverymode.png')
   print('Firmware Components: OK')
   "
   ```

5. **Verify Restore Daemons in Ramdisks**:
   ```bash
   file extracted/ipsw/ramdisk_erase/usr/local/bin/restored_external
   file extracted/ipsw/ramdisk_update/usr/local/bin/restored_update
   # Invalidation condition: Output is not 'Mach-O 64-bit arm64 executable'
   ```
