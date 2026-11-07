#!/usr/bin/env python3
"""
analyze_macho_headers.py
Exhaustive Mach-O static analysis for Apple TV (tvOS 13.4.8) target binaries.
Parses Mach-O headers, load commands, segments, sections, entry points,
UUIDs, build versions, and code signatures.
Strictly static analysis - zero execution of ARM64 binaries.
"""

import os
import sys
import json
import struct
import subprocess
import hashlib

TARGET_BINARIES = {
    "PineBoard": "extracted/rootfs/Applications/PineBoard.app/PineBoard",
    "HeadBoard": "extracted/rootfs/Applications/HeadBoard.app/HeadBoard",
    "PreBoard": "extracted/rootfs/Applications/PreBoard.app/PreBoard",
    "TVMusic": "extracted/rootfs/Applications/TVMusic.app/TVMusic",
    "TVSystemMenuService": "extracted/rootfs/Applications/TVSystemMenuService.app/TVSystemMenuService",
    "TVPeripheralAgent": "extracted/rootfs/Applications/TVPeripheralAgent.app/TVPeripheralAgent",
    "kernelcache": "extracted/kernel/kernelcache.macho",
    "dyld_shared_cache": "extracted/dyld_cache/dyld_shared_cache_arm64",
}

def compute_hashes(filepath):
    sha256 = hashlib.sha256()
    md5 = hashlib.md5()
    size = os.path.getsize(filepath)
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
            md5.update(chunk)
    return {
        "size_bytes": size,
        "sha256": sha256.hexdigest(),
        "md5": md5.hexdigest()
    }

def parse_macho_header_and_load_commands(filepath):
    """Parse Mach-O header and load commands via llvm-objdump and direct parsing."""
    res = {}
    
    # Run llvm-objdump --macho --private-headers
    cmd = ["llvm-objdump", "--macho", "--private-headers", filepath]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        return {"error": proc.stderr}

    lines = proc.stdout.splitlines()
    
    header = {}
    load_commands = []
    current_cmd = None
    current_sect = None

    idx = 0
    while idx < len(lines):
        line = lines[idx]
        
        if "Mach header" in line:
            # next lines contain header fields
            idx += 2
            if idx < len(lines):
                fields = lines[idx].split()
                if len(fields) >= 8:
                    header = {
                        "magic": fields[0],
                        "cputype": fields[1],
                        "cpusubtype": fields[2],
                        "caps": fields[3],
                        "filetype": fields[4],
                        "ncmds": int(fields[5]),
                        "sizeofcmds": int(fields[6]),
                        "flags": fields[7:]
                    }
            idx += 1
            continue

        if line.startswith("Load command "):
            if current_cmd:
                load_commands.append(current_cmd)
            cmd_num = int(line.split()[2])
            current_cmd = {"command_index": cmd_num, "sections": []}
            current_sect = None
            idx += 1
            continue

        if current_cmd is not None:
            stripped = line.strip()
            if stripped.startswith("cmd "):
                current_cmd["cmd"] = stripped.split()[1]
            elif stripped.startswith("cmdsize "):
                current_cmd["cmdsize"] = int(stripped.split()[1])
            elif stripped.startswith("segname "):
                current_cmd["segname"] = stripped.split()[1]
            elif stripped.startswith("vmaddr "):
                current_cmd["vmaddr"] = stripped.split()[1]
            elif stripped.startswith("vmsize "):
                current_cmd["vmsize"] = stripped.split()[1]
            elif stripped.startswith("fileoff "):
                current_cmd["fileoff"] = int(stripped.split()[1])
            elif stripped.startswith("filesize "):
                current_cmd["filesize"] = int(stripped.split()[1])
            elif stripped.startswith("maxprot "):
                current_cmd["maxprot"] = stripped.split()[1]
            elif stripped.startswith("initprot "):
                current_cmd["initprot"] = stripped.split()[1]
            elif stripped.startswith("nsects "):
                current_cmd["nsects"] = int(stripped.split()[1])
            elif stripped.startswith("flags ") and "segname" in current_cmd:
                current_cmd["segflags"] = stripped.split(None, 1)[1]
            elif stripped.startswith("name ") and current_cmd.get("cmd", "").startswith("LC_LOAD"):
                current_cmd["dylib_path"] = stripped.split()[1]
            elif stripped.startswith("current version "):
                current_cmd["current_version"] = stripped.split()[2]
            elif stripped.startswith("compatibility version "):
                current_cmd["compatibility_version"] = stripped.split()[2]
            elif stripped.startswith("platform "):
                current_cmd["platform"] = stripped.split()[1]
            elif stripped.startswith("minos "):
                current_cmd["minos"] = stripped.split()[1]
            elif stripped.startswith("sdk "):
                current_cmd["sdk"] = stripped.split()[1]
            elif stripped.startswith("entryoff "):
                current_cmd["entryoff"] = stripped.split()[1]
            elif stripped.startswith("stacksize "):
                current_cmd["stacksize"] = stripped.split()[1]
            elif stripped.startswith("uuid "):
                current_cmd["uuid"] = stripped.split()[1]
            elif stripped.startswith("dataoff "):
                current_cmd["dataoff"] = stripped.split()[1]
            elif stripped.startswith("datasize "):
                current_cmd["datasize"] = stripped.split()[1]
            elif stripped.startswith("path ") and current_cmd.get("cmd") == "LC_RPATH":
                current_cmd["rpath"] = stripped.split()[1]
            elif line.startswith("Section"):
                if current_sect:
                    current_cmd["sections"].append(current_sect)
                current_sect = {}
            elif current_sect is not None:
                if stripped.startswith("sectname "):
                    current_sect["sectname"] = stripped.split()[1]
                elif stripped.startswith("segname "):
                    current_sect["segname"] = stripped.split()[1]
                elif stripped.startswith("addr "):
                    current_sect["addr"] = stripped.split()[1]
                elif stripped.startswith("size "):
                    current_sect["size"] = stripped.split()[1]
                elif stripped.startswith("offset "):
                    current_sect["offset"] = int(stripped.split()[1])
                elif stripped.startswith("align "):
                    current_sect["align"] = stripped.split(None, 1)[1]
                elif stripped.startswith("type "):
                    current_sect["type"] = stripped.split()[1]
                elif stripped.startswith("attributes "):
                    current_sect["attributes"] = stripped.split(None, 1)[1]

        idx += 1

    if current_sect and current_cmd is not None:
        current_cmd["sections"].append(current_sect)
    if current_cmd:
        load_commands.append(current_cmd)

    return {
        "header": header,
        "load_commands_count": len(load_commands),
        "load_commands": load_commands
    }

def parse_dyld_cache(filepath):
    """Parse dyld_shared_cache header and image table."""
    with open(filepath, "rb") as f:
        hdr = f.read(128)
        magic = hdr[:16].decode("ascii", errors="replace").strip("\x00")
        mappingOffset, mappingCount, imagesOffset, imagesCount = struct.unpack("<IIII", hdr[16:32])
        dyldBaseAddress, codeSignatureOffset, codeSignatureSize, slideInfoOffset, slideInfoSize = struct.unpack("<QQQQQ", hdr[32:72])
        
        # Read mappings
        f.seek(mappingOffset)
        mappings = []
        for i in range(mappingCount):
            mbytes = f.read(32)
            address, size, fileOffset, maxProt, initProt = struct.unpack("<QQQII", mbytes)
            mappings.append({
                "mapping_index": i,
                "address": f"0x{address:x}",
                "size_bytes": size,
                "size_mb": round(size / (1024 * 1024), 2),
                "file_offset": f"0x{fileOffset:x}",
                "init_prot": initProt,
                "max_prot": maxProt
            })
            
        # Read all images
        f.seek(imagesOffset)
        images = []
        for i in range(imagesCount):
            ibytes = f.read(32)
            address, modTime, inode, pathFileOffset, pad = struct.unpack("<QQQII", ibytes)
            cur = f.tell()
            f.seek(pathFileOffset)
            path_bytes = b""
            while True:
                c = f.read(1)
                if c == b"\x00" or not c:
                    break
                path_bytes += c
            f.seek(cur)
            images.append({
                "index": i,
                "address": f"0x{address:x}",
                "path": path_bytes.decode("utf-8", errors="replace")
            })

    return {
        "magic": magic,
        "mapping_count": mappingCount,
        "mappings": mappings,
        "image_count": imagesCount,
        "images": images,
        "code_signature_offset": f"0x{codeSignatureOffset:x}",
        "code_signature_size": codeSignatureSize,
        "slide_info_offset": f"0x{slideInfoOffset:x}",
        "slide_info_size": slideInfoSize
    }

def main():
    print("=== Mach-O Static Binary Analysis ===")
    results = {}
    
    for name, path in TARGET_BINARIES.items():
        if not os.path.exists(path):
            print(f"[-] Missing binary: {path}")
            continue
        print(f"[+] Analyzing {name} ({path})...")
        hinfo = compute_hashes(path)
        
        if name == "dyld_shared_cache":
            cache_info = parse_dyld_cache(path)
            results[name] = {
                "file_info": hinfo,
                "cache_info": cache_info
            }
            print(f"    dyld cache with {cache_info['image_count']} images, {cache_info['mapping_count']} mappings")
        else:
            macho_info = parse_macho_header_and_load_commands(path)
            results[name] = {
                "file_info": hinfo,
                "macho_info": macho_info
            }
            hdr = macho_info.get("header", {})
            print(f"    Mach-O {hdr.get('magic')} {hdr.get('cputype')} ({hdr.get('filetype')}) - {macho_info.get('load_commands_count')} load commands")

    out_file = "analysis/symbols/macho_structures.json"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[+] Successfully wrote Mach-O structures to {out_file}")

if __name__ == "__main__":
    main()
