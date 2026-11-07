# Handoff Report: AEA Containers, Cryptographic Boundaries, and UI Evolution

**Agent**: `explorer_survey_ipsw_3`  
**Milestone**: M1_survey_ipsw_3  
**Working Directory**: `/home/prem/Projects/AppleTV/.agents/teamwork/explorer_survey_ipsw_3/`  
**Date**: 2026-11-06T21:12:00Z  
**Recipient**: `orchestrator_2` (`dca65d9e-caea-4f60-93bd-b30c8fc70405`)  

---

## 1. Observation

1. **IPSW Artifact Profiles**:
   - `AppleTV5,3_26.6.1_23L781_Restore.ipsw` (5,269,474,064 bytes) uncompressed to `/home/prem/Projects/AppleTV/AppleTV5,3_26.6.1_23L781_Restore/`.
   - Manifest plists:
     - `Restore.plist`: `ProductBuildVersion = 23L781`, `ProductVersion = 26.6.1`, `SystemRestoreImageFileSystems = {'094-98220-089.dmg.aea': 'APFS', '094-98312-089.dmg.aea': 'APFS'}`, `DeviceMap: [{'BDID': 52, 'BoardConfig': 'j42dap', 'CPID': 28672, 'Platform': 't7000'}]`.
     - `SystemVersion.plist`: `BuildID = 'C4F2A172-C67F-11F1-B898-89BA0ADA7B5F'`, `ProductBuildVersion = '23L781'`, `ProductName = 'Apple TVOS'`, `ProductVersion = '26.6.1'`.
     - `RestoreVersion.plist`: `RestoreVersion = '23.12.781.0.0'`.
     - `BuildManifest.plist`: `BuildIdentity[0]` (Customer Erase Install, OS: `094-98312-089.dmg.aea`, Ramdisk: `094-97800-089.dmg`), `BuildIdentity[1]` (Customer Upgrade Install, OS: `094-98312-089.dmg.aea`, Ramdisk: `094-97880-089.dmg`), `BuildIdentity[2]` (Recovery Customer Install, OS: `094-98220-089.dmg.aea`, Ramdisk: `094-97800-089.dmg`).

2. **AEA Container Header & Magic**:
   - Both `094-98312-089.dmg.aea` (4,831,838,208 bytes) and `094-98220-089.dmg.aea` (188,743,680 bytes) begin with bytes `41 45 41 31 01 00 00 00` (`AEA1`, Version 1, Profile 1: `SymmetricEncryption`).
   - Auth data length: 2,168 bytes for RootFS (`0x878`), 2,200 bytes for Recovery (`0x898`).
   - Metadata entries:
     - `com.apple.wkms.url`: `https://wkms.sd.apple.com`
     - `com.apple.wkms.auth-data`: Base64 protobuf with tag 3 SHA-256 digest `d3fdc97fa0f316d84ef15afadf4f90e5244ec24ca1dcba6d11ab4fbee70b8e13` and tag 4 ciphersuite `0010-0001-0002`.
     - `com.apple.wkms.fcs-response`:
       - RootFS: `enc-request`: `BGVe2XOQ70i4scCCk97qX4x4I727306BOPiG19PGQ0ImjtEpu1hSTudFsx1U2Q35O1E/C5K4nXw0Onv3+zZ15bI=`, `wrapped-key`: `T8z+k9S92HgNPwaMRKsALAgbRIfNl4O3+E+qawTkGvxVop8b9y7FhZjATeZgQlo0`.
       - Recovery: `enc-request`: `BF+SGXtsPeDamFpvTzC6x1XC1ZIR4vBth/U9yK0BdgfBjH+v3SayhxGWAl3Oro3XF173ewySirT3qKd/4o4hi9Y=`, `wrapped-key`: `ps2Q7bVqI3RJ2QQeDf2MKlfsEIrP9j/Mfm0gAxvRWceYawwadZSJg993kxymky4L`.
     - `com.apple.wkms.fcs-key-url`: `https://wkms-public.apple.com/fcs-keys/EqKp4rUE1uMIIEqnfHnqfscN_VFy_qgyE3Vus8_KQhE=`.

3. **FCS Public Key Resolution & HPKE Decryption**:
   - Querying `https://wkms-public.apple.com/fcs-keys/EqKp4rUE1uMIIEqnfHnqfscN_VFy_qgyE3Vus8_KQhE=` returned HTTP 200 with an unencrypted NIST P-256 EC Private Key PEM (`secp256r1`).
   - Executing RFC 9180 HPKE Base mode (`DHKEM(P-256, HKDF-SHA256)` + `HKDF-SHA256` + `AES-256-GCM`) decapsulated and unwrapped the 256-bit symmetric archive keys:
     - RootFS Key: `ca0d1a3eb45cdb15b15babced612a5d37914299f5d5d141d488ddccb40cda496`
     - Recovery Key: `efd41ef06e0adc9426ae40d7c6635dbca5c88f68029411bf465a34c7c9baf7d9`

4. **AEA Decrypted Root Header Dimensions**:
   - Deriving `mainKey` and `rootHdrKey` via HKDF yielded valid root header HMAC matches (`HMAC match?: True`).
   - RootFS uncompressed disk size: `8,562,671,616` bytes (7.97 GiB), segment size `1,048,576` bytes (1 MiB), 256 segments/cluster, LZFSE compression (`0x65`), SHA-256 checksums (`Type 2`).
   - Recovery OS uncompressed disk size: `186,642,646` bytes (178 MiB), segment size `1,048,576` bytes, 256 segments/cluster, LZFSE compression, SHA-256 checksums.

5. **Unencrypted Restore Ramdisks**:
   - `094-97800-089.dmg` (113,246,235 bytes) and `094-97880-089.dmg` (113,246,235 bytes) are Image4 payloads (`IM4P` tag `rdsk`).
   - Slicing 27 bytes reveals standard unencrypted APFS containers (`NXSB` at offset 59).
   - Ingested via 7-Zip 26.04 without errors:
     - 750 files, 314 directories in erase ramdisk; 1,364 entries in update ramdisk.
     - Binaries: `usr/local/bin/restored_external` (2.49 MB), `usr/libexec/diskimagesiod` (2.31 MB), `usr/libexec/driverkitd` (1.32 MB), `usr/sbin/asr` (396 KB).
     - UI Assets: `usr/share/progressui/` with 1080p (`images-AppleTV-1080/`), 4K (`images-AppleTV-2160/`), and standard TV progress bars, Apple logos, caps, and vector prompts (`disconnect-prompt.tga` 1536x2048, `power-button-prompt.tga` 1536x2048).
     - Vision Pro strap graphic: `System/Library/PrivateFrameworks/CoreAccessories.framework/vision.pro.developer.strap-N301a.png` (1024x1024 RGBA PNG).
     - Localization: 38+ language bundles (`.lproj`) across `LocalAuthenticationCore`, `MFAAuthentication`, and `apfs.fs`.
     - Frameworks: 76 frameworks showcasing heavy modern Swift infrastructure (`Combine`, `CryptoKit`, `SwiftASN1`, `AlgorithmsInternal`, `CollectionsInternal`).

---

## 2. Logic Chain

1. **Premise**: IPSW restore packages post-iOS/tvOS 16 package rootfs as `.dmg.aea`.
   - **Step 1**: From Observation 1, `Restore.plist` explicitly identifies `094-98312-089.dmg.aea` and `094-98220-089.dmg.aea` as APFS restore images.
   - **Step 2**: From Observation 2, both files start with `AEA1` magic, Profile 1 (`SymmetricEncryption`), and contain structured metadata keys pointing to `com.apple.wkms.*`.
2. **Premise**: Apple uses hybrid public-key encryption for key distribution.
   - **Step 1**: From Observation 2, `com.apple.wkms.fcs-response` carries `enc-request` (65-byte P-256 EC point) and `wrapped-key` (48-byte AES-GCM ciphertext).
   - **Step 2**: From Observation 3, Apple's public endpoint `https://wkms-public.apple.com/fcs-keys/<key_id>` returns the matching P-256 private key.
   - **Step 3**: Applying RFC 9180 HPKE decapsulation (`DHKEM(P-256, HKDF-SHA256)` + `HKDF-SHA256` + `AES-256-GCM`) derives the exact shared secret, decrypts the wrapped key, and recovers the 256-bit AES archive key.
3. **Premise**: The recovered keys are mathematically authentic.
   - **Step 1**: From Observation 4, using the recovered symmetric key to derive `mainKey` and `rootHdrKey` produces HMAC values matching the byte sequence in the file header (`HMAC match?: True`).
   - **Step 2**: The decrypted root header dimensions (8,562,671,616 bytes) match `OSDiskImageSize: 8166` in `BuildManifest.plist` exactly.
4. **Premise**: Offline decryption without Apple-held keys is infeasible.
   - **Step 1**: AES-256 search space ($2^{256}$) and NIST P-256 discrete log difficulty ($\approx 2^{128}$ operations) ensure that without Apple's published FCS key or device runtime dumping, decryption is mathematically impossible.
5. **Premise**: The restore ramdisk provides an immediate unencrypted window into tvOS 26.6.1 UI and system architecture.
   - **Step 1**: From Observation 5, the ramdisks lack AEA wrapping and contain raw APFS partitions with resolution-tiered `ProgressUI` assets and modern Swift framework stacks.

---

## 3. Caveats

1. **Full RootFS Volume Decompression**: The 8.56 GB uncompressed rootfs was not expanded to disk during this investigation turn to prevent disk exhaustion and maintain strict read-only survey scope, but the exact symmetric keys and decompression algorithms (`LZFSE` clusters) are fully documented.
2. **Firmware Execution Boundary**: Strictly adhered to R7; no ARM64 firmware binaries were executed on the Linux host.
3. **Hardware-bound KBAGs**: Early bootloaders (`LLB`, `iBoot`, `SEP`) utilize hardware-fused GID keys on A8 silicon which cannot be unwrapped over the network.

---

## 4. Conclusion

1. Apple's AEA container architecture in tvOS 26.6.1 combines `AEA1` profile 1 symmetric archive encryption with RFC 9180 HPKE key management.
2. For this production build (`23L781`), Apple published the FCS private key on `wkms-public.apple.com`, enabling full recovery of both RootFS and Recovery OS symmetric encryption keys.
3. The restore ramdisk is completely unencrypted, providing immediate recovery pathways for restore UI graphics (`ProgressUI` at 1080p, 4K, 1x, 2x), 112 system plists, 38+ language localization suites, and 76 system frameworks.
4. Compared to tvOS 13.4.8, tvOS 26.6.1 has evolved from an Objective-C-centric shell to a modern Swift-first architecture incorporating Sealed System Volumes (SSV), `DiskImages2`, and multi-resolution TV rendering pipelines.

---

## 5. Verification Method

To independently verify all findings and cryptographic derivations:

1. **Verify AEA Magic and Headers**:
   ```bash
   python3 -c "
   with open('/home/prem/Projects/AppleTV/AppleTV5,3_26.6.1_23L781_Restore/094-98312-089.dmg.aea', 'rb') as f:
       d = f.read(16)
   assert d[:4] == b'AEA1'
   assert int.from_bytes(d[4:8], 'little') == 1
   print('AEA1 Header Verified!')
   "
   ```

2. **Verify HPKE Key Recovery & Root Header HMAC**:
   Run the Python verification script in section 2.4 of `survey_aea_ui_report.md`:
   - Validates that HPKE AES-GCM decapsulation recovers `ca0d1a3eb45cdb15b15babced612a5d37914299f5d5d141d488ddccb40cda496`.
   - Validates that HKDF `AEA_RHEK` derivation produces `HMAC match?: True`.

3. **Verify Unencrypted Ramdisk APFS Partition**:
   ```bash
   python3 -c "
   with open('/home/prem/Projects/AppleTV/AppleTV5,3_26.6.1_23L781_Restore/094-97800-089.dmg', 'rb') as f:
       f.seek(59)
       assert f.read(4) == b'NXSB'
   print('APFS NXSB Superblock Verified!')
   "
   ```
