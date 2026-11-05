# Setup: one exact Indian Creta diesel firmware

## 1. Check eligibility before changing anything

The tested car is a 2024 Indian Creta diesel AT with factory wired Android Auto and CarPlay. Screen software: `SU2I_FL.IND.S5W_M.V010.001.260430`. Android product: `SU2IFL.IND.0000.V010.001.260430`. Onebin: `su2ifl_in`. Hardware: `SU2IFL.IND.STD_AVN_G5_WIDE.007.007`. Android 4.4.2/API 19/ARMv7.

Use Setup → General → SW Info/Update to compare the visible identifiers. Do not publish your VIN. Product/stock checks below must also pass. If identifiers or hashes differ, stop and open a compatibility report; do not edit the gates to make installation succeed. A shared model year, screen size or firmware date is not enough.

Stay parked with stable power for installation. If keeping a diesel engine running for power, remain outdoors. Root and projection changes can break infotainment, including cameras and audio. Recovery here depends on NEMESIS still being available; no full-system recovery image has been tested. Review [recovery](RECOVERY.md) before installing.

## 2. Install NEMESIS and preserve stock

The tested NEMESIS version is 1.16.7 from [commit 345f171](https://github.com/xwtk/hmg_nemesis/tree/345f171850c35742f84f0fbe511d0b7ab50364fc). Follow its pinned [DSP execution check](https://github.com/xwtk/hmg_nemesis/blob/345f171850c35742f84f0fbe511d0b7ab50364fc/01-DSP-OTA-troubleShooter.md) and [installation guide](https://github.com/xwtk/hmg_nemesis/blob/345f171850c35742f84f0fbe511d0b7ab50364fc/03-Install-and-Uninstall.md). Confirm the check passes on your unit before the installer. This repository does not redistribute or replace the NEMESIS exploit/installer.

Keep factory radio, camera, steering controls and wired CarPlay working before proceeding. Remove conflicting projection packages using their own removal procedures and verify the stock baseline. Do not stack this port with Leafia, generic wireless projection, Enhanced Phone Projection or another TBT package.

On a FAT32/exFAT USB drive, copy the **contents** of `ports/creta-diesel/usb/collect-stock` to its root. With Android running, insert it and approve Execute. Wait for operation completion. Return the USB to your computer and retain `CRETA-STOCK` privately. Its `COMPLETE.txt` marks collection completion; `missing.txt` means inputs were absent and the builder may refuse them. The files are selected factory software, not a complete vehicle backup. Keep them out of GitHub and public issues.

The collector is newly product-gated in this public version; the same allowlisted file collection was used for the original private baseline. NEMESIS is installed before collection, but HMG-API and projection mods must not yet have modified those stock inputs.

## 3. Build the diesel packages

Follow [BUILD.md](BUILD.md) using your own capture. A build must match all 42 reference stock hashes and the exact product. It produces separate `07-base` and `08-wireless` USB stages. Keep all ZIPs intact. Never copy several stage descriptors to the USB root at once.

## 4. Install the base and check its map

1. Copy the contents of the generated `07-base` directory to the USB root. It contains `NEMESIS.data` and `packages/hmgapi.zip`. Insert with Android running and approve installation. This base installer is for a fresh HMG-API installation; stop on a refusal.
2. Remove the USB. Open NEMESIS → My Packages → HMG-API → Launch → Restart unit. Leave Android running for at least **two minutes** after it returns; rapid restarts can trigger the hook boot guard.
3. Open HMG-API → Settings → Hook map → **Check the map on this car**. The expected result is **424/424**. Use the supplied map. Do not use “Map this car from its files”: that mapper borrowed an incorrect EV Bluetooth helper in our offline comparison.
4. Restart again after allowing the two-minute startup interval. Recheck radio, camera, steering controls and wired CarPlay. If any check fails, stop before wireless installation.
5. Optional status export: use `usb/status` as the USB stage. It creates `CRETA-HMG-STATUS`; retain it privately and review/redact before sharing.

## 5. Confirm the physical Wi-Fi radio

A Wi-Fi XML or driver file is not proof of a working radio. On the test car the driver initialized the SDIO radio during boot and unloaded it again. The normal Wi-Fi menu was hidden.

The tested way to open the client screen was `com.hkmc.wifisettings/.WifiClientSettings`. The supplied `usb/open-wifi-client` helper opens that screen on the exact product. Enable the Wi-Fi checkbox and confirm nearby networks actually appear. The public helper only opens the activity; it does not reproduce the earlier diagnostic experiments. A working scan established radio operation on the test car, including 2.4/5 GHz evidence.

**Engineering Mode → Hotspot Activation is not the radio power switch.** On this firmware it changed `wifi.hotspot.subscription`. During development that value was restored to the original false state. Do not toggle it as a general Wi-Fi fix, and do not change firewall/APN settings to try to find an SSID. An unrelated nearby SSID is not proof the car has started an access point.

If the screen will not open or scanning does not work, stop before wireless installation and report the exact behavior. No fabricated Wi-Fi marker or forced feature bypass is included.

## 6. Install wireless CarPlay

1. After the base/map/stock checks and Wi-Fi scan pass, copy the generated `08-wireless` contents to USB. Insert and approve installation. The preinstall rechecks stock files and calls `verify-map`; the engine checks the exact product and Wi-Fi evidence. Stop on any failure.
2. Remove the USB. Open HMG-API → Mods → Wireless CarPlay + AA — Creta diesel trial. Keep cluster turns **OFF** initially; leave Bluetooth bridge and Wi-Fi audio enabled. The wrapper installs and applies the mod; if the app reports pending changes, apply them before restarting.
3. Restart the unit and wait two minutes after startup. On the iPhone enable Bluetooth, Wi-Fi and Siri. Pair from the car’s Device Connections / Phone Projection screen and allow CarPlay, with the iPhone USB cable disconnected.
4. Test music, calls and Siri while parked. On the next normal start, confirm automatic reconnection. Recheck stock radio, camera and steering controls.
5. If an old pairing prevents connection, one fresh pairing can be tried: remove the car in iPhone Bluetooth/CarPlay settings and the phone in the car’s connection list. Repeated failure needs a report, not repeated reinstallations.

Keep the custom base/map and wireless package versions together. Do not accept upstream package updates or manufacturer firmware updates as a troubleshooting step; different software needs renewed validation. A separately generated signing key gives a different mod author identity and is not a drop-in update to someone else’s signed build.

## 7. Optional Google Maps directions in the cluster

Stock Hyundai navigation must already display directions on your cluster. The tested phone was an iPhone using Google Maps through CarPlay.

In HMG-API → Mods → Wireless CarPlay + AA — Creta diesel trial, enable only **Cluster turns**, Save settings → Apply changes → Restart unit. The existing label says “unsupported…keep off” because the original package excluded cluster output from its initial validation. This remains an experimental option: directions and arrival clearing now have one-owner confirmation, but manual cancellation left a stale instruction.

Cancel any built-in navigation route, start Google Maps while parked, and select the cluster’s navigation page with the usual controls. Compare what is shown. Do not install the Creta EV RHD renderer or EV routing to “complete” the diesel setup: these have not been validated here. Roundabouts, distances, route changes and long-term stability need more evidence.

Rollback for the cluster option: set it OFF → Save settings → Apply changes → Restart unit. Wireless bridge and audio can stay enabled. See [RESULTS.md](RESULTS.md) for the open route-stop investigation.

## Optional apps

Video Codec Fix 2.1 installed and preserved radio/CarPlay audio on the test car. SmartTube 32.68.6 launches but could not resolve `www.youtube.com`; playback is not confirmed. These are separate [upstream packages](https://github.com/KramerTech/gen5-SmartTube), not required for CarPlay. Head-unit internet access is separate from wireless CarPlay. Do not install an unvalidated network modification just to resolve this.
