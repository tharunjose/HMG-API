# Creta startup screen skip — 1.0.0 trial

Exact target: `SU2IFL.IND.0000.V010.001.260430`, `su2ifl_in`. The owner returned three matching SystemUI captures on 7 November 2026. Their APK/ODEX checksums and USB-to-Mac copies were verified. This trial is host-tested; Android startup, normal vehicle wake, and screen behavior are not yet vehicle-verified.

## Behavior

The normal final branch of `com.android.systemui.consentscreen.D.start()` calls the existing private `dc()` acceptance method instead of `T(0)`, which creates the screen. `dc()` sets `sys.boot.enabled_screen` and `sys.boot.confirm_screen`, then broadcasts `AGREE_USER_LICENSE`. Controller initialization, receiver registration, update-in-progress checks, factory/welcome paths, manual profile selection, and password handling are unchanged. This is a startup-screen change, not a timer or repeated button press. A profile password can still require its own screen.

The initial branch match follows [Cabinwright's documented skip approach](https://github.com/cabinwright/tweaks/blob/5c703f9b200952bacb1e2cd9546b9b9bc5ae0e8b/systemui/patch.py). The Creta implementation uses a same-size patch directly on the captured ODEX. The stock APK exceeds the installed lpatch's 8 MiB input limit, so rebuilding that APK would require a core tool change. This version needs no core update or APK replacement.

Only nine bytes differ: five bytes within one six-byte invoke instruction, plus the four-byte optimized DEX Adler-32 checksum. File size, all other instructions, original DEX signature identifier, ODEX dependency tables, and register maps are preserved. Dalvik updates the optimized DEX checksum while preserving the original signature identifier; see [AOSP DexFile.cpp](https://android.googlesource.com/platform/dalvik/+/android-4.4.2_r1/libdex/DexFile.cpp). A full deodex comparison confirms exactly one call change across all 626 classes. No decompiled/reassembled manufacturer code is shipped.

## Install and remove

1. While parked, install **Creta startup screen skip 1.0.0** from NEMESIS → Package Store → USB. If the separate **Creta startup agreement dismissal** fallback is installed, remove it first. The installer rejects coexistence.
2. After installation succeeds, wait until the head unit has been awake for at least two minutes, then use HMG-API → Restart unit once. The HMG-API **Allow mods to dismiss it** toggle can stay off: this patch does not call the permission-gated dismissal command.
3. Check whether normal startup reaches the home screen without the agreement. Confirm the status bar, radio, camera, wireless CarPlay, and steering controls work. Check the next ordinary car off/on separately; report whether the screen appears or briefly flashes.

To undo, uninstall **Creta startup screen skip** in NEMESIS and restart the head unit. HMG-API keeps the exact stock ODEX backup and restores it when this mod is removed. If removal reports an apply error, use HMG-API → Apply changes and confirm it succeeds before restarting. Never use **restore all** just to remove this trial; that also affects unrelated mods.

The installer refuses a different firmware, APK or ODEX, another unowned patched ODEX, an installed dismissal fallback, an alternate SystemUI Dalvik cache file, or a failing base hook-map check. A refusal is a reason to inspect the message, not bypass the check. The patch suppresses the manufacturer's normal agreement notice; it does not change driving restrictions.

## Build and validation

`build.py --help` lists the private input paths. Use the verified stage08 wrapper and existing owner key; keep the key outside the repository. `reference.json` pins source hashes and the instruction location. The builder checks the exact files, generates a hash-only recipe, verifies the reconstructed ODEX, signs the mod, and verifies the same signer as the existing wrapper. It emits the NEMESIS ZIP and a build report. The built package contains the recipe, metadata, signature, and existing wrapper scripts, with no manufacturer APK/ODEX.

Run `test.py --workspace /path/to/private/Nemesis` with Python and `unicorn==2.1.4`. The private fixture layout is defined in that script. Tests execute the installed ARM lpatch with an in-memory syscall environment, deodex both stock and patched files with API18 and the stock framework, and exercise the installed-base host engine. Covered: exact patch output, corrupted-source rejection, all-class comparison, wireless coexistence/settings preservation, idempotent apply, removal restoration, trial rollback, wrong firmware/stock rejection, and USB preinstall guards. Host mode does not execute Android or prove vehicle behavior.
