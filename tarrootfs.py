#!/usr/bin/env python
import argparse
import grp
import os
import pwd
import re
import sys
import tarfile


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('output', help='.tar.bz2 output file')

    args = parser.parse_args()

    script_path = os.path.dirname(os.path.realpath(sys.argv[0]))

    # exclude these files
    exclude_patterns = {
        ".*/.gitkeep$"
    }

    # build up permissions filter map
    perm_map = { }
    r = re.compile(r"^(\d+) (\d+) (\d+) (.+)$")
    for line in open(os.path.join(script_path, "rootfs.perms"), mode="rt").readlines():
        m = r.match(line)
        if m:
            perm_map[m.group(4)] = {
                "mode": int(m.group(1), 8),
                "uid": int(m.group(2)),
                "gid": int(m.group(3))
            }

    # pull in uid/gid mappings (/etc/passwd, /etc/group) from rootfs
    def read_passwd(path):
        out = { }
        r = re.compile(r"^([^:]+):([^:]+):(\d+)")
        for line in open(path, mode="rt").readlines():
            m = r.match(line)
            if m:
                out[int(m.group(3))] = m.group(1)
        return out
    uid_map = read_passwd(os.path.join(script_path, "rootfs/etc/passwd"))
    gid_map = read_passwd(os.path.join(script_path, "rootfs/etc/group"))

    # output tar
    tar_root = tarfile.open(args.output, mode='w:bz2')

    # start with /dev
    tar_dev = tarfile.open(os.path.join(script_path, "rootfs_dev.tar.bz2"), mode='r')
    for tarinfo in tar_dev:
        tar_root.addfile(tarinfo)
    tar_dev.close()


    def add_filter(tarinfo):
        for k in exclude_patterns:
            if re.match(k, tarinfo.name):
                return None

        if not tarinfo.name in perm_map:
            print("Missing permissions for {}".format(tarinfo.name))
        else:
            p = perm_map[tarinfo.name]
            tarinfo.mode = p["mode"]
            tarinfo.uid = p["uid"]
            tarinfo.uname = uid_map[tarinfo.uid]
            tarinfo.gid = p["gid"]
            tarinfo.gname = gid_map[tarinfo.gid]

        return tarinfo

    os.chdir(os.path.join(script_path, "rootfs"))
    for entries in os.listdir(os.path.join(script_path, "rootfs")):
        tar_root.add(entries, filter=add_filter)

    # additional packages
    package_dst = "usr/local"
    for dirpath, dirnames, filenames in os.walk(os.path.join(script_path, "packages")):
        for filename in filenames:
            # strip off extension
            ext = os.path.splitext(filename)
            if ext[1] not in [".bz2", ".gz"]:
                continue
            pre = os.path.splitext(ext[0])
            if pre[1] != ".tar":
                print("Skipping unsupported package '{}'".format(filename))
                continue
            pre = pre[0] + '/'  # <- packagename without .tar extension
            ext = ext[1]  # <- bz2, gz

            # explore the tar
            tar_package = tarfile.open(
                os.path.join(dirpath, filename),
                mode='r'
            )
            for tarinfo in tar_package:
                dst = tarinfo.name
                # remove top level directory with same name as the package
                if dst + "/" == pre:
                    continue
                elif dst.startswith(pre):
                    dst = dst[len(pre):]
                
                # adding to package_dst
                dst = os.path.join(package_dst, dst)

                # skip top level files
                if tarinfo.isfile() and package_dst == os.path.dirname(dst):
                    print("Package '{}' skipping '{}'".format(filename, tarinfo.name))
                    continue

                # remap unknown uid/gid's to root
                if tarinfo.uid not in uid_map:
                    tarinfo.uid = 0
                    tarinfo.uname = "root"
                if tarinfo.gid not in gid_map:
                    tarinfo.gid = 0
                    tarinfo.gname = "root"

                # extract to re-compress if package compression differs
                f = None if tarinfo.isdir() or ext == ".bz2" else tar_package.extractfile(tarinfo)

                tarinfo.name = dst
                tar_root.addfile(tarinfo, f)

            tar_package.close()

    tar_root.close()
