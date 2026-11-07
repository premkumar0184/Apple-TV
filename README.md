# Apple TV (tvOS) Deep Reverse Engineering & UI Architecture Analysis

An evidence-based reverse engineering investigation and architectural reconstruction of the official Apple TV operating system, analyzing both **Apple TV 4K (1st Gen, tvOS 13.4.8)** and **Apple TV HD (tvOS 26.6.1 / Build 23L781 Restore IPSW)**.

This repository contains all technical reports, reverse-engineering analyses, decoded user interface assets, extraction scripts, automated test suites, multi-agent orchestration logs, and an interactive **Graphify** knowledge graph.

> [!NOTE]
> All investigations were conducted using strictly non-destructive static analysis with **zero (0) host executions of ARM64 firmware binaries**. In compliance with copyright best practices and GitHub size limits, all raw proprietary Apple firmware containers, DMGs, and Mach-O binaries are excluded via `.gitignore`.

---

## 📑 Core Documentation Index

| Domain | Document | Description |
| :--- | :--- | :--- |
| **Restore IPSW Master Report** | [`reports/IPSW_TECHNICAL_REPORT.md`](reports/IPSW_TECHNICAL_REPORT.md) | Comprehensive report on tvOS 26.6.1 (Build `23L781`), AEA decapsulation, APFS ramdisks, and UI evolution |
| **tvOS 13.4.8 Master Report** | [`reports/TECHNICAL_REPORT.md`](reports/TECHNICAL_REPORT.md) | Baseline architectural study on tvOS 13.4.8 (Build `17M61`), PineBoard compositor, and Focus Engine |
| **IPSW Extraction Ledger** | [`reports/IPSW_EXTRACTION_LEDGER.md`](reports/IPSW_EXTRACTION_LEDGER.md) | Cryptographic ledger validating all 56 on-disk components, offsets, and SHA-256 digests |
| **OTA Extraction Ledger** | [`reports/EXTRACTION_LEDGER.md`](reports/EXTRACTION_LEDGER.md) | Forensic ledger for tvOS 13.4.8 streaming PBZX multi-chunk unpack |
| **AEA Cryptographic Report** | [`analysis/ipsw/AEA_CRYPTOGRAPHIC_REPORT.md`](analysis/ipsw/AEA_CRYPTOGRAPHIC_REPORT.md) | RFC 9180 HPKE WKMS key exchange decapsulation, symmetric keys, and 371k-file RootFS mtree |
| **UI Evolution Report** | [`analysis/ipsw/UI_EVOLUTION_REPORT.md`](analysis/ipsw/UI_EVOLUTION_REPORT.md) | Multi-scale ProgressUI asset ladders, 112 plists, and tvOS 13.4.8 $\rightarrow$ 26.6.1 UI evolution |
| **IPSW Binary Analysis** | [`analysis/ipsw/BINARY_ANALYSIS_REPORT.md`](analysis/ipsw/BINARY_ANALYSIS_REPORT.md) | Static Mach-O reverse engineering of restore daemons, iBoot-13822, and Darwin 25.6.0 kernel |
| **UI Stack Architecture** | [`analysis/UI_STACK_REPORT.md`](analysis/UI_STACK_REPORT.md) | Out-of-process compositor (`PineBoard`), SpringBoard (`HeadBoard`), and Control Center overlay |
| **Focus Engine & Physics** | [`analysis/focus_engine/FOCUS_ENGINE_ANALYSIS.md`](analysis/focus_engine/FOCUS_ENGINE_ANALYSIS.md) | 2D cone raycasting, 3D card parallax vectors, and Siri Remote Bluetooth LE HID pipeline |
| **Objective-C Taxonomy** | [`analysis/objc/OBJC_CLASS_INDEX.md`](analysis/objc/OBJC_CLASS_INDEX.md) | Statically extracted catalog of 607 classes, 9,935 methods, and 2,558 ivars |
| **Swift 5 & Metal Analysis** | [`analysis/swift/SWIFT_ANALYSIS.md`](analysis/swift/SWIFT_ANALYSIS.md) | Swift reflection types, metadata records, and Metal audio-visualizer shaders in `TVMusic` |
| **IPC & Mach Services** | [`analysis/ipc/IPC_CONTRACTS.md`](analysis/ipc/IPC_CONTRACTS.md) | Mach ports, XPC endpoints, and `NSXPCInterface` contracts (`PBSSystemService`, TopShelf) |

---

## 🔍 Key Technical Breakthroughs

### 1. AEA Container Decapsulation & RFC 9180 HPKE Reverse Engineering
- Modern restore images encapsulate system partitions in **Apple Encrypted Archive v1 (AEA1)** format.
- Dissected Apple's Wrapped Key Management Service (WKMS) schema implementing **RFC 9180 HPKE**:
  - **KEM**: `DHKEM(P-256, HKDF-SHA256)`
  - **KDF**: `HKDF-SHA256`
  - **AEAD**: `AES-256-GCM`
- Recovered both 256-bit symmetric volume encryption keys:
  - **RootFS (`094-98312-089.dmg.aea`) Key**: `ca0d1a3eb45cdb15b15babced612a5d37914299f5d5d141d488ddccb40cda496`
  - **Recovery OS (`094-98220-089.dmg.aea`) Key**: `efd41ef06e0adc9426ae40d7c6635dbca5c88f68029411bf465a34c7c9baf7d9`
- Parsed the unencrypted 87.52 MB AppleArchive manifest (`.mtree`), indexing **371,514 files, 47,145 directories, and 54 system applications** across the 8.56 GB root filesystem.

### 2. tvOS UI Stack & Compositor Architecture
- **Compositor Pattern**: Dissected `PineBoard.app`, which acts as the master compositor and window server, hosting `PBRootWindow` (WindowLevel `0.0`) and managing out-of-process `FBScene` surfaces.
- **Home Screen Grid**: Analyzed `HeadBoard.app`, which renders the 2D application matrix and hosts `HBTopShelfContainerView`, dynamically querying client extensions via Mach IPC (`TVTopShelfProvider`).
- **Focus Engine Mechanics**: Reconstructed the 2D spatial heading projection algorithm ($w_d \cdot d + w_\theta \cdot \theta + w_o \cdot O$) and `UIFocusMovementHint` 3D card parallax physics (dynamic $\pm 8^\circ$ rotation with 3-tier optical depth layers and specular highlight gradients).

### 3. Filesystem Extraction & Kernelcache Decompression
- Extracted unencrypted APFS restore ramdisks (`094-97800-089.dmg` and `094-97880-089.dmg`, **1,650 files total**) with 100% relative symlinks.
- Decompressed `kernelcache.release.j42d` into a verified **44,122,112-byte 64-bit ARM64 Mach-O** Darwin 25.6.0 kernel (`xnu-12377.163.4~3`).
- Extracted 19 compiled `.car` asset catalogs, yielding **490 raster PNGs** and **84 vector PDFs** into [`decoded/assets/`](decoded/assets/).
- Decoded resolution-tiered ProgressUI asset ladders across 1080p, 4K UHD, and Apple Vision Pro Developer Strap graphics.

---

## 🌐 Interactive Graphify Knowledge Graph

The entire reverse-engineered architecture has been compiled into a persistent, navigable knowledge graph:

- **Topology**: **775 nodes**, **1,545 edges**, partitioned into **9 Louvain communities**.
- **Cross-Firmware Synthesis**: Links components across both tvOS 13.4.8 (Apple TV 4K / A10X) and tvOS 26.6.1 (Apple TV HD / A8).

### How to View:
Simply open [`graphify-out/graph.html`](graphify-out/graph.html) or [`graphify-out/index.html`](graphify-out/index.html) in any modern web browser:
```bash
# Example: serve locally or open directly
xdg-open graphify-out/graph.html
# or
python3 -m http.server 8000 --directory graphify-out
```

- **Features**:
  - Full-text node search across classes, frameworks, binaries, and assets.
  - Interactive force-directed physics with drag-and-pin nodes.
  - Topological cluster filtering by Louvain community (e.g. Compositor, Focus Engine, AEA Cryptography).
  - Machine-readable database: [`graphify-out/graph.json`](graphify-out/graph.json).
  - Graph audit and connectivity metrics: [`graphify-out/GRAPH_REPORT.md`](graphify-out/GRAPH_REPORT.md).

---

## 📁 Repository Structure

```
.
├── reports/                 # Authoritative master technical reports & extraction ledgers
│   ├── IPSW_TECHNICAL_REPORT.md
│   ├── TECHNICAL_REPORT.md
│   ├── IPSW_EXTRACTION_LEDGER.md
│   └── EXTRACTION_LEDGER.md
├── analysis/                # Detailed technical analyses & subsystem breakdowns
│   ├── ipsw/                # IPSW-specific AEA, UI evolution, and binary reports
│   ├── focus_engine/        # 2D raycasting, parallax physics, and Siri Remote HID
│   ├── ipc/                 # Mach services, XPC protocols, and TopShelf contracts
│   ├── objc/                # 607 classes, 9,935 methods, and 2,558 ivars catalog
│   ├── swift/               # Swift 5 ABI reflection and Metal shader analysis
│   ├── UI_STACK_REPORT.md   # Out-of-process compositor architecture
│   └── BINARY_ANALYSIS_REPORT.md
├── decoded/                 # Extracted non-proprietary assets & metadata
│   ├── assets/              # 490 PNGs, 84 vector PDFs, and CoreGlyphs descriptors
│   ├── plists/              # Decoded XML/JSON daemons and entitlements
│   └── strings/             # 25,490 localized string pairs across 39 languages
├── graphify-out/            # Navigable knowledge graph & interactive D3 visualizer
│   ├── graph.html           # Interactive standalone force-directed graph
│   ├── index.html           # Embedded web visualizer
│   ├── graph.json           # GraphRAG-ready graph database
│   └── GRAPH_REPORT.md      # Graph topology, god nodes, and community analysis
├── scripts/                 # Reproducible extraction & analysis utilities
│   ├── extract_payload.py   # Streaming multi-chunk PBZX / XZ unpacker
│   └── build_knowledge_graph.py
├── tests/                   # 80 automated unit, integration, and integrity test suites
│   ├── test_ipsw_m1_integrity.py
│   ├── test_ipsw_m2_aea.py
│   ├── test_ipsw_m3_ui.py
│   ├── test_ipsw_m4_binary.py
│   └── test_pbzx_adversarial.py
├── .agents/                 # Multi-agent swarm transcripts, handoffs, and audit trails
└── PROJECT.md               # End-to-end milestone and feature ledger
```

---

## 🛠️ Reproducibility & Testing

All extraction scripts and verification suites are fully automated and self-contained:

```bash
# Run the complete test suite (80 unit and integrity tests)
pytest tests/ -v

# Run the PBZX streaming payload extractor
python3 scripts/extract_payload.py --help

# Rebuild the Graphify knowledge graph
python3 scripts/build_knowledge_graph.py
```

---

## ⚖️ Legal & Ethical Notice

This repository is published solely for educational, architectural analysis, and interoperability research purposes. 

No proprietary Apple operating system binaries, kernelcaches, disk images, or protected code containers are redistributed in this repository. All artifacts included are reverse-engineered technical reports, structural metadata, open-source extraction scripts, and non-proprietary decoded assets.
