#!/system/bin/sh
export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
[ "$(getprop ro.build.product)" = "SU2IFL.IND.0000.V010.001.260430" ] || exit 1
here=${0%/*}
usb=
for p in /storage/usb0 /storage/usb1 /storage/usb2; do
 [ -f "$p/CRETA-CAPABILITY-CAPTURE" ] && { usb=$p; break; }
done
[ -n "$usb" ] || { echo 'Insert prepared USB'; exit 2; }
/system/bin/sh "$here/capture.sh" </dev/null >> "$usb/CRETA-CAPTURE-LAUNCH.txt" 2>&1 &
echo 'Read-only capture started. Keep USB inserted; wait for the completion toast (usually 30–90 seconds).'
