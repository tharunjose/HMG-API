# RHD driver ventilation correction — 0.1.1

The owner’s 0.1.0 test switched on the physical left passenger seat. On this Indian RHD Creta, the native API’s driver label therefore does not identify the physical driver seat. The correction uses the opposite native label, passenger, as the right-driver candidate. That side still needs physical confirmation.

1. Switch off the left passenger ventilation using the normal seat control.
2. Park in P with the engine running. Install **Creta RHD driver ventilation test 0.1.1** from Nemesis → Package Store → USB as an update to the existing test.
3. Open My Packages → Creta RHD driver ventilation test → Launch.
4. Confirm the physical right driver seat reaches ventilation level 3 and the left passenger seat stays off. Lower or switch off the driver fan with its physical control.

This manual-only test sends one request after a valid Park reading. Startup automation is pending confirmation of the right seat. Installation, upgrade and removal were exercised on a host fixture. The script regression verifies the opposite native label and that non-P and unavailable gear readings send no command.

The service logs include raw API labels for both front seats. Native seat_vent passenger high currently means the right-driver candidate in this mod. To revert, uninstall only this ventilation test package.

Build with build.py using the original stage08 signed wrapper, owner key and signing engine classes. Run test-script.py for the seat selector and Park checks. The diesel native enum VENT_HIGH is 5. Native names and enum values were inspected before the first test, but their physical left/right meaning was established by the owner’s observation.
