# Forensic Survey Report: Restore Ramdisks, Kernelcache & Firmware Components
**Target Firmware**: `AppleTV5,3_26.6.1_23L781_Restore.ipsw` (Build `23L781`, Model `AppleTV5,3` / Apple TV HD A1625, Apple A8 SoC)  
**Author**: `explorer_survey_ipsw_2`  
**Date**: 2026-11-06  
**Status**: Complete & Verified  

---

## 1. Executive Summary & Inventory Matrix

This survey provides exhaustive forensic inspection, cryptographic boundary identification, and verified extraction recipes for the unencrypted restore ramdisks, kernelcache, and firmware partition components inside the official Apple TV full restore IPSW (`AppleTV5,3_26.6.1_23L781_Restore.ipsw`).

### Component Forensic Inventory

| Component File | Size (Bytes) | Outer Container | Inner Format | Compression | Encryption | Extractability |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `094-97800-089.dmg` | 113,246,235 | IM4P (`rdsk`) | APFS (`NXSB`) | None (Uncomp APFS) | Plaintext | **100% Extractable** (7z / dd) |
| `094-97880-089.dmg` | 113,246,235 | IM4P (`rdsk`) | APFS (`NXSB`) | None (Uncomp APFS) | Plaintext | **100% Extractable** (7z / dd) |
| `kernelcache.release.j42d` | 21,964,283 | IM4P (`krnl`) | Mach-O 64-bit ARM64 | Apple LZSS (`complzss`) | Plaintext | **100% Extractable** (pyimg4/lzss) |
| `DeviceTree.j42dap.im4p` | 17,246 | IM4P (`dtre`) | Apple DeviceTree | LZFSE (`bvx2`) | Plaintext | **100% Extractable** (pyimg4/lzfse) |
| `LLB.j42d.RELEASE.im4p` | 205,081 | IM4P (`illb`) | ARM64 Raw Binary | None | Plaintext | **100% Extractable** (pyimg4) |
| `iBSS.j42d.RELEASE.im4p` | 205,081 | IM4P (`ibss`) | ARM64 Raw Binary | None | Plaintext | **100% Extractable** (Identical to LLB) |
| `iBoot.j42d.RELEASE.im4p` | 846,105 | IM4P (`ibot`) | ARM64 Raw Binary | None | Plaintext | **100% Extractable** (pyimg4) |
| `iBEC.j42d.RELEASE.im4p` | 846,105 | IM4P (`ibec`) | ARM64 Raw Binary | None | Plaintext | **100% Extractable** (Identical to iBoot) |
| `applelogo~appletv.im4p` | 4,767 | IM4P (`logo`) | `iBootIm` (108x131 LA) | Apple LZSS | Plaintext | **100% Extractable** (Pillow PNG) |
| `recoverymode@1080~appletv5.im4p`| 44,629 | IM4P (`recm`) | `iBootIm` (582x154 BGRA)| Apple LZSS | Plaintext | **100% Extractable** (Pillow PNG) |
| `sep-firmware.j42d.RELEASE.im4p` | 2,171,132 | IM4P (`sepi`) | SEP Mach-O / OS | None | **Encrypted** (2 KBAGs)| **Hardware GID Gated** |
| `094-97800-089.dmg.trustcache` | 6,427 | IM4P (`rtsc`) | TrustCache v1 (290) | None | Plaintext | **100% Parseable** |
| `094-97880-089.dmg.trustcache` | 6,515 | IM4P (`rtsc`) | TrustCache v1 (294) | None | Plaintext | **100% Parseable** |
| `094-98220-089.dmg.aea.trustcache`| 5,903 | IM4P (`trst`) | TrustCache v2 (266) | None | Plaintext | **100% Parseable** |
| `094-98312-089.dmg.aea.trustcache`| 32,615 | IM4P (`trst`) | TrustCache v2 (1357)| None | Plaintext | **100% Parseable** |
| `094-98312-089.dmg.aea.mtree` | 27,131,653 | IM4P (`msys`) | AppleArchive (`AA01`)| pbze (LZFSE chunks)| Plaintext | **100% Decompressible** |
| `094-98312-089.dmg.aea.root_hash`| 229 | IM4P (`isys`) | APFS Root Hash Seal | None | Plaintext | **100% Inspectable** |

---

## 2. Restore Ramdisks Forensic Inspection

### Container Format & ASN.1 DER Header Breakdown
Both `094-97800-089.dmg` and `094-97880-089.dmg` are exact 113,246,235-byte files containing an IM4P wrapper around an uncompressed Apple File System (APFS) image.

```
Offset 0x00: 30 84 06 c0 00 15   (ASN.1 SEQUENCE, length = 113,246,229 bytes)
Offset 0x06: 16 04 49 4d 34 50   (IA5String "IM4P")
Offset 0x0c: 16 04 72 64 73 6b   (IA5String "rdsk")
Offset 0x12: 16 01 30            (IA5String "0" - description/version)
Offset 0x15: 04 84 06 c0 00 00   (OCTET STRING, length = 113,246,208 bytes = 0x6C00000 = exactly 108 MiB)
Offset 0x1b: [Start of raw APFS image payload]
```

### APFS Container Superblock Analysis
At relative byte 0x20 into the payload (file offset `0x3b` = 59):
- **Magic**: `4e 58 53 42 00` (`NXSB` at byte 32 of block 0)
- **Block Size**: 4096 bytes (`0x1000`)
- **Block Count**: 27,648 blocks
- **Total Filesystem Size**: $27,648 \times 4096 = 113,246,208\text{ bytes}$
- **Incompatible Features**: `0x02` (`NORMALIZATION_INSENSITIVE`)
- **Encryption**: None (`features = 0x0`, no crypto metadata, completely plaintext)

### Erase vs Update Ramdisk Roles

By cross-referencing `BuildManifest.plist` against the two DMGs:
- **`094-97800-089.dmg`**: Assigned to `Customer Erase Install (IPSW)` and `Recovery Customer Install`. Role: **Erase Restore Ramdisk**.
- **`094-97880-089.dmg`**: Assigned to `Customer Upgrade Install (IPSW)`. Role: **Update Restore Ramdisk**.

### Content Comparison & File Ledger

| Metric | `094-97800-089.dmg` (Erase) | `094-97880-089.dmg` (Update) |
| :--- | :--- | :--- |
| **Total Files** | 855 files (750 regular, 100 symlinks) | 1,005 files (900 regular, 100 symlinks) |
| **Total Directories** | 314 folders | 364 folders |
| **Uncompressed Size** | 268,824,552 bytes (~268.8 MB) | 272,349,852 bytes (~272.3 MB) |
| **Primary Daemon** | `usr/local/bin/restored_external` | `usr/local/bin/restored_update` |
| **LaunchDaemon Plist** | `com.apple.restored_external.plist` | `com.apple.restored_update.plist` |
| **Unique Components** | 2 files unique (daemon + plist) | 152 files unique (AppleRestoreUtils, CoreAccessories strings, HeimdalASN1) |

### Key Executables and Frameworks Recovered from Ramdisk
Both ramdisks provide an accessible archive of macOS/tvOS Darwin binaries and private frameworks:
- **Restore Daemons**: `usr/local/bin/restored_external` (2.49 MB) and `usr/local/bin/restored_update` (2.49 MB)
- **Filesystem Utilities**: `sbin/mount_apfs`, `sbin/newfs_apfs`, `sbin/fsck_apfs`, `sbin/apfs_hfs_convert`, `sbin/mount`, `sbin/fsck`
- **Device Management**: `usr/sbin/asr` (Apple Software Restore), `usr/libexec/diskimagesiod`, `usr/libexec/seputil`, `usr/libexec/driverkitd`, `usr/sbin/ioreg`, `usr/sbin/nvram`, `usr/sbin/hdik`
- **Firmware Flashers**: `usr/bin/nvmefwupdater`, `usr/bin/update_mcdp29xx`, `usr/bin/ampctl`, `usr/bin/peppytool`, `usr/bin/usbcfwflasher`, `usr/bin/TiSerialFlasher`
- **Core Frameworks**: `CoreFoundation`, `Foundation`, `CFNetwork`, `Security`, `CryptoKit`, `Network`, `DriverKit`, `PCIDriverKit`, `CoreCaptureDriverKit`
- **Swift Runtime**: `System/DriverKit/usr/lib/swift/libswiftCore.dylib` (7.64 MB)

---

## 3. Kernelcache Forensic Inspection (`kernelcache.release.j42d`)

### IM4P Envelope Breakdown
`kernelcache.release.j42d` is an IM4P container of size 21,964,283 bytes:
- **FourCC Tag**: `krnl`
- **Description**: `KernelCacheBuilder_release-3244.160.2`
- **Payload Offset**: Byte 63
- **Payload Length**: 21,964,220 bytes

### `complzss` Header Analysis
Starting at byte offset 63:
```
Offset 0x00 (file 63):  63 6f 6d 70 6c 7a 73 73   "complzss"
Offset 0x08 (file 71):  df dd bd 11               Adler32 Checksum (0xdfddbd11, Big-Endian)
Offset 0x0c (file 75):  02 a1 40 00               Uncompressed Size (44,122,112 bytes = 44.12 MB)
Offset 0x10 (file 79):  01 4e a4 3c               Compressed Size (21,931,068 bytes = 21.93 MB)
Offset 0x14 (file 83):  00 00 00 01               Version (1)
Offset 0x18 - 0x180:    00 00 00 ...              Zero padding (360 bytes)
Offset 0x180 (file 447): ff cf fa ed fe 0c ...    Start of LZSS compressed byte stream
```

### Decompression & Checksum Verification
- **Decompression Algorithm**: Apple LZSS ($N=4096$, $F=18$, $\text{THRESHOLD}=2$, ring buffer initialized to space `0x20`, start offset $N-F=4078$).
- **Decompressed Size**: Exactly 44,122,112 bytes.
- **Adler-32 Verification**: Calculated `adler32(decompressed)` = `0xdfddbd11` $\rightarrow$ **Exact 100% Match**.
- **Execution Performance**: 
  - Host C decompressor: **0.05 seconds**
  - Python `pyimg4` / `lzss` (C-extension): **0.21 seconds**

### Decompressed Mach-O Header Verification
- **Magic**: `0xfeedfacf` (`MH_MAGIC_64`)
- **CPU Type**: `0x0100000c` (`CPU_TYPE_ARM64`)
- **CPU Subtype**: `0x00000000` (`CPU_SUBTYPE_ARM64_ALL`)
- **Filetype**: `0x00000002` (`MH_EXECUTE`)
- **Number of Load Commands**: 25 (`0x00000019`)
- **Size of Load Commands**: 5,056 bytes (`0x000013c0`)
- **Flags**: `0x00200001` (`MH_NOUNDEFS | 0x200000`)
- **First Segment**: `LC_SEGMENT_64` (`__TEXT`), VM Address: `0xfffffff007004000`, VM Size: `0x0000000000a00000`

---

## 4. Firmware Partition Components Inspection (`Firmware/`)

### 1. DeviceTree (`Firmware/all_flash/DeviceTree.j42dap.im4p`)
- **FourCC Tag**: `dtre`
- **Description**: `EmbeddedDeviceTrees-11156.160.23`
- **Encryption**: Plaintext (`encrypted: False`, 0 keybags)
- **Compression**: LZFSE (`bvx2` chunk at payload offset 0, compression ID 2)
- **Sizes**: Compressed payload: 17,182 bytes $\rightarrow$ Decompressed: 105,596 bytes
- **Format**: Standard Apple DeviceTree node structure containing device properties: `regulatory-model-number`, memory configurations, interrupt maps, SoC device registers for `j42dap` (Apple TV HD).

### 2. Bootloader Binaries
All four bootloader binaries are **completely unencrypted and uncompressed ARM64 machine code**:

| Bootloader | Path | FourCC | Payload Size | Compression | Encryption | Relationship |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **LLB** | `Firmware/all_flash/LLB.j42d.RELEASE.im4p` | `illb` | 205,040 B | None | Plaintext | Identical to iBSS |
| **iBSS** | `Firmware/dfu/iBSS.j42d.RELEASE.im4p` | `ibss` | 205,040 B | None | Plaintext | Identical to LLB |
| **iBoot** | `Firmware/all_flash/iBoot.j42d.RELEASE.im4p` | `ibot` | 846,064 B | None | Plaintext | Identical to iBEC |
| **iBEC** | `Firmware/dfu/iBEC.j42d.RELEASE.im4p` | `ibec` | 846,064 B | None | Plaintext | Identical to iBoot |

- **Version String**: `iBoot-13822.120.5`
- **Copyright**: `Copyright 2007-2026, Apple Inc.`
- **Boot Commands Identified**: `fsboot`, `upgrade`, `recover`, `checkerboard`, `ramdisk`, `rsepfirmware`, `devicetree`, `getenv`, `setenv`, `saveenv`.

### 3. Restore Logos & Graphical UI Assets
Both restore images are wrapped in IM4P envelopes containing `iBootIm` containers:

| Image File | FourCC | Dimensions | Pixel Format | Compression | Decompressed Size |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `applelogo~appletv.im4p` | `logo` | 108 × 131 | 16-bit `grey` (`LA` mode) | Apple LZSS | 28,296 bytes ($108 \times 131 \times 2$) |
| `recoverymode@1080~appletv5.im4p` | `recm` | 582 × 154 | 32-bit `bgra` (`RGBA` mode)| Apple LZSS | 358,512 bytes ($582 \times 154 \times 4$)|

#### `iBootIm` 64-byte Header Structure:
- `0x00 - 0x07`: `iBootIm\0` magic
- `0x08 - 0x0b`: Checksum / Adler32
- `0x0c - 0x0f`: Compression magic (`lzss` / `sszl`)
- `0x10 - 0x13`: Pixel format fourcc (`grey` or `bgra`)
- `0x14 - 0x15`: Width (uint16 LE)
- `0x16 - 0x17`: Height (uint16 LE)
- `0x18 - 0x1b`: Flags / reserved
- `0x1c - 0x1f`: Compressed data length (uint32 LE)
- `0x20 - 0x3f`: Zero padding
- `0x40`: Start of compressed LZSS stream

### 4. Secure Enclave Processor (`sep-firmware.j42d.RELEASE.im4p`)
- **FourCC Tag**: `sepi`
- **Description**: ASN.1 sequence containing `impl1`, `arms`, `tz0s` (SEP core configuration)
- **Encryption**: **ENCRYPTED** (`encrypted: True`)
- **Keybags**: 2 embedded hardware Keybags:
  - **Keybag 0 (Production)**: `IV: 054e049860f25383052332515937e6dd`, `Key: 05ae50652f30ad18ad7c263a22a5229271e213ca60037b5b553fefc7aaa84afd` (AES-256 wrapped with Apple Production GID key)
  - **Keybag 1 (Development)**: `IV: fff43d5112fed56c973ac8b5bf8842a2`, `Key: cba38de8c4dcb1eee31395ca71c6a8441674895a7de86a1b8aad860c96ca21b7` (AES-256 wrapped with Apple Development GID key)
- **Cryptographic Boundary**: Without hardware execution on the A8 Secure Enclave or Apple internal GID key derivation, offline decryption is cryptographically impossible.
- **Companion Plist**: `sep-firmware.j42d.RELEASE.im4p.plist` provides SHA-1 digests for `rsep` (`51811d0ea592a38eebda19144cd5d35da06f02ab`) and `sepi` (`0c4827a03c74e5c8288152319b6ddc5bf02eadc2`).

### 5. TrustCache Files (`.trustcache`)
Contains lists of Code Directory Hashes (CDHashes) authorized to execute on the platform:
- **`094-97800-089.dmg.trustcache`**: TrustCache Version 1, UUID `be1d901adb66485e9749db5178d8c400`, **290 CDHash entries** (22 bytes per entry: 20-byte hash + 1-byte hash type + 1-byte flags).
- **`094-97880-089.dmg.trustcache`**: TrustCache Version 1, UUID `b26ad94c51e34da5b3b81ff7ea9df559`, **294 CDHash entries**.
- **`094-98220-089.dmg.aea.trustcache`**: TrustCache Version 2, UUID `160e1cb36ac84300bb3dc7aab65349e5`, **266 CDHash entries** (24 bytes per entry).
- **`094-98312-089.dmg.aea.trustcache`**: TrustCache Version 2, UUID `63d78e19d1a14dc68d44d9023319e47d`, **1,357 CDHash entries**.

### 6. Canonical Metadata Mtrees (`.mtree`)
- **`094-98312-089.dmg.aea.mtree`** (27.13 MB) & **`094-98220-089.dmg.aea.mtree`** (1.38 MB)
- **FourCC Tag**: `msys`
- **Format**: `pbze` (Apple pbzx stream containing 4 MB chunks compressed with LZFSE)
- **Payload Contents**: Full unencrypted **AppleArchive (`AA01`)** manifest of the root filesystem! It lists every single path (`PATP`), file type (`TYP1`), permissions (`PMOD`), UID, GID, modification timestamps (`MTMT`), and SHA-256 hashes of all files in the system rootfs.
- **Architectural Significance**: Enables reconstruction of the complete tvOS 26.6.1 file tree and daemon inventory even while the rootfs disk image remains encrypted in `.aea`!

---

## 5. Host Tooling Survey & Environment Capabilities

| Tool / Library | Version / Path | Availability | Capability | Recommended Role in Pipeline |
| :--- | :--- | :--- | :--- | :--- |
| `7z` | 26.04 (`/usr/bin/7z`) | Installed | APFS extraction at offset 27 | Primary ramdisk unpacker |
| `python3` | 3.14.0 (`/usr/bin/python3`) | Installed | Full scripting & orchestration | Pipeline execution |
| `pyimg4` | 0.8.9 (user site-packages) | Installed | IM4P parsing, decompress, decrypt | IM4P extraction & unpacking |
| `lzss` | 0.3.9 (`pylzss` C-ext) | Installed | Apple LZSS fast decompression | Kernelcache & iBootIm decompression |
| `lzfse` | 0.4.2 (`lzfse` C-ext) | Installed | LZFSE decompressor | DeviceTree & pbze mtree decompression |
| `Pillow` (PIL) | 13.0.0 (`python3-pillow`) | Installed | Image conversion to PNG | Logo & recovery mode conversion |
| `gcc` / `clang` | Host native x86_64 | Installed | Fast C compilation | High-speed C decompression helpers |
| `llvm-objdump` | LLVM 19 (`/usr/bin`) | Installed | Mach-O 64-bit static inspection | Disassembly & header dumps |
| `hfsplus` / `undmg`| None | **Missing** | HFS+ parsing | **Not needed** (ramdisks are APFS) |
| `img4lib` | None | **Missing** | C IM4P utility | **Replaced by pyimg4** (verified superior) |

---

## 6. Verified Extraction Recipes for Phase 1 Workers

### Recipe 1: Restore Ramdisk Extraction (APFS to Directory)
Workers can extract the entire restore ramdisk filesystem using `7z`:

```bash
# Erase Ramdisk:
mkdir -p extracted/ipsw/ramdisk/erase
7z x AppleTV5,3_26.6.1_23L781_Restore/094-97800-089.dmg -oextracted/ipsw/ramdisk/erase/ -y

# Update Ramdisk:
mkdir -p extracted/ipsw/ramdisk/update
7z x AppleTV5,3_26.6.1_23L781_Restore/094-97880-089.dmg -oextracted/ipsw/ramdisk/update/ -y
```

*Alternative (extract pure raw APFS image without IM4P header):*
```bash
dd if=AppleTV5,3_26.6.1_23L781_Restore/094-97800-089.dmg of=extracted/ipsw/ramdisk/erase_raw.apfs bs=27 skip=1
```

---

### Recipe 2: Kernelcache Extraction & Decompression
Using Python with `pyimg4`:

```python
import sys
import pyimg4

src_path = 'AppleTV5,3_26.6.1_23L781_Restore/kernelcache.release.j42d'
dst_path = 'extracted/ipsw/kernel/kernelcache.release.j42d.macho'

kc = pyimg4.IM4P(open(src_path, 'rb').read())
kc.payload.decompress()

with open(dst_path, 'wb') as f:
  f.write(kc.payload.data)

print(
    f'Successfully extracted kernelcache: {len(kc.payload.data)} bytes'
    f' (Mach-O magic: {hex(int.from_bytes(kc.payload.data[:4], "little"))})'
)
```

---

### Recipe 3: DeviceTree Extraction & Decompression
Using Python with `pyimg4`:

```python
import pyimg4

src_path = 'AppleTV5,3_26.6.1_23L781_Restore/Firmware/all_flash/DeviceTree.j42dap.im4p'
dst_path = 'extracted/ipsw/firmware/DeviceTree.j42dap.bin'

dt = pyimg4.IM4P(open(src_path, 'rb').read())
dt.payload.decompress()

with open(dst_path, 'wb') as f:
  f.write(dt.payload.data)

print(f'DeviceTree decompressed: {len(dt.payload.data)} bytes')
```

---

### Recipe 4: Bootloader Files Extraction (LLB, iBoot, iBSS, iBEC)
All bootloaders extract raw ARM64 machine code directly:

```python
import pyimg4

bootloaders = {
    'LLB.bin': 'Firmware/all_flash/LLB.j42d.RELEASE.im4p',
    'iBoot.bin': 'Firmware/all_flash/iBoot.j42d.RELEASE.im4p',
    'iBSS.bin': 'Firmware/dfu/iBSS.j42d.RELEASE.im4p',
    'iBEC.bin': 'Firmware/dfu/iBEC.j42d.RELEASE.im4p',
}

for out_name, in_path in bootloaders.items():
  im4p = pyimg4.IM4P(open(f'AppleTV5,3_26.6.1_23L781_Restore/{in_path}', 'rb').read())
  with open(f'extracted/ipsw/firmware/{out_name}', 'wb') as f:
    f.write(im4p.payload.data)
  print(f'Extracted {out_name}: {len(im4p.payload.data)} bytes')
```

---

### Recipe 5: Restore Images Conversion to PNG
Convert `applelogo` and `recoverymode` to standard PNG:

```python
import sys
import lzss
from PIL import Image
import pyimg4

# 1. Apple Logo (108x131 16-bit Luminance+Alpha)
logo_im4p = pyimg4.IM4P(
    open(
        'AppleTV5,3_26.6.1_23L781_Restore/Firmware/all_flash/applelogo~appletv.im4p',
        'rb',
    ).read()
)
logo_raw = lzss.decompress(logo_im4p.payload.data[64:])
img_logo = Image.frombytes('LA', (108, 131), logo_raw)
img_logo.save('extracted/ipsw/firmware/applelogo.png')

# 2. Recovery Mode (582x154 32-bit BGRA)
recm_im4p = pyimg4.IM4P(
    open(
        'AppleTV5,3_26.6.1_23L781_Restore/Firmware/all_flash/recoverymode@1080~appletv5.im4p',
        'rb',
    ).read()
)
recm_raw = lzss.decompress(recm_im4p.payload.data[64:])
img_recm = Image.frombytes('RGBA', (582, 154), recm_raw, 'raw', 'BGRA')
img_recm.save('extracted/ipsw/firmware/recoverymode.png')
```

---

### Recipe 6: TrustCache CDHash Extraction
Dump all CDHashes from TrustCache v1 and v2:

```python
import struct
import pyimg4


def parse_trustcache(im4p_path):
  im4p = pyimg4.IM4P(open(im4p_path, 'rb').read())
  data = im4p.payload.data
  version = struct.unpack('<I', data[:4])[0]
  uuid = data[4:20].hex()
  count = struct.unpack('<I', data[20:24])[0]
  entries = []
  if version == 1:
    for i in range(count):
      offset = 24 + i * 22
      cdhash = data[offset : offset + 20].hex()
      hash_type = data[offset + 20]
      flags = data[offset + 21]
      entries.append((cdhash, hash_type, flags))
  elif version == 2:
    for i in range(count):
      offset = 24 + i * 24
      cdhash = data[offset : offset + 20].hex()
      hash_type = data[offset + 20]
      flags = data[offset + 21]
      entries.append((cdhash, hash_type, flags))
  return {'version': version, 'uuid': uuid, 'count': count, 'entries': entries}
```

---

## 7. Strict Host Safety Verification

- **All analyzed firmware components are ARM64 machine code or proprietary Apple data structures.**
- **ZERO firmware binaries were executed on the Linux x86_64 host.**
- **All forensic inspections were performed via static ASN.1 DER parsing, header extraction, and userspace decompressors (`7z`, `pyimg4`, `lzfse`, `lzss`, `PIL`).**
