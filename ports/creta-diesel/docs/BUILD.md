# Build your own exact-firmware USB packages

This is a source-only port snapshot. Requirements: Git, Python 3.9+ and JDK 17 (`java` and `javac` on PATH). macOS was used for local validation. The builder compiles the upstream desktop signing engine; it does not need an Android SDK and does not recompile the upstream vehicle binaries.

## Inputs

- Your private `CRETA-STOCK` folder from the setup guide, with `product.txt` and 42 expected system files. All must match `reference/stock.md5`.
- Two upstream release ZIPs and source pinned in `reference/upstream.json`.
- A private signing key path outside this repository. A key is created if absent. Keep the same key for later builds; do not share or upload it.

From the repository root:

```sh
python3 ports/creta-diesel/scripts/fetch.py
python3 ports/creta-diesel/scripts/build.py \
  --stock /absolute/private/path/CRETA-STOCK \
  --key /absolute/private/path/creta-diesel.key
```

Replace the two example paths. The fetcher obtains the pinned Creta EV source/release as **build inputs**; do not install that unmodified EV bundle on the diesel. SHA-256 verification is mandatory. If source or release assets no longer match, the build stops.

Output: `ports/creta-diesel/out/07-base` and `out/08-wireless`. The work directory is under ignored `.build/`. Re-running requires a new `--output` directory; the builder will not overwrite a previous kit. It rejects changed upstream tracked source, wrong product, different stock, and wrong downloads. Extra files in the stock folder are not included in the gates or output.

Advanced inputs: `--upstream`, `--downloads`, `--output`, `--java` and `--javac` select explicit local paths. This permits offline building after the pinned inputs have been obtained. The reference hashes constrain the build to the originally tested stock, rather than accepting arbitrary firmware as a new baseline.

## What changes

The base retains upstream HMG-API 1.0.1 APK/ELF/JAR bytes and adds the diesel map, recalculated map manifests, exact-product preinstall and the helper-permissions fix. The wireless archive retains upstream 2.5.0 hook/native code and changes eligibility, stock hash lists, description and the default for cluster turns. It is re-signed locally. No full manufacturer app or library is added to the package.

Unsigned output, edited stock gates, or transplanting firmware from another car are not part of this workflow. The author notice will refer to your generated key, not the original developer’s private key.

## Checks

```sh
python3 ports/creta-diesel/tests/test-cluster-collector.py
python3 ports/creta-diesel/tests/check-port.py
```

The second command validates map structure, source hygiene and shell syntax. The first runs the corrected collector against mocked Android commands, including missing-service handling and exclusion of private text. Neither proves physical vehicle behavior. The original private lifecycle tests additionally used the owner’s stock/feature files; see RESULTS.md for their limits.

## Optional private integration tests

If you also privately captured the unmodified build.prop, factory featurexml.cfg and permissions tree, the local fixture can be exercised without a car. Compile `lpatch.c` from the pinned upstream with `cc -DHOST -O2 -o /private/path/lpatch-host <upstream>/tools/lpatch/lpatch.c`. Then run:

```sh
python3 ports/creta-diesel/tests/validate-local.py \
  --stock /private/path/CRETA-STOCK \
  --build-prop /private/path/build.prop \
  --factory-system /private/path/factory-system \
  --lpatch /private/path/lpatch-host
python3 ports/creta-diesel/tests/test-preinstall-extraction.py \
  --stock /private/path/CRETA-STOCK \
  --lpatch /private/path/lpatch-host
```

`factory-system` contains `onebin/su2ifl_in/featurexml.cfg` and `etc/permissions`. These test inputs are not published and are not needed for the ordinary package build. Tests create a temporary fixture, simulate Wi-Fi and enable host-only map testing; neither bypass is shipped to the vehicle.
