#!/usr/bin/env python3
"""Build the exact-firmware port locally; no manufacturer binaries are distributed."""
from pathlib import Path
import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = 'SU2IFL.IND.0000.V010.001.260430'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stock', type=Path, required=True, help='Your private CRETA-STOCK folder')
parser.add_argument('--key', type=Path, required=True, help='Private signing key; generated if absent. Keep it for future builds.')
parser.add_argument('--upstream', type=Path, default=ROOT/'upstream')
parser.add_argument('--downloads', type=Path, default=ROOT/'downloads')
parser.add_argument('--output', type=Path, default=ROOT/'out')
parser.add_argument('--java', default='java')
parser.add_argument('--javac', default='javac')
ARGS = parser.parse_args()
STOCK, SOURCE, DOWNLOADS, OUT = (p.resolve() for p in (ARGS.stock, ARGS.upstream, ARGS.downloads, ARGS.output))
JAVA = ARGS.java
LOCK = json.loads((ROOT/'reference/upstream.json').read_text())
EXPECTED = {line.split()[1]:line.split()[0] for line in (ROOT/'reference/stock.md5').read_text().splitlines()}
if (STOCK/'product.txt').read_text().strip() != PRODUCT:
    parser.error('Stock capture product does not match the one tested build')
for name, expected in EXPECTED.items():
    path = STOCK/name.lstrip('/')
    if not path.is_file() or hashlib.md5(path.read_bytes()).hexdigest() != expected:
        parser.error('Missing or different stock file: '+name)
if OUT.exists():
    parser.error('Output already exists; choose a new --output directory')
if subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'], text=True).strip() != LOCK['source_commit']:
    parser.error('Upstream source is not the pinned commit')
if subprocess.check_output(['git','-C',str(SOURCE),'status','--porcelain','--untracked-files=no'], text=True).strip():
    parser.error('Upstream tracked source files have local changes')
for name, info in LOCK['assets'].items():
    path = DOWNLOADS/name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != info['sha256']:
        parser.error('Missing or wrong upstream download: '+name)
(ROOT/'.build').mkdir(exist_ok=True)
WORK = Path(tempfile.mkdtemp(prefix='diesel-build-',dir=ROOT/'.build'))
CLASSES = WORK/'engine-host'
CLASSES.mkdir()
subprocess.run([ARGS.javac,'--release','8','-d',str(CLASSES),*[str(p) for p in sorted((SOURCE/'core/runtime/java/hmgapi/engine').glob('*.java'))]],check=True)
os.umask(0o077)

def digest(path):
    return hashlib.md5(path.read_bytes()).hexdigest()


def zip_tree(folder, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for path in sorted(folder.rglob('*')):
            if path.is_file():
                info = zipfile.ZipInfo(path.relative_to(folder).as_posix(), (2026, 11, 5, 0, 0, 0))
                mode = 0o755 if path.suffix == '.sh' or path.name in ('lpatch', 'hmgapid', 'app_process') else 0o644
                info.external_attr = (0o100000 | mode) << 16
                z.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)


def java(*args):
    subprocess.run([str(JAVA), '-cp', str(CLASSES), 'hmgapi.engine.Signing', *map(str, args)], check=True)


def stock_gate(lpatch, include_startup):
    gate = '''#!/system/bin/sh
umask 077
[ "$(getprop ro.build.product)" = "SU2IFL.IND.0000.V010.001.260430" ] || { echo 'Wrong product or firmware'; exit 1; }
[ "$(getprop ro.mobis.onebindir)" = "su2ifl_in" ] || { echo 'Wrong onebin'; exit 1; }
[ -f /system/onebin/su2ifl_in/featurexml.cfg ] || { echo 'Missing feature configuration'; exit 1; }
while read expected path; do
    [ -f "$path" ] || { echo "Missing $path"; exit 1; }
    result=$(LPATCH md5 "$path") || exit 1
    set -- $result
    [ "$1" = "$expected" ] || { echo "Stock bytes differ at $path"; exit 1; }
done < stock.md5
'''.replace('LPATCH', lpatch)
    if include_startup:
        gate += "[ ! -e /data/hmgapi/installed.txt ] || { echo 'This trial is for a fresh HMG-API install'; exit 1; }\n"
    if lpatch == './payload/lpatch':
        # Nemesis extracts every ZIP member as 0644, irrespective of ZIP mode bits.
        gate = gate.replace('while read expected path; do', 'chmod 755 ./payload/lpatch ./payload/hmgapid || exit 1\nwhile read expected path; do')
    return gate


WORK.mkdir(parents=True, exist_ok=True)
checksums = {name: value['sha256'] for name, value in LOCK['assets'].items()}
for name in ('hmgapi-1.0.1-nemesis.zip', 'wireless-carplay-aa-2.5.0.zip'):
    assert hashlib.sha256((DOWNLOADS/name).read_bytes()).hexdigest() == checksums[name]
base = WORK / 'base'
with zipfile.ZipFile(DOWNLOADS/'hmgapi-1.0.1-nemesis.zip') as outer:
    with zipfile.ZipFile(io.BytesIO(outer.read('packages/hmgapi.zip'))) as inner:
        inner.extractall(base)
payload = base/'payload'
shutil.copytree(ROOT/'maps', payload/'maps', dirs_exist_ok=True)
(payload/'MAPS.md5').write_text(''.join(digest(p)+'  '+p.relative_to(payload).as_posix()+'\n' for p in sorted((payload/'maps').rglob('*')) if p.is_file()))
# Recalculate only entries already tracked by the upstream installer manifest.
manifest = []
for line in (payload/'MANIFEST').read_text().splitlines():
    _, name = line.split(None, 1)
    manifest.append(digest(payload/name)+'  '+name+'\n')
(payload/'MANIFEST').write_text(''.join(manifest))
stock_files = [STOCK/path.lstrip('/') for path in sorted(EXPECTED)]
(base/'stock.md5').write_text(''.join(digest(p)+'  /'+p.relative_to(STOCK).as_posix()+'\n' for p in stock_files))
(base/'scripts/preinstall-diesel.sh').write_text(stock_gate('./payload/lpatch', True))
meta = (base/'NEMESIS.data').read_text().replace('name=HMG-API', 'name=HMG-API Creta diesel trial').replace('package-version=1.0.1', 'package-version=1.0.1.2').replace('os="any"', 'os="'+PRODUCT+'"').replace('postinstall=', 'preinstall=scripts/preinstall-diesel.sh\npostinstall=', 1)
(base/'NEMESIS.data').write_text(meta)
base_zip = OUT/'07-base/packages/hmgapi.zip'
zip_tree(base, base_zip)
(base_zip.parents[1]/'NEMESIS.data').write_text('[nemesis]\nversion=1.1\ntype=install\npath=packages/hmgapi.zip\n')

mod = WORK/'wireless'
with zipfile.ZipFile(DOWNLOADS/'wireless-carplay-aa-2.5.0.zip') as z:
    z.extractall(mod)
java('verify', mod)
m = json.loads((mod/'mod.json').read_text())
m['name'] = 'Wireless CarPlay + AA — Creta diesel trial'
m['version'] = '2.5.0-diesel.1'
m['system'] = {'model': 'SU2IFL', 'region': 'IND', 'firmware': '260430', 'product': PRODUCT, 'features': ['hmgapi.wifi']}
m['description'] = 'Local trial for SU2IFL India V010.001.260430. Cluster turn-by-turn defaults off.'
(mod/'mod.json').write_text(json.dumps(m, indent=2)+'\n')
s = json.loads((mod/'settings.json').read_text())
for setting in s['settings']:
    if setting['key'] == 'tbt':
        setting['default'] = False
        setting['title'] = 'Cluster turns — unsupported in this diesel trial; keep off'
(mod/'settings.json').write_text(json.dumps(s, indent=2)+'\n')
p = json.loads((mod/'patches.json').read_text())
p['cars'] = {'SU2IFL.IND.': 'su2ifl'}
(mod/'patches.json').write_text(json.dumps(p, indent=2)+'\n')
new_set = mod/'patches/su2ifl';new_set.mkdir(parents=True,exist_ok=True)
(new_set/'stock').write_text(''.join(p.name+' '+digest(p)+'\n' for p in stock_files if p.parent.name in ('app','lib')))
# This trial changes native libraries in process memory. The expect list is empty because no factory app/library is replaced on disk.
(new_set/'expect').write_text('')
key=ARGS.key.resolve()
key.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
if not key.exists():
    java('keygen',key)
    key.chmod(0o600)
java('sign',mod,key)
java('verify',mod)
mod_zip=WORK/'wireless-carplay-aa-diesel.zip'
zip_tree(mod,mod_zip)
package=WORK/'wireless-nemesis';(package/'mod').mkdir(parents=True,exist_ok=True)
shutil.copytree(SOURCE/'install/nemesis/mod/scripts',package/'scripts',dirs_exist_ok=True)
(package/'bin').mkdir(exist_ok=True)
shutil.copy2(SOURCE/'install/nemesis/bin/open.sh',package/'bin/open.sh')
shutil.copy2(mod_zip,package/'mod/package.zip')
(package/'mod/id').write_text('wireless-carplay-aa\n')
(package/'stock.md5').write_text(''.join(digest(p)+'  /'+p.relative_to(STOCK).as_posix()+'\n' for p in stock_files if p.name!='app_process'))
original=(package/'scripts/preinstall.sh').read_text()
gate=stock_gate('/system/bin/lpatch',False)
# Verification resolves names in the car's actual runtime before any projection install.
gate += '/system/bin/hmgapid engine verify-map || { echo "Hook map verification failed"; exit 1; }\n'
(package/'scripts/preinstall.sh').write_text(gate+original.replace('#!/system/bin/sh\n','',1))
(package/'NEMESIS.data').write_text('''[nemesis]
version=1.1
id=hmgapi.wireless-carplay-aa
name=Wireless CarPlay Creta diesel trial
type=application
package-version=2.5.0.1
short-desc="SU2IFL India 260430 trial; cluster turns off."
os="SU2IFL.IND.0000.V010.001.260430"
models="any"
depends="hmgapi@>=1.0.1,!wireless.projection,!projection.tbt,!enhanced.projection,!wireless.carplay.aa,!carplay.session"
preinstall=scripts/preinstall.sh
postinstall=scripts/postinstall.sh
preuninstall=scripts/preuninstall.sh

[app.0]
kind=sh
path=bin/open.sh
uid=root
''')
zip_tree(package,OUT/'08-wireless/packages/hmgapi.wireless-carplay-aa.zip')
(OUT/'08-wireless/NEMESIS.data').write_text('[nemesis]\nversion=1.1\ntype=install\npath=packages/hmgapi.wireless-carplay-aa.zip\n')
(ROOT/'.build/latest-build.txt').write_text(str(WORK)+'\n')
print('Built trial packages. On-car map verification and Wi-Fi check remain required.')
