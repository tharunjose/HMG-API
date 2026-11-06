# Driver ventilation at startup — manual command check

Owner selected driver seat only, level 3. The diesel map names USM setFrontSeatHeatDrvStep(int), and the captured firmware enum identifies ventilation high as 5, with heater values 6–8. The installed HMG-API seat_vent driver high command uses that same step.

This version 0.1.0 prepares the manual command check. Launch explicitly starts its manual-only service. Startup automation follows confirmation on the actual driver seat.

1. While parked in P with the engine running, insert the drive and install **Creta driver ventilation test 0.1.0** in Nemesis → Package Store → USB.
2. Open Nemesis → My Packages → Creta driver ventilation test → Launch.
3. Observe the driver seat fan and indicator. Confirm level 3 and that the passenger ventilation has not switched on.
4. Lower or switch off driver ventilation using the physical control and confirm it responds.

The script checks Park, waits up to 20 seconds for the vehicle service to become readable, sends one driver-high command and records readings before and after in the service log. A command reply alone is not proof the fan changed. It refuses a non-P or unavailable gear reading. To collect the log if needed, use hmgapid service-log creta-auto-vent test. To remove the test, uninstall the named package.

Host checks covered known-P, non-P and missing readings, exactly one command, manual-only service registration and install/apply/remove alongside the existing projection, Siri and Phone mods.

Build with build.py using the original signed stage08 wrapper, existing owner key and signing engine classes as for ../short-press-siri/build.py. This test supplies a manual script service and the declared seat_vent command through the existing vehicle hub.
