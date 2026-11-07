# Progress — Explorer 2 (Tooling & Environment Explorer)

Last visited: 2026-11-06T17:36:00Z

- [x] Read ORIGINAL_REQUEST.md
- [x] Recorded dispatch message in DISPATCH.md
- [x] Initialized BRIEFING.md
- [x] 1. Check system tools: python3 (3.14.8), pip (26.2.2), unzip, 7z (26.04), tar (1.35), cpio (2.15), xz (5.8.4), file (5.48), sha256sum (9.12), uv (0.13.4)
- [x] 2. Check Python packages: plistlib, lzma, bz2, zlib, zipfile, tarfile, sqlite3, struct, cryptography (50.0.2), networkx (3.7), pydantic (2.13.4), tree_sitter all available
- [x] 3. Check Apple / OTA extraction tools: No external compiled tools (pbzx, ota-tools, img4lib, jtool2, ldid, car-extractor, assetutil) installed globally, but:
  - Ramdisk (IM4P/HFSX) directly extractable via 7z (skipping 27 bytes ASN.1 header)
  - `payloadv2/payload.000-024` and `data_payload` are chunked PBZX streams cleanly decodable with standard Python `lzma` + `struct`!
  - Payload records use a simple `\x10\x01` (file) and `\x10\x02` (dir) format, allowing full pure-Python extraction without third-party dependencies.
  - Manifests (`BuildManifest.plist`, `Info.plist`) parse natively with standard `plistlib`.
- [x] 4. Review REA MCP tools for static inspection of tvOS binaries and UI assets: 230 tools available, key tools include `open_binary`, `inspect_macho`, `get_objc_classes`, `get_objc_protocols`, `analyze_swift_types`, `demangle_swift`, `inspect_asset_catalog`, `decode_interface_builder`, `project_apple_application_graph`.
- [x] 5. Review Ghidra MCP tools: 27 tools available via `bridge_mcp_ghidra.py` (requires Ghidra headless HTTP server on port 8080).
- [x] 6. Study Graphify skill and scripts: Located at `/home/prem/.config/AntigravityManager/profiles/d606a26b-7cc6-4974-a4e7-86cef5ccc397/home/.gemini/config/skills/graphify/SKILL.md`, package installed at `/home/prem/.local/lib/python3.14/site-packages/graphify` (v0.9.101), tested with `python3 -m graphify --help`.
- [x] 7. Synthesize findings and write handoff report to `handoff.md`
- [x] 8. Send notification message to parent
