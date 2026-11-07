# Execution Plan — AppleTV5,3 IPSW (23L781) Reverse Engineering

## Architecture
This project conducts deep, non-destructive, strictly static reverse engineering, filesystem extraction, AEA cryptographic evaluation, UI architecture reconstruction, REA binary analysis, Graphify knowledge graph expansion, and comparative reporting for the official Apple TV full restore IPSW (`AppleTV5,3_26.6.1_23L781_Restore.ipsw` / Build 23L781 / AppleTV5,3 / Apple TV HD A1625 / A8 T7000 SoC).

### Target Profile (Verified by Survey)
- **Archive File**: `AppleTV5,3_26.6.1_23L781_Restore.ipsw` (5,269,474,064 bytes)
- **SHA-256**: `08bb7001565746699636a00c73ae35c0cba7536a15bafc01c900de26048d77c1`
- **ProductType**: `AppleTV5,3` (Apple TV HD, Model A1625, DeviceClass `j42dap`)
- **Processor**: Apple A8 T7000 SoC (ApChipID `0x7000`, ApBoardID `0x34` / 52, ApSecurityDomain `0x01`)
- **OS Version & Build**: `Apple TVOS` 26.6.1, Build `23L781`, Restore Version `23.12.781.0.0`, BuildTrain `CharismaG`
- **Encryption & Cryptographic Boundaries**:
  - Restore Ramdisks (`094-97800-089.dmg` Erase, `094-97880-089.dmg` Upgrade): Unencrypted APFS containers inside 27-byte IM4P (`rdsk`) envelopes.
  - Kernelcache (`kernelcache.release.j42d`): Unencrypted `complzss` LZSS compressed (Adler-32 `0xdfddbd11`), yields 44.12 MB 64-bit ARM64 Mach-O kernel.
  - Bootloaders (`LLB`, `iBoot`, `iBSS`, `iBEC`): 100% plaintext ARM64 machine code.
  - DeviceTree (`DeviceTree.j42dap.im4p`): LZFSE compressed, plaintext.
  - Restore Graphics (`applelogo`, `recoverymode`): `iBootIm` LZSS images.
  - RootFS & Recovery AEA Containers (`094-98312-089.dmg.aea`, `094-98220-089.dmg.aea`): `AEA1` Profile 1 symmetric encryption. 256-bit symmetric keys recovered via RFC 9180 HPKE decapsulation using Apple's published FCS key on `wkms-public.apple.com`.
  - RootFS Manifest (`094-98312-089.dmg.aea.mtree`): Unencrypted AppleArchive (`AA01`) pbze stream containing complete file list, permissions, and SHA-256 hashes.
  - SEP Firmware: Hardware GID encrypted (unextractable offline without A8 silicon).

---

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---|---|---|---|
| 1 | Archive Hash & Manifest Forensics | Compute SHA-256, parse BuildManifest, Restore.plist, SystemVersion.plist, RestoreVersion.plist | IPSW-M1 | R1, survey |
| 2 | Unencrypted Ramdisk Extraction | Unpack 094-97800-089.dmg & 094-97880-089.dmg APFS containers via 7z into dedicated folders | IPSW-M1 | R2, survey |
| 3 | Kernelcache Decompression | Decompress kernelcache.release.j42d to 44.12MB Mach-O, verify Adler-32 match | IPSW-M1 | R2, survey |
| 4 | Firmware & Bootloader Extraction | Extract DeviceTree, LLB, iBoot, convert restore graphics (applelogo/recoverymode) to PNG | IPSW-M1 | R2, survey |
| 5 | Forensic Extraction Ledger | Authoritative ledger documenting all unpacked components, sizes, and hashes | IPSW-M1 | R1, R2, survey |
| 6 | AEA Header & Metadata Forensics | Analyze AEA1 headers, auth data, WKMS protobuf, and ciphersuites | IPSW-M2 | R2, survey |
| 7 | HPKE Key Decapsulation & Verification | Decapsulate RFC 9180 HPKE keys with Apple FCS key, derive AES keys, verify HMAC | IPSW-M2 | R2, survey |
| 8 | RootFS Mtree Manifest Decoding | Parse AA01 pbze stream to catalog full tvOS 26.6.1 rootfs directory tree | IPSW-M2 | R2, survey |
| 9 | AEA Boundary & Limits Report | Formally document cryptographic limits, why offline decryption without keys is infeasible, restore vs OTA | IPSW-M2 | R2, R6, survey |
| 10 | Recoverable UI Asset Extraction | Extract ProgressUI (1080p, 4K, 1x, 2x), TGA vector prompts, developer strap graphics | IPSW-M3 | R3, survey |
| 11 | Localization & Plist Cataloging | Catalog 112 plists and 38+ language bundles into structured JSON/markdown | IPSW-M3 | R3, survey |
| 12 | Comparative UI Evolution Analysis | Contrast with tvOS 13.4.8 (PineBoard, HeadBoard, Control Center, SwiftUI vs UIKit, focus engine) | IPSW-M3 | R3, survey |
| 13 | REA Binary Static Inspection | Analyze Mach-O headers, load commands, sections for restored_external, restored_update, iBoot | IPSW-M4 | R4, survey |
| 14 | Kernelcache Mach-O & Symbol Analysis | Analyze decompressed kernelcache Mach-O structure, sysent, drivers, Mach services | IPSW-M4 | R4, survey |
| 15 | Runtime Metadata & IPC Contracts | Extract Objective-C classes, Swift types, protocols, XPC/MIG interfaces | IPSW-M4 | R4, survey |
| 16 | Graphify Knowledge Graph Expansion | Ingest IPSW entities, filesystems, kernel symbols, AEA containers, and UI nodes | IPSW-M5 | R5, survey |
| 17 | Interactive Graph Visualization | Compile graph.json and interactive graph.html / index.html | IPSW-M5 | R5, survey |
| 18 | Master Technical Report | Produce exhaustive IPSW_TECHNICAL_REPORT.md covering all forensics, crypto, UI evolution, roadmap | IPSW-M5 | R6, survey |
| 19 | Execution Safety & Host Protection | Strictly static analysis — 0 executions of target ARM64 binaries on host | All | R7, survey |

---

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|---|---|---|---|
| IPSW-M1 | Firmware Forensics & Filesystem Unpacking | Features 1, 2, 3, 4, 5, 19 (R1, R2, R7) | Phase 0 (Survey) | READY |
| IPSW-M2 | AEA Cryptographic Boundary Evaluation | Features 6, 7, 8, 9, 19 (R2, R7) | IPSW-M1 | PLANNED |
| IPSW-M3 | UI Architecture, Asset Extraction & Comparative Evolution | Features 10, 11, 12, 19 (R3, R7) | IPSW-M1 | PLANNED |
| IPSW-M4 | Binary Analysis & REA Reverse Engineering | Features 13, 14, 15, 19 (R4, R7) | IPSW-M1 | PLANNED |
| IPSW-M5 | Graphify Knowledge Graph Expansion & Master Report | Features 16, 17, 18, 19 (R5, R6, R7) | IPSW-M2, IPSW-M3, IPSW-M4 | PLANNED |

---

## Iteration Loop Protocol per Milestone
Each milestone executes the mandatory quality cycle:
1. **Worker**: Implements extraction/analysis/reporting per recipes, produces evidence.
2. **Reviewers (2)**: Independent code & artifact review (APPROVE / REQUEST_CHANGES).
3. **Challengers (2)**: Adversarial stress testing, hash verification, and limit checks.
4. **Forensic Auditor**: Integrity verification (zero hardcoded fakes, authentic logic, host safety).
5. **Gate**: All 4 criteria must pass (AND) before advancing milestone.
