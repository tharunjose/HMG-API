#!/system/bin/sh
export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
H=/system/bin/hmgapid
sleep 12
attempt=0
while [ "$attempt" -lt 20 ]; do
 park=$("$H" vehicle gear.park 2>&1)
 case "$park" in
  'gear.park 1') "$H" vehicle-do startup_notice dismiss; exit $?;;
  'gear.park 0') echo 'Agreement dismissal skipped: car is not in Park'; exit 0;;
 esac
 attempt=$((attempt+1))
 sleep 3
done
echo 'Agreement dismissal skipped: no readable Park status'
exit 1
