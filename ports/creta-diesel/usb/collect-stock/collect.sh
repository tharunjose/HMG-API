#!/system/bin/sh
# NEMESIS runs this with the USB root as cwd. Copy only the listed factory software.
export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin
set -e
umask 077
[ "$(getprop ro.build.product)" = "SU2IFL.IND.0000.V010.001.260430" ] || exit 1
[ -f ./NEMESIS.data ] && [ -f ./stock-files.txt ] || exit 1
out=CRETA-STOCK
mkdir "$out"
getprop ro.build.product > "$out/product.txt"
while IFS= read -r src; do
    case "$src" in *..*) exit 2 ;; esac
    case "$src" in
        /system/app/*.apk|/system/app/*.odex|/system/framework/*.odex|/system/framework/*.jar|/system/lib/*.so|/system/bin/app_process) ;;
        *) exit 2 ;;
    esac
    if [ -f "$src" ]; then
        dst=$out$src
        mkdir -p "${dst%/*}"
        cp "$src" "$dst"
    else
        echo "$src" >> "$out/missing.txt"
    fi
done < ./stock-files.txt
echo 'collection finished; see missing.txt for unavailable inputs' > "$out/COMPLETE.txt"
sync
