#!/system/bin/sh
sh ./scripts/preuninstall-engine.sh || exit 1
if [ -d "${ROOT:-}/data/hmgapi/mods/creta-startup-notice" ]; then exit 0; fi
. ./scripts/permissions.sh || exit 1
restore_permissions || exit 1
rm -f "$saved/startup_notice.saved" "$saved/cmd.creta-startup-notice.startup_notice.saved"
exit 0
