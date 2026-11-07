#!/usr/bin/env python3
import os
import hashlib
import re
from PIL import Image

PROJECT_ROOT = '/home/prem/Projects/AppleTV'
ledger_path = os.path.join(PROJECT_ROOT, 'reports/IPSW_EXTRACTION_LEDGER.md')

with open(ledger_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Audit Table 5.2
t52_match = re.search(r'### 5\.2 Key Binaries & System Daemons Recovered\s*\n\n(.*?)(?=\n###|\n---)', text, re.DOTALL)
assert t52_match, 'Table 5.2 not found!'
t52_content = t52_match.group(1)

print('=== AUDITING TABLE 5.2 ===')
row_pat = re.compile(r'\|\s*`([^`]+)`\s*\|\s*([0-9,]+)\s*\|\s*([^|]+)\|\s*`([0-9a-f]{64})`\s*\|\s*([^|]+)\|')
rows_52 = row_pat.findall(t52_content)
print(f'Found {len(rows_52)} rows in Table 5.2')
assert len(rows_52) == 14, f'Expected 14 rows in Table 5.2, found {len(rows_52)}'

for rel_path, size_str, arch, recorded_hash, role in rows_52:
    expected_size = int(size_str.replace(',', ''))
    candidates = [
        os.path.join(PROJECT_ROOT, 'extracted/ipsw/ramdisk_erase', rel_path),
        os.path.join(PROJECT_ROOT, 'extracted/ipsw/ramdisk_update', rel_path),
        os.path.join(PROJECT_ROOT, rel_path),
    ]
    found = None
    for cand in candidates:
        if os.path.exists(cand):
            found = cand
            break
    assert found is not None, f'File not found: {rel_path}'
    real_size = os.path.getsize(found)
    with open(found, 'rb') as fp:
        real_hash = hashlib.sha256(fp.read()).hexdigest()
    
    size_ok = (real_size == expected_size)
    hash_ok = (real_hash == recorded_hash)
    print(f'{rel_path}:')
    print(f'  Size: real={real_size:,} vs ledger={expected_size:,} -> {size_ok}')
    print(f'  Hash: real={real_hash} vs ledger={recorded_hash} -> {hash_ok}')
    assert size_ok, f'Size mismatch for {rel_path}: {real_size} != {expected_size}'
    assert hash_ok, f'Hash mismatch for {rel_path}: {real_hash} != {recorded_hash}'

# 2. Audit Table 5.3
print('\n=== AUDITING TABLE 5.3 ===')
t53_match = re.search(r'### 5\.3 Recovered UI Graphics & Multi-Resolution Assets\s*\n\n(.*?)(?=\n###|\n---)', text, re.DOTALL)
assert t53_match, 'Table 5.3 not found!'
t53_content = t53_match.group(1)

rows_53 = row_pat.findall(t53_content)
print(f'Found {len(rows_53)} rows in Table 5.3')
assert len(rows_53) == 8, f'Expected 8 rows in Table 5.3, found {len(rows_53)}'

for rel_path, size_str, fmt_dims, recorded_hash, desc in rows_53:
    expected_size = int(size_str.replace(',', ''))
    candidates = [
        os.path.join(PROJECT_ROOT, 'extracted/ipsw/ramdisk_erase', rel_path),
        os.path.join(PROJECT_ROOT, 'extracted/ipsw/ramdisk_update', rel_path),
        os.path.join(PROJECT_ROOT, rel_path),
    ]
    found = None
    for cand in candidates:
        if os.path.exists(cand):
            found = cand
            break
    assert found is not None, f'File not found: {rel_path}'
    real_size = os.path.getsize(found)
    with open(found, 'rb') as fp:
        real_hash = hashlib.sha256(fp.read()).hexdigest()
    
    size_ok = (real_size == expected_size)
    hash_ok = (real_hash == recorded_hash)
    
    img_info = ''
    try:
        with Image.open(found) as img:
            img_info = f'{img.format} {img.size} {img.mode}'
    except Exception as e:
        img_info = f'Error opening image: {e}'
        
    print(f'{rel_path}:')
    print(f'  Size: real={real_size:,} vs ledger={expected_size:,} -> {size_ok}')
    print(f'  Hash: real={real_hash} vs ledger={recorded_hash} -> {hash_ok}')
    print(f'  Image on disk: {img_info} | Ledger says: {fmt_dims.strip()}')
    assert size_ok, f'Size mismatch for {rel_path}: {real_size} != {expected_size}'
    assert hash_ok, f'Hash mismatch for {rel_path}: {real_hash} != {recorded_hash}'

# 3. Audit entire document: every table row with a size and sha256 hash
print('\n=== AUDITING ENTIRE LEDGER (ALL TABLES) ===')
all_rows_pattern = re.compile(r'\|\s*`([^`]+)`\s*\|\s*([0-9,]+)\s*\|.*?`([0-9a-f]{64})`\s*\|')
all_matches = all_rows_pattern.findall(text)
print(f'Found {len(all_matches)} rows with paths, sizes, and sha256 hashes across ledger.')

audit_failures = []
for rel_path, size_str, recorded_hash in all_matches:
    expected_size = int(size_str.replace(',', ''))
    candidates = [
        os.path.join(PROJECT_ROOT, rel_path),
        os.path.join(PROJECT_ROOT, 'extracted/ipsw/ramdisk_erase', rel_path),
        os.path.join(PROJECT_ROOT, 'extracted/ipsw/ramdisk_update', rel_path),
        os.path.join(PROJECT_ROOT, 'AppleTV5,3_26.6.1_23L781_Restore', rel_path),
    ]
    disk_file = None
    for cand in candidates:
        if os.path.exists(cand) and not os.path.isdir(cand):
            disk_file = cand
            break
    if disk_file is None:
        audit_failures.append(f'MISSING FILE: {rel_path}')
        continue
    actual_size = os.path.getsize(disk_file)
    if actual_size != expected_size:
        audit_failures.append(f'SIZE MISMATCH {rel_path}: actual {actual_size} != ledger {expected_size}')
        continue
    with open(disk_file, 'rb') as fp:
        actual_hash = hashlib.sha256(fp.read()).hexdigest()
    if actual_hash != recorded_hash:
        audit_failures.append(f'HASH MISMATCH {rel_path}: actual {actual_hash} != ledger {recorded_hash}')
        continue

print(f'Total ledger rows audited: {len(all_matches)}')
if audit_failures:
    print('AUDIT DISCREPANCIES:')
    for f in audit_failures:
        print('  -', f)
    raise SystemExit(1)
else:
    print('100% OF LEDGER ROWS MATCH EXACT ON-DISK ARTIFACT SIZES AND SHA-256 DIGESTS!')
