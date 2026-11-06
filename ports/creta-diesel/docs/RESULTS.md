# Results and unresolved work

As of 6 November 2026; one owner, one 2024 India Creta diesel AT, full Android product `SU2IFL.IND.0000.V010.001.260430`. These are owner-reported functional results, with local code and file checks where noted. No broad compatibility claim is made.

## Confirmed on the car

NEMESIS 1.16.7; local base 1.0.1.2; map 424/424; wireless wrapper 2.5.0.1 containing mod 2.5.0-diesel.1. Wireless CarPlay connects, music/audio/calls/Siri work, and it reconnects after a normal restart. Stock radio/camera/steering controls remain functional. Google Maps directions appear in the cluster after enabling the existing TBT setting. Reaching the destination clears the directions.

## Manual cancellation remains unresolved

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
