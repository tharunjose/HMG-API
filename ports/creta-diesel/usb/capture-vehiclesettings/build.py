"""Build the source-only Nemesis collector; OEM files are copied only on the car."""
import argparse
import configparser
import hashlib
from pathlib import Path
import zipfile

p = argparse.ArgumentParser()
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
a.out.mkdir(parents=True, exist_ok=True)
here = Path(__file__).resolve().parent
descriptor = '''[nemesis]
version=1.1
id=creta.vehiclesettings.capture
name=Creta Vehicle Settings capture (read only)
type=application
package-version=1.0.1
short-desc="Copies Vehicle Settings and UI files for offline analysis."
os="SU2IFL.IND.0000.V010.001.260430"
models="any"
preinstall=scripts/preinstall.sh

[app.0]
kind=sh
path=bin/capture.sh
uid=root
'''
# Nemesis rejects descriptions above 64 Unicode characters before install.
metadata = configparser.ConfigParser(interpolation=None)
metadata.read_string(descriptor)
if len(metadata['nemesis']['short-desc'].strip('"')) > 64:
    raise ValueError('Nemesis short-desc must be at most 64 characters')
target = a.out / 'creta-vehiclesettings-capture.zip'
files = {'NEMESIS.data': descriptor.encode(),
         'bin/capture.sh': (here / 'capture.sh').read_bytes(),
         'scripts/preinstall.sh': (here / 'preinstall.sh').read_bytes()}
with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, data in files.items():
        entry = zipfile.ZipInfo(name, date_time=(2026, 11, 8, 0, 0, 0))
        entry.compress_type = zipfile.ZIP_DEFLATED
        entry.external_attr = (0o100755 if name.endswith('.sh') else 0o100644) << 16
        z.writestr(entry, data)
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    assert set(z.namelist()) == set(files)
    for name, data in files.items():
        assert z.read(name) == data
(a.out / 'CRETA-VEHICLESETTINGS-CAPTURE').write_text('Creta Vehicle Settings capture 1.0.1\n')
print(target, hashlib.sha256(target.read_bytes()).hexdigest())
