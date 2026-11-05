#!/system/bin/sh
# Disable the HMG-API preload on the next boot. Existing backups and settings stay available for normal removal.
export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
umask 077
[ -e RECOVERY-DONE.txt ] && exit 0
[ "$(getprop ro.build.product)" = 'SU2IFL.IND.0000.V010.001.260430' ] || exit 1
[ -d /data/hmgapi/hook ] || exit 2
: > /data/hmgapi/hook/disable || exit 3
echo 'HMG-API hooks disabled. Remove this USB after reboot. Use Manager to remove the trial and HMG-API.' > RECOVERY-DONE.txt || exit 4
sync
/system/bin/reboot
