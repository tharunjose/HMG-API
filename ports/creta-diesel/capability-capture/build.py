"""Generate a private catalogue and allowlist from the owner's exact firmware capture."""
import argparse,re,json,hashlib,subprocess,zipfile,tempfile
from pathlib import Path
p=argparse.ArgumentParser()
for key in ('deodex','android','r8','out'):p.add_argument('--'+key,type=Path,required=True)
p.add_argument('--java',required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
here=Path(__file__).resolve().parent
fw=a.deodex/'fw-automotive'; impl=a.deodex/'automotive-service.odex/com/hkmc/micom'
rows=[]
for f in sorted(fw.rglob('I*Service.smali')):
 for sig in re.findall(r'^\.method public abstract (.+)$',f.read_text(),re.M):
  rows.append({'interface':f.relative_to(fw).with_suffix('').as_posix().replace('/','.'),'signature':sig,'status':'exposed signature only; hardware support and write safety unproven'})
(a.out/'EXPOSED-INTERFACES.json').write_text(json.dumps(rows,indent=2)+'\n')
readers=[]
# USM getters accepted only if their entire implementation is a cached status lookup.
code=(impl/'USMService.smali').read_text()
for name,body in re.findall(r'^\.method public (get\w+)\(\)I\n(.*?)^\.end method',code,re.M|re.S):
 invokes=re.findall(r'^\s*invoke-\S+.*$',body,re.M)
 if len(invokes)==1 and 'Lcom/hkmc/micom/USMService;->getUSMStatus(I)I' in invokes[0] and not re.search(r'^\s*(?:[is]put|aput|monitor|throw|new-)',body,re.M):
  readers.append(('USM_SERVICE','com.hkmc.usm.IUSMService',name))
# The common getUSMStatus implementation itself is a pure cache lookup.
b=re.search(r'^\.method public getUSMStatus\(I\)I\n(.*?)^\.end method',code,re.M|re.S).group(1)
assert len(re.findall(r'^\s*invoke-',b,re.M))==1 and 'Lcom/hkmc/usm/USMStatus;->getUSMStatus(I)I' in b
for service,typ,file,names in [
 ('BCM_SERVICE','com.hkmc.bcm.IBCMService','BCMService.smali',['getSocStatus','getDrvSeatHeatState','getAstSeatHeatState','getIGNStatus','getEngineStatus','getClutchStatus','getNeutralMtStatus']),
 ('DATC_SERVICE','com.hkmc.datc.IDATCService','DATCService.smali',['getClimateType','getTemperatureUnit','getDriverOnlyValue','isIGN3Status'])]:
 text=(impl/file).read_text()
 for name in names:
  m=re.search(r'^\.method public '+name+r'\(\)([IZ])\n(.*?)^\.end method',text,re.M|re.S)
  if not m:continue
  # Restrict to direct cached reads; exclude methods invoking another service.
  if re.search(r'^\s*(?:invoke-|[is]put|aput|monitor|throw|new-)',m[2],re.M):continue
  readers.append((service,typ,name))
assert len(readers)>150
allow=''.join('\t'.join(r)+'\n' for r in readers)
(a.out/'readers.tsv').write_text(allow)
with tempfile.TemporaryDirectory() as t:
 w=Path(t);cl=w/'classes';cl.mkdir()
 subprocess.run([str(Path(a.java).with_name('javac')),'--release','8','-d',str(cl),str(here/'CapabilityRead.java')],check=True)
 subprocess.run([a.java,'-cp',str(a.r8),'com.android.tools.r8.D8','--release','--min-api','19','--lib',str(a.android),'--output',str(w/'capture.jar'),*map(str,cl.rglob('*.class'))],check=True)
 desc='''[nemesis]\nversion=1.1\nid=creta.capability.capture\nname=Creta capability capture (read only)\ntype=application\npackage-version=1.0.0\nshort-desc="One capture for settings, telemetry, input and mod status."\nos="SU2IFL.IND.0000.V010.001.260430"\nmodels="any"\npreinstall=scripts/preinstall.sh\n\n[app.0]\nkind=sh\npath=bin/launch.sh\nuid=root\n'''
 with zipfile.ZipFile(a.out/'creta-capability-capture.zip','w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('NEMESIS.data',desc);z.writestr('bin/readers.tsv',allow)
  z.write(here/'launch.sh','bin/launch.sh');z.write(w/'capture.jar','bin/capture.jar');z.write(here/'capture.sh','bin/capture.sh')
  z.write(here.parent/'usb/capture-systemui/preinstall.sh','scripts/preinstall.sh')
 print('Catalogue',len(rows),'interface methods; reviewed cached getters',len(readers))
 print('Package SHA256',hashlib.sha256((a.out/'creta-capability-capture.zip').read_bytes()).hexdigest())
