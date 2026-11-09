# Creta diesel base repair 1.0.2.1 (base only)

Upgrades an installed diesel base 1.0.1.2 (runtime 1.0.1, commit `3a81b46`) in place. Map, mods, settings and stock backups are kept. Exact-firmware gate: `SU2IFL.IND.0000.V010.001.260430` / `su2ifl_in`.

**Status: tested off-car only. Not yet installed on a car.**

## What it brings in

- Upstream HMG-API 1.0.2 boot fix (`boot-1.0.2.patch`): `hmgapid boot` returns at once, runs once per boot, and NEMESIS gets a boot service.
- Accepted vehicle-socket descriptors are fully closed (`socket-close.patch`). The approach follows the Creta EV fork's base 1.0.9.
- Vehicle reads require a complete answer (`strict-response.patch`, `response.h`). Partial, empty, truncated, duplicate or extra lines fail; they do not count as success.

Only 9 files are replaced (`files.list` in the package). Before any change, the installer checks the installed files and map against the verified baseline, then:
- saves a backup;
- adds a recovery guard to both boot scripts first;
- replaces each file by a verified rename.

A failure or power loss part-way restores the saved base on the next boot. `creta-base-rollback` restores it by hand.

## Build

```
python3 prepare.py --repo <HMG-API checkout> --out <new dir>
# hmgapid (static ARM): sh core/hmgapid/build.sh in a clang/lld container
python3 build-runtime.py --source <dir> --java <jdk17 java> --android <android.jar> --r8 <r8lib.jar>
python3 build.py --base <verified stage07 hmgapi.zip> --source <dir> --out <dir>
```

## Off-car tests

- `test-response.c`: the reply parser, split at every byte boundary.
- `test-daemon.py`: the real ARM daemon and client under qemu-arm. Covers boot, plus complete, fragmented, partial, malformed and repeated replies.
- `test-transaction.py`: the real install shell on a fixture. Covers success; refusal for wrong product, variant, base or map, or a pending journal; a write failure at each of the 9 steps; and power loss at each step. Mods, settings and state must survive install and rollback. A strict `cp` stand-in rejects flags, and every file's permission is checked.

Results (9 Nov 2026): parser PASS, daemon 23/23, transaction 24/24. All staged diesel mods' `hmgapi` ranges accept 1.0.2.1.

## Not yet verified

- On-car install with toolbox `cp`/`mv` and NEMESIS remount.
- Whether `battery12v.soc` now reaches the battery panel and Watchdog.
- How NEMESIS Manager lists HMG-API 1.0.2.1 after its sync.
