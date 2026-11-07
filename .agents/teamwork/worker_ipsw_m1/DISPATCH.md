## 2026-11-06T21:23:35Z
You are worker_ipsw_m1.
Your working directory is: /home/prem/Projects/AppleTV/.agents/teamwork/worker_ipsw_m1/
You must read /home/prem/Projects/AppleTV/.agents/teamwork/ORIGINAL_REQUEST.md before starting work.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Context & Explorer Handoffs:
Read the verified survey reports and extraction recipes prepared by the Survey Explorers:
- Archive & Manifests: /home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_ipsw_1/handoff.md
- Extraction Recipes: /home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_ipsw_2/handoff.md and /home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_ipsw_2/survey_firmware_ramdisk_report.md
- AEA & UI Findings: /home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_ipsw_3/handoff.md

Objective:
Execute Milestone IPSW-M1: Firmware Forensics & Filesystem Unpacking for `AppleTV5,3_26.6.1_23L781_Restore.ipsw`:
1. Checksum & Manifest Preservation:
   - Ensure directories `raw/ipsw/`, `raw/ipsw/manifests/`, `extracted/ipsw/`, `reports/` exist.
   - Record SHA-256 (`08bb7001565746699636a00c73ae35c0cba7536a15bafc01c900de26048d77c1`) and file size (`5,269,474,064`) in `raw/ipsw/checksums.sha256`.
   - Copy or extract the manifest plists (`BuildManifest.plist`, `Restore.plist`, `SystemVersion.plist`, `RestoreVersion.plist`) into `raw/ipsw/manifests/`.
2. Ramdisk Extraction:
   - Using the verified recipe with 7-Zip (`7z x`), extract the unencrypted APFS restore ramdisks from the IPSW:
     - `094-97800-089.dmg` (Erase Ramdisk) -> `extracted/ipsw/ramdisk_erase/`
     - `094-97880-089.dmg` (Upgrade Ramdisk) -> `extracted/ipsw/ramdisk_update/`
   - Verify that primary daemons (`usr/local/bin/restored_external`, `usr/local/bin/restored_update`) and system directories are successfully extracted.
3. Kernelcache Decompression:
   - Using the verified `pyimg4` recipe (or C/Python decompressor), decompress `kernelcache.release.j42d` into `extracted/ipsw/kernel/kernelcache.macho`.
   - Verify that the uncompressed size is exactly `44,122,112` bytes, Adler-32 checksum matches `0xdfddbd11`, and header starts with `0xfeedfacf` (Mach-O 64-bit ARM64).
4. Firmware Components Extraction:
   - In `extracted/ipsw/firmware/`:
     - Decompress `Firmware/all_flash/DeviceTree.j42dap.im4p` via `pyimg4`/`lzfse` to `DeviceTree.bin` (105,596 bytes).
     - Extract `LLB.j42d.RELEASE.im4p` and `iBoot.j42d.RELEASE.im4p` to `LLB.bin` (205,040 bytes) and `iBoot.bin` (846,064 bytes).
     - Decompress and convert `applelogo~appletv.im4p` and `recoverymode@1080~appletv5.im4p` to `applelogo.png` and `recoverymode.png`.
5. Extraction Ledger:
   - Create comprehensive forensic ledger in `/home/prem/Projects/AppleTV/reports/IPSW_EXTRACTION_LEDGER.md` documenting:
     - IPSW hash, size, and manifest properties.
     - Table of all files extracted across ramdisks, kernelcache, and firmware.
     - Byte counts, hashes, format descriptions, and cryptographic status (unencrypted vs AEA encrypted vs hardware GID encrypted SEP).
6. Execution Safety:
   - NEVER execute extracted ARM64 binaries on host.
7. Deliverables:
   - Report progress and results in `/home/prem/Projects/AppleTV/.agents/teamwork/worker_ipsw_m1/handoff.md`.
   - When complete, notify the orchestrator via send_message.
