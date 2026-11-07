#!/usr/bin/env bash
# Symlink Remediation Script
# Converts 6 host-absolute HFS symlinks in restore ramdisks into relative targets.

set -euo pipefail

PROJECT_ROOT="/home/prem/Projects/AppleTV"
cd "$PROJECT_ROOT"

echo "Remediating ramdisk_erase sbin symlinks..."
ln -sfn ../System/Library/Filesystems/hfs.fs/mount_hfs extracted/ipsw/ramdisk_erase/sbin/mount_hfs
ln -sfn ../System/Library/Filesystems/hfs.fs/fsck_hfs extracted/ipsw/ramdisk_erase/sbin/fsck_hfs
ln -sfn ../System/Library/Filesystems/hfs.fs/newfs_hfs extracted/ipsw/ramdisk_erase/sbin/newfs_hfs

echo "Remediating ramdisk_update sbin symlinks..."
ln -sfn ../System/Library/Filesystems/hfs.fs/mount_hfs extracted/ipsw/ramdisk_update/sbin/mount_hfs
ln -sfn ../System/Library/Filesystems/hfs.fs/fsck_hfs extracted/ipsw/ramdisk_update/sbin/fsck_hfs
ln -sfn ../System/Library/Filesystems/hfs.fs/newfs_hfs extracted/ipsw/ramdisk_update/sbin/newfs_hfs

echo "Verifying symlinks are relative and valid..."
python3 -c "
import os
for rd in ['extracted/ipsw/ramdisk_erase', 'extracted/ipsw/ramdisk_update']:
    for name in ['mount_hfs', 'fsck_hfs', 'newfs_hfs']:
        p = os.path.join(rd, 'sbin', name)
        assert os.path.islink(p), f'Not a link: {p}'
        target = os.readlink(p)
        assert not os.path.isabs(target), f'Still absolute: {p} -> {target}'
        resolved = os.path.normpath(os.path.join(rd, 'sbin', target))
        assert os.path.exists(resolved), f'Target broken: {resolved}'
print('All 6 symlinks verified relative and resolving!')
"
