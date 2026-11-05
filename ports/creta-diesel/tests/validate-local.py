"""Exercise the diesel package on a private local fixture, never on a vehicle."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile

import argparse
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stock',type=Path,required=True)
parser.add_argument('--build-prop',type=Path,required=True)
parser.add_argument('--factory-system',type=Path,required=True,help='Private folder containing onebin/su2ifl_in/featurexml.cfg and etc/permissions')
parser.add_argument('--lpatch',type=Path,required=True,help='Host-built lpatch executable')
parser.add_argument('--java',default='java')
args=parser.parse_args()
JAVA=args.java
STOCK=args.stock.resolve()
BUILD=Path((ROOT/'.build/latest-build.txt').read_text().strip())
CP=BUILD/'engine-host'
BASE=BUILD/'base'
MOD=BUILD/'wireless'
PRODUCT='SU2IFL.IND.0000.V010.001.260430'
log=[]

def run(args, **kwargs):
    p=subprocess.run(args,capture_output=True,text=True,**kwargs)
    log.append('$ '+' '.join(map(str,args))+'\n'+p.stdout+p.stderr)
    return p

def hashes(folder):
    return {p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.rglob('*') if p.is_file()}

with tempfile.TemporaryDirectory(prefix='creta-port-test-') as temp:
    root=Path(temp)
    shutil.copytree(STOCK/'system',root/'system')
    shutil.copy2(args.build_prop,root/'system/build.prop')
    feature=root/'system/onebin/su2ifl_in/featurexml.cfg';feature.parent.mkdir(parents=True)
    # Stage 10 captured the actual factory feature configuration and permissions.
    captured=args.factory_system
    shutil.copy2(captured/'onebin/su2ifl_in/featurexml.cfg',feature)
    shutil.copytree(captured/'etc/permissions',root/'system/etc/permissions')
    (root/'sys/class/net/wlan0').mkdir(parents=True)
    (root/'props.txt').write_text('ro.build.product='+PRODUCT+'\nro.board.platform=tcc803x\nro.build.version.release=4.4.2\nro.mobis.onebindir=su2ifl_in\n')
    shutil.copytree(BASE/'payload/maps',root/'data/hmgapi/maps')
    settings=root/'data/hmgapi/settings';settings.mkdir()
    # Only the host fixture uses this switch. Shipped packages retain the on-car verify-map gate.
    (settings/'hmgapi.json').write_text('{"testing_maps":true}')
    before=hashes(root/'system')
    env=dict(os.environ,HMGAPI_ROOT=str(root),HMGAPI_HOST='1',HMGAPI_PRODUCT=PRODUCT,HMGAPI_ONEBIN='su2ifl_in',HMGAPI_LPATCH=str(args.lpatch.resolve()))
    command=[str(JAVA),'-cp',str(CP),'hmgapi.engine.Engine']
    for args in [('install',str(BUILD/'wireless-carplay-aa-diesel.zip')),('plan',),('apply',)]:
        p=run(command+list(args),env=env)
        assert p.returncode==0,p.stdout+p.stderr
        assert "won't load" not in p.stdout and 'hooks are off' not in p.stdout,p.stdout
    after=hashes(root/'system')
    changed={name for name in before if before[name]!=after.get(name)}
    assert changed=={'onebin/su2ifl_in/featurexml.cfg'},changed
    assert (root/'system/lib/libleafiaaac.so').is_file()
    defaults=json.loads((root/'data/hmgapi/state/mods.json').read_text()) if (root/'data/hmgapi/state/mods.json').exists() else {}
    print('Plan/apply passed with all declared hooks mapped. Only expected config changed; factory apps and native libraries retain original bytes.')
    # Exercise the existing cluster switch independently of the working wireless baseline.
    # This verifies engine behaviour, not what the physical cluster renders.
    wireless_settings=settings/'wireless-carplay-aa.json'
    for enabled in (True, False):
        wireless_settings.write_text(json.dumps({'tbt':enabled}))
        for args in [('plan',),('apply',)]:
            p=run(command+list(args),env=env)
            assert p.returncode==0,p.stdout+p.stderr
            assert "won't load" not in p.stdout and 'hooks are off' not in p.stdout,p.stdout
        assert hashes(root/'system')==after,'Cluster switch changed system files beyond wireless baseline'
    print('Cluster TBT on/off plan and apply passed; system files identical to wireless baseline in both states.')
    for args in [('remove','wireless-carplay-aa'),('apply',)]:
        p=run(command+list(args),env=env);assert p.returncode==0,p.stdout
    assert hashes(root/'system')==before,'System restore differs'
    print('Removal restored every original system byte on the fixture.')
    # Reject wrong model/firmware and absence of Wi-Fi evidence at the mod package layer.
    for product in ('SU2IEV.IND.0000.V010.001.260430','SU2IFL.IND.0000.V010.001.260507'):
        e=dict(env,HMGAPI_PRODUCT=product)
        p=run(command+['install',str(BUILD/'wireless-carplay-aa-diesel.zip')],env=e)
        assert p.returncode!=0
    shutil.rmtree(root/'sys/class/net/wlan0')
    seen=root/'data/hmgapi/public/wifi-chip'
    if seen.exists():seen.unlink()
    p=run(command+['install',str(BUILD/'wireless-carplay-aa-diesel.zip')],env=env)
    assert p.returncode!=0 and 'hmgapi.wifi' in p.stdout,p.stdout
    print('Wrong model, wrong firmware and missing Wi-Fi evidence rejected.')
for directory in ('base','wireless-nemesis'):
    d=BUILD/directory
    for script in (d/'scripts').glob('*.sh'):
        assert run(['/bin/sh','-n',str(script)]).returncode==0
    for line in (d/'stock.md5').read_text().splitlines():
        expected,path=line.split()
        assert hashlib.md5((STOCK/path.lstrip('/')).read_bytes()).hexdigest()==expected
for name in ('MANIFEST','MAPS.md5'):
    for line in (BASE/'payload'/name).read_text().splitlines():
        expected,path=line.split()
        assert hashlib.md5((BASE/'payload'/path).read_bytes()).hexdigest()==expected
for path in (ROOT/'out').glob('*/packages/*.zip'):
    with zipfile.ZipFile(path) as z:assert z.testzip() is None
(ROOT/'.build/diesel-package-tests.log').write_text('\n'.join(log))
print('Shell syntax, stock gates, manifests and ZIP integrity passed.')
