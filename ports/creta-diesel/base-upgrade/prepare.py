"""Export a pinned source tree and apply only the reviewed base repairs."""
import argparse
import io
from pathlib import Path
import shutil
import subprocess
import tarfile

p=argparse.ArgumentParser()
p.add_argument('--repo',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args()
if a.out.exists():p.error('Choose a new source output directory')
here=Path(__file__).resolve().parent
a.out.mkdir(parents=True)
archive=subprocess.check_output(['git','-C',str(a.repo),'archive','3a81b461125ba373c2f842829f24a577b78147e5'])
with tarfile.open(fileobj=io.BytesIO(archive)) as t:t.extractall(a.out,filter='data')
for name in ['boot-1.0.2.patch','socket-close.patch','strict-response.patch']:
    subprocess.run(['git','apply',str(here/name)],cwd=a.out,check=True)
shutil.copy2(here/'response.h',a.out/'core/hmgapid/response.h')
p=a.out/'core/runtime/java/hmgapi/engine/Engine.java'
s=p.read_text();assert s.count('HMGAPI_VERSION = "1.0.1"')==1
p.write_text(s.replace('HMGAPI_VERSION = "1.0.1"','HMGAPI_VERSION = "1.0.2.1"'))
print(a.out)
