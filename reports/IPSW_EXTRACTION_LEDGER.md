# Apple TV (tvOS 26.6.1 / Build 23L781) Forensic IPSW Extraction Ledger

**Milestone**: IPSW-M1 (Firmware Forensics & Filesystem Unpacking)  
**Target IPSW**: `AppleTV5,3_26.6.1_23L781_Restore.ipsw`  
**Target Hardware**: Apple TV HD (4th Generation, Model A1625, BoardConfig `j42dap`, ProductType `AppleTV5,3`)  
**SoC Architecture**: Apple A8 SoC (T7000, `ApChipID = 0x7000`, `ApBoardID = 0x34`, ARM64 v8-A)  
**Execution Safety (R7)**: Strictly Static Analysis — 0 Target Host Executions  
**Date**: 2026-11-06T21:30:00Z  

---

## 1. Executive Forensic Summary

| Parameter | Forensic Value | Verification Method |
| :--- | :--- | :--- |
| **Archive File** | `AppleTV5,3_26.6.1_23L781_Restore.ipsw` | Host Filesystem Inspection |
| **Archive Size** | `5,269,474,064` bytes (~4.907 GiB, 5.27 GB) | `stat -c %s` |
| **SHA-256 Digest** | `08bb7001565746699636a00c73ae35c0cba7536a15bafc01c900de26048d77c1` | `sha256sum` |
| **Package Format** | Apple Full Restore IPSW (ZIP container format) | PKZIP 2.0 Directory Structure |
| **Total Archive Entries** | 29 entries (26 files, 3 directory nodes) | `zipfile` inventory |
| **Product Name** | `Apple TVOS` | `SystemVersion.plist` |
| **Product Version** | `26.6.1` (Marketed Release) | `SystemVersion.plist` / `Restore.plist` |
| **Product Build Version**| `23L781` | `SystemVersion.plist` / `Restore.plist` |
| **Build Train** | `CharismaG` | `BuildManifest.plist` |
| **Restore Version** | `23.12.781.0.0` (Long: `23.12.781.0.0,0`, Group: `0`) | `RestoreVersion.plist` |
| **Build ID** | `C4F2A172-C67F-11F1-B898-89BA0ADA7B5F` | `SystemVersion.plist` |
| **Hardware Platform** | Apple TV HD (Model A1625 / `AppleTV5,3` / `j42dap`) | `Restore.plist` DeviceMap |
| **SoC / Chip ID** | Apple T7000 (`CPID = 28672` / `0x7000`, Apple A8) | `Restore.plist` |
| **Board ID** | `BDID = 52` (`0x34`), Security Domain = `1`, SCEP = `0` | `Restore.plist` |
| **Supported Product IDs**| DFU: `872443904`, Recovery: `872443904` | `Restore.plist` |
| **System Partitions** | Customer OS Disk: `8166` MB, Recovery OS Disk: `178` MB | `BuildManifest.plist` |

---

## 2. Technical Cryptographic & Security Boundaries

The restore IPSW implements a layered security model spanning encrypted disk images, hardware-fused silicon keybags, compressed kernel containers, and unencrypted APFS restore ramdisks:

```
+---------------------------------------------------------------------------------------------------+
|                           AppleTV5,3_26.6.1_23L781_Restore.ipsw                                   |
+---------------------------------------------------------------------------------------------------+
       |                                      |                                    |
       v                                      v                                    v
+-----------------------------+ +-----------------------------+ +-----------------------------------+
|  RootFS & Recovery Volumes  | | Secure Enclave Processor    | | Unencrypted Partitions & Firmware |
|  (.aea Containers)          | | (sep-firmware IM4P)         | | (Ramdisk, Kernel, Bootloaders)    |
+-----------------------------+ +-----------------------------+ +-----------------------------------+
| - 094-98312-089.dmg.aea     | | - sep-firmware.j42d...im4p  | | - 094-97800-089.dmg (Erase rdsk)  |
| - 094-98220-089.dmg.aea     | | - Hardware GID AES-256-CBC  | | - 094-97880-089.dmg (Update rdsk) |
| - Apple Encrypted Archive 1 | | - Production & Dev Keybags  | | - kernelcache.release.j42d (krnl) |
| - Symmetric Profile 1       | | - Silicon fused A8 keys     | | - LLB.j42d, iBoot.j42d (illb/ibot)|
| - RFC 9180 HPKE Management  | | - Decryption impossible     | | - DeviceTree.j42dap.im4p (dtre)   |
| - Apple WKMS Escrow         | |   without physical chip     | | - applelogo, recoverymode (iBootIm|
+-----------------------------+ +-----------------------------+ +-----------------------------------+
```

### 2.1 Apple Encrypted Archive (AEA1) Containers
- **Target Images**:
  - `094-98312-089.dmg.aea` (4,831,838,208 bytes): Customer OS RootFS APFS disk image.
  - `094-98220-089.dmg.aea` (188,743,680 bytes): Recovery OS APFS disk image.
- **Container Structure**:
  - Magic: `41 45 41 31 01 00 00 00` (`AEA1`, Version 1, Profile 1: `SymmetricEncryption`).
  - Auth data size: 2,168 bytes (RootFS) / 2,200 bytes (Recovery).
  - Key escrow URLs: `https://wkms.sd.apple.com` and `https://wkms-public.apple.com/fcs-keys/EqKp4rUE1uMIIEqnfHnqfscN_VFy_qgyE3Vus8_KQhE=`.
- **Key Resolution Mechanism**:
  - Key encapsulation uses RFC 9180 HPKE Base Mode (`DHKEM(P-256, HKDF-SHA256)` + `HKDF-SHA256` + `AES-256-GCM`).
  - The published public FCS NIST P-256 key allows decapsulating the wrapped symmetric key into the 256-bit AES archive key:
    - RootFS Symmetric Key: `ca0d1a3eb45cdb15b15babced612a5d37914299f5d5d141d488ddccb40cda496`
    - Recovery Symmetric Key: `efd41ef06e0adc9426ae40d7c6635dbca5c88f68029411bf465a34c7c9baf7d9`
  - Validated via `HMAC match?: True` on decrypted root headers.
  - RootFS uncompressed disk dimensions: `8,562,671,616` bytes (7.97 GiB), matching `OSDiskImageSize: 8166` in `BuildManifest.plist`.

### 2.2 Canonical RootFS File Manifest (`.mtree`)
- **File**: `Firmware/094-98312-089.dmg.aea.mtree` (27,131,653 bytes)
- **Container**: IM4P envelope tag `msys`, containing a `pbze` stream (Apple pbzx stream with 4 MB chunks compressed with LZFSE).
- **Architectural Value**: Contains the unencrypted **AppleArchive (`AA01`)** catalog of every file, directory, symlink, permission, UID/GID, timestamp, and SHA-256 checksum across the entire 8.56 GB tvOS 26.6.1 root filesystem.

### 2.3 Secure Enclave Processor (`sep-firmware`)
- **File**: `Firmware/all_flash/sep-firmware.j42d.RELEASE.im4p` (2,171,132 bytes)
- **Tag**: `sepi`, containing embedded hardware keybags:
  - Keybag 0 (Production): IV `054e049860f25383052332515937e6dd`, Key `05ae50652f30ad18ad7c263a22a5229271e213ca60037b5b553fefc7aaa84afd`
  - Keybag 1 (Development): IV `fff43d5112fed56c973ac8b5bf8842a2`, Key `cba38de8c4dcb1eee31395ca71c6a8441674895a7de86a1b8aad860c96ca21b7`
- **Security Boundary**: Hardware AES-256-CBC wrapped under Apple's A8 Secure Enclave GID root key. Offline decryption is cryptographically impossible without silicon extraction.

### 2.4 Unencrypted APFS Restore Ramdisks
- **Files**:
  - `094-97800-089.dmg` (113,246,235 bytes): Assigned to `Customer Erase Install (IPSW)` and `Recovery Customer Install`.
  - `094-97880-089.dmg` (113,246,235 bytes): Assigned to `Customer Upgrade Install (IPSW)`.
- **Format**:
  - 27-byte ASN.1 Image4 (`rdsk`) wrapper.
  - Offset 27 onward: 108 MiB (113,246,208 bytes) uncompressed APFS container.
  - Byte 59: Superblock magic `NXSB`, block size 4096, 27,648 blocks, unencrypted (`features = 0x0`).
- **Extractability**: 100% extractable directly via 7-Zip (`7z x`), yielding complete restore system environments.

### 2.5 Unencrypted Kernelcache
- **File**: `kernelcache.release.j42d` (21,964,283 bytes)
- **Tag**: `krnl`, builder `KernelCacheBuilder_release-3244.160.2`
- **Compression**: `complzss` header at offset 63, Apple LZSS stream starting at offset 447.
- **Verification**: Decompressed payload is exactly 44,122,112 bytes, Adler-32 checksum `0xdfddbd11` (exact 100% match), Mach-O 64-bit ARM64 magic `0xfeedfacf`.

### 2.6 Unencrypted Bootloaders & DeviceTree
- `LLB.j42d.RELEASE.im4p` (205,040 bytes payload) & `iBoot.j42d.RELEASE.im4p` (846,064 bytes payload): Unencrypted raw ARM64 machine code (`iBoot-13822.120.5`).
- `iBSS.j42d.RELEASE.im4p` & `iBEC.j42d.RELEASE.im4p`: Byte-for-byte identical to LLB and iBoot respectively.
- `DeviceTree.j42dap.im4p`: LZFSE compressed (`bvx2`), uncompressed size 105,596 bytes, plaintext Apple DeviceTree hierarchy for `j42dap`.

### 2.7 UI Restore Graphics
- `applelogo~appletv.im4p` (108×131, 16-bit `grey` / `LA` mode) and `recoverymode@1080~appletv5.im4p` (582×154, 32-bit `bgra` / `RGBA` mode): Wrapped in `iBootIm` containers, LZSS compressed, converted directly to standard PNG.

---

## 3. Master Forensic Inventory of All Archive Files

All 26 files inside `AppleTV5,3_26.6.1_23L781_Restore.ipsw` cataloged with cryptographic digests and component classifications:

| File Path in Archive | Size (Bytes) | Format / Container | Encryption Status | SHA-256 Digest |
| :--- | :--- | :--- | :--- | :--- |
| `094-97800-089.dmg` | 113,246,235 | IM4P (`rdsk`) -> APFS | Plaintext | `09c6088cbb7f0c46a487f18ac76d390b6e1d197ce4ac304ee308ef66def27785` |
| `094-97880-089.dmg` | 113,246,235 | IM4P (`rdsk`) -> APFS | Plaintext | `7b0e46e0f45835e33829c75efb57fb1736fc549d8cdd297234efc8d03bd5876f` |
| `094-98220-089.dmg.aea` | 188,743,680 | Apple Encrypted Archive (AEA1) | AEA1 Profile 1 | `e15144fcc80fd7fbe1a05281cccde278aa8e1ebc34e85401f658e90e91962737` |
| `094-98312-089.dmg.aea` | 4,831,838,208 | Apple Encrypted Archive (AEA1) | AEA1 Profile 1 | `6374270cbdc8cbaff63d7ceef271fc7ebeed72564319ed5e83ae1996f926dda2` |
| `BuildManifest.plist` | 147,266 | XML Property List | Plaintext | `d5645c77e480a3393bd5a6b286f8de6864037ffa43450c541402807678023967` |
| `Restore.plist` | 1,094 | XML Property List | Plaintext | `aac215c8d53c99b3ce5d19ba0e784d5affc8d2edfef1b0823c41e3e971ccd935` |
| `RestoreVersion.plist` | 362 | XML Property List | Plaintext | `ccd62276e37be7ca18be996941a9d1662f84a8d1fbb40e23bc84b9863d466707` |
| `SystemVersion.plist` | 493 | XML Property List | Plaintext | `5957766dab9e35b456f569e7dcd17cb3b21d9df4cb9855ae9fa135228d6f673d` |
| `kernelcache.release.j42d` | 21,964,283 | IM4P (`krnl`) -> complzss | Plaintext | `e3ff5323f95750449b01c9bba9817e2c23ca2070ea5e99af117269f7ba48e096` |
| `Firmware/094-97800-089.dmg.trustcache` | 6,427 | IM4P (`rtsc`) -> TrustCache v1 | Plaintext | `626541cd0fcaa08a978d5cbb5776a7eddccfb372ed22d485602cf27e53a41f38` |
| `Firmware/094-97880-089.dmg.trustcache` | 6,515 | IM4P (`rtsc`) -> TrustCache v1 | Plaintext | `73cb66070ac6b38a3da7d9ecc305a67b882827830b30e968ba11333338071310` |
| `Firmware/094-98220-089.dmg.aea.mtree` | 1,375,743 | IM4P (`msys`) -> pbze (AA01) | Plaintext | `ba68e4ebfddb5586e89b01dfe92b64d1c605fb1235775796ed13c4313e20729c` |
| `Firmware/094-98220-089.dmg.aea.root_hash` | 229 | IM4P (`isys`) -> Root Hash | Plaintext | `3eaccfa5224b06e9b866d6460e73f8381ac9129fe020f07bd57914ebc8da079b` |
| `Firmware/094-98220-089.dmg.aea.trustcache` | 5,903 | IM4P (`trst`) -> TrustCache v2 | Plaintext | `fcfe4bf5dd3cd04625ddd4996ea5f01dcb9f1abab5b6babf7f9104595ee6550e` |
| `Firmware/094-98312-089.dmg.aea.mtree` | 27,131,653 | IM4P (`msys`) -> pbze (AA01) | Plaintext | `c1b4747ba66bc9a31e15746970ae8f1ef8820d438a1382c57ba91b988219eba4` |
| `Firmware/094-98312-089.dmg.aea.root_hash` | 229 | IM4P (`isys`) -> Root Hash | Plaintext | `15a3449fd3ebfdeca6368231388732443eacd3134745be855940165b119b9c5e` |
| `Firmware/094-98312-089.dmg.aea.trustcache` | 32,615 | IM4P (`trst`) -> TrustCache v2 | Plaintext | `38be4644c7d1bb99e09fe9bfb91d66359ed1429b07fa67eb0f66092838909eda` |
| `Firmware/dfu/iBEC.j42d.RELEASE.im4p` | 846,105 | IM4P (`ibec`) -> ARM64 Bin | Plaintext | `0f487167354a4f2c67ef38733c761b769ad4923436aa3a2feb73da239441c7e3` |
| `Firmware/dfu/iBSS.j42d.RELEASE.im4p` | 205,081 | IM4P (`ibss`) -> ARM64 Bin | Plaintext | `ee58dcdf6a798dc7988ef5842a2854f7c106497ff8424e798904537ba2c6783a` |
| `Firmware/all_flash/DeviceTree.j42dap.im4p` | 17,246 | IM4P (`dtre`) -> LZFSE | Plaintext | `185c59f2354dac06b158ace8ea34ebfe5db1a0c2535347be90ccfefb83e4e256` |
| `Firmware/all_flash/LLB.j42d.RELEASE.im4p` | 205,081 | IM4P (`illb`) -> ARM64 Bin | Plaintext | `504ecd60b4bdbc1ce5bf59e113c0b7ceb017a73d3125b78301cc15570365ecca` |
| `Firmware/all_flash/applelogo~appletv.im4p` | 4,767 | IM4P (`logo`) -> iBootIm | Plaintext | `b92fccdc697347a79c8dd0039d39c0f889fe0360be7a0e0da390a50562b43cf6` |
| `Firmware/all_flash/iBoot.j42d.RELEASE.im4p` | 846,105 | IM4P (`ibot`) -> ARM64 Bin | Plaintext | `faf7bb5fe3e6f89bda960d00ed8f5bf2a57ea1fe6009be3c7ab2a7e9c6b88501` |
| `Firmware/all_flash/recoverymode@1080~appletv5.im4p` | 44,629 | IM4P (`recm`) -> iBootIm | Plaintext | `5159d16962e3cead4f706b04c59e9765f178f7f0f638f4cf45d11ff9e196ff9f` |
| `Firmware/all_flash/sep-firmware.j42d.RELEASE.im4p` | 2,171,132 | IM4P (`sepi`) | **Encrypted** (2 KBAGs) | `39e45e153fdaca8cec50d1fb060fc6b02ea4c5a63e01c41264f6cd240b3719d1` |
| `Firmware/all_flash/sep-firmware.j42d.RELEASE.im4p.plist` | 396 | XML Property List | Plaintext | `4e69cf37e5eb118ea9de7e4eee691f2ac42e7fbd0f4f29fea8d42a8c184fd393` |

---

## 4. Extracted Kernel & Firmware Components (`extracted/ipsw/`)

| Extracted File Path | Size (Bytes) | Format Description | Verification Criteria | SHA-256 Digest |
| :--- | :--- | :--- | :--- | :--- |
| `extracted/ipsw/kernel/kernelcache.macho` | 44,122,112 | Mach-O 64-bit ARM64 Executable | Adler-32: `0xdfddbd11`, Magic: `0xfeedfacf` | `6d01ca4f6285fa9a8b7683d085040cee9b101402b13d8fdf31317cfcefce433f` |
| `extracted/ipsw/firmware/DeviceTree.bin` | 105,596 | Apple DeviceTree Binary | LZFSE uncompressed size exact match | `1b0de77f54fc18e4b4f6fc380d68f55243b39a9a4df156df775cd6c2922a5905` |
| `extracted/ipsw/firmware/LLB.bin` | 205,040 | Raw ARM64 Machine Code | iBoot-13822.120.5 bootloader | `4bbe057ad7b61aaa40beea6c4053e6bc98e7539a8ca9803f50c052206327e9fd` |
| `extracted/ipsw/firmware/iBoot.bin` | 846,064 | Raw ARM64 Machine Code | iBoot-13822.120.5 second stage | `7325829887eeb16a2fcaeb2246da0002f505abd0638190b1bc5de98e2b8e6480` |
| `extracted/ipsw/firmware/iBSS.bin` | 205,040 | Raw ARM64 Machine Code | Identical to LLB.bin | `4bbe057ad7b61aaa40beea6c4053e6bc98e7539a8ca9803f50c052206327e9fd` |
| `extracted/ipsw/firmware/iBEC.bin` | 846,064 | Raw ARM64 Machine Code | Identical to iBoot.bin | `7325829887eeb16a2fcaeb2246da0002f505abd0638190b1bc5de98e2b8e6480` |
| `extracted/ipsw/firmware/applelogo.png` | 2,514 | PNG (108×131, Luminance+Alpha) | Decompressed from iBootIm LA | `db01b67c87a9a0dffabaece1da46899f8efbcd5687ad6cd4659093773591d6ff` |
| `extracted/ipsw/firmware/recoverymode.png` | 7,309 | PNG (582×154, RGBA) | Decompressed from iBootIm BGRA | `a3c5637121b28e6a90aca169f4ba7fa015d8f110c5be8faab18b4acad8d047fe` |

---

## 5. Extracted Restore Ramdisk Filesystem Inventory

### 5.1 Ramdisk Metrics Summary

| Metric | `extracted/ipsw/ramdisk_erase/` | `extracted/ipsw/ramdisk_update/` |
| :--- | :--- | :--- |
| **Origin Partition** | `094-97800-089.dmg` | `094-97880-089.dmg` |
| **Filesystem Type** | Plaintext APFS Container (`NXSB`) | Plaintext APFS Container (`NXSB`) |
| **Volume Name / UUID** | `ramdisk` / `6efbcfd4-1c00-42f4-8074-74c7a5863ebf` | `ramdisk` / `dc6056c1-6f32-47e0-bc33-5afedc9fbfab` |
| **Block Size / Total Blocks** | 4,096 bytes / 27,648 blocks (108 MiB) | 4,096 bytes / 27,648 blocks (108 MiB) |
| **Total Regular Files** | 750 files | 900 files |
| **Total Directory Nodes** | 314 subdirectories (315 total) | 364 subdirectories (365 total) |
| **Total Symbolic Links** | 100 symlinks | 100 symlinks |
| **Unpacked Byte Footprint**| 268,824,552 bytes (~268.8 MB) | 272,349,852 bytes (~272.3 MB) |
| **Primary Restore Daemon** | `usr/local/bin/restored_external` | `usr/local/bin/restored_update` |
| **LaunchDaemon Config** | `System/Library/LaunchDaemons/com.apple.restored_external.plist` | `System/Library/LaunchDaemons/com.apple.restored_update.plist` |

### 5.2 Key Binaries & System Daemons Recovered

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

### 5.3 Recovered UI Graphics & Multi-Resolution Assets

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

---

## 6. Comparison: tvOS 13.4.8 (OTA) vs tvOS 26.6.1 (Full Restore IPSW)

| Architecture Dimension | tvOS 13.4.8 (`17M61` OTA Baseline) | tvOS 26.6.1 (`23L781` Full Restore IPSW) |
| :--- | :--- | :--- |
| **Archive Delivery Format** | Apple MobileAsset SoftwareUpdate (OTA Zip) | Apple Full Restore IPSW |
| **Archive File Size** | 2,014,940,073 bytes (~1.88 GiB) | 5,269,474,064 bytes (~4.91 GiB) |
| **Target Device & SoC** | Apple TV 4K 1st Gen (A1842 / A10X / `j105aap`) | Apple TV HD (A1625 / A8 / `j42dap`) |
| **Root Filesystem Packaging** | Multi-chunk PBZX payload (`payload.000`..`024`) | Apple Encrypted Archive (`094-98312-089.dmg.aea`) |
| **Root Filesystem Encryption** | Plaintext / Unencrypted | AEA1 Profile 1 (AES-256-GCM + RFC 9180 HPKE) |
| **RootFS Geometry** | ~3.8 GB flat filesystem | 8.56 GB Sealed System Volume (SSV) |
| **Restore Ramdisk Format** | HFSX (`HX\x00\x05` / `arm64SURamDisk.dmg`) | Plaintext APFS Container (`NXSB` / 108 MiB) |
| **Ramdisk Multiplicity** | Single unified recovery ramdisk | Dual ramdisks: Erase (`094-97800`) & Update (`094-97880`) |
| **Kernelcache Size** | 31,363,656 bytes decompressed (LZFSE `bvx2`) | 44,122,112 bytes decompressed (Apple LZSS) |
| **User-Space Drivers** | Traditional I/O Kit kernel extensions | Apple DriverKit userspace runtime (`driverkitd`) |
| **Disk Image Engine** | Legacy `hdik` / `diskimagesd` | Modern `DiskImages2` (`diskimagesiod`) |
| **Swift Adoption** | Swift 4/5 runtime embedded in user apps | Unified Swift system dylibs (`DriverKit/usr/lib/swift/`) |

---

## 7. Independent Forensic Verification Protocol

To independently verify all claims, checksums, and extracted structures in this ledger, execute the following commands from the project root:

```bash
# 1. Verify IPSW Checksum and File Size
sha256sum -c raw/ipsw/checksums.sha256
stat -c %s AppleTV5,3_26.6.1_23L781_Restore.ipsw # Output must be: 5269474064

# 2. Verify Manifest Plist Integrities
python3 -c "
import plistlib
p = plistlib.load(open('raw/ipsw/manifests/SystemVersion.plist', 'rb'))
assert p['ProductBuildVersion'] == '23L781'
assert p['ProductVersion'] == '26.6.1'
assert p['ProductName'] == 'Apple TVOS'
print('Manifests Verified!')
"

# 3. Verify Extracted Kernelcache Mach-O
python3 -c "
import zlib
data = open('extracted/ipsw/kernel/kernelcache.macho', 'rb').read()
assert len(data) == 44122112, 'Size mismatch'
assert zlib.adler32(data) == 0xdfddbd11, 'Adler-32 mismatch'
assert data[:4] == b'\xcf\xfa\xed\xfe', 'Mach-O magic mismatch'
print('Kernelcache Mach-O Verified!')
"

# 4. Verify Firmware Components
python3 -c "
import os
assert os.path.getsize('extracted/ipsw/firmware/DeviceTree.bin') == 105596
assert os.path.getsize('extracted/ipsw/firmware/LLB.bin') == 205040
assert os.path.getsize('extracted/ipsw/firmware/iBoot.bin') == 846064
assert os.path.exists('extracted/ipsw/firmware/applelogo.png')
assert os.path.exists('extracted/ipsw/firmware/recoverymode.png')
print('Firmware Components Verified!')
"

# 5. Verify Restore Daemons in Ramdisks
file extracted/ipsw/ramdisk_erase/usr/local/bin/restored_external
file extracted/ipsw/ramdisk_update/usr/local/bin/restored_update
# Expected output: Mach-O 64-bit arm64 executable
```
