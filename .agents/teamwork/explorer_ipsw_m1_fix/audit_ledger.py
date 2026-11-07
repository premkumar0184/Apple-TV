#!/usr/bin/env python3
"""
IPSW Ledger Audit Script
Audits and computes exact physical disk sizes, SHA-256 digests,
and image dimensions for all artifacts documented in reports/IPSW_EXTRACTION_LEDGER.md.
"""

import os
import hashlib
import struct
import re
from PIL import Image

PROJECT_ROOT = "/home/prem/Projects/AppleTV"

def sha256_path(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1048576):
            h.update(chunk)
    return h.hexdigest()

def audit_all():
    print("=" * 80)
    print("AUDITING IPSW LEDGER DELIVERABLES")
    print("=" * 80)

    # 1. Archive file
    ipsw_path = os.path.join(PROJECT_ROOT, "AppleTV5,3_26.6.1_23L781_Restore.ipsw")
    ipsw_size = os.path.getsize(ipsw_path)
    ipsw_hash = sha256_path(ipsw_path)
    print(f"\n[1] IPSW Archive:")
    print(f"Path: {ipsw_path}")
    print(f"Size: {ipsw_size:,} bytes")
    print(f"SHA-256: {ipsw_hash}")

    # 2. Section 3: 26 Archive member files in AppleTV5,3_26.6.1_23L781_Restore/
    archive_dir = os.path.join(PROJECT_ROOT, "AppleTV5,3_26.6.1_23L781_Restore")
    print(f"\n[2] Section 3 Archive Inventory ({archive_dir}):")
    section_3_files = [
        "094-97800-089.dmg",
        "094-97880-089.dmg",
        "094-98220-089.dmg.aea",
        "094-98312-089.dmg.aea",
        "BuildManifest.plist",
        "Restore.plist",
        "RestoreVersion.plist",
        "SystemVersion.plist",
        "kernelcache.release.j42d",
        "Firmware/094-97800-089.dmg.trustcache",
        "Firmware/094-97880-089.dmg.trustcache",
        "Firmware/094-98220-089.dmg.aea.mtree",
        "Firmware/094-98220-089.dmg.aea.root_hash",
        "Firmware/094-98220-089.dmg.aea.trustcache",
        "Firmware/094-98312-089.dmg.aea.mtree",
        "Firmware/094-98312-089.dmg.aea.root_hash",
        "Firmware/094-98312-089.dmg.aea.trustcache",
        "Firmware/dfu/iBEC.j42d.RELEASE.im4p",
        "Firmware/dfu/iBSS.j42d.RELEASE.im4p",
        "Firmware/all_flash/DeviceTree.j42dap.im4p",
        "Firmware/all_flash/LLB.j42d.RELEASE.im4p",
        "Firmware/all_flash/applelogo~appletv.im4p",
        "Firmware/all_flash/iBoot.j42d.RELEASE.im4p",
        "Firmware/all_flash/recoverymode@1080~appletv5.im4p",
        "Firmware/all_flash/sep-firmware.j42d.RELEASE.im4p",
        "Firmware/all_flash/sep-firmware.j42d.RELEASE.im4p.plist",
    ]
    for rel in section_3_files:
        full = os.path.join(archive_dir, rel)
        assert os.path.isfile(full), f"Missing archive file: {full}"
        sz = os.path.getsize(full)
        h = sha256_path(full)
        print(f"  {rel}: size={sz:,}, sha256={h}")

    # 3. Section 4: Extracted Kernel & Firmware Components
    print(f"\n[3] Section 4 Extracted Firmware & Kernel Components:")
    section_4_files = [
        "extracted/ipsw/kernel/kernelcache.macho",
        "extracted/ipsw/firmware/DeviceTree.bin",
        "extracted/ipsw/firmware/LLB.bin",
        "extracted/ipsw/firmware/iBoot.bin",
        "extracted/ipsw/firmware/iBSS.bin",
        "extracted/ipsw/firmware/iBEC.bin",
        "extracted/ipsw/firmware/applelogo.png",
        "extracted/ipsw/firmware/recoverymode.png",
    ]
    for rel in section_4_files:
        full = os.path.join(PROJECT_ROOT, rel)
        assert os.path.isfile(full), f"Missing extracted component: {full}"
        sz = os.path.getsize(full)
        h = sha256_path(full)
        print(f"  {rel}: size={sz:,}, sha256={h}")

    # 4. Section 5.2: Key Binaries & System Daemons Recovered
    print(f"\n[4] Section 5.2 Key Binaries:")
    binaries = [
        ("usr/local/bin/restored_external", ["extracted/ipsw/ramdisk_erase/usr/local/bin/restored_external"]),
        ("usr/local/bin/restored_update", ["extracted/ipsw/ramdisk_update/usr/local/bin/restored_update"]),
        ("usr/local/bin/tconctl", ["extracted/ipsw/ramdisk_erase/usr/local/bin/tconctl", "extracted/ipsw/ramdisk_update/usr/local/bin/tconctl"]),
        ("usr/local/bin/configdarwinbootargs", ["extracted/ipsw/ramdisk_update/usr/local/bin/configdarwinbootargs"]),
        ("usr/sbin/asr", ["extracted/ipsw/ramdisk_erase/usr/sbin/asr", "extracted/ipsw/ramdisk_update/usr/sbin/asr"]),
        ("usr/libexec/diskimagesiod", ["extracted/ipsw/ramdisk_erase/usr/libexec/diskimagesiod", "extracted/ipsw/ramdisk_update/usr/libexec/diskimagesiod"]),
        ("usr/libexec/driverkitd", ["extracted/ipsw/ramdisk_erase/usr/libexec/driverkitd", "extracted/ipsw/ramdisk_update/usr/libexec/driverkitd"]),
        ("usr/libexec/seputil", ["extracted/ipsw/ramdisk_erase/usr/libexec/seputil", "extracted/ipsw/ramdisk_update/usr/libexec/seputil"]),
        ("usr/sbin/nvram", ["extracted/ipsw/ramdisk_erase/usr/sbin/nvram", "extracted/ipsw/ramdisk_update/usr/sbin/nvram"]),
        ("usr/sbin/ioreg", ["extracted/ipsw/ramdisk_erase/usr/sbin/ioreg", "extracted/ipsw/ramdisk_update/usr/sbin/ioreg"]),
        ("System/Library/Filesystems/apfs.fs/mount_apfs", ["extracted/ipsw/ramdisk_erase/System/Library/Filesystems/apfs.fs/mount_apfs", "extracted/ipsw/ramdisk_update/System/Library/Filesystems/apfs.fs/mount_apfs"]),
        ("System/Library/Filesystems/apfs.fs/fsck_apfs", ["extracted/ipsw/ramdisk_erase/System/Library/Filesystems/apfs.fs/fsck_apfs", "extracted/ipsw/ramdisk_update/System/Library/Filesystems/apfs.fs/fsck_apfs"]),
        ("System/Library/Filesystems/apfs.fs/newfs_apfs", ["extracted/ipsw/ramdisk_erase/System/Library/Filesystems/apfs.fs/newfs_apfs", "extracted/ipsw/ramdisk_update/System/Library/Filesystems/apfs.fs/newfs_apfs"]),
        ("System/DriverKit/usr/lib/swift/libswiftCore.dylib", ["extracted/ipsw/ramdisk_erase/System/DriverKit/usr/lib/swift/libswiftCore.dylib", "extracted/ipsw/ramdisk_update/System/DriverKit/usr/lib/swift/libswiftCore.dylib"]),
    ]
    for name, paths in binaries:
        for p in paths:
            full = os.path.join(PROJECT_ROOT, p)
            assert os.path.isfile(full), f"Binary missing: {full}"
            sz = os.path.getsize(full)
            h = sha256_path(full)
            print(f"  {p}: size={sz:,}, sha256={h}")

    # 5. Section 5.3: Recovered UI Graphics & Multi-Resolution Assets
    print(f"\n[5] Section 5.3 UI Graphics & Multi-Resolution Assets:")
    ui_assets = [
        ("usr/share/progressui/images-AppleTV-1080/applelogo.tga", ["extracted/ipsw/ramdisk_erase/usr/share/progressui/images-AppleTV-1080/applelogo.tga", "extracted/ipsw/ramdisk_update/usr/share/progressui/images-AppleTV-1080/applelogo.tga"]),
        ("usr/share/progressui/images-AppleTV-2160/applelogo.tga", ["extracted/ipsw/ramdisk_erase/usr/share/progressui/images-AppleTV-2160/applelogo.tga", "extracted/ipsw/ramdisk_update/usr/share/progressui/images-AppleTV-2160/applelogo.tga"]),
        ("usr/share/progressui/images-AppleTV/applelogo.png", ["extracted/ipsw/ramdisk_erase/usr/share/progressui/images-AppleTV/applelogo.png", "extracted/ipsw/ramdisk_update/usr/share/progressui/images-AppleTV/applelogo.png"]),
        ("usr/share/progressui/images-1x/applelogo.png", ["extracted/ipsw/ramdisk_erase/usr/share/progressui/images-1x/applelogo.png", "extracted/ipsw/ramdisk_update/usr/share/progressui/images-1x/applelogo.png"]),
        ("usr/share/progressui/images-2x/applelogo.png", ["extracted/ipsw/ramdisk_erase/usr/share/progressui/images-2x/applelogo.png", "extracted/ipsw/ramdisk_update/usr/share/progressui/images-2x/applelogo.png"]),
        ("usr/share/progressui/power-button-prompt.tga", ["extracted/ipsw/ramdisk_erase/usr/share/progressui/power-button-prompt.tga", "extracted/ipsw/ramdisk_update/usr/share/progressui/power-button-prompt.tga"]),
        ("usr/share/progressui/disconnect-prompt.tga", ["extracted/ipsw/ramdisk_erase/usr/share/progressui/disconnect-prompt.tga", "extracted/ipsw/ramdisk_update/usr/share/progressui/disconnect-prompt.tga"]),
        ("System/Library/PrivateFrameworks/CoreAccessories.framework/vision.pro.developer.strap-N301a.png", ["extracted/ipsw/ramdisk_update/System/Library/PrivateFrameworks/CoreAccessories.framework/vision.pro.developer.strap-N301a.png"]),
    ]
    for name, paths in ui_assets:
        for p in paths:
            full = os.path.join(PROJECT_ROOT, p)
            assert os.path.isfile(full), f"UI asset missing: {full}"
            sz = os.path.getsize(full)
            h = sha256_path(full)
            with Image.open(full) as img:
                dims = f"{img.size[0]}×{img.size[1]}"
                fmt = img.format
                mode = img.mode
            print(f"  {p}: size={sz:,}, format={fmt} ({dims} {mode}), sha256={h}")

    print("\n" + "=" * 80)
    print("ALL DELIVERABLES SUCCESSFULLY AUDITED")
    print("=" * 80)

if __name__ == "__main__":
    audit_all()
