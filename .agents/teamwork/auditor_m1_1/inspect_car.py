#!/usr/bin/env python3
import os
import struct

def inspect_car(path):
    print(f"\n--- Inspecting Asset Catalog: {path} ---")
    size = os.path.getsize(path)
    print(f"File size: {size:,} bytes")
    with open(path, 'rb') as f:
        magic = f.read(8)
    print(f"Magic: {magic} (expected b'BOMStore')")
    assert magic == b'BOMStore', f"Invalid Asset Catalog magic: {magic}"
    with open(path, 'rb') as f:
        f.seek(8)
        version, num_blocks, index_offset, index_len = struct.unpack('>IIII', f.read(16))
    print(f"BOMStore header: version={version}, blocks={num_blocks}, index_offset={index_offset}, index_len={index_len}")

if __name__ == '__main__':
    inspect_car('/home/prem/Projects/AppleTV/extracted/rootfs/System/Library/CoreServices/CoreGlyphs.bundle/Assets.car')
    inspect_car('/home/prem/Projects/AppleTV/extracted/rootfs/Applications/HeadBoard.app/Assets.car')
    inspect_car('/home/prem/Projects/AppleTV/extracted/rootfs/Applications/PineBoard.app/Assets.car')
