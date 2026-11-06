"""Build the signed NEMESIS watchdog trial using the existing diesel mod signer."""
import argparse
import io
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

parser = argparse.ArgumentParser(description=__doc__)
for arg in ('java','engine-classes','key','output'):
    parser.add_argument('--'+arg, type=Path, required=True)
args = parser.parse_args()
here = Path(__file__).resolve().parent
port = here.parent
repo = port.parents[1]
mod_id = 'creta-battery-watchdog'
if not args.key.is_file():
    parser.error('Existing private mod key required')
with tempfile.TemporaryDirectory() as tmp:
    mod = Path(tmp)/mod_id
    shutil.copytree(repo/'mods'/mod_id, mod)
    signing = [args.java,'-cp',args.engine_classes,'hmgapi.engine.Signing']
    subprocess.run(signing+['sign',mod,args.key], check=True)
    subprocess.run(signing+['verify',mod], check=True)
    payload = io.BytesIO()
    with ZipFile(payload,'w',ZIP_DEFLATED) as z:
        for p in sorted(mod.rglob('*')):
            if p.is_file(): z.write(p,p.relative_to(mod))
    meta = json.loads((mod/'mod.json').read_text())
    descriptor = f"""[nemesis]
version=1.1
id=hmgapi.{mod_id}
name={meta['name']}
type=application
package-version={meta['version']}
short-desc="Warns on low 12V charge or a large drop between sessions."
os="{meta['system']['product']}"
models="any"
depends="hmgapi@>=1.0.1,!hmgapi.creta-battery-log,!battery.watchdog"
preinstall=scripts/preinstall.sh
postinstall=scripts/postinstall.sh
preuninstall=scripts/preuninstall.sh

[app.0]
kind=sh
path=bin/status.sh
uid=root
"""
    with ZipFile(args.output,'x',ZIP_DEFLATED) as z:
        z.writestr('NEMESIS.data',descriptor)
        z.writestr('mod/id',mod_id+'\n')
        z.writestr('mod/package.zip',payload.getvalue())
        z.write(here/'status.sh','bin/status.sh')
        z.write(port/'short-press-siri/preinstall.sh','scripts/preinstall.sh')
        for name in ('postinstall.sh','preuninstall.sh'):
            z.write(repo/'install/nemesis/mod/scripts'/name,'scripts/'+name)
