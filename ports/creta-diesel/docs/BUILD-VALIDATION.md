# Public-builder validation — 5 November 2026

The portable builder was run locally using the exact original private stock capture, pinned upstream source/release inputs and a new test signing key. No vehicle was modified by these tests.

- Every file inside the generated base package matches the previously installed base package contents byte-for-byte.
- Every file inside the wireless mod matches the original local mod except its signing manifest/signature, as expected for a new author key. Payload binaries, hook JAR, settings, recipes and eligibility are unchanged.
- Upstream input signature and newly generated signature verify successfully.
- Host install/plan/apply/remove passes with the captured factory feature configuration and permissions. TBT ON/OFF produces no extra system-file changes. Removal restores the fixture's original system hashes.
- Wrong model, wrong firmware, missing Wi-Fi evidence, missing stock and modified-stock rejection pass in their respective builder/engine/preinstall tests.
- Extraction regression reproduces the original 0644 permission failure and confirms the corrected preinstall; wrong product and changed stock still fail.
- Corrected cluster collector mock test records 60 samples with no sed, rejects unreadable service fields and excludes private sample text.
- Source check validates 424 map points, 42 stock gates, duplicate-map consistency and shell/Python syntax.

The public packaging code is locally validated. No second vehicle or public-build signing identity has been tested on a car. No claim of deterministic ZIP/signature bytes is made: ECDSA signatures and per-owner keys vary. The original test car's working result remains one vehicle on one exact firmware.
