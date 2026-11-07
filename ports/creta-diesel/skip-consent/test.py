"""Validate the exact ODEX trial against private stock and an isolated host engine.

Usage: python test.py --workspace /path/to/private/Nemesis
The workspace is a local fixture convention, not a published manufacturer payload.
Requires Unicorn only for executing the already-installed ARM lpatch in isolation.
"""
import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from zipfile import ZipFile
from build import REF, patched_odex
from arm_check import run as arm_run

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--workspace',type=Path,required=True)
a=p.parse_args()
ROOT=a.workspace.resolve()
JAVA=ROOT/'toolchain/jdk-17.0.21+9/Contents/Home/bin/java'
CP=ROOT/'analysis/engine-host'
STOCK=ROOT/'vehicle-evidence/2026-11-05-stock/CRETA-STOCK'
UI=ROOT/'vehicle-evidence/2026-11-07-systemui/CRETA-SYSTEMUI'
BUILD=Path((ROOT/'analysis/latest-diesel-build.txt').read_text().strip())
PACKAGE=ROOT/'Creta-CarPlay-trial/33-startup-screen-skip/packages/creta-skip-consent.zip'
PRODUCT=REF['product']
log=[]

def run(args,**kwargs):
    r=subprocess.run(list(map(str,args)),capture_output=True,text=True,**kwargs)
    log.append('$ '+' '.join(map(str,args))+'\n'+r.stdout+r.stderr)
    return r

def hashes(folder):
    return {f.relative_to(folder).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in folder.rglob('*') if f.is_file()}

def cls(tree):
    result={}
    for f in tree.rglob('*.smali'):
        text=f.read_text();name=re.search(r'^\.class [^\n]*?(L[^\s]+;)$',text,re.M).group(1)
        assert name not in result
        result[name]=text
    return result

try:
 with tempfile.TemporaryDirectory(prefix='creta-skip-test-') as tmp:
    work=Path(tmp)
    raw=(UI/'SystemUI.odex').read_bytes();patched=patched_odex(raw)
    assert sum(x!=y for x,y in zip(raw,patched))==9
    wrong=bytearray(raw);wrong[100]^=1
    try:patched_odex(bytes(wrong))
    except ValueError:pass
    else:raise AssertionError('Wrong source accepted')
    with ZipFile(PACKAGE) as outer:
        assert outer.testzip() is None
        inner=work/'mod.zip';inner.write_bytes(outer.read('mod/package.zip'))
        pre=outer.read('scripts/preinstall.sh').decode()
        for n in outer.namelist():
            if n.endswith('.sh'):assert run(['sh','-n'],input=outer.read(n).decode()).returncode==0
    with ZipFile(inner) as z:
        assert z.testzip() is None
        assert set(z.namelist())=={'mod.json','patches.json','systemui.recipe','META-HMGAPI/manifest.json','META-HMGAPI/signature'},z.namelist()
        recipe=z.read('systemui.recipe')
        mod=work/'mod';z.extractall(mod)
    assert run([JAVA,'-cp',CP,'hmgapi.engine.Signing','verify',mod]).returncode==0
    # The real installed ARM binary, with its original 8 MiB limit, must produce
    # precisely the same bytes as the host. EABI filesystem exists in memory only.
    with ZipFile(ROOT/'Creta-CarPlay-trial/07-base/packages/hmgapi.zip') as z:arm=z.read('payload/lpatch')
    rc,out,err,files=arm_run(arm,['apply','recipe','stock','patched'],{'recipe':recipe,'stock':raw})
    assert rc==0 and files['patched']==patched,(rc,out,err)
    bad=bytearray(raw);bad[REF['instruction_file_offset']]^=1
    rc,_,_,files=arm_run(arm,['apply','recipe','stock','patched'],{'recipe':recipe,'stock':bytes(bad)})
    assert rc!=0 and 'patched' not in files
    print('PASS existing ARM tool: exact patch, corrupt-source rejection.')
    # Disassemble both complete ODEX files against identical stock dependencies.
    boot='core conscrypt okhttp core-junit bouncycastle ext framework framework2 telephony-common voip-common mms-common android.policy services apache-xml webviewchromium automotive'.split()
    fw=STOCK/'system/framework'
    extra=':'.join(n for n in sorted(REF['framework_sha256']) if Path(n).stem not in boot)
    outputs=[]
    for name,data in [('stock',raw),('patched',patched)]:
        file=work/(name+'.odex');file.write_bytes(data)
        tree=work/name
        cmd=[JAVA,'-cp',str(ROOT/'toolchain/baksmali-deps/*'),'org.jf.baksmali.Main','x','-a','18','-d',fw,
             '-b',':'.join(n+'.odex' for n in boot),'-c',extra,file,'-o',tree]
        r=run(cmd);assert r.returncode==0 and not r.stderr,r.stderr
        outputs.append(cls(tree))
    before,after=outputs;target='Lcom/android/systemui/consentscreen/D;'
    assert len(before)==626 and before.keys()==after.keys()
    assert [k for k in before if before[k]!=after[k]]==[target]
    old='    :cond_14d\n    invoke-virtual {p0, v4}, '+target+'->T(I)V\n'
    new='    :cond_14d\n    invoke-direct {p0}, '+target+'->dc()V\n'
    assert before[target].count(old)==1
    assert before[target].replace(old,new)==after[target]
    # No unrelated decompiler repair or assembly enters the shipped ODEX.
    print('PASS 626-class comparison: only T(0) -> dc() in normal start; all other methods unchanged.')
    root=work/'car'
    shutil.copytree(STOCK/'system',root/'system')
    app=root/'system/priv-app';app.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(UI/'SystemUI.apk',app/'SystemUI.apk');shutil.copyfile(UI/'SystemUI.odex',app/'SystemUI.odex')
    shutil.copyfile(ROOT/'vehicle-evidence/2026-11-05-preinstall/build.prop',root/'system/build.prop')
    capture=ROOT/'vehicle-evidence/2026-11-05-wifi/CRETA-WIFI-CHECK/system'
    feature=root/'system/onebin/su2ifl_in/featurexml.cfg';feature.parent.mkdir(parents=True)
    shutil.copyfile(capture/'onebin/su2ifl_in/featurexml.cfg',feature)
    shutil.copytree(capture/'etc/permissions',root/'system/etc/permissions')
    (root/'sys/class/net/wlan0').mkdir(parents=True)
    (root/'props.txt').write_text('ro.build.product='+PRODUCT+'\nro.board.platform=tcc803x\nro.build.version.release=4.4.2\nro.mobis.onebindir=su2ifl_in\n')
    shutil.copytree(BUILD/'base/payload/maps',root/'data/hmgapi/maps')
    settings=root/'data/hmgapi/settings';settings.mkdir()
    (settings/'hmgapi.json').write_text('{"testing_maps":true}')
    env=dict(os.environ,HMGAPI_ROOT=str(root),HMGAPI_HOST='1',HMGAPI_PRODUCT=PRODUCT,HMGAPI_ONEBIN='su2ifl_in',HMGAPI_LPATCH=str(ROOT/'toolchain/lpatch-host'))
    command=[JAVA,'-cp',CP,'hmgapi.engine.Engine']
    def invoke(*args,ok=True,override=None):
        r=run(command+list(args),env=override or env)
        assert (r.returncode==0)==ok,r.stdout+r.stderr
        return r.stdout
    invoke('install',str(BUILD/'wireless-carplay-aa-diesel.zip'));invoke('apply')
    wireless=settings/'wireless-carplay-aa.json';wireless.write_text('{"tbt":true}')
    baseline=hashes(root/'system');saved_settings=hashes(settings)
    for product in ('SU2IEV.IND.0000.V010.001.260430','SU2IFL.IND.0000.V010.001.260507'):
        invoke('install',str(inner),ok=False,override=dict(env,HMGAPI_PRODUCT=product))
    invoke('install',str(inner));invoke('plan');invoke('apply')
    assert (app/'SystemUI.odex').read_bytes()==patched
    changed={k for k in baseline if baseline[k]!=hashes(root/'system').get(k)}
    assert changed=={'priv-app/SystemUI.odex'},changed
    assert hashes(settings)==saved_settings
    invoke('apply');assert (app/'SystemUI.odex').read_bytes()==patched
    invoke('remove','creta-skip-consent');invoke('apply')
    assert hashes(root/'system')==baseline and hashes(settings)==saved_settings
    invoke('install',str(inner));invoke('apply','--trial');invoke('recover')
    assert hashes(root/'system')==baseline
    invoke('remove','creta-skip-consent');invoke('apply')
    # A checksum mismatch stops engine planning as well as the USB preinstall.
    (app/'SystemUI.odex').write_bytes(bytes(wrong))
    invoke('install',str(inner));invoke('plan',ok=False)
    assert (app/'SystemUI.odex').read_bytes()==bytes(wrong)
    invoke('remove','creta-skip-consent')
    (app/'SystemUI.odex').write_bytes(raw)
    print('PASS installed-base engine: exact-file-only change, idempotence, remove/restore, trial rollback, wrong firmware/stock rejection.')
    # Execute the actual USB preinstall with stock files and mocked properties.
    bin=root/'system/bin';bin.mkdir(exist_ok=True)
    shutil.copyfile(ROOT/'toolchain/lpatch-host',bin/'lpatch');(bin/'lpatch').chmod(0o755)
    (bin/'hmgapid').write_text('#!/bin/sh\n[ "$1 $2" = "engine verify-map" ]\n');(bin/'hmgapid').chmod(0o755)
    mock=work/'mock';mock.mkdir()
    (mock/'getprop').write_text('#!/bin/sh\ncase "$1" in ro.build.product) echo "${TEST_PRODUCT}";; ro.mobis.onebindir) echo su2ifl_in;; esac\n');(mock/'getprop').chmod(0o755)
    penv=dict(os.environ,ROOT=str(root),PATH=str(mock)+os.pathsep+os.environ['PATH'],TEST_PRODUCT=PRODUCT)
    def precheck(ok=True):
        result=run(['sh','-c',pre],env=penv)
        assert (result.returncode==0)==ok,result.stdout+result.stderr
    precheck()
    penv['TEST_PRODUCT']='wrong';precheck(False);penv['TEST_PRODUCT']=PRODUCT
    (app/'SystemUI.odex').write_bytes(bytes(wrong));precheck(False);(app/'SystemUI.odex').write_bytes(raw)
    (app/'SystemUI.odex').write_bytes(patched);precheck(False)
    owner=root/'data/hmgapi/mods/creta-skip-consent';owner.mkdir();precheck();owner.rmdir()
    (app/'SystemUI.odex').write_bytes(raw)
    apk=(app/'SystemUI.apk').read_bytes();(app/'SystemUI.apk').write_bytes(b'wrong');precheck(False);(app/'SystemUI.apk').write_bytes(apk)
    fallback=root/'data/hmgapi/mods/creta-startup-notice';fallback.mkdir();precheck(False);fallback.rmdir()
    cache=root/'data/dalvik-cache/system@priv-app@SystemUI.apk@classes.dex';cache.parent.mkdir();cache.write_bytes(b'unknown');precheck(False);cache.unlink()
    (bin/'hmgapid').write_text('#!/bin/sh\nexit 1\n');precheck(False)
    print('PASS USB preinstall: stock accepted; wrong product/APK/ODEX, fallback conflict and alternate cache rejected.')
    print('ALL CHECKS PASSED. Android startup and UI behavior still require parked vehicle testing.')
finally:
 (ROOT/'analysis/validate-stage33.log').write_text('\n'.join(log))
