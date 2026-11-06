#!/system/bin/sh
[ "$(getprop ro.build.product)" = "SU2IFL.IND.0000.V010.001.260430" ] || exit 1
[ -x /system/bin/lpatch ] || exit 2
