# Creta EV 1.3.1: diesel compatibility review

Reviewed 6 November 2026. **A plausible port candidate, not a tested diesel upgrade.** The public builder and installed diesel baseline remain pinned to Creta EV 1.3.0. No new map, vehicle payload, USB installer or release was produced by this review.

## Exact source boundary

- Existing baseline: sirishant/HMG-API `3a81b461125ba373c2f842829f24a577b78147e5`, `creta-1.3.0`.
- Reviewed target: sirishant/HMG-API `e1664558ab715dbbb8416b5d21693d7e41bab6bc`, `creta-1.3.1`.
- Target components: HMG-API 1.0.5, wireless-carplay-aa 2.5.1, projection-extras 1.1.4. The upstream tag changes 56 files from the baseline; this is not a count of missing functional fixes.
- Diesel scope: only `SU2IFL.IND.0000.V010.001.260430`, screen software `SU2I_FL.IND.S5W_M.V010.001.260430`, with the existing stock-hash gates.

Sources: [release notes](https://github.com/sirishant/HMG-API/releases/tag/creta-1.3.1), [source comparison](https://github.com/sirishant/HMG-API/compare/3a81b461125ba373c2f842829f24a577b78147e5...e1664558ab715dbbb8416b5d21693d7e41bab6bc). Upstream credits and license remain applicable. The EV release itself is scoped to SU2IEV; it is not a diesel installer.

## Findings and disposition

| Area | Source finding | Diesel disposition |
|---|---|---|
| Startup | New detached `hmgapid boot`, per-boot marker, `boot.sh`, and NEMESIS boot service address the upstream startup delay. | Candidate for the base upgrade. Treat daemon, scripts, manifest and service as one change; test install, restart and recovery together. No diesel timing result yet. |
| Call button | `CarPlayKeys` replaces the no-call message with DiPO's Phone request while handling the call key. This applies from the car's own screens with no active call. On the CarPlay screen, the existing hook-switch behavior is retained. | Useful candidate, but narrower than “open Phone from every screen.” Test both screen contexts and preserve answer/end-call behavior. The release author explicitly marks the CarPlay buttons untested with an iPhone. |
| Voice button | Projection extras swaps short press to phone assistant and hold to car assistant. Version 1.1.4 removes the setting condition, making the swap unconditional when the mod is enabled. | Covers the short-press Siri proposal in source. Verify both press lengths, including without projection connected; not yet a diesel result. |
| Session and calls | New `CarPlayCalls` repeats DiPO's Bluetooth-to-CarPlay handover after activation when a session began during a Bluetooth call. `Switch` loads it unconditionally. | Separate experimental behavior, not a necessary consequence of button remapping. First button trial should isolate or explicitly gate this untested handover change. |
| Wireless and cluster | Wireless 2.5.1 removes the test toggle for retry/power-off rules, whose prior default was already on. `CpTurns.java` is unchanged. EV renderer changes concern roundabout icons and near-turn distances. | Existing wireless behavior is the baseline. This release does not supply a demonstrated diesel manual-cancellation fix. Keep cluster directions off by default; do not add the EV renderer or EV-routing mods to solve it. |

## Static hook check against the diesel capture

Compared the three changed EV map files (`dipo.json`, `framework.json`, `gpm.json`) with the existing private diesel deodex trees. For each added point, resolved the owning class through the target hook catalogue, checked a unique class file, and matched method parameters, return type and static flag, or field type and static flag. Catalogue string anchors were checked where supplied. No manufacturer code or private capture is included here.

**24 of 24 additions matched:** four classes, eighteen methods and two fields. The signatures below are source compatibility evidence only; this is not runtime `verify-map`, a complete rerun of the mapper's discovery constraints, or proof of vehicle behavior.

| Catalogue | Added entries matching the diesel capture |
|---|---|
| DiPO: 8 | `dipo.activity.dispatch_key_event`; `dipo.call_utils`; `dipo.call_utils.is_bt_call`; `dipo.service.call_key`; `dipo.service.display_map`; `dipo.service.display_music`; `dipo.service.display_phone`; `dipo.service.no_call_message` |
| Framework: 8 | `framework.mode_info`; `framework.mode_info.is_available`; `framework.mode_key_dispatcher.context`; `framework.mode_key_dispatcher.mode_state`; `framework.mode_key_dispatcher.request_shortcut`; `framework.mode_key_dispatcher.send_broadcast_key_event`; `framework.mode_manager_state`; `framework.mode_manager_state.get_mode_info` |
| GPM: 8 | `gpm.key_listener.all_keys`; `gpm.main_activity`; `gpm.main_activity.on_key_up`; `gpm.main_activity.on_resume`; `gpm.receiver_service.on_create`; `gpm.receiver_service.send_osd_message`; `gpm.receiver_service.start_music_view`; `gpm.receiver_service.start_navi_view` |

Adding these to the diesel map would produce **448 points**, retaining all 424 current entries and the three previously corrected diesel names. No map was changed during this review.

Projection extras 1.1.4 declares 35 hooks. Eleven are absent from the current diesel map; the candidate additions cover all eleven. The additional class, field and call targets are also included above. Wireless 2.5.1 declares 36 hooks, all already present in the diesel map. These counts do not validate the code paths behind those hooks.

## Upgrade and release blockers

1. **Builder and upgrade path.** `scripts/build.py` pins the old source/assets, hard-codes their filenames and versions, and intentionally rejects an existing HMG-API installation in the base preinstall. Changing `reference/upstream.json` alone cannot make an upgrade. Preserve exact firmware and stock checks, the executable-permissions fix, backups and restoration. A deliberate upgrade path must recognize legitimate installed files without treating arbitrary modified system files as stock.
2. **New base and map required for the full mod.** Projection extras 1.1.4 requires HMG-API >=1.0.5 and lists only the EV model. Port eligibility explicitly and add/verify the candidate diesel hooks; do not lower the dependency merely to force installation. Preserve the original authorship when producing a derived mod.
3. **Release signing is distinct from mod signing.** Target `UsbUpdates.java` pins sirishant's release signer. Re-signing a mod or repacking the EV base does not make that base accept this fork's future base updates. A self-updating diesel distribution needs a deliberate release identity and a rebuilt engine with matching trust configuration, or documented NEMESIS-only base updates. Keep private keys outside the repository.
4. **Off-car and parked validation.** Before an installable prerelease, check package extraction, wrong-product/modified-stock rejection, first install, upgrade, interrupted apply/recovery, and removal/restoration. Verify the expanded map on the car, then check startup, reconnection, audio, camera, radio, short/held voice presses, call key on both screens, and ordinary call handling. Test any call-handover experiment separately. Host checks cannot substitute for these vehicle checks.
5. **Release scope.** A source-only prerelease fits the current publication scope. Signed installable packages remain a later decision after preparation and validation. Keep EV routing, EV battery emulation, native music apps and cluster gauge redesign outside this port update. Manual cluster cancellation remains open; consult [RESULTS.md](RESULTS.md).

## Proposed implementation order

1. Prepare a candidate base/map upgrade with the 24 additions, installer migration and signing decisions above; retain the working 1.3.0 package as the rollback baseline.
2. Validate the base on its own, then port the button changes with untested call handover isolated. Preserve stock actions outside the intended projection context.
3. Publish a separately versioned diesel prerelease only with explicit tested/unverified results, checksums and installation/upgrade/removal instructions. Suggested first tag: `creta-diesel-0.1.0-beta.1`; no tag or release has been created.

The existing [build workflow](BUILD.md) still creates the original exact-firmware trial. This review does not authorize reporting the candidate as installed, working, or generally compatible with Indian Cretas.
