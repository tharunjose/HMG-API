# Credits, source and reports

This fork builds on substantial upstream work:

- [xwtk/hmg_nemesis](https://github.com/xwtk/hmg_nemesis), tested at `345f171850c35742f84f0fbe511d0b7ab50364fc`: root entry, manager, USB/package handling.
- [VysseCodes/HMG-API](https://github.com/VysseCodes/HMG-API): hook runtime, engine, mapping and projection infrastructure.
- [sirishant/HMG-API](https://github.com/sirishant/HMG-API/tree/3a81b461125ba373c2f842829f24a577b78147e5), Creta EV release `creta-1.3.0`: the source/release baseline used here. Its EV-specific support does not itself cover diesel Cretas.
- [KramerTech/gen5-codec-patch](https://github.com/KramerTech/gen5-codec-patch) and [gen5-SmartTube](https://github.com/KramerTech/gen5-SmartTube) for the optional apps, which are not bundled here.

The local contribution is the diesel map/packaging, exact-build gates, helper-permission fix, tests and owner documentation. Existing upstream license and copyright notices remain applicable. The fork is under the repository’s AGPL-3.0 license. There is no claim of endorsement by upstream authors or Hyundai.

## A useful public report

Include model/year/engine/transmission/region, full screen software and Android product (with VIN hidden), package versions, which step failed, and whether wired projection and stock functions still work. For cluster issues distinguish departure, manual cancellation, arrival, phone disconnect and switching to factory navigation. Report what was actually observed rather than assuming another owner’s result applies.

Do not attach full `/data` dumps, stock apps/libraries, VIN, serial numbers, phone numbers, SIM/IMEI, credentials, pairing information, signing keys or unredacted logs/screenshots. Keep private vehicle captures outside this repository. Metadata and selected hook map signatures/hashes can be reviewed without uploading manufacturer binaries.

The repository includes inherited EV mods because this is a fork. Changes for a new diesel firmware need its own map/stock checks and evidence; do not widen model gates solely to suppress a rejection. Fixes can be proposed here first. No upstream pull request has been sent as part of publishing this work.
