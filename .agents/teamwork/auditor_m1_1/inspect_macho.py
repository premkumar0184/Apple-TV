#!/usr/bin/env python3
import os
import struct

def inspect_macho(path):
    print(f"\n--- Inspecting {path} ---")
    size = os.path.getsize(path)
    print(f"File size: {size:,} bytes")
    with open(path, 'rb') as f:
        magic, cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags, reserved = struct.unpack('<IIIIIIII', f.read(32))
    print(f"Magic: 0x{magic:08x} (0xfeedfacf = Mach-O 64-bit)")
    assert magic == 0xfeedfacf, f"Invalid Mach-O magic: 0x{magic:08x}"
    print(f"CPU Type: 0x{cputype:08x} (0x0100000c = ARM64)")
    assert cputype == 0x0100000c, f"Invalid CPU type: 0x{cputype:08x}"
    print(f"CPU Subtype: 0x{cpusubtype:08x}")
    print(f"Filetype: 0x{filetype:08x} (0x2 = MH_EXECUTE)")
    print(f"Number of Load Commands: {ncmds}")
    print(f"Size of Load Commands: {sizeofcmds} bytes")
    
    # Read load commands to find segments and sections
    with open(path, 'rb') as f:
        f.seek(32)
        cmd_data = f.read(sizeofcmds)
    
    offset = 0
    segments = []
    dylibs = []
    for _ in range(ncmds):
        if offset + 8 > len(cmd_data):
            break
        cmd, cmdsize = struct.unpack('<II', cmd_data[offset:offset+8])
        if cmd == 0x19: # LC_SEGMENT_64
            segname = cmd_data[offset+8:offset+24].rstrip(b'\x00').decode('ascii', errors='ignore')
            vmaddr, vmsize, fileoff, filesize = struct.unpack('<QQQQ', cmd_data[offset+24:offset+56])
            nsects = struct.unpack('<I', cmd_data[offset+64:offset+68])[0]
            segments.append((segname, vmsize, filesize, nsects))
        elif cmd == 0x0c: # LC_LOAD_DYLIB
            name_offset = struct.unpack('<I', cmd_data[offset+8:offset+12])[0]
            dylib_name = cmd_data[offset+name_offset:offset+cmdsize].split(b'\x00')[0].decode('ascii', errors='ignore')
            dylibs.append(dylib_name)
        offset += cmdsize
    
    print(f"Segments found ({len(segments)}):")
    for s in segments:
        print(f"  {s[0]:16s}: VM size={s[1]:10,d}, File size={s[2]:10,d}, Sections={s[3]}")
    
    print(f"Linked dylibs ({len(dylibs)}):")
    for d in dylibs[:8]:
        print(f"  {d}")
    if len(dylibs) > 8:
        print(f"  ... and {len(dylibs)-8} more")

if __name__ == '__main__':
    inspect_macho('/home/prem/Projects/AppleTV/extracted/rootfs/Applications/PineBoard.app/PineBoard')
    inspect_macho('/home/prem/Projects/AppleTV/extracted/rootfs/Applications/HeadBoard.app/HeadBoard')
    inspect_macho('/home/prem/Projects/AppleTV/extracted/kernel/kernelcache.macho')
