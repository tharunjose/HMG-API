#!/system/bin/sh
H=${ROOT:-}/system/bin/hmgapid
saved=${ROOT:-}/data/hmgapi/data/creta-startup-notice
keys='startup_notice cmd.creta-startup-notice.startup_notice'
save_permissions() {
 mkdir -p "$saved" || return 1
 for key in $keys; do
  if [ ! -f "$saved/$key.saved" ]; then
   if [ -f "${ROOT:-}/data/hmgapi/settings/allow/$key" ]; then echo on > "$saved/$key.saved" || return 1
   else echo off > "$saved/$key.saved" || return 1; fi
  fi
 done
}
restore_permissions() {
 for key in $keys; do
  if [ -f "$saved/$key.saved" ]; then
   value=$(cat "$saved/$key.saved")
   "$H" allow "$key" "$value" || return 1
  fi
 done
}
