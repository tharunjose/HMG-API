#!/system/bin/sh
export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
H=/system/bin/hmgapid
attempt=0
while [ "$attempt" -lt 90 ]; do
 if [ "$(getprop sys.boot_completed)" = 1 ]; then
  registry=$(service check com.hkmc.factory 2>&1)
  case "$registry" in
   *'com.hkmc.factory: found'*)
    park=$("$H" vehicle gear.park 2>&1)
    case "$park" in
     'gear.park 1') "$H" vehicle-do startup_notice dismiss; exit $?;;
     'gear.park 0') echo 'Agreement dismissal skipped: car is not in Park'; exit 0;;
    esac;;
  esac
 fi
 attempt=$((attempt+1))
 if [ "$attempt" -lt 90 ]; then sleep 1; fi
done
echo 'Agreement dismissal skipped: Android, factory service or Park was not ready'
exit 1
