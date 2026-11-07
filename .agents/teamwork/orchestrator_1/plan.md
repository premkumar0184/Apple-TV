# Plan — tvOS Reverse Engineering & Architecture Reconstruction

## Overview
Decompose the project into sequential and parallel milestones to fulfill all requirements (R1 - R7) while strictly observing host execution safety (R7: static analysis only).

## Phases & Milestones

### Phase 0: Survey & Scope Mapping
- Dispatch 3 parallel Explorers:
  - `explorer_survey_1`: Inspect the target archive `8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip`, its SHA-256, internal structure, plists, manifests, and BOM files.
  - `explorer_survey_2`: Inspect available tools and environments (python, pip, 7z, unzip, ldid, otool, jtool2, pbzx, cpio, dmg, REA tools, ghidra, graphify).
  - `explorer_survey_3`: Inspect target directory structure design, payload formats (payloadv2, pbzx, chunked OTA formats), and define the non-destructive extraction plan.
- Synthesize findings into `PROJECT.md` with full Feature Inventory.

### Phase 1: Milestone Definition & Setup
- Finalize `PROJECT.md` at workspace root.
- Set up directories under `/home/prem/Projects/AppleTV/`:
  - `raw/`: Unmodified raw archive and checksum records
  - `extracted/`: Unpacked filesystem partitions, System/Library/Frameworks, Applications
  - `decoded/`: Extracted .car assets, nibs, strings, plist dumps
  - `analysis/`: REA binary analysis outputs, class dumps, symbol tables, dependency matrices
  - `graphify-out/`: Graphify knowledge graph outputs (graph.json, visualizer HTML, GRAPH_REPORT.md)
  - `reports/`: Comprehensive Technical Report and documentation

### Phase 2: Execution & Iteration Loop
- Milestone 1: Archive Forensics & Filesystem Extraction (R1, R2, R7)
- Milestone 2: UI Architecture & Asset Reverse Engineering (R3, R7)
- Milestone 3: Binary Analysis & REA Reverse Engineering (R4, R7)
- Milestone 4: Graphify Knowledge Graph & Technical Reporting (R5, R6)

### Phase 3: Final Verification & Reporting
- Audit against Acceptance Criteria.
- Generate and verify exhaustive technical report.
- Report completion to Sentinel via `send_message`.
