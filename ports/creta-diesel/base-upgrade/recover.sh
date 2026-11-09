#!/system/bin/sh
umask 077
ROOT=${ROOT:-}
T=$ROOT/data/creta-base-upgrade-1.0.2.1
. "$T/transaction.sh"
case "$(cat "$T/state" 2>/dev/null)" in
    complete) [ "$1" = boot ] && exit 0;;
    rolled-back) exit 0;;
    prepared|applying|restoring) ;;
    *) echo 'No recoverable base trial'; exit 1;;
esac
restore_base || exit 1
[ "$1" != boot ] || exit 19
