TARGETS = mountkernfs.sh hostname.sh udev mountdevsubfs.sh mountall.sh mountall-bootclean.sh networking urandom hwclock.sh checkroot.sh mountnfs.sh mountnfs-bootclean.sh resolvconf udev-finish procps checkfs.sh checkroot-bootclean.sh bootmisc.sh kmod screen-cleanup
INTERACTIVE = udev checkroot.sh checkfs.sh
udev: mountkernfs.sh
mountdevsubfs.sh: mountkernfs.sh udev
mountall.sh: checkfs.sh checkroot-bootclean.sh
mountall-bootclean.sh: mountall.sh
networking: mountkernfs.sh mountall.sh mountall-bootclean.sh urandom resolvconf procps
urandom: mountall.sh mountall-bootclean.sh hwclock.sh
hwclock.sh: mountdevsubfs.sh
checkroot.sh: hwclock.sh mountdevsubfs.sh hostname.sh
mountnfs.sh: mountall.sh mountall-bootclean.sh networking
mountnfs-bootclean.sh: mountall.sh mountall-bootclean.sh mountnfs.sh
resolvconf: mountall.sh mountall-bootclean.sh
udev-finish: udev mountall.sh mountall-bootclean.sh
procps: mountkernfs.sh mountall.sh mountall-bootclean.sh udev
checkfs.sh: checkroot.sh
checkroot-bootclean.sh: checkroot.sh
bootmisc.sh: checkroot-bootclean.sh mountall-bootclean.sh mountnfs-bootclean.sh mountall.sh mountnfs.sh udev
kmod: checkroot.sh
screen-cleanup: mountall.sh mountall-bootclean.sh mountnfs.sh mountnfs-bootclean.sh
