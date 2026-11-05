#!/system/bin/sh
export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
umask 077
out="$1"
filter="$2"
toast() {
    am broadcast -a com.hkmc.intent.action.TOAST -e com.hkmc.intent.extra.TOAST_MESSAGE "$1" --ez com.hkmc.intent.extra.TOAST_POPUPSHOWING true >/dev/null 2>&1
}
# Exact name derived from this car's com.hkmc.Service static initializer.
svc=com.hkmc.micom.cluster
. "$filter"
preflight=$(dumpsys "$svc" 2>/dev/null | cluster_fields)
printf '%s\n' "$preflight" > "$out/preflight.txt"
case "$preflight" in
    *'Display Type'*'='*) ;;
    *) echo 'No readable navigation display fields from stock cluster service' > "$out/FAILED.txt"
       toast 'Cluster diagnostic failed: reconnect USB to Mac'; exit 1;;
esac
{ date; getprop ro.build.product; echo "cluster_service=$svc"; /system/bin/hmgapid ping; } > "$out/status.txt" 2>&1
# Only fixed event labels are retained from logcat, never original log lines.
events() {
    while IFS= read -r line; do
        case "$line" in
            *'CarPlay: maneuver '*) echo CARPLAY_MANEUVER;;
            *'CarPlay: hud list type '*) echo CARPLAY_HUD_LIST;;
            *'RouteGuidanceUpdate'*) echo IAP2_ROUTE_UPDATE;;
            *'stopTurnByTurn()'*) echo STOCK_STOP_TBT;;
            *'Iap2SvcStopRouteGuidanceUpdate'*) echo IAP2_STOP_ROUTE_REQUEST;;
            *'cluster: '*failed*) echo CLUSTER_CALL_FAILED;;
        esac
    done
}
toast 'Cluster capture started: Google Maps route, then cancel'
i=0
while [ "$i" -lt 60 ]; do
    { echo "SAMPLE $i"; date; dumpsys "$svc" 2>/dev/null | cluster_fields; } >> "$out/cluster-fields.txt"
    { echo "SAMPLE $i"; logcat -d -v brief -s HMG-API:V DiPO:V iAP2:V Iap2:V IAP2:V '*:S' 2>/dev/null | events; } >> "$out/events.txt"
    i=$((i+1))
    sleep 3
done
echo 'CLUSTER CAPTURE COMPLETE' > "$out/COMPLETE.txt"
sync
toast 'Cluster capture complete: return USB to Mac'
