# Forensic Survey & Manifest Inspection Report: Apple TV HD (AppleTV5,3) Full Restore IPSW

**Date**: 2026-11-06  
**Investigator**: `explorer_survey_ipsw_1`  
**Target Archive**: `AppleTV5,3_26.6.1_23L781_Restore.ipsw`  
**Status**: Authoritative Archive Forensics Complete  

---

## 1. Executive Summary

A comprehensive, non-destructive forensic archive inspection was conducted on the official Apple TV full restore IPSW (`AppleTV5,3_26.6.1_23L781_Restore.ipsw`) located in `/home/prem/Projects/AppleTV/`. 

The archive provides the production restore software for the **Apple TV HD (4th Generation, Model A1625)**, powered by the Apple **A8** application processor (SoC **T7000 / S5L8960X**). The firmware release is tvOS version **26.6.1** under internal build **23L781** (BuildTrain: `CharismaG`, Restore Version: `23.12.781.0.0`).

All 26 contained files and 3 directory structures were inventoried, cryptographically hashed (SHA-256 and CRC-32), and categorized by container technology:
- **17 Image4 (IM4P) payloads**: Bootloaders (`illb`, `ibot`, `ibec`, `ibss`), kernelcache (`krnl`), device tree (`dtre`), SEP firmware (`sepi`), graphical assets (`logo`, `recm`), ramdisks (`rdsk`), trust caches (`rtsc`, `trst`), and system root hash/metadata (`isys`, `msys`).
- **2 Apple Encrypted Archive (AEA1) disk images**: The primary Customer APFS System Volume (`094-98312-089.dmg.aea`, 4.83 GB) and the Darwin Recovery APFS System Volume (`094-98220-089.dmg.aea`, 188.7 MB), both encrypted with session keys bound to Apple's Wireless Key Management Service (`https://wkms.sd.apple.com`).
- **2 Unencrypted Restore RamDisks**: `094-97800-089.dmg` (Erase Restore) and `094-97880-089.dmg` (Upgrade Restore), which contain complete APFS container filesystems (`NXSB`) inside standard IM4P containers.
- **5 Extracted Manifest Plists**: Extracted to `.agents/teamwork/explorer_survey_ipsw_1/manifests/` (`BuildManifest.plist`, `Restore.plist`, `RestoreVersion.plist`, `SystemVersion.plist`, and `sep-firmware.j42d.RELEASE.im4p.plist`).

---

## 2. Archive Forensic Identification & Integrity

| Attribute | Forensic Value |
|---|---|
| **Archive File Path** | `/home/prem/Projects/AppleTV/AppleTV5,3_26.6.1_23L781_Restore.ipsw` |
| **Exact Byte Size** | `5,269,474,064` bytes (5.269 GB / 4.907 GiB) |
| **Archive Format** | ZIP Archive (PKZIP 2.0 / Zip64) |
| **SHA-256 Checksum** | `08bb7001565746699636a00c73ae35c0cba7536a15bafc01c900de26048d77c1` |
| **Total Archive Entries** | 29 entries (26 files, 3 directory nodes) |
| **Internal Archive Timestamp** | `2007-01-09 09:41:00` (Apple standard static normalization timestamp) |

---

## 3. Comprehensive File Inventory & Cryptographic Manifest

Every file contained within `AppleTV5,3_26.6.1_23L781_Restore.ipsw` was analyzed for size, compression ratio, CRC-32, SHA-256 hash, and payload container type:

| Filename | Raw Size (Bytes) | Compressed Size | Zip Comp | CRC-32 | SHA-256 Checksum | Container / Tag |
|---|---|---|---|---|---|---|
| `094-97800-089.dmg` | 113,246,235 | 97,700,596 | Deflate | `0x7a482c70` | `09c6088cbb7f0c46a487f18ac76d390b6e1d197ce4ac304ee308ef66def27785` | IM4P (`rdsk`) / APFS |
| `094-97880-089.dmg` | 113,246,235 | 99,032,882 | Deflate | `0x93cdb0a4` | `7b0e46e0f45835e33829c75efb57fb1736fc549d8cdd297234efc8d03bd5876f` | IM4P (`rdsk`) / APFS |
| `094-98220-089.dmg.aea` | 188,743,680 | 188,743,680 | Store (0) | `0xb8a2cbe9` | `e15144fcc80fd7fbe1a05281cccde278aa8e1ebc34e85401f658e90e91962737` | AEA1 (Recovery RootFS) |
| `094-98312-089.dmg.aea` | 4,831,838,208 | 4,831,838,208 | Store (0) | `0x6281aa37` | `6374270cbdc8cbaff63d7ceef271fc7ebeed72564319ed5e83ae1996f926dda2` | AEA1 (Customer RootFS) |
| `BuildManifest.plist` | 147,266 | 6,863 | Deflate | `0x9cceb380` | `d5645c77e480a3393bd5a6b286f8de6864037ffa43450c541402807678023967` | XML Plist (Manifest) |
| `Firmware/` | 0 | 0 | Directory | `0x00000000` | N/A | Directory |
| `Firmware/094-97800-089.dmg.trustcache` | 6,427 | 6,232 | Deflate | `0x19b8cef8` | `626541cd0fcaa08a978d5cbb5776a7eddccfb372ed22d485602cf27e53a41f38` | IM4P (`rtsc`, TCv1 290) |
| `Firmware/094-97880-089.dmg.trustcache` | 6,515 | 6,317 | Deflate | `0xc6a47b1a` | `73cb66070ac6b38a3da7d9ecc305a67b882827830b30e968ba11333338071310` | IM4P (`rtsc`, TCv1 294) |
| `Firmware/094-98220-089.dmg.aea.mtree` | 1,375,743 | 1,365,156 | Deflate | `0x37bd947d` | `ba68e4ebfddb5586e89b01dfe92b64d1c605fb1235775796ed13c4313e20729c` | IM4P (`msys`, pbze) |
| `Firmware/094-98220-089.dmg.aea.root_hash` | 229 | 140 | Deflate | `0xadb4f4f2` | `3eaccfa5224b06e9b866d6460e73f8381ac9129fe020f07bd57914ebc8da079b` | IM4P (`isys`, DER) |
| `Firmware/094-98220-089.dmg.aea.trustcache` | 5,903 | 5,419 | Deflate | `0xfe681437` | `fcfe4bf5dd3cd04625ddd4996ea5f01dcb9f1abab5b6babf7f9104595ee6550e` | IM4P (`trst`, TCv2 244) |
| `Firmware/094-98312-089.dmg.aea.mtree` | 27,131,653 | 26,810,685 | Deflate | `0x033656b1` | `c1b4747ba66bc9a31e15746970ae8f1ef8820d438a1382c57ba91b988219eba4` | IM4P (`msys`, pbze) |
| `Firmware/094-98312-089.dmg.aea.root_hash` | 229 | 140 | Deflate | `0x5edc0898` | `15a3449fd3ebfdeca6368231388732443eacd3134745be855940165b119b9c5e` | IM4P (`isys`, DER) |
| `Firmware/094-98312-089.dmg.aea.trustcache` | 32,615 | 29,636 | Deflate | `0x8e97abd4` | `38be4644c7d1bb99e09fe9bfb91d66359ed1429b07fa67eb0f66092838909eda` | IM4P (`trst`, TCv2 1357) |
| `Firmware/all_flash/` | 0 | 0 | Directory | `0x00000000` | N/A | Directory |
| `Firmware/all_flash/DeviceTree.j42dap.im4p` | 17,246 | 17,256 | Deflate | `0x02d237af` | `185c59f2354dac06b158ace8ea34ebfe5db1a0c2535347be90ccfefb83e4e256` | IM4P (`dtre`, LZFSE) |
| `Firmware/all_flash/LLB.j42d.RELEASE.im4p` | 205,081 | 105,916 | Deflate | `0xbf545eb5` | `504ecd60b4bdbc1ce5bf59e113c0b7ceb017a73d3125b78301cc15570365ecca` | IM4P (`illb`, Mach-O) |
| `Firmware/all_flash/applelogo~appletv.im4p` | 4,767 | 4,389 | Deflate | `0x20844819` | `b92fccdc697347a79c8dd0039d39c0f889fe0360be7a0e0da390a50562b43cf6` | IM4P (`logo`, raw img) |
| `Firmware/all_flash/iBoot.j42d.RELEASE.im4p` | 846,105 | 431,560 | Deflate | `0xbb8411ec` | `faf7bb5fe3e6f89bda960d00ed8f5bf2a57ea1fe6009be3c7ab2a7e9c6b88501` | IM4P (`ibot`, Mach-O) |
| `Firmware/all_flash/recoverymode@1080~appletv5.im4p` | 44,629 | 18,431 | Deflate | `0x8e4d72e8` | `5159d16962e3cead4f706b04c59e9765f178f7f0f638f4cf45d11ff9e196ff9f` | IM4P (`recm`, raw img) |
| `Firmware/all_flash/sep-firmware.j42d.RELEASE.im4p` | 2,171,132 | 2,171,797 | Deflate | `0x1a4a7123` | `39e45e153fdaca8cec50d1fb060fc6b02ea4c5a63e01c41264f6cd240b3719d1` | IM4P (`sepi`, SEP OS) |
| `Firmware/all_flash/sep-firmware.j42d.RELEASE.im4p.plist` | 396 | 247 | Deflate | `0xf85c928b` | `4e69cf37e5eb118ea9de7e4eee691f2ac42e7fbd0f4f29fea8d42a8c184fd393` | XML Plist (SEP Hashes) |
| `Firmware/dfu/` | 0 | 0 | Directory | `0x00000000` | N/A | Directory |
| `Firmware/dfu/iBEC.j42d.RELEASE.im4p` | 846,105 | 431,560 | Deflate | `0xc2f66e53` | `0f487167354a4f2c67ef38733c761b769ad4923436aa3a2feb73da239441c7e3` | IM4P (`ibec`, Mach-O) |
| `Firmware/dfu/iBSS.j42d.RELEASE.im4p` | 205,081 | 105,916 | Deflate | `0xf961137c` | `ee58dcdf6a798dc7988ef5842a2854f7c106497ff8424e798904537ba2c6783a` | IM4P (`ibss`, Mach-O) |
| `Restore.plist` | 1,094 | 440 | Deflate | `0x2a3ef8c0` | `aac215c8d53c99b3ce5d19ba0e784d5affc8d2edfef1b0823c41e3e971ccd935` | XML Plist (Restore Map) |
| `RestoreVersion.plist` | 362 | 220 | Deflate | `0x26ae9fb2` | `ccd62276e37be7ca18be996941a9d1662f84a8d1fbb40e23bc84b9863d466707` | XML Plist (Version) |
| `SystemVersion.plist` | 493 | 277 | Deflate | `0x249a4ac9` | `5957766dab9e35b456f569e7dcd17cb3b21d9df4cb9855ae9fa135228d6f673d` | XML Plist (OS Build) |
| `kernelcache.release.j42d` | 21,964,283 | 20,635,083 | Deflate | `0x5da1d3f8` | `e3ff5323f95750449b01c9bba9817e2c23ca2070ea5e99af117269f7ba48e096` | IM4P (`krnl`, complzss) |

---

## 4. Hardware & Platform Identification

From `Restore.plist` and `BuildManifest.plist`, authoritative hardware identifiers were extracted:

| Hardware Attribute | Value | Description |
|---|---|---|
| **ProductType** | `AppleTV5,3` | Commercial Apple TV HD (4th Generation) |
| **Model Number** | `A1625` | 1080p Apple TV with USB-C service port |
| **DeviceClass** | `j42dap` | Hardware board design class |
| **Target / TargetType** | `J42dAP` / `j42d` | Restore target designation |
| **BoardConfig** | `j42dap` | Device tree / kernel board config string |
| **ApBoardID (BDID)** | `0x34` (52 decimal) | Application processor board identifier |
| **ApChipID (CPID)** | `0x7000` (28672 decimal) | Apple A8 processor (T7000 / S5L8960X architecture) |
| **Platform** | `t7000` | Apple Silicon T7000 SoC family |
| **ApSecurityDomain (SDOM)** | `0x01` (1 decimal) | Production Security Domain |
| **SCEP** | `0` | Security Component Execution Policy |
| **SupportedProductTypeIDs** | `{'DFU': [872443904], 'Recovery': [872443904]}` | Product type ID bitmask (`0x34000000` = BDID `0x34`) |
| **FDR Support** | `True` | Factory Data Recovery support enabled |
| **MobileDeviceMinVersion** | `1827.100.14` | Minimum iTunes / Apple Configurator MobileDevice runtime |

---

## 5. Operating System, Build, & Version Forensics

From `SystemVersion.plist`, `RestoreVersion.plist`, and `BuildManifest.plist`:

| Version Attribute | Value | Source File |
|---|---|---|
| **ProductName** | `Apple TVOS` | `SystemVersion.plist` |
| **ProductMarketingVersion** | `26.6.1` | `BuildManifest.plist` / `Restore.plist` |
| **ProductBuildVersion** | `23L781` | `SystemVersion.plist` / `BuildManifest.plist` |
| **BuildID** | `C4F2A172-C67F-11F1-B898-89BA0ADA7B5F` | `SystemVersion.plist` |
| **BuildTrain** | `CharismaG` | `BuildManifest.plist` (`Info.BuildTrain`) |
| **ProductCopyright** | `1983-2026 Apple Inc.` | `SystemVersion.plist` |
| **RestoreVersion** | `23.12.781.0.0` | `RestoreVersion.plist` |
| **RestoreLongVersion** | `23.12.781.0.0,0` | `RestoreVersion.plist` / `BuildManifest.plist` |
| **RestoreBuildGroup** | `0` | `RestoreVersion.plist` |
| **NeRDEpoch** | `0` | `BuildManifest.plist` |

---

## 6. Build Identities & Restore Variants Analysis

`BuildManifest.plist` defines three distinct `BuildIdentity` specifications:

### 6.1 BuildIdentity 0: Customer Erase Install (IPSW)
- **Variant**: `Customer Erase Install (IPSW)`
- **RestoreBehavior**: `Erase`
- **UniqueBuildID**: `aes88fab30d6ca67c80858e6a85121a97e003f15` (hex: `\xaes\x8f\xab0\xd6\xcag\xc8\x08X\xe6\xa8Q!\xa9~\x00?\x15`)
- **Primary RootFS (`OS`)**: `094-98312-089.dmg.aea` (4.83 GB APFS customer root image)
- **Restore RamDisk (`RestoreRamDisk`)**: `094-97800-089.dmg` (Erase Ramdisk, 113.2 MB)
- **Restore TrustCache**: `Firmware/094-97800-089.dmg.trustcache`
- **SystemVolume Hash (`SystemVolume`)**: `Firmware/094-98312-089.dmg.aea.root_hash`
- **Static TrustCache (`StaticTrustCache`)**: `Firmware/094-98312-089.dmg.aea.trustcache` (1,357 entries)
- **Metadata Tree (`Ap,SystemVolumeCanonicalMetadata`)**: `Firmware/094-98312-089.dmg.aea.mtree`

### 6.2 BuildIdentity 1: Customer Upgrade Install (IPSW)
- **Variant**: `Customer Upgrade Install (IPSW)`
- **RestoreBehavior**: `Update`
- **UniqueBuildID**: `c559608c4f8981b69db757ba7dbf32adc45539b3`
- **Primary RootFS (`OS`)**: `094-98312-089.dmg.aea` (4.83 GB APFS customer root image)
- **Restore RamDisk (`RestoreRamDisk`)**: `094-97880-089.dmg` (Upgrade Ramdisk, 113.2 MB)
- **Restore TrustCache**: `Firmware/094-97880-089.dmg.trustcache`
- **SystemVolume Hash & TrustCache**: Shares `094-98312-089.dmg.aea.root_hash` and `094-98312-089.dmg.aea.trustcache`

### 6.3 BuildIdentity 2: Recovery Customer Install
- **Variant**: `Recovery Customer Install`
- **RestoreBehavior**: `Erase`
- **Ap,OSReleaseType**: `Darwin Recovery`
- **AllowNeRDBoot**: `True`
- **UniqueBuildID**: `d92bc85654bbca9a5492b46169013cb30d9ea29d`
- **Primary RootFS (`OS`)**: `094-98220-089.dmg.aea` (188.7 MB APFS recovery image)
- **Restore RamDisk (`RestoreRamDisk`)**: `094-97800-089.dmg`
- **SystemVolume Hash (`SystemVolume`)**: `Firmware/094-98220-089.dmg.aea.root_hash`
- **Static TrustCache (`StaticTrustCache`)**: `Firmware/094-98220-089.dmg.aea.trustcache` (244 entries)
- **Metadata Tree (`Ap,SystemVolumeCanonicalMetadata`)**: `Firmware/094-98220-089.dmg.aea.mtree`

---

## 7. Partition Map & Storage Topology

The manifest explicitly specifies the APFS disk partitioning geometry required to provision the NAND flash:

### 7.1 System Partition Geometry
- **Target Filesystem**: `APFS` (Apple File System Container) for both customer and recovery images (`SystemRestoreImageFileSystems` in `Restore.plist`).
- **Customer System Partition Minimum (`MinimumSystemPartition`)**: `7,874 MB` (~7.69 GiB)
- **Customer OS Disk Image Size (`OSDiskImageSize`)**: `8,166 MB` (~7.97 GiB)
- **Customer OS Var Content Size (`OSVarContentSize`)**: `831,488` (sectors/KB -> ~812 MB)
- **Recovery System Partition Minimum (`MinimumSystemPartition`)**: `448 MB`
- **Recovery OS Disk Image Size (`OSDiskImageSize`)**: `178 MB`

### 7.2 System Partition Dynamic Padding Table
To accommodate wear-leveling and filesystem metadata scaling across varying NAND capacities, `BuildManifest.plist` provides the official padding rules (`SystemPartitionPadding` in MB):

| NAND Storage Tier | Capacity (GB) | System Partition Padding (MB) | Effective System Partition (MB) |
|---|---|---|---|
| **Tier 1** | 8 GB | 80 MB | 7,954 MB |
| **Tier 2** | 16 GB | 160 MB | 8,034 MB |
| **Tier 3 (Standard A1625 Base)** | 32 GB | 320 MB | 8,194 MB |
| **Tier 4 (Standard A1625 High)** | 64 GB | 640 MB | 8,514 MB |
| **Tier 5+ (Future / Extended)** | 128 GB - 1024 GB | 1,280 MB | 9,154 MB |

---

## 8. Firmware, Bootloader, & Cryptographic Component Analysis

### 8.1 Image4 Bootchain Components
All bootloader payloads are wrapped in standard Apple Image4 (`IM4P`) containers containing ASN.1 DER structures:
- `LLB.j42d.RELEASE.im4p` (Tag: `illb`): Low-Level Bootloader (`iBoot-13822.120.5~2081`)
- `iBoot.j42d.RELEASE.im4p` (Tag: `ibot`): Stage 2 bootloader (`iBoot-13822.120.5~2081`)
- `iBSS.j42d.RELEASE.im4p` (Tag: `ibss`): DFU Stage 1 bootloader (`iBoot-13822.120.5~2081`)
- `iBEC.j42d.RELEASE.im4p` (Tag: `ibec`): DFU Stage 2 bootloader (`iBoot-13822.120.5~2081`)
- `DeviceTree.j42dap.im4p` (Tag: `dtre`): Apple Device Tree (`EmbeddedDeviceTrees-11156.160.23`), compressed with LZFSE (`bvx2`).
- `kernelcache.release.j42d` (Tag: `krnl`): Pre-linked ARM64 kernelcache (`KernelCacheBuilder_release-3244.160.2`), compressed with `complzss`.
- `sep-firmware.j42d.RELEASE.im4p` (Tag: `sepi`): Secure Enclave Processor OS image for Apple A8 SEP.
- `applelogo~appletv.im4p` (Tag: `logo`): Boot logo (`EmbeddedImages-170.0.1`).
- `recoverymode@1080~appletv5.im4p` (Tag: `recm`): 1080p recovery mode display screen (`EmbeddedImages-170.0.1`).

### 8.2 Restore RamDisks
- `094-97800-089.dmg` & `094-97880-089.dmg`:
  - Wrapped in Image4 payload containers (Tag: `rdsk`).
  - At ASN.1 offset `0x1B` (byte 27), each payload starts with unencrypted Apple APFS container superblock header (`NXSB` at byte 59).
  - Both ramdisks are unencrypted APFS disk images and can be unpacked without decryption keys.

### 8.3 Trust Caches & CDHash Audits
- **RamDisk TrustCaches (v1)**:
  - `094-97800-089.dmg.trustcache`: Version 1, UUID `be1d901adb66485e9749db5178d8c400`, contains **290 CDHashes**.
  - `094-97880-089.dmg.trustcache`: Version 1, UUID `b26ad94c51e34da5b3b81ff70066bc12`, contains **294 CDHashes**.
- **System Volume Static TrustCaches (v2)**:
  - `094-98220-089.dmg.aea.trustcache`: Version 2, UUID `160e1cb36ac84300bb3dc7aa423b1d72`, contains **244 CDHashes** (Recovery OS binaries).
  - `094-98312-089.dmg.aea.trustcache`: Version 2, UUID `63d78e19d1a14dc68d44d9023319e47d`, contains **1,357 CDHashes** (Production Customer OS binaries).

### 8.4 Apple Encrypted Archive (AEA1) Containers
The two system volume images are encoded using Apple's modern `.aea` format:
- Magic: `AEA1` (`0x4145413101000000`)
- Profile/Version: 1
- Key Escrow Binding: `com.apple.wkms.url` -> `https://wkms.sd.apple.com`
- Payload structure: Encrypted APFS filesystem image.
- Decryption requirement: Online ticket or pre-shared key unwrapped via Apple's TSS / WKMS restore service.

---

## 9. Verification & Artifact Record

The extracted manifest plists have been non-destructively preserved in:
- `/home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_ipsw_1/manifests/BuildManifest.plist`
- `/home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_ipsw_1/manifests/Restore.plist`
- `/home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_ipsw_1/manifests/RestoreVersion.plist`
- `/home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_ipsw_1/manifests/SystemVersion.plist`
- `/home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_ipsw_1/manifests/sep-firmware.j42d.RELEASE.im4p.plist`

All commands and cryptographic checks documented in this report are independently reproducible against `/home/prem/Projects/AppleTV/AppleTV5,3_26.6.1_23L781_Restore.ipsw`.
