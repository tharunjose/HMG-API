"""Build the one-binding mod with the owner's signing key and existing Nemesis wrapper scripts."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile

here = Path(__file__).resolve().parent
p = argparse.ArgumentParser(description=__doc__)
for arg in ('baseline', 'key', 'engine-classes', 'output'):
    p.add_argument('--' + arg, type=Path, required=True)
p.add_argument('--java', default='java')
args = p.parse_args()
# The existing stage 08 wrapper provides the generic Nemesis install/remove scripts.
if hashlib.sha256(args.baseline.read_bytes()).hexdigest() != '04e0834b0965c6ac7524b9ae9ee35aadeb9a192a04c861fd842d995fe7101706':
    p.error('Expected the tested stage 08 wrapper')
with tempfile.TemporaryDirectory() as tmp:
    mod = Path(tmp)
    shutil.copyfile(here/'mod.json', mod/'mod.json')
    signing = [args.java, '-cp', str(args.engine_classes), 'hmgapi.engine.Signing']
    subprocess.run([*signing, 'sign', mod, args.key], check=True)
    subprocess.run([*signing, 'verify', mod], check=True)
    manifest = 'META-HMGAPI/manifest.json'
    with ZipFile(args.baseline) as original:
        with ZipFile(io.BytesIO(original.read('mod/package.zip'))) as base:
            assert json.loads(base.read(manifest))['uuid'] == json.loads((mod/manifest).read_bytes())['uuid']
        payload = io.BytesIO()
        with ZipFile(payload, 'w', ZIP_DEFLATED) as pack:
            for file in sorted(mod.rglob('*')):
                if file.is_file():
                    pack.write(file, file.relative_to(mod))
        descriptor = """[nemesis]
version=1.1
id=hmgapi.creta-siri-short
name=Creta steering voice (short press)
type=application
package-version=1.0.0
short-desc="Tap the wheel voice button to request a hold."
os="SU2IFL.IND.0000.V010.001.260430"
models="any"
depends="hmgapi@>=1.0.1"
preinstall=scripts/preinstall.sh
postinstall=scripts/postinstall.sh
preuninstall=scripts/preuninstall.sh

[app.0]
kind=sh
path=bin/open.sh
uid=root
"""
        with ZipFile(args.output, 'x', ZIP_DEFLATED) as wrapper:
            wrapper.writestr('NEMESIS.data', descriptor)
            wrapper.writestr('mod/id', 'creta-siri-short\n')
            wrapper.writestr('mod/package.zip', payload.getvalue())
            wrapper.write(here/'preinstall.sh', 'scripts/preinstall.sh')
            for name in ('bin/open.sh', 'scripts/postinstall.sh', 'scripts/preuninstall.sh'):
                wrapper.writestr(name, original.read(name))
print('Package SHA256', hashlib.sha256(args.output.read_bytes()).hexdigest())
