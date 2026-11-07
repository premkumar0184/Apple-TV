#!/usr/bin/env python3
import os
import struct
import hashlib

def verify_kernelcache():
    raw_path = '/home/prem/Projects/AppleTV/raw/firmware/kernelcache.release.j105a'
    extracted_path = '/home/prem/Projects/AppleTV/extracted/kernel/kernelcache.macho'
    
    with open(raw_path, 'rb') as f:
        raw_data = f.read()
    
    print(f"Raw kernelcache IM4P size: {len(raw_data)} bytes")
    # ASN.1 DER sequence check
    print(f"First 16 bytes: {raw_data[:16]}")
    # Search for 'bvx2' (LZFSE compressed payload) or IM4P tag 'krnl'
    krnl_idx = raw_data.find(b'krnl')
    print(f"Index of 'krnl' tag: {krnl_idx}")
    bvx2_idx = raw_data.find(b'bvx2')
    print(f"Index of 'bvx2' tag: {bvx2_idx}")
    
    # Check if lzfse is installed or decompress
    try:
        import lzfse
        has_lzfse = True
    except ImportError:
        has_lzfse = False
    print(f"Python lzfse available: {has_lzfse}")
    
    if has_lzfse and bvx2_idx != -1:
        decompressed = lzfse.decompress(raw_data[bvx2_idx:])
        print(f"Decompressed size: {len(decompressed)} bytes")
        h_decomp = hashlib.sha256(decompressed).hexdigest()
        print(f"Decompressed SHA-256: {h_decomp}")
        
        with open(extracted_path, 'rb') as f:
            disk_data = f.read()
        h_disk = hashlib.sha256(disk_data).hexdigest()
        print(f"Disk kernelcache SHA-256: {h_disk}")
        assert h_decomp == h_disk, "Kernelcache decompressed hash does not match disk!"
        print("EXACT MATCH: kernelcache.macho was genuinely decompressed from raw IM4P container!")
    else:
        # Check disk kernelcache directly
        with open(extracted_path, 'rb') as f:
            disk_data = f.read()
        print(f"Extracted kernelcache size: {len(disk_data)} bytes")
        u32 = struct.unpack('<I', disk_data[:4])[0]
        print(f"Magic: 0x{u32:08x} (expected 0xfeedfacf for 64-bit Mach-O)")
        assert u32 == 0xfeedfacf, "Invalid Mach-O magic!"
        h_disk = hashlib.sha256(disk_data).hexdigest()
        print(f"Disk SHA-256: {h_disk}")
        assert h_disk == 'df0d622ace9a648f3de12c1f2c003360f4048f1024a0a074cc28916e1ad5afe3'

if __name__ == '__main__':
    verify_kernelcache()
