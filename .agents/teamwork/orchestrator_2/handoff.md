# Soft Handoff Report — orchestrator_2 -> orchestrator_3

**Predecessor**: `orchestrator_2` (`dca65d9e-caea-4f60-93bd-b30c8fc70405`)  
**Working Directory**: `/home/prem/Projects/AppleTV/.agents/teamwork/orchestrator_2/`  
**Parent Conversation ID**: `21e6a8b9-d755-42a8-a05b-ebe729b46187`  
**Target Firmware**: `AppleTV5,3_26.6.1_23L781_Restore.ipsw` (Build `23L781`, Model `AppleTV5,3` / Apple TV HD A1625 / A8 T7000 SoC)  
**Date**: 2026-11-06T22:08:00Z  

---

## 1. Milestone State

| Milestone | Scope | Dependencies | Status | Artifacts / Deliverables |
|---|---|---|---|---|
| Phase 0: Survey | Scope mapping, recipes, HPKE key recovery | none | **DONE** | Explorer survey reports 1, 2, 3; HPKE keys recovered; recipes verified |
| IPSW-M1 | Firmware Forensics & Filesystem Unpacking | Phase 0 | **DONE (PASS)** | `raw/ipsw/checksums.sha256`, `raw/ipsw/manifests/`, `extracted/ipsw/ramdisk_erase/`, `extracted/ipsw/ramdisk_update/`, `extracted/ipsw/kernel/kernelcache.macho`, `extracted/ipsw/firmware/`, `reports/IPSW_EXTRACTION_LEDGER.md`, `tests/test_ipsw_m1_integrity.py` (51 tests passing) |
| IPSW-M2 | AEA Cryptographic Boundary Evaluation | IPSW-M1 | **READY TO DISPATCH** | Scope in `plan.md § Milestone IPSW-M2`. Recipes & keys ready from `explorer_survey_ipsw_3/handoff.md` |
| IPSW-M3 | UI Architecture, Asset Extraction & Comparative Evolution | IPSW-M1 | **READY TO DISPATCH** | Scope in `plan.md § Milestone IPSW-M3`. Assets ready in ramdisks and firmware |
| IPSW-M4 | Binary Analysis & REA Reverse Engineering | IPSW-M1 | **READY TO DISPATCH** | Scope in `plan.md § Milestone IPSW-M4`. Binaries ready in ramdisks and `kernelcache.macho` |
| IPSW-M5 | Graphify Knowledge Graph Expansion & Master Report | IPSW-M2, M3, M4 | **PLANNED** | Master report `reports/IPSW_TECHNICAL_REPORT.md` and `graphify-out/` |

---

## 2. Active Subagents
- **Active subagents**: None (all 15 subagents have completed and delivered verified handoffs).

---

## 3. Pending Decisions & Key Technical Findings
1. **AEA Container Keys Already Recovered**:
   - `094-98312-089.dmg.aea` (RootFS 8.56 GB uncompressed) symmetric key:
     `ca0d1a3eb45cdb15b15babced612a5d37914299f5d5d141d488ddccb40cda496`
   - `094-98220-089.dmg.aea` (Recovery OS 186 MB uncompressed) symmetric key:
     `efd41ef06e0adc9426ae40d7c6635dbca5c88f68029411bf465a34c7c9baf7d9`
   - RootFS manifest is completely available unencrypted in `094-98312-089.dmg.aea.mtree` (AppleArchive AA01 format).
   - In IPSW-M2, produce `/home/prem/Projects/AppleTV/analysis/ipsw/AEA_CRYPTOGRAPHIC_REPORT.md` validating the HPKE RFC 9180 decryption, header segment tables, mtree catalog, and comparative analysis of AEA in Restore IPSWs vs OTA update packages.
2. **Recoverable UI Architecture & Evolution (IPSW-M3)**:
   - ProgressUI in `extracted/ipsw/ramdisk_erase/usr/share/progressui/` contains full resolution ladders (1080p, 4K, 1x, 2x) with RLE TGAs and PNGs.
   - 112 plists and 38+ language bundles available in ramdisks.
   - Compare tvOS 13.4.8 (Objective-C UIKit shell in `extracted/rootfs/Applications/` PineBoard, HeadBoard, TVSystemMenuService) vs tvOS 26.6.1 (modern Swift-first frameworks, DriverKit, Sealed System Volume, multi-resolution rendering). Produce `analysis/ipsw/UI_EVOLUTION_REPORT.md`.
3. **Binary Analysis with REA (IPSW-M4)**:
   - Target binaries: `extracted/ipsw/ramdisk_erase/usr/local/bin/restored_external`, `extracted/ipsw/ramdisk_update/usr/local/bin/restored_update`, `usr/libexec/diskimagesiod`, `usr/libexec/driverkitd`, `usr/sbin/asr`, `extracted/ipsw/firmware/iBoot.bin`, and `extracted/ipsw/kernel/kernelcache.macho` (44.12 MB).
   - Use REA static tools (Mach-O load commands, symbols, Objective-C classes, Swift types, IPC contracts). Produce `analysis/ipsw/BINARY_ANALYSIS_REPORT.md`.
4. **Graphify & Master Report (IPSW-M5)**:
   - Synthesize all findings into `reports/IPSW_TECHNICAL_REPORT.md` and update Graphify knowledge graph (`graphify-out/`).

---

## 4. Concrete Next Steps for Successor (`orchestrator_3`)
1. Create own working directory `.agents/teamwork/orchestrator_3/` (or inherit orchestrator_2).
2. Start background heartbeat cron (`schedule(CronExpression="*/10 * * * *")`).
3. Dispatch Milestone IPSW-M2 (`worker_ipsw_m2`), Milestone IPSW-M3 (`worker_ipsw_m3`), and Milestone IPSW-M4 (`worker_ipsw_m4`) — they are independent and can execute concurrently!
4. Drive each through the standard gate loop (Worker -> Reviewers -> Challengers -> Forensic Auditor).
5. Dispatch Milestone IPSW-M5 (Graphify expansion and master report generation) once M2-M4 complete.
6. Verify final test suite and report completion to parent agent `21e6a8b9-d755-42a8-a05b-ebe729b46187`.

---

## 5. Key Artifacts
- Plan: `/home/prem/Projects/AppleTV/.agents/teamwork/orchestrator_2/plan.md`
- Briefing: `/home/prem/Projects/AppleTV/.agents/teamwork/orchestrator_2/BRIEFING.md`
- Gate Status: `/home/prem/Projects/AppleTV/.agents/teamwork/orchestrator_2/GATE_STATUS.md`
- Ledger: `/home/prem/Projects/AppleTV/reports/IPSW_EXTRACTION_LEDGER.md`
- Test Suite: `/home/prem/Projects/AppleTV/tests/test_ipsw_m1_integrity.py` and `tests/test_ipsw_m1_adversarial.py` (51 tests passing)
- Survey Reports: `/home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_ipsw_{1,2,3}/handoff.md`
