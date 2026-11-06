"""Mock Android commands, including absent printf/sed, and exercise capture preflight."""
from pathlib import Path
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]
stage=ROOT/'usb/cluster-stop-check'
for script in stage.glob('*.sh'):
    subprocess.run(['/bin/sh','-n',str(script)],check=True)
worker=(stage/'cluster-stop-worker.sh').read_text().replace('/system/bin/hmgapid ping', ':')
filter_source=(stage/'cluster-fields.sh').read_text()
with tempfile.TemporaryDirectory() as td:
    root=Path(td)
    cases=[('readable',True,False),('unreadable',False,False),('old_printf_failure',True,True)]
    for name,readable,old_printf in cases:
        out=root/name;out.mkdir()
        sample='  TBT Info:\n    Display Type  = Right\n    Distance      = 120 m\n  DestName = PRIVATE_DESTINATION\n  OperationStatus = 1\n  TurnList = PRIVATE_ROAD\n'
        if not readable:sample='Permission Denial: PRIVATE_ID\n'
        # These failures model commands actually missing on the head unit.
        # Mock output uses echo, so a host printf builtin cannot hide a regression.
        mock="""printf() { echo 'printf: not found' >&2; return 127; }
sed() { echo 'sed: not found' >&2; return 127; }
date() { echo MOCK_TIME; }
getprop() { echo SU2IFL.IND.0000.V010.001.260430; }
dumpsys() { echo '__SAMPLE__'; }
am() { :; }
sleep() { :; }
sync() { :; }
logcat() { echo 'CarPlay: maneuver PRIVATE_ROAD
CarPlay: hud list type 67
SECRET_UNRELATED_LINE'; }
""".replace('__SAMPLE__',sample)
        filter_file=root/(name+'-fields.sh')
        source=filter_source
        body=worker
        if old_printf:
            source=source.replace('echo "$field_line"', "printf '%s\\n' \"$field_line\"")
            body=body.replace('echo "$preflight"', "printf '%s\\n' \"$preflight\"")
        filter_file.write_text(source)
        harness=root/(name+'.sh');harness.write_text(mock+body)
        p=subprocess.run(['/bin/sh',str(harness),str(out),str(filter_file)],capture_output=True,text=True)
        succeeds=readable and not old_printf
        assert p.returncode==(0 if succeeds else 1),(name,p.stdout,p.stderr)
        if succeeds:
            assert (out/'COMPLETE.txt').exists()
            fields=(out/'cluster-fields.txt').read_text()
            assert fields.count('SAMPLE ')==60 and 'Display Type' in fields
            assert 'CARPLAY_MANEUVER' in (out/'events.txt').read_text()
            assert not p.stderr,p.stderr
        else:
            assert (out/'FAILED.txt').exists() and not (out/'COMPLETE.txt').exists()
            assert not (out/'cluster-fields.txt').exists()
        if old_printf:assert 'printf: not found' in p.stderr
        for f in out.iterdir():
            assert not any(x in f.read_text() for x in ('PRIVATE','SECRET_UNRELATED')),f
print('PASS: original missing-printf failure reproduced; corrected 60-sample capture works without printf/sed; unreadable-service failure and privacy filters pass.')
