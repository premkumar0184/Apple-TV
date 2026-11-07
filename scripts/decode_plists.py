#!/usr/bin/env python3
"""
Apple tvOS Property List (.plist) Static Extraction & Analysis Pipeline
Milestone: M2 (UI Architecture & Asset Reverse Engineering)
Strictly Static Analysis — Zero ARM64 Host Executions

Normalizes binary plists to JSON and XML representations and generates an architectural inventory.
"""

import os
import plistlib
import json

def serialize_custom(obj):
    if isinstance(obj, bytes):
        return f"<bytes: length={len(obj)}, hex={obj.hex()[:32]}...>"
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return str(obj)

def main():
    rootfs = '/home/prem/Projects/AppleTV/extracted/rootfs'
    output_dir = '/home/prem/Projects/AppleTV/decoded/plists'
    os.makedirs(output_dir, exist_ok=True)

    plist_files = []
    for root, dirs, files in os.walk(rootfs):
        for f in files:
            if f.endswith('.plist'):
                plist_files.append(os.path.join(root, f))

    plist_files.sort()
    print(f"Found {len(plist_files)} property list files in rootfs...")

    inventory = []

    for p in plist_files:
        rel_from_rootfs = os.path.relpath(p, rootfs)
        rel_clean = rel_from_rootfs.replace('/', '_')
        base_name = os.path.splitext(rel_clean)[0]
        
        target_json = os.path.join(output_dir, f"{base_name}.json")
        target_xml = os.path.join(output_dir, f"{base_name}.xml")

        try:
            with open(p, 'rb') as f:
                data = plistlib.load(f)

            # Write JSON
            with open(target_json, 'w', encoding='utf-8') as jf:
                json.dump(data, jf, indent=2, default=serialize_custom)

            # Write XML plist
            with open(target_xml, 'wb') as xf:
                plistlib.dump(data, xf, fmt=plistlib.FMT_XML)

            top_keys = list(data.keys()) if isinstance(data, dict) else [f"array_len_{len(data)}"]
            
            entry = {
                "original_path": rel_from_rootfs,
                "file_size": os.path.getsize(p),
                "decoded_json": os.path.basename(target_json),
                "decoded_xml": os.path.basename(target_xml),
                "top_keys": top_keys[:10],
                "total_keys": len(top_keys)
            }

            # Check specific plist types
            if "CFBundleIdentifier" in data:
                entry["bundle_id"] = data.get("CFBundleIdentifier")
                entry["executable"] = data.get("CFBundleExecutable")
                entry["min_os"] = data.get("MinimumOSVersion")
                entry["sdk"] = data.get("DTSDKName")
            
            inventory.append(entry)
            print(f"Decoded {rel_from_rootfs} -> {target_json}")

        except Exception as e:
            print(f"Failed to decode {rel_from_rootfs}: {e}")

    # Write inventory master
    inventory_path = os.path.join(output_dir, "PLISTS_MASTER.json")
    with open(inventory_path, 'w', encoding='utf-8') as inv_f:
        json.dump(inventory, inv_f, indent=2)

    # Generate Markdown report
    md_path = os.path.join(output_dir, "PLISTS_INVENTORY.md")
    with open(md_path, 'w', encoding='utf-8') as mdf:
        mdf.write("# Apple tvOS Decoded Property Lists & Entitlements Inventory\n\n")
        mdf.write("**Target**: tvOS 13.4.8 (Build 17M61, AppleTV6,2 / j105aap)\n")
        mdf.write(f"**Total Decoded Plists**: {len(inventory)}\n\n")
        mdf.write("| Original File | Bundle ID / Type | Size | Decoded JSON | Decoded XML |\n")
        mdf.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for it in inventory:
            b_id = it.get("bundle_id", "System / Config / Entitlements")
            mdf.write(f"| `{it['original_path']}` | `{b_id}` | {it['file_size']:,d} B | [`{it['decoded_json']}`](./{it['decoded_json']}) | [`{it['decoded_xml']}`](./{it['decoded_xml']}) |\n")
        
        mdf.write("\n## Architectural Findings from Plists\n\n")
        mdf.write("### 1. HeadBoard Default App Grid (`DefaultOrder.plist`)\n")
        mdf.write("The default tvOS Home Screen is ordered as a hierarchical folder structure (`HBRootFolderKey`):\n")
        mdf.write("- **Dock Row (GridOrder 1000 - 5000)**: Prime real estate apps with interactive Top Shelf extensions:\n")
        mdf.write("  1. `com.apple.TVWatchList` (Apple TV App / Up Next)\n")
        mdf.write("  2. `com.apple.TVMusic` (Apple Music)\n")
        mdf.write("  3. `com.apple.Arcade` (Apple Arcade)\n")
        mdf.write("  4. `com.apple.TVPhotos` (Photos & Shared Albums)\n")
        mdf.write("  5. `com.apple.TVAppStore` (App Store)\n")
        mdf.write("- **App Grid (GridOrder 6000 - 11000)**:\n")
        mdf.write("  6. `com.apple.podcasts`\n")
        mdf.write("  7. `com.apple.TVMovies` (iTunes Movies)\n")
        mdf.write("  8. `com.apple.TVShows` (iTunes TV Shows)\n")
        mdf.write("  9. `com.apple.TVSearch` (Siri & Spotlight Search)\n")
        mdf.write("  10. `com.apple.TVHomeSharing` (Local Media Streaming)\n")
        mdf.write("  11. `com.apple.TVSettings` (System Preferences)\n\n")

        mdf.write("### 2. PineBoard System Compositor Entitlements (`pineboard-Entitlements.plist`)\n")
        mdf.write("PineBoard holds supreme display and window management privileges:\n")
        mdf.write("- `com.apple.QuartzCore.displayable-context`: Direct CoreAnimation frame scheduling and hardware layer compositing.\n")
        mdf.write("- `com.apple.QuartzCore.global-capture` & `secure-capture`: Screen recording, AirPlay mirroring, and secure DRM display plane management.\n")
        mdf.write("- `com.apple.BTServer.supportsPairing` & `programmaticPairing`: Low-level Siri Remote / Bluetooth accessory handshake.\n")
        mdf.write("- `com.apple.appletv.pbs.allow-siri` & `allow-reboot`: Hardware button interception and power state machine execution.\n")

    print(f"Inventory written to {md_path}")

if __name__ == '__main__':
    main()
