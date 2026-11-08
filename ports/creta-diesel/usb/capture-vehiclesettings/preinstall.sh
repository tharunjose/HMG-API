#!/system/bin/sh
[ "$(getprop ro.build.product)" = "SU2IFL.IND.0000.V010.001.260430" ] || exit 1
[ "$(getprop ro.mobis.onebindir)" = "su2ifl_in" ] || exit 1
[ -x /system/bin/lpatch ] || exit 2
[ -r /system/app/HKMC_VehicleSetting.apk ] || exit 3
[ -r /system/app/HKMC_VehicleSetting.odex ] || exit 3
