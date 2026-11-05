#!/system/bin/sh
export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
umask 077
out=CRETA-HMG-STATUS
mkdir "$out" || exit 1
exec > "$out/status.txt" 2>&1
getprop ro.build.product
if [ ! -x /system/bin/hmgapid ]; then echo 'HMG-API binary missing'; exit 2; fi
/system/bin/hmgapid ping || exit 3
/system/bin/hmgapid engine map
/system/bin/hmgapid engine plan
for path in /sys/class/net/wlan* /sys/bus/sdio/devices/*; do
    [ -e "$path" ] && echo "device $path"
done
for name in enable disable starts; do
    file=/data/hmgapi/hook/$name
    if [ -f "$file" ]; then echo "hook $name present"; [ "$name" = starts ] && cat "$file"; fi
done
if [ -f /data/hmgapi/state/map-check.json ]; then
    cp /data/hmgapi/state/map-check.json "$out/map-check.json" || exit 4
fi
echo 'STATUS COMPLETE'
sync
