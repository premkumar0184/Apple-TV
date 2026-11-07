# BRIEFING — 2026-11-06T17:35:00Z

## Mission
Investigate tvOS archive payload files, pbzx/chunking format, extractability of rootfs/partitions/caches, and design the extraction architecture and directory layout separation.

## 🔒 My Identity
- Archetype: explorer
- Roles: explorer, extraction architecture investigator
- Working directory: /home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_3
- Original parent: 995e6d20-c347-437b-93ba-1b98ec79241b
- Milestone: Survey Phase - Extraction Architecture

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- Strictly adhere to R7: NEVER execute firmware binaries on the host
- Do NOT perform destructive full extraction in survey phase; test extraction cleanly/isolated if needed
- Write only to your own working directory: .agents/teamwork/explorer_survey_3

## Current Parent
- Conversation ID: 995e6d20-c347-437b-93ba-1b98ec79241b
- Updated: 2026-11-06T17:19:12Z

## Investigation State
- **Explored paths**: `8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip`, `AssetData/payloadv2/`, `AssetData/boot/`, `AssetData/payload/`, BOM files (`payload.bom`, `pre.bom`, `post.bom`), IM4P firmware containers, host disk capacity.
- **Key findings**:
  1. Archive contains 101 files, uncompressed size 2.08 GB.
  2. `payloadv2` contains 26 payload archives (`data_payload`, `payload.000` - `payload.024`) with 518 chunks (501 XZ compressed, 17 raw uncompressed, 0 LZFSE, 0 bzip2).
  3. Total decompressed payload is 4,210,309,961 bytes (~3.92 GB) at 2.22x compression.
  4. Decompressed stream follows an exact 30-byte record format (`>HQQIHHHH`) representing POSIX files/directories with byte-accurate consumption.
  5. `payload.001` contains the full 1.08 GB unencrypted `dyld_shared_cache_arm64`.
  6. All 38 tvOS applications (`PineBoard.app`, `HeadBoard.app`, `AppStore.app`, etc.) and their asset catalogs (`Assets.car`) are completely unencrypted.
  7. Ramdisk (`038-50764-064.dmg.image-img4`) is an unencrypted HFSX filesystem with volume `YagerG17M61.arm64SURamDisk`.
  8. Kernelcache is an unencrypted LZFSE (`bvx2`) Mach-O inside an IM4P container.
  9. Only early bootloaders (`LLB`, `iBoot`, `sep-firmware`, `iBEC`, `iBSS`) contain hardware GID KBAGs.
  10. Host available disk space is 4.3 GB, requiring a targeted/selective extraction strategy or consolidation of unzipped raw archives to avoid disk exhaustion.
- **Unexplored areas**: None within the survey scope; complete extraction architecture formulated.

## Key Decisions Made
- Confirmed pure Python streaming extraction architecture using built-in `lzma` and `struct` (no third-party dependencies required).
- Identified exact payload part locations for key binaries (PineBoard in payload.017, HeadBoard in payload.020, dyld cache in payload.001).
- Designed the 6-tier directory layout separation (`raw/`, `extracted/`, `decoded/`, `analysis/`, `graphify-out/`, `reports/`).

## Artifact Index
- DISPATCH.md — Initial dispatch message
- BRIEFING.md — Working memory index
- progress.md — Liveness heartbeat
- handoff.md — Comprehensive extraction architecture handoff report
