"""Exercise the packaged shell service with synthetic timestamps, readings and screen states."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess

root = Path(__file__).resolve().parents[3]
service = root / 'mods/creta-battery-watchdog/svc/watch.sh'
with TemporaryDirectory() as folder:
    tmp = Path(folder)
    def mock(name, script):
        p = tmp / name
        p.write_text('#!/bin/sh\n' + script + '\n')
        p.chmod(0o755)
    mock('date', 'cat time')
    mock('dumpsys', 'cat display')
    mock('hmgapid', '[ "$*" = "vehicle battery12v.soc" ] || exit 1; cat pct')
    mock('am', 'echo "$*" >> alerts')
    mock('sleep', 'kill -TERM "$PPID"')
    base = 1794000000
    env = dict(os.environ, HMGAPI_DATA=folder, PATH=folder+':'+os.environ['PATH'])
    def poll(seconds, pct, on=True):
        (tmp/'time').write_text(str(base+seconds))
        (tmp/'pct').write_text('battery12v.soc '+pct)
        (tmp/'display').write_text('mScreenOn='+('true' if on else 'false'))
        p = subprocess.run(['sh', str(service)], env=env, timeout=3)
        assert p.returncode == -15, p.returncode
    def alerts():
        return (tmp/'alerts').read_text().splitlines() if (tmp/'alerts').exists() else []
    poll(0, '-')
    assert not (tmp/'checkpoint').exists() and not alerts()
    poll(60, '80')
    poll(1260, '79', False)
    assert (tmp/'checkpoint').read_text().split()[3]=='80' and not alerts()
    poll(1320, '80')
    for t in range(1380, 2641, 60):
        poll(t, '78')
    poll(3600, '58')
    assert len(alerts()) == 1 and all(s in alerts()[0] for s in ('battery low', 'dropped 20 points', 'previous session'))
    before=(tmp/'checkpoint').read_bytes()
    for t,v in [(3660,'101'),(3720,'-'),(3780,'00'),(3840,'1.2')]:
        poll(t,v); assert (tmp/'checkpoint').read_bytes()==before and len(alerts())==1
    poll(3900, '57')
    assert len(alerts())==1
    poll(3960, '61'); poll(4020, '59')
    assert len(alerts())==2
    assert not any(p.suffix in ('.csv','.log') for p in tmp.iterdir())
print('PASS: low charge, parked drop, prior-session decrease, repeat suppression, recovery, sleep and invalid samples.')
