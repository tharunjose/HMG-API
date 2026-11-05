# Cluster route-stop diagnostic

Read-only sampling for the exact SU2IFL India 260430 build. Does not change mods, properties, navigation state or cluster output. The start script returns immediately and a background worker samples the stock cluster service 60 times at three-second intervals (about three minutes plus command time). It retains only selected navigation display fields and fixed event labels; no raw logcat, destinations, road names or phone identifiers are saved. Event buffers overlap between samples; repeated labels are not distinct event counts. No hook instrumentation is added, so an absent event label does not prove an event did not occur.

1. Park, leave wireless CarPlay connected, insert USB and approve the execute prompt. The operation-success dialog means the background capture started, not that it finished.
2. Start a Google Maps route, leave its cluster instruction visible for 15 seconds, cancel it and wait 15 seconds.
3. Start a route in Hyundai's built-in navigation, wait 15 seconds, cancel it and wait 15 seconds. Note whether the stuck instruction clears.
4. Keep the drive inserted until the completion toast, approximately three minutes after capture starts (allow up to four minutes). Return the drive to the Mac.

Output: CRETA-CLUSTER-STOP, with COMPLETE.txt when finished. FAILED.txt indicates service discovery failed. Existing output is never overwritten; archive it before retrying. Do not restart the unit during capture.

## Collector correction

First vehicle attempt failed before capture: worker.txt reports `sed: not found`. Revision 2 uses the exact service name derived from the captured stock framework and a POSIX-shell-only field filter. It checks for a readable Display Type field before announcing that capture started. The failed sed-based filter is not included in this public port; active filtering uses shell builtins. Revised collector is locally tested, not yet run on the vehicle.
