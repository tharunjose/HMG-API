# Creta diesel India port

See [SETUP.md](docs/SETUP.md) first, then [BUILD.md](docs/BUILD.md). This directory contains the exact-firmware builder, hash-only reference profile, USB helpers and local tests. The map is also integrated into the main repository’s `maps/hyundai/creta-diesel/ind/260430` tree.

The port’s upstream checkout, downloads, build output and private stock files are ignored by Git. Never commit vehicle captures or signing keys. The initial public snapshot contains no ready-made diesel binary release.

[Startup screen skip trial](skip-consent/README.md): exact captured SystemUI ODEX patch, host-tested; parked vehicle validation pending.
