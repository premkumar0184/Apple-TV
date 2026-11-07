# Handoff Report — Milestone IPSW-M1 Remediation Plan

**Agent**: `explorer_ipsw_m1_fix`  
**Archetype**: Explorer (Investigation & Synthesis)  
**Parent Orchestrator**: `dca65d9e-caea-4f60-93bd-b30c8fc70405`  
**Target Milestone**: IPSW-M1 Iteration 1 Review Remediation  
**Working Directory**: `/home/prem/Projects/AppleTV/.agents/teamwork/explorer_ipsw_m1_fix/`  
**Date**: 2026-11-06T21:58:00Z  

---

## 1. Observation

Direct empirical observations, measurements, line citations, and tool execution outputs:

### 1.1 Table 5.2 Discrepancies in `reports/IPSW_EXTRACTION_LEDGER.md`
- **Location**: `/home/prem/Projects/AppleTV/reports/IPSW_EXTRACTION_LEDGER.md`, lines 191–196:
  ```markdown
  191: | `usr/sbin/nvram` | 54,640 | Mach-O 64-bit arm64 | ff07711d957ba65df5d5c0e1189998248cb5e09f583f7a63529d486d30f789d2 | NVRAM Variable Management Tool |
  192: | `usr/sbin/ioreg` | 74,384 | Mach-O 64-bit arm64 | a906236b2cbb13658ebc31baec032906bbbf80fae3b6eb8bce5d57b1bc13e8e2 | I/O Kit Registry Inspector |
  193: | `sbin/mount_apfs` (target) | 204,800 | Mach-O 64-bit arm64 | ad833010f368f54cfdf755c3c0ef270e5b7c7b80dbfaee5d4ba512b9d072b225 | APFS Volume Mount Binary |
  194: | `sbin/fsck_apfs` (target) | 884,736 | Mach-O 64-bit arm64 | f08960f25f20f01b1935661d4a0a79caef81b5ff85eb3ee2a9ca18731b7d5ee7 | APFS Filesystem Consistency Checker |
  195: | `sbin/newfs_apfs` (target) | 286,720 | Mach-O 64-bit arm64 | 3ecf346b0a1d95db894aa72ae9eb2e0df401865a71eb677f5c71dbe438342db6 | APFS Filesystem Formatter |
  196: | `System/DriverKit/.../libswiftCore.dylib` | 7,639,536 | Mach-O 64-bit arm64 dylib | 8da318172d23a57f2e46648a49e1beec22bc304d35c54802bbb51e6178590ce5 | Swift 5.x DriverKit Core Runtime |
  ```
- **Physical Disk Measurements**:
  Executed `sha256sum` and `stat -c %s`:
  ```bash
  0e1cea414a30a260b67b9374978bcbe069542954480abff2608dff2ff6249d1b  extracted/ipsw/ramdisk_erase/usr/sbin/nvram (57,424 bytes)
  38ac5dea0d7481f6de124ec88a390c2eb1bbfb184075b9ee123210a36c19726c  extracted/ipsw/ramdisk_erase/usr/sbin/ioreg (75,072 bytes)
  ecd23b8f5c55f4a86bb1bcc062f1e7f3248450eb1263ae2065f5c5bcfbeb9e00  extracted/ipsw/ramdisk_erase/System/Library/Filesystems/apfs.fs/mount_apfs (72,912 bytes)
  4be481e681d2c555b3a91d293d57487f1694855a2358364cd6df496314e38355  extracted/ipsw/ramdisk_erase/System/Library/Filesystems/apfs.fs/fsck_apfs (561,536 bytes)
  d863028a0a01f90edb577d410917bc1a08086acf06126f26ab8ca1c12067e787  extracted/ipsw/ramdisk_erase/System/Library/Filesystems/apfs.fs/newfs_apfs (508,400 bytes)
  8da318172d23a57f2e46648a49e1beec22bc304d35c54802bbb51e6178590ce5  extracted/ipsw/ramdisk_erase/System/DriverKit/usr/lib/swift/libswiftCore.dylib (7,639,536 bytes)
  ```
  *(Crucial Verification Note: Reviewer `reviewer_ipsw_m1_2` correctly identified that `nvram` and `ioreg` had incorrect ledger entries, but the reviewer's handoff text contained a typo in the second half of the hexadecimal digests. Our direct cryptographic calculation on disk established the authentic, empirical values: `0e1cea...d1b` for `nvram` and `38ac5d...26c` for `ioreg`).*

### 1.2 Table 5.3 UI Asset Discrepancies in `reports/IPSW_EXTRACTION_LEDGER.md`
- **Location**: `/home/prem/Projects/AppleTV/reports/IPSW_EXTRACTION_LEDGER.md`, lines 202–209:
  The ledger documented theoretical uncompressed framebuffer calculations ($W \times H \times 4 + 44$) and assumed square iOS resolutions instead of true disk measurements:
  - `images-AppleTV-1080/applelogo.tga`: Recorded `262,188` (256×256) vs Actual disk: **`9,458` bytes, TGA (225×365 RGBA)**, SHA-256 `8326ee0a71555dbca5e5b43d5ce4e4efc338cb7595a3b405b2a8535e6c08d519`.
  - `images-AppleTV-2160/applelogo.tga`: Recorded `1,048,620` (512×512) vs Actual disk: **`23,222` bytes, TGA (450×730 RGBA)**, SHA-256 `044910aae1f0eaa0aa0a0b20022a692588a77c0197073ffbd2637f74d7f44f5a`.
  - `images-AppleTV/applelogo.png`: Recorded `2,789` (256×256) vs Actual disk: **`3,472` bytes, PNG (150×243 RGBA)**, SHA-256 `b71a97d4d788154878a4a7189aa33e7037ed46e19656039bf2df35554e7aa48c`.
  - `images-1x/applelogo.png`: Recorded `1,189` (128×128) vs Actual disk: **`7,281` bytes, PNG (96×160 RGBA)**, SHA-256 `62684d198df299411ecd0aac2293752d4f0611b549822ef54661c1d6858cde64`.
  - `images-2x/applelogo.png`: Recorded `2,789` (256×256) vs Actual disk: **`16,216` bytes, PNG (192×320 RGBA)**, SHA-256 `a1b7ee0d7cd01d1da3a26dc17a1211e8e057a340c801c19bf38aff01c5809cc4`.
  - `power-button-prompt.tga`: Recorded `12,582,956` vs Actual disk: **`169,162` bytes, TGA (1536×2048 RGBA)**, SHA-256 `473986a867afcc4c419ddd3bef74bd71f86364fd519f1b065a7537932ca38721`.
  - `disconnect-prompt.tga`: Recorded `12,582,956` vs Actual disk: **`171,849` bytes, TGA (1536×2048 RGBA)**, SHA-256 `e8523c3bf4a0cf88f73df24b4a2c79ac504f35e22edeca33e7c52f623291777c`.
  - `vision.pro.developer.strap-N301a.png`: Recorded `114,868` vs Actual disk: **`31,190` bytes, PNG (1024×1024 RGBA)**, SHA-256 `dfe2c789a7fcf8ca174dee87f42c67fb99cdf3a2e880fa5d6789c9485121763d`. Located at `System/Library/PrivateFrameworks/CoreAccessories.framework/vision.pro.developer.strap-N301a.png` (exclusive to `ramdisk_update`).

### 1.3 Test Suite Ledger Assertion Gap
- **Location**: `/home/prem/Projects/AppleTV/tests/test_ipsw_m1_integrity.py`, lines 170–194:
  `test_08_extraction_ledger` only asserts file presence and string inclusion (`self.assertIn("restored_external", ledger_text)`). It contains zero programmatic comparison of table rows (path, byte size, SHA-256) against the physical disk.

### 1.4 Absolute Symlink Anti-Pattern
- **Location**: 6 symlinks across the two ramdisks contain host-absolute paths:
  - `extracted/ipsw/ramdisk_erase/sbin/mount_hfs -> /home/prem/Projects/AppleTV/extracted/ipsw/ramdisk_erase/System/Library/Filesystems/hfs.fs/mount_hfs`
  - `extracted/ipsw/ramdisk_erase/sbin/fsck_hfs -> /home/prem/Projects/AppleTV/extracted/ipsw/ramdisk_erase/System/Library/Filesystems/hfs.fs/fsck_hfs`
  - `extracted/ipsw/ramdisk_erase/sbin/newfs_hfs -> /home/prem/Projects/AppleTV/extracted/ipsw/ramdisk_erase/System/Library/Filesystems/hfs.fs/newfs_hfs`
  - `extracted/ipsw/ramdisk_update/sbin/mount_hfs -> /home/prem/Projects/AppleTV/extracted/ipsw/ramdisk_update/System/Library/Filesystems/hfs.fs/mount_hfs`
  - `extracted/ipsw/ramdisk_update/sbin/fsck_hfs -> /home/prem/Projects/AppleTV/extracted/ipsw/ramdisk_update/System/Library/Filesystems/hfs.fs/fsck_hfs`
  - `extracted/ipsw/ramdisk_update/sbin/newfs_hfs -> /home/prem/Projects/AppleTV/extracted/ipsw/ramdisk_update/System/Library/Filesystems/hfs.fs/newfs_hfs`
- **Adversarial Test Dependency**:
  `tests/test_ipsw_m1_adversarial.py:test_03_audit_absolute_host_symlink_anti_pattern` (lines 280–284) currently asserts `self.assertEqual(len(host_absolute_links), 6)`. When remediated, this test must be updated to assert `0`.

---

## 2. Logic Chain

1. **Empirical Ground Truth Over Inference**:
   - The attestation deliverable `reports/IPSW_EXTRACTION_LEDGER.md` is the authoritative record of physical artifacts extracted from the IPSW.
   - For Sections 1, 3, and 4, the recorded hashes and byte counts match disk files bit-for-bit (confirmed by our `audit_ledger.py` execution across all 26 archive members and 8 extracted firmware/kernel binaries).
   - In Table 5.2, 5 entries contained unverified or synthetic entries. In Table 5.3, theoretical uncompressed bitmap buffer mathematics were recorded instead of physical on-disk file sizes.
   - Re-measuring every single artifact on disk using `hashlib.sha256()` and `os.path.getsize()` produces an airtight empirical dataset.

2. **Unambiguous Table Path Formatting**:
   - In Table 5.2, rows for `mount_apfs`, `fsck_apfs`, and `newfs_apfs` had `(target)` outside backticks, which prevented automated regex parsers from matching the columns.
   - Using canonical target paths in the first column (`System/Library/Filesystems/apfs.fs/mount_apfs`) and noting `(Target of sbin/mount_apfs)` in the description column allows automated parsers to cleanly resolve the path against the filesystem while preserving human clarity.
   - Expanding `System/DriverKit/.../libswiftCore.dylib` to `System/DriverKit/usr/lib/swift/libswiftCore.dylib` removes wildcard ambiguity.

3. **Cryptographic Parity for UI Graphics Table**:
   - Adding a `SHA-256 Digest` column to Table 5.3 brings it to the exact same cryptographic standard as Tables 3, 4, and 5.2.
   - Every single entry in the ledger is now covered by a SHA-256 digest and on-disk byte count.

4. **Permanent Automated Verification Gate**:
   - Implementing `test_09_extraction_ledger_veracity` in `tests/test_ipsw_m1_integrity.py` ensures that CI programmatically checks all 56 markdown table rows against physical disk files.
   - We verified this logic using `test_proposed_ledger.py`, which parsed the simulated updated ledger and achieved **56/56 passing rows (0 mismatches, 0 errors)**.

5. **Symlink Portability & Test Co-Adaptation**:
   - Converting the 6 legacy absolute symlinks to relative targets (`../System/Library/Filesystems/hfs.fs/<name>`) eliminates workstation-specific `/home/prem/...` paths.
   - Updating `tests/test_ipsw_m1_adversarial.py:test_03_audit_absolute_host_symlink_anti_pattern` from expecting 6 absolute links to asserting 0 ensures the test suite accurately reflects the hardened state.

---

## 3. Caveats

- **Host Safety**: Strictly maintained 0 executions of ARM64 firmware binaries on host Linux x86_64 system. All measurements performed via static read operations (`stat`, `sha256sum`, Python `Pillow`).
- **Reviewer Digest Correction**: The incoming dispatch and reviewer report contained a typographical discrepancy in the second half of the SHA-256 hashes for `nvram` and `ioreg`. The true values were independently calculated and confirmed by running `sha256sum` directly on disk.
- **Scope Discipline**: As an explorer agent, no source code or report modifications were committed to the workspace root; all patches, scripts, and prototypes were staged in `.agents/teamwork/explorer_ipsw_m1_fix/` for the implementing agent.

---

## 4. Conclusion & Actionable Remediation Plan

The remediation plan consists of five concrete, verified steps:

### Step 1: Apply Ledger Patch (`reports/IPSW_EXTRACTION_LEDGER.md`)
Apply patch file `/home/prem/Projects/AppleTV/.agents/teamwork/explorer_ipsw_m1_fix/ledger_patch.diff`:
- Replace Table 5.2 lines 186–196 with authentic physical sizes, authentic SHA-256 digests, and canonical relative paths.
- Replace Table 5.3 lines 201–209 with exact physical file sizes, authentic image dimensions, and SHA-256 digests.

#### Complete Replacement Table 5.2
```markdown
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
```

#### Complete Replacement Table 5.3
```markdown
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
```

### Step 2: Implement Automated Table Veracity Test in `tests/test_ipsw_m1_integrity.py`
Apply patch `/home/prem/Projects/AppleTV/.agents/teamwork/explorer_ipsw_m1_fix/tests_patch.diff` to add `test_09_extraction_ledger_veracity` to `TestIPSWExtractionM1`. This method:
- Parses all markdown tables formatted with `| `path` | size | ... | `sha256` |`.
- Automatically resolves paths across project root, `extracted/ipsw/ramdisk_erase/`, `extracted/ipsw/ramdisk_update/`, and `AppleTV5,3_26.6.1_23L781_Restore/`.
- Validates that `os.path.getsize(file) == expected_size` and `hashlib.sha256(data).hexdigest() == recorded_hash` for every single entry (56 total audited entries).
- Asserts that zero mismatches exist.

### Step 3: Remediate 6 Legacy HFS Symlinks
Execute script `/home/prem/Projects/AppleTV/.agents/teamwork/explorer_ipsw_m1_fix/symlink_fix.sh`:
```bash
ln -sfn ../System/Library/Filesystems/hfs.fs/mount_hfs extracted/ipsw/ramdisk_erase/sbin/mount_hfs
ln -sfn ../System/Library/Filesystems/hfs.fs/fsck_hfs extracted/ipsw/ramdisk_erase/sbin/fsck_hfs
ln -sfn ../System/Library/Filesystems/hfs.fs/newfs_hfs extracted/ipsw/ramdisk_erase/sbin/newfs_hfs

ln -sfn ../System/Library/Filesystems/hfs.fs/mount_hfs extracted/ipsw/ramdisk_update/sbin/mount_hfs
ln -sfn ../System/Library/Filesystems/hfs.fs/fsck_hfs extracted/ipsw/ramdisk_update/sbin/fsck_hfs
ln -sfn ../System/Library/Filesystems/hfs.fs/newfs_hfs extracted/ipsw/ramdisk_update/sbin/newfs_hfs
```

### Step 4: Update Adversarial Test Assertion in `tests/test_ipsw_m1_adversarial.py`
Apply patch `/home/prem/Projects/AppleTV/.agents/teamwork/explorer_ipsw_m1_fix/adversarial_test_patch.diff`:
- Update `test_03_audit_absolute_host_symlink_anti_pattern` line 282 from `self.assertEqual(len(host_absolute_links), 6)` to `self.assertEqual(len(host_absolute_links), 0)`.

### Step 5: Verification & Re-Review Signoff
Run the full test suite and verify that all 51 tests pass with 0 failures and 0 errors.

---

## 5. Verification Method

To independently verify this entire remediation plan before and after implementation:

```bash
# 1. Run the comprehensive audit script (proves true sizes and digests for all ledger files):
python3 .agents/teamwork/explorer_ipsw_m1_fix/audit_ledger.py

# 2. Run the proposed ledger validation script (proves 56/56 table rows achieve 100% match):
python3 .agents/teamwork/explorer_ipsw_m1_fix/test_proposed_ledger.py

# 3. Verify symlink target paths resolve without broken links:
bash .agents/teamwork/explorer_ipsw_m1_fix/symlink_fix.sh

# 4. Run the complete repository test suite:
python3 -m unittest discover tests -v
# Invalidation condition: Any failure, assertion error, or non-zero exit code
```
