#!/system/bin/sh
export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
umask 077
[ "$(getprop ro.build.product)" = "SU2IFL.IND.0000.V010.001.260430" ] || { echo 'Wrong firmware'; exit 1; }
[ "$(getprop ro.mobis.onebindir)" = "su2ifl_in" ] || { echo 'Wrong variant'; exit 1; }
[ -x /system/bin/lpatch ] || { echo 'Hash tool unavailable'; exit 1; }
out=
for usb in /storage/usb0 /storage/usb1 /storage/usb2; do
 if [ -f "$usb/CRETA-VEHICLESETTINGS-CAPTURE" ]; then out="$usb/CRETA-VEHICLESETTINGS"; break; fi
done
[ -n "$out" ] || { echo 'Insert the prepared USB before Launch'; exit 2; }
base="$out"; n=1
while [ -e "$out" ]; do n=$((n+1)); out="$base-$n"; done
mkdir "$out" || exit 3
notify() {
 echo "$1"
 am broadcast -a com.hkmc.intent.action.TOAST -e com.hkmc.intent.extra.TOAST_MESSAGE "$1" --ez com.hkmc.intent.extra.TOAST_POPUPSHOWING true >/dev/null 2>&1
}
fail() {
 echo "$1" > "$out/FAILED.txt"
 notify 'Vehicle Settings capture incomplete. Keep USB results for review; no retry needed.'
 exit 4
}
digest() {
 value=$(/system/bin/lpatch md5 "$1") || return 1
 set -- $value
 value=${1-}
 [ "${#value}" -eq 32 ] || return 1
 case "$value" in *[!0-9a-fA-F]*) return 1;; esac
 echo "$value"
}
{ date; getprop ro.build.product; getprop ro.mobis.onebindir; } > "$out/status.txt" || fail 'Status write failed'
# Fixed read-only source list, confirmed by the owner's file inventory.
# No Binder requests, settings writes, app launches or vehicle commands.
for file in /system/app/HKMC_VehicleSetting.apk /system/app/HKMC_VehicleSetting.odex /system/app/SettingsCommon.apk /system/app/SettingsCommon.odex /system/framework/hkmc-res.apk /system/framework/framework-res.apk; do
 [ -r "$file" ] || fail "Required source missing: $file"
 name=${file##*/}
 before=$(digest "$file") || fail "Source hash failed: $name"
 cp "$file" "$out/$name" || fail "Copy failed: $name"
 copied=$(digest "$out/$name") || fail "Copy hash failed: $name"
 after=$(digest "$file") || fail "Source recheck failed: $name"
 [ "$before" = "$copied" ] && [ "$before" = "$after" ] || fail "Copy mismatch or source changed: $name"
 echo "$copied  $name" >> "$out/MD5SUMS" || fail 'Manifest write failed'
done
echo 'VEHICLE SETTINGS SOURCE CAPTURE COMPLETE: six files verified' > "$out/COMPLETE.txt" || fail 'Completion write failed'
sync
notify 'Vehicle Settings copied and checked. Continue the other checks; return USB afterward.'
exit 0
