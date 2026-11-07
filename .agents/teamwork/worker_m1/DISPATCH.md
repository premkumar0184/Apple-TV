## 2026-11-06T17:37:15Z
You are Worker 1 (worker_m1) for Milestone 1 of the tvOS reverse engineering and architecture reconstruction project.
Your working directory is: /home/prem/Projects/AppleTV/.agents/teamwork/worker_m1
Workspace root: /home/prem/Projects/AppleTV

MANDATORY FIRST STEP:
Read /home/prem/Projects/AppleTV/.agents/teamwork/ORIGINAL_REQUEST.md before taking any action.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Context and Architecture:
- Read /home/prem/Projects/AppleTV/PROJECT.md
- Read Explorer 1 handoff: /home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_1/handoff.md
- Read Explorer 2 handoff: /home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_2/handoff.md
- Read Explorer 3 handoff: /home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_3/handoff.md

Your Exclusive Write Ownership:
- `/home/prem/Projects/AppleTV/raw/`
- `/home/prem/Projects/AppleTV/extracted/`
- `/home/prem/Projects/AppleTV/decoded/` (directory creation)
- `/home/prem/Projects/AppleTV/analysis/` (directory creation)
- `/home/prem/Projects/AppleTV/graphify-out/` (directory creation)
- `/home/prem/Projects/AppleTV/reports/`
- `/home/prem/Projects/AppleTV/scripts/`

Your Mission for Milestone 1 (Archive Forensics, Filesystem Extraction & Hierarchy Preservation):
1. Setup the 6-tier directory hierarchy:
   - `raw/manifests/`, `raw/firmware/`
   - `extracted/rootfs/Applications/`, `extracted/dyld_cache/`, `extracted/ramdisk/`, `extracted/kernel/`, `extracted/firmware/`
   - `decoded/assets/`, `decoded/strings/`, `decoded/plists/`, `decoded/nibs/`
   - `analysis/objc/`, `analysis/swift/`, `analysis/symbols/`, `analysis/ipc/`
   - `graphify-out/`
   - `reports/`
2. Populate `raw/`:
   - Compute and write `raw/checksums.sha256` containing SHA-256 hashes of the raw archive `8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip`, manifest plists, and BOM files.
   - Copy or link manifest plists into `raw/manifests/` (`BuildManifest.plist`, `Info.plist`, `ZipMetadata.plist`, `payload.bom`, `pre.bom`, `post.bom`).
   - Copy or link raw IM4P files into `raw/firmware/`.
3. Extract Ramdisk & Boot Components:
   - Unpack `arm64SURamDisk.dmg` / `038-50764-064.dmg.image-img4` (strip 27-byte ASN.1 header or run 7z) into `extracted/ramdisk/`. Verify extraction of framework directories and binaries.
   - Strip ASN.1 header from `kernelcache.release.j105a` and decompress LZFSE (`bvx2`) into `extracted/kernel/kernelcache.macho`.
   - Extract `DeviceTree.j105aap.im4p`, `applelogo~appletv.im4p`, `recoverymode@1080~appletv5.im4p` into `extracted/firmware/`.
4. Implement and run pure Python PBZX streaming extractor (`scripts/extract_payload.py`):
   - Use Explorer 3's verified 30-byte record format (`>HQQIHHHH`) with standard `lzma.decompress()`.
   - Process `AssetData/payloadv2/` to selectively unpack:
     - Core UI & System Applications: `PineBoard.app` (from `payload.017`), `HeadBoard.app` (from `payload.020` & `payload.018`), `PreBoard.app`, `Setup.app`, `TVSystemMenuService.app`, `TVSystemBulletinService.app`, `TVPeripheralAgent.app`, `TVIdleScreen.app`, `AppleTV.app`, `AppStore.app`.
     - Asset catalogs (`Assets.car`) across core applications and `CoreGlyphs.bundle`.
     - `dyld_shared_cache_arm64` from `payload.001` into `extracted/dyld_cache/dyld_shared_cache_arm64`.
   - Validate magic bytes (`0xfeedfacf` for 64-bit Mach-O, `BOMStore` for `.car`) on all extracted files.
5. Create `reports/EXTRACTION_LEDGER.md`:
   - Full inventory table of all unpacked files with byte sizes, paths, formats, and hashes.
   - Comprehensive technical section detailing the exact boundaries encountered (e.g. why bootloaders `LLB`, `iBoot`, `SEP` are hardware-encrypted under A10X silicon GID keys, while 100% of userspace applications, frameworks, ramdisk, and kernelcache are unencrypted).
6. Strict Host Execution Safety (R7):
   - Under no circumstances execute any of the extracted tvOS binaries on the host system.
7. Record detailed progress in `.agents/teamwork/worker_m1/progress.md`.
8. Write comprehensive handoff report to `.agents/teamwork/worker_m1/handoff.md`.
9. Send message to parent with summary and artifact paths.
