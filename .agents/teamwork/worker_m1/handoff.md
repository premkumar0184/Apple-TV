# Milestone 1 Handoff Report: Archive Forensics & Filesystem Extraction

**Author**: Worker 1 (`worker_m1`)  
**Role**: implementer / qa / specialist  
**Working Directory**: `/home/prem/Projects/AppleTV/.agents/teamwork/worker_m1`  
**Workspace Root**: `/home/prem/Projects/AppleTV`  
**Parent Conversation ID**: `995e6d20-c347-437b-93ba-1b98ec79241b`  
**Milestone**: M1 (Archive Forensics, Filesystem Extraction & Hierarchy Preservation)  
**Status**: COMPLETE (Hard Handoff)  
**Execution Safety (R7)**: Strictly Static Analysis — 0 Target Host Executions  

---

## 1. Observation

### 1.1 Firmware Identity, Manifests & Checksums
- **Input Archive**: `/home/prem/Projects/AppleTV/8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip` (2,014,940,073 bytes)
- **Authoritative Hash Ledger**: `/home/prem/Projects/AppleTV/raw/checksums.sha256`
- **Verified SHA-256 Checksums (`sha256sum -c raw/checksums.sha256`)**:
  ```text
  8725797b4ddfd93fc67023c93c1d9277f128e9731a9ac18618b9b2e812c027c1  8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip: OK
  81c1cce2ea89d67c48c89f9cb9094319034743698e16439f5f16dafaf8e9209c  raw/manifests/BuildManifest.plist: OK
  534bc881647ac16fdb7ea8d77e00e72d096c3fcc341283be48904785cebd03ee  raw/manifests/Info.plist: OK
  f5f6dfd30223573a91fffce16c6d3bfb46e4b9010133bdb0a2d7f9f161e65dcb  raw/manifests/AssetData_Info.plist: OK
  c656d3094d614f0af6af049495ca0713dd1106db78d130eacedafde93db4e21c  raw/manifests/ZipMetadata.plist: OK
  369c0c041c2a13b94ef676d92ea3a489fdeed0bad6e5030b2a2f0cead892cbb8  raw/manifests/payload.bom: OK
  c2786c62b22f78ec6c416e1b6b3605f002771e4ec1bb2d48d9effcbda6fd04f7  raw/manifests/pre.bom: OK
  b11c8762d7c1fd05bf35a9be32f81ad31d0c6df147457d4a93863e4c93840c22  raw/manifests/post.bom: OK
  c556af723da68b86ba178b54fbf3abdf2098fc60d3b0eed04c914be92b88a880  raw/firmware/038-50764-064.dmg.image-img4: OK
  182f88795e558102df6c3cfb382633a1eeb86dd207437917cfaab8989f9d7a60  raw/firmware/kernelcache.release.j105a: OK
  c556af723da68b86ba178b54fbf3abdf2098fc60d3b0eed04c914be92b88a880  raw/firmware/arm64SURamDisk.dmg: OK
  ef6db6486bf6ff111066561fb50849fbe84acc54386fb896d2f36393c7f03578  raw/firmware/DeviceTree.j105aap.im4p: OK
  389d5a24bcd8578cbc586cb6f9616e0b2d136d713de642a7da1847bad8289096  raw/firmware/applelogo~appletv.im4p: OK
  7f2bbba0e0b99f69f9f64b64a11f3a13ae358e95f6aec8f37275ffb0a911ff61  raw/firmware/recoverymode@1080~appletv5.im4p: OK
  4c9b4b8c16f2f6f6e422f4c161424915e97ec2ba0fe90b379d0b731ceac72cd9  raw/firmware/iBoot.j105a.RELEASE.im4p: OK
  ccb4ed2dbac95d813ae442aa1fd9fbb2a016e9c1783c04ac4bc849180dc714db  raw/firmware/LLB.j105a.RELEASE.im4p: OK
  0479d69f8fe9fd0f3bf15919165714eb79dfab61689bf01c1f84587c79401b05  raw/firmware/sep-firmware.j105a.RELEASE.im4p: OK
  a775541afa833e32f4ebd174e61978874f604d7cd10c07f71c98ad69d89b521c  raw/firmware/aopfw-j105aaop.im4p: OK
  a8da6d638fff3c29c07da51a68bc26718820fcc3dbfffee207a2abed4f305b95  raw/firmware/iBEC.j105a.RELEASE.im4p: OK
  00fd9908a766fbc89306808b39534bd1e1cb7056371397fb0eed4dd16391afcc  raw/firmware/iBSS.j105a.RELEASE.im4p: OK
  ```
- **Firmware Metadata (`raw/manifests/BuildManifest.plist` & `raw/manifests/Info.plist`)**:
  - `OSVersion`: `13.4.8`
  - `ProductBuildVersion`: `17M61`
  - `BuildTrain`: `YagerG`
  - `DeviceClass`: `j105aap`
  - `ProductType`: `AppleTV6,2` (Apple TV 4K 1st Gen, A1842)
  - `ApChipID`: `0x8011` (Apple A10X Fusion, T8011)
  - `ApBoardID`: `0x02`

### 1.2 Extracted Boot & Kernel Components
- `extracted/kernel/kernelcache.macho`:
  - Size: `31,363,656` bytes (~31.36 MB)
  - SHA-256: `df0d622ace9a648f3de12c1f2c003360f4048f1024a0a074cc28916e1ad5afe3`
  - Magic bytes: `0xfeedfacf` (Mach-O 64-bit arm64 executable)
  - Extraction mechanism: ASN.1 DER sequence parsed, stripped 53-byte header, LZFSE decompressed `bvx2` payload.
- `extracted/firmware/DeviceTree.bin`:
  - Size: `106,428` bytes
  - SHA-256: `7ca1b3949f6ebc71ebb0ead04d90a21d33a36534f4cfb1069f7e386f6146b46a`
- `extracted/firmware/applelogo.img3`:
  - Size: `4,723` bytes, magic: `iBootIm`
  - SHA-256: `433389a7a075f06d5d4e74bb0a07ee48e0483c5d035e843e0aa62f537c5e5fc0`
- `extracted/firmware/recoverymode.img3`:
  - Size: `44,585` bytes, magic: `iBootIm`
  - SHA-256: `e7cb602f056c9011588bea1a78b58be4c7b6da06315b7a9503253acb99317502`
- `extracted/ramdisk/`:
  - Extracted 507 files and 164 directories from HFSX image `arm64SURamDisk.dmg`.
  - Core frameworks: `CFNetwork`, `CoreFoundation`, `CoreServices`, `Foundation`, `IOSurface`, `MobileCoreServices`, `Security`, `SystemConfiguration`.
  - Utilities: `bin/cat`, `bin/ln`, `bin/mv`, `sbin/launchd`, `usr/sbin/asr`, `usr/sbin/syslogd`, etc.

### 1.3 Streaming PBZX Extractor Execution (`scripts/extract_payload.py`)
- Extraction run output:
  ```text
  [*] Beginning PBZX streaming extraction...
      Payloads: 11 archives
      Rootfs output: extracted/rootfs
      dyld output: extracted/dyld_cache
  ...
  [+] Extraction Complete!
      Total files/dirs extracted: 1,400
      Total bytes extracted: 1,211,919,364 (1155.8 MB)
      Total time: 22.23s

  [*] Validating extracted components...
  [VALID] dyld_shared_cache_arm64 magic verified: b'dyld_v1   arm64'

  Validation Summary:
    Files checked: 901
    Valid Mach-O 64-bit binaries: 12
    Valid Asset Catalogs (BOMStore): 17
    Valid dyld shared cache: True
  ```

### 1.4 Extracted Core Applications & Binaries
All 10 required system applications were extracted into `extracted/rootfs/Applications/`:
1. `PineBoard.app/PineBoard`: 3,645,792 bytes, Mach-O 64-bit arm64 (`1a72bb5bd7b18385bc720b0f1ec47b4589ac889131e46a7c5de8b04b5d9d44bc`)
2. `HeadBoard.app/HeadBoard`: 1,319,504 bytes, Mach-O 64-bit arm64 (`15c11e632a40c402e142102b912bbc6c1a7e195cc227933b5b2be0d4c542437b`)
3. `PreBoard.app/PreBoard`: 111,008 bytes, Mach-O 64-bit arm64 (`51d44a4c5c5589ee0c07bedbe6c0f3b89744b3c3a1451cb8a833d03aeba48305`)
4. `Setup.app/Setup`: 1,190,000 bytes, Mach-O 64-bit arm64 (`62fa7dbe70617d5fd40a0449fc53f53b0f16347885cabb5ad3ec06cdd77ed1ba`)
5. `TVSystemMenuService.app/TVSystemMenuService`: 129,472 bytes, Mach-O 64-bit arm64 (`d3dc9f056de85715cfbcbca08152e63f65e194ebf764a072bde5c7ad8ac64f47`)
6. `TVSystemBulletinService.app/TVSystemBulletinService`: 74,512 bytes, Mach-O 64-bit arm64 (`4617d638931a4978cd9321c3608bfa66515eb776835a638f0f5a6201b4007099`)
7. `TVPeripheralAgent.app/TVPeripheralAgent`: 130,176 bytes, Mach-O 64-bit arm64 (`ba276a6efc75bb7bfcad3bfe2de9436d41c2ad70a97b998d97c1a68b98f0465c`)
8. `TVIdleScreen.app/TVIdleScreen`: 269,776 bytes, Mach-O 64-bit arm64 (`3d68c35f42b8c0418932457638dd0aa89b5c4eed47e47744f552941904c1d014`)
9. `AppleTV.app/AppleTV`: 134,176 bytes, Mach-O 64-bit arm64 (`a0bf529c1688e7e39909a38ff65bb09118d04023535f241786f82482c1719347`)
10. `AppStore.app/AppStore`: 2,829,904 bytes, Mach-O 64-bit arm64 (`45aeda4bd7269c9b993ec5332277fb12ecc2ec072268a0e0d722ec043d27d40e`)
11. `AppleTV.app/PlugIns/TVUpNextExtension.appex/TVUpNextExtension`: 112,928 bytes, Mach-O 64-bit arm64 (`564772c152f2aa78d01e7bafb15be6bdb6a4757265a4e89386df07662339e7b4`)
12. `AppStore.app/PlugIns/AppStoreTopShelfExtension.appex/AppStoreTopShelfExtension`: 156,912 bytes, Mach-O 64-bit arm64 (`78459c8f60322e986a8c8dedec04c0363b0bc9c6d9c43f0b9cc659977788a0f2`)

### 1.5 Shared Libraries & Compiled Asset Catalogs
- `extracted/dyld_cache/dyld_shared_cache_arm64`: 1,086,013,440 bytes (`8b0cf8e0a862915d5c98a26ba07dd9b574e367aa332a20a1d94bf2dc51d30412`), magic `dyld_v1   arm64`. Symlinked to `extracted/rootfs/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64`.
- **17 Verified BOMStore Asset Catalogs (`.car`)**:
  - `CoreGlyphs.bundle/Assets.car`: 91,411,496 bytes (`e7d64ced57ba6f682518a5988b5eb671ea2e237eb50857068183375d1b747be1`)
  - `AppStore.app/Assets.car`: 13,073,384 bytes (`f85ac4211704e2a615cba7b3f87ba532aa6dd4fe31e23e4537ce55e65523ff6c`)
  - `TVPhotos.app/Assets.car`: 1,998,568 bytes (`6fcd4355565f1a394f9faecc41d7075191c78c9b1106e4c5464e98a7521de18a`)
  - `TVSearch.app/Assets.car`: 1,215,048 bytes (`a7de8894ea3a76488feed6ea8825f9924cf3cdf05631067f8c51795b1bc7ddd8`)
  - `HeadBoard.app/Assets.car`: 666,808 bytes (`5e0b756f78053054d5ec095761c831916ca810cc3f13d3d0bf801fe06409ecef`)
  - `AppleTV.app/Assets.car`: 359,208 bytes (`11344a3a5253f8c89e426d471ea607606da5f81a12e1a0f71cfdfc83e533f52f`)
  - `TVNowPlayingService.app/Assets.car`: 359,416 bytes (`f5cfcecef4e644712c8e000a906444f1728ede6a1c39083a571f4bca58a65307`)
  - `Siri.app/Assets.car`: 175,400 bytes (`df8ab96c4d973e98e7b404a982beea155cd0b537851d5178a377b7c8d4aca2d7`)
  - `PineBoard.app/Assets.car`: 116,088 bytes (`ccf03d5b6f663ae6e4817cfc3fb247f6ea3a4884e66c63d34621792f59ec05f8`)
  - `TVSystemBulletinService.app/Assets.car`: 101,448 bytes (`17966ae44f96c334ef0a523eb7989943ef4458f0473a9414b1a474878bb8745e`)
  - `Setup.app/Assets.car`: 27,624 bytes (`89ba9dc87d34272301eec08551493111d118bf0ceff78dd0d8e5432855bdc3a2`)
  - `PreBoard.app/Assets.car`: 25,512 bytes (`1c3ce0edffa5c2342df17888c71018b9be428938dff10bdef44e635b65ee0482`)
  - `TVSystemMenuService.app/Assets.car`: 19,512 bytes (`dfcff36046d9769688ba09f663ad7ee2db274a4a8ee494fdaf393084dd138b25`)
  - `AssistiveTouch.app`, `MobileCoreTypes.bundle`, `TVCRDService`, `TVDiagnostics`.

---

## 2. Logic Chain

1. **Premise**: Milestone 1 mandates non-destructive extraction, cryptographic verification, directory structure preservation, and forensic accounting of extractable vs encrypted boundaries for tvOS 13.4.8 without executing target ARM64 binaries on host (R1, R2, R7).
2. **From §1.1**: Direct calculation established authoritative SHA-256 digests for `8988ef3518b1f20f95c66d03be3c15eb4e1be2a0.zip` (`8725797b...`), manifests, and BOM files into `raw/checksums.sha256`. Parsing `BuildManifest.plist` verified `17M61` / `13.4.8` on Apple A10X Fusion (`0x8011`).
3. **From §1.2**: IM4P analysis proved that `kernelcache`, `arm64SURamDisk`, `DeviceTree`, and boot logos contain no `KBAG` sequences (unencrypted). Stripping the 53-byte ASN.1 header and LZFSE decompression yielded a 31.36 MB Mach-O 64-bit kernelcache (`0xfeedfacf`). 7z unpacked the HFSX ramdisk into `extracted/ramdisk/`, exposing core frameworks and system binaries.
4. **From §1.3**: The PBZX container wraps standard XZ compressed streams, where records are serialized with a 30-byte header (`>HQQIHHHH`). `scripts/extract_payload.py` implemented streaming chunk decompression and selective extraction to recover the entire UI application stack, asset catalogs, and dyld shared cache while respecting host disk limits.
5. **From §1.4 & §1.5**: All 12 application binaries were verified as valid 64-bit Mach-O ARM64 executables, and all 17 `.car` catalogs were verified as `BOMStore` databases.
6. **From §1.1–§1.5**: All extracted assets, byte counts, and SHA-256 digests were compiled into `reports/EXTRACTION_LEDGER.md`, documenting why early bootloaders (`LLB`, `iBoot`, `SEP`) contain silicon GID KBAGs while 100% of userspace, kernelcache, and ramdisk are unencrypted.

---

## 3. Caveats

1. **TVIdleScreen Screensaver Videos**: The aerial video assets (`Default@2x.mov` and `Default@2x_HDR.mov`, totaling 255 MB in `payload.002` and `payload.003`) were deliberately bypassed to prevent host disk exhaustion within the 2.5 GB headroom. The application binary `TVIdleScreen`, `Info.plist`, entitlements, code signatures, and localization strings were 100% extracted.
2. **Hardware GID Keys on Bootloaders**: `LLB`, `iBoot`, `SEP`, `iBSS`, and `iBEC` contain AES-256 keybags encrypted under the A10X GID key fused in silicon hardware. They cannot be statically decrypted without physical silicon exploitation, but they are irrelevant to tvOS UI and userspace reverse engineering.
3. **Execution Safety**: Compliant with R7, zero tvOS ARM64 binaries were executed on the Linux host. All verifications were performed via static header checks, magic byte analysis, and cryptographic hashing.

---

## 4. Conclusion

Milestone 1 is **100% complete**:
- The 6-tier directory hierarchy is strictly initialized and populated.
- The raw firmware archive and all manifests are cryptographically verified and recorded in `raw/checksums.sha256`.
- The restore ramdisk, kernelcache, DeviceTree, and boot images are completely extracted into `extracted/ramdisk/`, `extracted/kernel/`, and `extracted/firmware/`.
- The pure Python PBZX streaming extractor (`scripts/extract_payload.py`) has unpacked 10 core system applications, 17 asset catalogs, and the 1.08 GB `dyld_shared_cache_arm64`.
- The forensic ledger `reports/EXTRACTION_LEDGER.md` is fully generated, detailing all 1,400 extracted assets with byte sizes, formats, SHA-256 digests, and security boundary documentation.
- The workspace is ready for downstream UI analysis (M2), binary reverse engineering (M3), and knowledge graph construction (M4).

---

## 5. Verification Method

To independently verify all Milestone 1 deliverables from `/home/prem/Projects/AppleTV`:

### 1. Verify Raw Input Checksums
```bash
sha256sum -c raw/checksums.sha256
# Expected: All 20 items output OK
```

### 2. Verify Extracted Kernelcache Mach-O Binary
```bash
file extracted/kernel/kernelcache.macho
# Expected: Mach-O 64-bit arm64 executable, flags:<NOUNDEFS|PIE>
```

### 3. Verify dyld Shared Cache Header
```bash
python3 -c "
with open('extracted/dyld_cache/dyld_shared_cache_arm64', 'rb') as f:
    assert f.read(16).startswith(b'dyld_v1   arm64')
print('dyld shared cache header verified.')
"
```

### 4. Verify PBZX Extraction and Magic Bytes
```bash
python3 scripts/extract_payload.py --validate-only
# Expected:
# Valid Mach-O 64-bit binaries: 12
# Valid Asset Catalogs (BOMStore): 17
# Valid dyld shared cache: True
```

### 5. Inspect Forensic Ledger
```bash
head -n 35 reports/EXTRACTION_LEDGER.md
```
