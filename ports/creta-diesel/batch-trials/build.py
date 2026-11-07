"""Build two optional exact-diesel trials from pinned upstream sources; no base upgrade."""
import argparse, hashlib, io, json, os, shutil, subprocess, tempfile, zipfile
from pathlib import Path
p=argparse.ArgumentParser()
for k in ('repo','baseline','android','r8','engine','key','out'):
 p.add_argument('--'+k,type=Path,required=True)
p.add_argument('--java',required=True)
a=p.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
BASE='3a81b461125ba373c2f842829f24a577b78147e5'; EV='e1664558ab715dbbb8416b5d21693d7e41bab6bc'
PRODUCT='SU2IFL.IND.0000.V010.001.260430'
assert hashlib.sha256(a.baseline.read_bytes()).hexdigest()=='04e0834b0965c6ac7524b9ae9ee35aadeb9a192a04c861fd842d995fe7101706'
def run(args,**kw): subprocess.run(list(map(str,args)),check=True,**kw)
def export(ref,folder,dest):
 paths=subprocess.check_output(['git','-C',str(a.repo),'ls-tree','-r','--name-only',ref,'--',folder],text=True).splitlines()
 for f in paths:
  t=dest/f;t.parent.mkdir(parents=True,exist_ok=True)
  t.write_bytes(subprocess.check_output(['git','-C',str(a.repo),'show',ref+':'+f]))
def pack(folder):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
  for f in sorted(folder.rglob('*')):
   if f.is_file():z.write(f,f.relative_to(folder))
 return b.getvalue()
with tempfile.TemporaryDirectory(prefix='creta-batch-') as temp:
 w=Path(temp)
 for folder in ('core/runtime','mods/wireless-carplay-aa','mods/projection-extras'):export(BASE,folder,w)
 export(EV,'mods/wireless-creta-rhd',w)
 javac=Path(a.java).with_name('javac'); env=dict(os.environ,PATH=str(javac.parent)+os.pathsep+os.environ['PATH'])
 for mod in ('wireless-creta-rhd','projection-extras'):run(['sh',w/'mods'/mod/'test.sh'],env=env)
 stubs=w/'stubs';classes=w/'classes';api=w/'api'
 for d in (stubs,classes,api):d.mkdir()
 run([javac,'--release','8','-cp',a.android,'-d',stubs,*sorted((w/'core/runtime/stubs').rglob('*.java'))])
 run([javac,'--release','8','-cp',str(a.android)+os.pathsep+str(stubs),'-d',classes,*sorted((w/'core/runtime/java').rglob('*.java'))])
 run([javac,'--release','8','-cp',str(a.android)+os.pathsep+str(classes),'-d',api,w/'mods/wireless-carplay-aa/src/hmgapi/mods/wireless/api/TurnDisplay.java'])
 with zipfile.ZipFile(a.baseline) as base:
  for name,version,title in [('wireless-creta-rhd','1.3.1-diesel.1','Creta richer cluster navigation — trial'),('projection-extras','1.1.1-diesel.1','Creta Projection Extras — trial')]:
   folder=w/'mods'/name
   meta=json.loads((folder/'mod.json').read_text());meta['version']=version;meta['name']=title
   meta['system']={'product':PRODUCT,'model':'SU2IFL','region':'IND','firmware':'260430'}
   meta['authors'].append('Creta diesel port');meta['description']+=' Exact diesel trial; host-tested only.'
   if name=='projection-extras':
    # Keep the tested standalone Siri and Phone bindings as the only button owners.
    meta.pop('input',None)
    for key in ('gpm.key_listener.key_for_service','gpm.util.spec_step'):meta['hooks']['points'].pop(key)
    src=folder/'src/hmgapi/mods/projextras/Switch.java';s=src.read_text();s=s.replace('            CallKey.gpm(mod, app);','            // Diesel: standalone phone-button mod owns button behavior.');src.write_text(s)
    (folder/'src/hmgapi/mods/projextras/CallKey.java').unlink()
    settings=json.loads((folder/'settings.json').read_text());settings['settings']=[s for s in settings['settings'] if s['key']=='carplay_screen_retry'];(folder/'settings.json').write_text(json.dumps(settings,indent=2)+'\n')
    # Switch still refers to CallKey.GPM in the condition; replace with the literal package.
    src.write_text(src.read_text().replace('CallKey.GPM','"com.google.android.projection.sink"'))
   (folder/'mod.json').write_text(json.dumps(meta,indent=2)+'\n')
   outclasses=w/(name+'-classes');outclasses.mkdir()
   cp=os.pathsep.join(map(str,(a.android,classes,api)))
   run([javac,'--release','8','-cp',cp,'-d',outclasses,*sorted((folder/'src').rglob('*.java'))])
   payload=w/(name+'-payload');payload.mkdir()
   run([a.java,'-cp',a.r8,'com.android.tools.r8.D8','--release','--min-api','19','--lib',a.android,'--classpath',classes,'--classpath',api,'--output',payload/'hooks.jar',*sorted(outclasses.rglob('*.class'))])
   with zipfile.ZipFile(payload/'hooks.jar') as z:assert z.read('classes.dex')[:8]==b'dex\n035\x00'
   for f in folder.glob('*.json'):shutil.copyfile(f,payload/f.name)
   signing=[a.java,'-cp',a.engine,'hmgapi.engine.Signing']
   run([*signing,'sign',payload,a.key]);run([*signing,'verify',payload])
   with zipfile.ZipFile(io.BytesIO(base.read('mod/package.zip'))) as old:
    assert json.loads(old.read('META-HMGAPI/manifest.json'))['uuid']==json.loads((payload/'META-HMGAPI/manifest.json').read_text())['uuid']
   desc=f'''[nemesis]\nversion=1.1\nid=hmgapi.{name}\nname={title}\ntype=application\npackage-version={version.replace('-diesel.','.')}\nshort-desc="Optional exact-diesel projection trial; see batch guide."\nos="{PRODUCT}"\nmodels="any"\ndepends="hmgapi@>=1.0.1"\npreinstall=scripts/preinstall.sh\npostinstall=scripts/postinstall.sh\npreuninstall=scripts/preuninstall.sh\n\n[app.0]\nkind=sh\npath=bin/open.sh\nuid=root\n'''
   target=a.out/(name+'-diesel-trial.zip')
   with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('NEMESIS.data',desc);z.writestr('mod/id',name+'\n');z.writestr('mod/package.zip',pack(payload))
    z.write(Path(__file__).resolve().parent.parent/'phone-key/preinstall.sh','scripts/preinstall.sh')
    for f in ('bin/open.sh','scripts/postinstall.sh','scripts/preuninstall.sh'):z.writestr(f,base.read(f))
   print(target.name,hashlib.sha256(target.read_bytes()).hexdigest())
