# Fast startup-agreement dismissal fallback — 1.0.1

The preferred path is an exact-firmware SystemUI skip. Capture stage31 first. This fallback is prepared if a full skip cannot be matched on the Creta.

Version1.0.1 replaces the fixed12-second sleep. It immediately checks Android boot completion, factory Binder availability and gearP, then sends HMG-API’s native startup_notice dismiss request as soon as all are ready. If readiness is missing it checks once per second, with at most90 checks. A non-P reading skips dismissal. There is no extra grace sleep on the ready path. Actual elapsed time depends on the car and service-call latency.

The existing installer permission snapshot/restoration and HMG-API’s once-per-hub-start guard remain. This candidate is tied to Android startup. Actual screen effect and normal warm-wake behavior need vehicle validation. Native factory screen-state reversibility has not been established.

Tests passed the zero-sleep ready path, unavailable Android/factory/P timeout, non-P no-send case, single request, permissions, installer-failure restoration, engine upgrade/removal and existing-mod coexistence.

Build with build.py using the original stage08 wrapper, owner key and signing engine. Run test.py. The root service declares gear.park and startup_notice, starts with Android and exits after the bounded operation. Version1.0.0 is superseded.
