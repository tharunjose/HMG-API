#!/system/bin/sh
# Low-charge, parked-drop and drive-recovery rules follow zpoon's Battery Watchdog defaults.
# Persist one checkpoint for comparisons across head-unit sleep/restarts.
umask 077
cd "${HMGAPI_DATA:?}" || exit 1

percent() {
    case "$1" in 0|[1-9]|[1-9][0-9]|100) return 0;; *) return 1;; esac
}
timestamp() {
    case "$1" in ''|*[!0-9]*|0*|???????????*) return 1;; *) return 0;; esac
}
warn() {
    am broadcast -a com.hkmc.intent.action.TOAST \
       -e com.hkmc.intent.extra.TOAST_MESSAGE "$1" \
       --ez com.hkmc.intent.extra.TOAST_POPUPSHOWING true >/dev/null 2>&1
}

first=0; last=0; low=0
if [ -r checkpoint ] && read -r a b c d e < checkpoint &&
   timestamp "$a" && percent "$b" && timestamp "$c" && percent "$d" &&
   [ "$a" -le "$c" ] && { [ "$e" = 0 ] || [ "$e" = 1 ]; }; then
    first=$a; start_pct=$b; last=$c; last_pct=$d; low=$e
fi
# Refuse to infer a parked drop from a gap caused only by unavailable telemetry.
previous_poll=$last
off_since=0; new_session=0; compare=0
while :; do
    now=$(date +%s)
    if timestamp "$now"; then
        if [ "$previous_poll" -gt 0 ] && [ $((now - previous_poll)) -ge 600 ]; then
            new_session=1; compare=1
        fi
        if [ "$now" -lt "$previous_poll" ]; then new_session=1; compare=0; off_since=0; fi
        previous_poll=$now
        power=$(dumpsys power 2>/dev/null)
        case "$power" in
            *mScreenOn=false*|*mInteractive=false*|*mWakefulness=Asleep*|*'Display Power: state=OFF'*)
                [ "$off_since" -gt 0 ] || off_since=$now
                sleep 60; continue;;
        esac
        if [ "$off_since" -gt 0 ] && [ $((now - off_since)) -ge 600 ]; then
            new_session=1; compare=1
        fi
        off_since=0
        reply=$(hmgapid vehicle battery12v.soc 2>/dev/null) || reply=''
        pct=${reply#battery12v.soc }
        if [ "$reply" != "$pct" ] && percent "$pct"; then
            message=''
            if [ "$first" = 0 ] || [ "$new_session" = 1 ]; then
                if [ "$compare" = 1 ] && [ "$last" -gt 0 ] && [ "$now" -gt "$last" ]; then
                    drop=$((last_pct - pct))
                    if [ "$drop" -ge 15 ]; then message="12V dropped $drop points since last session ($last_pct% to $pct%). "; fi
                    duration=$((last - first))
                    if [ "$duration" -ge 1200 ] && [ "$duration" -le 86400 ] && [ "$last_pct" -lt "$start_pct" ]; then
                        message="${message}12V decreased during the previous session ($start_pct% to $last_pct%). "
                    fi
                fi
                first=$now; start_pct=$pct; low=0; new_session=0; compare=0
            fi
            if [ "$pct" -lt 60 ]; then
                if [ "$low" = 0 ]; then message="12V battery low ($pct%). $message"; fi
                low=1
            else
                low=0
            fi
            last=$now; last_pct=$pct
            echo "$first $start_pct $last $last_pct $low" > checkpoint.new && mv checkpoint.new checkpoint || exit 1
            [ -z "$message" ] || warn "$message"
        fi
    fi
    sleep 60
done
