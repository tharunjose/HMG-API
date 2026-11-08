# Installed diesel mods: upstream update review — 9 November 2026

Recommendation: selectively port and test updates; do not use Update All or install the EV release directly. This is a source/metadata assessment and preparation queue, not a completed diesel upgrade. No new executable package was placed on USB and no vehicle installation was performed.

## Baseline and evidence

Scope: owner’s 2024 India Creta diesel AT, SU2IFL.IND.0000.V010.001.260430. Installed state is reconstructed from the returned 7 November capture plus later owner confirmations and matching prepared package manifests; this is not a new live inventory. The base is the custom 1.0.1.2 wrapper with 424 verified map points. Wireless is 2.5.0-diesel.3, richer renderer 1.3.1-diesel.1, Extras 1.1.1-diesel.1, standalone Siri/Phone 1.0.0, startup ventilation 1.1.0, consent skip 1.0.0, custom battery Watchdog/panel 1.0.0, shortcut 1.1.0, Tilepad 1.1.1, codec 2.1 and SmartTube 32.68.6. Wrapper versions and embedded mod versions are separate.

Live GitHub API/repository fetches and the public Nemesis catalog were read on 8–9 November. The cached GitHub release webpage omitted Creta 1.4.0; the live API and fetched tag confirm it. Canonical HMG-API now redirects from VysseCodes to Open-HMG. Release versions from different forks are not interchangeable. Remote branch heads are development snapshots, not automatically released updates.

## Disposition

| Component | Verified upstream target | Decision |
|---|---|---|
| HMG-API base | Canonical release 1.0.2; Creta EV release 1.4.0 bundles base 1.0.11 | Highest-priority diesel preparation: boot fix, vehicle-read completion, socket cleanup, callback handling. Preserve diesel maps, stock hashes, settings, signer and recovery. Do not install either stock upstream base over this custom port. |
| Wireless projection | Creta 2.5.3 | Port candidate after base review. Adds current-turn refresh and session/sign-in/manual-connect handling; preserve our tested route-stop/compass behavior. |
| Richer renderer | Creta 1.3.2 | Port candidate. Native lane-image suppression while phone guides and straight fallback for unknown-direction roundabouts; retain diesel/RHD eligibility and regression checks. |
| Projection Extras | Creta 1.1.7, requires HMG-API >=1.0.11 | Follow base/wireless, with standalone Siri/Phone ownership preserved and new Bluetooth/call behavior isolated. Upstream explicitly has no iPhone-drive validation for its new CarPlay changes. Our spontaneous factory voice activation is unresolved, not a proven upstream fix. |
| Tilepad | Store 1.1.4; GitHub release 1.1.6 | HOLD. Both explicitly declare !hmgapi. Verified the 1.1.6 release ZIP against GitHub’s asset SHA256; its preinstall also checks HMG-API traces. Do not remove HMG-API or strip the conflict to obtain this launcher update. Existing 1.1.1 coexistence is not a compatibility guarantee. |
| SmartTube | 32.71-gen5w.1, store 32.71.1 | Available; keep paused with owner’s Wi-Fi/SmartTube work. Adds a rule excluding the car modem. Review settings/signing retention before an eventual update. It is not a Wi-Fi authentication fix. |
| Video codec / shortcut | Codec 2.1; NEMESIS shortcut 1.1.0 in latest canonical release | No newer release established; retain. |
| Nemesis core | Latest fetched source header remains 1.16.7 | No core upgrade established. Latest repository commit updates separate packages. Portal core-update query did not complete, so store updater status is unverified. |
| Custom Watchdog, battery panel, ventilation, Siri/Phone, consent skip | Local diesel implementations | No direct upstream replacement. Keep working behavior and settings. Original zpoon Watchdog release is 0.6.0 (store 0.6.0.66); development VERSION 0.7.0 is not a release. Its app is a different package and not an update to our custom shell service. |
| Enhanced Phone Projection | Store 1.23, CVEV.*.260507 / cvev_* | Do not layer over this HMG projection stack. Relevant improvements have been ported into Creta EV’s source; review those derived changes instead. |

## Battery lead requiring focused validation

[Commit d1f3290](https://github.com/sirishant/HMG-API/commit/d1f32904589ceaa44ddb392ddae231a79a363c9f), base 1.0.8, changes vehicle reads to stop after the expected answer lines rather than waiting for socket close. Its upstream diagnosis is values arriving but the command ending in error and the Java client discarding them. [Commit f31473c](https://github.com/sirishant/HMG-API/commit/f31473cb6d290b442bdbe8cf4daf704f0cd10291), base 1.0.9, shuts down and closes accepted socket descriptors to prevent leaks/restarts. Both remain in the 1.4.0 tag.

This closely matches our captured SOC 79 plus combined read exit=1; it is not yet proof of the diesel root cause. SOC is charge, not SOH. Test single-field and multi-field reads, fragmented responses, missing/truncated lines, timeouts, client disconnects and repeated reads before accepting a port. The upstream fallback can accept some newline-terminated partial replies: do not blindly treat an incomplete response as success or weaken the Watchdog’s checks. Verify the existing widget and Watchdog after a repaired data path before replacing them. No additional Vehicle Settings capture is needed to start this investigation.

## Preparation queue and release boundary

1. Freeze the working diesel package hashes and settings; implement a deliberate base migration with full rollback. Existing builder rejects an already installed base and cannot simply be repointed at 1.0.11. Review update signing and exact-firmware map changes.
2. Validate the base’s transport/startup fixes first, retaining incomplete-response rejection and custom mod permissions. Confirm new map entries against private diesel OEM captures and test upgrade, failure recovery and restoration off-car.
3. Port wireless/renderer improvements with route start/cancel/arrival and compass regression coverage. Port Extras separately, resolving overlap with standalone Siri/Phone and testing both connected/disconnected projection states.
4. Only then produce an ordered USB batch with old-version rollback packages and one consolidated parked checklist. Batch preparation does not mean enabling every change simultaneously: base first, projection next, Extras last with clear stop points.

No EV routing, EV health/range emulation, new climate commands, ADAS changes or replacement launcher is included in this upgrade scope. Owner Wi-Fi/SmartTube pause is preserved. No new car visit is requested by this review.

## Primary sources

- [Creta EV 1.4.0 release](https://github.com/sirishant/HMG-API/releases/tag/creta-1.4.0) and [pinned install/update guide](https://github.com/sirishant/HMG-API/blob/creta-1.4.0/docs/creta/README.md).
- [Canonical HMG-API 1.0.2](https://github.com/Open-HMG/HMG-API/releases/tag/v1.0.2).
- [Tilepad 1.1.6](https://github.com/KramerTech/gen5-Tilepad/releases/tag/v1.1.6) and [live store metadata](https://portal.xwtk.cloud/nemesis/v1/store/packages/tilepad).
- [SmartTube release](https://github.com/KramerTech/gen5-SmartTube/releases/tag/v32.71-gen5w.1), [codec 2.1](https://github.com/KramerTech/gen5-codec-patch/releases/tag/v2.1).
- [Original Battery Watchdog 0.6.0](https://github.com/zpoon/gen5w-BatteryWatchdog/releases/tag/v0.6.0), [Enhanced Projection metadata](https://portal.xwtk.cloud/nemesis/v1/store/packages/enhanced.projection), [Nemesis source header](https://github.com/xwtk/hmg_nemesis/blob/70e72d2dce4b/Sources/native/nemesis.h).
