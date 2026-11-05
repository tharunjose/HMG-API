# Removal and recovery

These procedures are based on the installed packages’ removal code. Host tests restore original bytes; full removal and boot recovery have **not** been tested on this car. Preserve private stock captures and package versions before installation.

## Cluster issue only

HMG-API → Mods → Wireless CarPlay + AA — Creta diesel trial → Cluster turns OFF → Save settings → Apply changes → Restart unit. Keep wireless bridge/audio enabled if they work. This is the first rollback for stale cluster directions.

## Remove projection, then base

In NEMESIS → My Packages, uninstall the wireless diesel package first. Restart and check wired CarPlay. Remove HMG-API afterward if needed, then restart. Preserve exact error messages and backups if restoration fails; do not manually delete the backups or layer another projection mod over a failed restore.

For optional SmartTube/codec packages, uninstall SmartTube before its Video Codec Fix dependency.

## NEMESIS shortcut lost

Selecting Setup in NEMESIS’s Trigger button picker changes the actual trigger; it is not another setup wizard. To regain entry, put the contents of `usb/open-manager` at the USB root and insert it with Android running. Then select Navigation as the trigger if you want triple-NAV back. Reinstalling NEMESIS preserves preferences and did not reset this choice during development.

## Android does not start

`usb/disable-hooks` disables HMG-API’s preload for the next boot and restarts the unit. It requires the existing NEMESIS USB handler to run. Use a separate USB with only that stage. If Android cannot prompt, an empty `NEMESIS.emergency` file at USB root enables the upstream emergency execute path. This is an explicit recovery action, not a file to leave on a normal installer drive.

A `RECOVERY-DONE.txt` marker prevents repeat rebooting; preserve and move it out of the USB root before an intentional later reuse. If Android returns, remove the wireless package and base normally to restore their changes. If the handler does not respond, do not assume this is a full recovery method; no tested firmware image or bootloader/MICOM recovery procedure is included.
