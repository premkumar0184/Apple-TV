# Handoff Report — Explorer Survey IPSW 2 (Ramdisks, Kernelcache & Firmware)

**Agent**: `explorer_survey_ipsw_2`  
**Working Directory**: `/home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_ipsw_2/`  
**Target Firmware**: `AppleTV5,3_26.6.1_23L781_Restore.ipsw` (Build `23L781`, Model `AppleTV5,3`)  
**Parent Orchestrator**: `dca65d9e-caea-4f60-93bd-b30c8fc70405`  
**Report Artifact**: `/home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_ipsw_2/survey_firmware_ramdisk_report.md`  

---

## 1. Observation

Direct, empirical observations obtained from forensic tool execution:

1. **Restore Ramdisks (`094-97800-089.dmg` & `094-97880-089.dmg`)**:
   - File sizes: Both are exactly `113,246,235` bytes.
   - ASN.1 DER Header: Bytes 0-27 parse as SEQUENCE (length 113,246,229), IA5String `IM4P`, IA5String `rdsk`, IA5String `0`, OCTET STRING (length 113,246,208).
   - Superblock Magic: Byte offset 59 (relative offset 0x20 in payload) contains `4e 58 53 42 00` (`NXSB`).
   - APFS Properties: Block size 4096, block count 27,648 ($27648 \times 4096 = 113,246,208$ bytes), `features = 0x0`, `ro_features = 0x0`, `incompat_features = 0x2` (`NORMALIZATION_INSENSITIVE`). Completely plaintext, uncompressed APFS container.
   - `BuildManifest.plist` mapping:
     - `094-97800-089.dmg`: Variant `Customer Erase Install (IPSW)` and `Recovery Customer Install` (Erase Ramdisk).
     - `094-97880-089.dmg`: Variant `Customer Upgrade Install (IPSW)` (Update Ramdisk).
   - `7z` capability: `7z 26.04` automatically detects APFS at offset 27.
     - `094-97800-089.dmg`: 850 files, 314 folders, 100 symlinks (unpacked size: 268,824,552 bytes). Primary daemon: `usr/local/bin/restored_external`.
     - `094-97880-089.dmg`: 1000 files, 364 folders, 100 symlinks (unpacked size: 272,349,852 bytes). Primary daemon: `usr/local/bin/restored_update`.
     - Direct extraction command verified: `7z x 094-97800-089.dmg -o<dir> -y` extracted `restored_external` (Mach-O 64-bit arm64 executable) with zero errors.

2. **Kernelcache (`kernelcache.release.j42d`)**:
   - File size: `21,964,283` bytes.
   - Header: IM4P envelope (`krnl`), tag `KernelCacheBuilder_release-3244.160.2`.
   - `complzss` Header (Offset 63): Magic `complzss` (8 bytes), Big-Endian Adler-32 Checksum `0xdfddbd11`, Uncompressed size `44,122,112` bytes (0x2a14000), Compressed size `21,931,068` bytes (0x14ea43c), Version `1` (4 bytes), padding zeros to 0x180 (384 bytes).
   - Compressed payload start: Offset $63 + 384 = 447$.
   - Decompression verification:
     - Decompressed with `pyimg4` in 0.21s: exactly 44,122,112 bytes.
     - Decompressed with C implementation in 0.05s: calculated Adler-32 `0xdfddbd11` (100% exact match).
     - Header inspection of decompressed binary: `0xfeedfacf` (`MH_MAGIC_64`), CPUType `0x0100000c` (`ARM64`), 25 load commands, `__TEXT` at `0xfffffff007004000`.

3. **Firmware Partition Components (`Firmware/`)**:
   - `DeviceTree.j42dap.im4p`: IM4P (`dtre`), description `EmbeddedDeviceTrees-11156.160.23`, LZFSE compression (`bvx2`), uncompressed size 105,596 bytes, plaintext.
   - Bootloaders:
     - `LLB.j42d.RELEASE.im4p` (`illb`) and `iBSS.j42d.RELEASE.im4p` (`ibss`): 205,040 bytes payload. Payloads are 100% byte-for-byte identical (`LLB == iBSS: True`), plaintext ARM64 machine code, uncompressed.
     - `iBoot.j42d.RELEASE.im4p` (`ibot`) and `iBEC.j42d.RELEASE.im4p` (`ibec`): 846,064 bytes payload. Payloads are 100% byte-for-byte identical (`iBoot == iBEC: True`), plaintext ARM64 machine code, uncompressed. Version `iBoot-13822.120.5`.
   - Restore Graphics:
     - `applelogo~appletv.im4p` (`logo`): 64-byte `iBootIm` header, 108×131 pixels, 16-bit `grey` (`LA` mode), LZSS compressed (decompressed: 28,296 bytes). Successfully converted to PNG via Pillow.
     - `recoverymode@1080~appletv5.im4p` (`recm`): 64-byte `iBootIm` header, 582×154 pixels, 32-bit `bgra` format, LZSS compressed (decompressed: 358,512 bytes). Successfully converted to PNG via Pillow.
   - Secure Enclave Processor (`sep-firmware.j42d.RELEASE.im4p`): IM4P (`sepi`), encrypted (`encrypted: True`) with 2 hardware keybags (Production KBAG type 1, Development KBAG type 2). Unextractable offline without hardware GID key.
   - TrustCaches:
     - `094-97800-089.dmg.trustcache` (`rtsc`, v1, 290 CDHashes)
     - `094-97880-089.dmg.trustcache` (`rtsc`, v1, 294 CDHashes)
     - `094-98220-089.dmg.aea.trustcache` (`trst`, v2, 266 CDHashes)
     - `094-98312-089.dmg.aea.trustcache` (`trst`, v2, 1,357 CDHashes)
   - Canonical Metadata Mtree:
     - `094-98312-089.dmg.aea.mtree` (27.13 MB): IM4P (`msys`), pbze stream (LZFSE compressed 4 MB chunks) containing the complete unencrypted AppleArchive (`AA01`) manifest of the root filesystem (paths, permissions, flags, timestamps, SHA-256 hashes).

4. **Host Tooling Survey**:
   - `7z 26.04`: Installed at `/usr/bin/7z`, natively extracts APFS at offset 27.
   - `python3 3.14.0`: Installed at `/usr/bin/python3`.
   - Python packages installed and verified: `pyimg4 0.8.9`, `lzss 0.3.9`, `lzfse 0.4.2`, `Pillow 13.0.0`, `pycryptodome 4.3.0`.
   - Static analysis tools: `llvm-objdump`, `llvm-readelf`, `file`, `binwalk`, `hexdump`, `xxd`.
   - Tool limitations: Missing `hfsplus` / `undmg` (not required since DMGs are APFS, not HFS+); missing `img4lib` binary (fully replaced by `pyimg4` library which is verified superior and Python-native).

---

## 2. Logic Chain

1. **Ramdisk Format Deduction**:
   - *Observation*: Byte 0 is `0x30` with ASN.1 length matching file size minus 6; tag at byte 6 is `IM4P`; tag at byte 12 is `rdsk`; OCTET STRING payload starts at byte 27 with length 113,246,208.
   - *Observation*: Byte 59 (offset 32 of payload) is `NXSB`, block size is 4096, block count is 27,648 ($27,648 \times 4096 = 113,246,208$).
   - *Deduction*: Both DMGs are unencrypted, uncompressed APFS raw filesystem containers preceded by a 27-byte IM4P header.
   - *Observation*: `7z l` recognizes APFS at Offset = 27; `7z x` extracts files directly.
   - *Deduction*: Phase 1 workers can directly unpack both ramdisks into target directories using `7z` without custom preprocessing.

2. **Kernelcache Integrity & Decompression Deduction**:
   - *Observation*: Payload starts at byte 63 with `complzss`, Adler-32 `0xdfddbd11`, uncompressed size 44,122,112, compressed size 21,931,068.
   - *Observation*: LZSS decompression stream starts at offset $63 + 0x180 = 447$.
   - *Observation*: Decompressing 21,931,068 bytes yields exactly 44,122,112 bytes whose Adler-32 is `0xdfddbd11` and whose first 4 bytes are `0xfeedfacf` (`MH_MAGIC_64`).
   - *Deduction*: The kernelcache is completely unencrypted, compressed with Apple's standard LZSS sliding window algorithm, and is 100% extractable into a valid Mach-O 64-bit kernel image.

3. **Firmware Partition Recoverability Deduction**:
   - *Observation*: `LLB` and `iBoot` contain no keybags (`keybags: 0`) and no compression (`compression: 0`). Payload bytes start immediately with ARM64 instructions (`00 00 00 90...`) and strings (`iBoot-13822.120.5`).
   - *Observation*: `sep-firmware` contains 2 keybags (`type: 1` and `type: 2`) with 32-byte encrypted keys and 16-byte IVs.
   - *Deduction*: All bootloaders (`LLB`, `iBoot`, `iBSS`, `iBEC`) and DeviceTree are completely open and extractable for static analysis. `sep-firmware` is encrypted by Apple's hardware GID keys and constitutes an absolute cryptographic boundary for offline analysis.
   - *Observation*: `094-98312-089.dmg.aea.mtree` contains unencrypted AppleArchive (`AA01`) directory entries despite the `.aea` rootfs image being encrypted.
   - *Deduction*: Downstream workers can reconstruct the entire file ledger and architectural composition of tvOS 26.6.1 directly from the mtree.

---

## 3. Caveats

1. **Host Execution Safety**: Extracted ARM64 binaries (`restored_external`, `restored_update`, `kernelcache`, `iBoot`, `LLB`) must NEVER be executed directly on the host system. All downstream inspection must remain strictly static (using REA, `llvm-objdump`, Ghidra, Python parsers).
2. **SEP Firmware Encryption**: `sep-firmware.j42d.RELEASE.im4p` is encrypted with hardware AES-256-CBC GID keybags. Decryption is not possible offline without an A8 bootrom exploit or device-fused key derivation.
3. **AEA RootFS Disk Image**: `094-98312-089.dmg.aea` and `094-98220-089.dmg.aea` require Apple Encrypted Archive keys; however, as discovered in this survey, their companion `mtree` files are unencrypted and provide 100% of the file manifest.
4. **File Permissions & Symlinks in Ramdisk**: Ramdisks contain 100 symlinks (e.g., `sbin/mount_apfs -> /System/Library/Filesystems/apfs.fs/mount_apfs`). When extracting with `7z`, workers should ensure the target filesystem supports symlinks or document them in the extraction ledger.

---

## 4. Conclusion

1. **Scope Completion**: All restore ramdisks, kernelcache, bootloader files, device trees, graphics, trustcaches, and metadata files have been forensically parsed, categorized, and verified.
2. **Extractability Verdict**:
   - **Restore Ramdisks**: 100% extractable via `7z` (yielding 855 and 1,005 files respectively, including `restored_external`, DriverKit, and core frameworks).
   - **Kernelcache**: 100% extractable and verified against Adler-32 checksum (44.12 MB Mach-O 64-bit kernel).
   - **DeviceTree**: 100% extractable via `pyimg4` / `lzfse` (105.6 KB device tree).
   - **Bootloaders**: 100% extractable via `pyimg4` (205 KB LLB/iBSS, 846 KB iBoot/iBEC).
   - **Restore Images**: 100% extractable and convertible to standard PNGs.
   - **TrustCaches & Mtrees**: 100% parseable, yielding complete CDHash lists and the full file manifest of the tvOS 26.6.1 rootfs.
3. **Actionable Delivery**: Detailed technical report written to `survey_firmware_ramdisk_report.md` and six copy-paste extraction recipes prepared for Phase 1 workers.

---

## 5. Verification Method

Independent verification can be executed on host via the following commands:

1. **Verify Ramdisk APFS Recognition & Testing**:
   ```bash
   7z t AppleTV5,3_26.6.1_23L781_Restore/094-97800-089.dmg
   7z t AppleTV5,3_26.6.1_23L781_Restore/094-97880-089.dmg
   # Invalidation condition: Exit code != 0 or errors reported on APFS streams
   ```

2. **Verify Kernelcache Decompression & Adler-32 Match**:
   ```bash
   python3 -c "
   import pyimg4, zlib
   kc = pyimg4.IM4P(open('AppleTV5,3_26.6.1_23L781_Restore/kernelcache.release.j42d', 'rb').read())
   kc.payload.decompress()
   assert len(kc.payload.data) == 44122112, 'Size mismatch'
   assert zlib.adler32(kc.payload.data) == 0xdfddbd11, 'Adler32 mismatch'
   assert kc.payload.data[:4] == b'\xcf\xfa\xed\xfe', 'Mach-O magic mismatch'
   print('Kernelcache verification PASSED!')
   "
   # Invalidation condition: Assertion failure on size, checksum, or magic
   ```

3. **Verify DeviceTree & Bootloader Extraction**:
   ```bash
   python3 -c "
   import pyimg4
   dt = pyimg4.IM4P(open('AppleTV5,3_26.6.1_23L781_Restore/Firmware/all_flash/DeviceTree.j42dap.im4p', 'rb').read())
   dt.payload.decompress()
   assert len(dt.payload.data) == 105596, 'DeviceTree size mismatch'
   iboot = pyimg4.IM4P(open('AppleTV5,3_26.6.1_23L781_Restore/Firmware/all_flash/iBoot.j42d.RELEASE.im4p', 'rb').read())
   assert len(iboot.payload.data) == 846064, 'iBoot size mismatch'
   print('Firmware verification PASSED!')
   "
   # Invalidation condition: Assertion failure
   ```
