# Indian Creta ADAS feasibility review

Read-only review, 7 November 2026, exact firmware SU2IFL.IND.0000.V010.001.260430. No ADAS-changing mod or controller commands are provided.

## What the sources establish

The [Indian Creta manual](https://www.hyundai.com/content/dam/hyundai/in/en/data/connect-to-service/owners-manual/2026/creta-cretanline-jan-2024-to-present.pdf), printed7-5/7-6, describes a combined Forward Safety setting and separate warning timing. Basic, Junction Turning and Direct Oncoming are grouped. It documents four factory SCC headway choices with persistence (7-56). This does not establish separate toggles for every advertised detection scenario or arbitrary headway calibration.

[Generic Gen5W documentation](https://ownersmanual.hyundai.com/ivi/STD_GEN5W/AVNT/USA/English/010_Settings_car2.html) includes Warning Only on equipped vehicles. This is not evidence the Indian Creta supports that option.

The [period SX(O) brochure](https://www.hyundai.com/content/dam/hyundai/in/en/data/brochure/cretabrochuree.pdf) restricts SCC with Stop & Go to automatic transmissions. The manual diesel's ADAS/AEB equipment does not by itself establish a supported ACC activation or retrofit path.

## Firmware limits

The firmware exposes multiple generations of USM assistance getters. A cached invalid result is not equivalent to a disabled feature, and method availability is not proof of hardware support. Per-field encoded values need OEM menu and validity interpretation before they can be described as settings.

The broad capability collector omitted HKMC_VehicleSetting APK/ODEX: it captured the Settings_W launcher, while the package inventory places the actual vehicle-settings UI in a separate app. A future narrow, hash-verified, read-only supplement should fill that gap. No such supplement has been staged by this research update. No repeat broad capture is requested.

## Community review

Reviewed19 mod manifests across Open-HMG/HMG-API main c3bc7edd559e96278d266d391e62886ff136e628 and sirishant/HMG-API creta-su2iev e1664558ab715dbbb8416b5d21693d7e41bab6bc. Also checked xwtk/hmg_nemesis tree345f171850c35742f84f0fbe511d0b7ab50364fc and targeted public searches. No matching independent ADAS/warning-only/manual-ACC implementation was identified in this scope. This is not a claim that none exists anywhere; external store packages and private Discord discussions were not comprehensively audited.

Warning-only feasibility remains unconfirmed. Next analysis needs the vehicle-settings menu eligibility and value mappings, with OEM support evidence before any change to safety-related behavior. Do not infer support by forcing a menu visible or trying guessed values.

## Supplement prepared — 8 November 2026

Vehicle Settings collector1.0.0 is now built and host-tested (14fixtures). It copies the actual VehicleSetting APK/ODEX, SettingsCommon APK/ODEX and hkmc/framework resource APKs, with source/copy hash verification and retained prior output. No ADAS commands or settings changes. This is local preparation only; physical USB copy and car collection remain pending. See [capture source and instructions](../usb/capture-vehiclesettings/README.md).
