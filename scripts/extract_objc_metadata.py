#!/usr/bin/env python3
"""
extract_objc_metadata.py
Robust, comprehensive Objective-C runtime metadata extractor for tvOS 13.4.8 binaries.
Parses class definitions, superclasses, protocols, instance/class methods,
ivars, and properties.
Strictly static analysis - zero execution of ARM64 binaries.
"""

import os
import sys
import json
import re
import subprocess

TARGET_APPS = {
    "PineBoard": "extracted/rootfs/Applications/PineBoard.app/PineBoard",
    "HeadBoard": "extracted/rootfs/Applications/HeadBoard.app/HeadBoard",
    "PreBoard": "extracted/rootfs/Applications/PreBoard.app/PreBoard",
    "TVMusic": "extracted/rootfs/Applications/TVMusic.app/TVMusic",
    "TVSystemMenuService": "extracted/rootfs/Applications/TVSystemMenuService.app/TVSystemMenuService",
    "TVPeripheralAgent": "extracted/rootfs/Applications/TVPeripheralAgent.app/TVPeripheralAgent",
}

def parse_objc_metadata(filepath):
    cmd = ["llvm-objdump", "--macho", "--objc-meta-data", filepath]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        print(f"[-] Error running llvm-objdump on {filepath}: {proc.stderr}")
        return []

    lines = proc.stdout.splitlines()
    classes = []
    
    current_class = None
    state = "NONE" # "BASE_METHODS", "CLASS_METHODS", "IVARS", "PROPERTIES", "PROTOCOLS"
    is_metaclass = False
    
    cur_method = None
    cur_ivar = None
    cur_prop = None

    def flush_method():
        nonlocal cur_method
        if cur_method and cur_method.get("name"):
            if is_metaclass:
                current_class["class_methods"].append(cur_method)
            else:
                current_class["instance_methods"].append(cur_method)
        cur_method = None

    def flush_ivar():
        nonlocal cur_ivar
        if cur_ivar and cur_ivar.get("name"):
            current_class["ivars"].append(cur_ivar)
        cur_ivar = None

    def flush_prop():
        nonlocal cur_prop
        if cur_prop and cur_prop.get("name"):
            current_class["properties"].append(cur_prop)
        cur_prop = None

    for line in lines:
        stripped = line.strip()

        # Check class boundary: 16 hex digits followed by 0x address
        if re.match(r"^[0-9a-fA-F]{16}\s+0x[0-9a-fA-F]+", line) and "Contents of" not in line:
            flush_method()
            flush_ivar()
            flush_prop()
            if current_class and current_class.get("name"):
                classes.append(current_class)
            current_class = {
                "class_addr": line.split()[0],
                "superclass": None,
                "name": None,
                "protocols": [],
                "ivars": [],
                "properties": [],
                "instance_methods": [],
                "class_methods": []
            }
            state = "NONE"
            is_metaclass = False
            continue

        if current_class is None:
            continue

        # Meta Class detection
        if stripped == "Meta Class" or (stripped.startswith("isa ") and "0x" in stripped and current_class.get("name")):
            flush_method()
            flush_ivar()
            flush_prop()
            is_metaclass = True
            state = "NONE"
            continue

        # Superclass
        if stripped.startswith("superclass "):
            sc = stripped.split("superclass ", 1)[1].strip()
            sc_parts = sc.split()
            if len(sc_parts) > 1:
                sc_name = sc_parts[1].replace("_OBJC_CLASS_$_", "")
                if not is_metaclass and not current_class["superclass"]:
                    current_class["superclass"] = sc_name
            elif sc == "0x0" and not is_metaclass and not current_class["superclass"]:
                current_class["superclass"] = "NSObject"
            continue

        # Section transitions
        if stripped.startswith("baseMethods "):
            flush_method()
            flush_ivar()
            flush_prop()
            state = "CLASS_METHODS" if is_metaclass else "BASE_METHODS"
            continue
        elif stripped.startswith("baseProtocols "):
            flush_method()
            flush_ivar()
            flush_prop()
            state = "PROTOCOLS"
            continue
        elif stripped.startswith("ivars "):
            flush_method()
            flush_ivar()
            flush_prop()
            state = "IVARS"
            continue
        elif stripped.startswith("baseProperties "):
            flush_method()
            flush_ivar()
            flush_prop()
            state = "PROPERTIES"
            continue

        # Parsing items within state
        if state in ("BASE_METHODS", "CLASS_METHODS"):
            if stripped.startswith("name "):
                flush_method()
                name_val = stripped.split()[-1]
                cur_method = {"name": name_val}
            elif stripped.startswith("types ") and cur_method is not None:
                cur_method["types"] = stripped.split()[-1]
            elif stripped.startswith("imp ") and cur_method is not None:
                cur_method["imp"] = stripped.split()[-1]

        elif state == "IVARS":
            if stripped.startswith("name "):
                flush_ivar()
                name_val = stripped.split()[-1]
                cur_ivar = {"name": name_val}
            elif stripped.startswith("type ") and cur_ivar is not None:
                cur_ivar["type"] = stripped.split(None, 1)[1]
            elif stripped.startswith("offset ") and cur_ivar is not None:
                cur_ivar["offset"] = stripped.split()[-1]
            elif stripped.startswith("size ") and cur_ivar is not None:
                cur_ivar["size"] = stripped.split()[-1]

        elif state == "PROPERTIES":
            if stripped.startswith("name "):
                flush_prop()
                name_val = stripped.split()[-1]
                cur_prop = {"name": name_val}
            elif stripped.startswith("attributes ") and cur_prop is not None:
                cur_prop["attributes"] = stripped.split(None, 1)[1]

        elif state == "PROTOCOLS":
            if stripped.startswith("name "):
                proto_name = stripped.split()[-1]
                if proto_name not in current_class["protocols"]:
                    current_class["protocols"].append(proto_name)

        elif state == "NONE":
            # Class name
            if stripped.startswith("name "):
                name_val = stripped.split()[-1]
                if not current_class["name"] and not is_metaclass:
                    current_class["name"] = name_val

    flush_method()
    flush_ivar()
    flush_prop()
    if current_class and current_class.get("name"):
        classes.append(current_class)

    # Deduplicate classes by name
    dedup = {}
    for c in classes:
        name = c["name"]
        if not name:
            continue
        if name not in dedup:
            dedup[name] = c
        else:
            existing = dedup[name]
            for m in c["instance_methods"]:
                if not any(x["name"] == m["name"] for x in existing["instance_methods"]):
                    existing["instance_methods"].append(m)
            for m in c["class_methods"]:
                if not any(x["name"] == m["name"] for x in existing["class_methods"]):
                    existing["class_methods"].append(m)
            for iv in c["ivars"]:
                if not any(x["name"] == iv["name"] for x in existing["ivars"]):
                    existing["ivars"].append(iv)
            for pr in c["properties"]:
                if not any(x["name"] == pr["name"] for x in existing["properties"]):
                    existing["properties"].append(pr)
            for proto in c["protocols"]:
                if proto not in existing["protocols"]:
                    existing["protocols"].append(proto)
            if not existing["superclass"] and c["superclass"]:
                existing["superclass"] = c["superclass"]

    return list(dedup.values())

def format_clean_objc_interface(cls):
    """Format an Objective-C class as an accurate, readable @interface block."""
    name = cls["name"]
    superclass = cls["superclass"] or "NSObject"
    protocols = f" <{', '.join(cls['protocols'])}>" if cls["protocols"] else ""
    
    lines = [f"@interface {name} : {superclass}{protocols}"]
    
    if cls["ivars"]:
        lines.append("{")
        for iv in cls["ivars"]:
            iv_type = iv.get("type", "id").replace('"', '')
            iv_name = iv.get("name", "ivar")
            lines.append(f"    {iv_type} {iv_name};")
        lines.append("}")
        
    if cls["properties"]:
        for prop in cls["properties"]:
            pname = prop.get("name", "prop")
            attrs = prop.get("attributes", "")
            lines.append(f"@property (nonatomic) id {pname}; // {attrs}")
            
    if cls["class_methods"]:
        lines.append("\n// Class Methods")
        for m in cls["class_methods"]:
            mname = m.get("name", "method")
            imp = m.get("imp", "0x0")
            lines.append(f"+ (id){mname}; // imp: {imp}")

    if cls["instance_methods"]:
        lines.append("\n// Instance Methods")
        for m in cls["instance_methods"]:
            mname = m.get("name", "method")
            imp = m.get("imp", "0x0")
            lines.append(f"- (id){mname}; // imp: {imp}")

    lines.append("@end\n")
    return "\n".join(lines)

def main():
    print("=== Extracting Comprehensive Objective-C Runtime Metadata ===")
    os.makedirs("analysis/objc", exist_ok=True)
    all_objc_data = {}
    
    total_classes = 0
    total_methods = 0
    total_ivars = 0
    
    for app_name, app_path in TARGET_APPS.items():
        if not os.path.exists(app_path):
            print(f"[-] Missing binary: {app_path}")
            continue
        print(f"[+] Parsing {app_name} ({app_path})...")
        classes = parse_objc_metadata(app_path)
        
        n_classes = len(classes)
        n_methods = sum(len(c["instance_methods"]) + len(c["class_methods"]) for c in classes)
        n_ivars = sum(len(c["ivars"]) for c in classes)
        
        total_classes += n_classes
        total_methods += n_methods
        total_ivars += n_ivars
        
        print(f"    {app_name}: {n_classes} classes, {n_methods} methods, {n_ivars} ivars")
        
        # Save formatted class dump
        txt_path = f"analysis/objc/{app_name}_classes.txt"
        with open(txt_path, "w") as f:
            f.write(f"// Objective-C Class Dump: {app_name}\n")
            f.write(f"// Target: {app_path}\n")
            f.write(f"// Statistics: {n_classes} classes, {n_methods} methods, {n_ivars} ivars\n\n")
            for c in sorted(classes, key=lambda x: x["name"]):
                f.write(format_clean_objc_interface(c))
                f.write("\n")

        all_objc_data[app_name] = {
            "binary": app_path,
            "class_count": n_classes,
            "method_count": n_methods,
            "ivar_count": n_ivars,
            "classes": classes
        }

    # Save complete JSON
    json_path = "analysis/objc/objc_classes.json"
    with open(json_path, "w") as f:
        json.dump(all_objc_data, f, indent=2)
    print(f"[+] Wrote {json_path}")

    # Generate OBJC_CLASS_INDEX.md
    index_md = "analysis/objc/OBJC_CLASS_INDEX.md"
    with open(index_md, "w") as f:
        f.write("# Objective-C Runtime Architecture & Class Taxonomy\n\n")
        f.write(f"Comprehensive extraction of Objective-C classes, hierarchies, methods, ivars, and protocols for tvOS 13.4.8 (Build 17M61).\n\n")
        f.write(f"**Total Classes Extracted**: {total_classes}  \n")
        f.write(f"**Total Methods Recovered**: {total_methods}  \n")
        f.write(f"**Total Instance Variables (Ivars)**: {total_ivars}  \n\n")
        f.write("## Target Application Summary\n\n")
        f.write("| Application | Binary Path | Classes | Methods | Ivars |\n")
        f.write("|---|---|---|---|---|\n")
        for app_name, data in all_objc_data.items():
            f.write(f"| **{app_name}** | `{data['binary']}` | {data['class_count']} | {data['method_count']} | {data['ivar_count']} |\n")
        f.write("\n---\n\n")
        
        for app_name, data in all_objc_data.items():
            f.write(f"## {app_name} Class Roster ({data['class_count']} classes, {data['method_count']} methods)\n\n")
            f.write("| Class Name | Superclass | Protocols | Instance Methods | Class Methods | Ivars | Properties |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for c in sorted(data["classes"], key=lambda x: x["name"]):
                protos = ", ".join(c["protocols"]) if c["protocols"] else "none"
                f.write(f"| `{c['name']}` | `{c['superclass'] or 'NSObject'}` | {protos} | {len(c['instance_methods'])} | {len(c['class_methods'])} | {len(c['ivars'])} | {len(c['properties'])} |\n")
            f.write("\n---\n\n")

    print(f"[+] Wrote {index_md}")
    print(f"[+] Summary: {total_classes} classes, {total_methods} methods, {total_ivars} ivars across {len(all_objc_data)} apps")

if __name__ == "__main__":
    main()
