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

    tar_root.close()
