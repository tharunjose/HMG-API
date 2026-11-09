"""Build the pinned runtime as DEX035 without rebuilding/resigning the APK."""
import argparse
from pathlib import Path
import os
import subprocess
import zipfile
p=argparse.ArgumentParser()
for name in ['source','java','android','r8']:p.add_argument('--'+name,type=Path,required=True)
a=p.parse_args();s=a.source.resolve();out=s/'out';out.mkdir(exist_ok=True)
stubs=out/'runtime-stubs';classes=out/'classes'
for d in [stubs,classes]:d.mkdir(exist_ok=True)
def run(args):subprocess.run(list(map(str,args)),check=True)
javac=a.java.parent/'javac'
run([javac,'--release','8','-cp',a.android,'-d',stubs,*sorted((s/'core/runtime/stubs').rglob('*.java'))])
run([javac,'--release','8','-cp',str(a.android)+os.pathsep+str(stubs),'-d',classes,*sorted((s/'core/runtime/java').rglob('*.java'))])
run([a.java,'-cp',a.r8,'com.android.tools.r8.D8','--release','--min-api','19','--lib',a.android,
     '--classpath',stubs,'--output',out/'hmgapi-hook.jar',*sorted(classes.rglob('*.class'))])
with zipfile.ZipFile(out/'hmgapi-hook.jar') as z:assert z.read('classes.dex')[:8]==b'dex\n035\0'
