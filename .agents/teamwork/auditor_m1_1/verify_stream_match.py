#!/usr/bin/env python3
import os
import struct
import lzma
import hashlib

def stream_pbzx(file_path):
    with open(file_path, "rb") as fp:
        magic = fp.read(4)
        if magic != b"pbzx":
            raise ValueError(f"Invalid PBZX magic in {file_path}: {magic}")
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

def find_and_compare_file(payload_path, target_rel_path, extracted_full_path):
    print(f"Searching for '{target_rel_path}' in {payload_path}...")
    sb = StreamBuffer(stream_pbzx(payload_path))
    found = False
    while True:
        hdr = sb.read(30)
        if len(hdr) < 30:
            break
        rtype, fsize, mtime, flags, nlen, uid, gid, mode = struct.unpack(">HQQIHHHH", hdr)
        name = sb.read(nlen).decode("utf-8", errors="replace")
        
        if name == target_rel_path:
            found = True
            print(f"FOUND {name} in {payload_path}! Type: 0x{rtype:04x}, Size: {fsize}")
            content = sb.read(fsize)
            assert len(content) == fsize, f"Read {len(content)} != fsize {fsize}"
            
            # Compute hash of stream content
            stream_hash = hashlib.sha256(content).hexdigest()
            print(f"Decompressed stream SHA-256: {stream_hash}")
            
            # Read extracted file from disk
            with open(extracted_full_path, "rb") as ef:
                extracted_content = ef.read()
            extracted_hash = hashlib.sha256(extracted_content).hexdigest()
            print(f"Extracted file on disk SHA-256: {extracted_hash}")
            
            assert stream_hash == extracted_hash, "STREAM HASH DOES NOT MATCH EXTRACTED FILE!"
            assert content == extracted_content, "CONTENT BYTES DO NOT MATCH EXACTLY!"
            print(f"MATCH CONFIRMED! 100% exact byte-for-byte identity verified for {target_rel_path}!")
            break
        else:
            if rtype == 0x1001:
                sb.skip(fsize)

    if not found:
        print(f"Not found in {payload_path}.")
    return found

if __name__ == '__main__':
    # Test 1: PkgInfo in payload.000
    find_and_compare_file(
        '/home/prem/Projects/AppleTV/8988ef3518b1f20f95c66d03be3c15eb4e1be2a0/AssetData/payloadv2/payload.000',
        'Applications/AppStore.app/PkgInfo',
        '/home/prem/Projects/AppleTV/extracted/rootfs/Applications/AppStore.app/PkgInfo'
    )
    # Test 2: Info.plist in payload.000
    find_and_compare_file(
        '/home/prem/Projects/AppleTV/8988ef3518b1f20f95c66d03be3c15eb4e1be2a0/AssetData/payloadv2/payload.000',
        'Applications/AppStore.app/Info.plist',
        '/home/prem/Projects/AppleTV/extracted/rootfs/Applications/AppStore.app/Info.plist'
    )
