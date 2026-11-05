#!/system/bin/sh
export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
umask 077
[ "$(getprop ro.build.product)" = "SU2IFL.IND.0000.V010.001.260430" ] || exit 1
am start -W -n com.hkmc.wifisettings/.WifiClientSettings
