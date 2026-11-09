#!/system/bin/sh
umask 077
unset ROOT
export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
[ "$(getprop ro.build.product)" = SU2IFL.IND.0000.V010.001.260430 ] || exit 1
usb=
for d in /storage/usb0 /storage/usb1 /storage/usb2 /mnt/media_rw/usb0 /mnt/media_rw/usb1 /mnt/media_rw/usb2; do
    [ -f "$d/CRETA-BASE-STATUS" ] && { usb=$d; break; }
done
[ -n "$usb" ] || exit 2
out=$usb/CRETA-BASE-STATUS-REPORT
n=1
while [ -e "$out" ]; do n=$((n+1)); out=$usb/CRETA-BASE-STATUS-REPORT-$n; done
mkdir "$out" || exit 1
{
    date
    getprop ro.build.product
    cat /data/creta-base-upgrade-1.0.2.1/state
    /system/bin/hmgapid version; echo "version_exit=$?"
    /system/bin/hmgapid vehicle battery12v.soc; echo "single_exit=$?"
    /system/bin/hmgapid vehicle battery12v.soc gear.park; echo "combined_exit=$?"
    /system/bin/hmgapid services; echo "services_exit=$?"
} > "$out/status.txt" 2>&1
# Only fixed base inventory and transaction checksums; no phone identifiers/log dump.
cp /data/hmgapi/installed.txt "$out/installed.txt" || exit 1
for f in old.md5 new.md5; do
    cp "/data/creta-base-upgrade-1.0.2.1/$f" "$out/$f" || exit 1
done
sync
echo 'Status collection finished; this is not a declaration that the readings passed.' > "$out/COMPLETE.txt"
sync
am broadcast -a com.hkmc.intent.action.TOAST -e com.hkmc.intent.extra.TOAST_MESSAGE "Base status saved. Keep USB report." --ez com.hkmc.intent.extra.TOAST_POPUPSHOWING true >/dev/null 2>&1
