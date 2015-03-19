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
        ".*/.gitkeep$": { "exclude": True },
        "bin/mount$": { "mode": 04755 },
        "bin/ping$": { "mode": 04755 },
        "bin/ping6$": { "mode": 04755 },
        "bin/su$": { "mode": 04755 },
        "bin/umount$": { "mode": 04755 },
        "etc/(group|passwd|gshadow|shadow)-$": { "mode": 0600 },
        "etc/g?shadow$": { "gname": "shadow", "mode": 0640 },
        "etc/apt/(trustdb|trusted).gpg$": { "mode": 0600 },
        "etc/security/opasswd$": { "mode": 0600 },
        "etc/ssh/ssh_.*_key$": { "mode": 0600 },
        "etc/ssl/private$": { "mode": 0700 },
        "root$": { "mode": 0700 },
        "run/initctl": { "mode": 0600 },
        "run/lock": { "mode": 01777 },
        "run/utmp": { "gname": "utmp", "mode": 0664 },
        "sbin/unix_chkpwd$": { "gname": "shadow", "mode": 02755 },
        "tmp$": { "mode": 01777 },
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
        "usr/local": { "gname": "staff", "mode": 02775 },
        "var/cache/man": { "uname": "man", "dirmode": 02755 },
        "var/cache/apt/archives/lock": { "mode": 0640 },
        "var/cache/ldconfig$": { "mode": 0700 },
        "var/cache/ldconfig/aux-cache$": { "mode": 0600 },
        "var/cache/man/.*/(CACHEDIR.TAG|index.db)$": { "mode": 0644 },
        "var/cache/debconf/passwords.dat": { "mode": 0600 },
        "var/lib/dpkg/lock": { "mode": 0640 },
        "var/lib/dpkg/triggers/Lock": { "mode": 0600 },
        "var/lib/libuuid": { "gname": "libuuid", "uname": "libuuid", "mode": 02775 },
        "var/lib/apt/lists/lock": { "mode": 0640 },
        "var/log/btmp$": { "gname": "utmp", "mode": 0660 },
        "var/log/dmesg": { "gname": "adm", "mode": 0640 },
        "var/log/lastlog": { "gname": "utmp", "mode": 0664 },
        "var/log/wtmp$": { "gname": "utmp", "mode": 0664 },
        "var/log/apt/term.log": { "gname": "adm", "mode": 0640 },
        "var/log/fsck/check(fs|root)$": { "gname": "adm", "mode": 0640 },
        "var/local": { "gname": "staff", "mode": 02775 },
        "var/mail$": { "gname": "mail", "mode": 02775 },
        "var/spool/cron/crontabs": { "gname": "netdev", "mode": 01730 },
        "var/tmp": { "mode": 01777 },
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
        # patch up permissions
        if tarinfo.isdir():
            tarinfo.mode = (tarinfo.mode & ~0777) | 0755
        elif tarinfo.isfile():
            if tarinfo.mode & 0111:  # executable
                tarinfo.mode = (tarinfo.mode & ~0777) | 0755
            else:
                tarinfo.mode = (tarinfo.mode & ~0777) | 0644

        # patch up user to root/root by default
        tarinfo.uname = "root"
        tarinfo.gname = "root"

        # handle special cases
        for k, v in filter_map.iteritems():
            if re.match(k, tarinfo.name):
                if "exclude" in v and v["exclude"]:
                    return None
                if "uname" in v: tarinfo.uname = v["uname"]
                if "gname" in v: tarinfo.gname = v["gname"]
                if "dirmode" in v and tarinfo.isdir():
                    tarinfo.mode = (tarinfo.mode & ~07777) | v["dirmode"]
                if "mode" in v:
                    tarinfo.mode = (tarinfo.mode & ~07777) | v["mode"]
        
        # fill in uid's & gid's
        tarinfo.uid = get_uid(tarinfo.uname)
        tarinfo.gid = get_gid(tarinfo.gname)
        return tarinfo

    os.chdir(os.path.join(script_path, "rootfs"))
    for entries in os.listdir(os.path.join(script_path, "rootfs")):
        tar_root.add(entries, filter=add_filter)

    tar_root.close()
