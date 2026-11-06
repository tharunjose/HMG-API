#!/system/bin/sh
message="Watchdog is waiting for a valid 12V reading."
checkpoint=/data/hmgapi/run/creta-battery-watchdog/watch/checkpoint
now=$(date +%s)
if [ -r "$checkpoint" ] && read -r start initial last charge low < "$checkpoint"; then
    case "$now:$last" in *[!0-9:]*|:*|*:) ;; *)
        age=$((now - last))
        if [ "$age" -ge 0 ] && [ "$age" -le 120 ]; then
            message="Watchdog received a recent 12V reading: $charge%."
        fi;;
    esac
fi
am broadcast -a com.hkmc.intent.action.TOAST -e com.hkmc.intent.extra.TOAST_MESSAGE "$message" --ez com.hkmc.intent.extra.TOAST_POPUPSHOWING true >/dev/null 2>&1
echo "$message"
