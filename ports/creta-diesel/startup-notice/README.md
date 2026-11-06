# Startup agreement dismissal — queued 1.0.0

Prepared for the owner’s requested startup-agreement dismissal on SU2IFL.IND.0000.V010.001.260430. Installation and the first vehicle test are queued for 7 November morning.

Install **Creta startup agreement dismissal 1.0.0** from Nemesis → Package Store → USB, after the queued ventilation1.1.0 update. The installer enables HMG-API's Startup notice permission and the permission for this mod's startup_notice command, saving the earlier permission choices.

A one-shot Android startup service waits12 seconds, then requests the built-in startup_notice dismiss command only after reading gear P. If P is unavailable it waits for up to20 readings at3-second intervals; if the car is already outside P it skips the request. HMG-API also checks permission, Park and once-per-vehicle-hub-start. This uses the exact mapped factory hideConsentScreen method.

The captured factory implementation calls its existing hard-key listener with value1 and broadcasts HIDE_CONSENT_SCREEN. It has no paired show function in the inspected interface. Actual dismissal timing and the screen state after removal have not been tested on this car. Removal restores the saved HMG-API permission choices. Execution is tied to Android startup; the normal off/on test must establish behavior on the owner’s usual car wake.

Tomorrow, restart the head unit once after installing both queued packages, keeping the car parked. Observe whether the agreement disappears without a tap after about12 seconds. Also check the usual next car startup. Record an unchanged agreement or any unexpected screen action and return the service log if it fails. Stop further retries until that evidence is reviewed. Do not manually restart the dismissal service repeatedly.

The package can be disabled or removed through HMG-API/Nemesis. Service log — hmgapid service-log creta-startup-notice dismiss.

## Checks and build

The signed payload declares gear.park and startup_notice only, with an Android-start one-shot service. Host fixtures verified install/apply/remove alongside ventilation1.1.0, Phone, Siri and wireless mods. Script tests cover validP, nonP, missing readings, one request, retained original permission flags, repeated installation and restoration on install failure. The upstream command tests verify its additional permission, Park and once-per-start guard. The native on-car path is pending.

Build using build.py with the original signed stage08 wrapper, existing author key and compiled signing engine. Run test.py for wrapper/service behavior. Manufacturer binaries and signing keys stay outside this source directory.
