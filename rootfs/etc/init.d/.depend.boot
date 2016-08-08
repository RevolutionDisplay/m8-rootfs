TARGETS = mountkernfs.sh hostname.sh udev mountdevsubfs.sh networking mountall.sh mountall-bootclean.sh urandom mountnfs.sh mountnfs-bootclean.sh hwclock.sh resolvconf checkroot.sh bootmisc.sh checkfs.sh checkroot-bootclean.sh kmod procps screen-cleanup udev-finish
INTERACTIVE = udev checkroot.sh checkfs.sh
udev: mountkernfs.sh
mountdevsubfs.sh: mountkernfs.sh udev
networking: mountkernfs.sh mountall.sh mountall-bootclean.sh urandom resolvconf procps
mountall.sh: checkfs.sh checkroot-bootclean.sh
mountall-bootclean.sh: mountall.sh
urandom: mountall.sh mountall-bootclean.sh hwclock.sh
mountnfs.sh: mountall.sh mountall-bootclean.sh networking
mountnfs-bootclean.sh: mountall.sh mountall-bootclean.sh mountnfs.sh
hwclock.sh: mountdevsubfs.sh
resolvconf: mountall.sh mountall-bootclean.sh
checkroot.sh: hwclock.sh mountdevsubfs.sh hostname.sh
bootmisc.sh: mountall-bootclean.sh checkroot-bootclean.sh mountnfs-bootclean.sh mountall.sh mountnfs.sh udev
checkfs.sh: checkroot.sh
checkroot-bootclean.sh: checkroot.sh
kmod: checkroot.sh
procps: mountkernfs.sh mountall.sh mountall-bootclean.sh udev
screen-cleanup: mountall.sh mountall-bootclean.sh mountnfs.sh mountnfs-bootclean.sh
udev-finish: udev mountall.sh mountall-bootclean.sh
