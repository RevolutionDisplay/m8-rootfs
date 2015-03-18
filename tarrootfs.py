#!/usr/bin/env python
import grp
import os
import pwd
import re
import sys
import tarfile

if __name__ == "__main__":
    script_path = os.path.dirname(os.path.realpath(sys.argv[0]))

    tar_root = tarfile.open(os.path.join(script_path, "rootfs.tar.bz2"), mode='w:bz2')

    # start with /dev
    tar_dev = tarfile.open(os.path.join(script_path, "dev.tar.bz2"), mode='r')
    for tarinfo in tar_dev:
        tar_root.addfile(tarinfo)
    tar_dev.close()


    filter_map = {
        "bin/mount$": { "mode": 04755 },
        "bin/ping$": { "mode": 04755 },
        "bin/ping6$": { "mode": 04755 },
        "bin/su$": { "mode": 04755 },
        "bin/umount$": { "mode": 04755 },
        "etc/shadow$": { "gname": "shadow" },
        "etc/gshadow$": { "gname": "shadow" },
        "sbin/unix_chkpwd$": { "gname": "shadow", "mode": 02755 },
        "usr/local": { "gname": "staff" },
        "usr/bin/bsd-write$": { "gname": "tty", "mode": 02755 },
        "usr/bin/chage$": { "gname": "shadow", "mode": 02755 },
        "usr/bin/chfn$": { "mode": 04755 },
        "usr/bin/chsh$": { "mode": 04755 },
        "usr/bin/crontab$": { "gname": "netdev", "mode": 02755 },
        "usr/bin/expiry$": { "gname": "shadow", "mode": 02755 },
        "usr/bin/g?passwd$": { "mode": 04755 },
        "usr/bin/newgrp$": { "mode": 04755 },
        "usr/bin/ssh-agent$": { "gname": "crontab", "mode": 02755 },
        "usr/bin/wall$": { "gname": "tty", "mode": 02755 },
        "usr/lib/pt_chown$": { "mode": 04755 },
        "usr/lib/openssh/ssh-keysign$": { "mode": 04755 },
        "run/utmp": { "gname": "utmp" },
        "var/cache/man": { "uname": "man" },
        "var/lib/libuuid": { "gname": "libuuid", "uname": "libuuid" },
        "var/log/dmesg": { "gname": "adm" },
        "var/log/lastlog": { "gname": "utmp" },
        "var/log/[bw]tmp$": { "gname": "utmp" },
        "var/log/apt/term.log": { "gname": "adm" },
        "var/log/fsck/check(fs|root)$": { "gname": "adm" },
        "var/local": { "gname": "staff" },
        "var/mail": { "gname": "mail" },
        "var/spool/cron/crontabs": { "gname": "netdev" },
    }


    uid_map = { "root": 0 }
    gid_map = { "root": 0 }
    def get_uid(name):
        if not name in uid_map:
            uid_map[name] = pwd.getpwnam(name).pw_uid
        return uid_map[name]
    def get_gid(name):
        if not name in gid_map:
            gid_map[name] = grp.getgrnam(name).gr_gid
        return gid_map[name]

    def add_filter(tarinfo):
        tarinfo.uname = "root"
        tarinfo.gname = "root"
        for k, v in filter_map.iteritems():
            if re.match(k, tarinfo.name):
                if "uname" in v: tarinfo.uname = v["uname"]
                if "gname" in v: tarinfo.gname = v["gname"]
                if "mode" in v:
                    tarinfo.mode = tarinfo.mode & 07777 | v["mode"]
                break
        tarinfo.uid = get_uid(tarinfo.uname)
        tarinfo.gid = get_gid(tarinfo.gname)
        return tarinfo

    os.chdir(os.path.join(script_path, "rootfs"))
    for entries in os.listdir(os.path.join(script_path, "rootfs")):
        tar_root.add(entries, filter=add_filter)

    tar_root.close()
