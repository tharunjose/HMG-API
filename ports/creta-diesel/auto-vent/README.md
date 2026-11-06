# Passenger startup ventilation settings — queued version 1.1.0

Prepared on 6 November 2026 for installation on 7 November morning. Installed ventilation 1.0.0 already passed the driver startup and physical-control tests.

This update adds independent passenger startup enable and level 1/2/3 settings. Passenger startup defaults off. Its stored level defaults to 3 for when the owner enables it. The driver's existing enable and fan level keys are retained. Seat labels describe the physical RHD seats — driver right, passenger left.

Install the update from Nemesis → Package Store → USB tomorrow. After installation, allow at least two minutes of Android uptime before selecting HMG-API → Restart unit. Open HMG-API → Mods → Creta RHD startup ventilation → Settings and confirm the passenger switch is off. At the next normal power-on, verify driver ventilation starts as before and passenger remains off.

If passenger startup is enabled later, Save settings and Apply changes. Its selected level takes effect at the next power-on. Existing seat-climate selections and later physical control changes keep priority independently for each seat.

Host checks exercised the actual scheduler with old driver-only settings, passenger off by default, separate levels and seat selection, one seat already selected or unavailable, duplicate startup notifications and an uncertain command reply. Upgrade from 1.0.0 retained the saved driver settings bytes. Runtime DEX and signatures were verified. The updated settings screen and passenger startup path still need vehicle verification.

## Build and test

Build with the original stage08 baseline, owner key and signing engine classes, an absolute JDK17 --java path, --android-jar and --r8. Compile-only runtime stubs from ../phone-key/api-stubs are excluded from the DEX. AutoVent uses a separate StartCycle for each SeatTarget. The existing driver settings keys startup_enabled and level remain intact. New passenger_enabled is false by default and passenger_level is high.

Run test-settings.py against the actual scheduler and StartCycleTest with assertions for the native power cycle. The tests use simulated service responses. Manual test 0.1.0 demonstrated that the native driver API selected the physical left passenger. Test 0.1.1 confirmed native passenger selected the physical right driver. Version1.0.0 passed automatic driver startup and manual override on this car.
