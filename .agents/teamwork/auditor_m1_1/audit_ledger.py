#!/usr/bin/env python3
import re
import os
import hashlib

def main():
    ledger_path = '/home/prem/Projects/AppleTV/reports/EXTRACTION_LEDGER.md'
    with open(ledger_path, 'r', encoding='utf-8') as f:
        ledger = f.read()

    # Pattern for table rows:
    # | `path` | size | format/desc | `hash` |
    # or
    # | `path` | size | `hash` |
    pattern4 = re.compile(r'\|\s*`([^`]+)`\s*\|\s*([0-9,]+)\s*\|[^|]+\|\s*`([a-f0-9]{64})`\s*\|')
    pattern3 = re.compile(r'\|\s*`([^`]+)`\s*\|\s*([0-9,]+)\s*\|\s*`([a-f0-9]{64})`\s*\|')

    entries = pattern4.findall(ledger) + pattern3.findall(ledger)
    print(f'Total matched entries in ledger: {len(entries)}')

    mismatches = []
    missing = []
    verified = 0

    for path, size_str, expected_hash in entries:
        full_path = os.path.join('/home/prem/Projects/AppleTV', path)
        if not os.path.exists(full_path):
            missing.append(path)
            continue
        expected_size = int(size_str.replace(',', ''))
        actual_size = os.path.getsize(full_path)
        if actual_size != expected_size:
            mismatches.append((path, 'size', expected_size, actual_size))
            continue
        h = hashlib.sha256()
        with open(full_path, 'rb') as fp:
            while chunk := fp.read(1048576):
                h.update(chunk)
        actual_hash = h.hexdigest()
        if actual_hash != expected_hash:
            mismatches.append((path, 'hash', expected_hash, actual_hash))
            continue
        verified += 1

    print(f'Successfully verified: {verified}')
    print(f'Missing files: {len(missing)}')
    if missing:
        for m in missing[:10]:
            print(f'  MISSING: {m}')
    print(f'Mismatches: {len(mismatches)}')
    if mismatches:
        for mm in mismatches[:10]:
            print(f'  MISMATCH: {mm}')

    if not missing and not mismatches and verified > 0:
        print('VERDICT_PRE: ALL LEDGER ENTRIES 100% CRYPTOGRAPHICALLY AND SIZES VERIFIED')

if __name__ == '__main__':
    main()
