#!/usr/bin/env python3
#
# writeusb -- write SAM disk image to USB floppy drive
#
# https://github.com/simonowen/writeusb

import argparse
import os
import re
import sys
from importlib.metadata import PackageNotFoundError, version
from mmap import mmap

from mgtdisklib import Disk, Image

if sys.platform == 'win32':
    import win32file as win32
    import winioctlcon
elif sys.platform == 'darwin':
    import fcntl
    import plistlib

loader_patches = {
    'SAMDOS2':
    [
     ('7B C6 08 5F D6 0A 38 06 28 04 5F',
      '-- -- -- -- -- 09 -- -- -- -- --'),
     ('C6 0A 05 F2 ?? ?? 47 CB 20 CB 21 0D',
      '-- 09 -- -- -- -- -- -- -- -- -- --'),
     ('C9 1C 7B FE 0B C0 1E 01 C9',
      '-- -- -- -- 0A -- -- -- --'),
     ('21 68 01 11 90 01 FE 28 28 0C FE 50 28 07 FE A8 28 03 21 88 04',
      '-- 44 01 -- 68 01 -- -- -- -- -- -- -- -- -- -- -- -- -- 14 04')
    ],

    'MasterDOS':
    [
     ('7B C6 08 5F D6 0B 3C 38 F2 5F',
      '-- -- -- -- -- 0A -- -- -- --'),
     ('87 90 21 00 00 06 0A 54 5F 19 10 FD',
      '-- -- -- -- -- -- 09 -- -- -- -- --'),
     ('4F 87 87 81 6F 26 00 29 79 FE 05 38 01 2B 29',
      '87 87 6F 60 29 FE 14 98 29 85 6F 8C 95 67 00'),
     ('7B FE 0B C0 1E 01 C9',
      '-- -- 0A -- -- -- --')
    ],

    'BDOS':
    [
     ('7B C6 08 5F D6 0A 38 06 28 04 5F',
      '-- -- -- -- -- 09 -- -- -- -- --'),
     ('C6 0A 05 F2 ?? ?? 47 CB 20 CB 21 0D',
      '-- 09 -- -- -- -- -- -- -- -- -- --'),
     ('C9 1C 7B FE 0B C0 1E 01 C9',
      '-- -- -- -- 0A -- -- -- --'),
    ],

    # These loaders follow the sector chain, so need no patching:

    'StarsAndSprites':
    [('3E 30 D3 FA 3E 7B 32 00 00 3A 00 00 FE 7B', '--')],

    'MNEMOtech':
    [('3E ?? 3C 08 01 ?? ?? ED 5B ?? ?? CB 7B', '--')],

    'D.T.A.':
    [('3E ?? 21 ?? ?? D3 FA 77 BE', '--')],

    'Pro-Dos-v2':
    [('ED 5F E6 07 D3 FE ED 78 CB 4F', '--')],

    'rom3reset':
    [('31 00 4F C3 C6 EB', '--')],
}


class Win32FloppyDevice:

    def __init__(self) -> None:
        dev = "\\\\.\\A:"
        if not os.path.exists(dev):
            raise RuntimeError('no floppy device found!')
        print(f'Opening floppy device ({dev})')
        self.h = win32.CreateFile(dev, win32.GENERIC_READ | win32.GENERIC_WRITE, win32.FILE_SHARE_READ | win32.FILE_SHARE_WRITE,
                                  None, win32.OPEN_EXISTING, win32.FILE_FLAG_NO_BUFFERING, 0)
        win32.DeviceIoControl(self.h.handle, winioctlcon.FSCTL_LOCK_VOLUME, None, 0, None)
        win32.DeviceIoControl(self.h.handle, winioctlcon.FSCTL_DISMOUNT_VOLUME, None, None)

    def close(self) -> None:
        self.h.close()

    def seek(self, pos: int) -> None:
        win32.SetFilePointer(self.h.handle, pos, win32.FILE_BEGIN)

    def read(self, len: int) -> bytes:
        _, data = win32.ReadFile(self.h.handle, len)
        return data if isinstance(data, bytes) else data.encode()  # always bytes!

    def write(self, data: bytes) -> int:
        length: int = win32.WriteFile(self.h.handle, data)[1]
        return length


class LinuxFloppyDevice:
    def __init__(self) -> None:
        devices = os.popen('lsblk --bytes --paths --raw --noheadings -o PATH,SIZE,TYPE').readlines()
        floppy_paths = [x.split()[0] for x in devices if '737280 disk' in x]
        if not floppy_paths:
            raise RuntimeError('no floppy device found!')
        print(f'Opening floppy device ({floppy_paths[0]})')
        flags = getattr(os, 'O_DIRECT', 0) | os.O_RDWR
        self.h = os.open(floppy_paths[0], flags)
        self.f = os.fdopen(self.h, 'rb+', 0)

    def seek(self, pos: int) -> None:
        os.lseek(self.h, pos, 0)

    def read(self, len: int) -> bytes:
        m = mmap(-1, len)
        self.f.readinto(m)
        return bytes(m)

    def write(self, data: bytes) -> int:
        m = mmap(-1, len(data))
        m.write(data)
        return os.write(self.h, m)


if sys.platform == 'darwin':
    class MacFloppyDevice(LinuxFloppyDevice):
        def __init__(self) -> None:
            plist_str = os.popen('diskutil list -plist').read()
            plist = plistlib.loads(bytes(plist_str, 'utf-8'))
            floppy_disks = [x['DeviceIdentifier'] for x in plist['AllDisksAndPartitions'] if x['Size'] == 737280]
            if not floppy_disks:
                raise RuntimeError('no floppy device found!')
            device = f'/dev/r{floppy_disks[0]}'
            print(f'Opening floppy device ({device})')
            self.h = os.open(device, os.O_RDWR)
            self.f = os.fdopen(self.h, 'rb+', 0)
            fcntl.fcntl(self.f, fcntl.F_NOCACHE, 1)


def patch_boot_loader(data: bytes) -> tuple[str | None, bytearray | None]:
    """Detect and patch known boot loaders"""
    for name, patches in loader_patches.items():
        offsets = []
        for search, _ in patches:
            pattern = ('\\x' + '\\x'.join(search.split(' '))).replace('\\x??', '.')
            match = re.search(bytes(pattern, 'ascii'), data, re.MULTILINE | re.DOTALL)
            if match:
                offsets.append(match.start())

        if len(offsets) == len(patches):
            patched_data = bytearray(data)
            for i, patch in enumerate(patches):
                for j, val in enumerate(patch[1].split(' ')):
                    if val != '--':
                        patched_data[offsets[i] + j] = int(val, 16)
            return name, patched_data
    return None, None


def used_tracks_set(image: Image, all: bool = False) -> set[int]:
    """Determine the set of tracks used by directory and files on the disk"""
    bam = Disk.from_image(image).bam()
    used_tracks = set()

    for head in range(2):
        for cyl in range(80):
            track = (head << 7) | cyl
            offset = (80 * head + cyl - 4) * image.spt
            if all or track <= 4 or bam[offset:offset+image.spt].any():
                used_tracks.add(track)

    return used_tracks


def pad_9_to_10_spt(image: Image) -> Image:
    """Add 10th sector to each track of a 9-sector image"""
    image10 = Image(spt=10)
    dir_tracks = Disk.from_image(image).dir_tracks
    dir_sector = (b'\x00\x20' + bytes(256 - 2)) * 2

    for head in range(2):
        for cyl in range(80):
            for sector in range(9):
                track = (head << 7) | cyl
                image10.write_sector(track, 1 + sector, image.read_sector(track, 1 + sector))

            padding = dir_sector if track < dir_tracks else bytes(512)
            image10.write_sector(track, 10, padding)

    return image10


def main() -> None:
    """Main program"""
    try:
        pkg_version = version('mgtwriteusb')
    except PackageNotFoundError:
        pkg_version = 'unknown'

    parser = argparse.ArgumentParser(description="Write SAM disk image to USB floppy drive")
    parser.add_argument('diskimage')
    parser.add_argument('-o', '--output', help="output to disk image file")
    parser.add_argument('-p', '--pad', default=False, action='store_true', help="pad output disk image to 10 sectors")
    parser.add_argument('-n', '--noverify', default=False, action='store_true', help="don't verify disk after writing")
    parser.add_argument('-f', '--force', default=False, action='store_true', help="write even if boot loader is unknown")
    parser.add_argument('-a', '--all', default=False, action='store_true', help="write all tracks, not just used tracks")
    parser.add_argument('-s', '--sniff', default=False, action='store_true', help="detect boot loader on source image")
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {pkg_version}')
    args = parser.parse_args()

    try:
        disk = Disk.open(args.diskimage)

        if disk.files and disk.files[0].is_bootable():
            name, patched_data = patch_boot_loader(disk.files[0].data)
            if name is not None:
                print(f"Detected {name} boot loader in {os.path.basename(args.diskimage)}")
                disk.files[0].data = patched_data

                # Remove Pang from StarsAndSprites so it fits
                if name == 'StarsAndSprites':
                    disk.delete('secret')
            elif not args.force:
                raise Exception(f"UNSUPPORTED BOOT LOADER ('{disk.files[0].name}') in {args.diskimage}.")
        else:
            disk.add_code_file(os.path.join(os.path.dirname(__file__), "samdos9"), at_index=0)
            args.pad = False

        if args.sniff:
            sys.exit(0)

        image = disk.to_image(spt=9)

        if args.output:
            if args.pad:
                image = pad_9_to_10_spt(image)

            print(f'Writing {image.spt}-sector image to {args.output}')
            image.save(args.output)
            sys.exit(0)

        if sys.platform == 'win32':
            f = Win32FloppyDevice()
        elif sys.platform == 'linux':
            f = LinuxFloppyDevice()
        elif sys.platform == 'darwin':
            f = MacFloppyDevice()
        else:
            raise Exception(f'Platform {sys.platform} is not currently supported.')

        used_tracks = sorted(used_tracks_set(image, args.all), key=lambda t: t & 0x7f)

        for i, track in enumerate(used_tracks):
            if track in used_tracks:
                track_data = b''.join(image.read_sector(track, 1 + sector) for sector in range(9))
                f.seek(image.sector_offset(track, 1))
                f.write(track_data)
            sys.stdout.write(f'\rWriting... {int(i*100/(len(used_tracks)-1))}%')
            sys.stdout.flush()

        if not args.noverify:
            print('')
            for i, track in enumerate(used_tracks):
                track_data = b''.join(image.read_sector(track, 1 + sector) for sector in range(9))
                f.seek(image.sector_offset(track, 1))
                if f.read(len(track_data)) != track_data:
                    raise RuntimeError(f'data mismatch on track {track}')
                sys.stdout.write(f'\rVerifying... {int(i*100/(len(used_tracks)-1))}%')
                sys.stdout.flush()
        del f
        print("\nDone.")

    except KeyboardInterrupt:
        pass
    except Exception as e:
        sys.exit(f'error: {e}')


if __name__ == "__main__":
    main()
