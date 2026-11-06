# Creta 12V Battery Watchdog trial

A read-only alerts service for the diesel head unit. The factory screen displays a warning when a valid reported 12V state of charge falls below 60%, when it drops by at least 15 percentage points across a session gap, or when the charge decreased over a previous session lasting 20 minutes to 24 hours. These rules use the defaults from [zpoon’s Battery Watchdog](https://github.com/zpoon/gen5w-BatteryWatchdog). This is a separate diesel implementation.

The service checks once per minute while Android is running, skips reads when the display reports sleep, and compares sessions after a gap of at least ten minutes. A gap can include time the head unit was powered off. The service takes no measurements while the unit is powered down. It uses the existing HMG-API mapping of the factory getBatSoc getter. Invalid readings are ignored. One overwritten private checkpoint holds the comparison values and alert state. There is no sample history or USB export.

The [original NEMESIS store package](https://portal.xwtk.cloud/nemesis/v1/store/packages/battery.watchdog) lists 260507 and 260903. This trial is gated to SU2IFL.IND.0000.V010.001.260430 and verifies the installed map before install. Vehicle data and toast delivery still need a parked check.

1. Park, insert the USB, and install **Creta 12V Battery Watchdog** from NEMESIS → Package Store → USB. If the old logger was installed separately, remove it through My Packages first.
2. After two minutes with the head unit awake, select **My Packages → Creta 12V Battery Watchdog → Launch**. It reports a fresh reading or that it is waiting. There is no need to lower the battery charge to test.
3. Remove the trial through My Packages if desired.

For a source build, run `build.py --help` in this directory. The builder takes the host HMG-API engine classes, Java, your existing private mod signing key and a new output path. `python3 test-watch.py` exercises the service against synthetic samples.
