#!/usr/bin/env python3
"""
map_framework_dependencies.py
Exhaustive framework dependency mapping, symbol table extraction, and reverse dependency
graph construction across Apple TV (tvOS 13.4.8) system applications.
Strictly static analysis - zero execution of ARM64 binaries.
"""

import os
import sys
import json
import glob
import subprocess
from collections import defaultdict

WORKSPACE_ROOT = "/home/prem/Projects/AppleTV"

TARGET_APPS = {
    "PineBoard": "extracted/rootfs/Applications/PineBoard.app/PineBoard",
    "HeadBoard": "extracted/rootfs/Applications/HeadBoard.app/HeadBoard",
    "PreBoard": "extracted/rootfs/Applications/PreBoard.app/PreBoard",
    "TVMusic": "extracted/rootfs/Applications/TVMusic.app/TVMusic",
    "TVSystemMenuService": "extracted/rootfs/Applications/TVSystemMenuService.app/TVSystemMenuService",
    "TVPeripheralAgent": "extracted/rootfs/Applications/TVPeripheralAgent.app/TVPeripheralAgent",
    "Setup": "extracted/rootfs/Applications/Setup.app/Setup",
    "TVSystemBulletinService": "extracted/rootfs/Applications/TVSystemBulletinService.app/TVSystemBulletinService",
    "TVIdleScreen": "extracted/rootfs/Applications/TVIdleScreen.app/TVIdleScreen",
    "AppleTV": "extracted/rootfs/Applications/AppleTV.app/AppleTV",
    "AppStore": "extracted/rootfs/Applications/AppStore.app/AppStore",
    "Siri": "extracted/rootfs/Applications/Siri.app/Siri",
}

def parse_load_dylibs(filepath):
    """Extract all LC_LOAD_DYLIB, LC_LOAD_WEAK_DYLIB, LC_REEXPORT_DYLIB commands."""
    cmd = ["llvm-objdump", "--macho", "--private-headers", filepath]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        return []

    lines = proc.stdout.splitlines()
    dylibs = []
    
    current_cmd = None
    for line in lines:
        stripped = line.strip()
        if line.startswith("Load command "):
            if current_cmd and "name" in current_cmd:
                dylibs.append(current_cmd)
            current_cmd = {"index": int(line.split()[2])}
        elif current_cmd is not None:
            if stripped.startswith("cmd "):
                current_cmd["cmd"] = stripped.split()[1]
            elif stripped.startswith("name ") and current_cmd.get("cmd", "").startswith("LC_"):
                current_cmd["name"] = stripped.split()[1]
            elif stripped.startswith("current version "):
                current_cmd["current_version"] = stripped.split()[2]
            elif stripped.startswith("compatibility version "):
                current_cmd["compatibility_version"] = stripped.split()[2]

    if current_cmd and "name" in current_cmd:
        dylibs.append(current_cmd)

    # Classify each dylib
    results = []
    for d in dylibs:
        p = d["name"]
        cmd_type = d.get("cmd", "LC_LOAD_DYLIB")
        is_weak = (cmd_type == "LC_LOAD_WEAK_DYLIB")
        is_reexport = (cmd_type == "LC_REEXPORT_DYLIB")
        
        category = "Other"
        if p.startswith("/System/Library/Frameworks/"):
            category = "Public Framework"
        elif p.startswith("/System/Library/PrivateFrameworks/"):
            category = "Private Framework"
        elif p.startswith("/usr/lib/swift/"):
            category = "Swift Runtime"
        elif p.startswith("/usr/lib/"):
            category = "System Dynamic Library"

        framework_name = os.path.basename(p)
        if ".framework" in p:
            framework_name = p.split(".framework")[0].split("/")[-1]

        results.append({
            "install_name": p,
            "framework_name": framework_name,
            "load_command": cmd_type,
            "weak": is_weak,
            "reexport": is_reexport,
            "current_version": d.get("current_version", "1.0.0"),
            "compatibility_version": d.get("compatibility_version", "1.0.0"),
            "category": category
        })
    return results

def extract_exports(filepath):
    """Extract exported symbols from Mach-O exports trie."""
    cmd = ["llvm-objdump", "--macho", "--exports-trie", filepath]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        return []
    exports = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("0x"):
            parts = line.split(None, 1)
            if len(parts) == 2:
                exports.append({
                    "address": parts[0],
                    "symbol": parts[1]
                })
    return exports

def extract_imports(filepath):
    """Extract imported symbols via bind and lazy-bind tables."""
    imports = []
    for flag, kind in [("--bind", "bind"), ("--lazy-bind", "lazy-bind")]:
        cmd = ["llvm-objdump", "--macho", flag, filepath]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            continue
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line.startswith("__"):
                parts = line.split()
                if len(parts) >= 6:
                    seg = parts[0]
                    sect = parts[1]
                    addr = parts[2]
                    dylib = parts[4] if kind == "bind" else parts[3]
                    sym = parts[5] if kind == "bind" else parts[4]
                    imports.append({
                        "kind": kind,
                        "segment": seg,
                        "section": sect,
                        "address": addr,
                        "dylib": dylib,
                        "symbol": sym
                    })
    return imports

def main():
    print("=== Mapping tvOS 13.4.8 Framework Dependencies & Symbols ===")
    os.makedirs("analysis/symbols", exist_ok=True)

    app_dependencies = {}
    reverse_deps = defaultdict(list)
    all_frameworks = {}
    
    exported_symbols = {}
    imported_symbols = {}

    for app_name, rel_path in TARGET_APPS.items():
        if not os.path.exists(rel_path):
            print(f"[-] Skipping missing binary: {rel_path}")
            continue

        print(f"[+] Processing {app_name} ({rel_path})...")
        dylibs = parse_load_dylibs(rel_path)
        app_dependencies[app_name] = {
            "binary_path": rel_path,
            "total_dependencies": len(dylibs),
            "dependencies": dylibs
        }

        # Accumulate reverse dependencies
        for d in dylibs:
            iname = d["install_name"]
            fname = d["framework_name"]
            cat = d["category"]
            reverse_deps[iname].append(app_name)
            if iname not in all_frameworks:
                all_frameworks[iname] = {
                    "install_name": iname,
                    "framework_name": fname,
                    "category": cat,
                    "current_version": d["current_version"],
                    "compatibility_version": d["compatibility_version"],
                }

        # Exports
        exps = extract_exports(rel_path)
        exported_symbols[app_name] = exps
        print(f"    {len(dylibs)} linked dylibs, {len(exps)} exported symbols")

        # Imports (for core target apps)
        if app_name in ("PineBoard", "HeadBoard", "PreBoard", "TVMusic", "TVSystemMenuService", "TVPeripheralAgent"):
            imps = extract_imports(rel_path)
            imported_symbols[app_name] = {
                "total_count": len(imps),
                "imports": imps
            }
            print(f"    {len(imps)} imported symbols (bind + lazy-bind)")

    # Build Framework Dependencies JSON
    framework_catalog = []
    for iname, info in sorted(all_frameworks.items(), key=lambda x: x[1]["framework_name"]):
        used_by = sorted(list(set(reverse_deps[iname])))
        framework_catalog.append({
            "framework_name": info["framework_name"],
            "install_name": iname,
            "category": info["category"],
            "current_version": info["current_version"],
            "compatibility_version": info["compatibility_version"],
            "dependent_apps_count": len(used_by),
            "dependent_apps": used_by
        })

    framework_output = {
        "metadata": {
            "os_version": "tvOS 13.4.8",
            "build": "17M61",
            "analyzed_applications": len(app_dependencies),
            "total_unique_frameworks": len(framework_catalog),
            "public_frameworks_count": sum(1 for f in framework_catalog if f["category"] == "Public Framework"),
            "private_frameworks_count": sum(1 for f in framework_catalog if f["category"] == "Private Framework"),
            "system_libraries_count": sum(1 for f in framework_catalog if f["category"] == "System Dynamic Library"),
            "swift_runtime_count": sum(1 for f in framework_catalog if f["category"] == "Swift Runtime")
        },
        "applications": app_dependencies,
        "framework_catalog": framework_catalog
    }

    dep_json_path = "analysis/symbols/framework_dependencies.json"
    with open(dep_json_path, "w") as f:
        json.dump(framework_output, f, indent=2)
    print(f"[+] Wrote {dep_json_path}")

    # Write Exports JSON
    exp_json_path = "analysis/symbols/exported_symbols.json"
    with open(exp_json_path, "w") as f:
        json.dump(exported_symbols, f, indent=2)
    print(f"[+] Wrote {exp_json_path}")

    # Write Imports JSON
    imp_json_path = "analysis/symbols/imported_symbols.json"
    with open(imp_json_path, "w") as f:
        json.dump(imported_symbols, f, indent=2)
    print(f"[+] Wrote {imp_json_path}")

    # Generate FRAMEWORK_DEPENDENCY_GRAPH.md
    md_path = "analysis/symbols/FRAMEWORK_DEPENDENCY_GRAPH.md"
    with open(md_path, "w") as f:
        f.write("# tvOS 13.4.8 System Framework Dependency Graph & Architecture\n\n")
        f.write("Synthesized from Mach-O load commands (`LC_LOAD_DYLIB`, `LC_LOAD_WEAK_DYLIB`, `LC_REEXPORT_DYLIB`) across core tvOS system applications.\n\n")
        
        f.write("## 1. High-Level Dependency Statistics\n\n")
        f.write(f"- **Applications Analyzed**: {len(app_dependencies)}\n")
        f.write(f"- **Total Unique Frameworks & Libraries**: {len(framework_catalog)}\n")
        f.write(f"  - **Public Frameworks (`/System/Library/Frameworks/`)**: {framework_output['metadata']['public_frameworks_count']}\n")
        f.write(f"  - **Private Frameworks (`/System/Library/PrivateFrameworks/`)**: {framework_output['metadata']['private_frameworks_count']}\n")
        f.write(f"  - **System Dynamic Libraries (`/usr/lib/`)**: {framework_output['metadata']['system_libraries_count']}\n")
        f.write(f"  - **Swift Runtime Libraries (`/usr/lib/swift/`)**: {framework_output['metadata']['swift_runtime_count']}\n\n")

        f.write("## 2. Application Dependency Footprint\n\n")
        f.write("| Application | Binary Path | Linked Dylibs | Public Frameworks | Private Frameworks | Swift Runtimes |\n")
        f.write("|---|---|---|---|---|---|\n")
        for app_name, app_data in sorted(app_dependencies.items(), key=lambda x: -x[1]["total_dependencies"]):
            n_pub = sum(1 for d in app_data["dependencies"] if d["category"] == "Public Framework")
            n_priv = sum(1 for d in app_data["dependencies"] if d["category"] == "Private Framework")
            n_swift = sum(1 for d in app_data["dependencies"] if d["category"] == "Swift Runtime")
            f.write(f"| **{app_name}** | `{app_data['binary_path']}` | **{app_data['total_dependencies']}** | {n_pub} | {n_priv} | {n_swift} |\n")
        f.write("\n---\n\n")

        f.write("## 3. Core Subsystem Framework Clusters\n\n")
        f.write("### A. Shell & Window Management (PineBoard Subsystem)\n")
        f.write("- `PineBoardServices.framework`: Inter-process communication client library for all tvOS applications communicating with PineBoard.\n")
        f.write("- `FrontBoard.framework` & `FrontBoardServices.framework`: Low-level application lifecycle, scene creation, process assertions, and display layout management.\n")
        f.write("- `BackBoardServices.framework`: HID event routing, discrete dispatching rules, and display fence handles.\n")
        f.write("- `BaseBoard.framework` & `BaseBoardUI.framework`: Foundational primitives (`BSTransaction`, `BSSimpleAssertion`, `BSAnimationSettings`).\n")
        f.write("- `RunningBoardServices.framework`: Process identity, target tracking, and lifecycle assertion management.\n\n")

        f.write("### B. User Interface & Home Grid (HeadBoard Subsystem)\n")
        f.write("- `HeadBoardModel.framework`: Data model representing the tvOS home screen icon grid, folders, and layout persistency.\n")
        f.write("- `HeadBoardUI.framework`: Visual presentation layer, focus-aware icon cells, and folder animation physics.\n")
        f.write("- `TVUIKit.framework` & `TVMLKit.framework`: tvOS-specific TV card views, poster buttons, and XML template rendering.\n")
        f.write("- `UIKit.framework`: Root UI framework (`UIApplication`, `UICollectionView`, `UIFocusEngine`).\n\n")

        f.write("### C. Audio/Video, Playback & Control\n")
        f.write("- `TVPlayback.framework`: Comprehensive playback controller (`TVPPlayer`, audio sessions, routing).\n")
        f.write("- `MediaRemote.framework`: Siri remote playback events, command center transport controls.\n")
        f.write("- `MediaPlaybackCore.framework`: Audio spectrum analysis and queue management.\n")
        f.write("- `TVCoreSettings.framework` & `ATVSystemState.framework`: Hardware display modes, LED indicators, and audio output sinks.\n\n")

        f.write("## 4. Top Most Widely Linked Frameworks & Libraries\n\n")
        f.write("| Rank | Framework / Library Name | Category | Dependent Apps Count | Dependent System Apps |\n")
        f.write("|---|---|---|---|---|\n")
        top_frameworks = sorted(framework_catalog, key=lambda x: -x["dependent_apps_count"])
        for idx, fw in enumerate(top_frameworks[:25], 1):
            apps_str = ", ".join(fw["dependent_apps"])
            f.write(f"| {idx} | `{fw['framework_name']}` | {fw['category']} | **{fw['dependent_apps_count']}** | {apps_str} |\n")
        f.write("\n---\n\n")

        f.write("## 5. Complete System Framework Catalog\n\n")
        f.write("| Framework Name | Install Name | Category | Version | Apps Count |\n")
        f.write("|---|---|---|---|---|\n")
        for fw in framework_catalog:
            f.write(f"| `{fw['framework_name']}` | `{fw['install_name']}` | {fw['category']} | `{fw['current_version']}` | {fw['dependent_apps_count']} |\n")

    print(f"[+] Wrote {md_path}")

if __name__ == "__main__":
    main()
