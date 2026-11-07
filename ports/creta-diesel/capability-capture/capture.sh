#!/system/bin/sh
export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
umask 077
[ "$(getprop ro.build.product)" = "SU2IFL.IND.0000.V010.001.260430" ] || { echo 'Wrong firmware'; exit 1; }
[ "$(getprop ro.mobis.onebindir)" = "su2ifl_in" ] || exit 1
here=${0%/*}
[ -f "$here/capture.jar" ] && [ -f "$here/readers.tsv" ] || { echo 'Capture files missing'; exit 2; }
usb=
for p in /storage/usb0 /storage/usb1 /storage/usb2; do
 [ -f "$p/CRETA-CAPABILITY-CAPTURE" ] && { usb=$p; break; }
done
[ -n "$usb" ] || { echo 'Insert prepared NEMESIS USB'; exit 3; }
out="$usb/CRETA-CAPABILITIES"; n=1
while [ -e "$out" ]; do n=$((n+1)); out="$usb/CRETA-CAPABILITIES-$n"; done
mkdir "$out" || exit 4
# Child-specific bounded read: never waits forever on a missing Binder service.
bounded() {
 label=$1; limit=$2; shift 2
 "$@" > "$out/$label.txt" 2>&1 &
 child=$!
 ticks=0
 while kill -0 "$child" 2>/dev/null; do
  if [ "$ticks" -ge "$limit" ]; then
   kill "$child" 2>/dev/null
   sleep 1
   kill -9 "$child" 2>/dev/null
   wait "$child" 2>/dev/null
   echo "$label TIMEOUT" >> "$out/status.txt"; return
  fi
  sleep 1; ticks=$((ticks+1))
 done
 wait "$child"; result=$?
 echo "$label exit=$result" >> "$out/status.txt"
}
{ date; getprop ro.build.product; getprop ro.build.version.release; getprop ro.mobis.onebindir; } > "$out/status.txt"
bounded services 10 service list
bounded input-devices 10 getevent -lp
bounded packages 10 pm list packages -f
if [ -x /system/bin/hmgapid ]; then
 bounded hmg-ping 10 /system/bin/hmgapid ping
 bounded hmg-mods 10 /system/bin/hmgapid mods
 bounded hmg-services 10 /system/bin/hmgapid services
 bounded vehicle-readings 15 /system/bin/hmgapid vehicle gear.park parking_brake speed moving battery12v.soc outside_temp outside_temp_f seat_state.driver seat_state.passenger seat_vent.driver seat_vent.passenger
fi
CLASSPATH="$here/capture.jar:/system/framework/automotive.jar"
export CLASSPATH
bounded cached-getters 30 app_process /system/bin creta.capture.CapabilityRead "$out" "$here/readers.tsv"
# Inventory names only. No arbitrary OEM command or setter is executed.
for f in /system/app/* /system/priv-app/* /system/framework/*; do [ -f "$f" ] && echo "$f"; done > "$out/system-files.txt"
mkdir "$out/settings-apps"
for f in /system/app/* /system/priv-app/*; do
 case "$f" in
  *USM*.apk|*USM*.odex|*Datc*.apk|*Datc*.odex|*DATC*.apk|*DATC*.odex|*Climate*.apk|*Climate*.odex|*/Settings_W.apk|*/Settings_W.odex|*/ButtonSettings.apk|*/ButtonSettings.odex)
   [ -f "$f" ] || continue
   name=${f##*/}
   [ ! -e "$out/settings-apps/$name" ] || continue
   cp "$f" "$out/settings-apps/$name" || { echo "$name copy-failed" >> "$out/status.txt"; continue; }
   before=$(/system/bin/lpatch md5 "$f"); set -- $before; expected=$1
   after=$(/system/bin/lpatch md5 "$out/settings-apps/$name"); set -- $after; actual=$1
   if [ -n "$expected" ] && [ "$expected" = "$actual" ]; then echo "$expected  settings-apps/$name" >> "$out/MD5SUMS"; else echo "$name HASH-FAILED" >> "$out/status.txt"; fi
   ;;
 esac
done
for f in /data/hmgapi/state/map-check.json /data/hmgapi/state/services.status /data/hmgapi/public/state.json; do
 [ -f "$f" ] && cp "$f" "$out/${f##*/}"
done
if [ -f "$out/CACHE-READS-FINISHED.txt" ]; then
 echo 'Collection finished. Individual fields may be unsupported; see status.txt.' > "$out/COMPLETE.txt"
 echo 'Capability capture finished. Keep results on USB for Mac review.'
 message='Creta capability capture finished. Continue your batch.'
else
 echo 'Runtime getters incomplete; other evidence retained.' > "$out/PARTIAL.txt"
 echo 'Partial capture saved. Return USB for review; no repeat needed now.'
 message='Creta partial capture saved. Continue batch; return USB afterward.'
fi
sync
am broadcast -a com.hkmc.intent.action.TOAST -e com.hkmc.intent.extra.TOAST_MESSAGE "$message" --ez com.hkmc.intent.extra.TOAST_POPUPSHOWING true >/dev/null 2>&1
exit 0
