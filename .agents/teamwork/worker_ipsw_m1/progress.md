# Progress — Milestone IPSW-M1: Firmware Forensics & Filesystem Unpacking

**Last visited**: 2026-11-06T21:35:00Z  
**Status**: COMPLETED  

## Tasks Checklist
- [x] 1. Checksum & Manifest Preservation:
  - [x] Ensure directories `raw/ipsw/`, `raw/ipsw/manifests/`, `extracted/ipsw/`, `reports/` exist.
  - [x] Record SHA-256 (`08bb7001565746699636a00c73ae35c0cba7536a15bafc01c900de26048d77c1`) and file size (`5,269,474,064`) in `raw/ipsw/checksums.sha256`.
  - [x] Copy or extract manifest plists (`BuildManifest.plist`, `Restore.plist`, `SystemVersion.plist`, `RestoreVersion.plist`) into `raw/ipsw/manifests/`.
- [x] 2. Ramdisk Extraction:
  - [x] Extract `094-97800-089.dmg` -> `extracted/ipsw/ramdisk_erase/` using `7z x`.
  - [x] Extract `094-97880-089.dmg` -> `extracted/ipsw/ramdisk_update/` using `7z x`.
  - [x] Verify primary daemons: `usr/local/bin/restored_external` and `usr/local/bin/restored_update`.
  - [x] Preserved 100 symlinks per partition, replacing 0-byte traversal placeholders with genuine relative symlinks.
- [x] 3. Kernelcache Decompression:
  - [x] Decompress `kernelcache.release.j42d` -> `extracted/ipsw/kernel/kernelcache.macho`.
  - [x] Verify size == `44,122,112` bytes, Adler-32 == `0xdfddbd11`, Mach-O 64-bit ARM64 magic `0xfeedfacf`.
- [x] 4. Firmware Components Extraction:
  - [x] `Firmware/all_flash/DeviceTree.j42dap.im4p` -> `extracted/ipsw/firmware/DeviceTree.bin` (105,596 bytes).
  - [x] `Firmware/all_flash/LLB.j42d.RELEASE.im4p` -> `extracted/ipsw/firmware/LLB.bin` (205,040 bytes).
  - [x] `Firmware/all_flash/iBoot.j42d.RELEASE.im4p` -> `extracted/ipsw/firmware/iBoot.bin` (846,064 bytes).
  - [x] `Firmware/dfu/iBSS.j42d.RELEASE.im4p` -> `extracted/ipsw/firmware/iBSS.bin` (205,040 bytes).
  - [x] `Firmware/dfu/iBEC.j42d.RELEASE.im4p` -> `extracted/ipsw/firmware/iBEC.bin` (846,064 bytes).
  - [x] `applelogo~appletv.im4p` -> `extracted/ipsw/firmware/applelogo.png` (108x131 LA PNG).
  - [x] `recoverymode@1080~appletv5.im4p` -> `extracted/ipsw/firmware/recoverymode.png` (582x154 RGBA PNG).
- [x] 5. Forensic Ledger:
  - [x] Create `/home/prem/Projects/AppleTV/reports/IPSW_EXTRACTION_LEDGER.md` documenting all 26 archive files, extracted partitions, cryptographic boundaries, and tvOS evolution.
- [x] 6. Self-Verification & Testing:
  - [x] Write `tests/test_ipsw_m1_integrity.py` covering all 8 verification vectors.
  - [x] All 37 project tests passing (0 failures, 0 regressions).
- [x] 7. Handoff & Orchestrator Notification:
  - [x] Write `handoff.md` and send completion message to parent.
