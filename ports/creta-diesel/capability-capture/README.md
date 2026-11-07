# One-shot read-only capability capture

Targets only SU2IFL.IND.0000.V010.001.260430 / su2ifl_in. No runtime map or control settings change. `build.py --help` takes the owner's private deodex directory and emits a private schema catalogue and exact-product Nemesis package.

The builder lists 2,458 signatures across 53 Binder service interfaces in this captured firmware. It selects349 primitive cached getters: USM getters whose implementations only call the cached `getUSMStatus`, plus a small set of direct-cache BCM/DATC getters. It checks the common USM cache path. Java rejects any non-get/is name, parameterized method or non-primitive/void return. No setters are called. Cached/unsupported values are not evidence of working hardware or permission to write.

Install package; launch once with a USB bearing CRETA-CAPABILITY-CAPTURE. The detached worker keeps independent reports and repeat capture directories. It records service/input/package inventory, mod/service status and selected non-EV HMG readings, invokes the cached-reader JVM with a timeout, and copies selected stock settings/USM/climate app files with MD5 comparison. Commands that fail or time out are recorded; partial results survive. COMPLETE means collection reached its end, not that every feature is supported. Copies and reports stay private on the owner's USB. It intentionally excludes raw logcat, navigation destinations, accounts and wireless credentials.

`CRETA_JAVA=/path/to/java python3 test.py` checks JVM mock results, unknowns, product gate, setter refusal, normal/partial capture, existing output preservation and timeout behavior. Static-shell and DEX035 checks accompany packaging. These do not prove access to native Binder services on the car.

The inventory is the Android-visible surface, not a complete ECU/CAN inventory. Metadata includes write signatures for later review but never tests them. No ACC, AEB, parking, engine, HVAC or seat commands are executed.
