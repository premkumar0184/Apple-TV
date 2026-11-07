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

def find_dyld():
    target = "System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
    payload_dir = '/home/prem/Projects/AppleTV/8988ef3518b1f20f95c66d03be3c15eb4e1be2a0/AssetData/payloadv2'
    for pf in ["payload.004", "payload.010", "payload.024"]:
        pp = os.path.join(payload_dir, pf)
        if not os.path.exists(pp): continue
        sb = StreamBuffer(stream_pbzx(pp))
        while True:
            hdr = sb.read(30)
            if len(hdr) < 30:
                break
            rtype, fsize, mtime, flags, nlen, uid, gid, mode = struct.unpack(">HQQIHHHH", hdr)
            name = sb.read(nlen).decode("utf-8", errors="replace")
            if name == target:
                print(f"[FOUND] {name} in {pf}! Size: {fsize}")
                # check first 64 bytes
                head_bytes = sb.read(64)
                print(f"Header: {head_bytes[:16]}")
                disk_path = "/home/prem/Projects/AppleTV/extracted/dyld_cache/dyld_shared_cache_arm64"
                with open(disk_path, "rb") as df:
                    disk_head = df.read(64)
                assert head_bytes == disk_head, "dyld cache header mismatch!"
                print("Header matches disk byte-for-byte!")
                return
            else:
                if rtype == 0x1001:
                    sb.skip(fsize)

if __name__ == '__main__':
    find_dyld()
