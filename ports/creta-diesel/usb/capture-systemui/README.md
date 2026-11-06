# Exact-firmware SystemUI capture for agreement-screen skipping

The owner prefers entirely skipping the startup agreement. The existing capture does not include SystemUI. The published EV6 method changes the SystemUI consent controller, which must first be identified in this Creta’s own files.

Install **Creta SystemUI source capture 1.0.0** from the prepared USB. Keep the USB plugged in and choose Nemesis → My Packages → Creta SystemUI source capture → Launch. It copies the current SystemUI APK and adjacent ODEX, when present, to a new CRETA-SYSTEMUI folder on that USB and verifies each MD5. Wait for “SystemUI copied and checked. Reconnect USB to Mac.” Return the drive for analysis.

The collector reads the car’s files and creates the USB report. It checks the exact product and the capture marker before running, and preserves earlier reports under numbered names. Captured manufacturer binaries remain private. After collecting, the capture package can be uninstalled.

Host fixtures checked the APK/ODEX copies, checksum comparison and preservation of a previous report.
