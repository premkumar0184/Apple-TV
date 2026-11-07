# Progress — auditor_ipsw_m1

- Status: Completed Phase 1 & Phase 2 Forensic Integrity Audit on Milestone IPSW-M1
- Last visited: 2026-11-06T21:43:00Z
- Verdict: CLEAN

## Verification Summary
1. `raw/ipsw/checksums.sha256`: Verified with `sha256sum -c` (All OK).
2. `raw/ipsw/manifests/`: Verified bit-for-bit against raw IPSW zip entries.
3. `extracted/ipsw/ramdisk_erase` & `extracted/ipsw/ramdisk_update`: Verified 750 and 900 genuine files, 100 resolved symlinks each, 0 empty files, authentic Mach-O binaries (`restored_external`, `restored_update`).
4. `extracted/ipsw/kernel/kernelcache.macho`: Verified exact 44,122,112 bytes, Adler-32 `0xdfddbd11`, Mach-O 64-bit ARM64 header, bit-for-bit match with independent decompression.
5. `extracted/ipsw/firmware/`: Verified `DeviceTree.bin`, `LLB.bin`, `iBoot.bin`, `iBSS.bin`, `iBEC.bin`, `applelogo.png`, `recoverymode.png` against raw IPSW IM4P containers.
6. Host Protection: Confirmed 0 ARM64 binary executions on Linux x86 host.
7. Test Suite: Ran `python3 -m unittest discover tests -v` — 37 tests passed cleanly in 4.7s.
8. `reports/IPSW_EXTRACTION_LEDGER.md`: 100% verified against physical disk and IPSW archive entries.
