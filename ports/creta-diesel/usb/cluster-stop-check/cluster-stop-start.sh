#!/system/bin/sh
export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
umask 077
[ "$(getprop ro.build.product)" = "SU2IFL.IND.0000.V010.001.260430" ] || exit 1
[ -f ./cluster-stop-worker.sh ] && [ -f ./cluster-fields.sh ] || exit 2
out="$PWD/CRETA-CLUSTER-STOP"
mkdir "$out" || exit 3
/system/bin/sh "$PWD/cluster-stop-worker.sh" "$out" "$PWD/cluster-fields.sh" </dev/null >"$out/worker.txt" 2>&1 &
echo 'Cluster diagnostic started. Keep USB inserted until completion toast (about 3 minutes).'
exit 0
