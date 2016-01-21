TARGETS = mountkernfs.sh hostname.sh udev mountdevsubfs.sh networking mountall.sh mountall-bootclean.sh urandom hwclock.sh checkroot.sh resolvconf mountnfs.sh mountnfs-bootclean.sh checkroot-bootclean.sh bootmisc.sh udev-finish checkfs.sh screen-cleanup kmod procps
INTERACTIVE = udev checkroot.sh checkfs.sh
udev: mountkernfs.sh
mountdevsubfs.sh: mountkernfs.sh udev
networking: mountkernfs.sh mountall.sh mountall-bootclean.sh urandom resolvconf procps
mountall.sh: checkfs.sh checkroot-bootclean.sh
mountall-bootclean.sh: mountall.sh
urandom: mountall.sh mountall-bootclean.sh hwclock.sh
hwclock.sh: mountdevsubfs.sh
checkroot.sh: hwclock.sh mountdevsubfs.sh hostname.sh
resolvconf: mountall.sh mountall-bootclean.sh
mountnfs.sh: mountall.sh mountall-bootclean.sh networking
mountnfs-bootclean.sh: mountall.sh mountall-bootclean.sh mountnfs.sh
checkroot-bootclean.sh: checkroot.sh
bootmisc.sh: checkroot-bootclean.sh mountnfs-bootclean.sh mountall-bootclean.sh mountall.sh mountnfs.sh udev
udev-finish: udev mountall.sh mountall-bootclean.sh
checkfs.sh: checkroot.sh
screen-cleanup: mountall.sh mountall-bootclean.sh mountnfs.sh mountnfs-bootclean.sh
kmod: checkroot.sh
procps: mountkernfs.sh mountall.sh mountall-bootclean.sh udev
