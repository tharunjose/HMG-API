#!/system/bin/sh
umask 077
fail() { echo "$1"; exit 1; }
[ "$(getprop ro.build.product)" = "SU2IFL.IND.0000.V010.001.260430" ] || fail 'Wrong firmware'
[ "$(getprop ro.mobis.onebindir)" = "su2ifl_in" ] || fail 'Wrong platform'
H=${ROOT:-}/system/bin/hmgapid
[ -x "$H" ] || fail 'Install HMG-API first'
[ ! -d "${ROOT:-}/data/hmgapi/mods/creta-startup-notice" ] || fail 'Remove Creta startup agreement dismissal before installing the full skip'
sum() { "${ROOT:-}/system/bin/lpatch" md5 "$1" 2>/dev/null | while read -r value rest; do echo "$value"; done; }
APP=${ROOT:-}/system/priv-app
[ "$(sum "$APP/SystemUI.apk")" = '@APK_MD5@' ] || fail 'SystemUI APK does not match captured stock'
odex=$(sum "$APP/SystemUI.odex")
if [ "$odex" = '@PATCHED_MD5@' ]; then
    [ -d "${ROOT:-}/data/hmgapi/mods/creta-skip-consent" ] || fail 'Patched ODEX is not owned by this mod'
else
    [ "$odex" = '@ODEX_MD5@' ] || fail 'SystemUI ODEX does not match captured stock'
fi
# The stock APK is odex-only. Refuse an alternate cached executable rather than
# deleting unknown code or letting it mask the checked adjacent ODEX.
for cache in "${ROOT:-}"/data/dalvik-cache/*SystemUI* "${ROOT:-}"/cache/dalvik-cache/*SystemUI*; do
    [ ! -f "$cache" ] || fail 'SystemUI has an alternate Dalvik cache file; return evidence before installing'
done
"$H" engine verify-map || fail 'Hook map check failed'
echo 'Exact Creta SystemUI matched. Restart the head unit after installing the skip.'
