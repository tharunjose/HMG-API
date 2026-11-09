#!/system/bin/sh
# Base-only transaction. Fixed paths/manifests come from the verified builder.
# ROOT is exclusively for the off-car fixture; entry points unset it on the car.
umask 077
ROOT=${ROOT:-}
T=$ROOT/data/creta-base-upgrade-1.0.2.1
hash() { result=$("$LP" md5 "$1") || return 1; set -- $result; [ ${#1} = 32 ] || return 1; echo "$1"; }
state() { echo "$1" > "$T/state.new" && mv "$T/state.new" "$T/state" && sync; }
remount() {
    [ -n "$ROOT" ] && return 0
    /system/xbin/nemesis remount "$1" >/dev/null 2>&1 && return 0
    "$T/old/system/bin/hmgapid" remount "$1" >/dev/null 2>&1
}
verify_set() {
    while read expected path; do
        if [ "$expected" = absent ]; then [ ! -e "$1/$path" ] || return 1
        else [ "$(hash "$1/$path")" = "$expected" ] || return 1; fi
    done < "$2"
}
restore_base() {
    [ -f "$T/READY" ] || { echo 'No verified base backup'; return 1; }
    LP=$T/lpatch
    verify_set "$T/old" "$T/old.md5" || { echo 'Backup integrity failed'; return 1; }
    # Never overwrite unrelated changes made after this transaction.
    while read old path; do
        new=
        while read h f; do [ "$f" = "$path" ] && new=$h; done < "$T/new.md5"
        if [ -e "$ROOT/$path" ]; then
            have=$(hash "$ROOT/$path") || return 1
            [ "$have" = "$old" ] || [ "$have" = "$new" ] || { echo "Changed since trial: $path"; return 1; }
        else
            [ "$old" = absent ] || { echo "Missing since trial: $path"; return 1; }
        fi
    done < "$T/old.md5"
    remount rw || return 1
    state restoring || return 1
    while read expected path; do
        if [ "$expected" = absent ]; then rm -f "$ROOT/$path" || return 1
        else
            cp "$T/old/$path" "$ROOT/$path.creta-new" || return 1
            mode=
            while read m f; do [ "$f" = "$path" ] && mode=$m; done < "$T/files.list"
            [ -n "$mode" ] && chmod "$mode" "$ROOT/$path.creta-new" || return 1
            [ "$(hash "$ROOT/$path.creta-new")" = "$expected" ] || return 1
            mv "$ROOT/$path.creta-new" "$ROOT/$path" || return 1
        fi
    done < "$T/old.md5"
    verify_set "$ROOT" "$T/old.md5" || return 1
    rm -f "$ROOT/data/dalvik-cache/system@framework@hmgapi-hook.jar@classes.dex"
    state rolled-back || return 1
    remount ro || true
    echo 'Saved base restored. Restart the head unit.'
}
