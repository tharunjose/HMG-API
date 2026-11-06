# Optional manual-cancellation trial for SU2IFL India 260430

The optional wireless wrapper 2.5.0.2 contains mod 2.5.0-diesel.2. On a stop after active generic CarPlay guidance, it sends a single no-symbol request through the existing Hyundai navigation display API. It tracks which route component supplied the main turn. An initial idle update from a different component must not remove the active main turn. The cluster may clear the arrow or return to its compass. This is a local test candidate. On-car cancellation, arrival and wireless CarPlay after the update still need verification.

## Build

Use the signed output of the existing diesel builder and the same owner key. The reference file pins the original hooks JAR. Use baksmali 2.5.2 and the smali 2.5.2 Java classpath with its dependencies, plus JDK 17 and the compiled signing engine from the original builder. Run test-source.py with --source pointing to the pinned Creta EV source checkout. Run build-trial.py --help for its inputs. Use the original stage 08 wrapper for --baseline and a new ZIP filename for --output.

The builder verifies the original signature, vehicle gate and hooks hash, applies the edits, then reassembles and disassembles the Dalvik bytecode. It compares the class list, every other disassembled class and untouched methods within the changed class. It signs the candidate with your existing owner key. The Java-side regression first fails against the baseline, then passes against the source equivalent. These checks cover the display component that owns the turn, repeated stops, session disconnection, and a registered custom renderer. The runtime behavior on the car remains to be tested.

## Trial and recovery

1. While parked, insert the USB with Android running. Open Nemesis → Package Store → USB. Select Wireless CarPlay Creta diesel trial, version 2.5.0.2, and install the update.
2. Wait for installation success before removing the USB. If it fails, keep the exact error and stop.
3. In HMG-API, tap Restart unit. Wait for CarPlay to reconnect. If the app reports a pending apply or failed map, stop and record the message.
4. Start a Google Maps route through CarPlay while parked. Wait until the turn appears, manually cancel the route, then watch the main cluster for 15 seconds. The test passes if the stale turn disappears. Report blank, compass, or still stuck.

For a quick fallback, switch Cluster turns OFF in the wireless mod, save settings, apply, and restart. To restore the original wireless package, uninstall only the Wireless CarPlay Creta diesel trial mod through Nemesis, then reinstall the original stage 08 package and restart. Retain the HMG-API base. The host fixture verified candidate removal and baseline reinstall. Vehicle rollback remains untested.

## Compass handoff trial (stage 17)

Stage 16 returned all 45 readable samples on the exact target with 2.5.0-diesel.2 installed. Samples 0–9 showed NO SYMBOL; sample 10 CALC ROUTE; 11–13 NO ROUTE GUIDANCE(COMPASS); 14 DIRECTION TO DESTINATION; 15–44 NO ROUTE GUIDANCE(COMPASS). The owner saw the compass return after the native navigation test. There were no button-press timestamps. Together with the previous capture this identifies the target main display mode; the stage 15 blank symbol is not equivalent to compass idle. Both reported angle fields were zero throughout this parked capture. It does not prove a live heading reached the CarPlay process.

Stage 17 (wrapper 2.5.0.3, mod 2.5.0-diesel.3) keeps the stage 15 ownership checks. When generic CarPlay guidance ends it sends exactly one type 8 main-display frame if it has a live Hyundai navigation heading no more than 30 seconds old. The angle is mirrored and rounded to the cluster's 22.5-degree steps. It leaves the secondary compass/trip frame to the car. Invalid, missing, sticky or stale heading cannot generate a compass request; stage 15's no-symbol fallback remains. There are no delayed writes. Host-tested; actual delivery of the heading and the resulting display are unverified on the vehicle.

Build from the same signed stage 08 baseline with --compass, --android-jar (Android API 16 stubs or equivalent), --r8 (Google R8 8.3.37 JAR), and --cluster-stub (the upstream wireless mod’s tools/aaturns/stubs/hmgapi/hook/Cluster.java). Put JDK 17 on PATH. Only DieselCompass is added from javac/D8 output; build stubs are excluded. Run test-compass.py with the same cluster stub, and test-source.py with --source as above. Install 2.5.0.3 from USB, restart and test cancelling Google Maps without opening native navigation. Success means the compass returns with no spinner.
