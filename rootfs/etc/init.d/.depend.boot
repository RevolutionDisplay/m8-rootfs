TARGETS = mountkernfs.sh hostname.sh udev mountdevsubfs.sh networking mountall.sh mountall-bootclean.sh urandom hwclock.sh checkroot.sh mountnfs.sh mountnfs-bootclean.sh bootmisc.sh udev-mtab checkfs.sh checkroot-bootclean.sh mtab.sh kmod procps
INTERACTIVE = udev checkroot.sh checkfs.sh
udev: mountkernfs.sh
mountdevsubfs.sh: mountkernfs.sh udev
networking: mountkernfs.sh mountall.sh mountall-bootclean.sh urandom
mountall.sh: checkfs.sh checkroot-bootclean.sh
mountall-bootclean.sh: mountall.sh
urandom: mountall.sh mountall-bootclean.sh hwclock.sh
hwclock.sh: mountdevsubfs.sh
checkroot.sh: hwclock.sh mountdevsubfs.sh hostname.sh
mountnfs.sh: mountall.sh mountall-bootclean.sh networking
mountnfs-bootclean.sh: mountall.sh mountall-bootclean.sh mountnfs.sh
bootmisc.sh: mountnfs-bootclean.sh mountall-bootclean.sh checkroot-bootclean.sh mountall.sh mountnfs.sh udev
udev-mtab: udev mountall.sh mountall-bootclean.sh
checkfs.sh: checkroot.sh mtab.sh
checkroot-bootclean.sh: checkroot.sh
mtab.sh: checkroot.sh
kmod: checkroot.sh
procps: mountkernfs.sh mountall.sh mountall-bootclean.sh udev
