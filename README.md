# HMG-API — Hyundai Creta ICE India

**Wireless CarPlay working on one 2024 Indian Hyundai Creta diesel AT.** This is a direct fork of [VysseCodes/HMG-API](https://github.com/VysseCodes/HMG-API). The `creta-ice-india` branch documents and packages the exact-build port developed from [sirishant’s Creta EV work](https://github.com/sirishant/HMG-API), itself based on [VysseCodes/HMG-API](https://github.com/VysseCodes/HMG-API). Installation uses [NEMESIS by xwtk](https://github.com/xwtk/hmg_nemesis).

This is an experimental community fork, not a Hyundai release or a claim of compatibility with all Indian Cretas. **Start with the [diesel setup guide](ports/creta-diesel/docs/SETUP.md).** There is no universal installer: this public snapshot ships source, maps and local build tools. It does not ship the owner’s private vehicle files or signing key.

## Exact tested configuration

| Item | Tested value |
|---|---|
| Car | 2024 Hyundai Creta diesel AT, India; wired AA/CarPlay already supported |
| Head unit | Gen5W / Android 4.4.2 / API 19 / ARMv7 |
| Screen software | `SU2I_FL.IND.S5W_M.V010.001.260430` |
| Android product | `SU2IFL.IND.0000.V010.001.260430` |
| Hardware identifier | `SU2IFL.IND.STD_AVN_G5_WIDE.007.007` |
| Onebin | `su2ifl_in` |
| NEMESIS | 1.16.7 |
| HMG-API base | Upstream binaries 1.0.1; local packaging 1.0.1.2 |
| Wireless mod | Upstream code 2.5.0; local mod 2.5.0-diesel.1; NEMESIS wrapper 2.5.0.1 |

The screen software and Android product use different spellings. Match the full identifiers and stock hashes. **Petrol, other transmissions, other years, regions and firmware builds have not been tested.** The date `260430` alone is insufficient.

## Owner-reported results — 5 November 2026

| Feature | Result |
|---|---|
| Wireless CarPlay, music/audio, calls, Siri | Working |
| Automatic CarPlay reconnection | Working after a normal restart cycle |
| Radio, camera, steering controls | Working with wireless CarPlay active |
| Google Maps through CarPlay → cluster | Directions display; clearing on arrival at destination works |
| Manually cancelling Google Maps | **Open issue:** previous instruction remained on the cluster in a parked test |
| Wireless Android Auto | Not validated on this diesel; community screenshots are not this car’s test evidence |
| Video Codec Fix 2.1 | Installed; radio and CarPlay audio still work |
| SmartTube 32.68.6 | Launches; YouTube DNS lookup fails; internet/playback unresolved |
| On-car uninstall/recovery; long-term reliability | Not established; host restoration tests are not on-car recovery tests |

Cluster turns remain **off by default** while a new owner establishes the wireless baseline. The optional cluster trial is documented with its limitations. No EV routing, charging, battery emulation or EV-specific cluster renderer was installed on the diesel.

## What this branch adds

- A 424-point diesel hook map, with three names corrected from the EV reference; the supplied map passed **424/424** on the test car. It remains `mapped`, not upstream-certified.
- A local package builder with pinned upstream downloads, exact product and stock-byte gates, and private per-builder signing.
- The fix for NEMESIS extracting ZIP files as mode `0644`: enable helper execution **before** running the preinstall checks.
- An owner guide, Wi-Fi discovery notes, rollback instructions and a privacy-filtered cluster diagnostic. The diagnostic’s first version failed because the unit lacks `sed`; the corrected version is locally tested, awaiting its vehicle result.

## Start here

1. [Compatibility and installation](ports/creta-diesel/docs/SETUP.md)
2. [Build locally](ports/creta-diesel/docs/BUILD.md)
3. [Evidence, limitations and open issues](ports/creta-diesel/docs/RESULTS.md)
4. [Recovery and removal](ports/creta-diesel/docs/RECOVERY.md)
5. [Contributing and upstream credits](ports/creta-diesel/docs/CONTRIBUTING.md)

The inherited repository contains EV and other-car mods. Their presence does **not** make them appropriate for this diesel. Use the dedicated port workflow, not the inherited generic installer or an unmodified Creta EV release. The [original upstream README](README-upstream.md) is retained for architecture context.

License: [AGPL-3.0](LICENSE). Existing upstream copyright and license notices remain in place. This branch is based on sirishant/HMG-API commit `3a81b461125ba373c2f842829f24a577b78147e5` (`creta-1.3.0`); later upstream changes have not been integrated or vehicle-tested here.
