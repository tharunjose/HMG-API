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
echo "$preflight" > "$out/preflight.txt"
case "$preflight" in
    *'Display Type'*'='*) ;;
    *) echo 'No readable navigation display fields from stock cluster service' > "$out/FAILED.txt"
       toast 'Cluster diagnostic failed: reconnect USB to Mac'; exit 1;;
esac
{ date; getprop ro.build.product; echo "cluster_service=$svc"; /system/bin/hmgapid ping; } > "$out/status.txt" 2>&1
# Identify which hooks are installed using only the hash of the known mod file.
installed=/data/hmgapi/mods/wireless-carplay-aa/hooks.jar
hash=$(/system/bin/lpatch md5 "$installed" 2>/dev/null)
set -- $hash
case "$1" in
    8259c75f656a679f1821c6b01b64f171) version='2.5.0-diesel.2';;
    9e42297ebb4fe9a3b3412de563765980) version='2.5.0-diesel.1';;
    *) version='unknown';;
esac
echo "wireless_hooks=$version" >> "$out/status.txt"
toast 'Idle capture started'
count=0
usable=0
while [ "$count" -lt 45 ]; do
    sample=$(dumpsys "$svc" 2>/dev/null | cluster_fields)
    { echo "SAMPLE $count"; date; echo "$sample"; } >> "$out/cluster-fields.txt"
    case "$sample" in *'Display Type'*'='*) usable=$((usable+1));; esac
    count=$((count+1))
    sleep 2
done
echo "readable_samples=$usable" >> "$out/status.txt"
if [ "$usable" -eq 0 ]; then
    echo 'No readable samples after preflight' > "$out/FAILED.txt"
    sync
    toast 'Idle capture failed: return USB to Mac'
    exit 1
fi
echo 'IDLE CAPTURE COMPLETE' > "$out/COMPLETE.txt"
sync
toast 'Idle capture complete: return USB to Mac'
