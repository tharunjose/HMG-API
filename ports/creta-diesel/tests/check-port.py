#!/usr/bin/env python3
"""Check the public source snapshot; no vehicle inputs or network required."""
from pathlib import Path
import json,subprocess,py_compile,tempfile
root=Path(__file__).resolve().parents[1]
repo=root.parents[1]
profile=root/'maps/hyundai/creta-diesel/ind/260430'
car=json.loads((profile/'car.json').read_text())
assert car['status']=='mapped' and car['verified'] is None
points={}
for p in profile.glob('*.json'):
    if p.name=='car.json':continue
    data=json.loads(p.read_text());assert not (points.keys() & data.keys())
    points.update(data)
    assert p.read_bytes()==(repo/'maps/hyundai/creta-diesel/ind/260430'/p.name).read_bytes()
assert len(points)==424,len(points)
assert points['btsettings.projection_helper']['class'].endswith('.iO')
assert len((root/'reference/stock.md5').read_text().splitlines())==42
for p in (root/'usb').rglob('*.sh'):
    subprocess.run(['/bin/sh','-n',str(p)],check=True)
with tempfile.TemporaryDirectory() as temp:
    for i,p in enumerate(list((root/'scripts').glob('*.py'))+list((root/'tests').glob('*.py'))):
        py_compile.compile(str(p),cfile=str(Path(temp)/str(i)),doraise=True)
# Check only publishable port sources; local private inputs and outputs are excluded by Git.
for top in ['scripts','tests','docs','reference','maps','usb']:
    for p in (root/top).rglob('*'):
        if not p.is_file():continue
        assert p.suffix.lower() not in ('.key','.pem','.p12','.apk','.odex','.dex','.jar','.so','.zip','.heic','.png','.jpg'),p
        data=p.read_bytes()
        assert b'/' + b'Users/' not in data,p
        assert b'BEGIN ' + b'PRIVATE KEY' not in data,p
        assert b'BEGIN ' + b'EC PRIVATE KEY' not in data,p
print('PASS: 424 points, duplicate map consistency, 42 stock gates, shell/Python syntax, public-source hygiene.')
