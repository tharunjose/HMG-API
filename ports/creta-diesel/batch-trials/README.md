# Optional projection trials for exact Indian Creta diesel

Owner reported the renderer checks passing on 7 November; Extras installed with one unexplained factory voice activation. See [dated results](../docs/RESULTS.md). Builder pins renderer source to Creta EV 1.3.1 (`e1664558ab715dbbb8416b5d21693d7e41bab6bc`) and compatible Projection Extras 1.1.1 to the installed-source baseline (`3a81b461125ba373c2f842829f24a577b78147e5`). Original author sirishant; AGPL-3.0 retained.

`build.py --help` lists required owner-local inputs. Use a full Android platform JAR (the stripped legacy Maven Android stub lacks org.json), Java17, D8, the tested stage08 wrapper, host engine classes and the existing private owner key. The builder exports exact Git revisions into temporary directories, runs upstream tests, compiles using the pinned runtime, emits DEX035, signs and verifies each mod, and checks signer continuity. Never commit the key or stock binaries.

- `wireless-creta-rhd` 1.3.1-diesel.1: original renderer, exact diesel eligibility. Leaves the installed wireless hooks byte-identical. Its `guidanceEnded` replaces the generic compass path; cancellation/arrival and OEM heading must be revalidated while parked. It is not an instrument-gauge redesign.
- `projection-extras` 1.1.1-diesel.1: switching and session/screen fixes, no input declarations or AA Call-key hook. Existing standalone Siri/Phone retain button ownership. Not equivalent to latest upstream 1.1.4 and not a fix claim for the post-call Phone regression.

Host results: 175 renderer checks;20 switch-rule checks; install/plan/apply/remove beside stage17 and standalone Siri/Phone preserved existing input bindings, wireless settings and system files. Wrong product/firmware rejection passed. Renderer vehicle checks now have an owner-reported pass; Extras session behavior remains under investigation. No HMG-API base upgrade or EV routing/emulation included.

Install and assess renderer first, then Extras in the same visit. Uninstall the specific trial, apply pending changes and restart to remove its in-memory behavior; leave the working base/wireless/Siri/Phone packages installed.

## After the first vehicle trial

Do not repeat successful installation steps. Keep the working renderer. If the unexpected factory voice UI recurs or disrupts CarPlay, remove only the optional Extras trial, apply pending changes and restart while parked. This is isolation, not a confirmed fix. Post-Extras Phone checks and explicit session checks remain open.
