#!/usr/bin/env python3
"""
Test script verifying that the proposed corrections to reports/IPSW_EXTRACTION_LEDGER.md
achieve 100% verification across all tables without a single mismatch or missing file.
"""

import os
import re
import hashlib
import unittest

PROJECT_ROOT = "/home/prem/Projects/AppleTV"

# Proposed Table 5.2
PROPOSED_TABLE_5_2 = """
| Relative Path in Ramdisk | Size (Bytes) | Executable Architecture | SHA-256 Digest | Role / Function |
| :--- | :--- | :--- | :--- | :--- |
| `usr/local/bin/restored_external` | 2,490,736 | Mach-O 64-bit arm64 | `25e55def1499f75b94c1958e409dd075ebb084e5112e2e07db71b81fbcc77fdf` | Primary Erase Restore Daemon |
| `usr/local/bin/restored_update` | 2,489,776 | Mach-O 64-bit arm64 | `624a2d945fd1678952cc25d271736114c0a7b790c3e492c86fdfa7e0fa424b1f` | Primary Upgrade Restore Daemon |
| `usr/local/bin/tconctl` | 242,480 | Mach-O 64-bit arm64 | `36035b437a11e4420d35382f247fe5b6c51c0d85a4ab20432dc5843760d6bc32` | Timing Controller Diagnostic Tool |
| `usr/local/bin/configdarwinbootargs`| 54,400 | Mach-O 64-bit arm64 | `7c91692c13f26524b93ec69b8dfada54d91efee89719ba06dcc5b3f5ca8c352f` | Darwin Boot Arguments Configurator (Exclusive to ramdisk_update) |
| `usr/sbin/asr` | 396,848 | Mach-O 64-bit arm64 | `44663b15113a52f248b6c83f8c77977d4a22ce2566e388b1687c5b1503fc0be5` | Apple Software Restore Engine |
| `usr/libexec/diskimagesiod` | 2,311,200 | Mach-O 64-bit arm64 | `77ebc1f0bc4367dd81f4e1cb3a186d9ff20d4cd6d4c6c43a13a9e51d7a182aaf` | DiskImages2 I/O Controller Daemon |
| `usr/libexec/driverkitd` | 1,317,984 | Mach-O 64-bit arm64 | `ef5bea1dc3c425b1d225fde97be6f967107db382a8020138ab69a257bdfc6b10` | User-space DriverKit Server |
| `usr/libexec/seputil` | 187,264 | Mach-O 64-bit arm64 | `55d1fbed1ee9770b24afd5c4c2c078935119dbb122b42f55b80bcb7eafc03fe2` | Secure Enclave Processor Utility |
| `usr/sbin/nvram` | 57,424 | Mach-O 64-bit arm64 | `0e1cea414a30a260b67b9374978bcbe069542954480abff2608dff2ff6249d1b` | NVRAM Variable Management Tool |
| `usr/sbin/ioreg` | 75,072 | Mach-O 64-bit arm64 | `38ac5dea0d7481f6de124ec88a390c2eb1bbfb184075b9ee123210a36c19726c` | I/O Kit Registry Inspector |
| `System/Library/Filesystems/apfs.fs/mount_apfs` | 72,912 | Mach-O 64-bit arm64 | `ecd23b8f5c55f4a86bb1bcc062f1e7f3248450eb1263ae2065f5c5bcfbeb9e00` | APFS Volume Mount Binary (Target of `sbin/mount_apfs`) |
| `System/Library/Filesystems/apfs.fs/fsck_apfs` | 561,536 | Mach-O 64-bit arm64 | `4be481e681d2c555b3a91d293d57487f1694855a2358364cd6df496314e38355` | APFS Filesystem Consistency Checker (Target of `sbin/fsck_apfs`) |
| `System/Library/Filesystems/apfs.fs/newfs_apfs` | 508,400 | Mach-O 64-bit arm64 | `d863028a0a01f90edb577d410917bc1a08086acf06126f26ab8ca1c12067e787` | APFS Filesystem Formatter (Target of `sbin/newfs_apfs`) |
| `System/DriverKit/usr/lib/swift/libswiftCore.dylib` | 7,639,536 | Mach-O 64-bit arm64 dylib | `8da318172d23a57f2e46648a49e1beec22bc304d35c54802bbb51e6178590ce5` | Swift 5.x DriverKit Core Runtime |
"""

# Proposed Table 5.3
PROPOSED_TABLE_5_3 = """
| Asset Path in Ramdisk | Size (Bytes) | Format / Dimensions | SHA-256 Digest | Description |
| :--- | :--- | :--- | :--- | :--- |
| `usr/share/progressui/images-AppleTV-1080/applelogo.tga` | 9,458 | TGA (225×365 RGBA) | `8326ee0a71555dbca5e5b43d5ce4e4efc338cb7595a3b405b2a8535e6c08d519` | 1080p Full HD Apple Restore Logo (RLE-compressed TGA) |
| `usr/share/progressui/images-AppleTV-2160/applelogo.tga` | 23,222 | TGA (450×730 RGBA) | `044910aae1f0eaa0aa0a0b20022a692588a77c0197073ffbd2637f74d7f44f5a` | 4K Ultra HD Apple Restore Logo (RLE-compressed TGA) |
| `usr/share/progressui/images-AppleTV/applelogo.png` | 3,472 | PNG (150×243 RGBA) | `b71a97d4d788154878a4a7189aa33e7037ed46e19656039bf2df35554e7aa48c` | Standard Apple TV Restore Logo |
| `usr/share/progressui/images-1x/applelogo.png` | 7,281 | PNG (96×160 RGBA) | `62684d198df299411ecd0aac2293752d4f0611b549822ef54661c1d6858cde64` | 1x Standard Display Restore Logo |
| `usr/share/progressui/images-2x/applelogo.png` | 16,216 | PNG (192×320 RGBA) | `a1b7ee0d7cd01d1da3a26dc17a1211e8e057a340c801c19bf38aff01c5809cc4` | 2x Retina Display Restore Logo |
| `usr/share/progressui/power-button-prompt.tga` | 169,162 | TGA (1536×2048 RGBA) | `473986a867afcc4c419ddd3bef74bd71f86364fd519f1b065a7537932ca38721` | Full Screen Power Button Prompt Vector |
| `usr/share/progressui/disconnect-prompt.tga` | 171,849 | TGA (1536×2048 RGBA) | `e8523c3bf4a0cf88f73df24b4a2c79ac504f35e22edeca33e7c52f623291777c` | Full Screen Cable Disconnect Prompt |
| `System/Library/PrivateFrameworks/CoreAccessories.framework/vision.pro.developer.strap-N301a.png` | 31,190 | PNG (1024×1024 RGBA) | `dfe2c789a7fcf8ca174dee87f42c67fb99cdf3a2e880fa5d6789c9485121763d` | Apple Vision Pro Developer Strap Graphic (Exclusive to ramdisk_update) |
"""

def test_proposed():
    with open(os.path.join(PROJECT_ROOT, "reports/IPSW_EXTRACTION_LEDGER.md"), "r") as f:
        content = f.read()

    # Splice proposed tables
    # Find Section 5.2
    idx52 = content.find("### 5.2 Key Binaries & System Daemons Recovered")
    idx53 = content.find("### 5.3 Recovered UI Graphics & Multi-Resolution Assets")
    idx6 = content.find("## 6. Comparison: tvOS 13.4.8")

    pre = content[:idx52]
    post = content[idx6:]

    simulated_content = (
        pre
        + "### 5.2 Key Binaries & System Daemons Recovered\n"
        + PROPOSED_TABLE_5_2.strip()
        + "\n\n### 5.3 Recovered UI Graphics & Multi-Resolution Assets\n\n"
        + PROPOSED_TABLE_5_3.strip()
        + "\n\n---\n\n"
        + post
    )

    row_pattern = re.compile(
        r"\|\s*`([^`]+)`\s*\|\s*([0-9,]+)\s*\|.*?`([0-9a-f]{64})`\s*\|",
        re.MULTILINE
    )

    matches = row_pattern.findall(simulated_content)
    print(f"Total rows extracted from simulated ledger: {len(matches)}")

    mismatches = []
    audited = 0

    for rel_path, size_str, recorded_hash in matches:
        expected_size = int(size_str.replace(",", ""))

        candidates = [
            os.path.join(PROJECT_ROOT, rel_path),
            os.path.join(PROJECT_ROOT, "extracted/ipsw/ramdisk_erase", rel_path),
            os.path.join(PROJECT_ROOT, "extracted/ipsw/ramdisk_update", rel_path),
            os.path.join(PROJECT_ROOT, "AppleTV5,3_26.6.1_23L781_Restore", rel_path),
        ]

        disk_file = None
        for cand in candidates:
            if os.path.exists(cand) and not os.path.isdir(cand):
                disk_file = cand
                break

        if disk_file is None:
            mismatches.append(f"MISSING: {rel_path}")
            continue

        actual_size = os.path.getsize(disk_file)
        if actual_size != expected_size:
            mismatches.append(f"SIZE MISMATCH for {rel_path}: actual {actual_size} vs expected {expected_size}")
            continue

        with open(disk_file, "rb") as fp:
            actual_hash = hashlib.sha256(fp.read()).hexdigest()
        if actual_hash != recorded_hash:
            mismatches.append(f"HASH MISMATCH for {rel_path}: actual {actual_hash} vs recorded {recorded_hash}")
            continue

        audited += 1

    print(f"Audited {audited} rows successfully.")
    print(f"Total mismatches: {len(mismatches)}")
    if mismatches:
        for m in mismatches:
            print("  FAIL:", m)
    else:
        print("ALL AUDITED ROWS PASSED 100% BIT-FOR-BIT VERIFICATION!")

if __name__ == "__main__":
    test_proposed()
