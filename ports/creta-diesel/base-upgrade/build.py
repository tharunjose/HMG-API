"""Package a base-only repair; never alter the tested map, APK or mod archives."""
import argparse
import hashlib
from pathlib import Path
import shutil
import tempfile
import zipfile

p = argparse.ArgumentParser()
p.add_argument('--base', type=Path, required=True, help='Verified stage07 hmgapi.zip')
p.add_argument('--source', type=Path, required=True, help='Prepared source with out/hmgapid and out/hmgapi-hook.jar')
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
if hashlib.sha256(a.base.read_bytes()).hexdigest() != 'b088b75a09e02d37f83703c187606780ab22310f04bd5444753d0addffff4cd6':
    p.error('Base ZIP differs from the verified stage07 1.0.1.2 package')
here = Path(__file__).resolve().parent
product = 'SU2IFL.IND.0000.V010.001.260430'
def md5(b): return hashlib.md5(b).hexdigest()
def put(p, b):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b)
def pack(folder, path):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(folder.rglob('*')):
            if f.is_file():
                i=zipfile.ZipInfo(f.relative_to(folder).as_posix(), (2026,11,9,0,0,0))
                i.external_attr=(0o100755 if f.suffix=='.sh' or f.name in ('lpatch','hmgapid') else 0o100644)<<16
                i.compress_type=zipfile.ZIP_DEFLATED
                z.writestr(i,f.read_bytes())
    with zipfile.ZipFile(path) as z: assert z.testzip() is None
    print(path.name, hashlib.sha256(path.read_bytes()).hexdigest())

a.out.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(a.base) as old:
    work=Path(tmp); pkg=work/'repair'; payload=pkg/'payload'; payload.mkdir(parents=True)
    oldmeta=old.read('NEMESIS.data').decode()
    assert 'package-version=1.0.1.2\n' in oldmeta and product in oldmeta
    assert old.read('payload/VERSION').strip()==b'1.0.1'
    for line in old.read('payload/MANIFEST').decode().splitlines():
        h,n=line.split(); assert md5(old.read('payload/'+n))==h
    binary=(a.source/'out/hmgapid').read_bytes()
    assert binary[:5]==b'\x7fELF\x01' and binary[18:20]==b'\x28\0'
    jar=(a.source/'out/hmgapi-hook.jar').read_bytes()
    with zipfile.ZipFile(a.source/'out/hmgapi-hook.jar') as z: assert z.read('classes.dex')[:8]==b'dex\n035\0'
    targets=[('755','system/etc/install-recovery.sh',None),('755','system/etc/qb_runtime.sh',None),
             ('700','data/hmgapi/lib.sh',(a.source/'install/common/lib.sh').read_bytes()),
             ('700','data/hmgapi/uninstall.sh',(a.source/'install/common/uninstall.sh').read_bytes()),
             ('700','data/hmgapi/boot.sh',(a.source/'install/common/boot.sh').read_bytes()),
             ('700','data/hmgapi/nemesis/bin/start.sh',(a.source/'install/nemesis/bin/start.sh').read_bytes()),
             ('644','system/framework/hmgapi-hook.jar',jar),('755','system/bin/hmgapid',binary),
             ('600','data/hmgapi/installed.txt',None)]
    for mode,n,b in targets:
        if b is not None: put(payload/'new'/n,b)
    put(payload/'files.list',''.join(f'{m} {n}\n' for m,n,_ in targets).encode())
    baseline=[]
    for src,dest in [('hmgapid','system/bin/hmgapid'),('lpatch','system/bin/lpatch'),('app_process','system/bin/app_process'),
                     ('libhmgapi_hook.so','system/lib/libhmgapi_hook.so'),('hmgapi-hook.jar','system/framework/hmgapi-hook.jar'),
                     ('HmgApi.apk','data/hmgapi/HmgApi.apk'),('lib.sh','data/hmgapi/lib.sh'),('uninstall.sh','data/hmgapi/uninstall.sh')]:
        baseline.append(f'{md5(old.read("payload/"+src))} {dest}\n')
    baseline += ['33f798115689d1859e8d2159dc88e7dc system/bin/app_process.hmgapi-stock\n',
                 '33f798115689d1859e8d2159dc88e7dc data/hmgapi/stock/system/bin/app_process\n']
    for line in old.read('payload/MAPS.md5').decode().splitlines():
        h,n=line.split(); assert md5(old.read('payload/'+n))==h
        baseline.append(f'{h} data/hmgapi/{n}\n')
    put(payload/'baseline.md5',''.join(baseline).encode())
    put(payload/'lpatch',old.read('payload/lpatch'))
    for n in ['install.sh','transaction.sh','recover.sh']: shutil.copy2(here/n,payload/n)
    put(payload/'payload.md5',''.join(f'{md5(f.read_bytes())} {f.relative_to(payload).as_posix()}\n' for f in sorted(payload.rglob('*')) if f.is_file()).encode())
    put(pkg/'scripts/postinstall.sh',b'#!/system/bin/sh\nunset ROOT\nexec /system/bin/sh ./payload/install.sh "$PWD/payload"\n')
    shutil.copy2(here/'status.sh',pkg/'status.sh')
    put(pkg/'NEMESIS.data',f'''[nemesis]
version=1.1
id=creta.base.repair
name=Creta base repair 1.0.2.1
type=application
package-version=1.0.2.1
short-desc="Repairs base startup and vehicle reads; keeps diesel mods."
os="{product}"
models=any
depends="hmgapi@>=1.0.1"
postinstall=scripts/postinstall.sh

[app.0]
kind=sh
path=status.sh
uid=root
'''.encode())
    pack(pkg,a.out/'creta-base-repair-1.0.2.1.zip')
    rollback=work/'rollback';rollback.mkdir()
    put(rollback/'rollback.sh',b'''#!/system/bin/sh
unset ROOT
[ "$(getprop ro.build.product)" = SU2IFL.IND.0000.V010.001.260430 ] || exit 1
[ -f /data/creta-base-upgrade-1.0.2.1/recover.sh ] || exit 1
/system/bin/sh /data/creta-base-upgrade-1.0.2.1/recover.sh manual || exit 1
am broadcast -a com.hkmc.intent.action.TOAST -e com.hkmc.intent.extra.TOAST_MESSAGE "Saved base restored. Restart the head unit now." --ez com.hkmc.intent.extra.TOAST_POPUPSHOWING true
''')
    put(rollback/'NEMESIS.data',f'''[nemesis]
version=1.1
id=creta.base.rollback
name=Creta base rollback - launch to restore
type=application
package-version=1.0.0
short-desc="Launch restores the saved base; restart afterward."
os="{product}"
models=any

[app.0]
kind=sh
path=rollback.sh
uid=root
'''.encode())
    pack(rollback,a.out/'creta-base-rollback-1.0.0.zip')
