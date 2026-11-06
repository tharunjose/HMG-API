#!/system/bin/sh
[ "$(getprop ro.build.product)" = "SU2IFL.IND.0000.V010.001.260430" ] || { echo 'Wrong firmware'; exit 1; }
[ "$(getprop ro.mobis.onebindir)" = "su2ifl_in" ] || { echo 'Wrong platform'; exit 1; }
/system/bin/hmgapid engine verify-map || { echo 'Hook map check failed'; exit 1; }
