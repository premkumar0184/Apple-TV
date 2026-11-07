# Project: Apple TV (tvOS 13.4.8) Reverse Engineering & Architecture Reconstruction

## Architecture
This project conducts deep, non-destructive, strictly static reverse engineering, filesystem extraction, UI stack reconstruction, REA binary inspection, and Graphify knowledge graph generation for Apple TV 4K (tvOS 13.4.8, Build 17M61, AppleTV6,2 / j105aap).

### Target Profile 1: OTA SoftwareUpdate (tvOS 13.4.8)
- **Archive File**: `8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip` (2,014,940,073 bytes)
- **SHA-256**: `8725797b4ddfd93fc67023c93c1d9277f128e9731a9ac18618b9b2e812c027c1`
- **Package Format**: Apple MobileAsset SoftwareUpdate package (PackageVersion 3.0)
- **OS Version & Build**: tvOS 13.4.8 (17M61, Train: YagerG)
- **Hardware Profile**: Apple TV 4K 1st Gen (Model A1842, DeviceClass `j105aap`, ProductType `AppleTV6,2`)
- **Processor**: Apple A10X Fusion SoC (T8011, ApChipID `0x8011`, ApBoardID `0x02`)
- **Encryption Status**: Userspace rootfs, applications, frameworks, asset catalogs, ramdisk, and kernelcache are 100% UNENCRYPTED. Early bootloaders (`LLB`, `iBoot`, `SEP`) contain hardware GID KBAGs.

### Target Profile 2: Full Restore IPSW (tvOS 26.6.1)
- **Archive File**: `AppleTV5,3_26.6.1_23L781_Restore.ipsw` (5,269,474,064 bytes)
- **SHA-256**: `08bb7001565746699636a00c73ae35c0cba7536a15bafc01c900de26048d77c1`
- **Package Format**: Official Apple Full Restore IPSW (ZIP container)
- **OS Version & Build**: tvOS 26.6.1 (Build `23L781`, Restore Version `23.12.781.0.0`, Train: `CharismaG`)
- **Hardware Profile**: Apple TV HD (Model A1625, DeviceClass `j42dap`, ProductType `AppleTV5,3`)
- **Processor**: Apple A8 T7000 SoC (ApChipID `0x7000`, ApBoardID `0x34` / 52)
- **Encryption Status**: RootFS & Recovery OS protected by Apple Encrypted Archive v1 (AEA1 Profile 1); unencrypted restore ramdisks, kernelcache, and bootloaders. Symmetric archive keys recovered via RFC 9180 HPKE decapsulation.

### Preserved Workspace Layout
1. `raw/`: Immutable input archives, checksums, raw boot manifests (`raw/manifests/`, `raw/ipsw/manifests/`), and BOM files.
2. `extracted/`: Unpacked filesystem partitions (`extracted/rootfs/`, `extracted/ipsw/ramdisk_erase/`, `extracted/ipsw/ramdisk_update/`, `extracted/ipsw/kernel/`, `extracted/ipsw/firmware/`).
3. `decoded/`: Extracted asset catalogs (`.car`), decoded NIBs/storyboards, and normalized string tables.
4. `analysis/`: REA static analysis outputs, Objective-C/Swift class hierarchies, symbol tables, dependency matrices, IPC contracts (`analysis/`, `analysis/ipsw/`).
5. `graphify-out/`: Graphify knowledge graph (`graph.json` [775 nodes, 1545 links, 9 communities], interactive `graph.html` / `index.html`, and `GRAPH_REPORT.md`).
6. `reports/`: Comprehensive `TECHNICAL_REPORT.md`, `IPSW_TECHNICAL_REPORT.md`, `EXTRACTION_LEDGER.md`, and `IPSW_EXTRACTION_LEDGER.md`.

---

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---|---|---|---|
| 1 | Archive Hash & Identity Forensics | Verify SHA-256, package format, OS build 17M61, device profile A1842/j105a | M1 | R1, survey |
| 2 | Manifest & BOM Parsing | Parse BuildManifest.plist, Info.plist, ZipMetadata, and decode post.bom | M1 | R1, survey |
| 3 | Directory Layout Preservation | Enforce preserved directory separation (`raw/`, `extracted/`, `decoded/`, `analysis/`, `graphify-out/`, `reports/`) | M1, IPSW-M1 | R2, survey |
| 4 | Ramdisk & Boot Firmware Extraction | Strip ASN.1 headers, unpack HFSX arm64SURamDisk via 7z, extract kernelcache, devicetree, boot logos | M1 | R2, survey |
| 5 | PBZX Streaming Filesystem Extraction | Pure Python streaming extraction of system apps (PineBoard, HeadBoard, Setup, TVSystemMenuService), dyld cache, and asset catalogs | M1 | R2, survey |
| 6 | Forensic Extraction Ledger | Document every unpacked file, byte counts, hashes, and technical explanation for encrypted bootloaders | M1, IPSW-M1 | R1, R2, survey |
| 7 | UI Asset Catalog Extraction | Inspect and decode compiled `.car` files (HeadBoard, PineBoard, CoreGlyphs, AppStore) into assets and metadata | M2 | R3, survey |
| 8 | Storyboard & NIB Reverse Engineering | Decode compiled interface builder files using REA `decode_interface_builder` | M2 | R3, survey |
| 9 | UI Localization & Strings Cataloging | Extract and normalize localization `.strings` into JSON catalogs | M2, IPSW-M3 | R3, survey |
| 10 | TV Shell & Window Manager Architecture | Reconstruct PineBoard compositor, HeadBoard home grid, Top Shelf, and PreBoard lifecycle | M2, IPSW-M3 | R3, survey |
| 11 | Focus Engine & Remote Interaction Analysis | Model UIFocusEngine navigation graph, Siri Remote touch, button events, and TouchRemote interaction | M2, IPSW-M3 | R3, survey |
| 12 | System UI Services Modeling | Model TVSystemMenuService (Control Center) and TVSystemBulletinService (alerts/HUD) | M2, IPSW-M3 | R3, survey |
| 13 | REA Mach-O Inspection & Symbol Analysis | Extract Mach-O slices, load commands, entry points, exported symbols for core binaries via REA | M3, IPSW-M4 | R4, survey |
| 14 | Objective-C & Swift Metadata Extraction | Extract ObjC class hierarchies, ivars, protocols, methods, and Swift types for PineBoard, HeadBoard, TVKit | M3, IPSW-M4 | R4, survey |
| 15 | System Framework Dependency Graph | Reconstruct dependency graph between UIKit, SwiftUI, TVSystemUI, TVKit, and PineBoardServices | M3, IPSW-M4 | R4, survey |
| 16 | Inter-Process Communication (IPC) Mapping | Map Mach services, NSXPC interfaces, and notification centers connecting PineBoard and applications | M3, IPSW-M4 | R4, survey |
| 17 | Graphify Knowledge Graph Construction | Generate `graphify-out/graph.json` mapping firmware, binaries, UI components, and services | M4, IPSW-M5 | R5, survey |
| 18 | Interactive HTML Graph Visualizer | Compile interactive graph visualization HTML (`graph.html` / `index.html`) | M4, IPSW-M5 | R5, survey |
| 19 | Graphify Structural Report | Generate `graphify-out/GRAPH_REPORT.md` with cluster detection and god node analysis | M4, IPSW-M5 | R5, survey |
| 20 | Comprehensive Technical Report | Exhaustive architectural report `reports/TECHNICAL_REPORT.md` and `reports/IPSW_TECHNICAL_REPORT.md` | M4, IPSW-M5 | R6, survey |
| 21 | Execution Safety & Host Protection | Strictly static analysis — 0 executions of target ARM64 binaries on host | All | R7, survey |
| 22 | IPSW AEA Cryptographic Boundary Evaluation | Analyze AEA1 containers, WKMS escrow, and execute RFC 9180 HPKE key decapsulation | IPSW-M2 | R2, survey |
| 23 | RootFS Mtree Manifest Forensics | Decompress pbze stream, decode AppleArchive (AA01) mtree.txt (856,252 lines, 54 apps) | IPSW-M2 | R2, survey |
| 24 | Multi-Resolution ProgressUI Extraction | Extract 1080p, 4K UHD, 1x, 2x, and $1536 \times 2048$ vector prompts | IPSW-M3 | R3, survey |
| 25 | Comparative UI Stack Evolution | Model transition from Objective-C UIKit to Swift-first Modular Control Center, FaceTime, and Sing | IPSW-M3 | R3, survey |
| 26 | Kernelcache Mach-O & KEXT Fileset Analysis | Disassemble 44.12 MB kernelcache, parse 167 unique KEXT manifests, Darwin 25.6.0 | IPSW-M4 | R4, survey |
| 27 | Early Bootloader Inspection | Static inspection of LLB.bin and iBoot.bin (iBoot-13822.120.5) | IPSW-M4 | R4, survey |

---

## Milestones
| # | Name | Scope | Dependencies | Status | Deliverables |
|---|---|---|---|---|---|
| M1 | Archive Forensics & Filesystem Extraction (OTA) | Features 1, 2, 3, 4, 5, 6, 21 | none | **DONE (PASS)** | `raw/manifests/`, `extracted/rootfs/`, `reports/EXTRACTION_LEDGER.md` |
| M2 | UI Architecture & Asset Reverse Engineering (OTA) | Features 7, 8, 9, 10, 11, 12, 21 | M1 | **DONE (PASS)** | `decoded/`, `analysis/UI_STACK_REPORT.md` |
| M3 | Binary Analysis & REA Reverse Engineering (OTA) | Features 13, 14, 15, 16, 21 | M1 | **DONE (PASS)** | `analysis/BINARY_ANALYSIS_REPORT.md` |
| M4 | Graphify Knowledge Graph & Technical Report (OTA) | Features 17, 18, 19, 20, 21 | M2, M3 | **DONE (PASS)** | `graphify-out/`, `reports/TECHNICAL_REPORT.md` |
| IPSW-M1 | Firmware Forensics & Filesystem Unpacking | Features 1, 2, 3, 4, 5, 6, 21 | Phase 0 Survey | **DONE (PASS)** | `raw/ipsw/`, `extracted/ipsw/`, `reports/IPSW_EXTRACTION_LEDGER.md` |
| IPSW-M2 | AEA Cryptographic Boundary Evaluation | Features 22, 23, 21 | IPSW-M1 | **DONE (PASS)** | `analysis/ipsw/AEA_CRYPTOGRAPHIC_REPORT.md` |
| IPSW-M3 | UI Architecture, Asset Extraction & Evolution | Features 24, 25, 21 | IPSW-M1 | **DONE (PASS)** | `analysis/ipsw/UI_EVOLUTION_REPORT.md` |
| IPSW-M4 | Binary Analysis & REA Reverse Engineering | Features 26, 27, 21 | IPSW-M1 | **DONE (PASS)** | `analysis/ipsw/BINARY_ANALYSIS_REPORT.md` |
| IPSW-M5 | Graphify Knowledge Graph & Master Report | Features 17, 18, 19, 20, 21 | IPSW-M2..M4 | **DONE (PASS)** | `graphify-out/` (775 nodes, 9 communities), `reports/IPSW_TECHNICAL_REPORT.md` |

---

## Interface Contracts

### M1 (Extraction) ↔ M2 (UI & Assets)
- **Extracted Rootfs Path**: `extracted/rootfs/Applications/`
  - `PineBoard.app/`: Contains `Info.plist`, `Assets.car`, `PineBoard` binary, localization resources.
  - `HeadBoard.app/`: Contains `Info.plist`, `Assets.car`, `HeadBoard` binary, localization resources.
  - `PreBoard.app/`, `Setup.app/`, `TVSystemMenuService.app/`, `TVSystemBulletinService.app/`.
- **Extracted Asset Catalogs**: `extracted/rootfs/Applications/*/*.car` and `extracted/rootfs/System/Library/CoreServices/CoreGlyphs.bundle/Assets.car`.
- **Extracted Ramdisk Path**: `extracted/ramdisk/` (HFSX partition contents).
- **Manifests & Ledger**: `raw/manifests/` and `reports/EXTRACTION_LEDGER.md`.

### M1 (Extraction) ↔ M3 (Binary Analysis)
- **Target Binaries**:
  - `extracted/rootfs/Applications/PineBoard.app/PineBoard` (Mach-O 64-bit executable arm64)
  - `extracted/rootfs/Applications/HeadBoard.app/HeadBoard` (Mach-O 64-bit executable arm64)
  - `extracted/rootfs/Applications/PreBoard.app/PreBoard`
  - `extracted/dyld_cache/dyld_shared_cache_arm64` (1.08 GB unified library cache)
  - `extracted/kernel/kernelcache.macho`
- **Symbols & Metadata**: Extracted binaries are untouched ARM64 Mach-O files ready for REA static tool ingestion.

### M2 (UI Stack) & M3 (Binaries) ↔ M4 (Graphify & Reporting)
- **UI Architecture Model**: `analysis/UI_STACK_REPORT.md` (component taxonomy, focus hierarchy, remote mapping, asset index).
- **Binary Analysis Model**: `analysis/BINARY_ANALYSIS_REPORT.md` (class hierarchies, exported symbols, IPC endpoints, framework dependency matrices).
- **Decoded Assets Catalog**: `decoded/` index mapping all UI assets, colors, and string keys.
- **Graphify Input**: JSON and markdown metadata ready for AST/Semantic parsing in `graphify-out/`.

---

## Code Layout
```
/home/prem/Projects/AppleTV/
├── PROJECT.md
├── raw/
│   ├── checksums.sha256
│   ├── manifests/
│   │   ├── BuildManifest.plist
│   │   ├── Info.plist
│   │   ├── payload.bom
│   │   └── post.bom
│   └── firmware/
├── extracted/
│   ├── rootfs/
│   │   ├── Applications/
│   │   │   ├── PineBoard.app/
│   │   │   ├── HeadBoard.app/
│   │   │   ├── Setup.app/
│   │   │   ├── PreBoard.app/
│   │   │   ├── TVSystemMenuService.app/
│   │   │   └── TVSystemBulletinService.app/
│   │   └── System/Library/
│   ├── dyld_cache/
│   │   └── dyld_shared_cache_arm64
│   ├── ramdisk/
│   └── kernel/
├── decoded/
│   ├── assets/
│   ├── strings/
│   ├── plists/
│   └── nibs/
├── analysis/
│   ├── UI_STACK_REPORT.md
│   ├── BINARY_ANALYSIS_REPORT.md
│   ├── objc/
│   ├── swift/
│   ├── symbols/
│   └── ipc/
├── graphify-out/
│   ├── graph.json
│   ├── graph.html
│   └── GRAPH_REPORT.md
└── reports/
    ├── TECHNICAL_REPORT.md
    └── EXTRACTION_LEDGER.md
```
