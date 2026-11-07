#!/usr/bin/env python3
import os
import struct
import lzma
import hashlib

def stream_pbzx(file_path):
    with open(file_path, "rb") as fp:
        magic = fp.read(4)
        if magic != b"pbzx":
            return
        buf_size = struct.unpack(">Q", fp.read(8))[0]
        while True:
            chdr = fp.read(16)
            if len(chdr) < 16:
                break
            dlen, clen = struct.unpack(">QQ", chdr)
            cdata = fp.read(clen)
            if len(cdata) < clen:
                break
            if dlen == clen:
                yield cdata
            else:
                yield lzma.decompress(cdata)

class StreamBuffer:
    def __init__(self, gen):
        self.gen = gen
        self.buf = bytearray()

    def read(self, n):
        while len(self.buf) < n:
            try:
                self.buf.extend(next(self.gen))
            except StopIteration:
                break
        res = bytes(self.buf[:n])
        del self.buf[:n]
        return res

    def skip(self, n):
        remaining = n
        if len(self.buf) >= remaining:
            del self.buf[:remaining]
            return
        remaining -= len(self.buf)
        self.buf.clear()
        while remaining > 0:
            try:
                chunk = next(self.gen)
            except StopIteration:
                break
            if len(chunk) <= remaining:
                remaining -= len(chunk)
            else:
                self.buf.extend(chunk[remaining:])
                remaining = 0

def locate_key_targets():
    targets = {
        "Applications/PineBoard.app/PineBoard": "/home/prem/Projects/AppleTV/extracted/rootfs/Applications/PineBoard.app/PineBoard",
        "Applications/HeadBoard.app/HeadBoard": "/home/prem/Projects/AppleTV/extracted/rootfs/Applications/HeadBoard.app/HeadBoard",
        "Applications/PineBoard.app/Assets.car": "/home/prem/Projects/AppleTV/extracted/rootfs/Applications/PineBoard.app/Assets.car",
        "Applications/HeadBoard.app/Assets.car": "/home/prem/Projects/AppleTV/extracted/rootfs/Applications/HeadBoard.app/Assets.car",
    }
    payload_dir = '/home/prem/Projects/AppleTV/8988ef3518b1f20f95c66d03be3c15eb4e1be2a0/AssetData/payloadv2'
    payload_files = sorted([f for f in os.listdir(payload_dir) if f.startswith('payload.') and not f.endswith('.ecc')])
    
    found_targets = {}
    
    for pf in payload_files:
        pp = os.path.join(payload_dir, pf)
        sb = StreamBuffer(stream_pbzx(pp))
        while True:
            hdr = sb.read(30)
            if len(hdr) < 30:
                break
            rtype, fsize, mtime, flags, nlen, uid, gid, mode = struct.unpack(">HQQIHHHH", hdr)
            name = sb.read(nlen).decode("utf-8", errors="replace")
            if name in targets:
                print(f"[FOUND] {name} in {pf} (size={fsize})")
                # Stream the bytes and hash them
                h = hashlib.sha256()
                remaining = fsize
                while remaining > 0:
                    chunk = sb.read(min(remaining, 65536))
                    if not chunk:
                        break
                    h.update(chunk)
                    remaining -= len(chunk)
                stream_hash = h.hexdigest()
                disk_path = targets[name]
                dh = hashlib.sha256(open(disk_path, 'rb').read()).hexdigest()
                print(f"   Stream SHA-256: {stream_hash}")
                print(f"   Disk SHA-256:   {dh}")
                assert stream_hash == dh, f"MISMATCH for {name}!"
                print(f"   VERIFIED: Exact byte match!")
                found_targets[name] = pf
            else:
                if rtype == 0x1001:
                    sb.skip(fsize)
        if len(found_targets) == len(targets):
            break

if __name__ == '__main__':
    locate_key_targets()
