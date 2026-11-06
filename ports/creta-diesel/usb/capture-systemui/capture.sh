#!/system/bin/sh
export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
umask 077
[ "$(getprop ro.build.product)" = "SU2IFL.IND.0000.V010.001.260430" ] || { echo 'Wrong firmware'; exit 1; }
out=
for usb in /storage/usb0 /storage/usb1 /storage/usb2; do
 if [ -f "$usb/CRETA-SYSTEMUI-CAPTURE" ]; then out="$usb/CRETA-SYSTEMUI"; break; fi
done
[ -n "$out" ] || { echo 'Insert the prepared USB before Launch'; exit 2; }
base="$out"
n=1
while [ -e "$out" ]; do n=$((n+1)); out="$base-$n"; done
mkdir "$out" || exit 3
date > "$out/status.txt"
getprop ro.build.product >> "$out/status.txt"
apk=
for candidate in /system/priv-app/SystemUI.apk /system/app/SystemUI.apk /system/priv-app/SystemUI/SystemUI.apk /system/app/SystemUI/SystemUI.apk; do
 if [ -f "$candidate" ]; then apk="$candidate"; break; fi
done
[ -n "$apk" ] || { echo 'SystemUI APK not found in expected locations' > "$out/FAILED.txt"; exit 4; }
for file in "$apk" "${apk%.apk}.odex"; do
 if [ -f "$file" ]; then
  name=${file##*/}
  cp "$file" "$out/$name" || { echo 'Copy failed' > "$out/FAILED.txt"; exit 5; }
  before=$(/system/bin/lpatch md5 "$file") || exit 6
  after=$(/system/bin/lpatch md5 "$out/$name") || exit 7
  set -- $before; expected="$1"
  set -- $after; actual="$1"
  [ "$expected" = "$actual" ] || { echo 'Copy hash mismatch' > "$out/FAILED.txt"; exit 8; }
  echo "$expected  $name" >> "$out/MD5SUMS"
 fi
done
echo 'SYSTEMUI SOURCE CAPTURE COMPLETE' > "$out/COMPLETE.txt"
sync
echo 'SystemUI copied and checked. Reconnect USB to Mac.'
exit 0
