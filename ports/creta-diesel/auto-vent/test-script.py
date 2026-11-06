"""Catch physical-seat targeting regressions and refuse sends without a valid Park reading."""
from pathlib import Path
import os
import subprocess
import tempfile

here = Path(__file__).resolve().parent
script = (here/'test.sh').read_text()
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    binaries = root/'bin'
    binaries.mkdir()
    mocks = {
        'am': 'exit 0',
        'sleep': 'exit 0',
        'hmgapid': '''
case "$*" in
 "vehicle gear.park") echo "gear.park $TEST_PARK";;
 vehicle-do*) echo "$*" >> "$TEST_CALLS"; echo "ok passenger seat ventilation high";;
 *) echo 'seat_vent.passenger 0';;
esac
'''
    }
    for name, body in mocks.items():
        file = binaries/name
        file.write_text('#!/bin/sh\n'+body+'\n')
        file.chmod(0o700)
    source = script.replace(
        'export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin',
        'export PATH='+str(binaries)+':/usr/bin:/bin').replace(
        'H=/system/bin/hmgapid', 'H='+str(binaries/'hmgapid'))
    for park in ('1', '0', '-'):
        calls = root/('calls-'+park)
        result = subprocess.run(['sh','-c',source], capture_output=True, text=True,
                                env=dict(os.environ, TEST_PARK=park, TEST_CALLS=str(calls)))
        assert result.returncode == (0 if park == '1' else 1), result.stdout+result.stderr
        if park == '1':
            assert calls.read_text() == 'vehicle-do seat_vent passenger high\n'
        else:
            assert not calls.exists()
print('PASS single opposite-seat high request in Park; none for non-P or unavailable reading.')
