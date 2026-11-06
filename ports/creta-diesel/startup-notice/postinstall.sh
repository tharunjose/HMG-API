#!/system/bin/sh
. ./scripts/permissions.sh || exit 1
save_permissions || exit 1
for key in $keys; do
 if ! "$H" allow "$key" on; then restore_permissions; exit 1; fi
done
if sh ./scripts/postinstall-engine.sh; then exit 0; fi
restore_permissions
exit 1
