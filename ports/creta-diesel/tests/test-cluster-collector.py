"""Host smoke test with mocked Android commands; proves no sed is needed."""
from pathlib import Path
import subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
stage=ROOT/'usb/cluster-stop-check'
for script in stage.glob('*.sh'):
    subprocess.run(['/bin/sh','-n',str(script)],check=True)
worker=(stage/'cluster-stop-worker.sh').read_text().replace('/system/bin/hmgapid ping', ':')
with tempfile.TemporaryDirectory() as td:
    root=Path(td)
    for readable in (True, False):
        out=root/str(readable);out.mkdir()
        sample='  TBT Info:\n    Display Type  = Right\n    Distance      = 120 m\n  DestName = PRIVATE_DESTINATION\n  OperationStatus = 1\n  TurnList = PRIVATE_ROAD\n'
        if not readable: sample='Permission Denial: PRIVATE_ID\n'
        # Functions supply every command used; the worker PATH has no macOS tools.
        mock="""date() { printf 'MOCK_TIME\n'; }
getprop() { printf 'SU2IFL.IND.0000.V010.001.260430\n'; }
dumpsys() { printf '%b' '__SAMPLE__'; }
am() { :; }
sleep() { :; }
sync() { :; }
logcat() { printf 'CarPlay: maneuver PRIVATE_ROAD\nCarPlay: hud list type 67\nSECRET_UNRELATED_LINE\n'; }
""".replace("__SAMPLE__", sample)
        harness=root/('worker-'+str(readable)+'.sh')
        harness.write_text(mock+worker)
        p=subprocess.run(['/bin/sh',str(harness),str(out),str(stage/'cluster-fields.sh')],capture_output=True,text=True)
        assert p.returncode==(0 if readable else 1),(p.stdout,p.stderr)
        if readable:
            assert (out/'COMPLETE.txt').exists()
            fields=(out/'cluster-fields.txt').read_text()
            assert fields.count('SAMPLE ')==60 and 'Display Type' in fields
            assert 'CARPLAY_MANEUVER' in (out/'events.txt').read_text()
        else:
            assert (out/'FAILED.txt').exists() and not (out/'COMPLETE.txt').exists()
        for f in out.iterdir():
            assert not any(x in f.read_text() for x in ('PRIVATE','SECRET_UNRELATED')),f
print('PASS: 60 samples with mocked Android commands; no sed; private strings excluded; unreadable-service preflight fails before capture.')
