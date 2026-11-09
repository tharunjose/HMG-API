#!/system/bin/sh
umask 077
P=${1:?payload directory required}
. "$P/transaction.sh"
LP=$P/lpatch
chmod 755 "$LP" || exit 1
fail() { echo "Base repair refused: $1"; exit 1; }
[ "$(getprop ro.build.product)" = SU2IFL.IND.0000.V010.001.260430 ] || fail 'wrong product'
[ "$(getprop ro.mobis.onebindir)" = su2ifl_in ] || fail 'wrong variant'
[ ! -e "$T" ] || fail 'a prior trial exists; return its report before retrying'
[ ! -e "$ROOT/data/hmgapi/state/journal.json" ] || fail 'pending HMG apply/recovery'
[ ! -e "$ROOT/data/hmgapi/hook/disable" ] || fail 'hooks disabled'
[ ! -e "$ROOT/data/hmgapi/public/HmgApi.apk" ] || fail 'app install is pending'
verify_set "$P" "$P/payload.md5" || fail 'damaged package'
verify_set "$ROOT" "$P/baseline.md5" || fail 'base or map differs from tested baseline'
case "$(cat "$ROOT/data/hmgapi/installed.txt")" in
    'version 1.0.1
'*) ;; *) fail 'unexpected installed base version';;
esac
[ -f "$ROOT/system/etc/install-recovery.sh" ] && [ -f "$ROOT/system/etc/qb_runtime.sh" ] || fail 'missing boot scripts'
mkdir -p "$T/old" "$T/new" || fail 'cannot create backup'
cp "$P/transaction.sh" "$P/recover.sh" "$LP" "$T/" || fail 'cannot preserve recovery tools'
chmod 700 "$T/recover.sh" "$T/lpatch" || fail 'cannot set recovery permissions'
: > "$T/old.md5"
while read mode path; do
    mkdir -p "$T/old/${path%/*}" "$T/new/${path%/*}" || fail 'backup directories'
    if [ -f "$ROOT/$path" ]; then
        cp "$ROOT/$path" "$T/old/$path" || fail "backup $path"
        chmod "$mode" "$T/old/$path" || fail "backup permissions $path"
        before=$(hash "$ROOT/$path") || fail "read $path"
        [ "$(hash "$T/old/$path")" = "$before" ] || fail "backup hash $path"
        echo "$before $path" >> "$T/old.md5"
    elif [ -e "$ROOT/$path" ]; then fail "not a regular file: $path"
    else echo "absent $path" >> "$T/old.md5"; fi
    if [ -f "$P/new/$path" ]; then cp "$P/new/$path" "$T/new/$path" || fail "prepare $path"; fi
done < "$P/files.list"
# Generate boot changes off to the side. Recovery precedes either HMG boot form.
cp "$T/old/system/etc/install-recovery.sh" "$T/new/system/etc/install-recovery.sh" || fail 'prepare boot'
cp "$T/old/system/etc/qb_runtime.sh" "$T/new/system/etc/qb_runtime.sh" || fail 'prepare warm boot'
saved_root=$ROOT
ROOT=$T/new
. "$P/new/data/hmgapi/lib.sh"
hook_add /system/etc/install-recovery.sh top || fail 'new boot hook'
hook_add /system/etc/qb_runtime.sh end || fail 'new warm hook'
ROOT=$saved_root
for path in system/etc/install-recovery.sh system/etc/qb_runtime.sh; do
    first=1
    while IFS= read -r line || [ -n "$line" ]; do
        echo "$line"
        if [ "$first" = 1 ]; then
            echo 'if [ -f /data/creta-base-upgrade-1.0.2.1/READY ]; then'
            echo '  /system/bin/sh /data/creta-base-upgrade-1.0.2.1/recover.sh boot'
            echo '  r=$?; if [ "$r" = 19 ]; then /system/bin/reboot; exit 0; fi'
            echo '  [ "$r" = 0 ] || exit 1'
            echo 'fi'
            first=0
        fi
    done < "$T/new/$path" > "$T/new/$path.tmp"
    mv "$T/new/$path.tmp" "$T/new/$path" || fail 'recovery hook'
done
# Update just the base inventory; preserve mods, preferences, stock and hook state.
while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
        'version '*) echo 'version 1.0.2.1';;
        'build '*) echo 'build creta-base-repair-1.0.2.1';;
        'file '*)
            set -- $line
            case "$3" in
                /system/bin/hmgapid|/system/framework/hmgapi-hook.jar) echo "file $(hash "$T/new$3") $3";;
                *) echo "$line";;
            esac;;
        *) echo "$line";;
    esac
done < "$T/old/data/hmgapi/installed.txt" > "$T/new/data/hmgapi/installed.txt"
: > "$T/new.md5"
while read mode path; do
    chmod "$mode" "$T/new/$path" || fail "missing candidate $path"
    h=$(hash "$T/new/$path") || fail "candidate hash $path"
    echo "$h $path" >> "$T/new.md5"
done < "$P/files.list"
verify_set "$T/old" "$T/old.md5" || fail 'saved base changed'
verify_set "$T/new" "$T/new.md5" || fail 'candidate damaged'
cp "$P/files.list" "$T/files.list" || fail 'save target list'
: > "$T/READY"
state prepared || fail 'save prepared state'
rollback_on_error() {
    trap - EXIT HUP INT TERM
    restore_base || echo 'Rollback incomplete. Keep USB and saved backup; do not retry.'
    exit 1
}
trap rollback_on_error EXIT HUP INT TERM
remount rw || exit 1
state applying || exit 1
# Boot recovery is installed first. Payload then changes by verified atomic renames.
while read mode path; do
    mkdir -p "$ROOT/${path%/*}" || exit 1
    cp "$T/new/$path" "$ROOT/$path.creta-new" || exit 1
    chmod "$mode" "$ROOT/$path.creta-new" || exit 1
    [ "$(hash "$ROOT/$path.creta-new")" = "$(hash "$T/new/$path")" ] || exit 1
    mv "$ROOT/$path.creta-new" "$ROOT/$path" || exit 1
    sync
done < "$P/files.list"
verify_set "$ROOT" "$T/new.md5" || exit 1
rm -f "$ROOT/data/dalvik-cache/system@framework@hmgapi-hook.jar@classes.dex"
state complete || exit 1
trap - EXIT HUP INT TERM
remount ro || true
echo 'Base repair installed. Remove USB and restart once. Mods/settings preserved.'
