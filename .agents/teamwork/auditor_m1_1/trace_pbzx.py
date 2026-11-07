#!/usr/bin/env python3
import os
import struct
import lzma
import hashlib

def trace_pbzx_chunk():
    payload_file = '/home/prem/Projects/AppleTV/8988ef3518b1f20f95c66d03be3c15eb4e1be2a0/AssetData/payloadv2/payload.000'
    print(f"Inspecting {payload_file}...")
    with open(payload_file, 'rb') as f:
        magic = f.read(4)
        print(f"Magic: {magic}")
        assert magic == b'pbzx', f"Invalid magic: {magic}"
        buf_size = struct.unpack('>Q', f.read(8))[0]
        print(f"Buffer size: {buf_size} ({buf_size / 1024 / 1024:.1f} MB)")
        
        chdr = f.read(16)
        dlen, clen = struct.unpack('>QQ', chdr)
        print(f"Chunk 0: dlen={dlen}, clen={clen}")
        cdata = f.read(clen)
        print(f"Read {len(cdata)} compressed bytes. XZ magic: {cdata[:6]}")
        assert cdata[:6] == b'\xfd7zXZ\x00', f"Invalid XZ magic: {cdata[:6]}"
        
        decompressed = lzma.decompress(cdata)
        print(f"Decompressed length: {len(decompressed)} (expected {dlen})")
        assert len(decompressed) == dlen, "Decompressed length mismatch!"

        # Inspect first record header
        hdr = decompressed[:30]
        rtype, fsize, mtime, flags, nlen, uid, gid, mode = struct.unpack('>HQQIHHHH', hdr)
        name = decompressed[30:30+nlen].decode('utf-8')
        print(f"First record: rtype=0x{rtype:04x}, fsize={fsize}, mtime={mtime}, flags={flags}, nlen={nlen}, uid={uid}, gid={gid}, mode={oct(mode)}")
        print(f"First record name: '{name}'")
        
        # Parse records in this chunk
        offset = 0
        record_idx = 0
        while offset + 30 <= len(decompressed) and record_idx < 15:
            hdr = decompressed[offset:offset+30]
            rtype, fsize, mtime, flags, nlen, uid, gid, mode = struct.unpack('>HQQIHHHH', hdr)
            offset += 30
            name = decompressed[offset:offset+nlen].decode('utf-8', errors='replace')
            offset += nlen
            print(f"  Record #{record_idx}: type=0x{rtype:04x} size={fsize:8d} mode={oct(mode)} name={name}")
            offset += fsize
            record_idx += 1

if __name__ == '__main__':
    trace_pbzx_chunk()
