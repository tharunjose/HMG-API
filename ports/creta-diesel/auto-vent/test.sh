#!/system/bin/sh
# Manual proof of the driver ventilation command before adding startup automation.
export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
H=/system/bin/hmgapid
toast() { am broadcast -a com.hkmc.intent.action.TOAST -e com.hkmc.intent.extra.TOAST_MESSAGE "$1" --ez com.hkmc.intent.extra.TOAST_POPUPSHOWING true >/dev/null 2>&1; }
echo 'Driver ventilation manual test'
attempt=0
park=
while [ "$attempt" -lt 10 ]; do
 park=$("$H" vehicle gear.park 2>&1)
 case "$park" in 'gear.park 1') break;; 'gear.park 0') echo 'Refused: gear is not P'; toast 'Seat test stopped: select Park'; exit 1;; esac
 attempt=$((attempt+1))
 sleep 2
done
if [ "$park" != 'gear.park 1' ]; then echo "$park"; toast 'Seat test stopped: no Park reading'; exit 1; fi
echo 'Before:'
"$H" vehicle seat_vent.driver seat_state.driver seat_vent.passenger
echo 'Request: seat_vent driver high'
if ! "$H" vehicle-do seat_vent driver high; then toast 'Driver ventilation command failed'; exit 1; fi
sleep 2
echo 'After:'
"$H" vehicle seat_vent.driver seat_state.driver seat_vent.passenger
toast 'Driver ventilation test sent: check driver level 3'
exit 0
