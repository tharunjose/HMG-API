# Results and unresolved work

As of 7 November 2026; one owner, one 2024 India Creta diesel AT, full Android product `SU2IFL.IND.0000.V010.001.260430`. These are owner-reported functional results, with local code and file checks where noted. No broad compatibility claim is made.

## Owner results — 7 November 2026

On the same exact Indian diesel firmware, the owner reports:

- The agreement screen stayed absent on a normal car start. Stock camera, radio and steering remained normal.
- Richer renderer `1.3.1-diesel.1` installed successfully. Two Google Maps route start/cancel cycles, near-turn and roundabout graphics, distance bar, arrival and return to compass worked.
- Baseline steering Phone opening still worked after a call in this run. The earlier intermittent post-call failure was not reproduced. Steering end-call did not work; the standalone Phone handler does not implement active-call hangup.
- Projection Extras `1.1.1-diesel.1` installed. One unsolicited factory voice-command UI activation occurred while CarPlay was active. No button press was reported. Cause is unproven; post-Extras Phone checks remain untested and full session validation is not claimed.

The pre-trial capability capture returned successfully: 24 files copied and verified privately, six OEM file hashes matched the capture manifest, and 349 cached-getter results included two missing-method errors. It predates renderer/Extras installation and cannot diagnose the later voice event. Battery SOC was readable through both the HMG path and a direct cached BCM getter; panel, Watchdog status and alert behavior remain unverified. A combined reading command returned nonzero despite emitting values, which is a diagnostic lead rather than justification to ignore transport errors.

The Extras port has no input declarations or AA Call-key hook. It does shorten DiPO's Siri-end next-screen check from 800ms to 300ms; the exact firmware has the matching stock path. A timing interaction is only a hypothesis. No speculative voice or call-control patch was staged.

Raw vehicle data, OEM binaries and identifying logs remain private. These are one owner's reported functional checks, not broad compatibility or long-term stability claims. Next checks are consolidated for a convenient visit; Wi-Fi/SmartTube remain paused.

## Earlier results and investigation history

The sections below preserve previous states; use the dated result above for current status.

## Confirmed on the car

NEMESIS 1.16.7; local base 1.0.1.2; map 424/424; wireless wrapper 2.5.0.1 containing mod 2.5.0-diesel.1. Wireless CarPlay connects, music/audio/calls/Siri work, and it reconnects after a normal restart. Stock radio/camera/steering controls remain functional. Google Maps directions appear in the cluster after enabling the existing TBT setting. Reaching the destination clears the directions.

On 6 November 2026 the owner reported success on the stage 17 parked test. After manually cancelling Google Maps on iPhone CarPlay, the cluster returned to the compass without starting Hyundai navigation. The tested wireless package was 2.5.0.3 (mod 2.5.0-diesel.3), with Cluster turns enabled, on SU2IFL.IND.0000.V010.001.260430.

## Manual cancellation on earlier versions

A parked Google Maps cancellation left the previous cluster instruction visible. Later clearing after a short drive was explicitly confirmed to be **arrival at the destination**, not manual cancellation. Treat these as different cases. On 6 November, the owner reproduced the Google Maps manual-cancellation issue and confirmed that starting a route in the head unit’s Hyundai navigation, then cancelling it, returns the cluster to normal. This is a temporary clearing workaround, not a repair of the CarPlay cancellation path.

A likely code gap is `CpTurns.stop()`: it clears HUD data and calls `display.guidanceEnded()` only if a car-specific display is registered. This diesel uses the generic path. The EV renderer has separate guidance-ended handling, but that is not proof that installing it on the diesel is correct. No fix has been installed and no captured trace yet proves the cause.

The diagnostic in `usb/cluster-stop-check` is read-only, with selected navigation fields and fixed event labels. First attempt failed before recording because the car lacks `sed`. Revision 2 uses shell builtins and the exact stock service name; a readable-display preflight must pass. It passed local mocked tests, but the owner reports that revision 2 also displayed a failure message. The retrieved report identifies `printf: not found`: the replacement filter could not emit its fields. Revision 3 uses echo and has a regression test that disables both printf and sed, reproduces the old failure, and passes the corrected capture. It remains untested on the vehicle. These are collector portability defects, not evidence of a broken cluster service.

## Wi-Fi findings

The physical radio existed but the regular menu was hidden. The actual Wi-Fi client activity opened and scanning worked. Engineering “Hotspot Activation” changed a subscription property instead of starting the radio. This incorrect early troubleshooting direction was corrected; it should not be repeated. The radio observation is more specific than finding a Wi-Fi XML, driver file or nearby SSID.

## Local verification

- Original stock capture: 42 selected system files, compared with USB copies using SHA-256.
- Offline map: 424 points, all 36 declared wireless hooks covered. Three names differ from the EV reference: HomeSetting `cu` instead of `cs`, PhoneProjection status `lN` instead of `lP`, Bluetooth helper `iO` instead of `iP`.
- Native CarPlay Core/Audio/Utils match the EV reference; recipe byte checks and in-memory patch checks passed against the captured copies.
- Host engine fixture: install/plan/apply/remove with actual factory feature configuration and permission files; original system hashes restored after removal. Model/firmware/no-Wi-Fi rejection tested.
- TBT setting ON/OFF: host plan/apply succeeds without additional system-file changes beyond the wireless baseline. Upstream synthetic CarPlay turn tests pass, including Google/India turn handling and HUD clearing; the vehicle cancellation issue shows why those tests do not establish cluster correctness.
- NEMESIS extraction: original failure reproduced with all ZIP members at 0644; setting helper permissions first fixes preinstall. Modified stock/wrong-product rejection still works.

The public builder is a portable adaptation of the private builder. It keeps the same vehicle payload/recipe code, adds fixed reference-stock checks, and generates the builder’s own author key. Its validation record is summarized in BUILD-VALIDATION.md.

## Not established

Petrol/other trims/firmware; wireless AA on this car; detailed cluster maneuvers/roundabouts; long-term reliability; on-car uninstall/recovery. SmartTube starts but cannot resolve YouTube; internet and playback remain deferred. The codec package installed and stock/CarPlay audio still worked afterward.

Do not report the earlier collector failure as an HMG-API or vehicle fault: it was a missing command in our helper. Do not report the arrival success as a manual-cancellation fix.

## Completed capture and cancellation trial — 6 November 2026

Revision 3 completed all 60 samples over about seven minutes. The initial cluster display was the compass. Samples 3–8 showed direction to destination. At sample 9 the trip distance became zero with an invalid distance unit and the compass degree returned, but the main display continued to indicate direction to destination. At sample 18 the direction and unit matched the pattern seen during the native route. At sample 21 the main display returned to the compass and stayed there through sample 59. The phase interpretation follows the requested test order. There were no owner action timestamps or definitive callback markers. This supports testing the main-display stop handling but leaves delivery of the Google Maps cancellation event unverified.

The optional wireless wrapper 2.5.0.2 contains mod 2.5.0-diesel.2. On a stop after active generic CarPlay guidance, it sends a single no-symbol request through the existing Hyundai navigation display API. It tracks which route component supplied the main turn. An initial idle update from a different component must not remove the active main turn. The cluster may clear the arrow or return to its compass. This is a local test candidate. On-car cancellation, arrival and wireless CarPlay after the update still need verification.

## First result from the symbol-clear trial

The owner reports that the direction cleared after cancelling Google Maps but a loading animation persisted. The main display did not visibly return to its ordinary idle state. The stage 15 candidate requests NO SYMBOL after guidance stops, whereas the earlier diesel capture recorded NO ROUTE GUIDANCE (COMPASS) after native cancellation. The observed animation still needs a post-trial cluster snapshot to identify its actual display type. The diesel firmware contains a receiver for the native navigation heading, but the live availability and angle for compass handoff have not been validated during this trial. Stage 16 captures the displayed fields across the animation and a native route cancellation and checks the installed hooks file against the owner’s two trial versions.

## Native idle confirmed; compass handoff trial prepared

Stage 16 returned all 45 readable samples on the exact target with 2.5.0-diesel.2 installed. Samples 0–9 showed NO SYMBOL; sample 10 CALC ROUTE; 11–13 NO ROUTE GUIDANCE(COMPASS); 14 DIRECTION TO DESTINATION; 15–44 NO ROUTE GUIDANCE(COMPASS). The owner saw the compass return after the native navigation test. There were no button-press timestamps. Together with the previous capture this identifies the target main display mode; the stage 15 blank symbol is not equivalent to compass idle. Both reported angle fields were zero throughout this parked capture. It does not prove a live heading reached the CarPlay process.

Stage 17 (wrapper 2.5.0.3, mod 2.5.0-diesel.3) keeps the stage 15 ownership checks. When generic CarPlay guidance ends it sends exactly one type 8 main-display frame if it has a live Hyundai navigation heading no more than 30 seconds old. The angle is mirrored and rounded to the cluster's 22.5-degree steps. It leaves the secondary compass/trip frame to the car. Invalid, missing, sticky or stale heading cannot generate a compass request; stage 15's no-symbol fallback remains. There are no delayed writes. Host-tested; actual delivery of the heading and the resulting display are unverified on the vehicle.

Owner-confirmed on 6 November 2026 — a short tap of the steering voice button opens Siri with creta-siri-short 1.0.0 installed. The physical hold worked before this install.

## Steering phone button

Owner-confirmed on 6 November 2026 — a short steering phone-button press opens CarPlay Phone with creta-carplay-phone 1.0.0 installed. Incoming-call answering with the button remains to be checked.

## Seat ventilation mapping

The owner requested startup ventilation on the right driver seat at level3. The 0.1.0 manual test using native seat_vent driver high activated the physical left passenger seat. Version0.1.1 selects the opposite native seat label for another manual test. Physical right-seat confirmation and startup automation are pending.

The owner confirmed corrected manual version0.1.1 works on the physical right driver seat. Automatic version1.0.0 is prepared with configurable level1/2/3 and a startup enable switch. The automatic start and manual override checks are pending.

Owner-confirmed on 6 November 2026 — creta-auto-vent 1.0.0 passed the requested startup and physical-control test. The physical right driver seat starts ventilation at the default level 3, the passenger seat stays off, and reducing or switching off ventilation with the physical control keeps that selection. Other level selections have host coverage; a separate vehicle test changing each startup level was not reported.

Version1.1.0 is prepared with independent physical RHD passenger startup enable and level controls, passenger off by default. Upgrade and scheduler tests passed on the host. Vehicle installation and optional passenger startup verification are pending.

Startup-agreement dismissal1.0.0 is prepared using HMG-API’s native startup_notice command, Park and once-per-start guard. Permission restoration and bounded script/engine tests passed on the host. The factory screen behavior and routine car-wake timing are pending owner verification.

The owner prefers complete startup-screen skipping. On 7 November 2026, three returned SystemUI captures matched exactly, with verified capture hashes and local copies. The exact normal-start branch matches the documented Cabinwright approach. [Creta startup screen skip 1.0.0](../skip-consent/README.md) changes the normal screen-construction call to the existing factory acceptance method through a nine-byte ODEX/checksum patch. The stock APK and HMG-API core remain unchanged. The actual installed ARM patch tool, 626-class comparison, installed-base apply/remove/rollback, coexistence, and refusal checks passed. The signed trial is prepared for parked vehicle testing; startup and warm-wake behavior are not yet verified on the car.

Fallback dismissal1.0.1 remains an alternative, with no fixed12-second delay. It must not run alongside the full-skip trial. The HMG-API startup-notice permission is not needed for the ODEX skip.
