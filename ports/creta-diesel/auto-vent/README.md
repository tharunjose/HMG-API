# Automatic RHD driver ventilation — 1.0.0

Owner-confirmed on 6 November 2026 — creta-auto-vent 1.0.0 passed the requested startup and physical-control test. The physical right driver seat starts ventilation at the default level 3, the passenger seat stays off, and reducing or switching off ventilation with the physical control keeps that selection.

The owner confirmed manual test 0.1.1 controls the physical right driver seat at level 3 and the seat controls work. This update requests that same native seat at startup.

1. Install **Creta RHD startup ventilation 1.0.0** from Nemesis → Package Store → USB as an update to the existing ventilation test.
2. Remove the USB. After Android has been running at least two minutes, use HMG-API → Restart unit. The new hooks load on that restart.
3. With the car parked and fan off, do a normal car shutdown, wait for the screen to go dark, then start again. Allow up to 60 seconds for driver ventilation. Confirm the passenger seat stays off.
4. Lower or switch off driver ventilation and wait 30 seconds. It should keep your selection.

In HMG-API → Mods → Creta RHD startup ventilation → Settings, use **Ventilation at startup** and **Startup fan level**. Choose level 1, 2 or 3 (default 3), Save settings and Apply changes. The next power-on cycle uses the new level. Ventilation or heat already selected at startup is preserved.

The trigger is the native ACC power-on state, not an engine-speed reading. It includes a head-unit restart while ACC is on. It waits five seconds initially, then allows at most twelve readiness checks at five-second intervals. Off cancels pending work. It makes at most one seat-setting request per cycle and does not keep enforcing the level.

To disable it, turn off Ventilation at startup and save/apply, or disable this mod. To remove it, uninstall only Creta RHD startup ventilation. Normal physical seat controls set the current fan level.

Host tests cover native ACCON 0 versus LOGICON 1, duplicate broadcasts, power-off cancellation, stale tasks, bounded retries, three level mappings, and upgrade/removal alongside the current Siri, Phone and wireless mods. DEX inspection confirms the physical RHD driver candidate uses the owner-confirmed passenger-labelled USM method. Automatic startup and the physical-control check passed the owner’s test on this car.

## Source and build

AutoVent uses the existing mapped automotive-service loader hook to listen for the car's sticky ACC status broadcast in system_server. Its seat reads and request follow the mapped BCM and USM APIs used by HMG-API’s vehicle hub. Native logical passenger maps to the physical RHD driver on this exact car, confirmed in manual test 0.1.1. Earlier version 0.1.0 selected the left passenger seat and was superseded.

Build from the same stage08 baseline with the owner key, signing engine classes, JDK17 --java path, --android-jar and --r8 as for ../phone-key/build.py. That folder’s compile-only API stubs are reused and excluded from the output. Compile StartCycle.java and StartCycleTest.java with javac and run the test with assertions. The manual scripts remain as the reference for the confirmed seat command.
