# Apple tvOS Forensic Extraction Ledger

**Milestone**: M1 (Archive Forensics, Filesystem Extraction & Hierarchy Preservation)  
**Date**: 2026-11-06T17:50:00Z  
**Target**: tvOS 13.4.8 (Build 17M61, AppleTV6,2 / j105aap / Apple TV 4K 1st Gen)  
**Execution Safety (R7)**: Strictly Static Analysis — 0 Target Host Executions  

---

## 1. Executive Forensic Summary

| Parameter | Forensic Value |
| :--- | :--- |
| **Archive File** | `8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip` |
| **Archive Size** | `2,014,940,073` bytes (~1.876 GiB, 2.01 GB) |
| **SHA-256** | `8725797b4ddfd93fc67023c93c1d9277f128e9731a9ac18618b9b2e812c027c1` |
| **SHA-1** | `6802f6170a3c713d7111e98b0a81a5afb33ed9b8` |
| **MD5** | `c29d3b384511eed5a4a0a309f907b4f9` |
| **Package Format** | Apple MobileAsset SoftwareUpdate Package (Version 3.0) |
| **Target OS Version** | `13.4.8` |
| **Target Build** | `17M61` (Train: `YagerG`) |
| **Target Device** | Apple TV 4K (1st Generation, Model A1842) |
| **Device Identifier** | `AppleTV6,2` / `j105aap` |
| **Target SoC** | Apple A10X Fusion (T8011, `ApChipID = 0x8011`, `ApBoardID = 0x02`) |
| **Filesystem Encryption** | **0% Encrypted** (Userspace rootfs, applications, dyld cache, ramdisk, kernelcache are plaintext) |
| **Hardware GID Encryption** | Early bootloaders only (`LLB`, `iBoot`, `SEP`, `iBEC`, `iBSS` contain silicon GID KBAGs) |
| **Extraction Pipeline** | Pure Python streaming PBZX decompressor (`scripts/extract_payload.py`) |

---

## 2. Technical Analysis: Security & Encryption Boundaries

### 2.1 The Two-Tier Firmware Boundary: Secure Boot vs. Userspace
Apple MobileAsset SoftwareUpdate packages enforce a strict cryptographic partition between early pre-kernel boot stages and operating system userspace:

1. **Hardware-Locked Pre-Kernel Stage (Encrypted via Silicon GID Keys)**:
   - **Components**: `LLB.j105a.RELEASE.im4p`, `iBoot.j105a.RELEASE.im4p`, `sep-firmware.j105a.RELEASE.im4p`, `iBSS.j105a.RELEASE.im4p`, `iBEC.j105a.RELEASE.im4p`.
   - **Container Structure**: Encapsulated in ASN.1 DER Image4 (`IM4P`) containers containing 5 sequence elements.
   - **Keybag Sequence**: Element 4 is a `KBAG` (Keybag) sequence containing AES-256 initialization vectors and ciphertexts encrypted under the Apple A10X Fusion SoC Group Identification (GID) key.
   - **Security Boundary**: The GID key is hard-fused into the silicon metal layers during chip fabrication and is accessible only to the AES crypto engine on physical hardware. It cannot be extracted or emulated in static software.
   - **Reverse Engineering Impact**: **Zero impact** on tvOS application, UI framework, or system architecture reverse engineering. These bootloaders only manage DRAM initialization, low-level power rails, and initial signature validation before handing execution to the kernel.

2. **Fully Accessible OS, Frameworks, and Application Stage (100% Plaintext)**:
   - **Kernelcache** (`kernelcache.release.j105a`): The IM4P container tag `krnl` contains **no KBAG**. Element 3 contains a raw LZFSE-compressed byte stream (`bvx2` magic). Decompression produces a standard 64-bit ARM64 Mach-O kernel executable (`0xfeedfacf`) of 31,363,656 bytes with all Mach-O headers, segment commands, and kext symbols intact.
   - **Restore Ramdisk** (`038-50764-064.dmg.image-img4` / `arm64SURamDisk.dmg`): The IM4P tag `rdsk` contains **no KBAG**. Stripping the 27-byte ASN.1 header reveals an unencrypted HFSX partition image (`HX\x00\x05`) with volume label `YagerG17M61.arm64SURamDisk`. Contains 507 files including core frameworks (`CoreFoundation`, `Foundation`, `CFNetwork`, `Security`) and utilities (`bin/`, `usr/bin/`).
   - **Device Configuration & Boot Graphics**: `DeviceTree.j105aap.im4p` (`dtre`), `applelogo~appletv.im4p` (`logo`), and `recoverymode@1080~appletv5.im4p` (`recm`) contain **no KBAG** and decompress directly into native DeviceTree nodes and `iBootIm` pixel buffers.
   - **Target OS Root Filesystem** (`038-50852-064.dmg` across `payloadv2/`): Chunked into 25 `pbzx` files (`payload.000` through `payload.024`). Zero encryption keys or DRM wrappers exist on these chunks. Every single file, directory, and framework is compressed with standard XZ / LZMA2 and extracts cleanly.

### 2.2 PBZX Container and Record Header Architecture
The root filesystem payload is distributed as a multi-chunk stream governed by Apple's `pbzx` format:
- **File Header**: 4-byte magic string `pbzx` followed by an 8-byte big-endian unsigned integer declaring the buffer chunk size (`0x0000000000800000` = 8,388,608 bytes / 8 MB).
- **Chunk Header**: 16 bytes per chunk: `dlen: uint64_be` (decompressed length) and `clen: uint64_be` (compressed length).
  - If `dlen == clen`: Raw uncompressed block.
  - If payload starts with `\xfd7zXZ\x00`: Standard XZ / LZMA2 container.
- **Record Header (Decompressed Stream)**: Every file and directory is encoded as an exact 30-byte header unpacked via `struct.unpack(">HQQIHHHH", hdr)`:
  - `rtype: uint16_be`: Record type (`0x1001` = Regular File, `0x1002` = Directory).
  - `fsize: uint64_be`: File byte count (0 for directories).
  - `mtime: uint64_be`: POSIX timestamp.
  - `flags: uint32_be`: Apple filesystem metadata flags.
  - `nlen: uint16_be`: Length of the UTF-8 relative path.
  - `uid: uint16_be`: User ID.
  - `gid: uint16_be`: Group ID.
  - `mode: uint16_be`: POSIX octal file permissions.
  - Followed by `nlen` path bytes, then `fsize` raw file data bytes.

---

## 3. Extracted Applications Inventory (`extracted/rootfs/Applications/`)

| Application Path | Size (Bytes) | Format | SHA-256 Digest |
| :--- | :--- | :--- | :--- |
| `extracted/rootfs/Applications/AppStore.app/AppStore` | 2,829,904 | Mach-O 64-bit ARM64 | `45aeda4bd7269c9b993ec5332277fb12ecc2ec072268a0e0d722ec043d27d40e` |
| `extracted/rootfs/Applications/AppStore.app/PlugIns/AppStoreTopShelfExtension.appex/AppStoreTopShelfExtension` | 156,912 | Mach-O 64-bit ARM64 | `78459c8f60322e986a8c8dedec04c0363b0bc9c6d9c43f0b9cc659977788a0f2` |
| `extracted/rootfs/Applications/AppleTV.app/AppleTV` | 134,176 | Mach-O 64-bit ARM64 | `a0bf529c1688e7e39909a38ff65bb09118d04023535f241786f82482c1719347` |
| `extracted/rootfs/Applications/AppleTV.app/PlugIns/TVUpNextExtension.appex/TVUpNextExtension` | 112,928 | Mach-O 64-bit ARM64 | `564772c152f2aa78d01e7bafb15be6bdb6a4757265a4e89386df07662339e7b4` |
| `extracted/rootfs/Applications/HeadBoard.app/HeadBoard` | 1,319,504 | Mach-O 64-bit ARM64 | `15c11e632a40c402e142102b912bbc6c1a7e195cc227933b5b2be0d4c542437b` |
| `extracted/rootfs/Applications/PineBoard.app/PineBoard` | 3,645,792 | Mach-O 64-bit ARM64 | `1a72bb5bd7b18385bc720b0f1ec47b4589ac889131e46a7c5de8b04b5d9d44bc` |
| `extracted/rootfs/Applications/PreBoard.app/PreBoard` | 111,008 | Mach-O 64-bit ARM64 | `51d44a4c5c5589ee0c07bedbe6c0f3b89744b3c3a1451cb8a833d03aeba48305` |
| `extracted/rootfs/Applications/Setup.app/Setup` | 1,190,000 | Mach-O 64-bit ARM64 | `62fa7dbe70617d5fd40a0449fc53f53b0f16347885cabb5ad3ec06cdd77ed1ba` |
| `extracted/rootfs/Applications/TVIdleScreen.app/TVIdleScreen` | 269,776 | Mach-O 64-bit ARM64 | `3d68c35f42b8c0418932457638dd0aa89b5c4eed47e47744f552941904c1d014` |
| `extracted/rootfs/Applications/TVMusic.app/PlugIns/TVMusicTopShelfExtension.appex/TVMusicTopShelfExtension` | 139,328 | Mach-O 64-bit ARM64 | `63aa9b8973c1a9d4260ba38e1c9d3d9856762ff7ebb02cf6d52d28e64cff6e70` |
| `extracted/rootfs/Applications/TVMusic.app/TVMusic` | 1,524,400 | Mach-O 64-bit ARM64 | `2d7d192ec3ea82867c2bcf62f616625cabffcda5a19b9627147cb5b083504a1c` |
| `extracted/rootfs/Applications/TVPeripheralAgent.app/TVPeripheralAgent` | 130,176 | Mach-O 64-bit ARM64 | `ba276a6efc75bb7bfcad3bfe2de9436d41c2ad70a97b998d97c1a68b98f0465c` |
| `extracted/rootfs/Applications/TVSystemBulletinService.app/TVSystemBulletinService` | 74,512 | Mach-O 64-bit ARM64 | `4617d638931a4978cd9321c3608bfa66515eb776835a638f0f5a6201b4007099` |
| `extracted/rootfs/Applications/TVSystemMenuService.app/TVSystemMenuService` | 129,472 | Mach-O 64-bit ARM64 | `d3dc9f056de85715cfbcbca08152e63f65e194ebf764a072bde5c7ad8ac64f47` |

---

## 4. Compiled UI Asset Catalogs (`.car`)

| Asset Catalog Path | Size (Bytes) | Format | SHA-256 Digest |
| :--- | :--- | :--- | :--- |
| `extracted/rootfs/Applications/AppStore.app/Assets.car` | 13,073,384 | BOMStore Asset Catalog (.car) | `f85ac4211704e2a615cba7b3f87ba532aa6dd4fe31e23e4537ce55e65523ff6c` |
| `extracted/rootfs/Applications/AppleTV.app/Assets.car` | 359,208 | BOMStore Asset Catalog (.car) | `11344a3a5253f8c89e426d471ea607606da5f81a12e1a0f71cfdfc83e533f52f` |
| `extracted/rootfs/Applications/Arcade.app/Assets.car` | 13,448,728 | BOMStore Asset Catalog (.car) | `55b509303cc359ac9cae05d1eeb8fd97d8b34b9f4aa991227f413b1f801f2a04` |
| `extracted/rootfs/Applications/HeadBoard.app/Assets.car` | 666,808 | BOMStore Asset Catalog (.car) | `5e0b756f78053054d5ec095761c831916ca810cc3f13d3d0bf801fe06409ecef` |
| `extracted/rootfs/Applications/PineBoard.app/Assets.car` | 116,088 | BOMStore Asset Catalog (.car) | `ccf03d5b6f663ae6e4817cfc3fb247f6ea3a4884e66c63d34621792f59ec05f8` |
| `extracted/rootfs/Applications/PreBoard.app/Assets.car` | 25,512 | BOMStore Asset Catalog (.car) | `1c3ce0edffa5c2342df17888c71018b9be428938dff10bdef44e635b65ee0482` |
| `extracted/rootfs/Applications/Setup.app/Assets.car` | 27,624 | BOMStore Asset Catalog (.car) | `89ba9dc87d34272301eec08551493111d118bf0ceff78dd0d8e5432855bdc3a2` |
| `extracted/rootfs/Applications/Siri.app/Assets.car` | 175,400 | BOMStore Asset Catalog (.car) | `df8ab96c4d973e98e7b404a982beea155cd0b537851d5178a377b7c8d4aca2d7` |
| `extracted/rootfs/Applications/TVCRDService.app/Assets.car` | 20,200 | BOMStore Asset Catalog (.car) | `dee26611341e66bc6d634d8d28ab55101209de018e14d4217c86a8d9bdf7f25f` |
| `extracted/rootfs/Applications/TVDiagnostics.app/Assets.car` | 97,288 | BOMStore Asset Catalog (.car) | `fd57429eb510ece001bf70cb84229994141b6e8584906eb2bb1b782fd569f335` |
| `extracted/rootfs/Applications/TVMusic.app/Assets.car` | 8,585,224 | BOMStore Asset Catalog (.car) | `5b113911e295f25e884caa9be6ef4d00f419f5bd491b40ffc3daf7bb597d1ef7` |
| `extracted/rootfs/Applications/TVNowPlayingService.app/Assets.car` | 359,416 | BOMStore Asset Catalog (.car) | `f5cfcecef4e644712c8e000a906444f1728ede6a1c39083a571f4bca58a65307` |
| `extracted/rootfs/Applications/TVPhotos.app/Assets.car` | 1,998,568 | BOMStore Asset Catalog (.car) | `6fcd4355565f1a394f9faecc41d7075191c78c9b1106e4c5464e98a7521de18a` |
| `extracted/rootfs/Applications/TVSearch.app/Assets.car` | 1,215,048 | BOMStore Asset Catalog (.car) | `a7de8894ea3a76488feed6ea8825f9924cf3cdf05631067f8c51795b1bc7ddd8` |
| `extracted/rootfs/Applications/TVSystemBulletinService.app/Assets.car` | 101,448 | BOMStore Asset Catalog (.car) | `17966ae44f96c334ef0a523eb7989943ef4458f0473a9414b1a474878bb8745e` |
| `extracted/rootfs/Applications/TVSystemMenuService.app/Assets.car` | 19,512 | BOMStore Asset Catalog (.car) | `dfcff36046d9769688ba09f663ad7ee2db274a4a8ee494fdaf393084dd138b25` |
| `extracted/rootfs/System/Library/CoreServices/AssistiveTouch.app/Assets.car` | 555,480 | BOMStore Asset Catalog (.car) | `894b90cecb0258de6d5418add32eb93a4724d060b25412453ff6744243057495` |
| `extracted/rootfs/System/Library/CoreServices/CoreGlyphs.bundle/Assets.car` | 91,411,496 | BOMStore Asset Catalog (.car) | `e7d64ced57ba6f682518a5988b5eb671ea2e237eb50857068183375d1b747be1` |
| `extracted/rootfs/System/Library/CoreServices/MobileCoreTypes.bundle/Assets.car` | 768,472 | BOMStore Asset Catalog (.car) | `31a07b533c53437400d48dfbe5910875f2d1291de05143983198544ab67d934a` |

---

## 5. System Partitions, Kernel & Shared Libraries

| Component Path | Size (Bytes) | Subsystem Description | SHA-256 Digest |
| :--- | :--- | :--- | :--- |
| `extracted/dyld_cache/dyld_shared_cache_arm64` | 1,086,013,440 | dyld Shared Cache (ARM64) | `8b0cf8e0a862915d5c98a26ba07dd9b574e367aa332a20a1d94bf2dc51d30412` |
| `extracted/firmware/DeviceTree.bin` | 106,428 | Decapsulated Apple DeviceTree Binary | `7ca1b3949f6ebc71ebb0ead04d90a21d33a36534f4cfb1069f7e386f6146b46a` |
| `extracted/firmware/applelogo.img3` | 4,723 | Decapsulated Boot Logo Image (iBootIm) | `433389a7a075f06d5d4e74bb0a07ee48e0483c5d035e843e0aa62f537c5e5fc0` |
| `extracted/firmware/recoverymode.img3` | 44,585 | Decapsulated Recovery Mode Image (iBootIm) | `e7cb602f056c9011588bea1a78b58be4c7b6da06315b7a9503253acb99317502` |
| `extracted/kernel/kernelcache.macho` | 31,363,656 | Decrypted/Decompressed Kernelcache (Mach-O 64-bit) | `df0d622ace9a648f3de12c1f2c003360f4048f1024a0a074cc28916e1ad5afe3` |

---

## 6. Restore Ramdisk Partition Components (`extracted/ramdisk/`)

| Component Path | Size (Bytes) | Subsystem Description | SHA-256 Digest |
| :--- | :--- | :--- | :--- |
| `extracted/ramdisk/System/Library/Frameworks/CFNetwork.framework/CFNetwork` | 5,067,376 | Mach-O 64-bit ARM64 (CFNetwork.framework) | `d4a8a254b415284bd295143a211a3a7aa367b4735b7272140bbd3b10d852e00f` |
| `extracted/ramdisk/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation` | 5,997,872 | Mach-O 64-bit ARM64 (CoreFoundation.framework) | `53ff4cbc9f5a4b410095486bd9d51f329647efdc0a9cf262ea76ffff7fff0bd9` |
| `extracted/ramdisk/System/Library/Frameworks/CoreServices.framework/CoreServices` | 2,960,256 | Mach-O 64-bit ARM64 (CoreServices.framework) | `9b48a150d8d7a634c565b24778fefc24eab042d3735a6d82e787430e8b78b101` |
| `extracted/ramdisk/System/Library/Frameworks/Foundation.framework/Foundation` | 6,471,296 | Mach-O 64-bit ARM64 (Foundation.framework) | `21927f62c504c418847b58a89f69c6d9c32378e840776841f338623ffbf49c8d` |
| `extracted/ramdisk/System/Library/Frameworks/IOSurface.framework/IOSurface` | 234,080 | Mach-O 64-bit ARM64 (IOSurface.framework) | `a86e0366953e42edc39b834912d474c24831cc6f4df53eea398c073abd63214e` |
| `extracted/ramdisk/System/Library/Frameworks/MobileCoreServices.framework/MobileCoreServices` | 17,056 | Mach-O 64-bit ARM64 (MobileCoreServices.framework) | `1d8eedc15c47c36d40aa85dbf40de1a084a3cf90bd37ec195f53322b733a529d` |
| `extracted/ramdisk/System/Library/Frameworks/Security.framework/Security` | 2,472,384 | Mach-O 64-bit ARM64 (Security.framework) | `a406706113ee9f5f104a12165b040f5344782b37e3569f84ee3edaee9d7a63d8` |
| `extracted/ramdisk/System/Library/Frameworks/SystemConfiguration.framework/SystemConfiguration` | 818,560 | Mach-O 64-bit ARM64 (SystemConfiguration.framework) | `a2addb4ce1960a2766688921e0db8bb827ea41f6f8406581c97641015bd497a3` |
| `extracted/ramdisk/bin/cat` | 51,728 | Mach-O 64-bit ARM64 | `597a87178fe871442bc342176adcfc89847f7651b83df07ffbff2a08aaa8d585` |
| `extracted/ramdisk/bin/expr` | 51,216 | Mach-O 64-bit ARM64 | `e3aed044b58a940932c8a027d0a6d47c1de8e6e060628bd18344ae40483ba638` |
| `extracted/ramdisk/bin/ln` | 51,232 | Mach-O 64-bit ARM64 | `1d79ab4c5c9bca0d2acd95920c0c3ba6d41b2984af03ae89b4dc116c7d6dea27` |
| `extracted/ramdisk/bin/mkdir` | 50,800 | Mach-O 64-bit ARM64 | `e38bf34c9bc65709292fb8558d774dd0299a74af0abb162f301581149e2fab46` |
| `extracted/ramdisk/bin/mv` | 52,448 | Mach-O 64-bit ARM64 | `cb540f598a634385f45500c43639cf15ef1685758b2c9959079b1c4dfe89c11f` |
| `extracted/ramdisk/bin/rm` | 52,192 | Mach-O 64-bit ARM64 | `901c369e5bf4a0a9614e103a14d8bfa9935367499b0b629e586eb49dc0896259` |
| `extracted/ramdisk/sbin/fsck` | 53,776 | Mach-O 64-bit ARM64 | `9ad6e0c6151fa4b4601b50b1abf5f1cc7ac4038bc7dd3fcc6062f81c97985982` |
| `extracted/ramdisk/sbin/halt` | 51,008 | Mach-O 64-bit ARM64 | `7472ad55236e7cb78d04bbd3408e1f14d85932128aa4c586a69effa9229bbf45` |
| `extracted/ramdisk/sbin/launchd` | 365,776 | Mach-O 64-bit ARM64 | `cb96819393bb497c334a08cce8c4e90c388e85d2a7e366645b4ba9f31e8b8059` |
| `extracted/ramdisk/sbin/mount` | 73,776 | Mach-O 64-bit ARM64 | `af3d4db9e417af76fdefe7e284bd6fb1e012c8a90e4fbbb3b4ee953f61ec8760` |
| `extracted/ramdisk/sbin/reboot` | 51,008 | Mach-O 64-bit ARM64 | `7472ad55236e7cb78d04bbd3408e1f14d85932128aa4c586a69effa9229bbf45` |
| `extracted/ramdisk/usr/bin/TiSerialFlasher` | 50,496 | Mach-O 64-bit ARM64 | `a1bf9febc72b0fda4754a19ea86e80c3a624dc3875be76cee01d0dd30b98f945` |
| `extracted/ramdisk/usr/bin/ampctl` | 73,136 | Mach-O 64-bit ARM64 | `a0cc3ee57b92f91727946397c40879cd210c766f18f38ecd8595dec973c08a58` |
| `extracted/ramdisk/usr/bin/nvmefwupdater` | 70,512 | Mach-O 64-bit ARM64 | `a5d6e726bb0831199eb7028718637041276bd1708842df4837e263a42959b9ae` |
| `extracted/ramdisk/usr/bin/peppytool` | 53,280 | Mach-O 64-bit ARM64 | `a0451ce31faa1e0575cf35fd08f5300cee00f38c9ab56c224f899caf04f1604c` |
| `extracted/ramdisk/usr/bin/sed` | 70,384 | Mach-O 64-bit ARM64 | `3242819df54b302f443fcd80e475cb45a682169a75b9e29404ea03c461546c5d` |
| `extracted/ramdisk/usr/bin/update_mcdp29xx` | 79,840 | Mach-O 64-bit ARM64 | `56d59d03e861fbbaab9988b105c0ca6f1549153455f24251b2fcdacdf41a9b17` |
| `extracted/ramdisk/usr/sbin/asr` | 361,680 | Mach-O 64-bit ARM64 | `7c7d06644c748f24d749cbd9b91c95ac459d225685a76f90e5201ee0537cad87` |
| `extracted/ramdisk/usr/sbin/hdik` | 56,832 | Mach-O 64-bit ARM64 | `51ffffbb5734fa1511f247dddce3ac7ff0967685d032b5706637cbf9f5ed79d0` |
| `extracted/ramdisk/usr/sbin/nvram` | 54,256 | Mach-O 64-bit ARM64 | `e1cee8a32383ccb1f58efef9271acda9d2090b81e32e09201c80af382691dc74` |
| `extracted/ramdisk/usr/sbin/syslogd` | 166,496 | Mach-O 64-bit ARM64 | `d74da14ca663a92dc2b22c45eef09c1904a537690a7607c867b51fb76e07c443` |

---

## 7. Raw Input Manifests & Firmware Checksums (`raw/`)

| File Path | Size (Bytes) | SHA-256 Digest |
| :--- | :--- | :--- |
| `8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip` | 2,014,940,073 | `8725797b4ddfd93fc67023c93c1d9277f128e9731a9ac18618b9b2e812c027c1` |
| `raw/firmware/038-50764-064.dmg.image-img4` | 73,174,043 | `c556af723da68b86ba178b54fbf3abdf2098fc60d3b0eed04c914be92b88a880` |
| `raw/firmware/DeviceTree.j105aap.im4p` | 106,482 | `ef6db6486bf6ff111066561fb50849fbe84acc54386fb896d2f36393c7f03578` |
| `raw/firmware/LLB.j105a.RELEASE.im4p` | 483,039 | `ccb4ed2dbac95d813ae442aa1fd9fbb2a016e9c1783c04ac4bc849180dc714db` |
| `raw/firmware/aopfw-j105aaop.im4p` | 187,421 | `a775541afa833e32f4ebd174e61978874f604d7cd10c07f71c98ad69d89b521c` |
| `raw/firmware/applelogo~appletv.im4p` | 4,768 | `389d5a24bcd8578cbc586cb6f9616e0b2d136d713de642a7da1847bad8289096` |
| `raw/firmware/arm64SURamDisk.dmg` | 73,174,043 | `c556af723da68b86ba178b54fbf3abdf2098fc60d3b0eed04c914be92b88a880` |
| `raw/firmware/iBEC.j105a.RELEASE.im4p` | 483,039 | `a8da6d638fff3c29c07da51a68bc26718820fcc3dbfffee207a2abed4f305b95` |
| `raw/firmware/iBSS.j105a.RELEASE.im4p` | 483,039 | `00fd9908a766fbc89306808b39534bd1e1cb7056371397fb0eed4dd16391afcc` |
| `raw/firmware/iBoot.j105a.RELEASE.im4p` | 483,039 | `4c9b4b8c16f2f6f6e422f4c161424915e97ec2ba0fe90b379d0b731ceac72cd9` |
| `raw/firmware/kernelcache.release.j105a` | 11,891,668 | `182f88795e558102df6c3cfb382633a1eeb86dd207437917cfaab8989f9d7a60` |
| `raw/firmware/recoverymode@1080~appletv5.im4p` | 44,630 | `7f2bbba0e0b99f69f9f64b64a11f3a13ae358e95f6aec8f37275ffb0a911ff61` |
| `raw/firmware/sep-firmware.j105a.RELEASE.im4p` | 1,994,970 | `0479d69f8fe9fd0f3bf15919165714eb79dfab61689bf01c1f84587c79401b05` |
| `raw/manifests/AssetData_Info.plist` | 1,909 | `f5f6dfd30223573a91fffce16c6d3bfb46e4b9010133bdb0a2d7f9f161e65dcb` |
| `raw/manifests/BuildManifest.plist` | 48,898 | `81c1cce2ea89d67c48c89f9cb9094319034743698e16439f5f16dafaf8e9209c` |
| `raw/manifests/Info.plist` | 1,940 | `534bc881647ac16fdb7ea8d77e00e72d096c3fcc341283be48904785cebd03ee` |
| `raw/manifests/ZipMetadata.plist` | 173 | `c656d3094d614f0af6af049495ca0713dd1106db78d130eacedafde93db4e21c` |
| `raw/manifests/payload.bom` | 40,596 | `369c0c041c2a13b94ef676d92ea3a489fdeed0bad6e5030b2a2f0cead892cbb8` |
| `raw/manifests/post.bom` | 6,300,220 | `b11c8762d7c1fd05bf35a9be32f81ad31d0c6df147457d4a93863e4c93840c22` |
| `raw/manifests/pre.bom` | 35,046 | `c2786c62b22f78ec6c416e1b6b3605f002771e4ec1bb2d48d9effcbda6fd04f7` |

---

## 8. Forensic Verification Protocol

To independently audit and verify this extraction ledger, execute the following commands from the project root:

### 1. Verify Raw Input Checksums
```bash
sha256sum -c raw/checksums.sha256
```

### 2. Verify Extracted Kernelcache Mach-O
```bash
file extracted/kernel/kernelcache.macho
# Expected: Mach-O 64-bit arm64 executable
```

### 3. Verify dyld Shared Cache Magic
```bash
head -c 16 extracted/dyld_cache/dyld_shared_cache_arm64
# Expected: dyld_v1   arm64
```

### 4. Verify Asset Catalogs BOMStore Header
```bash
head -c 8 extracted/rootfs/System/Library/CoreServices/CoreGlyphs.bundle/Assets.car
# Expected: BOMStore
```

### 5. Validate Application Binaries
```bash
file extracted/rootfs/Applications/PineBoard.app/PineBoard
file extracted/rootfs/Applications/HeadBoard.app/HeadBoard
file extracted/rootfs/Applications/Setup.app/Setup
```
