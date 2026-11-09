"""Run real shell transaction against private stock fixtures; never a mounted car."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys
import zipfile

p=argparse.ArgumentParser()
p.add_argument('--base',type=Path,required=True)
p.add_argument('--repair',type=Path,required=True)
p.add_argument('--stock-app-process',type=Path,required=True)
p.add_argument('--lpatch-host',type=Path,required=True)
a=p.parse_args()
here=Path(__file__).resolve().parent
def digest(p): return hashlib.md5(p.read_bytes()).hexdigest()
def inventory(root): return {str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file() and not p.name.endswith('.creta-new')}
def run_case(mode, index=0):
 with tempfile.TemporaryDirectory() as tmp:
    tmp=Path(tmp);root=tmp/'root';root.mkdir();pkg=tmp/'pkg';pkg.mkdir()
    with zipfile.ZipFile(a.repair) as z:z.extractall(pkg)
    payload=pkg/'payload'
    shutil.copy2(a.lpatch_host,payload/'lpatch');(payload/'lpatch').chmod(0o755)
    (payload/'payload.md5').write_text(''.join(f'{digest(f)} {f.relative_to(payload)}\n' for f in sorted(payload.rglob('*')) if f.is_file() and f.name!='payload.md5'))
    with zipfile.ZipFile(a.base) as z:
        for n in z.namelist():
            if n.startswith('payload/maps/'):
                dest=root/'data/hmgapi'/n[len('payload/'):];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(n))
        paths={'hmgapid':'system/bin/hmgapid','lpatch':'system/bin/lpatch','app_process':'system/bin/app_process',
               'hmgapi-hook.jar':'system/framework/hmgapi-hook.jar','libhmgapi_hook.so':'system/lib/libhmgapi_hook.so',
               'HmgApi.apk':'data/hmgapi/HmgApi.apk','lib.sh':'data/hmgapi/lib.sh','uninstall.sh':'data/hmgapi/uninstall.sh'}
        for src,dest in paths.items():
            f=root/dest;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(z.read('payload/'+src));f.chmod(0o755)
        for dest in ['system/bin/app_process.hmgapi-stock','data/hmgapi/stock/system/bin/app_process']:
            f=root/dest;f.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a.stock_app_process,f)
        data=root/'data/hmgapi';(data/'installed.txt').write_text('version 1.0.1\nbuild fixture\n'+''.join(f'file {digest(root/dest)} /{dest}\n' for dest in paths.values() if dest.startswith('system/')))
        # Working personal mods/preferences must survive upgrade AND rollback.
        for dest,body in [('settings/creta-auto-vent.json','{"driver":true,"passenger":false,"level":2}'),('mods/working/mod.json','working'),('state/keep.txt','state'),('hook/enable',''),('hook/starts','0')]:
            f=data/dest;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(body)
        (root/'system/etc').mkdir(parents=True)
        for n in ['install-recovery.sh','qb_runtime.sh']:
            f=root/'system/etc'/n;f.write_text('#!/system/bin/sh\necho stock\n# HMGAPI_HOOK begin\necho old\n# HMGAPI_HOOK end\necho nemesis\n');f.chmod(0o755)
    mock=tmp/'mock';mock.mkdir()
    (mock/'getprop').write_text('#!/bin/sh\ncase "$1" in\nro.build.product) echo "${PRODUCT:-SU2IFL.IND.0000.V010.001.260430}";;\nro.mobis.onebindir) echo "${VARIANT:-su2ifl_in}";;\nesac\n')
    (mock/'sync').write_text('#!/bin/sh\nexit 0\n')
    # Head-unit cp is not GNU/BSD cp: refuse every flag so scripts stay plain "cp src dst".
    (mock/'cp').write_text('#!/bin/sh\nfor x in "$@"; do case "$x" in -*) echo "cp: flag $x unsupported" >&2; exit 1;; esac; done\nexec /bin/cp "$@"\n')
    # Inject a one-shot copy/rename failure or a power loss at each committed path.
    (mock/'mv').write_text('''#!'''+str(Path(sys.executable).resolve())+'''
import os,sys,subprocess,signal
from pathlib import Path
src,dst=sys.argv[-2:]
hit=src.endswith('.creta-new') and dst.startswith(os.environ['ROOT']+'/')
counter=Path(os.environ['COUNTER']);n=int(counter.read_text()) if counter.exists() else 0
if hit:
 n+=1;counter.write_text(str(n))
 if n==int(os.environ['FAIL_INDEX']) and os.environ['MODE']=='fail':sys.exit(1)
r=subprocess.run(['/bin/mv',*sys.argv[1:]])
if hit and n==int(os.environ['FAIL_INDEX']) and os.environ['MODE']=='power':os.kill(os.getppid(),signal.SIGKILL)
sys.exit(r.returncode)
''')
    for f in mock.iterdir():f.chmod(0o755)
    env=dict(os.environ,ROOT=str(root),PATH=str(mock)+':/usr/bin:/bin',MODE=mode,FAIL_INDEX=str(index),COUNTER=str(tmp/'counter'))
    if mode=='wrong-product':env['PRODUCT']='SU2IEV.IND.0000.V010.001.260430'
    if mode=='wrong-variant':env['VARIANT']='su2iev_in'
    if mode=='changed-base':(root/'system/bin/hmgapid').write_text('changed')
    if mode=='bad-map':(root/'data/hmgapi/maps/points.txt').write_text('changed')
    if mode=='journal':(root/'data/hmgapi/state/journal.json').write_text('{}')
    before=inventory(root)
    r=subprocess.run(['/bin/sh',str(payload/'install.sh'),str(payload)],env=env,capture_output=True,text=True,timeout=45)
    t=root/'data/creta-base-upgrade-1.0.2.1'
    if mode in ['wrong-product','wrong-variant','changed-base','bad-map','journal']:
        assert r.returncode!=0 and inventory(root)==before,(mode,r.stdout,r.stderr)
    else:
        if mode=='success':
            assert r.returncode==0,(r.stdout,r.stderr)
            assert (t/'state').read_text().strip()=='complete'
            assert (root/'system/bin/hmgapid').read_bytes()==(payload/'new/system/bin/hmgapid').read_bytes()
            assert 'hmgapid boot' in (root/'system/etc/install-recovery.sh').read_text()
            # Toolbox cp has no -p: every installed file must carry its files.list mode.
            for line in (payload/'files.list').read_text().splitlines():
                m,n=line.split();assert oct((root/n).stat().st_mode&0o777)[2:]==m,(n,oct((root/n).stat().st_mode))
            for key,value in before.items():
                if key.startswith(('data/hmgapi/mods/','data/hmgapi/settings/','data/hmgapi/state/','data/hmgapi/hook/','data/hmgapi/stock/','data/hmgapi/maps/')):assert (root/key).read_bytes()==value,key
            # A later unrelated edit must not be overwritten by rollback.
            target=root/'system/bin/hmgapid';saved=target.read_bytes();target.write_bytes(b'foreign')
            rr=subprocess.run(['/bin/sh',str(t/'recover.sh'),'manual'],env=env,capture_output=True,text=True)
            assert rr.returncode!=0 and target.read_bytes()==b'foreign'
            target.write_bytes(saved)
        elif mode=='power':assert r.returncode!=0,(mode,index,r.stdout)
        else:assert r.returncode!=0 and (t/'state').read_text().strip()=='rolled-back',(mode,index,r.stdout,r.stderr)
        if mode in ['success','power']:
            env['MODE']='restore'
            rr=subprocess.run(['/bin/sh',str(t/'recover.sh'),'boot' if mode=='power' else 'manual'],env=env,capture_output=True,text=True)
            assert rr.returncode==(19 if mode=='power' else 0),(mode,index,rr.stdout,rr.stderr)
        after={k:v for k,v in inventory(root).items() if not k.startswith('data/creta-base-upgrade-')}
        assert after==before,(mode,index,set(after)^set(before),[k for k in before if after.get(k)!=before[k]])
    print('PASS',mode,index)
for mode in ['success','wrong-product','wrong-variant','changed-base','bad-map','journal']:run_case(mode)
for mode in ['fail','power']:
    for index in range(1,10):run_case(mode,index)
