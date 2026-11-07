# Extraction Architecture & Payload Investigation Report

**Agent**: Explorer Survey 3 (Extraction Architecture Explorer)  
**Workspace Root**: `/home/prem/Projects/AppleTV`  
**Report Path**: `/home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_3/handoff.md`  
**Date**: 2026-11-06T17:35:00Z  

---

## 1. Observation

### 1.1 Archive Container & Payload Layout
Direct inspection of `/home/prem/Projects/AppleTV/8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip` (size: 2,014,940,073 bytes) and its matching uncompressed tree `8988ef3518b1f20f95c66d03be3c15eb4e1be2a0` (101 files, 2,079,226,051 bytes) shows:
- **`AssetData/payloadv2/`**: Contains 26 payload archives (`data_payload`, `payload.000` through `payload.024`), 25 `.ecc` error-correction files, `prepare_payload` (12 bytes), `payload_chunks.txt` (331 bytes), and `links.txt` (0 bytes).
- **`AssetData/boot/`**: Contains `BuildManifest.plist` (48,898 bytes), `kernelcache.release.j105a` (11,891,668 bytes), `038-50764-064.dmg.image-img4` (73,174,043 bytes), and `Firmware/` (`all_flash/`, `dfu/`, `AOP/`).
- **`AssetData/payload/replace/`**: Contains `usr/standalone/update/ramdisk/arm64SURamDisk.dmg` (73,174,043 bytes) and `all_flash/` (`applelogo~appletv.im4p`, `recoverymode@1080~appletv5.im4p`).
- **BOM Manifests**: `AssetData/payload.bom` (40,596 bytes), `AssetData/pre.bom` (35,046 bytes), `AssetData/post.bom` (6,300,220 bytes, `BOMStore\x00\x00\x00\x01`).

### 1.2 Binary Magic Bytes & Header Analysis
Direct binary inspection revealed the following exact headers:
- **`prepare_payload`**: `70 62 7a 78 00 00 00 00 00 80 00 00`  
  ASCII: `pbzx` + 64-bit uint `0x0000000000800000` (8,388,608 bytes / 8 MB buffer size).
- **`data_payload` & `payload.000`–`payload.024`**: All 26 files begin with `pbzx\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00` (PBZX magic + 8 MB chunk buffer flag).
- **`038-50764-064.dmg.image-img4` & `arm64SURamDisk.dmg`**: ASN.1 DER sequence (`0x30`), Tag `IM4P`, Type `rdsk` (ramdisk).
  Stripping the 27-byte ASN.1 header exposes a raw HFSX disk image:  
  Offset 1024: `48 58 00 05 80 00 01 00 31 30 2e 30` (`HX\x00\x05` = HFSX, Volume: `YagerG17M61.arm64SURamDisk`).
- **`kernelcache.release.j105a`**: ASN.1 DER sequence (`0x30`), Tag `IM4P`, Type `krnl` (kernel).
  Element 3 is an unencrypted LZFSE payload: `62 76 78 32 16 a9 00 00` (`bvx2` magic). No encryption keybag.
- **Firmware IM4P Files**:
  - `DeviceTree.j105aap.im4p`: Tag `dtre`, 4 ASN.1 elements, NO keybag (unencrypted).
  - `applelogo~appletv.im4p`: Tag `logo`, 4 ASN.1 elements, NO keybag (unencrypted `iBootIm`).
  - `recoverymode@1080~appletv5.im4p`: Tag `recm`, 4 ASN.1 elements, NO keybag (unencrypted `iBootIm`).
  - `aopfw-j105aaop.im4p`: Tag `aopf`, 4 ASN.1 elements, NO keybag (unencrypted AOP firmware).
  - `LLB.j105a.RELEASE.im4p`: Tag `illb`, 5 ASN.1 elements, includes hardware GID KBAG (encrypted).
  - `iBoot.j105a.RELEASE.im4p`: Tag `ibot`, 5 ASN.1 elements, includes hardware GID KBAG (encrypted).
  - `sep-firmware.j105a.RELEASE.im4p`: Tag `sepi`, 5 ASN.1 elements, includes hardware GID KBAG (encrypted).
  - `iBEC.j105a.RELEASE.im4p`: Tag `ibec`, 5 ASN.1 elements, includes hardware GID KBAG (encrypted).
  - `iBSS.j105a.RELEASE.im4p`: Tag `ibss`, 5 ASN.1 elements, includes hardware GID KBAG (encrypted).

### 1.3 PBZX Chunk Compression & Distribution
Iterating over all 26 payload archives revealed:
- **Total Chunks**: 518 chunks.
- **Compression Types**:
  - `xz` (`fd 37 7a 58 5a 00` / `\xfd7zXZ`): 501 chunks (96.7%).
  - `uncompressed` (`dlen == clen`): 17 chunks (3.3%).
  - `lzfse` (`bvx`): 0 chunks.
  - `bzip2` (`BZh`): 0 chunks.
- **Total Compressed Size**: 1,899,524,868 bytes (1.77 GB).
- **Total Decompressed Size**: 4,210,309,961 bytes (3.92 GB).
- **Compression Ratio**: 2.22x.

#### Full Payload Chunk & Size Table
| Archive File | Compressed Size | Chunks | Decompressed Size | Primary Contents |
| :--- | :--- | :--- | :--- | :--- |
| `data_payload` | 494,292 | 1 | 1,469,403 | `private/var` hierarchy & data templates |
| `payload.000` | 172,048 | 1 | 3,531,268 | Rootfs directory tree (26,180 records, plists, strings) |
| `payload.001` | 252,996,028 | 130 | 1,086,013,530 | `System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64` |
| `payload.002` | 125,821,976 | 16 | 125,862,607 | `Applications/TVIdleScreen.app/Default@2x.mov` |
| `payload.003` | 129,625,352 | 16 | 129,714,767 | `Applications/TVIdleScreen.app/Default@2x_HDR.mov` |
| `payload.004` | 28,980,900 | 11 | 91,411,582 | `System/Library/CoreServices/CoreGlyphs.bundle/Assets.car` |
| `payload.005` | 45,543,808 | 10 | 77,081,731 | `System/Library/Fonts/LanguageSupport/PingFang.ttc` |
| `payload.006` | 81,896,748 | 13 | 104,295,536 | `System/Library/Fonts/Core/AppleColorEmoji@2x.ttc` |
| `payload.007` | 77,625,160 | 14 | 112,419,144 | `System/Library/Frameworks/Vision.framework/landmarks_v2.bin` |
| `payload.008` | 78,613,708 | 12 | 93,000,464 | `System/Library/Frameworks/Vision.framework/...espresso.weights` |
| `payload.009` | 75,767,208 | 11 | 88,595,778 | `System/Library/LinguisticData/.../Chinese.lm/lm.dat` |
| `payload.010` | 64,288,892 | 14 | 109,869,570 | `Applications/AppStore.app/Assets.car` |
| `payload.011` | 77,192,800 | 16 | 127,984,805 | `Applications/Arcade.app/Assets.car` |
| `payload.012` | 78,972,032 | 17 | 138,852,866 | `System/Library/PrivateFrameworks/VideoProcessing.framework/...` |
| `payload.013` | 86,982,912 | 21 | 170,630,728 | `System/Library/SpellingKeyboardSpeechModels/...` |
| `payload.014` | 81,192,692 | 17 | 138,167,501 | `System/Library/Audio/Tunings/IRs/Generic/HRIR_Movie.ir` |
| `payload.015` | 79,582,824 | 19 | 151,916,528 | `Applications/Podcasts.app/Assets.car` |
| `payload.016` | 73,805,104 | 18 | 148,903,674 | `Applications/TVShows.app/Assets.car` |
| `payload.017` | 74,030,332 | 23 | 189,952,056 | `Applications/PineBoard.app/PineBoard`, `AppStore.app/AppStore` |
| `payload.018` | 80,782,232 | 21 | 169,636,233 | `Applications/HeadBoard.app/Assets.car`, `TVMusic`, `TVSettings` |
| `payload.019` | 77,139,768 | 18 | 143,014,078 | `System/Library/CoreServices/VoiceOverTouch.app/vot` |
| `payload.020` | 81,603,188 | 20 | 159,503,754 | `Applications/HeadBoard.app/HeadBoard`, `AppleTV.app/Assets.car` |
| `payload.021` | 69,028,424 | 29 | 237,858,251 | `Applications/AppleTV.app/AppleTV.js` |
| `payload.022` | 57,567,964 | 30 | 246,533,824 | App Extensions, Plugins, `AppStoreTopShelfExtension` |
| `payload.023` | 16,141,400 | 16 | 133,664,320 | `.fseventsd`, system logs, miscellaneous data |
| `payload.024` | 3,677,076 | 4 | 30,425,963 | Localization `.strings` tables, plists |
| **TOTAL** | **1,899,524,868** | **518** | **4,210,309,961** | **Entire tvOS 13.4.8 Filesystem** |

### 1.4 Binary Record Header Structure in Decompressed Stream
Each entry in the decompressed stream is governed by an exact 30-byte header:
```
Offset  Size  Type       Field Name     Description
-----------------------------------------------------------------------
0x00    2     uint16_be  record_type    0x1001 = Regular File, 0x1002 = Directory
0x02    8     uint64_be  file_size      Payload data size in bytes
0x0A    8     uint64_be  mtime          POSIX epoch modification timestamp
0x12    4     uint32_be  flags          Apple metadata flags
0x16    2     uint16_be  name_len       Path string byte length
0x18    2     uint16_be  uid            POSIX user ID (e.g. 0 = root)
0x1A    2     uint16_be  gid            POSIX group ID (e.g. 0 = wheel, 80 = admin)
0x1C    2     uint16_be  mode           POSIX st_mode (0100644, 0100775, 040775)
-----------------------------------------------------------------------
Total Header Size: 30 bytes (struct unpack string: '>HQQIHHHH')
Followed by:
- name: string of name_len bytes (UTF-8 POSIX path)
- file_data: file_size bytes (if file_size > 0)
```
In `payload.000`, this parser successfully processed 26,180 records (7,951 regular files, 18,229 directories) consuming exactly 3,531,268 of 3,531,268 bytes (100.000% byte alignment with 0 remaining trailing bytes).

### 1.5 Host Disk Capacity Constraint
Running `df -h /home/prem/Projects/AppleTV` shows:
```
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p2  468G  440G  4.3G 100% /
```
Available disk space on the host is **4.3 GB**.
The compressed zip is 1.9 GB; the existing unzipped folder is 2.0 GB; total decompressed filesystem is 3.92 GB. Blind full decompression without directory consolidation would exhaust disk space.

---

## 2. Logic Chain

```
Observation (1.1, 1.2):
All 26 payload archives in AssetData/payloadv2/ begin with 'pbzx' followed by buffer length 0x800000 (8 MB).
    │
    ▼
Observation (1.3):
Scanning 518 chunks reveals that 501 chunks use XZ ('\xfd7zXZ') and 17 chunks are uncompressed (dlen == clen).
Zero chunks use LZFSE or bzip2.
    │
    ▼
Deduction (PBZX Decompressor Engine):
A custom streaming extractor written in pure Python using built-in `lzma` and `struct` can decompress and stream
100% of the payload files with ZERO external dependencies or host binary compilation.
    │
    ▼
Observation (1.4):
The decompressed stream consists of sequential 30-byte records ('>HQQIHHHH') providing path, permissions,
timestamps, and byte counts.
    │
    ▼
Verification (Tested on payload.018):
Extracted 'Applications/HeadBoard.app/Assets.car' (666,808 bytes, BOMStore), 'Setup.app/animation.caar' (1,758,928 bytes, bplist00),
and 'TVMusic.app/TVMusic' (1,524,400 bytes, MH_MAGIC_64 ARM64 executable) with exact byte counts and verified magic bytes.
    │
    ▼
Observation (1.2, Section 1.1):
- 'payload.001' decompresses to exactly 1,086,013,440 bytes of 'dyld_v1   arm64' shared cache.
- '038-50764-064.dmg.image-img4' is an unencrypted HFSX disk image with volume 'YagerG17M61.arm64SURamDisk'.
- 'kernelcache.release.j105a' is an unencrypted LZFSE-compressed Mach-O.
- All 38 system applications (PineBoard, HeadBoard, TVSettings, AppStore) and asset catalogs are in payloadv2.
- Only early bootloaders (LLB, iBoot, SEP, iBEC, iBSS) contain hardware GID KBAGs.
    │
    ▼
Deduction (Extractability Boundaries):
100% of userspace applications, UI frameworks, asset catalogs, the dyld shared cache, kernelcache, and ramdisk
are completely UNENCRYPTED and extractable. The encrypted IMG4 bootloaders only protect pre-kernel boot stages.
    │
    ▼
Observation (1.5):
Host available disk space is 4.3 GB, while the total uncompressed payload is 3.92 GB.
    │
    ▼
Deduction (Storage & Extraction Architecture):
The extraction pipeline must implement:
1. Directory layout separation separating raw, extracted, decoded, analysis, and reports.
2. Targeted / component-driven extraction capability to prioritize UI frameworks, PineBoard, HeadBoard, and dyld cache.
3. Directory consolidation (pointing `raw/` to existing unzipped payload files rather than duplicating 2 GB).
```

---

## 3. Caveats

1. **Storage Headroom (4.3 GB)**: Full uncompressed extraction of all 26 payload archives requires 3.92 GB. Performing a full extraction simultaneously alongside the 1.9 GB zip file and 2.0 GB unzipped staging directory without removing temporary files or streaming selectively will trigger an ENOSPC (Out of Disk Space) error. The extraction architecture must use selective unpacking or consolidate raw inputs.
2. **Hardcoded GID Bootloader Encryption**: `LLB.j105a.RELEASE.im4p`, `iBoot.j105a.RELEASE.im4p`, and `sep-firmware.j105a.RELEASE.im4p` cannot be decrypted statically because the AES-256 keys are fused inside Apple's A10X Fusion silicon. However, this does NOT affect userspace reverse engineering or UI reconstruction, as all application and framework binaries are in unencrypted userland.
3. **dyld Shared Cache Splitting**: Frameworks such as `UIKit`, `SwiftUI`, and `TVSystemUI` are housed inside `System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64`. REA can inspect Mach-O symbols directly within the cache, or individual dylibs can be extracted using dsc_extractor / ipsw tooling.
4. **Host Safety Compliance (R7)**: All extracted binaries are Mach-O ARM64 executables. Under no circumstances should `qemu-arm` or binary wrappers attempt to execute them on the x86_64 host.

---

## 4. Conclusion & Recommended Architecture

### 4.1 Extractability Matrix
| Component | Container Format | Encryption Status | Extraction Mechanism | Output Location |
| :--- | :--- | :--- | :--- | :--- |
| **All 38 Applications** | PBZX (`payload.000`–`024`) | **Unencrypted** | Pure Python streaming extractor | `extracted/rootfs/Applications/` |
| **PineBoard Shell** | PBZX (`payload.017`) | **Unencrypted** | Pure Python streaming extractor | `extracted/rootfs/Applications/PineBoard.app/` |
| **HeadBoard Home** | PBZX (`payload.020`, `018`) | **Unencrypted** | Pure Python streaming extractor | `extracted/rootfs/Applications/HeadBoard.app/` |
| **dyld Shared Cache** | PBZX (`payload.001`) | **Unencrypted** | Pure Python streaming extractor | `extracted/dyld_cache/dyld_shared_cache_arm64` |
| **Asset Catalogs (`.car`)**| PBZX (`payload.004`–`020`) | **Unencrypted** | Pure Python streaming extractor | `extracted/rootfs/.../Assets.car` |
| **Restore Ramdisk** | IM4P (`038-50764-064.dmg`) | **Unencrypted** | Strip 27-byte ASN.1 + `7z x` | `extracted/ramdisk/` |
| **Kernelcache** | IM4P (`kernelcache...`) | **Unencrypted** | Strip ASN.1 + LZFSE decompress | `extracted/kernel/kernelcache.macho` |
| **DeviceTree** | IM4P (`DeviceTree...`) | **Unencrypted** | Strip ASN.1 header | `extracted/firmware/DeviceTree.bin` |
| **Boot Graphics** | IM4P (`applelogo`, `recm`) | **Unencrypted** | Strip ASN.1 header | `extracted/firmware/boot_images/` |
| **Bootloaders (LLB/iBoot)**| IM4P with KBAG | **Hardware Encrypted** | Inaccessible (Hardware GID fuse) | Documented in Technical Limits |
| **SEP Firmware** | IM4P with KBAG | **Hardware Encrypted** | Inaccessible (Hardware GID fuse) | Documented in Technical Limits |

---

### 4.2 Preserved Directory Layout Separation
The workspace will strictly enforce the following 6-tier directory layout:

```
/home/prem/Projects/AppleTV/
├── raw/                                  # Tier 1: Immutable input assets & manifests
│   ├── archive/                          # Symlink or reference to 8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip
│   ├── checksums.sha256                  # SHA-256 ledger of all raw assets
│   ├── manifests/                        # Extracted plist & BOM metadata
│   │   ├── BuildManifest.plist
│   │   ├── Info.plist
│   │   ├── payload.bom
│   │   ├── pre.bom
│   │   └── post.bom
│   └── firmware/                         # Raw IM4P files and boot components
│       ├── kernelcache.release.j105a
│       ├── 038-50764-064.dmg.image-img4
│       └── all_flash/
├── extracted/                            # Tier 2: Unpacked filesystem partitions
│   ├── rootfs/                           # Reconstructed tvOS root filesystem
│   │   ├── Applications/                 # 38 System applications (PineBoard, HeadBoard, etc.)
│   │   ├── System/Library/               # Frameworks, PrivateFrameworks, CoreServices
│   │   ├── Library/                      # System support bundles
│   │   ├── usr/                          # System libraries and standalone updates
│   │   └── private/                      # Configuration files and data hierarchy
│   ├── dyld_cache/                       # dyld shared cache container
│   │   └── dyld_shared_cache_arm64       # 1.08 GB unified arm64 framework cache
│   ├── ramdisk/                          # Unpacked HFSX restore filesystem (launchd, asr)
│   └── kernel/                           # Decompressed Mach-O kernelcache and kexts
├── decoded/                              # Tier 3: Decoded assets, UI trees & text
│   ├── assets/                           # Extracted PNGs, SVGs, colors from .car catalogs
│   │   ├── PineBoard/
│   │   ├── HeadBoard/
│   │   └── CoreGlyphs/
│   ├── strings/                          # Normalized JSON/TXT localization string tables
│   ├── plists/                           # Normalized XML/JSON converted property lists
│   └── nibs/                             # Decoded interface builder files
├── analysis/                             # Tier 4: REA / Ghidra reverse-engineering data
│   ├── objc/                             # Extracted Objective-C headers & class structures
│   ├── swift/                            # Demangled Swift type hierarchies and protocols
│   ├── symbols/                          # Mach-O symbol tables, exports, and LC_LOAD_DYLIBs
│   ├── focus_engine/                     # UIFocusEngine interaction model & gesture bindings
│   └── ipc/                              # XPC interfaces, Mach service mappings, PineBoard protocols
├── graphify-out/                         # Tier 5: Graphify navigable knowledge graph
│   ├── graph.json                        # Queryable component-relationship knowledge graph
│   ├── index.html                        # Interactive graph navigator & visualizer
│   └── GRAPH_REPORT.md                   # Structural analysis report & god nodes
└── reports/                              # Tier 6: High-level technical reporting
    ├── TECHNICAL_REPORT.md               # Exhaustive reverse-engineering architectural report
    └── EXTRACTION_LEDGER.md              # File-by-file forensic inventory & checksum ledger
```

---

### 4.3 Python Streaming Extractor Specification
The verified extraction engine is implemented as a self-contained streaming extractor (`extract_pbzx.py`):

```python
import os, struct, lzma

def stream_pbzx(file_path):
    with open(file_path, 'rb') as fp:
        magic = fp.read(4)
        if magic != b'pbzx':
            raise ValueError(f"Invalid PBZX magic: {magic}")
        buf_size = struct.unpack('>Q', fp.read(8))[0]
        while True:
            chdr = fp.read(16)
            if len(chdr) < 16:
                break
            dlen, clen = struct.unpack('>QQ', chdr)
            cdata = fp.read(clen)
            if dlen == clen:
                yield cdata
            else:
                yield lzma.decompress(cdata)

class StreamBuffer:
    def __init__(self, gen):
        self.gen = gen
        self.buf = bytearray()
    
    def read(self, n):
        while len(self.buf) < n:
            try:
                self.buf.extend(next(self.gen))
            except StopIteration:
                break
        res = bytes(self.buf[:n])
        del self.buf[:n]
        return res

def extract_payload_archive(payload_path, output_dir, target_filter=None):
    sb = StreamBuffer(stream_pbzx(payload_path))
    while True:
        hdr = sb.read(30)
        if len(hdr) < 30:
            break
        rtype, fsize, mtime, flags, nlen, uid, gid, mode = struct.unpack('>HQQIHHHH', hdr)
        name = sb.read(nlen).decode('utf-8', errors='replace')
        
        target_path = os.path.join(output_dir, name)
        should_extract = target_filter is None or target_filter(name)
        
        if rtype == 0x1002: # Directory
            if should_extract:
                os.makedirs(target_path, exist_ok=True)
        elif rtype == 0x1001: # Regular file
            if should_extract:
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, 'wb') as out_f:
                    remaining = fsize
                    while remaining > 0:
                        block = sb.read(min(remaining, 65536))
                        if not block: break
                        out_f.write(block)
                        remaining -= len(block)
                os.chmod(target_path, mode & 0o777)
            else:
                # Discard file bytes efficiently without storing in memory
                remaining = fsize
                while remaining > 0:
                    block = sb.read(min(remaining, 65536))
                    if not block: break
                    remaining -= len(block)
```

---

## 5. Verification Method

### 5.1 Verification Commands
To independently verify all findings in this report, execute the following commands on the host:

1. **Verify Chunk Compression Types Across All 26 Payloads**:
   ```bash
   python3 -c "
   import glob, os, struct
   base = '/home/prem/Projects/AppleTV/8988ef3518b1f20f95c66d03be3c15eb4e1be2a0/AssetData/payloadv2'
   files = ['data_payload'] + [f'payload.{i:03d}' for i in range(25)]
   types = {}
   for f in files:
       with open(f'{base}/{f}', 'rb') as fp:
           fp.seek(12)
           while True:
               h = fp.read(16)
               if len(h) < 16: break
               d, c = struct.unpack('>QQ', h)
               m = fp.read(min(c, 6))
               t = 'raw' if d == c else ('xz' if m.startswith(b'\xfd7zXZ') else 'other')
               types[t] = types.get(t, 0) + 1
               fp.seek(c - len(m), 1)
   print('Chunk distribution:', types)
   "
   ```
   *Expected output*: `Chunk distribution: {'xz': 501, 'raw': 17}`.

2. **Verify Ramdisk HFSX Image Extraction**:
   ```bash
   python3 -c "
   with open('/home/prem/Projects/AppleTV/8988ef3518b1f20f95c66d03be3c15eb4e1be2a0/AssetData/boot/038-50764-064.dmg.image-img4', 'rb') as fp:
       fp.seek(27)
       data = fp.read(2048)
   print('Magic at 1024:', data[1024:1028])
   "
   ```
   *Expected output*: `Magic at 1024: b'HX\x00\x05'`.

3. **Verify dyld Shared Cache Magic in `payload.001`**:
   ```bash
   python3 -c "
   import struct, lzma
   with open('/home/prem/Projects/AppleTV/8988ef3518b1f20f95c66d03be3c15eb4e1be2a0/AssetData/payloadv2/payload.001', 'rb') as fp:
       fp.seek(12)
       d, c = struct.unpack('>QQ', fp.read(16))
       data = lzma.decompress(fp.read(c))
   hdr_len = 30 + struct.unpack('>H', data[22:24])[0]
   print('dyld magic:', data[hdr_len:hdr_len+16])
   "
   ```
   *Expected output*: `dyld magic: b'dyld_v1   arm64\x00'`.

4. **Verify PineBoard and HeadBoard Binary Locations**:
   - `payload.017` contains `Applications/PineBoard.app/PineBoard` (Mach-O ARM64).
   - `payload.020` contains `Applications/HeadBoard.app/HeadBoard` (Mach-O ARM64).
   - `payload.018` contains `Applications/HeadBoard.app/Assets.car` (Asset Catalog).

### 5.2 Invalidation Conditions
- Any occurrence of corrupted chunk decompression using standard `lzma`.
- Discovery of an unannounced encrypted APFS root container instead of unencrypted streaming PBZX.
- Host disk exhaustion resulting from non-consolidated duplicate full extraction.
