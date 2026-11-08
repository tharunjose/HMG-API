# Creta Vehicle Settings capture — read only

Prepared 8 November 2026 for SU2IFL.IND.0000.V010.001.260430 / su2ifl_in. This fills the missing ADAS menu-code capture; it does not enable or disable any ADAS function.

## At the next combined car visit, after USB preparation

1. While parked, install **Creta Vehicle Settings capture (read only) 1.0.1** from Nemesis → Package Store → USB.
2. Keep USB inserted. Open My Packages → Creta Vehicle Settings capture → Launch. Allow about two minutes. Wait for “Vehicle Settings copied and checked.” If incomplete, keep the saved results; no repeated retry is requested.
3. Continue the existing CarPlay/Phone, battery and Tilepad checks. Return the USB once afterward.

No Apply Changes or head-unit restart is required for this collector. It copies HKMC_VehicleSetting.apk/.odex, SettingsCommon.apk/.odex, hkmc-res.apk and framework-res.apk from fixed system paths. It checks firmware/variant and source readability, preserves older reports under numbered directories, and verifies source-before, copied-file and source-after MD5 values. COMPLETE.txt is written only after all six required files verify. Missing files, malformed hashes, source changes or copy errors leave an incomplete report. Capture output is CRETA-VEHICLESETTINGS[-n] on the marked USB. Keep OEM files private.

The only runtime app broadcast is a completion/failure toast. There are no vehicle-service calls, settings changes, actuator commands, remaps, or personal-data directory reads. Installation adds a removable collector package; capture writes its report only to USB.

## Host verification

Fourteen fixture cases passed: successful six-file capture, prior-output retention, wrong product, wrong variant, absent marker, absent hash tool, missing main ODEX, missing dependency, copy failure, hash mismatch, hash-tool failure, empty hash, malformed hash and source change. Shell syntax and ZIP contents verified. Native car run remains untested.

Source build: `python3 build.py --out /local/output`; tests: `python3 test.py`. Put the resulting marker at USB root and package under packages, merging its entry into the existing NEMESIS.data list rather than replacing unrelated entries.

## 1.0.1 packaging correction

The 1.0.0 installation attempt failed and appeared incompatible. Its 73-character short description violates Nemesis’s 64-character limit; the native metadata parser reproduces the rejection. The Store also marks failed metadata reads as incompatible. Version 1.0.1 shortens that description; firmware gates and collector scripts are unchanged. The corrected descriptor passes the native parser and reports full compatibility for the specified product. Vehicle installation and collection still require confirmation.

Regression check: `python3 test_descriptor.py --nemesis-source /path/to/hmg_nemesis/Sources`. This compiles Nemesis’s actual INI and metadata parsers, checks the generated ZIP descriptor, and reproduces the old rejection.
