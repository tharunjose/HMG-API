#!/usr/bin/env python3
"""Download and verify two pinned upstream assets; check out pinned source."""
from pathlib import Path
import hashlib,json,subprocess,urllib.request
root=Path(__file__).resolve().parents[1]
lock=json.loads((root/'reference/upstream.json').read_text())
source=root/'upstream'
if source.exists():
    actual=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    if actual!=lock['source_commit']:raise SystemExit('Existing upstream is a different commit; move it aside yourself.')
else:
    subprocess.run(['git','clone','--no-checkout',lock['source_repo'],str(source)],check=True)
    subprocess.run(['git','-C',str(source),'checkout','--detach',lock['source_commit']],check=True)
(root/'downloads').mkdir(exist_ok=True)
for name,info in lock['assets'].items():
    target=root/'downloads'/name
    if not target.exists():
        temp=target.with_suffix('.part')
        with urllib.request.urlopen(info['url'],timeout=60) as response,temp.open('wb') as output:
            while True:
                data=response.read(1024*1024)
                if not data:break
                output.write(data)
        if hashlib.sha256(temp.read_bytes()).hexdigest()!=info['sha256']:
            temp.unlink();raise SystemExit('Checksum failed: '+name)
        temp.rename(target)
    if hashlib.sha256(target.read_bytes()).hexdigest()!=info['sha256']:
        raise SystemExit('Checksum failed: '+name)
    print('Verified',name)
